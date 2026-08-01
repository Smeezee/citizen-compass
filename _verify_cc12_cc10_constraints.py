"""Prove the CC-12 constraints REJECT, and the CC-10 composite-PK trap is gone.

Hard rule 12: a constraint that has never rejected anything is an untested
constraint. This performs three deliberate bad inserts and REQUIRES each to
fail, then asserts each of the five detail tables has a single-column primary
key - the specific trap, since VerifiableMixin produces a composite PK and
create_all() accepts it silently.

Runs against a throwaway database this process creates and drops itself, never
production. Reuses run_e2e_test.py's safety guard rather than reimplementing it.

Exit 0 = all three rejections happened and all PK assertions hold.
Exit 1 = something that MUST fail succeeded, or a PK assertion failed.
"""
import os
import subprocess
import sys
import uuid
from urllib.parse import urlsplit, urlunsplit

import psycopg2
from psycopg2 import errors as pg_errors
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_e2e_test as harness  # noqa: E402  - reuse its guard, do not weaken it

REPO = os.path.dirname(os.path.abspath(__file__))
# Must match run_e2e_test.THROWAWAY_NAME_PATTERN, or its assert_disposable
# guard will (correctly) refuse to let this script drop its own database.
DB_NAME = "citizen_compass_e2e_%s" % uuid.uuid4().hex[:8]

failures = []


def check(label, ok, detail=""):
    if not ok:
        failures.append(label)
    print("  %-62s %s %s" % (label, "OK" if ok else "*** FAIL ***", detail))


# --- reuse the harness guard verbatim: refuses hosted hosts / unset DATABASE_URL
harness.assert_safe_target()
raw = os.environ["DATABASE_URL"]
parts = urlsplit(raw)
admin_url = urlunsplit((parts.scheme, parts.netloc, "/postgres", "", ""))
test_url = urlunsplit((parts.scheme, parts.netloc, "/" + DB_NAME, "", ""))
psycopg_admin = admin_url.replace("postgresql+psycopg2://", "postgresql://")
psycopg_test = test_url.replace("postgresql+psycopg2://", "postgresql://")

db = None
print("throwaway database: %s" % DB_NAME)
conn = psycopg2.connect(psycopg_admin)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
conn.cursor().execute('CREATE DATABASE "%s"' % DB_NAME)
conn.close()
print("created.")

try:
    env = {**os.environ, "DATABASE_URL": test_url}
    r = subprocess.run(["alembic", "upgrade", "head"], cwd=REPO, env=env,
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout, r.stderr)
        raise SystemExit("alembic upgrade failed")
    print("migrated to head.\n")

    db = psycopg2.connect(psycopg_test)
    db.autocommit = False
    cur = db.cursor()

    # Minimal valid prerequisites. The migrations already seed component_types,
    # so reuse an existing row rather than assuming the table is empty.
    cur.execute("SELECT id FROM component_types WHERE key = 'weapon'")
    row = cur.fetchone()
    if row:
        ctype = row[0]
    else:
        cur.execute(
            "INSERT INTO component_types (key, label) VALUES ('weapon','Weapon') RETURNING id")
        ctype = cur.fetchone()[0]

    cur.execute("SELECT id FROM manufacturers WHERE name = 'CC12 Proof Mfr'")
    row = cur.fetchone()
    if row:
        mfr = row[0]
    else:
        cur.execute(
            "INSERT INTO manufacturers (name, confidence) "
            "VALUES ('CC12 Proof Mfr','unverified') RETURNING id")
        mfr = cur.fetchone()[0]
    cur.execute(
        "INSERT INTO components (component_type_id, name, class_name, confidence) "
        "VALUES (%s,'Proof Weapon','PROOF_CLASS_1','unverified')", (ctype,))
    cur.execute(
        "INSERT INTO ships (name, manufacturer_id, status, confidence) "
        "VALUES ('Proof Ship',%s,'purchasable','unverified')", (mfr,))
    db.commit()
    print("=" * 78)
    print("THE THREE REJECTION TESTS - each MUST fail")
    print("=" * 78)

    # 1. duplicate class_name
    try:
        cur.execute(
            "INSERT INTO components (component_type_id, name, class_name, confidence) "
            "VALUES (%s,'Dup Weapon','PROOF_CLASS_1','unverified')", (ctype,))
        db.commit()
        check("1. duplicate class_name REJECTED", False, "-> INSERT SUCCEEDED, constraint is not working")
    except pg_errors.UniqueViolation as e:
        db.rollback()
        check("1. duplicate class_name REJECTED", True,
              "-> UniqueViolation on %s" % (e.diag.constraint_name,))
    except Exception as e:
        db.rollback()
        check("1. duplicate class_name REJECTED", False, "-> wrong error: %s" % type(e).__name__)

    # 2. NULL class_name
    try:
        cur.execute(
            "INSERT INTO components (component_type_id, name, class_name, confidence) "
            "VALUES (%s,'Null Weapon',NULL,'unverified')", (ctype,))
        db.commit()
        check("2. NULL class_name REJECTED", False, "-> INSERT SUCCEEDED, column is still nullable")
    except pg_errors.NotNullViolation as e:
        db.rollback()
        check("2. NULL class_name REJECTED", True,
              "-> NotNullViolation on %s.%s" % (e.diag.table_name, e.diag.column_name))
    except Exception as e:
        db.rollback()
        check("2. NULL class_name REJECTED", False, "-> wrong error: %s" % type(e).__name__)

    # 3. duplicate (name, manufacturer_id)
    try:
        cur.execute(
            "INSERT INTO ships (name, manufacturer_id, status, confidence) "
            "VALUES ('Proof Ship',%s,'purchasable','unverified')", (mfr,))
        db.commit()
        check("3. duplicate (name, manufacturer_id) REJECTED", False,
              "-> INSERT SUCCEEDED, ships still has no unique constraint")
    except pg_errors.UniqueViolation as e:
        db.rollback()
        check("3. duplicate (name, manufacturer_id) REJECTED", True,
              "-> UniqueViolation on %s" % (e.diag.constraint_name,))
    except Exception as e:
        db.rollback()
        check("3. duplicate (name, manufacturer_id) REJECTED", False,
              "-> wrong error: %s" % type(e).__name__)

    # Control: a VALID insert must still succeed, or the constraints are too broad
    try:
        cur.execute(
            "INSERT INTO components (component_type_id, name, class_name, confidence) "
            "VALUES (%s,'Valid Weapon','PROOF_CLASS_2','unverified')", (ctype,))
        db.commit()
        check("control: a VALID insert still succeeds", True)
    except Exception as e:
        db.rollback()
        check("control: a VALID insert still succeeds", False, "-> %s" % type(e).__name__)

    print()
    print("=" * 78)
    print("CC-10 - single-column primary keys on the five detail tables")
    print("=" * 78)
    for table in ("weapon_details", "missile_details", "missile_rack_details",
                  "gimbal_mount_details", "turret_details"):
        cur.execute("""
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = %s::regclass AND i.indisprimary
            ORDER BY a.attnum
        """, (table,))
        pk = [r[0] for r in cur.fetchall()]
        check("%-22s PK == ['component_id']" % table, pk == ["component_id"], "-> %s" % pk)

        cur.execute("""
            SELECT column_name, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = %s AND column_name IN
              ('confidence','verification_source','created_at','updated_at','last_verified_patch')
            ORDER BY column_name
        """, (table,))
        cols = {r[0]: (r[1], r[2]) for r in cur.fetchall()}
        check("%-22s has all 5 provenance columns" % table, len(cols) == 5, "-> %s" % sorted(cols))
        conf = cols.get("confidence")
        check("%-22s confidence NOT NULL default unverified" % table,
              bool(conf) and conf[0] == "NO" and "unverified" in (conf[1] or ""),
              "-> %s" % (conf,))

    # confidence CHECK must also bite
    print()
    try:
        cur.execute(
            "INSERT INTO components (component_type_id, name, class_name, confidence) "
            "VALUES (%s,'Bad Conf','PROOF_CLASS_3','bogus')", (ctype,))
        db.commit()
        check("bonus: invalid confidence value REJECTED", False, "-> SUCCEEDED")
    except pg_errors.CheckViolation as e:
        db.rollback()
        check("bonus: invalid confidence value REJECTED", True,
              "-> CheckViolation on %s" % (e.diag.constraint_name,))
    except Exception as e:
        db.rollback()
        check("bonus: invalid confidence value REJECTED", False, "-> %s" % type(e).__name__)

    cur.close()
    db.close()
    db = None
finally:
    # Clean up in a way that cannot mask the real error: if the drop itself
    # fails, report it rather than letting it replace whatever went wrong above.
    try:
        # Postgres refuses DROP DATABASE while any session is still attached,
        # so close ours before asking - including on the error path.
        try:
            if db is not None:
                db.close()
        except Exception:
            pass
        harness.assert_disposable(DB_NAME, "DROP DATABASE")
        conn = psycopg2.connect(psycopg_admin)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        conn.cursor().execute('DROP DATABASE IF EXISTS "%s"' % DB_NAME)
        conn.close()
        print("\ndropped throwaway database %s" % DB_NAME)
    except BaseException as cleanup_error:  # noqa: BLE001 - deliberately broad
        print("\nCLEANUP FAILED for %s: %r" % (DB_NAME, cleanup_error))
        print("The database was left in place. Drop it by hand when convenient.")

print()
if failures:
    print("FAILURES (%d):" % len(failures))
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("ALL CONSTRAINT REJECTIONS CONFIRMED - the constraints bite, and no composite PK remains")
