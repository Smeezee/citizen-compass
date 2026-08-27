# ORDER — The scatter fix. A gun inside a turret stays at its turret.

    from    C1
    date    2026-08-23
    for     Code
    file    data-layer/derived/holo-hardpoints/place_fleet.py
    status  RUN AFTER the deploy. S1 through S5, no decision gates.
    unlocks `--with-children`, +160 markers on 5 more hulls, and the hardpoints
            on the Drake Cutlass Black - which currently shows a hull with
            nothing on it because its guns live inside turret mounts.

---

## What is actually wrong

**Not the inheritance. That part works** — proven on the Hammerhead, 24 guns,
all carrying `turretOf`, all `placed_from: inherited`, walking to the outermost
`TurretBase` in their own chain rather than one level up.

**The scatter happens AFTER inheritance, in `place()`, and it has two causes that
are both hull-scale operations applied to a turret-scale problem.**

**1. The nearest-vertex search covers the entire hull.**

    p = P[int(np.argmin(d))]

`P` is every vertex in the model. The only constraint is `side_ok`, which is half
the ship. So a gun whose target lands near its turret can snap to any vertex on
that whole side, including one at the far end.

**2. The retry loop slides along the hull, in hull fractions.**

    u, v, w = target_uvw(loc, spread + attempt * 0.055 * (1 if attempt % 2 else -1))

Nine attempts at ±0.055 of hull LENGTH each. On a Hammerhead that is metres per
step and up to roughly 0.44 of the ship across the loop. That mechanism is
correct for two wing mounts sliding apart along a wing. **It is wrong for two
guns inside one turret**, which are perhaps a metre apart in reality.

**Result, measured by your own control: 12 of 24 Hammerhead guns land nearer a
different turret than their own.** A front-left gun drawn beside the rear turret
is a confident wrong answer, which this project holds to be worse than an absent
one.

## S1 — Place parents before children

An inherited port cannot be bounded against its turret until the turret has a
position. **Order the placement pass so every `TurretBase` is placed before any
port that inherits from it.** A child whose parent was not placed is REPORTED and
left unplaced, never placed unbounded as a fallback.

    CONTROL: assert every inherited point's parent has a position recorded
    BEFORE it. Negative: shuffle the input order and assert the pass still
    produces identical output - if order of input changes output, the sort is
    not doing its job.

## S2 — Bound the candidate vertices to the turret's neighbourhood

**This is the fix.** For an inherited port, the nearest-vertex search must run
over vertices **within a radius of the parent turret's placed position**, not
over the whole hull.

- **The radius is turret-scale, not hull-scale.** Derive it from the turret's own
  size where the data gives one; otherwise a small fraction of hull size — start
  at **0.06** and report what you used.
- **If fewer than a workable number of vertices fall inside the radius, grow it —
  and record that it grew, per point.** A silently-expanded radius is the
  hull-scale search coming back in through the side door.
- **If it grows past a ceiling, the point is REPORTED as unbounded and not
  placed.** Refusing is allowed. Guessing is not.

    CONTROL: on the Hammerhead, assert EVERY inherited gun is closer to its OWN
    turret than to any other turret. This is the exact measurement that caught
    the bug at 12 of 24, so it already exists - it must now read 24 of 24.
    NEGATIVE CONTROL, load-bearing: disable the bounding and assert the check
    FAILS at roughly 12 of 24. A control that passes with the fix switched off
    is measuring nothing.

## S3 — Bound the retry spread to the neighbourhood, not the hull

Inside the neighbourhood, `attempt * 0.055` of hull length is meaningless. **For
an inherited port, the retry step is a fraction of the bounding RADIUS.**

**And the separation minimum has to come down with it.** `minsep=0.06` of hull
size is larger than the neighbourhood itself on a big ship — two guns in one
turret can never satisfy it, so the loop exhausts all nine attempts and returns
its last, worst position. **For inherited ports, `minsep` is a fraction of the
radius.**

    CONTROL: assert no inherited point moves further than the radius from its
    parent, across the whole fleet. Report the maximum observed.

## S4 — Report the trade honestly, on all four crowding metrics

Before this fix, turning children on cost:

    crowding 117 -> 451 markers, 19 -> 34 hulls   (report metric)
              60 -> 216 markers,  9 -> 21 hulls   (proximity metric)

**Guns bunched correctly around their own turret will still read as crowded, and
that is not the same defect.** Two guns 1 m apart on one turret are *right*; two
guns 30 m apart on different turrets are wrong. So report both, separately:

- **crowding among siblings of the same turret** — expected, acceptable, and the
  labels handle it (`ORDER_every-ship-is-a-hologram` H1b)
- **crowding between unrelated ports** — the metric that must not get worse

**Do not merge them into one number.** The single number is what let the earlier
report say the half that improved.

## S5 — Turn children on, redeploy, and say what changed

Once S2's control reads 24 of 24 on the Hammerhead and S4's unrelated-crowding
metric has not risen:

- flip `--with-children` on
- **remove the `0 inherited / 0 children` guard**, which exists only to hold the
  line until this order lands
- rebuild, sweep, deploy to testing
- **report the marker census before and after**, and name the hulls that gained
  markers — **the Drake Cutlass Black by name**, because Sleven photographed it
  as a hull with nothing on it and it is the reason this order exists

---

## Run rules

- **No decision gates.** Pre-ruled throughout.
- **Ledger entry per item with the commit sha.**
- **Rule 12 on every item**, and S2's negative control is the one that matters:
  the check must fail with the fix off.
- Do not `git add -A`. Do not deploy the live site.

## The one thing to argue with

**If bounding to the turret makes guns visually indistinguishable** — four
markers inside one turret's radius, overlapping at every zoom level — then say
so, and propose collapsing them: **one marker for the turret, and the guns listed
inside its readout panel** rather than four dots nobody can tell apart.

That would be a better answer than four correct-but-unclickable dots, and it is
consistent with how the page already handles missiles carried on a rack
(`H1c`). **Measure it before proposing it.**
