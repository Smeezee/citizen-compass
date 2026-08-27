# FINDING — both open questions from this morning are closed by measurement. The wiki field our canonical source "did not carry" is a field I failed to look at, and it turns out to mean something useful. And CURRENT-STATE's "ten damage-multiplier profiles" is eight — three independent counts agree and none of them reaches ten.

    from      C3 (Cowork), 2026-08-27
    closes    §5 and §6b of FINDING_the-damage-multiplier-fields-exist-... (open)
              §7's 9-versus-10 reconciliation in ERRATUM_deflection-was-already-built
    corrects  my own §5, which was wrong, and CURRENT-STATE's profile count
    method    measured on disk, including against the BUILT payload this time
    PATCH     4.9 data. The counts are structural and survive; values do not.

---

## 1. CLOSED — `resistance_multiplier` is not a field we lack. It is a field I did not look at.

**My §5 said:** *"The wiki armour block carries `resistance_multiplier`... Our snapshot's
`Armor` block has exactly four keys... There is no resistance multiplier in it. I do not
know what this field is."*

**It is `Durability.Resistance[*].Multiplier` on the same armour item.**

    wiki    vehicle.armor.resistance_multipliers
    ours    ship-items.json -> stdItem.Durability.Resistance.<Channel>.Multiplier

    armour items carrying Durability.Resistance      285 of 285
    matching the wiki's values exactly                285 of 285
    mismatches                                          0

**Exact float equality on all six channels for every ship.** No tolerance needed.

**The error was mine and it is the same one for the third time today.** I enumerated the
keys of the `Armor` block, found four, and concluded about the record. `Durability` is a
sibling block on the same item and I never opened it. **Twice this morning I measured one
thing and reported about a larger thing; this is the third.** The pattern is not
carelessness about data — it is drawing the boundary of what I checked in the wrong place
and then speaking past it.

### 1a. What it actually means, and it is worth putting on the site

`Durability.Resistance` is an **item** durability field. The same block appears on the
shield generator (`Physical 0.9, Thermal 0.1`) and on the AD4B gatling
(`Physical 0.6`). **It governs damage to the component itself, not damage to the hull
behind it.**

That explains the inverted pattern that made it look like a contradiction:

    Armor.DamageMultipliers        physical 0.6-0.85   energy 0.4-1.1
      -> how much damage reaches the HULL. Below 1 = the hull is protected.

    Durability.Resistance          physical 0.72-0.9   energy 0.96-1.35
      -> how much damage the ARMOUR PLATING itself takes. Above 1 = it wears
         faster.

**Armour protects the hull from energy while taking more energy damage itself.** The
Avenger Stalker passes 0.65 of energy through to the hull and takes 1.35 on the plating.
That is a real, legible mechanic and it is not on the site.

**It is independent information, not a restatement.** Tested: the Avenger Stalker and the
Avenger Titan have **identical** `DamageMultipliers` (0.8 / 0.65) and **different**
`Durability.Resistance` (0.9 / 1.35 versus 0.81 / 1.21). Five candidate formulas were
tried across all 285 ships — `1 ± dm_change`, `2 − dm`, `1/dm`, `dm` — and **every one
failed on physical and energy** while trivially matching the three inert channels.
**Nothing derives it. It has to be read.**

**Consequence:** the `canonical-source-decision` is not undermined. There is no case here
of the non-canonical source carrying something canonical does not. **Withdraw that claim
from my finding — it was the most alarming line in it and it was false.**

## 2. CLOSED — the profile count is EIGHT, and three independent measurements agree

`CURRENT-STATE.md` has said since 08-22 that armour carries *"ten distinct
damage-multiplier profiles."* My finding counted nine and flagged the gap. **Both are
wrong and the answer is eight.**

    over the 179 armour records in the BUILT payload            8
    over the 305 ships that resolve armour in the BUILT payload 8
    over 285 ships joined by wiki UUID against the snapshot     8
    ---------------------------------------------------------------
    over all 209 armour ITEMS in the snapshot                   9

**The ninth is real but belongs to no ship.** It is the all-zeros record —
`{Physical 0.75, Energy 0, Distortion 0, Thermal 0, Biochemical 0, Stun 0}` — carried by
one item and referenced by nothing. That is the `Invulnerable` variant, and counting it
inflates an item tally without changing anything a visitor can see.

**Nothing produces ten.** The eight, with their real populations:

     178 ships   Physical 0.75  Energy 0.6      the default hull
      81 ships   Physical 0.70  Energy 0.5
      20 ships   Physical 0.60  Energy 0.4
      11 ships   Physical 0.85  Energy 0.7
       8 ships   Physical 0.80  Energy 0.65
       4 ships   Physical 0.75  Energy 0.95   Distortion 0.95  <- the only
                                                 hull that resists distortion
       2 ships   Physical 0.75  Energy 1.1    <- takes MORE energy damage
       1 ship    Physical 0.72  Energy 0.96

**Two of these are worth a line on the site by themselves.** Two hulls take *more* energy
damage than an unarmoured one, and exactly four resist distortion at all. In a field that
is otherwise 1.0 everywhere, those are the exceptions that make the number worth printing.

**How to read the disagreement rather than just correcting it:** three counts over three
populations, and the number only moves when the population does. **That is the healthy
version of this project's oldest defect** — the counts were never in conflict, the
denominators were, and nobody had written down which one CURRENT-STATE meant.
**Whoever fixes the ten should write the population next to it.**

## 3. Two things noticed while doing this, neither of them the task

**3a. The built payload is generated from the 1 August snapshot, not the newest.**
`loadout_data.gen.js` header: *"Source: scunpacked snapshot 20260801T204744Z."* The
repo holds `20260827T030607Z`. **No weapon or armour value differs between them** — I
verified that directly this afternoon on the control subjects, and all three snapshots
are identical there. **So this is not a live defect and nothing on the site is wrong
because of it.** It is recorded because "the site is built from the newest data we hold"
is the kind of thing everyone assumes and nobody has asserted.

**3b. The Q1 armour-naming fix is in the deployed payload.** `LOADOUT_ARMOR` reads
`"n": "Avenger Stalker ship armour"`. Confirmed from the built artifact rather than from
the update that announced it.

## 4. What I checked and what I did not

**Checked, by measurement:** all 285 wiki vehicles joined by UUID against
`Durability.Resistance` on the matching armour item, exact float comparison, six channels;
five candidate derivation formulas across all 285; the profile count over four different
populations including the built payload parsed out of the generated JS; the payload's
source-snapshot header; the Q1 fix in the deployed artifact.

**Did NOT check:**
- **Whether `Durability.Resistance` on armour behaves in game the way §1a describes.**
  The block's name, its shape, and its presence on guns and shield generators all point
  one way. **It is a reading of a field, not a tested mechanic.**
- **What `Threshold` is** — every channel carries `Multiplier` and `Threshold`, and I
  only measured the multiplier. The thresholds were 0 everywhere I looked and I did not
  sweep them.
- **Why CURRENT-STATE says ten.** I established it is eight; I did not find where ten
  came from, and the answer is probably in a session I cannot read.
- **I changed no code and no payload.** The only thing I have written today outside my
  own documents is the baseline directory and one dated section in CURRENT-STATE, which
  is itself flagged in §5 below.

## 5. One process item I am raising against myself

**`CURRENT-STATE.md` has one writer and M5 puts it on C1's queue. I appended a dated
section to it this afternoon.** It is additive and nothing was destroyed, but two
writers on one artifact is the exact defect rule 14 exists to prevent, and CIC declined
to touch the same file for that reason.

**I am not editing it again**, including to fix the ten-versus-eight in §2. That
correction is C1's to fold in during M5, and it is written here so he has it. **If the
standing answer is that C3 may append dated sections while C1 owns the structure, say so
and I will carry on; until then I treat it as his.**
