# Memo

To:      Engineering
From:    Build
Date:    2026-09-05
Status:  Answered
Subject: Q2 answered against the payload - the see-through is gone, the 85X is one ship, and two of the three X1s are identical BY YOUR OWN DESIGN

Measured in the real inspector, real browser, off the real payload. Shots in
`docs/renders_q2_20260905/`.

    ship             meshes     tris   sided        extent (m)
    85X                  53    79061   double   10.10 x  2.66 x 13.09
    Freelancer           30    82477   double   22.58 x  7.81 x 36.71
    Freelancer DUR       60   123883   double   22.58 x  7.92 x 37.17
    Freelancer MAX       29    97364   double   31.39 x  7.92 x 36.77
    Freelancer MIS       54    99135   double   22.58 x  7.87 x 37.36
    X1                  169   181544   double    1.05 x  1.78 x  4.84
    X1 Force            169   181544   double    1.05 x  1.78 x  4.84
    X1 Velocity         182   212526   double    1.24 x  1.78 x  4.84

Zero page errors across all eight.

## Q: X1 was one of the four see-through hulls. Is it still?

**No.** 169 materials, every one double-sided, none single-sided. Back faces are
drawn, so the cause is absent rather than masked.

## Q: the 85X should be one ship, not two. Is it?

**Yes.** The file is one node and one mesh - 53 primitives under it - so two
separated hulls cannot be present at all. Extent 10.10 x 2.66 x 13.09, which is
the single-cluster figure, not the old both-copies 14.0 x 13.5.

## Q: are the three X1s now different from each other?

**Two of the three are still identical, and that is what you specified.**

    X1           169 meshes  181,544 tris  1.05 m wide  geom sig 1438002580
    X1 Force     169 meshes  181,544 tris  1.05 m wide  geom sig 1438002580
    X1 Velocity  182 meshes  212,526 tris  1.24 m wide  geom sig 1348251888

X1 and X1_Force share a geometry signature sampled from the vertex buffers -
they are the same mesh. X1_Velocity differs.

**Your own order says why:** *"X1 Force keeps the bare hull, because the archive
holds no Force-specific geometry - the difference is `decal_force_*` nodes
inside the shared hull, and decals need textures we do not have."*

So the answer is yes to the defect and no to the question as phrased. **Q2 asked
whether all three are now different; the X1 order rules that out in advance.**
Raising it because the two documents disagree and somebody reading only Q2 would
record this as a failure.

**The defect you were fixing IS fixed.** Before, all three measured 1.24 m wide
- the Velocity's finned body on every one. Now the two that should be bare are
1.05, and only the Velocity carries fins at 1.24. That is exactly the correction
you described.

## A count, because it will matter when somebody verifies the deploy

**The batch is eight models, not nine.** Your memo says "Nine models, not eight"
and then lists eight; `_to_delete/models_pre_client_swap_20260905T053243/` holds
eight originals; and eight files in `testing/_deploy/models/` have changed since
09-03. X1 appears in the six of the earlier order AND in the three of the X1
order, and has been counted twice.

Nothing is missing. But anyone later checking "did all nine ship?" will come up
one short against a correct deploy, so it is worth correcting now rather than
re-investigating then.

## Q1

Sweep running. I will report what it returns and deploy if clean, per your
instruction not to use `-IgnoreSweep`.

---

ANSWERS:

**Architecture, 2026-09-08.**

**Accepted and closed.** Q2 answered against the payload. The two identical X1s are identical by the design decision that folds editions onto one hull, which is working as intended rather than a duplicate defect.
