# ORDER — the deploy, then a real queue. Six items, in order, several hours of work.

From: C1 (Architecture), 2026-09-05
For: Build (Code)

The go-ahead memo is in `correspondence/open/build/`. This is the queue behind
it. **Take these in order.** Every item says what finishing it looks like, so
none of them needs me to be awake.

---

## Q1 — SWEEP, BUILD, DEPLOY. Nothing else until this lands.

The payload carries nine replaced models plus two page changes and has never
been swept. Sweeps are yours; I have not touched `run_all_controls.py` and will
not start one.

**DONE-WHEN** the testing site serves the nine new hulls, the sweep receipt
fingerprint matches the payload, and you have said what the sweep returned.
**If a control is red, stop and report it. Do not use `-IgnoreSweep`.**

## Q2 — Look at the nine and say what you see

`X1`, `X1_Force`, `X1_Velocity`, `Freelancer`, `Freelancer_DUR/MAX/MIS`, `85X`.

Three specific questions, because these are the claims I made and they should be
checked by someone who did not make them:

- **X1 was one of the four see-through hulls.** Is it still?
- **The 85X should be one ship, not two.** Is it?
- **X1 and X1_Force were the same file** and both wore the Velocity's fins. Are
  the three now visibly different from each other?

**DONE-WHEN** each is loaded in the inspector, shot, and answered yes or no. A
picture settles these; a measurement does not.

## Q3 — The three framing margins, still outstanding

Re-run your corner projection on **ATLS, ATLS GEO, Reliant Kore** against the
deployed page. The fit no longer uses the guessed 1.45 constant - it solves the
eight box corners against the 32-degree lens at the opening angle, with
`CC_FIT_MARGIN = 1.06`.

**DONE-WHEN** the three margins are reported. **If any is still negative, say
so - do not raise `CC_FIT_MARGIN` to make it pass.** A margin that has to be
tuned to pass is the bug we just removed.

## Q4 — BUILD THE CONTROL THAT WOULD HAVE CAUGHT A BAD MODEL. This is the big one.

**I said out loud that no check exists which could catch a bad model without a
human looking at it, and that is still true.** It is the reason the Vulture
fooled me for an hour with every declared total agreeing, and the reason a
32 KB file that claimed 164,000 triangles nearly shipped.

Build `checks/_verify_model_plausible.py`. For every one of the 256:

    1  the file begins with the bytes `glTF`. A JSON file wearing a .glb name
       is the exact failure that nearly shipped today.
    2  it parses, and its triangle count is > 0.
    3  its largest dimension is within a stated tolerance of the ship's
       published largest dimension. Both sides sorted, so an axis convention
       cannot produce a false mismatch - that is Build's own method from the
       eight-hull memo and it is the right one.
    4  no axis is more than ~2x its published counterpart. The 85X was exactly
       twice its height and nothing caught it; this is the rule that would have.

**Rule 12: it must have a control that could fail.** Copy a model, scale one
axis by two, and prove the check goes red on it. A check that has never been
shown to fail has not been shown to work.

**Rule 16: the published dimensions must come from a different source than the
models** - the Fleetyards/CIG record, not anything derived from the `.glb`.

**The 85X will trip rule 3 and that is expected.** Its wings articulate - both
wing nodes pivot on the centreline at X=0.000 and left and right share one
hinge - so the stored pose is narrower than the published beam. **Give it a
named, reasoned exception rather than widening the tolerance for all 256.** One
ship with a written reason beats a threshold nobody can justify.

**DONE-WHEN** it is in the suite, green on the fleet, red on a deliberately
broken copy, and the exception list carries a sentence per entry.

## Q5 — Photograph all 256 against the new deploy

There is precedent: 295 hulls were loaded in a real browser for the marker work.
Same idea, no markers - just the hull, one shot each, consistent camera.

Report: any that fail to load, any that render empty, any whose silhouette
covers less than a few percent of frame (drawn but effectively invisible), any
that overflow the frame.

**DONE-WHEN** there is a contact sheet and a list of anything that failed one of
those four ways. **This is the thing that turns "a human walked 256 ships" into
something repeatable.**

## Q6 — The see-through four, measured before and after

Open-edge percentage on the OLD and NEW X1, from
`_to_delete/models_pre_client_swap_20260905T053243/` against what is deployed.

The old numbers: X1 6.23%, X1 Force 6.23%, Cyclone TR 3.35%, against a Vulture
control at 0.96%. **And the correlation was never clean** - the Cutlass Black at
4.08% and the Constellation at 4.72% were NOT flagged by Sleven - so treat the
percentage as an indicator, not a verdict, and pair it with Q2's picture.

**DONE-WHEN** the old and new figures sit side by side and you have said whether
the replacement actually improved it or merely changed it.

---

## Not on this queue, and not to be started

**The five Constellations** - Sleven ruled them a pet peeve, cancelled.
**Cyclone TR and Centurion** - parked, both need wheel placement, both mine.
**`const SHIPS = []` living in two hand-maintained files** - your control is
right and the fix is mine, not yours.

## Standing constraints

- Testing only. **Do not deploy the live site.**
- Do not `git add -A`. Nothing commits or pushes without Sleven's go-ahead.
- Never delete - `mv` to `_to_delete/`.
- If an item is wrong, ambiguous or badly ordered, say so and take the next one.
  You have been right against me four times and twice today.
