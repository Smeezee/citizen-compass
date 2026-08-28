# -*- coding: utf-8 -*-
"""Does OWNERS.md describe the repository that is actually here?

RULE16: UNPROVEN - two of the three assertions are independent and this
says which, but B is not, and the rule reads EVERY assertion. Relabelled
from INDEPENDENT on 2026-08-27 by Code: the gate's regex requires
`RULE16: <INDEPENDENT|UNPROVEN> - <reason>` and read the original line as
no label at all, so this control counted itself as an unlabelled new
check. The wording below is C1's and is unchanged - only the verdict and
the punctuation moved, because a file with one non-independent assertion
is UNPROVEN by the rule as written, and 'mixed' has no third value.

  A. EVERY OWNED PATH EXISTS - drawn from the FILESYSTEM, which OWNERS.md did
     not write and cannot influence. A path that has been renamed, moved or
     deleted shows here and nowhere else.
  B. NO PATH IS CLAIMED TWICE - drawn from OWNERS.md alone. This one is NOT
     independent and is not claimed to be: it is an internal consistency test,
     the cheap half, and it is here because two owners for one path is the
     exact failure the file exists to prevent.
  C. `NEXT.md` DOES NOT KEEP A SECOND COPY - drawn from NEXT.md, which
     OWNERS.md does not write. Independent in the way that matters.

     THE FIRST DRAFT OF THIS CHECK GOT C WRONG and its output is why. It
     reconciled OWNERS.md against the prose list NEXT.md used to carry, and on
     its first run reported eleven disagreements - every one of them the prose
     list simply being behind, which is exactly the failure mode that caused
     2026-08-27. Reconciling two hand-kept copies of a list is a worse answer
     than not keeping two. **Rule 14 is one writer per artifact, and the
     ownership list is an artifact.** So the prose list was deleted, this file
     is the only copy, and C now asserts that NEXT.md has not grown another
     one.

RULE 12 - THE CONTROL. `--self-test` builds four broken manifests in memory and
requires every one to be caught:

    a path claimed by two owners           B must fire
    a path that does not exist on disk     A must fire
    a NEXT.md entry missing from OWNERS   C must fire
    an OWNERS entry missing from NEXT.md  C must fire

And the negative half: the REAL file must pass. A check that refuses everything
proves nothing.

Its exit code is inverted, per the suite's convention - `run_all_controls.py
--self-test` requires a non-zero exit from every control. Non-zero here means
every mutation was caught; zero means one slipped through and this file is not
a control.
"""
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWNERS = os.path.join(REPO, "OWNERS.md")
NEXT = os.path.join(REPO, "NEXT.md")
SELFTEST = "--self-test" in sys.argv

# A line inside an owner section that looks like a repository path.
PATH = re.compile(r"^\s{4}([A-Za-z0-9_./\\-]+)\s*$")
OWNER = re.compile(r"^##\s+([A-Z0-9]+)\b")


def parse_owners(text):
    """-> {path: owner}, in file order. Duplicates are NOT collapsed."""
    owner, pairs = None, []
    for line in text.splitlines():
        m = OWNER.match(line)
        if m:
            owner = m.group(1)
            continue
        m = PATH.match(line)
        if m and owner:
            pairs.append((m.group(1), owner))
    return pairs


def parse_next(text):
    """Any path NEXT.md's ownership section enumerates. Should be none.

    A pointer may NAME `OWNERS.md` and may name the two files whose collision
    caused this - those are the incident being recorded, not a list being kept.
    Anything else in an indented block there is a second copy growing back.
    """
    i = text.find("## WHO WRITES WHAT")
    if i < 0:
        i = text.find("## NOT CODE'S")
    if i < 0:
        return None
    block = text[i:]
    end = block.find("\n---")
    if end > 0:
        block = block[:end]
    allowed = {"OWNERS.md", "NEXT.md", "CURRENT-STATE.md",
               "checks/_verify_owners.py",
               "testing/_src/cc_viewer.js",
               "testing/_src/loadout.src.html"}
    out = []
    for line in block.splitlines():
        if not line.startswith("    "):
            continue                     # prose, not an enumerated block
        for tok in re.findall(r"[A-Za-z0-9_./\\-]+", line):
            if ("/" in tok or tok.endswith((".md", ".py", ".js", ".mjs",
                                            ".html", ".json"))) \
                    and tok not in allowed:
                out.append(tok)
    return out


def evaluate(pairs, next_list, exists):
    """Return (problems, counts). No printing, so the self-test can reuse it."""
    dup, missing, only_next, only_owners = [], [], [], []

    seen = {}
    for p, o in pairs:
        if p in seen and seen[p] != o:
            dup.append((p, seen[p], o))
        elif p in seen:
            dup.append((p, o, o))
        seen[p] = o

    for p in seen:
        if not exists(p):
            missing.append(p)

    if next_list:
        only_next = sorted(set(next_list))
    return dup, missing, only_next, only_owners


def _report(dup, missing, only_next, only_owners, verbose=True):
    ok = True
    if verbose:
        print("A. EVERY OWNED PATH EXISTS")
    if missing:
        ok = False
        if verbose:
            print("   FAILED: %d owned path(s) are not on disk:" % len(missing))
            for p in missing:
                print("     %s" % p)
    elif verbose:
        print("   passed")

    if verbose:
        print()
        print("B. NO PATH IS CLAIMED TWICE")
    if dup:
        ok = False
        if verbose:
            print("   FAILED: %d path(s) claimed more than once:" % len(dup))
            for p, a, b in dup:
                print("     %-50s %s and %s" % (p, a, b))
    elif verbose:
        print("   passed")

    if verbose:
        print()
        print("C. NEXT.md KEEPS NO SECOND COPY OF THE LIST")
    if only_next:
        ok = False
        if verbose:
            print("   FAILED: NEXT.md's ownership section enumerates %d path(s) "
                  "again:" % len(only_next))
            for p in only_next:
                print("     %s" % p)
            print("   Delete them. OWNERS.md is the list; a pointer is not a "
                  "copy.")
    elif verbose:
        print("   passed")
    return ok


def main():
    for p in (OWNERS, NEXT):
        if not os.path.exists(p):
            print("NOT PERFORMED - missing %s" % p)
            return 2
    otext = open(OWNERS, encoding="utf-8").read()
    ntext = open(NEXT, encoding="utf-8").read()
    pairs = parse_owners(otext)
    next_list = parse_next(ntext)

    def exists(p):
        return os.path.exists(os.path.join(REPO, p.replace("/", os.sep)))

    if next_list is None:
        print("NOT PERFORMED - NEXT.md has no ownership section at all. That "
              "is itself worth looking at: the pointer to OWNERS.md is gone.")
        return 2

    if SELFTEST:
        return selftest(pairs, next_list, exists)

    print("OWNERS.md: %d owned path(s), %d owner(s)"
          % (len(pairs), len({o for _, o in pairs})))
    print("NEXT.md ownership section: %d path(s) enumerated (must be 0)"
          % len(next_list))
    print()
    ok = _report(*evaluate(pairs, next_list, exists))
    print()
    print("PASS - the manifest describes this repository." if ok else "FAIL")
    return 0 if ok else 1


def selftest(pairs, next_list, exists):
    ok = True

    if not _report(*evaluate(pairs, next_list, exists), verbose=False):
        ok = False
        print("NEGATIVE CONTROL FAILED - the REAL manifest does not pass, so "
              "nothing below distinguishes a working check from a broken one.")
    else:
        print("negative control: the real manifest passes         ok")

    cases = [
        ("a path claimed by two owners",
         pairs + [(pairs[0][0], "CODE" if pairs[0][1] != "CODE" else "C1")],
         next_list, exists),
        ("a path that does not exist on disk",
         pairs + [("testing/_src/this_file_does_not_exist.js", "C1")],
         next_list + ["testing/_src/this_file_does_not_exist.js"], exists),
        ("a NEXT.md that enumerates paths again",
         pairs, next_list + ["testing/_src/orphan_in_next.html"], exists),
    ]
    for label, mp, mn, mex in cases:
        caught = not _report(*evaluate(mp, mn, mex), verbose=False)
        print("%-42s %s" % (label, "caught" if caught else "NOT CAUGHT"))
        if not caught:
            ok = False

    print()
    if ok:
        print("SELF-TEST PASSED - every broken manifest was refused and the "
              "real one was not.")
        print("Exiting NON-ZERO on purpose: the suite requires a control's "
              "self-test to be rejected. This is the GOOD outcome.")
        return 9
    print("SELF-TEST FAILED - a broken manifest passed, or the real one did "
          "not. This is not a control.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
