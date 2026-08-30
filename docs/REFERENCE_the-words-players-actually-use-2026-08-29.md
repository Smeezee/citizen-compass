# REFERENCE — the words the game and its players actually use, and where our copy uses the wrong ones

    from    C1 (Cowork), 2026-08-29
    for     Sleven's instruction: use the real in-game terms, and name a
            feature by what it is called in the game rather than in general
    sources CIG's own developer comm-link, docs.sc, starcitizen.tools,
            scfocus.org glossary - cross-checked, never one source alone
    patch   4.10 is LIVE as of 2026-08 (hotfix thread updated 2026-08-28),
            which is the patch our data is scaled against

---

## 1. THE ONE THAT CHANGES THE MOST TEXT: WE SAY "PORT", THE GAME SAYS "HARDPOINT"

**CIG's own words, from The Shipyard: Weapon Hardpoints:**

> *"every item on a ship is attached to a hardpoint, or 'itemport' as we
> sometimes refer to them by their in-engine designation"*

**`itemport` is why our data is full of `hardpoint_*` names.** We have been
reading CIG's in-engine word and printing our own word over the top of it.

    we print       the player's word
    port           hardpoint      (a slot on the ship)
    mount          mount          - but a MOUNT is not a hardpoint. CIG:
                                    a hardpoint is the attachment point; a
                                    mount is HOW the gun attaches to it.
    fixed port     Fixed mount    CIG capitalises both Fixed and Gimbal Mount

**And the distinction is real, not cosmetic:**

> *"Attaching a weapon of matching size to the itemport directly is what we call
> a **Fixed** weapon mount"* — it gets *"the largest weapon made possible by
> that hardpoint"*.
>
> A **Gimbal Mount** takes the hardpoint's size but carries a weapon *"at least
> one size smaller due to the space it occupies."*

**A hardpoint takes ONE size.** CIG: hardpoints *"are restricted to a single
size item, no more ranges of item size such as Size 1-3"*. Our per-port, per-ship
editability model already matches this. **The words should match too.**

## 2. "CHANNEL" IS OURS. THE GAME HAS EIGHT DAMAGE TYPES; THREE MATTER TO SHIELDS.

**CORRECTED 2026-08-29, same day:** I first wrote *"the game has three damage
types"*. **Wrong.** Our own armour table carries **eight** — physical, energy,
distortion, thermal, biochemical, stun and more — which is the eight distinct
damage-multiplier profiles already recorded in CURRENT-STATE. Three is the set
that matters for **shields**, not the set of damage types. The error was mine
and it was in the reference for six hours.

Our armour and shield copy says *"each channel separately"*. Nobody says channel.

**The three that decide what a shield stops:**

    physical / ballistic   solid projectiles, limited ammo. Partly punch
                           through shields and hit hull directly.
    energy                 lasers and the like. Stopped by shields until the
                           shields are down, then they melt hull.
    distortion             "cannot harm hull integrity" but strips shields
                           fast, and on bare hull degrades power and
                           component performance.

**Players say "ballistics" for the guns and "physical" for the damage.** Both
are correct and they are not interchangeable: a gatling is a ballistic weapon
that deals physical damage.

## 3. THE FEATURE OUR SHIP PAGE MIRRORS HAS A NAME

The in-game screen where a player actually does what our page shows is the
**Vehicle Loadout Manager**, in mobiGlas, opened with **F1**. Its tabs are
**Systems** and **Weapons**, and its confirm button says **Save and Equip**.

**We should not invent a name for it.** Where the page explains what it is
showing, the reference point is the Vehicle Loadout Manager.

Component names it uses, which are the ones to print: **Quantum Drive**,
**Power Plant**, **Cooler**, **Shield Generator**, **Weapons**. Sizes are
written **Size 1**, **Size 2** and so on; players write **S1**, **S3**.

## 4. MONEY, AND THE ACRONYMS WORTH KNOWING

    aUEC    Alpha United Earth Credit - the in-game money NOW
    UEC     United Earth Credit
    QT/QD   Quantum Travel / Quantum Drive
    SCM     Standard Control Mode      (Master Modes)
    NAV     Navigation Mode            (Master Modes)
    PU      Persistent Universe        AC   Arena Commander
    CS      CrimeStat  - also Cross-Section (signature). CONTEXT DECIDES.
    ASOP    Automated Ship Organization Program - the ship retrieval terminal
    VMA     Vehicle Manager App        CCU  Cross Chassis Upgrade
    LTI     Lifetime Insurance         IAE  Intergalactic Aerospace Expo
    PDS/PDC Point Defence System / Cannon
    TTK     Time To Kill               AG   Auto Gimbal

**`CS` is ambiguous and our signature copy is about cross-section.** Spell it
out on the page. A reader who thinks CrimeStat will misread the whole panel.

## 5. A CONFLICT I AM NOT RESOLVING, AND WE SHOULD NOT PRINT AROUND

Our shield copy says physical absorption reads **Minimum 0, Maximum 0.45** -
measured in CIG's own files, 73 of 73 shields, one profile. So **55% to 100% of
physical damage reaches the hull.**

**starcitizen.tools says something different.** Its Ship weapons page:

> ballistics *"penetrate some percentage of enemy shields, somewhere between
> 20% to 60% depending on the shield"*

**Those do not agree**, and the wiki's own Shield generator page gives no
figures at all to back it. Ours is a primary-source measurement from the game
files; the wiki's is uncited and says "depending on the shield" about a stat we
measured as identical across all 73.

**Keep our number. Do not adopt the wiki's.** But know that a reader who has
read the wiki will think our page is wrong, which is an argument for the page
saying where its number comes from - **which it already does.**

## 6. WHAT THIS MEANS FOR THE REWRITE

**Say hardpoint, not port. Say damage type, not channel. Say ballistic when we
mean the gun and physical when we mean the damage. Name the Vehicle Loadout
Manager when explaining what the ship page is. Write aUEC.**

And the thing Sleven actually asked for - **say the useful thing a player came
for.** *"This is why ballistics are good against shields"* is the sentence. The
mechanism can follow it.

---

**Sources**
- CIG, *The Shipyard: Weapon Hardpoints* - robertsspaceindustries.com/en/comm-link/engineering/16181
- docs.sc - *How do I upgrade or modify my ship?*
- starcitizen.tools - *Ship weapons*, *Shield generator*, *Acronyms*, *Master Modes*
- scfocus.org - *Glossary*
