import json

with open(r"D:\prj\amp2026\website\data\seattle-data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Manual fixes for addresses Nominatim couldn't parse
fixes = {
    "Daawat Indian Grill & Bar": (47.6128, -122.3288),   # 9th & Pike
    "Din Tai Fung": (47.6125, -122.3363),                 # Pacific Place, 600 Pine St
    "Shuckers": (47.6065, -122.3350),                     # Fairmont Olympic, 411 University
}

for d in data["dining"]:
    if d["name"] in fixes:
        lat, lng = fixes[d["name"]]
        d["latitude"] = lat
        d["longitude"] = lng
        print("Fixed:", d["name"])

with open(r"D:\prj\amp2026\website\data\seattle-data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print("Done")
