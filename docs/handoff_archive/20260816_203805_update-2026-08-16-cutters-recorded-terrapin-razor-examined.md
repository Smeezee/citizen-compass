# Update - Cutters recorded as settled; Terrapin and Razor re-examined

Nothing was changed. The Cutter ruling is now recorded in the artifact and in
the code; the Terrapin and Razor findings are below and await a decision.

## 1. The Cutters, recorded so it cannot be reopened as a threshold question

In `build_hardpoint_alignment.py` beside the constant, and in the dataset's own
`MANIFEST.json` under `settled_on_geometry_not_tolerance` - so it travels with
the data, not only with the code:

> the Cutter has a plain roof, the Scout carries a large circular dome which IS
> the variant - RSI's copy calls it "a powerful onboard scanner" - and the
> Rambler carries a box structure instead. Raising the tolerance would not make
> these alignable, only make the mistake reachable.

**Measured, and it matches the art exactly:**

    base Cutter roof line            y = 2.766
    Rambler   1,848 vertices above it, footprint 3.10 x 5.29, up to y +3.26
    Scout     1,386 vertices above it, footprint 4.37 x 8.86, up to y +3.64

The Scout's structure is wider, longer and taller than the Rambler's. Two
different things on the roof, as Sleven said.

## 2. A weakness this exposed - Scout and Rambler are aligned TO EACH OTHER

They pass the mesh gate at 1.6%, because their overall bounding boxes are
similar even though their roofs are not. The gate compares sorted extents and
cannot see a shape difference that does not change the envelope.

**No harm done here:** no marker on any of the three Cutters sits above the base
roof line. The highest are Cutter +1.80, Rambler +2.14, Scout +2.32, all below
2.766. So nothing is on the dome or the box, and the Scout/Rambler alignment
moves nothing onto structure the other lacks.

**But the gate would not have caught it if there were.** Flagging rather than
patching.

## 3. Terrapin Medic - structure, but nowhere near a mount

    differing axis: x (BEAM, not height) 15.311 -> 16.404, +7.1%
    symmetric: +0.547 on each side
    660 of 70,538 sampled vertices beyond the base's beam (0.9%)
    footprint: 12% of the hull's length, near one end, 42% of its height
    vertex count 58,798 base vs 211,613 Medic - 3.6x, a higher-detail export

So: real added structure on both sides near one end - consistent with a medical
variant's side fittings - AND a different export detail level. Both are present.

**Its three markers sit at x = +5.82, -0.00, -6.09. The base hull already
extends to +/-7.656.** Nothing is on the part that differs.

## 4. Razor LX - the same answer, smaller

    differing axis: y (height) 2.261 -> 2.384, +5.4%  (6cm on an 11.5m hull)
    symmetric: +0.062 each way
    56 of 74,269 vertices beyond the base (0.1%)
    footprint: 82% of the width but 3% of the length, near one end
               - a thin spanwise blade, most likely a rear wing
    vertex count 72,820 vs 148,538 - again a higher-detail export

**Its eight markers span y -0.43 to +0.19, against a hull half-height of 1.13.**
Nothing is near the blade.

## Recommendation

**Leave both aligned.** The extra geometry is real in both cases, but in neither
does any mount sit on it, so the failure the Cutters demonstrate - a marker
dragged onto a roof line the variant does not have - cannot occur here. The
Razor LX was the outlier of three Razors and now agrees with both.

If the rule should instead be "any real structural difference disqualifies,
regardless of where the mounts are", say so and I will un-align both; that is a
one-line change to the bound, and it would also un-align nothing else currently
in the overlay.
