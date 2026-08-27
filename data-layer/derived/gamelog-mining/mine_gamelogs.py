#!/usr/bin/env python3
# mine_gamelogs.py - extract structured facts from Star Citizen Game.log archives.
#
# WHAT THIS DELIBERATELY DOES NOT DO
#
# It never emits a raw log line, never emits a "context" field, and never emits
# an identifier. The standing rule is that player handle, shard id, session id
# and other players' names are stripped BEFORE the file exists - not filtered
# afterwards - so this only ever writes fields it was built to write, by name.
#
# playerId is stripped even though it is Sleven's own. It is an identifier and
# the rule has no exception for the person running it.
#
# Encoding is stated on every open (hard rule 15). Logs are UTF-8 with the
# occasional stray byte, so errors="replace" - a bad byte must not silently
# truncate a session.

import json
import os
import re
import sys
from collections import Counter, defaultdict

# --- the patterns ----------------------------------------------------------
#
# Matched on the PAYLOAD SHAPE, not on the emitting class name. CIG renamed
# CEntityComponentShopUIProvider -> CEntityComponentShoppingProvider between
# 4.9 and 4.10 and added a field; a parser keyed on the class name would have
# silently stopped. The class name is captured as data so a rename is VISIBLE
# in the output instead of being fatal.

RE_TS = re.compile(r"^<([0-9T:.\-]+Z)>")
RE_CLASS = re.compile(r"<(CEntityComponent[A-Za-z]+)::([A-Za-z_]+)>")

# ONE pattern for all four transaction families. They share a field grammar,
# so keying on the payload name rather than the class name means a new family
# (or a renamed class) is picked up automatically and shows up as a new "kind"
# in the output rather than as silence.
#
#   SShopBuyRequest             item purchase
#   SShopSellRequest            item sale        <- the SELL prices we had none of
#   SShopCommodityBuyRequest    commodity purchase
#   SShopCommoditySellRequest   commodity sale
RE_TXN = re.compile(r"S(Shop(?:Commodity)?)(Buy|Sell)Request\s*-\s*(?P<body>.*)")
RE_FIELD = re.compile(r"([A-Za-z_]+)\[([^\]]*)\]")

RE_LOCATION = re.compile(r"requested inventory for Location\[([^\]]+)\]")
RE_QT = re.compile(r"Successfully calculated route to (\S+).*?fuel estimate ([0-9.]+)")
RE_SHIP = re.compile(
    r"\b((?:AEGS|ANVL|ARGO|BANU|CNOU|CRUS|DRAK|ESPR|GAMA|GRIN|KRIG|MISC|MRAI|"
    r"ORIG|RSI|TMBL|VNCL|XIAN|XNAA|GLSN|APAR)_[A-Za-z0-9_]+?)_\d{6,}")
RE_BUILD = re.compile(r"Changelist:\s*(\d+)")
RE_ENVTAG = re.compile(r"\[Trace\] Environment:\s*(\S+)")
RE_RESOLUTION = re.compile(r"Change resolution:\s*(\d+x\d+)\s*\(([^)]+)\)")
RE_D3D_LEVEL = re.compile(r"D3D Adapter: FeatureLevel = (.+)")
RE_VULKAN = re.compile(r"\bVulkan\b")

# Long digit runs are entity ids, and they turn up EMBEDDED in otherwise
# harmless-looking names - a quantum destination came through as
# "PartyMemberMarker_200179793657", which is another player's entity id
# wearing a label. Found by audit, not by design, which is the point of
# auditing. Everything free-text that reaches an output file goes through
# scrub_ids() first.
RE_EMBEDDED_ID = re.compile(r"\d{6,}")


def scrub_ids(text):
    """Replace any run of 6+ digits with a marker. Never returns an id."""
    return RE_EMBEDDED_ID.sub("<id>", text)

# Fields we are willing to emit. Anything not on this list is dropped, so a new
# CIG field cannot leak an identifier into the dataset by surprise.
TXN_KEEP = {"shopName", "kioskId", "client_price", "itemClassGUID",
            "itemName", "quantity", "currencyType", "amount", "resourceGUID"}

# Never emit these, whatever else changes.
FORBIDDEN = {"playerId", "shopId", "sessionId", "shardId", "nickname",
             "node_id", "playerGEID", "accountId", "geid"}


def parse_log(path):
    """Return one session record. Reads the file once."""
    name = os.path.basename(path)
    rec = {
        "source_file": name,
        "channel": "PTU" if "PTU" in path else "LIVE",
        "build": None,
        "environment": None,
        "renderer": None,
        "display_mode": None,
        "resolution": None,
        "buys": [],
        "commodity_sells": [],
        "locations": [],
        "quantum_routes": [],
        "ships_seen": [],
        "shop_classes": Counter(),
    }
    saw_vulkan = False
    locations, ships = set(), set()
    routes = {}

    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if rec["build"] is None:
                m = RE_BUILD.search(line)
                if m:
                    rec["build"] = m.group(1)
            if rec["environment"] is None:
                m = RE_ENVTAG.search(line)
                if m:
                    rec["environment"] = m.group(1)
            if rec["resolution"] is None:
                m = RE_RESOLUTION.search(line)
                if m:
                    rec["resolution"] = m.group(1)
                    rec["display_mode"] = m.group(2).split(" at ")[0].strip()
            if rec["renderer"] is None:
                m = RE_D3D_LEVEL.search(line)
                if m:
                    rec["renderer"] = m.group(1).strip()
            if not saw_vulkan and RE_VULKAN.search(line):
                saw_vulkan = True

            cm = RE_CLASS.search(line)
            if cm and "Shop" in cm.group(1):
                rec["shop_classes"][f"{cm.group(1)}::{cm.group(2)}"] += 1

            ts = RE_TS.match(line)
            ts = ts.group(1) if ts else None

            tm = RE_TXN.search(line)
            if tm:
                fields = dict(RE_FIELD.findall(tm.group("body")))
                row = {k: v for k, v in fields.items()
                       if k in TXN_KEEP and k not in FORBIDDEN}
                if row:
                    row["ts"] = ts
                    row["side"] = tm.group(2).lower()          # buy | sell
                    row["market"] = ("commodity"
                                     if tm.group(1).endswith("Commodity")
                                     else "item")
                    row["emitted_by"] = cm.group(1) if cm else None
                    for k in ("shopName", "itemName"):
                        if k in row:
                            row[k] = scrub_ids(row[k])
                    if row["market"] == "commodity":
                        rec["commodity_sells"].append(row)
                    else:
                        rec["buys"].append(row)

            lm = RE_LOCATION.search(line)
            if lm:
                locations.add(scrub_ids(lm.group(1)))

            qm = RE_QT.search(line)
            if qm:
                routes[scrub_ids(qm.group(1))] = float(qm.group(2))

            for s in RE_SHIP.findall(line):
                ships.add(s)

    if saw_vulkan and not rec["renderer"]:
        rec["renderer"] = "Vulkan"
    elif saw_vulkan:
        rec["renderer"] += " (+Vulkan mentioned)"

    rec["locations"] = sorted(locations)
    rec["ships_seen"] = sorted(ships)
    rec["quantum_routes"] = [{"destination": k, "fuel_estimate": v}
                             for k, v in sorted(routes.items())]
    rec["shop_classes"] = dict(rec["shop_classes"])
    return rec


def main(roots, outdir):
    sessions = []
    files = []
    for root in roots:
        if not os.path.isdir(root):
            continue
        for f in sorted(os.listdir(root)):
            if f.lower().endswith(".log"):
                files.append(os.path.join(root, f))

    for p in files:
        try:
            sessions.append(parse_log(p))
        except Exception as e:  # a bad file must not kill the run, but must show
            sessions.append({"source_file": os.path.basename(p),
                             "parse_error": str(e)})

    os.makedirs(outdir, exist_ok=True)

    # --- flatten -----------------------------------------------------------
    buys, sells = [], []
    locations = Counter()
    ships = Counter()
    routes = {}
    classes = Counter()
    builds = Counter()

    for s in sessions:
        if s.get("parse_error"):
            continue
        b = s.get("build")
        builds[b] += 1
        for row in s["buys"]:
            row = dict(row)
            row["build"] = b
            row["channel"] = s["channel"]
            buys.append(row)
        for row in s["commodity_sells"]:
            row = dict(row)
            row["build"] = b
            row["channel"] = s["channel"]
            sells.append(row)
        for l in s["locations"]:
            locations[l] += 1
        for sh in s["ships_seen"]:
            ships[sh] += 1
        for r in s["quantum_routes"]:
            routes.setdefault(r["destination"], set()).add(r["fuel_estimate"])
        for k, v in s["shop_classes"].items():
            classes[k] += v

    def w(nm, obj):
        p = os.path.join(outdir, nm)
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=2, ensure_ascii=False)
        return p

    w("shop_transactions.json", {
        "note": "Item-market transactions. 'side' is buy or sell. client_price "
                "is what the client sent, per unit, in the shop's currency. "
                "The SELL rows are the dataset this project previously had "
                "none of. No identifiers.",
        "count": len(buys),
        "by_side": dict(Counter(r["side"] for r in buys)),
        "rows": buys})
    w("commodity_transactions.json", {
        "note": "Commodity-market transactions. 'amount' is the QUANTITY the "
                "client offered or requested, NOT a price - there is no unit "
                "price in this line and it must not be inferred from one.",
        "count": len(sells),
        "by_side": dict(Counter(r["side"] for r in sells)),
        "rows": sells})
    w("locations.json", {
        "note": "Location names seen in RequestLocationInventory, with the "
                "number of sessions each appeared in.",
        "count": len(locations),
        "rows": [{"location": k, "sessions": v}
                 for k, v in locations.most_common()]})
    w("ships_seen.json", {
        "note": "Ship class identifiers observed. Instance ids stripped.",
        "count": len(ships),
        "rows": [{"ship_class": k, "sessions": v}
                 for k, v in ships.most_common()]})
    w("quantum_routes.json", {
        "note": "Destination -> observed fuel estimates. Multiple values mean "
                "the cost varied by origin; that is real, not an error.",
        "count": len(routes),
        "rows": [{"destination": k, "fuel_estimates": sorted(v)}
                 for k, v in sorted(routes.items())]})
    w("shop_class_names.json", {
        "note": "Every shop-related emitting class seen, with counts. This is "
                "the early-warning for a CIG rename: a name that stops "
                "appearing in new builds is a parser about to go silent.",
        "rows": [{"class": k, "lines": v} for k, v in classes.most_common()]})

    manifest = {
        "generated_by": "mine_gamelogs.py",
        "source": "Star Citizen Game.log archives, LIVE and PTU logbackups",
        "sessions_read": len(sessions),
        "parse_errors": sum(1 for s in sessions if s.get("parse_error")),
        "builds": [{"build": k, "sessions": v}
                   for k, v in sorted(builds.items(), key=lambda x: (x[0] or ""))],
        "privacy": "No playerId, shopId, session id, shard id, account id or "
                   "player handle is present in any output file. Only "
                   "explicitly allow-listed fields are emitted; anything CIG "
                   "adds is dropped unless it is added to the allow-list on "
                   "purpose.",
        "totals": {
            "item_txn_rows": len(buys),
            "commodity_txn_rows": len(sells),
            "distinct_locations": len(locations),
            "distinct_ship_classes": len(ships),
            "distinct_qt_destinations": len(routes),
        },
    }
    w("MANIFEST.json", manifest)
    return manifest, buys, sells, locations, ships, routes, classes


if __name__ == "__main__":
    m, *_ = main(sys.argv[1:-1], sys.argv[-1])
    print(json.dumps(m, indent=2))
