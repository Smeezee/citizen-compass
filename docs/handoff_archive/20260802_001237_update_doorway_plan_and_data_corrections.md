# Doorway plan filed + four corrections to the front-end build plan — 2026-08-02, C2

Plan at `claude/plan-doorways-and-browse-layer.md` on claude.ai. **C2 wrote
nothing to the repository** — new write-authority rule, see
`claude/session-write-authority.md`. C1 owns repo writes now.

All figures below were computed by reading UEX snapshot `20260801T235530Z`
directly, not quoted from any manifest.

## The number that matters

**Only 2,798 of 7,728 items (36%) have a price anywhere.** The other 4,930:
1,313 are pledge/subscriber/concierge exclusives, 1,080 are liveries, and
**2,524 have no explanation in the data at all.**

Design consequence: exclusives get an honest non-price answer ("you can't buy
this in game"), liveries stay out of the main doorways, and the 2,524 get flat
wording — "no shop we know of stocks this" — because we do not know why.

## Four corrections to `claude/front-end-build-plan-2026-08-02.md`

I wrote that plan and did not check these against the data first.

1. **"823 shops" is wrong.** 823 is all terminals. Item-selling terminals: **479**.
   With at least one price row: **469**. Also wrong in `claude/state-2026-08-02.md`.
2. **"What it sells for" must not be a standing item-page section.** Only
   **171 items of 7,728 (2.2%)** have a sell price; only 248 of 23,734 price rows
   carry one. Make it a conditional line, not a section.
3. **"Prices a day or older render amber" would amber the whole site.** Median
   price age is **66 days**; 75% of rows exceed 30 days. Thresholds must come off
   the real distribution. Sleven to set them.
4. **Items have no images; shops do.** 0 of 7,728 items have a `screenshot`.
   **394 of 479 item terminals do.** Shop and place pages can be visual. Whether
   we may display UEX-hosted screenshots is unresolved and touches the 7 unread
   `fan_kit_compliance` warnings in `logs/pipeline_check_results_fallback.jsonl`.

## Other verified facts worth having

- **Item terminals exist in 3 star systems only** — Stanton 269, Pyro 139,
  Nyx 71. The snapshot holds 96 systems. 93 have no item terminal.
- **Breadcrumbs cannot assume a city.** Of 479 item terminals: space station 379,
  planet 340, city 65, outpost 39, moon 9. Build the breadcrumb from whichever
  location fields are non-null.
- **Terminals carry `game_version`** — a real last-verified-patch per shop, set
  on 429 of 479. Heavily stale: 3.24.2 (154), 4.0 (108), 3.24.1 (56).
- **UEX's category tree is unusable as site structure.** 4 of 100 categories
  return zero items; `Full Set`, `Container` and `Other` each appear twice;
  `Consumable #69` is empty while the real consumables sit at
  `Miscellaneous → Consumables #16`.
- **Best-covered data on the site is Utility+Technology** — 104 priced of 111
  (94%) — and **Clothing**, 1,055 of 1,809 (58%).

## Explicitly NOT verified — do not build on these

- What `is_available` / `is_available_live` / `is_visible` mean. Check UEX docs.
- Whether `id_parent` is specifically a colour-variant link. **Inferred, not
  verified.** The variant-grouping design depends on it.
- `tags.json` in the scunpacked snapshot was never opened. It may replace the
  proposed tag model outright — worth ten minutes before building.
- Licence/hotlink status of UEX terminal screenshots.
