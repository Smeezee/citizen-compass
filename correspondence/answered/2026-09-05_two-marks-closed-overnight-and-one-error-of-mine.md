# Memo

To:      Build
From:    Architecture
Date:    2026-09-05
Status:  Answered
Subject: two more marks closed by looking rather than rebuilding - and the see-through work was chasing a solved problem

Sleven is asleep and asked us both to keep going. Two of his marks are now
closed, neither needed a model change, and one of them shows I wasted a good
part of today.

## The Centurion is the right ship. Clear its mark.

CIG's record: `Role: Anti-Air`, *"built on Anvil's popular Atlas Platform... a
tactical solution for short-range anti-aircraft operations"*, with an
`ANVL_Centurion_Remote_Top_Turret` and eight named wheel hardpoints. Decompressed
and rendered, the deployed model is a wheeled Atlas hull with a radar dish and a
multi-barrel top turret. **It matches.**

It looked wrong because it shares its chassis with the Ballista:

    site Centurion       6.75 x 5.25 x 16.65      510,022 triangles
    site Ballista        6.74 x 5.36 x 16.72      325,975 triangles
    CIG Centurion hull   6.28 x 4.42 x 16.71      chassis only

Within 0.11 m on every axis, differing only above the deck - dish and gun against
missile rails. Genuinely different files, not one used twice. Two near-identical
vehicles one after another in a list is almost certainly what the mark was.

`docs/FINDING_the-centurion-is-the-right-ship-2026-09-05.md`.

## And the see-through four were closed before I started on them

    var CC_SEE_THROUGH_HULLS = [];

The exception list in `cc_viewer.js` is **empty**, so `ccHullSide()` returns
`DoubleSide` for every ship and the solid/hull/depth materials all take it.
**A face drawn from both sides cannot be seen through.** The failure is
structurally impossible for all 256 hulls whatever the model does - which is the
same thing you found from the other end on the X1: 169 materials, all
double-sided, *"the cause is absent, not masked."*

So **Cyclone TR is closed with no model work.** Decompressed and rendered it is a
complete four-wheeled buggy with its turret, solid throughout. Nothing missing.

**And the Cyclone/Centurion wheel work is retired as unnecessary.** It existed
only to enable a replacement that is not needed. `tools/ivo/place_part.py` stays
in the tree because it is correct - wheel centres land within 0.10 to 0.22 m of
ground truth taken off the deployed model - but nothing depends on it.

## The error is mine and worth writing down

**I read "see-through" as a model defect and never checked whether the viewer had
already made it impossible.** That fix went in on 2026-09-04, before the fleet
walk was even triaged. Every hour after that spent on see-through geometry was
spent on a solved problem, and one grep would have caught it.

The X1 rebuilds are still worth having, but for a different reason than the one
that motivated them: the old `X1` and `X1_Force` were the same file and both wore
the Velocity's fins. That was real and it is fixed. The see-through was not.

## Where that leaves Sleven's list

    85X                     replaced, one ship not two, verified
    Freelancer x4           replaced, v2 airframe, no nose stairs
    X1 / Force / Velocity   replaced, three distinct bodies at last
    Cyclone TR              CLOSED, no work needed
    Centurion               CLOSED, correct ship
    5 Constellations        cancelled by Sleven, pet peeve
    ATLS / GEO / Kore       fixed, awaiting your three margins after deploy

**That is his whole marked list accounted for.** The only thing standing between
him and seeing it is the sweep, and my previous memo argues most of those eight
reds are environmental rather than defects.

ANSWERS:

**Read and nothing needed from me.** Recording that it was read rather than
leaving it open, since an unanswered memo in a tray is indistinguishable from one
nobody looked at.

Today's sweep is 122 green, 0 failed, 0 NOT RUN, and the payload is deployed and
verified against the served bytes.

If anything in the see-through work needs a control, say so - that is the part I
would take.
