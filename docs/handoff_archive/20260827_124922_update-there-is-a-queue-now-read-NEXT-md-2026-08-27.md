# Update — there is a queue now. `NEXT.md` at the repo root.

**C1, 2026-08-27 13:02 local. Protocol change, effective immediately.**

**Sleven:** *"I keep just letting Code pick his work because you're not giving
me stuff for him... a simple thing of, hey, check the updates, and he knows what
is next on the list."*

He is right and it was costing him. You have been choosing your own work and
choosing it well — M4 beat its brief, the scale fix shipped with a control that
fails on the real defect, P4e/P4f is the best check in the repo — but you should
not have to construct the board before you can work on it, and he should not
have to interrupt whatever he is doing to hand you one.

## The protocol

**`NEXT.md` at the repo root. C1 is its only writer — you never edit it.**

When you finish a unit of work:

1. Read `NEXT.md`.
2. Take the FIRST item whose DONE-WHEN is not satisfied and whose BLOCKED-BY is
   clear.
3. Report before you write, rule 5. Then do it.
4. File your handoff as usual.
5. Back to `NEXT.md`.

**Every item carries a DONE-WHEN you can evaluate yourself.** That is the whole
design: if C1 is mid-task or simply wrong, the queue still advances. **A stale
queue is a normal condition, not an error — if the top item is already done, say
so and take the next one.** Never stop and wait for the file to catch up.

**If an item is wrong, ambiguous, or badly prioritised, say so and take the next
one.** You have been right against C1 three times today. The list exists so you
do not have to build it, not so it can overrule you.

**Anything not on the list and not asked for by Sleven directly is a suggestion,
not work. File it as one.**

## Right now

**Q1 is DEPLOY, and it is the only thing that matters until it is done.** The
payload is built, correct, and not uploaded — 510 markers on CIG's own
coordinates, P1e, and the 19 rescaled models are all sitting there where Sleven
cannot see them.

Q2 through Q8 follow, with Q3 doubling as a free check on your own rescale.

*C1*
