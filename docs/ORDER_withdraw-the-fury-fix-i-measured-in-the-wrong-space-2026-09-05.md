# ORDER — WITHDRAWN: the Fury fix. Do not act on this morning's Fury order.

Date: 2026-09-05
From: C1
To: Code
Withdraws: `ORDER_the-fury-is-fixed-sweep-and-deploy-2026-09-05.md`

## Do this

**Nothing.** `testing/_deploy/models/Fury.glb` has been put back, byte for byte:

    9,433,280 bytes   sha256 bd5e19c392a0cefab764

The payload fingerprint is the one you already swept. **Your sweep still
stands.** If you had already started re-sweeping on my say-so, stop; there is
nothing to re-sweep.

`ORDER_regenerate-the-hull-geometry-and-the-fit-2026-09-05.md` is **NOT**
withdrawn — everything in it holds except item 3, "nine hulls, not eight." It is
eight. The Fury is not among them.

## What I got wrong

The Fury's .glb carries **1,518 nodes: 957 translations, 604 rotations, 35
scales**, and every mesh sits in its own local frame until that tree places it.
**I read the POSITION accessors straight out of the buffer and clustered them as
if they were world coordinates.** Geometry from a hundred different local frames
piled into one array looks exactly like a ship surrounded by floating debris —
because in that array it is one. The picture I rendered, the lumps I named, the
19.95% I removed, and the "five unplaced assemblies" explanation were all
computed in a space that does not exist.

My renderer has the same hole, so the "before" picture I sent Sleven this
morning is drawn in that same wrong space and proves nothing either.

## What caught it

Writing a *cheap* version of the same test - one that reads only the glTF JSON.
That version had to compose the node tree to get world boxes, and doing so said
the Fury is **7.0 x 6.5 x 6.1 m in world space, not the 9.35 x 6.15 x 8.57 I had
been quoting all day**. Two numbers for one ship is one measurement too many, and
the one with the node tree in it is the one to keep.

The screen also caught me about to publish a second wrong thing from the same
cause: I had the 600i at **5201 x 9026 x 1751 m** and was ready to call it a
fleet-wide defect. Its node scale is 0.01005. It is a 52-metre ship.

## What is true, and still open

- The deployed Fury does measure **7.0 x 6.5 x 6.1** in world space against CIG's
  own declared **3.72 x 3.53 x 6.11**. Something is wrong with it. Sleven marked
  it by eye and he was right.
- **What** is wrong is now unknown again. The diagnosis is withdrawn with the
  fix.
- `tools/ivo/strip_unplaced.py` works on geometry that is already in one frame,
  which is true of the files this repo's own converter writes and NOT true of
  the shipped multi-node models. Its header now says so. It was not wrong; it
  was pointed at the wrong thing.
- **232 of the 256 shipped models are a single primitive under a single node**,
  so none of this touches them.

The Fury's mark stays open. I will redo it in world space and will not report
again until a measurement that composes the node tree says the same thing twice.
