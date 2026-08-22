#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B5: a port with no position vocabulary of its own inherits its parent's.

WHAT THE ORDER SAID, AND WHAT THE DATA SAYS
===========================================
The order's premise:

    Guns inside a turret are named `hardpoint_class_2` and similar.
    `place_fleet.py` reads a mount's NAME for position vocabulary and that name
    contains none, so the gun falls to the `None` target (0.50, 0.50, 0.44) -
    the middle of the hull.

    CONTROL: the Hammerhead. Assert that BEFORE, N markers sit within a small
    radius of hull centre; AFTER, those ports sit at their turret's position;
    and the count landing on the `None` target DROPS.

THAT BEFORE/AFTER CANNOT BE PRODUCED, AND THIS SAYS SO RATHER THAN
MANUFACTURING ONE. Measured here, on the real data:

  * the Hammerhead has ZERO placed ports whose name yields no position
    vocabulary. All 20 read something.
  * `hardpoint_class_2` does not appear in the placed fleet at ALL. The
    placement input carries only TOP-LEVEL mounts - the six turret BASES - and
    the guns inside them are children in `ships.json` that never reach it.
  * fleet-wide, 76 of 1,798 placed points read no vocabulary, on 25 ships. NOT
    ONE of them has a parent, so the fallback cannot move any of them either.
    They are countermeasure launchers whose plural name the part table misses
    (`hardpoint_countermeasures_2`), and abbreviations it has never known
    (`hardpoint_PDC_04`, `hardpoint_CML_7`). That is a real defect and it is a
    DIFFERENT one - reported, not fixed here.

So the mechanism is built exactly as specified and it is a NO-OP on today's
input. Both halves of that sentence are asserted below: the branch is driven
with constructed input that must exercise it, and the real fleet is measured
BEFORE and AFTER with geometry held constant and required to be identical.

A control that reported "0 markers moved, PASS" without the first half would be
indistinguishable from one whose fallback did not work at all.

WHAT DID CHANGE, AND IS ASSERTED ON REAL DATA: the flatten. `walk_ports()`
always knew each port's parent and the slot record always threw it away.
12,318 of 26,000 slots now carry one.

Rule 15: every open states its encoding.

Usage:
    venv/Scripts/python.exe checks/_verify_turret_inheritance.py
        [--self-test]   invert every expectation; must exit non-zero
        [--fleet]       also run the two full placements (slow, ~3 min)
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

# ---------------------------------------------------- 2. the branch can fire
print("\n2. THE FALLBACK, DRIVEN WITH INPUT THAT MUST EXERCISE IT")
print("   The real placement input has no parents at all, so a run against it")
print("   proves nothing about this branch. It is driven directly instead.")
pf = load_place_fleet()

no_vocab = pf.read_location("hardpoint_class_2", "hardpoint_class_2")
check("a bare `hardpoint_class_2` yields NO position vocabulary - the case the "
      "item is about",
      not pf.has_vocabulary(no_vocab), json.dumps(no_vocab))
check("and its trailing number is not mistaken for one",
      no_vocab["index"] == 2 and not pf.has_vocabulary(no_vocab),
      "index=%s" % no_vocab["index"])

turret = pf.read_location("turret_side_front_left", "turret_side_front_left")
check("its parent `turret_side_front_left` DOES yield vocabulary",
      pf.has_vocabulary(turret),
      "side=%s lon=%s part=%s" % (turret["side"], turret["lon"], turret["part"]))
check("naming the turret, the side and the end",
      turret["part"] == "turret" and turret["side"] == "left"
      and turret["lon"] == "front")

own = pf.read_location("hardpoint_weapon_wing_left", "hardpoint_weapon_wing_left")
check("a port that DOES know where it is keeps its own answer - the fallback "
      "is never instead of it",
      pf.has_vocabulary(own) and own["part"] == "wing" and own["side"] == "left",
      json.dumps({k: own[k] for k in ("side", "part")}))

# The target the two resolve to must actually differ, or "it inherited" would
# be a distinction with no consequence.
t_none = pf.target_uvw(no_vocab)
t_par = pf.target_uvw(turret)
check("and the two resolve to DIFFERENT targets, so inheriting has a "
      "consequence rather than being a label",
      t_none != t_par, "%s vs %s" % (t_none, t_par))
check("the un-located one lands on the None target - the middle of the hull",
      abs(t_none[0]) < 1e-9 and abs(t_none[1] - 0.5) < 1e-9,
      str(t_none))

# ------------------------------------- 3. the fallback, end to end, synthetic
print("\n3. THE SAME BRANCH THROUGH place_fleet ITSELF, on a built fixture")
fixture = {
    "matched": {
        "FIXTURE": {
            "maker": "test", "bare": "FIXTURE", "model": "__fixture__.glb",
            "dimension": {"length": 20, "width": 15, "height": 6.5},
            "mounts": [
                # no vocabulary, WITH a parent that has some -> must inherit
                {"port": "hardpoint_class_2", "where": "Class 2",
                 "type": "WeaponGun", "size": 2, "item": {},
                 "parent": "turret_side_front_left"},
                # no vocabulary, NO parent -> must stay on the None target
                {"port": "hardpoint_class_3", "where": "Class 3",
                 "type": "WeaponGun", "size": 3, "item": {},
                 "parent": None},
                # OWN vocabulary, and a parent that would say something else.
                # THE NEGATIVE CONTROL: it must keep its own.
                {"port": "hardpoint_weapon_wing_left",
                 "where": "Weapon wing left",
                 "type": "WeaponGun", "size": 3, "item": {},
                 "parent": "turret_top"},
            ],
        }
    }
}
tmp = tempfile.mkdtemp(prefix="cc_b5_")
geo = os.path.join(tmp, "geo")
os.makedirs(geo, exist_ok=True)
# A box of points, dense enough that the nearest-vertex snap has somewhere to
# land on every face. Not a ship - the question here is which TARGET each mount
# resolves to, and a cube answers that without dragging a hull into it.
pts = []
n = 11
for i in range(n):
    for j in range(n):
        for k in range(n):
            if i in (0, n - 1) or j in (0, n - 1) or k in (0, n - 1):
                pts.append([(i / (n - 1.0)) * 20 - 10,
                            (j / (n - 1.0)) * 6.5 - 3.25,
                            (k / (n - 1.0)) * 15 - 7.5])
with io.open(os.path.join(geo, "__fixture__.json"), "w", encoding="utf-8") as fh:
    json.dump({"model": "__fixture__.glb", "count": len(pts),
               "sampled": len(pts), "pts": pts,
               "min": [-10, -3.25, -7.5], "max": [10, 3.25, 7.5]}, fh)
mfile = os.path.join(tmp, "matched.json")
with io.open(mfile, "w", encoding="utf-8") as fh:
    json.dump(fixture, fh)


def run_fixture(no_inherit):
    out = os.path.join(tmp, "out%s.json" % ("_before" if no_inherit else "_after"))
    cmd = [sys.executable, PLACE, "--matched", mfile, "--geo", geo,
           "--out", out, "--report", out + ".report"]
    if no_inherit:
        cmd.append("--no-inherit")
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0 or not os.path.exists(out):
        return None, (p.stdout or "") + (p.stderr or "")
    return read_json(out), ""


before, err1 = run_fixture(True)
after, err2 = run_fixture(False)
check("the fixture places with the fallback OFF", before is not None, err1[-200:])
check("and with it ON", after is not None, err2[-200:])

if before and after:
    b = {h["port"]: h for h in before["FIXTURE"]["hardpoints"]}
    a = {h["port"]: h for h in after["FIXTURE"]["hardpoints"]}

    check("BEFORE, the un-located gun is placed from its own name and reads "
          "nothing", b["hardpoint_class_2"]["placed_from"] == "own"
          and not b["hardpoint_class_2"]["read"],
          json.dumps(b["hardpoint_class_2"]["read"]))
    check("AFTER, it is placed from its PARENT and says so",
          a["hardpoint_class_2"]["placed_from"] == "inherited",
          a["hardpoint_class_2"]["placed_from"])
    check("and it now reads the turret's side, end and part",
          set(a["hardpoint_class_2"]["read"]) >= {"side", "lon", "part"},
          json.dumps(a["hardpoint_class_2"]["read"]))
    check("AND IT MOVED - the marker is somewhere else, not merely relabelled",
          a["hardpoint_class_2"]["unit"] != b["hardpoint_class_2"]["unit"],
          "%s -> %s" % (b["hardpoint_class_2"]["unit"],
                        a["hardpoint_class_2"]["unit"]))
    check("and the record names the parent it borrowed from",
          a["hardpoint_class_2"].get("parent") == "turret_side_front_left",
          str(a["hardpoint_class_2"].get("parent")))

    # THE NEGATIVE CONTROL THE ORDER NAMES: a gun that is not in a turret is
    # placed identically before and after. A fix that moves everything is not
    # this fix.
    check("a port with its OWN vocabulary is placed IDENTICALLY before and "
          "after, even though it has a parent that says something else",
          a["hardpoint_weapon_wing_left"]["unit"]
          == b["hardpoint_weapon_wing_left"]["unit"],
          "%s vs %s" % (b["hardpoint_weapon_wing_left"]["unit"],
                        a["hardpoint_weapon_wing_left"]["unit"]))
    check("and still says it was placed from its own name",
          a["hardpoint_weapon_wing_left"]["placed_from"] == "own")
    # A PORT WITH NO VOCABULARY AND NO PARENT GETS NOTHING INVENTED FOR IT.
    #
    # Its TARGET is unchanged - it still reads nothing and is still placed from
    # its own name. Its final POSITION is not, and that is worth stating
    # plainly rather than asserting away: place() spreads the mounts that share
    # a target key apart from each other, so when hardpoint_class_2 stopped
    # sharing the None group, the one left behind stopped being spread.
    #
    # This is a genuine property of the derivation and not a defect: the
    # separation pass is global by design, because two markers on top of each
    # other cannot both be clicked. But it means "the fallback moves only the
    # ports that inherit" is FALSE, and a control claiming otherwise would be
    # asserting something the code does not do.
    check("a port with no vocabulary and NO parent has nothing invented for "
          "it - it still reads nothing and is still placed from its own name",
          not a["hardpoint_class_3"]["read"]
          and a["hardpoint_class_3"]["placed_from"] == "own",
          json.dumps(a["hardpoint_class_3"]["read"]))
    moved_sibling = (a["hardpoint_class_3"]["unit"]
                     != b["hardpoint_class_3"]["unit"])
    if moved_sibling:
        _notes.append("NOTE: the un-parented sibling's POSITION did move "
                      "(%s -> %s). Not the fallback reaching it - it stopped "
                      "sharing a spread group with the port that inherited. "
                      "The separation pass is global by design."
                      % (b["hardpoint_class_3"]["unit"],
                         a["hardpoint_class_3"]["unit"]))

    nb = sum(1 for h in before["FIXTURE"]["hardpoints"] if not h["read"])
    na = sum(1 for h in after["FIXTURE"]["hardpoints"] if not h["read"])
    check("and the count landing on the None target DROPS", na < nb,
          "%d -> %d" % (nb, na))
    _notes.append("fixture: none-target %d -> %d, one point inherited and "
                  "moved, two unchanged" % (nb, na))

# ------------------------------------------- 4. the real fleet, measured
print("\n4. THE REAL FLEET - WHAT THE ORDER'S CONTROL ASKED FOR, MEASURED")
if not os.path.exists(FLEET):
    print("NOT PERFORMED: hardpoints_fleet.json is missing.")
else:
    fleet = read_json(FLEET)
    hammer = fleet.get("Hammerhead")
    check("the Hammerhead is in the placed fleet", bool(hammer))
    if hammer:
        novocab = [h for h in hammer["hardpoints"] if not h["read"]]
        print("     Hammerhead: %d placed ports, %d with no position "
              "vocabulary" % (len(hammer["hardpoints"]), len(novocab)))
        check("REPORTED, NOT ASSERTED AS A PASS: the Hammerhead has no ports "
              "on the None target, so the order's before/after cannot be "
              "produced on it",
              len(novocab) == 0,
              "%d such ports" % len(novocab))
        ports = set(h["port"] for h in hammer["hardpoints"])
        check("and `hardpoint_class_2` is not among its placed ports at all - "
              "the turret guns are children that never reach the placement",
              "hardpoint_class_2" not in ports)

    allhp = [h for v in fleet.values() for h in v["hardpoints"]]
    nov = [h for h in allhp if not h["read"]]
    print("     fleet: %d placed points, %d read no vocabulary, on %d ships"
          % (len(allhp), len(nov),
             len(set(n for n, v in fleet.items()
                     for h in v["hardpoints"] if not h["read"]))))
    if os.path.exists(MATCHED):
        matched = read_json(MATCHED)["matched"]
        par = 0
        for name, v in matched.items():
            for m in v["mounts"]:
                if m.get("parent"):
                    par += 1
        print("     placement input: %d mounts, %d with a parent"
              % (sum(len(v["mounts"]) for v in matched.values()), par))
        check("NOT ONE mount in the placement input has a parent, so the "
              "fallback provably cannot move a marker on today's data - "
              "stated, not hidden behind a green tick",
              par == 0, "%d with a parent" % par)
        _notes.append("real input: 0 of %d mounts have a parent, so B5's "
                      "fallback is a measured NO-OP today"
                      % sum(len(v["mounts"]) for v in matched.values()))
    _notes.append("the 76 none-target points are countermeasure/PDC/CML names "
                  "the part table misses, NOT turret guns - a different "
                  "defect, reported and not fixed here")

# ------------------------------------------------ 5. optional: the full run
if FLEETRUN:
    print("\n5. THE FULL FLEET, BEFORE AND AFTER, GEOMETRY HELD CONSTANT")
    tmp2 = tempfile.mkdtemp(prefix="cc_b5_fleet_")
    outs = {}
    for tag, extra in (("before", ["--no-inherit"]), ("after", [])):
        o = os.path.join(tmp2, tag + ".json")
        p = subprocess.run([sys.executable, PLACE, "--out", o,
                            "--report", o + ".report"] + extra,
                           capture_output=True, text=True)
        outs[tag] = o if p.returncode == 0 and os.path.exists(o) else None
        if outs[tag] is None:
            print("     %s run failed: %s" % (tag, (p.stderr or "")[-300:]))
    if outs["before"] and outs["after"]:
        A, B = read_json(outs["before"]), read_json(outs["after"])
        moved = 0
        for n in A:
            ha = {h["port"]: h for h in A[n]["hardpoints"]}
            for h in B[n]["hardpoints"]:
                if ha[h["port"]]["unit"] != h["unit"]:
                    moved += 1
        check("with the same geometry and the same sampling, the fallback "
              "moves exactly 0 markers on the real fleet - which is what "
              "0 parents in the input predicts",
              moved == 0, "%d moved" % moved)
        _notes.append("full fleet run: 0 markers moved, as 0 parents predicts")
    else:
        print("     NOT PERFORMED: a placement run did not complete.")
else:
    print("\n5. THE FULL FLEET RUN was not requested (--fleet). NOT PERFORMED,")
    print("   and therefore NOT counted as a pass.")

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
