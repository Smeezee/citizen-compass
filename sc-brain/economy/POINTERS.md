# Economy shelf — pointers to existing tools

Do not scrape Erkul/SPViewer. Call what we already have; file **compiled** summaries here.

| Need | Call (existing) | File compiled result under |
|---|---|---|
| UEX commodities/prices | `scripts/external_sources/uex_corp.py` + `import_uex_*` | `sc-brain/economy/uex/` |
| Wiki ship fields | `tools/import_wiki_ship_fields.py`, `scripts/external_sources/api_star_citizen_wiki.py` | `sc-brain/economy/` or build-truth as fits |
| scunpacked snapshots | `scripts/external_sources/scunpacked_com.py` + gates | `sc-brain/economy/shops/` (pointer + date) |
| Fleetyards models | `import_fleetyards_models.py` / sweep | pointer note here; binaries stay in data-layer |
| Pledge store | CIC price-sweep (when local forever-automation exists) | `sc-brain/economy/pledge-store/` |

## Done bar
Tracked + scheduled/automated + findable via `ask_sc_brain.py` / INDEX.
