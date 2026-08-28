# FINDING — we hold 28 MB of CIG trade data nobody has ever opened. It is not what it looks like, and I nearly published a badly wrong number from it. Here is what it actually is, what it cannot do, and the three things in it that are clean.

    from      C1 (Cowork), 2026-08-27 evening
    question  Sleven: "have we gone through all the data and found a use for
              everything?"
    answer    No. The ship side is mined out. The ECONOMY side — the half the
              site is named after — is barely touched.
    status    MEASURED. Nothing built, nothing published.

---

## 1. WHAT WE HOLD AND HAVE NEVER READ

Of CIG's own shipped data in the 4.10 snapshot, nothing in this repository reads:

    resources/commodity_trade_locations.json   28 MB    109 commodities
    resources/commodities.json                243 KB    206 commodities
    trade_locations.json                      1.6 MB    965 locations
    starmap.json + starmap_positions.json     2.5 MB  2,056 locations
    contracts/                              5,120 files
    factions/                                  74 files

**The site's tagline is "Know where to buy, before you fly."** CIG ships a file
called `commodity_trade_locations.json` and it has never been opened.

## 2. WHAT IT LOOKED LIKE

    commodities with trade data                        109
    SoldAt entries                                  47,980
    BoughtAt entries                                48,737
    distinct trade locations referenced                845
    location UUIDs that fail to join trade_locations.json  0

**A perfect UUID join, no fuzzy matching, 96,717 trade facts.** Against it, the
site's UEX price layer has 2,091 price rows for the same commodities.

That reads as **UEX covering 2.2% of the trade network** — and I was one step
from writing that down.

## 3. WHAT IT ACTUALLY IS, AND WHY THAT NUMBER IS WRONG

**Every one of the 47,980 SoldAt entries carries a `MatchedTagUUID`.** The file
is not a shop inventory. It is the output of matching a commodity's tags against
a location's `ProducesTags` / `ConsumesTags`. It says what a place is
**permitted** to trade, not what is on the shelf.

    commodities "sold" per location:   max 109, median 38, min 1  (of 109)
    locations "selling" more than half the catalogue:  404 of 837

    "On-Call Area"          sells 109 commodities
    "Lobby"                 sells 109 commodities
    "Security Checkpoint"   sells 109 commodities

**A security checkpoint is not a commodity market.** Comparing UEX's real shop
prices against this graph compares a shelf to a licence. The 2.2% is a
comparison of two different things and publishing it would have been a confident
wrong number about the site's own biggest gap.

**Rule: do not publish location counts from this file.** It is capability.

## 4. AND THE JOIN THAT WOULD FIX IT IS BLOCKED

To check UEX's shop rows against CIG's permission graph, UEX terminals must join
to CIG locations. They cannot:

    UEX terminals                                      823
    CIG trade locations carrying a display name        266
    exact name matches                        55  (6.7%)
    of those, AMBIGUOUS - name claimed by 2+ locations  12

CIG reuses display names heavily — 39 names belong to two locations, 14 to three,
and one belongs to six. **A name join here would be fuzzy AND mostly ambiguous**,
which is the matching this project has banned twice and been bitten by twice.

**There is no UUID path from UEX to CIG.** UEX is a community source and carries
its own ids. Unless UEX starts publishing CIG UUIDs, verifying the shop layer
against CIG's locations is not available at any level of effort.

**That is worth knowing plainly**: the shop layer's `shop_items_verified: 0` is
not laziness and not a missing afternoon's work. The join does not exist.

### 4a. AND IT IS WORSE THAN A MISSING JOIN — CIG SHIPS NO PRICES AT ALL

Having found the join blocked, I checked whether there was anything on the other
side of it to join TO. Every JSON in the snapshot, searched for any key
containing price, cost, buy or sell:

    blueprints.json / manufacturers.json / tags.json          none
    trade_locations.json / starmap.json                       none
    items.json / ship-items.json / fps-items.json
        AmmoCost · AmmoCostMultiplier · CostPerBullet

**Ammunition cost per bullet. That is the entire economic content of CIG's
export.** No shop prices, no buy or sell values, no stock, no inventories.
`ShopDisplay` appears 463 times in items.json and is a piece of furniture — a
display case — not a shop.

**So the shop layer can never be verified against the game files, because the
game files do not contain the answer.** Not this snapshot, not a later one:
scunpacked exports what CIG ships, and CIG does not ship prices.

**This changes what `shop_items_verified: 0` means.** It has been sitting on the
pre-live punch list as work somebody has not got to. **It is not work. It is a
thing that cannot be done from data**, and the only ways to verify a price are a
person standing in the shop, or a second independent community source that
disagrees or agrees.

**That belongs in Sleven's going-live decision rather than on a task list.** The
honest choices are to publish the prices clearly labelled as community-reported
and dated, or not to publish them — and the current site does neither, it just
shows them.

## 5. THREE THINGS IN THERE THAT ARE CLEAN AND UNUSED

### 5a. Thirty raw-to-refined pairs, stated by CIG outright

    Agricium (Ore)      -> Agricium        Aluminum (Ore)   -> Aluminum
    Aslarite (Raw)      -> Aslarite        Beryl (Raw)      -> Beryl
    Bexalite (Raw)      -> Bexalite        Borase (Ore)     -> Borase
    Copper (Ore)        -> Copper          Corundum (Raw)   -> Corundum
    Diamond (Raw)       -> Diamond
    Construction Pieces / Rubble / Salvage -> Construction Materials

`RefinedVersionUUID` and `RefinedVersionName` on the commodity record. **Exact,
authoritative, no inference.** A miner holding raw ore wants to know what it
becomes and the site cannot currently say.

### 5b. 203 named commodities with UUIDs, and a rarity tier on 27 of them

    common 10 · uncommon 6 · rare 5 · epic 3 · legendary 3

### 5c. A measurement of the source the site depends on

Testing every name UEX prices against every name CIG ships, exact equality,
case-folded, across items, ship-items, fps-items, commodities and resources:

    things UEX prices                     7,932
    names CIG also carries                7,049   (88.9%)
    names CIG has NO record of              883   (11.1%)

The unmatched are dominated by raw mining materials and generics — `Fireworks`,
`Ice (Raw)`, `Coal`, `Crude Oil`, `Krypton`, `Ship Ammunition - Size 1`.

**This is the first measurement anyone here has taken of UEX's agreement with
the game's own files**, and 11% is a number worth knowing before that data is
published as fact. It does not mean UEX is wrong — a name CIG spells differently
lands in this bucket too — but it bounds the problem.

## 6. WHAT I RECOMMEND

**Build 5a.** Raw-to-refined is thirty exact pairs from CIG's own records, it
needs no join to anything, and it answers a question every mining player has.
It is the cheapest real feature left in the data.

**Do not build anything from the trade-location graph** until someone can say,
with evidence, which entries are inventory rather than permission. My guess is
that nothing in this file can, and the answer lives in the shop terminals'
own records instead.

**Record §4 and §4a in CURRENT-STATE**, and take
`shop_items_verified: 0` off the pre-live punch list as a chore. **CIG ships no
prices**, so no amount of effort closes it. It is a labelling decision for
Sleven, not an engineering task, and leaving it on a list of things to do
implies otherwise to every session that reads the list.

## 7. What I checked and what I did not

**Checked:** every JSON file in the 4.10 snapshot for whether any script reads
it; the full SoldAt/BoughtAt structure and its tag provenance; the location-UUID
join (0 failures); commodities-per-location distribution; the UEX-to-CIG name
overlap across five source files; the UEX-terminal-to-CIG-location name join and
its ambiguity.

**Also checked, after the first draft of this document said it was the next
thing to do:** whether CIG's item records carry shop inventories or prices. They
do not — the only cost-like fields in the entire export are ammunition costs.
That is §4a, and it is the most consequential paragraph here.

**Did NOT check:** the 5,120 contract files or the 74 faction files — both
unread and both a separate question. Did not open `starmap.json` beyond counting
it.

---

*C1, 2026-08-27. The interesting part of this document is the number I did not
publish.*
