"""
The absence pass: an entity missing from a patch becomes VISIBLY missing.

WHY THIS EXISTS, AND WHY IT IS NOT THE SAME AS THE DELETE GUARD
---------------------------------------------------------------
app/preservation.py stops a removed entity's row being deleted. That is
necessary and it is not sufficient.

Because nothing deletes AND nothing marks absence, the Aurora Mk I survives the
next import still flagged `purchasable`, still stamped
`last_verified_patch = 4.9`, and indistinguishable from a ship that still
exists. **The row is not lost, it is quietly turned into a lie.**

Losing a fact is recoverable from a snapshot. Publishing "you can buy this"
about a ship CIG has removed is not - and it lands on the page a newcomer
trusts most.

There was no set-difference step anywhere in this project before this file.
Nothing compared "rows in the database" against "entities in this patch".

TWO RULES THAT ARE EASY TO GET WRONG
------------------------------------
1. **Same transaction as the import.** This function never commits and never
   opens its own session. An absence pass that can be skipped, or that runs
   afterwards, is one an interrupted import silently omits - and the result is
   indistinguishable from a successful run.

2. **`last_seen_patch` records when a row was last SEEN, not last looked for.**
   A row already marked absent is not re-stamped by a later import that also
   does not contain it. Re-stamping would slowly rewrite a retirement date
   forward until it read as current.

ORTHOGONALITY
-------------
This touches `lifecycle_status` ONLY. It must never write to `ships.status`,
which is commercial availability (purchasable / pledge_only). A ship that was
pledge_only and is now retired ends up **pledge_only + retired** - both true,
neither overwriting the other.
"""

from app.models import EVIDENCE_TIERS, LIFECYCLE_STATUSES

__all__ = ["mark_absent", "AbsencePassError", "disclaimer_for"]

# Statuses that mean "still here". Anything else is already absent and must not
# be re-stamped.
_PRESENT = "live"


class AbsencePassError(RuntimeError):
    pass


def mark_absent(session, model, present_keys, patch, key_attr="name",
                absent_status="retired", note=None, evidence_tier="sealed"):
    """Reconcile one table against the entities present in `patch`.

    session       an OPEN session inside the import's transaction. Not committed
                  here - the caller commits, so an interrupted import rolls the
                  marking back with the rest of its work rather than leaving
                  rows half-marked.
    present_keys  every key observed in this patch. An EMPTY set is refused:
                  the overwhelmingly likely cause is a failed parse, and acting
                  on it would retire the entire table in one pass.
    patch         patch version string, e.g. "4.9".

    Returns {"seen": n, "newly_absent": n, "already_absent": n}.
    """
    if absent_status not in LIFECYCLE_STATUSES:
        raise AbsencePassError("unknown lifecycle status %r" % absent_status)
    if evidence_tier not in EVIDENCE_TIERS:
        raise AbsencePassError("unknown evidence tier %r" % evidence_tier)
    if not patch:
        raise AbsencePassError("a patch version is required to mark absence")

    # An import that parsed nothing looks exactly like a patch that removed
    # everything. Refusing is the only safe reading, and it fails loudly.
    present = set(present_keys or ())
    if not present:
        raise AbsencePassError(
            "present_keys is empty - refusing to mark an entire table absent. "
            "A patch that genuinely removes every entity is not a thing; a "
            "failed parse is."
        )

    # A SQLAlchemy Session begins its transaction LAZILY, on first use, so
    # in_transaction() is False here even for a perfectly correct caller. An
    # earlier version raised on that and rejected legitimate usage - a guard
    # that fires on the good path is not a stricter guard, it is a broken one.
    #
    # The real enforcement is structural and already in the signature: this
    # takes a SESSION and never commits. It cannot run "later" or "separately"
    # because it has no connection of its own, so its work lands or rolls back
    # with the import's. Joining an already-open transaction is the normal case;
    # beginning one the caller must commit is the other.
    if not session.in_transaction():
        session.begin()

    if not hasattr(model, key_attr):
        raise AbsencePassError(
            "%s has no attribute %r to key on" % (model.__name__, key_attr))
    seen = newly_absent = already_absent = 0

    for row in session.query(model).all():
        key = getattr(row, key_attr)
        if key in present:
            seen += 1
            # Seen now: this is when last_seen_patch moves.
            row.last_seen_patch = patch
            if row.first_seen_patch is None:
                row.first_seen_patch = patch
            if row.lifecycle_status != _PRESENT:
                # It came back. Say so rather than leaving a stale retirement.
                row.lifecycle_status = _PRESENT
                row.removal_note = None
            continue

        if row.lifecycle_status != _PRESENT:
            # Already absent. last_seen_patch is when it was last SEEN and must
            # not creep forward every time we look and do not find it.
            already_absent += 1
            continue

        newly_absent += 1
        row.lifecycle_status = absent_status
        row.evidence_tier = evidence_tier
        # last_seen_patch deliberately NOT touched: it already holds the last
        # patch this row was actually observed in.
        if note:
            row.removal_note = note

    return {"seen": seen, "newly_absent": newly_absent,
            "already_absent": already_absent}


def disclaimer_for(row):
    """Generate the reader-facing disclaimer from the data.

    Never hand-written per page: it is derived from lifecycle_status +
    last_seen_patch + evidence_tier so it cannot drift out of sync with the
    data and cannot be forgotten on a new page type.

    Returns None when there is nothing to disclaim.
    """
    status = getattr(row, "lifecycle_status", None)
    if status in (None, _PRESENT):
        return None

    name = getattr(row, "name", None) or "This"
    patch = getattr(row, "last_seen_patch", None)
    tier = getattr(row, "evidence_tier", None)
    note = getattr(row, "removal_note", None)

    if status == "unknown":
        # The honest shape, and the one that matters more: it tells the reader
        # exactly how much to trust the page.
        return (
            "%s existed in Star Citizen and no longer does. We hold no sealed "
            "data for it; the details below are not verified against a game "
            "file." % name
        )

    verb = {
        "retired": "was removed from Star Citizen",
        "renamed": "was renamed",
        "replaced": "was replaced",
        "never_released": "was never released",
    }.get(status, "is no longer present in Star Citizen")

    parts = ["%s %s." % (name, verb)]
    if patch:
        parts.append("Last seen in patch %s." % patch)
    if tier == "sealed" and patch:
        parts.append(
            "These figures are preserved from our sealed %s snapshot and are "
            "not current." % patch
        )
    elif tier == "external":
        parts.append(
            "The details below come from an outside source and are not "
            "verified against a game file."
        )
    elif tier == "testimony":
        parts.append(
            "The details below are remembered rather than recorded, and are "
            "not verified against a game file."
        )
    if note:
        parts.append(note)
    return " ".join(parts)
