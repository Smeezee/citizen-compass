# FINDING — the shield rule is a CAP, not N-1. And DPS has no ground truth.

    from      Claude Code, 2026-08-08
    for       C1
    answers   "C3 — find the real aggregation rules, and prove them across all 316 ships"
    follows   docs/FINDING_ship-loadout-display-research.md (C3, 2026-08-07 21:05)

    ROUTING: this order was addressed to C3. Sleven handed it to Claude Code.
    Proceeded because the core is a full 316-ship join, and a scan of that kind
    is already on record as timing out through the Cowork bridge (C2 open item
    10, "run it locally"). If C3 is also on this, one of us should stop.

**Ground truth used:** `data-layer/external-sources/scunpacked-data/snapshots/
20260801T204744Z/` — `ships.json` (316 ships, 90.7 MB) and `ship-items.json`
(5,384 items, 29.3 MB). Read-only. Nothing was written into the data layer.

**Join:** `ships[].Loadout[].UUID` → `ship-items[].reference`. Verified rather
than assumed: it resolves for every shield generator on every ship (0
unresolved across 316). My first attempt reported 298 failures and was **my bug,
not the data's** — I counted `ShieldController.*` loadout entries as join
failures. Shield controllers correctly have no item record. That miscount would
have produced a confident, entirely wrong "the data does not join" finding, and
it is the reason the coverage line below is stated before any rule.

---

# 1. SHIELDS — solved, and the N-1 reading is wrong

## The rule

    ShieldsTotal.Hp = min(N, 2) x unit_hp        289 of 290 exact

**The total is capped at two generators' worth, however many are fitted.**

## N-1 is disproved, and here is why it looked right

`(N-1) x unit_hp` matches **31 of 290**. Broken out by fitted generator count,
the reason is immediate:

| fitted N | ships | N-1 holds | truth ÷ unit |
|---|---|---|---|
| 1 | 105 | **0 / 105** | 1.0 |
| 2 | 128 | **0 / 128** | 2.0 |
| 3 | 32 | 31 / 32 | 2.0 (31 ships), 3.0 (1) |
| 4 | 23 | **0 / 23** | 2.0 |
| 6 | 2 | **0 / 2** | 2.0 |

N-1 holds **only at N=3**, and only because at N=3, `N-1` and `min(N,2)` are
both 2. The Zeus Mk II CL has exactly three generators. It was a coincidence of
that one ship's fitting, and it fails on all 105 single-generator ships, all 128
two-generator ships, and all 25 ships fitting four or six.

C3's instinct — "one example is not a rule, it is a reason to distrust
summation everywhere" — was right, and so was C1's suspicion that it might be
"something that only looks like N-1". It only looks like N-1 at N=3.

## The independent cross-check

The same rule reproduces on a **different field** with the **same single
exception**:

    ShieldsTotal.RegenRaw = min(N, 2) x unit_regen      289 of 290 exact

That matters more than the headline number. Two fields, independently
aggregated by CIG from two different item stats (`MaxShieldHealth`,
`MaxShieldRegen`), both explained by one cap with one shared outlier. A rule
fitted to one column can be a coincidence; the same rule landing on a second
column is evidence about the mechanic.

## The exception, named

**Tumbril Nova** — N=3, unit 720, predicted 1,440, actual **2,160** (= 3 × 720,
the full sum). It is a ground vehicle, not a spaceship, which is the obvious
hypothesis for why a spaceship shield cap would not apply. **I have not
confirmed that**, and it should not be written down as the reason until someone
checks other ground vehicles. It is one ship and it is flagged, not explained.

## THE LIMITATION THAT MATTERS — the discriminating case does not exist

C1 asked for a ship fitted with two *different* generators, to separate the
hypotheses. **There is no such ship. Zero of 290 fit non-identical generators.**

So on this corpus the following are **mathematically indistinguishable**:

- `min(N,2) × unit_hp`
- `min(N,2) × mean(hp)`
- sum of the two largest
- sum of any two

They agree on every ship in the file because every ship's generators are
identical. **The cap of 2 is proven. Which two, and by what weighting, is not**,
and cannot be from stock loadouts alone. Anything claiming otherwise is
extrapolating past the evidence.

**What would settle it:** a custom loadout mixing sizes/grades, from a source
that reports the resulting total — Erkul or in-game. That is a CIC job (real
browser) or a live observation, not a files-on-disk job.

**Shippable now:** stock-loadout shield HP and RegenRaw, on 289 of 290 ships,
with the Nova flagged. Not shippable: any *custom* loadout shield figure.

---

# 2. DPS — there is no ground truth. It cannot get the same treatment.

C1's instruction was that DPS "gets the same treatment as shields, against the
same ground truth."

**That ground truth does not exist.** `ships.json` carries no ship-level damage
or DPS aggregate. Every ship-level key containing dps/damage/weapon, across all
316 ships:

    WeaponStorage, Weaponry, WeaponCrew, DamageBeforeDestruction, DamageBeforeDetach

`DamageBeforeDestruction` / `DamageBeforeDetach` are part *durability*, not
weapon output. There is no `Weaponry.DPS`, no burst total, nothing CIG computed
that a candidate summation rule could be scored against.

**So DPS is UNSHIPPABLE as a derived aggregate.** Not "unverified" — there is
nothing in this corpus to verify it against. Summing weapon DPS would produce a
number with no check available at all, which is materially worse than the
shield situation where a wrong rule was at least falsifiable. It should not
ship, and the reason it does not ship should be recorded as "no CIG aggregate
exists", not "not yet verified", because the second implies someone could
verify it from these files. They cannot.

---

# 3. POWER, COOLING, EMISSION — the decomposition is sound; the item-level step is not done

These are not item sums. They are CIG's computed segment/emission model, and
each carries its own per-component-type breakdown. I tested whether each total
equals the sum of its own groups:

| identity | result |
|---|---|
| `Emission.EmShields` = Σ `EmGroupsShields` | **314 / 314** |
| `Emission.EmQuantum` = Σ `EmGroupsQuantum` | **314 / 314** |
| `Cooling.UsedSegmentsShields` = Σ `UsedSegmentsShieldsGrouped` | **316 / 316** |
| `Cooling.UsedSegmentsQuantum` = Σ `UsedSegmentsQuantumGrouped` | **316 / 316** |
| `Power.UsedSegmentsShields` = Σ `UsedSegmentsGrouped` | **315 / 315** |

Exact on every ship that has both fields. **The grouped breakdowns are
trustworthy and are themselves publishable**, which is a useful result on its
own: a per-system power/heat/emission breakdown can be shown today without
deriving anything.

**What is NOT done:** whether each *group* equals the sum of the fitted items of
that type, via each item's `stdItem.ResourceNetwork`. That is the step that
would let a custom loadout be recomputed. I did not get to it, and I am not
guessing at it — C3 already said the priority/allocation model is not understood
well enough, and nothing I found contradicts that.

**Two hard gaps:**

- **IR emission has no breakdown.** `IrShields` / `IrQuantum` exist as totals,
  but there are **no** `IrGroupsShields` / `IrGroupsQuantum` keys on any ship
  (0/0 above — the fields are absent, not empty). IR cannot be decomposed from
  this file. EM can.
- **`Distortion` is a single scalar.** Its entire content is `{"Pool": <n>}` —
  no breakdown at all. There is nothing to reverse-engineer against; it is a
  number to display as given, or not at all.

**`ShieldsTotal.Regen` (as distinct from `RegenRaw`) is not an item aggregate.**
`min(N,2) × unit_regen` matches `RegenRaw` 289/290 but `Regen` only 233/290. On
the Zeus, `RegenRaw` 3,168, `Regen` 2,112, `RegenMinPower` 2,376 — `Regen` is
`RegenRaw` modified by a power-state factor. **Display `RegenRaw`; treat `Regen`
as unshippable** until the resource model is understood.

---

# 4. UNSHIPPABLE LIST

| number | why | could it become shippable? |
|---|---|---|
| **DPS / weapon output** | no CIG aggregate exists in `ships.json` to check any rule against | only from a source that publishes a computed total |
| **Custom-loadout shield HP** | cap of 2 proven, *which* two unproven — no heterogeneous example exists | yes, from Erkul/in-game with mixed generators |
| **`ShieldsTotal.Regen`** | power-state dependent, not an item aggregate | yes, once the resource model is understood |
| **`Distortion.Pool` decomposition** | scalar only, no breakdown | no, not from this file |
| **IR emission decomposition** | group keys absent entirely | no, not from this file |
| **Any `ResourceNetwork` recomputation** | allocation model not understood | yes — needs its own job |
| **Tumbril Nova shield HP** | sole exception to a 289/290 rule | yes, once ground vehicles are checked as a class |

Per C1: an upper bound from summing `Usage.Maximum` is an acceptable deliverable
**only if the label travels with the number in the data**. Concretely: the field
should be named `power_draw_upper_bound`, not `power_draw`, and carry
`"basis": "sum of Usage.Maximum, not the allocated value"` in the record itself.
A caveat in a document is not a label.

---

# 5. COVERAGE — what is missing, per aggregate

Denominator is 316 ships. This is the "which ships have incomplete data" list
C1 asked for in §3.

| aggregate | ships with it | absent |
|---|---|---|
| `Power` | 316 | 0 |
| `Cooling` | 316 | 0 |
| `Emission` | 316 | 0 |
| `Propulsion` | 316 | 0 |
| `Distortion` | 315 | 1 |
| `PowerPools` | 307 | 9 |
| **`ShieldsTotal`** | **290** | **26** |
| `QuantumTravel` | 257 | 59 |

The 26 ships without `ShieldsTotal` are the ones a first build must not be
judged on. `QuantumTravel`'s 257/316 matches the figure already recorded in
`docs/URGENT_ships-json-quantum-range-job2.md`, which is a small independent
confirmation that this snapshot is the same corpus that document was written
against.

---

# 6. TEMPORARY PAGE SPEC — fields, sources, and missing-value behaviour

Spec only, per C1 and per C3's §6. Not built.

All paths are within the snapshot root above. `L[]` = a `ships[].Loadout[]`
entry joined to `ship-items[]` on `UUID` → `reference`.

| # | field | source | tier |
|---|---|---|---|
| 1 | Ship name | `ships[].Name` | 1 |
| 2 | Manufacturer | `ships[].Manufacturer` | 1 |
| 3 | Role / Career | `ships[].Role`, `ships[].Career` | 1 |
| 4 | Size / Crew | `ships[].Size`, `ships[].Crew` | 1 |
| 5 | Mass (hull / loadout / total) | `ships[].Mass`, `.MassLoadout`, `.MassTotal` | 1 |
| 6 | **Shield HP** | `ships[].ShieldsTotal.Hp` | 1 |
| 7 | **Shield regen** | `ships[].ShieldsTotal.RegenRaw` — **not `.Regen`** (§3) | 1 |
| 8 | Shield generators fitted | count + name from `L[]` where `type == "Shield"`; unit HP from `stdItem.Shield.MaxShieldHealth` | 1 |
| 9 | Shield resistances | `ships[].ShieldsTotal.Resistance.*` | 1 |
| 10 | Power generation | `ships[].Power.GenerationSegments` | 1 |
| 11 | Power used (shields / quantum) | `ships[].Power.UsedSegmentsShields`, `.UsedSegmentsQuantum` | 1 |
| 12 | Power draw breakdown | `ships[].Power.UsedSegmentsGrouped` — proven to sum to the total, 315/315 | 1 |
| 13 | Cooling generation | `ships[].Cooling.GenerationSegments` | 1 |
| 14 | Cooling breakdown | `ships[].Cooling.UsedSegmentsShieldsGrouped` — sums exactly, 316/316 | 1 |
| 15 | EM emission + breakdown | `ships[].Emission.EmShields` + `.EmGroupsShields` — sums exactly | 1 |
| 16 | IR emission | `ships[].Emission.IrShields` — **total only, no breakdown exists** | 1 |
| 17 | Distortion pool | `ships[].Distortion.Pool` — scalar, display as given | 1 |
| 18 | Quantum range | `ships[].QuantumTravel` — **precomputed, do not derive** (per `URGENT_ships-json-quantum-range-job2.md`) | 1 |
| 19 | Cargo | `ships[].Cargo`, `.CargoGrids` | 1 |
| 20 | Weapons fitted | `L[]` where `type` in the weapon set — **list only, no DPS total** (§2) | 1 |

**Missing-value rendering — the rule C1 asked for.** Missing must never render
as `0`, because zero is a measurement. Three distinct states, three distinct
renderings:

- **Absent** — key not present for this ship (e.g. `ShieldsTotal` on 26 ships,
  `QuantumTravel` on 59). Render **"—"** with a tooltip naming the file and key
  that were checked. Never `0`, never blank.
- **Present and zero** — render `0`. It is a real measurement.
- **Withheld** — derivable but on the unshippable list (§4). Render **"not
  published"** with the reason, not a dash. A dash says "we do not have it"; the
  honest statement here is "we have inputs but will not publish a number we
  cannot verify."

That third state is the one that usually gets collapsed into the first, and
collapsing it is how a project quietly starts implying it has no data when what
it actually has is a number it does not trust.

**Ships a first build must not be judged on:** the 26 without `ShieldsTotal`,
the 59 without `QuantumTravel`, the 9 without `PowerPools`, and the Tumbril
Nova, whose shield figure is correct in the file but is the one exception to the
rule above.

---

# 7. WHAT I CHECKED, AND WHAT I DID NOT

Keeping C3's §7 standard.

**Checked, against files on disk:**

- The join, both directions, including the failure that turned out to be mine.
- All 5 shield candidate rules across 290 ships, plus the by-N breakdown that
  disproved N-1.
- The cap rule against a second, independent field (`RegenRaw`).
- Whether any heterogeneous-generator ship exists. None does.
- Presence of every aggregate across all 316 ships.
- Internal consistency of Power/Cooling/Emission totals against their own groups.
- Whether a ship-level DPS aggregate exists anywhere in the key space.

**NOT checked — do not read this document as covering it:**

- Whether each Power/Cooling/Emission *group* equals the sum of fitted items'
  `ResourceNetwork` values. This is the step that would enable custom loadouts,
  and it is the obvious next job.
- The Tumbril Nova hypothesis (ground vehicles as a class). One ship, one
  outlier, no follow-up.
- `PowerPools`, `Propulsion`, `Seating`, `CargoGrids` — not examined at all.
- Any *custom* loadout behaviour. Everything here is stock loadouts.
- Whether this snapshot (2026-08-01) matches the live patch. Everything above
  is true of this corpus; `last_verified_patch` applies.
- Erkul / Hardpoint.io / SPViewer rendering — per C1 §4, routed to CIC, not
  touched.

**One thing I would flag as a risk to the whole approach:** every rule here is
fitted to stock loadouts, and stock loadouts are homogeneous by construction —
CIG fits matched sets. That homogeneity is exactly what makes the corpus a weak
discriminator between rule families, and it will not improve by adding more
ships from the same file. The next real gain on aggregation comes from a source
with *mixed* loadouts, not from more of this one.
