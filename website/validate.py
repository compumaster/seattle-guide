"""
Validate all locations and links in seattle-data.json.
- Checks every website URL for HTTP status
- Flags dead links (404, 403, timeouts)
- Reports results for manual review
"""
import json, urllib.request, urllib.error, ssl, time

DATA = r"D:\prj\seattle-guide\website\data\seattle-data.json"

with open(DATA, "r", encoding="utf-8") as f:
    data = json.load(f)

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

results = []

def check_url(url, name, section):
    if not url or not url.startswith("http"):
        return
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) SeattleGuideValidator/1.0"
        })
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            code = resp.getcode()
            final_url = resp.geturl()
            results.append({"name": name, "section": section, "url": url, "status": code, "final_url": final_url, "ok": True})
            print(f"  ✓ {code} {name}")
    except urllib.error.HTTPError as e:
        results.append({"name": name, "section": section, "url": url, "status": e.code, "error": str(e), "ok": False})
        print(f"  ✗ {e.code} {name} — {url}")
    except Exception as e:
        results.append({"name": name, "section": section, "url": url, "status": 0, "error": str(e), "ok": False})
        print(f"  ✗ ERR {name} — {e}")
    time.sleep(0.5)

def scan_list(items, section):
    for item in items:
        name = item.get("name") or item.get("title") or item.get("era", "")
        url = item.get("website", "")
        if url:
            check_url(url, name, section)

# Scan all sections
print("=== VENUE & HOTEL ===")
check_url(data["venue"].get("website"), "Convention Center", "venue")
check_url(data["headquarterHotel"].get("website"), "Sheraton Grand", "hotel")

print("\n=== TRANSPORTATION ===")
scan_list(data.get("transportation", []), "transportation")

print("\n=== DINING ===")
scan_list(data.get("dining", []), "dining")

print("\n=== WALKABLE ATTRACTIONS ===")
scan_list(data["attractions"]["walkable"], "attractions")

print("\n=== DAY TRIPS ===")
scan_list(data["attractions"]["dayTrips"], "dayTrips")

print("\n=== TOURS ===")
scan_list(data.get("tours", []), "tours")

print("\n=== SHOPPING ===")
scan_list(data.get("shopping", []), "shopping")

print("\n=== ENTERTAINMENT ===")
scan_list(data.get("entertainment", []), "entertainment")

print("\n=== COFFEE & BARS ===")
scan_list(data.get("coffeeAndBars", []), "coffee")

print("\n=== FAMILY ACTIVITIES ===")
scan_list(data.get("familyActivities", []), "family")

print("\n=== SEASONAL EVENTS ===")
scan_list(data.get("seasonalEvents", []), "seasonal")

print("\n=== LIFE SCIENCES ===")
scan_list(data.get("lifeSciencesHeritage", []), "lifesciences")

# Summary
print("\n" + "=" * 60)
failed = [r for r in results if not r["ok"]]
print(f"Total URLs checked: {len(results)}")
print(f"OK: {len(results) - len(failed)}")
print(f"FAILED: {len(failed)}")
if failed:
    print("\n⚠️  FAILED LINKS:")
    for r in failed:
        print(f"  [{r['section']}] {r['name']}")
        print(f"    URL: {r['url']}")
        print(f"    Status: {r['status']} — {r.get('error', '')}")
        print()
