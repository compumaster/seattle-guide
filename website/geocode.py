"""Geocode all attractions and dining from their addresses using Nominatim."""
import json, time, urllib.request, urllib.parse

DATA = r"D:\prj\amp2026\website\data\seattle-data.json"

with open(DATA, "r", encoding="utf-8") as f:
    data = json.load(f)

def geocode(address):
    """Query Nominatim for lat/lng from address."""
    params = urllib.parse.urlencode({
        "q": address,
        "format": "json",
        "limit": 1,
        "countrycodes": "us",
    })
    url = f"https://nominatim.openstreetmap.org/search?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "SeattleGuide2026/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            results = json.loads(resp.read().decode())
            if results:
                return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception as e:
        print(f"  ERROR: {e}")
    return None, None

fixed = 0
total = 0

# Geocode walkable attractions
print("=== WALKABLE ATTRACTIONS ===")
for item in data["attractions"]["walkable"]:
    addr = item.get("address", "")
    if not addr or "Seattle" not in addr:
        print(f"  SKIP (no address): {item['name']}")
        continue
    total += 1
    time.sleep(1.1)  # Nominatim rate limit: 1 req/sec
    lat, lng = geocode(addr)
    if lat and lng:
        old_lat = item.get("latitude", "?")
        old_lng = item.get("longitude", "?")
        item["latitude"] = round(lat, 6)
        item["longitude"] = round(lng, 6)
        fixed += 1
        print(f"  ✓ {item['name']}: ({old_lat},{old_lng}) → ({lat:.6f},{lng:.6f})")
    else:
        print(f"  ✗ {item['name']}: geocode failed for '{addr}'")

# Geocode dining
print("\n=== DINING ===")
for item in data["dining"]:
    addr = item.get("address", "")
    if not addr:
        print(f"  SKIP (no address): {item['name']}")
        continue
    total += 1
    time.sleep(1.1)
    lat, lng = geocode(addr)
    if lat and lng:
        old_lat = item.get("latitude", "?")
        old_lng = item.get("longitude", "?")
        item["latitude"] = round(lat, 6)
        item["longitude"] = round(lng, 6)
        fixed += 1
        print(f"  ✓ {item['name']}: ({old_lat},{old_lng}) → ({lat:.6f},{lng:.6f})")
    else:
        print(f"  ✗ {item['name']}: geocode failed for '{addr}'")

print(f"\nGeocoded {fixed}/{total} addresses")

with open(DATA, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Saved!")
