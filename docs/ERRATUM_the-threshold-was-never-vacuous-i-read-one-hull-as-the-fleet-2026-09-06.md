# ERRATUM — my 5% ruling's central premise is wrong. The threshold is crossed by 14 shipped hulls. I read one hull's number as the fleet's.

    from      C1, 2026-09-06
    corrects  docs/RULING_the-5-percent-threshold-is-vacuous-and-my-five-ships-were-three-2026-09-06.md §2
    found by  Code, step A of that ruling's own instructions
    for       anyone who reads that ruling later

---

## What I wrote, and why it was wrong

The ruling said, quoting `_verify_holo_render.mjs:422`:

> measured on the shipped build, pure white 0.00% to 1.63% against a 5% threshold

and concluded: **"No hull in the shipped fleet gets within 3x of 5%... it has
never been able to fire on anything this project ships."**

**Measured across all 258 hulls: 14 are at or above 5%. The maximum is 9.21%,
the Dragonfly Yellowjacket** - confirmed through the control's own code path,
not by separate arithmetic:

    panel        pure white 9.12%   FAIL panel is below the 5% threshold
    solidlines   pure white 8.30%   FAIL

**The 1.63% is not a fleet range. It is the Liberator, one hull, and it is still
1.63% today.** It was the maximum of a smaller model library when that line was
written. I read a single subject's figure as a population's and built a ruling
on it.

**The threshold was never vacuous. Section 5 tests ONE hull and reads as though
it tested the fleet**, which is why nobody had seen the 14. That is the same
defect shape as the sweep-ordering finding - a control whose scope is narrower
than the sentence it prints.

## What survives, and it is most of it

- **Do not widen 5%** - now for the opposite reason. It is not too wide; it is
  being crossed, and widening would hide 14 hulls.
- **Step B was the right instruction and it was available.** Seven hulls sit
  under 2.5% shipped and over 8% with the pre-pass removed. Code chose the
  Liberator because `cc_viewer.js:447` names it as the hull the E7b floor
  decision was made about, so the negative control now runs on that case.
  1.63% shipped, 8.34% with the pre-pass removed.
- **Steps C and D are not needed and are withdrawn.** They existed only for the
  case where no hull could cross, and that case does not exist.
- **The ratio test as its own separate control** stands, and went in as
  directed: 5.1x, floor of 2x.

## The 14 hulls are NOT yet a defect, and Code was right to refuse to call them
## one

`pts` is a vertex sample **capped at 80,000**, so each sampled point stands for
`count/sampled` real vertices and that factor runs **1.0 to 79.4** across the
fleet. The Tyilui is decimated 79x, the Dragonfly 7x. Depth per cell is therefore
partly a sampling artefact, and a first attempt at correcting for it put 187
hulls over 5% - which the visibly-not-white site refutes.

**So the honest claim is the narrow one: in the model this control uses, 14 hulls
fail the threshold and nothing was looking at them.** Whether that is a render
defect or a sampling artefact is unanswered and is now on the queue.

**The within-hull comparison is unaffected** - same hull, same sample, same cap,
only the pre-pass differs, so the decimation confound cancels exactly. That is
why Step B is sound where a fleet comparison would not be.

## Recorded about the assertions themselves

Code checked his own new assertions against `--mutate-prepass` and reported that
**all three stay green**, because `sNo` is modelled arithmetic that never asks
the viewer whether a pre-pass exists. Section 4 is what proves the pre-pass is
present - it reads `_holoPasses` and does go red. Two different jobs, written
into the file next to the assertions rather than left for a reader to assume.

**Finding your own new work wanting, in the same update that ships it, is the
behaviour this project is trying to have.**

## Queue

1. **14 hulls at or above the 5% threshold** - render defect or sampling
   artefact. Unanswered.
2. **Section 5 tests one hull and prints as if it tested the fleet.** Same shape
   as the sweep-ordering finding.
3. `_verify_placer_candidates.py` raises a bare `FileNotFoundError` where NOT
   PERFORMED belongs.

---

*C1, 2026-09-06. Third of my numbers to be corrected by a check today. All three
were found by someone refusing to fit the measurement to what I had written.*
