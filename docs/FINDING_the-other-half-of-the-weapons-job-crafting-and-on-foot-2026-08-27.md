# FINDING — the half of the weapons request I never delivered. Crafting is fully readable and the answer to "what does it take to build this" is 26 minerals and a slot list. The big one: only 8 of 1,597 blueprints are available by default, ingredient quality moves finished stats by ±20%, and the six-channel damage model turns out to be a SHIP model — on foot it is a different game.

    from      C3 (Cowork), 2026-08-27
    closes    the crafting and FPS half of Sleven's original weapon request,
              and the open question "is ingredient quality player-controlled"
    method    measured on disk against the SEALED 4.9 snapshot. The 4.10 clone
              is still `.partial` and ungated; per the re-pull order nothing
              reads it until the five gates pass.
    PATCH     4.9. Structure survives a patch; counts do not.

---

## 1. THE ZERO-RECIPE QUESTION IS ANSWERED — and the answer is yes, they are all zero

I called this the most useful question in the whole request. **In 4.9 it is confirmed:**

    Missile            0 recipes
    MissileLauncher    0
    Turret             0
    WeaponDefensive    0
    BombLauncher       0

**You cannot craft anything that shoots a missile, sits in a turret, or defends a ship.**
Whatever the crafting system is for, it is not for those, and this holds across all
1,597 blueprints.

**Re-run this first after the 4.10 pull.** It has no CIG statement behind it either way,
so it is an observation and cannot be written as a pass/fail control — but it is the
cheapest meaningful thing to check and 4.10 adds new blueprint-shaped objects.

## 2. WHAT YOU CAN CRAFT — and it is overwhelmingly gear, not ship parts

    1597 blueprints, every one Kind="creation", every one exactly ONE tier

     859  FPS armour        helmets 217, torsos 216, arms 213, legs 213
     174  personal weapons
      96  ship weapons (WeaponGun)
      75  power plants
      74  coolers
      62  shields
      60  radars
      57  quantum drives
      36  weapon attachments
      17  mining weapons
       8  tractor beams          8  docking collars
      rest  salvage heads and modifiers, misc

**"Tiers" is not a progression.** Every blueprint has exactly one, and every one also
carries a `Dismantle` block. **A UI that promises tier-1-through-3 crafting would be
inventing a system that is not there** — worth saying because the field is named `Tiers`
and reads like a ladder.

Craft times run **10 seconds to 9,060 seconds** — a bit over two and a half hours.

## 3. THE BIGGEST PLAYER-FACING FACT — 8 blueprints of 1,597 are available by default

    Availability.Default = true      8
    Availability.Default = false  1589
    carrying RewardPools            724

**So the crafting system is almost entirely gated behind acquiring the blueprint, not
behind having the materials.** 724 come from named reward pools —
`BP_REWARDS_FullStrikeOnStationB` and its kin — and **roughly 865 have neither a default
flag nor a reward pool**, meaning they are obtained some third way this file does not
describe.

**This reframes the whole feature.** "Here is what a Omnisky III costs to build" is the
wrong lead when the honest answer for 1,589 of them is *you cannot build this until you
find the recipe.* **The blueprint is the scarce thing. The minerals are not.**

**I do not know what the third route is.** Vendors, Wikelo, mission rewards — the file
does not say and I am not guessing.

## 4. WHAT A RECIPE ACTUALLY IS — named slots, 26 minerals, quantities in SCU

    4,277  group nodes      the named slots you fill
    3,976  resource nodes   raw materials
      298  item nodes       recipes that eat FINISHED ITEMS, not just ore

**The slots are readable and they are good words:** Insulative Liner (856), Armored
Carapace (451), Frame (272), Shell (233), Support Structure (199), Casing, Barrel,
Wiring, Coolant, Pump Impeller, Segment Paneling.

**There are only 26 distinct ingredients in the entire crafting system:**

    Aslarite 856 · Ouratite 495 · Laranite 353 · Tungsten 266 · Iron 248
    Agricium 194 · Taranite 145 · Stileron 141 · Hephaestanite 122 · Lindinium 116
    Titanium · Copper · Riccite · Pressurized Ice · Savrilium · Silicon · Borase
    Torite · Corundum · Gold · Tin · Aluminum · Beryl · Quartz · Bexalite  ...

Each resource node carries `QuantityScu` and a `MinQuality` floor. **That is a complete,
publishable shopping list per item**, and it joins straight to the mining and refining
data the site already cares about.

## 5. INGREDIENT QUALITY IS PLAYER-CONTROLLED — the open question, closed, with numbers

This was recorded as unresolved. **It is resolved and the mechanism is fully specified in
the data.**

Every slot carries `Modifiers`, each with a `QualityRange` and a `ModifierRange`:

    QualityRange     0-1000 (3,963 cases), 0-500 (845), 500-1000 (249), others
    ModifierRange    0.8 to 1.2 (1,626) · 0.9 to 1.1 (668) · 0.85 to 1.15 (384)
                     1.2 to 0.8 (462)   · 1.4 to 0.6 (273)

**Put in better material, get a better item — up to ±20% on a named stat, and ±40% in
the widest case.**

**The stats quality actually moves, ranked by how often:**

    1338  Damage Mitigation        897  Min Temp / Max Temp
     462  Integrity                431  Impact Force
     245  Recoil Smoothness, Handling, Kick
     150  Coolant Rating, Power Pips
     133  Fire Rate                124  Max. Shield Strength
      60  Min/Max Assist Distance   57  Quantum Speed

**Read `ModifierRange` carefully — 462 of them run 1.2 down to 0.8, high quality first.**
That is not an error. For recoil and temperature a LOWER number is better, so quality
drives it down. **A UI that renders every modifier as "higher is better" will tell people
the opposite of the truth on a third of them.**

## 6. ON FOOT IS A DIFFERENT GAME — and this changes the presentation, not just the data

458 personal weapons, 398 with a full `Weapon` block, 393 with `Ammunition` — **the same
shape as ship weapons**, so the same extraction works.

**But the damage channels behave completely differently.** Across 393 FPS weapons against
212 ship weapons:

    channel        FPS weapons        SHIP weapons
    Energy             208                114
    Physical           177                 66
    Stun                31                  0
    Distortion          25                  3
    Thermal              2                  0
    Biochemical          0                  0

**Stun and Distortion are alive on foot and dead in space.** My earlier finding said
thermal, biochemical and stun are inert on both sides — **that was true of SHIP combat
and I stated it too broadly.** Stun is a real FPS mechanic with 31 weapons behind it.

**And FPS armour does not use the ship model at all.** Of 2,422 FPS armour pieces,
**zero** carry a `Durability.Resistance` block. Their protection is expressed some other
way — most likely the "Damage Mitigation" stat that dominates the crafting modifiers at
1,338 occurrences.

**The consequence for the site is a design rule, not a data note:** there is one damage
vocabulary and two different games underneath it. **A single shared damage table across
ship and FPS would be wrong in both directions** — it would show four dead columns in
space and hide stun on foot.

**The Arlington Rifle CIG published a stat block for is not in the 4.9 data.** Expected —
it is new in 4.10, and its arrival is a free extra confirmation that the pull landed.

## 7. What I checked and what I did not

**Checked, by measurement:** all 1,597 blueprints — kind, output type, tier count,
availability, dismantle presence, craft times; the full requirement tree walked to every
leaf, 8,551 nodes; all 26 ingredients with counts; every `Modifier` with its quality and
modifier ranges; all 458 personal weapons for block presence and damage channels; all
2,422 FPS armour pieces for a resistance block; the Arlington by name across the whole
FPS file.

**Did NOT check:**
- **What the third acquisition route is** for the ~865 blueprints with no default flag and
  no reward pool. §3. **Real gap, and it is the most important open thing here.**
- **What the 298 `item` nodes point at** — recipes that consume finished items. I counted
  them and did not resolve them.
- **How FPS armour actually protects.** §6 says it is not the ship mechanism and names
  "Damage Mitigation" as the likely candidate. **That is a guess and it is labelled one.**
- **Whether `MinQuality` on a resource is a gate or a floor.**
- **Anything in the 4.10 snapshot.** It is `.partial` and ungated. **Nobody should read it
  until the five gates pass, including me.**
