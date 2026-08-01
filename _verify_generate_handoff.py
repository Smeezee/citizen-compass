"""Characterization + regression test for generate_handoff.py's two
classification/parsing defects. Read-only: touches no aggregate file.

Run it BEFORE the fix to capture current behaviour, and AFTER to prove the
change. Every FAIL line below is a defect the fix is meant to close.

  python _verify_generate_handoff.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_handoff as g  # noqa: E402

failures = []


def check(label, got, expected):
    ok = got == expected
    if not ok:
        failures.append(f"{label}: got {got!r}, expected {expected!r}")
    print("  %-64s %-8s %s" % (label, got, "OK" if ok else "FAIL (want %r)" % (expected,)))


print("=" * 88)
print("DEFECT 1 - document classification")
print("=" * 88)
print("  A doc is a HANDOFF (replaces PROJECT NOTES) or an UPDATE (appends to the")
print("  running log). is_handoff_doc is checked first, so a false handoff wins.")
print()

CASES = [
    # (filename, text, expected_handoff, expected_update, why)
    ("update_push_landed.md",
     "# UPDATE - push landed\n\nCorrects the session handoff filed earlier.\n",
     False, True,
     "update whose BODY merely mentions the word handoff"),
    ("update_notes.md",
     "# UPDATE\n\nRoutine note. No special words.\n",
     False, True,
     "plain update"),
    ("update_second_pass.md",
     "# UPDATE\n\nFindings. See the handoff archive for context.\n",
     False, True,
     "update referencing the handoff archive"),
    ("citizen_compass_handoff.md",
     "# CITIZEN COMPASS HANDOFF\n\nFull state.\n",
     True, False,
     "genuine handoff by filename AND heading"),
    ("state_dump.md",
     "# CITIZEN COMPASS HANDOFF\n\nFull state.\n",
     True, False,
     "genuine handoff by heading alone"),
    ("state_dump2.md",
     "# SESSION ARCHIVE\n\nArchived session.\n",
     True, False,
     "genuine handoff via SESSION ARCHIVE heading"),
    ("weekly_handoff_notes.md",
     "# UPDATE\n\nSmall note.\n",
     True, False,
     "filename says handoff - filename rule is intentional, still wins"),
]

for name, text, want_h, want_u, why in CASES:
    p = Path(name)
    print("  case: %s" % why)
    check("    is_handoff_doc(%s)" % name, g.is_handoff_doc(p, text), want_h)
    if not want_h:
        check("    is_update_doc(%s)" % name, g.is_update_doc(p, text), want_u)

print()
print("=" * 88)
print("DEFECT 2 - updates log parsing")
print("=" * 88)
print("  append_update() writes '### <YYYY-MM-DD HH:MM:SS> - <source>'. Only those")
print("  are real entries; a ### subheading inside a body must NOT become one.")
print()

entries = g._parse_update_entries()
stamped = re.compile(r"^### \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
real = [e for e in entries if stamped.match(e)]
phantom = [e for e in entries if not stamped.match(e)]

print("  total entries parsed from _updates_log.md: %d" % len(entries))
print("  real (timestamped):                        %d" % len(real))
print("  phantom (### subheadings promoted):        %d" % len(phantom))
if phantom:
    print("  phantom entry titles:")
    for e in phantom[:12]:
        print("      %s" % e.splitlines()[0][:72])
check("  phantom entry count", len(phantom), 0)

# A phantom entry also STEALS body text from its parent, so the parent is truncated.
synthetic = (
    "### 2026-01-01 00:00:00 - a.md\n\n"
    "# UPDATE\n\nIntro paragraph.\n\n"
    "### Subheading One\n\nBelongs to a.md.\n\n"
    "### Subheading Two\n\nAlso belongs to a.md.\n\n"
    "### 2026-01-02 00:00:00 - b.md\n\n"
    "# UPDATE\n\nSecond entry.\n"
)
orig = g.UPDATES_LOG_PATH
tmp = Path("_verify_tmp_updates_log.md")
tmp.write_text(synthetic, encoding="utf-8")
g.UPDATES_LOG_PATH = tmp
try:
    parsed = g._parse_update_entries()
    print()
    print("  synthetic log with 2 real entries and 2 internal subheadings:")
    check("    entries parsed", len(parsed), 2)
    first = parsed[0] if parsed else ""
    check("    entry 1 retains 'Subheading One'", "Subheading One" in first, True)
    check("    entry 1 retains 'Subheading Two'", "Subheading Two" in first, True)
finally:
    g.UPDATES_LOG_PATH = orig
    tmp.unlink(missing_ok=True)

print()
print("=" * 88)
if failures:
    print("FAILURES (%d):" % len(failures))
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("ALL CHECKS PASSED")
