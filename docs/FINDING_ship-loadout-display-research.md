# FINDING — the ship loadout/fitting display: join verified, tool survey, three tiers, collector target list, and a proposal

    from      C3 (Cowork), 2026-08-08
    for       Sleven + C1
    answers   claude/prompt-c3-ship-loadout-display.md
    method    Verified directly against the actual files on Sleven's machine —
              staged and read with Python, not inferred from planning docs.

---

## 1. The join — measured, not guessed

**Join key: `UUID`.** `ships.json` `Loadout[]` entries carry a real `UUID`;
`ship-items.json` carries the same value in both its top-level `reference`
field and `stdItem.UUID` (5,384 records, 5,384 unique values, zero internal
mismatches between the two fields on any record). This is a real identifier
join, not name matching — the exact thing this project has been burned by
before (Ares Inferno/Starfighter Inferno) doesn't apply here.

**The `Loadout[]` field is a nested tree, not a flat list** — items can carry
their own child `Loadout[]` (a seat with a HUD display mounted in it, a
mining laser with a ventilation attachment). Walking the full tree across all
316 ships produces **36,584 fitted-component instances** (entries that carry
both a `UUID` and a `ClassName` — meaning something is actually mounted
there, as opposed to an empty port definition describing what *could* be
mounted, of which there are a separate 21,175).

**Raw match rate: 19,826 / 36,584 = 54.2%.**

**Reporting that single number would be the wrong answer, and here's why —
broken down by category, not guessed:**

    100% matched, no exceptions:
      MainThruster, ManeuverThruster, WeaponGun, Turret, WeaponDefensive,
      MissileLauncher, Missile, Shield, CargoGrid, FuelIntake, FuelTank,
      Cooler, PowerPlant, Radar, SelfDestruct, Armor, LifeSupportGenerator,
      FlightController

    97% matched (33 misses, all one root cause):
      WeaponAttachment — every single miss is `kegr_fire_extinguisher_01_mag`,
      the fire extinguisher's magazine. It's an FPS item, correctly absent
      from ship-items.json because it isn't a ship item. Not a defect.

    0% matched, entirely expected:
      Display (3,732 — cockpit MFD/screen definitions), Misc (2,394),
      SeatAccess, Seat, Door, AttachedPart, Relay, WeaponController,
      ControlPanel, SeatDashboard, Usable, DockingCollar, MissileController,
      LightController, EnergyController, DoorController, CommsController,
      CoolerController, CapacitorAssignmentController, ShieldController,
      AirTrafficController, LandingSystem, and similar.

**The 0% categories aren't a join failure — they're a category boundary.**
`ship-items.json` is specifically the catalogue of things with performance
stats (exactly the classes named in the original prompt: weapons, turrets,
power plants, coolers, radar, thrusters, shields, fuel tanks, armor). Doors,
seats, screens and internal controller nodes were never going to be in there
because CIG's own data doesn't model them as purchasable, statted items —
they're structural/UI plumbing. **Every category that actually matters for a
fitting display — everything Sleven named by name — is 100% joined on a real
identifier.**

**Bottom line: this is a display problem, confirmed a second time. The join
is not the risk.**

---

## 2. What the ship record ALREADY computes — this changes the scope

Before assuming any math needs to be built, check what's already sitting in
`ships.json` at the ship level. **It's more than expected.** For the stock
loadout, `ships.json` already carries CIG-computed aggregates: `ShieldsTotal`
(combined HP, regen, resistance/absorption by damage type), `Power`
(generation segments and usage by component group), `Cooling` (thermal load
by group), `Emission` (EM/IR signature, broken down by which component group
contributes how much), `Distortion.Pool`.

**For a ship's stock/default configuration, most of what Sleven asked for is
Tier 1 — read it, don't compute it.** The derivation problem below only
actually bites once a player customizes a loadout (swaps a weapon, a shield
generator, a cooler) — at that point the pre-computed ship-level numbers no
longer apply and something has to recompute them from the individual
component records.

**And here's why that recomputation is not simple summation — verified, not
assumed.** RSI Zeus Mk II CL has three shield generators fitted (three Aspis
units, each individually rated `MaxShieldHealth: 7200`). Naive sum: 21,600.
**The ship's own `ShieldsTotal.Hp` is 14,400** — exactly two generators'
worth, not three. Something in the game's actual model (almost certainly a
redundant/backup-generator mechanic, not simple stacking) means shield
capacity does not add linearly across fitted units. **This is exactly the
kind of thing the prompt warned about: a number whose derivation isn't
written down can't be checked later, and here's proof that the obvious
derivation is wrong on a real example.** Anyone building customized-loadout
math needs to reverse-engineer or source the real aggregation rule per
component type before shipping a number — do not assume summation for
anything until it's checked against a real ship the way this was.

---

## 3. Tool survey

Three tools actually matter in the community, per direct research (not
assumed):

**Erkul (erkul.games)** — described independently as "the de facto standard
... the single most-recommended tool in the community." Lets you mix
weapons, missiles, power plants, coolers and shields on a loadout and
recalculates DPS, shield HP, jump range, heat and power draw live as you
swap parts. Also shows where to buy each component in-game and at what
price. **What's worth stealing:** live recalculation as you swap one part,
and tying every component straight to a real shop/price — that second part
is something Citizen Compass's own data (UEX pricing, already wired) could
match or beat, since Erkul's pricing coverage isn't guaranteed current.

**Hardpoint.io** — "the most popular alternative to Erkul," positioned around
side-by-side loadout comparison with a detailed component breakdown.
**What's worth stealing:** comparison-first framing (two loadouts next to
each other) rather than one loadout at a time.

**SPViewer (Ship Performance Viewer)** — a different axis entirely: whole-ship
comparison rather than component-level fitting. Speed, fuel/hydrogen
runtime, quantum range, capacitor recharge, armor, shields, side by side
across ships. **What's worth stealing:** this is the "which ship" question,
answered separately from "what's fitted to it" — worth keeping those as two
distinct views rather than cramming both into one screen.

**On the newcomer-confusion question, honestly:** I could not get inside the
actual rendered interfaces of any of these tools — they're JavaScript
single-page apps and the fetch tool available to me only returns page
metadata, not the live rendered UI. I'm not going to guess at specific
screens I haven't seen. What I can say with real evidence: Erkul has enough
of an unexplained-terminology problem that multiple independent YouTube
walkthroughs exist specifically titled things like "How to Use DPS
Calculator" and "Understanding Ship Components in Erkul's DPS Calculator" —
a tool that needs its own tutorial series to be usable is not self-explaining
by definition, whatever the specific screens look like. That's the concrete
signal, not a guess at layout.

**Flagging, not deciding, per the instruction:** none of this suggested
copying anyone's visual layout — everything above is about which numbers to
show and how the interaction is framed, not what it looks like. If a build
later wants to visually resemble one of these tools specifically, that's a
Sleven call, same handling as the CIG-hologram-look question.

---

## 4. The three tiers

**Tier 1 — directly present, no computation:**
- Every individual component's stats via the now-confirmed clean UUID join:
  `Weapon.Damage` (DPS), `Emission.Em`/`Emission.Ir` (signature),
  `ResourceNetwork` (power/coolant usage), `Shield` block, `QuantumDrive`
  block, `Thruster` block — all read straight from `ship-items.json`.
- A ship's stock-loadout aggregates: `ShieldsTotal`, `Power`, `Cooling`,
  `Emission`, `Distortion.Pool` — already computed in `ships.json`, per §2.
  This covers most of what a "show me this ship's numbers" page needs with
  zero new math, as long as the loadout shown is the stock one.

**Tier 2 — derivable, but the formula must be stated and checked:**
- Total DPS across a *customized* loadout — sum of `Weapon.Damage.DpsTotal`
  across fitted weapons. Simple sum is plausible here (damage output isn't
  redundancy-pooled the way shields are) but **has not been verified against
  a real ship's aggregate the way shields were in §2** — check before
  trusting it the same way.
- Total shield HP on a *customized* loadout — **naive sum is confirmed wrong**
  (§2). The real rule needs to be found (likely N-1 redundant generators, or
  a pooling formula) before this ships as a number rather than a guess.
- Total power draw / cooling load on a customized loadout — `ResourceNetwork`
  is a genuine state machine (priority tiers, min/max power ranges,
  conversion rates), not a flat number. A first pass could sum `Usage.Maximum`
  per component as a rough upper bound, clearly labeled as an upper bound,
  not a true figure — the real model has priority-based allocation that a
  simple sum overstates.

**Tier 3 — not available from any file, live-only:**
- Real-time component health percentage, current temperature, current power
  draw under actual play conditions, wear state. These are runtime
  simulation values, not facts about the ship — see §5.

---

## 5. The collector target list — checked against what's already mined, per the instruction

Sleven said yes to the collector growing to get this. Before assuming
anything needs new OCR/vision work, I checked what the collector's existing
`Game.log` mining (`data-layer/derived/gamelog-mining/`, 233 sessions
already mined) actually captures: shop transactions (296), commodity
transactions, 41 locations, 988 ship classes seen, and — genuinely close to
this task — **55 quantum destinations with observed fuel figures**
(`quantum_routes.json`). That's real, already-mined, log-sourced data, not
screen-reading.

**But it doesn't cover the tier-3 list.** Component health, temperature,
live power draw and wear aren't transactional events the game log writes out
— they're continuous state on the Engineering screen (per
`claude/FINDING_engineering-holographic-display-research.md`), not something
that appears as a log line the way a purchase or a jump does. **Text-file
mining won't get this one; nothing in the existing mined data even brushes
against it.** So the tier-3 list stands as a genuine target for the
collector's *visual* reading — the same "read more of the screen" thread as
the Engineering display research, not a separate ask:

- Component health % (per fitted item, from the Rooms View)
- Current temperature (per fitted item)
- Live power draw (from the Engineering View's per-system readout)
- Wear state, if it's visually distinguishable from health

This becomes the concrete next-expansion target for the collector, rather
than a vague "read more of the screen."

---

## 6. The temporary thing, and the real thing after it

**Temporary (fast, cheap, honest about being a first pass):** a generated
per-ship page or table showing the stock loadout's fitted components (name,
manufacturer, size/grade — from the now-confirmed clean join) alongside the
ship-level aggregates already sitting in `ships.json` (§2) — total shield HP,
power/cooling load by group, EM/IR signature. **No customization, no
derived math, no live data.** This is entirely Tier 1 — nothing here needs
solving, only building. Costs almost nothing beyond page generation, because
the join is clean and the aggregates already exist. What it doesn't do:
let a player swap a component and see numbers change, and it can't show
anything from Tier 3.

**The real version, sketched:** a loadout builder that lets a component be
swapped and recalculates Tier 2 aggregates live (once the real formulas are
found, not assumed — §2/§4), shows per-component stats from the clean join,
flags stock vs. customized clearly, and — once the collector grows into
tier 3 — layers in live health/temperature/power on top of the static specs,
matching this project's own `last_verified_patch` convention so live data is
visibly marked as observed-not-guaranteed. The temporary version is a subset
of this, not a throwaway — the same join and the same ship-level data feed
both.

---

## 7. What I checked and did not

**Checked directly, against files on disk:** the full `Loadout[]` tree walk
across all 316 ships (36,584 fitted instances), the UUID join against all
5,384 `ship-items.json` records, the category breakdown of matches and
misses, the ship-level aggregate blocks on a real ship, and the shield-sum
discrepancy on that same ship. All of it reproducible from the two files
named at the top of the source prompt.

**Not checked / genuinely unverified:**
- Whether the shield-pooling behavior found on the Zeus Mk II CL (2 of 3
  generators counted) is a fixed "always N-1" rule or something more
  specific to that ship's configuration — one example is not a rule, it's a
  reason to be suspicious of summation everywhere else too.
- The actual rendered UI of Erkul, Hardpoint.io or SPViewer — the fetch tool
  available to me only sees page metadata on these JS-heavy sites, not the
  live app. The confusion signal in §3 is real (external tutorials exist)
  but I have not personally seen their screens.
- Whether `ResourceNetwork`'s priority/allocation model is fully understood
  well enough to build an accurate customized-loadout power/cooling
  calculation — flagged in §4 as needing more than this pass found.

**Stayed off `citizen-collector/` entirely, per the constraint** — this is
research and a proposal, not a build, and C1 is the sole writer there.
