# Update — not deployed. The mark guard and its control now contradict each other.

**2026-09-04 · Code**

Sweep: **115 passed, 1 failed** - `_verify_community_mark.py`, 5 of its 13
assertions. The deploy gate refuses a red sweep and I have not used
`-IgnoreSweep`.

## What the control says

    detector: unmarked 0.9909, marked 0.9988, threshold 0.50
    negative control: real build exited 0 on an unmarked CIG-sourced image
    positive control: real build exited 1 on the marked image

    FAIL an unmarked image scores below the threshold        0.9909 < 0.50
    FAIL the two are separated by a wide margin, not a hair gap    0.0079
    FAIL an image composited WITHOUT the mark is REFUSED by the build
    FAIL the SAME image, marked, is ACCEPTED

Read plainly: **the detector scores an image with no mark at 0.9909 against a
0.50 threshold**, and separates marked from unmarked by 0.0079. On those numbers
it cannot tell the two apart, and both of its build-level controls came out
inverted - the build accepting the unmarked plant and refusing the marked one.

## What I watched the same guard do, three hours earlier

    15:16  build REFUSED. 241 registered images, every score 0.000, needs >= 0.50
    15:42  images marked by another session
    15:47  build PASSED. "241 CIG-sourced image(s), all carry it"

That is the guard discriminating correctly on the real payload, in both
directions, on 241 real images - and scoring unmarked at **0.000**, not 0.9909.

**So the guard and its control disagree about the same mechanism, and I am not
able to say which is right from here.** The control is a week old (08-28) and
passed this morning; what changed under it is that `data-layer/cig_assets.json`
came into existence at 14:25 and the register went from empty to 499 assets. A
control that passed while its subject was switched off is not evidence the
subject works.

One of its messages - *"exit 1: site, because that register is the off switch"* -
suggests its build invocations are now failing for a reason unrelated to the
mark, which would make both of its build-level controls meaningless rather than
inverted. That is a guess and I am labelling it as one.

## Why I am not fixing it

**Hard rule 8.** This is the Fan Kit compliance guard. The control's own output
carries a `REPORTED, NOT FIXED (hard rule 8 - Fan Kit compliance is Sleven's)`
section, which is the same conclusion reached by whoever wrote it.

Changing a detector threshold or a scoring function to make this green would be
adjusting the instrument that decides whether the site complies with CIG's
terms. That is not a call I get to make, and making it by touching code is
worse than making it out loud.

**And there is a real possibility the control is right and my observation is the
lucky one.** If `mark_score()` genuinely returns ~0.99 for unmarked images under
some conditions, then the 241 images now shipping as "marked" have been checked
by a detector that says yes to almost anything - and the build's 0.000 scores
this afternoon were the exception rather than the rule. I cannot rule that out,
so I am not shipping on the strength of my own anecdote.

## Also reported by the control, and I am leaving it alone

    241 ship thumbnails in images/ do not carry the mark. Their provenance
    says the upstream pack is governed by terms naming 'Made by the
    Community', and equally that it is NOT established whether any
    individual image is a CIG asset, a screenshot or a render.

Which is a live question about whether those 241 images should have been marked
or registered at all - and Part 2 of that work order plans to replace them with
our own renders. Not mine.

## State

- **Nothing deployed.** The site still serves this morning's payload.
- The payload itself is built, clean and current: see-through fix in, inspector
  in, source notice on all four ship-content pages, `find.html` correctly
  without it.
- Everything else in the suite is green - 115 passed, including the two
  contradictions I resolved earlier today.

**What Sleven needs to decide:** whether the mark detector is trustworthy. Until
that is answered nothing should ship, because the thing in doubt is the check
that says we are complying.
