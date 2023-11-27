# -*- coding: utf-8 -*-
"""
Author: Peiyi Ding
作者： 丁沛奕
Created by 28918 on 2023/11/24
"""

# Please use this snippet to populate the database with fake exchange rate data for September and October for all currencies.

from datetime import datetime
from decimal import Decimal
import random
from cryptoapp.models import ExchangeRateHis, Currency
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Populates the database with fake exchange rate data for September and October for all currencies."

    def handle(self, *args, **kwargs):
        # Fetch all Currency instances from the database
        currency_instances = Currency.objects.all()

        # Determine dates for September and October
        current_year = datetime.now().year
        september_dates = [datetime(current_year, 9, day) for day in range(1, 31)]
        october_dates = [datetime(current_year, 10, day) for day in range(1, 31)]

        # Combine dates for September and October
        dates = september_dates + october_dates

        # Generate and save data for each currency
        for currency_instance in currency_instances:
            for date in dates:
                # Generate a random value between 0 and 5, in multiples of 0.5
                random_value = random.choice([x * 0.5 for x in range(0, 11)])

                # Calculate rate based on the random value
                rate = round(Decimal(100 * random_value + 2), 4)

                # Create or update ExchangeRateHis instance
                exchange_rate, created = ExchangeRateHis.objects.get_or_create(
                    currency=currency_instance,
                    date=date,
                    defaults={'rate': rate}
                )
                if not created:
                    # If data for the date exists, update the exchange rate
                    exchange_rate.rate = rate
                    exchange_rate.save()

        self.stdout.write(
            self.style.SUCCESS('Successfully populated exchange rates for September and October for all currencies.'))
