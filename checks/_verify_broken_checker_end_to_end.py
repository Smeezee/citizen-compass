"""
The demonstration this work order names specifically:

RULE16: UNPROVEN - the lifecycle is observed only through the table the
lifecycle writes. The sabotage is external and the expected statuses
(UNKNOWN, never CLOSED) are stated here rather than read back, but a
defect that corrupted the transition AND its record together would be
invisible to this. What it cannot reach is a second, independent account
of what happened to a finding.

    deliberately break a checker and prove it produces UNKNOWN rather than a
    wave of CLOSED.

Everything else in this layer is tested at the seams - the transition function
alone, the storage layer alone. This runs the REAL run_checks.py pipeline with
a REAL checker sabotaged, because the failure being guarded against is an
end-to-end one: a checker starts raising, the schedule keeps running, and the
findings table quietly reports that a pile of problems went away.

Sabotage used: missing_or_corrupt_3d_model_check is replaced with a function
that raises. That checker owns 6 genuinely-open DEFECTs (85X, Arrastra, Fury,
Mantis, Merchantman, PTV) plus the missing_preview_image findings, so if the
guard were absent the damage would be large, specific, and completely silent.

SAFELY, per hard rule 3: against TEMP tables shadowing the real ones for this
connection only. No DROP, no TRUNCATE, no database created. The real
pipeline_findings is asserted unchanged at the end.

Run: venv/Scripts/python.exe checks/_verify_broken_checker_end_to_end.py
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import checks.file_checks as file_checks  # noqa: E402
from checks.findings_store import (  # noqa: E402
    apply_run,
    connect,
    load_previous,
    new_run_id,
    status_counts,
)

PASSED, FAILED = 0, []


def check(label, cond):
    global PASSED
    if cond:
        PASSED += 1
        print(f"  ok   {label}")
    else:
        FAILED.append(label)
        print(f"  FAIL {label}")


def run_suite(conn, sabotage: bool, run_id: str):
    """Run the file group the way run_checks.py does, optionally sabotaged."""
    import run_checks

    checkers = list(file_checks.CHECKERS)
    if sabotage:
        def exploding_checker(repo_root):
            raise RuntimeError("simulated checker failure (deliberate)")
        checkers = [
            (n, exploding_checker if n == "missing_or_corrupt_3d_model" else fn)
            for n, fn in checkers
        ]

    findings, ran_ok, errored = run_checks._run_group("file", checkers, REPO, None)
    res = apply_run(conn, findings, checkers_ran_ok=ran_ok, run_id=run_id)
    return findings, ran_ok, errored, res


def main():
    conn = connect()
    with conn.cursor() as cur:
        for t in ("pipeline_findings", "pipeline_check_results", "pipeline_check_runs"):
            cur.execute(f"CREATE TEMP TABLE {t} (LIKE public.{t} INCLUDING ALL)")
        cur.execute("SELECT COUNT(*) FROM public.pipeline_findings")
        real_before = cur.fetchone()[0]
    conn.commit()

    print("\n--- baseline: a healthy run establishes the open findings ---")
    _, ran_ok, errored, res = run_suite(conn, sabotage=False, run_id=new_run_id())
    check("no checker errored in the healthy run", len(errored) == 0)
    baseline = load_previous(conn)
    model_keys = {
        k for k, v in baseline.items()
        if v["check_name"] in ("missing_or_corrupt_3d_model", "missing_preview_image")
        and v["status"] == "OPEN"
    }
    model_defects = {
        k for k in model_keys if baseline[k]["result"] == "DEFECT"
    }
    print(f"       {len(model_keys)} open findings belong to the checker about to be broken "
          f"({len(model_defects)} of them DEFECTs)")
    check("the checker being broken owns real open findings", len(model_keys) > 0)

    # THE DEFECT COUNT IS DATA, NOT AN EXPECTATION - and the assertions that
    # USE it are guarded, which is the actual find here.
    #
    # This said `len(model_defects) == 6` and went red on 2026-08-27 because the
    # count is now 0: the model library filled up during the day, so no model is
    # genuinely missing any more. That on its own would just be a stale number.
    #
    # What matters is what it was holding up. Two assertions below are of the
    # form `all(... for k in model_defects)`, and **on an empty set those pass
    # vacuously**. With the count assertion gone or updated, this control would
    # have reported two green lines about DEFECTs it never looked at - hard rule
    # 12's silent success, in the file whose whole subject is a checker that
    # silently stopped looking.
    #
    # So: when there are no DEFECTs the DEFECT-specific assertions are reported
    # NOT PERFORMED and are neither passed nor failed. When there are any, they
    # run exactly as before.
    have_defects = len(model_defects) > 0
    if not have_defects:
        print("       NOT PERFORMED - no missing-model DEFECT exists right now, "
              "so the three assertions about DEFECT survival cannot be "
              "exercised. Reported, never passed.")

    print("\n--- now break that checker and run again ---")
    _, ran_ok2, errored2, res2 = run_suite(conn, sabotage=True, run_id=new_run_id())
    check("the broken checker is reported as errored",
          "missing_or_corrupt_3d_model" in errored2)
    check("it is NOT in the set of checkers that ran ok",
          "missing_or_corrupt_3d_model" not in ran_ok2)
    check("other checkers still ran normally", len(ran_ok2) > 5)

    after = load_previous(conn)
    now_unknown = {k for k in model_keys if after[k]["status"] == "UNKNOWN"}
    now_closed = {k for k in model_keys if after[k]["status"] == "CLOSED"}

    print(f"\n       of {len(model_keys)} findings owned by the broken checker:")
    print(f"         -> UNKNOWN : {len(now_unknown)}")
    print(f"         -> CLOSED  : {len(now_closed)}")

    check("EVERY finding of the broken checker went to UNKNOWN",
          len(now_unknown) == len(model_keys))
    check("*** ZERO were CLOSED - no wave of false closures ***",
          len(now_closed) == 0)
    if have_defects:
        check("the %d genuinely-missing model DEFECTs are still visible, not "
              "closed" % len(model_defects),
              all(after[k]["status"] == "UNKNOWN" for k in model_defects))

    print("\n--- recovery: the checker is fixed and runs again ---")
    _, _, errored3, res3 = run_suite(conn, sabotage=False, run_id=new_run_id())
    recovered = load_previous(conn)
    check("no checker errored after the fix", len(errored3) == 0)
    if have_defects:
        check("the %d real DEFECTs came back as OPEN, not lost"
              % len(model_defects),
              all(recovered[k]["status"] == "OPEN" for k in model_defects))
    # The OPEN findings are the half that always has a population - 271 of them
    # today - so the recovery claim is asserted against those whatever the
    # DEFECT count is, rather than resting on a set that can empty out.
    check("every finding of the broken checker came back as OPEN, not lost",
          bool(model_keys) and
          all(recovered[k]["status"] == "OPEN" for k in model_keys))

    print("\n--- the real table was never touched ---")
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM public.pipeline_findings")
        check("public.pipeline_findings unchanged", cur.fetchone()[0] == real_before)
    conn.close()

    print("\n" + "=" * 66)
    if FAILED:
        print(f"FAILED {len(FAILED)} of {PASSED + len(FAILED)} assertions:")
        for x in FAILED:
            print(f"  - {x}")
        return 1
    print(f"All {PASSED} assertions passed.")
    print("A checker that stopped running did NOT look like a problem that went away.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
