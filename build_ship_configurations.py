#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_ship_configurations.py - THE THREE CONCRETE CASES, and nothing else.

Sleven's ruling of 2026-08-16 (docs/DECISION_hull-configuration-acquisition-
2026-08-16.md): a ship is a HULL, a CONFIGURATION, and a LIST of ways to get it.

The ruling is explicit that the schema must NOT be designed first:

    "Build two or three concrete cases before generalising into a shared shape.
     ... Build those three, then let the shared shape come out of what they
     actually needed."

So this script builds exactly three, from data, and reports what each one
needed. It does not touch app/models.py, it adds no migration, and it does not
loop over the other 86 game-only files. Generalising is the next decision, and
it is Sleven's to take with these three in front of him.

THE THREE CASES
===============

    1. Drake Clipper           hull in files, Wikelo config in files (4.10)
    2. Aegis Tiburon           hull in files, Wikelo config ANNOUNCED ONLY (4.11)
    3. Aegis Sabre Firebird    one of the 53 component-only editions

Case 2 is the one that earns its place. The 4.11 Tiburon reward does not exist
in any file we hold, so it is the case that decides whether this shape can hold
a configuration that is KNOWN but not yet SHIPPED - without inventing component
changes to fill the hole. If a shape can only describe what has already shipped,
it will be wrong every time a patch is announced.

WHAT IS EVIDENCE HERE AND WHAT IS NOT
=====================================

Every acquisition route carries `verified` and the evidence behind it. Three
sources, all of them files in this repo:

    shop      UEX vehicles_purchases_prices_all - a terminal and a price
    pledge    the site's own published row - pledge_price_usd and pledge_url
    factory   the snapshot itself - the components differ from stock in the
              shipped file, which is what "arrives fitted" means

    trade     NOT VERIFIABLE FROM ANY FILE WE HOLD. The Wikelo terminals are
              typed `fuel` and no vehicle price references them (finding
              §2/§6). CIG's roadmap says the ships are a reward for a Wikelo
              contract; that is a statement by the publisher, not a row in a
              file. It is recorded as `verified: false` with the roadmap as its
              stated source, and it must stay that way until somebody has been
              there.

PLACEHOLDER CHURN IS NOT A COMPONENT CHANGE
===========================================

CIG ships `<= PLACEHOLDER =>` entries in its own loadouts, and their class names
differ between a base ship and its edition while both remain placeholders. A
naive diff counts those as refits: the Sabre Firebird shows 11 differing ports,
of which 4 are placeholder-to-placeholder. Counting them would overstate what an
edition actually gives you, on a page whose whole job is to answer exactly that.

They are excluded and counted separately rather than dropped silently.

Rule 15: encodings stated.
"""

import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

SNAPSHOT = "20260801T204744Z"
SNAPDIR = os.path.join(HERE, "data-layer", "external-sources", "scunpacked-data",
                       "snapshots", SNAPSHOT)
SHIPS_JSON = os.path.join(SNAPDIR, "ships.json")
ITEMS_JSON = os.path.join(SNAPDIR, "ship-items.json")

UEX_SNAPSHOT = "20260801T235530Z"
UEX_PRICES = os.path.join(HERE, "data-layer", "external-sources", "uexcorp",
                          "snapshots", UEX_SNAPSHOT,
                          "vehicles_purchases_prices_all.json")

SITE = os.path.join(HERE, "releases", "latest.html")

OUTDIR = os.path.join(HERE, "data-layer", "derived", "ship-configurations")
OUT = os.path.join(OUTDIR, "configurations.json")
MANIFEST = os.path.join(OUTDIR, "MANIFEST.json")

PLACEHOLDER = "<= PLACEHOLDER =>"


def say(line):
    """stdout that survives a ship called San'tok.yai. See rule 15."""
    sys.stdout.buffer.write((line + "\n").encode("utf-8", "backslashreplace"))


def read_json(path, what):
    if not os.path.exists(path):
        sys.exit("MISSING INPUT: %s\n(%s)\nNothing was written - this script "
                 "cannot invent it." % (path, what))
    with io.open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------
# the loadout, flattened by port path
# --------------------------------------------------------------------------

def slots_by_port(ship):
    """{full port path: {class, name, type}} for every fitted entry.

    Keyed on `Path` joined, not on PortId: PortId is positional
    ("loadout.47.loadout.0") and shifts when CIG reorders a file, which would
    make two identical ships look like a hundred refits.
    """
    out = {}

    def walk(node):
        for e in node or []:
            if not isinstance(e, dict):
                continue
            path = "/".join(e.get("Path") or [])
            if path and e.get("ClassName"):
                out[path] = {
                    "class": e.get("ClassName"),
                    "name": e.get("Name"),
                    "type": e.get("Type"),
                }
            walk(e.get("Loadout"))

    walk(ship.get("Loadout"))
    return out


def component_changes(base, edition):
    """What an edition actually swaps, and what only looks like a swap.

    Returns (changes, placeholder_only, ports_compared).
    """
    a, b = slots_by_port(base), slots_by_port(edition)
    changes, placeholder_only = [], 0
    for port in sorted(set(a) | set(b)):
        was, now = a.get(port), b.get(port)
        if (was or {}).get("class") == (now or {}).get("class"):
            continue
        if (was or {}).get("name") == PLACEHOLDER and (now or {}).get("name") == PLACEHOLDER:
            placeholder_only += 1
            continue
        changes.append({
            "port": port,
            "from": {"name": (was or {}).get("name"), "class": (was or {}).get("class")},
            "to": {"name": (now or {}).get("name"), "class": (now or {}).get("class")},
            "type": (now or was or {}).get("type"),
        })
    return changes, placeholder_only, len(set(a) | set(b))


# --------------------------------------------------------------------------
# the routes, each with its evidence
# --------------------------------------------------------------------------

def shop_route(uex_rows, uex_name):
    """route = shop, from UEX terminals and prices.

    An EMPTY result is a result and is returned as such, because "no terminal
    sells this" and "nobody looked" are different facts and the second one must
    never be published as the first.
    """
    hits = [r for r in uex_rows
            if str(r.get("vehicle_name") or "").strip().lower() == uex_name.lower()]
    if not hits:
        return {
            "route": "shop",
            "available": False,
            "verified": True,
            "evidence": "no row for %r in UEX %s (%d vehicle price rows read)"
                        % (uex_name, UEX_SNAPSHOT, len(uex_rows)),
            "note": "an absence in this snapshot, not a claim that it can never "
                    "be bought - a terminal added after the pull would look the "
                    "same from here",
        }
    return {
        "route": "shop",
        "available": True,
        "verified": True,
        "evidence": "UEX %s" % UEX_SNAPSHOT,
        "terminals": sorted({r.get("terminal_name") for r in hits}),
        "price_auec": min(int(r["price_buy"]) for r in hits if r.get("price_buy")),
    }


def site_row(site_html, name):
    """The site's own published row for a ship. HARD FAILS if it is not there.

    Read from releases/latest.html because that IS the live site - not from a
    database this script would have to be trusted to have read correctly.

    THE MISSING-ROW CASE IS A STOP, NOT A SHRUG. The first version returned None
    and let pledge_route report "no pledge price", which is a FALSE statement
    dressed as a cautious one: the Clipper's row says $150 and the site has been
    publishing it for months. The regex was simply wrong - rows start
    `{"id":72,"name":...`, not `{"name":...`.
    """
    m = re.search(r'\{"id":\d+,"name":"%s",.*?\}' % re.escape(name), site_html)
    if not m:
        sys.exit("NO SITE ROW for %r in %s.\nRefusing to describe how a ship is "
                 "obtained while unable to read what the site already says about "
                 "it - a silent 'not available' here would be a false claim, not "
                 "a cautious one." % (name, os.path.relpath(SITE, HERE)))
    return json.loads(m.group(0))


def pledge_route(row):
    if not row or row.get("pledge_price_usd") in (None, ""):
        return {"route": "pledge", "available": False, "verified": False,
                "evidence": "no pledge price on the site's own row"}
    return {
        "route": "pledge",
        "available": True,
        "verified": True,
        "evidence": "the site's own published row in releases/latest.html",
        "price_usd": row.get("pledge_price_usd"),
        "url": row.get("pledge_url"),
    }


def wikelo_trade_route(patch, stated_by):
    """route = trade, and it is NOT verified. Deliberately.

    Every field here is a statement about what CIG said, never about what any
    file shows. The Wikelo terminals in UEX are typed `fuel` and no vehicle
    price references them, so there is nothing in the data to confirm or deny
    this, and the honest record of that is `verified: false` with the claim
    attributed.
    """
    return {
        "route": "trade",
        "available": True,
        "verified": False,
        "where": "Wikelo's Emporium",
        "stated_by": stated_by,
        "patch": patch,
        "evidence": None,
        "why_unverified":
            "The three Wikelo Emporium terminals in UEX are typed `fuel` and no "
            "vehicle price row references them. Nothing in any file we hold "
            "confirms how these ships are obtained. Must be confirmed in game "
            "before it goes on a page.",
    }


def factory_route(changes, source_class):
    """route = factory - the parts are already on it when you get it.

    This one IS verified, and it is the only Wikelo-adjacent thing that is: the
    shipped file has different components from stock. That is a fact about the
    file regardless of how anybody obtains the ship.
    """
    return {
        "route": "factory",
        "available": True,
        "verified": True,
        "evidence": "%s in snapshot %s carries %d component(s) different from "
                    "the base hull" % (source_class, SNAPSHOT, len(changes)),
    }


def livery_candidates(paints, hull_word):
    """Liveries that attach to this hull, by required_tags - never by name.

    WHICH of them is the "unique base livery" CIG's roadmap describes is NOT in
    any file. The candidates are listed and the question is left open rather
    than answered by picking the one with the most likely-sounding name.
    """
    out = []
    for it in paints:
        tags = it.get("required_tags") or []
        if isinstance(tags, str):
            tags = [tags]
        if not any(hull_word.lower() in str(t).lower() for t in tags):
            continue
        nm = it.get("name") or (it.get("stdItem") or {}).get("Name")
        if not nm or nm == PLACEHOLDER:
            continue
        out.append({"name": nm, "event_source": it.get("event_source") or None,
                    "required_tags": tags})
    return sorted(out, key=lambda x: x["name"])


# --------------------------------------------------------------------------

def main():
    ships = read_json(SHIPS_JSON, "the game's own ship records")
    items = read_json(ITEMS_JSON, "the game's own item records")
    uex = read_json(UEX_PRICES, "UEX vehicle purchase prices")
    uex_rows = uex.get("data") if isinstance(uex, dict) else uex
    site_html = io.open(SITE, "r", encoding="utf-8").read()

    by_name = {}
    for s in ships:
        if s.get("Name"):
            by_name.setdefault(s["Name"], s)

    paints = [it for it in items if str(it.get("type") or "").lower().startswith("paint")]

    def need(name):
        if name not in by_name:
            sys.exit("NOT IN THE SNAPSHOT: %r\nRefusing to write a case built on "
                     "a ship this script could not read." % name)
        return by_name[name]

    cases = []

    # ---- CASE 1: the Wikelo reward that HAS shipped -----------------------
    hull = need("Drake Clipper")
    ed = need("Drake Clipper Wikelo War Special")
    changes, ph, ports = component_changes(hull, ed)
    row = site_row(site_html, "Clipper")
    cases.append({
        "case": "drake-clipper",
        "why_this_case": "The 4.10 Wikelo reward, and it is already in the game "
                         "files - so it is the case that shows what a shipped "
                         "configuration looks like end to end.",
        "hull": {
            "name": "Drake Clipper",
            "site_name": (row or {}).get("name"),
            "class_name": hull.get("ClassName"),
            "in_files": True,
        },
        "configurations": [
            {
                "id": "stock",
                "display": "Standard",
                "in_files": True,
                "source_class": hull.get("ClassName"),
                "component_changes": [],
                "livery": None,
                "acquisition": [
                    shop_route(uex_rows, "Clipper"),
                    pledge_route(row),
                ],
            },
            {
                "id": "wikelo-war-special",
                "display": "Wikelo War Special",
                "in_files": True,
                "source_class": ed.get("ClassName"),
                "ports_compared": ports,
                "component_changes": changes,
                "placeholder_only_changes": ph,
                "livery": {
                    "stated_by": "CIG roadmap, 4.10 - 'a unique base livery'",
                    "identified_in_files": False,
                    "why": "No livery is recorded on the ship record and no paint "
                           "is marked as belonging to this edition. The hull's "
                           "liveries are listed as candidates; picking one would "
                           "be a guess.",
                    "candidates": livery_candidates(paints, "Clipper"),
                },
                "acquisition": [
                    wikelo_trade_route("4.10", "CIG roadmap, read by CIC 2026-08-16"),
                    factory_route(changes, ed.get("ClassName")),
                ],
            },
        ],
    })

    # ---- CASE 2: the Wikelo reward that has NOT shipped -------------------
    hull = need("Aegis Tiburon")
    row = site_row(site_html, "Tiburon")
    cases.append({
        "case": "aegis-tiburon",
        "why_this_case": "The 4.11 reward exists in CIG's roadmap and in NO file "
                         "we hold. It is the case that decides whether this shape "
                         "can hold a configuration that is known but not yet "
                         "shipped, without inventing the parts of it we cannot "
                         "see.",
        "hull": {
            "name": "Aegis Tiburon",
            "site_name": (row or {}).get("name"),
            "class_name": hull.get("ClassName"),
            "in_files": True,
        },
        "configurations": [
            {
                "id": "stock",
                "display": "Standard",
                "in_files": True,
                "source_class": hull.get("ClassName"),
                "component_changes": [],
                "livery": None,
                "acquisition": [
                    shop_route(uex_rows, "Tiburon"),
                    pledge_route(row),
                ],
            },
            {
                "id": "wikelo-4-11",
                "display": "Wikelo reward (announced, 4.11)",
                # THE FIELD THIS CASE EXISTS FOR.
                "in_files": False,
                "source_class": None,
                "component_changes": None,
                "component_changes_unknown_because":
                    "The configuration is announced and not shipped. There is no "
                    "file to diff. An empty list would say 'nothing is changed', "
                    "which is a different and false claim - so it is null.",
                "livery": {
                    "stated_by": "CIG roadmap, 4.11 - identical wording to 4.10",
                    "identified_in_files": False,
                    "why": "Nothing to identify yet.",
                    "candidates": livery_candidates(paints, "Tiburon"),
                },
                "acquisition": [
                    wikelo_trade_route("4.11", "CIG roadmap, read by CIC 2026-08-16"),
                ],
            },
        ],
    })

    # ---- CASE 3: one of the 53 component-only editions --------------------
    hull = need("Aegis Sabre Firebird")
    ed = need("Aegis Sabre Firebird Wikelo War Special")
    changes, ph, ports = component_changes(hull, ed)
    row = site_row(site_html, "Sabre Firebird")
    cases.append({
        "case": "aegis-sabre-firebird",
        "why_this_case": "One of the 53 editions that differ ONLY in fitted "
                         "components. These have been waiting since 2026-08-02 "
                         "for somewhere to live, and this is the shape they were "
                         "waiting for.",
        "hull": {
            "name": "Aegis Sabre Firebird",
            "site_name": (row or {}).get("name"),
            "class_name": hull.get("ClassName"),
            "in_files": True,
        },
        "configurations": [
            {
                "id": "stock",
                "display": "Standard",
                "in_files": True,
                "source_class": hull.get("ClassName"),
                "component_changes": [],
                "livery": None,
                "acquisition": [
                    shop_route(uex_rows, "Sabre Firebird"),
                    pledge_route(row),
                ],
            },
            {
                "id": "wikelo-war-special",
                "display": "Wikelo War Special",
                "in_files": True,
                "source_class": ed.get("ClassName"),
                "ports_compared": ports,
                "component_changes": changes,
                "placeholder_only_changes": ph,
                "livery": None,
                "acquisition": [
                    wikelo_trade_route(None, "the edition exists in the game files; "
                                             "how it is obtained is not recorded there"),
                    factory_route(changes, ed.get("ClassName")),
                ],
            },
        ],
    })

    if not os.path.isdir(OUTDIR):
        os.makedirs(OUTDIR)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"cases": cases}, fh, indent=1, ensure_ascii=False, sort_keys=False)
        fh.write("\n")

    manifest = {
        "dataset": "ship-configurations",
        "produced_by": "build_ship_configurations.py",
        "ruling": "docs/DECISION_hull-configuration-acquisition-2026-08-16.md",
        "what_this_is": "THREE CONCRETE CASES built to the hull / configuration / "
                        "routes ruling, so the shared shape can be taken from what "
                        "they needed rather than designed in advance.",
        "what_this_is_NOT": "Not a schema, not a migration, and not the other 86 "
                            "game-only files. Generalising is the next decision "
                            "and it is Sleven's.",
        "sources": {
            "scunpacked snapshot": SNAPSHOT,
            "uex snapshot": UEX_SNAPSHOT,
            "site rows": "releases/latest.html",
        },
        "unverified_by_design": [
            "route = trade. The Wikelo terminals are typed `fuel` and no vehicle "
            "price references them. CIG's roadmap is the only source and it is "
            "attributed as such.",
            "which livery is the edition's. No file marks one.",
        ],
    }
    with io.open(MANIFEST, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=1, ensure_ascii=False)
        fh.write("\n")

    say("wrote %s" % os.path.relpath(OUT, HERE))
    for c in cases:
        say("")
        say("  %s" % c["case"])
        for cfg in c["configurations"]:
            ch = cfg["component_changes"]
            if ch is None:
                desc = "component changes UNKNOWN - not in any file yet"
            elif not ch:
                desc = "stock"
            else:
                desc = "%d component(s) swapped" % len(ch)
                if cfg.get("placeholder_only_changes"):
                    desc += ", %d placeholder-only difference(s) excluded" \
                            % cfg["placeholder_only_changes"]
            routes = ", ".join("%s%s" % (r["route"], "" if r.get("verified") else "?")
                               for r in cfg["acquisition"])
            say("    %-28s %-58s routes: %s" % (cfg["id"], desc, routes))
    say("")
    say("  a route marked ? is NOT verified from any file - see the manifest")


if __name__ == "__main__":
    main()
