# Update - Razor and Terrapin aligned, Cutters left, live

Live and cache-busted:

    Razor    vs Razor LX         0.662 -> 0.080
    Razor EX vs Razor LX         0.660 -> 0.031
    Terrapin vs Terrapin Medic   0.154 -> 0.051

    Cutter   vs Cutter Rambler   0.410 -> 0.410   left alone, as ordered
    Cutter   vs Cutter Scout     0.404 -> 0.430   left alone
    Gladius Valiant vs Pirate    0.049            untouched

144 markers now carried by the overlay, up from 133.

## How it was expressed

The mesh gate is no longer the last word. A pair that fails it is asked the
CONFIGURATION question from Sleven's ruling - same ports, same published
dimensions, same pilot DPS, one name containing the other - and merges into the
same cluster if it passes.

**Pilot DPS turned out to be the discriminator that does the work.** It alone
separates the three Vanguards, the four Reliants, the A2 from the C2/M2, and the
Mustang Gamma/Omega from the Alpha/Beta - all of which share a port list and are
not configurations of anything.

**The Cutters are excluded by a number that encodes a human decision, and the
code says so.** `CONFIG_HULL_TOLERANCE = 0.10` admits Razor (5.2%) and Terrapin
(6.7%) and refuses the Cutters (14.8% / 14.4%). The comment states plainly that
it is a judgement rather than a measurement, and it is written as a bound rather
than as two ship names so the next 5% edition aligns on its own and the next 15%
one is refused and reported for a decision instead of waved through.

The report now carries `config_merged` and `config_too_different`, so both the
merges and the refusals are named in the artifact rather than only in a commit
message.

Not committed.
