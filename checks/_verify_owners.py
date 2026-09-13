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
  D. EVERY CLAIM IS IN AN OWNER SECTION, AND READABLE - added 2026-09-13, below.

THE PARSER WAS PASSING ON A SUBSET, 2026-09-13 - FOUND BY READING ITS OUTPUT.
Two defects, measured before this change:

  1. ANY `## WORD` heading opened an owner section, so five paths under
     "## THE ELEVEN UNOWNED PATHS" came back owned by a desk called `THE`.
  2. A path line followed by a description was not parsed at all - 22 of them,
     C1's own entries among them. So A and B never looked at those paths.

Architecture's ruling (`..._four-rulings-owners-parser-routing-basis-...`),
SHAPE (a): an owner section opens ONLY at the three owner headings - `## C1`,
`## CODE`, `## SLEVEN` - and EVERY other `##` closes it; a path line may carry a
description after two spaces. `###` subheadings stay inside their section.

A PATH LOOKS LIKE A PATH. Allowing descriptions let prose words in indented
lines ("why", "fonts", "legal") read as paths on the first run. A path here has
a `/` or a `.` in it; a bare word is prose. Stated, not inferred (rule 17).

AND D, BECAUSE (a) ALONE WOULD HIDE CLAIMS INSTEAD OF SURFACING THEM:
  - STRAY: a path line inside a note section ("A NOTE ON ... CLAIMED ...") is a
    claim written in prose. Under (a) it is no longer read as ownership, so D
    lists every such path that no owner section also claims.
  - UNREADABLE: a path followed by ONE space and more text is readable by
    neither shape (`testing/_src/inject_engine.py build tooling ...`). It is
    listed, not dropped - dropping it silently is the defect this replaced.
Architecture moves them in one pass. EXPECTED RED ON FIRST RUN, BY RULING: "a
control that goes green because it never looked is worse than one that goes
red because it did."

RULE 12 - THE CONTROL. `--self-test` parses a PLANTED manifest and requires
every defect to be caught - the parser defects included - and a planted CLEAN
manifest to pass. It runs before any file is read, so it needs neither
OWNERS.md nor NEXT.md. The negative control used to be the real file; it is
planted now, because the real file is the subject of D and is expected to be
red until Architecture's pass, and a self-test must not depend on the state of
the thing it tests.

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

# A path line: four spaces, a path, then nothing - or two spaces and a description.
PATH = re.compile(r"^\s{4}([A-Za-z0-9_./\\-]+)(?:\s{2,}\S.*)?\s*$")
# A path followed by ONE space and text: readable by neither shape.
ONE_SPACE = re.compile(r"^\s{4}([A-Za-z0-9_./\\-]+) \S")
# Shape (a): only these three headings open an owner section.
OWNER = re.compile(r"^##\s+(C1|CODE|SLEVEN)\b")
# Every other level-two heading closes it. `###` does not match (no space at 3).
ANY_H2 = re.compile(r"^##\s")


def looks_like_path(tok):
    return "/" in tok or "." in tok


def parse_owners(text):
    """-> [(path, owner)], in file order. Duplicates are NOT collapsed."""
    owner, pairs = None, []
    for line in text.splitlines():
        if ANY_H2.match(line):
            m = OWNER.match(line)
            owner = m.group(1) if m else None
            continue
        m = PATH.match(line)
        if m and owner and looks_like_path(m.group(1)):
            pairs.append((m.group(1), owner))
    return pairs


def stray_claims(text):
    """-> [(line_no, section, path, why)]: claims D refuses.

    'stray'      a path line outside any owner section, claimed by no owner section
    'unreadable' a path line with ONE space before its description, anywhere
    """
    owned = {p for p, _o in parse_owners(text)}
    section, out = "(before the first heading)", []
    for n, line in enumerate(text.splitlines(), 1):
        if ANY_H2.match(line):
            section = "" if OWNER.match(line) else line[3:].strip()
            continue
        u = ONE_SPACE.match(line)
        if u and looks_like_path(u.group(1)) and u.group(1) not in owned:
            out.append((n, section or "an owner section", u.group(1), "unreadable"))
            continue
        if not section:
            continue
        m = PATH.match(line)
        if m and looks_like_path(m.group(1)) and m.group(1) not in owned:
            out.append((n, section, m.group(1), "stray"))
    return out


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


def evaluate(pairs, next_list, exists, stray=()):
    """Return (problems...). No printing, so the self-test can reuse it."""
    dup, missing, only_next = [], [], []

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
    return dup, missing, only_next, list(stray)


def _report(dup, missing, only_next, stray, verbose=True):
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

    if verbose:
        print()
        print("D. EVERY CLAIM IS IN AN OWNER SECTION (## C1 / ## CODE / ## SLEVEN), AND READABLE")
    if stray:
        ok = False
        if verbose:
            print("   FAILED: %d path line(s) no owner section holds in a readable form:"
                  % len(stray))
            for n, section, p, why in stray:
                print("     line %-5d %-10s %-44s under: %s" % (n, why, p, section[:56]))
            print("   stray      = in a prose section; move it into its owner's section")
            print("   unreadable = one space before its description; shape (a) needs two")
            print("   Architecture's one pass. A claim in prose is discouragement.")
    elif verbose:
        print("   passed")
    return ok


def main():
    if SELFTEST:
        return selftest()
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

    print("OWNERS.md: %d owned path(s), owners %s"
          % (len(pairs), sorted({o for _, o in pairs})))
    print("NEXT.md ownership section: %d path(s) enumerated (must be 0)"
          % len(next_list))
    print()
    ok = _report(*evaluate(pairs, next_list, exists, stray_claims(otext)))
    print()
    print("PASS - the manifest describes this repository." if ok else "FAIL")
    return 0 if ok else 1


PLANT = """intro line, before any heading
    why
## C1 — Cowork. The only Cowork session that writes repository ARTIFACTS.
    a/one.md
    b/two.py                      a description after two spaces
    h/eight.py a description after ONE space
### a subsection stays inside C1
    c/three.js
## THE ELEVEN UNOWNED PATHS, RESOLVED
    d/four.py
## CODE — Claude Code, on the Windows machine.
    e/five.go
## A NOTE ON SOMETHING, CLAIMED 2026-08-30
    f/six.md                      claimed here, in prose
    a/one.md                      repeated, and already owned
    fonts
## SLEVEN — his alone
    g/seven.md
"""
CLEAN = """## C1 — Cowork
    a/one.md
    b/two.py                      described
## A NOTE ON SOMETHING
    a/one.md                      a repeat of an owned path is not a claim
    legal
## CODE — Claude Code
    e/five.go
"""


def selftest():
    ok = True
    everything = lambda p: True                       # noqa: E731
    pairs = parse_owners(PLANT)
    owners = {o for _p, o in pairs}
    paths = [p for p, _o in pairs]
    stray = stray_claims(PLANT)
    stray_paths = sorted(p for _n, _s, p, why in stray if why == "stray")
    unreadable = [p for _n, _s, p, why in stray if why == "unreadable"]

    checks = [
        ("no heading but the three opens a section (no desk 'THE')",
         owners == {"C1", "CODE", "SLEVEN"}),
        ("a path with a description after two spaces is parsed",
         "b/two.py" in paths),
        ("a ### subheading does not close the owner section",
         ("c/three.js", "C1") in pairs),
        ("a path under a non-owner ## is not owned by anybody",
         "d/four.py" not in paths),
        ("every other ## closes the section (the note's path is not C1's)",
         "f/six.md" not in paths),
        ("D lists the claims in prose sections, and only those",
         stray_paths == ["d/four.py", "f/six.md"]),
        ("D does not list a prose repeat of an owned path",
         "a/one.md" not in stray_paths),
        ("a bare prose word ('why', 'fonts') is not a path",
         "why" not in stray_paths and "fonts" not in stray_paths),
        ("a one-space description is listed UNREADABLE, not dropped",
         unreadable == ["h/eight.py"]),
    ]
    for label, good in checks:
        print("%-66s %s" % (label, "caught" if good else "NOT CAUGHT"))
        ok = ok and good

    clean_ok = _report(*evaluate(parse_owners(CLEAN), [], everything,
                                 stray_claims(CLEAN)), verbose=False)
    print("%-66s %s" % ("negative control: a planted CLEAN manifest passes",
                        "ok" if clean_ok else "FAILED"))
    ok = ok and clean_ok

    cpairs = parse_owners(CLEAN)
    cases = [
        ("a path claimed by two owners",
         cpairs + [("a/one.md", "CODE")], [], everything, []),
        ("a path that does not exist on disk",
         cpairs, [], lambda p: p != "e/five.go", []),
        ("a NEXT.md that enumerates paths again",
         cpairs, ["testing/_src/orphan_in_next.html"], everything, []),
        ("a claim living in a prose section",
         cpairs, [], everything, [(9, "A NOTE", "f/six.md", "stray")]),
    ]
    for label, mp, mn, mex, ms in cases:
        caught = not _report(*evaluate(mp, mn, mex, ms), verbose=False)
        print("%-66s %s" % (label, "caught" if caught else "NOT CAUGHT"))
        ok = ok and caught

    print()
    if ok:
        print("SELF-TEST PASSED - every broken manifest was refused and the "
              "clean one was not.")
        print("Exiting NON-ZERO on purpose: the suite requires a control's "
              "self-test to be rejected. This is the GOOD outcome.")
        return 9
    print("SELF-TEST FAILED - a broken manifest passed, or the clean one did "
          "not. This is not a control.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
