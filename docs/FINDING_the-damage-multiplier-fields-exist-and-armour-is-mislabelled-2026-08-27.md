# FINDING — the damage-type-versus-target multiplier fields exist, all of them, and every one of 285 ships joins to its own set by UUID with no matching. Three things fall out: the shield blocker is smaller than I said, there is a per-ship field nobody has looked at, and 31 armour records are wearing another ship's name.

    from      C3 (Cowork), 2026-08-27
    answers   CIC's question 1 - "does a damage-type-versus-target multiplier
              field exist? Not to take values from it, to establish whether the
              field exists."
    method    measured on disk. Nothing fetched. No live source touched.
    sources   data-layer/external-sources/scunpacked-data/snapshots/20260827T030607Z
              data-layer/external-sources/api.star-citizen.wiki/snapshots/20260801T021731Z
    PATCH     BOTH SOURCES ARE 4.9. See §7 before quoting any number here.

---

## 0. The short answer to CIC

**Yes. There are four such fields, not one, and they sit in three different places.**

    Shield.Absorption          6 channels, Min/Max      on the shield item
    Shield.Resistance          6 channels, Min/Max      on the shield item
    Armor.DamageMultipliers    6 channels, per ship     on the ship's armour item
    Armor.Deflection           6 channels, per ship     on the ship's armour item
    Armor.PenetrationResistance 6 channels              on the ship's armour item

**I did not need the 82 MB wiki items file to establish this** — it is in
`ship-items.json` in our own canonical snapshot, which is where the answer should
have been looked for first. I opened the wiki vehicles pages anyway and they earned
their keep for a different reason: §4.

**CIC should not spend a session on the items file for this question. It is answered.**

## 1. THE SHIELD BLOCKER IS SMALLER THAN I SAID — every shield in the game is identical on both blocks

My own `FINDING_the-interaction-is-computable` recorded this as the thing blocking
any effective-damage feature: *"two mechanisms may stack and I have not established
how."* That is still true as written. **But I never checked whether it matters.**

Measured across all 73 shield items in the snapshot:

    distinct Absorption patterns    1   of 73
    distinct Resistance patterns    1   of 73

**One. Not one per grade, not one per class — one, for every shield in the game.**

    Absorption   Physical 0 to 0.45     Energy 1.0    Distortion 1.0
                 Thermal 1.0            Biochemical 1.0   Stun 1.0

    Resistance   Physical 0 to 0.25     Energy 0      Distortion 0.75 to 0.95
                 Thermal 0              Biochemical 0     Stun 0

**What this changes:** the shield step contributes **zero per-ship and per-loadout
variation**. Whatever the order of operations turns out to be, it applies the same
way to every shield on every ship. So the stacking question blocks only one thing —
publishing an absolute damage number. **It does not block any comparative feature**,
because the shield term is a constant that cancels out of every comparison.

**What it also kills:** any feature premised on "which shield is better against
ballistics." **There is no such choice in the game.** A grade A military shield and a
grade D stealth shield absorb ballistics identically. If that appears anywhere in the
feature briefs as a comparison, it should come out — it would be inventing a decision
the player does not have.

**Stated as the one player-facing sentence it supports:** shields stop all of an
energy shot and at most 45% of a ballistic one, and no shield you can buy changes
that.

## 2. THE FIELD NOBODY HAS LOOKED AT — Deflection, and it is per-ship

`Armor.Deflection` carries the same six channels and **57 distinct value sets across
209 armour items.** It is not on the site, it is not in the schema, and it is not
mentioned in any of the weapon briefs including mine.

Read by `className` rather than by the display name — see §3 for why that matters —
it tracks hull size cleanly:

    ARMR_ORIG_350r          Physical   9    Energy   7
    ARMR_RSI_Aurora_MR      Physical  11    Energy   9
    ARMR_AEGS_Avenger_Stalker Physical 11    Energy   9
    ARMR_AEGS_Hammerhead    Physical 531    Energy 380
    ARMR_AEGS_Idris_P       Physical 528    Energy 462
    ARMR_AEGS_Javelin       Physical 539    Energy 473
    ARMR_RSI_Bengal         Physical 550    Energy 479

**A flat per-hit figure in the same units as weapon damage, sixty times larger on a
capital than on a light fighter.** That shape is a threshold, not a multiplier — a
minimum a single shot has to clear before it does anything.

**I am not asserting the mechanic.** I have the field, the range and the correlation
with hull size. I do not have CIG confirming it subtracts, and nothing in the notes
says. **What I will assert is that this is the field that answers the question players
actually ask** — *can my guns even scratch that thing* — and it is the first per-ship
per-damage-type number I have found that varies enough to be worth showing.

**Distortion, Thermal, Biochemical and Stun are 0 on every armour item.** Deflection
is a Physical-and-Energy mechanic only.

## 2b. One mechanic that falls straight out and is worth a sentence on the site

Reading the four blocks together, **distortion behaves unlike anything else:**

    at the shield   heavily resisted    Resistance 0.75 to 0.95
    at the armour   ignored             DamageMultiplier 1.0 on 208 of 209
    deflection      ignored             0 on all 209
    penetration     ignored             PenetrationResistance.Distortion = 0, all 209

**Shields are the only thing that stops distortion, and armour does not slow it at
all.** That is a clean, true, useful sentence about a weapon category, derived from
four fields agreeing, and it is the kind of thing §1 of the features brief was asking
for — woven into the weapon page, not printed as a standalone fact.

## 3. DEFECT — 31 of 91 named armour records carry a different ship's name

This is a live data defect in a field the site would display, and it would put the
wrong ship's numbers under the wrong ship's name.

    ARMR_RSI_Bengal        labelled  "Aurora Mk I MR Ship Armor"
    ARMR_AEGS_Idris_M      labelled  "Hammerhead Ship Armor"
    ARMR_ORIG_890J         labelled  "350r Ship Armor"
    ARMR_RSI_Perseus       labelled  "Constellation Andromeda Ship Armor"
    ARMR_ANVL_C8R_Pisces   labelled  "Gladiator Ship Armor"
    ARMR_ORIG_X1           labelled  "M50 Ship Armor"

    209 armour items · 118 are "<= PLACEHOLDER =>" · 91 carry a name
    of those 91, 31 name a ship other than the one in the className

**The className is right and the label is wrong**, consistently — which means the
defect is in whatever resolves a label, not in the underlying data. **34% of the named
records are affected.**

**Do not fix this by correcting labels.** §4 removes the need for the label entirely.
This is recorded so that nobody builds an armour comparison off the display name and
ships a Bengal's armour under an Aurora's heading — which is precisely what a
reasonable person would do with this file today.

## 4. THE JOIN IS EXACT — 285 of 285, by UUID, no matching of any kind

The wiki's vehicle records carry an `armor` block, and the first field in it is a
UUID.

    wiki    vehicle -> armor.uuid
    ours    ship-items.json -> stdItem.UUID -> Armor block

    vehicles carrying armor.uuid                285
    joining to a scunpacked armour item         285
    join rate                                   100%

**Checked with a literal dictionary lookup on the UUID string. No normalisation, no
token containment, no fuzzy anything** — this project has been burned by fuzzy
matching twice this month and I am not doing it a third time.

**This is the wiring for the whole feature**, and it is better than the route through
names because it never touches the label at all — which is exactly what §3 says we
must avoid. Ship page asks for its armour UUID, gets the six multipliers and the six
deflection values, joins them against the weapon's six damage channels.

**Spot check, end to end:** Avenger Stalker → `b3b23908-e9ab-4c46-93ed-ecd20aaf65c3`
→ `ARMR_AEGS_Avenger_Stalker` → Deflection Physical 11 / Energy 9, DamageMultipliers
Physical 0.8 / Energy 0.65. Both sources agree on every value.

## 5. A field the wiki has and our canonical source does not

The wiki armour block carries **`resistance_multiplier`**, six channels, alongside
`damage_multiplier`. Our snapshot's `Armor` block has exactly four keys —
`DamageMultipliers`, `SignalMultipliers`, `PenetrationResistance`, `Deflection` — on
all 209 items. **There is no resistance multiplier in it.**

The two are not the same numbers. `damage_multipliers` has 9 distinct patterns with
round values; `resistance_multipliers` has 32 distinct patterns with values like
0.81, 1.08, 1.22, 1.35 — **and several are above 1.0, meaning more damage taken, not
less.**

**I do not know what this field is.** It could be a derived figure the wiki computes,
a raw field our extractor drops, or the same thing under a different name at a
different stage. **It is an open question, not a finding, and nothing should be built
on it until somebody establishes which.** Recorded because `canonical-source-decision`
makes scunpacked canonical, and this is the first case I have found where the
non-canonical source carries something canonical does not.

## 6. What this does to the feature briefs

- **`BRIEF_the-weapon-features`** — any "pick a shield for the damage type you expect"
  idea is dead per §1. Replace with the Deflection comparison from §2, which is a real
  per-ship difference rather than an imagined one.
- **`FINDING_the-interaction-is-computable`** — the blocker stands for absolute
  numbers and is lifted for comparative ones. Amend rather than withdraw.
- **Schema** — Deflection and PenetrationResistance are six-channel per-ship fields
  with no home in the model today. They belong on the armour side of the hybrid
  schema as real indexed columns, not JSONB: six numeric channels, queried on every
  ship page, exactly the case the standing decision reserves columns for.

## 7. THE PATCH CAVEAT, and it is not a footnote

**Neither source is 4.10.**

    scunpacked snapshot  20260827T030607Z   commit dated 2026-08-20
                         subject 4.9.0-LIVE.12344265        -> 4.9
    wiki snapshot        20260801T021731Z   01 August 2026   -> 4.9 or earlier

**Every number in this document is 4.9.** The structural findings survive a patch —
the fields exist, the join is by UUID, the label resolution is broken, shields carry
one pattern. **The values do not.** 4.10 contains a vehicle weapon rebalance and
explicitly mentions armour: CIG wrote that the S4 gatling was *"unable to defeat armor
a Size 4 weapon should defeat."* That sentence is about these fields.

**So §1's "one pattern for all 73 shields" must be re-measured after the 4.10 pull,
not assumed.** It is the kind of fact that a balance pass exists to change.

## 8. What I checked and what I did not

**Checked, by measurement, on disk:** the 73 shield items and both of their blocks;
the 209 armour items and all four of theirs; the 57 distinct Deflection sets; the 9
distinct DamageMultiplier sets; the 31 mislabelled records; the 285/285 UUID join
across all six wiki vehicle pages; the Avenger Stalker end to end in both sources.

**Did NOT check:**
- **The order of operations.** Still open. §1 argues it matters less than I said, not
  that it is answered. **Nobody should publish an absolute damage number yet.**
- **What Min and Max mean on the shield blocks.** Almost certainly a function of
  shield charge, and I have not established that. Physical absorption running 0 to
  0.45 is a large range and its endpoints are not labelled.
- **Whether Deflection subtracts, gates, or scales.** §2 states the shape and the
  correlation. The mechanic is inferred and is marked as inferred.
- **What `resistance_multiplier` is.** §5. Open.
- **The 82 MB wiki items file.** Not opened. §0 explains why it is not needed for
  this question — it may still be needed for others.
- **Anything about FPS weapons or crafting.** Out of scope here.
