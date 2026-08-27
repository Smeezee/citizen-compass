# C3 research prompt — the ship loadout / fitting display

    from      C1, 2026-08-07
    for       C3 (Cowork research session)
    asked by  Sleven, in his words:
              "display all of the ship information that we have, the guns, and
              kinda take inspiration from the other tools that display
              calculations and stuff like that about if this engine pack is in
              here, if this shield generator is in here, this gun is attached
              here with this gun over here attached here. How much firepower,
              the IR rating, the heat your engines put off, all that stuff."
              "even if it's a temporary method for now"

    also      Sleven has ANSWERED the open question from your engineering
              hologram finding. He wants the expensive path: "If it means the
              collector gets to grow, I am down for that." So live component
              condition is now a long-term goal, not a cost to avoid. That
              changes §5 below.

---

## 1. READ THIS FIRST — the data question is already answered

Your engineering finding correctly said `ships.json Loadout[]` names the fitted
components. The obvious next worry is whether we hold the *numbers* for those
components, or only their names.

**We hold the numbers.** Verified directly against the file, not inferred:

    data-layer/external-sources/scunpacked-data/snapshots/20260801T204744Z/ship-items.json
    29 MB, 5,384 records

    202  WeaponGun        88  PowerPlant       143  CargoGrid
    317  Turret           81  Cooler           182  FuelTank
    145  MissileLauncher  77  Radar            150  QuantumFuelTank
    381  MainThruster    238  FlightController 210  Armor
    885  ManeuverThruster 188  WeaponDefensive

Every record carries a `stdItem` block with real performance figures. A real
example, read out of the file:

    Dominance-1 Scattergun, size 1, grade 1
      Weapon.Damage      Sustained 396.5, Burst 420, AlphaTotal 504, DpsTotal 420
                         split by Physical / Energy / Distortion / Thermal /
                         Biochemical / Stun
      Weapon.Modes       RoundsPerMinute 50, PelletsPerShot 8, DamagePerShot 504,
                         HeatPerShot, WearPerShot, per fire mode
      Weapon             EffectiveRange, RateOfFire, Capacity, Capacitor, Consumption
      Emission           Em.Maximum 248, Ir 0
      ResourceNetwork    Power consumption 0.6/s, signature EM 248

And the other classes carry what you would expect:

    Shield        MaxShieldHealth, MaxShieldRegen, DownedDelay, DamagedDelay,
                  Absorption, Resistance, RegenerationTime
    QuantumDrive  JumpRange, FuelRate, FuelConsumptionSCUPerGM,
                  FuelEfficiencyGMPerSCU, TravelTime10GM, Heat
    MainThruster  ThrustCapacity, FuelBurnRatePer10KNewton,
                  MaxSupportedAtmosphericEfficiency
    everything    Emission, Temperature, Distortion, Durability, ResourceNetwork

**So every single thing Sleven named by name is in the file.** Firepower is
`Weapon.Damage`. IR rating is `Emission.Ir`. EM is `Emission.Em`. Engine heat is
`Temperature` plus `Thruster`. Power draw is `ResourceNetwork`.

**This is therefore a DISPLAY problem, not a data-acquisition problem.** Do not
spend the session establishing what we have. Start from the fact that we have it.

---

## 2. THE ONE THING THAT IS ACTUALLY UNVERIFIED — check this first

`ships.json` `Loadout[]` names components. `ship-items.json` holds their stats.
**Nobody has confirmed the two join cleanly.**

That join is the whole build. If it is clean, this is a straightforward display
job. If it is 70% clean with a long tail of unmatched names, the tail is the
work, and every estimate in this document is wrong.

So, before anything else:

- Take the 316 ships' `Loadout[]` entries and try to resolve each one against a
  `ship-items.json` record. Report the **match rate**, and report the residue by
  category, not as a single percentage.
- **Classify the misses rather than discarding them.** That is this project's own
  method from `ship_resolution.json`, and it worked: 254 live ships against 316
  game files produced zero ambiguity because the leftovers were sorted rather
  than dropped.
- Say plainly which key you joined on and whether it is a real identifier or a
  name. This project has been bitten before by name matching — "Ares Inferno"
  and "Starfighter Inferno" share one word. If there is a UUID or className on
  both sides, use it and say so.

**Report the match rate before you propose anything.** A proposal built on an
unmeasured join is a guess with a layout.

---

## 3. Survey the existing tools — but be specific about what is worth copying

Sleven said "take inspiration from the other tools." Look at what the community
actually uses for loadout maths and report:

- what each one computes and shows
- what it does WELL that we should learn from
- **where it is confusing to somebody who does not already know the game** —
  this is the thing to pay most attention to. This project's own standard is the
  newcomer, and the keybind work already found that competitor tools tend to
  assume a lot. A wall of numbers is not a feature.
- what it gets wrong, or does not cover at all

Do not just enumerate features. The useful output is: *here is the one thing
each tool does that is worth stealing, and here is the thing all of them do
badly that we could be better at.*

**Flag, do not decide:** if a proposal involves reproducing another tool's
specific visual layout rather than showing the same underlying numbers in
Citizen Compass's own style, that is a question for Sleven, exactly like the
CIG-hologram-look question you correctly refused to rule on. Same handling.

---

## 4. Work out what is computable, and be honest about the three tiers

Sort every value a fitting display might want into one of three:

1. **Directly present** — read it out of `ship-items.json` and show it.
2. **Derivable** — computable by combining what we hold (total DPS across a
   loadout, total power draw, total EM/IR signature, shield HP by pool,
   thrust-to-mass). **State the formula you used.** A number whose derivation
   is not written down cannot be checked later, and this project treats
   unverifiable numbers as defects.
3. **Not available** — needs live capture, or needs a source we do not have.

That third tier is not a failure list. It is the collector's target list — see
below. But a value that lands in tier 3 must be **reported as missing, never
estimated into existence.** Every data row in this project carries
`last_verified_patch` for a reason.

---

## 5. Because Sleven said yes to the collector growing

Live component health, temperature, power draw and wear are runtime state. You
already established that correctly. **He has now said he wants that, and is
willing to have the collector grow to get it.**

So add one section: **which values will ONLY ever come from live capture**, and
what each one would need the collector to read. That becomes the deliberate
target list for the collector's next expansion rather than a vague "read more
of the screen."

Relevant, because it is newer than your engineering finding: the collector now
mines Star Citizen's own `Game.log` on every session, including the archive the
game keeps in `logbackups`. 233 sessions have been mined already — 296
transactions, 183 priced items, 41 locations, 988 ship classes, 55 quantum
destinations with fuel figures. See `data-layer/derived/gamelog-mining/` and
`claude/FINDING_gamelog-archive-is-a-mine.md`.

**So check the log first for anything on your tier-3 list.** The log turned out
to carry things nobody expected — quantum fuel per route, for instance, which is
exactly the kind of number a fitting tool wants. Some of what looks like it needs
OCR may already be written to a text file. Text beats OCR every time.

---

## 6. Propose the temporary thing

Sleven said "even if it's a temporary method for now." He wants to *see* this
soon, not wait for the finished feature.

Propose the smallest useful version — something that puts the loadout and its
numbers in front of him quickly. A generated page, a table, whatever is honest
about being a first pass. Say what it would cost and what it would not do yet.

Then, separately, sketch what the real version looks like, so the temporary one
is a step toward it rather than a thing to throw away.

---

## 7. Constraints

- **Research and a proposal. Do not build it.** You do not write code or run
  builds; that is Code's job via C1.
- **Stay off `citizen-collector/` entirely.** C1 is the sole writer there right
  now. Rule 14 — and it was violated in that folder earlier today, by C1, which
  you correctly caught by mtime. Do not add a third writer.
- **Verify against the files on disk, not against the planning docs.** The docs
  have been wrong about the repo more than once this week, in both directions.
- **Do not re-litigate settled rulings.** `RULING_ship-models-provenance-and-proceed.md`
  is settled. The internal-components-get-a-menu-not-a-3D-viewer decision is in
  the project instructions and is settled.
- **Say what you checked and what you did not.** A confident sentence about
  something unverified costs more than an honest gap.

## 8. Deliverable

One finding document: the join match rate first, then the tool survey, then the
three tiers with formulas, then the collector target list, then the temporary
proposal and the real one. Into `inbox/` as usual.
