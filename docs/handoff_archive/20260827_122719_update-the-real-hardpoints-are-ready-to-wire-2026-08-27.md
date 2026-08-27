# Update — 754 real hardpoint positions, in the overlay format your build already reads

**C1, 2026-08-27 12:41 local.** Not a request to start now — you are mid scale
fix and this deliberately does not collide with it. Read the last section first
if you only read one.

## What is on disk

    data-layer/derived/holo-hardpoints-align/alignment_overlay_client.json
    data-layer/derived/holo-hardpoints-align/MANIFEST_client_overlay.json

**64 hulls, 754 ports.** Real per-hardpoint coordinates out of CIG's own
geometry in `Data.p4k`, not derived from mount names.

Written BESIDE `alignment_overlay.json`, never over it. **Nothing reads it yet.**

## The join is an exact string equality, and that is the whole trick

`ships.json` gives every port a `HardpointName`. It is the SAME STRING as the
node name in the ship's `.cga`:

    HardpointName      hardpoint_weapon_nose_left
    .cga node name     hardpoint_weapon_nose_left

So the port a reader clicks and the transform the game uses to place that gun
are joined on CIG's own identifier. No fuzzy matching, no name similarity, no
vocabulary translation. 796 port names matched across 68 hulls on the first
attempt.

## How wrong the current markers are — measured, not asserted

Distance between each current marker and the real mount, normalised so 1.0 is
the hull's longest half-extent:

    median across 64 hulls        0.488
    AEGS_Reclaimer                1.090 median, 1.507 worst
    ESPR_Prowler                  0.963 median, 1.669 worst
    ANVL_Gladiator                0.895
    AEGS_Vanguard                 0.874
    DRAK_Corsair                  0.830
    best hull (ANVL_Arrow)        0.181

**The typical marker is about half a hull-length from the gun it names.** On the
Reclaimer the average marker is further from its mount than the hull's own
half-length. That is what Sleven has been reporting for three weeks.

## Checked before filing

    T1  overlay keys not in the fleet record            0
        overlay ports not in the fleet record           0
    T2  mirrored left/right pairs still mirrored        199 / 208
    T3  units outside +-1.05 of the half-extent         8 of 754

T1 is the one that matters to you: `build_holo_data.py` sys.exits if an overlay
entry matches nothing, and this emits only from the intersection, so it cannot
trip that guard. **That is by construction, which is weaker than a test - run
the build and let the guard speak for itself.**

The eight in T3 are named in the manifest. Herald's `weapon_regen_pool` is an
abstract port with no physical location; the Asgard's CML entries want an eye.

## THE PART THAT MATTERS TO YOUR SCALE FIX — and it is good news

**Rescaling a model does not invalidate these positions.**

    unit = pos_glb / H
    pos_glb = metres x glb_extent / Length      H = glb_extent / 2

Scale the model by f and `glb_extent` scales by f, so `pos_glb` scales by f and
`H` scales by f. **The ratio is unchanged.** The `unit` values in this overlay
are invariant to any rescale you apply.

`pos_model` is NOT invariant - it is scaled back out using each hull's own
existing `unit`/`pos_model` pair, so it moves with the model. **Regenerate this
file after your rescale lands** (`python3 build_hardpoint_overlay.py`, a few
seconds, no p4k access needed) and `pos_model` follows. The `unit` values will
come out identical, which is itself a check on the rescale: if a hull's `unit`
values MOVE after a rescale, something scaled the position and the box by
different amounts.

## Not started, not ordered, waiting on Sleven

Wiring it in means either merging into `alignment_overlay.json` or teaching
`build_holo_data.py` to read both. **The second is better** - the hand-made
overlay is somebody's deliberate correction and should not be silently
outvoted by a generated file, and keeping them apart means a bad generation can
be reverted by deleting one path.

Sequence, when he says go: your rescale lands, this regenerates, then wire, then
build, then the marker distances get measured again against the deployed page.

*C1*
