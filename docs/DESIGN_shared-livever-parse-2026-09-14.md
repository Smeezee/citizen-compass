# DESIGN â€” Shared LIVE/PTU parse (roadmap-watcher â†” rsi-watcher)
**Date:** 2026-09-14  
**Status:** DONE 2026-09-14 — see docs/OPS_livever-fold-2026-09-14.md

## Why
`roadmap-watcher/livever.go` and `rsi-watcher/livebuild.go` are stated twins (same board description field). Two `package main` trees cannot import each other. Drift already started (Live regex shapes differ slightly).

## Proposed fold (later, one package)
- New shared module e.g. `pkg/rsiboard` or `pkg/livever` with `ParseLiveVersions` / build helpers + tests.
- Both watchers import it; delete duplicate files.
- Keep fail-loud + A,/none semantics.

## Collision
Code owns open edits on `roadmap-watcher/` and `rsi-watcher/` sources. Ops will **Mailroom Build** once and wait for a free lane â€” not steal mid-edit.

## Until then
PARTIAL: twins documented; no code move this pass.