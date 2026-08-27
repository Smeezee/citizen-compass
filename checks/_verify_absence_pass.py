"""
Rule 12 proof for the absence pass.

The failure shape this guards against is the dangerous kind: **a row that looks
perfectly fine**. So the headline test is not "does marking work" but "if I
break the marking, does the row stay `live`" - the negative control the order
demands, because without it a passing test proves nothing.

Runs against TEMP tables shadowing the real ones for this connection only. No
real row is written. Hard rule 3.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.absence import AbsencePassError, disclaimer_for, mark_absent  # noqa: E402
from app.models import Ship  # noqa: E402

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
    return (os.environ.get("DATABASE_URL") or "").replace(
        "postgresql+psycopg2://", "postgresql://")


def seed(conn):
    """Two ships in a temp table: one that will stay, one that will vanish."""
    conn.execute(text("DROP TABLE IF EXISTS pg_temp.ships"))
    conn.execute(text("CREATE TEMP TABLE ships (LIKE public.ships INCLUDING ALL)"))
    conn.execute(text("INSERT INTO ships SELECT * FROM public.ships LIMIT 2"))
    conn.execute(text(
        "UPDATE ships SET lifecycle_status='live', last_seen_patch='4.9', "
        "first_seen_patch='4.9', evidence_tier='sealed', removal_note=NULL"))
    rows = conn.execute(text("SELECT name FROM ships ORDER BY id")).all()
    return [r[0] for r in rows]


def naive_mark_absent(session, model, present_keys, patch, **kw):
    """The version somebody writes without thinking: it writes what the patch
    contains and never looks for what is missing. This is the bug."""
    present = set(present_keys)
    for row in session.query(model).all():
        if getattr(row, "name") in present:
            row.last_seen_patch = patch
    return {"seen": 0, "newly_absent": 0, "already_absent": 0}


def main():
    engine = create_engine(db_url(), future=True)
    with engine.connect() as conn:
        names = seed(conn)
        keep, vanish = names[0], names[1]
        real_before = conn.execute(text("SELECT COUNT(*) FROM public.ships")).scalar()
        sess = Session(bind=conn, future=True)

        def row(n):
            return sess.query(Ship).filter(Ship.name == n).one()

        print("\n--- 1. a removed entity SURVIVES and is marked absent ---")
        res = mark_absent(sess, Ship, present_keys=[keep], patch="4.10",
                          note="Removed by CIG in 4.10.")
        sess.flush()
        r = row(vanish)
        check("row still exists (not deleted)", r is not None)
        check("lifecycle_status moved off live -> %r" % r.lifecycle_status,
              r.lifecycle_status == "retired")
        check("last_seen_patch stayed at the PREVIOUS patch 4.9, not 4.10",
              r.last_seen_patch == "4.9")
        check("the surviving ship advanced to 4.10",
              row(keep).last_seen_patch == "4.10")
        check("counts reported: 1 seen, 1 newly absent",
              res["seen"] == 1 and res["newly_absent"] == 1)

        print("\n--- 6. ORTHOGONALITY: pledge_only AND retired, neither overwritten ---")
        conn.execute(text("UPDATE ships SET status='pledge_only' WHERE name=:n"),
                     {"n": vanish})
        sess.expire_all()
        r = row(vanish)
        check("ships.status is still pledge_only (commercial availability)",
              r.status == "pledge_only")
        check("lifecycle_status is still retired (existence)",
              r.lifecycle_status == "retired")
        check("*** both true at once - neither overwrote the other ***",
              r.status == "pledge_only" and r.lifecycle_status == "retired")

        print("\n--- 3. an already-absent row is NOT re-stamped by a later import ---")
        before = row(vanish).last_seen_patch
        res2 = mark_absent(sess, Ship, present_keys=[keep], patch="4.11")
        sess.flush()
        after = row(vanish).last_seen_patch
        check("last_seen_patch unchanged (%s -> %s)" % (before, after), before == after)
        check("counted as already_absent, not newly_absent",
              res2["already_absent"] == 1 and res2["newly_absent"] == 0)

        print("\n--- 5. the disclaimer is generated and changes with status ---")
        r = row(vanish)
        d_retired = disclaimer_for(r)
        check("retired row produces a disclaimer", bool(d_retired))
        check("it names the last seen patch", "4.9" in (d_retired or ""))
        r.lifecycle_status = "unknown"
        sess.flush()
        d_unknown = disclaimer_for(row(vanish))
        check("changing status changes the text, with nobody editing a page",
              d_unknown != d_retired)
        check("unknown says we hold no sealed data",
              "no sealed data" in (d_unknown or ""))
        check("a live row gets NO disclaimer", disclaimer_for(row(keep)) is None)
        r.lifecycle_status = "retired"
        sess.flush()

        print("\n--- 2. *** NEGATIVE CONTROL: break the pass, row stays live *** ---")
        conn.execute(text("UPDATE ships SET lifecycle_status='live'"))
        sess.expire_all()
        naive_mark_absent(sess, Ship, present_keys=[keep], patch="4.12")
        sess.flush()
        check("with the pass BROKEN the removed row is still 'live'",
              row(vanish).lifecycle_status == "live")
        mark_absent(sess, Ship, present_keys=[keep], patch="4.12")
        sess.flush()
        check("the real pass then marks it absent",
              row(vanish).lifecycle_status == "retired")

        print("\n--- 4. an interrupted import leaves NOTHING half-marked ---")
        conn.execute(text("UPDATE ships SET lifecycle_status='live'"))
        sess.expire_all()
        sp = conn.begin_nested()
        mark_absent(sess, Ship, present_keys=[keep], patch="4.13")
        sess.flush()
        check("marked inside the transaction", row(vanish).lifecycle_status == "retired")
        sp.rollback()
        sess.expire_all()
        check("*** after rollback the marking is gone with the rest of the import ***",
              row(vanish).lifecycle_status == "live")

        print("\n--- the pass refuses to guess ---")
        try:
            mark_absent(sess, Ship, present_keys=[], patch="4.14")
            check("empty present_keys refused", False)
        except AbsencePassError:
            check("empty present_keys refused (a failed parse is not a mass retirement)",
                  True)
        try:
            mark_absent(sess, Ship, present_keys=[keep], patch="")
            check("missing patch refused", False)
        except AbsencePassError:
            check("missing patch version refused", True)

        print("\n--- real table untouched ---")
        check("public.ships unchanged",
              conn.execute(text("SELECT COUNT(*) FROM public.ships")).scalar() == real_before)
        sess.close()

    print("\n" + "=" * 64)
    if FAILED:
        print("FAILED %d of %d:" % (len(FAILED), PASSED + len(FAILED)))
        for f in FAILED:
            print("  -", f)
        return 1
    print("All %d assertions passed." % PASSED)
    return 0


if __name__ == "__main__":
    sys.exit(main())
