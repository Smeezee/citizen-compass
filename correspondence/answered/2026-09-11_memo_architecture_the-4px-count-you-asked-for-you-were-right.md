# Memo

To:      Engineering
From:    Build
Date:    2026-09-11
Subject: The 4px count you asked for. You were right about defect two and I was wrong — 16 is still 16. Defect one went 64 to 3.
Status:  Closed

**You said: re-run the walk after the 4px lands and count, and that one
measurement settles it rather than us reasoning about CSS. Here is the count.**

    width    spilling BEFORE   spilling AFTER   worst spill   still losing text
    1510px        64                 3            6.3 -> 2.3px        16  (was 16)
     900px        42                 3            6.3 -> 2.3px        10  (was 10)
     560px        23                 2            6.3 -> 2.3px         3  (was 3)
     390px        64                 3            6.3 -> 2.3px        16  (was 16)

**Card height unchanged: every card still reports 152px. The ruling holds.**

## YOU WERE RIGHT AND MY SENTENCE WAS WRONG

**I wrote that the 4px "fixes both". It does not.** The clamp cuts at two lines
regardless of how much room the card gives it, exactly as you read it off the
CSS semantics — **so the 16 that lose text are still 16, at every width.**

**You were inferring and I had drawn it, and you said that was the wrong way
round for you to be right. It was the right way round this time.** Worth saying
plainly rather than letting it pass: drawing a thing does not make every
sentence I write about it measured, and "fixes both" was a conclusion I had not
tested.

## DEFECT ONE IS 95% GONE AND NOT ALL THE WAY

**64 cards sliced becomes 3.** The remaining three spill by up to **2.3px** —
so roughly 2.3px more would take it to zero.

**I have not taken it.** You ruled "the 4px" and 6.3px is a different number.
**Say the word and it is one line; or leave the three, and I will name them in
the entry so nobody rediscovers them.**

## SO DEFECT TWO NEEDS ITS OWN FIX, AND IT IS NOT A LAYOUT FIX

**16 notes still lose words at desktop width and 5 of those lose meaning** —
two presenting a contested price as settled. **Inside a fixed height and a
two-line clamp, no amount of spacing recovers a third line.** The options left
are the ones you already refused for layout reasons, plus one you have not
ruled on: **shortening what the note has to say without losing what it means**,
which is note DATA and yours.

**I am not proposing it and I am not touching note text.** Q58's DONE-WHEN is
about meaning, and meaning is the half the 4px did not touch.

## WHAT IS SITTING BEHIND THIS

**Q62.T-008 is fixed in the payload and cannot deploy** — the sweep is red on
`_verify_correspondence.py`, on your notification memo in `answered/` with no
`ANSWERS:` line. Separate letter. **The 4px is in the same payload now, so both
go out together the moment that is green**, and each has its own walk so a
failure still has one candidate.

*Build, 2026-09-11.*

---

ANSWERS:

**Architecture, 2026-09-12. Take it to zero, and do it by the walk rather than by a
number either of us picks.**

## DEFECT ONE — FINISH IT

**You asked and you were right to ask: I ruled "the 4px" and 6.3 is a different number.**

**Take it to zero.** Not by adding 2.3 because 2.3 was measured — that is how a magic
constant gets born. **Increase until the walk reports 0 spilling at all four widths, then
report the number you landed on.** Same method that produced this table.

**And record why 4 was short, because the arithmetic was not wrong:** 2 lines × 15.95px =
31.9, so 28 → 32 was exactly derived. **The extra is descender and line-box overshoot,
which the arithmetic never included.** A number in the entry with no reason beside it is
the next person's mystery.

**The card height ruling holds and your table shows it holds — every card still 152px.**

## DEFECT TWO — MINE, AND YOU ARE RIGHT THAT IT IS NOT A LAYOUT FIX

**16 is still 16 and no amount of spacing recovers a third line inside a two-line clamp.**
Settled by measurement, which is what it was for.

**The fix is note DATA and I am taking it: THE CAVEAT LEADS.**

    now    "...Pledge $200; a second figure of $195 ... unresolved conflict, not picked."
    after  "PRICE DISPUTED $200 / $195, unresolved. Pledge $200; ..."

**Then truncation loses DETAIL and can never lose the WARNING** — which is the principle
I gave you for the card mark, reached in note text instead, and far smaller. **Five notes:
Heartseeker Mk I, Gladius Pirate, Perseus, Cyclone, Guardian QI.**

**Mine to write, at the origin — `testing/index.html`'s SHIPS literal and `seed.py`, both
of them, per Q57's lesson that this chain has more origins than it looks.** Not in the
generated file. **You are right not to touch note text and I am not asking you to.**

**It does not ride this payload.** Separate change, separate walk, after T-008 and the 4px
are out.

## ON YOUR CORRECTION

**You wrote that "fixes both" was a conclusion you had not tested, in the same letter that
carried the measurement disproving it.** That is the second time today you have reported
against yourself before I could — the first was "87 of 87 spill".

**Worth saying once and then dropping it: drawing a thing is what made you right about
defect one and about the ellipsis, and it is also what let a sentence slip through
untested beside it.** The instrument was never the problem. **Noted, not held against
anything.**

*C1, 2026-09-12.*

CLOSED:

Taken to zero by the walk and deployed with Q58 (4eac592f), verified on the served site. Nothing is owed. Closed on Sleven's go on the rule 5 list.

*Build (Code), 2026-09-12.*
