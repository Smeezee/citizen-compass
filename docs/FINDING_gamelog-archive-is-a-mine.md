# FINDING — the Game.log archive is a dataset, and it goes back to January 2024

    id      FINDING-LOG-02
    by      C1, 2026-08-07
    source  Star Citizen's own log backups, read directly from Sleven's machine:
              …\StarCitizen\LIVE\logbackups\   ~230 sessions, Jan 2024 - Aug 2026
              …\StarCitizen\PTU\logbackups\      6 sessions, Aug 2026
    status  115 sessions mined, 0 parse errors. Output is in the repo.

---

## 1. THE THING NOBODY NOTICED

Star Citizen does not overwrite `Game.log`. **It renames the old one and keeps
it**, in a `logbackups` folder beside the install. The header of every live log
says so and has always said so:

    BackupNameAttachment=" Build(12399239) 07 Aug 26 (17 18 42)"  -- used by backup system

So the project has not been sitting on two logs. It has been sitting on **two
and a half years of them**, unread, on a disk it already owns.

---

## 2. WHAT CAME OUT — 115 sessions mined, zero parse errors

    214   item-market transactions      206 buy, 8 SELL
      8   commodity-market transactions   1 buy, 7 sell
    156   distinct items with a price
     27   distinct shops named
     40   distinct locations
    916   distinct ship classes observed
     73   quantum destinations with fuel estimates

**The 8 sell rows matter out of proportion to their count.** This project has
listed sell prices as a dataset that does not exist and shipped a SELL tab with
nothing behind it. These are real, dated, per-shop observations:

    2026-01-29        30   rsi_deckcrew_undersuit_01_01_10      Cordrys, Levski
    2026-01-29       480   rsi_deckcrew_armor_light_helmet_01   Cordrys, Levski
    2026-01-29    10,024   grin_salvage_repair_01               Dumpers Depot, Area18
    2026-06-14        30   MISL_S03_CS_FSKI_Arrester            ShipWeapons, UtilStation
    2026-07-22       362   kegr_fire_extinguisher_01            XS MiningCart
    2026-08-07        23   crlf_consumable_healing_01           Conscientious Objects, Levski
    2026-08-07       810   grin_multitool_01_salvage_repair     XS MiningStall

Eight is not a dataset. **It is proof the pipeline exists**, and every future
session adds to it for free.

---

## 3. FOUR TRANSACTION FAMILIES, NOT ONE

`FINDING-LOG-01` described one shape. There are four, and they share a field
grammar:

    SShopBuyRequest            item purchase          206 seen
    SShopSellRequest           item sale                8 seen
    SShopCommodityBuyRequest   commodity purchase       1 seen
    SShopCommoditySellRequest  commodity sale           7 seen

**This is the payload-shape rule paying for itself immediately.** The miner
matches `S(Shop|ShopCommodity)(Buy|Sell)Request` and reads fields by name, so
all four fell out of one pattern — and the two families nobody knew about were
found by the parser rather than by a person.

**Do not read `amount` on a commodity line as a price.** It is the quantity the
client offered. There is no unit price in that line and inferring one would be
exactly the kind of confident-wrong number this project keeps getting bitten by.

### The class-name churn is now measurable

    186  CEntityComponentShopUIProvider::SendShopBuyRequest         (4.9 and earlier)
     20  CEntityComponentShoppingProvider::SendStandardItemBuyRequest  (4.10)
      8  CEntityComponentShopUIProvider::SendShopSellRequest

`shop_class_names.json` records every emitting class with a line count. **A name
that stops appearing in new builds is a parser about to go silent**, and now
that is visible in a file instead of being discovered a month later.

---

## 4. THE RENDERER AND WINDOW MODE ARE IN THE LOG

`FINDING-LOG-01` §5 asked for Win32 window-style inspection to tell exclusive
fullscreen from borderless. **Not needed.** The game states both, plainly:

    Change resolution: 1920x1080 (Borderless at 60.000Hz)
    D3D Adapter: FeatureLevel = DirectX 11.1

The miner already extracts `renderer`, `display_mode` and `resolution` per
session. That is the whole of the diagnostic that cost two evenings, available
from a file the collector already reads, at zero cost.

---

## 5. PRIVACY — how this obeys the standing rule

The rule is **strip before the file exists**, not filter afterwards. The miner:

- emits **only allow-listed field names**. A new CIG field is dropped unless
  someone adds it deliberately, so a future patch cannot leak an identifier into
  the dataset by surprise.
- carries a `FORBIDDEN` set — `playerId`, `shopId`, `sessionId`, `shardId`,
  `nickname`, `node_id`, `playerGEID`, `accountId`, `geid` — that is checked
  even for fields on the allow-list.
- **never emits a raw line and never emits a context field.** Not even for
  debugging. That is the hole every log tool eventually falls into.
- strips `playerId` even though it is Sleven's own. It is an identifier and the
  rule has no exception for the person running it.

**Audited, with a negative control.** Every output file was scanned for known
identifier VALUES (both character IDs, both handles, the account number, the
machine name, and the other players' names seen in earlier logs) and for any
bare 11+ digit number outside a kiosk field. Result: PASS. The audit was then
handed a planted handle and correctly flagged it — a check that cannot fail is
not a check.

**The raw logs stay out of the repo.** They were read from the install folder
and mined in a scratch environment. Only the stripped output is committed.

---

## 6. WHAT IS IN THE REPO

    data-layer/derived/gamelog-mining/
      MANIFEST.json                  sessions read, builds covered, totals, privacy note
      shop_transactions.json         214 item buy/sell rows
      commodity_transactions.json      8 commodity rows
      locations.json                  40 locations by session count
      ships_seen.json                916 ship classes by session count
      quantum_routes.json             73 destinations with fuel estimates
      shop_class_names.json          the rename early-warning
      mine_gamelogs.py               the miner, rerunnable

---

## 7. WHAT THIS CHANGES

- **The collector is no longer the only way to get this data.** It is the way to
  get it *going forward*; the archive is the backfill. Those are different jobs
  and the archive one is already done.
- **Re-run the miner after every session.** It is idempotent and takes seconds.
- **The 2024-2025 backfill is still on the table.** 115 of ~236 sessions were
  mined; the rest are mostly pre-December-2025 builds that predate shop logging,
  but they carry locations, ships and quantum routes. Worth a second pass, low
  priority.
- **`ships_seen.json` has 916 entries against a site that lists 254 ships.** Most
  of the excess will be NPC and derelict variants, and some will be
  `ship_resolution.json`'s 89 "leftovers" showing up in the wild. That comparison
  has not been run and is not claimed here — it is the obvious next question.
