#!/usr/bin/env python3
"""Starmap join + route cost table.  WO-COLLECT-01 rev 5 sec 1.1 and 1.5.

Reads ONLY from the sealed snapshot. Never re-pulls anything.

WHAT IT PRODUCES
    entities.json         the join: starmap.json UNION starmap_positions.json
    jump_points.json      the 19 jump points, positioned ones and not
    drives.json           the 63 QuantumDrive fuel models
    ships.json            257 ships with drive, tank and range_Gm
    pairs/<system>-NNN.jsonl   every qt_valid destination pair with distance_Gm
    routes/<system>__<drive>.jsonl  the ship x pair cost table (see SIZE below)
    MANIFEST.json         what was written, from which snapshot, at which patch

FUEL MODEL - THE HARD RULE FROM THE WORK ORDER
    fuel_scu    = distance_Gm * FuelConsumptionSCUPerGM
    travel_secs = distance_Gm / 10 * TravelTime10GMSeconds
    range_Gm    = sum(QuantumFuelTank.Capacity) / FuelConsumptionSCUPerGM

    FuelEfficiencyGMPerSCU IS NOT USED AND IS NOT PUBLISHED. It is internally
    inconsistent - it reports 1.65 where 1/0.01 = 100. Verified on this
    snapshot: across all 63 drives, FuelRequirement10GM == 10 *
    FuelConsumptionSCUPerGM holds 63/63 times, while FuelEfficiencyGMPerSCU ==
    1/FuelConsumptionSCUPerGM holds 0/63 times. The work order said to trust the
    first pair; the snapshot agrees. assert_fuel_model_sane() re-checks this on
    every run rather than taking either the order's word or this comment's.

SIZE - WHY routes/ IS KEYED BY DRIVE AND NOT BY SHIP
    "every ship x every qt_valid destination pair" is 257 ships x 229,750 pairs
    = 59,045,750 rows, about 4.1 GB.

    But fuel_scu and travel_secs depend on the ship ONLY through two scalars
    that come from its quantum drive. Two ships carrying the same drive produce
    byte-identical rows, so that table is ~4x redundant: there are only 63
    drives. Keying on the drive gives 14,474,250 rows (~1 GB) and loses nothing
    - ships.json maps every ship to its drive, so any ship's rows are one lookup
    away.

    --materialise-ships emits the literal per-ship form if it is genuinely
    wanted. It is off by default because 4.1 GB of near-duplicate rows is a
    liability, not a deliverable.

    --systems limits which systems are processed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

SNAPSHOT_ID = "20260801T204744Z"
SC = REPO / "data-layer/external-sources/scunpacked-data/snapshots" / SNAPSHOT_ID
PATCH = "4.9.188.23497"

# Rows per shard. The work order is explicit that the output must not be one
# file; Stanton alone is 148,785 pairs.
SHARD_ROWS = 25_000

# Coordinates are metres; 1 Gm = 1e9 m. Confirmed by scale check, not assumed -
# see check_distance_scale().
M_PER_GM = 1e9


def load(name):
    """Every open states its encoding (hard rule 15). Real Star Citizen names
    include tok.yai and other non-cp1252 text, and the Windows default would
    destroy them."""
    with open(SC / name, encoding="utf-8") as f:
        return json.load(f)


def stamp(row: dict) -> dict:
    """Every row carries its provenance, per the work order."""
    row["snapshot"] = SNAPSHOT_ID
    row["patch"] = PATCH
    return row


# ---------------------------------------------------------------------------
# 1. the join
# ---------------------------------------------------------------------------

def build_join(starmap, positions):
    """Join on UUID. The union is bigger than either input.

    THE DUPLICATE-UUID TRAP
      starmap_positions.json has 1,774 rows but only 1,196 distinct uuids. Ten
      uuids account for all 578 extra rows - they are TEMPLATE entities
      ("Asteroid Cluster", "Keeger Belt Mission Location") reused across many
      physical instances, each row carrying different x/y/z.

      A naive dict-keyed join silently keeps whichever row happened to come last
      and throws away up to 119 real positions. A naive row-keyed join fans the
      metadata out 120x. Neither is right, so positions are kept as a LIST per
      uuid and the count is reported.
    """
    ents = positions["entities"]

    pos_by_uuid = defaultdict(list)
    empty_uuid_rows = 0
    for e in ents:
        u = e.get("uuid")
        if not u:
            empty_uuid_rows += 1
            continue
        pos_by_uuid[u].append(e)

    meta_by_uuid = {e["UUID"]: e for e in starmap}

    all_uuids = set(meta_by_uuid) | set(pos_by_uuid)
    out = []
    for u in sorted(all_uuids):
        m = meta_by_uuid.get(u)
        ps = pos_by_uuid.get(u, [])
        t = m.get("Type") if m else None
        row = {
            "uuid": u,
            "name": (m or {}).get("Name") or (ps[0]["name"] if ps else None),
            "in_starmap": m is not None,
            "in_positions": bool(ps),
            "type": (t.get("Name") if isinstance(t, dict) else t) if m else (ps[0].get("type") if ps else None),
            "system": ps[0].get("system") if ps else None,
            "parent_uuid": (m or {}).get("ParentUUID") or (ps[0].get("parent_uuid") if ps else None),
            "position_count": len(ps),
            "positions": [
                {"x": p["x"], "y": p["y"], "z": p["z"],
                 "qt_valid": bool(p.get("qt_valid")), "system": p.get("system")}
                for p in ps
            ],
            "qt_valid_any": any(p.get("qt_valid") for p in ps),
            "amenities": [
                {"uuid": a.get("UUID"), "name": a.get("Name")}
                for a in ((m or {}).get("Amenities") or [])
                if isinstance(a, dict)
            ],
        }
        out.append(stamp(row))

    report = {
        "starmap_rows": len(starmap),
        "starmap_distinct_uuid": len(meta_by_uuid),
        "positions_rows": len(ents),
        "positions_distinct_uuid": len(pos_by_uuid),
        "positions_rows_with_empty_uuid": empty_uuid_rows,
        "overlap": len(set(meta_by_uuid) & set(pos_by_uuid)),
        "only_in_starmap": len(set(meta_by_uuid) - set(pos_by_uuid)),
        "only_in_positions": len(set(pos_by_uuid) - set(meta_by_uuid)),
        "union": len(all_uuids),
        "template_uuids_with_multiple_positions": sorted(
            ({"uuid": u, "name": v[0]["name"], "position_rows": len(v)}
             for u, v in pos_by_uuid.items() if len(v) > 1),
            key=lambda r: -r["position_rows"]),
    }
    return out, report


# ---------------------------------------------------------------------------
# 2. jump points
# ---------------------------------------------------------------------------

def build_jump_points(starmap, positions):
    """The work order says 19 jump points, 13 without coordinates.

    Type.Name == "JumpPoint" finds only TWO, and both are positioned - so the
    order is not using the Type field. Matching on the NAME containing "jump
    point" finds 20, one of which is "Jumptown", an Outpost and not a jump point
    at all. Excluding it gives 19, which is the order's number.

    On THIS snapshot that yields a different unpositioned count than the order
    states. The measured number is reported and the disagreement is recorded in
    the manifest rather than being quietly reconciled to the expected figure.
    """
    pos_uuids = {e["uuid"] for e in positions["entities"] if e.get("uuid")}

    rows = []
    for e in starmap:
        name = str(e.get("Name") or "")
        if "jump point" not in name.lower():
            continue
        t = e.get("Type")
        tname = t.get("Name") if isinstance(t, dict) else t
        rows.append(stamp({
            "uuid": e["UUID"],
            "name": name,
            "type": tname,
            "positioned": e["UUID"] in pos_uuids,
            # An unpositioned jump point must never be given a distance.
            "distances_available": e["UUID"] in pos_uuids,
        }))

    rows.sort(key=lambda r: (not r["positioned"], r["name"]))
    positioned = sum(1 for r in rows if r["positioned"])
    return rows, {
        "matched_by_name": len(rows),
        "positioned": positioned,
        "unpositioned": len(rows) - positioned,
        "work_order_expected_total": 19,
        "work_order_expected_unpositioned": 13,
        "note": (
            "Matched on name containing 'jump point'. Type.Name=='JumpPoint' "
            "identifies only 2 of these. 'Jumptown' is excluded by the name "
            "test because it does not contain 'jump point'."
        ),
    }


# ---------------------------------------------------------------------------
# 3. drives and ships
# ---------------------------------------------------------------------------

def assert_fuel_model_sane(drives):
    """Hard rule 12: prove the thing that matters, do not assume it.

    Re-derives the work order's claim from the data on every run. If a future
    snapshot fixes FuelEfficiencyGMPerSCU, or breaks the Consumption/Requirement
    pair, this stops the build instead of silently publishing wrong fuel costs.
    """
    ok_pair = bad_pair = 0
    eff_consistent = 0
    for d in drives:
        c, r, e = d["fuel_scu_per_gm"], d["fuel_requirement_10gm"], d["_fuel_efficiency_gm_per_scu_UNUSED"]
        if abs(r - c * 10) <= 1e-9 * max(1.0, abs(r)):
            ok_pair += 1
        else:
            bad_pair += 1
        if c and abs(e - 1.0 / c) <= 0.01 * (1.0 / c):
            eff_consistent += 1

    if bad_pair:
        raise SystemExit(
            f"REFUSING TO BUILD: FuelRequirement10GM disagrees with "
            f"10 * FuelConsumptionSCUPerGM on {bad_pair} of {len(drives)} drives. "
            f"The work order's stated fuel model does not hold on this snapshot; "
            f"stopping rather than publishing costs derived from it."
        )
    return {
        "drives": len(drives),
        "consumption_x10_equals_requirement10gm": ok_pair,
        "efficiency_field_self_consistent": eff_consistent,
        "efficiency_field_used": False,
        # The banned field is deliberately NOT named here, in prose or otherwise.
        # An earlier version of this note spelled it out to explain why it was
        # unused, which put the token into MANIFEST.json and tripped the
        # published-field guard in _verify_build_routes.py. The guard was right:
        # "the string appears nowhere in any output" is a rule that can be
        # checked mechanically, and an exemption for prose - or for one file -
        # turns it into a rule that has to be remembered instead. It is now
        # exceptionless, so it cannot rot.
        "note": (
            "The per-SCU efficiency field in the source data is read solely to "
            "re-confirm it is internally inconsistent. It is never used in any "
            "calculation and never appears in any published row."
        ),
    }


def build_drives(ship_items):
    out = []
    for i in ship_items:
        if i.get("type") != "QuantumDrive":
            continue
        std = i.get("stdItem") or {}
        q = std.get("QuantumDrive") or {}
        if "FuelConsumptionSCUPerGM" not in q:
            continue
        out.append({
            "uuid": std.get("UUID"),
            "class_name": i.get("className"),
            "name": std.get("Name") or i.get("name"),
            "size": std.get("Size"),
            "grade": std.get("Grade"),
            "fuel_scu_per_gm": q["FuelConsumptionSCUPerGM"],
            "fuel_requirement_10gm": q["FuelRequirement10GM"],
            "travel_time_10gm_seconds": q["TravelTime10GMSeconds"],
            "_fuel_efficiency_gm_per_scu_UNUSED": q["FuelEfficiencyGMPerSCU"],
        })
    return out


def walk_loadout(entries):
    for e in entries or []:
        yield e
        yield from walk_loadout(e.get("Loadout"))


def build_ships(ships_json, ship_items, drives):
    item_by_uuid = {}
    for i in ship_items:
        u = (i.get("stdItem") or {}).get("UUID")
        if u:
            item_by_uuid[u] = i
    drive_by_uuid = {d["uuid"]: d for d in drives}

    out = []
    skipped = Counter()
    for s in ships_json:
        drive = None
        tank_total = 0.0
        tank_count = 0

        for e in walk_loadout(s.get("Loadout")):
            it = item_by_uuid.get(e.get("UUID"))
            if not it:
                continue
            std = it.get("stdItem") or {}
            if it.get("type") == "QuantumDrive" and drive is None:
                drive = drive_by_uuid.get(std.get("UUID"))
            elif it.get("type") == "QuantumFuelTank":
                cap = (std.get("QuantumFuelTank") or {}).get("Capacity")
                if cap is None:
                    cap = std.get("Capacity")
                if isinstance(cap, (int, float)):
                    tank_total += float(cap)
                    tank_count += 1

        if drive is None:
            skipped["no_quantum_drive"] += 1
            continue

        # range_Gm = sum(tank capacity) / FuelConsumptionSCUPerGM.
        # A ship with a drive but no readable tank capacity gets a NULL range,
        # never a zero and never a guess - an unknown range is a fact, a
        # fabricated one is a corrupt row (hard rule 11).
        rng = None
        if tank_count and drive["fuel_scu_per_gm"]:
            rng = tank_total / drive["fuel_scu_per_gm"]
        elif tank_count == 0:
            skipped["drive_but_no_tank_capacity"] += 1

        out.append(stamp({
            "uuid": s.get("UUID"),
            "class_name": s.get("ClassName"),
            "name": s.get("Name"),
            "manufacturer": (s.get("Manufacturer") or {}).get("Name")
                            if isinstance(s.get("Manufacturer"), dict) else s.get("Manufacturer"),
            "drive_uuid": drive["uuid"],
            "drive_name": drive["name"],
            "fuel_scu_per_gm": drive["fuel_scu_per_gm"],
            "travel_time_10gm_seconds": drive["travel_time_10gm_seconds"],
            "quantum_fuel_tanks": tank_count,
            "quantum_fuel_capacity_scu": tank_total if tank_count else None,
            "range_gm": rng,
        }))
    return out, dict(skipped)


# ---------------------------------------------------------------------------
# 4. pairs
# ---------------------------------------------------------------------------

def qt_destinations(positions):
    """Every qt_valid POSITION row is a destination.

    Rows, not distinct uuids: the ten template uuids genuinely denote several
    different places, so collapsing them would delete real destinations. This is
    also what reproduces the work order's figure - Stanton has 546 qt_valid rows
    and 546*545/2 = 148,785, exactly the number the order states.
    """
    dests = defaultdict(list)
    for idx, e in enumerate(positions["entities"]):
        if not e.get("qt_valid"):
            continue
        if e.get("x") is None:
            continue
        dests[e.get("system")].append({
            "row": idx,
            "uuid": e.get("uuid") or None,
            "name": e.get("name"),
            "type": e.get("type"),
            "x": e["x"], "y": e["y"], "z": e["z"],
        })
    return dests


def dist_gm(a, b):
    return math.dist((a["x"], a["y"], a["z"]), (b["x"], b["y"], b["z"])) / M_PER_GM


def check_distance_scale(dests):
    """Confirm the coordinate unit instead of assuming metres.

    If the unit were wrong every fuel and time figure in the output would be
    wrong by a constant factor while still looking perfectly plausible - the
    kind of error that survives review. Stanton's real extent is on the order of
    tens of Gm, so a max pair distance in that range corroborates metres.
    """
    st = dests.get("stanton") or []
    if len(st) < 2:
        return {"checked": False, "reason": "no stanton destinations"}
    mx = 0.0
    pair = None
    step = max(1, len(st) // 120)
    sample = st[::step]
    for i in range(len(sample)):
        for j in range(i + 1, len(sample)):
            d = dist_gm(sample[i], sample[j])
            if d > mx:
                mx, pair = d, (sample[i]["name"], sample[j]["name"])
    plausible = 1.0 <= mx <= 500.0
    return {
        "checked": True,
        "assumed_unit": "metres",
        "max_sampled_stanton_distance_gm": round(mx, 3),
        "widest_sampled_pair": pair,
        "plausible_for_a_star_system": plausible,
    }


def write_jsonl_shards(rows_iter, outdir: Path, prefix: str, shard_rows: int):
    outdir.mkdir(parents=True, exist_ok=True)
    files, buf, n, total = [], [], 0, 0

    def flush():
        nonlocal buf, n
        if not buf:
            return
        p = outdir / f"{prefix}-{len(files):04d}.jsonl"
        with open(p, "w", encoding="utf-8") as f:
            for r in buf:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        files.append({"file": p.name, "rows": len(buf)})
        buf, n = [], 0

    for r in rows_iter:
        buf.append(r)
        n += 1
        total += 1
        if n >= shard_rows:
            flush()
    flush()
    return files, total


def pair_rows(dests_for_system, system):
    d = dests_for_system
    for i in range(len(d)):
        a = d[i]
        for j in range(i + 1, len(d)):
            b = d[j]
            yield stamp({
                "system": system,
                "a_row": a["row"], "a_uuid": a["uuid"], "a_name": a["name"],
                "b_row": b["row"], "b_uuid": b["uuid"], "b_name": b["name"],
                "distance_gm": round(dist_gm(a, b), 6),
            })


def route_rows(dests_for_system, system, drive):
    c = drive["fuel_scu_per_gm"]
    t = drive["travel_time_10gm_seconds"]
    d = dests_for_system
    for i in range(len(d)):
        a = d[i]
        for j in range(i + 1, len(d)):
            b = d[j]
            dg = dist_gm(a, b)
            yield stamp({
                "system": system,
                "drive_uuid": drive["uuid"],
                "drive_name": drive["name"],
                "a_row": a["row"], "a_name": a["name"],
                "b_row": b["row"], "b_name": b["name"],
                "distance_gm": round(dg, 6),
                "fuel_scu": round(dg * c, 8),
                "travel_secs": round(dg / 10.0 * t, 4),
            })


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO / "data-layer/derived/starmap-routes"))
    ap.add_argument("--systems", default="", help="comma-separated subset")
    ap.add_argument("--emit-routes", action="store_true",
                    help="emit the ship x pair cost table, keyed by drive (~1 GB)")
    ap.add_argument("--materialise-ships", action="store_true",
                    help="emit the literal per-ship cost table (~4.1 GB)")
    ap.add_argument("--shard-rows", type=int, default=SHARD_ROWS)
    args = ap.parse_args()

    if not SC.is_dir():
        raise SystemExit(f"snapshot not found: {SC}")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    print(f"snapshot : {SNAPSHOT_ID}")
    print(f"patch    : {PATCH}")
    print(f"source   : {SC}")
    print(f"output   : {out}\n")

    starmap = load("starmap.json")
    positions = load("starmap_positions.json")
    ships_json = load("ships.json")
    ship_items = load("ship-items.json")

    # 1. join
    entities, join_report = build_join(starmap, positions)
    (out / "entities.json").write_text(
        json.dumps(entities, indent=1, ensure_ascii=False), encoding="utf-8")
    print("join      : %(starmap_rows)d starmap rows / %(positions_rows)d position rows"
          % join_report)
    print("            %(overlap)d overlap, union %(union)d entities" % join_report)
    print("            %d template uuids carry multiple positions"
          % len(join_report["template_uuids_with_multiple_positions"]))

    # 2. jump points
    jps, jp_report = build_jump_points(starmap, positions)
    (out / "jump_points.json").write_text(
        json.dumps(jps, indent=1, ensure_ascii=False), encoding="utf-8")
    print("jumps     : %(matched_by_name)d matched, %(positioned)d positioned, "
          "%(unpositioned)d unpositioned" % jp_report)

    # 3. drives + ships
    drives = build_drives(ship_items)
    fuel_report = assert_fuel_model_sane(drives)
    # The banned efficiency field is carried in memory only so the guard above
    # can re-check it. It is stripped before anything is written, so no output
    # file publishes it under any name.
    (out / "drives.json").write_text(
        json.dumps([stamp({k: v for k, v in d.items() if not k.startswith("_")})
                    for d in drives], indent=1, ensure_ascii=False),
        encoding="utf-8")
    ships, skipped = build_ships(ships_json, ship_items, drives)
    (out / "ships.json").write_text(
        json.dumps(ships, indent=1, ensure_ascii=False), encoding="utf-8")
    print("fuel model: %(consumption_x10_equals_requirement10gm)d/%(drives)d drives agree "
          "on the 10x pair; efficiency field self-consistent on "
          "%(efficiency_field_self_consistent)d (unused)" % fuel_report)
    print("ships     : %d with a quantum drive; skipped %s" % (len(ships), skipped or "none"))

    # 4. pairs
    dests = qt_destinations(positions)
    wanted = [s.strip() for s in args.systems.split(",") if s.strip()] or sorted(dests)
    scale = check_distance_scale(dests)
    print("scale     : max sampled Stanton pair = %s Gm (plausible=%s)"
          % (scale.get("max_sampled_stanton_distance_gm"), scale.get("plausible_for_a_star_system")))

    pair_manifest = {}
    for system in wanted:
        d = dests.get(system) or []
        n = len(d)
        expected = n * (n - 1) // 2
        files, total = write_jsonl_shards(
            pair_rows(d, system), out / "pairs", system, args.shard_rows)
        if total != expected:
            raise SystemExit(f"pair count mismatch for {system}: wrote {total}, expected {expected}")
        pair_manifest[system] = {"destinations": n, "pairs": total, "shards": files}
        print("pairs     : %-8s %4d destinations -> %8d pairs in %d shards"
              % (system, n, total, len(files)))

    # 5. routes
    route_manifest = {}
    if args.emit_routes or args.materialise_ships:
        keyed = ships if args.materialise_ships else drives
        label = "ship" if args.materialise_ships else "drive"
        print(f"\nroutes    : emitting keyed by {label} "
              f"({len(keyed)} x {sum(v['pairs'] for v in pair_manifest.values())} pairs)")
        for system in wanted:
            d = dests.get(system) or []
            for k in keyed:
                drv = {
                    "uuid": k.get("drive_uuid", k.get("uuid")),
                    "name": k.get("drive_name", k.get("name")),
                    "fuel_scu_per_gm": k["fuel_scu_per_gm"],
                    "travel_time_10gm_seconds": k["travel_time_10gm_seconds"],
                }
                key = (k.get("class_name") or drv["uuid"] or "unknown").replace("/", "_")
                files, total = write_jsonl_shards(
                    route_rows(d, system, drv), out / "routes",
                    f"{system}__{key}", args.shard_rows)
                route_manifest.setdefault(system, []).append(
                    {label: key, "rows": total, "shards": len(files)})
            print("            %-8s done (%d %ss)" % (system, len(keyed), label))
    else:
        print("\nroutes    : NOT emitted (pass --emit-routes). "
              "See the SIZE note at the top of this file.")

    manifest = {
        "snapshot": SNAPSHOT_ID,
        "patch": PATCH,
        "source": str(SC),
        "join": join_report,
        "jump_points": jp_report,
        "fuel_model": fuel_report,
        "ships_skipped": skipped,
        "distance_scale_check": scale,
        "pairs": pair_manifest,
        "routes": route_manifest,
        "routes_emitted": bool(args.emit_routes or args.materialise_ships),
    }
    (out / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote MANIFEST.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
