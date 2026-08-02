"""Rule 12 proof for checks/schema_checks.py.

A guard that has never fired is not a guard. This creates a table that is in
neither app/models.py nor env.py's EXCLUDED_TABLES and confirms the checker
reports it - against a throwaway database this process creates and drops
itself, never production. Reuses run_e2e_test.py's safety guard.
"""
import os
import sys
import uuid
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import run_e2e_test as harness  # noqa: E402
from checks.schema_checks import schema_ownership_check  # noqa: E402

DB_NAME = "citizen_compass_e2e_%s" % uuid.uuid4().hex[:8]
failures = []


def check(label, ok, detail=""):
    if not ok:
        failures.append(label)
    print("  %-62s %-6s %s" % (label, "OK" if ok else "FAIL", detail))


class Sess:
    """Minimal SQLAlchemy-Session-shaped wrapper so the real checker runs."""
    def __init__(self, conn):
        self.conn = conn

    def execute(self, clause, params=None):
        sql = getattr(clause, "text", str(clause))
        cur = self.conn.cursor()
        cur.execute(sql, params or ())
        rows = cur.fetchall()
        cur.close()

        class R:
            def all(self_inner):
                return rows
        return R()


harness.assert_safe_target()
parts = urlsplit(os.environ["DATABASE_URL"])
admin = urlunsplit((parts.scheme, parts.netloc, "/postgres", "", "")).replace("postgresql+psycopg2://", "postgresql://")
test = urlunsplit((parts.scheme, parts.netloc, "/" + DB_NAME, "", "")).replace("postgresql+psycopg2://", "postgresql://")

print("throwaway database:", DB_NAME)
c = psycopg2.connect(admin); c.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
c.cursor().execute('CREATE DATABASE "%s"' % DB_NAME); c.close()

db = None
try:
    db = psycopg2.connect(test)
    db.autocommit = True
    cur = db.cursor()
    sess = Sess(db)

    print()
    print("=" * 84)
    print("BASELINE - a table that IS declared in models.py must not be reported")
    print("=" * 84)
    cur.execute("CREATE TABLE ships (id serial primary key)")
    f = schema_ownership_check(sess, REPO)
    defects = [x for x in f if x.result == "DEFECT"]
    check("declared table produces no DEFECT", len(defects) == 0,
          "results=%s" % [x.result for x in f])

    print()
    print("=" * 84)
    print("KNOWN-BAD 1 - a table claimed by NEITHER authority MUST be reported")
    print("=" * 84)
    cur.execute("CREATE TABLE pipeline_something_nobody_registered (id serial primary key)")
    f = schema_ownership_check(sess, REPO)
    defects = [x for x in f if x.result == "DEFECT"]
    subjects = [x.subject for x in defects]
    check("guard FIRED", len(defects) >= 1, "%d defect(s)" % len(defects))
    check("names the offending table",
          "pipeline_something_nobody_registered" in subjects, str(subjects))
    if defects:
        print("     -> %s" % defects[0].details[:150])

    print()
    print("=" * 84)
    print("KNOWN-BAD 2 - an EXCLUDED table is correctly NOT reported as unclaimed")
    print("=" * 84)
    cur.execute("CREATE TABLE pipeline_findings (id serial primary key)")
    f = schema_ownership_check(sess, REPO)
    unclaimed = [x.subject for x in f if x.result == "DEFECT"]
    check("excluded table not flagged as unclaimed",
          "pipeline_findings" not in unclaimed, str(unclaimed))

    print()
    print("=" * 84)
    print("KNOWN-BAD 3 - a table claimed by BOTH authorities MUST be reported")
    print("=" * 84)
    # ship_registry is declared in models.py. Temporarily also name it excluded.
    env_path = REPO / "alembic" / "env.py"
    original = env_path.read_text(encoding="utf-8")
    try:
        tampered = original.replace(
            '    "pipeline_check_runs",\n', '    "pipeline_check_runs",\n    "ship_registry",\n', 1)
        env_path.write_text(tampered, encoding="utf-8")
        cur.execute("CREATE TABLE ship_registry (id serial primary key)")
        f = schema_ownership_check(sess, REPO)
        both = [x.subject for x in f if x.result == "DEFECT" and "BOTH" in x.details]
        check("double-claim FIRED", "ship_registry" in both, str(both))
    finally:
        env_path.write_text(original, encoding="utf-8")
        check("env.py restored byte-identical",
              env_path.read_text(encoding="utf-8") == original, "")

    print()
    print("=" * 84)
    print("CLEAN - with the offender gone, the checker PASSES")
    print("=" * 84)
    cur.execute("DROP TABLE pipeline_something_nobody_registered")
    cur.execute("DROP TABLE ship_registry")
    f = schema_ownership_check(sess, REPO)
    check("no DEFECTs remain", not [x for x in f if x.result == "DEFECT"],
          [x.result for x in f])
    check("reports PASS", any(x.result == "PASS" for x in f), "")

    print()
    print("=" * 84)
    print("NO SESSION - reports LIMITATION, never a false PASS")
    print("=" * 84)
    f = schema_ownership_check(None, REPO)
    check("LIMITATION not PASS", f[0].result == "LIMITATION", f[0].result)
finally:
    try:
        if db is not None:
            db.close()
    except Exception:
        pass
    harness.assert_disposable(DB_NAME, "DROP DATABASE")
    c = psycopg2.connect(admin); c.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    c.cursor().execute('DROP DATABASE IF EXISTS "%s"' % DB_NAME); c.close()
    print("\ndropped throwaway database", DB_NAME)

print()
if failures:
    print("FAILURES (%d): %s" % (len(failures), failures))
    sys.exit(1)
print("ALL ASSERTIONS PASSED - the guard fires on an unclaimed table and on a double claim")
