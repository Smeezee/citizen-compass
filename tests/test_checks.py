"""
Tests for the checks/ pluggable checker framework and file-based checkers.

Per the same principle as tests/test_audit_ship_components.py: a
findings-only tool that never finds anything real is worse than useless.
These tests build small synthetic repo trees under tmp_path and confirm
each checker actually flags the problem it claims to catch, and does NOT
flag well-formed input.
"""

import json
import subprocess
from pathlib import Path

import pytest

from checks.file_checks import (
    broken_asset_references_check,
    naming_convention_typo_check,
    orphaned_test_fixture_check,
    placeholder_null_density_check,
    secrets_in_repo_check,
)
from checks.framework import Finding, RESULTS


def test_finding_rejects_invalid_result():
    with pytest.raises(AssertionError):
        Finding("some_check", None, "NOT_A_REAL_RESULT", "details")


def test_finding_accepts_all_taxonomy_values():
    for result in RESULTS:
        Finding("some_check", None, result, "details")


def _write_hardpoints(ships_dir: Path, folder_name: str, ship_slug: str, hardpoints=None):
    ship_dir = ships_dir / folder_name
    ship_dir.mkdir(parents=True)
    (ship_dir / "hardpoints.json").write_text(
        json.dumps({"ship_name": folder_name, "ship_slug": ship_slug, "hardpoints": hardpoints or []})
    )
    return ship_dir


def test_naming_convention_typo_check_flags_mismatched_slug(tmp_path):
    ships_dir = tmp_path / "tests" / "testing-site" / "ships"
    _write_hardpoints(ships_dir, "cutlass-black", "cuttlass_black")  # the real bug this caught

    findings = naming_convention_typo_check(tmp_path)

    defects = [f for f in findings if f.result == "DEFECT"]
    assert len(defects) == 1
    assert "cuttlass_black" in defects[0].details
    assert defects[0].subject == "cutlass-black"


def test_naming_convention_typo_check_passes_matching_slug(tmp_path):
    ships_dir = tmp_path / "tests" / "testing-site" / "ships"
    _write_hardpoints(ships_dir, "arrow", "arrow")

    findings = naming_convention_typo_check(tmp_path)

    assert all(f.result == "PASS" for f in findings)


def test_placeholder_null_density_check_flags_generic_label(tmp_path):
    ships_dir = tmp_path / "tests" / "testing-site" / "ships"
    _write_hardpoints(
        ships_dir,
        "cutlass-black",
        "cutlass-black",
        hardpoints=[{"name": "hardpoint_missile_rack_missiles", "type": "missile_rack", "label": "Missiles"}],
    )

    findings = placeholder_null_density_check(tmp_path)

    warnings = [f for f in findings if f.result == "WARNING"]
    assert len(warnings) == 1
    assert "hardpoint_missile_rack_missiles" in warnings[0].details


def test_placeholder_null_density_check_passes_specific_label(tmp_path):
    ships_dir = tmp_path / "tests" / "testing-site" / "ships"
    _write_hardpoints(
        ships_dir,
        "arrow",
        "arrow",
        hardpoints=[{"name": "hardpoint_weapon_gun_s2_left", "type": "weapon_gun", "label": "S2  Left"}],
    )

    findings = placeholder_null_density_check(tmp_path)

    assert all(f.result == "PASS" for f in findings)


def test_broken_asset_references_check_flags_missing_file(tmp_path):
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    (static_dir / "index.html").write_text('<img src="/static/logos/does-not-exist.png">')

    findings = broken_asset_references_check(tmp_path)

    defects = [f for f in findings if f.result == "DEFECT"]
    assert len(defects) == 1
    assert "does-not-exist.png" in defects[0].details


def test_broken_asset_references_check_passes_existing_file(tmp_path):
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    (static_dir / "logo.png").write_bytes(b"\x89PNG")
    (static_dir / "index.html").write_text('<img src="/static/logo.png">')

    findings = broken_asset_references_check(tmp_path)

    assert all(f.result == "PASS" for f in findings)


def test_orphaned_test_fixture_check_flags_folder_without_registry_entry(tmp_path):
    ships_dir = tmp_path / "tests" / "testing-site" / "ships"
    ships_dir.mkdir(parents=True)
    (ships_dir / "some-new-ship").mkdir()
    data_dir = tmp_path / "tests" / "testing-site" / "data"
    data_dir.mkdir(parents=True)
    (data_dir / "ships-master.json").write_text(json.dumps([{"slug": "arrow"}]))

    findings = orphaned_test_fixture_check(tmp_path)

    warnings = [f for f in findings if f.result == "WARNING"]
    assert len(warnings) == 1
    assert "some-new-ship" in warnings[0].details


def test_orphaned_test_fixture_check_passes_when_all_match(tmp_path):
    ships_dir = tmp_path / "tests" / "testing-site" / "ships"
    ships_dir.mkdir(parents=True)
    (ships_dir / "arrow").mkdir()
    data_dir = tmp_path / "tests" / "testing-site" / "data"
    data_dir.mkdir(parents=True)
    (data_dir / "ships-master.json").write_text(json.dumps([{"slug": "arrow"}]))

    findings = orphaned_test_fixture_check(tmp_path)

    assert all(f.result == "PASS" for f in findings)


def test_secrets_in_repo_check_flags_tracked_env_file(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / ".env").write_text("DATABASE_URL=postgresql://x\n")
    subprocess.run(["git", "add", ".env"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "test"], cwd=tmp_path, check=True)

    findings = secrets_in_repo_check(tmp_path)

    defects = [f for f in findings if f.result == "DEFECT"]
    assert len(defects) == 1
    assert defects[0].subject == ".env"


def test_secrets_in_repo_check_passes_when_env_not_tracked(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("hello\n")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "test"], cwd=tmp_path, check=True)

    findings = secrets_in_repo_check(tmp_path)

    env_findings = [f for f in findings if f.subject == ".env"]
    assert len(env_findings) == 1
    assert env_findings[0].result == "PASS"
