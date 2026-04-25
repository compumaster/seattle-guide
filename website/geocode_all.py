"""Add lat/lng coordinates to day trips, family activities, shopping, entertainment, and coffee/bars."""
import json, time, urllib.request, urllib.parse

DATA = r"D:\prj\amp2026\website\data\seattle-data.json"

with open(DATA, "r", encoding="utf-8") as f:
    data = json.load(f)

def geocode(address):
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

def process_list(items, label):
    print(f"\n=== {label} ===")
    fixed = 0
    for item in items:
        addr = item.get("address", "")
        if not addr:
            print(f"  SKIP (no address): {item['name']}")
            continue
        # Clean address of parenthetical notes
        clean_addr = addr.split("(")[0].strip().rstrip(",")
        if "latitude" in item and item["latitude"]:
            # Check if it's one of our manual estimates (round numbers)
            lat_str = str(item["latitude"])
            if len(lat_str.split(".")[-1]) <= 4:
                # Likely a manual estimate, re-geocode
                pass
            else:
                print(f"  SKIP (already geocoded): {item['name']}")
                continue
        time.sleep(1.1)
        lat, lng = geocode(clean_addr)
        if lat and lng:
            item["latitude"] = round(lat, 6)
            item["longitude"] = round(lng, 6)
            fixed += 1
            print(f"  ✓ {item['name']}: ({lat:.6f},{lng:.6f})")
        else:
            print(f"  ✗ {item['name']}: failed for '{clean_addr}'")
    return fixed

total = 0
total += process_list(data["attractions"]["dayTrips"], "DAY TRIPS")
total += process_list(data["familyActivities"], "FAMILY ACTIVITIES")
total += process_list(data["shopping"], "SHOPPING")
total += process_list(data["entertainment"], "ENTERTAINMENT")
total += process_list(data["coffeeAndBars"], "COFFEE & BARS")

print(f"\nTotal geocoded: {total}")

with open(DATA, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print("Saved!")
