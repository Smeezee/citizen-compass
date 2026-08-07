# FULL DIG — everything left in the data layer. Report for C1.

    from    C2, 2026-08-06
    for     C1 -> Claude Code
    method  read directly off the machine. Every number counted this session
            unless marked SAMPLE.
    scope   every source, every snapshot, every folder not previously opened.

**Two of my own load-bearing claims are wrong and are corrected below — §1 and
§2. Both were stated as fact in `WO-COLLECT-01 rev 5`. Read those first; they
change what the collector is for.**

---

# 1. CORRECTION — mission payouts ARE in the files, for about half of them

**Rev 5 Part 3 row 1 says: "CalculatedReward is a BOOLEAN. NO FILE CONTAINS IT.
Only observable." That is wrong, and it was the #1 justification for the whole
collector.**

**`FixedReward` is a separate field I never looked for.** It is a dict with a
real amount:

    {"Amount": 4000, "Max": 0, "BonusEligible": false,
     "Currency": "UEC", "ReputationBonus": "14d6becd-..."}

**SAMPLE — every 4th contract file, 1,277 of 5,108:**

    FixedReward present        643   (50.4%)  — dict, real aUEC amounts
    CalculatedReward present   593   (46.4%)  — bool, always true, no number
    both on one contract         0
    Cost present                35   (2.7%)   — int, e.g. 50,000 buy-in

Real amounts seen: Bounty Hunter 4,000 · Maintenance 6,250 · Mercenary 12,000 ·
Mercenary 20,000 · Hauling 25,000 · Priority 0.

**A full census timed out on the mount — 5,108 file reads is too slow through
the bridge. Treat 50/46 as a sample, not a count, and re-run it locally.**

### What this changes

**The two fields are mutually exclusive and they mean different things:**

    FixedReward       the payout is fixed and IS in the file. Publish it.
    CalculatedReward  the payout is computed at runtime. Genuinely unobtainable
                      from files. This half still needs observation.

**So the collector's mission-payout job halves, and becomes targeted rather than
blanket: only observe contracts whose `CalculatedReward` is true.** That is a
better job than the one rev 5 described — smaller, and it knows which missions
are worth watching before the player accepts one.

**And roughly 2,500 contracts can show a payout on the site today.**

---

# 2. CORRECTION — UEX was never asked for commodity prices

**Every plan in this project rests on "we hold zero commodity prices, and
screenshots are the only route." The first half is true. The second is not
established, because the endpoint was never called.**

`data-layer/external-sources/uexcorp/snapshots/20260801T235530Z/_pull_summary.json`
lists exactly what was requested:

    /items/                          400 - requires an id, body not saved
    /items_prices_all/               200 - 23,734 rows
    /terminals/                      200 - 823 rows
    /categories/ /companies/ /cities/ /moons/ /outposts/ /planets/
    /space_stations/ /star_systems/  200
    /vehicles_purchases_prices_all/  200 - 288 rows
    /items/?id_category=N            x100  (56 with data, 44 empty)

**No commodity endpoint appears anywhere in that list.**

**UEX API 2.0 publishes these, confirmed from UEX's own documentation today:**

    /commodities/                  the catalogue
    /commodities_prices/           per commodity
    /commodities_prices_all/       the complete price set
    /commodities_prices_history/   history
    /commodities_averages/         15-day averages
    /commodities_raw_prices/       and _all, and _raw_averages
    /commodities_routes/ /commodities_ranking/ /commodities_status/
    /commodities_alerts/

All Bearer-token, same key already in `.env`, 120 req/min, 172,800/day.

**And UEX's own terminal list already carries the commodity side:**

    terminal type    479 item · 161 commodity · 98 fuel · 32 vehicle_rent
                      23 commodity_raw · 21 refinery · 9 vehicle_buy

**205 commodity, commodity_raw and refinery terminals are already catalogued,
with full location joins, and we never asked what they charge.**

### What this changes

**Commodity prices may be one API call away.** Not confirmed until the call is
made — but the claim that screenshots are the only route is not supportable and
should stop being repeated, including by me.

**Caveats that stay true:** UEX is tier C, community-reported, **±20% tolerance
on commodities**, and `claude/plan-collection-channels.md` records a 66-day
median price age. **A UEX pull gives coverage, not freshness or accuracy.**

**So the collector is not cancelled — it is repositioned.** From *the only way
to get commodity prices* to *the way to verify and refresh them, and the only
way to get stock, runtime payouts and shop reality.* **That is still worth
building, and it is a more honest pitch.**

**`/commodities_prices_history/` and `/commodities_averages/` deserve a look on
their own** — a price with a 15-day average and a history behind it is exactly
the confidence position the site is built on, and nothing in this project has
history of any kind yet.

---

# 3. THE GRABBER IS BUILT AND WORKING — with one defect to fix before the crew

`citizen-collector/` exists in the repo root. **Code shipped it tonight.**

    main.go · capture.go · capture_wgc.go · capture_dxgi.go · capture_gdi.go
    gamelog.go · hotkey.go · winapi.go · testimage.go
    variant_crew.go · variant_master.go
    collector.exe (4,093,952 bytes) · collector-master.exe · README.md

**Six real captures taken, 03:12–03:15 UTC.** The sidecar is better than rev 5
specified:

    patch 4.9.188.23497 · build 12344265 · branch sc-alpha-4.9.0
    capture method wgc, 1920x1032, hardware driver, 410 ms
    patch_source "FileVersion" · build_source "BackupNameAttachment Build()"
    location_source 'gamerules="SC_Frontend" (VERIFIED pattern)'
    location_pattern_verified true · lines_read 776

**Recording the *source* of each field, and a `location_pattern_verified` flag,
is better provenance than I asked for. Keep it.**

### The defect

**Capture 0006 grabbed a DuckDuckGo browser window, not the game.**

    "window": { "title": "Citizen Compass v0.3.9 - DuckDuckGo",
                "exe": "duckduckgo.exe",
                "how_found": "matched --window against the title" }

Fine as a bench test. **Not fine on a crew member's machine.** Title matching
will capture whatever happens to match — a browser, a chat client, anything.
**That is precisely the leak `rev 5 §4.12` exists to prevent, arriving through
a different door.**

**Fix before anyone else installs it: match on the process — `StarCitizen.exe` —
and refuse to capture any other window, with the title match as a hint only, not
authority.** Bench testing against a browser can stay behind an explicit
`--allow-any-window` flag that the crew build does not compile in. **The variant
split already exists (`variant_crew.go` / `variant_master.go`), so this costs
almost nothing.**

---

# 4. THE UEX SNAPSHOT — full inventory

`uexcorp/snapshots/20260801T235530Z`, 114 files.

    items_prices_all.json      6.3 MB   23,734 rows   zero commodities
    terminals.json             1.0 MB      823 rows   55 fields each
    _items_by_category_summary  81 KB
    categories.json             100 rows  {id, name, section, type,
                                           is_game_related, is_mining}
    companies.json              311 rows  {industry, is_item_manufacturer,
                                           is_vehicle_manufacturer, wiki}
    star_systems.json            96 · planets.json 324 · moons.json 73
    space_stations.json          60 · outposts.json 117 · cities.json 5
    vehicles_purchases_prices_all 288 rows {id_terminal, id_vehicle, price_buy}
    items_category_1..112       100 files, 56 with data, 44 empty (57 bytes)

### `terminals.json` is far richer than the project has used

55 fields per terminal. **Service flags nobody has surfaced:**

    is_refinery · is_refuel · is_repair · is_medical · is_food · is_habitation
    is_jump_point · is_cargo_center · is_shop_fps · is_shop_vehicle
    is_player_owned · is_nqa · is_auto_load · is_affinity_influenceable
    has_docking_port · has_freight_elevator · has_loading_dock
    max_container_size · mcs

**And the location join is complete:** `id_star_system`, `id_planet`, `id_orbit`,
`id_moon`, `id_space_station`, `id_outpost`, `id_poi`, `id_city`, `id_faction`,
`id_company`, plus the resolved `*_name` for each.

**`game_version` per terminal** — per-row freshness, which the site's confidence
panel wants and currently derives from date fields only.

**`screenshot`, `screenshot_full`, `screenshot_author`** — the shop images.
394 of 479 item terminals carry one. **Display rights unresolved. Do not use.**

    is_available   768 of 823 · is_visible 773 of 823

**`space_stations.json`, `outposts.json` and `cities.json` carry the same
service flags** — `has_refinery`, `has_clinic`, `has_food`, `has_habitation`,
`has_cargo_center`, `has_quantum_marker`, `has_gravity`, `has_repair`.

**This is a second, independent source for the `Amenities` finding.** Two sources
agreeing is a check that can fail — **cross-check them and publish the
disagreements as findings.** Neither is authoritative alone.

---

# 5. THE REST OF `scunpacked-data`

**`manufacturers.json` — 141 rows.** `{Code, Name, Reference, Description}`.
**Some rows have a numeric code as the name** — first row is `Code "987",
Name "987"`. Real prose in `Description`. **Note the count: 141, not the 152
carried in earlier docs.** One of the two is wrong; 141 is what is in this file.

**`trade_locations.json` — 965 rows.** `{UUID, ClassName, DisplayName, Disabled,
ProducesTags, ConsumesTags}`. **`Disabled` is false on all 965** — nothing is
turned off. `ProducesTags` and `ConsumesTags` are each `{Positive[], Negative[]}`
of `{UUID, Name}` — the **Negative arrays have never been examined by anyone**
and may encode what a location refuses.

**Superseded by `resources/commodity_trade_locations.json`** for anything
item-level — see the commodity note filed earlier. **Keep this one for the
tag-level production model, not for inventory.**

**`blueprints.json` — 1,597 rows.** `{UUID, Key, Kind, Output, Tiers,
Availability, CategoryUUID, Dismantle}`. **`Dismantle` and `Kind` have never
been examined** — `Dismantle` is likely the salvage-return model and would
answer "what do I get back if I break this down", which no competitor shows.

**`factions/` — 74 files.** `{UUID, Name, DefaultReaction, FactionType,
AbleToArrest, PolicesLawfulTrespass, PolicesCriminality, NoLegalRights}`.
**This is the law model** and it pairs directly with the `Jurisdiction` block
found in `starmap.json` — base fine, stolen-goods limit, prison flag. **Together
they answer "who polices this, will they arrest me, and what does it cost."
Nobody publishes that.** Many `Name` values are `<= UNINITIALIZED =>`.

**`contracts/` — 5,108 files, 65 distinct top-level fields.** Beyond §1, the
ones never touched:

    HaulingOrders · MissionTokens · ObjectiveTokens · EntitySpawns
    CombatSummary (194) · NpcNames (81) · ItemCounts (146) · CrimeStat (510)
    Deadline (430) · Lifetime · Prerequisites (555) · RequiredMissions (57)
    JournalEntries (14) · BadgeAward (8) · RewardItems (59) · CompletionTags
    MaxPlayersPerInstance · AvailableInPrison · FailIfBecameCriminal
    NotForRelease · WorkInProgress · HiddenInMobiglas (15)

**`NotForRelease` and `WorkInProgress` are gates we should be honouring.** If
either is true, that contract is unshipped content. **Nothing in the project
filters on them, so any contract-derived page may currently be advertising
missions that do not exist in the live game.** Check this before WO-3 ships
blueprint source lists built from contracts.

---

# 6. THE OTHER TWO SOURCES

**`scunpacked.com`, 3 snapshots, newest `20260801T171748Z`:** only
`labels.json` (6.7 MB) and `ships.json` (501 KB). **Both are smaller than the
`scunpacked-data` equivalents** (11.4 MB and 90.7 MB). **This is the website's
trimmed API, not the raw dump.** Useful only as a cross-check on labels.
**Low value — do not spend time here.**

**`api.star-citizen.wiki`, newest `20260801T021731Z`:** 25+ `items_page_N.json`
at ~1 MB each, plus `game_version_default.json` and a 330 KB `_pull_summary`.
**Confirmed in earlier sessions to carry no 3D hardpoint coordinates for any
ship** — 0 of 61/74/123 ports on the three sampled. **Its value is Galactapedia
lore text and wiki-sourced stats, both of which sit under the same unresolved
text-rights question as CIG descriptions.** Parked, correctly.

---

# 7. `data-layer/processed` and `data-layer/raw`

**`processed/`:**

    blueprint_index.json        11,439,463 bytes   <- STILL 11.4 MB
    item_descriptions.json       2,151,854
    defaultProfile.plain.xml       218,387         <- moved in from Downloads
    keybinds_site.json             311,854         <- moved in from Downloads
    blueprints/ · hardpoints_by_type/

**The keybind extraction outputs are in the repo now.** That closes the
"two files in Downloads, C2 cannot write there" item from the 5 August handover.

**`blueprint_index.json` is still 11.4 MB at the top level.** `CURRENT-STATE.md`
says the split shipped and page p99 dropped from 63,706 to 3,129 bytes — the
per-page files are in `processed/blueprints/`. **Confirm whether the monolith is
still read by anything, or is a leftover that should be retired.** Under the
static ruling, a page that fetches it is the failure mode.

**`raw/`:** four files only — `arrow_api_raw.json`,
`constellation-aquila_api_raw.json`, `gladius_api_raw.json`,
`misc/viewers-manifest.json`. **The three-ship hardpoint research. Nothing new.**

---

# 8. REPO HYGIENE — three malformed directories

**Three top-level directories exist whose names are paths with the separators
stripped:**

    data-layerexports                         (empty)
    data-layerprocessedhardpoints_by_type     (empty)
    data-layerrawhardpoints/ship_specs.json   (one file)

**These are a path-construction bug — `"data-layer" + "raw" + "hardpoints"` with
no separator — that ran at least three times and created real directories.**

**Two are empty and are junk. The third contains `ship_specs.json`, which is
not obviously duplicated anywhere else and should be looked at before removal.**

**Worth finding the code that wrote them.** A path bug that silently creates
sibling directories instead of nested ones will do it again, and the next time
it may write data somewhere nothing reads it back from. **Rule 12 applies: a
path join that cannot produce a wrong directory is the fix, not deleting these
three.**

---

# 9. WHAT IS NOW GENUINELY MISSING — revised

**Shorter than this morning, and two entries moved:**

    1  stock levels / availability      nowhere, in any source
    2  runtime mission payouts          the ~46% with CalculatedReward true.
                                        The other ~50% are in the files - §1
    3  live shop reality vs recorded    what is actually on the shelf tonight
    4  price freshness and verification 66-day median; UEX gives coverage,
                                        not currency - §2
    5  refinery rates and yields        nowhere
    6  mission board contents by place  files give the pool, never the board
    7  item images                      zero of 7,728
    8  commodity prices                 MAYBE ALREADY AVAILABLE - §2.
                                        Make the call before assuming.

**Items 1, 3, 5 and 6 are the collector's real remaining justification, plus the
verification role in 4. That is a smaller and more defensible scope than rev 5
claimed, and it is still worth building.**

---

# 10. SUGGESTED ORDER — C1's call

1. **Call the UEX commodity endpoints.** §2. One script run against a key that
   already exists. **Blocks nothing, and it may close the project's largest
   stated gap. Do it before any more collector design.**
2. **Fix the window matcher to key on `StarCitizen.exe`.** §3. Before anyone
   else installs the grabber. Small, and it is a privacy defect.
3. **Re-run the `FixedReward` census locally.** §1. My 50/46 is a sample; the
   real number decides how much payout observation is worth.
4. **Filter `NotForRelease` and `WorkInProgress`** out of anything
   contract-derived. §5. Possibly already shipping unreleased content.
5. **Cross-check UEX terminal service flags against starmap `Amenities`.** §4.
   Two independent sources; publish the disagreements.
6. **Settle `blueprint_index.json`** — live dependency or leftover. §7.
7. **Find the path-join bug.** §8. Then remove the three directories.

---

# 11. NOT VERIFIED

- **The `FixedReward` / `CalculatedReward` split is a 25% sample**, not a census.
  A full scan timed out through the bridge.
- **Whether the UEX commodity endpoints return data for this account.** The
  documentation says they exist; nobody has called them. **Do not treat §2 as
  closed until a real 200 with rows lands.**
- **Whether `FixedReward.Amount` is the actual payout or a base before
  modifiers.** `BonusEligible`, `Max` and `ReputationBonus` sit beside it and
  suggest a bonus layer. **Publish it as "listed reward", not "what you get."**
- **What `Dismantle` on blueprints contains.** Never opened.
- **What the `Negative` arrays in `ProducesTags`/`ConsumesTags` mean.**
- **Whether `data-layerrawhardpoints/ship_specs.json` is duplicated elsewhere.**
- **`items/` (21,849 files) and `ships/` (316 files) as directories** were not
  compared against `items.json` and `ships.json`. **Assumed to be the same data
  split per file, not verified.**
- **`tags.json`** — 18,844 UUID→{name, parent_uuid}, examined 2 August and found
  to be the engine tag tree, not a consumer taxonomy. **Not re-examined.**
