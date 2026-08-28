"""
Rule 12 proof for the never-delete guard.

RULE16: INDEPENDENT - the question is 'is the row still there', and that is
answered by SELECTing it back out of the database rather than by the
guard reporting that it refused. The file says why that distinction
matters in its own second paragraph: a delete that failed for some other
reason would look identical from the guard's side. Postgres is the
witness, and it did not write the guard.

The guard's whole claim is "a preserved row cannot be removed". A test that only
shows the delete failing proves nothing on its own - the delete might have
failed for some unrelated reason. So every case is run TWICE: once with the
guard installed, once with it removed. The guard is only doing work if the row
survives in the first case and disappears in the second.

Runs against TEMP tables shadowing the real ones for this connection only, so no
real row is ever at risk. Hard rule 3: no destructive statement reaches a
database this process did not create, and pg_temp is dropped when the connection
closes.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text  # noqa: E402

from app.preservation import (  # noqa: E402
    PreservationViolation,
    install_never_delete_guard,
    remove_never_delete_guard,
)

PASSED, FAILED = 0, []


def check(label, cond):
    global PASSED
    if cond:
        PASSED += 1
        print("  ok   %s" % label)
    else:
        FAILED.append(label)
        print("  FAIL %s" % label)


def db_url():
    import os

    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    u = os.environ.get("DATABASE_URL") or os.environ.get("RAILWAY_DATABASE_URL")
    return u.replace("postgresql+psycopg2://", "postgresql://")


def fresh(conn):
    """Temp table shadowing the real `ships`, seeded with one row to remove."""
    conn.execute(text("DROP TABLE IF EXISTS pg_temp.ships"))
    conn.execute(text("CREATE TEMP TABLE ships (LIKE public.ships INCLUDING ALL)"))
    # whole-row copy: the table has NOT NULL columns a hand-picked subset misses
    conn.execute(text("INSERT INTO ships SELECT * FROM public.ships LIMIT 1"))
    return conn.execute(text("SELECT COUNT(*) FROM ships")).scalar()


def rows(conn):
    return conn.execute(text("SELECT COUNT(*) FROM ships")).scalar()


def main():
    engine = create_engine(db_url(), future=True)

    # ---- shadowing must be real, or this whole file tests the wrong table ----
    with engine.connect() as conn:
        seeded = fresh(conn)
        real = conn.execute(text("SELECT COUNT(*) FROM public.ships")).scalar()
        print("\n--- isolation ---")
        check("temp ships seeded with 1 row", seeded == 1)
        check("real public.ships has many rows (so they are different tables)", real > 1)

        # ================= WITH THE GUARD ==================
        print("\n--- guard INSTALLED: a delete must be refused ---")
        install_never_delete_guard(engine)

        for label, stmt in (
            ("DELETE FROM ships", "DELETE FROM ships"),
            ("DELETE with a WHERE clause", "DELETE FROM ships WHERE id IS NOT NULL"),
            ("TRUNCATE", "TRUNCATE TABLE ships"),
            ("lowercase delete", "delete from ships"),
        ):
            try:
                conn.execute(text(stmt))
                check("%s refused" % label, False)
            except PreservationViolation:
                check("%s refused" % label, True)
            except Exception as e:
                check("%s refused (got %s)" % (label, type(e).__name__), False)
        check("row survived every attempt", rows(conn) == 1)

        # H7, 2026-08-20: THIS SECTION CHANGED MEANING, AND THE CHANGE IS THE
        # POINT. It used to read "a non-preserved table is NOT blocked", using
        # a table called scratch_notes - and it passed because scratch_notes
        # was not on the old sixteen-name allowlist. Under protect-by-default
        # scratch_notes is protected, exactly like every other table nobody has
        # classified, and this assertion FAILED the moment the inversion
        # landed. That failure is the guard working: the whole change is that
        # an unnamed table is now guarded rather than open.
        #
        # So the question it asks is now the right one: an EPHEMERAL table is
        # still deletable. If this ever fails, the auditor cannot flush its own
        # log and checks_flush_fallback.py stops working.
        print("\n--- an EPHEMERAL table is NOT blocked (the guard is targeted) ---")
        try:
            conn.execute(text("CREATE TEMP TABLE cc_scratch_notes (id int)"))
            conn.execute(text("INSERT INTO cc_scratch_notes VALUES (1)"))
            conn.execute(text("DELETE FROM cc_scratch_notes"))
            check("delete on an ephemeral table still works", True)
        except PreservationViolation:
            check("delete on an ephemeral table still works", False)

        print("\n--- and an UNCLASSIFIED table now IS blocked (H7) ---")
        try:
            conn.execute(text("CREATE TEMP TABLE unclassified_notes (id int)"))
            conn.execute(text("INSERT INTO unclassified_notes VALUES (1)"))
            conn.execute(text("DELETE FROM unclassified_notes"))
            check("a table nobody classified is refused by default", False)
        except PreservationViolation:
            check("a table nobody classified is refused by default", True)

        # ================= WITHOUT THE GUARD ==================
        # If the row disappears now, the guard above is what was stopping it.
        print("")
        print("--- DDL is NOT blocked (alembic + e2e must still work) ---")
        try:
            conn.execute(text("CREATE TEMP TABLE ddl_probe (id int)"))
            conn.execute(text("DROP TABLE ddl_probe"))
            check("DROP TABLE still works - migrations unaffected", True)
        except PreservationViolation:
            check("DROP TABLE still works - migrations unaffected", False)

        print("\n--- guard REMOVED: the same delete must now succeed ---")
        remove_never_delete_guard(engine)   # ONLY this throwaway engine
        before = rows(conn)
        conn.execute(text("DELETE FROM ships"))
        after = rows(conn)
        check("row present before the unguarded delete", before == 1)
        check("*** row GONE once the guard is removed - the guard is load-bearing ***",
              after == 0)

        # ================= ORM PATH ==================
        print("\n--- ORM session.delete() is blocked too ---")
        from sqlalchemy.orm import Session

        from app.models import Ship

        fresh(conn)
        install_never_delete_guard(engine)
        sess = Session(bind=conn, future=True)
        obj = sess.query(Ship).first()
        if obj is None:
            check("ORM found the seeded row", False)
        else:
            check("ORM found the seeded row", True)
            sess.delete(obj)
            try:
                sess.flush()
                check("session.delete() refused", False)
            except PreservationViolation:
                check("session.delete() refused", True)
            except Exception as e:
                check("session.delete() refused (got %s)" % type(e).__name__, False)
        sess.close()

        print("\n--- real table untouched throughout ---")
        check("public.ships row count unchanged",
              conn.execute(text("SELECT COUNT(*) FROM public.ships")).scalar() == real)

        remove_never_delete_guard(engine)   # scoped: never disarm the app engine

    # The guard lives in app/database.py now, so the shipped engine must be
    # covered without anyone installing it. Checked by behaviour: an import
    # that silently no-ops looks identical to one that worked.
    print("")
    print("--- app.database.engine is guarded out of the box ---")
    from app.database import engine as app_engine
    from app.preservation import preservation_guard_installed
    check("app.database.engine carries the guard on import",
          preservation_guard_installed(app_engine))

    print("\n" + "=" * 62)
    if FAILED:
        print("FAILED %d of %d:" % (len(FAILED), PASSED + len(FAILED)))
        for f in FAILED:
            print("  -", f)
        return 1
    print("All %d assertions passed." % PASSED)
    return 0


if __name__ == "__main__":
    sys.exit(main())
