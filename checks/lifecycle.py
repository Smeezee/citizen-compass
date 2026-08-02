"""
Finding lifecycle: identity, status, and the transition rules.

WHY THIS EXISTS
---------------
Parts A and B loaded 890 findings and established that most described problems
that no longer existed. Of 33 DEFECTs, roughly 6 were live: 32 rows described 11
subjects; a corrupt-file report was a checker bug already fixed six hours
earlier; four ships flagged as missing models had models copied in afterwards;
seven fan-kit warnings were one warning seen seven times.

A findings table that is mostly ghosts is worse than no table, because the only
rational response is to skim it - and skimming is how the real one gets missed.

WHERE THE STATE LIVES - and why it is a companion table
-------------------------------------------------------
`pipeline_check_results` stays exactly as it is: an append-only OBSERVATION log,
one row per thing-a-run-saw. That history is not redundant - it is precisely
what made the staleness diagnosis possible, by letting finding timestamps be
compared against commit times.

Lifecycle state is a different thing: one row per distinct condition, describing
what is true NOW. Collapsing the two would destroy the observation history to
gain a status column.

So: new table `pipeline_findings`, keyed by `finding_key`, one row per condition.
`pipeline_check_results` is untouched and keeps accumulating.

THE LOAD-BEARING RULE
---------------------
**A finding is CLOSED only by a run that looked for it and did not find it.**

If its checker errored, was skipped, or is no longer registered, the finding
becomes UNKNOWN - never CLOSED. A checker that stopped running must never look
like a problem that went away. This project has already had a scheduled process
stop unnoticed, and has already had a status brief claim something had stopped
when it was still running. Silence is not evidence of absence, so that is
encoded here rather than remembered.

Nothing is ever closed by a human, by a session, or by inference. If it is
fixed, the next run proves it.
"""
import hashlib
import re

# ---------------------------------------------------------------- statuses
OPEN = "OPEN"
CLOSED = "CLOSED"
UNKNOWN = "UNKNOWN"
ACKNOWLEDGED = "ACKNOWLEDGED"
STATUSES = (OPEN, CLOSED, UNKNOWN, ACKNOWLEDGED)


# ------------------------------------------------------------ normalisation
# Every pattern here strips something that VARIES BETWEEN RUNS while the
# underlying condition stays the same. Getting this wrong reproduces the
# 32-rows-for-11-problems result exactly: key off "this ship has no model",
# never off "checked at 14:57 and this ship has no model".
_NORMALISERS = (
    # ISO timestamps, with or without microseconds/zone
    (re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?"), "<TS>"),
    # bare dates
    (re.compile(r"\b\d{4}-\d{2}-\d{2}\b"), "<DATE>"),
    # Windows paths -> keep only the filename. Must handle BOTH absolute
    # ("C:\repo\sc-ships\85X\model.glb") and relative ("sc-ships\85X\model.glb"),
    # because the same condition is reported both ways depending on which
    # checker produced it. Requiring a drive letter here was a real bug: it made
    # those two spellings different findings, which is exactly the
    # near-duplicate problem this module exists to stop.
    (re.compile(r"(?:[A-Za-z]:)?(?:[^\\\s\"']*\\)+"), ""),
    # POSIX absolute paths
    (re.compile(r"(?<![\w.])/(?:[^/\s\"']+/)+"), ""),
    # hex ids: git sha, uuid, run id
    (re.compile(r"\b[0-9a-f]{7,40}\b", re.I), "<HEX>"),
    (re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I), "<UUID>"),
    # counts that drift as data grows - "62 DB ship name(s)" is the same
    # condition as "63 DB ship name(s)"
    (re.compile(r"\b\d[\d,]*\b"), "<N>"),
)


def normalise_condition(details: str) -> str:
    """Reduce a details string to the condition it describes.

    Deliberately aggressive about numbers. A count that drifts by one is the
    same finding; treating it as new is how a table fills with near-duplicates.
    """
    if details is None:
        return ""
    text = details.strip()
    for pattern, replacement in _NORMALISERS:
        text = pattern.sub(replacement, text)
    # collapse whitespace last, after substitutions have left gaps
    return re.sub(r"\s+", " ", text).strip().lower()


def finding_key(check_name: str, subject, details: str) -> str:
    """Stable identity for a condition: check + subject + normalised condition.

    Same condition seen twice is one finding, not two rows - regardless of when
    it was seen, which run saw it, or how the count drifted.
    """
    basis = "\x1f".join((
        (check_name or "").strip().lower(),
        (subject or "").strip().lower(),
        normalise_condition(details),
    ))
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:32]


# ------------------------------------------------------------- transitions
def reconcile(previous, seen_now, checkers_ran_ok, run_id):
    """Compute the new lifecycle state.

    previous        {finding_key: {"status":…, "check_name":…, "acknowledged":…}}
    seen_now        {finding_key: finding-dict} observed by THIS run
    checkers_ran_ok set of check_names that completed successfully this run
    run_id          identifier for this run

    Returns (to_open, to_close, to_unknown, unchanged) as lists of finding_key.

    The rules, in order of precedence:
      1. Seen this run                        -> OPEN (or stays ACKNOWLEDGED)
      2. Not seen, its checker ran cleanly     -> CLOSED
      3. Not seen, its checker did NOT run ok  -> UNKNOWN
    """
    to_open, to_close, to_unknown, unchanged = [], [], [], []

    for key in seen_now:
        prev = previous.get(key)
        if prev is None:
            to_open.append(key)
        elif prev.get("status") == ACKNOWLEDGED:
            # Still real, still accepted. Stays acknowledged, last_seen moves.
            unchanged.append(key)
        elif prev.get("status") == OPEN:
            unchanged.append(key)
        else:
            # Was CLOSED or UNKNOWN and has reappeared. Reopening clears any
            # acknowledgement: the world changed, look again.
            to_open.append(key)

    for key, prev in previous.items():
        if key in seen_now:
            continue
        if prev.get("status") in (CLOSED,):
            continue  # already closed, nothing to do
        checker = prev.get("check_name")
        if checker in checkers_ran_ok:
            # A run looked for it and did not find it. This is the ONLY way a
            # finding closes.
            to_close.append(key)
        else:
            # Its checker errored, was skipped, or is no longer registered.
            # Absence of evidence is not evidence of absence.
            to_unknown.append(key)

    return to_open, to_close, to_unknown, unchanged


def implausible_mass_close(closed_count, open_before, threshold=0.5):
    """A mass close is far more often a broken checker than a productive
    afternoon. Returns True if this run closed an implausible share."""
    if open_before <= 0:
        return False
    return (closed_count / open_before) >= threshold
