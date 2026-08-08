"""
Ship Items component importer (Phase 3 / Priority 8 - Component Database).

Populates the components / *_details tables (see
alembic/versions/219446ebce6a_*.py and app/models.py's Ship Items domain)
from a ship's raw port-tree data pull (data-layer/raw/<slug>/<slug>_api_raw.json).

Per docs/ARCHITECTURE_DECISIONS.md section 2 (Generic Data Pipeline, LOCKED
staged): this is a hand-curated, per-ship importer, not a generic
auto-extractor - the plan is 2-3 real importers first, then generalize once
real patterns are known. What IS locked in now, per that same section's
"minimal contract":
  - upsert on a natural key (class_name, matching the game's own internal
    item identifiers - the same idea as registry-builder's ship codes)
  - every row stamps verification_source / confidence, matching
    VerifiableMixin
  - logs to logs/ship_components_import.log, one line per run, matching
    the project's per-tool log convention (pkg/pipelinelog's Go pattern,
    mirrored here in Python since this importer is Python/SQLAlchemy like
    the rest of app/)

Data honesty rule for this importer: only fields with real evidence get
populated. Where the raw port data doesn't resolve an ambiguity (e.g. a
manufacturer prefix I can't confidently identify, or a size figure that's
contradicted by a different signal), the field is left NULL and the
ambiguity is written into the component's `notes` column - never guessed.
See ARROW_COMPONENTS below for the specific calls made and why.

Usage:
    python import_ship_components.py                 # imports the Arrow
    python import_ship_components.py --dry-run        # parse/validate only, no DB writes
"""

import argparse
import datetime
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

from sqlalchemy import select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.database import engine  # noqa: E402
from app.preservation import install_never_delete_guard  # noqa: E402
from app.models import (  # noqa: E402
    Component,
    ComponentType,
    GimbalMountDetail,
    Manufacturer,
    MissileDetail,
    MissileRackDetail,
    TurretDetail,
    WeaponDetail,
)

LOG_PATH = PROJECT_ROOT / "logs" / "ship_components_import.log"

SOURCE_NOTE = (
    "data-layer/raw/arrow/arrow_api_raw.json ports tree, cross-checked "
    "against docs/HARDPOINT_MOUNT_TYPES.md (2026-07-30 session)"
)

# ---------------------------------------------------------------------------
# ARROW_COMPONENTS: hand-curated from the Arrow's real port tree (see the
# 2026-07-30 session's port-tree dump). Each entry's class_name is verbatim
# from that source - the one field in every row that is never guessed.
#
# Manufacturer prefixes resolved with real confidence: BEHR = Behring,
# KLWE = Klaus & Werner, ANVL = Anvil Aerospace (all well-established SC
# manufacturer codes). GATS, FSKI, and TALN are NOT confidently resolved -
# left as manufacturer=None with a note, rather than guessed.
# ---------------------------------------------------------------------------
ARROW_COMPONENTS = [
    {
        "type_key": "turret",
        "name": "Arrow Turret (OEM)",
        "class_name": "ANVL_Arrow_Turret",
        "manufacturer": "Anvil Aerospace",
        "size": None,
        "grade": None,
        "confidence": "medium",
        "notes": (
            "OEM top turret housing, ships default-equipped per "
            "docs/HARDPOINT_MOUNT_TYPES.md's Arrow case study. Own size "
            "rating not directly evidenced - left null rather than assumed."
        ),
        "details": {"kind": "turret", "weapon_slots": 2, "slot_weapon_size": 1, "manned": False},
    },
    {
        "type_key": "weapon",
        "name": "Ballistic Gatling (S1)",
        "class_name": "GATS_BallisticGatling_S1",
        "manufacturer": None,
        "size": 1,
        "grade": None,
        "confidence": "medium",
        "notes": (
            "Size 1 is unambiguous from the class name. Manufacturer prefix "
            "'GATS' not confidently identified this session (may denote "
            "weapon archetype 'Gatling' rather than a manufacturer code) - "
            "left null rather than guessed. Damage/RPM/DPS stats not sourced "
            "from authoritative data this session - not populated."
        ),
        "details": {"kind": "weapon", "damage_type": "ballistic"},
    },
    {
        "type_key": "gimbal_mount",
        "name": "Gimbal Mount (S3)",
        "class_name": "Mount_Gimbal_S3",
        "manufacturer": None,
        "size": 3,
        "grade": None,
        "confidence": "medium",
        "notes": (
            "Generic mount class name (no manufacturer brand embedded, "
            "unlike the wing-gun item referenced in the earlier viewer "
            "prototype as 'VariPuck S3 Gimbal Mount' - that name came from "
            "a different, wiki-sourced pass and has NOT been confirmed to "
            "be the same item as this class name; flagged, not merged)."
        ),
        "details": {"kind": "gimbal_mount", "accepts_weapon_size": 2},
    },
    {
        "type_key": "weapon",
        "name": "Laser Repeater (gimbal-rated S3)",
        "class_name": "KLWE_LaserRepeater_S3",
        "manufacturer": "Klaus & Werner",
        "size": None,
        "grade": None,
        "confidence": "low",
        "notes": (
            "Manufacturer (Klaus & Werner, KLWE) is confident. Actual "
            "mounted/effective size is AMBIGUOUS: the class name's '_S3' "
            "suffix may denote the gimbal it's rated for rather than the "
            "weapon's own size, and it sits under a 'hardpoint_class_2' "
            "wrapper (suggesting Size 2) inside the Mount_Gimbal_S3 gimbal "
            "above. Left size null rather than picking one interpretation. "
            "Damage/RPM/DPS stats not sourced this session."
        ),
        "details": {"kind": "weapon", "damage_type": "energy"},
    },
    {
        "type_key": "missile_rack",
        "name": "Missile Rack, Single S2",
        "class_name": "MRCK_S02_BEHR_Single_S02",
        "manufacturer": "Behring",
        "size": 2,
        "grade": None,
        "confidence": "medium",
        "notes": "Wingtip mount, fixed Size 2, single missile capacity.",
        "details": {"kind": "missile_rack", "native_missile_size": 2, "missile_capacity": 1},
    },
    {
        "type_key": "missile_rack",
        "name": "Missile Rack, Dual S2 (on S3 mount)",
        "class_name": "MRCK_S03_BEHR_Dual_S02",
        "manufacturer": "Behring",
        "size": 3,
        "grade": None,
        "confidence": "medium",
        "notes": (
            "Wing-root mount: a genuine Size 3 hardpoint currently fitted "
            "with this dual-S2 rack (2x S2 missiles) as an alternative to a "
            "single S3 missile mounted directly - real evidence of the "
            "rack-swap mechanic, not assumed."
        ),
        "details": {"kind": "missile_rack", "native_missile_size": 2, "missile_capacity": 2},
    },
    {
        "type_key": "missile",
        "name": "Ignite-family Missile (S2, IR)",
        "class_name": "MISL_S02_IR_FSKI_Ignite",
        "manufacturer": None,
        "size": 2,
        "grade": None,
        "confidence": "low",
        "notes": (
            "Size and IR guidance are unambiguous from the class name. "
            "Manufacturer prefix 'FSKI' not confidently identified this "
            "session - left null rather than guessed. Damage/tracking/"
            "lock-time stats not sourced this session."
        ),
        "details": {"kind": "missile", "guidance_type": "ir"},
    },
    {
        "type_key": "missile",
        "name": "Dominator-family Missile (S2, EM)",
        "class_name": "MISL_S02_EM_TALN_Dominator",
        "manufacturer": None,
        "size": 2,
        "grade": None,
        "confidence": "low",
        "notes": (
            "Size and EM guidance are unambiguous from the class name. "
            "Manufacturer prefix 'TALN' not confidently identified this "
            "session - left null rather than guessed. Damage/tracking/"
            "lock-time stats not sourced this session."
        ),
        "details": {"kind": "missile", "guidance_type": "em"},
    },
]


def log_line(message: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {message}\n")


def get_or_create_manufacturer(session: Session, name: str | None) -> "Manufacturer | None":
    if not name:
        return None
    existing = session.scalar(select(Manufacturer).where(Manufacturer.name == name))
    if existing:
        return existing
    mfr = Manufacturer(name=name, confidence="medium", verification_source=SOURCE_NOTE)
    session.add(mfr)
    session.flush()
    log_line(f"Created manufacturer '{name}' (was not already in the DB)")
    return mfr


def get_component_type(session: Session, key: str) -> ComponentType:
    ct = session.scalar(select(ComponentType).where(ComponentType.key == key))
    if not ct:
        raise RuntimeError(
            f"component_type '{key}' not found - has the Ship Items migration "
            "(219446ebce6a) been applied and its component_types seed rows loaded?"
        )
    return ct


def upsert_component(session: Session, spec: dict) -> tuple[Component, bool]:
    """Upsert on class_name (the natural key). Returns (component, created)."""
    existing = session.scalar(
        select(Component).where(Component.class_name == spec["class_name"])
    )
    manufacturer = get_or_create_manufacturer(session, spec["manufacturer"])
    component_type = get_component_type(session, spec["type_key"])

    if existing:
        existing.name = spec["name"]
        existing.component_type_id = component_type.id
        existing.manufacturer_id = manufacturer.id if manufacturer else None
        existing.size = spec["size"]
        existing.grade = spec["grade"]
        existing.notes = spec["notes"]
        existing.verification_source = SOURCE_NOTE
        existing.confidence = spec["confidence"]
        return existing, False

    component = Component(
        component_type_id=component_type.id,
        manufacturer_id=manufacturer.id if manufacturer else None,
        name=spec["name"],
        class_name=spec["class_name"],
        size=spec["size"],
        grade=spec["grade"],
        notes=spec["notes"],
        verification_source=SOURCE_NOTE,
        confidence=spec["confidence"],
    )
    session.add(component)
    session.flush()
    return component, True


def upsert_detail(session: Session, component: Component, details: dict) -> None:
    kind = details["kind"]
    if kind == "turret":
        row = session.get(TurretDetail, component.id) or TurretDetail(component_id=component.id)
        row.weapon_slots = details.get("weapon_slots")
        row.slot_weapon_size = details.get("slot_weapon_size")
        row.manned = details.get("manned")
        session.merge(row)
    elif kind == "weapon":
        row = session.get(WeaponDetail, component.id) or WeaponDetail(component_id=component.id)
        row.damage_type = details.get("damage_type")
        session.merge(row)
    elif kind == "gimbal_mount":
        row = session.get(GimbalMountDetail, component.id) or GimbalMountDetail(component_id=component.id)
        row.accepts_weapon_size = details.get("accepts_weapon_size")
        session.merge(row)
    elif kind == "missile_rack":
        row = session.get(MissileRackDetail, component.id) or MissileRackDetail(component_id=component.id)
        row.native_missile_size = details.get("native_missile_size")
        row.missile_capacity = details.get("missile_capacity")
        session.merge(row)
    elif kind == "missile":
        row = session.get(MissileDetail, component.id) or MissileDetail(component_id=component.id)
        row.guidance_type = details.get("guidance_type")
        session.merge(row)
    else:
        raise ValueError(f"unknown detail kind: {kind}")


def run(dry_run: bool = False) -> int:
    created_count = 0
    updated_count = 0

    # Preservation: importers create and update, never delete. Installed here
    # rather than trusted to every future edit of this file - an entity absent
    # from a patch is MARKED absent, not dropped. Proven by
    # checks/_verify_never_delete_guard.py, which removes the guard and confirms
    # the row then disappears.
    install_never_delete_guard(engine)

    with Session(engine) as session:
        for spec in ARROW_COMPONENTS:
            component, created = upsert_component(session, spec)
            upsert_detail(session, component, spec["details"])
            if created:
                created_count += 1
                log_line(f"CREATE {spec['type_key']}: {spec['name']} ({spec['class_name']})")
            else:
                updated_count += 1
                log_line(f"UPDATE {spec['type_key']}: {spec['name']} ({spec['class_name']})")

        if dry_run:
            session.rollback()
            log_line(
                f"DRY RUN complete: would create {created_count}, update {updated_count} "
                f"(no changes committed)"
            )
        else:
            session.commit()
            log_line(
                f"Import complete: {created_count} created, {updated_count} updated, "
                f"ship=arrow, source={SOURCE_NOTE}"
            )

    print(f"{'[DRY RUN] ' if dry_run else ''}Created {created_count}, updated {updated_count} components.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Parse and validate only, no DB writes")
    args = parser.parse_args()
    sys.exit(run(dry_run=args.dry_run))
