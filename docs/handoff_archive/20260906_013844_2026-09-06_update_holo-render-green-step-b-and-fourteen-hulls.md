# Update - holo_render is GREEN. Step B taken, on the Liberator. And Step A turned up something the ruling did not expect.

Answers `ORDER_both-of-my-blockers-are-closed-holo-render-is-yours-2026-09-06.md`
and `RULING_the-5-percent-threshold-is-vacuous...`.

**First: you were right that I asked twice for a decision already on disk.** The
ruling was filed 00:16 and I asked at 00:37 and again at 01:11. Rule 24 says read
the mail before answering and I did not. Noted, not excused.

## STEP A - measured, nothing written. THE RULING'S PREMISE DOES NOT HOLD.

The ruling says, quoting line 422: shipped pure white runs **0.00% to 1.63%**, so
"no hull gets within 3x of 5%" and the threshold can never fire.

**Measured across all 258 hulls in the file's own model: 14 hulls are AT OR ABOVE
5% as shipped. The maximum is 9.21%, the Dragonfly Yellowjacket.**

Not my arithmetic being clever - **confirmed through the control's own code
path**, by pointing `CC_GEO_DIR` at that hull alone:

    panel        pure white 9.12%   FAIL panel is below the 5% threshold
    solidlines   pure white 8.30%   FAIL

So the threshold is not vacuous. **It is being crossed by 14 shipped hulls, and
section 5 has never seen them because it only ever tests ONE hull.** That is the
same shape as the ordering finding: a control that looks at one subject and
reports as if it looked at the fleet.

The 1.63% in line 422 is not wrong - it is the Liberator, and the Liberator is
still 1.63% today. It was the max of a smaller library.

### The caveat, and it is a real one

**Comparing these percentages BETWEEN hulls is not sound.** `pts` is a sample
CAPPED at 80,000, so each point stands for `count/sampled` real vertices and that
factor runs from **1.0 to 79.4** across the fleet. The Tyilui is decimated 79x;
the Dragonfly 7x. Cell depth is therefore partly a sampling artefact.

I tried correcting for it and the correction is clearly wrong too - it puts the
Tyilui at 68% pure white and 187 hulls over 5%, which the visibly-not-white site
refutes. **So I am not claiming the 14 hulls are physically too bright.** What I
am claiming is narrower and solid: *in the model this control uses and this
project has been quoting, 14 hulls fail the threshold and nobody was looking.*

Whether that is a render problem or a sampling artefact is a real question and
**I have not answered it.** Flagging, not fixing.

## STEP B - TAKEN. Available, and the subject picked itself.

Seven hulls sit under 2.5% shipped and over 8% with the pre-pass removed. Chose
the **Liberator** because it is the hull E7b is ABOUT - cc_viewer.js:447 names it
as the one whose lines whited out the deployed page - so the negative control now
runs on the case the floor decision was made for.

    Liberator:  as shipped 1.63% pure white,  no pre-pass + DoubleSide 8.34%

Nothing else changed, as the ruling specified. Added an assertion the old one
lacked: **the subject must PASS at shipped defaults**, or the line below it
proves nothing.

**Why this comparison is legitimate where the fleet one is not:** it is WITHIN
one hull - same sample, same cap, only the pre-pass differs - so the decimation
confound cancels exactly.

## The ratio test went in as its own control, under its own name, as directed

    PRE-PASS EFFECT (its own control, not the threshold's): removing the
    pre-pass at least doubles the saturation      1.63% -> 8.34% = 5.1x

Floor of 2x, well under the 5.0x and 5.1x measured at both ends of the density
range. Not substituted for the threshold control - added beside it.

## RULE 12: I FOUND MY OWN NEW ASSERTIONS WANTING AND SAID SO IN THE FILE

Run with `--mutate-prepass`, **all three of my new assertions stay green.** `sNo`
is MODELLED - the x2 stands for "no dedup, plus DoubleSide" - and the arithmetic
never asks the viewer whether a pre-pass is actually there.

So they prove the threshold **is crossable** on a hull that passes as shipped.
They do **not** prove the viewer still has a pre-pass. Section 4 proves that - it
reads `_holoPasses` directly and does go red under the mutation (3 failures).

Two different jobs, and I have written that into the file next to the assertions
rather than let a future reader assume more. I considered strengthening them to
read the viewer's pass list, and stopped: the ruling said "nothing else changes",
the limitation is inherited rather than introduced, and section 6 already
declares this section a model and not a frame.

    47 passed, 0 failed

## Now

Full sweep running. If green: build and deploy TESTING, testing only, nothing to
the live site, no commit or push without Sleven (rule 2), no `git add -A`.

## For the queue, not for tonight

1. **14 hulls over the 5% threshold** - real or sampling artefact, unanswered.
2. **Section 5 tests one hull and reads as if it tested the fleet** - the same
   shape as the ordering finding you have already queued.
3. `_verify_placer_candidates.py` raises a bare `FileNotFoundError` where a NOT
   PERFORMED belongs.
