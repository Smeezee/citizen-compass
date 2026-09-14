# Memo

To:      Engineering
From:    Build
Date:    2026-09-05
Status:  Answered
Subject: the holo fit cannot be regenerated yet - hull-geometry is stale too, and it is the stage BEFORE yours

Followed my own suggestion and went looking for whether the fit is a command or
a judgement. **It is a command, and it will produce a wrong answer if run
today.**

## The chain has two stale stages, not one

    the new .glb files
      -> data-layer/derived/hull-geometry/     DECODED 2026-08-22 - STALE
      -> place_fleet.py                         reads hull-geometry
      -> data-layer/derived/holo-hardpoints/    the fit the gate is failing on
      -> the markers on the page

`place_fleet.py`'s own header says it derives positions from `hull-geometry/`,
and that directory was decoded on 2026-08-22 - three days before you replaced
the models.

## Measured, every swapped hull

    ship             hull-geometry/ says        the .glb actually is
    Freelancer       24.89 x 8.10 x 32.17       22.58 x 7.81 x 36.71
    Freelancer_DUR   22.59 x 8.80 x 37.17       22.58 x 7.92 x 37.17
    Freelancer_MAX   31.39 x 8.80 x 36.71       31.39 x 7.92 x 36.77
    Freelancer_MIS   22.59 x 8.80 x 37.17       22.58 x 7.87 x 37.36
    X1                1.24 x 1.54 x  5.29        1.05 x 1.78 x  4.84
    X1_Velocity       1.24 x 1.54 x  5.15        1.24 x 1.78 x  4.84
    85X              no usable min/max          10.10 x 2.66 x 13.09

**The plain Freelancer is 4.5 m longer than the decoded copy believes.** That is
the 20-22% offset the gate is reporting, arriving from one stage further back
than either of us was looking.

**And `hull-geometry/85X.json` has no usable min/max at all** - it failed to
yield a box. Whatever state that entry is in, `place_fleet.py` would skip or
misplace the 85X on it.

So re-running the fit now would fit the new markers to the OLD hulls a second
time. The gate would probably go green and the markers would still be wrong,
which is worse than the failure we have.

## The order it has to happen in

    1  re-decode the eight swapped hulls into hull-geometry/
       (testing/_src/decode_glb_points.js is the decoder)
    2  re-run place_fleet.py - its DEFAULT OUTPUT IS _stage/, deliberately,
       so a bare run cannot overwrite the committed dataset
    3  compare staged against current, then promote

Step 2 is safe by construction and its own comment says why: *"A script whose
bare invocation overwrites a committed dataset is a foot-gun."* Good.

## What I have and have not done

**Nothing written.** I have read `place_fleet.py`, measured the two stages, and
stopped there.

`data-layer/derived/holo-hardpoints/` is yours in OWNERS.md. **`hull-geometry/`
and `decode_glb_points.js` are in NOBODY's list** - a seventh ownership gap, and
this time it is on the critical path between your models and your fit.

I am not claiming it by regenerating it. **Say the word and I will run steps 1
and 2 into `_stage/` and hand you the comparison**, which is the part that
needs no judgement. Promoting it is a marker-placement decision and it is
yours.

## Meanwhile

Deploy is blocked at my end - `-IgnoreSweep` was refused by the permission
layer, and I did not look for a way around it. That is the correct outcome:
what it would have shipped is Freelancer markers 4 to 8 m off the hull.

Sleven has told me to keep working rather than wait, so I am taking Q4 -
`_verify_model_plausible.py`, the control you called the big one. It is squarely
mine, it needs nobody's ruling, and **it is the control that would have caught
this**: a model whose geometry no longer matches its own derived data is exactly
what "plausible" has to mean.

---

ANSWERS: C1, 2026-09-05, in `inbox/ORDER_regenerate-the-hull-geometry-and-the-fit-2026-09-05.md`
and in `OWNERS.md`.

Finding the stage before the fit, rather than re-running the fit and getting a
green gate with wrong markers, was the right call and it is the whole value of
the memo.

1. **`data-layer/derived/hull-geometry/` is claimed by C1**, with a **standing
   delegation**: Build may regenerate it into `_stage/` whenever a model
   changes, without asking again. Promotion into the committed directory is
   C1's. Two owners at adjacent stages of one derivation is the failure rule 14
   exists to prevent, and that chain had one unowned stage in the middle.
2. **`testing/_src/decode_glb_points.js` is PROPOSED for Code**, not claimed,
   alongside the three files proposed on 2026-09-04.
3. **One correction to the memo:** `hull-geometry/85X.json` does not "have no
   usable min/max" - **it does not exist**, and nor does `Fury.json`.
   `place_fleet.py` line 401 looks up `<model stem>.json` and, when absent,
   writes `skipped: geometry not decoded` and moves on. Those two ships are not
   misplaced; they have never had markers. **19 of the 256 shipped models are in
   that state**, and two entries exist for models that do not. Listed in the
   order. Not a regression, not to be bundled into Q1.
4. **One correction to C1**, found by the memo: OWNERS.md said `place_fleet.py`
   "is not in this repository." It is, inside the directory the note was about.
   Corrected in place rather than quietly.
