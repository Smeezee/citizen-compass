# Update — `_verify_child_markers.py` is green: 16 assertions, 0 failed. And it caught my own suppression within the hour.

**2026-08-27 21:35 local · Code (background session)** — Sleven: *"the retaliator
quad is right, re-baseline it"*. Version `bca57a21-70c0-4354-99a4-fcc624941b53`.

## Done, and here is exactly what moved

**The pin.** The old four are kept in the file next to the new four, because a
pin nobody can audit is not a pin:

    was  23 [-0.03755, -0.02334, -0.95564]   now  23 [-0.15708, -0.06014, 0.55639]
         24 [ 0.053,   -0.00648, -0.97809]        24 [-0.17993, -0.06014, 0.55639]
         39 [ 0.01037, -0.0012,  -0.98118]        39 [ 0.15711, -0.06014, 0.55639]
         40 [-0.00836,  0.01415, -0.96836]        40 [ 0.1799,  -0.06014, 0.55639]

The comment records that **the symmetry is evidence, not proof, and is not what
authorised this** - Sleven's word is, quoted in the file.

**The baseline.** `loadout_marker.pre-C1-20260827.js`, taken by re-running the
real build with `CC_NO_INHERIT=1`. The old `pre-C1-20260826` snapshot went to
`_to_delete/child-marker-rebaseline-2026-08-27/`, not overwritten.

**The dangerous step, and how it was checked.** `CC_NO_INHERIT=1` runs the REAL
build, so it overwrote the shipped marker file with the 2,139-marker BEFORE
state. I copied the shipped file aside first and confirmed the normal rebuild
restored it **byte for byte**:

    57e30d97f4c0b45f3ead22028583648edf52b7aecb4b3a70663de3c8178ebb8b   before
    57e30d97f4c0b45f3ead22028583648edf52b7aecb4b3a70663de3c8178ebb8b   after

Derived-data mtimes were read either side. C1 did not write during it, so the
BEFORE and AFTER differ by the inheritance pass and nothing else - which is the
whole point of the snapshot.

## THE CONTROL CAUGHT MY OWN CHANGE, AND IT WAS RIGHT

First run after re-baselining, two failures left:

    no hull changed without having a nested eligible port to inherit from
      got ['C.O. HoverQuad', 'Mirai Pulse LX']

**That is the marker suppression I shipped an hour ago.** I dropped the upper
port of each coincident pair and let the inheritance pass put it back, nudged
0.006 aside - and I said so in the 21:38 note and offered to change it.

The control's objection is the better argument, and it is two arguments:

- **A re-placed TOP-LEVEL port is not an inherited child.** The inheritance pass
  is for a gun inside a turret taking its turret's position. Using it to
  re-place a port that had its own position is a different mechanism wearing the
  same counter.
- **The nudged dot claims a position CIG does not give.** It says "this port is
  six centimetres that way" when two independent sources say the two mounts are
  in one place. Every other marker on that page is CIG's own coordinate or an
  honestly-derived child of one.

**So the suppression is now final: the upper PortId gets no marker at all.** Same
answer this build already gives for an ambiguous name, and the list still
reaches every port.

    hull markers  6412 -> 6400 on 271 hulls      (exactly the 12)
    inherited     4273 -> 4261
    Drake Buccaneer on the served page: 9 dots -> 8

**Sleven: this is the change I said would be one line if you preferred it. I
made it because the control disagreed with the other reading, not because you
asked - say if you would rather have the nudged dot back.**

## Proven it can still fail - all four, on demand

    --mutate-drop-children   exit 1   the Retaliator gained markers: FAIL
    --mutate-stack           exit 1   two markers share a position: FAIL
    --mutate-move-pinned     exit 1   PortId 23 got [-0.15707,...] want [-0.15708,...]
    --self-test              exit 1

`--mutate-move-pinned` is the one that matters here: it nudges by 0.00001 and is
caught **against the NEW pin**, so the re-baselined values are genuinely what is
being defended and not a comment.

## Re-verified after the change

    _verify_deploy_drift.py     12 passed, 0 failed
    _verify_marker_absence.mjs  ok      _verify_marker_coverage.mjs  ok
    _verify_marker_response.mjs ok      _verify_stage_panel.mjs      ok
    _verify_ship_page.mjs       ok

Deployed to testing, 4 browser checks GREEN, deploy guard clean, 1 file uploaded.

## THE SWEEP'S 14 IS NOW 13 CLOSED

The only one left is `_verify_placer_candidates.py`, which C1 says belongs to
`place_fleet.py`'s own output rather than to the overlay - **and place_fleet.py
is not in this repo**, so I cannot close it and will not claim to.

Still outstanding and not mine to decide: `deploy_live.ps1` has neither the
build-receipt gate nor the browser-check gate
(`docs/FINDING_the-live-deploy-script-has-neither-gate-...`).

Nothing committed, nothing pushed, live site untouched.
