# -*- coding: utf-8 -*-
"""The rule 2 documentation-commit guard.

WHAT THIS IS
============
Ruling 21 (2026-09-12) lets Code run `git commit` on documentation without
asking, and makes that permission conditional on THIS FILE being installed as a
pre-commit hook and having been PROVEN able to refuse. The rule text says so in
its own words:

    "If the guard is not installed, or cannot be shown to refuse, the exception
     does not apply and rule 2 stands unchanged."

So the recorded refusals are the artifact, not the guard's existence. A guard
that has only ever been seen passing is not a guard (hard rule 12).

THE SET IS A RULE, NOT A LIST - RULED, AND THE REASON IS IN THE RULING
======================================================================
"A literal list of eight hundred filenames is stale the first time somebody
writes a new document, and stale is how a guard starts passing what it should
refuse."

So: tracked `.md` under docs/, claude/, design/ and correspondence/, plus the
three named root documents. Anything else is refused, and a new document written
tomorrow is covered without anybody maintaining a list.

WHAT IT REFUSES, AND WHY EACH ONE
=================================
  a path outside the set        the whole point
  CLAUDE.md, OWNERS.md          permanently excluded by the ruling. "A
                                permission that lets a desk commit the file
                                containing the permission is not a narrow
                                permission."
  a rename or a deletion        the ruling excludes both. A rename is how a
                                file leaves the set without anybody noticing.
  a non-.md file under docs/    the directory does not make it a document

WHAT IT CANNOT SEE, STATED RATHER THAN IMPLIED
==============================================
It cannot tell HOW something was staged, so it cannot enforce "staged by name"
or "one work item per commit". Those stay human obligations under rule 2, and
this guard does not pretend to cover them. Saying so here is the difference
between a guard and a guard people think is bigger than it is.

RULE16: INDEPENDENT - it reads the git index through `git diff --cached`, which
is the same thing the commit is about to use. It does not consult the caller's
account of what is being committed.

Usage:
    python checks/commit_guard.py               # reads the staged set
    python checks/commit_guard.py --paths A B   # judges an explicit list,
                                                # staging nothing (for proofs)
    python checks/commit_guard.py --self-test   # the four ruled cases

Exit 0 = every staged path is inside the documentation set.
Exit 1 = refused, with the reason and the offending paths named.
Exit 2 = could not look (no git, not a repo). Refused, never passed.
"""
import os
import subprocess
import sys

DOC_DIRS = ("docs/", "claude/", "design/", "correspondence/")
DOC_ROOT_FILES = ("NEXT.md", "LIVE.md", "RECOVERY.md")
NEVER = ("CLAUDE.md", "OWNERS.md")


def in_doc_set(path):
    """True when `path` is inside the documentation set, by RULE.

    Returns (ok, reason_when_not).
    """
    p = path.replace("\\", "/").strip()
    if not p:
        return False, "empty path"
    if p in NEVER:
        return False, ("%s is permanently outside the exception - it needs his "
                       "word every time" % p)
    if p in DOC_ROOT_FILES:
        return True, None
    if not p.lower().endswith(".md"):
        return False, "not a .md file"
    for d in DOC_DIRS:
        if p.startswith(d):
            return True, None
    return False, ("not under %s and not one of %s"
                   % (", ".join(DOC_DIRS), ", ".join(DOC_ROOT_FILES)))


def judge(entries):
    """entries: (status, path) pairs, as `git diff --cached --name-status` gives.

    Returns a list of refusal strings. Empty list means the commit may proceed.
    """
    refusals = []
    if not entries:
        refusals.append("nothing is staged - refusing rather than passing an "
                        "empty commit through a guard that then proves nothing")
        return refusals
    for status, path in entries:
        s = (status or "").strip().upper()
        # A rename arrives as R### with two paths; the caller splits them out.
        if s.startswith("R"):
            refusals.append("%s is a RENAME. The ruling excludes renames - a "
                            "rename is how a file leaves the documentation set "
                            "without anybody noticing." % path)
            continue
        if s.startswith("D"):
            refusals.append("%s is a DELETION. The ruling excludes deletions, "
                            "and hard rule 1 says move aside rather than "
                            "delete." % path)
            continue
        ok, why = in_doc_set(path)
        if not ok:
            refusals.append("%s is outside the documentation set: %s" % (path, why))
    return refusals


def staged_entries(repo):
    """Read the index. Exits 2 if it cannot - never returns an empty list to
    mean 'nothing wrong'."""
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-status", "-z"],
            cwd=repo, capture_output=True, check=True)
    except Exception as exc:                      # noqa: BLE001
        sys.stderr.write("commit_guard: could not read the index (%s: %s). "
                         "Refusing.\n" % (exc.__class__.__name__, exc))
        sys.exit(2)
    parts = out.stdout.decode("utf-8", "replace").split("\0")
    entries, i = [], 0
    while i < len(parts):
        tok = parts[i].strip()
        if not tok:
            i += 1
            continue
        if tok.upper().startswith("R") and i + 2 < len(parts):
            # rename: status, old, new - both paths reported
            entries.append((tok, parts[i + 1] + " -> " + parts[i + 2]))
            i += 3
            continue
        if i + 1 < len(parts):
            entries.append((tok, parts[i + 1]))
            i += 2
            continue
        i += 1
    return entries


def report(refusals):
    if not refusals:
        return 0
    sys.stderr.write("\nCOMMIT REFUSED by the rule 2 documentation guard.\n\n")
    for r in refusals:
        sys.stderr.write("  - %s\n" % r)
    sys.stderr.write(
        "\nThe standing exception covers tracked .md files under docs/, claude/,\n"
        "design/ and correspondence/, plus NEXT.md, LIVE.md and RECOVERY.md -\n"
        "modifications and additions only.\n\n"
        "Anything else needs Sleven's word for that change, in that message.\n"
        "Rule 2 is unchanged for everything this guard refuses.\n\n")
    return 1


def self_test():
    """The four cases the ruling requires, judged without staging anything."""
    cases = [
        ("a .py file alongside a document",
         [("M", "docs/NOTE_example.md"), ("M", "checks/file_checks.py")], False),
        ("CLAUDE.md alone",
         [("M", "CLAUDE.md")], False),
        ("a document RENAME",
         [("R100", "docs/a.md -> docs/b.md")], False),
        ("a document DELETION",
         [("D", "docs/a.md")], False),
        ("two documents for one named item",
         [("M", "docs/FINDING_one.md"), ("A", "correspondence/open/build/x.md")], True),
    ]
    print("the rule 2 commit guard, driven both ways\n")
    bad = 0
    for label, entries, want_pass in cases:
        refusals = judge(entries)
        passed = not refusals
        ok = (passed == want_pass)
        print("  %-6s %-40s %s" % ("ok" if ok else "WRONG", label,
                                   "PASSED" if passed else "REFUSED"))
        if refusals and not want_pass:
            print("         %s" % refusals[0][:96])
        if not ok:
            bad += 1
    # and the guard must refuse an empty index rather than wave it through
    empty_ok = bool(judge([]))
    print("  %-6s %-40s %s" % ("ok" if empty_ok else "WRONG",
                               "an empty index", "REFUSED" if empty_ok else "PASSED"))
    if not empty_ok:
        bad += 1
    print("")
    if bad:
        print("SELF-TEST FAILED - %d case(s) went the wrong way. The guard must "
              "not be trusted." % bad)
        return 3
    print("SELF-TEST PASSED - every ruled case went the way the ruling says.")
    print("This proves the LOGIC. It does not prove the hook fires; that is "
          "proven separately against a real repository.")
    return 0


def main(argv):
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if "--self-test" in argv:
        return self_test()
    if "--paths" in argv:
        paths = argv[argv.index("--paths") + 1:]
        entries = [("M", p) for p in paths]
        return report(judge(entries))
    return report(judge(staged_entries(repo)))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
