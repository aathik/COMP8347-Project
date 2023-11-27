from django.core.management.base import BaseCommand
from faker import Faker
import random
from cryptoapp.models import BitcoinData
from django.utils import timezone

fake = Faker()

class Command(BaseCommand):
    help = 'Generates fake data for BitcoinData model'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Generating fake data...'))

        def generate_fake_data():
            for _ in range(50):
                timestamp = fake.date_time_between(start_date='-30d', end_date='now', tzinfo=timezone.utc)
                price = random.uniform(30000, 60000)  # Adjust the price range as needed
                BitcoinData.objects.create(timestamp=timestamp, price=price)

        generate_fake_data()

        self.stdout.write(self.style.SUCCESS('Fake data generation complete.'))
