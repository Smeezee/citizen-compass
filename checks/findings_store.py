"""
Persistence for the finding lifecycle: loads previous state, applies the
transition rules from checks/lifecycle.py, and writes the result.

WHAT THIS MODULE IS CAREFUL ABOUT
---------------------------------
Exactly one thing, and everything here follows from it:

    A finding is CLOSED only by a run that looked for it and did not find it.

That means a caller can never simply hand over "the findings I saw". It must
also hand over **which checkers actually completed**, because the meaning of a
finding's absence depends entirely on whether anything looked. `apply_run`
therefore takes `checkers_ran_ok` as a required argument, not an optional one,
and there is deliberately no default. A caller that does not know which
checkers succeeded cannot use this module - which is the intended outcome,
because such a caller would otherwise close findings it had no evidence about.

WRITES
------
This module writes ONLY to pipeline_findings and pipeline_check_runs. It never
modifies pipeline_check_results (append-only observation log) and never touches
project data. Findings-only, per ARCHITECTURE_DECISIONS.md section 4 (LOCKED).
"""

import datetime
import os
import socket
import uuid

from checks.lifecycle import (
    ACKNOWLEDGED,
    CLOSED,
    OPEN,
    UNKNOWN,
    finding_key,
)


def new_run_id() -> str:
    """Run ids are sortable-by-time and unique. The host is included because
    Part D's schedule and a human at a terminal both write here, and telling
    them apart afterwards matters."""
    stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    return f"{stamp}-{socket.gethostname()[:12]}-{uuid.uuid4().hex[:6]}"


# ------------------------------------------------------------------ run rows
def start_run(conn, run_id: str, groups: str, source_process: str) -> None:
    """Record that a run began, BEFORE any checker executes.

    Written up front on purpose. A run that crashes half way through leaves a
    row with a NULL ended_at, which is a visible, queryable "this run did not
    finish" - whereas writing the row at the end would leave a crashed run
    indistinguishable from a run that never started.
    """
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO pipeline_check_runs (run_id, started_at, groups, source_process) "
            "VALUES (%s, %s, %s, %s)",
            (run_id, datetime.datetime.now(), groups, source_process),
        )
    conn.commit()


def finish_run(conn, run_id: str, *, attempted, ok, errored, errored_names,
               opened, closed, unknown, unchanged, notes=None) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE pipeline_check_runs SET ended_at=%s, checkers_attempted=%s, "
            "checkers_ok=%s, checkers_errored=%s, errored_names=%s, findings_opened=%s, "
            "findings_closed=%s, findings_unknown=%s, findings_unchanged=%s, notes=%s "
            "WHERE run_id=%s",
            (datetime.datetime.now(), attempted, ok, errored,
             ", ".join(sorted(errored_names)) if errored_names else None,
             opened, closed, unknown, unchanged, notes, run_id),
        )
    conn.commit()


# ------------------------------------------------------------- current state
def load_previous(conn) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT finding_key, check_name, subject, result, status, acknowledged, "
            "first_seen, occurrences FROM pipeline_findings"
        )
        return {
            r[0]: {
                "finding_key": r[0], "check_name": r[1], "subject": r[2], "result": r[3],
                "status": r[4], "acknowledged": r[5], "first_seen": r[6], "occurrences": r[7],
            }
            for r in cur.fetchall()
        }


def _index_findings(findings) -> dict:
    """Collapse a run's findings to one entry per finding_key.

    Two checkers can report the same condition, and one checker can report it
    twice. Collapsing here is what stops 32 rows describing 11 problems.
    """
    seen = {}
    for f in findings:
        key = finding_key(f.check_name, f.subject, f.details)
        if key in seen:
            seen[key]["occurrences"] += 1
            continue
        seen[key] = {
            "finding_key": key, "check_name": f.check_name, "subject": f.subject,
            "result": f.result, "details": f.details, "occurrences": 1,
        }
    return seen


def apply_run(conn, findings, checkers_ran_ok, run_id: str, scope=None) -> dict:
    """Apply one run's observations to the lifecycle table.

    `checkers_ran_ok` is a set of check_names that COMPLETED. It is required.
    A checker that raised, was skipped, or is no longer registered must not be
    in it - that is what sends its findings to UNKNOWN rather than CLOSED.

    `scope` is the set of check_names this run was RESPONSIBLE for - normally
    every checker registered in the groups being run. Findings outside it are
    left completely untouched.

    Scope exists because without it, partial runs corrupt each other. The order
    schedules the file group and the db group as separate daily invocations; a
    db-only run does not observe any file finding, so an unscoped run would
    mark all of them UNKNOWN, and the next file run would mark all the db ones
    UNKNOWN in turn. The two schedules would spend every day undoing each
    other, and the table would permanently misreport whichever ran second.

    Note what scope does NOT do: it never causes a CLOSE. A checker inside the
    scope that did not complete still sends its findings to UNKNOWN, exactly as
    before. Scope only decides what a run is entitled to have an opinion about.
    """
    if checkers_ran_ok is None:
        raise ValueError(
            "checkers_ran_ok is required: without it, absence of a finding is "
            "ambiguous and this function would close findings nothing verified."
        )
    checkers_ran_ok = set(checkers_ran_ok)

    from checks.lifecycle import reconcile

    previous = load_previous(conn)
    if scope is not None:
        scope = set(scope)
        previous = {k: v for k, v in previous.items() if v["check_name"] in scope}
    seen_now = _index_findings(findings)
    to_open, to_close, to_unknown, unchanged = reconcile(
        previous, seen_now, checkers_ran_ok, run_id
    )

    now = datetime.datetime.now()
    with conn.cursor() as cur:
        # Seen this run: upsert. ACKNOWLEDGED survives being seen again -
        # it is a real finding that is known and accepted, so seeing it is
        # confirmation, not news.
        for key, f in seen_now.items():
            prev = previous.get(key)
            if prev is None:
                cur.execute(
                    "INSERT INTO pipeline_findings (finding_key, check_name, subject, result, "
                    "details, status, first_seen, last_seen, status_changed_at, run_id, occurrences) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (key, f["check_name"], f["subject"], f["result"], f["details"],
                     OPEN, now, now, now, run_id, f["occurrences"]),
                )
            else:
                keep_ack = prev["status"] == ACKNOWLEDGED
                new_status = ACKNOWLEDGED if keep_ack else OPEN
                reopening = prev["status"] in (CLOSED, UNKNOWN)
                cur.execute(
                    "UPDATE pipeline_findings SET last_seen=%s, result=%s, details=%s, "
                    "status=%s, run_id=%s, occurrences=occurrences+%s, "
                    "closed_at=NULL, closed_by_run=NULL, "
                    "status_changed_at=CASE WHEN status<>%s THEN %s ELSE status_changed_at END, "
                    # Reopening clears an acknowledgement: the world changed,
                    # so the acceptance has to be made again deliberately.
                    "acknowledged=CASE WHEN %s THEN FALSE ELSE acknowledged END, "
                    "acknowledged_by=CASE WHEN %s THEN NULL ELSE acknowledged_by END, "
                    "acknowledged_reason=CASE WHEN %s THEN NULL ELSE acknowledged_reason END "
                    "WHERE finding_key=%s",
                    (now, f["result"], f["details"], new_status, run_id, f["occurrences"],
                     new_status, now, reopening, reopening, reopening, key),
                )

        # Not seen, and its checker ran cleanly. The ONLY path to CLOSED.
        for key in to_close:
            cur.execute(
                "UPDATE pipeline_findings SET status=%s, closed_at=%s, closed_by_run=%s, "
                "status_changed_at=%s WHERE finding_key=%s",
                (CLOSED, now, run_id, now, key),
            )

        # Not seen, and its checker did NOT run cleanly. Absence of evidence
        # is not evidence of absence.
        for key in to_unknown:
            cur.execute(
                "UPDATE pipeline_findings SET status=%s, "
                "status_changed_at=CASE WHEN status<>%s THEN %s ELSE status_changed_at END "
                "WHERE finding_key=%s",
                (UNKNOWN, UNKNOWN, now, key),
            )
    conn.commit()

    # "Opened" alone is misleading: a brand-new problem and a known problem
    # coming back are different events, and the first lifecycle run reported
    # "+289 opened" when 264 of those were backfilled findings reappearing.
    return {
        "opened": len(to_open), "closed": len(to_close), "unknown": len(to_unknown),
        "unchanged": len(unchanged), "seen": len(seen_now), "previous": len(previous),
        "new": sum(1 for k in to_open if k not in previous),
        "reopened": sum(1 for k in to_open if k in previous),
    }


# ----------------------------------------------------------------- backfill
def backfill_from_results(conn, run_id: str) -> dict:
    """Collapse the existing pipeline_check_results rows into pipeline_findings.

    Per the addendum: these rows are historical and mostly stale, so their
    history is NOT reconstructed. Every one lands as UNKNOWN - not OPEN -
    because nothing has verified them today. The next full run is what decides
    which are genuinely open.

    Marking them OPEN would be the tempting choice and the wrong one: it would
    assert 890 current problems on the strength of observations nobody has
    re-checked, which is the same unfounded confidence the lifecycle exists to
    remove.
    """
    with conn.cursor() as cur:
        cur.execute(
            "SELECT check_name, subject, result, details, checked_at "
            "FROM pipeline_check_results ORDER BY checked_at"
        )
        rows = cur.fetchall()

    collapsed = {}
    for check_name, subject, result, details, checked_at in rows:
        key = finding_key(check_name, subject, details)
        entry = collapsed.get(key)
        if entry is None:
            collapsed[key] = {
                "check_name": check_name, "subject": subject, "result": result,
                "details": details, "first_seen": checked_at, "last_seen": checked_at,
                "occurrences": 1,
            }
        else:
            entry["occurrences"] += 1
            if checked_at < entry["first_seen"]:
                entry["first_seen"] = checked_at
            if checked_at > entry["last_seen"]:
                entry["last_seen"] = checked_at
                # Keep the most recent wording of the condition.
                entry["result"] = result
                entry["details"] = details

    now = datetime.datetime.now()
    with conn.cursor() as cur:
        for key, e in collapsed.items():
            cur.execute(
                "INSERT INTO pipeline_findings (finding_key, check_name, subject, result, "
                "details, status, first_seen, last_seen, status_changed_at, run_id, occurrences) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                "ON CONFLICT (finding_key) DO NOTHING",
                (key, e["check_name"], e["subject"], e["result"], e["details"],
                 UNKNOWN, e["first_seen"], e["last_seen"], now, run_id, e["occurrences"]),
            )
    conn.commit()

    return {"source_rows": len(rows), "distinct_findings": len(collapsed)}


def status_counts(conn) -> dict:
    with conn.cursor() as cur:
        cur.execute("SELECT status, COUNT(*) FROM pipeline_findings GROUP BY status")
        return dict(cur.fetchall())


def open_by_result(conn) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT result, COUNT(*) FROM pipeline_findings "
            "WHERE status IN ('OPEN','ACKNOWLEDGED') GROUP BY result"
        )
        return dict(cur.fetchall())


def connect():
    """psycopg2 connection from DATABASE_URL. Callers handle failure - this
    deliberately does not swallow it, because a silent no-DB path is how the
    fallback log became the only path for a week."""
    import psycopg2
    from dotenv import load_dotenv

    from checks.framework import REPO_ROOT

    load_dotenv(REPO_ROOT / ".env")
    url = os.environ.get("DATABASE_URL") or os.environ.get("RAILWAY_DATABASE_URL")
    if not url:
        raise RuntimeError("neither DATABASE_URL nor RAILWAY_DATABASE_URL is set")
    return psycopg2.connect(url.replace("postgresql+psycopg2://", "postgresql://"))
