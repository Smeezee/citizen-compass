#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Every name on the page is the name the GAME shows, or is honestly ours.

RULE16: INDEPENDENT - the truth comes from CIG's own localisation file,
    `labels.json` in the scunpacked snapshot, which is the table the game
    itself renders from. The page is built from ships.json and ship-items.json
    and never reads labels.json, so neither file can see the other.

SLEVEN'S RULE, 2026-08-29, in his own words: *"The words we use need to match
the ones that the players would see in game."* A name in CIG's code files is
not that. `labels.json` is - it is what the client puts on screen.

WHAT THIS REFUSES
=================
    PLACEHOLDER     CIG ships `<= PLACEHOLDER =>` for names it has not written
                    yet. 61 of them reached the deployed page as paint names.
                    Publishing CIG's placeholder as a product name is worse
                    than saying nothing.
    truncated       A display name cut off at an escaped quote. The game's
                    `MRX "Torrent"` reached the page as `MRX \`. Six of these.
    a class name    A displayed name still carrying underscores is the code's
                    identifier, not a name - `MRCK_S04_KRIG_S65_Stingray_Left`.
    disagreement    Where CIG ships a display name and ours is different, ours
                    is wrong by definition. 23 of these, including a Gladius
                    part labelled Avenger and a VariPuck S7 labelled S6.

WHAT IT DELIBERATELY ALLOWS
===========================
**Most items have no CIG display name at all** - 3,724 of 3,943 when this was
written. That is not a fault to fix: CIG localises what a player can pick in
the Vehicle Loadout screen and leaves the rest, so a ship's own welded-in
thrusters have no name because nobody ever reads one. **Our own plain wording
is correct there and this control does not touch it.**

**Shorthand the game itself displays is kept.** CIG's own strings say
`PDC` and `Fixed Mav Thruster`. Expanding those would move us further from what
a player sees, not closer.

Rule 15: labels.json and the payload are opened utf-8 with errors=replace.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAYLOAD = os.path.join(ROOT, "testing", "_deploy", "loadout_data.gen.js")
SNAPS = os.path.join(ROOT, "data-layer", "external-sources",
                     "scunpacked-data", "snapshots")
SELFTEST = "--self-test" in sys.argv

ITEM_RX = re.compile(r'"([A-Za-z0-9_\.\-]{4,})":\{(?=[^{}]*"n":)([^{}]*)\}')
NAME_RX = re.compile(r'"n":"([^"]*)"')


def newest_labels():
    if not os.path.isdir(SNAPS):
        return None, "no snapshot directory"
    for snap in sorted(os.listdir(SNAPS), reverse=True):
        p = os.path.join(SNAPS, snap, "labels.json")
        if os.path.exists(p):
            d = json.load(open(p, encoding="utf-8", errors="replace"))
            return ({k.lower(): v for k, v in d.items()
                     if k.lower().startswith("item_name")}, snap)
    return None, "no labels.json in any snapshot"


def page_items(src):
    out = []
    for k, body in ITEM_RX.findall(src):
        m = NAME_RX.search(body)
        if m:
            out.append((k, m.group(1)))
    return out


def classify(items, cig):
    bad = {"placeholder": [], "truncated": [], "class name": [], "disagrees": []}
    for k, n in items:
        if "PLACEHOLDER" in n.upper():
            bad["placeholder"].append((k, n, None))
            continue
        if n.rstrip().endswith("\\") or not n.strip():
            bad["truncated"].append((k, n, cig.get("item_name" + k.lower())))
            continue
        if re.search(r"_[A-Za-z0-9]", n):
            bad["class name"].append((k, n, cig.get("item_name" + k.lower())))
            continue
        c = cig.get("item_name" + k.lower())
        if c and c.strip() != n.strip():
            bad["disagrees"].append((k, n, c))
    return bad


def report(items, cig, snap):
    bad = classify(items, cig)
    covered = sum(1 for k, _n in items if "item_name" + k.lower() in cig)
    print("display names: %d item name(s) on the page, %d with a CIG display "
          "name (snapshot %s)" % (len(items), covered, snap))
    total = sum(len(v) for v in bad.values())
    if not total:
        print()
        print("PASS - no placeholder, no truncation, no class name on screen, "
              "and every name CIG ships is the name we print.")
        return True, 0
    print()
    print("  REFUSED - %d name(s) a visitor can read:" % total)
    for why in ("placeholder", "truncated", "class name", "disagrees"):
        rows = bad[why]
        if not rows:
            continue
        print("   %-12s %d" % (why, len(rows)))
        for k, n, c in rows[:5]:
            print("      %-34s shows %s" % (k[:34], repr(n)[:34]))
            if c:
                print("      %-34s game  %s" % ("", c[:52]))
        if len(rows) > 5:
            print("      + %d more" % (len(rows) - 5))
    return False, total


def main():
    if not os.path.exists(PAYLOAD):
        print("NOT PERFORMED - no %s. Nothing has been built." % PAYLOAD)
        return 2
    cig, snap = newest_labels()
    if cig is None:
        print("NOT PERFORMED - %s, so there is nothing to check the page "
              "against. No name was verified." % snap)
        return 2
    src = open(PAYLOAD, encoding="utf-8", errors="replace").read()
    items = page_items(src)
    if not items:
        print("NOT PERFORMED - no item names parsed out of the payload.")
        return 2
    clean, _n = report(items, cig, snap)
    if SELFTEST:
        return selftest(clean, cig)
    return 0 if clean else 1


def selftest(clean_now, cig):
    """RULE 12. Plant each defect and require this control to see it, and
    plant the things it MUST tolerate and require silence."""
    print()
    print("SELF-TEST")
    print("  negative control: the real payload passes             %s"
          % ("ok" if clean_now else "NOT YET - payload still carries names"))

    planted = [
        ("placeholder", [("Paint_Test", "<= PLACEHOLDER =>")]),
        ("truncated", [("Turret_X", "MRX \\")]),
        ("class name", [("Rack_X", "MRCK_S04_KRIG_S65_Stingray_Left")]),
    ]
    ok = True
    for why, rows in planted:
        found = classify(rows, {})
        caught = bool(found[why])
        print("  plant %-22s %s" % (why, "caught" if caught else "NOT CAUGHT"))
        ok = ok and caught

    # disagreement needs a CIG name to disagree with
    fake = {"item_namewidget_a": "Aegis Avenger - Noise Launcher"}
    d = classify([("Widget_A", "Aegis Gladius - Noise Launcher")], fake)
    print("  plant %-22s %s" % ("disagrees",
                                "caught" if d["disagrees"] else "NOT CAUGHT"))
    ok = ok and bool(d["disagrees"])

    # AND WHAT IT MUST NOT FIRE ON.
    safe = [
        ("a name CIG does not ship", [("AEGS_Avenger_Thruster_Main",
                                       "AEGS Avenger Thruster Main")], {}),
        ("shorthand the game itself shows", [("Turret_PDC_X", "PDC")], {}),
        ("a CIG name we match exactly", [("Widget_B", "Fixed Mav Thruster")],
         {"item_namewidget_b": "Fixed Mav Thruster"}),
    ]
    for label, rows, table in safe:
        found = classify(rows, table)
        fired = [w for w, v in found.items() if v]
        print("  allow %-22s %s" % (label[:22],
                                    "correctly quiet" if not fired
                                    else "WRONGLY FLAGGED: %s" % fired[0]))
        ok = ok and not fired

    print()
    if ok and not clean_now:
        print("DETECTION PROVEN - every planted defect is caught and nothing "
              "safe is flagged - but the real payload is not clean yet.")
        print("Exiting NON-ZERO: detection works, the payload does not.")
        return 9
    if ok:
        print("SELF-TEST PASSED - defects are caught, safe names are not, and "
              "the payload is clean.")
        print("Exiting NON-ZERO on purpose: the suite requires a control's "
              "self-test to be rejected. This is the GOOD outcome.")
        return 9
    print("SELF-TEST FAILED - this is not currently a control.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
