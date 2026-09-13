# Update - NOT DEPLOYING YET. C1's 18:10 regeneration fixed every missing picture and broke the one-height rule Sleven approved.

## Answering "deploy, or is something broken?"

**The live testing site is healthy and was never at risk.**

    /next                   200, 120,898 bytes   sha 8fc457226b8dc881
    /                       200, 396,153 bytes
    /models/Hammerhead.glb  200, 4,153,816 bytes

It serves exactly the bytes verified at 16:39.

## Two things happened during my sweep, and only one was a defect

### 1. `_verify_deploy_drift.py` failed - a RACE, not a defect

**C1 regenerated `testing/_src/next.src.html` at 18:10:23**, mid-sweep:
110,188 -> 130,588 bytes, `_src/images` 241 -> 242. Drift ran at 18:10:47 and
compared a payload built from the OLD source against the NEW one.

Rebuilt cleanly and re-ran it alone: **14 passed, 0 failed.** Not a defect.

**This is our contention agreement in a new shape.** This afternoon it was CPU -
her OCR sweep against my survey, my hundred node probes against my own sweep.
This time nobody was competing for CPU: **the SOURCE moved under a running
sweep.** Same lesson, different resource, and worth naming so the agreement
covers it.

### 2. THE REAL ONE - the cards are no longer one height

Sleven's approved design, and the order's own acceptance list, say **"253 cards,
all one height."** Measured in a real browser against the freshly built payload:

    253 cards render                     ok    253
    every card is the same height        FAIL  8 distinct: 129,130,131,144,145,146,147,155
    every picture loads                  ok    247 of 247
    manufacturer groups A-Z              ok    18
    ships A-Z inside every manufacturer  ok
    no page errors                       ok    0
    cards showing NO IMAGE                     0    (was 7)

**The regeneration is a real improvement in one way and a regression in another.**
Every missing picture is now filled - NO IMAGE went 7 to 0. But the grid is ragged.

Diagnosed rather than just reported, so it is actionable:

    height 129-131   143 cards
    height 144-147   109 cards
    height 155         1 card   Valkyrie, 11 text lines

- **Two clusters about 15px apart**, not a continuous spread.
- **The name element is a uniform 21px on every single card**, so this is NOT
  long names wrapping to a second line.
- **The Valkyrie at 155 is correct and expected** - it is the edition fold from
  Sleven's ruling, carrying the Liberator as a line on the parent's card. That
  one is the design working, not breaking.

## Why I have not deployed it

The page is better in one respect and violates an approved design criterion in
another. **A visible regression against something Sleven signed off on should not
ship because it arrived attached to a fix.** Nothing is lost by waiting - the
live site is current and healthy.

**It is a one-word decision.** Say ship it and I will sweep and deploy as it
stands; the pictures being complete may well be worth more to him than a level
grid. Or C1 levels the cards and it goes out whole.

## Also found, and it is C1's control that found it

    testing/_src/next.src.html has NO declared owner in OWNERS.md

Reported by `_verify_deploy_drift.py` itself, in its own words: *"that is a gap
rather than permission, and is worth reporting."* The file is plainly C1's - she
generates it - but the list does not say so, and OWNERS.md is the thing that
settles ownership when two documents disagree (rule 14). **Sixth ownership gap
found this way.**

## Green, for the record

    _verify_front_page_assets.py   exit 0 in the sweep, 0.1s - the new control
                                   holds in context
    _verify_deploy_drift.py        14 passed, 0 failed, against a clean build
    120 controls green apart from the drift race
