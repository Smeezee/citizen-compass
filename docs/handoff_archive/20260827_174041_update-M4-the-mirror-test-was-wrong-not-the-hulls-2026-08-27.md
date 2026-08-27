# Update — M4. Sixteen hulls were being failed by my test, not by their data. And it did NOT move coverage.

**C1, 2026-08-27 18:34 local.** My files. Overlay regenerated and unchanged at
93 hulls / 952 ports — **read the last section before assuming this bought
anything.**

    transforms acceptance   80 passing  ->  96 passing   (of 116)
    overlay                 93 hulls / 952 ports  ->  UNCHANGED

## Three faults, all in the test

**1. The tolerance was absolute.** 5 cm, applied identically to a 3-metre PTV
and a 123-metre Carrack. The Carrack's turret controllers sit a quarter-metre
apart — **0.2% of that ship** — and were being called a failed mirror. The same
25 cm on a Gladius is 1.2% and deserves to fail. **A fixed tolerance is a
different test on every hull.** Now 0.4% of the hull's own span.

**2. Left and right are not always numbered in the same order.** On the
ANVL_Hornet_F7A_MK1:

    countermeasure_left_01  (-2.599, -1.147, -0.996)
    countermeasure_right_02 ( 2.580, -1.147, -0.996)   <- its mirror
    countermeasure_left_02  (-2.599, -0.736, -1.265)
    countermeasure_right_01 ( 2.580, -0.736, -1.265)   <- its mirror

**Perfectly symmetric, and CIG numbered the sides in opposite order.** Pairing
`_left_01` to `_right_01` scored 0 of 2 on an exactly symmetric hull. The name
says which FAMILY, not which member — families are now matched as a set.

**3. The gate was asking the wrong question.** "80% of pairs mirror" measures
whether the SHIP is symmetric. Eleven hulls decode perfectly and are simply not:

    VNCL_Scythe   gun_nose_left/right   dx 0.000  exact
                  gun_wing_left/right   dx 4.061  different in all three axes
    drak_clipper  weapon_left/right     dx 0.008
                  missile racks x3      right side offset ~2.5 m throughout

Vanduul hulls and the Clipper are **asymmetric by design.** Failing them was the
page punishing the data for being true.

**The gate now asks for PROOF THE DECODE IS RIGHT: at least one exterior pair
mirroring EXACTLY.** A wrong stride scrambles names across transforms and cannot
land dx 0.000 by accident. One exact pair proves the read; the ratio only ever
described the ship, and it stays in the manifest as a diagnostic.

**This is a weakening and I am not hiding it.** A hull could in principle decode
wrongly and still land one near-exact pair. What stops that being the whole
story is that placement runs a **second, independent geometric test** — every
exterior mount must fall inside that hull's own measured box — and the two
checks share no assumption.

## AND IT BOUGHT NO NEW MARKERS. Saying so before anyone infers otherwise.

**The overlay is byte-for-byte the same: 93 hulls, 952 ports.**

`build_hardpoint_placement.py` never read the transforms' acceptance flag — it
reads every decoded hull and gates on **containment**. So the mirror gate was
never what stood between a hull and the page. **Sixteen hulls were mislabelled
in the manifest and that is all this fixed.** Worth fixing, because the manifest
is the record of what is trusted — but it is not coverage and I will not report
it as coverage.

## What IS blocking coverage, exactly

    12  no hull geometry     Basher, Fury, 85X, Mantis, Tiburon, Pitbull,
                             Tyilui, Starlite, M80, Aurora SE, Aurora Mk II
    10  no ships.json row, and no variant of it carries one with a model
     6  not hulls at all
    10  failed containment   named, geometry rejected them

**Twelve of those twenty-seven are one missing generator run.** Every one is a
Fleetyards import from today; `hull-geometry` predates them. They have models
and decoded hardpoints and cannot be placed until their boxes exist. **That is
the single largest coverage win available and it is in your lane** — it includes
the Mantis, which is one of the two ships Sleven opened at random and found
empty.

*C1*
