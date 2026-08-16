#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the configuration builder's checks can FAIL. Hard rule 12.

`build_ship_configurations.py` decides what an edition actually gives you and
how a ship can be obtained. Both answers go on a page a visitor reads as fact,
and both are the kind of thing that looks right until somebody plants a case
that must break it.

So each one is driven here with input that MUST fail it, and with input that
must pass. Both directions: a diff that reports everything is as useless as one
that reports nothing, and an acquisition check that answers "not available" to
everything would look reassuringly cautious while being wrong.

Run:  python checks/_verify_ship_configurations.py

Rule 15: encodings stated.
"""

import copy
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from build_ship_configurations import (  # noqa: E402
    component_changes, shop_route, site_row, PLACEHOLDER,
)

failures = []


def check(name, ok, detail):
    if ok:
        print("  [ok  ] %s" % name)
    else:
        failures.append("%s -- %s" % (name, detail))
        print("  [FAIL] %s\n         %s" % (name, detail))


def ship(entries):
    """A ship record shaped the way the snapshot shapes one."""
    return {"Name": "Fixture", "Loadout": entries}


def entry(path, cls, name, typ="PowerPlant.Power", children=None):
    return {"Path": path, "ClassName": cls, "Name": name, "Type": typ,
            "Loadout": children or []}


BASE = ship([
    entry(["hardpoint_power_plant_1"], "PWR_A", "ZapJet"),
    entry(["hardpoint_shield_1"], "SHD_A", "INK", "Shield.Shield"),
    entry(["hardpoint_weapon_left"], "MNT_A", "Gimbal", "Turret.GunTurret", [
        entry(["hardpoint_weapon_left", "hardpoint_class_2"], "GUN_A", "Repeater",
              "WeaponGun.Gun"),
    ]),
])


def main():
    print("build_ship_configurations - driving the checks with input that must fail")
    print()

    # ---- 1. THE DIFF FINDS A REAL SWAP --------------------------------
    swapped = copy.deepcopy(BASE)
    swapped["Loadout"][0]["ClassName"] = "PWR_B"
    swapped["Loadout"][0]["Name"] = "DynaFlux"
    changes, ph, ports = component_changes(BASE, swapped)
    check("a swapped component IS reported",
          len(changes) == 1 and changes[0]["port"] == "hardpoint_power_plant_1"
          and changes[0]["to"]["name"] == "DynaFlux",
          "got %r" % changes)

    # NEGATIVE CONTROL. A ship against itself must report nothing, or every
    # edition would look like a refit and the number on the page is noise.
    changes0, ph0, _ = component_changes(BASE, copy.deepcopy(BASE))
    check("NEGATIVE CONTROL: a ship against itself reports no changes",
          changes0 == [] and ph0 == 0,
          "got %d change(s) comparing a ship with a copy of itself" % len(changes0))

    # ---- 2. A SWAP INSIDE A MOUNT IS STILL FOUND ----------------------
    #
    # The guns hang off mounts, so a diff that only walked the top level would
    # miss every weapon change on most hulls.
    nested = copy.deepcopy(BASE)
    nested["Loadout"][2]["Loadout"][0]["ClassName"] = "GUN_B"
    nested["Loadout"][2]["Loadout"][0]["Name"] = "Cannon"
    changes, _, _ = component_changes(BASE, nested)
    check("a swap NESTED inside a mount is found",
          len(changes) == 1 and changes[0]["port"].endswith("hardpoint_class_2"),
          "got %r - a top-level-only walk would miss every gun" % changes)

    # ---- 3. PLACEHOLDER CHURN IS EXCLUDED, AND COUNTED ----------------
    ph_base = copy.deepcopy(BASE)
    ph_base["Loadout"].append(entry(["hardpoint_wingcap"], "PH_A", PLACEHOLDER))
    ph_ed = copy.deepcopy(ph_base)
    ph_ed["Loadout"][-1]["ClassName"] = "PH_B"   # different class, still a placeholder
    changes, ph, _ = component_changes(ph_base, ph_ed)
    check("a placeholder-to-placeholder difference is NOT counted as a refit",
          changes == [] and ph == 1,
          "got %d change(s), %d placeholder(s) - counting these overstates what "
          "an edition gives you, on a page whose job is to answer exactly that"
          % (len(changes), ph))

    # NEGATIVE CONTROL for the exclusion: a REAL part replacing a placeholder
    # must still be reported, or the rule above quietly hides real fittings.
    real_ed = copy.deepcopy(ph_base)
    real_ed["Loadout"][-1]["ClassName"] = "WING_A"
    real_ed["Loadout"][-1]["Name"] = "Wing Cap"
    changes, ph, _ = component_changes(ph_base, real_ed)
    check("NEGATIVE CONTROL: a real part replacing a placeholder IS reported",
          len(changes) == 1 and ph == 0,
          "got %r / %d placeholder(s)" % (changes, ph))

    # ---- 4. ORDER IS NOT A CHANGE -------------------------------------
    #
    # Keyed on Path rather than PortId deliberately: PortId is positional
    # ("loadout.47.loadout.0") and shifts when CIG reorders a file, which would
    # make two identical ships look like a hundred refits.
    reordered = ship(list(reversed(copy.deepcopy(BASE)["Loadout"])))
    changes, _, _ = component_changes(BASE, reordered)
    check("NEGATIVE CONTROL: reordering the file is not a component change",
          changes == [],
          "got %d change(s) from reordering alone - the diff is keyed on "
          "position rather than on the port" % len(changes))

    # ---- 5. THE SHOP ROUTE, BOTH DIRECTIONS ---------------------------
    rows = [{"vehicle_name": "Clipper", "terminal_name": "New Deal Lorville",
             "price_buy": 3619730},
            {"vehicle_name": "Clipper", "terminal_name": "Buy and Fly Ruin Station",
             "price_buy": 3810240}]
    r = shop_route(rows, "Clipper")
    check("a ship with terminals reports the shop route as available",
          r["available"] and r["verified"] and r["price_auec"] == 3619730
          and len(r["terminals"]) == 2,
          "got %r" % r)

    r = shop_route(rows, "Tiburon")
    check("NEGATIVE CONTROL: a ship with NO terminals reports not available",
          r["available"] is False and r["verified"] is True and r.get("note"),
          "got %r" % r)
    check("and the absence is recorded as an absence, not as a certainty",
          "not a claim that it can never be bought" in (r.get("note") or ""),
          "a terminal added after the pull would look identical from here, and "
          "the record has to say so")

    # A ROUTE THAT ANSWERS 'NO' TO EVERYTHING WOULD PASS THE CHECK ABOVE.
    # This is the control that catches it.
    r = shop_route([], "Clipper")
    check("NEGATIVE CONTROL: with no rows at all, even a real ship is 'not "
          "available' - so the check above is about the DATA, not the name",
          r["available"] is False,
          "got %r" % r)

    # ---- 6. A MISSING SITE ROW IS A STOP ------------------------------
    #
    # The first version of site_row returned None and let the pledge route say
    # "no pledge price", which is a FALSE statement dressed as a cautious one:
    # the Clipper's row says $150 and has for months. Silence must not be an
    # answer here.
    html = '[{"id":72,"name":"Clipper","manufacturer":"Drake","pledge_price_usd":150.0}]'
    row = site_row(html, "Clipper")
    check("a present site row is read",
          row and row.get("pledge_price_usd") == 150.0, "got %r" % row)

    stopped = False
    try:
        site_row(html, "Nonexistent Ship")
    except SystemExit:
        stopped = True
    check("NEGATIVE CONTROL: a MISSING site row stops the build",
          stopped,
          "it returned quietly instead - which is how a ship that costs $150 "
          "gets published as having no pledge price")

    print()
    if failures:
        print("VERIFY FAILED (%d)" % len(failures))
        for f in failures:
            print("  - %s" % f)
        return 1
    print("VERIFY PASSED - every check above was driven with input that must "
          "fail it, and it did")
    return 0


if __name__ == "__main__":
    sys.exit(main())
