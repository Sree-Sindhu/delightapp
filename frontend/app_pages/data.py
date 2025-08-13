# frontend/app_pages/data.py

STORES = {
    # id: brand (no area here)
    "bakingo": "Bakingo",
    "brown-bear": "Brown Bear Bakers",
    "cakezone": "CakeZone",
    # Hyderabad stores (same brands, different areas)
    "hyd-banjara-karachi": "Karachi Bakery",
    "hyd-madhapur-justbake": "Just Bake",
    "hyd-gachibowli-sweettruth": "Sweet Truth",
    "hyd-hitech-city-cakezone2": "CakeZone",
    "hyd-kondapur-citybakers": "City Bakers",
    "hyd-jubilee-theobroma": "Theobroma",
    # More branches
    "hyd-himayatnagar-karachi": "Karachi Bakery",
    "hyd-secunderabad-karachi": "Karachi Bakery",
    "hyd-kukatpally-justbake": "Just Bake",
    "hyd-begumpet-cakezone": "CakeZone",
    "hyd-miyapur-citybakers": "City Bakers",
    "hyd-gachibowli-theobroma": "Theobroma",
}

# Optional store metadata for maps (demo coordinates)
STORE_DETAILS = {
    "bakingo": {
        "address": "Bakingo - Koramangala, 1st Main Rd, 5th Block, Bengaluru, KA 560095",
        "city": "Bengaluru",
    "area": "Koramangala",
    "rating": 4.4,
    "reviews": 1240,
    },
    "brown-bear": {
        "address": "Brown Bear Bakers - Jubilee Hills, Hyderabad, TG 500033",
        "city": "Hyderabad",
    "area": "Jubilee Hills",
    "rating": 4.2,
    "reviews": 860,
    },
    "cakezone": {
        "address": "CakeZone - Indiranagar, 100 Feet Rd, Bengaluru, KA 560038",
        "city": "Bengaluru",
    "area": "Indiranagar",
    "rating": 4.3,
    "reviews": 2120,
    },
    # Hyderabad store addresses
    "hyd-banjara-karachi": {
        "address": "Karachi Bakery - Road No.1, Banjara Hills, Hyderabad, TG 500034",
        "city": "Hyderabad",
    "area": "Banjara Hills",
    "rating": 4.5,
    "reviews": 3400,
    },
    "hyd-madhapur-justbake": {
        "address": "Just Bake - Madhapur Main Rd, Hyderabad, TG 500081",
        "city": "Hyderabad",
    "area": "Madhapur",
    "rating": 4.1,
    "reviews": 980,
    },
    "hyd-gachibowli-sweettruth": {
        "address": "Sweet Truth - Gachibowli, Hyderabad, TG 500032",
        "city": "Hyderabad",
    "area": "Gachibowli",
    "rating": 4.0,
    "reviews": 650,
    },
    "hyd-hitech-city-cakezone2": {
        "address": "CakeZone - Hitech City, Hyderabad, TG 500081",
        "city": "Hyderabad",
    "area": "Hitech City",
    "rating": 4.2,
    "reviews": 1430,
    },
    "hyd-kondapur-citybakers": {
        "address": "City Bakers - Kondapur, Hyderabad, TG 500084",
        "city": "Hyderabad",
    "area": "Kondapur",
    "rating": 4.1,
    "reviews": 740,
    },
    "hyd-jubilee-theobroma": {
        "address": "Theobroma - Jubilee Hills, Hyderabad, TG 500033",
        "city": "Hyderabad",
    "area": "Jubilee Hills",
    "rating": 4.6,
    "reviews": 2850,
    },
    "hyd-himayatnagar-karachi": {
        "address": "Karachi Bakery - Himayatnagar, Hyderabad, TG 500029",
        "city": "Hyderabad",
    "area": "Himayatnagar",
    "rating": 4.4,
    "reviews": 1920,
    },
    "hyd-secunderabad-karachi": {
        "address": "Karachi Bakery - S.D Road, Secunderabad, TG 500003",
        "city": "Hyderabad",
    "area": "Secunderabad",
    "rating": 4.3,
    "reviews": 1570,
    },
    "hyd-kukatpally-justbake": {
        "address": "Just Bake - Kukatpally, Hyderabad, TG 500072",
        "city": "Hyderabad",
    "area": "Kukatpally",
    "rating": 4.0,
    "reviews": 820,
    },
    "hyd-begumpet-cakezone": {
        "address": "CakeZone - Begumpet, Hyderabad, TG 500016",
        "city": "Hyderabad",
    "area": "Begumpet",
    "rating": 4.2,
    "reviews": 1180,
    },
    "hyd-miyapur-citybakers": {
        "address": "City Bakers - Miyapur, Hyderabad, TG 500049",
        "city": "Hyderabad",
    "area": "Miyapur",
    "rating": 4.1,
    "reviews": 540,
    },
    "hyd-gachibowli-theobroma": {
        "address": "Theobroma - Gachibowli, Hyderabad, TG 500032",
        "city": "Hyderabad",
    "area": "Gachibowli",
    "rating": 4.5,
    "reviews": 1670,
    },
}

# Stores that accept custom cake orders
CUSTOM_CAKE_STORES = [
    "bakingo", "brown-bear", "hyd-banjara-karachi", "hyd-madhapur-justbake",
    "hyd-kondapur-citybakers"
]

# Size options and multipliers for dynamic pricing (base price ~ 0.5 kg)
CAKE_SIZES = {
    "options": ["0.5 kg", "1 kg", "2 kg"],
    "multipliers": {"0.5 kg": 1.0, "1 kg": 1.8, "2 kg": 3.3}
}

CAKES = [
    {
        "id": "hazelnut",
        "name": "Hazelnut Cake",
        "image": "hazelnutcake.jpeg",
        "price": 599,
        "description": "A rich, nutty hazelnut sponge layered with silky cream and roasted hazelnut crunch.",
        "stores": ["bakingo", "brown-bear"],
    },
    {
        "id": "chocolate",
        "name": "Classic Chocolate",
        "image": "chocolate.jpeg",
        "price": 499,
        "description": "Moist chocolate sponge with decadent cocoa ganache—an all-time favorite.",
        "stores": ["bakingo", "brown-bear", "cakezone"],
    },
    {
        "id": "fruit",
        "name": "Fresh Fruit Cake",
        "image": "fruit.jpeg",
        "price": 749,
        "description": "Vanilla sponge topped with seasonal fresh fruits and light whipped cream.",
        "stores": ["cakezone"],
    },
    {
        "id": "custom",
        "name": "Custom Cake",
        "image": "custom.jpeg",
        "price": 999,
        "description": "Design your own cake—choose flavors, sizes, and themes for every occasion.",
        "stores": CUSTOM_CAKE_STORES, # Available only where customization is offered
    },
    {
        "id": "italian",
        "name": "Italian Forest",
        "image": "italian.jpeg",
        "price": 699,
        "description": "An Italian twist on the classic forest cake with cherries and cream.",
        "stores": ["bakingo"],
    },
    {
        "id": "blackforest",
        "name": "Black Forest",
        "image": "blackforest.jpeg",
        "price": 629,
        "description": "Chocolate sponge with cherries, whipped cream, and dark chocolate shavings.",
        "stores": ["bakingo", "brown-bear", "cakezone"],
    },
    {
        "id": "icecream",
        "name": "Ice Cream Cake",
        "image": "icecream.jpeg",
        "price": 799,
        "description": "Creamy ice cream layers over soft sponge—served chilled for extra delight.",
        "stores": ["brown-bear", "cakezone"],
    },
    {
        "id": "redvelvet",
        "name": "Red Velvet",
        "image": "redvelvet.jpeg",
        "price": 679,
        "description": "Velvety crimson layers with classic cream cheese frosting.",
        "stores": ["bakingo", "brown-bear"],
    },
    {
        "id": "blackcurrant",
        "name": "Blackcurrant Cake",
        "image": "blackcurrant.jpeg",
        "price": 569,
        "description": "Tangy blackcurrant compote meets vanilla sponge and fresh cream.",
        "stores": ["cakezone"],
    },
    # New varieties
    {
        "id": "butterscotch",
        "name": "Butterscotch",
        "image": "butterscotch.jpeg",
        "price": 549,
        "description": "Crunchy praline with caramel butterscotch cream.",
        "stores": ["hyd-banjara-karachi", "hyd-madhapur-justbake", "hyd-kondapur-citybakers"],
    },
    {
        "id": "pineapple",
        "name": "Pineapple",
        "image": "pineapple.jpeg",
        "price": 479,
        "description": "Classic pineapple cake with fruit chunks and cream.",
        "stores": ["hyd-gachibowli-sweettruth", "hyd-hitech-city-cakezone2"],
    },
    {
        "id": "blueberry",
        "name": "Blueberry",
        "image": "blueberry.jpeg",
        "price": 689,
        "description": "Blueberry compote with soft vanilla sponge.",
        "stores": ["hyd-jubilee-theobroma", "hyd-banjara-karachi"],
    },
    {
        "id": "choco-truffle",
        "name": "Chocolate Truffle",
        "image": "truffle.jpeg",
        "price": 599,
        "description": "Rich chocolate layers with silky truffle ganache.",
        "stores": ["hyd-madhapur-justbake", "bakingo", "cakezone"],
    },
    {
        "id": "strawberry",
        "name": "Strawberry",
        "image": "strawberry.jpeg",
        "price": 559,
        "description": "Fresh strawberry cream and vanilla sponge.",
        "stores": ["hyd-kondapur-citybakers", "hyd-gachibowli-sweettruth"],
    },
    {
        "id": "mango",
        "name": "Mango",
        "image": "mango.jpeg",
        "price": 599,
        "description": "Seasonal mango cream delight.",
        "stores": ["hyd-hitech-city-cakezone2", "brown-bear"],
    },
    {
        "id": "oreo",
        "name": "Oreo Crunch",
        "image": "oreo.jpeg",
        "price": 619,
        "description": "Chocolate sponge with Oreo bits and cream.",
        "stores": ["hyd-jubilee-theobroma", "bakingo"],
    },
]
