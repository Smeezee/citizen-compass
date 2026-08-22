#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_loadout_data.py - real ship loadouts for /loadout, generated not typed.

Reads the scunpacked snapshot and emits testing/_src/loadout_data.gen.js.

WHAT CHANGED AT L1 (order: the ship page, 2026-08-22)
=====================================================

The old generator carried a HAND-WRITTEN list of five component types. That is
exactly the mistake the order forbids: it applies editability BY TYPE, when the
game states it PER PORT, PER SHIP. A by-type rule breaks the industrial hulls
first - plain `FuelTank` is 0-editable across 436 ports so "fuel is fixed" looks
safe, while `ExternalFuelTank` is 20 editable and every one of them is on a
refueller, where the loadout IS the ship.

So THE TYPE LIST IS NOW DERIVED, not written. `select_types()` scans every port
on every ship and keeps a type when BOTH conditions hold:

    1. the port says `Editable: true`, and
    2. the port's `CompatibleTypes` names a type that has real items in
       `ship-items.json`.

`Editable` ALONE is not enough and using it alone is the second forbidden
mistake: 26,182 ports are editable, but 1,349 of those are untyped and the rest
include Displays, Misc, Doors, Buttons and Decals. Doors and dashboards. The
second condition is what separates a component from a light switch.

When CIG opens a port in a future patch, the next generation picks the type up
with no code change. That is the point.

THE FITMENT RULE, AND ITS LIMIT - READ THIS BEFORE TRUSTING THE PICKER
=====================================================================

What a port accepts comes from `CompatibleTypes` + `MinSize`/`MaxSize` ON THAT
PORT. Two traps, both measured rather than assumed:

  SUBTYPES ARE A TRAP IF ENFORCED NAIVELY. 253 quantum ports declare
  `SubTypes: ["QDrive"]`, and all 63 QuantumDrive items in the catalogue carry
  `subType: "UNDEFINED"`. Enforce the subtype strictly and EVERY QUANTUM DRIVE
  PICKER ON THE SITE IS EMPTY - 253 ports, essentially every ship, silently.
  `UNDEFINED` means "not stated", so it is treated as no claim on both sides.
  Same shape on JumpDrive, 247 ports.

  CIG'S OWN DATA DISAGREES WITH ITSELF ON 48 PORTS. Measured with the strongest
  control available: does the part the GAME ships in a port pass our fitment
  test for that port? 7,633 of 7,681 do - 99.38%. The 48 that do not are CIG's
  inconsistency, not ours: an Anvil Centurion turret port declares it accepts
  `WeaponGun` and has a `Turret` fitted; three missile racks are size 3 in a
  2..2 window. So THE STOCK PART IS ALWAYS OFFERED AT ITS OWN PORT, whatever
  the declared rule says, because the game demonstrably mounts it there. That
  rule is `always_include_stock` below and it exists to stop the page telling a
  player that the part already on their ship cannot go there.

The 6,720-entry fitment table is DEDUPLICATED: 8,180 editable ports resolve to
just 136 distinct rules, so the lists are emitted once and referenced by key.
Emitting them per port would be 552,310 entries for the same information.

WHAT IS CARRIED, AND WHY IT IS NOT EVERYTHING
=============================================

H1's lesson: 5,566 unused UUIDs were 80% of a file. So a part is carried only
if some real editable port on some real ship can actually take it, or if it is
fitted at a fixed port and the page therefore has to name it. 4,971 of 5,384.

This is also the honest answer to "do not build pickers for thrusters". The
order says thrusters are effectively fixed - 30 manoeuvre ports of 4,683 and 5
main of 1,060 are editable - and an earlier draft would have shipped 1,266
thruster records to serve 35 ports. It does NOT follow that those 35 ports
should be lied about: the game says they are editable and the per-port rule is
the whole point of the order. So the type is not excluded by name; the ITEMS
are filtered to what those 35 ports actually accept. Nobody gets a dead picker
and nobody gets a false "cannot be changed" either.

WHOSE NUMBER IS IT - THE DISTINCTION THE PAGE HAS TO CARRY
==========================================================

  CIG'S OWN, precomputed for the stock loadout and read directly off
  `ships.json` - `Systems.Weapons.Summary.PilotDps`, `ShieldsTotal.Hp`,
  `Power.*`, `Cooling.*`, `Emission.*`, `Distortion.Pool`.

  OURS, summed from the fitted parts, which is what has to happen the moment a
  visitor swaps a component - CIG cannot have precomputed a loadout that did
  not exist until the user clicked.

Both are emitted, `cig` carries CIG's, and the generator REPORTS the match rate.

ARMOUR IS A SHIP PROPERTY, NOT A PICKER (L5)
============================================

Armour is 0-editable across 305 ports, so it gets no picker - but it is NOT
skipped, because it moves two things players care about and neither is in the
schema today. A hull can be tough against ballistics and soft against lasers
(the Drake Vulture takes Physical at 0.7 and Energy at 0.5), and armour also
carries SIGNAL multipliers, so it moves stealth.

HOW IT ATTACHES WAS ESTABLISHED, NOT ASSUMED, and the answer is not the one the
order expected. `RequiredTags` is a dead end - 0 of 210 armour items carry a
top-level `requiredTags` in this snapshot. Armour attaches the same way every
other component does: through the ship's own `Loadout`, at a port whose Type is
`Armor`. 305 of 316 ships have one and ALL 305 RESOLVE. The other 11 are the
five ATLS variants, the ATLS GEO pair and the Power Suit - exosuits, not ships.
So hull resistance is resolvable for every actual ship, and 31 of the 210
armour items are simply never fitted by anything.

WHAT IS DELIBERATELY ABSENT
===========================

PRICES, SHOPS AND LOCATIONS. Market data, not in the game files, and the only
price source in this repo has no proven join to these items.

LIVERIES ARE EMITTED BUT TAKE NO PART IN THE READOUT (L7). They are a real
fitted slot - 279 of 316 ships have exactly one - but they are cosmetic, and
`hardpoint_paint` is spelled `Hardpoint_Paint` on six ships, so the match is
CASE-INSENSITIVE or six ships silently lose their liveries.

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

# The patch this snapshot was taken from.
LAST_VERIFIED_PATCH = "4.9"

# L4: "`Editable` carries `last_verified_patch` - Sleven expects more ports to
# open up later, and THAT MUST BE A DATA CHANGE, NOT A CODE CHANGE."
#
# So the patch under which a port's editability was last confirmed is data.
# This optional file overrides it per ship class and hardpoint; anything absent
# uses LAST_VERIFIED_PATCH. Shipping an empty mechanism would be an untested
# one, so `checks/_verify_loadout_fitment.py` plants an override and proves it
# reaches the emitted slot.
PATCH_OVERRIDES = os.path.join(HERE, "data-layer", "editability_patches.json")

# EXCLUDED REGARDLESS, per the order. Flair is cockpit ornament - it is a real
# editable port but it is a bobblehead, not a component. GroundVehicleMissile-
# Launcher is excluded by name in the order.
#
# NOTHING ELSE IS EXCLUDED BY TYPE. Armor, FuelTank, FuelIntake and
# QuantumFuelTank do not need excluding: they have ZERO editable ports, so the
# scan never selects them. That is the difference between a rule and a list.
EXCLUDED_TYPES = {
    "Flair_Surface", "Flair_Wall", "Flair_Floor", "Flair_Cockpit",
    "GroundVehicleMissileLauncher",
}

# Liveries are selected by the scan like anything else, but they are handled
# separately: cosmetic, no stats, and they take no part in the readout (L7).
PAINT_TYPE = "Paints"

# CIG writes "not stated" as this, on both sides of the join.
UNDEFINED = "UNDEFINED"

# Display only. A type the scan finds that is NOT here still ships - it gets a
# generated code and the "Other" group, and the generator SAYS SO loudly rather
# than dropping it. A silent drop is how a page stops offering a component
# nobody notices is missing.
TYPE_DISPLAY = {
    "WeaponGun":                    ("wpn", "Weapons",          "Weapon"),
    "WeaponMining":                 ("min", "Mining",           "Mining laser"),
    "WeaponDefensive":              ("def", "Weapons",          "Countermeasure"),
    "WeaponAttachment":             ("wat", "Weapons",          "Weapon attachment"),
    "Turret":                       ("tur", "Weapons",          "Turret mount"),
    "MissileLauncher":              ("mlr", "Weapons",          "Missile rack"),
    "Missile":                      ("msl", "Weapons",          "Missile"),
    "BombLauncher":                 ("blr", "Weapons",          "Bomb rack"),
    "Bomb":                         ("bmb", "Weapons",          "Bomb"),
    "EMP":                          ("emp", "Weapons",          "EMP"),
    "Shield":                       ("shd", "Shields",          "Shield generator"),
    "PowerPlant":                   ("pow", "Power & cooling",  "Power plant"),
    "Cooler":                       ("col", "Power & cooling",  "Cooler"),
    "QuantumDrive":                 ("qtm", "Quantum",          "Quantum drive"),
    "JumpDrive":                    ("jmp", "Quantum",          "Jump module"),
    "QuantumInterdictionGenerator": ("qig", "Quantum",          "Interdiction"),
    "Radar":                        ("rad", "Sensors",          "Radar"),
    "Scanner":                      ("scn", "Sensors",          "Scanner"),
    "Transponder":                  ("trn", "Sensors",          "Transponder"),
    "FlightController":             ("flc", "Flight",           "Flight controller"),
    "MainThruster":                 ("mth", "Flight",           "Main thruster"),
    "ManneuverThruster":            ("nth", "Flight",           "Manoeuvre thruster"),
    "ExternalFuelTank":             ("eft", "Fuel",             "External fuel tank"),
    "LifeSupportGenerator":         ("lsg", "Life support",     "Life support"),
    "CargoGrid":                    ("crg", "Cargo & industry", "Cargo grid"),
    "Container":                    ("con", "Cargo & industry", "Container"),
    "TractorBeam":                  ("trc", "Cargo & industry", "Tractor beam"),
    "TowingBeam":                   ("tow", "Cargo & industry", "Towing beam"),
    "SalvageHead":                  ("slv", "Cargo & industry", "Salvage head"),
    "SalvageModifier":              ("slm", "Cargo & industry", "Salvage module"),
    "SelfDestruct":                 ("sdt", "Other",            "Self destruct"),
    # FIXED-ONLY TYPES. The scan never selects these - they have zero editable
    # ports - but L4 says a fixed port is SHOWN, not hidden, because the fuel
    # tank still counts toward range. They are here so they render with a real
    # name rather than a generated code.
    "FuelTank":                     ("fut", "Fuel",             "Fuel tank"),
    "FuelIntake":                   ("fui", "Fuel",             "Fuel intake"),
    "QuantumFuelTank":              ("qft", "Fuel",             "Quantum fuel tank"),
    "Armor":                        ("arm", "Other",            "Armour"),
    PAINT_TYPE:                     ("pnt", "Livery",           "Livery"),
}

# Display order. "Other" is last and catches anything new.
GROUP_ORDER = ["Weapons", "Shields", "Power & cooling", "Quantum", "Flight",
               "Sensors", "Fuel", "Life support", "Cargo & industry", "Other",
               "Livery"]


def say(line):
    """stdout that survives a ship called tok.yaai."""
    sys.stdout.buffer.write((line + "\n").encode("utf-8", "backslashreplace"))


def num(v):
    """A number, or None. Never a string, never a bool, never NaN."""
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


def code_for(type_name):
    """The page's short code for a component type.

    Known types get a curated code so the page reads well. An UNKNOWN type -
    one CIG added since this file was written - still gets a stable code
    derived from its name rather than being dropped.
    """
    if type_name in TYPE_DISPLAY:
        return TYPE_DISPLAY[type_name][0]
    return "x" + type_name.lower().replace("_", "")[:6]


def group_for(type_name):
    if type_name in TYPE_DISPLAY:
        return TYPE_DISPLAY[type_name][1]
    return "Other"


def label_for(type_name):
    if type_name in TYPE_DISPLAY:
        return TYPE_DISPLAY[type_name][2]
    return type_name


# --------------------------------------------------------------------------
# ports
# --------------------------------------------------------------------------

def walk_ports(node, out, pilot=True, parent=None):
    """Every PORT in the tree, depth first, carrying whether the PILOT can fire
    whatever sits in it.

    A port and a fitted item are the same record in this data: `CompatibleTypes`
    describes the socket, `ClassName` names what is currently in it, and either
    can be absent. Both matter - the socket decides what may be offered, the
    ClassName IS the stock loadout (L2).

    `pilot` implements the proven exclusion (finding s2, 275/275): once an
    ancestor says IsPilotSlaveable false, that is FINAL for everything below it.
    A descendant mount saying true on itself does not reopen it, because that
    flag describes the mount hardware's capability rather than who operates it
    on this hull - a manned turret is false while its own gimbals are true.

    Getting this wrong is not a small error. Summing naively put the RSI Perseus
    at 16,596 DPS against CIG's 1,494.
    """
    for entry in node or []:
        if not isinstance(entry, dict):
            continue
        here = pilot
        if here and entry.get("IsPilotSlaveable") is False:
            here = False
        out.append((entry, here, parent))
        walk_ports(entry.get("Loadout"), out, here, entry)


def port_rules(entry, catalogue_types):
    """What this port accepts, as ((Type, (SubType, ...)), ...).

    Only types that (a) have real items and (b) are not excluded survive. A port
    listing nothing but Misc and Display comes back empty, which is what makes
    it structure rather than a component slot.
    """
    out = set()
    for c in entry.get("CompatibleTypes") or []:
        if not isinstance(c, dict):
            continue
        t = c.get("Type")
        if not t or t in EXCLUDED_TYPES or t not in catalogue_types:
            continue
        subs = c.get("SubTypes") or []
        if isinstance(subs, str):
            subs = [subs]
        # `$editable` is not a subtype. CIG uses $-prefixed pseudo-values as
        # markers - the Origin M80's right power-plant port declares
        # `SubTypes: ["$editable"]`, and no power plant in the catalogue has
        # that subType, so enforcing it as a literal leaves the port offering
        # nothing but the part already in it. The control caught exactly that.
        subs = tuple(sorted(x for x in subs
                            if x and x != UNDEFINED and not x.startswith("$")))
        out.add((t, subs))
    return tuple(sorted(out))


def rule_key(rules, mn, mx):
    """A stable name for one fitment rule, so 8,180 ports share 136 lists."""
    return "%s|%s|%s" % (
        ";".join("%s%s" % (t, (":" + ",".join(s)) if s else "") for t, s in rules),
        "" if mn is None else mn, "" if mx is None else mx)


def item_fits(it, rules, mn, mx):
    """Does this catalogue item mount at a port with these rules?

    `UNDEFINED` on either side means NOT STATED, and an unstated subtype
    constrains nothing. Enforcing it as a literal value empties every quantum
    and jump picker on the site - see the module docstring.
    """
    t = it.get("type") or ""
    st = it.get("subType") or ""
    if st == UNDEFINED:
        st = ""
    sz = num(it.get("size"))
    for pt, subs in rules:
        if t != pt:
            continue
        if subs and st and st not in subs:
            continue
        if sz is not None:
            if mn is not None and sz < mn:
                continue
            if mx is not None and sz > mx:
                continue
        return True
    return False


# --------------------------------------------------------------------------
# items
# --------------------------------------------------------------------------

def part_record(it, type_name, fitted=False):
    """One component, trimmed to what a readout reads.

    `<= PLACEHOLDER =>` IS CIG'S "NO DISPLAY NAME", NOT "NOT A REAL PART", and
    telling those two apart is worth a paragraph because getting it wrong goes
    both ways.

    8,229 fitted ports hold an item CIG has never given a localised name -
    `GATS_BallisticGatling_Barrel_S2` is a real gatling barrel, and
    `TMBL_Cyclone_CargoGrid_Main` is a real cargo grid. Refusing them outright
    left 14,503 ports rendering as a fixed row with nothing in it, which tells
    a visitor less than nothing about their own ship.

    So the rule splits by what the part is being used for:

      OFFERED IN A PICKER - never. An unnamed row is unpickable in practice,
      and offering one as an alternative to a named gun is the page asking
      somebody to choose something it cannot describe.

      FITTED AT A PORT - yes, carried, named from its className and MARKED
      `nn` so the page can say the game files give it no name. That is an
      honest gap; a blank row is just a gap.
    """
    st = it.get("stdItem") or {}
    placeholder = ("PLACEHOLDER" in (it.get("name") or "")
                   or "PLACEHOLDER" in (st.get("Name") or ""))
    if placeholder and not fitted:
        return None
    mfr = st.get("Manufacturer")
    mfr = (mfr or {}).get("Name") if isinstance(mfr, dict) else None

    name = st.get("Name") or it.get("name") or it.get("className")
    rec = {
        "n": name,
        "m": mfr or it.get("manufacturer") or "Unknown",
        "t": code_for(type_name),
        "s": num(it.get("size")) or 0,
    }
    if placeholder:
        # The className, spaced out. Derived, never invented: `GATS_Ballistic
        # Gatling_Barrel_S2` reads as "GATS Ballistic Gatling Barrel S2", which
        # is what the game file actually calls it.
        rec["n"] = (it.get("className") or "").replace("_", " ").strip() or "Unnamed part"
        rec["nn"] = 1

    # MASS IS A REAL COUPLING AND MUST NOT BE DROPPED (L6). Fitted parts change
    # the ship's total mass, which changes handling - and since thrusters are
    # effectively fixed, mass is the main lever a player has left over agility.
    # That makes it MORE important than it would be otherwise, not less.
    rec["ms"] = r2(num(st.get("Mass")))

    w = dict_or_none(st.get("Weapon"))
    if w:
        dmg = dict_or_none(w.get("Damage")) or {}
        # Sustained is the honest one for a DPS comparison: DpsTotal is the
        # burst figure and would flatter every weapon with a small magazine.
        rec["dps"] = r2(num(dmg.get("Sustained")))
        rec["alpha"] = r2(num(dmg.get("AlphaTotal")))
        # WHICH DAMAGE, NOT JUST HOW MUCH - the other half of L5, and the half
        # without which armour resistance cannot be applied to anything.
        #
        # `Damage.Dps` splits a weapon's output across the SAME six channels
        # armour resists: Physical, Energy, Distortion, Thermal, Biochemical,
        # Stun. A ballistic gun is Physical, a repeater is Energy, and a hull
        # that takes Physical at 0.75 and Energy at 0.6 turns those into two
        # different fights. Only the non-zero channels are carried - most
        # weapons use exactly one.
        split = dict_or_none(dmg.get("Dps")) or {}
        mix = {k: r2(num(v)) for k, v in split.items() if num(v)}
        if mix:
            rec["dmg"] = mix

    sh = dict_or_none(st.get("Shield"))
    if sh:
        rec["ehp"] = r2(num(sh.get("MaxShieldHealth")))
        rec["regen"] = r2(num(sh.get("MaxShieldRegen")))

    q = dict_or_none(st.get("QuantumDrive"))
    if q:
        jr = num(q.get("JumpRange"))
        # JumpRange is in metres; the page shows Gm.
        rec["qt"] = r2(jr / 1e9) if jr else None
        rec["qsp"] = r2(num(q.get("Speed")))

    em = dict_or_none(st.get("Emission")) or {}
    e = em.get("Em")
    rec["em"] = r2(num(e.get("Maximum")) if isinstance(e, dict) else num(e))
    rec["ir"] = r2(num(em.get("Ir")))

    # DETECTION. A radar's sensitivity and piercing are how far it sees and
    # through how much cover - the "detection" half of L6. Carried as the two
    # aggregate numbers rather than the full 8-entry SignatureDetection table,
    # which the readout does not use and which would be 77 x 8 rows of ballast.
    rd = dict_or_none(st.get("Radar"))
    if rd:
        sens = dict_or_none(rd.get("Sensitivity")) or {}
        pier = dict_or_none(rd.get("Piercing")) or {}
        v = [num(x) for x in sens.values() if num(x) is not None]
        if v:
            rec["sens"] = r2(sum(v) / len(v))
        v = [num(x) for x in pier.values() if num(x) is not None]
        if v:
            rec["pierce"] = r2(sum(v) / len(v))
        rec["rcool"] = r2(num(rd.get("Cooldown")))

    # MINING. Throughput and range are what a player picks a head for.
    ml = dict_or_none(st.get("MiningLaser"))
    if ml:
        rec["mrate"] = r2(num(ml.get("ExtractionThroughput")))
        rec["mrange"] = r2(num(ml.get("MaximumRange")))
        mods = dict_or_none(ml.get("Modifiers")) or {}
        mm = {k: r2(num(v)) for k, v in mods.items() if num(v) is not None}
        if mm:
            rec["mmod"] = mm

    # SALVAGE AND TRACTOR both live under TractorBeam - a salvage head is a
    # beam with a different job, which is CIG's modelling and not ours.
    tb = dict_or_none(st.get("TractorBeam"))
    if tb:
        rec["force"] = r2(num(tb.get("MaxForce")))
        rec["beam"] = r2(num(tb.get("MaxDistance")))

    # CARGO, and it is NOT where you would first look. A cargo grid states no
    # SCU figure at all - `InventoryOccupancy` is how much room the GRID ITSELF
    # takes up, which is a different question and reads as 0 for every one of
    # the 143 grids. What a grid holds is stated by its DIMENSIONS, in the
    # game's 1.25m cargo unit: 2.5 x 1.25 x 1.25 is 2 x 1 x 1 = 2 SCU.
    #
    # Written down because reading InventoryOccupancy.SCU here would have put
    # "0 SCU" on every container on the site, and 0 is a number somebody
    # believes.
    ic = dict_or_none(st.get("InventoryContainer"))
    if ic:
        d = [num(ic.get(k)) for k in ("X", "Y", "Z")]
        if all(v is not None and v > 0 for v in d):
            units = 1
            for v in d:
                units *= max(1, int(round(v / 1.25)))
            rec["scu"] = units

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
    if rec["t"] != "col":
        sig = None
        for state in rn.get("States") or []:
            if (state or {}).get("Name") == "Online":
                sig = dict_or_none(state.get("Signature"))
        if sig and num(sig.get("IR")):
            rec["ht"] = r2(num(sig.get("IR")))

    return {k: v for k, v in rec.items() if v is not None}


def paint_record(it):
    """A livery. NO STATS - it takes no part in the readout, per L7.

    `required_tags` ties it to a hull, `event_source` says how it was obtained.
    That is the acquisition-routes model already ruled, not a new one.
    """
    st = it.get("stdItem") or {}
    mfr = st.get("Manufacturer")
    mfr = (mfr or {}).get("Name") if isinstance(mfr, dict) else None
    rec = {
        "n": st.get("Name") or it.get("name") or it.get("className"),
        "m": mfr or it.get("manufacturer") or "",
    }
    ev = it.get("event_source") or st.get("EventSource")
    if isinstance(ev, str) and ev:
        rec["ev"] = ev
    tags = it.get("requiredTags") or st.get("RequiredTags")
    if isinstance(tags, str):
        tags = [t for t in tags.split() if t]
    if tags:
        rec["tags"] = list(tags)
    return rec


def armor_record(it):
    """A hull's armour, which is FIXED but is NOT nothing (L5).

    Survivability is not one number. Deltas (`*Change`) are dropped: they
    restate the multiplier against a 1.0 baseline and the page can subtract.
    """
    a = dict_or_none((it.get("stdItem") or {}).get("Armor")) or {}
    out = {"n": (it.get("stdItem") or {}).get("Name") or it.get("name")
                or it.get("className")}
    for src, dst in (("DamageMultipliers", "dm"), ("SignalMultipliers", "sm"),
                     ("PenetrationResistance", "pr"), ("Deflection", "df")):
        d = dict_or_none(a.get(src))
        if not d:
            continue
        vals = {k: r2(num(v)) for k, v in d.items()
                if not k.endswith("Change") and num(v) is not None}
        if vals:
            out[dst] = vals
    return out


# --------------------------------------------------------------------------
# the scan that replaces the hand-written type list
# --------------------------------------------------------------------------

def select_types(all_ports, catalogue_types):
    """L1: DERIVE the swappable type list. Both conditions, no transcription.

    Returns (selected, editable_total, untyped_editable, per_type_port_counts).
    """
    selected = {}
    editable_total = untyped = 0
    for entry, _pilot, _parent in all_ports:
        if not entry.get("Editable"):
            continue
        editable_total += 1
        if not entry.get("CompatibleTypes"):
            untyped += 1
            continue
        rules = port_rules(entry, catalogue_types)
        if not rules:
            continue
        for t, _subs in rules:
            selected[t] = selected.get(t, 0) + 1
    return selected, editable_total, untyped


# --------------------------------------------------------------------------
# ships
# --------------------------------------------------------------------------

# Every PortId in the snapshot starts `loadout.`, which is 8 identical bytes on
# 25,875 slots. Stripped here and stated in META, so the id stays reversible.
PORT_PREFIX = "loadout."


def strip_port_prefix(pid):
    if not pid:
        return None
    return pid[len(PORT_PREFIX):] if pid.startswith(PORT_PREFIX) else pid


def pretty_hardpoint(name):
    """`hardpoint_weapon_nose_left` -> `Weapon nose left`. Nothing invented."""
    if not name:
        return "Port"
    s = name
    for pre in ("hardpoint_", "Hardpoint_", "$", "hardpoint"):
        if s.startswith(pre):
            s = s[len(pre):]
    s = s.replace("_", " ").strip()
    return (s[:1].upper() + s[1:]) if s else "Port"


def cig_aggregates(s):
    """CIG'S OWN precomputed figures for the STOCK loadout. Reporting, not
    asserting - and L13 says that distinction must survive the layout."""
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
        cig["regen"] = r2(num(shields.get("Regen")))
    v = num(s.get("ShieldHp"))
    if v is not None:
        cig["shp"] = r2(v)
    power = dict_or_none(s.get("Power"))
    if power:
        cig["pw"] = r2(num(power.get("UsedSegmentsShields")))
        cig["cap"] = r2(num(power.get("GenerationSegments")))
    # POWER POOLS. CIG allocates power by ITEM TYPE with a size cap, and -1
    # means "no cap" rather than "no power" - reading it as a number would put
    # a negative allocation on the page. Only the real caps are carried.
    pools = dict_or_none(s.get("PowerPools"))
    if pools:
        pp = {}
        for k, v in pools.items():
            sz = num((v or {}).get("Size")) if isinstance(v, dict) else None
            if sz is not None and sz >= 0:
                pp[k] = r2(sz)
        if pp:
            cig["pools"] = pp
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
        cig["qfuel"] = r2(num(qt.get("FuelCapacity")))
        cig["qspool"] = r2(num(qt.get("SpoolTime")))
    prop = dict_or_none(s.get("Propulsion"))
    if prop:
        cig["fuel"] = r2(num(prop.get("FuelCapacity")))
        cig["intake"] = r2(num(prop.get("FuelIntakeRate")))
    fc = dict_or_none(s.get("FlightCharacteristics")) or {}
    ifcs = dict_or_none(fc.get("IFCS")) or fc
    for src, dst in (("ScmSpeed", "scm"), ("MaxSpeed", "vmax")):
        v = num(ifcs.get(src))
        if v is not None:
            cig[dst] = r2(v)
    xs = dict_or_none(s.get("CrossSection"))
    if xs:
        cig["xs"] = r2(num(xs.get("Maximum")) or num(xs.get("Value")))
    return {k: v for k, v in cig.items() if v is not None}


def ship_record(s, parts, part_keys, armors, paints, fits_index, catalogue_types,
                overrides, stats, hp_names, hp_index, type_of_code,
                by_class_ref):
    """One ship: every port it has, fixed and editable alike (L2, L3, L4)."""
    name = s.get("Name")
    cls = s.get("ClassName") or name
    mfr = s.get("Manufacturer")
    mfr = (mfr or {}).get("Name") if isinstance(mfr, dict) else (mfr or "Unknown")

    ports = []
    walk_ports(s.get("Loadout"), ports)

    slots, counts = [], {}
    ship_paint_tags = set()
    armor_key = None
    for entry, pilot, _parent in ports:
        etype = (entry.get("Type") or "").split(".")[0]
        stock_cls = entry.get("ClassName")
        stock_key = part_keys.get((stock_cls or "").lower())

        # --- armour: fixed, no picker, but read off the same Loadout -------
        #
        # An armour port never becomes a slot, whether or not it resolves. It
        # is rendered by the armour readout instead, which says more than a
        # "cannot be changed" row would. An UNRESOLVED one is counted rather
        # than passed through as a mystery component.
        if etype == "Armor":
            k = (stock_cls or "").lower()
            if k and k in armors:
                armor_key = armors[k]
            else:
                stats["armor_unresolved"] += 1
            continue

        rules = port_rules(entry, catalogue_types)
        editable = bool(entry.get("Editable"))

        # --- liveries: a real fitted slot, but cosmetic and separate (L7) --
        #
        # CASE-INSENSITIVE, because 6 of the 308 paint ports are spelled
        # `Hardpoint_Paint` and matching exactly loses those six ships.
        #
        # AND THE TAG IS THE JOIN, NOT THE TYPE. `CompatibleTypes` on a paint
        # port says only `Paints`, which is every livery in the game - offering
        # 1,077 liveries on every hull would be the page making 1,077 false
        # claims per ship, and it put 8 MB of repeated lists in the file the
        # first time round. The port's `RequiredTags` is what ties it to its
        # hull: `Paint_Hornet_F7_Mk2` -> the Hornet Mk II liveries.
        hp = (entry.get("HardpointName") or "")
        is_paint = ("paint" in hp.lower()) or any(t == PAINT_TYPE for t, _ in rules)
        if is_paint:
            tags = entry.get("RequiredTags") or []
            if isinstance(tags, str):
                tags = tags.split()
            tags = sorted(set(t for t in tags if t))
            stats["paint_ports"] += 1
            if tags:
                # UNION, not last-one-wins. Four hulls carry several paint
                # ports - the Drake Caterpillar's first is untagged and a later
                # one is not - so overwriting would drop whichever came first
                # and would depend on walk order, which is not a decision
                # anybody made.
                ship_paint_tags.update(tags)
                stats["paint_tagged"] += 1
            continue

        # A PORT WITH SOMETHING FITTED IN IT IS A PORT, WHATEVER IT DECLARES.
        #
        # This cost six of the Aegis Javelin's twenty-two M9A cannons and it is
        # worth writing down. Deciding what a slot is purely from
        # `CompatibleTypes` drops any port that declares nothing and still has
        # a real component sitting in it - and CIG has plenty. The build's own
        # gate caught it: our pilot-DPS sum went from reproducing CIG on all
        # 275 ships to 272, and the Javelin was 9,295 against CIG's 37,180.
        #
        # A port holding an M9A cannon is unambiguously a weapon port. So the
        # fitted item's own type is the fallback - it is evidence, not a guess.
        fitted_item = by_class_ref.get((stock_cls or "").lower())
        fitted_type = (fitted_item or {}).get("type") or ""
        if not rules:
            if (fitted_type and fitted_type in catalogue_types
                    and fitted_type not in EXCLUDED_TYPES
                    and fitted_type != PAINT_TYPE):
                # Typed by what is in it. It opens no picker either way,
                # because the port states no rule for what else would fit -
                # and L3 is explicit that a port rule is never guessed.
                main_type = fitted_type
                rules = ()
                stats["typed_by_fitted"] += 1
            else:
                # No real component type accepts anything here and nothing
                # component-shaped is in it. Structure - a door, a display, a
                # light group. Not a slot, and not a lie either. Counted so the
                # omission stays visible.
                if editable:
                    stats["editable_not_component"] += 1
                continue
        else:
            # The type shown is the port's own first accepted type, not the
            # fitted item's - because the port is the thing being described.
            main_type = rules[0][0]
        code = code_for(main_type)
        counts[code] = counts.get(code, 0) + 1
        # `h` is an INDEX INTO LOADOUT_HP, not a label.
        #
        # Two reasons, and the first is L10 rather than size. A hull marker has
        # to select "port N and no other, BY IDENTITY, never by screen
        # position", and the identity the marker data uses is the game's own
        # hardpoint name. A prettified label cannot be reversed back to it. So
        # the raw name is carried and the page prettifies for display.
        # Deduplicating it is then free: 25,875 slots draw on ~2,400 names.
        #
        # `g` is NOT carried - LOADOUT_TYPES already maps the type code to its
        # group, and repeating it per slot was 360 KB of the same eleven words.
        hp_name = entry.get("HardpointName") or ""
        if hp_name not in hp_index:
            hp_index[hp_name] = len(hp_names)
            hp_names.append(hp_name)
        # `p` IS THE GAME'S OWN PORT ID, AND IT IS THE ONLY REAL IDENTITY HERE.
        #
        # A hardpoint NAME is not unique within a ship: 287 of 316 hulls have
        # slots sharing one, 11,283 slots in all, and the RSI Polaris has
        # THIRTY ports called `MEC`, thirty called `VEN` and thirty called
        # `POW`. `PortId` is unique - 57,759 ports, 57,759 distinct ids,
        # checked across the whole snapshot.
        #
        # L10 requires a hull marker to select "port N and no other, BY
        # IDENTITY, never by screen position". A name cannot do that. This can,
        # and it is what any marker join must be made on.
        slot = {
            "id": "%s%d" % (code, counts[code]),
            "t": code,
            "s": num(entry.get("MaxSize")),
            "h": hp_index[hp_name],
            "p": strip_port_prefix(entry.get("PortId")),
        }
        if slot["s"] is None:
            slot["s"] = num(entry.get("MinSize")) or 0
        if stock_key:
            slot["stock"] = stock_key
        if editable and rules:
            key = rule_key(rules, entry.get("MinSize"), entry.get("MaxSize"))
            slot["fit"] = key
            stats["editable_component"] += 1
        else:
            # L4: A FIXED PORT IS SHOWN, NOT HIDDEN. It still counts toward
            # totals because it is part of the ship; it just opens no picker.
            slot["fix"] = 1
            stats["fixed_component"] += 1
        # A gunner's weapon is REAL and belongs on the page - it is part of the
        # ship. It just is not part of what the pilot can fire, so it is marked
        # and excluded from the pilot-DPS total rather than hidden.
        if not pilot:
            slot["turret"] = 1
        ov = overrides.get("%s|%s" % (cls, entry.get("HardpointName") or ""))
        if ov:
            slot["v"] = ov
        slots.append(slot)

    def group_rank(sl):
        g = group_for(type_of_code.get(sl["t"], ""))
        return GROUP_ORDER.index(g) if g in GROUP_ORDER else len(GROUP_ORDER)
    slots.sort(key=lambda x: (group_rank(x), x["t"], x["id"]))

    rec = {
        "n": name,
        "m": mfr,
        "role": s.get("Role") or "",
        "career": s.get("Career") or "",
        # HULL HP, not mass. The page's "Effective HP" is hull + shields, and
        # feeding it Mass would produce a confident number that means nothing.
        # `Health` is present on 307 of 316; the rest report it as absent
        # rather than as zero, which would read as "this ship is made of paper".
        "hull": r2(num(s.get("Health"))),
        # L6: mass, all three of CIG's figures. `ms` is the bare hull, `msl` is
        # what the stock loadout adds, `mst` is the total CIG states. The page
        # recomputes `mst` when a part is swapped; the other two anchor it.
        "ms": r2(num(s.get("Mass"))),
        "msl": r2(num(s.get("MassLoadout"))),
        "mst": r2(num(s.get("MassTotal"))),
        "crew": r2(num(s.get("Crew"))),
        "cargo": r2(num(s.get("Cargo"))),
        "size": r2(num(s.get("Size"))),
        "slots": slots,
    }
    seats = s.get("Seats")
    if isinstance(seats, list):
        rec["seats"] = len(seats)
    elif num(seats) is not None:
        rec["seats"] = r2(num(seats))
    dims = [r2(num(s.get(k))) for k in ("Length", "Width", "Height")]
    if all(d is not None for d in dims):
        rec["dim"] = dims

    if armor_key:
        rec["arm"] = armor_key
    # `PenetrationMultiplier` - damage passes through to fuses and components
    # at these rates. CIG writes an absent one as an empty list.
    pen = dict_or_none(s.get("PenetrationMultiplier"))
    if pen:
        p = {k.lower()[:4]: r2(num(v)) for k, v in pen.items() if num(v) is not None}
        if p:
            rec["pen"] = p
    if ship_paint_tags:
        rec["pset"] = "+".join(sorted(ship_paint_tags))

    cig = cig_aggregates(s)
    if cig:
        rec["cig"] = cig

    rec = {k: v for k, v in rec.items() if v is not None}

    # SAY WHY THERE IS NOTHING, rather than rendering an empty panel. Six
    # records in the snapshot are not ships: five ATLS exosuit variants and a
    # Power Suit. They are in ships.json because CIG models them as vehicles.
    # A category boundary, not a join failure.
    if not slots:
        if s.get("IsPowerSuit") or "ATLS" in (s.get("ClassName") or "") \
                or "PowerSuit" in (s.get("ClassName") or ""):
            rec["why"] = ("this is an exosuit rather than a ship - it has no "
                          "weapons, shields or drives to fit")
        else:
            rec["why"] = ("no fittable components in the game files for this "
                          "hull")
    return rec


# --------------------------------------------------------------------------

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
    overrides = {}
    if os.path.exists(PATCH_OVERRIDES):
        with io.open(PATCH_OVERRIDES, "r", encoding="utf-8") as fh:
            overrides = json.load(fh) or {}

    catalogue_types = set()
    by_class = {}
    for it in items:
        t = it.get("type") or ""
        if t:
            catalogue_types.add(t)
        cn = it.get("className")
        if cn:
            by_class[cn.lower()] = it

    # --- every port on every ship, once ----------------------------------
    all_ports = []
    for s in ships:
        walk_ports(s.get("Loadout"), all_ports)

    # --- L1: THE SCAN ----------------------------------------------------
    selected, editable_total, untyped = select_types(all_ports, catalogue_types)
    unknown = sorted(t for t in selected if t not in TYPE_DISPLAY)

    # --- the fitment table, deduplicated ---------------------------------
    #
    # 8,180 editable component ports collapse to ~136 distinct rules. Emitting
    # a list per port would be half a million entries saying the same thing.
    rule_defs = {}
    for entry, _pilot, _parent in all_ports:
        if not entry.get("Editable"):
            continue
        rules = port_rules(entry, catalogue_types)
        if not rules:
            continue
        key = rule_key(rules, entry.get("MinSize"), entry.get("MaxSize"))
        if key not in rule_defs:
            rule_defs[key] = (rules, entry.get("MinSize"), entry.get("MaxSize"))

    # Which items each rule accepts. Paint rules are resolved here too - the
    # ship record picks them up as `paints` and they never reach the readout.
    fits_index, reachable = {}, set()
    for key, (rules, mn, mx) in rule_defs.items():
        keys = []
        for it in items:
            if not item_fits(it, rules, mn, mx):
                continue
            cn = it.get("className")
            if not cn or "PLACEHOLDER" in (it.get("name") or ""):
                continue
            keys.append(cn)
        keys.sort()
        fits_index[key] = keys
        reachable.update(keys)

    # --- parts, armour and liveries --------------------------------------
    #
    # A part is carried if a real editable port can take it OR it is fitted at
    # a fixed port and the page therefore has to name it. Everything else is
    # 5,566-unused-UUIDs bloat.
    stock_fitted = set()
    for entry, _pilot, _parent in all_ports:
        cn = (entry.get("ClassName") or "").lower()
        it = by_class.get(cn)
        if it and (it.get("type") or "") in catalogue_types:
            stock_fitted.add(it.get("className"))

    parts, part_keys, armors, paints = {}, {}, {}, {}
    paint_tags = {}
    armor_defs = {}
    for it in items:
        cn = it.get("className")
        t = it.get("type") or ""
        if not cn:
            continue
        if t == "Armor":
            armors[cn.lower()] = cn
            armor_defs[cn] = armor_record(it)
            continue
        if t == PAINT_TYPE:
            paints[cn] = paint_record(it)
            part_keys[cn.lower()] = cn
            tags = (it.get("stdItem") or {}).get("RequiredTags") or []
            if isinstance(tags, str):
                tags = tags.split()
            paint_tags[cn] = set(x for x in tags if x)
            continue
        if t in EXCLUDED_TYPES:
            continue
        if cn not in reachable and cn not in stock_fitted:
            continue
        rec = part_record(it, t, fitted=(cn in stock_fitted))
        if not rec or not rec.get("n"):
            continue
        parts[cn] = rec
        part_keys[cn.lower()] = cn

    # Armour is only carried for hulls that actually fit it - 31 of 210 are
    # never fitted by anything and would be dead weight.
    used_armor = set()
    for s in ships:
        ports = []
        walk_ports(s.get("Loadout"), ports)
        for entry, _p, _par in ports:
            if (entry.get("Type") or "").split(".")[0] == "Armor":
                k = (entry.get("ClassName") or "").lower()
                if k in armors:
                    used_armor.add(armors[k])
    armor_out = {k: v for k, v in armor_defs.items() if k in used_armor}

    # --- ships ------------------------------------------------------------
    # The shared hardpoint-name table and the code->type reverse map.
    hp_names, hp_index = [], {}
    type_of_code = {}
    for t in list(selected) + sorted(TYPE_DISPLAY) + sorted(catalogue_types):
        type_of_code.setdefault(code_for(t), t)

    stats = {"editable_component": 0, "fixed_component": 0,
             "editable_not_component": 0, "paint_ports": 0,
             "typed_by_fitted": 0,
             "armor_unresolved": 0,
             "paint_tagged": 0}
    built, empty, no_armor = {}, [], []
    for s in ships:
        cls = s.get("ClassName") or s.get("Name")
        if not cls:
            continue
        rec = ship_record(s, parts, part_keys, armors, paints, fits_index,
                          catalogue_types, overrides, stats, hp_names, hp_index,
                          type_of_code, by_class)
        if not rec["slots"]:
            empty.append(rec["n"] or cls)
        if not rec.get("arm"):
            no_armor.append(rec["n"] or cls)
        built[cls] = rec

    # Only keep fitment lists some ship's slot actually references, and only
    # the part keys we carried.
    used_keys = set()
    for rec in built.values():
        for sl in rec["slots"]:
            if sl.get("fit"):
                used_keys.add(sl["fit"])
    fits_out = {}
    for key in used_keys:
        fits_out[key] = [k for k in fits_index.get(key, []) if k in parts]
    # --- L7: the livery sets, keyed by the port's own RequiredTags --------
    #
    # One list per distinct tag set, referenced by every hull that shares it,
    # so a variant family does not repeat its liveries once per variant.
    paint_sets = {}
    for rec in built.values():
        key = rec.get("pset")
        if not key:
            continue
        if key not in paint_sets:
            want = set(key.split("+"))
            paint_sets[key] = sorted(
                cn for cn, tags in paint_tags.items()
                if cn in paints and want & tags)
        if not paint_sets[key]:
            # The port names a tag no livery answers to. Say nothing rather
            # than render an empty picker.
            del paint_sets[key]
            del rec["pset"]
    # Only carry liveries some hull can actually reach.
    reachable_paints = set()
    for v in paint_sets.values():
        reachable_paints.update(v)
    paints = {k: v for k, v in paints.items() if k in reachable_paints}

    # THE STOCK PART IS ALWAYS OFFERED AT ITS OWN PORT.
    #
    # 48 ports fail their own declared rule in CIG's data - an Anvil Centurion
    # turret port says it accepts WeaponGun and has a Turret in it. The game
    # demonstrably mounts that part there, so refusing to offer it would be the
    # page contradicting the game. Applied per ship, so it cannot leak a part
    # into a rule used by a different port.
    forced = 0
    for rec in built.values():
        for sl in rec["slots"]:
            k, st = sl.get("fit"), sl.get("stock")
            if not k or not st or st not in parts:
                continue
            if st not in fits_out.get(k, []):
                sl["also"] = st        # the page merges this into the list
                forced += 1

    # A PORT WITH NOTHING TO OFFER MUST NOT OPEN AN EMPTY PICKER.
    #
    # 134 editable ports name a real component type that NO catalogue item
    # satisfies at that size - the Gladius's `$IP_rack_addon_02` accepts a
    # missile rack in a window nothing is built for. The order is explicit:
    # "Where the data does not say: exclude and log it. Never guess a port
    # rule." So the port still RENDERS - it is part of the ship - but it loses
    # its picker and gains `nofit`, which is the page's cue to say that the
    # game files list no part for it rather than open a window with nothing in
    # it. An empty picker still renders, and looks exactly like a broken one.
    nofit = []
    for cls, rec in built.items():
        for sl in rec["slots"]:
            k = sl.get("fit")
            if not k:
                continue
            if fits_out.get(k) or sl.get("also"):
                continue
            del sl["fit"]
            sl["nofit"] = 1
            nofit.append("%s / %s" % (rec["n"], hp_names[sl["h"]]))
    # And drop the now-unreferenced empty rules rather than shipping them.
    still_used = set()
    for rec in built.values():
        for sl in rec["slots"]:
            if sl.get("fit"):
                still_used.add(sl["fit"])
    fits_out = {k: v for k, v in fits_out.items() if k in still_used}

    # --- ships the site lists that the game has NOT built (L14 case 2) ----
    unreleased = [{"n": e.get("site"), "m": e.get("mfr") or "",
                   "why": "not released yet - CIG has not built this ship, so it "
                          "has no components to show"}
                  for e in resolution.get("no_game_file") or []]

    # --- OUR SUM vs CIG'S OWN NUMBER -------------------------------------
    agree = dis = 0
    worst = []
    for cls, rec in built.items():
        cig = rec.get("cig") or {}
        if "sdps" not in cig or not rec["slots"]:
            continue
        ours = 0.0
        for sl in rec["slots"]:
            if sl.get("turret"):
                continue          # the proven exclusion - finding s2
            p = parts.get(sl.get("stock")) or {}
            ours += p.get("dps") or 0
        if not ours:
            continue
        cigv = cig["sdps"]
        if abs(ours - cigv) <= max(1.0, cigv * 0.01):
            agree += 1
        else:
            dis += 1
            worst.append((abs(ours - cigv) / max(cigv, 1), rec["n"], r2(ours), cigv))

    meta = {
        "snapshot": SNAPSHOT,
        "generated_by": "build_loadout_data.py",
        "last_verified_patch": LAST_VERIFIED_PATCH,
        "ships": len(built),
        "parts": len(parts),
        "armors": len(armor_out),
        "paints": len(paints),
        "paint_sets": len(paint_sets),
        "fits": len(fits_out),
        "hardpoints": len(hp_names),
        "port_id_prefix": PORT_PREFIX,
        "ports_with_no_part": len(nofit),
        "types": sorted(selected),
        "unreleased": len(unreleased),
        "has_prices": False,
        "editable_ports": editable_total,
        "editable_component_ports": stats["editable_component"],
        "fixed_component_ports": stats["fixed_component"],
    }
    # EVERY code that appears on a slot, not just the scanned ones. Fixed-only
    # types - FuelTank, FuelIntake, QuantumFuelTank - are never SELECTED by the
    # scan because they have no editable ports, but L4 still renders them, and
    # a slot whose type code is missing here has no name and no group.
    used_codes = set()
    for rec in built.values():
        for sl in rec["slots"]:
            used_codes.add(sl["t"])
    type_out = {}
    for t in sorted(set(selected) | set(type_of_code.get(c, c)
                                        for c in used_codes)):
        c = code_for(t)
        if c in used_codes or t in selected:
            type_out[c] = {"t": t, "g": group_for(t), "n": label_for(t)}
    orphan = sorted(c for c in used_codes if c not in type_out)
    for c in orphan:
        type_out[c] = {"t": type_of_code.get(c, c), "g": "Other",
                       "n": type_of_code.get(c, c)}

    def dump(v):
        return json.dumps(v, separators=(",", ":"), sort_keys=True,
                          ensure_ascii=False)

    out = [
        "/* GENERATED by build_loadout_data.py - do not hand edit.",
        "   Source: scunpacked snapshot %s" % SNAPSHOT,
        "     ships.json (%d ships) + ship-items.json (%d items)" % (len(ships), len(items)),
        "   plus data-layer/ship_resolution.json for ships the game has not built.",
        "",
        "   THE TYPE LIST IS DERIVED, NOT WRITTEN. Every port on every ship was",
        "   scanned; a type is here because some port is Editable AND names a",
        "   type that has real items. Editability is PER PORT, PER SHIP - never",
        "   per component type.",
        "",
        "   A slot's `h` indexes LOADOUT_HP, the game's OWN hardpoint name.",
        "   That name - not a screen position and not a prettified label - is",
        "   how a hull marker selects one port and no other.",
        "",
        "   LOADOUT_FITS is the fitment table, keyed by a port's rule",
        "   (CompatibleTypes + size window) so ports sharing a rule share a",
        "   list. A slot's `fit` names its rule; `also` names a stock part CIG",
        "   mounts there despite its own declared rule.",
        "",
        "   `cig` on a ship is CIG'S OWN precomputed aggregate for the STOCK",
        "   loadout. Anything the page sums from parts is OURS, and the page",
        "   says which is which. They are not the same claim.",
        "",
        "   LOADOUT_ARMOR is per-hull damage and signal resistance. It is FIXED",
        "   - no picker - but survivability is not one number and armour moves",
        "   stealth too, so it is shown.",
        "",
        "   NO PRICES. Shops and prices are market data, are not in the game",
        "   files, and the only price source in this repo has no proven join to",
        "   these items. The page says so rather than showing an invented one. */",
        "",
        "const LOADOUT_META=%s;" % json.dumps(meta, sort_keys=True),
        "const LOADOUT_TYPES=%s;" % dump(type_out),
        "const LOADOUT_HP=%s;" % dump(hp_names),
        "const LOADOUT_PARTS=%s;" % dump(parts),
        "const LOADOUT_FITS=%s;" % dump(fits_out),
        "const LOADOUT_ARMOR=%s;" % dump(armor_out),
        "const LOADOUT_PAINTS=%s;" % dump(paints),
        "const LOADOUT_PAINTSETS=%s;" % dump(paint_sets),
        "const LOADOUT_SHIPS=%s;" % dump(built),
        "const LOADOUT_UNRELEASED=%s;" % json.dumps(unreleased, separators=(",", ":"),
                                                    ensure_ascii=False),
        "",
    ]
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out))

    import gzip
    with io.open(OUT, "rb") as fh:
        raw = fh.read()
    gz = len(gzip.compress(raw, 9))

    say("wrote %s" % os.path.relpath(OUT, HERE))
    say("  raw %.1f KB   gzipped %.1f KB" % (len(raw) / 1024.0, gz / 1024.0))
    say("")
    say("  THE SCAN (L1) - derived, not transcribed:")
    say("    ports total                    : %d" % len(all_ports))
    say("    editable                       : %d" % editable_total)
    say("      of which untyped             : %d" % untyped)
    say("    types SELECTED                 : %d" % len(selected))
    for t in sorted(selected, key=lambda x: -selected[x]):
        mark = "  <-- NOT IN TYPE_DISPLAY" if t in unknown else ""
        say("      %-30s %6d editable ports%s" % (t, selected[t], mark))
    if orphan:
        say("    TYPE CODES ON SLOTS WITH NO CURATED NAME: %s" % ", ".join(orphan))
    if unknown:
        say("    NEW TYPES CIG HAS OPENED SINCE THIS FILE WAS WRITTEN: %s"
            % ", ".join(unknown))
        say("    They are EMITTED under the 'Other' group rather than dropped.")
    say("")
    say("  PORTS AS THE PAGE SEES THEM:")
    say("    editable component slots       : %d" % stats["editable_component"])
    say("    fixed component slots (shown)  : %d" % stats["fixed_component"])
    say("    editable but NOT a component   : %d  (doors, displays, decals)"
        % stats["editable_not_component"])
    say("    armour ports that did NOT resolve: %d" % stats["armor_unresolved"])
    say("    ports typed by what is FITTED in them: %d  (the port declares"
        " nothing)" % stats["typed_by_fitted"])
    say("")
    say("  CARRIED:")
    say("    parts    %5d of %d catalogue items" % (len(parts), len(items)))
    say("    fitment  %5d rules, %d entries" % (len(fits_out),
                                                sum(len(v) for v in fits_out.values())))
    say("    armour   %5d of %d (%d never fitted by any ship)"
        % (len(armor_out), len(armor_defs), len(armor_defs) - len(armor_out)))
    say("    hardpoint names %5d distinct, shared by %d slots"
        % (len(hp_names), sum(len(r["slots"]) for r in built.values())))
    say("    liveries %5d in %d hull sets  (%d livery ports, %d tagged)"
        % (len(paints), len(paint_sets), stats["paint_ports"],
           stats["paint_tagged"]))
    say("    stock parts forced into their own port's list: %d" % forced)
    say("    editable ports with NO part in the catalogue: %d  (shown, no"
        " picker)" % len(nofit))
    for x in nofit[:5]:
        say("      %s" % x)
    if len(nofit) > 5:
        say("      ... and %d more" % (len(nofit) - 5))
    say("")
    say("  SHIPS:")
    say("    with a loadout                 : %d" % (len(built) - len(empty)))
    say("    with NO slots                  : %d" % len(empty))
    say("    with NO armour resolved        : %d  %s"
        % (len(no_armor), ("(" + ", ".join(no_armor[:8]) + ")") if no_armor else ""))
    say("    unreleased (site, no game file): %d" % len(unreleased))
    say("")
    say("  OUR SUM vs CIG's PilotSustainedDps, within 1%:")
    say("    agree %d   disagree %d" % (agree, dis))
    if worst:
        worst.sort(reverse=True)
        say("    worst disagreements:")
        for frac, n, ours, cigv in worst[:5]:
            say("      %-34s ours %-9s CIG %-9s  %.0f%% off" % (n, ours, cigv, frac * 100))
    return 0


if __name__ == "__main__":
    sys.exit(main())
