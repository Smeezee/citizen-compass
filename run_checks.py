#!/usr/bin/env python3
"""
CLI entry point for the pluggable checker system (docs/ARCHITECTURE_DECISIONS.md
section 4, LOCKED). Runs every registered checker, prints a human-readable
summary, and writes findings to pipeline_check_results (or the local
fallback log if no DB connection is available/configured).

Deliberately split into two groups, because the two groups have genuinely
different environment requirements (see LATEST_HANDOFF.md 2026-07-30 for
the full explanation):

  --group file    (default when no DB is reachable): checks/file_checks.py.
      stdlib + git only. Runs anywhere, including the device bridge's
      isolated Linux VM, which has no network/DB access at all.

  --group db      : checks/db_checks.py. Needs sqlalchemy and a real
      Postgres connection (via DATABASE_URL, using the app's own
      SessionLocal). Only runs where that's available - this session,
      that's nowhere for the REAL database, so these are validated
      against a scratch Postgres instead and shipped un-executed-for-real,
      exactly like every other DB-dependent piece of tonight's work.

  --group network : checks/network_checks.py. Needs outbound internet
      access. Only dependency_vulnerability_check is registered in
      CHECKERS - external_reachability_check exists and is unit-tested
      but is deliberately NOT wired in yet (see that module's docstring:
      it targets the exact host WebFetch failed against three times
      tonight, and this session's no-workaround rule applies).

  --group all     : runs file + db + network.

Usage:
  python run_checks.py --group file
  python run_checks.py --group db        # requires DATABASE_URL + sqlalchemy
  python run_checks.py --group network   # requires outbound internet + pip-audit
  python run_checks.py --group all
"""

import argparse
import sys
from pathlib import Path

from checks.framework import summarize, write_findings

REPO_ROOT = Path(__file__).resolve().parent


def _run_group(group_name, checkers, repo_root, db_conn):
    """Run a group and report WHICH checkers completed, not just what they said.

    The second return value is load-bearing. A checker that raised did not
    look, so its previous findings must go to UNKNOWN rather than CLOSED - and
    that decision is impossible without knowing which checkers succeeded. This
    used to return findings alone, which meant a crashed checker was
    indistinguishable from a clean one that found nothing.
    """
    all_findings, ran_ok, errored = [], set(), set()
    for name, fn in checkers:
        try:
            findings = fn(repo_root) if group_name == "file" else fn(db_conn, repo_root)
        except Exception as e:
            from checks.framework import Finding

            findings = [Finding(name, None, "WARNING", f"checker itself raised an exception: {e!r}")]
            errored.add(name)
        else:
            # A checker that completed vouches for every check_name it owns,
            # not merely its registered name - see CHECKER_EMITS.
            ran_ok.update(_emitted_names(name))
        all_findings.extend(findings)
    return all_findings, ran_ok, errored


def _emitted_names(registered_name):
    """Every check_name a given registered checker is allowed to produce."""
    try:
        from checks.file_checks import CHECKER_EMITS
    except Exception:
        return {registered_name}
    return CHECKER_EMITS.get(registered_name, {registered_name})


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--group", choices=["file", "db", "network", "all"], default="file")
    parser.add_argument("--source-process", default="run_checks.py")
    parser.add_argument("--no-write", action="store_true", help="print findings only, don't call write_findings")
    args = parser.parse_args()

    all_findings = []
    ran_ok, errored = set(), set()

    def _collect(triple):
        findings, ok, bad = triple
        all_findings.extend(findings)
        ran_ok.update(ok)
        errored.update(bad)

    if args.group in ("file", "all"):
        from checks.file_checks import CHECKERS as FILE_CHECKERS

        _collect(_run_group("file", FILE_CHECKERS, REPO_ROOT, None))

    if args.group in ("db", "all"):
        try:
            from checks.db_checks import CHECKERS as DB_CHECKERS
        except ImportError as e:
            print(f"--group {args.group}: checks/db_checks.py not importable here ({e}) - "
                  f"this is expected wherever sqlalchemy/the app package or a real DB connection "
                  f"isn't available. Skipping the db group.", file=sys.stderr)
        else:
            # db_checks.py's checkers take a SQLAlchemy Session (same as
            # audit_ship_components.py and the rest of the app), not a raw
            # psycopg2 connection - reuse the app's own engine/session
            # factory so this always talks to whatever DATABASE_URL the
            # app itself is configured for.
            session = None
            try:
                from sqlalchemy import text as _sql_text

                from app.database import SessionLocal

                session = SessionLocal()
                session.execute(_sql_text("SELECT 1"))
            except Exception as e:
                print(f"--group {args.group}: could not open a DB session ({e}) - "
                      f"running db checkers against no session will fail per-checker "
                      f"instead of silently skipping.", file=sys.stderr)
                if session is not None:
                    session.close()
                    session = None
            _collect(_run_group("db", DB_CHECKERS, REPO_ROOT, session))
            if session is not None:
                session.close()

    if args.group in ("network", "all"):
        from checks.network_checks import CHECKERS as NETWORK_CHECKERS

        _collect(_run_group("file", NETWORK_CHECKERS, REPO_ROOT, None))

    print(summarize(all_findings))

    if not args.no_write:
        # Fixed 2026-08-02. This previously passed db_conn=None unconditionally,
        # so EVERY finding this system ever produced went to the fallback log
        # even when the database was perfectly reachable - 874 of them, across
        # seven runs, sitting in a file with no path into the table. The session
        # opened above was used for the checkers and then never used for the
        # write. The degradation path was doing all the work, permanently.
        #
        # write_findings needs a psycopg2-style connection (it uses %s params
        # and .cursor()/.commit()), not the SQLAlchemy Session above, so open
        # one here. If that fails, fall through to the fallback log exactly as
        # before - degrading is still correct, it just must not be the default.
        write_conn = None
        try:
            import os

            import psycopg2
            from dotenv import load_dotenv

            load_dotenv(REPO_ROOT / ".env")
            _url = os.environ.get("DATABASE_URL") or os.environ.get("RAILWAY_DATABASE_URL")
            if _url:
                write_conn = psycopg2.connect(
                    _url.replace("postgresql+psycopg2://", "postgresql://"))
        except Exception as e:
            print(f"\n(no direct pipeline_check_results connection: "
                  f"{type(e).__name__}: {e})", file=sys.stderr)

        try:
            write_findings(all_findings, source_process=args.source_process, db_conn=write_conn)
        finally:
            if write_conn is not None:
                write_conn.close()

        if write_conn is not None:
            print(f"\n({len(all_findings)} findings written directly to pipeline_check_results)")
        else:
            print(f"\n({len(all_findings)} findings queued to "
                  f"logs/pipeline_check_results_fallback.jsonl - no DB connection available. "
                  f"Run checks_flush_fallback.py once the database is reachable.)")

        _apply_lifecycle(args, all_findings, ran_ok, errored)

    return 0 if not any(f.result == "DEFECT" for f in all_findings) else 1


def _apply_lifecycle(args, all_findings, ran_ok, errored):
    """Fold this run's observations into pipeline_findings and record the run.

    Note what is NOT done here: a `--group file` run passes only the file
    checkers in ran_ok, so db and network findings correctly go to UNKNOWN
    rather than CLOSED. A partial run must never look like a clean bill of
    health for the checkers it did not run.
    """
    from checks import findings_store as store

    try:
        conn = store.connect()
    except Exception as e:
        print(f"\n(lifecycle not updated - no DB connection: {type(e).__name__}: {e})",
              file=sys.stderr)
        return

    run_id = store.new_run_id()
    try:
        store.start_run(conn, run_id, groups=args.group, source_process=args.source_process)
        res = store.apply_run(conn, all_findings, checkers_ran_ok=ran_ok, run_id=run_id)
        store.finish_run(
            conn, run_id,
            attempted=len(ran_ok) + len(errored), ok=len(ran_ok),
            errored=len(errored), errored_names=errored,
            opened=res["opened"], closed=res["closed"],
            unknown=res["unknown"], unchanged=res["unchanged"],
        )
        counts = store.status_counts(conn)
        print(f"\nrun {run_id}")
        print(f"  checkers: {len(ran_ok)} ok, {len(errored)} errored"
              + (f" ({', '.join(sorted(errored))})" if errored else ""))
        print(f"  lifecycle: {res['new']} new, {res['reopened']} reopened, "
              f"{res['closed']} closed, {res['unknown']} -> unknown, "
              f"{res['unchanged']} unchanged")
        print(f"  pipeline_findings now: "
              + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
        if errored:
            print("  NOTE: findings belonging to the errored checkers above were sent to "
                  "UNKNOWN, not CLOSED - nothing looked for them this run.")
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
