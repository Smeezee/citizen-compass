"""
Checkers that need outbound network access - dependency-vulnerability
scanning (PyPI's advisory feed via pip-audit) and external-source
reachability (confirming a third-party API this project depends on for
data pulls still responds with the shape the importer expects).

Environment split, confirmed this session (2026-07-30, see
LATEST_HANDOFF.md):

  - dependency_vulnerability_check hits PyPI's own advisory service via
    `pip-audit`, a different host entirely from the one that's actually
    blocked - this one has been run for real in the cloud sandbox tonight
    (see the run log this ships with).

  - external_reachability_check specifically targets
    api.star-citizen.wiki, the exact host WebFetch failed against three
    times tonight with a PROVENANCE_REQUIRED timeout (unanswered
    permission prompt in an unattended session) trying to source
    Aquila/Gladius hardpoint data. Per this session's explicit rule -
    once WebFetch fails on a target, curl/requests workarounds are
    prohibited, and that applies regardless of the fetching method - this
    checker's *code* is written and unit-tested against a mocked
    response, but it has deliberately NOT been executed against the real
    api.star-citizen.wiki host this session. Run it for real once you
    have a live session that can either get a WebFetch approval for that
    host, or run it in an environment this rule doesn't apply to.
"""

import json
import subprocess
from pathlib import Path

from checks.framework import Finding


def dependency_vulnerability_check(repo_root: Path) -> list[Finding]:
    """Run `pip-audit` against requirements.txt (and requirements-dev.txt
    if present) and surface any known CVE. Requires network access to
    PyPI's advisory database and `pip-audit` installed - returns
    LIMITATION if either isn't available rather than a false DEFECT."""
    findings = []
    req_files = [f for f in ("requirements.txt", "requirements-dev.txt") if (repo_root / f).exists()]
    if not req_files:
        return [Finding("dependency_vulnerability", None, "LIMITATION", "no requirements*.txt found")]

    for req_file in req_files:
        try:
            result = subprocess.run(
                ["pip-audit", "-r", str(repo_root / req_file), "--format", "json"],
                capture_output=True, text=True, timeout=120,
            )
        except FileNotFoundError:
            findings.append(Finding("dependency_vulnerability", req_file, "LIMITATION", "pip-audit not installed in this environment"))
            continue
        except subprocess.TimeoutExpired:
            findings.append(Finding("dependency_vulnerability", req_file, "WARNING", "pip-audit timed out after 120s (network issue?)"))
            continue
        except Exception as e:
            findings.append(Finding("dependency_vulnerability", req_file, "WARNING", f"could not run pip-audit: {e}"))
            continue

        try:
            report = json.loads(result.stdout)
        except Exception:
            # pip-audit exits non-zero on findings, but always documents its
            # output shape as JSON when --format json is passed; a parse
            # failure here means something else went wrong (bad requirements
            # line, no network, etc.) - treat as a review-worthy WARNING,
            # not a silent skip.
            findings.append(
                Finding("dependency_vulnerability", req_file, "WARNING",
                        f"pip-audit did not return parseable JSON (exit {result.returncode}): "
                        f"{(result.stdout + result.stderr).strip()[:1000]}")
            )
            continue

        dependencies = report.get("dependencies", report if isinstance(report, list) else [])
        vulnerable = [d for d in dependencies if d.get("vulns")]
        if vulnerable:
            for dep in vulnerable:
                vuln_ids = [v.get("id") for v in dep.get("vulns", [])]
                findings.append(
                    Finding("dependency_vulnerability", f"{req_file}:{dep.get('name')}", "DEFECT",
                            f"{dep.get('name')}=={dep.get('version')} has known advisories: {vuln_ids}")
                )
        else:
            findings.append(Finding("dependency_vulnerability", req_file, "PASS", f"{len(dependencies)} package(s) scanned, no known advisories"))

    return findings


def external_reachability_check(repo_root: Path, url: str = "https://api.star-citizen.wiki/api/vehicles/anvl-arrow",
                                 fetch=None) -> list[Finding]:
    """Confirm the external API this project's importer pulls from is
    reachable and still returns the shape the importer expects (a JSON
    object with a top-level 'data' key, matching arrow_api_raw.json's
    actual structure). `fetch` is injectable for testing (defaults to a
    real `requests.get` call) - see tests/test_network_checks.py, which
    exercises this with a mocked fetch rather than a live call, since this
    module must not be executed against the real host this session (see
    the module docstring)."""
    if fetch is None:
        import requests

        def fetch(u):
            resp = requests.get(u, timeout=10)
            return resp.status_code, resp.text

    try:
        status_code, body = fetch(url)
    except Exception as e:
        return [Finding("external_reachability", url, "WARNING", f"request failed: {e!r} - could be transient, or the source may be down/changed")]

    if status_code != 200:
        return [Finding("external_reachability", url, "WARNING", f"unexpected HTTP status {status_code}")]

    try:
        parsed = json.loads(body)
    except Exception as e:
        return [Finding("external_reachability", url, "DEFECT", f"response is not valid JSON: {e} - importer would fail on this")]

    if not isinstance(parsed, dict) or "data" not in parsed:
        return [Finding("external_reachability", url, "DEFECT",
                         "response no longer has the expected top-level 'data' key (see arrow_api_raw.json for the shape "
                         "the importer expects) - this is exactly the kind of upstream shape change that should surface "
                         "here instead of as a silent importer failure")]

    return [Finding("external_reachability", url, "PASS", "reachable, HTTP 200, response has the expected 'data' shape")]


CHECKERS = [
    ("dependency_vulnerability", dependency_vulnerability_check),
]
# external_reachability_check is deliberately NOT in CHECKERS yet - it has
# code and tests (mocked) but has never been run against the real host
# this session, per the WebFetch-failure rule in the module docstring.
# Add it to CHECKERS once it's been run for real at least once (from a
# session/environment where that's permitted) and confirmed to behave.
