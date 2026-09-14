# OPS — LIVE/PTU parse fold
**Date:** 2026-09-14  
**Status:** DONE

## What moved
- New shared module: `pkg/livever` (`citizencompass/pkg/livever`)
  - `ParseLiveVersions`, `ParseBuild`, `PatchGap`, `WithBuild`
  - Merged regexes: Alpha / LIVE / PTU literals + build numbers (from rsi-watcher livebuild) + Roundup + fail-loud Problems (from roadmap-watcher livever)
  - PTU none accepts `A,` / `ø` / `none` / `n/a`
- `roadmap-watcher/livever.go` → thin type/func shim
- `rsi-watcher/livebuild.go` → `ParseBuild` delegates; `FetchBuild` stays local
- `go.work` + both watchers' `go.mod` replace directives

## Tests
- `go test` pkg/livever — ok
- `go test` roadmap-watcher (LiveVersions/PatchGap/September) — ok
- `go test` rsi-watcher (ParseBuild) — ok
- `go build` rsi-watcher.exe — ok

## Note
Executor attempt failed (no Windows machineId). Ops finished on DESKTOP-TQEKVJB directly.