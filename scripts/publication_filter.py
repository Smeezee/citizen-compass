"""The single place that decides whether a game-file record may be published.

WHY THIS MODULE EXISTS AS A MODULE

Star Citizen's game files carry records that CIG has not released. Two flags
mark them, and they survive into our derived tables on purpose - the derived
data is a faithful record of what is in the files, so stripping them at
derivation time would destroy the evidence that a record is unreleased.

The filtering therefore has to happen at PUBLICATION time, and it has to happen
in exactly one place. If each future page re-implements "skip the unreleased
ones", the first page that forgets is the one that ships them - and nobody finds
out from the code, they find out from a player asking why a mission that does
not exist is listed on a fan site.

THE NUMBERS, measured 2026-08-07

    data-layer/derived/contracts-by-system/contracts_full.json
        5,107 records, 958 not_for_release, 22 work_in_progress
        959 flagged in total - 18.8%, nearly one in five

    contracts_by_system.json
        5,108 records, 960 flagged

NOT CURRENTLY A LIVE LEAK. Verified 2026-08-07: nothing published reads these
tables. `scripts/split_craft_pages.py` touches `mission_type` but writes to
data-layer/processed/, never to releases/ or static/. So this module goes in
BEFORE the first contract page ships rather than after - which is the only
cheap moment to do it.

Rule 14: one writer per artifact. This decision has one definition, here.
"""

from __future__ import annotations

# The two flags, exactly as they are spelled in the derived tables. Both are
# real Python bools in the current data (checked across 2,000 sampled records);
# the truthiness test below deliberately also catches the string forms "true"/
# "1" in case an upstream serialiser ever changes shape, because a flag that
# silently stops being recognised is worse than one that was never there.
UNRELEASED_FLAGS = ("not_for_release", "work_in_progress")

_TRUTHY_STRINGS = {"true", "yes", "1"}


def _is_set(value) -> bool:
    """True if this flag value means 'flagged'.

    Deliberately strict about strings: the literal "false" must never read as
    set, and a bare non-empty string like "false" WOULD under plain truthiness.
    That is the trap this function exists to avoid.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in _TRUTHY_STRINGS
    if isinstance(value, (int, float)):
        return value != 0
    return False


def unreleased_reasons(record: dict) -> list[str]:
    """Names of the flags set on this record. Empty list means publishable."""
    if not isinstance(record, dict):
        return []
    return [flag for flag in UNRELEASED_FLAGS if _is_set(record.get(flag))]


def is_publishable(record: dict) -> bool:
    """True if this record may appear in anything a player can see."""
    return not unreleased_reasons(record)


def filter_publishable(records):
    """Return (publishable, withheld). Both are returned on purpose.

    The withheld list is not discarded, because "we removed 959 records" is a
    number a publisher should be able to log and a reviewer should be able to
    check. A filter that silently drops rows is indistinguishable from a filter
    that never ran.
    """
    publishable, withheld = [], []
    for record in records:
        (publishable if is_publishable(record) else withheld).append(record)
    return publishable, withheld
