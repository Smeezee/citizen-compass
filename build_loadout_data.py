#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_loadout_data.py - real ship loadouts for /loadout, generated not typed.

Reads the scunpacked snapshot and emits testing/_src/loadout_data.gen.js. Same
pattern as build_holo_data.py and build_kb_actions.py: one generator, one
writer, a header naming the script and the snapshot, and a PAGES entry.

It replaces a hand-typed mockup - 4 ships and 16 components, honestly labelled
`.mock` - with 316 real ships.

THE TRIM, WHICH IS THE WHOLE TRICK
==================================

`ship-items.json` carries ~40 fields per record and the page renders about
eight. The field list below was taken from reading every property access in
`loadout.src.html`, NOT from what looked interesting in the data:

    part:  n m t s  dps ehp qt cap cool ir em pw ht
    ship:  n m role hull base slots[]
    slot:  id g t s stock fixed label

If the page does not render it, it is not here. Add a field to the page first,
then add it here.

WHOSE NUMBER IS IT - THE DISTINCTION THE PAGE HAS TO CARRY
==========================================================

Two different kinds of figure end up on that screen and they are NOT the same
claim:

  CIG'S OWN, precomputed for the stock loadout and read directly off
  `ships.json` - `Systems.Weapons.Summary.PilotDps`, `ShieldsTotal.Hp`,
  `Power.*`, `Cooling.*`, `Emission.*`, `Distortion.Pool`. Where CIG publishes
  a number we use CIG's, per the order.

  OURS, summed from the fitted parts, which is what has to happen the moment a
  visitor swaps a component - CIG cannot have precomputed a loadout that did
  not exist until the user clicked.

Both are emitted. `cig` carries CIG's, the page sums parts for anything
customised, and the generator REPORTS the match rate between the two so a
disagreement is a finding rather than something nobody looked at.

WHAT IS DELIBERATELY ABSENT
===========================

PRICES, SHOPS AND LOCATIONS. The mock invented `pr`, `shop` and `loc`, and the
page has a whole "what build B costs and where to get it" section driven by
them. Those are market data. They are NOT in the game files, and the only price
source in the repo (uexcorp) has no proven join to these items - it is not one
of the joins the research finding validated.

So no price is emitted, and the page says prices are not in this dataset rather
than showing a number somebody might spend real time on. An honest gap beats an
invented aUEC figure, and this is the first page where a visitor reads a number
and acts on it.

PER-WEAPON DPS IS A DIRECT READ, NOT DERIVED MATHS. `Weapon.Damage.Sustained`
is stated on the item. The trap the aggregation finding warns about is which
weapons count toward a SHIP total (the `IsPilotSlaveable` outermost-lock rule),
and that is exactly why the ship total comes from CIG rather than from us.

Rule 15: encodings stated.
"""

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SNAPSHOT = "20260801T204744Z"
SNAPDIR = os.path.join(HERE, "data-layer", "external-sources", "scunpacked-data",
                       "snapshots", SNAPSHOT)
SHIPS_JSON = os.path.join(SNAPDIR, "ships.json")
ITEMS_JSON = os.path.join(SNAPDIR, "ship-items.json")
RESOLUTION = os.path.join(HERE, "data-layer", "ship_resolution.json")
OUT = os.path.join(HERE, "testing", "_src", "loadout_data.gen.js")

# The patch this snapshot was taken from. Every row carries it, per the standing
# rule that the front end can flag unverified data.
LAST_VERIFIED_PATCH = "4.9"

# Item type -> the page's short type code and its display group. Only these
# types become swappable slots; everything else on a hull is structure, not a
# component a visitor chooses.
#
# Display, Misc, Seat, Door and the controller nodes are ABSENT ON PURPOSE.
# They join at 0% because CIG does not model them as statted purchasable items
# - a category boundary, not a join failure. See the research finding.
# TURRET AND MISSILELAUNCHER ARE NOT HERE, and that is a correction rather than
# an omission. They are MOUNTS - a "Remote Turret" carries no damage figure of
# its own, and including them put 471 statless entries in the picker offering
# themselves as alternatives to real guns. The guns fitted INSIDE a turret are
# WeaponGun records and the loadout walk already reaches them, so nothing is
# lost by leaving the mount out.
TYPE_MAP = {
    "WeaponGun":    ("wpn", "Weapons"),
    "Shield":       ("shd", "Shields"),
    "PowerPlant":   ("pow", "Power & cooling"),
    "Cooler":       ("col", "Power & cooling"),
    "QuantumDrive": ("qtm", "Quantum"),
}

# Display order for the groups, so the page reads the same way every time.
GROUP_ORDER = ["Weapons", "Shields", "Power & cooling", "Quantum"]


def say(line):
    """stdout that survives a ship called tok.yaai."""
    sys.stdout.buffer.write((line + "\n").encode("utf-8", "backslashreplace"))


def num(v):
    """A number, or None. Never a string, never NaN."""
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, (int, float)):
        return v
    return None


def r2(v):
    """Two decimals, and integers stay integers - the page formats, not this."""
    if v is None:
        return None
    if abs(v - round(v)) < 1e-9:
        return int(round(v))
    return round(v, 2)


def dict_or_none(v):
    """CIG uses an empty LIST where a dict is absent - reading .get on it throws.

    Named rather than inlined because it is the single most common trap in this
    dataset: ShieldsTotal, Power and Cooling are all a dict on ships that have
    the system and a bare list on ships that do not.
    """
    return v if isinstance(v, dict) else None


# --------------------------------------------------------------------------
# items
# --------------------------------------------------------------------------

def part_record(it):
    """One component, trimmed to what the page renders. None = not a component
    the page can offer."""
    typ = it.get("type") or ""
    if typ not in TYPE_MAP:
        return None
    # CIG ships placeholder rows in its own data. They are not components and
    # must never be offered as one.
    if "PLACEHOLDER" in (it.get("name") or ""):
        return None
    st = it.get("stdItem") or {}
    code, _group = TYPE_MAP[typ]

    mfr = st.get("Manufacturer")
    mfr = (mfr or {}).get("Name") if isinstance(mfr, dict) else None

    rec = {
        "n": st.get("Name") or it.get("name"),
        "m": mfr or it.get("manufacturer") or "Unknown",
        "t": code,
        "s": num(it.get("size")) or 0,
    }

    # --- the stats the page shows, each a DIRECT read off the item ---------
    w = dict_or_none(st.get("Weapon"))
    if w:
        dmg = dict_or_none(w.get("Damage")) or {}
        # Sustained is the honest one for a DPS comparison: DpsTotal is the
        # burst figure and would flatter every weapon with a small magazine.
        rec["dps"] = r2(num(dmg.get("Sustained")))

    sh = dict_or_none(st.get("Shield"))
    if sh:
        rec["ehp"] = r2(num(sh.get("MaxShieldHealth")))

    q = dict_or_none(st.get("QuantumDrive"))
    if q:
        jr = num(q.get("JumpRange"))
        # JumpRange is in metres; the page shows Gm.
        rec["qt"] = r2(jr / 1e9) if jr else None

    em = dict_or_none(st.get("Emission")) or {}
    e = em.get("Em")
    rec["em"] = r2(num(e.get("Maximum")) if isinstance(e, dict) else num(e))
    rec["ir"] = r2(num(em.get("Ir")))

    # Power draw and generation both live in the resource network.
    # THE RESOURCE NETWORK CARRIES THREE KINDS OF DELTA, not two.
    #
    # Consumption and Generation are the obvious pair. CONVERSION is the one
    # that matters and the one the first version missed: a cooler consumes
    # Power at `Rate` and produces Coolant at `GeneratedRate`. Handling only
    # the first two gave every one of the 81 coolers no cooling figure at all,
    # which would have rendered every ship on the site as overheating.
    rn = dict_or_none(st.get("ResourceNetwork")) or {}
    draw, gen, coolant = 0.0, 0.0, 0.0
    for state in rn.get("States") or []:
        if (state or {}).get("Name") != "Online":
            continue
        for delta in state.get("Deltas") or []:
            d = delta or {}
            kind, res = d.get("Type"), d.get("Resource")
            rate = num(d.get("Rate")) or 0
            if kind == "Consumption" and res == "Power":
                draw += rate
            elif kind == "Generation" and res == "Power":
                gen += rate
            elif kind == "Conversion":
                if res == "Power":
                    draw += rate
                grate = num(d.get("GeneratedRate")) or 0
                if d.get("GeneratedResource") == "Coolant":
                    coolant += grate
                elif d.get("GeneratedResource") == "Power":
                    gen += grate
    if draw:
        rec["pw"] = r2(draw)
    if gen:
        rec["cap"] = r2(gen)
    if coolant:
        rec["cool"] = r2(coolant)

    # Heat produced, for anything that is not itself a cooler.
    if code != "col":
        sig = None
        for state in rn.get("States") or []:
            if (state or {}).get("Name") == "Online":
                sig = dict_or_none(state.get("Signature"))
        if sig and num(sig.get("IR")):
            rec["ht"] = r2(num(sig.get("IR")))

    return {k: v for k, v in rec.items() if v is not None}


def walk_loadout(node, out, pilot=True):
    """Every fitted component in the tree, depth first, carrying whether the
    PILOT can fire it.

    The Loadout is nested - a turret holds its own guns - and a flat read would
    miss every weapon on a ship whose guns hang off mounts, which is most of
    them.

    `pilot` implements the proven exclusion (finding §2, 275/275): once an
    ancestor says IsPilotSlaveable false, that is FINAL for everything below it.
    A descendant mount saying true on itself does not reopen it, because that
    flag describes the mount hardware's capability rather than who operates it
    on this hull - a manned turret is false while its own gimbals are true.

    Getting this wrong is not a small error. Summing naively put the RSI Perseus
    at 16,596 DPS against CIG's 1,494 - it was counting every gunner's turret as
    though the pilot were firing it.
    """
    for entry in node or []:
        if not isinstance(entry, dict):
            continue
        here = pilot
        if here:
            # Only a false can change anything; once excluded, stay excluded.
            flag = entry.get("IsPilotSlaveable")
            if flag is False:
                here = False
        uuid = entry.get("UUID")
        if uuid:
            out.append((entry, here))
        walk_loadout(entry.get("Loadout"), out, here)


# --------------------------------------------------------------------------
# ships
# --------------------------------------------------------------------------

def ship_record(s, parts_by_uuid, part_keys):
    """One ship, with its stock loadout expressed as the page's slot shape."""
    name = s.get("Name")
    mfr = s.get("Manufacturer")
    mfr = (mfr or {}).get("Name") if isinstance(mfr, dict) else (mfr or "Unknown")

    fitted = []
    walk_loadout(s.get("Loadout"), fitted)

    slots, counts = [], {}
    for entry, pilot in fitted:
        key = part_keys.get(entry.get("UUID"))
        if not key:
            continue
        p = parts_by_uuid[entry["UUID"]]
        code = p["t"]
        group = next(g for t, (c, g) in TYPE_MAP.items() if c == code)
        counts[code] = counts.get(code, 0) + 1
        slot = {
            "id": "%s%d" % (code, counts[code]),
            "g": group,
            "t": code,
            "s": p.get("s", 0),
            "stock": key,
        }
        # A gunner's weapon is REAL and belongs on the page - it is part of the
        # ship. It just is not part of what the pilot can fire, so it is
        # marked and excluded from the pilot-DPS total rather than hidden.
        if code == "wpn" and not pilot:
            slot["turret"] = 1
        slots.append(slot)

    slots.sort(key=lambda x: (GROUP_ORDER.index(x["g"]), x["t"], x["id"]))

    # --- CIG's own precomputed aggregates for the STOCK loadout -----------
    cig = {}
    summ = dict_or_none((dict_or_none(s.get("Systems")) or {}).get("Weapons"))
    summ = dict_or_none((summ or {}).get("Summary")) or {}
    for src, dst in (("PilotDps", "dps"), ("PilotSustainedDps", "sdps"),
                     ("PilotAlpha", "alpha")):
        v = num(summ.get(src))
        if v is not None:
            cig[dst] = r2(v)

    shields = dict_or_none(s.get("ShieldsTotal"))
    if shields:
        cig["ehp"] = r2(num(shields.get("Hp")))
    power = dict_or_none(s.get("Power"))
    if power:
        cig["pw"] = r2(num(power.get("UsedSegmentsShields")))
        cig["cap"] = r2(num(power.get("GenerationSegments")))
    cooling = dict_or_none(s.get("Cooling"))
    if cooling:
        cig["ht"] = r2(num(cooling.get("UsedSegmentsShields")))
        cig["cool"] = r2(num(cooling.get("GenerationSegments")))
    emis = dict_or_none(s.get("Emission"))
    if emis:
        cig["em"] = r2(num(emis.get("EmShields")))
        cig["ir"] = r2(num(emis.get("IrShields")))
    dist = dict_or_none(s.get("Distortion"))
    if dist:
        cig["dist"] = r2(num(dist.get("Pool")))
    qt = dict_or_none(s.get("QuantumTravel"))
    if qt:
        # CIG states the ship's own quantum range. Preferred over summing the
        # fitted drive, per the order: where CIG publishes a number, use it.
        rng = num(qt.get("Range"))
        if rng:
            cig["qt"] = r2(rng / 1e9)
    cig = {k: v for k, v in cig.items() if v is not None}

    rec = {
        "n": name,
        "m": mfr,
        "role": s.get("Role") or s.get("Career") or "",
        # HULL HP, not mass. The page's "Effective HP" is hull + shields, and
        # feeding it Mass would produce a confident number that means nothing.
        # `Health` is present on 307 of 316; the rest report it as absent
        # rather than as zero, which would read as "this ship is made of paper".
        "hull": r2(num(s.get("Health"))),
        "slots": slots,
    }
    if rec.get("hull") is None:
        del rec["hull"]
    if cig:
        rec["cig"] = cig

    # SAY WHY THERE IS NOTHING, rather than rendering an empty panel. Six
    # records in the snapshot are not ships: five ATLS exosuit variants and a
    # Power Suit. They are in ships.json because CIG models them as vehicles,
    # and they have no weapons, shields, power plants or drives because they
    # are something a person wears. A category boundary, not a join failure.
    if not slots:
        if s.get("IsPowerSuit") or "ATLS" in (s.get("ClassName") or "")                 or "PowerSuit" in (s.get("ClassName") or ""):
            rec["why"] = ("this is an exosuit rather than a ship - it has no "
                          "weapons, shields or drives to fit")
        else:
            rec["why"] = ("no fittable components in the game files for this "
                          "hull")
    return rec


def main():
    for p in (SHIPS_JSON, ITEMS_JSON, RESOLUTION):
        if not os.path.exists(p):
            sys.exit("MISSING INPUT: %s\nRefusing to emit a partial dataset." % p)

    with io.open(SHIPS_JSON, "r", encoding="utf-8") as fh:
        ships = json.load(fh)
    with io.open(ITEMS_JSON, "r", encoding="utf-8") as fh:
        items = json.load(fh)
    with io.open(RESOLUTION, "r", encoding="utf-8") as fh:
        resolution = json.load(fh)

    # --- parts -----------------------------------------------------------
    parts, parts_by_uuid, part_keys = {}, {}, {}
    for it in items:
        rec = part_record(it)
        if not rec or not rec.get("n"):
            continue
        uuid = ((it.get("stdItem") or {}).get("UUID")) or it.get("reference")
        if not uuid:
            continue
        key = it.get("className") or uuid
        parts[key] = rec
        parts_by_uuid[uuid] = rec
        part_keys[uuid] = key

    # --- ships -----------------------------------------------------------
    built, empty = {}, []
    for s in ships:
        cls = s.get("ClassName") or s.get("Name")
        if not cls:
            continue
        rec = ship_record(s, parts_by_uuid, part_keys)
        if not rec["slots"]:
            empty.append(rec["n"] or cls)
        built[cls] = rec

    # --- ships the site lists that the game has NOT built -----------------
    #
    # Carried through rather than dropped, so the page can say why a ship has
    # no loadout instead of rendering an empty panel. Same discipline as
    # HOLO_UNMATCHED in the holo viewer.
    unreleased = [{"n": e.get("site"), "m": e.get("mfr") or "",
                   "why": "not released yet - CIG has not built this ship, so it "
                          "has no components to show"}
                  for e in resolution.get("no_game_file") or []]

    # --- OUR SUM vs CIG'S OWN NUMBER -------------------------------------
    #
    # The order asks for this rate explicitly and says a disagreement is a
    # finding. Compared only where CIG publishes a figure AND we have parts to
    # sum - anything else is not a disagreement, it is an absence.
    agree = dis = 0
    worst = []
    for cls, rec in built.items():
        cig = rec.get("cig") or {}
        if "sdps" not in cig or not rec["slots"]:
            continue
        ours = 0.0
        for sl in rec["slots"]:
            if sl.get("turret"):
                continue          # the proven exclusion - finding §2
            p = parts.get(sl["stock"]) or {}
            ours += p.get("dps") or 0
        if not ours:
            continue
        cigv = cig["sdps"]
        if abs(ours - cigv) <= max(1.0, cigv * 0.01):
            agree += 1
        else:
            dis += 1
            worst.append((abs(ours - cigv) / max(cigv, 1), rec["n"], r2(ours), cigv))

    out = [
        "/* GENERATED by build_loadout_data.py - do not hand edit.",
        "   Source: scunpacked snapshot %s" % SNAPSHOT,
        "     ships.json (%d ships) + ship-items.json (%d items)" % (len(ships), len(items)),
        "   plus data-layer/ship_resolution.json for ships the game has not built.",
        "",
        "   TRIMMED TO WHAT THE PAGE RENDERS. ship-items.json carries ~40 fields",
        "   per record; the page shows about eight. The field list came from",
        "   reading loadout.src.html, not from the data.",
        "",
        "   `cig` on a ship is CIG'S OWN precomputed aggregate for the STOCK",
        "   loadout. Anything the page sums from parts is OURS, and the page",
        "   says which is which. They are not the same claim.",
        "",
        "   NO PRICES. Shops and prices are market data, are not in the game",
        "   files, and the only price source in this repo has no proven join to",
        "   these items. The page says so rather than showing an invented one. */",
        "",
        "const LOADOUT_META=%s;" % json.dumps({
            "snapshot": SNAPSHOT,
            "generated_by": "build_loadout_data.py",
            "last_verified_patch": LAST_VERIFIED_PATCH,
            "ships": len(built),
            "parts": len(parts),
            "unreleased": len(unreleased),
            "has_prices": False,
        }, sort_keys=True),
        "const LOADOUT_PARTS=%s;" % json.dumps(parts, separators=(",", ":"),
                                               sort_keys=True, ensure_ascii=False),
        "const LOADOUT_SHIPS=%s;" % json.dumps(built, separators=(",", ":"),
                                               sort_keys=True, ensure_ascii=False),
        "const LOADOUT_UNRELEASED=%s;" % json.dumps(unreleased, separators=(",", ":"),
                                                    ensure_ascii=False),
        "",
    ]
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out))

    kb = os.path.getsize(OUT) / 1024.0
    say("wrote %s  (%.1f KB)" % (os.path.relpath(OUT, HERE), kb))
    say("  ships with a loadout : %d" % (len(built) - len(empty)))
    say("  ships with NO slots  : %d" % len(empty))
    say("  unreleased (site, no game file): %d" % len(unreleased))
    say("  parts emitted        : %d of %d items" % (len(parts), len(items)))
    say("")
    say("  OUR SUM vs CIG's PilotSustainedDps, within 1%%:")
    say("    agree %d   disagree %d" % (agree, dis))
    if worst:
        worst.sort(reverse=True)
        say("    worst disagreements:")
        for frac, n, ours, cigv in worst[:5]:
            say("      %-34s ours %-9s CIG %-9s  %.0f%% off" % (n, ours, cigv, frac * 100))
    return 0


if __name__ == "__main__":
    sys.exit(main())
