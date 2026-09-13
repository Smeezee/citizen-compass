# Update — the 85X renders exist now, and the caveat matters as much as the pictures

**Code**

    docs/renders_20260905/85X_1_whole.png    129,642 bytes
    docs/renders_20260905/85X_2_xlt4.png     126,572 bytes   736 primitives
    docs/renders_20260905/85X_3_xge4.png      94,038 bytes   249 primitives

Same camera on all three, nothing edited in any model file.

**736 + 249 = 985, which is every primitive in the file.** The two halves add up
to the whole ship, which the earlier attempt did not.

## Three defects in my own harness, all found in the output

1. **Three byte-identical images.** The inspector draws on demand; toggling
   visibility repainted nothing. Fixed by calling the page's own `draw()` and
   awaiting a frame.
2. **Name matching reached 26 of 985.** GLTFLoader puts the node name on a Group
   and leaves its primitive children unnamed, so `o.isMesh && names.has(o.name)`
   missed nearly everything.
3. **Walking up to the nearest named ancestor still reached only 455 of 985** -
   and 455 is worse than 26, because it looks like it worked. Two images that
   each omit half the ship are actively misleading for a picture whose job is to
   say which cluster is real.

Now partitioned by POSITION, which covers all 985 by construction rather than by
whether a name plumbed through. The reasoning is in the file at the fix.

## THE CAVEAT, and C1 should read this before trusting the split

**The threshold is my reconstruction of C1's X=4, not C1's X=4.**

Their coordinates are this file's multiplied by 5.840674 - the `CC_SCALE_ROOT`
wrapper, confirmed exactly by their dominant offset 8.747 against my 1.498. So
X=4 becomes 0.6849 here, which is 0.594 of the way along the hull's X extent,
and that fraction is what the render splits on.

**But our histograms still do not reconcile even after that factor**, over the
same 246 mesh-bearing nodes: theirs spans -4..13 with a clean gap between 3 and
5; mine spans -37..32 after scaling, with no empty bin. And the split I rendered
gives 736/249 primitives where C1's clusters were 110 and 136 NODES - different
units, so not directly comparable, but not obviously the same division either.

**So these pictures may not show the division C1 measured.** They show the
division at C1's stated threshold as best I can map it. If the images do not
look like two ships, that is evidence about my mapping, not about the 85X.

What would settle it: C1's script, or the histogram re-run against the DEPLOYED
file. If theirs shows -37..32 on this file, we agree and only the threshold
needs restating. If it still shows -4..13, they are measuring a different copy -
which is the same shape as the Fury disagreement, and would explain both.

## Standing

- Fury: 36 coincident, not 301. Stopped, untouched.
- ATLS, ATLS GEO, Reliant Kore: all three still CROPPED, vertically, measured.
  Radius not touched.
- Triage section 1: blocked - the marks are in Sleven's browser only.
- Nothing deployed. Nothing committed.
