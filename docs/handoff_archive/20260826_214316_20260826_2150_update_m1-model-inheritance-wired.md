# Update — queue item 2 done: 76 editions gained a model. Committed 6e25e27.

**2026-08-26 · Code** — progress update, not a stop. Taking item 3 next.

## Result

    models resolved   203 -> 279 ships (76 by inheritance)
    hull markers      3,707 on 165 hulls -> 5,490 on 232 hulls
    new asset files   none

Sixty-seven more hulls now carry markers, because an edition shares its base's
geometry and therefore its derived mount positions. No download, no new `.glb`,
nothing added to `_deploy` except entries in a generated map.

Verified in the shipped bytes rather than from the generator's own report:

    DRAK_Cutlass_Black_BIS2950  -> Cutlass_Black.glb
    ANVL_Carrack_BIS2950        -> Carrack.glb
    DRAK_Vulture_Teach          -> Vulture.glb
    AEGS_Idris_P                -> Idris-P.glb      (its own, not conflated)
    AEGS_Idris_M                -> Idris-M.glb      (its own)
    AEGS_Sabre                  -> Sabre.glb
    AEGS_Sabre_Firebird         -> Sabre_Firebird.glb
    AEGS_Gladius_Dunlevy        -> no model, correctly - it is held for review

## The 37 held ships are refused by construction

The build **exits non-zero** if the inheritance map ever names a ship from
`needs_human_review.json`. Proven by planting one - `AEGS_Gladius_Dunlevy` -
and confirming the build refused with the reason and wrote nothing. The map was
restored byte-for-byte afterwards.

That guard matters because several of the 37 would be actively wrong to
auto-map: Idris-P and Idris-M differ at the nose, Sabre and Sabre Firebird are
different airframes, Hornet Mk I and Mk II are different shapes.

## Ordering that is not incidental

Inheritance is applied **before** the takedown filter. An inherited model is
the same FILE as its base's, so if that asset is ever withdrawn the editions
must lose it too. Applying it afterwards would republish a withdrawn model
under a different ship's name.

## Two mistakes of mine, both caught by the build's own output

**The first attempt inherited nothing** - 0 of 76. I gated on `_model_absent`,
which covers only the 221 ship-page-linked ships, while most of the 76 editions
carry a loadout without carrying a ship-page link. The map I was writing into
is the loadout page's, which is wider.

**The second printed "ship-page models: 279 of 221 linked ships".** A count
that exceeds its own denominator is a line measuring something it is not
counting. The linked figure and the total are now separate numbers with
separate words, and the accounting invariant is restated over the link set
where it belongs.

Neither was caught by reading the code. Both were caught by reading what the
build printed, which is the argument for the build printing real numbers.

## Deployed and committed

Sweep **35/35**. Deployed to testing; `_verify_picker_deployed` passes against
the served bytes. Committed **6e25e27**. Not pushed.

## Next

Queue item 3: A3/A4 - rescale the Asgard to metres, and the bounding-box vs
`dim` auditor that flags and never rescales.
