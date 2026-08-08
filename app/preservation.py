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
    "install_never_delete_guard",
    "remove_never_delete_guard",
    "preservation_guard_installed",
]


class PreservationViolation(RuntimeError):
    """Raised when something tries to remove a row from a preserved table."""


# Tables holding history that can never be re-derived once dropped. The
# auditor's own tables are deliberately NOT here: pipeline_check_results is an
# append-only observation log that is allowed to be flushed and archived, and
# guarding it would break checks_flush_fallback.py.
PRESERVED_TABLES = frozenset({
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
})

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
        if table and table.lower() in PRESERVED_TABLES:
            raise _violation(table, how)

    def _before_flush(session, flush_context, instances):
        for obj in session.deleted:
            t = getattr(getattr(obj, "__table__", None), "name", None)
            if t and t.lower() in PRESERVED_TABLES:
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
