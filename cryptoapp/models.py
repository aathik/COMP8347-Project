from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class User(AbstractUser):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ]

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    photo = models.ImageField(upload_to='user_photos/')
    mobile_number = models.CharField(max_length=15, default='')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    # Specify unique related names for groups and user_permissions
    groups = models.ManyToManyField(Group, verbose_name='Groups', blank=True, related_name='cryptoapp_user_groups')
    user_permissions = models.ManyToManyField(Permission, verbose_name='User Permissions', blank=True,
                                              related_name='cryptoapp_user_permissions')


# class UserProfile(models.Model):
#     GENDER_CHOICES = [
#         ('M', 'Male'),
#         ('F', 'Female'),
#     ]
#     username = models.CharField(max_length=100)
#     password = models.CharField(max_length=100)
#     email = models.EmailField()
#     first_name = models.CharField(max_length=50)
#     last_name = models.CharField(max_length=50)
#     gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
#     photo = models.ImageField(upload_to='user_photos/')
#     mobile_number = models.CharField(max_length=15, default='')

class Currency(models.Model):
    CURRENCY_TYPES = (('Forex', 'Forex'), ('Crypto', 'Cryptocurrency'),)
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    trend = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    trend_rate = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    market_cap = models.CharField(max_length=20, blank=True, null=True)
    currency_type = models.CharField(max_length=20, choices=CURRENCY_TYPES, default='Crypto')
    link = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.symbol


class Payment_Transaction(models.Model):
    TYPES = (('purchased', 'purchased'), ('sold', 'sold'),)
    METHOD = (('wallet', 'Wallet'), ('card', 'Credit/Debit Card'),)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=6, choices=METHOD, default='')
    currency_from = models.ForeignKey(Currency, related_name='payment_from_currency', on_delete=models.PROTECT,
                                      default='')
    currency_to = models.ForeignKey(Currency, related_name='payment_to_currency', on_delete=models.PROTECT, default='')
    amount_from = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_to = models.DecimalField(max_digits=10, decimal_places=6, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=10, choices=TYPES)
    balance_after_transaction = models.DecimalField(max_digits=10, decimal_places=2)
    sold = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - {self.currency_to} Payment'


class BitcoinData(models.Model):
    timestamp = models.DateTimeField()
    price = models.FloatField()


class CryptoWallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crypto_wallets')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)  # Assuming 2 decimal places for currency amounts

    def __str__(self):
        return f"{self.user_id} - {self.currency.name} : {self.amount}"


class ExchangeRateHis(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    date = models.DateField()
    rate = models.DecimalField(max_digits=10, decimal_places=6)

    class Meta:
        unique_together = ('currency', 'date')

    def __str__(self):
        return f"{self.currency.symbol} - {self.date} - {self.rate}"
