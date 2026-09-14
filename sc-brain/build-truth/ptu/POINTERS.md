# PTU — pointers (not a clone)

Where PTU / build-line truth already lives in Citizen Compass. Tools stay put.

## Primary
- RSI board description (LIVE + PTU) via `roadmap-watcher` / `rsi-watcher` using shared `pkg/livever`
- Live state after a good run: `sc-brain/plumbing/state/rsi-watcher-state.json` fields `live`, `ptu`, `build_since`
- Cards on change: `sc-brain/cig-firehose/patches/` (see sibling POINTERS)

## Related
- `sc-brain/build-truth/live/CURRENT.md` — LIVE stamp pointer
- `sc-brain/cig-firehose/roadmap/CURRENT.md` — roadmap watcher link

## Do not
Move `data-layer/` or relocate watcher binaries here.