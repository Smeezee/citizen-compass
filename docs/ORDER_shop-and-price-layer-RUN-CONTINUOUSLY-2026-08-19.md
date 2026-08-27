# ORDER — build the shop and price layer, and make FIND real. RUN CONTINUOUSLY.

    from    C1, 2026-08-19
    for     Code
    status  GO. No stop points. No decision gates. Nothing in this document
              requires Sleven before you start or while you run.
    size    Measured, not guessed: 23,734 price rows, 823 terminals,
              100 categories, ~99 category files. This is a multi-hour build.

---

## 0. Why this order looks different from the last five

Your last run was 16m35s and produced 1,073 correct lines. **That is not a slow
agent. That is an agent finishing what it was given.** The fault is mine: I have
been handing you one commit's worth of work and then asking why you stopped after
one commit.

So this order is not "the same thing but try harder". It is a **drain list of 25
items with a measurable finish condition**, every decision pre-ruled, and a ledger
you append to so that a context compaction does not end the run.

**Finishing an item is not a stopping point.** Read §1 before anything else.

---

## 1. RUN RULES — these govern the whole run

1. **The only legitimate stops are:** every item in §5 is marked DONE or BLOCKED
   in the ledger, or you are out of usage. Nothing else.
2. **After each item:** append one line to the ledger (§4), commit that item, and
   **begin the next item immediately.** Do not summarise to the user between
   items. Do not ask if you should continue.
3. **Do not ask questions.** Every decision I could foresee has a default in §3.
   If you hit one I did not foresee, take the option that is **cheapest to
   reverse**, write it in the ledger under `DECIDED-BY-DEFAULT`, and keep going.
   Sleven will overrule it later if he wants to; a stopped run costs more than a
   reversible wrong default.
4. **A blocked item does not block the run.** Mark it `BLOCKED — <one line why>`
   and go to the next item. Come back at the end if time remains.
5. **If you are compacted, read the ledger first.** It is the resume point and it
   is why it exists. Do not re-derive state from git log.
6. **Commit per item**, so a crash costs one item and not the run. Never
   `git add -A` — name the paths.
7. **Do not cut a release.** Sleven tests before anything ships.
8. **Every check needs a control that could have failed it** (Rule 12). An
   auditor never observed firing is not an auditor. This is not optional
   polish — it is half of each acceptance line in §5.

---

## 2. GROUND TRUTH — measured in the repo today, not remembered

    data-layer/external-sources/uexcorp/snapshots/20260801T235530Z/
      items_prices_all.json    23,734 rows   id_item, id_terminal, price_buy,
                                             price_sell, item_uuid, item_name,
                                             terminal_name, date_modified
      terminals.json              823 rows   id, name, fullname, nickname, code,
                                             type, and the full location
                                             hierarchy: id_star_system, id_planet,
                                             id_orbit, id_moon, id_space_station,
                                             id_outpost, id_poi, id_city
      categories.json             100 rows   id, type, section, name,
                                             is_game_related, is_mining
      items_category_<N>.json    ~99 files   uuid, name, category, section, size,
                                             company_name, vehicle_name, slug,
                                             url_store

    data-layer/external-sources/uexcorp/snapshots/20260806T033315Z/
      commodities_prices_all.json  2,597 rows   buy/sell, avg, scu stock, status

**The database has none of this.** `app/models.py` today defines Patch, System,
Manufacturer, Ship, Dealer, ShipDealerListing, PledgeLink, ComponentType,
Component, WeaponDetail, MissileDetail, MissileRackDetail, GimbalMountDetail,
TurretDetail, ShipRegistry. **There is no Terminal, no Location, no ShopItem, no
ItemPrice, no Commodity.** The entire shop layer is unbuilt. That is this order.

**`testing/_deploy/find.html` is a mockup** — its own banner says so:
*"MOCKUP — prices and shops are invented"*, 17 invented items across 9 invented
shops. **It is the last big mockup on the site and it is what blocks 0.4.0.**
23,734 real price rows are sitting on disk unread.

---

## 3. PRE-RULED — do not ask, do not re-litigate

1. **Prices display as whole aUEC with thousand separators.** Buy and sell are
   **separate columns**. A blended average is **never** shown as if it were a
   price. If only one side exists, show that side and leave the other blank —
   blank means "no data", and blank is honest.
2. **Join on UUID. Never on display name.** One display name spans up to 12
   records; this has already bitten this project. Where a name collides in the
   UI, show `name` plus the smallest disambiguator that separates them (size,
   then grade, then manufacturer).
3. **Whether thrusters, armour and fuel tanks are shop-bought is NOT ruled — it
   is MEASURED.** Item C4 counts, per category, how many items carry at least one
   price row. Build for all 100 categories regardless. Hiding a category is a
   display decision Sleven makes later, from that number. **This is the pattern:
   a question I would have asked him becomes a measurement you record.**
4. **Prices are append-only, keyed by snapshot.** Never overwrite a price row.
   The roadmap watcher already overwrote history once on this project and it cost
   a rebuild. A price is a fact with a date attached.
5. **A UEX field whose meaning is unclear goes into the JSONB `detail` blob**, and
   the uncertainty goes in the ledger. Do not drop it. Do not invent a column for
   it. Do not guess what it means in a comment.
6. **An item with no price rows still gets a row.** Absence is data and the site
   must be able to say "nobody sells this".
7. **Currency is aUEC. Do not convert anything to anything.**
8. **`is_game_related = 0` categories are imported and flagged, not skipped.**
9. **Hybrid schema, per standing rule:** real indexed columns for anything queried
   — name, uuid, category, terminal, price, location — and JSONB only for the
   category-specific tail. Items across 100 categories with wildly different
   detail is precisely the case that rule was written for. **Do not put price in
   JSONB.** Do not put the whole record in JSONB.
10. **Every row carries `last_verified_patch`** and the front end flags unverified
    data. Standing rule, no exceptions for this layer.

---

## 4. THE LEDGER — write it first, before item A1

Create `docs/LEDGER_shop-price-layer-2026-08-19.md`. **Append-only.** One line per
item, appended the moment the item finishes:

    A1  DONE     <commit sha>  <one line: what exists now that did not before>
    A2  BLOCKED  <one line: why, and what would unblock it>
    B4  DONE     <sha>  DECIDED-BY-DEFAULT: <the call you made and why it reverses cheaply>

This file is the resume point after a compaction and it is the thing Sleven reads
instead of a conversation. **Do not rewrite earlier lines.** Append.

---

## 5. THE WORK LIST — 25 items, in order

### Phase A — schema

**A1. Location hierarchy.** UEX terminals carry system/planet/orbit/moon/station/
outpost/poi/city. Model it. Real columns for the levels that get queried, JSONB for
the tail. Alembic migration.
*Acceptance:* a terminal resolves to a readable location string. *Control:* a
terminal with a null mid-level (station but no moon) still resolves and does not
crash or emit "None".

**A2. `Terminal`.** uex_id UNIQUE, name, nickname, code, type, location FK,
`detail` JSONB, `last_verified_patch`.
*Acceptance:* 823 rows import. *Control:* a duplicate uex_id is REFUSED by the
database, observed.

**A3. `ItemCategory`.** 100 rows: id, section, name, is_game_related, is_mining.
*Acceptance:* 100 rows, sections group correctly.

**A4. `ShopItem`.** uuid UNIQUE (the join key), name, category FK, company_name,
vehicle_name, size, slug, url_store, `detail` JSONB.
*Acceptance:* uuid is unique and indexed. *Control:* two items sharing a display
name both import and stay distinct.

**A5. `ItemPrice`.** item FK, terminal FK, price_buy, price_sell, source
date_modified, snapshot FK. UNIQUE(item, terminal, snapshot). Indexed on item, on
terminal, on price_buy.
*Acceptance:* the unique key exists. *Control:* re-running the same snapshot
inserts zero new rows.

**A6. `Snapshot`.** One row per UEX snapshot directory — path, captured_at,
row counts. This is what makes §3.4 real.
*Acceptance:* both existing snapshots (20260801T235530Z, 20260806T033315Z) are rows.

**A7. Hard constraints.** Non-negative prices, no orphan FKs, unique keys. This is
the DB-constraint half of the standing validation rule.
*Control:* each constraint is observed REFUSING a deliberately bad insert. A
constraint nobody has seen reject anything is not a constraint.

### Phase B — three concrete importers, THEN generalise

**B1. Terminals importer** — concrete, hand-written, 823 rows.
**B2. Items importer for category 20 only** — 1,099 rows, the largest file.
Concrete. Not generic. Resist.
**B3. Prices importer** — 23,734 rows, append-only per snapshot.
*Acceptance for each:* row counts match the source file exactly, and a re-run is
idempotent.

**B4. NOW generalise.** Read what B1–B3 actually needed and extract the shared
pipeline from that. **Do not design it before B1–B3 exist** — standing rule, and
the reason it exists is that the abstraction guessed in advance is always wrong.
Record in the ledger what the three genuinely shared and what you thought they
would share and did not.

**B5. Run the pipeline over the remaining ~99 category files.**
*Acceptance:* total imported items equals the sum of the source file lengths.
*Control:* a malformed category file fails loudly, and does not silently import
zero rows and report success.

**B6. Commodities.** 2,597 rows from the 08-06 snapshot into the same shape.
Commodity prices carry stock and status fields items do not — those go in `detail`.

### Phase C — auditors. FLAG ONLY, never auto-fix.

All write to the existing findings store (`checks/findings_store.py`).

**C1. Price outliers** — prices absurd against their category's distribution.
**C2. Orphans** — price rows whose item or terminal is missing.
**C3. Name collisions** — how many display names map to more than one uuid, and the
worst case. Record the numbers in the ledger.
**C4. Category price coverage** — for each of the 100 categories, how many items
carry at least one price row. **This is the item that answers Sleven's thruster/
armour/fuel-tank question with a number.** Put the full table in the ledger.
**C5. Staleness** — age of each row's source date_modified, bucketed.
**C6. Negative control for C1–C5.** Feed each auditor a row that must trip it and
**observe it fire.** Then feed clean data and observe it stay silent. Both halves,
or the auditor is not proven.

### Phase D — API

**D1.** Generic CRUD/router factory over Terminal, ShopItem, ItemCategory —
list + filter + detail, per standing rule. Lock the response envelope and
pagination format now, in writing, before there are three consumers of it.
**D2.** `item uuid → every terminal selling it`, with resolved location, buy and
sell separate.
**D3.** The reverse: `terminal → what it sells`.
**D4.** Search: name substring, category filter, price range.
*Acceptance for each:* verified against the running API, not against the code.
*Control:* a uuid that does not exist returns a clean 404, not a 500 and not an
empty 200.

### Phase E — FIND stops being a mockup

**E1.** Wire `find.html` to D2/D3/D4. Delete the invented data block — the file
has a section literally commented `/* ================= invented data ================= */`.
**E2.** **Remove the MOCKUP banner ONLY after fetching the deployed URL and
confirming real rows come back.** Not after a successful build. Not after a
successful deploy. After reading the live page. This project has been burned by
"deployed" meaning "deployed" three times.
**E3.** Buy and sell in separate columns, per §3.1.
**E4.** Every row shows its snapshot date and `last_verified_patch`; unverified
data is visibly flagged, per standing rule.
*Control:* a search that matches nothing shows an honest empty state, not a
spinner and not invented filler.

### Phase F — the leftovers, if the run still has time

**F1.** `data-layer/derived/holo-hardpoints-join/join_report.json` lists **39
skipped** ships. Report why each was skipped, grouped by cause, in the ledger. Do
not fix them yet — the grouping is the deliverable, because it will show that most
of the 39 share two or three causes.
**F2.** The **7 `unchecked_hull`** entries — same treatment.
**F3.** `testing/_deploy/index.html` has **two `cc-pending` panels** saying
hardpoint and component data "reaches this panel once the API is wired in".
Phase D wires an API. Say in the ledger what those two panels would now need.

---

## 6. WHAT MUST NOT HAPPEN

- **Do not stop between items.** §1.
- **Do not ask a question you can convert into a measurement.** §3.3.
- **Do not remove the MOCKUP banner before reading the live page.** §E2.
- **Do not overwrite price history.** §3.4.
- **Do not design the shared pipeline before B1–B3 exist.** §B4.
- **Do not auto-fix anything from an auditor.** Auditors flag. Standing rule.
- **Do not `git add -A`.**
- **Do not cut a release.**
- **Do not touch the collector in this run.** It is finished for now and it is a
  different component; mixing them makes both harder to test.

## 7. AT THE END, REPORT

- The ledger, as it stands.
- The C4 table — price coverage per category. That is the one Sleven wants.
- The C3 numbers — how bad the name collisions actually are.
- Anything you marked `DECIDED-BY-DEFAULT`, so he can overrule it cheaply.
- Anything in this order you think is wrong. §B4 and §3.9 are the parts most worth
  arguing with, and an argument backed by what the data turned out to look like is
  worth more than compliance.
