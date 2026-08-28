"""
Rule 12 proof for the missing_encoding checker, in BOTH directions.

RULE16: UNPROVEN - it imports missing_encoding_check and asks that function about
call sites this file planted, so a checker whose idea of 'specifies an
encoding' is wrong is wrong on both sides. The INPUT is independent and
is the point: bad call sites are written into a temp repo and every one
must be caught, clean ones must not be flagged.
This is a RULE 12 control, and rule 16 is a different axis. Proving a
checker fires on input that must trip it and stays silent on clean input
is exactly what rule 12 asks for, and this file does both halves. Being
UNPROVEN under rule 16 is not a criticism of it - it is the observation
that a checker cannot be an independent source of truth about itself.

A linter is trusted more than almost anything else in a codebase, because
people stop looking once it is green. So it gets tested the hard way:

  * every planted bad call site MUST be caught  (no false negatives)
  * every correct call site MUST NOT be flagged (no false positives)

The addendum is explicit that a linter with a false negative is worse than
none, and it is right: a checker that silently misses cases converts "we
looked" into "we are fine", which is exactly the silent-success failure this
project keeps finding.

Runs against a throwaway fixture tree in a temp directory - the checker takes
repo_root as a parameter, so nothing is planted in the real repo.

Run: venv/Scripts/python.exe checks/_verify_missing_encoding.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from checks.file_checks import missing_encoding_check  # noqa: E402

# Each entry: (source line, must_be_flagged)
CASES = [
    # ---- MUST be caught -------------------------------------------------
    ('data = open(path).read()',                                   True),
    ('fh = open(path, "w")',                                       True),
    ('fh = open(path, "r")',                                       True),
    ('text = Path(p).read_text()',                                 True),
    ('Path(p).write_text(payload)',                                True),
    ('with open(target, "a") as fh:',                              True),
    ('cfg = open(os.path.join(a, b))',                             True),

    # ---- MUST NOT be flagged -------------------------------------------
    ('fh = open(path, encoding="utf-8")',                          False),
    ('fh = open(path, "w", encoding="utf-8")',                     False),
    ('text = Path(p).read_text(encoding="utf-8")',                 False),
    ('Path(p).write_text(payload, encoding="utf-8")',              False),
    # binary mode takes no encoding and is correct as written
    ('fh = open(path, "rb")',                                      False),
    ('fh = open(path, "wb")',                                      False),
    ('with open(model, "rb") as fh:',                              False),
    # a commented-out call is not a call
    ('# data = open(path).read()',                                 False),

    # ---- REGRESSION CASES ------------------------------------------------
    # These are not hypothetical. The first regex version of this checker
    # passed every case above and then flagged all three of these against the
    # real repo: its own docstring, and its own fixture table. Both are text
    # ABOUT call sites, not call sites.
    ('s = "data = open(path).read()"',                             False),
    ("cases = [('fh = open(p)', True)]",                           False),
    ('x = 1  # mentions open() and read_text() in prose',          False),
]


def main():
    tmp = Path(tempfile.mkdtemp(prefix="cc_enc_"))
    lines, expected_bad_lines = [], set()
    for i, (src, must_flag) in enumerate(CASES):
        lines.append(src)
        if must_flag:
            expected_bad_lines.add(i + 1)
    (tmp / "fixture.py").write_text("\n".join(lines) + "\n", encoding="utf-8")

    findings = missing_encoding_check(tmp)
    flagged = {
        int(f.subject.rsplit(":", 1)[1])
        for f in findings
        if f.result == "DEFECT" and f.subject
    }

    passed, failed = 0, []
    print("--- false negatives (planted bad call sites that MUST be caught) ---")
    for i, (src, must_flag) in enumerate(CASES):
        if not must_flag:
            continue
        ln = i + 1
        if ln in flagged:
            passed += 1
            print(f"  ok   caught: {src}")
        else:
            failed.append(f"MISSED (false negative): {src}")
            print(f"  FAIL missed: {src}")

    print("\n--- false positives (correct call sites that MUST NOT be flagged) ---")
    for i, (src, must_flag) in enumerate(CASES):
        if must_flag:
            continue
        ln = i + 1
        if ln not in flagged:
            passed += 1
            print(f"  ok   left alone: {src}")
        else:
            failed.append(f"FALSE POSITIVE: {src}")
            print(f"  FAIL flagged:   {src}")

    # A clean tree must report PASS, and that PASS must be reachable -
    # otherwise the checker could never tell anyone the code is fine.
    print("\n--- a clean file reports PASS ---")
    clean = Path(tempfile.mkdtemp(prefix="cc_enc_ok_"))
    (clean / "ok.py").write_text(
        'fh = open(p, encoding="utf-8")\nq = Path(x).read_text(encoding="utf-8")\n',
        encoding="utf-8",
    )
    clean_findings = missing_encoding_check(clean)
    if len(clean_findings) == 1 and clean_findings[0].result == "PASS":
        passed += 1
        print("  ok   clean tree reports a single PASS")
    else:
        failed.append("clean tree did not report PASS")
        print(f"  FAIL clean tree reported: {[(f.result, f.details) for f in clean_findings]}")

    print("\n" + "=" * 62)
    if failed:
        print(f"FAILED {len(failed)} of {passed + len(failed)}:")
        for x in failed:
            print(f"  - {x}")
        return 1
    print(f"All {passed} assertions passed "
          f"({len(expected_bad_lines)} bad caught, "
          f"{len(CASES) - len(expected_bad_lines)} good left alone).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
