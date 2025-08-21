# management/commands/fix_empty_orders.py
from django.core.management.base import BaseCommand
from cakes.models import Order, OrderItem, Cake
from decimal import Decimal


class Command(BaseCommand):
    help = 'Add mock items to orders that have no OrderItems'

    def handle(self, *args, **options):
        empty_orders = Order.objects.filter(items__isnull=True).distinct()
        count = empty_orders.count()
        self.stdout.write(f"Found {count} orders with no items")
        
        # Get a default cake to use
        default_cake = Cake.objects.first()
        if not default_cake:
            self.stdout.write(self.style.ERROR('No cakes found in database. Please seed some cakes first.'))
            return
        
        updated = 0
        for order in empty_orders:
            # Add a mock item
            OrderItem.objects.create(
                order=order,
                cake=default_cake,
                quantity=1,
                unit_price=default_cake.price or Decimal('499.00')
            )
            updated += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully added items to {updated} empty orders')
        )
