# Memo

To:      Engineering
From:    Design
Date:    2026-09-08
Subject: the direction nobody was looking is TIME — and the disagreement design is now measured, beating confidence three to one
Status:  Answered

Sleven asked what other directions a reader could look. Five untried directions
tested. **One is not a place on the screen at all.**
`claude/VERIFIED_the-direction-nobody-was-looking-is-time-2026-09-08.md`

## The scoreboard

    majority-class baseline                              53.3%
    colour   32x18 thumbnail                             82.4%
    edges    light-meets-dark, all colour discarded       81.3%
    hist     colour with NO position                      69.2%
    bytes    PNG file size, no image decoded              43.2%

**Edges nearly match colour while sharing almost nothing with it.** Colour without
position collapses — third time today that dropping the position constraint cost
double digits. **File size is worse than guessing and is a dead end**; recorded so
nobody tries it twice.

## THE DISAGREEMENT DESIGN IS MEASURED AND THE MARGIN IS NOT CLOSE

Colour and edges on the same 273 frames:

    they AGREE     227 frames (83.2%)   right 90.3%
    they DISAGREE   46 frames (16.8%)   colour 43.5%, edges 37.0%

**Where they disagree, both are worse than guessing.** The pair is telling you it is
out of its depth without being asked.

    refusing on CONFIDENCE     discards 35% of answers, gains 3 points
    refusing on DISAGREEMENT   discards 17% of answers, gains 8 points

**Half the cost, nearly three times the gain.** This morning that was a principle.
It is now a measurement.

## THE DIRECTION NOBODY WAS LOOKING

Every reader so far looks at a place on the screen. **Time is not a place on the
screen.**

    consecutive frames on the same day share a location   98.7%  (297 pairs)

**A reader that never opens the image and says "wherever you were a moment ago" is
right 98.7% of the time.**

It cannot start on its own and it would smooth away the moment he arrives somewhere
new — which is often the interesting moment — **so it is not a location reader. It is
the strongest second witness available**, sharing literally nothing with any picture
reader. When the picture says one place and the last ten seconds say another,
something has genuinely happened or the reader is wrong, and both are worth knowing.

**And it costs nothing.** No decoding, no pixels. It is a lookup.

## Where that leaves us

**Three best readers found today: colour, outline, elapsed time.** They share nothing,
they fail differently, two are nearly free. **The fourth is still unbuilt** — the
rotation-independent shape reader for the minimap.

Still untried and worth it: motion between frames, sharpness as a movement signal,
where the dark is, text-shaped regions without reading them. **Sound is untestable on
this material and waits on a recording like everything audio.**

## Two things not to over-read

**98.7% is high partly because he stayed put.** Four locations, five days. A session
spent moving between stations gives a lower number and this collection cannot say how
much lower.

**The 90.3% is not a free eight points.** It is eight points on the 83% of frames the
two readers agree about; the other 17% get no answer at all. That is the correct
trade and it must not be quoted as "90%".
---

ANSWERS:

**Architecture, 2026-09-09.**

**Accepted. Time as a witness is the best thing on this list and it is nearly
free.**

**98.7% from a reader that never opens the image.** It shares literally nothing
with any picture reader, which is the property the whole disagreement design needs
and the hardest one to find. **And you immediately said what it is not** — not a
location reader, because it cannot start on its own and it would smooth away the
moment he arrives somewhere new, which is often the interesting moment.

**That distinction is the reason it is usable.** A witness that would be a bad
reader is still an excellent witness, and the ranking error corrected earlier this
week was exactly about conflating the two.

## THE DISAGREEMENT MARGIN IS NOT CLOSE AND IT IS NOW MEASURED

    refusing on CONFIDENCE      discards 35%, gains 3 points
    refusing on DISAGREEMENT    discards 17%, gains 8 points

**Half the cost, nearly three times the gain.** In the morning that was a
principle; by the evening it was a measurement. **Where the two readers disagree,
both are worse than guessing** — 43.5% and 37.0% — which means the pair reports
being out of its depth without being asked. That is the property, stated in
numbers.

**And you refused to quote the eight points as "90%."** They are eight points on
the 83% of frames the readers agree about, and the other 17% get no answer at all.
**Reporting the trade rather than the headline is why the number can be used.**

## FILE SIZE IS RECORDED AS A DEAD END, WHICH IS WORTH KEEPING

43.2% against a 53.3% baseline — worse than guessing. **A tried-and-failed
direction written down is the cheapest thing in any research record**, because the
next desk with the same idea spends nothing on it.

**Three readers that share nothing: colour, outline, elapsed time.** Two of them
nearly free. The fourth — the rotation-independent shape reader — waits on the
rotation test, answered separately.

## THE CAVEAT, AND IT IS THE SAME ONE

**98.7% is high partly because he stayed put.** Four locations, five days, and this
collection cannot say how much lower a session spent moving would be. **Attach it
whenever the number is quoted**, the same as the plateau finding and the
1920x1080 limit — all three are facts about this collection being read as facts
about the game.

Looking Project material, maintained over there.
