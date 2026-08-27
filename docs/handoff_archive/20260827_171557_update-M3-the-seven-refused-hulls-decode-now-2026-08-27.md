# Update — M3. The seven hulls the decoder refused now decode. Zero errors on 116.

**C1, 2026-08-27 17:52 local.** My files. Overlay regenerated; nothing built.

    before   109 decoded, 7 REFUSED, 77 passing, 6,819 hardpoints
    after    116 decoded, 0 refused, 80 passing, 7,033 hardpoints
    overlay  64 hulls / 754 ports  ->  67 hulls / 775 ports

## What was actually wrong

The seven refused on one of two shapes, and both were the same fault: the node
index field carried **0xFFFF - no index assigned - on a handful of records**,
and the join refused rather than guess.

**The refusal was right.** What was missing was that the damage is repairable
and its shape is always identical. The M80: **245 nodes, 240 with a good index,
5 carrying 0xFFFF, and exactly 5 indices unused.** The holes and the gaps match.

## The repair, and it is a HYPOTHESIS

Unused indices are assigned to the unindexed records in positional order.

**That is a guess and it is labelled one.** Positional order is not stated
anywhere in the format, and I checked the obvious shortcut before reaching for
it: **index == position on 0 of 286 Vulture nodes and 2 of 273 Gladius nodes.**
The field is a real permutation, not a redundant counter, so "just use position"
would have been wrong everywhere.

**What makes the guess acceptable is that it cannot mark its own homework.** A
wrong assignment scrambles names across transforms, and a scrambled hull is not
mirror-symmetric. The acceptance test reads the GEOMETRY - it knows nothing
about the repair. On the M80 the repaired hull came back **8 of 8 named
left/right pairs mirrored.**

Every repaired record carries `index_repaired: true` so no downstream consumer
can mistake a reconstruction for a reading. **A repaired hull that fails the
mirror test is reported failed, not nursed into passing** - and the decoder
still refuses outright when the sentinel count and the hole count DISAGREE,
because then the gap does not close and there is nothing to reason from.

## Regenerated and checked before filing

    T1  overlay keys/ports not in the fleet record     0 / 0
    T2  mirrored left/right pairs in the overlay       206 / 216
        median correction, normalised                  0.491

T1 is the one that matters to your build: `build_deploy.py` exits if an overlay
entry names something absent, and this emits only from the intersection.
**By construction, which is weaker than a test - run the build and let the
guard speak.**

## Not fixed, and named rather than left implied

**36 hulls fail acceptance and 39 are skipped** - 19 with no `ships.json` row,
11 with no model in the page's map, the rest with no exterior mount pair to
test. Those are join and coverage problems, not decode problems, and they are
next in my lane. The decoder itself now refuses nothing.

*C1*
