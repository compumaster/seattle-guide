import json

with open(r"D:\prj\amp2026\website\data\seattle-data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Walkable attraction coordinates (lat, lng)
attraction_coords = {
    "Pike Place Market": (47.6097, -122.3422),
    "Seattle Art Museum (SAM)": (47.6073, -122.3380),
    "Seattle Waterfront & Pier 57": (47.6060, -122.3402),
    "Seattle Great Wheel": (47.6060, -122.3423),
    "Pioneer Square": (47.6020, -122.3340),
    "Bill Speidel's Underground Tour": (47.6022, -122.3335),
    "Capitol Hill": (47.6253, -122.3222),
    "Olympic Sculpture Park": (47.6165, -122.3553),
    "Space Needle": (47.6205, -122.3493),
    "Chihuly Garden and Glass": (47.6206, -122.3505),
    "Museum of Pop Culture (MoPOP)": (47.6215, -122.3481),
    "Seattle Aquarium": (47.6075, -122.3430),
    "Kerry Park": (47.6295, -122.3600),
    "Freeway Park": (47.6110, -122.3300),
    "Bill & Melinda Gates Foundation Discovery Center": (47.6238, -122.3502),
    "Pacific Science Center": (47.6192, -122.3516),
}

# Dining coordinates
dining_coords = {
    "Bombo Italian Kitchen": (47.6135, -122.3280),
    "Alder & Ash": (47.6130, -122.3340),
    "Daawat Indian Grill & Bar": (47.6132, -122.3275),
    "Wild Ginger": (47.6090, -122.3380),
    "The Capital Grille": (47.6088, -122.3368),
    "Din Tai Fung": (47.6125, -122.3363),
    "Purple Cafe and Wine Bar": (47.6078, -122.3370),
    "Japonessa Sushi Cocina": (47.6082, -122.3420),
    "Serious Pie": (47.6145, -122.3410),
    "Pike Place Chowder": (47.6101, -122.3424),
    "Matt's in the Market": (47.6094, -122.3416),
    "Metropolitan Grill": (47.6045, -122.3360),
    "Shuckers": (47.6062, -122.3345),
    "Taylor Shellfish Oyster Bar": (47.6245, -122.3478),
    "Canlis": (47.6430, -122.3470),
    "Beecher's Handmade Cheese": (47.6098, -122.3425),
}

# Apply to attractions
for a in data["attractions"]["walkable"]:
    if a["name"] in attraction_coords:
        a["latitude"], a["longitude"] = attraction_coords[a["name"]]

# Apply to dining (exact or partial match)
for d in data["dining"]:
    if d["name"] in dining_coords:
        d["latitude"], d["longitude"] = dining_coords[d["name"]]
    else:
        for k, v in dining_coords.items():
            if k.lower() in d["name"].lower() or d["name"].lower() in k.lower():
                d["latitude"], d["longitude"] = v
                break

# Report
wa_with = sum(1 for a in data["attractions"]["walkable"] if "latitude" in a)
di_with = sum(1 for d in data["dining"] if "latitude" in d)
print(f"Attractions with coords: {wa_with}/{len(data['attractions']['walkable'])}")
print(f"Dining with coords: {di_with}/{len(data['dining'])}")

for a in data["attractions"]["walkable"]:
    if "latitude" not in a:
        print(f"  MISSING attraction: {a['name']}")
for d in data["dining"]:
    if "latitude" not in d:
        print(f"  MISSING dining: {d['name']}")

with open(r"D:\prj\amp2026\website\data\seattle-data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Done!")
