# Memo

To:      Engineering
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
---

ANSWERS:

**Architecture, 2026-09-09.**

**Accepted, and the shape reader is NOT built on your explanation until the
explanation is tested. You said so yourself and you were right to.**

**Measured: the minimap corner reads worst, by twenty points. Reasoned: that
rotation is why.** Those are different claims. **A small dark crop carrying little
signal would produce the same result**, and a shape reader built on the wrong one
of those two is an afternoon spent proving nothing.

**So the rotation test comes first and it is cheap** — rotate the crops and see
whether a rotation-independent comparison recovers the twenty points. If it does,
the shape reader has a reason. If it does not, the minimap is simply a bad region
and the idea dies for a fraction of the cost.

**His instinct still deserves the test.** A minimap is drawn from map data rather
than from lighting and view direction, which is a genuinely different kind of
signal from everything else on the list. **That is the argument for testing it, not
a substitute for testing it.**

## THE THREE FAILURES ARE THE RESULT, NOT THE FAILURES

Bigger buys eight tenths of a point. More examples plateau after a quarter of the
data. Looking at one part of the screen is worse than looking at all of it.

**All three say the same thing: improvement comes from a different KIND of looking,
not more or bigger of the same.** That is the ten-eyes argument measured three
times in one day instead of asserted once, and **three independent measurements
agreeing is worth more than any one of them.**

**More DIFFERENT places, not more frames.** Limited by variety, not volume — and
that is a fact about what to collect, which is worth more than a fact about how to
read.

## THE CAVEAT YOU PUT ON YOUR OWN CEILING

**Four locations, five days. The flat curve may be flat because four places are
easy, not because the method is saturated.** Carried, and it should be attached to
the plateau finding every time it is quoted, because "the method is the ceiling" is
exactly the kind of conclusion that gets repeated without its sample size.

Looking Project material, maintained over there.
