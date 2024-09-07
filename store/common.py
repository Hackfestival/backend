import math

default_radius = 2

# Haversine formula to calculate distance between two points on the Earth
def haversine(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return default_radius

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Radius of the Earth in kilometers
    R = 6371
    distance = R * c
    return distance