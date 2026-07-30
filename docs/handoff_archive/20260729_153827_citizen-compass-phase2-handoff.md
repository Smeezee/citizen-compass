# Citizen Compass — Phase 2 Handoff
## The New Infrastructure Plan

**Date:** 2026-07-24
**Current status:** Phase 1 complete. v0.2.7 is live at https://citizencompass.netlify.app/
**Phase 1 deliverable:** Self-contained HTML ship purchase matrix — 232 ships, 229 verified RSI buy-links, alphabetical order, category search, mobile-friendly, clean language, no AI fingerprints.

---

## Why Phase 2 Exists

The current HTML/Python setup is at its ceiling. It handles the ship matrix well. It cannot handle 50,000–100,000+ data entries across ships, components, gear, loot locations, and blueprints without becoming unmaintainable. Phase 2 builds infrastructure that is future-proofed for the long run — designed today to handle the scale Star Citizen will eventually reach.

---

## The Target Stack

| Layer | Technology | Why |
|---|---|---|
| Database | PostgreSQL | Production-grade, free, handles millions of rows, proper querying |
| Backend | Python + FastAPI | Python already used in this project; FastAPI serves data via API |
| Frontend | HTML/CSS/JavaScript | Real web app querying live data, still mobile-friendly |
| Hosting (eventual) | VPS — Hetzner or DigitalOcean | ~$4-6/month, runs the whole stack |
| Dev environment | Local (Sleven's machine, Windows 11) | Build and test locally first |

---

## Database Schema (planned tables)

Every table carries `last_verified_patch` — the patch version when that row was last confirmed accurate. Anything unverified in the current patch gets flagged on the front end. This is how 100% accuracy is maintained at scale.

**Core reference tables:**
- `patches` — version history (4.9.0, 4.10, etc.)
- `systems` — Stanton, Pyro, Nyx (and future systems)
- `manufacturers` — the 18 manufacturers

**Ship data (migrated from Phase 1):**
- `ships` — every ship, all attributes, flyable status, role/category
- `dealers` — every in-game location that sells anything
- `ship_dealer_listings` — ship × dealer × aUEC price
- `pledge_links` — 229 verified RSI store URLs

**Components:**
- `components` — every ship component (weapons, shields, drives, coolers, power plants, etc.) with size, grade, type, manufacturer
- `component_dealer_listings` — component × location × aUEC price × system

**FPS Gear:**
- `fps_gear` — armor sets, personal weapons, utility items
- `gear_dealer_listings` — gear × location × price

**Loot & Farm:**
- `loot_sources` — missions, enemy types, specific locations that drop gear
- `gear_loot_links` — connects gear to how/where it drops

**Blueprints:**
- `blueprints` — what exists, what it crafts, required materials, unlock method
- `blueprint_sources` — where/how blueprints are obtained

---

## Build Order

**Step 1** — Install PostgreSQL on Sleven's machine (one-time setup, ~10 min)
**Step 2** — Build the database schema (I write this, Sleven runs it)
**Step 3** — Migrate Phase 1 ship data into PostgreSQL (Python migration script, I write it)
**Step 4** — Build FastAPI backend — serves ship data via API
**Step 5** — Rebuild frontend as a real web app querying the API (still looks like Citizen Compass, just powered by a database now)
**Step 6** — Add components as the first new data layer
**Step 7** — Add FPS gear and loot locations
**Step 8** — Add blueprints
**Step 9** — When ready: deploy to VPS, point citizencompass.netlify.app or a custom domain at it

Each step is independently functional. The ship matrix works after Step 5 and just gets richer from there.

---

## Division of Labor

**Sleven's side:**
- Installing software (exact commands provided, copy/paste)
- Data gathering — URLs, prices, component info (same as Phase 1)
- Flagging inaccuracies when something doesn't match what's in-game
- Making decisions about scope and presentation

**Claude's side:**
- Every line of code
- Architecture decisions
- Migration scripts
- Debugging
- Plain-English explanations at every step

---

## Accuracy Standard

Sleven's stated goal: **100% accuracy on confirmed data, no guesswork.**

Enforced by:
- Every data row carries `last_verified_patch`
- Front end flags anything not verified in the current patch
- Nothing gets added without a confirmed source (RSI store, CStone live terminal data, in-game verification)
- Conflicts are flagged rather than silently resolved

---

## Phase 1 Files (preserved, used for migration)

- `/home/claude/sc_ships/data.py` — single source of truth for all ship data
- `/home/claude/sc_ships/build_html.py` — HTML generator
- `/home/claude/sc_ships/build.py` — xlsx generator (retired but preserved)
- Live site: https://citizencompass.netlify.app/
- Current version: v0.2.7

---

## First Action Required from Sleven

Run this in Command Prompt (Windows key + R → cmd → Enter):

```
python --version
```

Report back what it says. That determines whether we start immediately or spend 5 minutes installing Python first.

