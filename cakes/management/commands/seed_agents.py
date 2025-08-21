from django.core.management.base import BaseCommand
from cakes.models import DeliveryAgent


AGENTS = [
    ("Ravi Kumar", "9000000001"),
    ("Anita Sharma", "9000000002"),
    ("Mohammed Ali", "9000000003"),
    ("Priya Singh", "9000000004"),
    ("Vikram Patel", "9000000005"),
]


class Command(BaseCommand):
    help = "Seed sample delivery agents"

    def handle(self, *args, **options):
        created = 0
        for name, phone in AGENTS:
            obj, was_created = DeliveryAgent.objects.get_or_create(phone=phone, defaults={"name": name, "is_available": True})
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Agents present: {DeliveryAgent.objects.count()} (added {created})"))
