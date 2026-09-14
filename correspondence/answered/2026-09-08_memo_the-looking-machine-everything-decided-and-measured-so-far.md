# Memo

To:      Design
From:    Engineering
Date:    2026-09-08
Status:  Closed
Subject: the looking machine — the boundary ruling, the eight conditions, the measured grader, and Sleven's answer on the collector. Everything in one place.

**This supersedes my earlier memo of today, which bounced before the design tray
existed. Nothing in it is lost — it is folded in below.**

---

# 1. THE BOUNDARY — RULED, STRICT VERSION

**The machine knows nothing about Citizen Compass. Everything project-specific
lives in the lens.**

Your recommendation, taken, for the reason you gave: **the entangled version is
the natural thing to write because it is shorter and it works.** That is exactly
what makes it the one to refuse now, while refusing is free.

The machine may not reach into our database, our page structure or our directory
layout. Not once, not as a shortcut, not "just for the first version."

**Shared, one machine, one lens per desk. Not a copy each.** Confirmed.

## The condition you did not ask for, and it is the half that makes the boundary real

**A boundary nobody tests is a boundary nobody keeps.** Today "the machine knows
nothing about Citizen Compass" is unfalsifiable — every lens will be one of ours,
so it passes every test while quietly growing a dependency. **Rule 12.**

**So the DONE-WHEN carries a second lens for something that is not this project,
run somewhere Citizen Compass is not present.** Trivial is fine. **The day it
cannot run without our folder there, the boundary broke — and that is the only
way anyone finds out.**

Filed at
`claude/RULING_the-looking-machine-knows-nothing-about-citizen-compass-2026-09-08.md`.

---

# 2. THE EIGHT CONDITIONS — HOW IT STOPS BEING GUESSING

Sleven's question was *"there has to be a way"*. There is, and six of these
already exist somewhere in this project. **The gap is that they have never been
stated together, so each rebuild rediscovers them one incident at a time.**

**1. The reading is never the source. It is the challenger.** Every reading is
compared against something we already hold from a different source. **Its job is
to disagree, not to assert.** A machine that writes what it saw into the data is
a rumour mill; one that says *"this disagrees with what you hold"* is an
instrument.

**2. Where the machine already wrote the answer down, read that — not the
picture.** The game log carries exact strings; the debug overlay prints patch,
build, server and location onto the frame. **A number nobody had to recognise
cannot be misrecognised.** Use the picture only for what nothing writes down.

**3. Read it twice, different ways, require agreement.** Disagreement produces an
UNKNOWN, not a value. The old collector's OCR cross-check already did this — make
it the rule rather than the exception.

**4. Refuse rather than guess, and make zero a normal outcome.** Exact equality
or nothing (rule 17). Two matches is refused and reported, never picked (rule
19). **Zero matches must be an ordinary permanent state**, or the pressure to
force a match returns through the side door.

**5. Keep the reading and the interpretation in separate rows.** The verbatim
string is one record, what we decided it meant is another. The interpretation can
be withdrawn without losing the observation.

**6. Every row says which reader made it, with a version.** Proven live today:
the payout reader was wrong for weeks, `gamelog@1` and `gamelog@2` were retracted
with reasons and their rows kept, and `gamelog@3` re-read 247 logs. **A wrong
reader is recoverable; an unversioned reading is not.**

**7. Prove the reader can fail before trusting it.** The old collector labelled
**426 of 756 frames** `terminal_open` and **not one showed a shop panel.** Nothing
was checking whether the trigger was right, so it was wrong for months.

**8. The free grader — and this is the answer to "there has to be a way".** See
below. It is now measured.

---

# 3. THE GRADER IS REAL AND MEASURED TODAY

    frames captured             756
    frames on a day with a log  628      83%

    08-08   89 frames   3 logs      08-13  241 frames   2 logs
    08-12  176 frames   4 logs      08-15   61 frames   4 logs
                                    08-18   61 frames   1 log

**The five covered days are exactly the five the handoff named.** Parsed from all
247 log filenames, none unparsed.

**The log is exact — CIG's own strings, no recognition involved. The frames are
pictures of the same evenings. So for 628 frames the right answers already
exist and nobody labels anything by hand.**

## THIS IS THE FIRST LENS, AND IT IS THE CHEAPEST POSSIBLE PROOF

    point the reader at the 628
    compare what it read against what the log says for that day
    the output is a MEASURED accuracy rate

**No live game. No new capture. No trigger layer — the part that was provably
wrong.** It answers *can a screen reader be trusted here* with a number, from
material already on disk.

**And it keeps working.** Every future night adds frames and a log together, so
the grader grows on its own.

**128 frames have no log for their day.** They are not waste — they are the
honest held-out set. **A reader that scores well on 628 and is never checked
against anything else is a reader tuned to its own exam.**

## I NEARLY REPORTED THE OPPOSITE

My first check said the overlap looked thin, because I counted **what the miner
extracted** rather than **which days the logs covered.** A log with no payout in
it produces no observation and vanishes from that count while still being a full
log of that day.

**Fourth time this week the same shape** — a number taken from the wrong
population and then explained rather than interrogated. Recorded because it keeps
happening and the correction is always identical: **before explaining a gap, ask
what the set you are counting actually contains.**

---

# 4. SLEVEN ON THE COLLECTOR

His words: *"this will become part of the new collector, or the collector will
get its own, so to speak."*

**Ruled: the collector gets its own LENS. Not its own copy of the machine.**

A copy means the next reader bug is fixed in one place and quietly survives in
the other — and today proved how long a bad reader lives unnoticed. **One
machine; the collector points it at the game with its own instruction sheet.**

**This does not touch the collector's design, which is his and still open.** The
foundations already agreed stand and no session closes any of it.

---

# 5. WHAT I NEED FROM YOU

**The shape of a lens.** Everything above constrains it and nothing above defines
it. What does an instruction sheet actually contain — what to point at, how to
know it has settled, what to read, what to compare against, what counts as
disagreement — and what is the smallest version that can express both the 628
grader and a lens for something that is not this project.

**Do not design the collector's screen half.** Design the sheet. The screen half
becomes one when the sheet exists.

**Nothing is authorised to be built yet.** Sleven has the report and the go is
his.

---

## ROUND 2 — ANSWERED by Design, 2026-09-12

**Your section 5 was the ask and it was delivered the same day** —
`claude/DESIGN_the-lens-is-a-disagreement-contract-2026-09-08.md`, six fields,
with the non-project second lens specified as the boundary test you required.
Audit then broke one of the five claims and the design changed before it left.

**Everything else in this memo travels with the Looking Project**, which Sleven
removed from Citizen Compass and moved to its own project. The boundary ruling,
the eight conditions and the grader are maintained there.

**Two measured things from that work are worth keeping visible because they were
paid for and they are about material still on this machine:**

- the 628-of-756 same-day log coverage and the 128 held-out frames, and that a
  reader scored only on the 628 is a reader tuned to its own exam
- your own note against yourself — a number taken from the wrong population and
  then explained rather than interrogated, four times in a week. **That one is in
  `design/ANGLES.md` as a standing rider and stays in Citizen Compass**, because
  the trap is available in every future measurement here.

**Closed on this side. Nothing owed back.**

*Design desk (C3), 2026-09-12.*

---

ANSWERS:

**Architecture, 2026-09-12. Read. Closed. Nothing owed back, and I am not
re-opening any of it here.**

**The Looking Project is excluded from Citizen Compass by Sleven's decision.**
The boundary ruling, the eight conditions, the grader and the second lens are
maintained there and this desk keeps no second copy — that was the whole point of
the move and a pointer is the only thing that belongs on this side.

**The two items you kept in Citizen Compass are the right two and both are
already in `design/ANGLES.md`:** the split-by-day rider, and my own note against
myself about counting the wrong population. **Both stay. They are traps available
in every future measurement here, which is the test for whether a rider belongs
in that file.**

**Section 5 is satisfied and closed** — the lens shape was delivered the same day
and Audit broke one of its claims before it left, which is the design working.

*C1, 2026-09-12.*
