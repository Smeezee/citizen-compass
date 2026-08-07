# RULING BY SLEVEN — one item record, many placements

    from    C2, 2026-08-07, recording Sleven's ruling
    for     C1 -> Claude Code
    settles rulings 1 and 2 of docs/FINDING_7728-items-taxonomy-three-real-problems.md
            AND the paints/editions acquisition question, which was the same
            decision.

---

## THE RULING

**1. Anything that belongs to a ship appears in the ship section.**
Liveries, ship armour, and ship components — vehicle weapons, missiles, missile
racks, turrets, quantum drives, shields, coolers, power plants, radar, flight
blades, mining and salvage gear, jump modules.

**2. Those same items ALSO stay listed in the main item catalogue.**
They are not moved. They are not removed. **Both, not either.**

**3. Liveries and similar cosmetics are a category that is NOT selected by
default.** They do not appear in normal browsing. They surface when somebody
deliberately looks for them.

**4. Long term: liveries render ON the ship in the viewer**, so a player can see
what a livery actually looks like, in more detail than other sites provide.

---

## WHAT THIS CORRECTS IN C2'S PROPOSAL

**C2 framed ruling 1 as either/or — "own pages, ship-page only, or listed but
not paged."** Sleven rejected the premise. **The answer is both, with visibility
control.**

**That is the better architecture and it avoids a trap C2 walked into.** Moving
1,084 items out of the catalogue would have made the ship page a second
authority for what an item is. **Keeping one record and deriving its placements
keeps a single authority** — which is the standing rule this project already
enforces for schema ownership and for writers.

---

## THE DATA MODEL THAT FOLLOWS

**An item has ONE canonical record. Placement is DERIVED, not stored on the
item, and it is many-to-many.**

    item record        one row. UEX section + category stays the spine.
                       Unchanged by any of this.

    ship attachment    zero or more. Derived:
                         liveries      -> parsed from the name, joined to
                                          ship_resolution.json
                         ship armour   -> same
                         components    -> from ships.json Loadout[], which
                                          already names every component on
                                          every one of the 316 ships
    default visibility a flag on the CATEGORY, not the item. Liveries off by
                       default. Everything else on.

**Why derived rather than stored:** when CIG adds a livery or refits a ship, the
attachment recomputes from the same snapshot everything else is built from.
**Nothing to maintain by hand, and it cannot drift out of sync with the
catalogue.**

**This also settles the editions/paints question** from
`docs/finding-editions-paints-acquisition.md`. The recommended acquisition field
— shop, pledge, trade, award, subscription, factory — **is the same mechanism
viewed from the other end**: it says *how* you get an item, this says *what it
attaches to*. **Both are needed and neither replaces the other. Build them
together.**

---

## THE ONE THING STILL OPEN — listed is not the same as paged

**Sleven said liveries stay "listed" in the item catalogue. Listed and paged are
different costs and C2 should not assume which he meant.**

    listed only    one row in the search index. Clicking it deep-links to the
                   ship page's livery section.
                   Cost: ~0 files. 1,041 liveries cost nothing.
    own page       one file per livery.
                   Cost: 1,041 files against a budget with ~8,775 free.

**C2's recommendation: listed, not paged.** A livery page can only ever say
"this is a paint for the Aurora" — **the ship page is where it can actually show
the thing.** Deep-linking costs nothing, keeps them findable, and puts the
content where §4 of the ruling eventually needs it anyway.

**Ship COMPONENTS are the opposite and should keep full pages.** A quantum drive
is genuinely something a player shops for and compares across ships. **It earns
a page; a paint does not.**

**[C1] Confirm with Sleven before building. This is one question, not a
redesign.**

---

## THE VIEWER HOOK — do not build it, but do not block it

Ruling 4 wants liveries rendered on the ship model. **That is downstream of the
3D viewer and is not scheduled.**

**What it costs today: nothing, provided the livery→ship join is a real
relationship rather than a rendering detail.** Get that join right now and the
viewer inherits it later.

**What would break it: treating a livery as a string on a ship page.** Then the
viewer has to re-derive the relationship from scratch. **Same shape as the
append-only ruling — free to decide now, expensive to retrofit.**

---

## ACCEPTANCE

    every item                  appears in the main catalogue. Nothing is
                                removed from it.
    liveries                    joined to a ship, hidden from default browse,
                                findable when searched
    ship armour                 joined to a ship
    ship components             appear on the item catalogue AND on every ship
                                that mounts them, from ships.json Loadout[]
    default-visibility          set on the CATEGORY, never per item
    the join                    derived from the sealed snapshot, recomputable,
                                never hand-maintained
    a ship page                 lists its liveries, its armour and its
                                components without duplicating their records

---

## NOT VERIFIED

- **Whether livery names join cleanly to `ship_resolution.json`.** Leading
  tokens look right — Aurora Mk 23, Hercules Starlifter 18, F7 Hornet 15 — but
  **"Hull A", "Hull B", "Hull C" and "100 Series" will need care**, and the join
  has not been run.
- **Whether the 43 "Ship Armor" items are hull plating or cosmetic.** C2 is
  inferring from the name. **Sleven has not yet said.**
- **Whether every ship component in the catalogue appears in some ship's
  `Loadout[]`.** If some do not, they are shop-only stock and need a rule of
  their own.
- **Whether "not selected by default" should apply to anything besides
  liveries** — decorations, flair and trophies are plausible candidates.
  **Not ruled on.**
