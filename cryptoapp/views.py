from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.serializers import serialize
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from COMP8347 import settings
from .forms import UserForm, PaymentForm, UserProfileUpdateForm, amountTransfer, ConvertForm
from .models import Payment_Transaction, Currency, User, BitcoinData, ExchangeRateHis, CryptoWallet


def register(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()

            # Add a success message
            messages.success(request, 'User has been successfully registered!')

            # Update the redirect URL to the actual homepage URL or login page
            return redirect('cryptoapp:login_view')
        else:
            messages.success(request, 'User there was an issue in the form!')
            print(form)
            return render(request, 'cryptoapp/register.html', {'form': form})
    else:
        form = UserForm()

    return render(request, 'cryptoapp/register.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    # request.session.flush()
    # Deletes the current session data from the session and deletes the session cookie.
    # last_login_info = request.session.pop('last_login_info',None)
    return render(request, 'cryptoapp/logout.html')


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            recaptcha_response = request.POST.get('g-recaptcha-response')
            if not recaptcha_response:
                form.add_error(None, 'Please complete the reCAPTCHA.')
            else:
                # reCAPTCHA verification passed
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('cryptoapp:homepage')  # Redirect to a different page after login
        else:
            form.add_error(None, 'Invalid username or password.')
            error_message = "Invalid username or password. Please try again"
            return render(request, 'cryptoapp/login.html', {'form': form, 'error_message': error_message})
    else:
        form = AuthenticationForm()

    return render(request, 'cryptoapp/login.html', {'form': form, 'recaptcha_site_key': settings.RECAPTCHA_PUBLIC_KEY})


@login_required
def user_dashboard(request):
    user_profile = request.user
    context = {'user_profile': user_profile}
    return render(request, 'cryptoapp/user_dashboard.html', context)


@login_required(login_url='cryptoapp:login_view')
def edit_profile(request):
    user_profile = request.user

    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('cryptoapp:user_dashboard')
    else:
        form = UserProfileUpdateForm(instance=user_profile)

    return render(request, 'cryptoapp/edit_info.html', {'form': form})

def logout_view(request):
    request.session.set_expiry(0)
    logout(request)
    return redirect('cryptoapp:homepage')


@login_required(login_url='cryptoapp:login_view')
def delete_account(request):
    if request.method == 'POST':
        password = request.POST.get('password', '')

        # Check if the entered password is valid
        if not request.user.check_password(password):
            messages.error(request, 'Incorrect password. Please try again.')
            return redirect('cryptoapp:delete_account')

        user = request.user

        user.delete()

        messages.success(request, 'Your account has been deleted.')
        logout(request)  # Log the user out after deleting the account
        return redirect('cryptoapp:register')

    return render(request, 'cryptoapp/delete_account.html')


@login_required()
def make_payment(request, currency_to, order_amount):
    user = request.user
    # user = UserProfile.objects.get(id=1)
    currency_to = Currency.objects.get(symbol=currency_to)
    currency_from = Currency.objects.get(id=1)
    currency_recieved = round(order_amount / currency_to.price, 8)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        print("Error", form.errors)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            print("form Validated, PM: ", payment_method)

            if payment_method == 'card':
                # Credit card payment logic
                # name_on_card = form.cleaned_data['name_on_card']
                # card_number = form.cleaned_data['card_number']
                # expiry = form.cleaned_data['expiry']
                # cvv = form.cleaned_data['cvv']

                # Create a Payment_Transaction record for the credit card payment
                transaction = Payment_Transaction.objects.create(
                    # user=request.user,
                    user=user,
                    currency_from=currency_from,
                    currency_to=currency_to,
                    amount_from=order_amount,
                    amount_to=currency_recieved,
                    payment_method=payment_method,
                    transaction_type='purchased',  # Adjust as needed
                    balance_after_transaction=0,
                    sold=False
                )

                return redirect('cryptoapp:payment_success', transaction_id=transaction.id)

            elif payment_method == 'wallet':

                if order_amount > user.balance:
                    # Insufficient balance, handle accordingly (redirect, show error, etc.)
                    return redirect('cryptoapp:payment_failure')

                # Process wallet payment logic here
                # Deduct points from the user's wallet
                user.balance = user.balance - order_amount
                print(user.balance)
                user.save()

                # Create a Payment_Transaction record for the wallet payment
                transaction = Payment_Transaction.objects.create(
                    # user=request.user,
                    user=user,
                    currency_from=currency_from,
                    currency_to=currency_to,
                    amount_from=order_amount,
                    amount_to=currency_recieved,
                    payment_method=payment_method,
                    transaction_type='purchased',  # Adjust as needed
                    balance_after_transaction=user.balance,
                    sold=False
                )
                return redirect('cryptoapp:payment_success', transaction_id=transaction.id)

    else:
        form = PaymentForm()

    return render(request, 'cryptoapp/make_payment.html', {
        'form': form,
        'user': user,
        'order_amount': order_amount,
        'currency': currency_to,
        'currency_recieved': currency_recieved,
    })


@login_required()
def payment_success(request, transaction_id):
    transaction = Payment_Transaction.objects.get(id=transaction_id)
    return render(request, 'cryptoapp/payment_success.html', {'transaction': transaction})


@login_required()
def payment_failure(request):
    return render(request, 'cryptoapp/payment_failed.html')


@login_required
def payment_history(request):
    user = request.user
    payments = Payment_Transaction.objects.filter(user=user)
    return render(request, 'cryptoapp/payment_history.html', {'payments': payments})


def update_balance(request, transaction_id):
    user = request.user
    if request.method:
        transaction = get_object_or_404(Payment_Transaction, pk=transaction_id)
        order_amount = transaction.amount_to

        if transaction.balance_after_transaction >= 0:
            # Update balance_after_transaction
            update_balance = Payment_Transaction.objects.create(
                user=user,
                payment_method='wallet',  # Provide a valid default value
                currency_from=transaction.currency_to,
                currency_to=transaction.currency_to,
                amount_from=transaction.amount_from,  # Use the correct field for the amount
                amount_to=order_amount,
                timestamp=transaction.timestamp,
                transaction_type='sold',
                balance_after_transaction=user.balance + transaction.amount_from,
                sold=True,
            )

            transaction.sold = True
            transaction.save()

            user.balance = user.balance + transaction.amount_from
            user.save()

            return render(request, 'cryptoapp/history_success.html')
        return render(request, 'cryptoapp/history_failure.html')


def delete_object(request, pk):
    user = request.user
    obj = Payment_Transaction.objects.get(pk=pk)
    obj.delete()
    obj = Payment_Transaction.objects.filter(user=user)
    return render(request, 'cryptoapp/payment_history.html', {'payments': obj})

def homepage(request):
    data = BitcoinData.objects.all()
    currency = Currency.objects.all()
    return render(request, 'cryptoapp/homepage.html', {'data': data, 'currency': currency})


def bitcoin_chart(request):
    data = BitcoinData.objects.all()
    return render(request, 'cryptoapp/bitcoin_chart.html', {'data': data})

# @login_required()
def currency_detail(request, name):

    currency = get_object_or_404(Currency, name=name)
    all_currency = Currency.objects.all()
    exchange_rates = ExchangeRateHis.objects.filter(currency=currency).order_by('-date')


    # try:
    # latest_exchange_rate = currency.price
        # if latest_exchange_rate is None:
        #     # Print error log or display error message on frontend
        #     latest_rate = "No available exchange rate data"
        #     print(f"No latest exchange rate record found for {name}.")
        # else:
        #     latest_rate = latest_exchange_rate.rate
    # except Exception as e:
        # Handle any exceptions here, such as database connection issues, etc.
        # latest_rate = "Error: Unable to retrieve exchange rate"
        # print(f"Error occurred while retrieving the latest exchange rate for {name}: {e}")

    exchange_rates_json = serialize('json', exchange_rates)
    # user_wallets = Wallet.objects.filter(user=request.user)

    # wallet, created = Wallet.objects.get_or_create(user=request.user)
    # cryptowallet, created = CryptoWallet.objects.get_or_create(user=user, currency=currency)
    # latest_exchange_rate = ExchangeRateHis.objects.filter(currency=currency).order_by('-date').first()

    # quantity = CryptoWallet.objects.filter(user=user, currency=currency).first()
    # notional_value = round(quantity.amount * latest_exchange_rate.rate, 2)

    # other_show_currencies = Currency.objects.all()
    # for others in other_show_currencies:
    #     # Fetch the latest price
    #     l_rate = ExchangeRateHis.objects.filter(currency=others).order_by('-date').first()
    #     if l_rate:
    #         others.current_price = l_rate.rate
    #     else:
    #         others.current_price = "Data Incomplete"

    #  initialize forms
    form1 = amountTransfer()
    form2 = ConvertForm()
    ans = 0.00

    if 'jump' in request.POST:
        if request.method == 'POST':
            form1 = amountTransfer(request.POST)
            if form1.is_valid():
                return redirect('cryptoapp:make_payment', currency_to=currency.symbol, order_amount=form1.cleaned_data['amount'])

    if 'convert' in request.POST:
        if request.method == 'POST':
            form2 = ConvertForm(request.POST)
            if form2.is_valid():
                ans = form2.update_Cryptowallet(currency)

    ans = round(ans, 2)
    context = {
        'currency': currency,
        'exchange_rates': exchange_rates_json,
        # 'latest_exchange_rate': latest_rate,
        # 'user_info': user,
        'form1': form1,
        'form2': form2,
        # 'quantity': quantity,
        # 'notional_value': notional_value,
        # 'other_show_currencies': other_show_currencies,
        'ans': ans,
        'all_currency': all_currency,
        # 'cryptowallet': cryptowallet
    }
    return render(request, 'cryptoapp/currency_detail.html', context)