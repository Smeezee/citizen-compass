# Update — status against ORDER_fix-the-marked-ships-and-deploy, task by task

**Code**

Received at 23:36. Four of the five are already answered, from work done before
it arrived; one is stopped by its own condition; one is blocked structurally.
**Nothing needs rebuilding or deploying.**

## 1. Clear the 20 stale marks — BLOCKED, and not by choice

The marks are `localStorage['cc_inspect_v1']`, in Sleven's browser. I searched
the tree: no server-side or repo-side copy exists, and the page reads its state
from nowhere else.

**I cannot move 20 entries to a resolved state from here.** It needs either page
code in `_inspect.src.html` that migrates those specific entries on load - C1's
file, and this order names no file - or Sleven doing it in the browser.

Reported at 00:35 as well. This is the one task in the order that no amount of
work on my side completes.

## 2. Three framing re-checks — DONE. All three are STILL CROPPED.

Measured by projecting each hull's eight bounding-box corners through the live
camera in a real browser:

    ship            worstX   worstY   margin   verdict
    ATLS             0.381    1.259   -0.259   CROPPED
    ATLS GEO         0.409    1.242   -0.242   CROPPED
    Reliant Kore     0.308    1.203   -0.203   CROPPED

All three overflow **vertically** with room to spare horizontally - the same
pattern on all three, which points at the fit being computed against a width the
stage does not have vertically rather than three ships each being slightly big.

Renders at `docs/renders_20260905/frame_*.png`. Radius untouched, as instructed.

## 3. The Fury — AUTHORISED, and STOPPED by the order's own condition

    "If your count is not exactly 301, stop and report the difference."

**My count is 36.** The Fury is untouched.

Reported in full at 00:10. In short: my method reproduces C1's 85X numbers
EXACTLY - pairs 344, coincident 3, displaced 341, all three - so the pairing and
the world-translation accumulation are sound. On the Fury I get 594 pairs,
matching C1, and 36 coincident against their 301.

No copy on disk and no definition reaches 301:

    world tolerance 1e-6 .. 1e-2   36        local translations identical  542
    world tolerance 0.1            43        both local at the origin      202
    world tolerance 0.5            55
    world tolerance 1.0            86

Five Fury copies measured: 36, 36, 36, 55, 55. Never 301.

**I am not tuning the method until it produces the expected number.** The 85X
matching on three independent figures is what says the method is right.

## 4. The 85X — DONE, report only, nothing changed

    docs/renders_20260905/85X_1_whole.png   whole file
    docs/renders_20260905/85X_2_xlt4.png    736 primitives
    docs/renders_20260905/85X_3_xge4.png    249 primitives

Same camera. 736 + 249 = 985 = every primitive, so the halves add up.

**Caveat repeated because it decides how to read them:** the threshold is my
reconstruction of C1's X=4. Their coordinates are this file's multiplied by
5.840674 - the `CC_SCALE_ROOT` wrapper, confirmed exactly by their 8.747 offset
against my 1.498. Even after that factor our histograms do not reconcile over
the same 246 nodes: theirs -4..13 with a clean gap, mine -37..32 with no empty
bin. **If the pictures do not show two ships, that is evidence about my mapping,
not about the 85X.**

## 5. Build and deploy — NOT NEEDED, and doing it would be theatre

    last build            2026-09-04T21:12:52
    source newer than it  nothing
    payload fingerprint   446a772a82a87699
    last sweep            446a772a82a87699, 0 failed

Tasks 1 and 3 changed no files; 2 and 4 were report-and-render only. The payload
is unchanged, already swept clean, and already deployed. A rebuild would produce
the same bytes and a deploy would upload nothing.

**Say the word and I will run both anyway** - but I would rather tell you it is a
no-op than perform one and report a deploy that moved nothing.

## The one thing that would unblock two tasks at once

C1 re-running their histogram and their Fury count against the **deployed**
files. If their 85X histogram shows -37..32 on this copy we agree and only the
threshold needs restating. If it still shows -4..13, they are measuring a
different copy - which would explain the Fury's 301 as well, and both
disagreements collapse into one cause.
