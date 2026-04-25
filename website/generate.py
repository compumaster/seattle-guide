#!/usr/bin/env python3
"""
Generate the Welcome to Seattle website.
Reads data from seattle-data.json and produces index.html.
"""
import json, os

DATA_PATH = r"D:\prj\seattle-guide\website\data\seattle-data.json"
OUTPUT_PATH = r"D:\prj\seattle-guide\docs\index.html"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

def sort_key_dist(x):
    """Sort by best available time: walk > drive > ferry > transit, None last."""
    for k in ("walkingMinutes", "drivingMinutes", "ferryMinutes", "transitMinutes"):
        v = x.get(k)
        if v is not None:
            return v
    return 9999

def price_dots(tier):
    if tier == "Free":
        return '<span class="price-free">FREE</span>'
    count = tier.count("$") if tier else 0
    return '<span class="price-tier">' + ("$" * count) + '<span class="price-dim">' + ("$" * (3 - count)) + '</span></span>'

def walk_badge(item):
    wm = item.get("walkingMinutes")
    dm = item.get("drivingMinutes")
    fm = item.get("ferryMinutes")
    tm = item.get("transitMinutes")
    if wm == 0:
        return '<span class="badge badge-gold">📍 On-Site</span>'
    if wm is not None:
        return f'<span class="badge badge-blue">🚶 {wm} min walk</span>'
    if dm is not None:
        return f'<span class="badge badge-navy">🚗 {dm} min drive</span>'
    if fm is not None:
        return f'<span class="badge badge-navy">⛴️ {fm} min ferry</span>'
    if tm is not None:
        return f'<span class="badge badge-blue">🚇 {tm} min transit</span>'
    return ''

def must_see_badge(item):
    if item.get("mustSee"):
        return '<span class="badge badge-gold">⭐ Must See</span>'
    return ''

def new_badge():
    return '<span class="badge badge-new">NEW!</span>'

def card_html(item, extra_badges="", show_cuisine=False, show_category=False):
    name = item.get("name", "")
    desc = item.get("description", "")
    addr = item.get("address", "")
    website = item.get("website", "")
    tip = item.get("tip", "")
    note = item.get("note", "")
    cuisine = item.get("cuisine", "")
    category = item.get("category", "")
    pt = item.get("priceTier", "")
    lat = item.get("latitude", "")
    lng = item.get("longitude", "")
    
    data_attrs = f' data-lat="{lat}" data-lng="{lng}"' if lat and lng else ''
    dist = item.get("walkingMinutes") or item.get("drivingMinutes") or item.get("ferryMinutes") or item.get("transitMinutes") or 999
    data_attrs += f' data-name="{name}" data-distance="{dist}"'
    html = f'<div class="card"{data_attrs}>\n'
    html += f'  <button class="heart-btn" onclick="toggleFav(this)" aria-label="Favorite">♡</button>\n'
    html += f'  <div class="card-header">\n'
    html += f'    <h3 class="card-title">{name}</h3>\n'
    html += f'    <div class="card-badges">{walk_badge(item)} {must_see_badge(item)} {extra_badges}'
    if pt:
        html += f' {price_dots(pt)}'
    html += '</div>\n'
    if show_cuisine and cuisine:
        html += f'    <span class="cuisine-tag">{cuisine}</span>\n'
    if show_category and category:
        html += f'    <span class="category-tag">{category}</span>\n'
    html += f'  </div>\n'
    html += f'  <p class="card-desc">{desc}</p>\n'
    if tip:
        html += f'  <p class="card-tip">💡 {tip}</p>\n'
    if note:
        html += f'  <p class="card-note">📌 {note}</p>\n'
    if addr:
        html += f'  <p class="card-addr">📍 {addr}</p>\n'
    if website:
        html += f'  <a href="{website}" target="_blank" rel="noopener" class="card-link">Visit Website →</a>\n'
    html += '</div>\n'
    return html

# Build transport cards
def transport_card(t):
    icons = {"Link Light Rail": "🚇", "Link 2 Line": "🚇", "King County Metro Bus": "🚌",
             "Seattle Monorail": "🚝", "Rideshare (Uber/Lyft)": "🚗", "Taxis": "🚕",
             "Lime Bikes & Scooters": "🚲", "Washington State Ferries": "⛴️",
             "Water Taxi": "🚢", "Shuttle Express": "🚐"}
    mode = t.get("mode", "")
    icon = "🚏"
    for k, v in icons.items():
        if k.lower() in mode.lower():
            icon = v
            break
    is_new = "2 Line" in mode
    new_tag = ' <span class="badge badge-new">NEW!</span>' if is_new else ''
    cost = t.get("cost", "")
    desc = t.get("description", "")
    dur = t.get("duration", "")
    
    html = f'<div class="transport-card{"  transport-highlight" if is_new else ""}">\n'
    html += f'  <div class="transport-icon">{icon}</div>\n'
    html += f'  <div class="transport-info">\n'
    html += f'    <h4>{mode}{new_tag}</h4>\n'
    if cost:
        html += f'    <span class="transport-cost">{cost}</span>\n'
    if dur:
        html += f'    <span class="transport-dur">{dur}</span>\n'
    html += f'    <p>{desc}</p>\n'
    html += f'  </div>\n</div>\n'
    return html

# ─── Assemble the full HTML ───

weather = data["weather"]
venue = data["venue"]
hotel = data["headquarterHotel"]
event = data["event"]

# Section order — single source of truth for nav AND page layout
# Grouped: Essentials → Explore → Culture & Context → Reference
sections = [
    # Essentials
    ("home", "Home"),
    ("venue", "Venue & Hotel"),
    ("transport", "Weather & Transit"),
    ("practical", "Need to Know"),
    ("medical", "Medical"),
    ("dining", "Dining"),
    ("coffee", "Coffee & Bars"),
    ("shopping", "Shopping"),
    # Explore
    ("attractions", "Attractions"),
    ("daytrips", "Day Trips"),
    ("tours", "Tours"),
    ("entertainment", "Entertainment"),
    ("family", "Family"),
    ("seasonal", "Seasonal Events"),
    ("photospots", "Photo Spots"),
    # Culture & Context
    ("history", "History"),
    ("famous", "Famous Faces"),
    ("popculture", "On Screen"),
    ("geography", "Geography"),
    ("lifesciences", "Life Sciences"),
    # Reference
    ("insights", "Local Tips"),
    ("index", "Index"),
]

nav_links = "\n".join(f'<a href="#{sid}" class="nav-link">{label}</a>' for sid, label in sections)

# Dining cards
dining_cards = "\n".join(
    card_html(d, show_cuisine=True, 
              extra_badges=('<span class="badge badge-gold">📍 ON-SITE</span>' if d.get("walkingMinutes") == 0 else ''))
    for d in sorted(data["dining"], key=sort_key_dist)
)

# Walkable attraction cards
attraction_cards = "\n".join(
    card_html(a, show_category=True)
    for a in sorted(data["attractions"]["walkable"], key=sort_key_dist)
)

# Tour cards
tour_cards = "\n".join(card_html(t) for t in sorted(data.get("tours", []), key=sort_key_dist))

# Day trip cards
daytrip_cards = "\n".join(
    card_html(d, show_category=True,
              extra_badges=('<span class="badge badge-navy">🚗 Requires transport</span>' if d.get("requiresTransport") else ''))
    for d in sorted(data["attractions"]["dayTrips"], key=sort_key_dist)
)

# Transport cards
transport_cards = "\n".join(transport_card(t) for t in data["transportation"])

# Shopping cards
shopping_cards = "\n".join(card_html(s) for s in sorted(data["shopping"], key=sort_key_dist))

# Entertainment cards
entertainment_cards = "\n".join(card_html(e) for e in sorted(data["entertainment"], key=sort_key_dist))

# Coffee cards
coffee_cards = "\n".join(card_html(c) for c in sorted(data["coffeeAndBars"], key=sort_key_dist))

# Life sciences cards
lifesci_cards = "\n".join(
    f'''<div class="card card-lifesci">
  <h3 class="card-title">{ls["name"]}</h3>
  <span class="category-tag">{ls.get("category","")}</span>
  {f'<span class="neighborhood-tag">📍 {ls["neighborhood"]}</span>' if ls.get("neighborhood") else ""}
  <p class="card-desc">{ls["description"]}</p>
  {f'<p class="card-note">🔬 {ls["relevance"]}</p>' if ls.get("relevance") else ""}
  {f'<a href="{ls["website"]}" target="_blank" class="card-link">Learn More →</a>' if ls.get("website") else ""}
</div>'''
    for ls in data["lifeSciencesHeritage"]
)

# Family activity cards
family_cards = "\n".join(
    f'''<div class="card card-family" data-name="{fa["name"]}" data-distance="{fa.get("walkingMinutes") or fa.get("drivingMinutes") or fa.get("transitMinutes") or 999}">
  <div class="card-header">
    <h3 class="card-title">{fa["name"]}</h3>
    <div class="card-badges">
      {walk_badge(fa)} {price_dots(fa.get("priceTier",""))}
      {'<span class="badge badge-indoor">🏠 Indoor</span>' if fa.get("indoor") else '<span class="badge badge-outdoor">🌳 Outdoor</span>'}
      {f'<span class="badge badge-age">Ages: {fa["ageRange"]}</span>' if fa.get("ageRange") else ""}
    </div>
  </div>
  <p class="card-desc">{fa["description"]}</p>
  {f'<a href="{fa["website"]}" target="_blank" class="card-link">Plan Visit →</a>' if fa.get("website") else ""}
</div>'''
    for fa in sorted(data["familyActivities"], key=sort_key_dist)
)

# Seasonal events
seasonal_cards = "\n".join(
    f'''<div class="card card-seasonal">
  <h3 class="card-title">🎄 {se["name"]}</h3>
  <span class="category-tag">{se.get("category","")}</span>
  {f'<span class="badge badge-blue">📅 {se["dates"]}</span>' if se.get("dates") else ""}
  {price_dots(se.get("priceTier",""))}
  <p class="card-desc">{se["description"]}</p>
  {f'<p class="card-tip">💡 {se["tip"]}</p>' if se.get("tip") else ""}
  {f'<a href="{se["website"]}" target="_blank" class="card-link">Details →</a>' if se.get("website") else ""}
</div>'''
    for se in data["seasonalEvents"]
)

# Famous Faces
famous_cards = "\n".join(
    f'''<div class="card">
  <div class="card-header">
    <h3 class="card-title">{ff["name"]}</h3>
    <div class="card-badges"><span class="cuisine-tag">{ff["industry"]}</span> <span class="badge badge-blue">{ff["connection"]}</span></div>
  </div>
  <p class="card-desc">{ff["description"]}</p>
</div>'''
    for ff in data.get("famousFaces", [])
)

# Pop Culture
pop_tv = "\n".join(
    f'''<div class="card">
  <div class="card-header">
    <h3 class="card-title">📺 {p["title"]}</h3>
    <span class="category-tag">{p["type"]}</span>
  </div>
  <p class="card-desc">{p["description"]}</p>
</div>'''
    for p in data.get("popCulture", {}).get("television", [])
)
pop_film = "\n".join(
    f'''<div class="card">
  <div class="card-header">
    <h3 class="card-title">🎬 {p["title"]} ({p["year"]})</h3>
  </div>
  <p class="card-desc">{p["description"]}</p>
</div>'''
    for p in data.get("popCulture", {}).get("film", [])
)

# History
history_cards = "\n".join(
    f'''<div class="card" style="border-left:4px solid var(--gold);">
  <h3 class="card-title">{h["era"]}</h3>
  <p class="card-desc">{h["description"]}</p>
</div>'''
    for h in data.get("history", [])
)

# Geography — with images
geo_images = {
    "Mount Rainier": "https://images.unsplash.com/photo-1570302603871-0db6a1ee37c3?w=600&q=80",
    "Mount St. Helens": "https://images.unsplash.com/photo-1661833599314-098858d9507d?w=600&q=80",
    "The Cascade Range": "https://images.unsplash.com/photo-1640920205006-fdeade482d38?w=600&q=80",
    "Puget Sound": "https://images.unsplash.com/photo-1593985549158-90bf9d1f9ec2?w=600&q=80",
    "Olympic Mountains": "https://images.unsplash.com/photo-1660409343000-41911ec6525e?w=600&q=80",
    "Lake Washington & Lake Union": "https://images.unsplash.com/photo-1613417113853-1544a43eee7b?w=600&q=80",
    "Elliott Bay": "https://images.unsplash.com/photo-1573144279658-e2c26b572605?w=600&q=80",
    "The Ring of Fire": "https://images.unsplash.com/photo-1735744605821-e241a794f0a3?w=600&q=80",
}

def geo_card(g):
    img_url = geo_images.get(g["name"], "")
    img_html = ""
    if img_url:
        img_html = f'<div style="height:180px;overflow:hidden;margin:-1.5rem -1.5rem 1rem -1.5rem;"><img src="{img_url}" alt="{g["name"]}" style="width:100%;height:100%;object-fit:cover;" loading="lazy"></div>'
    return f'''<div class="card" style="border-left:4px solid var(--teal);overflow:hidden;">
  {img_html}
  <div class="card-header">
    <h3 class="card-title">{g["name"]}</h3>
    <span class="category-tag">{g["type"]}</span>
  </div>
  <p class="card-desc">{g["description"]}</p>
</div>'''

geo_cards = "\n".join(geo_card(g) for g in data.get("geography", []))

# Practical info
pinfo = data.get("practicalInfo", {})

def practical_section():
    html = ""
    # Veterans Day
    vd = pinfo.get("veteransDay", {})
    if vd:
        html += f'<div class="card" style="border-left:4px solid #1565C0;"><h3 class="card-title">{vd["title"]}</h3><p class="card-desc">{vd["content"]}</p>'
        if vd.get("link"):
            html += f'<a href="{vd["link"]}" target="_blank" class="card-link">Holiday Transit Schedule →</a>'
        html += '</div>\n'
    # Safety
    sf = pinfo.get("safety", {})
    if sf:
        tips_html = "".join(f"<li>{t}</li>" for t in sf.get("tips", []))
        html += f'<div class="card" style="border-left:4px solid #F57F17;"><h3 class="card-title">{sf["title"]}</h3><ul style="padding-left:1.2rem;font-size:0.9rem;color:#555;line-height:1.8;">{tips_html}</ul></div>\n'
    # Accessibility
    acc = pinfo.get("accessibility", {})
    if acc:
        tips_html = "".join(f"<li>{t}</li>" for t in acc.get("tips", []))
        html += f'<div class="card" style="border-left:4px solid var(--teal);"><h3 class="card-title">{acc["title"]}</h3><p class="card-desc">{acc["content"]}</p><ul style="padding-left:1.2rem;font-size:0.9rem;color:#555;line-height:1.8;">{tips_html}</ul></div>\n'
    # Childcare
    cc = pinfo.get("childcare", {})
    if cc:
        svcs = "".join(f'<li><strong>{s["name"]}</strong> — {s["note"]} <a href="{s["website"]}" target="_blank">Website →</a></li>' for s in cc.get("services", []))
        html += f'<div class="card" style="border-left:4px solid #7B1FA2;"><h3 class="card-title">{cc["title"]}</h3><p class="card-desc">{cc["content"]}</p><ul style="padding-left:1.2rem;font-size:0.9rem;color:#555;line-height:1.8;">{svcs}</ul><p class="card-tip">💡 {cc.get("tip","")}</p></div>\n'
    return html

practical_cards = practical_section()

# Medical facility cards (own section)
med = pinfo.get("medical", {})
medical_cards = ""
for fac in med.get("facilities", []):
    medical_cards += f'''<div class="card" style="border-left:4px solid #E91E63;">
  <div class="card-header">
    <h3 class="card-title">{fac["name"]}</h3>
    <div class="card-badges"><span class="badge badge-blue">{fac["type"]}</span></div>
  </div>
  <p class="card-desc">{fac.get("note","")}</p>
  <p class="card-addr">📍 {fac["address"]}</p>
  <p class="card-addr">📞 {fac["phone"]} | 🚶 {fac["distance"]}</p>
</div>\n'''
ph = med.get("pharmacy", {})
medical_cards += f'''<div class="card" style="border-left:4px solid #7B1FA2;">
  <h3 class="card-title">💊 Pharmacies</h3>
  <p class="card-desc"><strong>Walkable:</strong> {ph.get("walkable","")}</p>
  <p class="card-desc"><strong>24-hour:</strong> {ph.get("allNight","")}</p>
  <p class="card-tip">💡 {med.get("tip","")}</p>
</div>\n'''

# Photo spots
photo_cards = "\n".join(
    f'''<div class="card" style="border-left:4px solid #E91E63;">
  <div class="card-header">
    <h3 class="card-title">📸 {ps["name"]}</h3>
    <div class="card-badges">
      <span class="badge badge-blue">🕐 {ps["bestTime"]}</span>
      {f'<span class="badge badge-blue">🚶 {ps["walkingMinutes"]} min walk</span>' if ps.get("walkingMinutes") else f'<span class="badge badge-navy">🚗 {ps.get("drivingMinutes","")} min drive</span>'}
    </div>
  </div>
  <p class="card-desc">{ps["tip"]}</p>
  <p class="card-tip">📷 Pro tip: {ps["pro"]}</p>
</div>'''
    for ps in data.get("photoSpots", [])
)

# Local insights
insights = data.get("localInsights", {})
insight_boxes = "\n".join(
    f'<div class="insight-box"><h4>{k.replace("lifeSciences","🧬 Life Sciences").replace("coffeeCapital","☕ Coffee Capital").replace("grunge","🎸 Grunge Heritage").replace("techHub","💻 Tech Hub").replace("pikePlace","🐟 Pike Place Market").replace("safetyTip","🛡️ Safety")}</h4><p>{v}</p></div>'
    for k, v in insights.items()
)

# Price key
price_key = data.get("priceKey", {})
price_legend = " | ".join(f'<strong>{k}</strong> = {v}' for k, v in price_key.items())

# ─── Map marker data as JSON for Leaflet ───
import html as html_mod

venue_lat = data["venue"]["latitude"]
venue_lng = data["venue"]["longitude"]

def markers_json(items):
    markers = []
    for i, item in enumerate(items):
        if "latitude" in item and "longitude" in item:
            markers.append({
                "idx": i,
                "name": item["name"],
                "lat": item["latitude"],
                "lng": item["longitude"],
                "walk": item.get("walkingMinutes", ""),
                "price": item.get("priceTier", ""),
                "cuisine": item.get("cuisine", item.get("category", "")),
            })
    return json.dumps(markers)

dining_sorted = sorted(data["dining"], key=sort_key_dist)
attractions_sorted = sorted(data["attractions"]["walkable"], key=sort_key_dist)

dining_markers_json = markers_json(dining_sorted)
attraction_markers_json = markers_json(attractions_sorted)

daytrips_sorted = sorted(data["attractions"]["dayTrips"], key=sort_key_dist)
daytrip_markers_json = markers_json(daytrips_sorted)
family_markers_json = markers_json(data["familyActivities"])
shopping_sorted = sorted(data["shopping"], key=sort_key_dist)
shopping_markers_json = markers_json(shopping_sorted)
entertainment_markers_json = markers_json(data["entertainment"])
tours_sorted = sorted(data.get("tours", []), key=sort_key_dist)
tour_markers_json = markers_json(tours_sorted)

# Trivia data
trivia_data = data.get("trivia", [])
trivia_json = json.dumps(trivia_data)

# Lunch picker data
lunch_data = []
for d in dining_sorted:
    lunch_data.append({
        "name": d["name"],
        "cuisine": d.get("cuisine", ""),
        "walk": d.get("walkingMinutes"),
        "drive": d.get("drivingMinutes"),
        "price": d.get("priceTier", ""),
        "desc": d.get("description", ""),
    })
lunch_json = json.dumps(lunch_data)
coffee_sorted = sorted(data["coffeeAndBars"], key=sort_key_dist)
coffee_markers_json = markers_json(coffee_sorted)

# ─── Build location index ───
all_locations = []
def add_to_index(items, section_name, section_id):
    for item in items:
        name = item.get("name", "")
        addr = item.get("address", "")
        wm = item.get("walkingMinutes")
        dm = item.get("drivingMinutes") or item.get("ferryMinutes") or item.get("transitMinutes")
        dist_label = f"{wm} min walk" if wm is not None and wm > 0 else ("On-Site" if wm == 0 else (f"{dm} min" if dm else ""))
        website = item.get("website", "")
        all_locations.append((name, section_name, section_id, addr, dist_label, website))

add_to_index(dining_sorted, "Dining", "dining")
add_to_index(attractions_sorted, "Attractions", "attractions")
add_to_index(daytrips_sorted, "Day Trips", "daytrips")
add_to_index(data["familyActivities"], "Family", "family")
add_to_index(shopping_sorted, "Shopping", "shopping")
add_to_index(data["entertainment"], "Entertainment", "entertainment")
add_to_index(tours_sorted, "Tours", "tours")
add_to_index(coffee_sorted, "Coffee & Bars", "coffee")

all_locations.sort(key=lambda x: x[0].lstrip("The "))

def index_row(loc):
    link_cell = f'<a href="{loc[5]}" target="_blank">🔗</a>' if loc[5] else ""
    return (f'<tr><td class="idx-name">{loc[0]}</td>'
            f'<td><span class="idx-section" data-section="{loc[2]}">{loc[1]}</span></td>'
            f'<td class="idx-dist">{loc[4]}</td>'
            f'<td class="idx-addr">{loc[3]}</td>'
            f'<td>{link_cell}</td></tr>')

index_rows = "\n".join(index_row(loc) for loc in all_locations)

# ─── HTML Template ───
html = f'''<!DOCTYPE html>
<!-- TEMPLATE: Welcome to [CITY] -->
<!-- TEMPLATE: Replace seattle-data.json with new city data to regenerate -->
<!-- Generated from seattle-data.json — all content is data-driven -->
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Welcome to Seattle — Seattle Guide 2026</title>
<meta name="description" content="Your guide to Seattle, November 10-14, 2026. Dining, attractions, day trips, and local insights centered on the Seattle Convention Center.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
/* ─── CSS Variables (Design Language) ─── */
:root {{
  --navy: #1B2A4A;
  --sky: #29B6F6;
  --gold: #D4A017;
  --teal: #00ACC1;
  --charcoal: #333333;
  --light-gray: #E8E8E8;
  --white: #FFFFFF;
  --rose: #B5294E;
  --success: #4CAF50;
  --gradient-hero: linear-gradient(135deg, #FF6B35 0%, #C23B72 30%, #7B2D8E 60%, #1B2A4A 100%);
}}

/* ─── Reset & Base ─── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; scroll-padding-top: 70px; }}
body {{ font-family: 'Roboto', Arial, sans-serif; color: var(--charcoal); line-height: 1.6; background: var(--white); }}
a {{ color: var(--sky); text-decoration: none; transition: color 0.2s; }}
a:hover {{ color: var(--teal); }}
img {{ max-width: 100%; height: auto; }}

/* ─── Navigation ─── */
.navbar {{
  position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
  background: var(--navy); padding: 0 2rem; height: 64px;
  display: flex; align-items: center; justify-content: space-between;
  box-shadow: 0 2px 10px rgba(0,0,0,0.3);
}}
.nav-brand {{
  font-weight: 900; font-size: 1.4rem; color: var(--white); letter-spacing: 1px;
  flex-shrink: 0; white-space: nowrap;
}}
.nav-brand span {{ color: var(--gold); }}
.nav-links {{ display: none; position: absolute; top: 64px; left: 0; right: 0;
  background: var(--navy); flex-direction: column; padding: 1rem; z-index: 1100;
  max-height: 80vh; overflow-y: auto; box-shadow: 0 8px 30px rgba(0,0,0,0.4); }}
.nav-links.active {{ display: flex; }}
.nav-link {{
  color: rgba(255,255,255,0.85); padding: 0.5rem 0.8rem; font-size: 0.82rem;
  font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;
  border-radius: 4px; transition: all 0.2s;
}}
.nav-link:hover {{ color: var(--white); background: rgba(255,255,255,0.1); }}
.hamburger {{
  display: block; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.3);
  color: var(--gold); padding: 0.4rem 1rem; border-radius: 4px;
  font-size: 0.85rem; font-weight: 700; cursor: pointer; letter-spacing: 1px;
  font-family: 'Roboto', sans-serif; text-transform: uppercase;
}}

/* ─── Hero ─── */
.hero {{
  margin-top: 64px; min-height: 85vh; display: flex; align-items: center;
  justify-content: center; text-align: center; position: relative; overflow: hidden;
  background: var(--gradient-hero);
}}
.hero::before {{
  content: ''; position: absolute; inset: 0;
  background: url('https://images.unsplash.com/photo-1502175353174-a7a70e73b362?w=1920&q=80') center/cover;
  opacity: 0.3;
}}
.hero-content {{
  position: relative; z-index: 2; padding: 2rem; max-width: 900px;
}}
.hero h1 {{
  font-size: 3.5rem; font-weight: 900; color: var(--white);
  letter-spacing: 4px; text-transform: uppercase; margin-bottom: 0.5rem;
  text-shadow: 2px 2px 8px rgba(0,0,0,0.5);
}}
.hero .subtitle {{
  font-size: 1.3rem; color: rgba(255,255,255,0.9); margin-bottom: 2rem;
  font-weight: 400;
}}
.hero-buttons {{ display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }}
.btn {{
  display: inline-block; padding: 0.9rem 2rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 1px; font-size: 0.95rem;
  border: none; cursor: pointer; transition: all 0.3s; border-radius: 3px;
}}
.btn-primary {{ background: var(--sky); color: var(--white); }}
.btn-primary:hover {{ background: var(--teal); color: var(--white); }}
.btn-outline {{ background: transparent; color: var(--white); border: 2px solid var(--white); }}
.btn-outline:hover {{ background: var(--white); color: var(--navy); }}

/* ─── Info Bar ─── */
.info-bar {{
  background: var(--navy); padding: 1rem 2rem; display: flex;
  justify-content: center; flex-wrap: wrap; gap: 2rem;
}}
.info-item {{ color: rgba(255,255,255,0.9); font-size: 0.9rem; white-space: nowrap; }}
.info-item strong {{ color: var(--gold); }}

/* ─── Sections ─── */
.section {{
  padding: 4rem 2rem; max-width: 1300px; margin: 0 auto;
}}
.section-header {{
  text-align: center; margin-bottom: 3rem;
}}
.section-header h2 {{
  font-size: 2rem; font-weight: 900; text-transform: uppercase;
  letter-spacing: 2px; color: var(--navy); margin-bottom: 0.5rem;
}}
.section-header .section-line {{
  width: 60px; height: 4px; background: var(--gold); margin: 0.8rem auto;
}}
.section-header p {{ color: #666; font-size: 1.05rem; max-width: 700px; margin: 0 auto; }}

.section-alt {{ background: #F8F9FA; }}
.section-navy {{ background: var(--navy); }}
.section-navy .section-header h2 {{ color: var(--white); }}
.section-navy .section-header p {{ color: rgba(255,255,255,0.7); }}

/* ─── Card Grid ─── */
.card-grid {{
  display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}}
.card {{
  background: var(--white); border-radius: 8px; padding: 1.5rem;
  border: 1px solid #E0E0E0; transition: transform 0.2s, box-shadow 0.2s;
  display: flex; flex-direction: column;
}}
.card:hover {{ transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,0,0,0.1); }}
.card-header {{ margin-bottom: 0.8rem; }}
.card-title {{ font-size: 1.15rem; font-weight: 700; color: var(--navy); margin-bottom: 0.4rem; }}
.card-badges {{ display: flex; flex-wrap: wrap; gap: 0.4rem; align-items: center; }}
.card-desc {{ font-size: 0.9rem; color: #555; flex: 1; margin-bottom: 0.6rem; }}
.card-tip {{ font-size: 0.85rem; color: var(--teal); font-style: italic; margin-bottom: 0.4rem; }}
.card-note {{ font-size: 0.85rem; color: var(--rose); margin-bottom: 0.4rem; }}
.card-addr {{ font-size: 0.8rem; color: #888; margin-bottom: 0.5rem; }}
.card-link {{
  font-size: 0.85rem; font-weight: 700; color: var(--sky);
  text-transform: uppercase; letter-spacing: 0.5px; margin-top: auto;
}}

/* ─── Badges ─── */
.badge {{
  display: inline-block; padding: 0.2rem 0.6rem; border-radius: 12px;
  font-size: 0.75rem; font-weight: 700; white-space: nowrap;
}}
.badge-blue {{ background: #E3F2FD; color: #1565C0; }}
.badge-navy {{ background: #E8EAF6; color: var(--navy); }}
.badge-gold {{ background: #FFF8E1; color: #F57F17; }}
.badge-new {{ background: var(--rose); color: white; animation: pulse 2s infinite; }}
.badge-indoor {{ background: #E8F5E9; color: #2E7D32; }}
.badge-outdoor {{ background: #FFF3E0; color: #E65100; }}
.badge-age {{ background: #F3E5F5; color: #7B1FA2; }}
@keyframes pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0.7; }} }}

.cuisine-tag {{
  display: inline-block; background: var(--sky); color: white;
  padding: 0.15rem 0.6rem; border-radius: 12px; font-size: 0.75rem; font-weight: 700;
}}
.category-tag {{
  display: inline-block; background: var(--navy); color: white;
  padding: 0.15rem 0.6rem; border-radius: 12px; font-size: 0.75rem; font-weight: 700;
}}
.neighborhood-tag {{
  display: inline-block; background: #E8F5E9; color: #2E7D32;
  padding: 0.15rem 0.6rem; border-radius: 12px; font-size: 0.75rem;
}}

.price-tier {{ font-weight: 700; color: var(--gold); font-size: 0.9rem; }}
.price-dim {{ opacity: 0.25; }}
.price-free {{ font-weight: 700; color: var(--success); font-size: 0.8rem; }}

/* ─── Transport Grid ─── */
.transport-grid {{
  display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem;
}}
.transport-card {{
  display: flex; gap: 1rem; background: var(--white); border-radius: 8px;
  padding: 1.2rem; border: 1px solid #E0E0E0; transition: all 0.2s;
}}
.transport-card:hover {{ box-shadow: 0 4px 15px rgba(0,0,0,0.08); }}
.transport-highlight {{ border: 2px solid var(--rose); background: #FFF5F5; }}
.transport-icon {{ font-size: 2rem; flex-shrink: 0; }}
.transport-info h4 {{ font-size: 0.95rem; color: var(--navy); margin-bottom: 0.3rem; }}
.transport-cost {{ display: inline-block; background: #E8F5E9; color: #2E7D32; padding: 0.1rem 0.5rem; border-radius: 8px; font-size: 0.8rem; font-weight: 700; margin-right: 0.5rem; }}
.transport-dur {{ font-size: 0.8rem; color: #888; }}
.transport-info p {{ font-size: 0.82rem; color: #666; margin-top: 0.3rem; }}

/* ─── Venue Cards ─── */
.venue-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 1.5rem; }}
.venue-card {{
  background: var(--white); border-radius: 8px; overflow: hidden;
  border: 1px solid #E0E0E0;
}}
.venue-card-header {{
  background: var(--navy); padding: 1rem 1.5rem; color: var(--white);
}}
.venue-card-header h3 {{ font-weight: 700; font-size: 1.1rem; }}
.venue-card-body {{ padding: 1.5rem; }}
.venue-card-body p {{ font-size: 0.9rem; color: #555; margin-bottom: 0.5rem; }}
.venue-card-body .venue-detail {{ display: flex; gap: 0.5rem; align-items: baseline; margin-bottom: 0.3rem; }}
.venue-card-body .venue-label {{ font-weight: 700; color: var(--navy); font-size: 0.85rem; min-width: 80px; }}

/* ─── Weather ─── */
.weather-transport {{ display: grid; grid-template-columns: 1fr 2fr; gap: 2rem; }}
.weather-card {{
  background: linear-gradient(135deg, #1B2A4A, #2D4A7A); border-radius: 12px;
  padding: 2rem; color: white; text-align: center;
}}
.weather-card .temp {{ font-size: 3rem; font-weight: 900; }}
.weather-card .temp-small {{ font-size: 1rem; opacity: 0.8; }}
.weather-details {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: 1rem; }}
.weather-detail {{ background: rgba(255,255,255,0.1); padding: 0.5rem; border-radius: 6px; font-size: 0.8rem; }}
.weather-tip {{ background: rgba(212,160,23,0.2); border: 1px solid var(--gold); padding: 0.8rem; border-radius: 6px; margin-top: 1rem; font-size: 0.85rem; color: var(--gold); }}

/* ─── Life Sciences ─── */
.card-lifesci {{ border-left: 4px solid var(--gold); }}
.card-family {{ border-left: 4px solid var(--teal); }}
.card-seasonal {{ border-left: 4px solid var(--rose); }}

/* ─── Insight Boxes ─── */
.insight-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }}
.insight-box {{
  background: var(--white); border-radius: 8px; padding: 1.2rem;
  border: 1px solid var(--gold); border-top: 3px solid var(--gold);
}}
.insight-box h4 {{ font-size: 0.95rem; color: var(--navy); margin-bottom: 0.4rem; }}
.insight-box p {{ font-size: 0.85rem; color: #555; }}

/* ─── Price Legend ─── */
.price-legend {{
  text-align: center; background: #F8F9FA; padding: 1.5rem;
  border-radius: 8px; font-size: 0.9rem; color: #666;
}}

/* ─── Footer ─── */
.footer {{
  background: var(--navy); color: rgba(255,255,255,0.7); text-align: center;
  padding: 3rem 2rem;
}}
.footer h3 {{ color: var(--white); font-size: 1.3rem; margin-bottom: 0.3rem; }}
.footer h3 span {{ color: var(--gold); }}
.footer p {{ font-size: 0.85rem; margin-bottom: 0.3rem; }}
.footer a {{ color: var(--sky); }}

/* ─── Back to Top ─── */
.back-to-top {{
  position: fixed; bottom: 2rem; right: 2rem; width: 48px; height: 48px;
  background: var(--sky); color: white; border: none; border-radius: 50%;
  font-size: 1.2rem; cursor: pointer; opacity: 0; transition: all 0.3s;
  z-index: 999; box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}}
.back-to-top.visible {{ opacity: 1; }}
.back-to-top:hover {{ background: var(--teal); transform: scale(1.1); }}

/* ─── Scroll Animations ─── */
.fade-in {{ opacity: 0; transform: translateY(20px); transition: all 0.6s ease-out; }}
.fade-in.visible {{ opacity: 1; transform: translateY(0); }}

/* ─── Responsive ─── */
@media (max-width: 900px) {{
  .hero h1 {{ font-size: 2.2rem; }}
  .card-grid {{ grid-template-columns: 1fr; }}
  .weather-transport {{ grid-template-columns: 1fr; }}
  .venue-grid {{ grid-template-columns: 1fr; }}
  .info-bar {{ flex-direction: column; gap: 0.5rem; align-items: center; }}
}}
@media (max-width: 600px) {{
  .hero h1 {{ font-size: 1.7rem; letter-spacing: 2px; }}
  .section {{ padding: 2rem 1rem; }}
  .transport-grid {{ grid-template-columns: 1fr; }}
  .navbar {{ padding: 0 0.5rem; height: 56px; }}
  .nav-brand {{ font-size: 1rem; }}
  .hamburger {{ padding: 0.3rem 0.5rem; font-size: 0.7rem; letter-spacing: 0; }}
  .fav-nav-btn {{ padding: 0.3rem 0.5rem; font-size: 0.7rem; }}
  .nav-links {{ top: 56px; }}
}}

/* ─── Maps ─── */
.map-container {{
  width: 100%; height: 420px; border-radius: 12px; overflow: hidden;
  border: 2px solid var(--gold); margin-bottom: 2rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}}
.map-section-layout {{
  display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;
}}
.map-section-layout .card-grid {{
  max-height: 600px; overflow-y: auto; padding-right: 0.5rem;
  grid-template-columns: 1fr;
}}
.map-section-layout .card-grid::-webkit-scrollbar {{ width: 6px; }}
.map-section-layout .card-grid::-webkit-scrollbar-thumb {{ background: var(--gold); border-radius: 3px; }}
.card.card-active {{ border: 2px solid var(--sky); box-shadow: 0 0 15px rgba(41,182,246,0.3); transform: translateY(-2px); }}
.map-wide {{ width: 100%; height: 350px; border-radius: 12px; overflow: hidden; border: 2px solid var(--gold); margin-bottom: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
.sort-controls {{ display: flex; gap: 0.5rem; justify-content: center; margin-bottom: 1.5rem; flex-wrap: wrap; }}
.sort-btn {{ padding: 0.4rem 1rem; border: 2px solid var(--navy); background: var(--white); color: var(--navy); font-weight: 700; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px; border-radius: 20px; cursor: pointer; transition: all 0.2s; }}
.sort-btn:hover {{ background: var(--navy); color: var(--white); }}
.sort-btn.active {{ background: var(--navy); color: var(--gold); }}
@keyframes fadeSlideIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

/* ─── Location Index ─── */
.index-table-wrap {{ overflow-x: auto; }}
.index-table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
.index-table th {{ background: var(--navy); color: var(--white); padding: 0.7rem 1rem; text-align: left; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; font-size: 0.75rem; position: sticky; top: 0; cursor: pointer; }}
.index-table th:hover {{ background: #2a3d66; }}
.index-table td {{ padding: 0.5rem 1rem; border-bottom: 1px solid #E8E8E8; }}
.index-table tr:hover {{ background: #F5F9FF; }}
.idx-name {{ font-weight: 700; color: var(--navy); white-space: nowrap; }}
.idx-addr {{ color: #888; font-size: 0.8rem; }}
.idx-dist {{ white-space: nowrap; color: var(--teal); font-weight: 600; }}
.idx-section {{ display: inline-block; padding: 0.15rem 0.5rem; border-radius: 10px; font-size: 0.7rem; font-weight: 700; background: #E3F2FD; color: #1565C0; }}
.idx-section[data-section="dining"] {{ background: #FCE4EC; color: #B5294E; }}
.idx-section[data-section="attractions"] {{ background: #E3F2FD; color: #1565C0; }}
.idx-section[data-section="daytrips"] {{ background: #E8F5E9; color: #2E7D32; }}
.idx-section[data-section="family"] {{ background: #F3E5F5; color: #7B1FA2; }}
.idx-section[data-section="shopping"] {{ background: #FFF3E0; color: #E65100; }}
.idx-section[data-section="entertainment"] {{ background: #FCE4EC; color: #C2185B; }}
.idx-section[data-section="coffee"] {{ background: #EFEBE9; color: #4E342E; }}
.index-search {{ width: 100%; max-width: 400px; padding: 0.6rem 1rem; border: 2px solid var(--navy); border-radius: 8px; font-size: 0.9rem; margin-bottom: 1rem; outline: none; }}
.index-search:focus {{ border-color: var(--sky); box-shadow: 0 0 0 3px rgba(41,182,246,0.2); }}
.index-count {{ font-size: 0.85rem; color: #888; margin-bottom: 0.5rem; }}

/* ─── Trivia ─── */
.trivia-btn {{
  background: var(--gold); color: var(--navy); border: none; padding: 0.4rem 1rem;
  border-radius: 4px; font-size: 0.85rem; font-weight: 700; cursor: pointer;
  letter-spacing: 1px; font-family: 'Roboto', sans-serif; text-transform: uppercase;
}}
.trivia-btn:hover {{ background: #e6b800; }}
.trivia-overlay {{
  display: none; position: fixed; inset: 0; z-index: 2000;
  background: rgba(0,0,0,0.85); justify-content: center; align-items: center;
  flex-direction: column; padding: 1rem;
}}
.trivia-overlay.active {{ display: flex; }}
.trivia-close {{
  position: absolute; top: 1rem; right: 1.5rem; background: none; border: none;
  color: white; font-size: 2rem; cursor: pointer; z-index: 2001;
}}
.trivia-close:hover {{ color: var(--gold); }}
.trivia-category {{
  color: var(--gold); font-size: 0.8rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 1px; margin-bottom: 1rem;
}}
.trivia-counter {{
  color: rgba(255,255,255,0.5); font-size: 0.8rem; margin-bottom: 0.5rem;
}}
.trivia-card-wrap {{
  perspective: 1000px; width: 100%; max-width: 500px; height: 320px;
  cursor: pointer; margin-bottom: 1.5rem;
}}
.trivia-card {{
  position: relative; width: 100%; height: 100%;
  transition: transform 0.6s; transform-style: preserve-3d;
}}
.trivia-card.flipped {{ transform: rotateY(180deg); }}
.trivia-face {{
  position: absolute; inset: 0; backface-visibility: hidden;
  border-radius: 16px; padding: 2rem; display: flex;
  align-items: center; justify-content: center; text-align: center;
}}
.trivia-front {{
  background: linear-gradient(135deg, var(--navy), #2a3d66);
  color: var(--white); font-size: 1.2rem; line-height: 1.5; font-weight: 500;
  border: 2px solid var(--gold);
}}
.trivia-front::after {{
  content: '👆 Tap to reveal'; position: absolute; bottom: 1rem;
  font-size: 0.75rem; color: var(--gold); opacity: 0.7;
}}
.trivia-back {{
  background: linear-gradient(135deg, #D4A017, #e6c84a);
  color: var(--navy); font-size: 1.1rem; line-height: 1.5; font-weight: 700;
  transform: rotateY(180deg); border: 2px solid var(--navy);
}}
.trivia-nav {{
  display: flex; gap: 1rem; align-items: center;
}}
.trivia-nav button {{
  background: rgba(255,255,255,0.15); color: white; border: 1px solid rgba(255,255,255,0.3);
  padding: 0.6rem 1.5rem; border-radius: 8px; font-size: 0.9rem; font-weight: 700;
  cursor: pointer; font-family: 'Roboto', sans-serif;
}}
.trivia-nav button:hover {{ background: rgba(255,255,255,0.25); }}
@media (max-width: 600px) {{
  .trivia-card-wrap {{ height: 280px; }}
  .trivia-front {{ font-size: 1rem; padding: 1.5rem; }}
  .trivia-back {{ font-size: 0.95rem; padding: 1.5rem; }}
}}

/* ─── Heart / Favorites ─── */
.heart-btn {{
  position: absolute; top: 0.7rem; right: 0.7rem; background: none; border: none;
  font-size: 1.4rem; cursor: pointer; color: #ccc; transition: all 0.2s; z-index: 5;
  line-height: 1;
}}
.heart-btn:hover {{ color: #E91E63; transform: scale(1.2); }}
.heart-btn.hearted {{ color: #E91E63; }}
.card {{ position: relative; }}
.fav-nav-btn {{
  background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.3);
  color: var(--gold); padding: 0.4rem 1rem; border-radius: 4px; font-size: 0.85rem;
  font-weight: 700; cursor: pointer; font-family: 'Roboto', sans-serif;
  letter-spacing: 1px; text-transform: uppercase;
}}
.fav-nav-btn:hover {{ background: rgba(255,255,255,0.2); }}
#favCount {{ color: var(--gold); }}
.fav-panel {{
  display: none; position: fixed; top: 64px; right: 0; width: 350px; max-width: 90vw;
  max-height: 80vh; background: var(--white); z-index: 1200;
  box-shadow: -4px 0 30px rgba(0,0,0,0.3); overflow-y: auto; border-radius: 0 0 0 12px;
}}
.fav-panel.active {{ display: block; }}
.fav-panel-header {{
  background: var(--navy); color: white; padding: 1rem; display: flex;
  justify-content: space-between; align-items: center; position: sticky; top: 0;
}}
.fav-panel-header h3 {{ font-size: 1rem; margin: 0; }}
.fav-item {{
  padding: 0.8rem 1rem; border-bottom: 1px solid #eee; cursor: pointer;
  display: flex; justify-content: space-between; align-items: center;
}}
.fav-item:hover {{ background: #F5F9FF; }}
.fav-item-name {{ font-weight: 700; color: var(--navy); font-size: 0.9rem; }}
.fav-item-remove {{ color: #ccc; cursor: pointer; font-size: 1.1rem; }}
.fav-item-remove:hover {{ color: #E91E63; }}
.fav-empty {{ padding: 2rem; text-align: center; color: #999; font-size: 0.9rem; }}
.fav-clear {{ background: none; border: 1px solid rgba(255,255,255,0.5); color: white; padding: 0.3rem 0.8rem; border-radius: 4px; font-size: 0.75rem; cursor: pointer; }}

/* ─── Lunch Picker ─── */
.lunch-overlay {{
  display: none; position: fixed; inset: 0; z-index: 2000;
  background: rgba(0,0,0,0.85); justify-content: center; align-items: center;
  flex-direction: column; padding: 1rem;
}}
.lunch-overlay.active {{ display: flex; }}
.lunch-close {{
  position: absolute; top: 1rem; right: 1.5rem; background: none; border: none;
  color: white; font-size: 2rem; cursor: pointer;
}}
.lunch-close:hover {{ color: var(--gold); }}
.lunch-card {{
  background: white; border-radius: 16px; padding: 2.5rem; text-align: center;
  max-width: 450px; width: 100%; box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}}
.lunch-card h2 {{ color: var(--navy); font-size: 1.5rem; margin-bottom: 0.3rem; }}
.lunch-card .lunch-cuisine {{ color: #E91E63; font-weight: 700; font-size: 0.9rem; margin-bottom: 0.5rem; }}
.lunch-card .lunch-detail {{ color: #666; font-size: 0.9rem; margin-bottom: 0.3rem; }}
.lunch-card .lunch-desc {{ color: #555; font-size: 0.85rem; margin: 1rem 0; line-height: 1.5; }}
.lunch-spin {{
  background: #E91E63; color: white; border: none; padding: 0.8rem 2.5rem;
  border-radius: 30px; font-size: 1.1rem; font-weight: 700; cursor: pointer;
  margin-top: 1rem; font-family: 'Roboto', sans-serif; letter-spacing: 1px;
}}
.lunch-spin:hover {{ background: #C2185B; }}
.lunch-spinning {{ animation: lunchShake 0.1s infinite; }}
@keyframes lunchShake {{
  0% {{ transform: rotate(0deg); }} 25% {{ transform: rotate(2deg); }}
  50% {{ transform: rotate(0deg); }} 75% {{ transform: rotate(-2deg); }}
}}
@media (max-width: 900px) {{
  .map-section-layout {{ grid-template-columns: 1fr; }}
  .map-container {{ height: 300px; }}
  .map-section-layout .card-grid {{ max-height: none; }}
}}
</style>
</head>
<body>

<!-- ═══ NAVIGATION ═══ -->
<nav class="navbar">
  <div class="nav-brand">SEATTLE <span>GUIDE</span></div>
  <div style="display:flex;gap:0.3rem;align-items:center;flex-shrink:1;min-width:0;">
    <button class="fav-nav-btn" onclick="toggleFavPanel()" aria-label="Favorites">❤️ <span id="favCount">0</span></button>
    <button class="hamburger" onclick="openLunchPicker()">🎰 LUNCH</button>
    <button class="hamburger" onclick="openTrivia()">🎯 TRIVIA</button>
    <button class="hamburger" onclick="document.querySelector('.nav-links').classList.toggle('active')" aria-label="Menu">☰ MENU</button>
  </div>
  <div class="nav-links">{nav_links}</div>
</nav>

<!-- ═══ HERO ═══ -->
<!-- TEMPLATE: Replace hero background with [CITY] skyline image -->
<section class="hero" id="home">
  <div class="hero-content">
    <h1>Welcome to {event["city"]}</h1>
    <p class="subtitle">{event["name"]} | {event["dates"]}</p>
    <div class="hero-buttons">
      <a href="#attractions" class="btn btn-primary">Explore Attractions</a>
      <a href="#transport" class="btn btn-outline">Getting Around</a>
    </div>
  </div>
</section>

<!-- ═══ INFO BAR ═══ -->
<!-- TEMPLATE: Update venue, dates, weather for new city -->
<div class="info-bar">
  <span class="info-item">📍 <strong>{venue["name"]}</strong> (Arch + Summit)</span>
  <span class="info-item">📅 <strong>{event["dates"]}</strong></span>
  <span class="info-item">🌡️ <strong>{weather["highF"]}°F / {weather["lowF"]}°F</strong> ({weather["highC"]}°C / {weather["lowC"]}°C)</span>
  <span class="info-item">🌅 Sunrise {weather["sunrise"]} / Sunset {weather["sunset"]}</span>
  <span class="info-item">☔ <strong>Skip the umbrella</strong> — pack a hooded rain jacket!</span>
</div>

<!-- ═══ VENUE SECTION ═══ -->
<section class="section" id="venue">
  <div class="section-header">
    <h2>Venue & Hotel</h2>
    <div class="section-line"></div>
    <p>The convention center campus spans two buildings with over 1 million square feet of event space</p>
  </div>
  <div class="venue-grid">
    <div class="venue-card">
      <div class="venue-card-header"><h3>🏛️ SCC Arch Building</h3></div>
      <div class="venue-card-body">
        <p>{venue.get("archBuilding", {}).get("description", "")}</p>
        <div class="venue-detail"><span class="venue-label">Address:</span> {venue.get("archBuilding", {}).get("address", venue["address"])}</div>
        <div class="venue-detail"><span class="venue-label">Space:</span> {venue.get("archBuilding", {}).get("sqft", 0):,} sq ft</div>
      </div>
    </div>
    <div class="venue-card">
      <div class="venue-card-header"><h3>🏢 SCC Summit Building</h3></div>
      <div class="venue-card-body">
        <p>{venue.get("summitBuilding", {}).get("description", "")}</p>
        <div class="venue-detail"><span class="venue-label">Address:</span> {venue.get("summitBuilding", {}).get("address", "")}</div>
        <div class="venue-detail"><span class="venue-label">Opened:</span> {venue.get("summitBuilding", {}).get("opened", "")}</div>
      </div>
    </div>
    <div class="venue-card">
      <div class="venue-card-header"><h3>🏨 {hotel["name"]} (HQ Hotel)</h3></div>
      <div class="venue-card-body">
        <div class="venue-detail"><span class="venue-label">Distance:</span> {hotel["distanceToVenue"]}</div>
        <div class="venue-detail"><span class="venue-label">Rate:</span> {hotel["rate"]}</div>
        <div class="venue-detail"><span class="venue-label">Amenities:</span> {", ".join(hotel["amenities"])}</div>
        <a href="{hotel["website"]}" target="_blank" class="card-link">Book Hotel →</a>
      </div>
    </div>
  </div>
</section>

<!-- ═══ WEATHER & TRANSPORT ═══ -->
<section class="section section-alt" id="transport">
  <div class="section-header">
    <h2>Weather & Getting Around</h2>
    <div class="section-line"></div>
    <!-- TEMPLATE: Update weather and transport for new city -->
  </div>
  <div class="weather-transport">
    <div>
      <!-- Live weather widget -->
      <div class="weather-live" id="weatherLive" style="margin-bottom:1rem;">
        <div style="background:linear-gradient(135deg,#29B6F6,#0288D1);border-radius:12px;padding:1.5rem;color:white;text-align:center;">
          <div style="font-size:0.75rem;text-transform:uppercase;letter-spacing:1px;opacity:0.8;margin-bottom:0.3rem;">📡 Right Now in Seattle</div>
          <div id="liveTemp" style="font-size:2.5rem;font-weight:900;">--°F</div>
          <div id="liveDesc" style="font-size:0.9rem;opacity:0.9;">Loading...</div>
          <div style="display:flex;justify-content:center;gap:1rem;margin-top:0.8rem;font-size:0.8rem;">
            <span id="liveWind">💨 --</span>
            <span id="liveHumidity">💧 --</span>
            <span id="liveRain">🌧️ --</span>
          </div>
          <div id="liveTime" style="font-size:0.7rem;opacity:0.5;margin-top:0.5rem;"></div>
        </div>
      </div>
      <!-- November averages card -->
      <div class="weather-card">
      <div style="font-size:3rem;">🌧️</div>
      <div class="temp">{weather["highF"]}°<span class="temp-small">/{weather["lowF"]}°F</span></div>
      <p style="opacity:0.8;margin:0.5rem 0;">November in {event["city"]}</p>
      <div class="weather-details">
        <div class="weather-detail">🌧️ {weather.get("rainDays","")} rain days</div>
        <div class="weather-detail">☀️ {weather.get("daylightHours","")} hrs daylight</div>
        <div class="weather-detail">🌅 Rise {weather["sunrise"]}</div>
        <div class="weather-detail">🌇 Set {weather["sunset"]}</div>
        <div class="weather-detail">☁️ {weather.get("clearSkyProbability","")} clear</div>
        <div class="weather-detail">🌧️ {weather.get("precipitation","")}</div>
      </div>
      <div class="weather-tip">💡 {weather.get("tip","")}</div>
    </div>
    </div>
    <div>
      <div class="transport-grid">
        {transport_cards}
      </div>
      <div style="text-align:center;margin-top:1.5rem;">
        <a href="https://www.soundtransit.org/ride-with-us/schedules-maps" target="_blank" class="btn btn-primary" style="display:inline-block;">🗺️ Sound Transit Maps & Schedules</a>
      </div>
    </div>
  </div>
</section>

<!-- ═══════════════════════════════════════════════════════════════════
     ESSENTIALS — What every visitor needs first
     ═══════════════════════════════════════════════════════════════════ -->

<!-- ═══ PRACTICAL INFO ═══ -->
<section class="section section-alt" id="practical">
  <div class="section-header">
    <h2>⚠️ Need to Know</h2>
    <div class="section-line"></div>
    <p>Veterans Day impacts, safety tips, medical resources, accessibility, and childcare</p>
  </div>
  <div class="card-grid">
    {practical_cards}
  </div>
</section>

<!-- ═══ MEDICAL ═══ -->
<section class="section" id="medical">
  <div class="section-header">
    <h2>🏥 Medical & Emergency</h2>
    <div class="section-line"></div>
    <p>🚨 In an emergency, call 911. Five hospitals and urgent care facilities near the convention center.</p>
  </div>
  <div class="card-grid">
    {medical_cards}
  </div>
</section>

<!-- ═══ DINING ═══ -->
<section class="section" id="dining">
  <div class="section-header">
    <h2>🍽️ Dining & Drinks</h2>
    <div class="section-line"></div>
    <p>{len(data["dining"])} curated restaurants sorted by distance from the convention center</p>
  </div>
  <div id="diningMap" class="map-wide"></div>
  <div class="sort-controls" data-target="diningCards">
    <button class="sort-btn active" data-sort="distance">↕ Distance</button>
    <button class="sort-btn" data-sort="name">A→Z Name</button>
  </div>
  <div class="card-grid" id="diningCards">
    {dining_cards}
  </div>
</section>

<!-- ═══ COFFEE & BARS ═══ -->
<section class="section section-alt" id="coffee">
  <div class="section-header">
    <h2>☕ Coffee & Bars</h2>
    <div class="section-line"></div>
    <p>Seattle is the birthplace of Starbucks and the epicenter of American specialty coffee culture</p>
  </div>
  <div id="coffeeMap" class="map-wide"></div>
  <div class="sort-controls" data-target="coffeeCards">
    <button class="sort-btn active" data-sort="distance">↕ Distance</button>
    <button class="sort-btn" data-sort="name">A→Z Name</button>
  </div>
  <div class="card-grid" id="coffeeCards">
    {coffee_cards}
  </div>
</section>

<!-- ═══ SHOPPING ═══ -->
<section class="section" id="shopping">
  <div class="section-header">
    <h2>🛍️ Shopping</h2>
    <div class="section-line"></div>
  </div>
  <div id="shoppingMap" class="map-wide"></div>
  <div class="sort-controls" data-target="shoppingCards">
    <button class="sort-btn active" data-sort="distance">↕ Distance</button>
    <button class="sort-btn" data-sort="name">A→Z Name</button>
  </div>
  <div class="card-grid" id="shoppingCards">
    {shopping_cards}
  </div>
</section>

<!-- ═══════════════════════════════════════════════════════════════════
     EXPLORE — Things to see and do
     ═══════════════════════════════════════════════════════════════════ -->

<!-- ═══ WALKABLE ATTRACTIONS ═══ -->
<section class="section section-alt" id="attractions">
  <div class="section-header">
    <h2>🏛️ Walkable Attractions</h2>
    <div class="section-line"></div>
    <p>{len(data["attractions"]["walkable"])} attractions within walking distance of the convention center</p>
  </div>
  <div id="attractionsMap" class="map-wide"></div>
  <div class="sort-controls" data-target="attractionsCards">
    <button class="sort-btn active" data-sort="distance">↕ Distance</button>
    <button class="sort-btn" data-sort="name">A→Z Name</button>
  </div>
  <div class="card-grid" id="attractionsCards">
    {attraction_cards}
  </div>
</section>

<!-- ═══ DAY TRIPS ═══ -->
<section class="section" id="daytrips">
  <div class="section-header">
    <h2>🚗 Day Trips & Beyond</h2>
    <div class="section-line"></div>
    <p>Venture beyond downtown — {len(data["attractions"]["dayTrips"])} destinations within 2 hours</p>
  </div>
  <div id="daytripsMap" class="map-wide"></div>
  <div class="sort-controls" data-target="daytripsCards">
    <button class="sort-btn active" data-sort="distance">↕ Distance</button>
    <button class="sort-btn" data-sort="name">A→Z Name</button>
  </div>
  <div class="card-grid" id="daytripsCards">
    {daytrip_cards}
  </div>
</section>

<!-- ═══ TOURS ═══ -->
<section class="section section-alt" id="tours">
  <div class="section-header">
    <h2>🚢 Tours & Excursions</h2>
    <div class="section-line"></div>
    <p>Boat cruises, seaplane flights, helicopter tours, and walking food tours</p>
  </div>
  <div id="toursMap" class="map-wide"></div>
  <div class="sort-controls" data-target="toursCards">
    <button class="sort-btn active" data-sort="distance">↕ Distance</button>
    <button class="sort-btn" data-sort="name">A→Z Name</button>
  </div>
  <div class="card-grid" id="toursCards">
    {tour_cards}
  </div>
</section>

<!-- ═══ ENTERTAINMENT ═══ -->
<section class="section section-alt" id="entertainment">
  <div class="section-header">
    <h2>🎭 Entertainment & Nightlife</h2>
    <div class="section-line"></div>
  </div>
  <div id="entertainmentMap" class="map-wide"></div>
  <div class="sort-controls" data-target="entertainmentCards">
    <button class="sort-btn active" data-sort="distance">↕ Distance</button>
    <button class="sort-btn" data-sort="name">A→Z Name</button>
  </div>
  <div class="card-grid" id="entertainmentCards">
    {entertainment_cards}
  </div>
</section>

<!-- ═══ FAMILY ACTIVITIES ═══ -->
<section class="section" id="family">
  <div class="section-header">
    <h2>👨‍👩‍👧‍👦 Family Activities</h2>
    <div class="section-line"></div>
    <p>Rainy-day-proof fun for families — indoor and outdoor options for all ages</p>
  </div>
  <div id="familyMap" class="map-wide"></div>
  <div class="sort-controls" data-target="familyCards">
    <button class="sort-btn active" data-sort="distance">↕ Distance</button>
    <button class="sort-btn" data-sort="name">A→Z Name</button>
  </div>
  <div class="card-grid" id="familyCards">
    {family_cards}
  </div>
</section>

<!-- ═══ SEASONAL EVENTS ═══ -->
<section class="section section-alt" id="seasonal">
  <div class="section-header">
    <h2>🎄 Seasonal Events</h2>
    <div class="section-line"></div>
    <p>November in Seattle means the start of holiday magic</p>
  </div>
  <div class="card-grid">
    {seasonal_cards}
  </div>
</section>

<!-- ═══ PHOTO SPOTS ═══ -->
<section class="section" id="photospots">
  <div class="section-header">
    <h2>📸 Seattle Photo Spots</h2>
    <div class="section-line"></div>
    <p>The most Instagrammable spots in the city — with pro tips on timing and angles</p>
  </div>
  <div class="card-grid">
    {photo_cards}
  </div>
</section>

<!-- ═══════════════════════════════════════════════════════════════════
     CULTURE & CONTEXT — Know the city
     ═══════════════════════════════════════════════════════════════════ -->

<!-- ═══ HISTORY ═══ -->
<section class="section" id="history">
  <div class="section-header">
    <h2>📜 From Sawdust to Software</h2>
    <div class="section-line"></div>
    <p>Seattle's growth has been defined by massive boom-and-bust cycles, reshaping the landscape — and even the physical elevation — of the city</p>
  </div>
  <div class="card-grid" style="grid-template-columns: 1fr;">
    {history_cards}
  </div>
</section>

<!-- ═══ FAMOUS FACES ═══ -->
<section class="section section-alt" id="famous">
  <div class="section-header">
    <h2>⭐ Seattle's Own: Famous Faces</h2>
    <div class="section-line"></div>
    <p>Seattle has been a launchpad for revolutionaries in music, technology, and entertainment</p>
  </div>
  <div class="card-grid">
    {famous_cards}
  </div>
</section>

<!-- ═══ POP CULTURE ═══ -->
<section class="section" id="popculture">
  <div class="section-header">
    <h2>🎬 The Emerald City on Screen</h2>
    <div class="section-line"></div>
    <p>Seattle's moody weather, stunning skyline, and surrounding waterways make it an incredibly atmospheric setting</p>
  </div>
  <h3 style="text-align:center;color:var(--navy);margin-bottom:1rem;">📺 Television</h3>
  <div class="card-grid">
    {pop_tv}
  </div>
  <h3 style="text-align:center;color:var(--navy);margin:2rem 0 1rem;">🎬 Film</h3>
  <div class="card-grid">
    {pop_film}
  </div>
</section>

<!-- ═══ GEOGRAPHY ═══ -->
<section class="section section-navy" id="geography">
  <div class="section-header">
    <h2>🌋 Fire and Ice: Seattle's Geography</h2>
    <div class="section-line"></div>
    <p>Nestled between mountain ranges and deep waterways, sitting on the Pacific Ring of Fire</p>
  </div>
  <div class="card-grid">
    {geo_cards}
  </div>
</section>

<!-- ═══ LIFE SCIENCES HERITAGE ═══ -->
<section class="section" id="lifesciences">
  <div class="section-header">
    <h2>🧬 Seattle's Life Sciences Legacy</h2>
    <div class="section-line"></div>
    <p>Seattle is a global epicenter for molecular pathology, immunology, and precision medicine</p>
  </div>
  <div class="card-grid">
    {lifesci_cards}
  </div>
</section>

<!-- ═══════════════════════════════════════════════════════════════════
     REFERENCE
     ═══════════════════════════════════════════════════════════════════ -->

<!-- ═══ LOCAL INSIGHTS ═══ -->
<section class="section section-alt" id="insights">
  <div class="section-header">
    <h2>💡 Local Insights</h2>
    <div class="section-line"></div>
  </div>
  <div class="insight-grid">
    {insight_boxes}
  </div>
</section>

<!-- ═══ LOCATION INDEX ═══ -->
<section class="section" id="index">
  <div class="section-header">
    <h2>📍 All Locations Index</h2>
    <div class="section-line"></div>
    <p>Every location in this guide — {len(all_locations)} places, searchable and sortable</p>
  </div>
  <input type="text" class="index-search" id="indexSearch" placeholder="🔍 Search locations..." autocomplete="off">
  <div class="index-count" id="indexCount">{len(all_locations)} locations</div>
  <div class="index-table-wrap">
    <table class="index-table" id="indexTable">
      <thead>
        <tr>
          <th data-col="0">Name ↕</th>
          <th data-col="1">Category ↕</th>
          <th data-col="2">Distance ↕</th>
          <th data-col="3">Address</th>
          <th>Link</th>
        </tr>
      </thead>
      <tbody>
        {index_rows}
      </tbody>
    </table>
  </div>
</section>

<!-- ═══ PRICE KEY ═══ -->
<div class="section">
  <div class="price-legend">
    <strong>Price Key:</strong> {price_legend}
  </div>
</div>

<!-- ═══ FAVORITES PANEL ═══ -->
<div class="fav-panel" id="favPanel">
  <div class="fav-panel-header">
    <h3>❤️ My Favorites</h3>
    <button class="fav-clear" onclick="clearFavs()">Clear All</button>
  </div>
  <div id="favList"></div>
</div>

<!-- ═══ LUNCH PICKER OVERLAY ═══ -->
<div class="lunch-overlay" id="lunchOverlay">
  <button class="lunch-close" onclick="closeLunchPicker()">✕</button>
  <h2 style="color:var(--gold);margin-bottom:1rem;font-size:1.2rem;">🎰 Where Should We Eat?</h2>
  <div class="lunch-card" id="lunchCard">
    <h2 id="lunchName">Press Spin!</h2>
    <div class="lunch-cuisine" id="lunchCuisine"></div>
    <div class="lunch-detail" id="lunchWalk"></div>
    <div class="lunch-detail" id="lunchPrice"></div>
    <div class="lunch-desc" id="lunchDesc"></div>
    <button class="lunch-spin" onclick="spinLunch()">🎰 SPIN!</button>
  </div>
</div>

<!-- ═══ TRIVIA OVERLAY ═══ -->
<div class="trivia-overlay" id="triviaOverlay">
  <button class="trivia-close" onclick="closeTrivia()" aria-label="Close trivia">✕</button>
  <div class="trivia-category" id="triviaCategory"></div>
  <div class="trivia-counter" id="triviaCounter"></div>
  <div class="trivia-card-wrap" onclick="flipTrivia()">
    <div class="trivia-card" id="triviaCard">
      <div class="trivia-face trivia-front" id="triviaQ"></div>
      <div class="trivia-face trivia-back" id="triviaA"></div>
    </div>
  </div>
  <div class="trivia-nav">
    <button onclick="prevTrivia()">← Prev</button>
    <button onclick="flipTrivia()">Flip</button>
    <button onclick="nextTrivia()">Next →</button>
  </div>
</div>

<!-- ═══ FOOTER ═══ -->
<!-- TEMPLATE: Update org info, year, and contact emails -->
<footer class="footer">
  <h3>SEATTLE <span>GUIDE</span></h3>
  <p><strong>Welcome to Seattle</strong></p>
  <p>{event["dates"]} — {event["city"]}, {event["state"]}</p>
  <p style="margin-top:1rem;">
    <a href="https://visitseattle.org" target="_blank">Visit Seattle</a> |
    <a href="https://seattleconventioncenter.com" target="_blank">Convention Center</a>
  </p>
  <div style="margin-top:2rem;display:flex;flex-direction:column;align-items:center;gap:0.5rem;">
    <img src="cigdem.jpg" alt="Çiğdem Uşşaklı" style="width:64px;height:64px;border-radius:50%;object-fit:cover;border:2px solid var(--gold);">
    <p style="font-size:0.8rem;color:rgba(255,255,255,0.7);margin:0;">Executive Producer <strong style="color:var(--gold);">Çiğdem Uşşaklı</strong></p>
  </div>
  <p style="margin-top:1rem;font-size:0.75rem;opacity:0.5;">Seattle Guide 2026 — Your curated city companion</p>
</footer>

<!-- ═══ BACK TO TOP ═══ -->
<button class="back-to-top" onclick="window.scrollTo({{top:0,behavior:'smooth'}})" aria-label="Back to top">↑</button>

<script>
// Close menu on link click
document.querySelectorAll('.nav-links a').forEach(link => {{
  link.addEventListener('click', () => {{
    document.querySelector('.nav-links').classList.remove('active');
  }});
}});

// Back-to-top visibility
const btn = document.querySelector('.back-to-top');
window.addEventListener('scroll', () => {{
  btn.classList.toggle('visible', window.scrollY > 500);
}});

// Scroll animations
const observer = new IntersectionObserver((entries) => {{
  entries.forEach(e => {{ if(e.isIntersecting) e.target.classList.add('visible'); }});
}}, {{ threshold: 0.1 }});
document.querySelectorAll('.card, .venue-card, .transport-card, .insight-box').forEach(el => {{
  el.classList.add('fade-in');
  observer.observe(el);
}});

// ─── LEAFLET MAPS ───
const VENUE = [{venue_lat}, {venue_lng}];
const TILE_URL = 'https://{{s}}.basemaps.cartocdn.com/rastertiles/voyager/{{z}}/{{x}}/{{y}}@2x.png';
const TILE_ATTR = '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>';

function venueIcon() {{
  return L.divIcon({{
    className: 'venue-marker',
    html: '<div style="background:#D4A017;color:#1B2A4A;width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:14px;border:3px solid #1B2A4A;box-shadow:0 2px 8px rgba(0,0,0,0.4);">SCC</div>',
    iconSize: [36, 36],
    iconAnchor: [18, 18],
    popupAnchor: [0, -20]
  }});
}}

function placeIcon(color, label) {{
  return L.divIcon({{
    className: 'place-marker',
    html: '<div style="background:' + color + ';color:#fff;min-width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:11px;border:2px solid #fff;box-shadow:0 2px 6px rgba(0,0,0,0.3);padding:0 4px;">' + label + '</div>',
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    popupAnchor: [0, -14]
  }});
}}

function initMap(mapId, cardsId, markersData, color) {{
  const mapEl = document.getElementById(mapId);
  if (!mapEl) return;

  const map = L.map(mapId, {{ scrollWheelZoom: false }}).setView(VENUE, 14);
  L.tileLayer(TILE_URL, {{ attribution: TILE_ATTR, maxZoom: 18 }}).addTo(map);

  // Venue marker
  L.marker(VENUE, {{ icon: venueIcon(), zIndexOffset: 1000 }})
    .addTo(map)
    .bindPopup('<strong>Seattle Convention Center</strong><br>Arch + Summit Buildings');

  const cards = document.querySelectorAll('#' + cardsId + ' .card');
  const markers = [];

  markersData.forEach((m, i) => {{
    const marker = L.marker([m.lat, m.lng], {{ icon: placeIcon(color, (i+1).toString()) }})
      .addTo(map)
      .bindPopup('<strong>' + m.name + '</strong>' +
        (m.walk ? '<br>🚶 ' + m.walk + ' min walk' : '') +
        (m.price ? '<br>' + m.price : '') +
        (m.cuisine ? '<br><em>' + m.cuisine + '</em>' : ''));

    markers.push(marker);

    // Click marker → highlight card
    marker.on('click', () => {{
      cards.forEach(c => c.classList.remove('card-active'));
      if (cards[m.idx]) {{
        cards[m.idx].classList.add('card-active');
        cards[m.idx].scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
      }}
    }});
  }});

  // Click card → highlight marker + open popup
  cards.forEach((card, i) => {{
    card.addEventListener('click', (e) => {{
      if (e.target.closest('a')) return; // don't hijack link clicks
      cards.forEach(c => c.classList.remove('card-active'));
      card.classList.add('card-active');
      if (markers[i]) {{
        map.setView([markersData[i].lat, markersData[i].lng], 16, {{ animate: true }});
        markers[i].openPopup();
      }}
    }});
    card.style.cursor = 'pointer';
  }});

  // Fit bounds to show all markers
  const allLatLngs = [VENUE, ...markersData.map(m => [m.lat, m.lng])];
  map.fitBounds(allLatLngs, {{ padding: [30, 30] }});

  // Fix map rendering when section scrolls into view
  new IntersectionObserver((entries) => {{
    if (entries[0].isIntersecting) map.invalidateSize();
  }}).observe(mapEl);
}}

// Initialize all maps
const diningMarkers = {dining_markers_json};
const attractionMarkers = {attraction_markers_json};
const daytripsMarkers = {daytrip_markers_json};
const familyMarkers = {family_markers_json};
const shoppingMarkers = {shopping_markers_json};
const entertainmentMarkers = {entertainment_markers_json};
const tourMarkers = {tour_markers_json};
const coffeeMarkers = {coffee_markers_json};

initMap('attractionsMap', 'attractionsCards', attractionMarkers, '#29B6F6');
initMap('diningMap', 'diningCards', diningMarkers, '#B5294E');
initMap('daytripsMap', 'daytripsCards', daytripsMarkers, '#4CAF50');
initMap('familyMap', 'familyCards', familyMarkers, '#7B1FA2');
initMap('shoppingMap', 'shoppingCards', shoppingMarkers, '#FF6F00');
initMap('entertainmentMap', 'entertainmentCards', entertainmentMarkers, '#E91E63');
initMap('toursMap', 'toursCards', tourMarkers, '#00897B');
initMap('coffeeMap', 'coffeeCards', coffeeMarkers, '#795548');

// ─── SORTING ───
document.querySelectorAll('.sort-controls').forEach(controls => {{
  const targetId = controls.dataset.target;
  const grid = document.getElementById(targetId);
  if (!grid) return;

  controls.querySelectorAll('.sort-btn').forEach(btn => {{
    btn.addEventListener('click', () => {{
      controls.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const cards = [...grid.querySelectorAll('.card')];
      const sortBy = btn.dataset.sort;

      cards.sort((a, b) => {{
        if (sortBy === 'name') {{
          return (a.dataset.name || '').localeCompare(b.dataset.name || '');
        }} else {{
          return (parseFloat(a.dataset.distance) || 999) - (parseFloat(b.dataset.distance) || 999);
        }}
      }});

      cards.forEach(card => {{
        card.style.animation = 'none';
        card.offsetHeight;
        grid.appendChild(card);
        card.style.animation = 'fadeSlideIn 0.3s ease-out forwards';
      }});
    }});
  }});
}});

// ─── INDEX SEARCH & SORT ───
const indexSearch = document.getElementById('indexSearch');
const indexTable = document.getElementById('indexTable');
const indexCount = document.getElementById('indexCount');
if (indexSearch && indexTable) {{
  indexSearch.addEventListener('input', () => {{
    const q = indexSearch.value.toLowerCase();
    let visible = 0;
    indexTable.querySelectorAll('tbody tr').forEach(row => {{
      const text = row.textContent.toLowerCase();
      const show = text.includes(q);
      row.style.display = show ? '' : 'none';
      if (show) visible++;
    }});
    indexCount.textContent = visible + ' locations';
  }});

  let sortDir = {{}};
  indexTable.querySelectorAll('thead th[data-col]').forEach(th => {{
    th.addEventListener('click', () => {{
      const col = parseInt(th.dataset.col);
      sortDir[col] = !sortDir[col];
      const rows = [...indexTable.querySelectorAll('tbody tr')];
      rows.sort((a, b) => {{
        let aVal = a.children[col].textContent.trim();
        let bVal = b.children[col].textContent.trim();
        if (col === 2) {{
          aVal = parseInt(aVal) || 9999;
          bVal = parseInt(bVal) || 9999;
          return sortDir[col] ? bVal - aVal : aVal - bVal;
        }}
        return sortDir[col] ? bVal.localeCompare(aVal) : aVal.localeCompare(bVal);
      }});
      rows.forEach(r => indexTable.querySelector('tbody').appendChild(r));
    }});
  }});
}}

// ─── LIVE WEATHER (Open-Meteo, free, no API key) ───
(function() {{
  const WMO = {{0:'☀️ Clear',1:'🌤️ Mostly clear',2:'⛅ Partly cloudy',3:'☁️ Overcast',
    45:'🌫️ Foggy',48:'🌫️ Rime fog',51:'🌦️ Light drizzle',53:'🌧️ Drizzle',55:'🌧️ Heavy drizzle',
    61:'🌧️ Light rain',63:'🌧️ Rain',65:'🌧️ Heavy rain',71:'🌨️ Light snow',73:'🌨️ Snow',
    75:'🌨️ Heavy snow',80:'🌧️ Rain showers',81:'🌧️ Heavy showers',82:'⛈️ Violent showers',
    95:'⛈️ Thunderstorm',96:'⛈️ Hail storm',99:'⛈️ Heavy hail storm'}};
  fetch('https://api.open-meteo.com/v1/forecast?latitude=47.6117&longitude=-122.3321&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,precipitation&temperature_unit=fahrenheit&wind_speed_unit=mph&timezone=America%2FLos_Angeles')
    .then(r => r.json())
    .then(d => {{
      const c = d.current;
      document.getElementById('liveTemp').textContent = Math.round(c.temperature_2m) + '°F';
      document.getElementById('liveDesc').textContent = WMO[c.weather_code] || 'Weather data';
      document.getElementById('liveWind').textContent = '💨 ' + Math.round(c.wind_speed_10m) + ' mph';
      document.getElementById('liveHumidity').textContent = '💧 ' + c.relative_humidity_2m + '%';
      document.getElementById('liveRain').textContent = '🌧️ ' + c.precipitation + ' in';
      const t = new Date(c.time);
      document.getElementById('liveTime').textContent = 'Updated: ' + t.toLocaleString('en-US', {{timeZone:'America/Los_Angeles', hour:'numeric', minute:'2-digit', hour12:true}}) + ' Seattle time';
    }})
    .catch(() => {{
      document.getElementById('liveDesc').textContent = 'Unable to load live weather';
    }});
}})();

// ─── FAVORITES ───
let favs = JSON.parse(localStorage.getItem('seattleFavs') || '[]');

function updateFavUI() {{
  document.getElementById('favCount').textContent = favs.length;
  // Sync heart buttons
  document.querySelectorAll('.heart-btn').forEach(btn => {{
    const name = btn.closest('.card')?.dataset.name || '';
    btn.classList.toggle('hearted', favs.includes(name));
    btn.textContent = favs.includes(name) ? '♥' : '♡';
  }});
  // Render panel
  const list = document.getElementById('favList');
  if (favs.length === 0) {{
    list.innerHTML = '<div class="fav-empty">No favorites yet!<br>Tap ♡ on any card to save it.</div>';
  }} else {{
    list.innerHTML = favs.map(function(n) {{
      var safe = n.replace(/"/g, '&quot;');
      return '<div class="fav-item" onclick="scrollToCard(&quot;' + safe + '&quot;)">' +
        '<span class="fav-item-name">' + n + '</span>' +
        '<span class="fav-item-remove" onclick="event.stopPropagation();removeFav(&quot;' + safe + '&quot;)">✕</span></div>';
    }}).join('');
  }}
}}

function toggleFav(btn) {{
  const name = btn.closest('.card')?.dataset.name || '';
  if (!name) return;
  if (favs.includes(name)) {{
    favs = favs.filter(f => f !== name);
  }} else {{
    favs.push(name);
    btn.style.transform = 'scale(1.5)';
    setTimeout(() => btn.style.transform = '', 300);
  }}
  localStorage.setItem('seattleFavs', JSON.stringify(favs));
  updateFavUI();
}}

function removeFav(name) {{
  favs = favs.filter(f => f !== name);
  localStorage.setItem('seattleFavs', JSON.stringify(favs));
  updateFavUI();
}}

function clearFavs() {{
  favs = [];
  localStorage.setItem('seattleFavs', JSON.stringify(favs));
  updateFavUI();
}}

function toggleFavPanel() {{
  document.getElementById('favPanel').classList.toggle('active');
}}

function scrollToCard(name) {{
  document.getElementById('favPanel').classList.remove('active');
  const card = document.querySelector('.card[data-name="' + name + '"]');
  if (card) {{
    card.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
    card.classList.add('card-active');
    setTimeout(() => card.classList.remove('card-active'), 2000);
  }}
}}

// Close fav panel on outside click
document.addEventListener('click', e => {{
  const panel = document.getElementById('favPanel');
  const btn = document.querySelector('.fav-nav-btn');
  if (panel.classList.contains('active') && !panel.contains(e.target) && !btn.contains(e.target)) {{
    panel.classList.remove('active');
  }}
}});

updateFavUI();

// ─── LUNCH PICKER ───
const lunchData = {lunch_json};

function openLunchPicker() {{
  document.getElementById('lunchOverlay').classList.add('active');
  document.body.style.overflow = 'hidden';
  document.getElementById('lunchName').textContent = 'Press Spin!';
  document.getElementById('lunchCuisine').textContent = '';
  document.getElementById('lunchWalk').textContent = '';
  document.getElementById('lunchPrice').textContent = '';
  document.getElementById('lunchDesc').textContent = 'Tap the button and we\\'ll pick a restaurant for you!';
}}

function closeLunchPicker() {{
  document.getElementById('lunchOverlay').classList.remove('active');
  document.body.style.overflow = '';
}}

function spinLunch() {{
  const card = document.getElementById('lunchCard');
  card.classList.add('lunch-spinning');
  let count = 0;
  const interval = setInterval(() => {{
    const r = lunchData[Math.floor(Math.random() * lunchData.length)];
    document.getElementById('lunchName').textContent = r.name;
    count++;
    if (count > 15) {{
      clearInterval(interval);
      card.classList.remove('lunch-spinning');
      const pick = lunchData[Math.floor(Math.random() * lunchData.length)];
      document.getElementById('lunchName').textContent = '🎉 ' + pick.name;
      document.getElementById('lunchCuisine').textContent = pick.cuisine;
      const dist = pick.walk != null ? (pick.walk === 0 ? '📍 On-Site!' : '🚶 ' + pick.walk + ' min walk') : '🚗 ' + pick.drive + ' min drive';
      document.getElementById('lunchWalk').textContent = dist;
      document.getElementById('lunchPrice').textContent = pick.price;
      document.getElementById('lunchDesc').textContent = pick.desc;
    }}
  }}, 80);
}}

// ─── TRIVIA ───
const triviaData = {trivia_json};
let triviaIdx = 0;
let triviaShuffled = [];

function shuffleTrivia() {{
  triviaShuffled = [...triviaData].sort(() => Math.random() - 0.5);
  triviaIdx = 0;
}}

function showTrivia() {{
  const t = triviaShuffled[triviaIdx];
  document.getElementById('triviaCategory').textContent = t.category;
  document.getElementById('triviaCounter').textContent = (triviaIdx + 1) + ' / ' + triviaShuffled.length;
  document.getElementById('triviaQ').textContent = t.question;
  document.getElementById('triviaA').textContent = t.answer;
  document.getElementById('triviaCard').classList.remove('flipped');
}}

function openTrivia() {{
  shuffleTrivia();
  showTrivia();
  document.getElementById('triviaOverlay').classList.add('active');
  document.body.style.overflow = 'hidden';
}}

function closeTrivia() {{
  document.getElementById('triviaOverlay').classList.remove('active');
  document.body.style.overflow = '';
}}

function flipTrivia() {{
  document.getElementById('triviaCard').classList.toggle('flipped');
}}

function nextTrivia() {{
  triviaIdx = (triviaIdx + 1) % triviaShuffled.length;
  showTrivia();
}}

function prevTrivia() {{
  triviaIdx = (triviaIdx - 1 + triviaShuffled.length) % triviaShuffled.length;
  showTrivia();
}}

// Swipe support
(function() {{
  let startX = 0;
  const el = document.getElementById('triviaOverlay');
  el.addEventListener('touchstart', e => {{ startX = e.touches[0].clientX; }}, {{passive: true}});
  el.addEventListener('touchend', e => {{
    const diff = e.changedTouches[0].clientX - startX;
    if (Math.abs(diff) > 60) {{
      if (diff < 0) nextTrivia(); else prevTrivia();
    }}
  }});
}})();

// Keyboard support
document.addEventListener('keydown', e => {{
  if (!document.getElementById('triviaOverlay').classList.contains('active')) return;
  if (e.key === 'Escape') closeTrivia();
  if (e.key === 'ArrowRight' || e.key === ' ') {{ e.preventDefault(); nextTrivia(); }}
  if (e.key === 'ArrowLeft') prevTrivia();
  if (e.key === 'Enter') flipTrivia();
}});
</script>
</body>
</html>
'''

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Website generated: {{len(html):,}} characters → {{OUTPUT_PATH}}")
