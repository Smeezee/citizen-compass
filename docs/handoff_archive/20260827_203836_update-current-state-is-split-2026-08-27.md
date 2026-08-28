# Update — CURRENT-STATE.md is split. 13,571 words became 1,487, and nothing was deleted.

**2026-08-27 20:45 local · C1**

## Why

It opened by telling the reader that later sections were history **without
saying where that line was**. The only safe way to read it was all of it, every
session, forever — and it contradicted itself in places, because it had grown by
appending for three weeks. The collector section still said *"None of it has run
on Windows"* on the day your selftest passed 575 checks.

## What now exists

    docs/CURRENT-STATE.md                       1,487 words
    docs/STATE-ARCHIVE-through-2026-08-27.md   13,801 words - the original, verbatim

**Nothing was deleted.** The archive is the old file exactly as it was, with a
header naming its own known-stale parts so nobody has to find them the hard way.

**The new one has no "later section wins" rule because it has no later
sections.** It carries a maintenance rule instead: *it does not grow by
appending.* A fact that stops being true is edited or deleted there and the
reasoning goes in a dated `FINDING_` or `DECISION_`. A snapshot, not a log.

## What it says about your side

- The build is machine-bound and that is recorded as proven, not assumed
- `build_deploy.py` and the check suite are named as yours
- The eleven hard rules are in one list, including the ones that keep biting:
  no fuzzy matching, one writer per artifact, every check needs a control that
  could have failed it, ambiguity is refused rather than picked

Both files are also written to the claude.ai project, since the project
instructions point new sessions at `claude/CURRENT-STATE.md` rather than the
repo copy.

**If you disagree with anything it states as current, say so** — it is short
enough to argue with now, which was the point.

— C1
