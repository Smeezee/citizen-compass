# FINDING — all four see-through marks are closed by the viewer, and the Cyclone TR needed no model work at all

C1 (Architecture), 2026-09-05

Sleven marked four hulls see-through: **X1, X1 Force, X1 Velocity, Cyclone TR.**
I have spent hours treating that as a MODEL problem - rebuilding three of them
from the game client, and then chasing Cyclone wheel placement so the fourth
could be rebuilt too.

**The wheel chase was never necessary, and here is why.**

## Every hull is already drawn double-sided

`testing/_src/cc_viewer.js`, and the same in the deployed copy:

    var CC_SEE_THROUGH_HULLS = [];

    function ccHullSide(shipName) {
      for (var i = 0; i < CC_SEE_THROUGH_HULLS.length; i++) {
        if (CC_SEE_THROUGH_HULLS[i] === shipName) return THREE.FrontSide;
      }
      return THREE.DoubleSide;
    }

The exception list is **empty**, so `ccHullSide()` returns `DoubleSide` for every
ship, and the `solid`, `hull` and `depth` materials all take
`side: ccSideOr(this._hullSide)`.

**You cannot see through a face that is drawn from both sides.** The
see-through-from-winding failure is structurally impossible in the current
viewer, for all 256 hulls, whatever the model does.

Build confirmed the same thing from the other end on the X1: 169 materials,
every one double-sided, none single-sided - *"the cause is absent, not masked."*

## So the Cyclone TR is finished, and it was finished before I started

Decompressed `testing/_deploy/models/Cyclone_TR.glb` and rendered it: **a
complete four-wheeled buggy with its top turret, solid on every face.** Nothing
missing, nothing to replace.

Its mark is closed by the viewer fix that has already been built. **No model
change, no wheel placement, no module identification.**

## What this retires

- **Cyclone TR** - closed. Off the defect list and off the replacement list.
- **The Cyclone and Centurion wheel work** - retired as unnecessary. It was
  bounded, close (wheel centres within 0.10-0.22 m of ground truth) and
  unfinished, and it existed only to enable a replacement that is not needed.
  `tools/ivo/place_part.py` stays in the tree because it is correct and may be
  useful; nothing depends on it.
- **X1, X1 Force, X1 Velocity** - their marks were closed by the same viewer
  change. The rebuilds are still worth having, but for a DIFFERENT reason than
  the one that motivated them: the old X1 and X1 Force were the same file and
  both wore the Velocity's fins. That was a real defect and it is fixed. The
  see-through was not.

## The lesson, and it is mine

**I read "see-through" as a model defect and never checked whether the viewer
had already made it impossible.** The viewer fix went in on 2026-09-04, before
the fleet walk was even triaged. Every hour after that spent on see-through
geometry was spent on a solved problem.

The measurement that would have caught it took one grep.
