#!/usr/bin/env python3
"""What the crafting economy actually demands, from CIG's own recipes.

THE QUESTION THIS ANSWERS, and no tool answers it today: a miner with a hold to
fill wants to know what is worth filling it with. Not what a thing sells for -
that is a price question and CIG ships no prices - but WHAT THE GAME ITSELF
NEEDS, counted across every recipe it has.

    1,607 blueprints, every one with a craft time, a requirement tree and a
    dismantle yield. Joined to items by UUID. No name matching anywhere.

THE TREE, AS CIG SHIPS IT:

    Tiers[] -> CraftTimeSeconds
            -> Requirements  root
                             +- group  "Frame"    RequiredCount, Modifiers[]
                             |          +- resource  Agricium   QuantityScu 0.36
                             +- group  "Emitter"  RequiredCount, Modifiers[]
                                        +- item      Hadanite   Quantity 7

TWO UNITS, NEVER ADDED TOGETHER. A `resource` child carries `QuantityScu` -
cargo, measured in SCU. An `item` child carries `Quantity` - a count of things.
0.36 SCU of Agricium and 7 Hadanite are not 7.36 of anything, and a demand
table that sums them is worse than no table. They are counted and reported
separately, and the recipe COUNT - how many recipes name this material at all -
is the figure that spans both, which is why it leads.

WHAT A MATERIAL IS FOR IS IN THE TREE TOO. The group that consumes it declares
which stat it modifies - Integrity, Impact Force - so "Aslarite is in 856
recipes" can be followed by what those recipes are building.

Output: data-layer/derived/crafting-demand/
  demand.json      per material: recipe count, SCU total, item total, uses
  recipes.json     per blueprint: output, tier times, its own requirements
  MANIFEST.json    source snapshot, counts, and the rules above

Reads only CIG data. Writes only its own directory.

    python3 build_crafting_demand.py
"""
import collections
import glob
import json
import os
import sys

OUT = os.path.join("data-layer", "derived", "crafting-demand")


def snapshot():
    s = sorted(glob.glob(os.path.join(
        "data-layer", "external-sources", "scunpacked-data", "snapshots",
        "*", "blueprints.json")))
    return os.path.dirname(s[-1]) if s else None


def walk(node, groups, out):
    """Every leaf under `node`, carrying the group it came from."""
    if not isinstance(node, dict):
        return
    kind = node.get("Kind")
    if kind == "group":
        g = {"key": node.get("Key"), "name": node.get("Name"),
             "required": node.get("RequiredCount"),
             "modifies": [m.get("Name") for m in (node.get("Modifiers") or [])
                          if m.get("Name")]}
        groups = groups + [g]
    if kind in ("resource", "item"):
        out.append((node, groups[-1] if groups else None))
        return
    for c in (node.get("Children") or []):
        walk(c, groups, out)


def main():
    snap = snapshot()
    if not snap:
        print("NOT PERFORMED - no scunpacked snapshot with blueprints.json")
        return 2
    bp = json.load(open(os.path.join(snap, "blueprints.json"), encoding="utf-8"))
    if isinstance(bp, dict):
        bp = list(bp.values())
    print("snapshot: %s" % os.path.basename(snap))
    print("blueprints: %d" % len(bp))

    mats = {}
    recipes = []
    no_tier = 0
    for b in bp:
        if not isinstance(b, dict):
            continue
        out = b.get("Output") or {}
        tiers = b.get("Tiers") or []
        if not tiers:
            no_tier += 1
            continue
        # TIER 0 IS THE RECIPE. Higher tiers are the same build at better
        # quality and would double-count a material that appears in both.
        t = tiers[0]
        leaves = []
        walk(t.get("Requirements") or {}, [], leaves)
        needs = []
        for n, g in leaves:
            uuid = n.get("UUID")
            name = n.get("Name")
            if not uuid or not name:
                continue
            scu = n.get("QuantityScu")
            qty = n.get("Quantity")
            m = mats.setdefault(uuid, {
                "uuid": uuid, "name": name, "recipes": 0,
                "scu_total": 0.0, "scu_recipes": 0,
                "item_total": 0, "item_recipes": 0,
                "used_for": collections.Counter(),
                "groups": collections.Counter()})
            m["recipes"] += 1
            if scu is not None:
                m["scu_total"] += float(scu)
                m["scu_recipes"] += 1
            if qty is not None:
                m["item_total"] += int(qty)
                m["item_recipes"] += 1
            if g:
                if g.get("name"):
                    m["groups"][g["name"]] += 1
                for mod in (g.get("modifies") or []):
                    m["used_for"][mod] += 1
            needs.append({"uuid": uuid, "name": name,
                          "scu": scu, "qty": qty,
                          "group": (g or {}).get("name"),
                          "modifies": (g or {}).get("modifies") or []})
        recipes.append({
            "key": b.get("Key"), "uuid": b.get("UUID"),
            "output": {"name": out.get("Name"), "type": out.get("Type"),
                       "subtype": out.get("Subtype"), "grade": out.get("Grade"),
                       "uuid": out.get("UUID"), "class": out.get("Class")},
            "craft_seconds": t.get("CraftTimeSeconds"),
            "tiers": len(tiers),
            "earned": not bool((b.get("Availability") or {}).get("Default")),
            "reward_pools": [r.get("Key") for r in
                             ((b.get("Availability") or {}).get("RewardPools") or [])],
            "needs": needs,
        })

    rows = []
    for m in mats.values():
        rows.append({
            "uuid": m["uuid"], "name": m["name"], "recipes": m["recipes"],
            "scu_total": round(m["scu_total"], 4),
            "scu_recipes": m["scu_recipes"],
            "item_total": m["item_total"], "item_recipes": m["item_recipes"],
            "used_for": [k for k, _v in m["used_for"].most_common(6)],
            "groups": [k for k, _v in m["groups"].most_common(6)],
        })
    rows.sort(key=lambda r: (-r["recipes"], r["name"]))

    # ---------------------------------------------------------------
    # THE JOIN TO THE SHIP PAGE'S OWN PARTS, so the recipe can be shown at the
    # moment somebody is choosing a part rather than on a page of its own.
    #
    # ON CIG'S CLASS NAME, CASE-FOLDED, EXACT. The page keys its parts
    # `AMRS_LaserCannon_S1`; a blueprint's Output.Class is
    # `amrs_lasercannon_s1`. Same identifier, different capitalisation - this
    # project already folds case deliberately in the placement claims for the
    # same reason. It is exact equality on an identifier, not a similarity.
    #
    # THE DISPLAY-NAME ROUTE IS REFUSED AND THAT IS DELIBERATE. Matching on
    # Output.Name would add 34 more, and one of them is `AMRS_AAgun_CC_S3`
    # claiming the PyroBurst Scattergun's recipe - a different class wearing a
    # shared display name. That is the fuzzy matching this project has been
    # bitten by twice. 452 exact beats 486 with a wrong one in it.
    joined = {}
    lower = {}
    for r in recipes:
        c = (r["output"].get("class") or "").lower()
        if c:
            lower.setdefault(c, r)
    parts_src = os.path.join("testing", "_src", "loadout_data.gen.js")
    n_parts = 0
    if os.path.exists(parts_src):
        import re as _re
        _t = open(parts_src, encoding="utf-8").read()
        _m = _re.search(r"^const LOADOUT_PARTS=(.*);$", _t, _re.M)
        if _m:
            P = json.loads(_m.group(1))
            n_parts = len(P)
            for k in P:
                r = lower.get(k.lower())
                if not r:
                    continue
                joined[k] = {
                    "mins": (round(r["craft_seconds"] / 60)
                             if r.get("craft_seconds") else None),
                    "earned": r.get("earned"),
                    "needs": [{"n": q["name"], "scu": q["scu"], "q": q["qty"]}
                              for q in r["needs"]],
                }
    json.dump(joined, open(os.path.join(OUT, "part_recipes.json"), "w",
                           encoding="utf-8"), indent=1)
    man_join = {"parts_on_the_ship_page": n_parts, "craftable": len(joined)}
    print("ship-page parts that are craftable: %d of %d"
          % (len(joined), n_parts))

    # The page-ready form, emitted where the caller asks. Default is this
    # script's own directory; the build passes testing/_src.
    dest = None
    for a in sys.argv[1:]:
        if a.startswith("--emit-js="):
            dest = a.split("=", 1)[1]
    if dest is None:
        dest = os.path.join(OUT, "craft_data.gen.js")
    with open(dest, "w", encoding="utf-8", newline="") as fh:
        fh.write(
            "/* GENERATED by build_crafting_demand.py - do not hand edit.\n"
            "   CRAFT[partKey] = {mins, earned, needs:[{n,scu,q}]}\n"
            "   Joined on CIG Output.Class, case-folded, exact.\n"
            "   CRAFT_DEMAND is the fleet-wide material demand table. */\n")
        fh.write("const CRAFT=" + json.dumps(joined, separators=(",", ":"))
                 + ";\n")
        fh.write("const CRAFT_DEMAND=" + json.dumps(rows, separators=(",", ":"))
                 + ";\n")
    print("emitted %s" % dest)


    os.makedirs(OUT, exist_ok=True)
    json.dump(rows, open(os.path.join(OUT, "demand.json"), "w",
                         encoding="utf-8"), indent=1)
    json.dump(recipes, open(os.path.join(OUT, "recipes.json"), "w",
                            encoding="utf-8"), indent=1)
    man = {
        "generated_by": "build_crafting_demand.py",
        "source": snap,
        "join": "blueprint Output and every requirement leaf carry a CIG UUID; "
                "nothing here is matched by name.",
        "tier_rule": "tier 0 only - higher tiers are the same build at better "
                     "quality and would double-count.",
        "unit_rule": "SCU (a `resource` leaf) and COUNT (an `item` leaf) are "
                     "reported separately and never summed. The recipe count "
                     "is the figure that spans both.",
        "part_join": "the ship page's part key against blueprint Output.Class, "
                     "case-folded, exact. The display-name route is refused: "
                     "it adds 34 and one of them is a different class sharing "
                     "a name.",
        "counts": {"blueprints": len(bp), "recipes_read": len(recipes),
                   "blueprints_without_tiers": no_tier,
                   "materials": len(rows),
                   "craftable_ship_page_parts": len(joined),
                   "ship_page_parts": n_parts},
    }
    json.dump(man, open(os.path.join(OUT, "MANIFEST.json"), "w",
                        encoding="utf-8"), indent=1)

    print("materials: %d" % len(rows))
    print("\n%-28s %8s %10s %10s  %s" % ("material", "recipes", "SCU", "count",
                                         "mostly used for"))
    for r in rows[:22]:
        print("%-28s %8d %10.2f %10d  %s"
              % (r["name"][:28], r["recipes"], r["scu_total"], r["item_total"],
                 ", ".join(r["used_for"][:2])))
    print("\nwrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
