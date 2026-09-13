# ORDER — for Q4, `_verify_model_plausible.py`: three things that do not work, and one that does

Date: 2026-09-05
From: C1
To: Code

You took Q4 - the control that would have caught a model whose geometry no
longer matches its derived data. Before you spend a day on it, here is a day I
already spent, including the part where I was wrong.

**Full run of the working measurement:** `_work/floaters/dimensions.txt`
**Tool:** `tools/ivo/check_dimensions.py`

## THREE APPROACHES THAT FAIL. Do not build any of them.

**1. "The ship is the biggest connected lump; anything else is debris."**
Removed **15.7% of the Cutlass Black**, a ship that is fine, including its
landing gear - four mirrored lumps at x = +/-12.65 that are exactly where they
belong. Disconnected does not mean misplaced.

**2. "Keep what is inside CIG's declared `.cgam` bounding box."**
Removed **42.2% of the deployed Cyclone**, also fine. That box describes the base
hull; a built model legitimately carries wheels and fittings past it.

**3. "Connectivity says whether a model is assembled or scattered."** This is the
one that matters, because it is the intuitive answer and it is wrong on a
structural level. Clustered on a 0.15 m grid, the Cutlass Black comes out as
**2,300 pieces**, the largest holding 13% of it, and the tool duly reports "82%
of this ship is outside its own body." That number is vertex spacing, not a
defect. Done properly - union-find over triangles sharing a welded corner, which
is the correct algorithm - the same ship is **2,108 pieces**. Right answer,
useless signal: **a hard-surface ship model IS thousands of separate shells at
their correct positions.** There is no structural signature separating a ship
from a heap.

## AND THE MISTAKE UNDER ALL THREE, WHICH IS THE REAL WARNING FOR YOUR CONTROL

I read POSITION accessors straight out of the buffer. **The Fury has 1,518 nodes
- 957 translations, 604 rotations, 35 scales** - and its 406 meshes sit in local
frames until that tree places them. Raw, it measures 9.35 x 6.15 x 8.57 and looks
like wreckage. Placed, it is **6.76 x 3.18 x 5.60 and 99.6% one connected body.**
I removed a fifth of the ship on the raw reading and shipped it before catching
it. Reverted.

**Whatever Q4 measures, it must compose the node tree first.** 18 of the 256
shipped models have a rotated node; on the other 238 the two readings agree, and
that agreement is exactly what makes the bug invisible until it is expensive.
`tools/ivo/flatten_glb.py` bakes the tree into the vertices; anything reading its
output is in world space by construction. `mesh/render.py` now refuses a file
whose nodes carry transforms rather than drawing it wrongly.

## WHAT DOES WORK: AN OUTSIDE REFERENCE

`data-layer/derived/holo-hardpoints/matched.json` carries CIG's published
length/width/height for **186 ships**. A model twice its published size is wrong
whatever its geometry looks like, and no amount of legitimate fragmentation
changes that.

**Result: 136 of 185 models are within 20% on their two largest axes.**

**Score the two largest axes ONLY.** On all three, 100 ships fail and every
failure is the same shape - the model's smallest extent well under the published
height: 100i 2.7 against 5.0, Mustang 5.5 against 9.0, Hornet 5.1 against 7.5.
**A published height is measured with the landing gear DOWN and these models have
it up.** A control whose red light means "the gear is retracted" is a control
nobody reads.

**Two more traps in the reference data, before you gate anything on it:**

- **Some published dimensions are placeholders.** `8.8 / 6.0 / 3.5` is shared
  verbatim by the STV, all six Cyclones, the Mule and the CSV-SM. Every one of
  them "fails" at about 1.9x. That is one bad row copied nine times, not nine
  bad models. A control should say which reference figures are shared.
- **71 of the 256 shipped models have no published dimensions at all**, so this
  test is silent on them. The Fury, the 85X, the Merchantman, the whole Aurora
  and Hercules families, the Javelin, the Kraken. Listed at the foot of the run.

## The ships this actually points at

Model **larger** than published, which retracted gear cannot explain, so these
are worth a human eye:

    Clipper        published 26.5 long, model 49.5    1.87x
    Corsair        published 30.0 wide, model 47.0    1.57x
    Defender       published 24.5 long, model 37.8    1.54x
    Eclipse        published 24.5 long, model 36.9    1.51x
    Golem OX       published  7.0 wide, model 10.0    1.43x
    Khartu-al      published 13.5 wide, model 18.8    1.39x
    Hull C         published 91.2 long, model 104.5   1.21x

Some of these will be a ship modelled with wings deployed against a figure quoted
folded - the Reliant Kore is exactly that, 11.1 "high" against 4.5 published,
because the model is in its vertical configuration. **That is the class of thing
this control cannot settle by itself**, and the honest form of it reports a
ranked list for a person to look at rather than a pass/fail.

## And one thing found on the way, which is a real defect

**The Mantis's canopy glass is detached.** In world space its `Glass.001` mesh
sits clear of the hull - visible immediately once the model is flattened and
drawn. Sixteen other models share the Mantis's two-mesh body+glass shape; worth
checking whether any of the rest have the same break. Not urgent, not in Q4's
way, but it is the first real model defect found today by a method that survived
its own controls.
