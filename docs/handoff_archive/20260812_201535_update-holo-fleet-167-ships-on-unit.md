# Update — the holo viewer is on the 167-ship fleet, and the placement rule is now proven against every hull rather than argued for

`build_holo_data.py`, `holo.src.html`, new `_verify_holo_placement.py`. Built,
all six gates green. **Not deployed.**

```
4 ships, 46 hardpoints   ->   167 ships, 1798 hardpoints
unmatched: 0 of 167
holo_data.gen.js: 4.7 KB -> 261 KB
```

The matcher this generator used to carry is **gone, not fixed** — the fleet
dataset resolves its own model, so manufacturer stripping and suffix matching
became unnecessary. What replaced it is a check that the named `.glb` is
actually present, so a ship can never be offered as an entry that 404s.

## `unit`, and the reason it is not `pos_model`

The fleet spans **10,000x** in model scale: 0.0093 model units per metre for the
Starlancer TAC, 101.16 for the Asgard, ~0.97 median. There is no fixed
multiplier that could be correct, so the page must not be handed one.

```
world = unit * (longest half-extent of the loaded mesh)
```

One scalar, on every axis. `HOLO_PLACEMENT` now says `{"mode":"unit"}` and the
page derives the scalar from the hull in front of it. An unrecognised mode is
**refused out loud** — markers are hidden and the page says so — rather than
falling back to something plausible, because a silent fallback here draws 1798
markers in the wrong place and looks like bad derivation.

## The verification found something I had assumed, and I was wrong

My first check tested `pos_model / unit` as a plain ratio. **The F7C Hornet Mk II
failed it by 39,000%.**

That was not a defect in the data. It was a defect in my hypothesis. The
Hornet's hull is not centred on its own origin — its bounding box centre sits at
**(0, 1.338, 0.301)** — and `unit` is centre-**relative**. The real relation is:

```
pos_model  ==  unit * (longest half-extent)  +  (hull bbox centre)
```

Fitting the offset as well as the scalar makes the Hornet agree to three decimal
places. **And it independently confirms the recentring step in `load()`**, which
until then I had simply assumed lined up with the dataset's convention. Chasing
a failure I had caused proved something I had been taking on trust.

## What is now asserted, across all 167 ships and against the real meshes

`_verify_holo_placement.py` reads the POSITION accessors' min/max out of each
`.glb`'s JSON chunk — which sits before the DRACO payload, so true hull bounds
are readable without decoding geometry, which headless still cannot do.

```
408 axis fits used, 93 skipped (mounts too clustered on that axis to fit)

PASS  the scalar fitted for x, y and z agrees to within what each ship's own
      stored precision can resolve
        closest to its noise floor: MISC Reliant Mako, 0.0059% vs 0.0145%
PASS  and that scalar IS the hull's longest half-extent  (worst 0.1102%)
PASS  and the fitted offset IS the hull's own bbox centre (worst 1.2073%)
PASS  no marker sits beyond 1.10x its hull's half-extent (167 ships,
      5394 axis placements)
```

**The three model-scale conventions §8 asks to spot-check are all in there** —
the sweep is the whole fleet, not a sample, so Starlancer TAC (0.0093), the
typical ~1 u/m ships and the Asgard (101.16) are all covered by the same
assertions.

## Two places I nearly set a tolerance instead of finding the cause

**The Nox Kue** failed the axis-agreement check by 3.5%. Cause: five mounts
spanning **0.0044** on x — all on the centreline. A slope fitted across a range
that small, from values stored to three decimals, is rounding noise with a
number attached. Ill-conditioned axes are now excluded, and the **count of used
and skipped axes is asserted and printed**, so this cannot quietly decay into a
check that fits nothing.

**The Asgard** then failed at 0.0006% against a computed floor of 0.0002%. Cause:
my noise floor only accounted for `pos_model`'s three decimals. `unit` is stored
to **five**, and on a hull with a 2,427-unit half-extent that second term is the
entire error. **That was an error source left out of the model, not a tolerance
set too tight** — adding it is a correction, not a loosening. Each ship now gets
the tolerance its own numbers can support, which is the only thing that can
serve both ends of a 10,000x fleet.

## The one real residual, named rather than tolerated away

**MISC Starfarer Gemini.** Its fitted scalar matches its hull to **0.002% on all
three axes** — but its mounts sit **0.557 model units low in y**, 1.2% of hull
size, about **0.56 m on a 92 m ship**. One axis, one hull, and not a unit-system
error.

Rather than widen a threshold until it disappeared, the check **prints every
ship over 0.5% by name on every run**, and the failure threshold sits above it
at 2%. The number stays in front of whoever reads the output.

Same for placement: the worst five overshoots are printed every run —
`600i Touring / Remote turret top` at **1.085x**, then two Idris-P turrets. All
five are mounts sitting slightly proud of a bounding box, which is what a mount
on a hull skin does. For scale, the bug this replaced put a marker **49
ship-lengths** off the hull.

## The gate proves itself, on every build

`--prove` feeds it a per-axis normalisation and a 3x wrong scalar and requires
rejection: 3 of 8 checks fail, including **2193 grossly misplaced markers**.
`build_deploy.py` runs the gate **twice** — once normally, once with `--prove` —
so the self-proof happens on every build instead of depending on somebody having
typed it by hand at some point in the past.

Six gates now run before the build writes anything:

```
_verify_slots.js  _verify_conflict.js  _verify_poll.js  _verify_navkeys.js
_verify_holo_placement.py (checks + self-proof)
inline JS parse: _layer.src.html (12 blocks), keybinds.src.html (4 blocks)
```

## Not claimed

**Nothing here has been rendered.** These are analytic checks against glTF
bounds and the dataset — they establish that markers land on hulls, not that the
page looks right. §1's white-out fix and the visual result still want a browser
over `http://`, and I have not run one.

The generator emits only the fields the page renders. The full record —
`pos_model`, port, type, dps, alpha, manufacturer, frame — stays in
`hardpoints_fleet.json`, which is the dataset. Copying all of it would have put
1798 mounts of unrendered fields on the wire and made the `.gen.js` a second
home for data that already has one.

## That is the master order complete, except

- **Fonts** — blocked on rule 8, needs one word from Sleven.
- **§8 commit / push / deploy** — everything is in the working tree, unpushed.
