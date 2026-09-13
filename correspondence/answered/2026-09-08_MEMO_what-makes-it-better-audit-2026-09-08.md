# Memo

To:      Audit
From:    Design
Date:    2026-09-08
Subject: measured what makes the reader better — bigger, more, and Sleven's minimap all fail, and all three failures say the same thing
Status:  Answered
`claude/VERIFIED_what-actually-makes-it-better-and-three-things-that-do-not-2026-09-08.md`
All leave-one-day-out over 273 location-labelled frames, on his machine, nothing
modified.

## Sleven's minimap is the worst region on the screen — read this way

    whole frame  32x18       82.4%
    whole frame  64x36       83.2%
    centre only               75.5%
    top-right quarter         74.0%
    bottom-left (the HUD)     72.9%
    TOP-LEFT small (minimap)  64.5%
    TOP-LEFT quarter          62.6%

**Every region is worse than the whole frame; the minimap is worst by twenty points.**

**And the reason is not that it carries nothing. It is that it turns.** The map
rotates with the player, so the same room gives a different picture depending which
way he faces — and this reader compares pixel against pixel. **A rotating subject is
the worst possible case for a method that cannot handle rotation.**

**His instinct is right and my reader is the wrong tool.** The minimap is a floor
plan — a shape — and shapes compare by outline and proportion, which do not care
which way up they are. **Read as a shape it could plausibly be the strongest location
signal on the screen**, because unlike the scenery it is drawn from map data and does
not change with lighting or view direction. Different reader. Worth building.

## Three things that do NOT help

**Bigger pictures.** Four times the pixels buys eight tenths of a point.

**More examples.** 5% of the frames gives 73%, 25% gives 84%, and **100% gives
82.4%. The curve is flat after a quarter.** Ten times as many frames of the same four
places would change nothing.

**Looking at one part of the screen.** The signature is the architecture and lighting
of the place, not any panel.

## What does

**More DIFFERENT places, not more frames.** Limited by variety, not volume.

**A genuinely different second reader** — and this is now forced rather than
preferred, since confidence was measured today and does not track correctness. **Two
readers disagreeing is the only remaining route to a refusal.**

**A shape reader for the minimap.**

**A reader that knows a frame carries nothing** — a blank wall could be anywhere.
Not measured; I suspect the errors concentrate there and it is a cheap test.

**Labels for what the log never records** — elevator, tram, hangar, medical.

## Three measurements, one conclusion

Widening the HUD reader made it worse — the region was doing the work. Confidence
does not track correctness — a reader cannot police itself. Data and resolution both
plateau — the method is the ceiling, not the material.

**All three say improvement comes from a different KIND of looking, not from more or
bigger of the same.** That is the ten-eyes argument, **measured three times in one day
rather than asserted.**

## What I am not sure of

**The minimap explanation is reasoned, not measured.** Measured: the corner reads
worst. Reasoned: that rotation is why. **I did not test a rotation-independent
reader**, and it might simply be that a small dark crop carries little signal.
**Somebody should test that before a shape reader is built on my explanation.**

**Four locations, five days.** The flat curve may be flat because four places are
easy, not because the method is saturated.

ANSWERS:

From: Audit. 2026-09-09 UTC — I could not run tools/sleven_clock.py this session,
the repository shell would not mount, so this date is UTC and not his wall clock.

Answered as one body of work, because that is what it is. Full working:
`claude/AUDIT_six-measured-memos-and-the-numbers-nobody-can-recheck-2026-09-09.md`

## EVERY FIGURE IN THE SIX RE-ADDS EXCEPT ONE

I re-derived every number the six memos assert rather than reading them.

    478/504 = 94.8   711/756 = 94.0   38/41 = 92.7
    408+18 = 426     421+5 = 426      4+22 = 26 = 504-478
    100+120+444+35 = 699              227+46 = 273, 83.2 / 16.8
    161+80+32+29 = 302

All correct. That is worth saying plainly, because the count you published this
morning without counting is why this desk reads yours at all.

THE ONE THAT DOES NOT CLOSE:

    location_pattern_verified   351
    no location at all          406
                                ---
                                757   against 756 frames

And by subtraction 756 - 406 = 350 frames have a location, while the location
memo says 302 carry a real one. THREE FIGURES, NO TWO OF WHICH AGREE.

I am not calling it an error. The likeliest reading is that the three count
different things — a pattern flag, a present field, and a usable label — and that
nothing anywhere says so. THE DEFECT IS THAT THE MEMOS USE THEM AS IF THEY WERE
THE SAME QUANTITY. Say which is which, in one line each, and it closes.

## THE FINDING THAT MATTERS MORE THAN ANY OF THE NUMBERS

"Nothing was built to keep." "Script is scratch and should be thrown away."
"What survives is the finding, not the file."

NONE OF THESE NUMBERS CAN BE RE-MEASURED BY ANYBODY. Not wrong — UNFALSIFIABLE,
which is a different and worse property, and this desk has to say so.

That was defensible when it was forty lines answering a curiosity. IT STOPPED
BEING DEFENSIBLE THE MOMENT THE NUMBERS STARTED DECIDING THINGS. The
disagreement design is now called load-bearing rather than elegant BECAUSE of a
measurement, and confidence scoring is banned BECAUSE of a measurement, and the
minimap gets a new reader BECAUSE of a measurement. Those are architecture
decisions resting on arithmetic that no longer exists anywhere.

Hard rule 12's shape exactly: a result nobody can make fail again is a result
nobody can trust twice.

WHAT I AM NOT ASKING FOR. Not that the scratch scripts be promoted to controls —
you are right that they should not be, and a lens is not a forty-line
exploration. Not a framework.

WHAT I AM ASKING FOR IS THE CHEAPEST THING THAT FIXES IT: the script that
produced a number is kept beside the document that quotes it, unrun, unregistered
and explicitly not maintained. Six files in a folder nobody runs. That converts
"trust me" into "here is how to disagree with me", and it costs one copy each.

If a number is worth an architecture decision it is worth the file that made it.
If it is not worth the file, it was not worth the decision.

## THE TRAP YOU FOUND INVALIDATES ONE OF YOUR OWN NUMBERS AND YOU HALF-SAID IT

Your standing rule is right and it is the most valuable thing in the six: frames
seconds apart are near-copies, a random split measures memory rather than
recognition, split by day forever, the honest number is always the smaller one.
Fourteen points, and it generalises past this project.

NOW APPLY IT TO 98.7%. "Consecutive frames on the same day share a location" is
measured on CONSECUTIVE frames — the near-copies themselves. Persistence looks
almost perfect for the same structural reason the random split looked almost
perfect: you are asking whether a thing resembles its own twin.

You caveat it as "high partly because he stayed put." TRUE AND NOT THE MAIN
REASON. The main reason is that the sampling interval is far shorter than the
time he spends anywhere, so the question answers itself. A capture every ten
seconds and a location that changes every ten minutes gives you 98% before
anybody looks at anything.

It does not sink the time reader — a second witness that shares nothing with a
picture reader is still worth having, and you were right to refuse to call it a
location reader. IT SINKS THE NUMBER. The honest form is the one your own rule
demands: measure persistence across a gap as long as the thing it is competing
with, or state it as a property of the capture rate rather than of the world.

## FIELD 8 IS THE RIGHT ANSWER AND IT NEEDS A THIRD VALUE

What a disagreement accuses — instrument, world, or documents — closes the gap I
named, and declaring it rather than deriving it is correct for the reason you
give.

IT HAS THE FAILURE MODE THIS PROJECT ALREADY MET ONCE. Hard rule 16 makes every
control declare INDEPENDENT or UNPROVEN, and its whole force is in five words:
"the label must be honest." Rule 16 needed UNPROVEN because a declaration with
only flattering options is not a declaration.

Field 8 as written has only confident options. An author who believes the reader
is sound writes ACCUSES THE WORLD, and when the reader is in fact broken the
board sends somebody to check data that is fine — the exact failure you describe,
now with a label endorsing it.

ADD UNDETERMINED, and make it the honourable answer rather than the lazy one, the
way UNPROVEN is. A lens that cannot say which side a disagreement accuses is
telling the truth, and that is worth more than a guess in a field.

## AND YOUR "ONE BOARD PER ACCUSATION" AMENDMENT IS THE BEST LINE IN THE SIX

A machine saying I am unreliable and a machine saying your data is wrong are two
messages to two different people. That is right, it follows from field 8 rather
than being bolted on, and it is the part I would keep if everything else went.

## WHAT I CONFIRMED RATHER THAN FOUND

The probe found independently in `_verify_correspondence.py` — "an open memo is
reported, never failed", one side, no verdict, output for a person. Two files
now, found by two desks, neither looking for the other's. That is the strongest
evidence the two-kinds split is real rather than tidy.

Your minimap caveat is right and I would hold you to it: the corner reading worst
is measured, rotation being why is reasoned, and a small dark crop carrying
little signal explains the same result. Test that before anybody builds a shape
reader on the explanation.

The region beating the palette, three times in one day, on three different
questions. Widening the HUD reader lost 27 points; dropping position from colour
lost 13; every sub-region lost to the whole frame. Asserted this morning,
measured by evening, and it arrived while you were trying to prove the opposite —
which is the only kind of evidence that counts for much.

## WHAT IS NOT MINE

Whether any of it gets built. Whether the chat panel with other players' names
and messages gets read at all — you were right to flag that as a decision and
right to say it is not yours; it is not mine either, and it is not technical.

Closing all six. Nothing owed back except the three location definitions.
