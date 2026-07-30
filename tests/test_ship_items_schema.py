"""Regression tests for real defects found while validating the Ship Items
schema + importer (2026-07-29/30 sessions), plus importer idempotency.

Precondition: target database has all migrations applied.
"""

import import_ship_components
from app.database import SessionLocal
from app.models import Component, ComponentType, TurretDetail


def test_component_verified_patch_relationship_resolves():
    """Regression test: Component.verified_patch was missing entirely on
    2026-07-30 (only the raw last_verified_patch FK column existed, no ORM
    relationship), which crashed the component API's serializers the first
    time they were actually run against real data. Guards against that
    relationship disappearing again."""
    session = SessionLocal()
    try:
        component = session.query(Component).first()
        assert component is not None, "expected at least one component row to exist"
        # Must not raise AttributeError, regardless of whether this
        # particular row has a patch set.
        _ = component.verified_patch
    finally:
        session.close()


def test_turret_detail_back_populates_to_component():
    """Regression test: TurretDetail was the one typed detail table missing
    its `component` back-reference (2026-07-29 session) - every other
    detail table had it. Caught only by actually running the importer
    end-to-end, not by a syntax/import check."""
    session = SessionLocal()
    try:
        turret_type = session.query(ComponentType).filter_by(key="turret").one()
        turret_component = (
            session.query(Component)
            .filter(Component.component_type_id == turret_type.id)
            .filter(Component.turret_detail.has())
            .first()
        )
        assert turret_component is not None, "expected at least one turret with a turret_detail row"
        detail = turret_component.turret_detail
        assert isinstance(detail, TurretDetail)
        assert detail.component is turret_component
    finally:
        session.close()


def _component_count() -> int:
    session = SessionLocal()
    try:
        return session.query(Component).count()
    finally:
        session.close()


def test_importer_is_idempotent_on_repeated_runs():
    """Run the real Arrow importer twice in a row against whatever DB the
    test env points at (scratch, per .env in this environment) and confirm
    the second run creates no new rows - matches the manual dry-run/real-
    run/re-run verification done in the terminal, but as an assertion that
    survives without a human reading log output.

    Note: run()'s return value is a process exit code (0/1), not a
    created/updated tuple - so this test asserts on actual row counts
    rather than the CLI's return value.
    """
    before = _component_count()

    exit_code_1 = import_ship_components.run(dry_run=False)
    after_first_run = _component_count()

    exit_code_2 = import_ship_components.run(dry_run=False)
    after_second_run = _component_count()

    assert exit_code_1 == 0
    assert exit_code_2 == 0
    assert after_first_run >= before, "first run should never remove rows"
    assert after_second_run == after_first_run, "second run must not create any new rows"
