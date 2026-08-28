# BUILD AND DEPLOY. I found a real defect while cleaning up — markers sitting at the dead centre of the ship — and fixed it.

**2026-08-27 21:15 local · C1** — read from `date`.

    client marker records added for 41 hull(s) the dataset had none for
    client hardpoint overlay: 1693 port(s) moved onto CIG positions

Down from 1,720 **on purpose**. 27 of those were wrong.

## The defect

A node whose transform is exactly the hull origin is a node whose transform was
**never set** — CIG's identity value — not a gun mounted at the dead centre of
the ship. There is no physically mountable exterior port at a hull's origin; the
origin is inside the hull.

**`Paladin / hardpoint_remoteturret_middle` is a port the ship page DRAWS**, and
it was being given `[0.0, 0.0, 0.0]`. A turret marker floating in the middle of
the hull — the exact "hardpoints not set up" shape Sleven has reported before.

    overlay ports at the origin      27    1 of them drawn today
    added-record ports at the origin 318   0 drawn today

**The 318 are withheld too**, even though nothing draws them yet. A record that
says "this gun is at the centre of the ship" is wrong data whether or not
anything reads it this week.

**Exact zero, not near zero.** A mount genuinely close to the centreline is a
real mount and keeps its position. The refused ports fall back to their derived
positions rather than getting a confident wrong one.

## And my first attempt at the fix was wrong, which is worth reading

I tested the raw `pos` for exact zero. **Eleven ports were still emitted at the
origin**, because `unit` is `pos / H0` rounded to five decimals — a position of
1e-7 is not zero in `pos` and IS zero in `unit`.

**Testing the input to a rounding step tells you nothing about its output.** It
now tests the emitted number, which is the one that reaches a reader, against
both denominators the file uses.

    ports emitted at the origin, after:  overlay 0, client 0

## Numbers

    overlay      167 hulls / 1,720 -> 166 hulls / 1,693 ports
    client       41 hulls / 3,430 -> 41 hulls / 3,112 ports
    ship page    245 -> 244 classes fully on CIG coordinates

**One hull left the overlay** because every one of its CIG ports was an origin
port, and one class moved from "fully correct" to "partial" for the same reason.
Both are the fix working.

## Also closed, both mine

    _verify_rule16_labels.py   exit 0   the label was one line from me
    _verify_ship_gaps.py       exit 0   re-baselined on what the section proves,
                                        not flipped to match the new number

Placement directory matches its manifest, 284/284, zero stale.
`_verify_placement_gate.py` exits 0.

## `_verify_child_markers.py` — I need one thing from you

Its BEFORE is `loadout_marker.pre-C1-20260826.js`, a snapshot from **26 August**,
and its four pinned Retaliator positions are pre-overlay values. Everything it
compares moved on purpose. **Its own docstring says the BEFORE should be made by
re-running the build with `CC_NO_INHERIT=1`** — which needs PostgreSQL, so only
you can make it.

If you re-take it, the control goes back to testing the inheritance pass instead
of testing my overlay. **The four pinned values need re-deriving from the same
run**, or they will keep failing for the same reason.

I have not touched the file.

Testing only. Nothing to the live site without Sleven's go-ahead.

— C1
