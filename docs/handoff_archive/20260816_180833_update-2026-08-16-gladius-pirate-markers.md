# Update - Gladius Pirate Edition markers, checked

Asked to look at the one ship whose hull check could not be run. Findings:

**It is not really borrowing anything.** It resolved to `Gladius Pirate`, which
is its OWN mount record - 12 ports, identical to the base `Gladius` record port
for port, same dimensions (21 x 17.5 x 5.5), same pilot DPS (1,597.9). So the
rule picked the ship's own data, not another hull's.

**All 12 markers are on the hull.** Distance from each to the nearest real
vertex is 1.20% of hull size or less, and 1.2% is exactly the deliberate lift
`push_out` applies. Nothing is floating. Left/right pairs are symmetric to two
decimal places. Proportion match against the published dimensions is 0.047,
against a 0.35 threshold.

**Why the hull check could not run: there is no `Gladius.glb`.** The library has
only `Gladius_Pirate_Edition.glb` and `Gladius_Valiant.glb`. My earlier decode
batch included a Gladius.glb that does not exist and I did not notice, because I
counted output lines instead of checking the exit code - the script did report
it.

**So it was checked against the sibling instead.** C3 already placed
`Gladius Valiant` - same hull class, same 12 ports, independent run:

    8 of 12 markers agree within 0.10 unit (guns, countermeasures,
      weapon rack, both regen pools; nose gun 0.081)
    4 missile racks differ by 0.27 - 0.38, all in the LENGTH axis

Mine sit at the nominal target for a wing mount (unit z 0.07-0.13, just aft of
centre); C3's sit further aft (0.39-0.44). The mount records list the racks in
the same order, so it is not an ordering difference - it is the snap landing
differently on two meshes that are genuinely different (their bounding boxes
differ by 8.7%).

**Neither is demonstrably wrong and I am not changing it on a guess.** For
Sleven's eye: on the page, are the Gladius Pirate's four missile racks in the
right place along the wing?
