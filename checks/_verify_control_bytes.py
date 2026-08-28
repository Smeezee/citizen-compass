# -*- coding: utf-8 -*-
"""Prove `control_bytes_check` catches an escape-mangled regex and does not
flag clean source.

RULE16: UNPROVEN - it imports control_bytes_check and judges its verdicts. The
planted input is independent - source with a genuine escape-mangled
regex in it, written here - and the checker has to find it and has to
leave clean source alone.
This is a RULE 12 control, and rule 16 is a different axis. Proving a
checker fires on input that must trip it and stays silent on clean input
is exactly what rule 12 asks for, and this file does both halves. Being
UNPROVEN under rule 16 is not a criticism of it - it is the observation
that a checker cannot be an independent source of truth about itself.

WHY THIS CHECKER EXISTS, which is also why this file has to exist.

A regex written as /\\bpinned\\b/ and passed through a tool that reads \\b as
an escape becomes /<0x08>pinned<0x08>/. It is a VALID regular expression. It
matches nothing. And it is invisible - in an editor, in `git diff`, in a code
review - because a terminal renders 0x08 as nothing at all.

It happened four times in this repo in one session:

  _verify_sorts.mjs      a FAILING assertion, on a page that was correct.
                         Announced itself, cost an hour.
  _verify_dim.mjs        a PASSING assertion that could not fail. It had
                         already been reported as an `ok`.
  _loadout_harness.mjs   the tag parser in a stub built to observe element
                         positions. It observed none.
  leak_selftest.go       a comment that lost its meaning.

The second one is why this is machine-enforced rather than a habit. A byte that
turns a check into a check-shaped no-op cannot be guarded by remembering to look
for it, BECAUSE LOOKING IS EXACTLY WHAT DOES NOT WORK.

Run: venv/Scripts/python.exe checks/_verify_control_bytes.py
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from checks.file_checks import control_bytes_check  # noqa: E402

PASSED = []
FAILED = []


def check(ok, label, detail=""):
    if ok:
        PASSED.append(label)
        print("  [ok  ] %s" % label)
    else:
        FAILED.append("%s %s" % (label, detail))
        print("  [FAIL] %s %s" % (label, detail))


def write(root, rel, text):
    p = Path(root) / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def main():
    print("=" * 66)
    print("control_bytes_check - proven against planted bad input")
    print("=" * 66)

    BS = chr(8)
    ESC = chr(27)
    SEP = chr(1)

    # --- 1. CLEAN SOURCE IS NOT FLAGGED -------------------------------------
    print("\n--- 1. clean source passes ---")
    with tempfile.TemporaryDirectory() as clean:
        write(clean, "ok.mjs",
              'const re = /' + chr(92) + 'bpinned' + chr(92) + 'b/;\n'
              'export default re;\n')
        write(clean, "ok.py", 'import re\nR = re.compile(r"'
              + chr(92) + 'bword' + chr(92) + 'b")\n')
        write(clean, "tabs.js", "const a = 1;\n\tconst b = 2;\r\n")
        out = control_bytes_check(Path(clean))
        bad = [f for f in out if f.result != "PASS"]
        check(not bad,
              "a correctly-escaped regex is NOT flagged - the checker does not "
              "simply fail on every backslash",
              str([f.subject for f in bad]))
        check(any(f.result == "PASS" for f in out),
              "and the clean run reports a PASS naming how many files it read",
              (out[0].details or "")[:60] if out else "no findings at all")
        check(all("tabs.js" not in str(f.subject) for f in bad),
              "tab, newline and carriage return are text and are left alone")

    # --- 2. THE PLANTED DEFECT IS CAUGHT ------------------------------------
    print("\n--- 2. the mangled byte is caught, in every language ---")
    with tempfile.TemporaryDirectory() as dirty:
        write(dirty, "mangled.mjs",
              'const re = /' + BS + 'pinned' + BS + '/;\n'
              'export default re;\n')
        write(dirty, "mangled.py",
              'import re\nR = re.compile("' + BS + 'word' + BS + '")\n')
        write(dirty, "mangled.go",
              "package x\n// the old `" + BS + "Vulkan" + BS + "` matcher\n")
        out = control_bytes_check(Path(dirty))
        defects = [f for f in out if f.result == "DEFECT"]
        subjects = " ".join(str(f.subject) for f in defects)
        check(len(defects) == 3,
              "all three planted files are reported", str(len(defects)))
        for name in ("mangled.mjs", "mangled.py", "mangled.go"):
            check(name in subjects, "%s is named" % name)
        check(all(":" in str(f.subject) for f in defects),
              "and each finding names the LINE, not just the file",
              str([f.subject for f in defects])[:90])
        check(any("0x08" in (f.details or "") for f in defects),
              "and states the byte it found, in hex")
        check(all(BS not in (f.details or "") for f in defects),
              "AND THE FINDING ITSELF IS PRINTABLE - the byte is rendered as "
              "<0x08> rather than pasted raw into a report nobody can read, "
              "which is the whole reason this defect survives review")

    # --- 3. THE WHOLE MANGLED SET, NOT JUST 0x08 ----------------------------
    print("\n--- 3. every byte an escape can produce from a letter ---")
    with tempfile.TemporaryDirectory() as many:
        for i, code in enumerate((0x07, 0x08, 0x0B, 0x0C, 0x1B)):
            write(many, "m%d.js" % i, "const s = 'a%sb';\n" % chr(code))
        out = control_bytes_check(Path(many))
        defects = [f for f in out if f.result == "DEFECT"]
        check(len(defects) == 5,
              "\\a \\b \\f \\v and \\e are all caught", str(len(defects)))

    # --- 4. A DELIBERATE SEPARATOR IS NOT THE SAME CLAIM --------------------
    print("\n--- 4. a deliberate control character is reported, not failed ---")
    with tempfile.TemporaryDirectory() as sep:
        write(sep, "join.js",
              "const key = parts.join('" + SEP + "');\n")
        out = control_bytes_check(Path(sep))
        check(all(f.result != "DEFECT" for f in out),
              "0x01 used as a field separator is NOT a defect - roundtrip.js "
              "does exactly this on purpose",
              str([(f.result, f.subject) for f in out]))
        check(any(f.result == "WARNING" for f in out),
              "but it IS reported, so it is a decision somebody can see rather "
              "than a byte nobody knows about")
        check(ESC not in "".join(str(f.details or "") for f in out),
              "and nothing in the report smuggles a control byte of its own")

    # --- 5. THE REAL REPO ---------------------------------------------------
    print("\n--- 5. the repo as it stands ---")
    root = Path(__file__).resolve().parent.parent
    out = control_bytes_check(root)
    defects = [f for f in out if f.result == "DEFECT"]
    warns = [f for f in out if f.result == "WARNING"]
    check(not defects,
          "no source file in this repo carries an escape-mangled byte",
          str([f.subject for f in defects])[:160])
    print("    %d warning(s): %s"
          % (len(warns), ", ".join(str(f.subject) for f in warns) or "none"))

    print("\n" + "=" * 66)
    if FAILED:
        print("FAILED: %d of %d" % (len(FAILED), len(FAILED) + len(PASSED)))
        for f in FAILED:
            print("  " + f)
        return 1
    print("VERIFY PASSED - %d assertions. The checker catches the byte in "
          "three languages, tells a deliberate separator apart from a mangled "
          "escape, and renders what it found in a form a person can read."
          % len(PASSED))
    return 0


if __name__ == "__main__":
    sys.exit(main())
