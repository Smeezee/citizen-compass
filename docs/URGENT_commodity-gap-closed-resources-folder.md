# URGENT — the commodity gap is closed. It has been on disk since 1 August.

    from   C2, 2026-08-06
    for    C1 -> Claude Code
    files  snapshot 20260801T204744Z, resources/ — four files, never opened
    effect closes the ONE blocker in WO-COLLECT-01 rev 5 §4.4, and closes the
           "remaining gap" declared in claude/location-data-acquisition-note.md

**Do not pull the UEX commodity endpoint. Do not build an open-vocabulary path.
Both were recommended in rev 5 and both are unnecessary.**

---

## 1. `resources/commodities.json` — 206 commodities, named

    206 rows · 203 with a real display name · 30 with a raw -> refined link

**My "~200 commodities" estimate, carried unverified through every revision of
the collector, was 206.** It is now counted.

Fields per commodity:

    UUID · Key · Name · Description · CommodityGroups · Tier
    RefinedVersionUUID · RefinedVersionName
    DensityGPerCc · Volatility · VolatilityHealthDecayPerSecond
    Instability · Resistance
    QualityDistributionUUID · QualityLocationOverrideUUID
    CargoContainers[] · HasDefaultCargoContainers · ValidateDefaultCargoBox

**The refinery chain is explicit** — 30 raw/refined pairs:

    Agricium (Ore)      -> Agricium         Aluminum (Ore)  -> Aluminum
    Aslarite (Raw)      -> Aslarite         Beryl (Raw)     -> Beryl
    Bexalite (Raw)      -> Bexalite         Borase (Ore)    -> Borase
    Construction Pieces -> Construction Materials
    Construction Rubble -> Construction Materials

**`names.dat` gets its commodity list today, from a file already gated and
sealed. §4.4 is no longer a blocker.**

---

## 2. `resources/commodity_trade_locations.json` — THE BIG ONE

**41.6 MB. 109 commodities. 234 distinct trade locations.**

    SoldAt rows      47,980
    BoughtAt rows    48,737
    ------------------------
    total pairs      96,717

Each entry, verbatim shape:

    { "CommodityUUID": "...", "CommodityKey": "Agricium",
      "CommodityName": "Agricium",
      "SoldAt":   [ {TradeLocationUUID, TradeLocationClassName,
                     TradeLocationDisplayName, StarmapObjectUUID,
                     MatchedTagUUID, MatchedTagName} ... ],
      "BoughtAt": [ ... same shape ... ] }

**`StarmapObjectUUID` is the join into `starmap.json` and
`starmap_positions.json`** — so commodity, location, hierarchy and coordinates
connect with no name matching anywhere.

Most widely traded: Waste 750 · Aphorite 485 · Dolivine 485 · Hadanite 485 ·
Astatine 481 · Chlorine 481 · Iodine 481 · CompBoard 480.

### This closes a gap the project declared open and never revisited

`claude/location-data-acquisition-note.md`, 2026-07-31, said:

> **Item-level inventory by location.** `trade_locations.json` records what a
> location produces and consumes at the level of *category tags* — "Luxury,"
> "Commodity" — not at the level of specific items. **There is no visible
> mapping saying *this shop sells this weapon at this price*. That mapping is
> the remaining gap, and it is what the flagship query actually depends on.**

It then listed UEX, Cornerstone and StarHead as candidate external sources.

**For commodities the mapping exists, in the same snapshot, in a file that was
never opened.** *"Where can I buy Agricium"* and *"who buys what I am carrying"*
are answerable now, offline, with no external source and no capture.

**What it still does not give is the price.** That remains the gap and remains
the collector's job.

---

## 3. WHAT THIS DOES TO THE COLLECTOR

**Rev 5 Part 3 row 2 said "commodity prices — zero rows held." Still true. But
the job just got much smaller.**

Before: read the commodity name, read the place, read the number, match all three.

**Now: we already know the 206 names and the 234 places and which of the 96,717
combinations are even possible. The collector only has to read the number.**

    the name    known - 206, closed vocabulary, §1
    the place   known - 234, and which commodities trade there, §2
    the number  UNKNOWN - the only thing left to capture

**That is a far higher-confidence read.** Standing at a terminal we already know
what should be listed, so a row that matches nothing is a genuine finding rather
than a suspected misread — §4.6's shop-inventory prior, but for commodities and
available immediately.

**Amend rev 5 §4.4:** the "one genuine blocker in Part 4" is closed. Remove the
UEX commodity pull from the build order.

---

## 4. `resources/locations.json` — mining and salvage prospecting

    66 providers · 247 groups · 1,133 deposit entries

Group names are the activity: `SpaceShip_Mineables`, `GroundVehicle_Mineables`,
`FPS_Mineables`, `Harvestables`, `Salvage_FreshDerelicts`,
`Salvage_BrokenShips_Poor` / `_Normal` / `_Elite`.

Each group carries `GroupProbability` and a `Deposits[]` list of
`{ResourceUUID, RelativeProbability}`.

**This is "where do I find X, and how likely is it" — per location, with real
probabilities.** Nobody publishes it. It is the natural companion to the
crafting surface, since Aslarite alone appears in 856 of 1,597 blueprints.

---

## 5. `items.json` — `Mineable`, 37 rows

Ore composition, e.g. Carinite:

    DepositName "Carinite" · MinimumDistinctElements 1
    Composition[] of {ResourceTypeClassName, ResourceTypeDisplayName,
                      MinPercentage, MaxPercentage, Probability, QualityScale}

Named deposits seen: Carinite, Feynmaline, Hadanite, Dolivine, Aphorite,
Glacosite, Sadaryx, Janalite, Carinite (Pure), Rock Slab, Irradiated Valakkar
Hide. **These are the hand-mined gems that `build-spec-descriptions...` flagged
as unpriced and uncosted.** Composition and quality ranges are now available for
them even though prices are not.

---

## 6. `resources/resources.json` — 557 rows, mostly unnamed

`{UUID, Key, Name, Kind}`. `Kind` includes `cave_harvestable`. **Almost every
`Name` is `<= PLACEHOLDER =>`** — this is an internal registry, not a content
source. **Low value. Do not spend time on it.**

---

## 7. ORDER OF WORK — SUGGESTED, C1's CALL

1. **Fold the 206 commodity names into `names.dat` now.** One file read. It
   unblocks the collector's first real target.
2. **Build the commodity -> location index** from §2. 96,717 pairs, joined to
   coordinates via `StarmapObjectUUID`. **Shard it — 41.6 MB raw, and the static
   ruling applies.**
3. **Merge it into the amenities targeting list** (rev 5 §5.3). The list stops
   being "31 refineries, go look" and becomes "this terminal trades these 14
   commodities and we have a price for none of them."
4. Mining/salvage prospecting from §4 — real, but it is a site feature, not a
   collector dependency. **Not tonight.**

---

## 8. NOT VERIFIED

- **Whether `SoldAt`/`BoughtAt` reflect current 4.9 behaviour** or are stale
  design data. 96,717 pairs across 234 locations is plausible but unchecked
  against the game. **The first commodity kiosk screenshot tests it** — which is
  another reason tonight's grabber matters.
- **Whether all 234 `TradeLocationDisplayName` values join cleanly** to
  `starmap.json` via `StarmapObjectUUID`. Some are null in the sample.
- **Why 109 commodities have trade locations when 206 exist.** The other 97 may
  be non-tradeable, mission-only, or simply absent. **Do not present the
  difference as "cannot be traded" until someone checks.**
- **Whether `Tier`, `Volatility` and `Instability` mean what they sound like.**
  Present on the commodity rows, never examined.
