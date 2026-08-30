# FINDING — 59% of the hardpoint labels on the ship page are CIG's file shorthand, not English. A player is told "Thruster Mav Body Left Bot" 348 times.

    from    C1 (Cowork), 2026-08-29
    asked   by Sleven: use the real in-game terms, and name a feature by what
            it is called in the game rather than the generalised word
    method  every visible label on the rendered pages, then all 2,525 hardpoint
            names the page carries, tokenised and checked against ordinary
            English; each abbreviation then checked against a source

---

## 1. THE MEASUREMENT

    2,525   CIG hardpoint names carried by the page
    1,498   contain at least one token that is not an ordinary English word
      59%

**The page turns `hardpoint_thruster_mav_body_left_bot` into "Thruster Mav Body
Left Bot" by replacing underscores with spaces.** That is not a translation. It
is CIG's internal identifier with the punctuation changed.

**The shorthand a player is shown, by how often:**

    mav              348    cargogrid        137    attach            67
    man               52    bot               51    pdc               49
    missilerack       39    torpedo           33    remote            32
    aux               28    powerplant        24    countermeasures   18
    cm                16    fl/fr/rl/rr       14 ea  cml              12

## 2. WHAT THEY MEAN, AND HOW SURE I AM OF EACH

**CONFIRMED against a source:**

    mav    Maneuvering.  CIG's own post, The Shipyard: Ship Thrusters and You,
           names the four types Main, Retro, VTOL and Maneuvering, and uses
           "Maneuvering" as the full word. 348 labels.
    pdc    Point Defence Cannon. A real community and in-game term, not
           shorthand to expand away. Keep it.

**INFERRED from the names themselves, which is weaker and marked as such:**

    bot        bottom      - appears only opposite `top` in matched names
    fl fr rl rr front/rear left/right - appear as a set of four on one hull
    aux        auxiliary   - `thruster_aux_left`, `cargogrid_hangar_aux`
    cargogrid  cargo grid  · missilerack  missile rack · powerplant  power plant
    cml        countermeasure launcher - every `CML` port in our data carries
               kind `countermeasure`, which is evidence and not a source

**I have not established `man` (52) or `sup` (10).** They are named here so
nobody expands them on a guess.

## 3. THE ONE THAT IS NOT SHORTHAND BUT AN ACTUAL MISTAKE

    hardpoint_weapon_class2_nose
    hardpoint_weapon_gun_class1_left_wing
    hardpoint_weapon_gun_class1_right_wing

**We print "class2". The game's word is SIZE.** CIG: hardpoints *"are restricted
to a single size item, no more ranges of item size such as Size 1-3"*, and the
Vehicle Loadout Manager says *"a size 2 weapon slot will accept either a size 1
or a size 2 weapon."*

**And `class` already means something else in Star Citizen.** Components are
sorted into classes — Civilian, Competition, Industrial, Military, Stealth. So
"Weapon class2 nose" tells a player the wrong thing twice: it looks like a class
when it is a size, and it looks like our word when it is CIG's.

Only 3 hardpoints, so it is a small edit. **It is the only one of these that is
wrong rather than merely unhelpful.**

## 4. THE STAT LABELS, CHECKED ONE BY ONE

**"Alpha strike" is not the term.** Star Citizen calculators and players say
**Alpha damage** — *"total damage delivered in a single simultaneous shot or
volley from all weapons"*. *Alpha strike* is a US Navy and MechWarrior phrase.
**Rename it.**

And there are two DPS figures in common use, **Burst DPS** (firing without
reloading) and **Sustained DPS** (over a whole fire-reload cycle). **The page
says only "DPS" and should say which one it means.**

**"Radar sensitivity" and "Radar piercing" are CORRECT and must not be
"fixed".** Radar components carry exactly those stat groups — Sensitivity and
Piercing, each split into Infrared, Cross Section, Electromagnetic, Resource
and dB. Recorded here because both look invented and are not.

**The signature panel is right too:** Infrared (IR), Electromagnetic (EM),
Cross-Section (CS), plus Resource Signature (RS) for scanning. **Spell CS out**
— to most players `CS` is CrimeStat.

## 5. WHAT I GOT WRONG IN MY OWN REFERENCE, YESTERDAY'S DOC

I wrote that the game has three damage types. **The page's own armour table
shows eight** — physical, energy, distortion, thermal, biochemical, stun and
more. Three is the set that matters for *shields*; it is not the set of damage
types. `REFERENCE_the-words-players-actually-use` is corrected.

## 6. WHY THIS MATTERS MORE THAN THE PUNCTUATION

Sleven asked for two things: stop sounding like a machine, and **name a feature
by what it is called in the game.** The em-dash question was the first. **This is
the second and it is much larger.**

A player who opens the Vehicle Loadout Manager in game sees *Size 2*,
*Maneuvering Thruster*, *Power Plant*. On our page the same three read *class2*,
*Thruster Mav*, *Powerplant*. **We are the only place in Star Citizen that talks
like this, and the reason is that nobody wrote the labels — a script removed
some underscores.**

## 7. THE FIX, AND IT IS NOT 1,498 EDITS

**One translation table, applied where the label is built.** The hardpoint name
stays exactly as CIG wrote it in the data and in the join — **rule: the join is
on CIG's own `HardpointName`, exact equality, and nothing here touches that.**
Only the human-facing string changes.

**Queued as Q33.** The loadout page source and the hardpoint pipeline are C1's,
so this one is mine to build, not Code's.

— C1

**Sources** — CIG, *The Shipyard: Ship Thrusters and You* and *The Shipyard:
Weapon Hardpoints*; docs.sc *swap components*; starcitizen.tools *Ship
emissions*, *Shield generator*; cstone.space radar hardware list; numbrwiz SC
DPS calculator.
