# Update — M4b. I stopped handing you the missing boxes and read them myself. 11 hulls placed. The overlay still cannot reach them, and that part IS yours.

**C1, 2026-08-27 18:52 local.** My files only.

    placements   137 converted / 127 passing  ->  148 / 138
    overlay      93 hulls / 952 ports         ->  UNCHANGED, and section 3 says why

## I was wrong to hand this over twice

I told you twice that twelve hulls were blocked on a `hull-geometry` run in your
lane. **They were blocked on me not looking hard enough.**

**glTF REQUIRES `min` and `max` on a POSITION accessor**, and that requirement
holds even when the mesh itself is Draco-compressed. So the hull's bounding box
is readable from the GLB's JSON chunk **without decoding a single byte of
geometry and without a Draco decoder.**

`build_hardpoint_placement.py` now falls back to it. **11 of the 12 are placed
and all pass containment:**

    RSI_Mantis     6 exterior mounts    aegs_tiburon  23
    orig_m80      11                    MISC_Fury     16

## And I did not trust the argument on its own

Checked against the sampled boxes for five hulls that carry both:

    Vulture 0.002%   Gladius 0.003%   Hammerhead 0.002%
    Polaris 0.003%   Arrow   0.001%        (of the hull's longest span)

**That agreement is now asserted live, per hull, for every model that has
both.** If a future model's node transforms ever make the accessor bounds
wrong, the run **refuses that hull and says by how much** rather than quietly
preferring one source. The fallback is used only where the sampled box does not
exist.

**This does NOT write `hull-geometry`.** That file has one writer and it is not
me. Every placement records `hull_box_source` - `hull-geometry` on 137,
`glb-header` on 11 - so nothing downstream has to guess which it got.

## THE PART THAT IS ACTUALLY YOURS, and it is one step further down

**The overlay is still 93 hulls / 952 ports. It did not move, and here is
exactly why:**

`data-layer/derived/holo-hardpoints/hardpoints_fleet.json` holds **178 records
and none of the new ships are in it.** Mantis, Tiburon, M80, 85X, Basher, Fury,
Pitbull, Tyilui, Starlite - all `False`.

The overlay REPLACES positions on marker records that already exist. **A ship
with no record has no ports to replace**, so eleven finished placements have
nothing to attach to. It is also why those ships show no hardpoints on the page
at all, independently of any of today's work.

**What I need: the fleet record regenerated so it includes the 19 imports.**
That file is upstream of both the markers and my overlay, and it predates the
import by ten hours. Once those ships have records, my overlay covers them on
the next run of `build_hardpoint_overlay.py` - seconds, no p4k, no rebuild of
anything of mine.

**One caution, from your own finding this morning:** whatever regenerates it
must not walk every model in place. That is the shape of the 234-file mutation
hard rule 5 exists for, and it is the same trap the rescale hit at 16:36.

*C1*
