"""
Node-based checkers: the sc_export.js round-trip and mutation harnesses.

WHY THESE ARE HERE RATHER THAN IN A CI FILE

This repo has no GitHub Actions and no .github/workflows directory. What it
actually has is this framework plus run_checks_scheduled.ps1, so "put both
harnesses in CI" means registering them here, in the `file` group - these two
need stdlib, git and `node`, no database and no network.

WHY THE EXIT CODE IS NOT TRUSTED FOR THE MUTATION SUITE

Hard rule 12. `mutate.js` exits 0 whether it catches 20 mutations, 19, or 3 -
it reports the count on stdout and returns success regardless. Confirmed by
running it: 19/20 with a survivor still exits 0. So a checker that only asked
"did it exit cleanly?" would report PASS while the suite silently degraded,
which is this project's SILENT SUCCESS shape exactly. The count and the
survivor's identity are therefore parsed out of stdout and compared by name.

WHY 19/20 IS THE PASSING VALUE, AND 20/20 IS A DEFECT

M18 (`sort actions case-insensitively`) is expected to survive. Neither real
fixture contains a pair of action names that sorts differently under ASCII
versus case-insensitive ordering, so the evidence cannot decide it, and
roundtrip.js asserts that ambiguity deliberately rather than guessing. If the
count ever reaches 20/20, something has changed about the check rather than
improved about the code - so it is reported as a DEFECT in both directions,
not just when the number goes down.
"""

import shutil
import subprocess
from pathlib import Path

from checks.framework import Finding

# The exact expectations, stated once. See the module docstring for why 19/20
# rather than 20/20 is the correct passing value.
EXPECTED_CAUGHT = 19
EXPECTED_TOTAL = 20
EXPECTED_SURVIVOR = "M18"

# mutate.js spawns a full roundtrip.js run per mutation - 20 child node
# processes - so it is slow by construction rather than by accident.
ROUNDTRIP_TIMEOUT = 300
MUTATE_TIMEOUT = 1800


def _node_missing(check_name: str, repo_root: Path) -> Finding | None:
    """Report an unrunnable check as NOT PERFORMED rather than as a pass.

    Rule 11: if a check cannot be performed, say so. A missing `node` or a
    missing node_modules is a LIMITATION - an honest gap - and must never be
    allowed to look like a green run.
    """
    if shutil.which("node") is None:
        return Finding(check_name, None, "LIMITATION",
                       "node is not on PATH, so this harness could not be run. "
                       "NOT PERFORMED - this is not a pass.")
    if not (repo_root / "testing" / "_src" / "node_modules" / "@xmldom").is_dir():
        return Finding(check_name, None, "LIMITATION",
                       "testing/_src/node_modules/@xmldom is absent, so the harness cannot "
                       "import its parser. Run `npm install` inside testing/_src. "
                       "NOT PERFORMED - this is not a pass.")
    return None


def _run(script: str, repo_root: Path, timeout: int):
    """Run a harness from the repo root and hand back its result.

    encoding is stated explicitly per rule 15 - the harnesses print real Star
    Citizen action names, and the Windows default of cp1252 cannot represent
    all of them.
    """
    return subprocess.run(
        ["node", str(Path("testing") / "_src" / script)],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def export_roundtrip_check(repo_root: Path) -> list[Finding]:
    """The exporter must reproduce two files Star Citizen itself wrote, byte
    for byte, both as read and from shuffled input."""
    name = "export_roundtrip"
    blocked = _node_missing(name, repo_root)
    if blocked:
        return [blocked]

    script = repo_root / "testing" / "_src" / "roundtrip.js"
    if not script.is_file():
        return [Finding(name, "testing/_src/roundtrip.js", "DEFECT",
                        "the round-trip harness is missing from the repo")]

    try:
        proc = _run("roundtrip.js", repo_root, ROUNDTRIP_TIMEOUT)
    except subprocess.TimeoutExpired:
        return [Finding(name, "testing/_src/roundtrip.js", "DEFECT",
                        f"did not finish within {ROUNDTRIP_TIMEOUT}s")]

    out = proc.stdout or ""
    # BOTH conditions, not either. A harness that crashed before printing
    # anything exits non-zero with no banner; one that was edited to always
    # print the banner would still fail on the exit code.
    if proc.returncode != 0 or "ALL CHECKS PASSED" not in out:
        fails = [ln.strip() for ln in out.splitlines() if ln.strip().startswith("FAIL")]
        detail = f"exit={proc.returncode}, banner={'present' if 'ALL CHECKS PASSED' in out else 'ABSENT'}"
        if fails:
            detail += "; " + "; ".join(fails[:5])
        if proc.stderr:
            detail += f"; stderr: {proc.stderr.strip()[:300]}"
        return [Finding(name, "testing/_src/roundtrip.js", "DEFECT", detail)]

    passes = out.count("PASS")
    return [Finding(name, "testing/_src/roundtrip.js", "PASS",
                    f"both real profiles reproduced byte for byte; {passes} checks passed")]


def export_mutation_check(repo_root: Path) -> list[Finding]:
    """The round-trip suite must actually be able to fail.

    Reports a DEFECT if the caught count is anything other than the expected
    19/20, INCLUDING a higher number - see the module docstring.
    """
    name = "export_mutation"
    blocked = _node_missing(name, repo_root)
    if blocked:
        return [blocked]

    script = repo_root / "testing" / "_src" / "mutate.js"
    if not script.is_file():
        return [Finding(name, "testing/_src/mutate.js", "DEFECT",
                        "the mutation harness is missing from the repo")]

    try:
        proc = _run("mutate.js", repo_root, MUTATE_TIMEOUT)
    except subprocess.TimeoutExpired:
        return [Finding(name, "testing/_src/mutate.js", "DEFECT",
                        f"did not finish within {MUTATE_TIMEOUT}s")]

    out = proc.stdout or ""
    label = f"expected {EXPECTED_CAUGHT}/{EXPECTED_TOTAL} with {EXPECTED_SURVIVOR} the sole survivor"

    # The count line is the whole point of running this, so its absence is a
    # DEFECT rather than something to shrug at - it means the suite did not
    # get far enough to report, and no conclusion can be drawn from that.
    caught = None
    total = None
    for line in out.splitlines():
        stripped = line.strip()
        if "mutations caught" in stripped:
            head = stripped.split(" mutations caught")[0]
            if "/" in head:
                left, right = head.split("/", 1)
                if left.strip().isdigit() and right.strip().isdigit():
                    caught, total = int(left.strip()), int(right.strip())
            break

    if caught is None:
        detail = f"could not find the 'N/M mutations caught' line in the output ({label})"
        if proc.stderr:
            detail += f"; stderr: {proc.stderr.strip()[:300]}"
        return [Finding(name, "testing/_src/mutate.js", "DEFECT", detail)]

    survivors = [ln.strip().split("SURVIVED", 1)[1].strip()
                 for ln in out.splitlines() if "SURVIVED" in ln]
    survivor_ids = [s.split()[0] for s in survivors if s.split()]

    if caught != EXPECTED_CAUGHT or total != EXPECTED_TOTAL:
        direction = "FEWER" if caught < EXPECTED_CAUGHT else "MORE"
        return [Finding(name, "testing/_src/mutate.js", "DEFECT",
                        f"{caught}/{total} mutations caught - {direction} than the {label}. "
                        f"survivors: {survivor_ids or 'none'}. "
                        "A higher count is also a defect: it means the deliberate "
                        "ambiguity about action sort order stopped being asserted.")]

    if survivor_ids != [EXPECTED_SURVIVOR]:
        return [Finding(name, "testing/_src/mutate.js", "DEFECT",
                        f"{caught}/{total} caught, but the survivor set is {survivor_ids} "
                        f"rather than ['{EXPECTED_SURVIVOR}'] ({label}). The count is right "
                        "and the identity is wrong, so a different check has gone blind.")]

    return [Finding(name, "testing/_src/mutate.js", "PASS",
                    f"{caught}/{total} mutations caught, {EXPECTED_SURVIVOR} the sole survivor "
                    "as expected - no real fixture distinguishes ASCII from case-insensitive "
                    "action sort, and roundtrip.js asserts that ambiguity deliberately")]


CHECKERS = [
    ("export_roundtrip", export_roundtrip_check),
    ("export_mutation", export_mutation_check),
]
