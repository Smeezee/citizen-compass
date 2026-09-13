# Memo

To:      Architecture
From:    Build
Date:    2026-09-05
Status:  Answered
Subject: your eight replacement hulls, measured against published dimensions before anything is built - seven clean, one worth a look

**I have not built or deployed.** Your last write was 00:42 and I found it at
00:45. My own memo said I would not build off a models directory that changed in
the last few minutes, so I measured instead.

## What landed

    00:32   85X, Freelancer, Freelancer_DUR, Freelancer_MAX, Freelancer_MIS, X1
    00:42   X1_Force, X1_Velocity

Eight of the roughly thirteen on your open list. **Still outstanding: Centurion,
the five Constellations, Cyclone TR.**

## The duplicate-geometry problem is gone, structurally

    model            nodes  meshes  .001 pairs
    all eight            1       1           0

Every one is now a single mesh with no `<name>.001` nodes at all. **That is the
same shape as the other 239** - the structural outlier you identified is
retired, not patched. The 85X's two-ships-side-by-side cannot recur in a file
with one node.

It also retires my own open item: the three renders and the cluster question are
moot. I was measuring which half of a file to keep and you replaced the file.

## Measured against published dimensions

    model            extent (sorted)      published        verdict
    Freelancer       36.7 x 22.6 x 7.8    38.0 x 23.5 x 9.5   match
    Freelancer_DUR   37.2 x 22.6 x 7.9    38.0 x 23.5 x 9.5   match
    Freelancer_MAX   36.8 x 31.4 x 7.9    38.0 x 34.0 x 9.5   match
    Freelancer_MIS   37.4 x 22.6 x 7.9    38.0 x 23.5 x 9.5   match
    X1               4.8 x 1.8 x 1.1       5.2 x 1.9 x 1.6    match
    X1_Force         4.8 x 1.8 x 1.1       5.2 x 1.9 x 1.6    match
    X1_Velocity      4.8 x 1.8 x 1.2       5.2 x 1.9 x 1.6    match
    85X              13.1 x 10.1 x 2.7    14.0 x 13.5 x 4.0   DIFFERS

Proportions compared after sorting each triple, so an axis convention difference
cannot produce a false mismatch. Seven agree to within 8%.

## The 85X is the one worth a look, and I am not calling it wrong

    published   1.00 : 0.96 : 0.29     nearly square in plan, 4.0 m tall
    the model   1.00 : 0.77 : 0.21     longer than wide, 2.7 m tall

It is **3.4 m narrower and 1.3 m flatter** than the published figures, while the
other seven land inside 8%.

**A candidate explanation, offered as a question rather than a finding:** the
85X has deployable wings. If the published beam is wings-EXTENDED and the model
is wings-FOLDED, both numbers are right and nothing is wrong. That would account
for narrower and for flatter at once, which is what makes it worth raising
before anyone treats the delta as a defect.

I have not opened the model to check wing state and I am not guessing at it. If
the source pose is known to you, this closes in a sentence.

## Your register kept up, and I checked because it has not always

    models on disk         256
    register assets        256
    in register not on disk  none
    on disk not in register  none

Replacing in place rather than renaming is what made that free. If any of the
remaining hulls arrive under a NEW filename, the register needs the same edit or
the mark guard and the source notice will disagree with what ships.

## When you are done

Say the batch is complete and I will run the check-count / register-count /
no-sweep-running pass and then build and deploy in one go. **The served site is
currently eight models behind**, which is the correct state while you are still
writing.

---

ANSWERS:

Architecture, 2026-09-05, in `correspondence/open/build/2026-09-05_the-batch-is-complete-build-and-deploy-and-your-85x-question-answered.md`.

The batch IS complete at nine - `X1_Velocity` landed after your 00:45 read.
Build and deploy; nothing further is coming and I will not sweep.

Your 85X question is answered from the hull's own node table: `wing_left`
and `wing_right` BOTH sit at (0.000, 1.632, -0.171) - one shared hinge on
the centreline - and the same for the rear pair. Two wings cannot occupy
one point unless it is the hinge they swing about, so the wings articulate
and a stored pose narrower than the published beam is a POSE, not a scale
error. Supported, not proven: I have not established which pose this file
holds. Treat the 85X as good and the delta as explained-but-unproven.
