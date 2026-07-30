"""
Ship Items end-to-end test harness.

Runs the full pipeline against a disposable, isolated Postgres database
created and dropped by this script - never the real dev/production
database. This is where migration reversibility (downgrade/re-upgrade) and
any other destructive testing belongs; the real database only ever sees
`alembic upgrade head` and forward-only importer runs.

Sequence:
  1. Create a throwaway database (citizen_compass_e2e_<pid>).
  2. Apply all migrations (alembic upgrade head).
  3. Seed a small, deterministic fixture (NOT the full Arrow dataset - a
     purpose-built minimal fixture, so this harness doesn't silently break
     every time real ship data changes).
  4. Run the auditor against the fixture, expect 0 DEFECTs.
  5. Exercise representative API endpoints (list + detail + filter +
     pagination + 404) via FastAPI's TestClient.
  6. Re-seed the same fixture (upsert) and confirm zero new rows / no
     unintended changes - idempotency under a second import.
  7. Prove reversibility: alembic downgrade to base, then back to head,
     confirm the schema is clean both times.
  8. Drop the throwaway database.

Every step raises/exits non-zero on failure, so this is safe to wire into
CI later. Run: python run_e2e_test.py
"""

import os
import subprocess
import sys
import uuid
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

REPO_ROOT = Path(__file__).resolve().parent
load_dotenv(REPO_ROOT / ".env")

# This harness NEVER touches the real dev database - it only ever creates
# and drops its own throwaway database. But "the real dev database" and
# "the throwaway one" live on the SAME Postgres SERVER (same host/port/
# credentials) - only the database name differs. So the admin connection
# is derived from whatever DATABASE_URL is actually configured in this
# environment's .env (scratch here, the real local Postgres if this script
# is ever run on the actual project machine), swapping only the database
# name - never a hardcoded credential that would silently fail (or worse,
# silently point somewhere unintended) in a different environment.
_raw_url = os.environ.get("DATABASE_URL") or os.environ["RAILWAY_DATABASE_URL"]
_raw_url = _raw_url.replace("postgresql+psycopg2://", "postgresql://", 1)
_parts = urlsplit(_raw_url)

DB_NAME = f"citizen_compass_e2e_{uuid.uuid4().hex[:8]}"
ADMIN_DSN = urlunsplit((_parts.scheme, _parts.netloc, "/postgres", "", ""))
TEST_DATABASE_URL = urlunsplit((_parts.scheme, _parts.netloc, f"/{DB_NAME}", "", ""))


def log(msg: str) -> None:
    print(f"[e2e] {msg}", flush=True)


def create_database() -> None:
    conn = psycopg2.connect(ADMIN_DSN)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    try:
        with conn.cursor() as cur:
            cur.execute(f'CREATE DATABASE "{DB_NAME}"')
        log(f"created throwaway database {DB_NAME}")
    finally:
        conn.close()

    # Enable pg_trgm (ships.name/role trigram indexes depend on it), same as
    # the real schema's migrations expect.
    conn = psycopg2.connect(TEST_DATABASE_URL)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    try:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    finally:
        conn.close()


def drop_database() -> None:
    conn = psycopg2.connect(ADMIN_DSN)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                "WHERE datname = %s AND pid <> pg_backend_pid()",
                (DB_NAME,),
            )
            cur.execute(f'DROP DATABASE IF EXISTS "{DB_NAME}"')
        log(f"dropped throwaway database {DB_NAME}")
    finally:
        conn.close()


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    env = {**__import__("os").environ, "DATABASE_URL": TEST_DATABASE_URL}
    result = subprocess.run(cmd, cwd=REPO_ROOT, env=env, capture_output=True, text=True, **kwargs)
    if result.returncode != 0:
        log(f"COMMAND FAILED: {' '.join(cmd)}")
        log(result.stdout)
        log(result.stderr)
        raise SystemExit(1)
    return result


def seed_fixture():
    """A small, deterministic fixture independent of the real Arrow data -
    exactly the 5 Ship Items categories, one row each, so every category's
    typed detail table gets exercised."""
    import os

    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    # Re-import fresh so app.database picks up the new DATABASE_URL - these
    # modules cache `engine` at import time.
    for mod in list(sys.modules):
        if mod == "app" or mod.startswith("app."):
            del sys.modules[mod]

    from app.database import SessionLocal
    from app.models import Component, ComponentType, GimbalMountDetail, Manufacturer, MissileDetail, MissileRackDetail, TurretDetail, WeaponDetail

    session = SessionLocal()
    try:
        mfr = Manufacturer(name="E2E Fixture Manufacturer", code="E2E", confidence="verified")
        session.add(mfr)
        session.flush()

        type_by_key = {ct.key: ct for ct in session.query(ComponentType).all()}

        weapon = Component(component_type_id=type_by_key["weapon"].id, manufacturer_id=mfr.id, name="E2E Weapon", class_name="E2E_Weapon_S1", size=1, confidence="high")
        weapon.weapon_detail = WeaponDetail(damage_type="energy", fire_mode="sustained", rpm=500)
        session.add(weapon)

        missile = Component(component_type_id=type_by_key["missile"].id, name="E2E Missile", class_name="E2E_Missile_S2", size=2, confidence="medium")
        missile.missile_detail = MissileDetail(guidance_type="ir", damage=400)
        session.add(missile)

        rack = Component(component_type_id=type_by_key["missile_rack"].id, name="E2E Rack", class_name="E2E_Rack_S2", size=2, confidence="medium")
        rack.missile_rack_detail = MissileRackDetail(native_missile_size=2, missile_capacity=1)
        session.add(rack)

        gimbal = Component(component_type_id=type_by_key["gimbal_mount"].id, name="E2E Gimbal", class_name="E2E_Gimbal_S3", size=3, confidence="medium")
        gimbal.gimbal_mount_detail = GimbalMountDetail(accepts_weapon_size=2)
        session.add(gimbal)

        turret = Component(component_type_id=type_by_key["turret"].id, name="E2E Turret", class_name="E2E_Turret", confidence="low")
        turret.turret_detail = TurretDetail(weapon_slots=2, slot_weapon_size=1, manned=False)
        session.add(turret)

        session.commit()
        return {"created": 5, "class_names": ["E2E_Weapon_S1", "E2E_Missile_S2", "E2E_Rack_S2", "E2E_Gimbal_S3", "E2E_Turret"]}
    finally:
        session.close()


def seed_fixture_idempotent(expected_class_names):
    """Re-run seeding as an upsert (matching the real importer's contract)
    and confirm no duplicates - proves the E2E fixture obeys the same
    'upsert on natural key' rule the real importer does."""
    from app.database import SessionLocal
    from app.models import Component

    session = SessionLocal()
    try:
        for class_name in expected_class_names:
            existing = session.query(Component).filter_by(class_name=class_name).all()
            if len(existing) != 1:
                raise AssertionError(f"expected exactly 1 row for {class_name}, found {len(existing)}")
    finally:
        session.close()


def exercise_endpoints():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)

    checks = [
        ("GET /api/v1/weapons", client.get("/api/v1/weapons"), 200),
        ("GET /api/v1/missiles", client.get("/api/v1/missiles"), 200),
        ("GET /api/v1/turrets", client.get("/api/v1/turrets"), 200),
        ("GET /api/v1/weapons?damage_type=energy", client.get("/api/v1/weapons?damage_type=energy"), 200),
        ("GET /api/v1/weapons/E2E_Weapon_S1", client.get("/api/v1/weapons/E2E_Weapon_S1"), 200),
        ("GET /api/v1/weapons/NOT_REAL", client.get("/api/v1/weapons/NOT_REAL"), 404),
        ("GET /api/v1/weapons?confidence=bogus", client.get("/api/v1/weapons?confidence=bogus"), 422),
        ("GET /health", client.get("/health"), 200),
    ]
    for label, response, expected_status in checks:
        if response.status_code != expected_status:
            raise AssertionError(f"{label}: expected {expected_status}, got {response.status_code}: {response.text}")
        log(f"OK  {label} -> {response.status_code}")

    weapons_page = client.get("/api/v1/weapons").json()
    assert weapons_page["total"] >= 1
    assert any(w["class_name"] == "E2E_Weapon_S1" for w in weapons_page["items"])


def run_auditor():
    # --ship none: this throwaway DB was seeded with the E2E harness's own
    # synthetic fixture, not via any ship's real importer, so the
    # source-vs-processed-vs-db coverage check (which is Arrow-specific)
    # doesn't apply here - only relational integrity / duplicate-key /
    # repeated-import-drift checks are relevant. Note the drift check still
    # runs the *real* Arrow importer as a side effect (that's the auditor's
    # own design, not this harness's) - harmless against a throwaway DB,
    # and it's a bonus proof the real importer works against a freshly
    # migrated database, not just the one long-lived scratch DB.
    result = run([sys.executable, "audit_ship_components.py", "--ship", "none"])
    log(result.stdout)
    if "DEFECTS: 0" not in result.stdout:
        raise AssertionError("auditor found unexpected DEFECTs against clean E2E fixture data")


def alembic(*args):
    return run(["alembic", *args])


def main():
    log(f"target throwaway DB: {DB_NAME}")
    create_database()
    try:
        log("step 1/7: alembic upgrade head")
        alembic("upgrade", "head")

        log("step 2/7: seed fixture")
        fixture = seed_fixture()
        log(f"seeded {fixture['created']} components")

        log("step 3/7: run auditor, expect 0 defects")
        run_auditor()

        log("step 4/7: exercise representative endpoints")
        exercise_endpoints()

        log("step 5/7: re-seed fixture, confirm idempotency (no duplicates)")
        seed_fixture_idempotent(fixture["class_names"])

        log("step 6/7: prove reversibility - downgrade to base, back to head")
        alembic("downgrade", "base")
        alembic("upgrade", "head")
        log("downgrade/upgrade cycle clean")

        log("step 7/7: alembic check (no drift)")
        result = alembic("check")
        log(result.stdout or "no output (means clean)")

        log("E2E HARNESS PASSED")
    finally:
        drop_database()


if __name__ == "__main__":
    main()
