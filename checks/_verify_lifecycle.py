"""Rule 12 proof for checks/lifecycle.py.

RULE16: UNPROVEN - it imports checks.lifecycle and asks those functions what a
finding's next state should be, so a wrong transition table is applied
identically on both sides. The load-bearing assertion - a checker that
stopped running must produce UNKNOWN rather than a wave of CLOSED - is
driven from states constructed here, which is what makes it worth having
even though the rule doing the deciding is the one under test.

The load-bearing assertion: a checker that stopped running must produce UNKNOWN,
never CLOSED. That failure mode is why this module exists, so it is tested
directly rather than assumed.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from checks.lifecycle import (  # noqa: E402
    ACKNOWLEDGED, CLOSED, OPEN, UNKNOWN,
    finding_key, implausible_mass_close, normalise_condition, reconcile,
)

failures = []


def check(label, got, expected):
    ok = got == expected
    if not ok:
        failures.append(f"{label}: got {got!r}, expected {expected!r}")
    print("  %-64s %-9s %s" % (label, got, "OK" if ok else "FAIL(want %r)" % (expected,)))


print("=" * 88)
print("IDENTITY - the same condition seen twice must be ONE finding")
print("=" * 88)

# The exact shape that produced 32 rows for 11 problems.
a = finding_key("missing_or_corrupt_3d_model", "85X", r"sc-ships\85X\model.glb does not exist")
b = finding_key("missing_or_corrupt_3d_model", "85X", r"C:\Users\david\citizen-compass\sc-ships\85X\model.glb does not exist")
check("same condition, different absolute path -> same key", a == b, True)

c = finding_key("registry_sync", "db-not-in-registry", "62 DB ship name(s) have no matching entry")
d = finding_key("registry_sync", "db-not-in-registry", "63 DB ship name(s) have no matching entry")
check("count drifted by one -> same key", c == d, True)

e = finding_key("x", "y", "failed at 2026-08-01T14:57:32 while reading")
f = finding_key("x", "y", "failed at 2026-08-02T09:11:04 while reading")
check("different timestamps -> same key", e == f, True)

g = finding_key("missing_or_corrupt_3d_model", "85X", "model.glb does not exist")
h = finding_key("missing_or_corrupt_3d_model", "Fury", "model.glb does not exist")
check("different subject -> DIFFERENT key", g != h, True)

i = finding_key("check_a", "s", "model.glb does not exist")
j = finding_key("check_b", "s", "model.glb does not exist")
check("different checker -> DIFFERENT key", i != j, True)

k = finding_key("x", "y", "the file is missing")
m = finding_key("x", "y", "the file is corrupt")
check("genuinely different condition -> DIFFERENT key", k != m, True)

print()
print("  normalisation examples:")
for s in (r"C:\Users\david\repo\sc-ships\85X\model.glb does not exist",
          "62 DB ship name(s) have no matching ship_registry.json entry",
          "failed at 2026-08-01T14:57:32 (run 4764726896973204a798325ed0f9ed7253e995e5)"):
    print("    %-64s -> %s" % (s[:64], normalise_condition(s)[:60]))

print()
print("=" * 88)
print("TRANSITIONS - the load-bearing rules")
print("=" * 88)

prev = {
    "k_open":  {"status": OPEN, "check_name": "checker_a"},
    "k_gone":  {"status": OPEN, "check_name": "checker_a"},
    "k_orphan": {"status": OPEN, "check_name": "checker_dead"},
    "k_ack":   {"status": ACKNOWLEDGED, "check_name": "checker_a", "acknowledged": True},
    "k_closed": {"status": CLOSED, "check_name": "checker_a"},
}

print("\n  -- checker ran cleanly: unseen findings CLOSE --")
o, cl, un, unch = reconcile(prev, {"k_open": {}, "k_ack": {}}, {"checker_a"}, "run1")
check("k_gone CLOSED (checker ran, did not find it)", "k_gone" in cl, True)
check("k_open unchanged (still seen)", "k_open" in unch, True)
check("k_ack stays acknowledged, not reopened", "k_ack" in unch, True)
check("k_orphan NOT closed - its checker never ran", "k_orphan" in cl, False)
check("k_orphan -> UNKNOWN", "k_orphan" in un, True)

print("\n  -- THE CRITICAL CASE: checker errored, nothing may close --")
o2, cl2, un2, unch2 = reconcile(prev, {}, set(), "run2")
check("nothing CLOSED when no checker ran", cl2, [])
check("k_open -> UNKNOWN", "k_open" in un2, True)
check("k_gone -> UNKNOWN", "k_gone" in un2, True)
check("k_orphan -> UNKNOWN", "k_orphan" in un2, True)
check("already-CLOSED stays closed, not re-flagged", "k_closed" in un2, False)

print("\n  -- a new condition opens --")
o3, cl3, un3, unch3 = reconcile(prev, {"k_new": {}}, {"checker_a"}, "run3")
check("k_new OPENED", "k_new" in o3, True)

print("\n  -- a CLOSED finding that reappears REOPENS --")
o4, cl4, un4, unch4 = reconcile({"k_closed": {"status": CLOSED, "check_name": "checker_a"}},
                                {"k_closed": {}}, {"checker_a"}, "run4")
check("reappearing finding reopens", "k_closed" in o4, True)

print("\n  -- an UNKNOWN finding that reappears REOPENS --")
o5, cl5, un5, unch5 = reconcile({"k_u": {"status": UNKNOWN, "check_name": "checker_a"}},
                                {"k_u": {}}, {"checker_a"}, "run5")
check("reappearing unknown reopens", "k_u" in o5, True)

print()
print("=" * 88)
print("MASS-CLOSE ALARM - a broken checker looks like a productive afternoon")
print("=" * 88)
check("closing 40 of 50 open is implausible", implausible_mass_close(40, 50), True)
check("closing 2 of 50 open is fine", implausible_mass_close(2, 50), False)
check("no open findings -> never alarms", implausible_mass_close(0, 0), False)

print()
print("=" * 88)
if failures:
    print("FAILURES (%d):" % len(failures))
    for x in failures:
        print("  -", x)
    sys.exit(1)
print("ALL LIFECYCLE ASSERTIONS PASSED")
print("Critically: a checker that did not run produces UNKNOWN, never CLOSED.")
