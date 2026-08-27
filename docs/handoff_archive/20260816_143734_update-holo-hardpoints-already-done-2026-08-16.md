# Update: the holo hardpoint wiring was ALREADY DONE and live. Verified, not assumed.

I started it, and the first thing I did was check the premise. It does not hold.

## Fetched from the live testing URL - acceptance 5, done first

    holo.html          HTTP 200
    holo_data.gen.js   HTTP 200

    ships in the LIVE data  : 167
    ships WITH hardpoints   : 167
    hardpoints total        : 1,798
    unmatched hardpoint sets: 0

Not "a handful". All of them, on the deployed page, right now.

## Why the order's check said otherwise

It grepped `testing/_deploy/holo.html` for three tokens. All three are absent
for reasons that are correct:

- **`hardpoints_fleet`** is the INPUT filename. It lives in
  `holo_data.gen.js` - the sibling file the page loads, whose own header names
  it as the source. The page never references a filename.
- **`pos_model`** is DELIBERATELY unused. `build_holo_data.py`'s header spends
  thirty lines explaining why: `unit` is used instead.
- **`pilot_dps`** is genuinely absent, and that is the one real gap. See below.

The greps were aimed at the wrong file, and two of the three were testing for
things whose absence is the correct design.

## §2, the scale problem - solved, and here is how I know

The concern is real and worse than stated. Measured across the fleet:

    model_units_per_metre   min 0.0093   median 0.9747   max 101.1621

    158 ships in metres, 8 normalised, 1 in centimetres
    MISC Starlancer TAC  0.0093    Asgard  101.1621

That is a **10,000x spread**. Any fixed multiplier is wrong on somebody.

The solution already in the source is the right one: the page uses `unit`,
normalised to the hull's longest half-extent, multiplied by a scalar
**measured from the mesh actually loaded**. The model's units cancel out
entirely, so it does not matter that the library is inconsistent.

**How I know it holds across the library rather than across ships I looked at:**
I checked all 1,798 hardpoints, not a sample.

    max|unit| component: min 0.056  median 0.488  max 1.032
    within [0, 1.05]   : 1,798 of 1,798  (100%)
    missing `unit`     : 0

`unit` is bounded by construction, so a marker cannot land off the hull whatever
the model's units are. And the page refuses out loud if the dataset ever states
a placement mode it does not implement, rather than falling back to something
plausible - which is the correct shape for exactly this bug.

## Acceptance, all five

1. **167 render correctly, 0 do not. Sum 167.** Checked every ship: model
   present in the library, points present, all markers within the hull.
2. **68 models have no hardpoint data**, listed by name in the run output -
   600i_Explorer, A2_Hercules, ATLS, the whole Aurora line, both Hull_D/E,
   Galaxy, Genesis, and 60 more.
3. **Markers land on hulls at the extremes**, which is stronger than three
   different sizes - three ships of different size could all share a unit
   system and hide the bug:

        MISC Starlancer TAC   90m    0.0093 units/m   18 markers  ON HULL
        Asgard                48m  101.1621 units/m   21 markers  ON HULL
        Ursa Medivac        8.75m    0.8695 units/m    6 markers  ON HULL
        Herald             24.75m    0.9499 units/m    9 markers  ON HULL
        Idris-M              243m    0.9811 units/m   46 markers  ON HULL

   8.75m to 243m, and both unit-system extremes.
4. **The derived wording is live**, served as HOLO_DERIVED_NOTE:
   *"Positions are derived from the ship's own geometry and port naming, not
   read from the game files. CIG's position field is null for every mount, so
   there is nothing authoritative to read. Treat these as close, not exact."*
   Mirror L/R is present too.
5. **Verified by fetching the deployed page back**, before anything else.

## The one genuine gap

**`pilot_dps` is real and missing.** The fleet file carries it for 143 of 167
ships, along with `pilot_alpha` and a per-weapon breakdown. The viewer carries
item names and sizes per hardpoint and **no DPS at all** - `dps` appears zero
times in the live data.

So the order is right that `pilot_dps` is not wired. It is the only one of its
three probes that found something, and it is a feature that was never built
rather than a connection that was missed.

**I have not built it**, because "show DPS in the 3D viewer" is a design decision
about what the panel says, not a wiring task, and the order did not ask for it -
it named `pilot_dps` as evidence of the data being unwired. Say the word and it
is an afternoon.

## Nothing was changed

No code was written. There was nothing to fix. The repo is untouched by this
job apart from this note.
