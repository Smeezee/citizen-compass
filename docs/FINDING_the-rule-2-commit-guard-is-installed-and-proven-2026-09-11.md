# THE RULE 2 COMMIT GUARD — INSTALLED, AND PROVEN ABLE TO REFUSE

**Code, 2026-09-11. This is the evidence ruling 21 requires, not a description
of it.** The ruling's own words: *"No exception exists until the guard is
installed AND has refused a real path outside the set in a deliberate test"*,
and *"the recorded refusals are the artifact, not the guard's existence."*

    the guard      checks/commit_guard.py
    the hook       .git/hooks/pre-commit   (machine-local, untracked)
    the proof      _needs_review/guard_proof.py

---

## 1. THE FOUR RULED CASES, AGAINST A REAL `git commit`

**Run in a throwaway repository, never this one.** The real working tree carries
a day of uncommitted work and staging files to test a guard is a way to lose it.

    a .py file alongside a document      exit 1   REFUSED
    CLAUDE.md alone                      exit 1   REFUSED
    a document rename                    exit 1   REFUSED
    a document deletion                  exit 1   REFUSED
    two documents for one named item      exit 0   COMMITTED
    an empty index                       exit 1   REFUSED

**And the refusals left nothing behind.** The scratch repository ends with
exactly two commits — the base, and the one legitimate documentation commit — so
every refusal really did stop a commit rather than merely printing something.

**Each refusal names its reason**, e.g.
*"CLAUDE.md is permanently outside the exception - it needs his word every
time"*, and *"docs/b.md -> docs/renamed.md is a RENAME. The ruling excludes
renames - a rename is how a file leaves the documentation set without anybody
noticing."*

## 2. THE SET IS A RULE, NOT A LIST

Ruled, and the reason is the ruling's: *"a literal list of eight hundred
filenames is stale the first time somebody writes a new document, and stale is
how a guard starts passing what it should refuse."*

    IN     tracked .md under docs/, claude/, design/, correspondence/
           plus NEXT.md, LIVE.md, RECOVERY.md
    OUT    everything else, and permanently CLAUDE.md and OWNERS.md
    OUT    every rename and every deletion, whatever the path

A document written tomorrow is covered without anybody maintaining anything.

## 3. WHAT THE GUARD CANNOT SEE, SAID PLAINLY

**It cannot tell HOW something was staged**, so it does not enforce "staged by
name" or "one work item per commit". **Those remain human obligations under rule
2 and this guard does not pretend to cover them.** Saying so is the difference
between a guard and a guard people think is bigger than it is.

**It reads the index through `git diff --cached`** — the same thing the commit
is about to use — rather than any caller's account of what is being committed.

**It refuses when it cannot look.** No git, not a repository, or an unreadable
index exits 2 and refuses. It never returns "nothing wrong" because it failed to
find out.

## 4. THE CONSEQUENCE FOR EVERY OTHER COMMITTER, WHICH IS NOT A DETAIL

**The permission is Code's. A pre-commit hook is the tree's.** So anyone
committing in this working tree meets this guard, including Sleven committing
code by hand.

**`git commit --no-verify` passes it**, which is git's own bypass and is the
right escape for a human. **Code does not use that flag** — `CLAUDE.md` forbids
skipping hooks unless explicitly asked, and rule 2 binds Code whether or not a
hook is installed.

**Uninstalling is deleting one file**, `.git/hooks/pre-commit`. Nothing depends
on it existing.

## 5. WHAT THIS DOES NOT SWITCH ON

**`CLAUDE.md` does not yet carry the exception, so the rule file and the ruling
still disagree on paper.** The guard being proven does not change that by
itself.

**And the rule-file edit is excluded from the exception it creates** — *"a
permission that lets a desk commit the file containing the permission is not a
narrow permission."* It needs Sleven's own word, for that change, in his own
message. **A relayed clearance in a memo is not that, and this desk is not
treating it as one.**

*Code, 2026-09-11. Self-test: `python checks/commit_guard.py --self-test`.
End-to-end proof: `python _needs_review/guard_proof.py`.*
