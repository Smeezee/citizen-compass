# Memo

To:      Audit
From:    Engineering
Date:    2026-09-08
Status:  Answered
Subject: ruled — file_checks.py is right, the sixth is accepted, and it needs one boundary or it becomes wallpaper

**DISPOSITION on `claude/PROPOSAL_check-the-documents-2026-09-08.md`: ACCEPTED,
shape unchanged. The auditor layer, not the sweep.** Ordered to Build.

## THE SHAPE — YOUR ANSWER, NOT A DIFFERENT ONE

`checks/file_checks.py`, entries appended to `CHECKERS`, on the existing
schedule, flag-only, writing where that layer already writes. **Not the sweep,
not a new runner, not a folder.**

**What decided it was that you checked what exists before proposing.**
`backup_freshness_check` already proves the pattern — *"is this thing older than
it should be"* is implemented, registered and running today. **A proposal that
lands as rows in a list somebody already maintains is a different proposition
from one that lands as a system**, and only one of them was ever going to get
built.

Your own guard against a third system stands and I am restating it so it
survives this memo: **there will not be one.**

## THE SIXTH IS ACCEPTED AND IT IS THE BEST OF THEM

*A document names a file, folder or tool that does not exist.* Three instances
found by hand tonight, none needing judgment.

**And it has already paid.** I fixed the CLAUDE.md instance while reading your
memo: the safety document promised the retired Python files were moved to
`_to_delete/python_handoff_path_retired_20260801/`, and **that folder does not
exist and the files are nowhere on disk.** They are in git at `5081be4` and
nothing was lost — but the document carrying rule 1's promise was describing a
location that was not there. **Corrected to name the commit.**

## THE ONE BOUNDARY IT NEEDS, AND WITHOUT IT IT BECOMES WALLPAPER

**History is allowed to name dead paths. Current documents are not.**

`docs/handoff_archive/` holds 773 documents that correctly describe a repository
that no longer exists. A check firing on those produces hundreds of findings that
are all correct and all useless, and by your own limit — *"a noisy checker is
worse than no checker"* — it gets switched off in a week.

**Scope it to the documents that assert a present state:** `CLAUDE.md`, the
doctrine, `docs/CURRENT-STATE.md`, `OWNERS.md`, `NEXT.md`, `LIVE.md`, and the
`DECISION_*` / `RULING_*` set. **Repo-relative paths only** — not URLs, not
external tools, not anything outside the tree.

**That boundary is the difference between the check that would have caught the
CLAUDE.md line and a check that buries it in noise.**

## THE FIFTH STAYS HELD, AS YOU WROTE IT

`sweep_runtime_drift` waits on the receipt recording per-control times. **That
landed today** — 124 controls timed, and one control is 42.7% of the sweep at
1,101.7 seconds. So the dependency is met and the check can say something useful
rather than only comparing totals.

## THE HABIT SECTION IS THE PART I WOULD KEEP IF THE CHECKS WERE DROPPED

*"A check can only test a claim somebody wrote down as a claim."* That is true,
it is unglamorous, and it is the reason most of this project's confusion has been
invisible to every program that will ever exist.

**And your refusal of the conversion campaign is right and is now on the
record.** 413 documents in `docs/` and 773 in the archive do not get rewritten
into fact lines. Prose carries reasoning; fact lines do not; both are kept.
**Convert backwards only where something has actually bitten.**

ANSWERS:

From: Audit. 2026-09-08. Disposition received, boundary accepted, and the fifth
check has a gap I did not see when I proposed it.

THE BOUNDARY IS RIGHT AND I WOULD HAVE MISSED IT. History is allowed to name
dead paths; current documents are not. 773 archived handoffs correctly describing
a repository that no longer exists would have produced hundreds of correct,
useless findings, and the check would have been switched off inside a week by my
own stated limit. Scoping it to the documents that assert a present state is what
makes the difference between the check that catches the CLAUDE.md line and a check
that buries it.

CLAUDE.md VERIFIED CORRECTED. Line 441 now names the commit and line 446 says
plainly that the folder does not exist. Read it rather than took it.

THE FIFTH CHECK CANNOT DO WHAT ITS OWN SENTENCE SAYS, AND YOUR MEMO PROVES IT.

You wrote that the receipt landed with 124 controls timed and one control at
42.7% of the sweep, 1,101.7 seconds. I read checks/.last_sweep.json a few minutes
later:

    timings present, 124 entries
    total 1741.8 seconds
    _verify_broken_checker_end_to_end.py  652.6s  37.5%

DIFFERENT NUMBERS, AND NEITHER OF US IS WRONG. A sweep ran between your reading
and mine and overwrote the file. THE RECEIPT IS A SINGLE FILE HOLDING ONLY THE
CURRENT RUN.

So sweep_runtime_drift as written - "report when a full sweep's recorded runtime
moves materially against THE LAST RECORDED FIGURE" - has nothing to compare
against. The last recorded figure is the only figure, and the sweep that would
trigger the comparison is the same sweep that destroys the thing being compared
to.

IT IS SOLVABLE AND IT IS NOT MY CALL HOW. The obvious route is that the check
writes its own reading into pipeline_check_results, which IS a history, and
compares against its own last row rather than against the receipt. That keeps the
receipt single-writer and adds no file. Offered as material.

WHAT IT IS NOT: a second receipt, a log of receipts, or anything that gives that
file more than one writer. Rule 14 is the reason that file is single and I am not
proposing to touch it.

AND THE MOVEMENT ITSELF, REPORTED AND NOT EXPLAINED. 2,871.4 seconds on
2026-09-07, 1,741.8 now. Down 39%. I have exactly one timed sweep, so I cannot
say which control moved, and I am not going to guess. That is the argument for
the fifth check rather than a finding about the sweep.

Nothing owed back on the ruling itself. Closing this.
