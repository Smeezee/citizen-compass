"""HARD RULE 16, made enforceable: every check declares where its truth comes from.

RULE16: UNPROVEN - this gate reads the DECLARATION, never the truth of it. It can
prove a label is present and well formed; it cannot prove a label is honest. A
check that claims INDEPENDENT while quietly asserting against its own output
passes here. That gap is real, it is structural, and the only thing that closes
it is a person reading the label next to the check. Said first, before anything
else in this file, because a gate that hides its own limit is the thing rule 16
exists to catch.

THE RULE, as adopted 2026-08-27
===============================
    A check must draw its truth from a different source than the thing it
    checks. Where that is impossible, the check is labelled UNPROVEN and says
    what it could not reach.

WHY THIS IS NOT RULE 12 AGAIN
=============================
Rule 12 catches a check that CANNOT FAIL. Rule 16 catches a check that CAN fail
but cannot fail FOR THE REAL REASON, because the check and the code share an
assumption. The three cases in the project's record all passed rule 12:

  - the stub camera that always looked at its target, modelling the fix. 23
    green checks over three days of a completely black site.
  - ui.go compiling clean - a file the product does not use.
  - the callback control asserting 50 calls consumed 50 slots, when Go dedupes
    identical closures and one slot was consumed.

Each COULD have failed. None could have failed for the reason that mattered.

THE FORMAT
==========
One line, anywhere in the first 60 lines of the file:

    RULE16: INDEPENDENT - <where the truth comes from, and why the thing under
                           test cannot have produced it>
    RULE16: UNPROVEN - <what it could not reach>

INDEPENDENT means EVERY assertion in the file draws on a source the code under
test did not produce. If one assertion does not, the file is UNPROVEN and the
label names which - that keeps the word meaning something.

WHY A RATCHET AND NOT A FLAG DAY
================================
There are ~96 checks. Requiring a label on all of them today makes this gate red
on day one and red every day after, and a permanently red gate is one nobody
reads - which is how the board ends up worse instead of better.

So the currently-unlabelled set is recorded in `rule16_baseline.txt` as DEBT
THAT IS VISIBLE AND COUNTABLE. The gate fails on:

    a NEW check with no label            <- the ratchet: the debt cannot grow
    a MALFORMED label                    <- a label that says nothing is worse
                                            than no label, because it looks done
    a baseline entry that no longer exists <- keeps the list honest

and it never fails for a file that was already unlabelled when the rule was
adopted. The baseline can only shrink. Every line removed from it is a real gap
closed.

Usage:
    python checks/_verify_rule16_labels.py
    python checks/_verify_rule16_labels.py --write-baseline   (once, at adoption)
    python checks/_verify_rule16_labels.py --report           (what is left)
"""

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
BASELINE = os.path.join(HERE, "rule16_baseline.txt")
LABEL = re.compile(r"RULE16:\s*(INDEPENDENT|UNPROVEN)\s*[-—:]\s*(.+)")
HEAD_LINES = 60
MIN_REASON = 30

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def checks():
    for n in sorted(os.listdir(HERE)):
        if not n.startswith("_verify_"):
            continue
        if os.path.splitext(n)[1] not in (".py", ".mjs", ".js"):
            continue
        if n == os.path.basename(__file__):
            continue
        yield n


def label_of(name):
    """(state, reason) or (None, why-not)."""
    path = os.path.join(HERE, name)
    try:
        with open(path, encoding="utf-8") as fh:
            head = [next(fh, "") for _ in range(HEAD_LINES)]
    except OSError as exc:
        return None, "could not be read: %s" % exc
    hits = [LABEL.search(l) for l in head]
    hits = [h for h in hits if h]
    if not hits:
        return None, "no RULE16: line in the first %d lines" % HEAD_LINES
    if len(hits) > 1:
        return None, "%d RULE16: lines - a check has one status" % len(hits)
    state, reason = hits[0].group(1), hits[0].group(2).strip()

    # A LABEL IS ALLOWED TO WRAP, AND THE READER HAS TO FOLLOW IT.
    # The first version read only the line the regex matched, so a reason
    # wrapped to a readable width was truncated at its first line and --report
    # printed "for the 19 Fleetyards imports the MODEL and the" - the half of
    # the sentence that says nothing. The reason IS the deliverable here; a
    # reader that shows a tenth of it defeats the rule it enforces.
    idx = next(i for i, l in enumerate(head) if LABEL.search(l or ""))
    for cont in head[idx + 1:]:
        t = (cont or "").rstrip("\n")
        stripped = t.strip().lstrip("*").strip()
        if not stripped or stripped.startswith('"""') or stripped.startswith("/*"):
            break
        if not (t.startswith((" ", "\t")) or t.lstrip().startswith("*")):
            break
        reason += " " + stripped
    reason = " ".join(reason.split())

    if len(reason) < MIN_REASON:
        return None, ("the reason is %d characters. A label that says nothing is "
                      "worse than no label, because it looks done" % len(reason))
    return state, reason


def read_baseline():
    if not os.path.exists(BASELINE):
        return None
    with open(BASELINE, encoding="utf-8") as fh:
        return {l.strip() for l in fh
                if l.strip() and not l.startswith("#")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-baseline", action="store_true")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    labelled, unlabelled, malformed = {}, [], []
    for n in checks():
        state, reason = label_of(n)
        if state is None:
            if "no RULE16: line" in reason:
                unlabelled.append(n)
            else:
                malformed.append((n, reason))
        else:
            labelled[n] = (state, reason)

    total = len(labelled) + len(unlabelled) + len(malformed)

    if args.write_baseline:
        with open(BASELINE, "w", encoding="utf-8") as fh:
            fh.write("# Checks that carried no RULE16 label when hard rule 16 was\n"
                     "# adopted, 2026-08-27. THIS LIST CAN ONLY SHRINK.\n"
                     "#\n"
                     "# Every line here is a check whose truth may share a source\n"
                     "# with the thing it checks and which has not said so either\n"
                     "# way. That is a known gap, not an accepted one.\n"
                     "#\n"
                     "# Remove a line by adding a RULE16: line to that file. The\n"
                     "# gate fails if a line here names a file that no longer\n"
                     "# needs it, so the list cannot rot into fiction.\n")
            for n in sorted(unlabelled):
                fh.write(n + "\n")
        print("wrote %s with %d entr(ies)" % (os.path.relpath(BASELINE, REPO),
                                              len(unlabelled)))
        return 0

    base = read_baseline()
    print("=" * 70)
    print("RULE 16 LABELS - %d check(s)" % total)
    print("=" * 70)
    print("  labelled            %d  (%d INDEPENDENT, %d UNPROVEN)"
          % (len(labelled),
             sum(1 for s, _ in labelled.values() if s == "INDEPENDENT"),
             sum(1 for s, _ in labelled.values() if s == "UNPROVEN")))
    print("  unlabelled          %d" % len(unlabelled))
    print("  malformed label     %d" % len(malformed))

    if args.report:
        print("\n-- UNPROVEN, and what each could not reach --")
        for n, (s, r) in sorted(labelled.items()):
            if s == "UNPROVEN":
                print("  %s\n      %s" % (n, r))
        print("\n-- still unlabelled --")
        for n in sorted(unlabelled):
            print("  " + n)
        return 0

    if base is None:
        print("\nNOT PERFORMED: no baseline. Run --write-baseline once, at "
              "adoption, so the debt is recorded before it can be forgotten.")
        return 1

    failures = []
    for n, reason in malformed:
        failures.append("%s: %s" % (n, reason))
    new_unlabelled = sorted(set(unlabelled) - base)
    for n in new_unlabelled:
        failures.append("%s: a NEW check with no RULE16 label. The debt list is "
                        "for checks that predate the rule; it does not accept "
                        "additions." % n)
    stale = sorted(base - set(unlabelled) - set(labelled) - {m[0] for m in malformed})
    for n in stale:
        failures.append("%s: on the baseline but no longer a check. Remove the "
                        "line - a debt list that names things that do not exist "
                        "stops being read." % n)
    closed = sorted(base & set(labelled))

    if closed:
        print("\n  %d baseline entr(ies) CLOSED since adoption:" % len(closed))
        for n in closed:
            print("      %s  ->  %s" % (n, labelled[n][0]))
        print("  (remove these lines from rule16_baseline.txt)")

    print("")
    if failures:
        print("%d failure(s):" % len(failures))
        for f in failures:
            print("  - " + f)
        print("RED.")
        return 1
    print("GREEN - every check either declares its rule 16 status or was "
          "already on the baseline. %d gap(s) still on the list." % len(base))
    return 0


if __name__ == "__main__":
    sys.exit(main())
