# Update: Job 4 complete — collector --auto mode (2026-08-06)

`citizen-collector` gains `--auto`. Builds clean, `--selftest` passes, and every
new check has been **seen to fail** before being trusted.

## What was added

New files `auto.go` and `auto_selftest.go`; `main.go` and `winapi.go` amended.

- **Tails Game.log**, polling every 2s (`--poll`). Reads only APPENDED bytes,
  carrying a partial trailing line to the next poll so a line split across two
  polls is not parsed as two broken ones.
- **Captures on state change**, reusing the parsers already in `gamelog.go` —
  `reGameRules`, `reMap`, `reLoadingScreen`, and the `OnClientSpawned-zone`
  pattern, which is looked up **by name** so a rename in `gamelog.go` breaks
  loudly instead of silently binding to nothing.
  - state: `gamerules`, `map`, `zone`, `location`
  - events: `loading_screen`, `client_spawned`
- **Debounce** 3s (`--debounce`).
- **Interval fallback** every N minutes with no change, default 10, `0` = off
  (`--interval`).
- **Window gate**: captures only while a `StarCitizen.exe` window exists.
- **Trigger recorded in every sidecar**, e.g.
  `{"kind":"state_change","field":"gamerules","from":"SC_Frontend","to":"SC_Default"}`.
  Interval captures say `{"kind":"interval","minutes":10}`; manual ones now say
  `hotkey` or `once` rather than nothing.
- **No console**: `--auto` hides the console window and logs to
  `collector-auto.log` next to the exe. Every recoverable problem is logged and
  the loop continues, so it survives being left running.
- **Settings** from `collector-settings.txt` next to the exe, written with
  commented defaults on first run and never overwritten. Command-line flags win
  over the file.

No OCR, no database routing, no ZIP packager — as instructed.

## Three design points worth recording

1. **The first poll never fires.** Game.log already holds a whole session when
   the tool starts; feeding that backlog through the detector would fire a
   burst of captures for state changes that happened before launch, stamped
   now. The first read primes silently. Same on log rotation — a new session
   truncates Game.log, and that re-primes rather than replaying.
2. **`--allow-any-window` cannot combine with `--auto`.** The flag only exists
   in the master build at all, but a master build left running unattended with
   the process restriction lifted would photograph whatever was on screen for
   hours into a corpus meant to be shared. The combination is refused at
   startup, and the auto loop passes a literal `false` — there is no variable
   to get wrong.
3. **`doCapture` takes a `Trigger`, not a `*Trigger`,** and refuses an empty
   `Kind`. A capture with no stated reason is a bug, so it cannot be written.

## Checks — and the mutation testing that proves them

`--selftest` gained 16 checks. The negative control runs **first**: a synthetic
log with no state changes must produce **exactly zero** triggers, and if it
fires the whole group is reported **VOID** (exit 2) rather than as a set of
passes.

Known sequence asserts count **and** exact reasons:

    event:loading_screen "Frontend_Main : SC_Frontend"
    state_change:gamerules "SC_Frontend"->"SC_Default"
    state_change:map "megamap"->"pyro"
    state_change:zone ""->"Stanton_1_Hurston"
    event:client_spawned "Stanton_1_Hurston"
    event:client_spawned "Stanton_1_Hurston"

**All checks passed first time, so per rule 12 I broke each one deliberately
and confirmed it failed.** Six mutations, all caught:

| mutation | caught by |
|---|---|
| tailer starts primed | `priming fires nothing` — 2 triggers from backlog |
| detector fires on every line | **NEGATIVE CONTROL fired -> VOID, exit 2** |
| debounce ignored | `debounce holds to 1 per 3s` |
| `interval 0` no longer means off | `interval 0 never fires` |
| BOM no longer stripped | `settings reads first line despite BOM` |
| zone parser renamed in `gamelog.go` | `shared zone parser found` |

**Two of those mutations initially escaped, and both revealed a weak test:**

- The BOM fixture had a **comment** on line 1, so an unstripped BOM corrupted a
  comment and changed nothing. The check was passing vacuously. Fixture now
  puts a live setting first, and the check fails properly.
- The zone-parser mutation was applied to the call site in `auto.go` rather
  than to the pattern name in `gamelog.go`, so the selftest's own lookup was
  untouched. Retargeted at the real thing.

Source restored byte-for-byte from a pristine copy afterwards and the baseline
re-confirmed clean; no mutation residue remains.

## Not done in this job

The `--auto` loop has not been exercised against a **live** Star Citizen
session — the game is not running. Every trigger path is proven against a
synthetic log, but the window gate and the capture path under real conditions
are untested. That is a real gap and I am stating it rather than implying
coverage I do not have.
