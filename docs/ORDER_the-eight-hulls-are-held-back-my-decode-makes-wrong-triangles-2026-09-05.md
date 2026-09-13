# ORDER — the eight replacement hulls are out of the payload. My decode makes the wrong triangles.

Date: 2026-09-05
From: C1
To: Code

## What changed on disk

Eight models in `testing/_deploy/models/` have been put back to the sc-ships
build, rebuilt through `cc-uvfix-compress.cjs` from
`sc-ships/<name>/model_scaled.glb`:

    85X  Freelancer  Freelancer_DUR  Freelancer_MAX  Freelancer_MIS
    X1   X1_Force    X1_Velocity

My versions are kept, not deleted, in `_work/ivo/_mine_held_back/`.

**The payload fingerprint has changed. Re-sweep before deploying.** The Fury is
untouched and is still the file you swept.

## Why

The hulls I decoded out of CIG's `#ivo` files this morning have the right
vertices and the wrong triangles.

**Measured against the site's own Gladius, which shares no code and no bytes
with my decoder:**

    the site's Gladius       416,502 tris     936.3 m2 surface
    my Gladius               339,426 tris   4,316.7 m2 surface     4.6x

Both are the same ship to within a few centimetres of bounding box - 17.0 x 5.6
x 19.8 against 17.4 x 5.1 x 19.7 - which is why the silhouette looked right and
every count I checked agreed. The area is where it shows.

**It is a tail, not a systemic misread.** My median triangle edge is 3 cm, which
is real geometry; the p99 is 1.41 m against the reference's 0.63 m, and the max
is 6.91 m on a 19.8 m ship. Drop every triangle with an edge over 1 m and the
area lands at **917.8 m2 against the reference's 936.3**, keeping 92.8% of the
triangles. So roughly **7% of my triangles span the hull** instead of tiling it.

**Independently, open edges** - unique edges used by exactly one triangle,
degenerates removed, positions welded at 2 mm:

    Vulture        (site)   0.63%
    Arrow          (site)   5.92%
    Cutlass Black  (site)   7.42%
    my Freelancer          78.09%
    my X1                  65.70%
    my Gladius             67.71%

    the same eight, reverted, measured the same way:
    Freelancer              4.18%      X1   2.29%      85X   10.72%

## What I chased first and why it was wrong

I thought CIG's index buffer was a triangle STRIP read as a list, and the open
edges collapse from 78% to 20% under a strip reading, which looked like a
finding. **It is not one.** CIG's descriptor states an index count that divides
by three, and so does every one of the 176-plus subsets independently - that
does not happen to a strip. The strip reading also puts the Gladius at
**12,564 m2**, thirteen times the reference, which is worse than what I have.
The list reading is right; the index BASE is what is wrong on about 7% of
triangles, and that is the unfinished work.

## What I am asking for

1. Re-run the sweep against the new payload.
2. Deploy testing if it is otherwise clean. **Testing only.**
3. Nothing else here is for you - the decode is mine to fix.

## What this costs, stated plainly

The eight reverted hulls carry back the defects Sleven marked in the fleet walk:
the plain Freelancer is the pre-v2 airframe at 32.2 m, the X1 and X1 Force are
the same file again. **I am choosing a known, catalogued wrong model over an
unverified one.** A replacement that puts 7% of its triangles across the hull
would be marked again on the next walk, and rightly.

`ORDER_regenerate-the-hull-geometry-and-the-fit-2026-09-05.md` still stands but
its subject is now smaller: with the eight reverted, **the holo placement fit
should no longer be stale against them** - their geometry is what it was when the
fit was made. Check that before doing the re-decode work; it may be that the gate
goes green on its own and the only stale entry left is nothing at all. If so, say
so and skip steps 1 and 2 of that order.
