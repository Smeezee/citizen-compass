# WORK ORDER — ship-attached items: liveries, ship armour, and the placement model

    id      WO-PLACE-01
    from    C2, 2026-08-07
    for     C1 -> Claude Code
    rests   docs/RULING_one-item-record-many-placements.md  (Sleven, binding)
    on      docs/FINDING_7728-items-taxonomy-three-real-problems.md
    data    UEX snapshot 20260801T235530Z. Every count computed 2026-08-07.
    repo    C2 wrote nothing except inbox/*.md

**Sleven's ruling, restated because everything below derives from it:**

> Anything belonging to a ship appears in the ship section. Those same items
> ALSO stay listed in the main item catalogue. Liveries and similar are a
> category NOT selected by default. Long term, liveries render on the ship in
> the viewer.

**One item record. Placement is derived and many-to-many. Nothing is moved out
of the catalogue.**

---

## 0. BEFORE ANYTHING — a record that does not exist and should

**Sleven states he has already reviewed the Fan Kit and has already emailed CIG
and received approval for the live site.**

**C2 grepped all of `docs/`, `docs/handoff_archive/` and the claude.ai project.
There is no record of either.** Every hit on "approval" is about schema fixes or
WebFetch prompts.

**This is the project's single most important legal fact and it exists only in
Sleven's head and his email client.** Consequences already observed:

- C2 spent this session re-deriving the rights position from the ToS, and got it
  wrong twice before correcting.
- `WO-IMAGE-01` was written treating the Fan Kit as an unopened dependency.
- Every future session will repeat that unless it is written down.

**[C1] Ask Sleven for: the date sent, the date of reply, who at CIG replied,
what exactly was approved, and any conditions attached. Then file it as
`docs/RECORD_cig-fansite-approval.md` and reference it from `CURRENT-STATE.md`.**

**Until it is recorded, no session can rely on it, and `WO-IMAGE-01 §3` should
be read as already satisfied rather than blocking.**

---

## 1. THE PLACEMENT MODEL

**One canonical record per item. Placement derived, never stored on the item.**

    item record          UEX section + category stays the spine. Unchanged.
    ship attachment      0..n. Derived from:
                           liveries     name -> ship_resolution.json
                           ship armour  name -> ship_resolution.json
                           components   ships.json Loadout[] - already names
                                        every component on all 316 ships
    default visibility   a flag on the CATEGORY, not the item

**Derived, not stored, because when CIG adds a livery or refits a ship the
attachment recomputes from the same sealed snapshot everything else is built
from. Nothing hand-maintained. It cannot drift out of sync with the catalogue.**

---

## 2. LIVERIES — 1,041 items

**Name shape is rigid: `<ship> <theme> Livery`.** Leading tokens measured:
Aurora Mk 23, Hercules Starlifter 18, F7 Hornet 15, Mercury Star 14, Ares Star
12, C8 Pisces 12, Zeus MK 11, 100 Series 11, Hornet Mk 10, Hull A/B/C 5 each,
F8C Lightning 4, Nova Tank 3.

**19 of 1,041 carry a price.**

### 2a. Listed, not paged — C2's recommendation, override if Sleven disagrees

    listed only   one row in the search index. Clicking deep-links to the ship
                  page's livery section. ~0 files.
    own page      1,041 files against ~8,775 free headroom.

**A livery page can only ever say "this is a paint for the Aurora." The ship
page is where it can eventually show the thing** — which is what Sleven's ruling
§4 wants. **Deep-linking costs nothing and puts the content where it belongs.**

**[C1] If Sleven wants full pages, the only change is generating them. The join
work below is identical either way — do not block on this.**

### 2b. The join

**Parse the ship name from the livery name, resolve against
`data-layer/ship_resolution.json`.**

**Known hard cases, do not let them fail silently:**

    "Hull A" / "Hull B" / "Hull C"     single-letter suffixes. Greedy matching
                                       will collide.
    "100 Series"                       a family, not one ship. May attach to
                                       100i / 125a / 135c, or to the family.
    "Aurora Mk I" vs "Aurora MK I"     casing differs across rows.
    "Hornet Mk" vs "F7 Hornet"         same ship, two naming conventions.

**Report the residue. Do not discard it.** The ship-identity work already
established the rule: *no automated name match will ever be complete; classify
the residue rather than discard it.* **Assert the match rate and fail the build
if it drops.**

### 2c. Default visibility

**Set on the CATEGORY, never per item.** Liveries off by default in browse and
in search facets. **They must still be findable by an explicit search for the
name.**

**[C1] Sleven has not ruled on whether Decorations, Flair or trophies should
also default off. Do not extend it to them without asking.**

---

## 3. SHIP ARMOUR — 43 items, and UEX has them in two wrong places

**Measured this session, and this is a real data defect:**

    38 of 43   filed as  Miscellaneous > Miscellaneous
     5 of 43   filed as  Armor > Arms          <- PERSONAL armour arms
     0 of 43   have a price
     0 of 43   appear at any shop

**The five in `Armor > Arms` are the defect worth naming.** *"Starfarer Gemini
Ship Armor"*, *"Talisman R5 Ship Armor"*, *"Stinger Ship Armor"*, *"Starfarer
Ship Armor"* and *"Void Ship Armor"* are sitting in the category that holds
personal armour arm pieces. **A player filtering Armor > Arms for something to
wear currently gets ship hull plating.**

**Reclassify all 43 as ship-attached, out of both wrong homes.** Name shape is
`<ship> Ship Armor` and the same join as §2b applies.

**Nothing is purchasable** — zero priced, zero shops — so these are
factory-fitted or pledge-only. **The page must not imply they can be bought.**

**[C1] C2 is inferring from the name that these are hull plating rather than a
cosmetic. Sleven has not confirmed. If they are cosmetic they belong beside
liveries; if structural they belong beside components. Either way they are
ship-attached, so §1 and §2b are unaffected — only the category label changes.**

---

## 4. SHIP COMPONENTS — appear in both places, keep full pages

**Sections that are ship equipment:** Vehicle Weapons 324, Systems 272, Avionics
136, Utility 91, Module 23, Propulsion 3. **Roughly 849 items.**

**These are the opposite of liveries.** A quantum drive is genuinely something a
player shops for and compares. **Full page, in the catalogue, AND listed on
every ship that mounts it.**

**The join is already available and unused: `ships.json` `Loadout[]` names every
component on all 316 ships.** No name parsing needed — it is a structured
reference.

**Assert it.** Every component in the catalogue either appears in some ship's
`Loadout[]` or does not. **Report the count that does not** — those are shop-only
stock and need their own rule, not a silent gap.

---

## 5. WHAT A SHIP PAGE GAINS

Without duplicating a single item record:

    its liveries         from §2b, off by default, expandable
    its ship armour      from §3
    its fitted loadout   from ships.json Loadout[]
    its quantum range    QuantumTravel.Range - already computed, 257 of 316
    its hydrogen burn    Propulsion block - all 316
    its insurance        ExpeditedCost / claim times - all 316
    its cargo            149 of 316 carry a figure, max 4,608 SCU

---

## 6. ACCEPTANCE — all assertable, all able to fail

    every item                  still present in the main catalogue. The count
                                before and after is 7,728.
    livery join                 match rate reported; residue listed by name,
                                never silently dropped
    Hull A/B/C, 100 Series      explicitly handled, and named in the output
    ship armour                 all 43 reclassified; ZERO remain in Armor > Arms
    "can I buy it"              no ship-armour page implies purchasability
    components                  count that appears in a Loadout[] reported, and
                                the count that does not
    default visibility          set on the CATEGORY; a livery is still findable
                                by explicit name search
    file count                  reported after the build, against the 20,000 cap
    ship page                   lists liveries, armour and components without
                                duplicating their records

---

## 7. NOT VERIFIED

- **Whether livery names join cleanly.** Leading tokens look right; **the join
  has not been run.** §2b lists the known hard cases.
- **Whether "Ship Armor" is structural or cosmetic.** §3. C2 is inferring.
- **Whether every ship component appears in some `Loadout[]`.** §4.
- **Whether "100 Series" resolves to one ship or a family.** §2b.
- **Whether default-off should extend beyond liveries.** §2c. Not ruled on.
- **The CIG approval on file.** §0. **Stated by Sleven, recorded nowhere.**
