"""
UEX locations + terminals importer (B1 of the shop/price layer order).

Concrete and hand-written, per §B1 and the standing "three real importers
before any abstraction" rule. Nothing here is generic. B4 extracts the shared
pipeline from this and its two siblings AFTER all three exist, because the
abstraction guessed in advance is always the wrong one.

WHY LOCATIONS ARE IN THE TERMINALS IMPORTER
-------------------------------------------
A terminal without its location hierarchy is a row pointing at nothing. The
six location endpoints are 675 rows in total, they exist only to give
terminals a place, and splitting them into a seventh script would mean two
things that must run in a fixed order and no reason on disk saying so. They
run here, first, in one pass.

PARENTS ARE HAND-DECLARED, NOT INFERRED
---------------------------------------
PARENT_CANDIDATES below is written out per kind rather than derived from a
specificity ranking, because containment is not a single ladder: an outpost
sits on a moon or a planet but never inside a city, while a space station
sometimes does sit inside one. Measured in this snapshot:

    planet          324 rows, all with a star system
    moon             73 rows, but only 18 name a planet - 55 do not
    city              5 rows, 4 name a planet
    space_station    60 rows, 46 name a planet, 5 name a CITY, 1 names a moon
    outpost         117 rows, all name a planet, 51 also name a moon

The 55 planet-less moons are why app/locations.py skips absent levels rather
than rendering them: those rows parent straight to their star system, and a
resolver that printed the gap would put "None" on a live page.

Referential integrity was measured before this was written: across all ten
parent references in these six files, ZERO dangle. Same for all six location
references on all 823 terminals. That is not assumed here - the importer
counts anything that fails to resolve and reports it, because "it was clean
in August" is not a guarantee about September.

Usage:
    venv/Scripts/python.exe import_uex_terminals.py
    venv/Scripts/python.exe import_uex_terminals.py --dry-run
"""

import argparse
import datetime
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

from sqlalchemy import select  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.database import engine  # noqa: E402
from app.locations import (  # noqa: E402
    most_specific_reference,
    resolve_path_from_chain,
    unresolvable_references,
)
from app.models import Location, Terminal  # noqa: E402

SNAPSHOT_ROOT = PROJECT_ROOT / "data-layer" / "external-sources" / "uexcorp" / "snapshots"
DEFAULT_SNAPSHOT = "20260801T235530Z"
LOG_PATH = PROJECT_ROOT / "logs" / "shop_layer_import.log"

# kind -> source file. Order matters: parents must be inserted before children.
LOCATION_FILES = [
    ("star_system", "star_systems.json"),
    ("planet", "planets.json"),
    ("moon", "moons.json"),
    ("city", "cities.json"),
    ("space_station", "space_stations.json"),
    ("outpost", "outposts.json"),
]

# Most specific candidate first. See the module docstring for the measurements
# behind each list.
PARENT_CANDIDATES = {
    "star_system": [],
    "planet": [("id_star_system", "star_system")],
    "moon": [("id_planet", "planet"), ("id_star_system", "star_system")],
    "city": [("id_moon", "moon"), ("id_planet", "planet"),
             ("id_star_system", "star_system")],
    "space_station": [("id_city", "city"), ("id_moon", "moon"),
                      ("id_planet", "planet"), ("id_star_system", "star_system")],
    "outpost": [("id_moon", "moon"), ("id_planet", "planet"),
                ("id_star_system", "star_system")],
}

# Promoted to real columns on Location; everything else goes to `detail`.
LOCATION_PROMOTED = {"id", "name", "code", "nickname", "date_modified"}

# Promoted to real columns on Terminal.
TERMINAL_PROMOTED = {
    "id", "name", "fullname", "nickname", "displayname", "code", "type",
    "company_name", "is_available", "is_available_live", "date_modified",
}


def log(message: str) -> None:
    stamp = datetime.datetime.now().isoformat(timespec="seconds")
    line = f"[{stamp}] terminals: {message}"
    print(line)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def load_envelope(path: Path) -> list:
    """The rows in a UEX file, or a loud failure.

    A file that is missing, unparseable, or not a UEX envelope stops the run.
    §B5's control - "a malformed file fails loudly, and does not silently
    import zero rows and report success" - applies to every importer here, not
    only the one it is written under.
    """
    if not path.exists():
        raise SystemExit(f"MALFORMED SOURCE: {path} does not exist")
    try:
        with open(path, encoding="utf-8") as fh:
            payload = json.load(fh)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"MALFORMED SOURCE: {path} is not valid JSON - {exc}")

    if not isinstance(payload, dict) or "data" not in payload:
        raise SystemExit(
            f"MALFORMED SOURCE: {path} has no 'data' key - this is not a UEX "
            f"envelope and its shape will not be guessed at"
        )
    rows = payload["data"]
    if rows is None:
        # A real and legitimate case - HTTP 200, envelope ok, no rows. It is
        # NOT malformed, and it is NOT silently treated as success either: the
        # caller decides whether an empty endpoint is acceptable.
        return []
    if not isinstance(rows, list):
        raise SystemExit(
            f"MALFORMED SOURCE: {path} has 'data' as "
            f"{type(rows).__name__}, not a list"
        )
    return rows


def to_dt(value):
    try:
        seconds = int(value)
    except (TypeError, ValueError):
        return None
    if seconds <= 0:
        return None
    return datetime.datetime.fromtimestamp(
        seconds, tz=datetime.timezone.utc
    ).replace(tzinfo=None)


def to_bool(value):
    if value is None:
        return None
    try:
        return bool(int(value))
    except (TypeError, ValueError):
        return None


def clean(value):
    """Empty string -> None. UEX uses "" where it means 'not set', and storing
    it as "" makes every downstream `IS NOT NULL` check quietly wrong."""
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


def import_locations(session, snapshot, source_rows, dry_run):
    """Insert/update the six location endpoints, parents before children.

    Returns (index, stats) where index maps (kind, uex_id) -> Location, so the
    terminal pass can look up what a terminal points at without re-querying.
    """
    # (kind, uex_id) -> Location, seeded from whatever is already stored so a
    # re-run updates rather than duplicating.
    index = {}
    for row in session.execute(select(Location)).scalars():
        index[(row.kind, row.uex_id)] = row

    stats = {"inserted": 0, "updated": 0, "unchanged": 0, "unresolved_parents": []}

    for kind, filename in LOCATION_FILES:
        rows = source_rows[kind]
        for row in rows:
            uex_id = row.get("id")
            if uex_id is None:
                stats["unresolved_parents"].append(f"{kind}: row with no id")
                continue

            # Find the parent: the first candidate this row actually names AND
            # that we hold. A named-but-missing parent is recorded, never
            # silently dropped to NULL as though the row were top-level.
            parent = None
            for field, parent_kind in PARENT_CANDIDATES[kind]:
                ref = row.get(field)
                if not ref:
                    continue
                parent = index.get((parent_kind, ref))
                if parent is not None:
                    break
                stats["unresolved_parents"].append(
                    f"{kind} {uex_id} ({row.get('name')!r}) names "
                    f"{field}={ref} but no {parent_kind} with that id is held"
                )

            star_system = None
            if kind == "star_system":
                star_system = None
            elif row.get("id_star_system"):
                star_system = index.get(("star_system", row["id_star_system"]))

            # The readable path, built as a recurrence rather than a parent
            # walk. LOCATION_FILES is ordered parents-before-children, so by
            # the time this row is reached its parent already carries a
            # finished resolved_path - "ArcCorp, Stanton" - and this row's is
            # just its own name in front of it.
            #
            # Deliberately NOT resolve_path(): that walks `.parent`, and these
            # objects are freshly added rather than loaded, so the
            # relationship may not be traversable yet. Same skipping rules
            # either way, because both go through resolve_path_from_chain().
            parent_path = parent.resolved_path if parent is not None else None
            chain = [clean(row.get("name"))]
            if parent_path:
                chain.extend(parent_path.split(", "))
            resolved = resolve_path_from_chain(chain)

            detail = {k: v for k, v in row.items() if k not in LOCATION_PROMOTED}
            values = {
                "name": clean(row.get("name")) or f"{kind} {uex_id}",
                "code": clean(row.get("code")),
                "nickname": clean(row.get("nickname")),
                "parent_id": parent.id if parent is not None else None,
                "star_system_id": star_system.id if star_system is not None else None,
                "resolved_path": resolved,
                "detail": detail or None,
                "verification_source": f"uexcorp snapshot {snapshot}",
                "confidence": "medium",
            }

            current = index.get((kind, uex_id))
            if current is None:
                current = Location(uex_id=uex_id, kind=kind, **values)
                index[(kind, uex_id)] = current
                stats["inserted"] += 1
                if not dry_run:
                    session.add(current)
                    # Flush so children in later files can point at this row's
                    # real primary key rather than a pending object.
                    session.flush()
                else:
                    # In a dry run there is no id to hand to children, so give
                    # the object its identity fields only. Nothing is written.
                    current.id = None
            else:
                if any(getattr(current, k) != v for k, v in values.items()):
                    stats["updated"] += 1
                    if not dry_run:
                        for k, v in values.items():
                            setattr(current, k, v)
                else:
                    stats["unchanged"] += 1

    return index, stats


def import_terminals(session, snapshot, rows, location_index, dry_run):
    stats = {"inserted": 0, "updated": 0, "unchanged": 0,
             "no_location": [], "unresolved": []}

    existing = {
        t.uex_id: t for t in session.execute(select(Terminal)).scalars()
    }

    for row in rows:
        uex_id = row.get("id")
        if uex_id is None:
            stats["unresolved"].append("terminal row with no id")
            continue

        reference = most_specific_reference(row)
        location = None
        if reference is None:
            stats["no_location"].append(
                f"terminal {uex_id} ({row.get('name')!r}) names no resolvable "
                f"location level"
            )
        else:
            location = location_index.get(reference)
            if location is None:
                stats["no_location"].append(
                    f"terminal {uex_id} ({row.get('name')!r}) points at "
                    f"{reference[0]} {reference[1]}, which is not held"
                )

        star_system = None
        if row.get("id_star_system"):
            star_system = location_index.get(("star_system", row["id_star_system"]))

        detail = {k: v for k, v in row.items() if k not in TERMINAL_PROMOTED}
        # Rule 11: orbit and poi ids cannot be named from this snapshot. Keep
        # them as ids, labelled, rather than dropping the fact or inventing a
        # name for it.
        unresolvable = unresolvable_references(row)
        if unresolvable:
            detail["_unresolvable_location_ids"] = unresolvable

        values = {
            "name": clean(row.get("name")) or f"terminal {uex_id}",
            "fullname": clean(row.get("fullname")),
            "nickname": clean(row.get("nickname")),
            "displayname": clean(row.get("displayname")),
            "code": clean(row.get("code")),
            "type": clean(row.get("type")),
            "location_id": location.id if location is not None else None,
            "star_system_id": star_system.id if star_system is not None else None,
            "resolved_path": location.resolved_path if location is not None else None,
            "company_name": clean(row.get("company_name")),
            "is_available": to_bool(row.get("is_available")),
            "is_available_live": to_bool(row.get("is_available_live")),
            "source_date_modified": to_dt(row.get("date_modified")),
            "detail": detail or None,
            "verification_source": f"uexcorp snapshot {snapshot}",
            "confidence": "medium",
        }

        current = existing.get(uex_id)
        if current is None:
            stats["inserted"] += 1
            if not dry_run:
                session.add(Terminal(uex_id=uex_id, **values))
        else:
            if any(getattr(current, k) != v for k, v in values.items()):
                stats["updated"] += 1
                if not dry_run:
                    for k, v in values.items():
                        setattr(current, k, v)
            else:
                stats["unchanged"] += 1

    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", default=DEFAULT_SNAPSHOT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    base = SNAPSHOT_ROOT / args.snapshot
    source_rows = {kind: load_envelope(base / name)
                   for kind, name in LOCATION_FILES}
    terminal_rows = load_envelope(base / "terminals.json")

    expected_locations = sum(len(v) for v in source_rows.values())
    log(f"snapshot {args.snapshot}: {expected_locations} location rows, "
        f"{len(terminal_rows)} terminals"
        f"{' (DRY RUN - nothing will be written)' if args.dry_run else ''}")

    if not terminal_rows:
        log("FAILED: terminals.json carried no rows - refusing to report success")
        return 1

    with Session(engine) as session:
        index, loc_stats = import_locations(
            session, args.snapshot, source_rows, args.dry_run
        )
        term_stats = import_terminals(
            session, args.snapshot, terminal_rows, index, args.dry_run
        )
        if args.dry_run:
            session.rollback()
        else:
            session.commit()

    for kind, filename in LOCATION_FILES:
        log(f"  {kind}: {len(source_rows[kind])} source rows")
    log(f"locations: inserted {loc_stats['inserted']}, "
        f"updated {loc_stats['updated']}, unchanged {loc_stats['unchanged']}")
    if loc_stats["unresolved_parents"]:
        log(f"locations: {len(loc_stats['unresolved_parents'])} unresolved "
            f"parent reference(s) - these are REPORTED, not silently nulled:")
        for line in loc_stats["unresolved_parents"][:20]:
            log(f"    {line}")

    log(f"terminals: inserted {term_stats['inserted']}, "
        f"updated {term_stats['updated']}, unchanged {term_stats['unchanged']}")
    if term_stats["no_location"]:
        log(f"terminals: {len(term_stats['no_location'])} could not be placed:")
        for line in term_stats["no_location"][:20]:
            log(f"    {line}")

    with Session(engine) as session:
        held_locations = session.query(Location).count()
        held_terminals = session.query(Terminal).count()
        placed = session.query(Terminal).filter(
            Terminal.location_id.isnot(None)
        ).count()

    log(f"locations table holds {held_locations} rows "
        f"(source had {expected_locations})")
    log(f"terminals table holds {held_terminals} rows "
        f"(source had {len(terminal_rows)}); {placed} resolve to a location")

    if args.dry_run:
        return 0

    # Fail closed. A short import that reports success is the exact defect
    # rule 12 names, and this is where it would happen.
    failures = []
    if held_locations < expected_locations:
        failures.append(
            f"locations: source had {expected_locations}, table holds "
            f"{held_locations}"
        )
    if held_terminals < len(terminal_rows):
        failures.append(
            f"terminals: source had {len(terminal_rows)}, table holds "
            f"{held_terminals}"
        )
    for line in failures:
        log(f"FAILED: {line}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
