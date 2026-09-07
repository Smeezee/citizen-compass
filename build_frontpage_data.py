#!/usr/bin/env python3
"""Joins the front page's 254 ships to hull dimensions, traced outlines and the
real starmap position of every dealer. Emits one payload for the concept pages.

THE JOIN IS EXACT, under one stated normalisation and no others:

    testing/index.html  SHIPS[].name          the site's own name  (254)
      -> data-layer/ship_resolution.json      site -> game file    (221 matched)
      -> case-folded stem == hull key         219 land, 2 refused
      -> silhouettes.json                     201 have a traced outline

Case folding is exact matching under a normalisation, not fuzzy matching, and it
was checked first: ZERO hull keys and ZERO silhouette keys collide when folded.
The two that do not land are named in the output rather than guessed at.

Writer: C1.
"""
import json, re, collections, os

OUT = "data-layer/derived/main-page-concepts/frontpage_data.json"

fp = json.loads(re.search(r'(?:var|const)\s+SHIPS\s*=\s*(\[.*?\])\s*;\s*\n',
      open('testing/index.html', encoding='utf-8').read(), re.S).group(1))
res = json.load(open('data-layer/ship_resolution.json', encoding='utf-8'))
sil = json.load(open('data-layer/derived/ship-silhouettes/silhouettes.json'))['ships']
dd  = {s['k']: s for s in json.loads(re.search(r'id="DATA"[^>]*>(.*?)</script>',
      open('data-layer/derived/main-page-concepts/five-main-pages.html',
           encoding='utf-8').read(), re.S).group(1))}

fold = collections.defaultdict(list)
for k in dd: fold[k.casefold()].append(k)
bad = [v for v in fold.values() if len(v) > 1]
if bad: raise SystemExit("REFUSED: hull keys collide when case-folded: %s" % bad[:3])

site2hull, refused = {}, []
for m in res['matched']:
    stem = m['file'][:-5] if m['file'].endswith('.json') else m['file']
    c = stem.casefold()
    if c in fold: site2hull[m['site']] = fold[c][0]
    else: refused.append({"site": m['site'], "file": stem})

ents = json.load(open('data-layer/derived/starmap-routes/entities.json', encoding='utf-8'))
def where(nm):
    for x in ents:
        if x['name'] == nm and x.get('positions'):
            p = x['positions'][0]
            return {"x": p['x'], "y": p['y'], "system": p.get('system')}
    return None

DEALERS = [
  {"k": "New Deal",          "place": "Lorville",     "body": "Hurston"},
  {"k": "Astro Armada",      "place": "Area18",       "body": "ArcCorp"},
  {"k": "Crusader Showroom", "place": "Orison",       "body": "Crusader"},
  {"k": "Teach's",           "place": "Levski",       "body": "Delamar"},
  {"k": "Buy & Fly",         "place": "Ruin Station", "body": "Pyro"},
]
for d in DEALERS:
    p = where(d["place"])
    if not p: raise SystemExit("REFUSED: no starmap position for " + d["place"])
    d.update(p)

try:
    DPRICE = json.load(open("data-layer/derived/ship-prices/ship_dealer_prices.json",
                            encoding="utf-8"))["prices"]
except FileNotFoundError:
    DPRICE = {}

ships, no_hull, no_out = [], 0, 0
for r in fp:
    hk = site2hull.get(r['name'])
    h  = dd.get(hk) if hk else None
    s  = sil.get(hk) if hk else None
    if not h: no_hull += 1
    if not s: no_out += 1
    ships.append({
      "id": r['id'], "n": r['name'], "m": r['manufacturer'], "role": r['role'],
      "status": r['status'], "conf": r['confidence'],
      "auec": r.get('auec_price'), "usd": r.get('pledge_price_usd'),
      "url": r.get('pledge_url'), "deal": r.get('dealers') or [],
      # PER-DEALER PRICES. The same ship costs different amounts at different
      # shops - measured 2026-08-31 across 63 ships, 47 of which vary. A page
      # that prints one number beside three shop names is telling two of them
      # a lie. Absent means we have no per-dealer figure and the single price
      # still stands; it does NOT mean they are all the same.
      "dprice": DPRICE.get(r['name'], {}),
      "note": r.get('notes'), "patch": r.get('last_verified_patch'),
      "hull": hk,
      "L": h.get('L') if h else None, "crew": h.get('crew') if h else None,
      "cargo": h.get('cargo') if h else None, "vmax": h.get('vmax') if h else None,
      "career": h.get('career') if h else None,
      "d": s['d'] if s else None, "hb": s.get('hb') if s else None,
    })

payload = {"generated_by": "build_frontpage_data.py",
           "join": "site name -> ship_resolution.matched -> case-folded hull key (0 collisions)",
           "dealers": DEALERS, "ships": ships,
           "refused_join": refused,
           "counts": {"front_page": len(fp), "with_hull": len(fp)-no_hull,
                      "with_outline": len(fp)-no_out,
                      "with_per_dealer_prices": sum(1 for s in ships if s["dprice"]),
                      "prices_that_vary": sum(1 for s in ships
                                              if len(set(s["dprice"].values())) > 1)}}
json.dump(payload, open(OUT, 'w', encoding='utf-8'), separators=(',', ':'))
print("front page ships %d   with hull figures %d   with traced outline %d"
      % (len(fp), len(fp)-no_hull, len(fp)-no_out))
print("dealers placed from the game's own starmap: %d   systems: %s"
      % (len(DEALERS), sorted({d['system'] for d in DEALERS})))
print("refused joins (named, not guessed): %s" % [x['site'] for x in refused])
print("wrote %s (%.2f MB)" % (OUT, os.path.getsize(OUT)/1e6))
