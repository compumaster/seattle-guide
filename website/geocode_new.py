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

for a in data["attractions"]["walkable"]:
    if "latitude" not in a or not a.get("latitude"):
        addr = a.get("address", "").split("(")[0].strip()
        if addr:
            time.sleep(1.1)
            lat, lng = geocode(addr)
            if lat:
                a["latitude"] = round(lat, 6)
                a["longitude"] = round(lng, 6)
                print("Geocoded:", a["name"], lat, lng)
            else:
                print("FAILED:", a["name"])

with open(r"D:\prj\seattle-guide\website\data\seattle-data.json", "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print("Done")
