# management/commands/backfill_unit_prices.py
from django.core.management.base import BaseCommand
from cakes.models import OrderItem


class Command(BaseCommand):
    help = 'Backfill unit_price for OrderItems that have unit_price=0'

    def handle(self, *args, **options):
        zero_items = OrderItem.objects.filter(unit_price=0)
        count = zero_items.count()
        self.stdout.write(f"Found {count} items with unit_price=0")
        
        updated = 0
        for item in zero_items:
            if item.cake and item.cake.price:
                item.unit_price = item.cake.price
                item.save()
                updated += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated} OrderItems with unit_price')
        )
