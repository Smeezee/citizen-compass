# INVENTORY — what every ship has, and what it is missing

**Built 2026-09-12 by the Adjutant desk, at Sleven's order, from the deployed test-site
files as they stood at the 2026-09-11 rebuild: `testing/_deploy/next.html`,
`loadout_data.gen.js`, `loadout_model.gen.js`, `loadout_marker.gen.js`. Counted by machine,
not by eye. The per-ship table is `claude/ship-coverage-2026-09-12.csv`, 253 rows.**

## CORRECTION, SAME DAY, BEFORE ANYBODY ACTS ON THIS

**Two counts below are wrong because this document counted the FRONT PAGE's data only.**

- **"No ship has width or height. Not one." — WRONG.** `LOADOUT_SHIPS` in
  `loadout_data.gen.js` carries `dim` as three numbers for **all 318 ships**; the Cutlass
  Black reads 37.5 x 26.5 x 11.5. The front page's own `d`, `w` and `h` fields are null on
  all 253 rows, which is a separate and real gap — the front page does not carry what the
  project holds.
- **Paint data: this document did not claim it, but two others did say we hold none.**
  `LOADOUT_PAINTS` holds 924 paints with names, manufacturers and ship tags,
  `LOADOUT_PAINTSETS` holds 105 sets, and 260 of 318 ships point at one. No textures.

Found 2026-09-12 while reading the loadout page for a separate review, and recorded here
rather than left for somebody to trip over. Everything else below was counted the same way
and carries the same limit: **it describes the front page's data, not every dataset in the
project.**

## THE HEADLINE, AND IT IS ONE CAUSE WEARING SIX FACES

**Thirty-four ships carry no hull identifier, and that single gap costs them everything
that hangs off it.** The same 34 ships — exactly the same list, checked as a set — have:

- no ship page
- no 3D model
- no length, crew or cargo figure
- no career, which is why no category button can ever show them (Q62.T-003)

**So T-003 is not a filter defect. It is thirty-four rows that were never joined to the
game-file data, showing up in the one place a visitor notices.** Fixing the filter would
hide it; fixing the join fixes all six.

**The thirty-four:** Arrastra, Crucible, CSV-FM, E1 Spirit, Endeavor, Expanse, G12, G12a,
G12r, Galaxy, Genesis Starliner, Hull D, Hull E, Javelin, Kraken, Kraken Privateer,
Legionnaire, Liberator, Merchantman, MOTH, Nautilus, Odin, Odyssey, Orion, Pioneer,
Ranger CV, Ranger RC, Ranger TR, RAPTOR, Starlancer BLD, Vulcan, Zeus Mk II MR,
F7C-M Super Hornet Heartseeker Mk I, Mustang Alpha Vindicator.

## COVERAGE, ALL 253 SHIPS

    picture                     247   missing  6     98%
    pledge price (real money)   237   missing 16     94%
    in-game price               179   missing 74     71%   (every purchasable ship has one)
    link to RSI                 229   missing 24     91%
    hull identifier             219   missing 34     87%
    ship page                   219   missing 34     87%
    3D model                    217   missing 36     86%
    hardpoint markers           195   missing 58     77%
    length                      219   missing 34     87%
    width and height              0   missing 253     0%
    crew                        219   missing 34     87%
    cargo                       219   missing 34     87%
    a written note               87   missing 166    34%
    edition line                  1   missing 252     0%

    sold somewhere in game      179   missing 74     71%
    a price per dealer           63   missing 190    25%
    a location named            179   missing 74     71%

    status: 179 purchasable in game, 74 pledge only
    role: every ship has one. career: 34 have none.

## THE FIVE GAPS WORTH A DECISION

**1. No ship has width or height. Not one.** Length is held for 219; `d`, `w` and `h` are
null across all 253. Anything that compares hangar fit, or draws a ship to scale, has one
dimension out of three.

**2. Only 63 of the 179 purchasable ships carry a price per dealer.** The other 116 show
one in-game price with the dealers named beside it, which reads as "this price, at these
shops" and is not what the data says. **This is run 3's T-011 and run 4's M-005 at scale:**
the ship page cannot show a shop price for two thirds of the ships that have shops.

**3. Twenty-four ships have no RSI link — and most of them are exactly the variants.**
600i Executive Edition, Carrack Expedition, Constellation Phoenix Emerald, F7A Hornet Mk I
and Mk II, F7C-M Hornet Heartseeker Mk II, F7C-M Super Hornet Heartseeker Mk I, F7C-M Super
Hornet Mk II, F8C Lightning Executive Edition, Gladius Dunlevy, Gladius Pirate, Mustang
Alpha Vindicator, Mustang Omega, P-72 Archimedes Emerald, Sabre Raven, Ursa Fortuna, plus
ATLS GEO IKTI, ATLS IKTI, ATLS IKTI RAD, Ballista Dunestalker, Ballista Snowblind, CSV-FM,
RAPTOR and Starlancer BLD.
**This matters directly to the variant-and-paint plan: the link that plan sends people to
does not exist for the rows that need it most.**

**4. Twenty-two ships have a 3D model with no hardpoint markers** — ATLS, ATLS GEO, Aurora
SE, Clipper, CSV-SM, Cyclone and its four variants, M80, MDC, MPUV Cargo, MPUV Personnel,
Mule, PTV, ROC, ROC-DS, STV, UTV, and the three IKTI ATLS rows. Mostly ground vehicles.
**Two ships have a page and no model at all:** F7C-M Hornet Heartseeker Mk II, Gladius
Dunlevy.

**5. Six ships have no picture:** CSV-FM, Genesis Starliner, MOTH, RAPTOR, Starlancer BLD,
F7C-M Hornet Heartseeker Mk II. Five of those six also have no ship page.

## WHAT THIS SAYS ABOUT THE WORST ROWS

**CSV-FM, RAPTOR and Starlancer BLD have nothing**: no picture, no page, no model, no
price of any kind, no RSI link, no career. **Eight rows carry no price at all** — those
three plus ATLS GEO IKTI, ATLS IKTI, ATLS IKTI RAD, Ballista Dunestalker and Ballista
Snowblind.

## METHOD, SO ANYBODY CAN RE-RUN IT

Every figure is a field count over the 253 rows in the front page's own embedded data, with
the ship page, model and marker columns tested by looking up each row's hull identifier in
the three generated data files. **No estimate, no sampling.** The CSV beside this document
carries one row per ship and one column per field, so any of these counts can be re-derived.
