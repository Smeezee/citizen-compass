# SC Brain index

Ask / find surface stub. Grow this as shelves fill.

## Quick jumps
- CIG firehose → `cig-firehose/`
- Build truth (LIVE/PTU) → `build-truth/`
- Economy → `economy/`
- Creator claims → `creators/claims/`
- Bugs / workarounds → `bugs/`
- Orgs → `orgs/`
- Pipeline board → `pipeline/{announced,teased,speculated}/`
- Historian → `historian/`
- Lore / SQ42 → `lore/` (SQ42 is spoiler-gated)
- Fresh pillars → `pillars/`
- Soft community → `community/`
- Watcher state / indexes → `plumbing/`

## How agents should file
1. Normalize outside (or in tool output dirs)
2. Write the **compiled** note/JSON under the matching shelf
3. Add one line here (or under `plumbing/indexes/`) when a new standing series starts
4. Creators: entities, numbers, patch, stance, link+timestamp — **no verbatim**

## Status
Folder map landed 2026-09-14. Collection automation still to wire (plan order: local RSI watcher next).

## Maps for steps 2–8
- [[_meta/ACQUISITION-MAPS_steps-2-through-8-2026-09-14]] — flushed Architecture maps (schemas, shelves, done bars)
## Local ask (free)
```
python sc-brain/plumbing/ask_sc_brain.py shelves
python sc-brain/plumbing/ask_sc_brain.py recent
python sc-brain/plumbing/ask_sc_brain.py find hardpoint
```