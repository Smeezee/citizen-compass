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
    all_findings = []
    for name, fn in checkers:
        try:
            findings = fn(repo_root) if group_name == "file" else fn(db_conn, repo_root)
        except Exception as e:
            from checks.framework import Finding

            findings = [Finding(name, None, "WARNING", f"checker itself raised an exception: {e!r}")]
        all_findings.extend(findings)
    return all_findings


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--group", choices=["file", "db", "network", "all"], default="file")
    parser.add_argument("--source-process", default="run_checks.py")
    parser.add_argument("--no-write", action="store_true", help="print findings only, don't call write_findings")
    args = parser.parse_args()

    all_findings = []

    if args.group in ("file", "all"):
        from checks.file_checks import CHECKERS as FILE_CHECKERS

        all_findings.extend(_run_group("file", FILE_CHECKERS, REPO_ROOT, None))

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
            all_findings.extend(_run_group("db", DB_CHECKERS, REPO_ROOT, session))
            if session is not None:
                session.close()

    if args.group in ("network", "all"):
        from checks.network_checks import CHECKERS as NETWORK_CHECKERS

        all_findings.extend(_run_group("file", NETWORK_CHECKERS, REPO_ROOT, None))

    print(summarize(all_findings))

    if not args.no_write:
        # write_findings itself degrades to the local fallback log when
        # db_conn is None - see checks/framework.py.
        write_findings(all_findings, source_process=args.source_process, db_conn=None)
        print(f"\n(findings also queued to logs/pipeline_check_results_fallback.jsonl - "
              f"no live pipeline_check_results DB connection from this environment)")

    return 0 if not any(f.result == "DEFECT" for f in all_findings) else 1


if __name__ == "__main__":
    sys.exit(main())
