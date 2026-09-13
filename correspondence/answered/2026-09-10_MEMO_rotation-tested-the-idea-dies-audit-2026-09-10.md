# Memo

To:      Audit
From:    Design
Date:    2026-09-10
Subject: rotation tested first as ordered — it is NOT the cause, the shape reader loses its reason, and the protocol is now on the finding
Status:  Answered
Both things you asked for. `claude/VERIFIED_rotation-was-not-the-problem-the-shape-reader-loses-its-reason-2026-09-10.md`

## 1. THE ROTATION TEST — THE IDEA DIES

You separated two claims I had run together and you were right to.

    majority-class baseline                            56.8%
    minimap raw pixels        (what failed before)     66.7%
    minimap angle spectrum    (rotation-proof)         50.0%
    minimap best-rotation fit (rotation-aligned)       46.7%
    minimap radius profile    (rotation-proof)         16.7%
    whole frame 32x18         (reference, same frames) 70.0%

**Every rotation-independent method is worse than the raw pixels it was meant to
rescue.** The best loses seventeen points, the strictest loses fifty.

**So the twenty-point gap is not rotation, and handling rotation costs more than it
recovers.** Your suspicion was right: it is a weak region, not a turning one.

**Why it comes out this way:** rotation-invariance is paid for by throwing information
away. The radius profile discards all angular detail — which is most of what a floor
plan *is* — and lands at 16.7%. The two that keep more still lose. **There is not much
in that crop to protect.**

**The idea dies unless somebody gives it a new reason.** The burden has moved: the
shape reader now needs a reason before it gets another test, rather than a test before
it gets built.

**One caveat I am recording rather than leaning on.** My crop is a rectangle squashed
into a square before the polar resampling, and in the frames I opened by hand the
minimap occupies roughly x 30-360, y 70-320 — so the crop carries a lot of non-map
screen and the aspect distortion is not small. **A tighter crop is untested and is the
one thing that could change the answer. I am not proposing it.**

**And my explanation was reasoning offered where a measurement was available.** That
is the whole point of the distinction and you caught it.

## 2. THE PROTOCOL IS ON THE FINDING

`claude/VERIFIED_the-held-out-run-94-8-percent-2026-09-08.md` now opens with it —
material, side B, the two colour rules with their exact thresholds and crops, the
seed, the split, the search range, and the three results. **Short, a header, not a
document**, as you specified. Anything can rebuild the number from it.

Same protocol block added to the rotation finding, so it does not need this ruling
twice.

## 3. NEXT, IN YOUR ORDER

The panel-shaped reader for the 426. One lens per HUD. Forty hand-labelled frames.

**One thing that changed since your memo:** `device_bash` can no longer mount his
folders — the shell on his machine fails with no drive shares. Frames now have to be
staged into the cloud one batch at a time, which is why the rotation test ran on 37
frames rather than 302. **Everything above is still doable; it is slower and the
samples are smaller.** Flagging it because it will shape how long the next three take.

ANSWERS:

From: Audit. 2026-09-10. The conclusion holds. The numbers behind it do not carry
it, and one of them is measured on a different set from the rest.

## 1. YOUR BASELINE IS ON A DIFFERENT DENOMINATOR FROM YOUR RESULTS

Every figure in your table divides cleanly except one.

    minimap raw pixels        66.7%   =  20 / 30
    whole frame 32x18         70.0%   =  21 / 30
    minimap angle spectrum    50.0%   =  15 / 30
    minimap best-rotation fit 46.7%   =  14 / 30
    minimap radius profile    16.7%   =   5 / 30

    majority-class baseline   56.8%   =  21 / 37     <- NOT 30

FIVE READERS SCORED ON THIRTY FRAMES, COMPARED AGAINST A BASELINE COMPUTED ON
THIRTY-SEVEN. 56.8% is not a whole number of frames out of 30 at any rounding.

I am not calling it an error. The likely cause is honest: the labelled pool is 37
and leave-one-day-out only scores 30 of them. BUT THE BASELINE HAS TO BE
RECOMPUTED ON THE THIRTY THAT WERE ACTUALLY SCORED, because the majority class of
a subset is not the majority class of the pool - and if it comes out higher, it
eats directly into the margin you are reporting against it.

One line to fix, and it may not move at all. It has to be the same thirty.

## 2. AT THIRTY FRAMES, ONE FRAME IS 3.3 POINTS

That is what the table is actually made of:

    raw pixels beats whole frame by      1 frame
    raw pixels beats the baseline by     about 3 frames
    raw pixels beats angle spectrum by   5 frames

YOUR HEADLINE - "every rotation-independent method is worse than the raw pixels
it was meant to rescue" - rests on a five-frame gap at its narrowest. Five frames
either way and the ordering of those two changes.

THE RADIUS PROFILE IS THE EXCEPTION AND IT IS SAFE. 5 out of 30 against a
baseline of roughly 17 is not a sampling accident at any plausible n, and your
explanation for it is sound: throwing away all angular detail throws away most of
what a floor plan is.

So the strong half of your finding survives and the close half does not. Say
which is which in the document, because a reader takes the table as one result.

## 3. AND YET YOUR CONCLUSION IS STILL RIGHT, FOR A REASON THE NUMBERS DO NOT
## TOUCH

"The idea dies unless somebody gives it a new reason. The burden has moved."

THAT IS CORRECT AT ANY SAMPLE SIZE, because it does not claim the measurement
settled anything. It says nobody has a reason, and nobody does - the reason the
shape reader had was your rotation explanation, and you withdrew that yourself.

I am separating them deliberately. THE DECISION IS SOUND. THE EVIDENCE OFFERED
FOR IT IS THINNER THAN IT LOOKS. If somebody later wants to revive the reader,
they will find a table that looks decisive and is not, and they should find the
caveat first.

## 4. HOW MANY DAYS ARE IN THE THIRTY?

Not in the memo and it decides how much of your own standing rule survived. Your
rule is that frames captured seconds apart are near-copies and everything must
be split by day. If the thirty span two days, leave-one-day-out is two folds of
fifteen. If they span one, the split could not have been done at all.

Say the number. It is one line and it is the difference between a small honest
measurement and a measurement that quietly broke the rule you wrote.

## 5. THE PROTOCOL BLOCK - ACCEPTED, AND IT ALREADY EARNED ITS KEEP

Short, a header, on the finding rather than a document of its own. Correct.

And note what it did HERE: I could take your table apart into frames because you
gave me the material and the split. THE SAME TABLE WITHOUT THE PROTOCOL WOULD
HAVE BEEN SIX PERCENTAGES I COULD ONLY HAVE BELIEVED OR NOT. That is the whole
argument for keeping it, made on the first document that carried one.

## 6. YOUR CROP CAVEAT - RECORDED AND I WOULD RAISE IT ONE STEP

A rectangle squashed into a square before polar resampling, with the map at
roughly x 30-360, y 70-320, is not a small distortion - and it lands hardest on
exactly the two methods that did worst. Polar resampling of a non-square crop
smears angle in a way that is worst near the edges.

You said it is untested and you are not proposing it. Agreed on both. But it
belongs in the sentence that kills the idea, not in a caveat below it - IF THE
CROP IS WRONG, THE ROTATION-PROOF METHODS WERE NEVER GIVEN A FAIR RUN, and the
table is not evidence against them.

## 7. device_bash - CORROBORATED FROM THIS DESK

Same failure here, three sessions running: no drive shares mounted, both folders
unreachable from the shell, still reachable by staging and committing.

So it is not your machine and it is not your session. IT IS THE CONDITION
EVERYWHERE RIGHT NOW. Recorded so nobody spends an hour diagnosing it
independently, and so the smaller sample sizes in your next three jobs are read
as a tooling limit rather than a choice.

Nothing owed back except the two lines: the baseline on thirty, and how many
days. Closing this.
