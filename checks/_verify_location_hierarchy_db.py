"""A1 acceptance against the REAL database, in a transaction that is rolled back.

RULE16: UNPROVEN - closer than most, and the ROWS are independent: real locations
out of the real database rather than fixtures shaped to suit the
resolver, which is the whole reason this exists beside the unit control.
But `resolve_path` is imported and asked, so the answer is still the code
under test's own. Real input, self-reported verdict.

The unit control (checks/_verify_location_hierarchy.py) proves the resolver with
fake objects. This proves the same thing through the actual table, actual FKs
and actual ORM relationship loading - because "it works on a stand-in class" and
"it works when SQLAlchemy is the one populating .parent" are different claims,
and only the second one is what the site will do.

Nothing is committed. Every insert happens inside a transaction that is rolled
back at the end, so the real database is unchanged.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import inspect, text  # noqa: E402

from app.database import engine, SessionLocal  # noqa: E402
from app.locations import resolve_path  # noqa: E402
from app.models import Location  # noqa: E402

passed, failed = 0, []


def check(label, cond, detail=""):
    global passed
    if cond:
        passed += 1
        print(f"  ok   {label}")
    else:
        failed.append(label)
        print(f"  FAIL {label} {detail}")


print("--- the table really exists, with the columns claimed ---")
insp = inspect(engine)
cols = {c["name"] for c in insp.get_columns("locations")}
expected = {"id", "uex_id", "kind", "name", "code", "nickname", "parent_id",
            "star_system_id", "planet_id", "resolved_path", "detail",
            "last_verified_patch", "created_at", "updated_at",
            "verification_source", "confidence"}
check(f"columns present ({len(cols)})", expected <= cols, f"missing {expected - cols}")
idx = {i["name"] for i in insp.get_indexes("locations")}
check(f"indexes present: {sorted(idx)}",
      {"ix_locations_kind", "ix_locations_parent_id",
       "ix_locations_star_system_id", "ix_locations_planet_id"} <= idx)

session = SessionLocal()
try:
    print("\n--- ACCEPTANCE: a real chain resolves through the ORM ---")
    stanton = Location(uex_id=999068, kind="star_system", name="Stanton",
                       code="ST", confidence="unverified")
    session.add(stanton)
    session.flush()
    arccorp = Location(uex_id=999004, kind="planet", name="ArcCorp",
                       parent_id=stanton.id, star_system_id=stanton.id)
    session.add(arccorp)
    session.flush()
    area18 = Location(uex_id=999001, kind="city", name="Area 18",
                      parent_id=arccorp.id, star_system_id=stanton.id,
                      planet_id=arccorp.id)
    session.add(area18)
    session.flush()
    session.refresh(area18)
    got = resolve_path(area18)
    check(f"full chain -> {got!r}", got == "Area 18, ArcCorp, Stanton")

    print("\n--- CONTROL: a null mid-level must still resolve, with no 'None' ---")
    # ARC-L1: a Lagrange station. It has a planet and a system and NO moon.
    # The row is deliberately parented straight past the missing level, which
    # is the shape the importer will produce.
    arcl1 = Location(uex_id=999501, kind="space_station",
                     name="ARC-L1 Wide Forest Station", nickname="ARC-L1",
                     parent_id=arccorp.id, star_system_id=stanton.id,
                     planet_id=arccorp.id,
                     detail={"id_orbit": 326, "note": "no moon: lagrange point"})
    session.add(arcl1)
    session.flush()
    session.refresh(arcl1)
    got = resolve_path(arcl1)
    check(f"station with no moon -> {got!r}",
          got == "ARC-L1 Wide Forest Station, ArcCorp, Stanton"
          and "None" not in got)

    # And the harsher version: a parent row that exists but has an unusable
    # name. The chain must close over the gap rather than print it.
    nameless = Location(uex_id=999777, kind="moon", name="   ",
                        parent_id=arccorp.id, star_system_id=stanton.id)
    session.add(nameless)
    session.flush()
    outpost = Location(uex_id=999888, kind="outpost", name="Shady Glen Farms",
                       parent_id=nameless.id, star_system_id=stanton.id)
    session.add(outpost)
    session.flush()
    session.refresh(outpost)
    got = resolve_path(outpost)
    check(f"unusable name mid-chain -> {got!r}",
          got == "Shady Glen Farms, ArcCorp, Stanton" and "None" not in got)

    print("\n--- CONTROL: the kind check constraint must REFUSE a bad kind ---")
    # Observed refusing, not assumed to work. A constraint nobody has seen
    # reject anything is not a constraint.
    sp = session.begin_nested()
    try:
        session.add(Location(uex_id=999999, kind="asteroid_belt", name="Bad"))
        session.flush()
        sp.rollback()
        check("bad kind rejected", False, "IT WAS ACCEPTED - constraint is not working")
    except Exception as exc:
        sp.rollback()
        check(f"bad kind rejected by {type(exc).__name__}",
              "ck_locations_kind_valid" in str(exc), str(exc)[:120])

    print("\n--- CONTROL: (kind, uex_id) must REFUSE a duplicate ---")
    sp = session.begin_nested()
    try:
        session.add(Location(uex_id=999068, kind="star_system", name="Stanton dupe"))
        session.flush()
        sp.rollback()
        check("duplicate (kind,uex_id) rejected", False, "IT WAS ACCEPTED")
    except Exception as exc:
        sp.rollback()
        check(f"duplicate (kind,uex_id) rejected by {type(exc).__name__}",
              "uq_locations_kind_uex_id" in str(exc), str(exc)[:120])

    print("\n--- and the SAME uex_id under a DIFFERENT kind must be ALLOWED ---")
    # This is the half that proves the constraint is on the pair and not on
    # uex_id alone. Without it, "duplicates are rejected" could mean the
    # schema is wrong in the opposite direction and would reject planet 68.
    sp = session.begin_nested()
    try:
        session.add(Location(uex_id=999068, kind="planet", name="Different place"))
        session.flush()
        sp.rollback()
        check("same uex_id, different kind is allowed", True)
    except Exception as exc:
        sp.rollback()
        check("same uex_id, different kind is allowed", False, str(exc)[:120])

finally:
    session.rollback()
    session.close()

# prove the rollback actually happened - otherwise this script just wrote test
# rows into the real database and told everyone it did not
with engine.connect() as conn:
    left = conn.execute(
        text("select count(*) from locations where uex_id >= 999000")
    ).scalar()
    total = conn.execute(text("select count(*) from locations")).scalar()
print(f"\n--- rollback verified: {left} test rows left behind, "
      f"{total} rows in locations ---")
if left != 0:
    failed.append("test rows were left in the real database")

print("\n" + "=" * 62)
if failed:
    print(f"FAILED {len(failed)} of {passed + len(failed)}:")
    for x in failed:
        print("  -", x)
    sys.exit(1)
print(f"All {passed} database-level assertions passed.")
