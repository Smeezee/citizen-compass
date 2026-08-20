"""
The never-delete guard: importers may create and update rows, never remove them.

WHY THIS EXISTS
---------------
Citizen Compass is a preservation project. An entity that disappears from a
patch has not stopped having existed - it has been retired, and the row is the
only record we will ever hold of it.

The natural behaviour of a patch importer is to write what the patch contains.
When the Aurora Mk I disappears from ships.json, a normal import simply does not
write it, and a loader that REPLACES rather than merges drops the row.
**Nothing errors. The run reports success.**

That is the silent-success shape this project has now logged six times - the
robocopy [\/] bug, the $null->0 exit code, `wrangler pages deploy` publishing
to a different URL, the vacuous privacy check, the unreachable schema-version
branch, and this. It is the default outcome unless something prevents it.

Port Olisar is the proof that this is not hypothetical. The location gazetteer
resolves 2,066 entities and Port Olisar is not one of them. It survives only as
a decoration item and a T-shirt description. The Aurora Mk I survives only
because a snapshot happened to catch it before anyone knew there was a reason
to.

ENFORCED BY CONSTRUCTION, NOT BY MEMORY
---------------------------------------
A rule that depends on every future importer author remembering it is a
convention. This raises instead.

Two layers, because there are two ways to delete a row and blocking one is
worth nothing:

  * ORM      - session.delete(obj), and cascade deletes triggered by a flush
  * Core/SQL - DELETE and TRUNCATE, including raw text passed to execute()

A wholesale "replace" is DELETE-then-INSERT, so blocking DELETE catches it too.

PROTECT BY DEFAULT, NOT BY LIST (H7, 2026-08-20)
------------------------------------------------
Every table is protected unless it is explicitly named as ephemeral. See the
comment above EPHEMERAL_TABLES for what that replaced and why. The short
version: an allowlist was silently off for nine tables built in a single week,
and nothing reported it.

WHAT THIS DOES NOT DO
---------------------
It does not mark the absent row retired - that needs the lifecycle columns in
WORKORDER_preservation-model-and-never-delete-rule.md section 4
(first_seen_patch, last_seen_patch, status, successor_id, removal_note,
evidence_tier), which are a schema migration and are not installed here.

So today this guard makes the loss impossible; it does not yet make the absence
visible. That is the correct order - a row that is still there can be marked
later, a row that is gone cannot be recovered.
"""

import re

from sqlalchemy import event
from sqlalchemy.orm import Session as _OrmSession
from sqlalchemy.sql import Delete

__all__ = [
    "PreservationViolation",
    "PRESERVED_TABLES",
    "EPHEMERAL_TABLES",
    "EPHEMERAL_PREFIXES",
    "is_ephemeral",
    "is_protected",
    "classification_problems",
    "install_never_delete_guard",
    "remove_never_delete_guard",
    "preservation_guard_installed",
]


class PreservationViolation(RuntimeError):
    """Raised when something tries to remove a row from a protected table."""


# ---------------------------------------------------------------------------
# H7, 2026-08-20. THIS USED TO BE AN ALLOWLIST, AND IT WAS SILENTLY OFF FOR
# EVERYTHING BUILT IN THE WEEK BEFORE THAT DATE.
#
# Sixteen tables were named here and protected. Every table added by the A-G
# runs - shop_items, item_prices, terminals, locations, item_categories,
# snapshots, shop_item_commodity_xref, ship_hardpoints,
# ship_hardpoint_coverage - was not. 26,657 prices and 2,195 slots sat
# unguarded and nothing said so. That is how a control DELETE reached a real
# table during G5.
#
# The failure is not that somebody forgot nine names. It is that forgetting was
# possible AND SILENT - the same defect this module docstring argues against a
# few paragraphs above: "a rule that depends on every future importer author
# remembering it is a convention". An allowlist depends on every future TABLE
# author remembering it, which is that same convention wearing a different hat.
#
# SO IT IS INVERTED. Protection is the default. A table is unprotected only if
# it is named below as genuinely ephemeral. A table added to app/models.py
# tomorrow is protected from the moment it exists, by construction, with nobody
# having done anything.
#
# WHY BOTH LISTS STILL EXIST. The guard needs only EPHEMERAL_TABLES; everything
# else is protected. PRESERVED_TABLES is the CLASSIFICATION, and it exists so
# that "protected because somebody decided it should be" and "protected because
# nobody has looked at it yet" are different states. The
# preservation_classification checker requires every mapped table to appear in
# exactly one of the two, so an unclassified table is protected AND reported
# rather than protected and unnoticed.
#
# That distinction matters the day somebody adds a genuinely ephemeral table:
# under the old allowlist they would have got the right behaviour by accident
# and never learned the question existed.
# ---------------------------------------------------------------------------

# The only tables anything may remove rows from. Each entry carries WHY,
# because an unexplained name here is a hole nobody can audit later.
EPHEMERAL_TABLES = frozenset({
    # The auditor own output. pipeline_check_results is an append-only
    # observation log that is deliberately flushed and archived, and
    # checks_flush_fallback.py exists to do exactly that. A finding is
    # re-derived by re-running the checker; nothing here is unrecoverable.
    "pipeline_check_results",
    "pipeline_check_runs",
    "pipeline_findings",
    # alembic bookkeeping. It holds a POINTER to the current revision, not a
    # record of anything, and alembic rewrites it on every migration. Guarding
    # it would mean guarding a value that is meant to change. Note that alembic
    # runs on its own engine - alembic/env.py builds one with
    # engine_from_config - so this guard never sees those statements anyway.
    # The entry is here so the classification is honest rather than accidental.
    "alembic_version",
})

# Throwaway tables created and destroyed inside a single harness run.
#
# THE RISK, STATED RATHER THAN BURIED: a prefix is a bypass. Anybody who names
# a real table cc_scratch_prices loses its protection. That is closed for
# anything that is actually a table in app/models.py - the classification
# checker treats a mapped table wearing this prefix as a DEFECT - and it is NOT
# closed for a raw-SQL table nobody declared. The alternative was requiring an
# edit to this file for every harness temp table, and a guard that is annoying
# to work with is a guard people find ways around.
EPHEMERAL_PREFIXES = ("cc_scratch_",)

# The classification. Not consulted by the guard - protection is the default -
# but required to be complete by the preservation_classification checker.
#
# Every one of these holds rows we could never re-derive if they went: an
# entity absent from a patch has not stopped having existed. Port Olisar is the
# proof. It resolves to nothing in the location gazetteer and survives only as
# a decoration item and a T-shirt description.
PRESERVED_TABLES = frozenset({
    # Ships and the things that describe them.
    "ships",
    "ship_registry",
    "manufacturers",
    "components",
    "component_types",
    "systems",
    "patches",
    "dealers",
    "ship_dealer_listings",
    "pledge_links",
    "weapon_details",
    "missile_details",
    "missile_rack_details",
    "turret_details",
    "gimbal_mount_details",
    # The shop and price layer, built over the A-G runs on 2026-08-19. A price
    # is a fact with a date attached and the table is append-only by design -
    # the unique key includes snapshot_id precisely so that a later pull ADDS
    # rows. Deleting one destroys the only record of what something cost in
    # August.
    "shop_items",
    "item_prices",
    "terminals",
    "locations",
    "item_categories",
    "snapshots",
    "shop_item_commodity_xref",
    # Hardpoints, G8. Derived from mesh measurement, and the coverage table
    # records WHY a hull has no slots - a reason that took a build to produce
    # and cannot be recovered from the slots themselves.
    "ship_hardpoints",
    "ship_hardpoint_coverage",
})


def is_ephemeral(table):
    """True if rows may be removed from this table.

    The single definition. The guard, the checker and every caller ask this
    rather than testing membership themselves, so there is one answer to the
    question instead of three that can drift apart.
    """
    if not table:
        return False
    name = str(table).lower()
    return name in EPHEMERAL_TABLES or name.startswith(EPHEMERAL_PREFIXES)


def is_protected(table):
    """True if rows may NOT be removed. The default for anything unclassified."""
    return not is_ephemeral(table)


def classification_problems(metadata=None):
    """Every mapped table must appear in exactly one of the two lists.

    This is what makes forgetting LOUD. Protection already happens by default,
    so an unclassified table is safe - but "safe because nobody looked" and
    "safe because somebody decided" are different states, and only one of them
    is a decision. Returns a list of strings; empty means fully classified.
    """
    if metadata is None:
        from app.database import Base
        from app import models  # noqa: F401 - importing registers the models
        metadata = Base.metadata

    mapped = {name.lower() for name in metadata.tables}
    problems = []

    for name in sorted(mapped - PRESERVED_TABLES - EPHEMERAL_TABLES):
        if name.startswith(EPHEMERAL_PREFIXES):
            continue  # reported below, with a sharper message
        problems.append(
            "table %r is mapped in app/models.py but classified in NEITHER "
            "PRESERVED_TABLES nor EPHEMERAL_TABLES. It is protected by "
            "default, so nothing is at risk - but nobody has decided whether "
            "it should be. Add it to one of the two lists in "
            "app/preservation.py." % name)

    for name in sorted(mapped & PRESERVED_TABLES & EPHEMERAL_TABLES):
        problems.append(
            "table %r is in BOTH PRESERVED_TABLES and EPHEMERAL_TABLES. One of "
            "those is wrong, and the guard will treat it as ephemeral - which "
            "is the dangerous reading of an ambiguity." % name)

    for name in sorted(n for n in mapped if n.startswith(EPHEMERAL_PREFIXES)):
        problems.append(
            "table %r is a real mapped table wearing an ephemeral prefix (%s). "
            "The prefix exists for harness throwaways; a declared table using "
            "it silently loses its protection. Rename it." % (
                name, ", ".join(EPHEMERAL_PREFIXES)))

    # A name in a list that is not a table any more. Not dangerous, but the
    # classification then describes something that does not exist - usually a
    # rename nobody finished - and a list nobody trusts is a list nobody reads.
    for name in sorted(PRESERVED_TABLES - mapped):
        problems.append(
            "%r is named in PRESERVED_TABLES but is not a mapped table. Either "
            "it was renamed and the list was not, or it is owned by another "
            "authority and belongs in that authority own record." % name)

    return problems


# TRUNCATE and DELETE in raw text. Matched case-insensitively; the table name is
# extracted so the message can name what was about to be lost.
_RAW_DESTRUCTIVE = re.compile(
    r"\b(?P<verb>DELETE\s+FROM|TRUNCATE(?:\s+TABLE)?)\s+"
    r"(?:ONLY\s+)?[\"']?(?P<table>[A-Za-z_][A-Za-z0-9_]*)",
    re.IGNORECASE,
)

_INSTALLED = []


def _violation(table, how):
    return PreservationViolation(
        "REFUSING to remove rows from %r via %s.\n"
        "Citizen Compass never deletes preserved rows: an entity absent from a "
        "patch is MARKED absent, not dropped. This is the only record we hold "
        "of things CIG has removed - Port Olisar is already lost this way.\n"
        "If the entity is gone from the game, update the row (status/"
        "last_seen_patch) instead of deleting it.\n"
        "PROTECTION IS THE DEFAULT HERE (H7). If this table is genuinely "
        "ephemeral - an auditor log, a harness throwaway - say so by adding it "
        "to EPHEMERAL_TABLES in app/preservation.py, with the reason. Do not "
        "reach around the guard.\n"
        "See docs/WORKORDER_preservation-model-and-never-delete-rule.md" % (table, how)
    )


def install_never_delete_guard(target):
    """Install on an Engine, Session or sessionmaker. Idempotent per target."""

    def _before_execute(conn, clauseelement, multiparams, params, execution_options):
        table = None
        if isinstance(clauseelement, Delete):
            t = clauseelement.table
            table = getattr(t, "name", None)
            how = "a DELETE statement"
        else:
            text = getattr(clauseelement, "text", None)
            if text is None:
                text = str(clauseelement) if clauseelement is not None else ""
            m = _RAW_DESTRUCTIVE.search(text)
            if m:
                table = m.group("table")
                how = m.group("verb").upper().split()[0]
        if table and is_protected(table):
            raise _violation(table, how)

    def _before_flush(session, flush_context, instances):
        for obj in session.deleted:
            t = getattr(getattr(obj, "__table__", None), "name", None)
            if t and is_protected(t):
                raise _violation(t, "session.delete()")

    # Core/SQL layer, on whatever was passed in.
    event.listen(target, "before_execute", _before_execute, retval=False)
    _INSTALLED.append((target, "before_execute", _before_execute))

    # ORM layer. before_flush is a SESSION event and does not exist on an
    # Engine. An earlier version registered it on the target and swallowed the
    # failure with a bare except, so passing an Engine installed HALF a guard
    # and said nothing - the ORM path stayed open while the code read as though
    # it were covered. A guard that silently does not install is worse than one
    # that is absent, so it now binds to the Session class explicitly and
    # covers every session regardless of what was passed here.
    if not any(t is _OrmSession and n == "before_flush" for t, n, _ in _INSTALLED):
        event.listen(_OrmSession, "before_flush", _before_flush)
        _INSTALLED.append((_OrmSession, "before_flush", _before_flush))

    return target


def remove_never_delete_guard(target=None):
    """Uninstall listeners. TARGET-SCOPED BY DEFAULT, and that is deliberate.

    This exists so the negative control can prove the guard is what stops the
    delete - a check that cannot fail is not a check (hard rule 12).

    But an earlier version removed EVERY listener this module had registered,
    process-wide. The verification called it to disarm its own throwaway engine
    and silently disarmed app.database.engine as well - a test helper that
    turns off the production guard, which is a worse defect than the one the
    guard prevents. It is now scoped: pass the target whose guard you want
    removed. Omitting the target removes all of them and is test-only.
    """
    remaining = []
    for entry in _INSTALLED:
        t, name, fn = entry
        if target is not None and t is not target:
            remaining.append(entry)
            continue
        try:
            event.remove(t, name, fn)
        except Exception:
            remaining.append(entry)
    _INSTALLED[:] = remaining


def preservation_guard_installed(target):
    """True if this module has a live listener on `target`."""
    return any(t is target for t, _, _ in _INSTALLED)
