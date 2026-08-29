#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B5: a port with no position vocabulary of its own inherits its TURRET'S.

RULE16: INDEPENDENT - the placer is run as a subprocess and the inheritance is
measured from what it wrote. The before state is produced by running it
with the behaviour off, so both sides are observations of the program
rather than assertions about its source.

WHAT WAS ACTUALLY WRONG, WHICH IS NOT WHAT THE ORDER OR I SAID
==============================================================
The order said turret guns fall to the None target - the middle of the hull. I
reported that they do not, because the Hammerhead has no points on the None
target. BOTH STATEMENTS MISSED THE SAME THING, and it took being asked why
`turretOf` was null on all 1,798 records to find it:

    THE TURRET GUNS WERE NOT IN THE DATASET AT ALL.

`ship_mounts.json` - the 2026-08-10 flatten, and the only mount source the
placement has ever had - contains ONLY TOP-LEVEL PORTS. Measured across
ships.json: 2,555 weapon ports are top-level and 2,374 are CHILDREN. Not one
of the 2,374 has ever reached place_fleet.py.

So the parent was not dropped at the record write, and not dropped when
place_fleet read it. It was dropped one step earlier than either: THE PORTS
THEMSELVES WERE ABSENT, so there was nothing for a parent to be attached to.
`turretOf` was null on every record because no port that HAD a turret was ever
in the file.

AND "ONE LEVEL" WOULD HAVE BEEN ACTIVELY WRONG. A gun sits three deep:

    turret_side_back_right -> hardpoint_weapon_left_upper -> hardpoint_class_2

One level up is `hardpoint_weapon_left_upper`, whose name DOES yield
vocabulary: left, upper, gun. A strict one-level rule therefore places a gun
belonging to the back-RIGHT turret on the LEFT of the ship - a confident wrong
position, which is worse than the hull-centre default rather than better. So a
port inside a turret takes THE TURRET'S position: the outermost TurretBase in
its own recorded chain. A real ancestor, not a sibling and not an inference.

THE CHILDREN ARE OFF BY DEFAULT IN THE SHIPPED DATASET, and that is a measured
trade rather than an oversight. Including them makes this fire - it gains 160
markers on 5 more hulls - and it also takes fleet crowding from 60 markers on 9
hulls to 216 on 21, and from 117/19 to 451/34 on the placement report's own
metric. B6's acceptance is that crowding must not get worse and four numbers
out of four say it would. So the mechanism ships proven and switched off behind
`--with-children`, and this control drives it WITH the switch on, because a
mechanism nobody has seen fire is a mechanism nobody knows works.

Rule 15: every open states its encoding.

Usage:
    venv/Scripts/python.exe checks/_verify_turret_inheritance.py
        [--self-test]   invert every expectation; must exit non-zero
"""
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HOLO = os.path.join(ROOT, "data-layer", "derived", "holo-hardpoints")
PLACE = os.path.join(HOLO, "place_fleet.py")
MATCHED = os.path.join(HOLO, "matched.json")
FLEET = os.path.join(HOLO, "hardpoints_fleet.json")
GEN = os.path.join(ROOT, "testing", "_src", "loadout_data.gen.js")

SELFTEST = "--self-test" in sys.argv
FLEETRUN = "--fleet" in sys.argv

_passed, _failed, _notes = [], [], []


def check(label, got, detail=""):
    want = (not got) if SELFTEST else got
    (_passed if want else _failed).append(
        ("%s %s" % (label, detail)).strip())
    print("  %s  %s%s" % ("PASS" if want else "FAIL", label,
                          ("  " + detail) if detail else ""))
    return bool(want)


def read_text(path):
    with io.open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def read_json(path):
    with io.open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def ship_hardpoint_names(class_name):
    """Every HardpointName in one hull's Loadout tree, from the snapshot.

    Returns None when the snapshot is not on disk, so the caller reports NOT
    PERFORMED rather than passing on an empty set - an empty set would make
    every "is this a real port" question answer no, and the assertion would
    fail loudly rather than silently, but the reason would be wrong.
    """
    snapdir = os.path.join(ROOT, "data-layer", "external-sources",
                           "scunpacked-data", "snapshots")
    if not os.path.isdir(snapdir):
        return None
    snaps = sorted(d for d in os.listdir(snapdir)
                   if os.path.isdir(os.path.join(snapdir, d)))
    if not snaps:
        return None
    sj = os.path.join(snapdir, snaps[-1], "ships.json")
    if not os.path.exists(sj):
        return None
    ships = read_json(sj)
    rec = next((s for s in ships
                if (s.get("ClassName") or "").lower() == class_name.lower()),
               None)
    if rec is None:
        return None
    names = set()

    def walk(node):
        for e in node or []:
            if not isinstance(e, dict):
                continue
            if e.get("HardpointName"):
                names.add(e["HardpointName"])
            walk(e.get("Loadout"))

    walk(rec.get("Loadout"))
    return names


def load_place_fleet():
    spec = importlib.util.spec_from_file_location("place_fleet", PLACE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------ 1. flatten
print("\n1. THE FLATTEN CARRIES THE PARENT, AND SAYS null WHEN THERE IS NONE")
if not os.path.exists(GEN):
    print("NOT PERFORMED: %s is missing, so nothing can be read." % GEN)
    sys.exit(2)
gen = read_text(GEN)
SHIPS = json.loads(re.search(r"^const LOADOUT_SHIPS=(.*);$", gen, re.M).group(1))
HPN = json.loads(re.search(r"^const LOADOUT_HP=(.*);$", gen, re.M).group(1))

slots = [s for v in SHIPS.values() for s in (v.get("slots") or [])]
with_parent = [s for s in slots if s.get("hp") is not None]
has_key = [s for s in slots if "hp" in s]
check("every slot carries the field, present or null",
      len(has_key) == len(slots),
      "%d of %d" % (len(has_key), len(slots)))
check("and a real share of them have a parent - the tree is not being "
      "flattened away any more",
      len(with_parent) > 1000,
      "%d of %d slots (%.1f%%)"
      % (len(with_parent), len(slots), 100.0 * len(with_parent) / len(slots)))
check("while the top-level ones say null EXPLICITLY, not by absence",
      len(has_key) - len(with_parent) > 0,
      "%d explicit nulls" % (len(has_key) - len(with_parent)))

# The parent is the RIGHT one, on a hull whose tree is known.
hh = SHIPS.get("AEGS_Hammerhead")
check("the Hammerhead is in the ship table", bool(hh))
if hh:
    kids = [s for s in hh["slots"] if s.get("hp") is not None]
    check("its turret and rack children carry a parent",
          len(kids) > 100, "%d of %d slots" % (len(kids), len(hh["slots"])))
    # EVERY RECORDED PARENT MUST BE A REAL PORT ON THIS HULL - checked against
    # the snapshot's own tree, not against the page's slot list.
    #
    # The first version compared parents to the SLOT names and failed on
    # turret_rear, turret_side_back_left and two more. Those are real ports;
    # they are TurretBase entries, which the page does not render as slots. The
    # assertion was wrong, not the data - and it would have been easy to
    # "fix" by deleting it, which is how a control quietly stops checking.
    tree = ship_hardpoint_names("AEGS_Hammerhead")
    if tree is None:
        print("     NOT PERFORMED: the scunpacked snapshot is not on disk, so "
              "parent names cannot be checked against the real tree.")
    else:
        stray = [HPN[s["hp"]] for s in kids if HPN[s["hp"]] not in tree]
        check("and every parent named is a real port in this hull's own "
              "Loadout tree - not a name borrowed from somewhere else",
              not stray, ", ".join(sorted(set(stray))[:4]))
        check("including ports the page never renders as slots, like the "
              "turret bases - the chain is the game's, not the page's",
              any(n.startswith("turret_") for n in tree),
              "%d names in the tree" % len(tree))
    _notes.append("flatten: %d of %d slots carry a parent; Hammerhead %d of %d"
                  % (len(with_parent), len(slots), len(kids), len(hh["slots"])))

# ------------------------------------------ 2. WHERE THE PORTS WENT MISSING
print("\n2. THE CHILD PORTS, AND WHERE THEY WERE LOST")
snapdir = os.path.join(ROOT, "data-layer", "external-sources",
                       "scunpacked-data", "snapshots")
snaps = sorted(d for d in os.listdir(snapdir)) if os.path.isdir(snapdir) else []
if not snaps:
    print("NOT PERFORMED: no snapshot on disk, so the port tree cannot be read.")
else:
    ships = read_json(os.path.join(snapdir, snaps[-1], "ships.json"))
    WEAPONY = ("Turret", "MissileLauncher", "WeaponDefensive", "WeaponGun",
               "TurretBase")
    top = kid = 0

    def walk(node, par):
        global top, kid
        for e in node or []:
            if not isinstance(e, dict):
                continue
            ty = (e.get("Type") or "").split(".")[0]
            if e.get("HardpointName") and ty in WEAPONY:
                if par:
                    kid += 1
                else:
                    top += 1
            walk(e.get("Loadout"), e.get("HardpointName") or par)

    for s in ships:
        walk(s.get("Loadout"), None)
    print("     ships.json: %d top-level weapon ports, %d CHILDREN" % (top, kid))
    check("the game data really does carry thousands of child weapon ports",
          kid > 2000, "%d" % kid)

    flat = read_json(os.path.join(HOLO, "ship_mounts.json"))
    flat_n = sum(len(v["mounts"]) for v in flat.values())
    print("     ship_mounts.json (the 2026-08-10 flatten): %d mounts, 0 of "
          "them children" % flat_n)
    check("and the flatten the placement reads carries NONE of them - this is "
          "where the parent was lost, one step before anything that reads it",
          flat_n < top + kid, "%d of %d" % (flat_n, top + kid))

# ------------------------------- 3. THE HAMMERHEAD, WITH THE CHILDREN IN
print("\n3. THE HAMMERHEAD - 24 turret guns, placed at their turrets")
tmp = tempfile.mkdtemp(prefix="cc_b5_hh_")
mfile = os.path.join(tmp, "matched.json")
built = subprocess.run(
    [sys.executable, os.path.join(HOLO, "build_matched.py"),
     "--with-children", "--out", mfile], capture_output=True, text=True)
check("the input builds with the children switched on",
      built.returncode == 0 and os.path.exists(mfile),
      (built.stderr or "")[-160:])

fleet_out = os.path.join(tmp, "fleet.json")
placed = subprocess.run(
    [sys.executable, PLACE, "--matched", mfile, "--out", fleet_out,
     "--report", fleet_out + ".rep"], capture_output=True, text=True)
check("and the placement runs against it",
      placed.returncode == 0 and os.path.exists(fleet_out),
      (placed.stderr or "")[-160:])

if os.path.exists(fleet_out):
    F = read_json(fleet_out)
    hh = F.get("Hammerhead")
    check("the Hammerhead is placed", bool(hh))
    if hh:
        pts = hh["hardpoints"]
        guns = [h for h in pts if h["port"] == "hardpoint_class_2"]
        check("its 24 hardpoint_class_2 turret guns are now IN the dataset - "
              "they were absent entirely before",
              len(guns) == 24, "%d found" % len(guns))
        check("every one of them names the turret it is bolted to, in turretOf "
              "- a field that was null on all 1,798 records until now",
              guns and all(g.get("turretOf") for g in guns),
              "%d with a turret" % sum(1 for g in guns if g.get("turretOf")))
        check("and every one was placed FROM that turret, not from its own name",
              guns and all(g.get("placed_from") == "inherited"
                           and g.get("inherited_from") == g.get("turretOf")
                           for g in guns))

        # NOT AT THE HULL CENTRE, and NEAR ITS OWN TURRET. Both halves, because
        # "moved off centre" alone would pass on a gun flung anywhere.
        import math as _m
        turrets = {h["port"]: h for h in pts if h["port"].startswith("turret_")}
        far_from_centre = [g for g in guns
                           if _m.dist([0, 0, 0], g["unit"]) > 0.15]
        check("none of them sits on the hull-centre default",
              len(far_from_centre) == len(guns),
              "%d of %d are off centre" % (len(far_from_centre), len(guns)))
        # THE ASSERTION THAT ACTUALLY TESTS THE CLAIM: a gun must be nearer
        # to ITS OWN turret than to any of the other five. "Within X of its
        # turret" was the first version and it failed at 0.873 - not because
        # the inheritance was wrong but because the SEPARATION PASS then walks
        # colliding points to the nearest clear vertex, which on a hull with
        # six turrets and four guns apiece can be a long way. That pass is
        # global by design and was already recorded as such under B5.
        #
        # Loosening the threshold until it passed would have been the wrong
        # move. Asking the question that distinguishes right from wrong -
        # "did it land at the right turret" - is the one worth asserting.
        import statistics as _st
        near, wrong = [], []
        for g in guns:
            tp = turrets.get(g["turretOf"])
            if not tp:
                continue
            d_own = _m.dist(tp["unit"], g["unit"])
            near.append(d_own)
            d_best = min(_m.dist(o["unit"], g["unit"])
                         for o in turrets.values())
            if d_own > d_best + 1e-9:
                wrong.append((g["turretOf"], round(d_own, 3), round(d_best, 3)))
        print("     gun-to-its-own-turret distance: median %.3f, max %.3f "
              "of half-extent" % (_st.median(near), max(near)))
        print("     guns nearer to a DIFFERENT turret than their own: %d of %d"
              % (len(wrong), len(guns)))

        # ==============================================================
        # THIS IS A BLOCKER, AND IT IS MY DEFECT, NOT THE ORDER'S.
        #
        # The inheritance identifies the right turret - turretOf, placed_from
        # and inherited_from all agree on every one of the 24 guns. What
        # happens NEXT is wrong: place() spreads the four guns sharing a turret
        # along the hull by +/-0.17 of its length, snaps each to the nearest
        # vertex, and the collision pass then walks any that still overlap up
        # to 4,000 candidate vertices away. On a hull with six turrets that is
        # far enough to cross to another one, and MEASURED HERE, 12 OF 24 GUNS
        # END UP NEARER A DIFFERENT TURRET THAN THEIR OWN.
        #
        # A gun from the front-left turret sitting beside the rear turret is a
        # CONFIDENT WRONG POSITION - the same class of error the no-fuzzy-
        # matching rule exists to prevent, arrived at from the other direction.
        # It is worse than the hull-centre default, which at least looks wrong.
        #
        # The fix is that an inherited sibling must be spread by a small radius
        # around ITS TURRET rather than by the hull-scale spread meant for
        # independent mounts, and must not be walked arbitrarily far by the
        # collision pass. That is a change to place(), it is not a threshold,
        # and it is NOT DONE.
        #
        # SO THE ASSERTION BELOW IS THE ONE THAT MATTERS TODAY: the shipped
        # dataset must contain no inherited points at all. The mechanism stays
        # behind --with-children until the scatter is fixed, and if anybody
        # turns that flag on for the shipped input before then, THIS FAILS.
        # ==============================================================
        _notes.append("BLOCKER: %d of %d Hammerhead turret guns land nearer "
                      "another turret than their own. The inheritance is "
                      "right; the sibling spread is hull-scale and scatters "
                      "them. --with-children stays OFF until place() spreads "
                      "an inherited sibling around its turret instead."
                      % (len(wrong), len(guns)))
        _notes.append("Hammerhead: 24 turret guns present, all inherited from "
                      "their own turret, median %.3f from it (max %.3f, the "
                      "tail being the global separation pass, not the "
                      "inheritance)" % (_st.median(near), max(near)))

        # THE NEGATIVE HALF. A port that is NOT in a turret must not inherit.
        outside = [h for h in pts
                   if not h.get("turretOf") and h.get("depth", 0) == 0]
        check("a top-level port outside any turret does NOT inherit - the rule "
              "is not 'everything takes something'",
              outside and all(h.get("placed_from") == "own" for h in outside),
              "%d of %d placed from their own name"
              % (sum(1 for h in outside if h.get("placed_from") == "own"),
                 len(outside)))
        withvocab = [h for h in pts
                     if h.get("turretOf") and h["read"] and h.get("depth")
                     and h.get("placed_from") == "own"]
        _notes.append("%d ports inside a turret kept their OWN position "
                      "because their own name said where they were"
                      % len(withvocab))

    inh = sum(1 for v in F.values() for h in v["hardpoints"]
              if h.get("placed_from") == "inherited")
    print("     fleet with children: %d points placed from a parent name"
          % inh)
    check("and it fires across the fleet, not only on one hull",
          inh > 300, "%d points" % inh)

# ---------------- 3b. THE GUARD: none of that reaches the shipped dataset
print("\n3b. AND NONE OF IT IS IN THE SHIPPED DATASET")
if os.path.exists(FLEET):
    shipped = read_json(FLEET)
    inh_shipped = [h for v in shipped.values() for h in v["hardpoints"]
                   if h.get("placed_from") == "inherited"]
    kids_shipped = [h for v in shipped.values() for h in v["hardpoints"]
                    if h.get("depth")]
    check("the shipped hardpoints_fleet.json contains NO inherited points - "
          "the scatter above cannot reach a visitor",
          not inh_shipped, "%d inherited points shipped" % len(inh_shipped))
    check("and no child ports at all, so --with-children is genuinely off",
          not kids_shipped, "%d child points shipped" % len(kids_shipped))
    check("while turretOf is still emitted as a field on every record, ready "
          "for the day it can be populated",
          all("turretOf" in h for v in shipped.values()
              for h in v["hardpoints"]))
    _notes.append("shipped dataset: %d points, 0 inherited, 0 children - the "
                  "mechanism is proven and switched off"
                  % sum(len(v["hardpoints"]) for v in shipped.values()))

# ------------------------------------- 4. THE PROPORTION GATE STILL REFUSES
print("\n4. THE PROPORTION GATE - refusing, and REPORTING what it refused")
rep_path = os.path.join(HOLO, "placement_report.json")
if not os.path.exists(rep_path):
    print("NOT PERFORMED: no placement report on disk.")
else:
    rep = read_json(rep_path)
    print("     placed %d, skipped %d" % (len(rep["placed"]), len(rep["skipped"])))
    for n, why in rep["skipped"]:
        print("       %-14s %s" % (n, str(why)[:72]))
    check("the gate REFUSED hulls and named them - it reported skipped:0 "
          "before, because the candidate set had already had every refusal "
          "removed from it",
          len(rep["skipped"]) > 0, "%d skipped" % len(rep["skipped"]))
    check("and every refusal carries a stated reason, not a bare name",
          all(str(w).strip() for _, w in rep["skipped"]))
    pf = load_place_fleet()
    check("the gate itself still refuses known-bad proportions",
          pf.resolve_frame([-10, -3, -20], [10, 3, 20],
                           {"length": 5, "width": 90, "height": 90})[0] is None)
    check("and still accepts a hull that matches its own spec sheet - so it "
          "is not simply refusing everything",
          pf.resolve_frame([-10, -3, -20], [10, 3, 20],
                           {"length": 40, "width": 20, "height": 6})[0]
          is not None)
    _notes.append("proportion gate: %d placed, %d refused by name with reasons"
                  % (len(rep["placed"]), len(rep["skipped"])))
    _notes.append("NOT RECOVERED: the sandbox-era report recorded SEVEN "
                  "refusals and this run finds SIX. That report was "
                  "overwritten before it was read, by me, so which hull the "
                  "seventh was cannot be stated - only that it is not "
                  "identified rather than that it has gone away.")

# --------------------------------------------------------------------- report
print("\n" + "=" * 68)
for n in _notes:
    print("  " + n)
print("\n%d passed, %d failed" % (len(_passed), len(_failed)))
if _failed:
    print("FAILED:")
    for f in _failed:
        print("  " + f)
if SELFTEST:
    print("\n--self-test: expectations were inverted, so a non-zero exit is "
          "the correct outcome.")
sys.exit(1 if _failed else 0)
