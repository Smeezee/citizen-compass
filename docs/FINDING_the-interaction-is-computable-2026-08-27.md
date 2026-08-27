# FINDING — yes, we can tell a new player what a weapon does to a ship, and it comes from CIG's own numbers. Every shield in the game absorbs 45% of ballistic damage and 100% of energy damage.

    from      C3 (Cowork), 2026-08-27
    for       C1 + Sleven
    ask       Sleven: "Are we able to provide the information to new users about
              exactly what that weapon will do, how it interacts with other
              player ships or NPC ships?"
    source    scunpacked 20260827T030607Z. CIG's shipped values.
    scope     measurement only. Nothing built, no page touched.

---

## 1. The answer

**Yes for the mechanics. No for the advice. And the mechanics half is better than
anyone assumed — it is a computable chain, not a lookup.**

Two hours ago the position was "the data says a gun deals 65 Physical and never
says what Physical is good against." **That was wrong.** It says exactly what
Physical is good against, on every shield and every armour plate in the game.

## 2. THE HEADLINE, and it is one number

**All 67 shields in the game carry the identical absorption profile:**

    Physical      0.45
    Energy        1.00
    Distortion    1.00
    Thermal       1.00
    Biochemical   1.00
    Stun          1.00

**Not a range. Not a spread. Every single shield, the same six values.**

**A shield absorbs 100% of energy damage and only 45% of physical damage.**

**So a ballistic weapon puts roughly half its damage straight through a raised
shield and into the hull, and a laser puts none.** That is the ballistic-versus-
laser tradeoff every new player asks about, it is a hard number from CIG's own
files, and it is uniform across the entire game.

**That single fact is worth more to a new player than any statistic on any weapon
page**, and no fan tool states it plainly because it is not written on any weapon
— it is written on every shield.

## 3. The full chain, and every link is in the data

    weapon        ImpactDamage per channel      on the gun
    -> shield     Absorption per channel        on the shield
    -> armour     DamageMultipliers per channel on the armour plate
    -> hull       Durability.Resistance         on the item struck

**Every step is a shipped number.** The interaction is not folklore to be
researched; it is arithmetic we can do.

**Ship armour is where the variation lives** — 91 plates, and unlike shields they
differ:

    Physical      0.60 to 0.85    five distinct values
    Energy        0.00 to 0.70    six distinct values

**Armour is generally kinder to energy than to ballistic**, which is the exact
inverse of the shield. **So the honest answer to "ballistic or laser" is
"against what, and is its shield up" — and we can now answer that concretely
rather than with a shrug.**

Some plates read 0 for Distortion, Thermal and Biochemical — full immunity.

## 4. What this makes possible on a ship page

**A weapon can state what it does against a specific target**, because both sides
are known. Not "1,266 DPS" in isolation, but what fraction of it lands on that
hull, through that shield, past that armour.

**And it explains the three dead damage channels honestly.** Thermal, Biochemical
and Stun are zero on every gun. Every shield absorbs them fully and some armour is
immune. **They are unimplemented on both sides of the equation** — which is a much
stronger statement than "no gun uses them", and it means the site can say so
rather than showing empty columns.

## 5. What is STILL not in the data, and it is smaller than it was

**Advice.** Which weapon a new player should buy, what suits their ship, what to
fly against a Hammerhead. That is judgement and it stays Sleven's or a researched
source's.

**Behaviour the numbers do not carry:** heat build-up over sustained fire, how
much ammunition a ballistic actually carries in a fight, how projectile speed
feels against a fast target, and gimbal versus fixed. Some of that is in the data
as raw figures; **whether it matters is not.**

**So the CIC brief filed earlier today should be narrowed.** Job 2 asked what the
damage types do. **Half of it is now answered from data and should not be
researched.** What remains for CIC is only the practical layer — heat, ammunition,
projectile speed, gimbal versus fixed — and whether CIG has ever confirmed the
45% figure in writing, which would let us cite them rather than our own reading of
their files.

## 6. What I checked and what I did not

**Checked:** all 67 shields for the absorption block — every one carries all six
channels and the values are identical across the set; all 91 ship armour items for
`DamageMultipliers`; the resistance block on a gun and on a shield to confirm items
carry their own per-channel resistance as well.

**Did NOT check:**
- **Whether absorption is the whole story.** Shields also carry a `Resistance`
  block alongside `Absorption`, and I read the absorption values only.
  **Two mechanisms may stack and I have not established how.** Anybody building a
  damage calculator must resolve that before publishing a number.
- **Whether 0.45 is current in 4.10.** This snapshot's upstream commit is
  2026-08-20, six days before the patch — see
  `FINDING_weapon-data-is-not-4-10-2026-08-27.md`. **The figure is 4.9-era.**
- **Ship hull resistance.** I confirmed items carry `Durability.Resistance`; I did
  not establish what a ship's bare hull uses when no armour is fitted.
- **Whether NPC ships differ from player ships.** Sleven asked specifically. The
  item data does not distinguish them and I found nothing that does. **Reported as
  not established, not as "they are the same."**
