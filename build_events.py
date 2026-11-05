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
    # "from" price = cheapest seat type that still has seats; fall back to any on-sale type
    prices = [t["price"] for t in tts if t["status"] == "on_sale" and (t.get("quantity") or 0) > 0] or [t["price"] for t in tts if t["status"] == "on_sale"]
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

# ---- merch.json: public store products only (no stock/sales counts, no secrets). Failure never touches events.json.
def build_merch():
    import re
    STORE = "https://tickets.brunchplz.com/events/brickyardonmain/store"
    raw, url = [], "https://api.tickettailor.com/v1/products?limit=100"
    while url:
        d = get(url); raw += d["data"]
        nxt = d.get("links", {}).get("next"); url = ("https://api.tickettailor.com/v1" + nxt) if nxt else None
    LINES = {"Brunch Please LED Light Wand": ("LED Light Wand", "We sync every wand to the music. Rechargeable, yours to keep."),
             "Feral Girl Brunch Bundle": ("Feral Girl Bundle", "FERAL hat, hand fan, scrunchie, button + hangover relief. Waiting on your table."),
             "Hot Girl Brunch Bundle": ("Hot Girl Bundle", "Hand fan, scrunchie, button + hangover relief. Waiting on your table."),
             "Dancing Women Tee": ("Dancing Women Tee", "Cream, pink or charcoal. Pick it up at brunch.")}
    ORDER = ["Feral Girl Brunch Bundle", "Hot Girl Brunch Bundle", "Dancing Women Tee", "Brunch Please LED Light Wand"]
    SIZE_ORDER = ["S", "Small", "M", "Medium", "L", "Large", "XL", "XXL", "XXXL"]
    SIZES = set(SIZE_ORDER)
    def sort_sizes(vals):
        rank = {s: i for i, s in enumerate(SIZE_ORDER)}
        sizes = [v for v in vals if v in rank]
        other = [v for v in vals if v not in rank]
        sizes.sort(key=lambda v: rank[v])
        return sizes + other
    g = {}
    for p in raw:
        if p.get("status") != "ON_SALE" or str(p.get("sell_in_store")) != "true": continue
        c = re.search(r"\((Cream|Pink|Charcoal)\)", p["name"])
        base = re.sub(r"\s*\(.*\)$", "", re.sub(r"\s*\((Cream|Pink|Charcoal)\)", "", p["name"])).strip()
        it = g.setdefault(base, {"base": base, "price": p["price"] / 100, "img": p.get("image"), "opts": [], "colors": [], "desc": p.get("description") or "", "ok": False})
        v = p.get("variant")
        if c and c.group(1) not in it["colors"]: it["colors"].append(c.group(1))
        if v and "Fan Style" in v: o = v.split(":", 1)[1].strip().strip('"')
        else: o = v
        if o and o not in it["opts"]: it["opts"].append(o)
        q = p.get("quantity")
        if q is None or q - (p.get("issued_count") or 0) > 0: it["ok"] = True
    items = []
    for k in ORDER + sorted(x for x in g if x not in ORDER):
        if k not in g: continue
        it = g[k]; name, line = LINES.get(k, (k, it["desc"][:90]))
        sizes = sort_sizes([o for o in it["opts"] if o in SIZES])
        non_size = [o for o in it["opts"] if o not in SIZES]
        opts = it["colors"] or (sizes if sizes else non_size)
        row = {"name": name, "price": it["price"], "line": line, "img": it["img"], "opts": opts, "avail": "on_sale" if it["ok"] else "sold_out"}
        if sizes:
            row["sizes"] = sizes
        items.append(row)
    if not items: raise RuntimeError("no store items")
    mp = os.path.join(os.path.dirname(os.path.abspath(path)), "merch.json")
    json.dump({"generated": int(time.time()), "store": STORE, "items": items}, open(mp + ".tmp", "w"), indent=1)
    os.replace(mp + ".tmp", mp)
    print(len(items), "merch cards ->", mp)
try:
    build_merch()
except Exception as ex:  # keep last good merch.json
    print("merch skipped:", type(ex).__name__, ex)
