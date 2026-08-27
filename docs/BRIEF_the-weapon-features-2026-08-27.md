# BRIEF — sixteen features, grouped by the question a player is actually asking. Plus two big ones nobody has touched: what a crafted gun is worth, and what your armour does to your signature.

    from      C3 (Cowork), 2026-08-27
    for       C1 + Sleven
    ask       Sleven: "those are features, those aren't the whole subject. We
              need to find more of them and different ways to do it. And then
              once we figure out all the features, then we have to figure out
              how to actually show it to the user."
    replaces  the six-item list in BRIEF_what-to-build-from-the-weapon-data.
              Sleven's critique of it is in §0 and it is correct.
    status    features only. Presentation deliberately NOT designed here.

---

## 0. The critique, and it reframes the whole thing

**Sleven, on the "print one sentence" idea:**

> *"I don't want to print just one sentence on the site. It needs to be where the
> players look... woven into the information with the weapons and ships we're
> talking about. But we don't want to info dump and put too much info, which
> causes people not to want to read what we're putting."*

**He is right and the framing was wrong.** A fact printed on a page is a fact
nobody reads. **The same fact attached to the weapon it explains, at the moment
somebody is choosing that weapon, is the product.**

**So there is no "shield fact feature."** There is a weapon page that knows the
shield rule and says the relevant half of it, once, where it matters.

**One principle carried forward into the presentation work later:** every fact
below attaches to a thing, not to a page. If it cannot be attached to a specific
weapon, ship or decision, it does not go on the site.

## 1. GROUP A — "will this even work on my ship?"

**A1. Does it fit.** Ship ports carry sizes; weapons carry sizes. **"This gun fits
47 ships"** and, on a ship, **"these 23 guns fit this mount."** Data is complete —
25,150 ports and 948 weapons. Nothing blocked.

**A2. Can your ship power it.** Every item carries a `ResourceNetwork` with power
and coolant usage; ships carry power plants and coolers. **"This loadout draws
more than your plant makes"** is a real constraint players hit blind. **Partially
blocked** — the usage figures are fractions, not watts, and the relationship to
plant output needs establishing before any number is shown.

**A3. Will you run out of ammunition.** Ballistics carry `Capacity`; every weapon
carries `RateOfFire`. **Capacity ÷ rate = seconds of fire.** Against a target's
health that becomes "can you finish it before you are dry." **Energy weapons never
run out — that is the trade, and it is the other half of the ballistic answer.**

**A4. Time to kill.** Weapon damage, target shield HP, shield regen, hull HP. **A
ship whose shield regenerates faster than your gun removes it cannot be killed by
that gun.** That is a hard, checkable, genuinely useful answer.

## 2. GROUP B — "which one should I pick?"

**B1. Effective damage against a chosen target.** The one already agreed. Weapon
→ shield absorption → armour multiplier → hull. **Still blocked on whether shield
`Absorption` and `Resistance` stack.**

**B2. Projectile speed against a moving target.** Weapons carry `Speed`,
`Lifetime` and `EffectiveRange`. **A slow projectile at long range against a fast
ship misses**, and that is why experienced players pick what they pick. Speed
ranges widely across the set and nothing surfaces it.

**B3. The size ladder.** Sizes 0 to 12 exist, **and there is no size 11.** Show
what a size step actually buys — damage, mass, power — rather than assuming bigger
is better.

**B4. Fire modes as a real difference.** Only four exist across 193 guns: Single
153, Rapid 25, Charge 9, Beam 5. **Charge and Beam weapons behave completely
differently and there are only fourteen of them.** Worth calling out rather than
burying in a stat block.

**B5. Recoil, and it is three separate numbers.** Crafting exposes **Recoil Kick,
Recoil Handling and Recoil Smoothness** as distinct modifiable stats. If crafting
tracks them separately, the base items carry them too. **Nobody surfaces recoil on
ship weapons at all.**

## 3. GROUP C — "how do I get it, and is building it better?"

**C1. Where to buy.** 823 terminals with a full location path — "Area 18,
ArcCorp, Stanton." **This is the site's tagline doing its job on a weapon page.**

**C2. Craft or buy.** Price against recipe. 1,597 recipes, ingredients, SCU
quantities, craft times from 10 seconds to two and a half hours.

**C3. THE BIG ONE — a crafted gun is not the same gun.**

This is the feature nobody has and it is bigger than "craft or buy."

**Every recipe carries modifiers driven by ingredient QUALITY.** Measured across
all 1,597:

    Damage Mitigation    on 1,326 recipes    0.80x  to  1.15x
    Integrity            on   462 recipes    0.80x  to  1.20x
    Impact Force         on   427 recipes    0.85x  to  1.10x
    Min / Max Temp       on   894 recipes    0.80x  to  1.20x
    Recoil (x3)          on   245 recipes    0.80x  to  1.20x
    Coolant Rating       on   150 recipes    0.85x  to  1.00x

**Worked example, the Omnisky III Cannon.** Its emitter and its aperture iris each
scale damage 0.95x to 1.05x on ingredient quality. **Both at maximum quality is
roughly +10% damage. Both at minimum is roughly -10%.** Its frame swings integrity
±10% the same way.

**So "should I craft this" is not a cost question. It is: a crafted gun can be
about a tenth better or a tenth worse than the one in the shop, and which depends
on the quality of the rocks you fed it.**

**That is a strategy layer no fan tool covers**, and we hold every number needed
to show it.

**C4. What can I make with what I have.** The reverse lookup — ingredients in,
recipes out. **"You are two Hadanite short of an Omnisky."**

**C5. Say what cannot be crafted.** Missiles, launchers, turrets, countermeasures:
zero recipes. Absence, stated.

## 4. GROUP D — "what does this do to ME?"

**D1. THE OTHER BIG ONE — armour is a stealth choice, not just a damage choice.**

Ship armour carries signal multipliers, and unlike shields **they vary enormously**
across the 91 plates:

    Cross-section     0.60x  to  1.50x
    Infrared          0.30x  to  1.50x
    Electromagnetic   0.60x  to  3.00x

**One plate makes you three times as visible on EM. Another cuts your infrared to
under a third.**

**That is a whole axis of the game — how easily you are seen and targeted — and
nothing tools it.** It is also a genuine tradeoff against D-group damage numbers:
the plate that protects you best may be the one that lights you up.

**D2. Your loadout has a signature too.** Items carry `Emission` with EM and IR
values. **What you fit changes how visible you are**, not just your armour.

**D3. Distortion, and being honest about it.** Non-zero on 3 guns out of 193, and
CIC could not source a CIG explanation of what it does. **Say that plainly** — a
weapon type the game barely uses and the developer has never explained is worth
one honest line, not a shrug.

## 5. GROUP E — "is any of this still true?"

**E1. Patch-stamp on the number, not in a footer.** Already have
`last_verified_patch` on every row.

**E2. "This changed in 4.10."** CIG confirmed the energy-versus-shield bonus was
**broken and fixed in 4.10**. Every guide from that window taught a bug. **We can
date our claims; almost nobody else can.**

**E3. Craft times and prices age differently from stats.** A stat is true until
patched. A price is stale in weeks. **They should not look equally trustworthy on
the same page.**

## 6. What is blocked, and by what

    B1  effective damage      Absorption vs Resistance stacking - UNRESOLVED
    A2  power budget          usage fractions vs plant output - not established
    everything else           nothing. The data is on disk today.

**Two of sixteen are blocked. Fourteen are buildable from what is already here.**

**And all of it is 4.9-era** until the 4.10 pull happens. 4.10 changed armour
mitigation, which touches B1 and D1 directly.

## 7. What I checked and what I did not

**Checked:** every figure quoted - the crafting modifier ranges across all 1,597
recipes, the armour signal spread across all 91 plates, the shield absorption
across all 67, fire modes and sizes across the weapon set, the Omnisky worked
example read from its own recipe.

**Did NOT check:**
- **Whether ship power plants and item power usage are in comparable units.** A2
  depends on it entirely and I did not resolve it.
- **Whether base items carry recoil values**, or whether recoil only exists as a
  crafting modifier. B5 assumes the former. **Checkable in minutes and worth doing
  before anyone scopes it.**
- **Whether ingredient quality is something a player controls or something the
  game rolls.** C3's whole value depends on that answer and it is a gameplay
  question, not a data one. **Sleven will know.**
- **What a visitor actually wants.** Sixteen features, zero measurements of
  demand. The unanswered-question log idea from the Historian work would fix that
  and still does not exist.
