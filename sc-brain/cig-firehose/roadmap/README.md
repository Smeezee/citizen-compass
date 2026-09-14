# Roadmap shelf (pointer)

Live roadmap polling is owned by **`roadmap-watcher/`** (do not rebuild here).

## Where the data is today
- State: `roadmap-watcher/roadmap-watcher-state.json`
- History: `roadmap-watcher/roadmap-watcher-history.jsonl`
- Settings: `roadmap-watcher/roadmap-watcher-settings.json`

## SC Brain role
Compiled “easy to get” summaries land here when the sync helper runs:

```text
python sc-brain/plumbing/sync_roadmap_pointer.py
```

That writes `CURRENT.md` in this folder from the watcher state (no network).
