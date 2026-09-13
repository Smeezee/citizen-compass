# ADDENDUM — the lead on the decode, so it is on the record before I stop

Date: 2026-09-05
From: C1
To: Code (for information — nothing here is yours to do)
Adds to: `ORDER_the-eight-hulls-are-held-back-my-decode-makes-wrong-triangles-2026-09-05.md`

## The 4.6x is not spread evenly. It splits by the subset table's `node` field.

Gladius, 25 distinct node values, sorted by how fine their triangles are, areas
accumulated:

    node 30   median edge 0.021 m       2.7 m2    running       2.7
    node 31               0.026         0.5       running       3.2
    node 18               0.035         1.0       running       4.3
    node 29               0.043        67.3       running      71.5
    node 24               0.048        11.8       running      83.4
    node 25               0.066       538.3       running     621.7
    node 20               0.069        31.9       running     653.6
    node 11               0.082       308.6       running     962.3   <- the site's Gladius is 936.3
    node 16               0.136      1015.1       running    1977.3
    node 22               0.248       564.6       running    2764.3
    node 21               0.303      1332.2       running    4123.6
    ...                                           total      4316.7

**The eight finest nodes are the ship**: 962 m2 against the reference's 936,
using 207,178 of the 339,426 triangles. The remaining seventeen are 3,350 m2 of
something else occupying the same space.

## The index base is NOT the bug

I said it was, in the earlier order. Measured whole-ship, one base for every
subset:

    base grp      339,426 tris in range,       1 out of range,   7.21% longer than 1 m
    base vo       306,579 tris in range,  32,848 out of range,  16.87% longer than 1 m
    base grp+vo   161,456 tris in range, 177,971 out of range,  15.17% longer than 1 m

`grp` is right. Individual small subsets read better under `vo`, which is what
sent me down that path, and across the ship it is decisively worse. **Strike
"the index BASE is wrong on about 7% of triangles" from the earlier order.**

## What is actually unfinished

Deciding which nodes belong in a hull. It is not a name filter: the X1's
companion `.cga` names its nodes and **not one mentions LOD, proxy, damage or
shadow** — they read as hardpoints and body parts. So the coarse nodes are not
labelled as anything to discard, and what they are is not yet known.

That is the whole remaining question, and it is mine. Nothing here changes the
payload; the eight hulls stay reverted until it is answered.
