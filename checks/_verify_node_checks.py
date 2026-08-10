"""
Rule 12 proof for the two node-based export checkers, in BOTH directions.

These two checkers are the only thing standing between "the exporter still
reproduces files the game wrote" and nobody noticing that it stopped. So they
are tested the hard way: every failure mode is fed to them deliberately and
must be reported, and the healthy case must NOT be reported.

The cases that matter most are the ones that look like success:

  * a harness that exits 0 but never printed its banner - the shape of
    scunpacked_com.py's main() returning None
  * a mutation suite reporting 20/20 instead of 19/20 - a number going UP,
    which reads as an improvement and is actually the deliberate ambiguity
    about action sort order having stopped being asserted
  * a mutation suite reporting the right COUNT with the wrong SURVIVOR - the
    arithmetic is fine and a different check has gone blind

Hermetic by construction: every case runs against a throwaway repo tree in a
temp directory with stub harnesses, so nothing here reads the real fixtures,
the real exporter, or anything else on this machine. (The alternative - point
it at the real repo and hope - is how a test ends up passing only on machines
that lack the thing it is testing.)

Run: python checks/_verify_node_checks.py
"""

import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from checks.node_checks import (  # noqa: E402
    export_mutation_check,
    export_roundtrip_check,
)


def _make_repo(tmp: Path, roundtrip_js: str, mutate_js: str, with_deps: bool = True) -> Path:
    """A throwaway repo root with stub harnesses in place of the real ones."""
    src = tmp / "testing" / "_src"
    src.mkdir(parents=True)
    (src / "roundtrip.js").write_text(roundtrip_js, encoding="utf-8")
    (src / "mutate.js").write_text(mutate_js, encoding="utf-8")
    if with_deps:
        (src / "node_modules" / "@xmldom").mkdir(parents=True)
    return tmp


def _js(lines: str, exit_code: int = 0) -> str:
    """A stub harness that prints a fixed transcript and exits as told."""
    body = "\n".join(f"console.log({line!r});" for line in lines.splitlines())
    return f"{body}\nprocess.exit({exit_code});\n"


# (label, roundtrip stub, exit, expected result)
ROUNDTRIP_CASES = [
    ("healthy run is NOT flagged",
     "  PASS  byte-for-byte identical to what the game wrote\nALL CHECKS PASSED", 0, "PASS"),
    ("a failing harness IS caught",
     "  FAIL  byte-for-byte identical to what the game wrote", 1, "DEFECT"),
    ("exit 0 with NO banner is caught (the silent-success shape)",
     "  PASS  something\n(fell out of the loop early)", 0, "DEFECT"),
    ("banner present but non-zero exit is caught",
     "ALL CHECKS PASSED", 1, "DEFECT"),
    ("a harness that printed nothing at all is caught", "", 0, "DEFECT"),
]

# (label, mutate stub, expected result)
MUTATION_CASES = [
    ("healthy 19/20 with M18 surviving is NOT flagged",
     "  SURVIVED M18 sort actions case-insensitively\n19/20 mutations caught.", "PASS"),
    ("FEWER caught is caught",
     "  SURVIVED M7 sort the categories\n  SURVIVED M18 sort actions\n18/20 mutations caught.", "DEFECT"),
    ("MORE caught is ALSO caught - 20/20 is a defect, not an improvement",
     "20/20 mutations caught.", "DEFECT"),
    ("right count, WRONG survivor is caught",
     "  SURVIVED M7 sort the categories\n19/20 mutations caught.", "DEFECT"),
    ("a missing count line is caught",
     "  SURVIVED M18 sort actions case-insensitively", "DEFECT"),
]


def main() -> int:
    if shutil.which("node") is None:
        print("NOT PERFORMED: node is not on PATH, so these checkers cannot be "
              "exercised. Reporting that rather than a pass.")
        return 2

    failures = 0

    def report(label, want, got, detail):
        nonlocal failures
        ok = got == want
        if not ok:
            failures += 1
        print(f"  [{'ok  ' if ok else 'FAIL'}] {label}\n           want {want}, got {got} - {detail}")

    print("--- export_roundtrip ---")
    for label, out, code, want in ROUNDTRIP_CASES:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td), _js(out, code), _js("19/20 mutations caught."))
            f = export_roundtrip_check(root)[0]
            report(label, want, f.result, f.details[:110])

    print("--- export_mutation ---")
    for label, out, want in MUTATION_CASES:
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td), _js("ALL CHECKS PASSED"), _js(out))
            f = export_mutation_check(root)[0]
            report(label, want, f.result, f.details[:110])

    # NOT PERFORMED, never PASS. An absent dependency must not look green.
    print("--- unrunnable is reported as a LIMITATION, not a pass ---")
    for name, fn in (("export_roundtrip", export_roundtrip_check),
                     ("export_mutation", export_mutation_check)):
        with tempfile.TemporaryDirectory() as td:
            root = _make_repo(Path(td), _js("ALL CHECKS PASSED"),
                              _js("19/20 mutations caught."), with_deps=False)
            f = fn(root)[0]
            report(f"{name}: missing node_modules -> LIMITATION", "LIMITATION", f.result, f.details[:110])

    # And a missing harness file is a DEFECT, not a silent skip.
    print("--- a missing harness file is a DEFECT ---")
    with tempfile.TemporaryDirectory() as td:
        root = _make_repo(Path(td), _js("ALL CHECKS PASSED"), _js("19/20 mutations caught."))
        (root / "testing" / "_src" / "roundtrip.js").unlink()
        f = export_roundtrip_check(root)[0]
        report("deleted roundtrip.js -> DEFECT", "DEFECT", f.result, f.details[:110])

    print()
    if failures:
        print(f"VERIFY FAILED: {failures} case(s) did not behave as required")
        return 1
    print("VERIFY PASSED: both checkers report every failure mode and stay quiet on the healthy one")
    return 0


if __name__ == "__main__":
    sys.exit(main())
