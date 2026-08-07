# WORKORDER — catalog-01: closing the four remaining item-filing rulings

    from     C3 (Cowork), 2026-08-07
    for      C1 -> Claude Code, after Sleven answers the three boxed rulings below
    scope    the four rulings still open per docs/FINDING_7728-items-taxonomy-three-real-problems.md §6
             and HANDOFF-all-sessions-2026-08-07.md Part 3. LIVERIES and SHIP ARMOR placement
             are already settled in WORKORDER_place-01 and are not reopened here.
    data     data-layer/external-sources/uexcorp/snapshots/20260801T235530Z (items export,
             7,728 rows, via Downloads\_cc_items_merged.json) cross-checked against
             snapshots/20260806T033315Z/commodities.json (204 rows, live UEX commodity
             endpoint) and data-layer/external-sources/scunpacked-data/snapshots/
             20260801T204744Z/resources/commodities.json (206 rows, game files).
             Every count below was computed against the actual files this session — none
             of it is sampled or estimated.
    companion junk-drawer-366-classified.json — all 366 items, one row each, with a
             proposed bucket and destination. Load this directly rather than re-deriving
             the rules; it supersedes FINDING_7728's 45-item sample.

**Per Sleven's instruction this session: classification uses each item's own name and
type, checked against every category — not just the section it's currently filed under.
That's the method behind everything below.** Where that produces a confident answer, this
document proposes one and flags it for override, per the project's standing rule that
classifiers flag and never auto-fix. Three questions came back with no confident answer
from the data — those need Sleven's word before C1 builds anything.

---

## RULING NEEDED 1 — "Full Set" (112 items: 109 Armor + 3 Clothing)

Behaves like a bundle: buying it presumably grants the individual pieces, which already
exist as separate catalog items (Helmets, Torso, Legs, etc. are already priced and paged
on their own).

**Also found, not in the original 112:** a 113th Full Set outside Armor/Clothing —
"RCMBNT Full Set" (Associated Sciences & Development), filed under Other > Other, in the
junk drawer. Same shape, different domain (electronics, not wearables). Whatever the
ruling is, it should say whether this one is covered by it or needs its own call.

> **NEEDS SLEVEN:** does a Full Set get its own catalog page as a bundle/SKU (with a
> component list), or is it purely a purchase path — no page, just "buy all pieces
> together," since every piece already has one?

---

## RULING NEEDED 2 — the junk drawer, now classified in full (366 of 366, not 45)

FINDING_7728 identified six buckets from a 45-item sample and said so explicitly. This
session ran the full 366 through name-pattern rules built from that same read. Real
picture, eight buckets plus real residue:

    131  trophies_tat            plushies, coins, medals, mugs, posters, replicas,
                                  figures, statues — decorations/flair, largest bucket
     60  organic_food            named fauna/flora/food items — SEE COMMODITY OVERLAP below
     38  ship_armour             "<ship> Ship Armor" — same class WO-PLACE-01 already
                                  ruled on. 5 more of this exact class sit misfiled under
                                  Armor > Arms (open item #14 on the main handoff) —
                                  38 + 5 = the 43 that ruling covers.
     38  data_schematics         Comp-Boards, keycards, schematics, memory/secure drives,
                                  access protocols, prototype electronics (RCMBNT/GRX)
     30  ship_models_takuetsu    display models, maker "Takuetsu Starships" — decorations.
                                  NOTE: this bucket also caught cargo-container minis
                                  (branded UDM/Ling/TABA/Red Wind/ITG/Covalex) by the same
                                  "*Model" name pattern — different thing, needs a manual
                                  split, not automatic
     28  UNCLASSIFIED            matched none of the 8 patterns — full list below
     22  artifact_fragments      artifact fragments, war medals/markers, ingots, scrap —
                                  collectibles, not consumables
     14  countermeasures         decoy launchers, noise launchers, EMP generators — real
                                  equippable ship components, shop-sold. Should not be
                                  decorations.
      5  scrip_tokens            "MG Scrip," "Council Scrip," "Tholo Token," "Wikelo
                                  Favor" — read as in-game event currency/vouchers, not
                                  physical items. Candidate for excluding from the catalog
                                  outright rather than filing anywhere.

**The commodity overlap, which changes the organic_food count:** 25 of the 60
organic_food items name-match an entry in UEX's live commodity endpoint (204 rows) —
Amioshi Plague, Golden Medmon, Pitambu, Blue Bilva, Kopion Horn (and its Tundra/Cave/
Irradiated variants), Lunes, Decari Pod, Degnous Root, Heart of the Woods, Prota, Ranta
Dung, Revenant Pod, Sunset Berries, Stone Bug Shell, E'Tam, and four "Year of the ___
Envelope" / "Luminalia Gift" items whose match may be coincidental rather than real (those
last four need an eyeball, not a rule). **These 25 are candidates to move to Commodities
outright rather than being decorations** — full list and per-item flag in the companion
JSON (`commodity_name_match_204endpoint`).

**The 28 unclassified**, for a direct read rather than a guess:

    Fish Tank (Gold)                    Book
    Polaris Bit                         Bottle
    Expired Quantanium Fuel Canister    Radegast Whiskey 2947 Homeward Limited-Edition
    Compboard                           Luminalia Gift
    Luminalia Cookie Jar                Space Globe - Glorious Moments
    "Quantanium" Water Bottle           BB-12 Manned Maneuvering Unit
    Datapad                             Medivac Rescue Light
    Pyrotechnic Amalgamated Toolbox     Space Globe - Good Health
    Vasli Fragment Stone                Retired Drill Head
    Vanduul Scythe Armor                Personal Care Product
    Planet Artifact                     Ration Pack
    Cockpit Recorder Prop               Codi the Coramor Bear
    Picoball                            Field Medic Kit
    Alignment Blade                     GP-XP Industrial Battery

**Three of those — Ration Pack, Field Medic Kit, Personal Care Product — look like they
belong in the existing Consumables category** (Miscellaneous > Consumables, 13 items
already), not in the junk drawer at all. Worth checking whether they were miscategorized
independently of this cleanup.

> **NEEDS SLEVEN:** confirm/override the eight proposed destinations above (one line per
> bucket is enough — "yes" or "no, put X here instead"), rule on the 5 scrip/token items
> (catalog or drop), and give the 28 unclassified + 4 uncertain-commodity-matches a look.
> Everything else in this ruling is a rename, not a decision — C1 can implement the rest
> straight from the companion JSON once these are answered.

---

## RULING NEEDED 3 — commodities: the three counts, reconciled, and the real question underneath them

FINDING_7728 posed this as "three counts, which is authoritative." Running the actual
diff this session found the real issue is not which number is right — **it's that the
three sources measure different things, and two of them disagree with each other more
than expected even after accounting for that.**

    175   UEX items-export, section = "Commodities" (2026-08-01 snapshot)
    204   UEX's own dedicated commodities API endpoint (2026-08-06 pull)
    206   resources/commodities.json — raw game files (2026-08-01 snapshot)

**175 vs 204:** 175 is essentially a subset of 204 — 169 of 175 match by name exactly, and
4 of the remaining 6 are pure formatting differences ("audio visual equipment" vs
"audio-visual equipment," "raw ice" vs "ice (raw)," etc., not real gaps). **175 is not a
third commodity count — it's the join between "is a commodity" and "also has a shop
listing in the general item catalog."** It should not be presented as a competing count at
all.

**204 vs 206 — the real open question.** 206 raw rows include 11 that are not tradeable
cargo at all (`HasDefaultCargoContainers: false`) — Heat, Cooler, Life Support, Oxygen,
CO2, Power — these are ship-system simulation values reusing the commodity schema, not
things you buy or sell. Filtering those out (and one row whose Name never resolved past
`<= PLACEHOLDER =>`) leaves **193 real tradeable commodities in the game files.**

Diffed against the 204-endpoint by name: **only 165 of 193 match — 28 of the game files'
tradeable commodities don't appear on UEX's live endpoint, and 39 names on UEX's endpoint
don't appear in this game-files snapshot.** Some of that is naming variance (Hephaestanite
"(Raw)" vs "(R)"), but 28-in-206-not-in-204 is too large to wave off as formatting. This
was never checked before now — `URGENT_commodity-gap-closed-resources-folder.md` declared
206 the closed, counted answer without diffing it against either UEX source, which is the
same "stopped at the first count" pattern the project's own Part 5 has now caught six
times. **It should be downgraded from settled to re-verify, same as the MyBook backup was
in Part 0.**

**Recommendation, not a ruling — this one's an engineering call, flagged for sign-off
rather than pure Sleven judgment:** treat `resources/commodities.json` as the spine (it's
the internal source of truth, same reasoning the project already applies to quantum range
and fuel consumption — game files over third-party APIs), filtered to
`HasDefaultCargoContainers: true` with a resolved name (193 rows), one page type, joined
to UEX for live price/terminal data where a name match exists. The 28-name gap needs a
real reconciliation pass (likely fuzzy match on the Raw/R and parenthetical variants)
before that join is trustworthy — **that's a C1/Code task, not a rename.**

> **NEEDS SLEVEN:** confirm the recommendation above (game files as spine, one page type),
> or say if there's a reason to prefer the UEX endpoint instead. Either way, flag that the
> "206, closed" finding from 2026-08-06 needs a correction note — the number holds, but
> "closed" doesn't yet.

---

## RULING 4 — no manufacturer (3,218 items, 42%) — Sleven's answer already given, here's the rule

Sleven's instruction this session: *items without a manufacturer have a name and usually a
type; classify using those, checked against every category, not one.* Applied:

**175 of the 3,218 (5.4%) are commodities, and commodities structurally never carry a
manufacturer** — every single item in the Commodities section (175/175) has `company_name`
null. This isn't a data gap to fill, it's a property of the category: raw materials in
this game aren't attributed to a maker. **Recommendation: exclude the Commodities section
from the manufacturer filter/facet entirely** rather than counting it toward "unknown."
That alone reframes the real gap from 3,218 down to 3,043.

Breakdown of the remaining 3,043 by section, for scale:

    953  Armor            405  Liveries           68  Vehicle Weapons
    761  Clothing         157  Personal Weapons    39  Avionics
    433  Miscellaneous     76  Undersuits          31  Flair
                            71  Decorations        11  Systems
                            29  Other                9  Utility

**Proposed mechanism, reusing the project's existing auditor pattern rather than
inventing a new one** (validation = DB constraints + a pluggable checker layer that flags,
never auto-fixes, per the standing architecture decision): add a `manufacturer_inference`
checker that proposes a candidate manufacturer only where there's a real join — the
clearest case is Liveries (405 of the 3,043), where `ship_resolution.json` already
resolves the parent ship, and the parent ship's own manufacturer is known. A livery for a
`crus_starfighter_*` ship can safely inherit Crusader's manufacturer; that's not a guess,
it's the same fact stated twice. Everywhere else (Armor, Clothing, Personal Weapons, etc.)
a name-prefix guess is exactly the kind of second taxonomy FINDING_7728 already warned
against — **leave those blank rather than infer them from pattern-matching alone.**

**This part needs no further ruling — it's specified enough for C1 to build**: exclude
Commodities from the facet, add the liveries-inherit-from-ship-manufacturer checker,
leave the rest blank. Findings go to the results table for review same as every other
checker; nothing auto-writes to `company_name`.

---

## SUMMARY — what's ready for C1 now vs. what's still waiting on Sleven

**Ready to build once the three boxed rulings land:**
- Junk-drawer reclassification per the companion JSON (buckets are confirmed or corrected
  in one pass over 8 lines, not 366 individual decisions)
- The manufacturer checker (Ruling 4 — no further sign-off needed)

**Blocked on Sleven, one line each:**
1. Full Set — own page or purchase-path-only (and does it cover "RCMBNT Full Set" too)
2. Junk-drawer bucket destinations — confirm/override 8 lines, rule on scrip/tokens, eyeball 28 + 4 items
3. Commodities — confirm game-files-as-spine recommendation, and sign off on downgrading
   the "206, closed" finding to re-verify

**Not this document's call, flagged for the record:** the commodities re-verification
(28-name gap between the 193 real tradeable game-files commodities and the 204-endpoint)
needs a proper reconciliation pass before any join is built on it. That's implementation
work for C1/Code once Ruling 3 is answered, not something to guess at here.
