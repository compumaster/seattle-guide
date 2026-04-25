import json, time, urllib.request, urllib.parse

def geocode(addr):
    params = urllib.parse.urlencode({"q": addr, "format": "json", "limit": 1, "countrycodes": "us"})
    url = f"https://nominatim.openstreetmap.org/search?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "SeattleGuide/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        r = json.loads(resp.read().decode())
        if r:
            return float(r[0]["lat"]), float(r[0]["lon"])
    return None, None

with open(r"D:\prj\seattle-guide\website\data\seattle-data.json", "r") as f:
    data = json.load(f)

for item in data["entertainment"]:
    if "latitude" not in item or not item.get("latitude"):
        addr = item.get("address", "")
        if addr:
            time.sleep(1.1)
            lat, lng = geocode(addr)
            if lat:
                item["latitude"] = round(lat, 6)
                item["longitude"] = round(lng, 6)
                print("Geocoded:", item["name"], lat, lng)

with open(r"D:\prj\seattle-guide\website\data\seattle-data.json", "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print("Done")
