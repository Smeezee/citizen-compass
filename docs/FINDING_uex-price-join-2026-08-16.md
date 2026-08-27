# FINDING — the price join works, and it works on a REAL identifier. UEX's UUIDs are the game's UUIDs: 99.8% resolve. The loadout bench is unblocked today. FIND is not, and the reason is not the join.

    from      C3 (Cowork), 2026-08-16
    for       C1 + Sleven
    ask       "Does Citizen Compass's price data actually join to its item and
              component data? Nobody has checked, and two pages are blocked."
    method    joined on disk, read not estimated. UEX snapshot 20260801T235530Z
              (23,734 price rows, 7,728 catalogue items, 823 terminals) against
              scunpacked snapshot 20260801T204744Z (ship-items 5,384,
              fps-items 5,420, items 21,849).
    scope     research only. Nothing built, nothing changed, nothing in
              citizen-collector touched.

---

## 1. The identifier question, answered first because everything rests on it

**The join is on a UUID, not a name. And the UUID is real.**

    UEX catalogue items carrying a uuid          5,566
    of those that resolve in the game's files    5,344 of 5,356  =  99.8%

    UEX priced items (distinct uuid)             2,424
    resolving in the game's catalogues           2,421          =  99.9%

**These are the same identifiers CIG uses.** That is the thing C1 flagged as
"looks true until someone checks" — it was checked, and it is true. Twelve
catalogue UUIDs out of 5,356 do not resolve; that is the entire cost.

**No name matching is needed and name matching must NOT be used.** I tested it as
a fallback and it is actively dangerous here:

    CF-557 Galdereen Repeater    game 01948ce4...   UEX d55ffb79...
    Revenant Gatling             game 83671df2...   UEX 8bd04e05...
    Impact II Mining Laser       game ac0185ec...   UEX 30545178...

Same display name, **different UUID on each side**. The game file carries multiple
records under one name — up to **12 copies** of a single name — because a part
mounted on different hulls is a different record. A name join silently picks one
and calls it the price of all of them. **The UUID join is correct and the name
join is a bug waiting to happen.**

## 2. The headline number is 7.2% and it is worthless

Priced ship components, as a fraction of `ship-items.json`: **389 of 5,384 = 7.2%.**

**Do not report that number.** It is the same trap as the 54.2% on the loadout
join. Three things inflate the denominator:

- **2,247 of the 5,384 records are literally named `<= PLACEHOLDER =>`** — 42% of
  the file has no name at all.
- **Whole types are not sold to players and never will have a price.** Maneuvering
  thrusters (885), main thrusters (381), flight controllers (238), armour (210),
  fuel tanks (182), fuel intakes (155), quantum fuel tanks (150), cargo grids
  (143), decorative flair (159). That is **2,503 records that a shop does not
  stock**, counted as misses.
- **313 records are called "Remote Turret"** — ship mount hardware, not a
  purchasable item.

## 3. The number that means something, broken down by category

Counting **distinct named parts** in the types a player actually buys:

    661 distinct names,  347 priced  =  52.5%

    WeaponMining         17 names    16 priced     94.1%
    QuantumDrive         58 names    45 priced     77.6%
    TractorBeam          11 names     8 priced     72.7%
    Cooler               73 names    50 priced     68.5%
    Shield               64 names    42 priced     65.6%
    JumpDrive             5 names     3 priced     60.0%
    SalvageModifier       5 names     4 priced     80.0%
    SalvageHead           7 names     4 priced     57.1%
    PowerPlant           74 names    42 priced     56.8%
    WeaponGun           152 names    84 priced     55.3%
    Missile              63 names    30 priced     47.6%
    MissileLauncher      63 names    18 priced     28.6%
    BombLauncher         11 names     1 priced      9.1%
    Radar                58 names     0 priced      0.0%

**The five component classes the loadout bench exists to show — power plant,
cooler, shield, quantum drive, weapon — all land between 55% and 78%.** That is a
working join, not a broken one.

## 4. The residue, classified rather than discarded

The 314 unpriced names sort into four real groups:

**A — Radar, all 58 names, zero priced.** Not a matching failure. **UEX does not
carry radar prices at all**, and no radar UUID appears in the price file. This is
a gap in the source, and it is clean: we can say "no price data exists for radar"
rather than showing a blank.

**B — Missile launchers and bomb launchers, 55 unpriced.** Racks are largely
ship-fitted rather than shop-stocked. Plausibly correct absence, not a defect.

**C — Named parts genuinely absent from UEX** — the largest group, and the honest
one. `Mauler Shield Generator`, `Sukoran`, `SecureShield`, `Suldrath`, `Mirage`,
`Veil`, `Holdstrong`, `RS-Barrier`. Real parts, real names, no UEX row. **These
are the ones a contributor's screenshot could fill** — which is exactly the
patch-attributed-observation role the collector was re-scoped to.

**D — Duplicate-name variants, 69 names on 2 to 12 records each.** One name, many
UUIDs, and UEX prices one. **The display decision is whether a price found on one
variant may be shown on its siblings.** That is a judgement, not a bug, and it
should be made deliberately rather than by whichever join was written first.

## 5. The FIND page — the join is fine, the COVERAGE is not

    7,728 UEX catalogue items
    2,798 have at least one price row  =  36.2%

**Nearly two thirds of the catalogue has no price anywhere.** Unpriced, by section:

    Armor              1,656        Miscellaneous        347
    Liveries           1,080        Commodities          175
    Clothing             754        Vehicle Weapons      139
    Personal Weapons     401        Undersuits            94

**This is not a join failure and no amount of matching work fixes it.** UEX simply
has no price for those items. A FIND page built on this shows a price on roughly
one item in three, and the gaps are concentrated in the sections a visitor is most
likely to browse — armour and clothing.

## 6. Freshness — and one figure that should decide the display

Every price row carries `date_modified`, so **age is available per row**. It is not
a patch number; it is a timestamp.

    oldest    2026-04-01
    median    2026-05-27
    newest    2026-07-31

    by month:  Apr 5    May 14,538    Jun 2,983    Jul 6,208

**Over 60% of the price rows were last touched in May.** As of today that is
roughly **eleven weeks old**, and the snapshot itself is from 1 August — sixteen
days stale before anyone opens the page.

**Prices also carry a terminal**, and there are 823 of them with system, planet,
moon, station and city IDs. So "where to buy" is answerable, which is the half of
the tagline the loadout bench cannot currently deliver.

## 7. On the ±20% / ±100% tolerance — my read, for Sleven's decision

**These should not be displayed as a number with a currency symbol and nothing
else.** Two independent reasons, and the second is the stronger one:

- UEX's own declared tolerance is ±20%, widening to ±100%. A figure that may be
  double is not a price, it is an indication.
- **Independently of tolerance, the median row is eleven weeks old.** Even a
  perfectly accurate figure from May is not a fact about today.

**What I would show:** the figure, plus its age in plain words, plus the terminal
it came from. `"~ 21,500 aUEC · seen at CenterMass Area 18 · UEX, 11 weeks old"`.
The age is the honest part and we have it per row, so there is no reason to omit
it.

**What I would not do is hide the number behind a range.** A range computed from a
±100% tolerance is uninformative, and it reads as precision we do not have. **An
old exact figure with its date is more useful and more honest than a wide band
with no date.** But this is Sleven's call, not mine, and the numbers above are
what he needs to make it.

**Every row is `data_tier C` and should stay that way.** Nothing here upgrades it.

## 8. Which page this unblocks

**The loadout bench: UNBLOCKED.** The five component classes it shows land 55-78%
by distinct name, on a verified UUID join, with a terminal attached. It can show a
price and a place to buy for most fitted components today, and say "no price data"
for the rest — including radar, where the absence is now explained rather than
mysterious.

**FIND: NOT UNBLOCKED, and the join is not why.** The identifier works. The
coverage does not — 36.2% of the catalogue has any price at all, with armour,
liveries and clothing largely empty. **A FIND page built on this is two thirds
blank in the sections people browse most.** That is a source problem, and the
decision it needs is a scoping one: FIND could ship over the priced third and say
so, or wait. Neither is a matching job.

## 9. What I checked and what I did not

**Checked:** the UUID resolution in both directions; the name join, specifically to
establish that it is unsafe rather than to use it; type-by-type coverage counted
two ways, by record and by distinct name, because the two differ by a factor of
seven; the placeholder count; freshness from the actual timestamps.

**Did NOT check:**
- **Whether the types I called "not purchasable" truly are.** I classified thrusters,
  flight controllers, armour, fuel tanks and cargo grids as ship-fitted from the
  data's shape and from their total absence in a 23,734-row price file. **That is
  inference, and Sleven can confirm or kill it in ten seconds from the game.** If
  any of them IS shoppable, that category becomes a real gap.
- **Whether a price on one duplicate-name variant is valid for its siblings.** §4
  group D. Not mine to decide.
- **Whether a newer UEX snapshot exists.** I used 20260801T235530Z because it is
  the one on disk with item prices. A newer pull would move the freshness figures
  and nothing else in this finding.
- **Anything in `citizen-collector/`.** Untouched, as instructed.
