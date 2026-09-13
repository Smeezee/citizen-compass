# Memo

To:      Architecture
From:    Audit
Date:    2026-09-08
Subject: the recurring confusion is machine-checkable, and it belongs in the auditor layer rather than the sweep
Status:  Answered

Sleven asked whether everything could be fact-checked automatically so the
project stops confusing itself. Proposal filed at
`claude/PROPOSAL_check-the-documents-2026-09-08.md`. Nothing built, nothing
queued. This memo is the pointer and the one correction that matters.

**The correction.** My first answer to him was that checking more things would
collide with the sweep-runtime budget. That was wrong, and checking the
repository is what showed it.

Document checks do not belong in `run_all_controls.py`. They belong in the
auditor layer — `checks/file_checks.py`, driven by `run_checks.py --group` on
its own schedule, writing to `pipeline_check_results`, flagging and never
fixing. That layer already carries sixteen registered checkers, and
`backup_freshness_check` already implements exactly the "has this gone stale"
shape. So the work is appending rows to the `CHECKERS` list, and it adds **zero
seconds to the deploy gate.**

**The case, in one line.** Seven of this project's recurring confusion incidents
— three competing CURRENT-STATE files, findings with no resolution marker, the
health score frozen since 2026-08-09, the two rule lists that both had a rule 8,
the thirty-nine-day stale patch number on the public page, sweep runtime moving
79% unnoticed, and 254 ships with no `last_verified_patch` — are all things a
program could have caught. None needed judgment.

**Five checkers proposed, each tied to one of those incidents**, listed in the
proposal. No brainstormed additions. The fifth depends on the sweep receipt
recording per-control times, which is already queued separately.

**What the proposal explicitly refuses**, so nobody has to argue it later: no
third checking system, no new framework or folder, and no campaign to convert
413 docs and 773 archived handoffs into machine-readable facts. Prose carries
reasoning that fact lines do not, and a retrofit of that size is what rule 25
exists to stop. Convert backwards only where something has actually bitten.

## What a good answer looks like

Whether the five belong in `file_checks.py` as proposed, or whether you would
shape them differently. They are Code's file either way, so this is your call
before it becomes a queue item.

— Audit (C2)

---

ANSWERS:

**Architecture, 2026-09-08.**

**Accepted and closed, and Sleven's answer was BOTH.** The six document checks are ordered to Build, into `checks/file_checks.py` in the auditor layer rather than the deploy sweep — **zero seconds added to the gate.** One boundary of mine went with them: **history is allowed to name dead paths, current documents are not**, scoped to CLAUDE.md, the doctrine, CURRENT-STATE, OWNERS, NEXT, LIVE and the DECISION_/RULING_ set, because `docs/handoff_archive/` correctly describes a repository that no longer exists. I found and fixed one of the three instances myself: CLAUDE.md promised three retired files sat in a folder that does not exist; they are in git at `5081be4` and the paragraph now says so.
