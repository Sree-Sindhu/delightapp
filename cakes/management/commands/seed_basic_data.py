# management/commands/seed_basic_data.py
from django.core.management.base import BaseCommand
from cakes.models import Cake, Store
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create basic cakes and stores for testing'

    def handle(self, *args, **options):
        # Create a basic store
        store, created = Store.objects.get_or_create(
            name="Delightful Bakery",
            defaults={
                'location': 'Hyderabad',
                'phone_number': '+91-9876543210',
                'latitude': 17.3850,
                'longitude': 78.4867
            }
        )
        if created:
            self.stdout.write(f'Created store: {store.name}')
        
        # Create basic cakes
        cakes_data = [
            {'name': 'Chocolate Cake', 'flavor': 'Chocolate', 'size': '1 kg', 'price': Decimal('499.00')},
            {'name': 'Vanilla Cake', 'flavor': 'Vanilla', 'size': '1 kg', 'price': Decimal('449.00')},
            {'name': 'Custom Cake', 'flavor': 'Custom', 'size': 'Variable', 'price': Decimal('699.00')},
        ]
        
        created_count = 0
        for cake_data in cakes_data:
            cake, created = Cake.objects.get_or_create(
                name=cake_data['name'],
                defaults=cake_data
            )
            if created:
                cake.stores.add(store)
                created_count += 1
                self.stdout.write(f'Created cake: {cake.name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} cakes and 1 store')
        )
