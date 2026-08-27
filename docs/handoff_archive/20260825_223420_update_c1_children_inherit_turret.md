# Update — C1/C2 done. Retaliator 4 -> 24. Deployed 3d19834e.

**Deployed to testing: `3d19834e-f4f4-46b1-8ac8-385f2dcc7482`.** Committing next.

## The mechanism, and it needed no inference

**A PortId is a path.** `15.loadout.0.loadout.0` is the gun, inside the mount
`15.loadout.0`, inside the turret base `15`. Trimming one `.loadout.N` walks up
a level. No name matching anywhere, and what comes back is still a PortId, so
L10 is untouched.

**The first attempt placed nothing on the Retaliator and still reported 2,052
inherited markers.** The turret bases - PortIds 15, 18, 28, 94, 96 - **are not
slots in `LOADOUT_SHIPS` at all**, because a TurretBase is not a port a reader
can change. Walking the path up to `15` found nothing and every Retaliator child
resolved to None, while plenty of other hulls DID carry their parent as a slot
and inflated the counter. **A partial mechanism reporting a big number is
exactly the shape of thing that gets mistaken for working** - it was caught by
checking the ship the order names, not by the total.

The parent's NAME is already on the child: `hp` is the parent's hardpoint-name
index, so `turret_left` reads `hardpoint_turret_backbottom` - which the placer
positioned. The walk tries the parent slot first and falls back to the named
parent when there is no slot to walk to.

## Results

    markers          1252 -> 3707        hulls with markers  163 -> 165
    inherited        2455               refused as unseparable  0
    median coverage  38% -> 100% of ELIGIBLE ports

    Aegis Retaliator            4 of 24  ->  24 of 24
    Aegis Sabre Peregrine       2 of  2  ->   2 of  2   (already full)
    Anvil Ballista              2 of 15  ->   9 of 15
    Anvil Ballista Dunestalker  2 of 15  ->   9 of 15
    Anvil Ballista Snowblind    2 of 15  ->   9 of 15

**PortIds 23, 24, 39 and 40 hold their exact coordinates.** Asserted to 5dp
against the values in the order.

**C2, the eligibility rule, stated:** a port is eligible only if its bench type
is one of the eleven physically mountable kinds. Across the 165 marked hulls
that is **3,976 eligible of 13,497 total - 9,521 ports excluded.** Target
selectors and weapon regen pools carry no marker. Coverage is reported over
eligible, never over total.

**Zero markers share coordinates to 5dp, fleet-wide.** Siblings are offset from
their anchor; where the port's own name carries a direction (`turret_left`,
`turret_right`) the offset follows it, and where it does not the offset is a
deterministic ring that means nothing beyond "not on top of its sibling". A
final pass nudges any collision until unique, so the guarantee is produced
rather than hoped for. **The arrangement is not a positional claim** - a child
inheriting a derived parent position is still an estimate.

## THE COST, MEASURED, AND IT IS SLEVEN'S TO WEIGH

**Label crowding got worse, and it is not small.**

    hulls placing every label cleanly   159 of 163  ->  100 of 165
    RSI Polaris                          24 markers  ->  133, 100 with no room
    Aegis Reclaimer                      15 markers  ->   50, 23 with no room

**I checked whether a narrower rule would rescue it and it would not.** Marking
only LEAF ports - the gun but not the gimbal mount it sits in - gives 2,508
markers instead of 3,707, a 32% reduction, and the Polaris still carries 94.
**The crowding is intrinsic to giving every eligible port on a capital ship its
own marker, not to the mount/gun pair.** It would also leave the mounts
unselectable from the hull for no gain on the ships that actually hurt. So the
order shipped as written.

**The page handles it correctly** - H1b's solver turns labels off when they do
not fit and says `133 hardpoints · 100 have no room / show all labels anyway`.
Every marker still responds; 0 silent, fleet-wide, from the served bytes.
**But 65 hulls now open with labels down that used to open with them up, and
that is a change to what a reader sees.** Flagged, not decided.

## Five controls were pinned to counts this changed

Each was a number from the day it was written, not an assertion. All fixed by
reading the value rather than by editing the constant:

- **`_verify_label_threshold.mjs`** named the Reclaimer as its "labels fit"
  exemplar and the Perseus as its "labels do not fit" one. The Reclaimer now
  carries 50 and opens DOWN, so the section asserted the opposite of what the
  page correctly does. **Both exemplars are chosen by the solver's own answer
  now** and named in the output. Also six literal `15`s.
- **One assertion in it REVERSED, and the reversal is the result.** It used to
  record - honestly - that the fleet separated by marker count, so a plain
  threshold would have agreed with the solver and R1's claim was not yet
  demonstrated. It no longer separates: largest clean hull 28 markers, smallest
  crowded 18. **No single number reproduces the solver's split**, which is
  precisely what R1 claimed and could not previously show. Asserted in the
  direction the data now supports, with the old numbers recorded beside it.
- **`_verify_marker_response.mjs`** and **`_verify_picker_deployed.mjs`** pinned
  the Origin 400i at 10 markers and a 2/8 picker/fixed split. B8's acceptance
  was "all ten respond", and the ten was what it carried that day. The count is
  a floor now; the split is accounted (`picker + fixed === total`, both
  non-zero) rather than pinned. **52 markers, 44 picker, 8 fixed, 0 silent.**
  The deployed one only went red AFTER the deploy, which is worth knowing: it
  reads the served site, so it cannot fail during a pre-deploy sweep.

## Control

`checks/_verify_child_markers.py` — 16 assertions. Compares the shipped marker
table against a BEFORE captured by re-running the real build with a new
`CC_NO_INHERIT=1` switch, so the rise is **measured, not described** -
`place_fleet.py` carries the same switch for the same reason.

    normal                   0
    --self-test              1
    --mutate-drop-children   1  every inherited marker removed; Retaliator -> 4
    --mutate-stack           1  two markers given identical coordinates
    --mutate-move-pinned     1  PortId 23 nudged by 0.00001
    no BEFORE snapshot       2  NOT PERFORMED, never passed

**Its negative control was rewritten before it shipped.** The first version
looked for hulls with no nested ports anywhere and found three, so "not one of
them changed" was true of almost nothing. It now takes every hull that DID
change - 152 of them - and requires each to have had a nested eligible port to
inherit from, plus asserts that **every marker that existed before is still
there, unmoved.**

**Stated limit:** the control reads the shipped `loadout_marker.gen.js`. It does
not re-execute the builder, so it verifies the table the site carries rather
than proving the builder would reproduce it from scratch.

## Sweep

**78 ok, 1 failed, 3 skipped** (was 76/2/3 before this work; the extra pass is
`_verify_g3_matcher_delta.py`, which now runs).

Still red: **`_verify_stage_floor.mjs`**, crashing on
`this.camera.updateMatrixWorld`. E5's guarantee is unverified. Noted as needing
a decision rather than left silently.

## Also committing two files missed in 10c30ac

`testing/_src/loadout_marker.gen.js` and `testing/_src/loadout_model.gen.js` are
tracked and were left out of the P1/P2 commit, so the committed source did not
reproduce the artifact I deployed. Both go in this commit.

## Queued, not started

`claude/FINDING_the-dimension-table-has-collisions-2026-08-26.md` - an auditor
that decides each collision by comparing MEASURED extents, flags only, never
auto-fixes, and does not loosen the proportion guard.
