"""
Checkers for the Ships domain that need a real Postgres connection (via
SQLAlchemy, matching the app's own DB layer in app/database.py). Distinct
in scope from audit_ship_components.py, which covers the Ship Items
(weapons/missiles/turrets) domain only - this module covers Ship,
Manufacturer, Dealer, ShipDealerListing.

Environment note (2026-07-30): this session has no path to the real
Postgres database from any available tool (see LATEST_HANDOFF.md - a
direct TCP test from both the cloud sandbox and the device bridge's
isolated Linux VM both got Connection refused). These checkers were
built and tested against a disposable scratch Postgres in the cloud
sandbox, the same way every other DB-dependent piece of tonight's work
was validated - they have NOT been run against the real database.

Each function takes a SQLAlchemy `Session` (see app/database.py's
SessionLocal) and returns list[Finding]. registry_sync_check additionally
takes `repo_root` since it needs to read data-layer/ship_registry.json
off disk - it's the only checker in this module with a filesystem
dependency, so it takes repo_root as an explicit second argument rather
than folding filesystem access into every checker's signature.
"""

import json
import re
import subprocess
from pathlib import Path

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import CONFIDENCE_LEVELS, Dealer, Manufacturer, Ship, ShipDealerListing
from checks.framework import Finding

REGISTRY_PATH = Path("data-layer") / "ship_registry.json"


def referential_integrity_check(session: Session, repo_root: Path = None) -> list[Finding]:
    """Confirm every Ship/ShipDealerListing FK actually resolves, and that
    every row satisfies the same confidence/status vocabulary the DB
    CheckConstraints already enforce - a second, independent check in
    case any row was ever inserted by something that bypasses the ORM
    (e.g. a raw INSERT in a one-off migration script)."""
    findings = []

    from app.models import Patch

    manufacturer_ids = {m.id for m in session.query(Manufacturer.id).all()}
    patch_ids = {p.id for p in session.query(Patch.id).all()}
    dealer_ids = {d.id for d in session.query(Dealer.id).all()}

    ships = session.query(Ship).all()
    orphaned_manufacturer = [s for s in ships if s.manufacturer_id not in manufacturer_ids]
    orphaned_patch = [s for s in ships if s.last_verified_patch is not None and s.last_verified_patch not in patch_ids]
    bad_confidence = [s for s in ships if s.confidence not in CONFIDENCE_LEVELS]

    if orphaned_manufacturer:
        findings.append(Finding("referential_integrity", "ships.manufacturer_id", "DEFECT",
                                 f"{len(orphaned_manufacturer)} ship(s) reference a manufacturer_id with no matching row: "
                                 f"{[s.id for s in orphaned_manufacturer]}"))
    else:
        findings.append(Finding("referential_integrity", "ships.manufacturer_id", "PASS",
                                 f"all {len(ships)} ships have a valid manufacturer_id"))

    if orphaned_patch:
        findings.append(Finding("referential_integrity", "ships.last_verified_patch", "DEFECT",
                                 f"{len(orphaned_patch)} ship(s) reference a last_verified_patch with no matching row: "
                                 f"{[s.id for s in orphaned_patch]}"))
    else:
        findings.append(Finding("referential_integrity", "ships.last_verified_patch", "PASS",
                                 "all non-null last_verified_patch values resolve"))

    if bad_confidence:
        findings.append(Finding("referential_integrity", "ships.confidence", "DEFECT",
                                 f"{len(bad_confidence)} ship(s) have a confidence value outside the expected vocabulary: "
                                 f"{[(s.id, s.confidence) for s in bad_confidence]}"))
    else:
        findings.append(Finding("referential_integrity", "ships.confidence", "PASS", "all confidence values valid"))

    listings = session.query(ShipDealerListing).all()
    ship_ids = {s.id for s in ships}
    orphaned_listing_ship = [l for l in listings if l.ship_id not in ship_ids]
    orphaned_listing_dealer = [l for l in listings if l.dealer_id not in dealer_ids]

    if orphaned_listing_ship or orphaned_listing_dealer:
        findings.append(Finding("referential_integrity", "ship_dealer_listings", "DEFECT",
                                 f"{len(orphaned_listing_ship)} listing(s) with a bad ship_id, "
                                 f"{len(orphaned_listing_dealer)} with a bad dealer_id"))
    else:
        findings.append(Finding("referential_integrity", "ship_dealer_listings", "PASS",
                                 f"all {len(listings)} listings have valid ship_id and dealer_id"))

    return findings


def duplicate_identifier_check(session: Session, repo_root: Path = None) -> list[Finding]:
    """Flag (name, manufacturer_id) pairs that appear more than once - the
    natural key a duplicate-import bug would violate. Two ships can
    legitimately share a bare name across manufacturers (rare, but not
    impossible for reused fan-fiction-style names) - it's the same name
    under the same manufacturer that indicates a real duplicate row."""
    dupes = (
        session.query(Ship.name, Ship.manufacturer_id, func.count(Ship.id))
        .group_by(Ship.name, Ship.manufacturer_id)
        .having(func.count(Ship.id) > 1)
        .all()
    )
    if dupes:
        return [
            Finding("duplicate_identifier", None, "DEFECT",
                    f"{len(dupes)} (name, manufacturer_id) pair(s) have more than one row: "
                    f"{[(n, m, c) for n, m, c in dupes]}")
        ]
    return [Finding("duplicate_identifier", None, "PASS", "no duplicate (name, manufacturer_id) pairs in ships")]


def registry_sync_check(session: Session, repo_root: Path) -> list[Finding]:
    """Compare the DB's canonical ship names against
    data-layer/ship_registry.json's ship_name field. A mismatch either
    way is a WARNING, not a DEFECT - the registry and DB can legitimately
    be mid-sync during staged import work (see docs/ARCHITECTURE_DECISIONS.md
    on the staged-pipeline decision already used by audit_ship_components.py
    for the same reasoning on Ship Items)."""
    registry_path = repo_root / REGISTRY_PATH
    if not registry_path.exists():
        return [Finding("registry_sync", None, "LIMITATION", f"{registry_path} not found - nothing to compare")]

    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except Exception as e:
        return [Finding("registry_sync", None, "DEFECT", f"{registry_path} is not valid JSON: {e}")]

    registry_names = {entry.get("ship_name") for entry in registry if isinstance(entry, dict) and entry.get("ship_name")}
    db_names = {s.name for s in session.query(Ship.name).all()}

    in_db_not_registry = db_names - registry_names
    in_registry_not_db = registry_names - db_names

    findings = []
    if in_db_not_registry:
        findings.append(Finding("registry_sync", "db-not-in-registry", "WARNING",
                                 f"{len(in_db_not_registry)} DB ship name(s) have no matching ship_registry.json entry: "
                                 f"{sorted(in_db_not_registry)[:20]}"))
    if in_registry_not_db:
        findings.append(Finding("registry_sync", "registry-not-in-db", "WARNING",
                                 f"{len(in_registry_not_db)} ship_registry.json entries have no matching DB row "
                                 f"(expected during staged import - registry covers more ships than are in the DB yet): "
                                 f"{sorted(in_registry_not_db)[:20]}"))
    if not findings:
        findings.append(Finding("registry_sync", None, "PASS", f"all {len(db_names)} DB ship names match a registry entry"))
    return findings


# An alembic operation tuple opens with ('op_name', at a position that is NOT
# preceded by an identifier character. That negative lookbehind is what keeps
# Column('check_name', - which has the identical shape - from being mistaken
# for an operation.
_ALEMBIC_OP = re.compile(r"(?<![A-Za-z_])\('([a-z_]+)',")
_ALEMBIC_TARGET = re.compile(r"(?:Table|Index|Column)\('([^']+)'")


def summarise_alembic_ops(raw: str) -> list[str]:
    """Reduce `alembic check`'s output to a sorted list of "op:target".

    WHY THIS EXISTS - and it is not cosmetic.

    The raw output cannot be used as a finding's `details`, because two things
    in it change between runs while the drift itself does not:

      1. **Memory addresses.** Every server_default renders as
         `<sqlalchemy.sql.elements.TextClause object at 0x0000017059E56C10>`.
         That address is different on every single run. It also survives
         lifecycle.normalise_condition() untouched - the hex normaliser is
         anchored with \\b, and there is no word boundary between the `x` and
         the digits of `0x...`, so it never matches.
      2. **Operation order**, which autogenerate does not guarantee.

    Either one alone means the same drift hashes to a new finding_key every
    run. Put that on Part D's schedule and the findings table grows one fresh
    ghost per run, forever - the exact failure the lifecycle exists to stop,
    delivered on a timer.

    No normaliser can fix this from the outside, because a memory address is
    indistinguishable from data at that level. It has to be fixed here, by
    emitting the condition rather than a dump of it.

    Sorted and de-duplicated, so the same drift produces byte-identical text
    on every run.
    """
    marker = "New upgrade operations detected:"
    idx = raw.find(marker)
    payload = raw[idx + len(marker):] if idx != -1 else raw

    ops = []
    for m in _ALEMBIC_OP.finditer(payload):
        tail = payload[m.end(): m.end() + 400]
        target = _ALEMBIC_TARGET.search(tail)
        ops.append(f"{m.group(1)}:{target.group(1)}" if target else m.group(1))
    return sorted(set(ops))


def schema_drift_check(session: Session, repo_root: Path) -> list[Finding]:
    """Run `alembic check` (Alembic >=1.9) to confirm the live DB schema
    matches what the current model metadata expects - i.e. no model
    change was made without a corresponding migration. Requires alembic
    on PATH and a configured alembic.ini in repo_root; returns LIMITATION
    if either isn't available rather than a false DEFECT."""
    alembic_ini = repo_root / "alembic.ini"
    if not alembic_ini.exists():
        return [Finding("schema_drift", None, "LIMITATION", f"{alembic_ini} not found")]

    try:
        result = subprocess.run(
            ["alembic", "check"], cwd=repo_root, capture_output=True, text=True, timeout=60
        )
    except FileNotFoundError:
        return [Finding("schema_drift", None, "LIMITATION", "alembic not on PATH in this environment")]
    except Exception as e:
        return [Finding("schema_drift", None, "WARNING", f"could not run alembic check: {e}")]

    if result.returncode == 0:
        return [Finding("schema_drift", None, "PASS", "alembic check: no schema drift detected")]

    ops = summarise_alembic_ops(result.stdout + result.stderr)
    if not ops:
        # Non-zero exit we could not parse. Say exactly that rather than
        # inventing a drift description - and keep it stable by not echoing
        # output we have not understood.
        return [Finding("schema_drift", None, "WARNING",
                         f"alembic check exited {result.returncode} but no operations could be "
                         f"parsed from its output; the drift, if any, is unclassified")]

    return [Finding("schema_drift", None, "DEFECT",
                     f"alembic check reports {len(ops)} drift operation(s): " + ", ".join(ops))]


CHECKERS = [
    ("referential_integrity", referential_integrity_check),
    ("duplicate_identifier", duplicate_identifier_check),
    ("registry_sync", registry_sync_check),
    ("schema_drift", schema_drift_check),
]
