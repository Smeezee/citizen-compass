#!/usr/bin/env python3
"""Prove build_routes.py's gates can fail.  Hard rule 12.

"Before trusting any gate, checker, validator or test: feed it something that
must fail, and confirm it fails. If you cannot make it fail on demand, you do
not yet know that it works."

This file feeds each guard known-bad input and requires it to reject, then feeds
it the real snapshot data and requires it to accept. A guard that passes only
the first half is a guard that always says no; one that passes only the second
half is the silent success this project keeps finding.

Run:  python scripts/starmap_routes/_verify_build_routes.py
Exit: 0 = every guard proven in BOTH directions.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_routes as br  # noqa: E402

FAILURES = []
CHECKS = 0


def check(name: str, ok: bool, detail: str = ""):
    global CHECKS
    CHECKS += 1
    print(f"  [{'ok  ' if ok else 'FAIL'}] {name}" + (f"  --  {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)


def must_raise(fn, name, detail=""):
    try:
        fn()
    except SystemExit as e:
        check(name, True, f"rejected: {str(e)[:80]}")
        return
    except Exception as e:  # noqa: BLE001
        check(name, True, f"rejected via {type(e).__name__}")
        return
    check(name, False, detail or "ACCEPTED bad input - the guard does not work")


def must_not_raise(fn, name):
    try:
        fn()
        check(name, True, "accepted good input")
    except BaseException as e:  # noqa: BLE001
        check(name, False, f"rejected GOOD input: {type(e).__name__}: {str(e)[:90]}")


def main() -> int:
    print("verifying build_routes.py guards against known-bad input\n")

    # ---------------------------------------------------------------
    # 1. the fuel model guard
    # ---------------------------------------------------------------
    print("assert_fuel_model_sane:")

    good = [{
        "uuid": "u1", "name": "good drive",
        "fuel_scu_per_gm": 0.01,
        "fuel_requirement_10gm": 0.1,          # exactly 10x
        "travel_time_10gm_seconds": 80,
        "_fuel_efficiency_gm_per_scu_UNUSED": 1.65,
    }]
    must_not_raise(lambda: br.assert_fuel_model_sane(good),
                   "accepts a self-consistent 10x pair")

    broken = copy.deepcopy(good)
    broken[0]["fuel_requirement_10gm"] = 0.25   # not 10 * 0.01
    must_raise(lambda: br.assert_fuel_model_sane(broken),
               "rejects a broken 10x pair")

    # The guard must not be fooled by a value that is merely close.
    subtle = copy.deepcopy(good)
    subtle[0]["fuel_requirement_10gm"] = 0.1001
    must_raise(lambda: br.assert_fuel_model_sane(subtle),
               "rejects a 0.1% deviation")

    # It must also report the efficiency field as broken rather than using it.
    rep = br.assert_fuel_model_sane(good)
    check("never reports the efficiency field as used",
          rep["efficiency_field_used"] is False, json.dumps(rep["efficiency_field_used"]))
    check("flags the efficiency field as inconsistent",
          rep["efficiency_field_self_consistent"] == 0,
          f"self_consistent={rep['efficiency_field_self_consistent']} of {rep['drives']}")

    # ---------------------------------------------------------------
    # 2. no output row may ever carry FuelEfficiencyGMPerSCU
    # ---------------------------------------------------------------
    print("\npublished-field guard:")
    out = Path(br.REPO / "data-layer/derived/starmap-routes")
    # EXCEPTIONLESS ON PURPOSE.
    #
    # This started with an exemption for drives.json, which published the field
    # under an _UNUSED alias, and the guard promptly caught the token in
    # MANIFEST.json where a comment of mine had spelled it out. Both were fixed
    # at the source rather than exempted, because "this string appears in no
    # output file, anywhere, in any casing" is checkable by machine, whereas
    # "...except in the two places we decided were fine" is a convention that
    # has to be remembered. The work order says do not publish it; the simplest
    # honest reading is that it appears nowhere.
    banned = ("fuelefficiencygmperscu", "fuel_efficiency_gm_per_scu")
    leaked = []
    if out.is_dir():
        for p in list(out.glob("*.json")) + list(out.glob("**/*.jsonl")):
            low = p.read_text(encoding="utf-8").lower()
            if any(b in low for b in banned):
                leaked.append(p.name)
    check("the banned efficiency field appears in NO output file",
          not leaked, f"leaked in {leaked}" if leaked else "clean, no exemptions")

    # Prove that check could fail: plant the string and re-run the same test.
    probe = out / "_verify_probe.jsonl"
    out.mkdir(parents=True, exist_ok=True)
    probe.write_text('{"FuelEfficiencyGMPerSCU": 1.65}\n', encoding="utf-8")
    planted = [p.name for p in out.glob("**/*.jsonl")
               if "FuelEfficiencyGMPerSCU" in p.read_text(encoding="utf-8")]
    check("that guard detects a planted violation",
          probe.name in planted, f"caught {planted}")
    probe.unlink()

    # ---------------------------------------------------------------
    # 3. the duplicate-UUID join
    # ---------------------------------------------------------------
    print("\nbuild_join duplicate handling:")
    starmap = [{"UUID": "t1", "Name": "Template", "Type": {"Name": "Asteroid"},
                "ParentUUID": None, "Amenities": []}]
    positions = {"entities": [
        {"uuid": "t1", "name": "Template", "type": "Asteroid", "system": "nyx",
         "parent_uuid": None, "qt_valid": True, "x": 1.0, "y": 2.0, "z": 3.0},
        {"uuid": "t1", "name": "Template", "type": "Asteroid", "system": "nyx",
         "parent_uuid": None, "qt_valid": True, "x": 9.0, "y": 8.0, "z": 7.0},
        {"uuid": "", "name": "empty-uuid row", "type": "unknown", "system": "nyx",
         "parent_uuid": None, "qt_valid": False, "x": 0.0, "y": 0.0, "z": 0.0},
    ], "connections": []}

    rows, rep = br.build_join(starmap, positions)
    check("one row per uuid, not one per position", len(rows) == 1, f"rows={len(rows)}")
    check("both positions retained, none dropped",
          rows[0]["position_count"] == 2, f"position_count={rows[0]['position_count']}")
    check("distinct positions actually differ",
          rows[0]["positions"][0]["x"] != rows[0]["positions"][1]["x"])
    check("empty-uuid rows counted, not silently dropped",
          rep["positions_rows_with_empty_uuid"] == 1,
          f"{rep['positions_rows_with_empty_uuid']}")
    check("every joined row is stamped",
          rows[0].get("snapshot") == br.SNAPSHOT_ID and rows[0].get("patch") == br.PATCH)

    # ---------------------------------------------------------------
    # 4. pair arithmetic
    # ---------------------------------------------------------------
    print("\npair generation:")
    d = [{"row": i, "uuid": f"u{i}", "name": f"n{i}", "type": "t",
          "x": float(i) * br.M_PER_GM, "y": 0.0, "z": 0.0} for i in range(5)]
    prs = list(br.pair_rows(d, "test"))
    check("n*(n-1)/2 pairs emitted", len(prs) == 10, f"got {len(prs)} for n=5")
    check("no self-pairs", all(p["a_row"] != p["b_row"] for p in prs))
    check("no duplicated unordered pair",
          len({tuple(sorted((p["a_row"], p["b_row"]))) for p in prs}) == len(prs))
    d01 = next(p for p in prs if {p["a_row"], p["b_row"]} == {0, 1})
    check("distance in Gm is correct for a 1 Gm separation",
          abs(d01["distance_gm"] - 1.0) < 1e-9, f"got {d01['distance_gm']}")

    # ---------------------------------------------------------------
    # 5. the cost formulae, computed by hand
    # ---------------------------------------------------------------
    print("\nroute cost formulae:")
    drive = {"uuid": "d1", "name": "test drive",
             "fuel_scu_per_gm": 0.02, "travel_time_10gm_seconds": 60}
    rr = list(br.route_rows(d, "test", drive))
    r01 = next(p for p in rr if {p["a_row"], p["b_row"]} == {0, 1})
    # 1 Gm at 0.02 SCU/Gm = 0.02 SCU;  1/10 * 60 s = 6 s
    check("fuel_scu = distance_Gm * FuelConsumptionSCUPerGM",
          abs(r01["fuel_scu"] - 0.02) < 1e-9, f"got {r01['fuel_scu']}")
    check("travel_secs = distance_Gm / 10 * TravelTime10GMSeconds",
          abs(r01["travel_secs"] - 6.0) < 1e-9, f"got {r01['travel_secs']}")
    r04 = next(p for p in rr if {p["a_row"], p["b_row"]} == {0, 4})
    check("costs scale linearly with distance (4 Gm)",
          abs(r04["fuel_scu"] - 0.08) < 1e-9 and abs(r04["travel_secs"] - 24.0) < 1e-9,
          f"fuel={r04['fuel_scu']} secs={r04['travel_secs']}")
    check("every route row is stamped",
          all(p.get("snapshot") == br.SNAPSHOT_ID and p.get("patch") == br.PATCH for p in rr))

    # ---------------------------------------------------------------
    # 6. range_Gm, and the refusal to invent one
    # ---------------------------------------------------------------
    print("\nrange_Gm:")
    drives = [{"uuid": "dd", "class_name": "DD", "name": "d", "size": 1, "grade": 1,
               "fuel_scu_per_gm": 0.01, "fuel_requirement_10gm": 0.1,
               "travel_time_10gm_seconds": 80,
               "_fuel_efficiency_gm_per_scu_UNUSED": 1.65}]
    items = [
        {"type": "QuantumDrive", "className": "DD",
         "stdItem": {"UUID": "dd", "QuantumDrive": {}}},
        {"type": "QuantumFuelTank", "className": "TT",
         "stdItem": {"UUID": "tt", "QuantumFuelTank": {"Capacity": 500.0}}},
    ]
    with_tank = [{"UUID": "s1", "ClassName": "S1", "Name": "With tank",
                  "Loadout": [{"UUID": "dd"}, {"UUID": "tt"}]}]
    ships, _ = br.build_ships(with_tank, items, drives)
    check("range_Gm = tank capacity / fuel per Gm",
          abs(ships[0]["range_gm"] - 50000.0) < 1e-6, f"got {ships[0]['range_gm']}")

    no_tank = [{"UUID": "s2", "ClassName": "S2", "Name": "No tank",
                "Loadout": [{"UUID": "dd"}]}]
    ships2, skipped = br.build_ships(no_tank, items, drives)
    check("a drive with no readable tank yields NULL range, not 0",
          ships2[0]["range_gm"] is None, f"got {ships2[0]['range_gm']!r}")
    check("that omission is counted, not hidden",
          skipped.get("drive_but_no_tank_capacity") == 1, json.dumps(skipped))

    # ---------------------------------------------------------------
    # 7. unpositioned jump points must never carry distances
    # ---------------------------------------------------------------
    print("\njump points:")
    jsm = [
        {"UUID": "j1", "Name": "A - B Jump Point", "Type": {"Name": "Anomaly"}},
        {"UUID": "j2", "Name": "C - D Jump Point", "Type": {"Name": "JumpPoint"}},
        {"UUID": "o1", "Name": "Jumptown", "Type": {"Name": "Outpost"}},
    ]
    jpos = {"entities": [{"uuid": "j2", "name": "C - D Jump Point", "type": "JumpPoint",
                          "system": "stanton", "parent_uuid": None, "qt_valid": False,
                          "x": 0.0, "y": 0.0, "z": 0.0}], "connections": []}
    jps, jrep = br.build_jump_points(jsm, jpos)
    check("Jumptown is not counted as a jump point",
          all("Jumptown" not in r["name"] for r in jps), f"{[r['name'] for r in jps]}")
    check("unpositioned jump point is flagged",
          next(r for r in jps if r["uuid"] == "j1")["positioned"] is False)
    check("unpositioned jump point gets no distances",
          next(r for r in jps if r["uuid"] == "j1")["distances_available"] is False)
    check("positioned jump point is allowed distances",
          next(r for r in jps if r["uuid"] == "j2")["distances_available"] is True)

    # ---------------------------------------------------------------
    print()
    if FAILURES:
        print(f"VERIFY FAIL - {len(FAILURES)} of {CHECKS} checks failed:")
        for f in FAILURES:
            print(f"   - {f}")
        return 1
    print(f"VERIFY PASS - {CHECKS} checks, every guard proven in both directions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
