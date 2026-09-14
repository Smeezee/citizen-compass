# SC Brain index

Ask / find surface stub. Grow this as shelves fill.

## Quick jumps
- CIG firehose â†’ `cig-firehose/`
- Build truth (LIVE/PTU) â†’ `build-truth/`
- Economy â†’ `economy/`
- Creator claims â†’ `creators/claims/`
- Bugs / workarounds â†’ `bugs/`
- Orgs â†’ `orgs/`
- Pipeline board â†’ `pipeline/{announced,teased,speculated}/`
- Historian â†’ `historian/`
- Lore / SQ42 â†’ `lore/` (SQ42 is spoiler-gated)
- Fresh pillars â†’ `pillars/`
- Soft community â†’ `community/`
- Watcher state / indexes â†’ `plumbing/`

## How agents should file
1. Normalize outside (or in tool output dirs)
2. Write the **compiled** note/JSON under the matching shelf
3. Add one line here (or under `plumbing/indexes/`) when a new standing series starts
4. Creators: entities, numbers, patch, stance, link+timestamp â€” **no verbatim**

## Historian seed (2026-09-14)
- Port Olisar → Seraphim — `historian/locations/port-olisar-to-seraphim-2023-09-19.md`
- Aurora Mk I sunset — `historian/pledges/aurora-mk-i-sunset-2026-03-25.md`

## Status
Folder map landed 2026-09-14. Collection automation still to wire (plan order: local RSI watcher next).

## Maps for steps 2â€“8
- [[_meta/ACQUISITION-MAPS_steps-2-through-8-2026-09-14]] â€” flushed Architecture maps (schemas, shelves, done bars)
## Local ask (free)
```
python sc-brain/plumbing/ask_sc_brain.py shelves
python sc-brain/plumbing/ask_sc_brain.py recent
python sc-brain/plumbing/ask_sc_brain.py find hardpoint
```

## Migrate status (2026-09-14)
- Plan: [[_meta/MIGRATE_existing-knowledge-2026-09-14]]
- Phase 1 pointers: hardpoints, LIVE, patches, ships
- Phase 2: FINDING harvest (Research)
