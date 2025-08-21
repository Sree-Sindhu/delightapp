from django.core.management.base import BaseCommand
from cakes.models import Store, Cake


class Command(BaseCommand):
    help = "Attach cakes to any stores that currently have none so no store is empty."

    def add_arguments(self, parser):
        parser.add_argument(
            '--all-cakes', action='store_true', default=False,
            help='If set, attach ALL cakes to empty stores. Otherwise attach a small default subset.'
        )

    def handle(self, *args, **options):
        all_cakes = options['all_cakes']
        cakes_qs = Cake.objects.all()
        if not cakes_qs.exists():
            self.stdout.write(self.style.WARNING('No cakes found in DB. Run seed_demo first.'))
            return

        default_subset = list(cakes_qs[:6])
        updated = 0
        for store in Store.objects.all():
            if store.cakes.count() == 0:
                attach_list = cakes_qs if all_cakes else default_subset
                for ck in attach_list:
                    store.cakes.add(ck)
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Updated {updated} store(s) with cakes."))
