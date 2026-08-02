# PLAN — Build A (find / item / shop) under the static ruling

**From C2 to C1. 2026-08-02. Planning only. Nothing built, nothing written to the repository.**

Written after reading `docs/order-front-end-build.md` and the 2026-08-02 handoff
archive, so it starts from the rulings rather than from my earlier plan. Where
this and `docs/workorder-front-end-build-plan.md` disagree, **this is the
correction** — the differences are listed in §7.

---

## 1. THE MEASUREMENT THAT SETTLES THE ARCHITECTURE

The static ruling left an open question nobody had measured: whether a static
site can actually carry 7,728 items, 23,734 prices and 479 shops.

**It can, easily. Measured, trimmed to the fields the front end needs, gzipped:**

| payload | rows | raw | gzipped |
|---|---:|---:|---:|
| item index — id, name, category, section, manufacturer, uuid, slug | 7,728 | 1.16 MB | **0.28 MB** |
| price table — item, terminal, buy, sell, date | 23,734 | 1.15 MB | **0.15 MB** |
| shop table — 479 item terminals with location fields + game_version | 479 | 0.07 MB | **0.01 MB** |
| **total** | | **2.38 MB** | **0.44 MB** |

**The entire searchable catalogue is under half a megabyte over the wire.**

For scale: `testing/_deploy/index.html` is already 1.5 MB, and `_deploy/` is
**349 MB** — 235 ship models. The data is noise next to what already ships.

### What follows from it

- **No page-per-item build.** Three JSON files, client-side routing. That is
  **3 files against the 20,000 cap, not 8,867.** The cap stops being a
  consideration at all.
- **No sharding, no lazy-loading of the core three.** They load once and the
  whole site is interactive.
- **No FastAPI, and now for a second independent reason.** The ruling rested on
  the zero-runtime-dependency property. This adds: there is nothing a backend
  would do here that 440 KB of JSON does not already do faster.

### The one payload that does NOT go in the bundle

**Descriptions.** 5,344 items carry CIG prose (WO-CRAFT-01 §WO-1), averaging
several hundred characters — roughly 2.7 MB raw before compression. That is six
times the rest of the bundle combined for something only ever read one item at a
time.

**Shard them.** `desc/<bucket>.json` keyed by item id, bucket = `id % 64`, fetched
on demand when an item page opens. 64 files, ~40 KB each. Still trivially inside
the cap.

---

## 2. DATA CONTRACT

Emitted by a build step from the sealed snapshots, into `testing/_deploy/data/`.

    items.json      [{i:id, n:name, c:category, s:section, m:manufacturer,
                      u:uuid, g:slug, x:exclusivity, p:parent_id, col:color}]
    prices.json     [{i:id_item, t:id_terminal, b:price_buy,
                      s:price_sell, d:date_modified}]
    shops.json      [{i:id, n:name, ty:type, sy:star_system, p:planet,
                      ss:space_station, ci:city, o:outpost, gv:game_version,
                      f:{food,medical,shop_fps,shop_vehicle,freight_elevator}}]
    desc/NN.json    {item_id: "description text"}     64 shards
    meta.json       {snapshot, patch, built_at, counts}

Single-letter keys are not premature optimisation — they are most of the gap
between 2.38 MB and something worth thinking about. **Document the mapping in
`meta.json` so it is not folklore.**

**Joins, all by id, none by name:**

    items.i  ->  prices.i
    prices.t ->  shops.i
    items.u  ->  desc shard        (uuid only used to build the shard, not at runtime)

---

## 3. THE DOORWAYS

Eight, ordered by how many *priced* items sit behind them. Full reasoning in
`claude/plan-doorways-and-browse-layer.md`; corrections to it are in §7.

| # | doorway | UEX sections | items | priced |
|---|---|---|---:|---:|
| 1 | Suits & armour | Armor, Undersuits | 2,565 | 815 |
| 2 | Clothing | Clothing | 1,809 | 1,055 |
| 3 | Weapons & ammo | Personal Weapons | 558 | 157 |
| 4 | Ship parts | Systems, Vehicle Weapons, Avionics, Propulsion, Module | 758 | 474 |
| 5 | Tools & equipment | Utility, Technology | 111 | 104 |
| 6 | Food, drink & meds | Misc → Foods #63, Drinks #62, Consumables #16 | 170 | ~110 |
| 7 | Ships | source 1 + `ship_resolution.json` | 254 live | — |
| 8 | Places | shops, stations, cities, planets, systems | 479 shops | — |

Liveries (1,099), Decorations (77), Flair (31), Commodities (175), Other (41) and
the `Miscellaneous → Miscellaneous #61` bucket (325) are **findable by search and
tag, with no doorway.** That is the point of tags.

**Doorway 7 must use `data-layer/ship_resolution.json`** — 254 live, 215 matched,
2 ambiguous, 37 without a game file, 6 tier variants, **95 game files parked by
Sleven, do not surface them.** Do not re-derive this.

**Each doorway page is:** an honesty sentence with real counts → sub-category
tiles with count and priced-count → the views strip → nothing else.

---

## 4. THE THREE PAGES

### 4.1 Search

One text field, ordinary English. Stop-word strip before matching (list in
`docs/workorder-front-end-build-plan.md` §A1). Match against name, category,
manufacturer, shop name, place name. Location-aware: *"flight suits new babbage"*
ranks New Babbage stock first and says why.

Nine real test phrases are in that plan and are the requirement, not a
convenience. **A real phrase returning nothing is a search bug.**

Runs entirely client-side over `items.json` — 7,728 rows is nothing to filter in
a browser.

### 4.2 Item page

Order: breadcrumb → header → **description** → answer line → where to buy → sell
line (conditional) → confidence panel → others in this category.

**Description sits above the answer line and is the biggest change from the
earlier plan.** 69% coverage, against 36% for price and 0% for images. Two
rendering modes — prose, and CIG's newline-delimited stat blocks
(*"Item Type: Heavy Armor / Damage Reduction: 40%"*). **My detection heuristic
for telling them apart is untested — validate against a sample.**

**Answer line:** *"Sold at 4 shops. Cheapest is Casaba Outlet in Area18 at
12,400 aUEC."*

**For the 4,930 items with no price**, the answer line changes rather than
disappearing:

    exclusive (1,313)   "You can't buy this in the game. It came with a pledge."
    unexplained (2,524) "No shop we know of stocks this."
    liveries (1,080)    cosmetic; treated as above

**Sell price is one conditional line, not a section** — 171 items of 7,728 have
one.

**Price age colouring must come off the real distribution:** median 66 days, 75%
over 30 days. The earlier plan's "amber at one day old" would render the whole
site amber. Suggested fresh <30 / amber 30–75 / red >75 — **Sleven's call, not
mine.**

### 4.3 Shop page

479 shops, not 823 — 823 counts fuel, refinery, commodity and rental terminals
too. 469 have at least one price row.

Breadcrumb built from **whichever location fields are non-null**, not a fixed
shape: of 479 item terminals, space station is set on 379, planet 340, city 65,
outpost 39, moon 9, system 479. **The earlier plan's "system › planet › city ›
shop" is the minority path.**

Answer line, what they sell, what they buy, also-at-this-location.

**Shops have pictures — 394 of 479 carry a `screenshot`.** Whether we may display
UEX-hosted community screenshots is unresolved and touches the 7 unread
`fan_kit_compliance` warnings. **Design the page to work without them and treat
images as an enhancement pending that answer.**

Each shop carries `game_version` — a real last-verified-patch, set on 429 of 479,
and mostly stale (3.24.2 on 154, 4.0 on 108). Show it. Nobody else does.

---

## 5. ENTRY POINTS — planned both ways so this does not block

The tab layout is the only decision still blocking Builds A, B and C. **Both
branches are planned so work can start before it lands.**

Measured: the base page's nav is at `releases/latest.html:452-454` and uses
**in-page anchors** (`#matrix`, `#calendar`), not page links. That matters —
"put FIND in the nav" is not a one-line change to an existing pattern.

**Branch 1 — C1's recommendation (my preference).** DISPLAY and FEEDBACK stay on
the right edge. FIND and KEYBINDS become nav entries. LOADOUT already goes on the
ship page. Since the nav is anchor-based, either the nav gains its first true
page link, or Find becomes a section on the same page. **The second is more
consistent and cheaper, and suits a client-rendered app.**

**Branch 2 — right edge keeps everything.** Requires solving the geometry:
five tabs at `44% + 0/150/290/430/570px` puts FIND at 1045px on a 1080px
viewport. Only works at 1440p. Not recommended.

**Either way the build owns an explicit list with an explicit position per
entry, controlled by Sleven** — not re-emitted from whatever was last in the
file. That is the correction to my §8a, which would have restored the LOADOUT
tab after every rebuild and overridden a decision already made twice.

---

## 6. VERIFICATION — HARD RULE 12

- **Assert the bundle stays under 1 MB gzipped.** Measured 0.44 MB today. This
  is the assertion that keeps the static ruling true as data grows.
- **Assert every one of the nine real search phrases returns a correct result.**
- **Assert an item page renders complete with description, price and image all
  empty.** 2,384 items have no description; 4,930 have no price; 7,728 have no
  image. **All three absent at once is the common case, not the edge case.**
- **Assert a price never renders without its age and source.**
- **Assert the shop breadcrumb renders for a terminal with no city** — 414 of
  479 have no `city_name`.
- **Assert no name-based join anywhere.**
- **Assert the 95 parked game-file ships never appear.**
- **Assert the compliance footer is present on every page and every overlay.**

---

## 7. CORRECTIONS TO MY EARLIER PLANS

Both live in the project and the repo; treat these as amendments.

| # | earlier claim | correction |
|---|---|---|
| 1 | "823 shops" | **479** item terminals, 469 with a price row |
| 2 | "What it sells for" as a page section | **171 items of 7,728 (2.2%)** — one conditional line |
| 3 | "amber at a day old" | median age **66 days**; 75% over 30. Thresholds from the distribution |
| 4 | "design pages that work without a picture" | true for items (0 of 7,728); **false for shops** (394 of 479) |
| 5 | "no 'what it's good for' — that's writing, not data" | **5,344 items (69%)** have CIG prose |
| 6 | "Build B forces the FastAPI backend" | **ruled against.** §1 shows nothing needs it |
| 7 | §8a — build re-emits the tabs | **would override Sleven's LOADOUT removal.** Do not implement |
| 8 | "verify the `Loadout` array across ships" | **confirmed by C1**, 10 of 10. Closed |
| 9 | ship identity not addressed | **`ship_resolution.json` exists.** Use it |
| 10 | `commodity_trade_locations.json` gives where-to-buy | **tag-matched, not stock.** 15 materials share one identical 468-location set |

---

## 8. WHAT I DID NOT VERIFY

- **The stat-block vs prose detection heuristic.** Mine, untested.
- **Whether the nav can take a page link at all** without disturbing the
  anchor-scroll behaviour. Read the markup; did not test.
- **Description coverage per doorway.** Total is 69%; the split is unknown, so I
  cannot say whether Ship parts reads better or worse than Clothing.
- **Whether `is_available` / `is_available_live` / `is_visible` should filter
  shops.** 768 / 755 / 773 of 823 are true. Meaning unknown — **check UEX's docs
  before using them**, or ~20 shops get wrongly shown or hidden.
- **Licence and hotlink status of the 394 shop screenshots.**
- **Real gzip transfer size**, as opposed to my `gzip.compress` estimate.
  Cloudflare may use brotli, which would be smaller.

---

## 9. OPEN FOR SLEVEN

1. **Tab layout** — branch 1 or 2 in §5. Blocks A, B and C.
2. **Price-age thresholds** — fresh/amber/red boundaries.
3. **Shop screenshots** — display or not, given the Fan Kit position.
4. **Does Clothing get its own doorway**, or fold into Suits & armour? It is the
   best-covered data on the site — 1,055 of 1,809 priced — and burying it costs
   the most of any single call here.
