#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_verify_document_checks.py - rule 12 proof for the seven document checks.

RULE16: UNPROVEN - it imports the seven checkers and asks those functions about
repositories this file planted, so a checker whose idea of "a path that exists"
or "a state document" is wrong is wrong on both sides of the comparison. The
INPUT is independent and that is the point: every planted defect must be caught
and every clean fixture must stay quiet. Rule 12 and rule 16 are different axes,
and a checker cannot be an independent source of truth about itself.

WHY THIS FILE EXISTS. Architecture's order of 2026-09-08 ends with the
requirement in plain words: "Each checker gets a case that makes it fire - a
document naming a path you delete, a FINDING with its status line removed, a
state file made older than its sibling. A checker nobody has seen go red is a
checker nobody will believe when it does."

So each of the seven gets BOTH halves, because a checker with a false negative is
worse than no checker at all - it converts "we looked" into "we are fine":

    MUST FIRE   planted input that the check is supposed to catch
    MUST NOT    clean input, and the near-misses the scope rules exist to
                exclude - a bare filename, prose that contains a slash, an
                exempt namespace

NOTHING IS PLANTED IN THE REAL REPOSITORY. Every checker takes repo_root as a
parameter, so each case builds a throwaway tree under tempfile and hands that
over. This file never writes inside citizen-compass.

--self-test inverts every expectation and MUST exit 1. If it exits 0 the harness
below has stopped asserting anything, which is the exact failure a self-test
exists to rule out.

Rule 15: every open states its encoding.

Run: python checks/_verify_document_checks.py
     python checks/_verify_document_checks.py --self-test
"""

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from checks.file_checks import (  # noqa: E402
    derived_number_freshness_check,
    finding_resolution_marker_check,
    named_thing_exists_check,
    published_patch_currency_check,
    skill_mirror_check,
    state_document_agreement_check,
    sweep_runtime_drift_check,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# --- fixture plumbing --------------------------------------------------------

def write(root: Path, rel: str, text: str, mtime: float | None = None) -> Path:
    """Rule 15: the encoding is stated even in a throwaway fixture. One of the
    four pipeline breakages this project has had was in a diagnostic script."""
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    if mtime is not None:
        os.utime(path, (mtime, mtime))
    return path


def defects(findings) -> list:
    return [f for f in findings if f.result == "DEFECT"]


def results(findings) -> set:
    return {f.result for f in findings}


# --- 1. state_document_agreement ---------------------------------------------

def case_state_two_files_no_pointer(root: Path):
    """Two files claiming to be project state and the older names nothing."""
    write(root, "docs/CURRENT-STATE.md", "the real one\n", mtime=2_000_000_000)
    write(root, "CURRENT-STATE.md", "a note about which URL is which\n",
          mtime=1_000_000_000)
    return state_document_agreement_check(root)


def case_state_pointer_at_missing_file(root: Path):
    """The pointer outlived the file."""
    write(root, "docs/CURRENT-STATE.md", "the real one\n")
    write(root, "CLAUDE.md", "Start by reading `archive/CURRENT-STATE.md` first.\n")
    return state_document_agreement_check(root)


def case_state_onboarding_names_the_older(root: Path):
    """The 2026-09-07 incident exactly: onboarding names the stale sibling."""
    write(root, "docs/CURRENT-STATE.md", "the real one\n", mtime=2_000_000_000)
    write(root, "CURRENT-STATE.md", "see `docs/CURRENT-STATE.md`\n",
          mtime=1_000_000_000)
    write(root, "CLAUDE.md", "Every session starts at `CURRENT-STATE.md`.\n")
    return state_document_agreement_check(root)


def case_state_clean(root: Path):
    write(root, "docs/CURRENT-STATE.md", "the only one\n")
    write(root, "CLAUDE.md", "Start at `docs/CURRENT-STATE.md`.\n")
    return state_document_agreement_check(root)


def case_state_sibling_that_does_point(root: Path):
    """Two files is not the defect. A sibling with no pointer is."""
    write(root, "docs/CURRENT-STATE.md", "the real one\n", mtime=2_000_000_000)
    write(root, "CURRENT-STATE.md",
          "AUTHORITATIVE: `docs/CURRENT-STATE.md`. This note covers URLs only.\n",
          mtime=1_000_000_000)
    write(root, "CLAUDE.md", "Start at `docs/CURRENT-STATE.md`.\n")
    return state_document_agreement_check(root)


# --- 2. finding_resolution_marker --------------------------------------------

IN_SCOPE = "docs/FINDING_planted-2098-01-01.md"
BACKLOG = "docs/FINDING_ancient-2020-01-01.md"


def case_finding_no_status_line(root: Path):
    write(root, IN_SCOPE, "# FINDING\n\nSomething, on 2098-01-01.\n")
    return finding_resolution_marker_check(root)


def case_finding_no_date(root: Path):
    write(root, IN_SCOPE, "# FINDING\n\nStatus: OPEN\n\nNo date anywhere.\n")
    return finding_resolution_marker_check(root)


def case_finding_clean(root: Path):
    write(root, IN_SCOPE, "# FINDING\n\nStatus: CLOSED\n\nFixed 2098-01-02.\n")
    return finding_resolution_marker_check(root)


def case_finding_backlog_is_not_a_defect(root: Path):
    """A document that predates the rule is a backlog line, never a DEFECT.
    This is the case that keeps the checker off the wallpaper."""
    write(root, BACKLOG, "# FINDING\n\nSomething, 2020-01-01, no marker.\n")
    return finding_resolution_marker_check(root)


def case_finding_bold_marker_counts(root: Path):
    """The project writes **Status:** OPEN as often as Status: OPEN."""
    write(root, IN_SCOPE, "# FINDING\n\n**Status:** WITHDRAWN\n\nOn 2098-01-03.\n")
    return finding_resolution_marker_check(root)


# --- 3. derived_number_freshness ---------------------------------------------

GEN_SRC = 'SNAPSHOT = "SNAP1"\n'
SNAP = "data-layer/external-sources/scunpacked-data/snapshots/SNAP1"


def _derived_fixture(root: Path, ships: str, output: str) -> None:
    write(root, "build_loadout_data.py", GEN_SRC)
    write(root, f"{SNAP}/ships.json", ships)
    write(root, f"{SNAP}/ship-items.json", '{"items": 1}\n')
    write(root, "data-layer/ship_resolution.json", '{"resolution": 1}\n')
    write(root, "testing/_src/loadout_data.gen.js", output)


def case_derived_input_moved_output_did_not(root: Path):
    """The LAST_VERIFIED_PATCH = "4.9" shape, reproduced."""
    _derived_fixture(root, '{"ships": 1}\n', "const A=1;\n")
    derived_number_freshness_check(root)          # records the baseline
    _derived_fixture(root, '{"ships": 2}\n', "const A=1;\n")   # input moved only
    return derived_number_freshness_check(root)


def case_derived_both_moved(root: Path):
    _derived_fixture(root, '{"ships": 1}\n', "const A=1;\n")
    derived_number_freshness_check(root)
    _derived_fixture(root, '{"ships": 2}\n', "const A=2;\n")
    return derived_number_freshness_check(root)


def case_derived_nothing_moved(root: Path):
    _derived_fixture(root, '{"ships": 1}\n', "const A=1;\n")
    derived_number_freshness_check(root)
    return derived_number_freshness_check(root)


def case_derived_output_missing(root: Path):
    write(root, "build_loadout_data.py", GEN_SRC)
    write(root, f"{SNAP}/ships.json", '{"ships": 1}\n')
    write(root, f"{SNAP}/ship-items.json", '{"items": 1}\n')
    write(root, "data-layer/ship_resolution.json", '{"resolution": 1}\n')
    return derived_number_freshness_check(root)


def case_derived_input_missing_is_not_a_pass(root: Path):
    """An absent input must be NOT PERFORMED, never a quiet pass."""
    write(root, "build_loadout_data.py", GEN_SRC)
    write(root, "testing/_src/loadout_data.gen.js", "const A=1;\n")
    write(root, "data-layer/ship_resolution.json", '{"resolution": 1}\n')
    return derived_number_freshness_check(root)


# --- 4. published_patch_currency ---------------------------------------------

MANIFEST = "data-layer/external-source-manifests/20990101T000000Z/01_x_manifest.json"


def _page(patch: str) -> str:
    return f'<p class="patch-info">Patch: Alpha {patch} &quot;X&quot; (LIVE)</p>\n'


def _manifest(subject: str) -> str:
    return json.dumps({"git_metadata_captured_before_stripping":
                       {"git_head_subject": subject}})


def case_patch_page_behind(root: Path):
    write(root, "static/preview.html", _page("4.9.0"))
    write(root, MANIFEST, _manifest("4.10.0-LIVE.12519617"))
    return published_patch_currency_check(root)


def case_patch_page_current(root: Path):
    write(root, "static/preview.html", _page("4.10.0"))
    write(root, MANIFEST, _manifest("4.10.0-LIVE.12519617"))
    return published_patch_currency_check(root)


def case_patch_no_manifest_is_not_a_pass(root: Path):
    write(root, "static/preview.html", _page("4.10.0"))
    return published_patch_currency_check(root)


def case_patch_no_line_on_page(root: Path):
    write(root, "static/preview.html", "<p>no patch stated at all</p>\n")
    write(root, MANIFEST, _manifest("4.10.0-LIVE.12519617"))
    return published_patch_currency_check(root)


# --- 5. sweep_runtime_drift --------------------------------------------------

def _receipt(root: Path, at: str, seconds: float, timings=None, partial=False):
    write(root, "checks/.last_sweep.json", json.dumps({
        "at": at, "seconds": seconds, "passed": 124, "partial": partial,
        "failed": [], "not_run": [], "timings": timings or {}}))


def case_sweep_doubled(root: Path):
    _receipt(root, "2026-01-01T00:00:00", 100.0, {"a.py": 10.0})
    sweep_runtime_drift_check(root)
    _receipt(root, "2026-01-02T00:00:00", 1000.0, {"a.py": 910.0})
    return sweep_runtime_drift_check(root)


def case_sweep_steady(root: Path):
    _receipt(root, "2026-01-01T00:00:00", 1000.0, {"a.py": 10.0})
    sweep_runtime_drift_check(root)
    _receipt(root, "2026-01-02T00:00:00", 1050.0, {"a.py": 12.0})
    return sweep_runtime_drift_check(root)


def case_sweep_small_absolute_move_is_quiet(root: Path):
    """A fast sweep wobbling must never speak: 10s -> 20s is 100% and 10
    seconds. BOTH thresholds have to be crossed."""
    _receipt(root, "2026-01-01T00:00:00", 10.0)
    sweep_runtime_drift_check(root)
    _receipt(root, "2026-01-02T00:00:00", 20.0)
    return sweep_runtime_drift_check(root)


def case_sweep_partial_is_not_compared(root: Path):
    _receipt(root, "2026-01-01T00:00:00", 1000.0)
    sweep_runtime_drift_check(root)
    _receipt(root, "2026-01-02T00:00:00", 100.0, partial=True)
    return sweep_runtime_drift_check(root)


def case_sweep_first_receipt_is_not_a_pass(root: Path):
    _receipt(root, "2026-01-01T00:00:00", 1000.0)
    return sweep_runtime_drift_check(root)


# --- 6. named_thing_exists ---------------------------------------------------

def case_named_missing_path(root: Path):
    write(root, "checks/real.py", "x\n")
    write(root, "CLAUDE.md", "The tool is `checks/gone.py` and it runs nightly.\n")
    return named_thing_exists_check(root)


def case_named_clean(root: Path):
    write(root, "checks/real.py", "x\n")
    write(root, "CLAUDE.md", "The tool is `checks/real.py` and it runs nightly.\n")
    return named_thing_exists_check(root)


def case_named_bare_filename_is_not_a_path(root: Path):
    write(root, "checks/real.py", "x\n")
    write(root, "CLAUDE.md", "Run `build_deploy.py`, then check `.glb` output.\n")
    return named_thing_exists_check(root)


def case_named_prose_with_a_slash_is_not_a_path(root: Path):
    """`Freelancer_DUR/MAX/MIS` and `wheelFL/FR/BL/BR` are real strings out of
    this project's documents. A first segment that is not in the repo means it
    was never a repo-relative path."""
    write(root, "checks/real.py", "x\n")
    write(root, "CLAUDE.md", "The `Freelancer_DUR/MAX/MIS` set and `wheelFL/FR/BL/BR`.\n")
    return named_thing_exists_check(root)


def case_named_exempt_namespace(root: Path):
    write(root, "correspondence/README.md", "x\n")
    write(root, "CLAUDE.md", "Raised in `correspondence/open/build/moved-away.md`.\n")
    return named_thing_exists_check(root)


def case_named_glob_is_not_a_path(root: Path):
    write(root, "checks/real.py", "x\n")
    write(root, "CLAUDE.md", "Everything under `checks/_verify_*.py` is swept.\n")
    return named_thing_exists_check(root)


def case_named_archive_is_out_of_scope(root: Path):
    """History is allowed to name dead paths. The scope rule is what keeps this
    check off 773 archived handoffs."""
    write(root, "checks/real.py", "x\n")
    write(root, "docs/handoff_archive/old.md", "It was at `checks/long-gone.py`.\n")
    return named_thing_exists_check(root)


def case_named_demoted_state_and_boot_are_out_of_scope(root: Path):
    """docs/CURRENT-STATE.md was demoted to history on 2026-09-12 and BOOT.md is
    the state. History may name dead paths, and BOOT.md prints MISSING paths on
    purpose - neither is a present-state document for this check. The SAME dead
    path in CLAUDE.md still fires: see case_named_missing_path."""
    write(root, "checks/real.py", "x\n")
    write(root, "docs/CURRENT-STATE.md", "It was at `checks/long-gone.py`.\n")
    write(root, "CURRENT-STATE.md", "It was at `checks/long-gone.py`.\n")
    write(root, "BOOT.md", "    last build     MISSING - `checks/long-gone.py`\n")
    return named_thing_exists_check(root)


# --- the harness -------------------------------------------------------------

# Each case: (check name, label, function, expectation)
#   "fires"  - the planted defect MUST produce at least one DEFECT
#   "quiet"  - clean or near-miss input MUST produce no DEFECT
#   "not_performed" - the checker MUST say it could not look, rather than PASS
CASES = [
    ("state_document_agreement", "two state files, older names nothing",
     case_state_two_files_no_pointer, "fires"),
    ("state_document_agreement", "onboarding points at a file that is gone",
     case_state_pointer_at_missing_file, "fires"),
    ("state_document_agreement", "onboarding names the OLDER sibling",
     case_state_onboarding_names_the_older, "fires"),
    ("state_document_agreement", "one state file, pointed at correctly",
     case_state_clean, "quiet"),
    ("state_document_agreement", "two state files, the older DOES point",
     case_state_sibling_that_does_point, "quiet"),

    ("finding_resolution_marker", "in-scope finding with no status line",
     case_finding_no_status_line, "fires"),
    ("finding_resolution_marker", "in-scope finding with no date",
     case_finding_no_date, "fires"),
    ("finding_resolution_marker", "in-scope finding, marker and date present",
     case_finding_clean, "quiet"),
    ("finding_resolution_marker", "**Status:** bold form counts",
     case_finding_bold_marker_counts, "quiet"),
    ("finding_resolution_marker", "pre-cutoff backlog is never a DEFECT",
     case_finding_backlog_is_not_a_defect, "quiet"),

    ("derived_number_freshness", "inputs moved, derived artifact did not",
     case_derived_input_moved_output_did_not, "fires"),
    ("derived_number_freshness", "registered artifact not on disk",
     case_derived_output_missing, "fires"),
    ("derived_number_freshness", "inputs and artifact both moved",
     case_derived_both_moved, "quiet"),
    ("derived_number_freshness", "nothing moved",
     case_derived_nothing_moved, "quiet"),
    ("derived_number_freshness", "an absent input is NOT PERFORMED",
     case_derived_input_missing_is_not_a_pass, "not_performed"),

    ("published_patch_currency", "page states a patch behind the data",
     case_patch_page_behind, "fires"),
    ("published_patch_currency", "page states the current patch",
     case_patch_page_current, "quiet"),
    ("published_patch_currency", "no manifest is NOT PERFORMED, not a pass",
     case_patch_no_manifest_is_not_a_pass, "not_performed"),
    ("published_patch_currency", "no patch line on the page is reported",
     case_patch_no_line_on_page, "not_performed"),

    ("sweep_runtime_drift", "the sweep took ten times as long",
     case_sweep_doubled, "fires"),
    ("sweep_runtime_drift", "a 5% move says nothing",
     case_sweep_steady, "quiet"),
    ("sweep_runtime_drift", "10s to 20s is 100% and stays quiet",
     case_sweep_small_absolute_move_is_quiet, "quiet"),
    ("sweep_runtime_drift", "a partial sweep is recorded, not compared",
     case_sweep_partial_is_not_compared, "not_performed"),
    ("sweep_runtime_drift", "one receipt is NOT PERFORMED, not steady",
     case_sweep_first_receipt_is_not_a_pass, "not_performed"),

    ("named_thing_exists", "a present-state doc names a path that is gone",
     case_named_missing_path, "fires"),
    ("named_thing_exists", "the path it names exists",
     case_named_clean, "quiet"),
    ("named_thing_exists", "a bare filename is shorthand, not a path",
     case_named_bare_filename_is_not_a_path, "quiet"),
    ("named_thing_exists", "prose containing a slash is not a path",
     case_named_prose_with_a_slash_is_not_a_path, "quiet"),
    ("named_thing_exists", "an exempt namespace is not resolved here",
     case_named_exempt_namespace, "quiet"),
    ("named_thing_exists", "a glob names a shape, not a file",
     case_named_glob_is_not_a_path, "quiet"),
    ("named_thing_exists", "the archive is out of scope",
     case_named_archive_is_out_of_scope, "quiet"),
    ("named_thing_exists", "demoted CURRENT-STATE and BOOT.md are out of scope",
     case_named_demoted_state_and_boot_are_out_of_scope, "quiet"),
]


# --- 7. skill_mirror (ordered 2026-09-13) --------------------------------------

def case_mirror_differing_byte(root: Path):
    write(root, "skills/aar-loop/SKILL.md", "# AAR\nstep one\n")
    write(root, ".claude/skills/aar-loop/SKILL.md", "# AAR\nstep One\n")
    return skill_mirror_check(root)


def case_mirror_skill_only_in_claude(root: Path):
    write(root, "skills/aar-loop/SKILL.md", "# AAR\n")
    write(root, ".claude/skills/aar-loop/SKILL.md", "# AAR\n")
    write(root, ".claude/skills/stray/SKILL.md", "# a skill nobody filed\n")
    return skill_mirror_check(root)


def case_mirror_skill_only_in_skills(root: Path):
    write(root, "skills/aar-loop/SKILL.md", "# AAR\n")
    write(root, "skills/new-one/SKILL.md", "# not mirrored yet\n")
    write(root, ".claude/skills/aar-loop/SKILL.md", "# AAR\n")
    return skill_mirror_check(root)


def case_mirror_case_is_not_folded(root: Path):
    """Rule 17: SKILL.md and skill.md are two names, even on this disk."""
    write(root, "skills/aar-loop/SKILL.md", "# AAR\n")
    write(root, ".claude/skills/aar-loop/skill.md", "# AAR\n")
    return skill_mirror_check(root)


def case_mirror_identical_with_top_level_readme(root: Path):
    """Today's real shape: one skill, identical, and a README for people only."""
    write(root, "skills/README.md", "How the skill pack works.\n")
    write(root, "skills/aar-loop/SKILL.md", "# AAR\n")
    write(root, ".claude/skills/aar-loop/SKILL.md", "# AAR\n")
    return skill_mirror_check(root)


def case_mirror_absent_is_not_a_pass(root: Path):
    write(root, "skills/aar-loop/SKILL.md", "# AAR\n")
    return skill_mirror_check(root)


def case_mirror_no_source_is_not_a_pass(root: Path):
    write(root, ".claude/skills/aar-loop/SKILL.md", "# AAR\n")
    return skill_mirror_check(root)


CASES += [
    ("skill_mirror", "one byte differs between the two copies",
     case_mirror_differing_byte, "fires"),
    ("skill_mirror", "a skill only in .claude/skills/",
     case_mirror_skill_only_in_claude, "fires"),
    ("skill_mirror", "a skill only in skills/",
     case_mirror_skill_only_in_skills, "fires"),
    ("skill_mirror", "SKILL.md vs skill.md is not folded",
     case_mirror_case_is_not_folded, "fires"),
    ("skill_mirror", "identical, plus a top-level README",
     case_mirror_identical_with_top_level_readme, "quiet"),
    ("skill_mirror", "no .claude/skills/ is NOT PERFORMED",
     case_mirror_absent_is_not_a_pass, "not_performed"),
    ("skill_mirror", "no skills/ is NOT PERFORMED",
     case_mirror_no_source_is_not_a_pass, "not_performed"),
]

# The drift check's WARNING is its fire. Everything else fires as a DEFECT.
FIRES_AS_WARNING = {"sweep_runtime_drift"}


def judge(check: str, expectation: str, findings) -> tuple[bool, str]:
    got = results(findings)
    if expectation == "fires":
        want = "WARNING" if check in FIRES_AS_WARNING else "DEFECT"
        return (want in got), f"expected a {want}, got {sorted(got) or 'nothing'}"
    if expectation == "quiet":
        loud = [f for f in findings
                if f.result in ("DEFECT", "WARNING")
                and (check not in FIRES_AS_WARNING or f.result != "PASS")]
        loud = [f for f in loud if f.result == ("WARNING" if check in FIRES_AS_WARNING else "DEFECT")]
        return (not loud), ("expected silence, got: "
                            + "; ".join(f.details[:110] for f in loud))
    if expectation == "not_performed":
        return ("LIMITATION" in got or "WARNING" in got) and "DEFECT" not in got, (
            f"expected NOT PERFORMED (LIMITATION/WARNING) and no DEFECT, got "
            f"{sorted(got) or 'nothing'}")
    raise AssertionError(f"unknown expectation {expectation!r}")


def main() -> int:
    inverted = "--self-test" in sys.argv
    print("THE SEVEN DOCUMENT CHECKS - rule 12 proof, both directions")
    if inverted:
        print("SELF-TEST: every expectation below is INVERTED. This run must "
              "exit 1.")
    print("=" * 74)

    failures = []
    by_check: dict[str, list[bool]] = {}
    for check, label, fn, expectation in CASES:
        tmp = Path(tempfile.mkdtemp(prefix="ccdoc_"))
        try:
            findings = fn(tmp)
            ok, why = judge(check, expectation, findings)
        except Exception as e:                      # noqa: BLE001 - fail closed
            ok, why = False, f"the case CRASHED: {type(e).__name__}: {e}"
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

        if inverted:
            ok = not ok
        by_check.setdefault(check, []).append(ok)
        mark = "ok  " if ok else "FAIL"
        print(f"  [{mark}] {check:26s} {expectation:14s} {label}")
        if not ok:
            failures.append(f"{check} / {label}: {why}")

    print("=" * 74)
    for check, oks in sorted(by_check.items()):
        print(f"  {check:28s} {sum(oks)}/{len(oks)} cases")

    if failures:
        print(f"\n{len(failures)} FAILURE(S):")
        for f in failures:
            print(f"  - {f}")
        if inverted:
            print("\nSELF-TEST PASSED: the inverted run failed, as it must. The "
                  "harness is asserting something.")
            return 1
        return 1

    if inverted:
        print("\nSELF-TEST FAILED: every expectation was inverted and the run "
              "still passed. This harness is asserting NOTHING - the exact "
              "silent-success shape rule 12 is about.")
        return 1

    print(f"\nALL {len(CASES)} CASES PASS. Each of the seven has been seen to fire "
          f"on planted input and to stay silent on clean input, including the "
          f"near-misses its scope rules exist to exclude.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
