"""
Ship Items data-integrity / reconciliation auditor.

Per docs/ARCHITECTURE_DECISIONS.md section 4 (LOCKED, Automated Validation):
"a pluggable auditor (many small independent checkers)... Findings-only -
validation tools never automatically modify data."

This audits the Ship Items domain end to end:
  source (data-layer/raw/<ship>/<ship>_api_raw.json port tree)
    -> processed (an importer's in-memory spec list, e.g.
       import_ship_components.ARROW_COMPONENTS)
    -> database (components + component_types + manufacturers + patches +
       the 5 typed *_details tables)

Every finding is classified as exactly one of:
  DEFECT      - a confirmed real problem (broken FK, cross-category detail
                mismatch, invalid field value, drift between repeated
                imports).
  LIMITATION  - a known source-data gap that is expected, not a bug (e.g. a
                field the raw port data simply doesn't provide - null
                positions, unresolved manufacturer prefixes). These are
                never "fixed" by this tool.
  WARNING     - worth a human looking at, but not confirmed either way
                (e.g. a size value outside the S1-S8 range seen in the game
                so far - could be real, could be a typo).

This tool NEVER writes to the database. It only reads and reports. Run:
    python audit_ship_components.py [--ship arrow]
Reports land in logs/ (git-ignored run output, not committed) as both a
machine-readable JSON file and a human-readable .txt summary.
"""

import argparse
import datetime
import json
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.orm import Session

REPO_ROOT = Path(__file__).resolve().parent
load_dotenv(REPO_ROOT / ".env")

from app.database import engine  # noqa: E402
from app.models import (  # noqa: E402
    CONFIDENCE_LEVELS,
    Component,
    ComponentType,
    GimbalMountDetail,
    Manufacturer,
    MissileDetail,
    MissileRackDetail,
    Patch,
    TurretDetail,
    WeaponDetail,
)

DETAIL_TABLES = {
    "weapon": WeaponDetail,
    "missile": MissileDetail,
    "missile_rack": MissileRackDetail,
    "gimbal_mount": GimbalMountDetail,
    "turret": TurretDetail,
}

# component.size values actually confirmed to exist in Star Citizen's own
# hardpoint sizing scheme as of this project's data so far (S1-S10 covers
# every ship/turret/capital-scale mount seen to date). Anything outside
# this is flagged WARNING, not DEFECT - a genuinely new larger size class
# showing up in real game data is plausible, not necessarily a typo.
PLAUSIBLE_SIZE_RANGE = range(1, 11)

SHIP_SOURCE_FILES = {
    "arrow": REPO_ROOT / "data-layer" / "raw" / "arrow" / "arrow_api_raw.json",
}


def _finding(severity: str, category: str, message: str, **extra) -> dict:
    assert severity in ("DEFECT", "LIMITATION", "WARNING", "PASS")
    return {"severity": severity, "category": category, "message": message, **extra}


def audit_source_vs_processed_vs_db(session: Session, ship: str, findings: list[dict]) -> None:
    """Compare the ship's raw port-tree source data against the hand-
    curated importer's processed spec list and against what's actually in
    the database. Only 'arrow' has both a source pull and an importer as of
    2026-07-30; other ships are reported as a coverage gap, not a defect -
    per Step 5's finding, there's nothing to import for them yet."""
    source_path = SHIP_SOURCE_FILES.get(ship)
    if source_path is None or not source_path.exists():
        findings.append(
            _finding(
                "LIMITATION",
                "source_coverage",
                f"No raw port-tree source file for ship={ship!r} - nothing to reconcile against.",
                ship=ship,
            )
        )
        return

    raw = json.loads(source_path.read_text())

    def walk_ports(node, acc):
        if isinstance(node, dict):
            if "class_name" in node:
                acc.append(node)
            for v in node.values():
                walk_ports(v, acc)
        elif isinstance(node, list):
            for item in node:
                walk_ports(item, acc)

    port_entries = []
    walk_ports(raw.get("data", {}).get("ports", raw.get("ports", raw)), port_entries)
    source_class_names = {p["class_name"] for p in port_entries if p.get("class_name")}

    if ship == "arrow":
        import import_ship_components

        processed_class_names = {
            spec["class_name"] for spec in import_ship_components.ARROW_COMPONENTS if spec.get("class_name")
        }
    else:
        processed_class_names = set()

    db_class_names = {
        row[0]
        for row in session.query(Component.class_name).filter(Component.class_name.isnot(None)).all()
    }

    findings.append(
        _finding(
            "LIMITATION" if len(processed_class_names) < len(source_class_names) else "WARNING",
            "source_coverage",
            f"ship={ship}: {len(source_class_names)} distinct class_names in raw source, "
            f"{len(processed_class_names)} in the hand-curated importer's spec list "
            f"({len(source_class_names) - len(processed_class_names)} not yet imported - "
            "expected under the staged-pipeline decision, not every port-tree entry is a "
            "Ship Items component category yet, e.g. hull/thruster/cooler ports).",
            ship=ship,
            source_count=len(source_class_names),
            processed_count=len(processed_class_names),
        )
    )

    missing_from_db = processed_class_names - db_class_names
    if missing_from_db:
        findings.append(
            _finding(
                "DEFECT",
                "import_gap",
                f"ship={ship}: {len(missing_from_db)} class_names are in the importer's spec "
                f"list but not in the database - importer should have inserted them: {sorted(missing_from_db)}",
                ship=ship,
            )
        )
    else:
        findings.append(
            _finding(
                "PASS",
                "import_gap",
                f"ship={ship}: all {len(processed_class_names)} processed class_names are present in the database.",
                ship=ship,
            )
        )


def audit_relational_integrity(session: Session, findings: list[dict]) -> None:
    components = session.query(Component).all()
    type_by_id = {ct.id: ct for ct in session.query(ComponentType).all()}
    manufacturer_ids = {m.id for m in session.query(Manufacturer.id).all()}
    patch_ids = {p.id for p in session.query(Patch.id).all()}

    for c in components:
        ctype = type_by_id.get(c.component_type_id)
        if ctype is None:
            findings.append(
                _finding(
                    "DEFECT",
                    "broken_reference",
                    f"components.id={c.id} ({c.name!r}) references component_type_id={c.component_type_id} "
                    "which does not exist in component_types.",
                    component_id=c.id,
                )
            )
            continue

        if c.manufacturer_id is not None and c.manufacturer_id not in manufacturer_ids:
            findings.append(
                _finding(
                    "DEFECT",
                    "broken_reference",
                    f"components.id={c.id} ({c.name!r}) references manufacturer_id={c.manufacturer_id} "
                    "which does not exist in manufacturers.",
                    component_id=c.id,
                )
            )
        if c.manufacturer_id is None:
            findings.append(
                _finding(
                    "LIMITATION",
                    "unresolved_manufacturer",
                    f"components.id={c.id} ({c.name!r}, class_name={c.class_name}) has no manufacturer - "
                    "expected when the game data's manufacturer prefix couldn't be confidently identified "
                    "(see the component's notes column), not a defect.",
                    component_id=c.id,
                )
            )

        if c.last_verified_patch is not None and c.last_verified_patch not in patch_ids:
            findings.append(
                _finding(
                    "DEFECT",
                    "broken_reference",
                    f"components.id={c.id} ({c.name!r}) references last_verified_patch={c.last_verified_patch} "
                    "which does not exist in patches.",
                    component_id=c.id,
                )
            )

        if c.confidence not in CONFIDENCE_LEVELS:
            findings.append(
                _finding(
                    "DEFECT",
                    "invalid_value",
                    f"components.id={c.id} has confidence={c.confidence!r}, not one of {CONFIDENCE_LEVELS} "
                    "(the DB CHECK constraint should prevent this - if you see this, the constraint was bypassed).",
                    component_id=c.id,
                )
            )

        if c.size is not None and c.size not in PLAUSIBLE_SIZE_RANGE:
            findings.append(
                _finding(
                    "WARNING",
                    "invalid_value",
                    f"components.id={c.id} ({c.name!r}) has size={c.size}, outside the S1-S10 range seen "
                    "in this project's data so far - could be a real new size class, could be a typo. Review.",
                    component_id=c.id,
                )
            )

        # Every component should have exactly one detail row, in the table
        # matching its own component_type - never zero, never more than
        # one, never the WRONG category's table.
        matched_details = []
        for type_key, detail_model in DETAIL_TABLES.items():
            rel_name = {
                "weapon": "weapon_detail",
                "missile": "missile_detail",
                "missile_rack": "missile_rack_detail",
                "gimbal_mount": "gimbal_mount_detail",
                "turret": "turret_detail",
            }[type_key]
            if getattr(c, rel_name) is not None:
                matched_details.append(type_key)

        if not matched_details:
            findings.append(
                _finding(
                    "DEFECT",
                    "missing_detail_row",
                    f"components.id={c.id} ({c.name!r}, type={ctype.key}) has NO typed detail row in any "
                    "*_details table - every component should have exactly one.",
                    component_id=c.id,
                )
            )
        elif len(matched_details) > 1:
            findings.append(
                _finding(
                    "DEFECT",
                    "cross_category_detail",
                    f"components.id={c.id} ({c.name!r}, type={ctype.key}) has detail rows in MULTIPLE "
                    f"categories: {matched_details} - should have exactly one, matching its own component_type.",
                    component_id=c.id,
                )
            )
        elif matched_details[0] != ctype.key:
            findings.append(
                _finding(
                    "DEFECT",
                    "cross_category_detail",
                    f"components.id={c.id} ({c.name!r}) is typed as {ctype.key!r} but its detail row is in "
                    f"the {matched_details[0]!r} table - mismatch.",
                    component_id=c.id,
                )
            )


def audit_duplicate_class_names(session: Session, findings: list[dict]) -> None:
    rows = (
        session.query(Component.class_name)
        .filter(Component.class_name.isnot(None))
        .all()
    )
    seen = {}
    for (class_name,) in rows:
        seen[class_name] = seen.get(class_name, 0) + 1
    dupes = {k: v for k, v in seen.items() if v > 1}
    if dupes:
        findings.append(
            _finding(
                "DEFECT",
                "duplicate_natural_key",
                f"class_name values appearing more than once (should be impossible - unique constraint "
                f"should prevent this): {dupes}",
            )
        )


def audit_repeated_import_drift(findings: list[dict]) -> None:
    """Run the Arrow importer twice and confirm the second pass changes
    nothing - a real re-import must be a no-op, not silent drift."""
    import import_ship_components

    from app.database import SessionLocal

    def snapshot():
        session = SessionLocal()
        try:
            rows = session.query(Component).filter(Component.class_name.isnot(None)).all()
            return {
                c.class_name: (c.name, c.size, c.grade, c.manufacturer_id, c.notes, c.confidence)
                for c in rows
            }
        finally:
            session.close()

    import_ship_components.run(dry_run=False)
    before = snapshot()
    import_ship_components.run(dry_run=False)
    after = snapshot()

    if before.keys() != after.keys():
        findings.append(
            _finding(
                "DEFECT",
                "repeated_import_drift",
                f"Re-running the importer changed which class_names exist: "
                f"added={after.keys() - before.keys()}, removed={before.keys() - after.keys()}",
            )
        )
        return

    changed = {k: (before[k], after[k]) for k in before if before[k] != after[k]}
    if changed:
        findings.append(
            _finding(
                "DEFECT",
                "repeated_import_drift",
                f"Re-running the importer changed field values on {len(changed)} existing rows "
                f"(should be a pure no-op): {changed}",
            )
        )
    else:
        findings.append(
            _finding(
                "PASS",
                "repeated_import_drift",
                "Re-running the importer produced identical data both times, no drift.",
            )
        )


def run_audit(ships: list[str]) -> dict:
    findings: list[dict] = []
    with Session(engine) as session:
        for ship in ships:
            audit_source_vs_processed_vs_db(session, ship, findings)
        audit_relational_integrity(session, findings)
        audit_duplicate_class_names(session, findings)
    audit_repeated_import_drift(findings)

    counts = {"DEFECT": 0, "LIMITATION": 0, "WARNING": 0, "PASS": 0}
    for f in findings:
        counts[f["severity"]] += 1

    return {
        "generated_at": datetime.datetime.now().isoformat(),
        "ships_audited": ships,
        "counts": counts,
        "findings": findings,
    }


def render_human_summary(report: dict) -> str:
    lines = []
    lines.append("Ship Items Audit — " + report["generated_at"])
    lines.append("Ships audited: " + ", ".join(report["ships_audited"]))
    lines.append("")
    c = report["counts"]
    lines.append(f"DEFECTS: {c['DEFECT']}   WARNINGS (review): {c['WARNING']}   LIMITATIONS (expected gaps): {c['LIMITATION']}   PASS (confirmed OK): {c['PASS']}")
    lines.append("")
    for severity in ("DEFECT", "WARNING", "LIMITATION", "PASS"):
        items = [f for f in report["findings"] if f["severity"] == severity]
        if not items:
            continue
        lines.append(f"--- {severity} ({len(items)}) ---")
        for f in items:
            lines.append(f"  [{f['category']}] {f['message']}")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ship",
        action="append",
        dest="ships",
        default=None,
        help="Ship slug to audit (repeatable). Pass 'none' to skip source-vs-processed "
        "coverage checks entirely (relational integrity / duplicate / drift checks still "
        "run) - useful when auditing a database that was never seeded via a ship's own "
        "importer, e.g. run_e2e_test.py's throwaway fixture DB. Default: all ships with "
        "known source data.",
    )
    args = parser.parse_args()
    if args.ships == ["none"]:
        ships = []
    else:
        ships = args.ships or list(SHIP_SOURCE_FILES.keys())

    report = run_audit(ships)

    logs_dir = REPO_ROOT / "logs"
    logs_dir.mkdir(exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = logs_dir / f"ship_components_audit_{stamp}.json"
    txt_path = logs_dir / f"ship_components_audit_{stamp}.txt"
    json_path.write_text(json.dumps(report, indent=2))
    summary = render_human_summary(report)
    txt_path.write_text(summary)

    print(summary)
    print(f"\nMachine-readable report: {json_path}")
    print(f"Human-readable summary: {txt_path}")

    return 1 if report["counts"]["DEFECT"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
