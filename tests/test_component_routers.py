"""Unit + integration tests for the generic Ship Items component router
factory (app/routers/component_factory.py + weapons/missiles/turrets.py).

Precondition: the target database already has all migrations applied
(`alembic upgrade head`) so `component_types` is seeded with the 5 Ship
Items categories - these tests insert their own fixture Component rows in
a rolled-back transaction, they do not depend on import_ship_components.py
having been run.
"""

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models import Component, ComponentType, Manufacturer, MissileDetail, TurretDetail, WeaponDetail

# db_session fixture lives in conftest.py, shared across the test suite.


@pytest.fixture()
def client(db_session):
    def _get_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture()
def seeded(db_session):
    """A small, deterministic fixture set - independent of whatever the
    real importer has or hasn't populated."""
    mfr = Manufacturer(name="Test Manufacturer Co", code="TMC", confidence="verified")
    db_session.add(mfr)
    db_session.flush()

    weapon_type = db_session.query(ComponentType).filter_by(key="weapon").one()
    missile_type = db_session.query(ComponentType).filter_by(key="missile").one()
    turret_type = db_session.query(ComponentType).filter_by(key="turret").one()

    weapon = Component(
        component_type_id=weapon_type.id,
        manufacturer_id=mfr.id,
        name="Test Laser Repeater",
        class_name="TEST_LaserRepeater_S1",
        size=1,
        grade="A",
        confidence="high",
    )
    weapon.weapon_detail = WeaponDetail(damage_type="energy", fire_mode="sustained", rpm=600, dps=250.5)
    db_session.add(weapon)

    weapon2 = Component(
        component_type_id=weapon_type.id,
        name="Test Ballistic Cannon",
        class_name="TEST_BallisticCannon_S2",
        size=2,
        confidence="medium",
    )
    weapon2.weapon_detail = WeaponDetail(damage_type="ballistic", fire_mode="burst")
    db_session.add(weapon2)

    missile = Component(
        component_type_id=missile_type.id,
        name="Test IR Missile",
        class_name="TEST_Missile_S2_IR",
        size=2,
        confidence="medium",
    )
    missile.missile_detail = MissileDetail(guidance_type="ir", damage=500)
    db_session.add(missile)

    turret = Component(
        component_type_id=turret_type.id,
        name="Test Manned Turret",
        class_name="TEST_Turret_Manned",
        confidence="low",
    )
    turret.turret_detail = TurretDetail(weapon_slots=2, slot_weapon_size=1, manned=True)
    db_session.add(turret)

    db_session.commit()
    return {
        "manufacturer": mfr,
        "weapon": weapon,
        "weapon2": weapon2,
        "missile": missile,
        "turret": turret,
    }


# --- List endpoints ---------------------------------------------------------


def test_list_weapons_returns_page_envelope(client, seeded):
    r = client.get("/api/v1/weapons")
    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) == {"items", "total", "limit", "offset"}
    assert body["total"] >= 2
    names = [item["name"] for item in body["items"]]
    assert "Test Laser Repeater" in names
    assert "Test Ballistic Cannon" in names


def test_list_weapons_only_returns_weapons_not_other_categories(client, seeded):
    r = client.get("/api/v1/weapons")
    names = [item["name"] for item in r.json()["items"]]
    assert seeded["missile"].name not in names
    assert seeded["turret"].name not in names


def test_list_is_deterministically_ordered_by_name_then_id(client, seeded):
    r = client.get("/api/v1/weapons")
    names = [item["name"] for item in r.json()["items"]]
    assert names == sorted(names)


def test_list_pagination_bounds(client, seeded):
    r = client.get("/api/v1/weapons?limit=1&offset=0")
    assert r.status_code == 200
    assert len(r.json()["items"]) == 1
    assert r.json()["limit"] == 1

    r_over_max = client.get("/api/v1/weapons?limit=99999")
    assert r_over_max.status_code == 422

    r_zero = client.get("/api/v1/weapons?limit=0")
    assert r_zero.status_code == 422


def test_filter_by_manufacturer_substring_case_insensitive(client, seeded):
    r = client.get("/api/v1/weapons?manufacturer=test manufacturer")
    assert r.status_code == 200
    names = [item["name"] for item in r.json()["items"]]
    assert "Test Laser Repeater" in names
    assert "Test Ballistic Cannon" not in names  # weapon2 has no manufacturer set


def test_filter_by_size(client, seeded):
    r = client.get("/api/v1/weapons?size=2")
    names = [item["name"] for item in r.json()["items"]]
    assert "Test Ballistic Cannon" in names
    assert "Test Laser Repeater" not in names


def test_filter_by_category_specific_field_weapon_damage_type(client, seeded):
    r = client.get("/api/v1/weapons?damage_type=energy")
    names = [item["name"] for item in r.json()["items"]]
    assert "Test Laser Repeater" in names
    assert "Test Ballistic Cannon" not in names


def test_filter_by_category_specific_field_missile_guidance_type(client, seeded):
    r = client.get("/api/v1/missiles?guidance_type=ir")
    assert r.status_code == 200
    assert any(item["name"] == "Test IR Missile" for item in r.json()["items"])

    r_none = client.get("/api/v1/missiles?guidance_type=em")
    assert all(item["name"] != "Test IR Missile" for item in r_none.json()["items"])


def test_filter_turret_manned_boolean(client, seeded):
    r_true = client.get("/api/v1/turrets?manned=true")
    assert any(item["name"] == "Test Manned Turret" for item in r_true.json()["items"])

    r_false = client.get("/api/v1/turrets?manned=false")
    assert all(item["name"] != "Test Manned Turret" for item in r_false.json()["items"])


def test_invalid_confidence_value_returns_422(client, seeded):
    r = client.get("/api/v1/weapons?confidence=not-a-real-level")
    assert r.status_code == 422
    assert "confidence" in r.json()["detail"]


# --- Detail endpoint ---------------------------------------------------------


def test_get_weapon_by_id(client, seeded):
    r = client.get(f"/api/v1/weapons/{seeded['weapon'].id}")
    assert r.status_code == 200
    assert r.json()["class_name"] == "TEST_LaserRepeater_S1"
    assert r.json()["damage_type"] == "energy"


def test_get_weapon_by_class_name(client, seeded):
    r = client.get("/api/v1/weapons/TEST_LaserRepeater_S1")
    assert r.status_code == 200
    assert r.json()["id"] == seeded["weapon"].id


def test_get_weapon_not_found_returns_404(client, seeded):
    r = client.get("/api/v1/weapons/NOT_A_REAL_CLASS_NAME")
    assert r.status_code == 404
    assert "weapon" in r.json()["detail"]


def test_get_weapon_wrong_category_returns_404_not_leak(client, seeded):
    """A missile's id must not resolve through the weapons detail route -
    categories are isolated even though they all share the same
    `components` base table."""
    r = client.get(f"/api/v1/weapons/{seeded['missile'].id}")
    assert r.status_code == 404


def test_get_weapon_huge_numeric_identifier_does_not_crash(client, seeded):
    r = client.get("/api/v1/weapons/999999999999999999999999999999")
    assert r.status_code == 404


# --- Cross-cutting: doesn't break existing endpoints -------------------------


def test_existing_ships_endpoint_unaffected(client):
    r = client.get("/api/v1/ships")
    assert r.status_code == 200


def test_openapi_includes_new_routes(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    paths = r.json()["paths"]
    for p in ("/api/v1/weapons", "/api/v1/missiles", "/api/v1/turrets"):
        assert p in paths
        assert f"{p}/{{identifier}}" in paths
