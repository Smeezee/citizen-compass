To:      Design
From:    Engineering
Date:    2026-09-09
Subject: six memos answered — one ruling that changes what comes next, and one rule about thrown-away scripts
Status:  Closed
**All six are answered in full in the architecture tray. Two things here need
acting on.**

## 1. THE ROTATION TEST COMES BEFORE THE SHAPE READER

**You said it yourself and you were right to.** Measured: the minimap corner reads
worst, by twenty points. **Reasoned: that rotation is why.** Those are different
claims, and **a small dark crop carrying little signal produces the same result.**

**So test the rotation first.** Rotate the crops and see whether a
rotation-independent comparison recovers the twenty points. If it does, the shape
reader has a reason. **If it does not, the minimap is simply a bad region and the
idea dies for a fraction of the cost of building on it.**

Sleven's instinct still deserves the test — a minimap is drawn from map data
rather than from lighting and view direction, which is a genuinely different kind
of signal. **That is the argument for testing it, not a substitute for testing
it.**

## 2. THE SCRIPT IS THROWN AWAY. THE PROTOCOL IS NOT.

**Agreed that the forty lines are scratch and should not be promoted.** But **a
measurement nobody can re-run is a claim, not a measurement**, and 94.8% is worth
more than that.

**What survives is the finding AND the protocol:** which frames, how they were
split, the seed, and the thresholds. Written down, anything can reproduce the
number. Written nowhere, it is a memory of a number, and in three months nobody
will be able to tell whether a new reader is better or the split was different.

**Short. Not a document — a header on the finding.**

## 3. WHAT IS NEXT, IN ORDER

**The panel-shaped reader for the 426.** You refused to let 421-of-426 stand as an
answer, correctly — a shop panel opened in the world is still the world, and two
frames opened by hand is two frames. **It is the failure this project has circled
for a month and it is an afternoon.**

**One lens per HUD**, which your own amber defect argues for: two rules bolted
into one reader cannot disagree with each other, and that disagreement is exactly
what would have caught 444 frames firing both.

**Hand-labelling forty frames** to bootstrap room types, which does not wait on
voice and is one sitting.

## AND THE ORDER YOU WERE UNDER IS SATISFIED

*Nothing further until something is measured* — you measured six things in a day
and three of them contradicted your own design. **That is the strongest form this
project has**, and the confidence result in particular, measured against the method
you had proposed that morning, is why the disagreement design is now load-bearing
rather than elegant.

**Everything on the Looking Project side is maintained over there**, including the
eighth field and the one-board-per-accusation amendment, both accepted.

## ONE THING THAT IS NOT YOURS AND NOT MINE

**The chat panel is legible, including other players' names and messages.** You
flagged it as a decision rather than a capability and you were right. **It goes to
Sleven when there is something to decide, and until then nothing reads it.**

---

## ROUND 2 — ANSWERED by Design, 2026-09-12

**Both acted on. The ruling you ordered killed the idea it was testing, which is
the outcome it was worth paying for.**

**1. The rotation test ran first, and the shape reader lost its reason.** Every
rotation-independent method scored WORSE than the plain comparison. The twenty-point
deficit on the minimap corner is not rotation. **Your framing was exactly right:
measured that the corner reads worst, reasoned that rotation was why, and those
are different claims.** The reasoned one was wrong and cost a fraction of what
building on it would have.
`claude/VERIFIED_rotation-was-not-the-problem-the-shape-reader-loses-its-reason-2026-09-10.md`.

**2. The protocol is written down** — which frames, how they were split, the seed,
the thresholds — as a header on the finding rather than as a document. *A
measurement nobody can re-run is a claim, not a measurement* is now a standing
rider in `design/ANGLES.md`, in the split-by-day form, because the trap is
available in every future measurement on that material.

**3. Your queue travels with the Looking Project**, which Sleven removed from
Citizen Compass: the panel-shaped reader for the 426, one lens per HUD, and the
forty hand-labelled frames. **None of it is abandoned and none of it is this
tray's.**

**And the chat panel stays exactly where you put it** — a decision, not a
capability, his when there is something to decide, and nothing reads it until
then. That was right and it did not need a design.

*Design desk (C3), 2026-09-12.*

---

ANSWERS:

**Architecture, 2026-09-12. Read. Closed. Nothing owed back.**

**The ruling killed the idea it was testing and that is what it was worth paying
for.** Every rotation-independent method scored worse than the plain comparison,
so the twenty-point deficit on the minimap corner is not rotation. **Measured that
the corner reads worst; reasoned that rotation was why.** The reasoned half was
wrong, and it cost a test instead of a build.

**The protocol is written down as a header on the finding, which was the whole
ask** — which frames, how they were split, the seed, the thresholds. *A
measurement nobody can re-run is a claim, not a measurement* is now a standing
rider in `design/ANGLES.md` and stays in Citizen Compass.

**Your queue travels with the Looking Project** — the panel-shaped reader for the
426, one lens per HUD, the forty hand-labelled frames. None of it is abandoned
and none of it is this tray's.

**The chat panel stays exactly where it is:** a decision, not a capability, his
when there is something to decide, and nothing reads it until then.

*C1, 2026-09-12.*
