# FINDING — the 7,728 items are already well filed. Three things are wrong, and they are structural.

    from    C2, 2026-08-07
    for     C1 -> Claude Code, pending six rulings from Sleven
    data    UEX snapshot 20260801T235530Z, 56 items_category_*.json files
            merged, joined to items_prices_all.json (23,734 rows) and
            terminals.json (823). Every count below computed this session.

**Sleven asked for these to be sorted into the right category on the right page.
Before proposing a taxonomy, C2 measured the one that already exists.**

**Headline: UEX's taxonomy is good and should be kept. Do not replace it.
Three specific things are wrong, and none of them is "the categories are bad."**

---

## 1. WHAT EXISTS TODAY

**17 sections, 55 categories, and it is broadly correct.**

    2366  Armor         Helmets 670 · Arms 486 · Torso 476 · Legs 475 ·
                        Backpacks 150 · Full Set 109
    1809  Clothing      Jackets 453 · Shirts 367 · Legwear 347 · Footwear 307 ·
                        Hats 187 · Gloves 131 · Eyeware 14 · Full Set 3
    1099  Liveries      one category
     558  Personal Wpn  Personal Weapons 388 · Attachments 170
     504  Miscellaneous Miscellaneous 325 · Foods 102 · Drinks 55 ·
                        Consumables 13 · Container 9
     324  Vehicle Wpn   Guns 154 · Missile Racks 56 · Missiles 55 · Turrets 35 ·
                        PDC 11 · Bomb Racks 8 · Bombs 3 · Torpedo Tubes 2
     272  Systems       Power Plants 75 · Coolers 73 · Shields 64 ·
                        Quantum Drives 57 · Life Support 3
     199  Undersuits    ·  175 Commodities  ·  136 Avionics (Flight Blade 80,
     Radar 56)  ·  91 Utility (10 cats)  ·  77 Decorations  ·  41 Other
      31  Flair  ·  23 Module  ·  20 Technology (Mobiglas)  ·  3 Propulsion

**Priced coverage by section is uneven and worth knowing:** Clothing 1055 of
1809, Armor 710 of 2366, Liveries **19 of 1099**, Commodities **0 of 175**.

---

## 2. PROBLEM ONE — 1,084 items should not have their own pages at all

**This is the largest structural finding and it is 14% of the catalogue.**

    1,041   "<ship> ... Livery"        e.g. "Aurora MK I Green and Gold Livery"
       43   "<ship> Ship Armor"        e.g. "Aegis Redeemer Ship Armor"
    -----
    1,084   14.0% of all items

**These are not things you look up. They are attributes of a ship.** A page
reading *"Aurora MK I Green and Gold Livery — a paint for the Aurora"* has
nothing on it that the Aurora's own page could not say better, and there would
be 1,041 of them.

**The name encodes the parent** — every livery leads with a ship name. Leading
tokens: Aurora Mk 23, Hercules Starlifter 18, F7 Hornet 15, Mercury Star 14,
Ares Star 12, C8 Pisces 12, Zeus MK 11, 100 Series 11, Hornet Mk 10, Hull A/B/C
5 each.

**`data-layer/ship_resolution.json` already resolves ship identity** — 254 live,
221 matched. **The join is available and nobody has used it for this.**

**Note this collides with an existing open decision.** The editions/paints
finding already recommended an **acquisition field with six routes** — shop,
pledge, trade, award, subscription, factory — because paints attach to ships via
`required_tags` and carry `event_source`. **That decision and this one are the
same decision. Settle them together.**

---

## 3. PROBLEM TWO — 366 items are in a junk drawer, and they decompose cleanly

`Miscellaneous > Miscellaneous` (325) plus `Other > Other` (41). **They are not
miscellaneous. They are six distinct things nobody separated:**

    ship armour        "300i Ship Armor", "Aurora Mk I CL Ship Armor"
                       -> a ship component, misfiled as bric-a-brac
    countermeasures    "Aegis Avenger - Decoy Launcher", "Anvil Noise Launcher"
                       -> a ship component
    ship models        "350R Model", "Aegis Sabre Model" - maker "Takuetsu
                       Starships" -> a decoration
    trophies & tat     posters, plaques, coins, plushies, tankards, mugs,
                       paintings, replicas -> decorations / flair
    organic & food     "Blue Bilba", "Boreal Quasi Grazer Egg", "Banded Fessle",
                       "Amioshi Plague" (which is a COMMODITY)
    data & schematics  "ASD Memory Drive", "ASD Secure Drive", 25 schematics

**Every one of those is identifiable from the name.** That is what Sleven meant
by filing by what they are named, and on this bucket he is exactly right.

---

## 4. PROBLEM THREE — 3,218 items have no manufacturer

**42% of the catalogue has `company_name` null.** 130 distinct manufacturers
exist across the rest — Clark Defense Systems 455, RSI 402, Kastak Arms 218,
Greycat 199, Fiore 146, Behring 137.

**"Who makes it" is a filter the site cannot currently offer to four items in
ten.** Whether that is fixable from the game files is unchecked.

---

## 5. THE METHOD — and a warning against the obvious approach

**C2 tested name-pattern rules across the whole catalogue: 21 rules matched
3,733 items, 48%.**

**That result is misleading and the approach is wrong.** Most of those matches —
Helmet 672, Core/Torso 461, Arms 456, Legs 456, Undersuit 146, Backpack 138 —
are **re-deriving classifications UEX already supplies correctly.** Building a
second taxonomy over a working one creates two authorities for one fact, which
is the exact defect class this project has already been bitten by three times.

**The rule that follows:**

> **UEX's section and category stay the spine. Name rules apply ONLY where UEX
> is silent (Miscellaneous, Other) or where the item's shape is wrong
> (liveries, ship armour). Never as a parallel classification.**

**Scoped that way the job is small:** roughly a dozen rules for §3's junk
drawer, plus one parent-resolution rule for §2. **Not 7,728 decisions — about
fifteen rules and six rulings.**

**Rules live in a data file, not in code**, so a new pattern costs a line.
**And per the standing rule, the classifier flags — it never auto-fixes.**
Findings go to the results table for review.

---

## 6. THE SIX RULINGS NEEDED FROM SLEVEN

**Nobody should hand-sort 7,728 items. These six decisions sort them.**

    1  LIVERIES (1,041)   own pages, ship-page only, or listed-but-not-paged?
                          Also settles the paints/editions acquisition-field
                          question, which is the same decision.
    2  SHIP ARMOR (43)    a ship component page, or ship-page only?
    3  "FULL SET" (112)   Armor 109 + Clothing 3. Is a set an item, or a
                          container of items? It behaves like a bundle.
    4  JUNK DRAWER (366)  confirm the six buckets in §3, name them, and say
                          which get pages.
    5  COMMODITIES        175 here, 206 in resources/commodities.json, 204 from
                          UEX's own endpoint. Three counts. One page type or
                          two, and which list is authoritative?
    6  NO MANUFACTURER    3,218 items. Leave blank, infer from name, or hide
       (3,218)            the filter when unknown?

---

## 7. NOT VERIFIED

- **Whether livery names join cleanly to `ship_resolution.json`.** Leading
  tokens look right; the join has not been run. **"Hull A" and "100 Series" will
  need care.**
- **Whether the 175 UEX commodities overlap the 206 in the game files**, or are
  a different set. **Not compared.**
- **Whether manufacturer is recoverable** for the 3,218 from `items.json` or
  `fps-items.json`. Unchecked.
- **Whether "Ship Armor" is the hull-plating component or a cosmetic.** C2 is
  inferring from the name. **Sleven will know in one second.**
- **The junk-drawer buckets are C2's reading of 45 sampled names**, not a
  classification of all 366.
