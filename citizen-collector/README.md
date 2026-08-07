# citizen-collector — the grabber

**WO-COLLECT-01 rev 5 §5.1.** Single static Go binary, no installer, no
dependencies. One hotkey.

## What it does

Press the hotkey. It captures the Star Citizen window and writes two files into
`captures\`:

```
captures\20260806T031239Z_0001.png     the frame
captures\20260806T031239Z_0001.json    patch, build, UTC, location, sequence
```

Every press makes a noise — rising two-tone for a capture, a lower falling tone
for a failure. There is no silent operation, and a failure is audible precisely
because the operator is looking at a game, not at this console.

## What it deliberately does NOT do

**No OCR. No atlas. No vocabulary. No zones.** That is the reading half and it
is not in this binary.

## Why it exists

To answer one question, open since 2 August, that gates the entire reading half
of the collector:

> **Is the game font legible in a captured frame at Sleven's resolution?**

Everything here serves that. It is why the capture method is recorded in every
sidecar, why the display resolution is stamped on every capture, and why a blank
frame is a hard failure rather than a written file.

## Build

```
go build -o collector.exe .                      # crew build
go build -tags master -o collector-master.exe .  # master build (Sleven only)
```

`CGO_ENABLED=0` and no C compiler is required — every Win32/COM/WinRT call is
hand-dispatched through `syscall`. That is the price of "single static binary,
no installer", and it is why there is no `go.sum`.

> Built from the repo root you may need `GOWORK=off`, or use the `go.work` entry.

## Use

```
collector.exe                          hotkey mode, default Alt+F3
collector.exe --hotkey ctrl+alt+f10    different hotkey
collector.exe --once                   capture once and exit
collector.exe --list-windows           show what is capturable
collector.exe --selftest               internal checks, exit 0 = pass
collector.exe --backend dxgi           force one capture path
```

Master build only — these flags **do not exist** in `collector.exe`:

```
collector-master.exe --allow-any-window   lift the process restriction (bench testing)
collector-master.exe --window "Firefox"   title hint for choosing among windows
```

## What it will capture: StarCitizen.exe, and nothing else

Rev 5 §3. The target is chosen by **process**, never by title. A window title is
a string any program can set, and matching on it is how auto-detection once
selected this project's own terminal — titled "Build Star Citizen data pipeline
with three jobs" — and reported a confident match on the wrong window.

An intermediate fix used an exact-title test plus a denylist of known bystanders.
That was still wrong in kind: exact-title is still title-as-authority (a browser
tab can be titled anything), and **a denylist fails open** — it stops the
programs someone thought of and silently permits every one they did not.

Process matching is a whitelist and **fails closed**. Title is now a hint used
only to choose among that process's own windows; it can never widen the set to
another process.

Verified 2026-08-05, five checks:

| | |
|---|---|
| `collector.exe --allow-any-window` | exit 2 — *flag provided but not defined* |
| `collector.exe --window ...` | exit 2 — not defined either |
| `collector.exe --once` with a browser titled "Citizen Compass" on screen | refuses, naming all 8 refused processes |
| `collector-master.exe --allow-any-window --window Claude` | exit 0, captures |
| `collector-master.exe --window Claude` (no flag) | refuses the same window |

The bench flags are not disabled in the crew build — they are **absent**.
`registerBenchFlags()` in `variant_crew.go` registers nothing, so there is no
code path in that binary that can set `allowAny`. A flag that exists but
defaults to false can be re-enabled by a later edit or a config file; one that
is not compiled in cannot.

A hotkey with no modifier is rejected: `RegisterHotKey` is global, so a bare F9
would be swallowed system-wide — including inside the game.

## The capture chain

Tried in order, first one that yields a **non-blank** frame wins:

| # | Backend | Notes |
|---|---------|-------|
| 1 | `wgc` | Windows.Graphics.Capture. Targets the *window*. Survives occlusion and fullscreen. The Win11 yellow capture border is suppressed. |
| 2 | `dxgi` | Desktop Duplication, cropped to the window rect. **Captures what is on screen** — an occluded window yields whatever is in front of it. Fine for a fullscreen game, wrong for a background window. |
| 3 | `gdi` | `PrintWindow`/`BitBlt`. Not in the work order; present because it still works when the other two are blocked. Usually returns black against a hardware-accelerated game. |

### Success is decided by the pixels, not the return code

Every one of these APIs can return `S_OK` and hand back a fully black buffer. A
backend only counts as having worked if `looksBlank` says the frame carries
content; otherwise the chain moves on and the error names what each backend
actually did.

`--selftest` proves that detector **in both directions** — it must reject a
uniform frame and accept a patterned one. A check that cannot fail is not a
check (hard rule 12).

## Verified, 2026-08-05, 1920×1080

All three backends were run against a real window and the images inspected —
not merely checked for exit 0:

| Backend | Result |
|---|---|
| `wgc` | 1920×1032, text crisp and fully legible, ~436 ms |
| `dxgi` | 1920×1040 cropped from a 1920×1080 output, ~312 ms |
| `gdi` | 1936×1048 via `PrintWindow`, ~115 ms |

Patch `4.9.188.23497` and build `12344265` were read correctly from the real
`Game.log` in every case.

**This does not yet answer the legibility question**, because Star Citizen was
not running. The capture path is proven; the game's own font at 1080p has not
been photographed yet. That needs one press with the game open.

## The sidecar

The five fields the work order asks for — `sequence`, `utc`, `patch`, `build`,
`location` — plus provenance: which backend produced the image, how the window
was identified, the window rect, the display size, and the parse state of every
`Game.log` field.

### Location is reported honestly or not at all

`Game.log` patterns are split into **VERIFIED** (matched against a real log on
this machine) and **UNVERIFIED** (plausible, unconfirmed). Anything from an
unverified pattern carries `location_pattern_verified: false`.

The sample log available never left the main menu, so **there is no in-world
location line to verify an in-world pattern against.** When nothing matches,
`location` is `null` and `location_reason` says why — it is never filled with a
plausible-looking default.

To close the gap: capture once while actually in the PU and read
`location_candidates[]`, which carries the raw lines the parser found
interesting but could not confidently parse. That is the intended route from
UNVERIFIED to VERIFIED.

Two defects found by running this against the real log, both now fixed:

- An unverified pattern scraped `state` out of `taskname="ResolveSpawnLocation"
  state=eCVS_UnstowPlayer(14)` by walking across a field boundary. Patterns now
  match quoted values only, and log-structure tokens are rejected outright.
- An unverified guess was tested **before** the verified answer and overwrote it.
  A guess may now only fill a gap, never displace something known.

## Two builds from one source

Per the rev 5 addendum (2026-08-06): `collector.exe` is capture/read/export;
`collector-master.exe` adds calibration, zone tuning, the review pen and
*Generate crew package*. Same codebase, one build tag — `variant_crew.go` and
`variant_master.go` are the entire difference.

**The master features do not exist yet.** They are downstream of the reading
half, and *Generate crew package* is blocked on its own payload: of the seven
files it must assemble, only `names.dat` is buildable today. `atlas\`,
`zones.json` and `profiles.json` all come from calibration. A generator written
now would assert against a payload it cannot produce and verify nothing while
reporting PASS.

## Files

| File | |
|---|---|
| `main.go` | hotkey loop, window identification, sidecar, `--selftest` |
| `capture.go` | frame type, fallback chain, blank detection, crop |
| `capture_wgc.go` | Windows.Graphics.Capture (WinRT) |
| `capture_dxgi.go` | DXGI Desktop Duplication |
| `capture_gdi.go` | `PrintWindow`/`BitBlt` |
| `gamelog.go` | `Game.log` parsing, verified/unverified split |
| `winapi.go` | Win32/COM/WinRT plumbing |
| `hotkey.go` | hotkey string parsing |
| `variant_*.go` | the crew/master build flag |
