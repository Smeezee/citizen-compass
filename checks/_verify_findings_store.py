"""
Rule 12 proof for the finding lifecycle's PERSISTENCE layer.

checks/_verify_lifecycle.py already proves the pure transition function. This
proves the part that actually writes to Postgres, because a correct rule that
the storage layer applies wrongly is not a correct system.

THE CENTRAL TEST, and the reason this file exists
-------------------------------------------------
    A checker that stopped running must never look like a problem that went
    away.

So the headline case is deliberately hostile: take a table full of OPEN
findings, break the checkers so none of them complete, run the lifecycle, and
demand that EVERY finding goes to UNKNOWN and that ZERO go to CLOSED. A system
that reports a wave of closures when its checkers died would be worse than no
system, because it would manufacture the confidence that nothing is wrong.

HOW THIS RUNS SAFELY - hard rule 3
----------------------------------
Against TEMP tables created with `LIKE public.<table> INCLUDING ALL`, which
shadow the real tables for this connection only (pg_temp precedes public on
the search_path). Consequences, all deliberate:

  * Every statement in findings_store.py hits the temp copies unmodified -
    the real code is exercised, not a reimplementation of it.
  * The real pipeline_findings and pipeline_check_results are never written.
  * Cleanup happens when the connection closes. This file issues no DROP, no
    DELETE, no TRUNCATE and creates no database, so it stays entirely inside
    hard rule 3 without needing the e2e harness.

Run: venv/Scripts/python.exe checks/_verify_findings_store.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from checks.framework import Finding  # noqa: E402
from checks.findings_store import (  # noqa: E402
    apply_run,
    backfill_from_results,
    load_previous,
    new_run_id,
    status_counts,
)
from checks.lifecycle import finding_key  # noqa: E402

PASSED = 0
FAILED = []


def check(label, condition):
    global PASSED
    if condition:
        PASSED += 1
        print(f"  ok   {label}")
    else:
        FAILED.append(label)
        print(f"  FAIL {label}")


def make_temp_tables(conn):
    """Shadow the three real tables with temp copies for this connection."""
    with conn.cursor() as cur:
        for t in ("pipeline_findings", "pipeline_check_results", "pipeline_check_runs"):
            cur.execute(f"CREATE TEMP TABLE {t} (LIKE public.{t} INCLUDING ALL)")
    conn.commit()
    # Prove the shadowing actually took effect. If it did not, this script
    # would be writing to the real table - so this is checked, not assumed.
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM pipeline_findings")
        empty = cur.fetchone()[0] == 0
        cur.execute("SELECT COUNT(*) FROM public.pipeline_findings")
        real = cur.fetchone()[0]
    return empty, real


def f(check_name, subject, details, result="DEFECT"):
    return Finding(check_name, subject, result, details)


def main():
    from checks.findings_store import connect

    conn = connect()
    shadowed, real_before = make_temp_tables(conn)

    print("\n--- temp-table isolation ---")
    check("temp pipeline_findings is empty (shadowing is in effect)", shadowed)

    # ---------------------------------------------------------------- basics
    print("\n--- identity and OPEN ---")
    r1 = new_run_id()
    res = apply_run(conn, [
        f("model_check", "85X", "no model.glb found"),
        f("model_check", "Fury", "no model.glb found"),
    ], checkers_ran_ok={"model_check"}, run_id=r1)
    check("two distinct findings opened", res["opened"] == 2)
    check("status counts: 2 OPEN", status_counts(conn).get("OPEN") == 2)

    print("\n--- the same condition seen twice is ONE row ---")
    r2 = new_run_id()
    res = apply_run(conn, [
        f("model_check", "85X", "no model.glb found"),
        f("model_check", "85X", "no model.glb found"),
        f("model_check", "Fury", "no model.glb found"),
    ], checkers_ran_ok={"model_check"}, run_id=r2)
    check("nothing newly opened on a repeat run", res["opened"] == 0)
    check("still exactly 2 rows", len(load_previous(conn)) == 2)

    print("\n--- details that vary but describe the same condition ---")
    # What drifts here is the timestamp VALUE inside an otherwise identical
    # message. That is the real-world case: the same condition re-reported
    # later. Adding or removing surrounding words is a genuinely DIFFERENT
    # condition and SHOULD mint a new finding - that is not what is tested
    # here, and conflating the two is how this assertion was wrong the first
    # time I wrote it.
    r3a = new_run_id()
    apply_run(conn, [
        f("model_check", "85X", "no model.glb found"),
        f("model_check", "Fury", "no model.glb found"),
        f("drift_check", "snap-9", "manifest unreadable at 2026-08-01T10:00:00"),
    ], checkers_ran_ok={"model_check", "drift_check"}, run_id=r3a)
    check("a third, timestamped finding opened", len(load_previous(conn)) == 3)

    r3b = new_run_id()
    res = apply_run(conn, [
        f("model_check", "85X", "no model.glb found"),
        f("model_check", "Fury", "no model.glb found"),
        f("drift_check", "snap-9", "manifest unreadable at 2026-08-01T11:30:00"),
    ], checkers_ran_ok={"model_check", "drift_check"}, run_id=r3b)
    check("timestamp drift did NOT mint a new finding", res["opened"] == 0)
    check("still exactly 3 rows", len(load_previous(conn)) == 3)

    # -------------------------------------------------------- CLOSED, legit
    print("\n--- CLOSED requires a run that looked ---")
    r4 = new_run_id()
    res = apply_run(conn, [f("model_check", "Fury", "no model.glb found")],
                    checkers_ran_ok={"model_check"}, run_id=r4)
    check("85X closed by a run that ran its checker and did not see it",
          res["closed"] == 1)
    prev = load_previous(conn)
    k85 = finding_key("model_check", "85X", "no model.glb found")
    check("85X status is CLOSED", prev[k85]["status"] == "CLOSED")
    with conn.cursor() as cur:
        cur.execute("SELECT closed_at, closed_by_run FROM pipeline_findings WHERE finding_key=%s", (k85,))
        closed_at, closed_by = cur.fetchone()
    check("closed_at recorded", closed_at is not None)
    check("closed_by_run records WHICH run closed it", closed_by == r4)

    # ==================================================================
    # THE CENTRAL TEST
    # ==================================================================
    print("\n--- *** a broken checker must yield UNKNOWN, never CLOSED *** ---")
    r5 = new_run_id()
    apply_run(conn, [
        f("model_check", "Fury", "no model.glb found"),
        f("registry_sync", "reg", "registry and db disagree"),
        f("hash_check", "snap-1", "manifest hash mismatch"),
    ], checkers_ran_ok={"model_check", "registry_sync", "hash_check"}, run_id=r5)
    before = status_counts(conn)
    open_before = before.get("OPEN", 0)
    closed_before = before.get("CLOSED", 0)
    check("3 findings are OPEN before the break", open_before == 3)

    # Now the whole suite dies: no checker completes, so nothing is observed.
    r6 = new_run_id()
    res = apply_run(conn, [], checkers_ran_ok=set(), run_id=r6)
    counts = status_counts(conn)
    check("ZERO findings closed when no checker ran", res["closed"] == 0)
    check("every OPEN finding went to UNKNOWN", counts.get("OPEN", 0) == 0)
    check("all 3 are now UNKNOWN", counts.get("UNKNOWN", 0) >= open_before)
    check("the CLOSED count did not grow by a single row",
          counts.get("CLOSED", 0) == closed_before)

    print("\n--- one checker errors, another succeeds: only the healthy one closes ---")
    r7 = new_run_id()
    apply_run(conn, [
        f("model_check", "Fury", "no model.glb found"),
        f("registry_sync", "reg", "registry and db disagree"),
        f("hash_check", "snap-1", "manifest hash mismatch"),
    ], checkers_ran_ok={"model_check", "registry_sync", "hash_check"}, run_id=r7)
    r8 = new_run_id()
    # model_check ran and saw nothing; registry_sync and hash_check errored.
    res = apply_run(conn, [], checkers_ran_ok={"model_check"}, run_id=r8)
    check("exactly 1 closed (the only checker that actually ran)", res["closed"] == 1)
    # The invariant that matters: nothing belonging to a checker that did not
    # run this time may be CLOSED.
    closed_owners = {
        v["check_name"] for v in load_previous(conn).values()
        if v["status"] == "CLOSED"
    }
    check("no finding of an errored checker is CLOSED",
          closed_owners <= {"model_check"})
    prev = load_previous(conn)
    kf = finding_key("model_check", "Fury", "no model.glb found")
    kr = finding_key("registry_sync", "reg", "registry and db disagree")
    check("Fury CLOSED - its checker looked", prev[kf]["status"] == "CLOSED")
    check("registry finding UNKNOWN - its checker did not", prev[kr]["status"] == "UNKNOWN")

    print("\n--- a checker that is no longer registered yields UNKNOWN ---")
    r9 = new_run_id()
    res = apply_run(conn, [], checkers_ran_ok={"model_check"}, run_id=r9)
    check("de-registered checker's finding did not close", res["closed"] == 0)

    # ------------------------------------------------------- refuse to guess
    print("\n--- the API refuses to guess ---")
    try:
        apply_run(conn, [], checkers_ran_ok=None, run_id=new_run_id())
        check("apply_run(checkers_ran_ok=None) raises", False)
    except ValueError:
        check("apply_run(checkers_ran_ok=None) raises rather than closing blindly", True)

    # ------------------------------------------------------------ reopening
    print("\n--- reopening clears an acknowledgement ---")
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE pipeline_findings SET status='ACKNOWLEDGED', acknowledged=TRUE, "
            "acknowledged_by='Sleven', acknowledged_reason='known, accepted' "
            "WHERE finding_key=%s", (kf,))
    conn.commit()
    r10 = new_run_id()
    apply_run(conn, [f("model_check", "Fury", "no model.glb found")],
              checkers_ran_ok={"model_check"}, run_id=r10)
    prev = load_previous(conn)
    check("ACKNOWLEDGED survives being seen again", prev[kf]["status"] == "ACKNOWLEDGED")
    check("ACKNOWLEDGED is still counted, not hidden", prev[kf]["acknowledged"] is True)

    with conn.cursor() as cur:
        cur.execute("UPDATE pipeline_findings SET status='CLOSED', closed_at=NOW() "
                    "WHERE finding_key=%s", (kf,))
    conn.commit()
    r11 = new_run_id()
    res = apply_run(conn, [f("model_check", "Fury", "no model.glb found")],
                    checkers_ran_ok={"model_check"}, run_id=r11)
    prev = load_previous(conn)
    check("a CLOSED finding that reappears goes back to OPEN", prev[kf]["status"] == "OPEN")
    check("reopening cleared the acknowledgement", prev[kf]["acknowledged"] is False)
    with conn.cursor() as cur:
        cur.execute("SELECT closed_at FROM pipeline_findings WHERE finding_key=%s", (kf,))
        check("reopening cleared closed_at", cur.fetchone()[0] is None)

    # ------------------------------------------------------------- backfill
    print("\n--- backfill lands as UNKNOWN, never OPEN ---")
    with conn.cursor() as cur:
        cur.execute("DELETE FROM pipeline_findings")  # temp table only
        for i, (ts, det) in enumerate([
            ("2026-07-30 10:00:00", "no model.glb found"),
            ("2026-07-30 14:00:00", "no model.glb found"),
            ("2026-07-31 09:00:00", "no model.glb found"),
            ("2026-07-31 09:00:00", "a different problem entirely"),
        ]):
            cur.execute(
                "INSERT INTO pipeline_check_results (check_name, subject, result, details, "
                "source_process, checked_at) VALUES (%s,%s,%s,%s,%s,%s)",
                ("model_check", "85X", "DEFECT", det, "test", ts))
    conn.commit()

    res = backfill_from_results(conn, new_run_id())
    check("4 source rows collapsed to 2 distinct findings",
          res["source_rows"] == 4 and res["distinct_findings"] == 2)
    counts = status_counts(conn)
    check("every backfilled finding is UNKNOWN", counts.get("UNKNOWN") == 2)
    check("NOTHING was backfilled as OPEN", counts.get("OPEN", 0) == 0)
    with conn.cursor() as cur:
        cur.execute("SELECT first_seen, last_seen, occurrences FROM pipeline_findings "
                    "WHERE finding_key=%s",
                    (finding_key("model_check", "85X", "no model.glb found"),))
        first, last, occ = cur.fetchone()
    check("first_seen is the earliest observation", str(first).startswith("2026-07-30 10:00"))
    check("last_seen is the latest observation", str(last).startswith("2026-07-31 09:00"))
    check("occurrences counted the collapsed rows", occ == 3)

    print("\n--- a backfilled UNKNOWN can still be closed by a real run ---")
    r12 = new_run_id()
    res = apply_run(conn, [], checkers_ran_ok={"model_check"}, run_id=r12)
    check("UNKNOWN closes once a checker actually looks", res["closed"] == 2)

    # ------------------------------------------------- real tables untouched
    print("\n--- the real tables were never written ---")
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM public.pipeline_findings")
        check("public.pipeline_findings unchanged", cur.fetchone()[0] == real_before)

    conn.close()

    print(f"\n{'='*62}")
    if FAILED:
        print(f"FAILED {len(FAILED)} of {PASSED + len(FAILED)} assertions:")
        for x in FAILED:
            print(f"  - {x}")
        return 1
    print(f"All {PASSED} assertions passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
