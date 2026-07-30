"""
Tests for checks/db_checks.py (Ships-domain DB checkers). Uses the same
db_session fixture (savepoint-rollback) as tests/test_component_routers.py
so nothing here leaks into the shared scratch database between tests.
"""

import json

from app.models import Manufacturer, Ship
from checks.db_checks import (
    duplicate_identifier_check,
    referential_integrity_check,
    registry_sync_check,
)


def _make_manufacturer(session, name="Test Mfg"):
    m = Manufacturer(name=name, confidence="verified")
    session.add(m)
    session.flush()
    return m


def test_referential_integrity_check_passes_on_well_formed_ship(db_session):
    m = _make_manufacturer(db_session)
    db_session.add(Ship(name="Test Ship", manufacturer_id=m.id, status="purchasable", confidence="verified"))
    db_session.flush()

    findings = referential_integrity_check(db_session)

    assert all(f.result != "DEFECT" for f in findings)


def test_referential_integrity_check_flags_orphaned_manufacturer(db_session):
    m = _make_manufacturer(db_session)
    ship = Ship(name="Orphan Ship", manufacturer_id=m.id, status="purchasable", confidence="verified")
    db_session.add(ship)
    db_session.flush()

    # Simulate a row that bypassed the FK constraint check at the ORM layer
    # by pointing at a manufacturer_id that doesn't exist - done via a raw
    # UPDATE so the DB's own FK constraint (if enforced) would also have
    # to be temporarily deferred; if the constraint blocks this, that
    # itself is a good sign and the test is skipped.
    from sqlalchemy import text

    try:
        db_session.execute(text("SET CONSTRAINTS ALL DEFERRED"))
        db_session.execute(text("UPDATE ships SET manufacturer_id = :bad WHERE id = :id"),
                            {"bad": m.id + 999999, "id": ship.id})
        db_session.flush()
    except Exception:
        import pytest
        pytest.skip("DB enforces the manufacturer FK immediately - can't construct this bad state to test against")

    findings = referential_integrity_check(db_session)

    defects = [f for f in findings if f.result == "DEFECT" and f.subject == "ships.manufacturer_id"]
    assert len(defects) == 1


def test_duplicate_identifier_check_flags_duplicate_name_and_manufacturer(db_session):
    m = _make_manufacturer(db_session)
    db_session.add(Ship(name="Dupe Ship", manufacturer_id=m.id, status="purchasable", confidence="verified"))
    db_session.add(Ship(name="Dupe Ship", manufacturer_id=m.id, status="purchasable", confidence="verified"))
    db_session.flush()

    findings = duplicate_identifier_check(db_session)

    defects = [f for f in findings if f.result == "DEFECT"]
    assert len(defects) == 1
    assert "Dupe Ship" in defects[0].details


def test_duplicate_identifier_check_passes_same_name_different_manufacturer(db_session):
    m1 = _make_manufacturer(db_session, "Mfg One")
    m2 = _make_manufacturer(db_session, "Mfg Two")
    db_session.add(Ship(name="Shared Name", manufacturer_id=m1.id, status="purchasable", confidence="verified"))
    db_session.add(Ship(name="Shared Name", manufacturer_id=m2.id, status="purchasable", confidence="verified"))
    db_session.flush()

    findings = duplicate_identifier_check(db_session)

    assert all(f.result == "PASS" for f in findings)


def test_registry_sync_check_flags_db_ship_missing_from_registry(db_session, tmp_path):
    m = _make_manufacturer(db_session)
    db_session.add(Ship(name="Not In Registry", manufacturer_id=m.id, status="purchasable", confidence="verified"))
    db_session.flush()

    data_layer = tmp_path / "data-layer"
    data_layer.mkdir()
    (data_layer / "ship_registry.json").write_text(json.dumps([{"ship_name": "Some Other Ship"}]))

    findings = registry_sync_check(db_session, tmp_path)

    warnings = [f for f in findings if f.result == "WARNING" and f.subject == "db-not-in-registry"]
    assert len(warnings) == 1
    assert "Not In Registry" in warnings[0].details


def test_registry_sync_check_passes_when_names_match(db_session, tmp_path):
    m = _make_manufacturer(db_session)
    db_session.add(Ship(name="Matched Ship", manufacturer_id=m.id, status="purchasable", confidence="verified"))
    db_session.flush()

    data_layer = tmp_path / "data-layer"
    data_layer.mkdir()
    (data_layer / "ship_registry.json").write_text(json.dumps([{"ship_name": "Matched Ship"}]))

    findings = registry_sync_check(db_session, tmp_path)

    assert all(f.result == "PASS" for f in findings)
