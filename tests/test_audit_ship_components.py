"""Tests that the auditor actually catches real problems, not just that it
runs without crashing on clean data. A findings-only tool that never flags
anything real is worse than useless - it looks like a passing safety net."""

from audit_ship_components import audit_relational_integrity
from app.models import Component, ComponentType, TurretDetail, WeaponDetail


def test_auditor_flags_cross_category_detail_mismatch(db_session):
    """A component typed 'weapon' that (erroneously) has a turret_detail
    row instead of a weapon_detail row must be flagged DEFECT - this is
    exactly the kind of bug the TurretDetail-relationship regression could
    have let slip through silently."""
    weapon_type = db_session.query(ComponentType).filter_by(key="weapon").one()
    bad = Component(component_type_id=weapon_type.id, name="Mistyped Component", class_name="TEST_Mistyped")
    bad.turret_detail = TurretDetail(weapon_slots=1, slot_weapon_size=1, manned=False)
    db_session.add(bad)
    db_session.flush()

    findings = []
    audit_relational_integrity(db_session, findings)

    defects = [f for f in findings if f["severity"] == "DEFECT" and f["component_id"] == bad.id]
    assert defects, "auditor should have flagged the mistyped component as a DEFECT"
    assert any(f["category"] == "cross_category_detail" for f in defects)


def test_auditor_flags_missing_detail_row(db_session):
    weapon_type = db_session.query(ComponentType).filter_by(key="weapon").one()
    orphan = Component(component_type_id=weapon_type.id, name="No Detail Row", class_name="TEST_NoDetail")
    db_session.add(orphan)
    db_session.flush()

    findings = []
    audit_relational_integrity(db_session, findings)

    defects = [f for f in findings if f["severity"] == "DEFECT" and f["component_id"] == orphan.id]
    assert any(f["category"] == "missing_detail_row" for f in defects)


def test_auditor_does_not_flag_a_well_formed_component(db_session):
    weapon_type = db_session.query(ComponentType).filter_by(key="weapon").one()
    good = Component(
        component_type_id=weapon_type.id,
        name="Well-formed Weapon",
        class_name="TEST_WellFormed",
        confidence="high",
    )
    good.weapon_detail = WeaponDetail(damage_type="energy")
    db_session.add(good)
    db_session.flush()

    findings = []
    audit_relational_integrity(db_session, findings)

    defects = [f for f in findings if f["severity"] == "DEFECT" and f.get("component_id") == good.id]
    assert defects == [], f"well-formed component should not be flagged, got: {defects}"
