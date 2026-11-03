#!/usr/bin/env python3
"""Build a PUBLIC events.json for BRUNCH, PLEASE! from the Ticket Tailor API.
Only public event info goes out: no API key, no orders, no customer data, no revenue.
Usage: TICKET_TAILOR_API_KEY=... python3 build_events.py [out_path]"""
import json, os, sys, time, base64, urllib.request
KEY = os.environ["TICKET_TAILOR_API_KEY"]
AUTH = "Basic " + base64.b64encode(f"{KEY}:".encode()).decode()
def get(url):
    req = urllib.request.Request(url, headers={"Authorization": AUTH, "Accept": "application/json", "User-Agent": "brunchplz-events/1.1"})
    return json.load(urllib.request.urlopen(req, timeout=30))
evs, url = [], f"https://api.tickettailor.com/v1/events?start_at.gte={int(time.time())}&limit=100"
while url:
    d = get(url); evs += d["data"]
    nxt = d.get("links", {}).get("next"); url = ("https://api.tickettailor.com/v1" + nxt) if nxt else None
def t12(hm):
    h, m = map(int, hm.split(":")); return f"{(h % 12) or 12}{'' if m == 0 else ':%02d' % m}{'AM' if h < 12 else 'PM'}"
out = []
for e in sorted(evs, key=lambda e: e["start"]["unix"]):
    if e["status"] != "published" or e.get("hidden") == "true" or e.get("private") == "true": continue
    if "BRUNCH, PLEASE" not in e["name"].upper() or "HIDDEN" in e["name"].upper(): continue
    tts = e.get("ticket_types", [])
    left = sum(t.get("quantity") or 0 for t in tts if t["status"] == "on_sale")
    cap = left + (e.get("total_issued_tickets") or 0)
    prices = [t["price"] for t in tts if t["status"] == "on_sale"]
    prices += [b["price"] / sum(x["quantity"] for x in b["ticket_types"]) for b in e.get("bundles", []) if b["status"] == "ON_SALE" and b["ticket_types"]]
    sold = e.get("tickets_available") != "true" or left <= 0
    if sold: badge = "SOLD OUT"
    elif left <= 10 or left <= 0.15 * cap: badge = "Almost gone"
    elif left <= 40: badge = f"{left} left"
    else: badge = "On sale"
    theme = e["name"].split("!", 1)[1].strip(" -") if "!" in e["name"] else ""
    out.append({"id": e["id"], "name": e["name"], "theme": theme,
                "date": e["start"]["date"], "day": time.strftime("%a", time.strptime(e["start"]["date"], "%Y-%m-%d")),
                "time": t12(e["start"]["time"]), "start_iso": e["start"]["iso"], "label": e["start"]["formatted"],
                "from_price": round(min(prices) / 100, 2) if prices else None,
                "left": left, "badge": badge, "sold_out": sold,
                "url": e["url"].replace("www.tickettailor.com", "tickets.brunchplz.com"),
                "checkout_url": e.get("checkout_url")})
doc = {"generated": int(time.time()), "source": "Ticket Tailor (public event info only)", "events": out}
path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "events.json")
json.dump(doc, open(path, "w"), indent=1)
print(len(out), "events ->", path)
