# FINDING — the Fury's defect is real and measured. My replacement was worse, so it is reverted.

C1 (Architecture), 2026-09-05

Sleven marked the Fury during his walk. I then told him and Build the cause was
**301 doubled node pairs**, Build measured 36 and refused to act on my number,
and I later confirmed Build was right and my 301 came from ignoring parent
rotations. **That left the Fury marked with no established cause at all**, and
it has stayed that way since. Tonight I looked at the model itself.

## The defect is real, and it is not doubling

Decompressed and rendered from `testing/_deploy/models/Fury.glb`: the ship sits
in the middle of the frame with **large detached chunks floating around it** - a
ring/engine assembly above and left, a fuselage section below and right, and
smaller debris. It is not two copies of the ship. **It is one ship in pieces.**

The bounding box says the same thing without a picture:

    deployed Fury      9.35 x 6.15 x 8.57
    CIG's own hull     3.72 x 3.53 x 6.11

**Two and a half times too wide and nearly twice too tall.** The Fury is a snub
fighter about six metres long; the deployed model's box is inflated by debris
sitting metres off the hull. The length is the giveaway - 8.57 against 6.11 -
because a scattered part pushes the box out in every direction at once.

`Fury_LX` is off in the same direction, less badly: 5.05 x 2.56 x 6.46 deployed
against 3.78 x 3.32 x 6.40 from the client. Length agrees; width and height do
not.

## My replacement was worse and is reverted

I converted `MISC_Fury.cgam` and `MISC_Fury_LX.cgam` out of `Data.p4k`,
compressed them, installed them - and then rendered them, which is the step that
saved this from shipping.

**The result is not a Fury.** One connected object at the right overall size,
and a jumble: a chimney-like column standing off the top, spiky fragments
through the body, nothing resembling the sleek snub fighter. Whatever
`MISC_Fury.cgam` holds, my reader is not turning it into the ship.

**Both are reverted to the originals.** The payload fingerprint is back to
`675bc38080d1421b3334`, which is the one Build already swept, so nothing about
its sweep is invalidated.

## Why it is worth saying that the numbers looked fine

Every figure I had said the replacement was right:

    correct overall extents          3.72 x 3.53 x 6.11 against a published ~6 m
    one connected object             no detached debris
    triangle count plausible         396,251
    valid GLB, compressed clean      2.3 MB

**A model can pass every number I know how to check and still not be the ship.**
That is the third time today the same shape of thing has happened - the Vulture
blob whose totals all agreed, the 32 KB file that claimed 164,000 triangles, and
now this. The picture is the check that catches it, and it is the one that
cannot be automated away.

## Where the Fury stands

- **The mark stays open.** The defect is confirmed and measured; the cause is
  scattered geometry, not doubling.
- **My 301-pairs claim is withdrawn** for the second time, and this finding is
  the record of what replaced it.
- **No replacement exists.** Reading `MISC_Fury.cgam` correctly is unfinished
  work, and it is mine.
- Sleven should look at the two renders before anyone tries again - he knows
  what a Fury looks like and I evidently do not well enough to judge it alone.
