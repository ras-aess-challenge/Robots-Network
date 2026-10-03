import math

# Anchor point: where the Writer's local (0, 0) sits in the real world.
# Replace with your actual deployment site if you have one (e.g. ESPRIT campus).
ANCHOR_LAT = 36.8065   # Tunis, as a placeholder
ANCHOR_LON = 10.1815

EARTH_RADIUS_M = 6378137.0  # meters (WGS84 equatorial radius)

def local_to_gps(x, y, anchor_lat=ANCHOR_LAT, anchor_lon=ANCHOR_LON):
    """
    Converts a local (x, y) offset in meters to a real-world GPS coordinate.
    x = east-west offset (meters), y = north-south offset (meters).
    Uses the equirectangular approximation — accurate enough for short
    distances (a few km), which fits this challenge's scale.
    """
    delta_lat = (y / EARTH_RADIUS_M) * (180 / math.pi)
    delta_lon = (x / (EARTH_RADIUS_M * math.cos(math.radians(anchor_lat)))) * (180 / math.pi)

    return {
        "lat": anchor_lat + delta_lat,
        "lon": anchor_lon + delta_lon
    }


if __name__ == "__main__":
    # Test 1: the anchor itself — (0,0) must return exactly the anchor point
    result = local_to_gps(0, 0)
    print(f"(0, 0) -> lat={result['lat']:.6f}, lon={result['lon']:.6f}")

    # Test 2: a realistic beacon position from our Writer (10.5, 0.0)
    result = local_to_gps(10.5, 0)
    print(f"(10.5, 0) -> lat={result['lat']:.6f}, lon={result['lon']:.6f}")

    # Test 3: a larger offset, to sanity-check it doesn't blow up
    result = local_to_gps(500, 300)
    print(f"(500, 300) -> lat={result['lat']:.6f}, lon={result['lon']:.6f}")