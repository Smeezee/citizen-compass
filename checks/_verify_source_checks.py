"""
Rule 12 proof for the three Stage 1 source auditors.

The order is specific about what each one must be fed:

    a tampered hash, a planted disagreement, a broken join key

An auditor whose failure path has never executed is decoration, so each of
these is driven with input that MUST fail, and separately with input that must
NOT - a checker that flags everything is as useless as one that flags nothing.

All fixtures are built in temp directories. The checkers take repo_root as a
parameter, so nothing is planted in the real repo and no real snapshot is
touched.

Run: venv/Scripts/python.exe checks/_verify_source_checks.py
"""

import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from checks.source_checks import (  # noqa: E402
    cross_source_disagreement_check,
    snapshot_integrity_check,
    uex_join_health_check,
)

PASSED, FAILED = 0, []


def check(label, cond):
    global PASSED
    if cond:
        PASSED += 1
        print(f"  ok   {label}")
    else:
        FAILED.append(label)
        print(f"  FAIL {label}")


def results(findings, name=None):
    return [f for f in findings if name is None or f.check_name == name]


def has(findings, result, needle):
    return any(f.result == result and needle.lower() in (f.details or "").lower()
               for f in findings)


def sha(p: Path):
    return hashlib.sha256(p.read_bytes()).hexdigest()


# --------------------------------------------------------------- C1 fixture
def build_snapshot(root: Path, files: dict):
    snap = root / "data-layer" / "external-sources" / "demo" / "snapshots" / "20260101T000000Z"
    snap.mkdir(parents=True)
    for name, content in files.items():
        (snap / name).write_text(content, encoding="utf-8")

    mdir = root / "data-layer" / "external-source-manifests" / "20260101T000000Z"
    mdir.mkdir(parents=True)
    manifest = {
        "snapshot_status": "complete",
        "snapshot_path": "data-layer/external-sources/demo/snapshots/20260101T000000Z",
        "file_inventory": {
            "total_files": len(files),
            "total_bytes": sum(len(c) for c in files.values()),
            "files": [
                {"file": n, "byte_size": (snap / n).stat().st_size, "sha256": sha(snap / n)}
                for n in files
            ],
        },
    }
    (mdir / "99_demo_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return snap, mdir / "99_demo_manifest.json"


def c1():
    print("\n=== C1 snapshot_integrity ===")

    print("\n-- a sealed, untouched snapshot verifies --")
    root = Path(tempfile.mkdtemp(prefix="cc_c1_ok_"))
    snap, _ = build_snapshot(root, {"a.json": '{"x":1}', "b.json": '{"y":2}'})
    fs = snapshot_integrity_check(root)
    check("clean snapshot reports PASS", has(fs, "PASS", "match their recorded sha256"))
    check("clean snapshot reports no DEFECT", not [f for f in fs if f.result == "DEFECT"])

    print("\n-- TAMPERED HASH: a file's contents change after sealing --")
    root = Path(tempfile.mkdtemp(prefix="cc_c1_tamper_"))
    snap, _ = build_snapshot(root, {"a.json": '{"x":1}', "b.json": '{"y":2}'})
    (snap / "a.json").write_text('{"x":999}', encoding="utf-8")   # the tamper
    fs = snapshot_integrity_check(root)
    check("*** tampered file is caught as CHANGED ***", has(fs, "DEFECT", "have CHANGED since sealing"))
    check("the changed file is named", any("a.json" in (f.details or "") for f in fs))

    print("\n-- MISSING FILE: something deleted from a sealed snapshot --")
    root = Path(tempfile.mkdtemp(prefix="cc_c1_missing_"))
    snap, _ = build_snapshot(root, {"a.json": '{"x":1}', "b.json": '{"y":2}'})
    (snap / "b.json").unlink()
    fs = snapshot_integrity_check(root)
    check("missing file is caught", has(fs, "DEFECT", "are MISSING from"))
    check("missing is reported DISTINCTLY from changed",
          not has(fs, "DEFECT", "have CHANGED since sealing"))

    print("\n-- UNREADABLE MANIFEST: the record itself is broken --")
    root = Path(tempfile.mkdtemp(prefix="cc_c1_badman_"))
    snap, mpath = build_snapshot(root, {"a.json": '{"x":1}'})
    mpath.write_text("{ this is not json", encoding="utf-8")
    fs = snapshot_integrity_check(root)
    check("unreadable manifest is caught", has(fs, "DEFECT", "manifest unreadable"))
    check("unreadable manifest is DISTINCT from missing/changed",
          not has(fs, "DEFECT", "MISSING from") and not has(fs, "DEFECT", "have CHANGED"))

    print("\n-- a snapshot directory that vanished entirely --")
    root = Path(tempfile.mkdtemp(prefix="cc_c1_nodir_"))
    snap, _ = build_snapshot(root, {"a.json": '{"x":1}'})
    shutil.rmtree(snap)
    fs = snapshot_integrity_check(root)
    check("vanished snapshot dir is a DEFECT when status=complete",
          has(fs, "DEFECT", "does not exist"))


# --------------------------------------------------------------- C2 fixture
def build_two_sources(root: Path, com_ship: dict, wiki_vehicle: dict):
    com = root / "data-layer" / "external-sources" / "scunpacked.com" / "snapshots" / "20260101T000000Z"
    com.mkdir(parents=True)
    (com / "ships.json").write_text(json.dumps([com_ship]), encoding="utf-8")

    wiki = root / "data-layer" / "external-sources" / "api.star-citizen.wiki" / "snapshots" / "20260101T000000Z"
    wiki.mkdir(parents=True)
    (wiki / "vehicles_page_1.json").write_text(
        json.dumps({"data": [wiki_vehicle]}), encoding="utf-8")


AGREE_COM = {"Name": "Test Ship", "Manufacturer": "Aegis Dynamics",
             "Mass": 50000, "Cargo": 10, "Size": 2}
AGREE_WIKI = {"name": "Test Ship", "manufacturer": {"name": "Aegis Dynamics"},
              "mass_hull": 49000, "mass_total": 52000, "cargo_capacity": 10,
              "size_class": 2, "size": {"en_EN": "Small"}}


def c2():
    print("\n=== C2 cross_source_disagreement ===")

    print("\n-- two sources that agree produce no disagreement --")
    root = Path(tempfile.mkdtemp(prefix="cc_c2_ok_"))
    build_two_sources(root, dict(AGREE_COM), dict(AGREE_WIKI))
    fs = cross_source_disagreement_check(root)
    warns = [f for f in fs if f.result == "WARNING"]
    check("agreeing sources yield zero WARNINGs", not warns)
    check("and it says so explicitly rather than silently",
          has(fs, "PASS", "no disagreements"))

    print("\n-- PLANTED DISAGREEMENT: cargo --")
    root = Path(tempfile.mkdtemp(prefix="cc_c2_cargo_"))
    w = dict(AGREE_WIKI); w["cargo_capacity"] = 64
    build_two_sources(root, dict(AGREE_COM), w)
    fs = cross_source_disagreement_check(root)
    check("*** planted cargo disagreement is caught ***", has(fs, "WARNING", "cargo disagrees"))
    check("BOTH values appear in the finding",
          any("10" in (f.details or "") and "64" in (f.details or "") for f in fs))
    check("BOTH sources are named",
          any("scunpacked.com" in (f.details or "") and "star-citizen.wiki" in (f.details or "")
              for f in fs))
    check("it does NOT pick a winner",
          any("does not choose between sources" in (f.details or "") for f in fs))

    print("\n-- PLANTED DISAGREEMENT: manufacturer --")
    root = Path(tempfile.mkdtemp(prefix="cc_c2_manu_"))
    w = dict(AGREE_WIKI); w["manufacturer"] = {"name": "Roberts Space Industries"}
    build_two_sources(root, dict(AGREE_COM), w)
    fs = cross_source_disagreement_check(root)
    check("planted manufacturer disagreement is caught",
          has(fs, "WARNING", "manufacturer disagrees"))

    print("\n-- an abbreviation is NOT a disagreement --")
    root = Path(tempfile.mkdtemp(prefix="cc_c2_abbrev_"))
    c = dict(AGREE_COM); c["Manufacturer"] = "RSI"
    w = dict(AGREE_WIKI); w["manufacturer"] = {"name": "RSI Roberts Space Industries"}
    build_two_sources(root, c, w)
    fs = cross_source_disagreement_check(root)
    check("'RSI' vs 'RSI Roberts Space Industries' is not flagged",
          not has(fs, "WARNING", "manufacturer disagrees"))

    print("\n-- mass inside the hull..total bracket is NOT flagged --")
    root = Path(tempfile.mkdtemp(prefix="cc_c2_massok_"))
    c = dict(AGREE_COM); c["Mass"] = 51000      # between hull 49000 and total 52000
    build_two_sources(root, c, dict(AGREE_WIKI))
    fs = cross_source_disagreement_check(root)
    check("mass between hull and total is not a disagreement",
          not has(fs, "WARNING", "mass disagrees"))

    print("\n-- mass no definition explains IS flagged --")
    root = Path(tempfile.mkdtemp(prefix="cc_c2_massbad_"))
    c = dict(AGREE_COM); c["Mass"] = 3275858    # the real Carrack-style gap
    build_two_sources(root, c, dict(AGREE_WIKI))
    fs = cross_source_disagreement_check(root)
    check("*** mass far outside the bracket is caught ***", has(fs, "WARNING", "mass disagrees"))


# --------------------------------------------------------------- C3 fixture
def build_uex(root: Path, uex_items: list, fps_records: list):
    uex = root / "data-layer" / "external-sources" / "uexcorp" / "snapshots" / "20260101T000000Z"
    uex.mkdir(parents=True)
    (uex / "items_category_1.json").write_text(
        json.dumps({"status": "ok", "data": uex_items}), encoding="utf-8")

    sc = root / "data-layer" / "external-sources" / "scunpacked-data" / "snapshots" / "20260101T000000Z"
    sc.mkdir(parents=True)
    (sc / "fps-items.json").write_text(json.dumps(fps_records), encoding="utf-8")


def c3():
    print("\n=== C3 uex_join_health ===")
    good_uuid = "2b021c8a-5cfc-4316-a228-6e8e0e220162"
    other_uuid = "11111111-2222-3333-4444-555555555555"

    print("\n-- a healthy join reports a high rate --")
    root = Path(tempfile.mkdtemp(prefix="cc_c3_ok_"))
    build_uex(root,
              [{"name": "A", "uuid": good_uuid}, {"name": "B", "uuid": other_uuid}],
              [{"reference": good_uuid}, {"stdItem": {"UUID": other_uuid}}])
    fs = uex_join_health_check(root)
    check("100% join reports PASS", has(fs, "PASS", "join to fps-items.json"))

    print("\n-- BROKEN JOIN KEY: fps-items carries different UUIDs --")
    root = Path(tempfile.mkdtemp(prefix="cc_c3_broken_"))
    build_uex(root,
              [{"name": "A", "uuid": good_uuid}, {"name": "B", "uuid": other_uuid}],
              [{"reference": "99999999-0000-0000-0000-000000000000"}])
    fs = uex_join_health_check(root)
    check("*** a broken join key is caught, not reported as PASS ***",
          any(f.result in ("DEFECT", "WARNING") and "join to fps-items" in (f.details or "")
              for f in fs))
    check("no PASS is emitted for the join rate",
          not has(fs, "PASS", "join to fps-items.json"))

    print("\n-- join key ABSENT from fps-items entirely --")
    root = Path(tempfile.mkdtemp(prefix="cc_c3_nokey_"))
    build_uex(root, [{"name": "A", "uuid": good_uuid}], [{"name": "no uuid fields here"}])
    fs = uex_join_health_check(root)
    check("absent join key is a DEFECT", has(fs, "DEFECT", "documented join key is absent"))

    print("\n-- uuid presence is measured from the data, not the manifest --")
    root = Path(tempfile.mkdtemp(prefix="cc_c3_presence_"))
    build_uex(root,
              [{"name": "A", "uuid": good_uuid}, {"name": "B"}, {"name": "C"}],
              [{"reference": good_uuid}])
    fs = uex_join_health_check(root)
    check("reports 1 of 3 carrying a uuid",
          any("1 of 3" in (f.details or "") for f in fs))


def main():
    c1()
    c2()
    c3()
    print("\n" + "=" * 66)
    if FAILED:
        print(f"FAILED {len(FAILED)} of {PASSED + len(FAILED)} assertions:")
        for x in FAILED:
            print(f"  - {x}")
        return 1
    print(f"All {PASSED} assertions passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
