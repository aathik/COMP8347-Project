from django import forms
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from datetime import datetime
from django.core.exceptions import ValidationError
from .validators import validate_email_value
from .models import User, ExchangeRateHis, Currency
from .validators import validate_password_uppercase, validate_password_lowercase, validate_password_special_characters, \
    validate_mobile_number

class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        validators=[
            validate_password,
            validate_password_uppercase,
            validate_password_lowercase,
            validate_password_special_characters,
        ],
        help_text='Your password must meet the requirements.',
    )

    mobile_number = forms.CharField(validators=[validate_mobile_number])
    email = forms.EmailField(validators=[validate_email_value])

    gender = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={'class': 'gender-radio'}),
        choices=User.GENDER_CHOICES,
        initial='male'
    )

    # gender = forms.ChoiceField(widget=forms.RadioSelect, choices=User.GENDER_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'gender', 'photo', 'mobile_number']
        # Add any other fields you want to include in the registration form

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].help_text = ''
        self.fields['password'].help_text = ''
        self.fields['photo'].label = 'Photo ID'

        # self.fields['password'].widget = forms.HiddenInput()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])

        if commit:
            user.save()

        return user


class PaymentForm(forms.Form):
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('wallet', 'Wallet'),
    ]
    payment_method = forms.ChoiceField(
        widget=forms.Select(attrs={'id': 'payment-method-form', 'style': 'display: none;'}),
        choices=PAYMENT_METHOD_CHOICES,
        initial='',
        required=True
    )

    name_on_card = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'id': 'name'}),
        required=False  # Initial value, can be adjusted dynamically

    )
    card_number = forms.CharField(
        widget=forms.TextInput(attrs={'id': 'cardnumber', 'type': 'text', 'inputmode': 'numeric'}),
        required=False  # Initial value, can be adjusted dynamically
    )
    expiry = forms.CharField(
        widget=forms.TextInput(attrs={'id': 'expirationdate', 'type': 'text', 'inputmode': 'numeric'}),
        required=False  # Initial value, can be adjusted dynamically
    )
    cvv = forms.CharField(
        widget=forms.TextInput(attrs={'id': 'securitycode', 'type': 'password', 'inputmode': 'numeric'}),
        required=False  # Initial value, can be adjusted dynamically
    )

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')
        name_on_card = cleaned_data.get('name_on_card')
        card_number = cleaned_data.get('card_number')
        expiry = cleaned_data.get('expiry')
        cvv = cleaned_data.get('cvv')
        print("Informs:", payment_method)
        # Adjust the required attribute based on the selected payment method
        if payment_method == 'wallet':
            self.fields['name_on_card'].required = False
            self.fields['card_number'].required = False
            self.fields['expiry'].required = False
            self.fields['cvv'].required = False
        else:
            # if payment_method == 'card' and (name_on_card == '' or card_number == '' or expiry == '' or cvv == ''):
            print(expiry[3:])
            print(expiry[:-3])
            current_date = datetime.now()
            year = current_date.strftime("%y")
            month = current_date.strftime("%m")
            print(int(year))

            if name_on_card == 0:
                self._errors['name_on_card'] = self.error_class(['* required'])
            elif len(name_on_card) > 20:
                self._errors['name_on_card'] = self.error_class(['Name should be less than 20 characters'])
            elif card_number == '':
                self._errors['card_number'] = self.error_class(['* required'])
            elif len(card_number) < 16 or len(card_number) > 19:
                self._errors['card_number'] = self.error_class(['Invalid card number'])
            elif len(cvv) != 3:
                self._errors['cvv'] = self.error_class(['invalid expiry'])
            elif expiry == '':
                self._errors['expiry'] = self.error_class(['* required'])

            elif int(expiry[3:]) < int(year):
                self._errors['expiry'] = self.error_class(['invalid expiry'])
            if int(expiry[3:]) == int(year) and int(expiry[:-3]) <= int(month):
                self._errors['expiry'] = self.error_class(['invalid expiry'])

        return cleaned_data
class UserProfileUpdateForm(forms.ModelForm):
    username = forms.CharField(help_text=False)

    class Meta:
        model = User
        fields = ['mobile_number', 'email', 'username', 'photo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Optionally, you can customize the labels or help_text for the fields here
        self.fields['mobile_number'].label = 'Mobile Number'
        self.fields['email'].label = 'Email'
        self.fields['username'].label = 'Username'

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data['mobile_number']
        # You can add any additional validation for mobile_number if needed
        return mobile_number

    def clean_email(self):
        email = self.cleaned_data['email']
        # You can add any additional validation for email if needed
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        # You can add any additional validation for username if needed
        return username


#crypto-exchange

class ConvertForm(forms.Form):
    crypto_to = forms.ModelChoiceField(queryset=Currency.objects.all())
    crypto_amount = forms.DecimalField(max_digits=15, decimal_places=2)

    def update_Cryptowallet(self, crypto_to):
        amount = self.cleaned_data['crypto_amount']
        rate_from = ExchangeRateHis.objects.filter(currency=self.cleaned_data['crypto_to']).order_by('-date')[0]
        rate_to = ExchangeRateHis.objects.filter(currency=crypto_to).order_by('-date')[0]
        ans = amount * rate_from.rate / rate_to.rate
        return ans


class amountTransfer(forms.Form):
    amount = forms.DecimalField(max_digits=15, decimal_places=2)