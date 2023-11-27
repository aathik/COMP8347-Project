from django.contrib import admin
from .models import User,Currency,Payment_Transaction, BitcoinData, CryptoWallet,ExchangeRateHis

# Register your models here.
# admin.site.register(UserProfile)
admin.site.register(User)
admin.site.register(Currency)
# admin.site.register(UserTransaction)
# admin.site.register(PaymentHistory)
admin.site.register(Payment_Transaction)
admin.site.register(BitcoinData)
admin.site.register(CryptoWallet)
admin.site.register(ExchangeRateHis)
