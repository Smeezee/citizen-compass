# FINDING — the real aggregation rules, found and proven across all 316 ships

    from      C3 (Cowork), 2026-08-08
    for       C1 -> Code
    answers   claude/prompt-c3-find-aggregation-rules.md
    follows   docs/FINDING_ship-loadout-display-research.md (2026-08-07)
    method    Every rule below was tested against all 316 ships (or the
              relevant subset) programmatically, not spot-checked. Every
              number in this document is a real count out of a real
              denominator. Files: ships.json (316 records) and
              ship-items.json (5,384 records) from the 20260801T204744Z
              snapshot, read directly with Python.

---

## 0. Headline

Four of the five things you asked me to nail down are now **fully proven, exact
formulas, 100% across every ship that has the relevant system** (not "close,"
not "mostly" — exact matches, every ship checked). The fifth (weapon-mount
power draw) has a real, characterized residual that I did not force to 100%.
Emission and Distortion — genuinely tried, genuinely didn't crack them. Full
detail below, in the order you asked for: rule, then residual, then what
counts as unshippable.

---

## 1. SHIELDS — proven, 267/267 spaceships (100%)

**Rule: total shield HP = the sum of the TWO LARGEST fitted generators'
`MaxShieldHealth`, not all of them.** For a ship with 1 or 2 generators this
is just the plain sum. For 3+ it caps at two.

Tested against every ship with `ShieldsTotal.Hp` set: **267/267 spaceships
match exactly.** The only miss in the raw dataset (290 ships with any shield
signal) is the **Tumbril Nova — a ground vehicle** (`IsSpaceship: false`),
where the real answer is the plain sum of all three generators. That's not a
crack in the rule, it's a category boundary: **the redundancy cap is a
spaceship shield mechanic; ground vehicles just add.**

**On the N-1 question you asked me to resolve specifically:** every ship in
this dataset with 3+ shield generators has them **all identical** — there is
no ship with mixed-capacity generators to discriminate "top 2 by value" from
"any 2" from "first 2 fitted." I tested the strongest form of the hypothesis
(sum of the two *largest*, which degrades gracefully to plain summation and
to "any 2" when generators are identical) and it is exact on every case that
exists. **Flagging honestly: this has not been tested against a mixed-size
case because none exists in the current ship catalogue.** If CIG ever ships a
loadout with two different shield models on one ship, re-run this check
before trusting the number.

Worked example, the one you flagged: RSI Zeus Mk II CL, three Aspis
`MaxShieldHealth: 7200` generators, sum 21,600, **top-2 sum 14,400 — matches
`ShieldsTotal.Hp` exactly.** Six-generator case checked too (Aegis Redeemer,
Aegis Retaliator): 6× 10,560, top-2 sum 21,120, matches exactly. The cap does
not scale with generator count — it is always exactly two, on every ship
tested regardless of whether 3, 4, or 6 are fitted.

---

## 2. DPS — proven, 275/275 (100%) on all three figures

**Rule:** sum `Weapon.Damage.DpsTotal` / `.Sustained` / `.AlphaTotal` across
every fitted `WeaponGun`, **except** any gun whose nearest
`IsPilotSlaveable`-carrying ancestor says `false` — and once any ancestor says
`false`, that exclusion is final; a descendant mount saying `true` on itself
does not reopen it. A plain gimbal or fixed hardpoint with no such ancestor
at all counts by default (implicitly pilot-fired).

**Tested against 275 ships** (every ship with a `PilotDps` figure — see §5 for
the 41 that don't have one, and why). **PilotDps, PilotSustainedDps and
PilotAlpha all match exactly on all 275, simultaneously.**

**A real trap here, worth flagging loudly: there are two different "total DPS"
numbers on the ship record, and they are not the same thing.**
`Systems.Weapons.Summary.FixedWeapons.DpsTotal` sounds like the ship's total
pilot DPS. **It is not** — it excludes any turret that's technically a
turret mount, even a pilot-slaveable remote one. The real total pilot DPS is
the **sibling field**, `Systems.Weapons.Summary.PilotDps`. Example that broke
this open: RSI Scorpius has 4 fixed nose guns (2,182.4 DPS) plus a
pilot-slaveable remote quad turret (another 2,182.4 DPS). `FixedWeapons.DpsTotal`
reports only the nose guns (2,182.4). `PilotDps` reports both (4,364.8) — and
4,364.8 is the number that actually matches summing every gun the pilot can
fire. **Use `PilotDps`, not `FixedWeapons.DpsTotal`, for a "this ship's total
firepower" display** — the latter will silently under-report every ship with
a slaved remote turret (Scorpius, Starlancer TAC, and others).

The exclusion mechanism itself: a `TurretBase.MannedTurret` (a real separate
gunner seat) carries `IsPilotSlaveable: false` on itself. Its own internal
gimbal weapon mounts *also* carry `IsPilotSlaveable: true` on themselves
(that flag describes the mount hardware's technical capability, not who
actually operates it on this specific ship) — which is exactly why "nearest
ancestor wins" is the wrong rule and "outermost `false` locks it" is the
right one. Confirmed on MISC Starlancer TAC's manned side turrets, which have
this exact shape.

---

## 3. POWER — proven for 10 of 11 categories (100% each), one real residual

**Rule:** sum each fitted component's `ResourceNetwork.States[0].Deltas[]`
entries where `Resource == "Power"` and `Type` is `Consumption` or
`Conversion`, grouped by component category. (`States[0]` because most
components have one state named `Online` or similar; a few — quantum drives,
fuel valves — have more than one and `[0]` is the resting/default one. Not
re-verified against the small multi-state minority individually — flagging
that as untested, not as broken.)

**Ten categories, checked against every ship that has each one, 100% exact
on every single one:**

    Cooler                  307/307
    FlightController        276/276
    LifeSupportGenerator    277/277
    QuantumInterdictionGenerator  6/6
    Radar                   313/313
    SalvageHead              10/10
    Shield                  268/268   (using the same top-2 cap as §1)
    TowingBeam                 1/1
    TractorBeam              33/33
    WeaponMining              17/17

That's over 1,500 individual ship-category checks with zero misses.

**The one real residual: `WeaponGun`. 219/286 (76.6%), and it's a clean,
one-directional miss — every mismatch over-predicts, never under- (67 of 286,
0 under-predicted).** Plain summation over-counts. The DPS exclusion rule
from §2 (`IsPilotSlaveable`, outermost-lock) does **not** fix this — applying
it made things *worse* (187/286), which tells me the ship's WeaponGun power
budget and the ship's pilot-fireable-DPS list are scoped by two different
rules, not the same one. **I did not find the real rule. Reporting the
residual rather than forcing a number:** something about which weapon mounts
draw from the ship's central power bus versus a turret's own separate supply
is real and I have not characterized it. Mark ship-level `WeaponGun` power
segments **unshippable** until someone finds the actual scope rule — the
proven Power categories above are unaffected and safe to use today.

**Also legitimately out of scope, not a failure:** `EMP`, `QuantumDrive` and
`WheeledController` never appear in `Power.UsedSegmentsGrouped` at all, on
any ship — these draw from budgets this particular dict doesn't track
(quantum drives specifically draw only during the separate "Quantum" travel
mode, covered next). Nothing to derive; the ground truth itself doesn't
carry these categories here.

---

## 4. COOLING — the "Shields-mode" breakdown is proven, 315/315 (100%),
and it turned out **not to be independently derivable** — it's Power's own
answer, reused

I went looking for a Coolant-resource equivalent of the Power formula and it
mostly doesn't exist — for most components, `ResourceNetwork` carries a
`Coolant` delta with `Rate: 0`, a placeholder, not real data. **The real
rule is simpler and different: `Cooling.UsedSegmentsShieldsGrouped` is just
`Power.UsedSegmentsGrouped`, copied, for every category except `Cooler`,
`WeaponGun` and `FlightController` — plus one new entry, `PowerPlant`, whose
value is the ship's own `Power.UsedSegmentsShields` total** (the power
plant's cooling load scales 1:1 with how much power the ship is actually
drawing — a sensible physical model, and an exact one).

**Tested on all 315 ships that carry this block: 315/315 exact.** Since this
formula is built entirely from Power's own already-proven numbers, **it
inherits Power's one residual** — a ship's `WeaponGun` figure never appears
in Cooling's breakdown at all (it's one of the three excluded categories), so
§3's unresolved `WeaponGun` question doesn't even touch Cooling. Good news
there.

**The "Quantum-mode" breakdown** (`Cooling.UsedSegmentsQuantumGrouped`,
active during quantum travel rather than combat) shows the same shape —
`Radar`/`TractorBeam`/`LifeSupportGenerator` carry the identical numbers as
the Shields-mode versions, a fresh `QuantumDrive` entry appears (presumably
its own raw power draw), and `PowerPlant` echoes `Power.UsedSegmentsQuantum`
instead. **I did not run this across all 316 ships** — spotted the pattern on
one worked example and ran out of time budget to prove it exhaustively. This
is a strong lead, not a proven rule. Flagging honestly rather than presenting
it as done.

---

## 5. EMISSION (Em/Ir) and DISTORTION.Pool — tried, did not crack them.
**Marking both unshippable for now, not guessing.**

**Emission:** tested the natural hypothesis — `EmGroupsShields[category] =
Cooling.UsedSegmentsShieldsGrouped[category] × EmPerSegment` (the same
segment counts already proven in §4, times a per-ship constant already
sitting on the record). **It only sort-of works, and only for one category.**
Restricted to `PowerPlant` alone (the category where it looked closest): 165
of 267 spaceships (62%) — not exact, not reliable, not a rule I'd ship. Every
other category (`Radar`, `Shield`, `LifeSupportGenerator`) misses by a wide,
inconsistent margin under this hypothesis. I did not find the real
derivation. **Recommend: do not attempt to derive per-category EM/IR
signature from parts data yet — read the ship-level totals (`Emission.EmShields`,
`Emission.IrShields`) directly, which are already correct and precomputed
(see §6), and leave category-level breakdown as a future research item.**

**Distortion.Pool:** ship-level values are in the millions (Zeus CL:
2,556,900); the only per-shield-generator distortion-related figure I could
find (`Shield.Distortion.Maximum` on the individual item, 4,200 on that same
ship) is three orders of magnitude smaller and clearly isn't the same
quantity, or at least isn't summed the naive way. **I did not investigate
further — this needs a fresh pass, not a guess appended to this one.**

---

## 6. Why none of §5's gaps block the temporary page — Tier 1 already has
everything, precomputed

This matters enough to say plainly: **everything the temporary page in §7
needs is a ship-level number CIG already computed and put directly on the
record — `ShieldsTotal.Hp`, `Power.UsedSegmentsShields`/`GenerationSegments`,
`Cooling.UsedSegmentsShields`/`GenerationSegments`, `Emission.EmShields`/
`IrShields`, `Distortion.Pool`, and — genuinely the best find of this pass —
`Systems.Weapons.Summary.PilotDps`/`PilotSustainedDps`/`PilotAlpha` is
**already summed for you**, no derivation needed at all for the stock
loadout. The unresolved items in §3-§5 only matter the moment someone wants
to show a number for a **customized** loadout (swap a part, see the total
change) — that's Tier 2/3 work, not the temporary page. Don't let "Emission
isn't derivable yet" read as "the temporary page is blocked" — it isn't.

---

## 7. The temporary page — spec'd, not built, per the constraint

**Field list, in display order, source file + key path, all Tier 1 (direct
reads, no computation) unless marked:**

| Field | Source | Key path | Missing-value behavior |
|---|---|---|---|
| Ship name / manufacturer | `ships.json` | `Name`, `Manufacturer.Name` | Always present |
| Fitted components list | `ships.json` → `ship-items.json` | `Loadout[]` walked, joined on `UUID` = `stdItem.UUID` | Empty ports omitted, not shown as blank rows |
| Total pilot DPS / sustained / alpha | `ships.json` | `Systems.Weapons.Summary.PilotDps` / `PilotSustainedDps` / `PilotAlpha` | **"No pilot-fired weapons"**, not `0` — 41/316 ships have no `PilotDps` field at all (haulers, industrial ships with turrets only or no guns); `0` would misrepresent an unarmed hauler as "0 DPS" rather than "not a combat ship" |
| Missile count / damage | `ships.json` | `Systems.Weapons.Summary.Missiles.Count` / `.Damage.Total` | "No missile racks" if absent |
| Total shield HP | `ships.json` | `ShieldsTotal.Hp` (⚠ `ShieldsTotal` is a **list**, not a dict, on ships with no shields — check `isinstance(...,dict)` before reading `.Hp`, or it throws) | "Unshielded" — 26/316 ships have no real `ShieldsTotal` block |
| Power used / max | `ships.json` | `Power.UsedSegmentsShields` / `Power.GenerationSegments` | "—" if `Power` isn't a dict (1/316 ships) |
| Cooling used / max | `ships.json` | `Cooling.UsedSegmentsShields` / `Cooling.GenerationSegments` | Same guard as Power |
| EM signature | `ships.json` | `Emission.EmShields` | "—" if absent |
| IR signature | `ships.json` | `Emission.IrShields` | "—" if absent |
| Distortion pool | `ships.json` | `Distortion.Pool` | "—" if absent |

**On "missing must not render as zero" specifically:** the join and every
field above already distinguishes "ship genuinely has zero of this" (a real
measured `0`, e.g. an EM-silent component) from "this system doesn't exist on
this ship" (field absent, or the wrong JSON type like an empty list where a
dict is expected) — the table above states which is which per field, and the
build should carry that distinction through to the page rather than
collapsing both to "0".

**Ships with incomplete data, so the first build isn't judged against them:**
49 of 316 ships aren't flagged `IsSpaceship` (ground vehicles, gravlev,
power suits) — every field above still *reads* for them, but the shield §1
redundancy cap and the derived Power/Cooling numbers were only proven against
spaceships; ground-vehicle numbers should be treated as unverified until
someone runs the same check restricted to that set. 26 ships have no real
shield block. 41 have no `PilotDps`. These aren't bugs to fix before shipping
— they're real facts about real ships (a cargo hauler doesn't have a gun) —
the page just needs to say so instead of showing a blank or a zero.

---

## 8. Routing note acknowledged

Not spending further time on Erkul/Hardpoint.io/SPViewer's rendered UI —
that's CIC's job with a real browser, not mine with a metadata-only fetch.
Nothing further to add here beyond what's already on record.

---

## 9. What I checked and did not — the standard from last time, kept

**Checked directly, against files on disk, across the full 316-ship set (or
the stated relevant subset):** the shield top-2 rule (267/267 spaceships),
DPS via `PilotDps`/`PilotSustainedDps`/`PilotAlpha` with the outermost-lock
`IsPilotSlaveable` rule (275/275), ten of eleven Power categories (100% each,
~1,500+ checks), the Cooling-Shields-mode reuse-of-Power rule (315/315).

**Not checked, or checked and found wanting — said so rather than guessed:**
`WeaponGun`'s ship-level power segment figure (76.6%, one-directional
residual, real rule not found); Cooling's Quantum-mode breakdown (spotted the
pattern, not exhaustively proven); Emission's per-category EM/IR breakdown
(tried, 62% at best, not shippable); Distortion.Pool (not meaningfully
investigated — flagged for a fresh pass); the shield top-2 rule's behavior on
a ship with two *different*-capacity generators (no such ship exists in the
current catalogue to test against — noted as an open discriminator, not
resolved); multi-state `ResourceNetwork` components beyond `States[0]`
(assumed the first state is the right one for every Power/Cooling check —
not individually re-verified for the minority of components with 2+ states).

**Stayed off `citizen-collector/` entirely** — C1 is actively writing there,
per rule 14. This is pure research against the two snapshot files named at
the top, nothing built.
