import math


def fake_geocode(addr: str, city_hint: str = ""):
    """Deterministically derive a pseudo lat/lon for an address without external APIs.
    Centers around major Indian cities if hinted; otherwise near Hyderabad.
    """
    base = {
        'Bengaluru': (12.9716, 77.5946),
        'Hyderabad': (17.3850, 78.4867),
        'Mumbai': (19.0760, 72.8777),
        'Delhi': (28.6139, 77.2090),
    }.get(city_hint or '', (17.3850, 78.4867))
    h = abs(hash(addr)) % 10000
    dlat = ((h % 200) - 100) / 10000.0
    dlon = (((h // 200) % 200) - 100) / 10000.0
    return base[0] + dlat, base[1] + dlon


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two points on Earth in kilometers."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c
