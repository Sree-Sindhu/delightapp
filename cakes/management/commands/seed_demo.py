from django.core.management.base import BaseCommand
from cakes.models import Store, Cake, Category

# Minimal mirror of frontend data for seeding
STORES_MAP = {
    "bakingo": "Bakingo",
    "brown-bear": "Brown Bear Bakers",
    "cakezone": "CakeZone",
    "hyd-banjara-karachi": "Karachi Bakery",
    "hyd-madhapur-justbake": "Just Bake",
    "hyd-gachibowli-sweettruth": "Sweet Truth",
    "hyd-hitech-city-cakezone2": "CakeZone",
    "hyd-kondapur-citybakers": "City Bakers",
    "hyd-jubilee-theobroma": "Theobroma",
    "hyd-himayatnagar-karachi": "Karachi Bakery",
    "hyd-secunderabad-karachi": "Karachi Bakery",
    "hyd-kukatpally-justbake": "Just Bake",
    "hyd-begumpet-cakezone": "CakeZone",
    "hyd-miyapur-citybakers": "City Bakers",
    "hyd-gachibowli-theobroma": "Theobroma",
}

CAKES = [
    {"name": "Hazelnut Cake", "price": 599, "stores": ["bakingo", "brown-bear"]},
    {"name": "Classic Chocolate", "price": 499, "stores": ["bakingo", "brown-bear", "cakezone"]},
    {"name": "Fresh Fruit Cake", "price": 749, "stores": ["cakezone"]},
    {"name": "Custom Cake", "price": 999, "stores": [
        "bakingo", "brown-bear", "hyd-banjara-karachi", "hyd-madhapur-justbake", "hyd-kondapur-citybakers"
    ]},
    {"name": "Italian Forest", "price": 699, "stores": ["bakingo"]},
    {"name": "Black Forest", "price": 629, "stores": ["bakingo", "brown-bear", "cakezone"]},
    {"name": "Ice Cream Cake", "price": 799, "stores": ["brown-bear", "cakezone"]},
    {"name": "Red Velvet", "price": 679, "stores": ["bakingo", "brown-bear"]},
    {"name": "Blackcurrant Cake", "price": 569, "stores": ["cakezone"]},
    {"name": "Butterscotch", "price": 549, "stores": ["hyd-banjara-karachi", "hyd-madhapur-justbake", "hyd-kondapur-citybakers"]},
    {"name": "Pineapple", "price": 479, "stores": ["hyd-gachibowli-sweettruth", "hyd-hitech-city-cakezone2"]},
    {"name": "Blueberry", "price": 689, "stores": ["hyd-jubilee-theobroma", "hyd-banjara-karachi"]},
    {"name": "Chocolate Truffle", "price": 599, "stores": ["hyd-madhapur-justbake", "bakingo", "cakezone"]},
    {"name": "Strawberry", "price": 559, "stores": ["hyd-kondapur-citybakers", "hyd-gachibowli-sweettruth"]},
    {"name": "Mango", "price": 599, "stores": ["hyd-hitech-city-cakezone2", "brown-bear"]},
    {"name": "Oreo Crunch", "price": 619, "stores": ["hyd-jubilee-theobroma", "bakingo"]},
]

class Command(BaseCommand):
    help = "Seed demo Stores and Cakes so the frontend can add items to cart."

    def handle(self, *args, **options):
        # Create or get a default Category
        cat, _ = Category.objects.get_or_create(name="Cakes", defaults={"description": "All cakes"})

        # Create Stores by brand name (unique names)
        brand_to_store = {}
        for sid, brand in STORES_MAP.items():
            if brand in brand_to_store:
                continue
            store, _ = Store.objects.get_or_create(
                name=brand,
                defaults={
                    "location": f"{brand} - Hyderabad",
                    "phone_number": "0000000000",
                },
            )
            brand_to_store[brand] = store

        created_cakes = 0
        for c in CAKES:
            name = c["name"]
            price = c["price"]
            cake, created = Cake.objects.get_or_create(
                name=name,
                defaults={
                    "flavor": "classic",
                    "size": "1 kg",
                    "category": cat,
                    "price": price,
                },
            )
            # Attach stores based on brand names derived from ids
            brands = {STORES_MAP[sid] for sid in c.get("stores", []) if sid in STORES_MAP}
            for brand in brands:
                store = brand_to_store.get(brand)
                if store:
                    cake.stores.add(store)
            if created:
                created_cakes += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seeding complete. Stores: {len(brand_to_store)}, Cakes created: {created_cakes}."
        ))
