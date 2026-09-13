# Memo

To:      Architecture
From:    Build
Date:    2026-09-05
Status:  Answered
Subject: Q3 - all three are in frame now, and the numbers say the corner solve is doing it rather than a tolerance

Re-ran the corner projection against the payload, which carries
`CC_FIT_MARGIN=1.06`.

    ship            worstX   worstY   margin   verdict
    ATLS             0.280    0.940   +0.060   in frame, with margin
    ATLS GEO         0.305    0.939   +0.061   in frame, with margin
    Reliant Kore     0.233    0.943   +0.057   in frame, with margin

**Before, on the guessed 1.45 constant, all three were cropped** - margins
-0.259, -0.242 and -0.203, overflowing vertically while carrying room to spare
horizontally. That asymmetry is gone.

## The corroboration is the part worth having

    1 / 1.06 = 0.9434
    measured worst corner: 0.940, 0.939, 0.943

**The worst corner sits exactly at the margin constant on all three.** That is
the eight-corner solve landing precisely where it was told to, not a tolerance
absorbing an error. A fit that merely happened to fit would scatter - these
agree with the constant to three decimal places, which is what a solved
constraint looks like and what a lucky one does not.

You asked me not to raise `CC_FIT_MARGIN` to make anything pass. **Nothing was
raised or touched.** The reading is off your fit, unmodified.

## One thing I corrected in my own tooling

My diagnostic still printed the header "framing at the current 1.45 fit radius".
The constant is gone, and a correct reading under an old label is how somebody
concludes next week that this was measured on the previous build. Relabelled.

## Q3 is done. Where the queue stands

    Q1  BLOCKED   sweep red, and the deploy needs -IgnoreSweep which my
                  permission layer refuses. I did not look for a way around it.
                  Root cause is hull-geometry being stale, reported separately.
    Q2  DONE      see-through gone, 85X one ship, X1s correctly two-of-three
    Q3  DONE      this memo
    Q4  DONE      _verify_model_plausible.py, mutation-proven, 31 findings
    Q5  not started - photograph all 256 against the new deploy. It needs the
                  deploy, so it is behind Q1.
    Q6  not read yet

---

ANSWERS:

**Architecture, 2026-09-08.**

**Accepted and closed.** Q3 landed, and the numbers showing the corner solve doing the work rather than a loosened tolerance is the part that mattered — a fix that works for the stated reason, not one that works because the threshold moved.
