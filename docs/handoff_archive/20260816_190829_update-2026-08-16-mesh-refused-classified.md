# Update - overlay committed; the 15 the mesh gate blocked, classified

`218bce1` **The same hull in the same place, and the ships that only looked
alike.** Overlay, verifier, dataset, and the read-time apply in
`build_holo_data.py`.

## The mesh-blocked pairs, against the configuration test

Sleven's test: same ports + same published dimensions + same pilot DPS + one
name contains the other.

**4 pairs qualify as configurations of one hull (3 families):**

    Razor    vs Razor LX          markers 0.662   boxes differ 5.2%  (one axis)
    Cutter   vs Cutter Rambler    markers 0.410   boxes differ 14.8% (one axis)
    Cutter   vs Cutter Scout      markers 0.404   boxes differ 14.4% (one axis)
    Terrapin vs Terrapin Medic    markers 0.154   boxes differ 6.7%  (one axis)

**28 pairs do not**, and the test says why for each - most fail on pilot DPS,
which is the cleanest signal in the set:

    A2 vs C2/M2 Hercules        different pilot DPS
    Vanguard Harbinger/Hoplite/Warden   different pilot DPS
    MISC Reliant Kore vs Mako/Sen/Tana  different pilot DPS
    Glaive vs Vanduul Scythe            different pilot DPS
    Aurora LX vs the other four         different pilot DPS
    Mustang Alpha/Beta vs Gamma/Omega   different pilot DPS
    MISC Freelancer vs MAX              different dimensions AND DPS
    300i vs 325a                        different dimensions AND DPS

No Best In Show, Pirate Edition or livery appears in the blocked list - those
were either already mesh-identical and are now aligned, or were already inside
tolerance.

## Before changing them - the thing I want ruled on

The premise was that a mesh difference between configurations is an export
artifact. For the Gladius Pirate at 8.7% that is very likely right. For these
four I am less sure, because **the difference is in ONE axis and it is the axis
that would carry the mount:**

    Cutter   [5.56, 12.72, 19.89]  vs Rambler [6.53, 12.72, 19.71]
             height +17%, length and width identical to the centimetre

That is the shape of a raised roof, not of an export setting - the Rambler and
Scout are the Cutter with a different cab. Terrapin vs Medic is the same
pattern, 15.31 vs 16.40 on one axis. If a mount sits on that roof, aligning it
to the base Cutter's position puts it where the Rambler's roof is not.

So: **4 pairs qualify by the stated test, and 2 of the 3 families have a
one-axis shape difference that looks real rather than exported.** Razor vs
Razor LX (5.2%) and Terrapin vs Medic (6.7%) are the safer two; the Cutters are
the ones I would want a look at first.

Nothing changed. Reporting, as instructed.
