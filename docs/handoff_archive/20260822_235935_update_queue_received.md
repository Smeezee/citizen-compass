# Update - the queue received. Q1 through Q10, starting at Q1.

`docs/ORDER_the-queue-2026-08-23.md`. Read it, plus E11 / E11a / E11b in the
errata. Running top to bottom, no decision gates.

**Q1 first.** `renderMarkers` is in the animation loop; `renderLabels` is called
once from `renderAll`. Labels are placed and abandoned, so rotating the hull
leaves them behind with leader stubs pointing at nothing.

**The trap is read and understood.** `layoutLabels()` is a collision solver -
six candidate rings per label, nearest-first - and it is what took the Perseus
from 15 placed to 26 with zero overlaps. Running it 60 times a second on 35
labels costs the framerate on exactly the hulls that need it most. So: anchors
and leader lines every frame off the projection `renderMarkers` already
performs, and the ARRANGEMENT solve throttled. The line is the promise; the ring
position is the tidiness.

**And the negative control must fail on the current build, on every hull.** If
it passes today it is measuring nothing - which is the shape H1b's control had:
it asserted the labels existed and did not overlap, and never that they stayed
attached to anything.

Then Q2 (E11b - E8 is recorded done and the Pisces symptom persists; find the
path and SAY WHICH IT WAS, because that decides whether E8's control was wrong
or merely narrow) and Q3 (E6 - the panel Sleven reported as missing while
looking straight at it).
