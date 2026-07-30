"""
Tests for checks/network_checks.py.

external_reachability_check is tested here with a mocked `fetch` callable
only - it must NOT make a real request to api.star-citizen.wiki this
session (see checks/network_checks.py's module docstring: WebFetch failed
against that exact host three times tonight, and the no-workaround rule
applies regardless of fetching method). dependency_vulnerability_check IS
exercised for real against requirements.txt, since it talks to PyPI's
advisory service, not the blocked host.
"""

from pathlib import Path

from checks.network_checks import dependency_vulnerability_check, external_reachability_check


def test_dependency_vulnerability_check_runs_for_real_against_requirements(tmp_path):
    # A minimal, syntactically valid requirements file is enough to prove
    # pip-audit actually runs end-to-end in this environment - not
    # asserting on a specific vulnerability count, since that's a moving
    # target (today's clean package could get a CVE tomorrow).
    (tmp_path / "requirements.txt").write_text("idna==3.7\n")

    findings = dependency_vulnerability_check(tmp_path)

    assert len(findings) >= 1
    assert all(f.result in ("PASS", "DEFECT", "WARNING") for f in findings)
    # Confirm it didn't silently no-op.
    assert any(f.check_name == "dependency_vulnerability" for f in findings)


def test_dependency_vulnerability_check_limitation_when_no_requirements_file(tmp_path):
    findings = dependency_vulnerability_check(tmp_path)
    assert len(findings) == 1
    assert findings[0].result == "LIMITATION"


def test_external_reachability_check_passes_on_expected_shape():
    def fake_fetch(url):
        return 200, '{"data": {"uuid": "abc", "name": "Arrow"}}'

    findings = external_reachability_check(Path("."), fetch=fake_fetch)

    assert len(findings) == 1
    assert findings[0].result == "PASS"


def test_external_reachability_check_flags_missing_data_key():
    def fake_fetch(url):
        return 200, '{"uuid": "abc", "name": "Arrow"}'  # no top-level "data"

    findings = external_reachability_check(Path("."), fetch=fake_fetch)

    assert len(findings) == 1
    assert findings[0].result == "DEFECT"
    assert "data" in findings[0].details


def test_external_reachability_check_flags_non_json_response():
    def fake_fetch(url):
        return 200, "<html>not json</html>"

    findings = external_reachability_check(Path("."), fetch=fake_fetch)

    assert findings[0].result == "DEFECT"


def test_external_reachability_check_warns_on_bad_status():
    def fake_fetch(url):
        return 503, ""

    findings = external_reachability_check(Path("."), fetch=fake_fetch)

    assert findings[0].result == "WARNING"


def test_external_reachability_check_warns_on_request_exception():
    def fake_fetch(url):
        raise ConnectionError("no route to host")

    findings = external_reachability_check(Path("."), fetch=fake_fetch)

    assert findings[0].result == "WARNING"
