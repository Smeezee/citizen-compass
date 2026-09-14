# SC Brain migrate — compile existing CC knowledge (2026-09-14)

**Owner ask:** move known Star Citizen info into `sc-brain/` so one human-readable home exists.

## Rule (do not break the house)
| Do | Don't |
|---|---|
| File **compiled** cards, indexes, POINTERS into `sc-brain/` | Clone whole `data-layer/`, `sc-ships/`, tools, or site JSON |
| Leave extractors / watchers where they run | Break working paths by relocating tools |
| Prefer pointer + one CURRENT.md / INDEX entry | Duplicate megabytes of raw dumps |

## Who
- **Engineering** — pointers, sync scripts, build-truth/cig-firehose plumbing, indexes
- **Research** — human cards from FINDINGs / owner notes that are *verse facts* (historian, lore, pipeline, bugs, orgs)

## Phase 1 — wire what we already have (pointers + CURRENT)
1. `build-truth/hardpoints/POINTERS.md` → `data-layer/derived/hardpoint-transforms/` (~157 JSON) + holo fleet file
2. `build-truth/live/CURRENT.md` → root `LIVE.md` stamp
3. `build-truth/ptu/POINTERS.md` → PTU extract locations
4. `cig-firehose/roadmap/CURRENT.md` — confirm roadmap-watcher link
5. `cig-firehose/patches/POINTERS.md` → rsi-watcher
6. `economy/` — already has POINTERS.md
7. Refresh `sc-brain/INDEX.md`

## Phase 2 — Research FINDING harvest
From `docs/FINDING_*` (~101): tag verse-fact vs product/tool vs stale. Verse → sc-brain cards.

## Phase 3 — ships
Do **not** move `sc-ships/`. Add `build-truth/ships/POINTERS.md` only.

## Phase 4 — empty shelves for real
creators / bugs / orgs / pipeline / lore / pillars via acquisition plan.

## Done bar
Human can answer "where is X?" from `sc-brain/INDEX.md` without hunting the whole repo. Tools still run from old paths.
