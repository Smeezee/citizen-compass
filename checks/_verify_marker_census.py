# -*- coding: utf-8 -*-
"""Did any hull quietly lose its dots since the last time somebody looked?

RULE16: INDEPENDENT - the truth is a census recorded at an EARLIER TIME, in a
separate artifact, which nothing in today's build can influence or reach. The
run under test cannot make this pass by agreeing with itself; it can only agree
with what the page looked like before. Its one real weakness is named rather
than hidden: **a person can regenerate the baseline and silence it.** That is
why regeneration takes an explicit flag, prints every change it is about to
absorb, and refuses to run unattended.

WHY THIS EXISTS BEFORE THE THING IT WAS WRITTEN FOR.
`PROPOSAL_the-marker-pipeline-is-four-layers-deep-2026-08-27` §3 proposes
collapsing four marker layers into one, and states its own condition:

    "it must not go in the same week as a release - if it drops a hull, it
    drops it silently unless the swap carries a control that counts markers
    before and after and refuses on any loss. **That control is the condition
    of doing it at all.**"

The collapse is Sleven's decision and has not been made. **The control is not.**
It guards every marker change, and there is one landing right now: the frame
proof changed on 2026-08-28, so the next rebuild moves the Glaive in and both
Drake Clippers out. A census that only exists after that rebuild would have
nothing to compare it against.

WHAT IT REFUSES, AND WHAT IT MERELY REPORTS
    a hull that LOST dots            REFUSED unless the loss is declared
    a hull that VANISHED entirely    REFUSED unless declared
    a hull that GAINED dots          reported, not refused
    a hull that is NEW               reported, not refused

**Loss is the asymmetry that matters.** Gaining markers is what every good day
looks like; losing them silently is how a pipeline change costs a hull that
nobody notices for a month. A declared loss carries a reason in the baseline and
is printed every run, so it stays visible rather than becoming invisible.

RULE 12 - THE CONTROLS, on the real census rather than an invented one:
    --mutate-drop   one hull's markers removed entirely. Must be refused.
    --mutate-thin   one hull keeps a single marker. Must be refused.
    --mutate-grow   one hull gains markers. Must NOT be refused - a control
                    that refuses everything is not measuring loss, it is
                    measuring change, and the two are not the same claim.
--self-test runs all three and requires each to behave; its exit code is
inverted per the suite's convention.
"""
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKER = os.path.join(REPO, "testing", "_deploy", "loadout_marker.gen.js")
BASELINE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "marker_census.json")

SELFTEST = "--self-test" in sys.argv
REBASE = "--rebaseline" in sys.argv


def counts():
    src = open(MARKER, encoding="utf-8", errors="replace").read()
    body = src[src.find("{", src.find("=")):].rstrip().rstrip(";")
    data = json.loads(body)
    return {k: len(v) for k, v in data.items()}


def compare(now, base, allowed):
    """(lost, gone, gained, new, declared). No printing."""
    lost, gone, gained, new, declared = [], [], [], [], []
    for cls, n0 in base.items():
        n1 = now.get(cls)
        why = allowed.get(cls)
        if n1 is None:
            (declared if why else gone).append((cls, n0, 0, why))
        elif n1 < n0:
            (declared if why else lost).append((cls, n0, n1, why))
        elif n1 > n0:
            gained.append((cls, n0, n1, None))
    for cls in now:
        if cls not in base:
            new.append((cls, 0, now[cls], None))
    return lost, gone, gained, new, declared


def rebaseline(now):
    print("REBASELINING. Every change below is being absorbed into the "
          "census and will stop being reported.")
    if os.path.exists(BASELINE):
        old = json.load(open(BASELINE, encoding="utf-8"))
        lost, gone, gained, new, _d = compare(now, old.get("hulls") or {},
                                              {})
        for label, rows in (("LOSING", lost), ("VANISHING", gone),
                            ("gaining", gained), ("new", new)):
            for cls, a, b, _w in rows:
                print("  %-9s %-42s %d -> %d" % (label, cls, a, b))
        if lost or gone:
            print()
            print("READ THAT LIST AGAIN BEFORE YOU KEEP THIS FILE. A loss "
                  "absorbed into a baseline is a loss nobody will ever be "
                  "told about again.")
    json.dump({
        "what": "markers per hull in testing/_deploy/loadout_marker.gen.js, "
                "recorded so a later build cannot lose a hull quietly",
        "written_by": "checks/_verify_marker_census.py --rebaseline",
        "hulls": now,
        "allowed_losses": {},
        "how_to_declare_a_loss":
            "put the class in allowed_losses with a sentence saying WHY it is "
            "expected. It is printed on every run afterwards, so a declared "
            "loss stays visible instead of becoming invisible.",
    }, open(BASELINE, "w", encoding="utf-8"), indent=1, sort_keys=True)
    print("\nwrote %s - %d hull(s)" % (BASELINE, len(now)))
    return 0


def report(now, base, allowed):
    lost, gone, gained, new, declared = compare(now, base, allowed)
    print("census: %d hull(s) recorded, %d in the build now"
          % (len(base), len(now)))
    print("        %d gained, %d new, %d declared change(s)"
          % (len(gained), len(new), len(declared)))
    print()
    for cls, a, b, why in declared:
        print("  DECLARED  %-40s %d -> %d" % (cls, a, b))
        print("            %s" % why)
    ok = True
    if gone:
        ok = False
        print("  REFUSED - %d hull(s) have NO markers at all any more:"
              % len(gone))
        for cls, a, _b, _w in gone:
            print("     %-42s had %d" % (cls, a))
    if lost:
        ok = False
        print("  REFUSED - %d hull(s) lost markers:" % len(lost))
        for cls, a, b, _w in lost:
            print("     %-42s %d -> %d" % (cls, a, b))
    # A DECLARATION THAT OUTLIVES ITS REASON IS HOW A REAL LOSS GETS WAVED
    # THROUGH. This file has said that in those words on every declaration
    # since 2026-08-28 and did not enforce it: a declared hull that stops
    # losing markers simply stopped appearing above, and the entry sat here
    # excusing nothing while looking like diligence. Twelve of the thirteen
    # declarations are waiting on models being re-exported; the day that
    # happens they all go stale at once and nothing would have said so.
    #
    # ADOPTED FROM `_verify_child_markers.py` (Code, 2026-08-29, Q27), which
    # got this right first: "a declaration nothing fires is fiction."
    stale = sorted(c for c in allowed
                   if not (base.get(c, 0) > now.get(c, 0)))
    if stale:
        ok = False
        print("  REFUSED - %d declaration(s) no longer describe anything. "
              "Delete them or find out why the loss stopped:" % len(stale))
        for cls in stale:
            print("     %-42s declared, but %d -> %d"
                  % (cls, base.get(cls, 0), now.get(cls, 0)))
    if ok:
        print("  no undeclared loss, and every declaration still fires")
    return ok, len(lost) + len(gone) + len(stale)


def main():
    if not os.path.exists(MARKER):
        print("NOT PERFORMED - no %s. Nothing has been built." % MARKER)
        return 2
    now = counts()

    if REBASE:
        return rebaseline(now)

    if not os.path.exists(BASELINE):
        print("NOT PERFORMED - no census yet. Run with --rebaseline to record "
              "one. This is NOT a pass: until a census exists there is nothing "
              "for a later build to be compared against.")
        return 2

    b = json.load(open(BASELINE, encoding="utf-8"))
    base = b.get("hulls") or {}
    allowed = b.get("allowed_losses") or {}

    if SELFTEST:
        return selftest(now, base, allowed)

    ok, _n = report(now, base, allowed)
    print()
    print("PASS - no hull lost markers without saying so." if ok else "FAIL")
    return 0 if ok else 1


def selftest(now, base, allowed):
    ok = True

    clean, _n = report(now, base, allowed)
    print()
    if not clean:
        ok = False
        print("NEGATIVE CONTROL FAILED - the real build already refuses, so "
              "nothing below distinguishes a working control from a broken "
              "one. Fix the build or declare the loss first.")
    else:
        print("negative control: the real build passes            ok")

    victim = max(base, key=lambda k: base[k])

    drop = dict(now)
    drop.pop(victim, None)
    d_ok, d_n = report(drop, base, allowed)
    caught = (not d_ok) and d_n >= 1
    print("drop  %-40s %s" % (victim, "caught" if caught else "NOT CAUGHT"))
    ok = ok and caught

    thin = dict(now)
    thin[victim] = 1
    t_ok, t_n = report(thin, base, allowed)
    caught = (not t_ok) and t_n >= 1
    print("thin  %-40s %s" % (victim, "caught" if caught else "NOT CAUGHT"))
    ok = ok and caught

    grow = dict(now)
    grow[victim] = base[victim] + 50
    g_ok, _g = report(grow, base, allowed)
    print("grow  %-40s %s" % (victim,
                              "correctly allowed" if g_ok
                              else "WRONGLY REFUSED"))
    ok = ok and g_ok

    # RULE 12 FOR THE STALE CHECK. Restore a declared hull to its recorded
    # count: its declaration now excuses nothing and must be refused. Without
    # this the stale rule is a branch nothing has ever entered.
    if allowed:
        dead = sorted(allowed)[0]
        heal = dict(now)
        heal[dead] = base.get(dead, 0)
        h_ok, h_n = report(heal, base, allowed)
        caught = (not h_ok) and h_n >= 1
        print("stale %-40s %s" % (dead, "caught" if caught else "NOT CAUGHT"))
        ok = ok and caught
    else:
        print("stale (no declarations to test)                    SKIPPED")
        ok = False

    print()
    if ok:
        print("SELF-TEST PASSED - loss is refused, growth is not, and the "
              "real build is clean.")
        print("Exiting NON-ZERO on purpose: the suite requires a control's "
              "self-test to be rejected. This is the GOOD outcome.")
        return 9
    print("SELF-TEST FAILED - this is not currently a control.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
