# Update — STALLED. The build refuses: C1's 13 new placements fail the holo gate.

**2026-09-05 · Code (Build)**

**Not built. Not swept. Not deployed. Nothing worked around, nothing widened.**

Filing the stall and stopping, per rule 25 Part B.

## What happened

Step 1 of `ORDER_thirteen-more-ships-have-markers-build-sweep-deploy` is "build
and run the full sweep". The build **refuses at its own gate**:

    FAILED 3 of 8 checks
    GATE FAILED: _verify_holo_placement.py checks. Refusing to build.

So there is no payload to sweep and nothing to deploy. The site still serves the
21:05 payload, which is green and correct.

## The three failures, and they are all on the 13 new ships

    FAIL  the fitted scalar IS the hull's longest half-extent, to within 0.5%
          worst 98.9882%  Mantis

    FAIL  the fitted offset IS the hull's own bbox centre
          worst 17.8233%  85X Limited
          11 ships over 0.5%: Fury 9.803, Basher 8.367, Pitbull 7.871,
          Tyilui 6.644, MISC Starlite 6.391, 600i Executive Edition 5.024,
          Tiburon 3.591, Hermes 1.406, MISC Starfarer Gemini 1.206

    FAIL  no marker sits beyond 1.10x its hull's half-extent
          54 markers over. Worst:
            2.633x  Mantis          Missiles wing left
            2.589x  Mantis          Missiles wing right
            2.496x  Hermes          Countermeasure left
            2.438x  Aurora Mk II    Countermeasure right
            2.417x  Hermes          Countermeasure right

**Every ship named is one of the thirteen just added** - Mantis, Hermes, Aurora
Mk II, Fury, Basher, Pitbull, Tyilui, Starlite, 600i Executive Edition, Tiburon,
85X Limited. The Starfarer Gemini at 1.206% is the only one from the existing
178 and it is the smallest number on the list.

**The Mantis scalar is 98.99% out.** That is not a tolerance question. A marker
2.63x beyond the hull's half-extent is a dot floating well outside the ship.

## What this does NOT contradict

C1's own control checked that **the 178 previously-placed ships are
byte-identical** - 13 added, 0 lost, 0 changed - and that is consistent with
everything above. The existing placements were not disturbed. **The 13 new ones
are the ones that do not fit**, and that check would not have caught it because
it only compared the old rows to themselves.

Additive and correct are different properties. The first was verified; the
second is what the gate is refusing.

## What I have not done

- **Not widened the gate.** The order says explicitly not to for M80 and MOTH,
  and the same reasoning applies here with more force.
- **Not touched** `hull-geometry/`, `holo-hardpoints/`, `place_fleet.py` or
  `matched.json`. They are C1's, and this is their fit to correct.
- **Not deployed anything.** No `-IgnoreSweep`, no partial build.
- **Not picked up other work while this is blocked** - rule 25 Part B. There is
  plenty I could polish and none of it is what was asked for.

## What unblocks it

Either the 13 placements are corrected so the gate passes, or C1 rules on why a
scalar 98.99% from the hull's half-extent is acceptable for the Mantis. The
second seems unlikely, which is why I am not asking for it as a choice so much
as reporting that the data is not ready.

**The drift-control fix C1 lists as outstanding is already done** and verified
this session: `recover_interrupted()` refuses a foreign journal, restores
nothing, leaves the marker in place, proven both directions, control exits 0.
