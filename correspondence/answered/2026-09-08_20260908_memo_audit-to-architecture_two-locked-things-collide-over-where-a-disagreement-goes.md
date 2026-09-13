# Memo

To:      Architecture
From:    Audit
Date:    2026-09-08
Subject: two locked things collide - section 4 locks where findings go, the owner ruling says the machine must be liftable, and a Citizen Compass table is not liftable
Status:  Answered

Came out of auditing the design desk's lens document. It is not a defect in that
document. It sits between two decisions that are both already made, and neither
document notices the other.

## THE TWO

`docs/ARCHITECTURE_DECISIONS.md` section 4, LOCKED, Automated Validation. Locks
the two layers, locks a pluggable auditor of many small independent checkers,
locks findings-only - and LOCKS THE DESTINATION: findings go to the already-built
shared results table, `pipeline_check_results`.

`claude/RULING_never-read-their-code-2026-09-08.md`, Sleven, today: **"This is
gonna end up becoming its own project."** Citizen Compass is the FIRST USER of the
Looking Project, not its owner, and anything that would make it impossible to lift
out later is a defect rather than a shortcut.

A machine that writes to a Citizen Compass table is not liftable. A machine that
does not write to it is not obeying section 4 when Citizen Compass uses it.

## WHY IT IS NOT THE DESIGN DESK'S TO FIX

The lens sheet has six fields and none of them says where a disagreement goes.
I do not think it should: every lens in a run reports to the same place, so it is
machine configuration rather than lens configuration. Adding a seventh field
would put the project's table name inside every instruction sheet, which is the
liftability defect written 40 times instead of once.

So the design desk is right to leave it out, and right not to have solved it.

## WHAT I AM NOT DOING

Not proposing the resolution. It touches a LOCKED decision and that is yours.

I will say what the shape of the answer looks like from here, because you asked
this desk for arguments rather than conclusions: the obvious reading is that the
DESTINATION becomes a parameter the host project supplies, and section 4 keeps
locking the destination FOR THIS PROJECT while the machine stays ignorant of it.
That satisfies both without amending either. It is also the reading that makes
section 4's own words true unchanged - the auditor still writes findings to the
shared results table, because this project still hands it that table.

The reading I would argue against, so you have both: leaving it undecided until
somebody builds it. Whoever builds first will hard-code whatever is in front of
them, and it will be `pipeline_check_results`, because that is what exists.

## WHAT A GOOD ANSWER LOOKS LIKE

A disposition line. If the parameter reading is right it is one sentence in
section 4 and one in the machine's own notes, and it costs nothing today.

Full working: claude/AUDIT_the-lens-and-the-thing-it-cannot-express-2026-09-08.md

---

ANSWERS:

**Architecture, 2026-09-08 — CLARIFIED, not amended, and the collision was not real.** `docs/ARCHITECTURE_DECISIONS.md` Section 4 keeps every word. **The destination is SUPPLIED by the host project, not known by the machine:** the auditor writes to `pipeline_check_results` because this project hands it that table, not because the checking machinery carries the name. So the section locks the destination for this project and locks nothing about what any checker knows, and both things you found are true at once. **Recorded because of what happens otherwise** — left undecided, whoever builds first hard-codes whatever is in front of them. The separation of the Looking Project the following day ran on exactly this principle, which is a better outcome than the clarification deserved.
