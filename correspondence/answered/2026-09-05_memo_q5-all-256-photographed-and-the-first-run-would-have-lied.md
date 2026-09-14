# Memo

To:      Engineering
From:    Build
Date:    2026-09-05
Status:  Answered
Subject: Q5 - all 256 photographed, all 256 clean, and the first attempt would have reported 69 broken ships that are not broken

    LOAD FAILED  0
    EMPTY        0
    INVISIBLE    0
    OVERFLOW     0
    ok           256 of 256
    retried once 0
    page errors  0

`docs/contact_sheet_20260905/index.html` - 256 shots plus an index, flagged
hulls outlined in red so a bad one is findable without reading the list. Rule
21: internal working material, not published.

## The first run said 69 hulls failed to load

Clean through 96 and then **every remaining ship timed out**, starting at the
Fury. Not 69 bad models - one dead WebGL context. A hundred
multi-hundred-thousand-triangle hulls in a single page under software GL
exhausts it, and every load after that point fails identically.

**From the outside, "the renderer died" and "this model is broken" are the same
observation.** I killed the run rather than report it. Two changes, both about
telling those apart:

- the page is recycled every 40 hulls, so the context never gets that far;
- **any failure is retried once on a fresh page before it is called a failure**,
  and the run prints how many retries were needed. A retry that then succeeds
  was a harness stumble, not a model.

The clean run needed **zero** retries, which is the evidence that the recycling
is doing the work rather than the retry papering over it.

## The threshold was a coincidence and I replaced it

First pass used a typed 1.0% "invisible" bar against an observed minimum of
**1.10%** - the Khartu-Al. Everything passed, and a change of viewport, lens or
fit margin would have pushed real ships under it.

**Checked it was not a measurement artifact before touching it**, because the
absolute numbers looked low: coverage is FLAT from a colour-difference of 4
through 96 - 3.28% to 3.22% on the Cutlass Black - and the hull's centre pixel
is [107,132,156] against a [11,15,20] backdrop. It is reading real lit pixels,
not clipping dark hull against dark sky. A ship's silhouette is simply a small
fraction of the bounding box that gets framed.

So the bar is now a quarter of the fleet's own median, computed per run:

    fleet median 2.45%  ->  invisible below 0.61%   (min observed 1.07%)

A 1.75x margin instead of 1.1x, and it moves with the fleet instead of needing
somebody to remember it.

## What it is worth

It answers "did anything break" in about twenty minutes without a person
looking at 256 ships, which was the point. **It does not answer "does this look
right"** - a hull can load, fill the frame, and be the wrong ship. That is still
eyes, and the contact sheet is what makes the eyes fast.

## Queue

    Q1  BLOCKED  deploy needs -IgnoreSweep, refused by my permission layer;
                 and under it hull-geometry/ is stale, so the holo fit cannot
                 be regenerated correctly yet. Both reported separately.
    Q2  done     see-through gone, 85X one ship, X1s two-of-three by design
    Q3  done     all three in frame, worst corner exactly at 1/1.06
    Q4  done     _verify_model_plausible.py, mutation-proven
    Q5  done     this memo
    Q6  done     the metric does not survive your pipeline change, with proof

Everything you queued is finished except the one item that needs a permission I
do not have and a dataset that is not mine.

---

ANSWERS: C1, 2026-09-05.

Accepted, and the part worth keeping is the part you flagged yourself: **a hull
can load, fill the frame, and be the wrong ship.** That is exactly what happened
to me today - my decoded Gladius loads, fills the frame, matches CIG's declared
bounding box to three decimals, and renders as a flat shredded sheet. Every
number agreed.

**Re-shoot it.** The sheet was taken before the revert, so it shows models that
are no longer on disk.

Catching that your first threshold was a coincidence, and replacing it rather
than shipping 69 false positives, is the right instinct. Keep doing that.
