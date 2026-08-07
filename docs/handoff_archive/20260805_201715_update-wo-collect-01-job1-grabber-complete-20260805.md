# Update — job 1 (the grabber) built and verified; legibility question still open

**When:** 2026-08-05

WO-COLLECT-01 rev 5 §5.1. `citizen-collector/` — single static Go binary, no
installer, no external modules. Builds clean, `go vet` clean, both variants.

## Built

`main.go`, `capture.go`, `capture_wgc.go`, `capture_dxgi.go`, `capture_gdi.go`,
`gamelog.go`, `winapi.go`, `hotkey.go`, `variant_crew.go`, `variant_master.go`,
`testimage.go`, `README.md`, `.gitignore`.

Hotkey (default Ctrl+Alt+F9) → capture the SC window → `captures\<utc>_<seq>.png`
+ sidecar `.json` with the five required fields (patch, build, UTC, location,
sequence) plus provenance. Rising two-tone on success, lower falling tone on
failure — **failure is audible too**, since a silent failed press is
indistinguishable from a press that never registered.

**No OCR, no atlas, no vocabulary, no zones** — as scoped.

`CGO_ENABLED=0` with no C compiler on this machine, so C++/WinRT was
unavailable and every Win32/COM/WinRT call is hand-dispatched through
`syscall.SyscallN`. Verified up front that `SyscallN`, `RoInitialize`, `d3d11`
and `dxgi` all work before writing the plumbing.

## Verified by running it, not by reading it

All three backends run against a real window, **images opened and inspected**:

| Backend | Result |
|---|---|
| `wgc` | 1920×1032, text crisp and fully legible, ~436 ms. Win11 yellow capture border successfully suppressed. |
| `dxgi` | 1920×1040 cropped from a 1920×1080 output, ~312 ms |
| `gdi` | 1936×1048 via `PrintWindow(PW_RENDERFULLCONTENT)`, ~115 ms |

Patch `4.9.188.23497` and build `12344265` read correctly from the real
`Game.log` every time — matching the patch the work order states.

**Gates proven able to fail, per hard rule 12:**

- Blank-frame detector proven in **both** directions by `--selftest`: rejects a
  uniform frame, accepts a patterned one.
- Hotkey registration proven real by running two instances — the second is
  refused with "Hot key is already registered", a different combo succeeds.
- Auto-detection proven to refuse when SC is absent, while `--window` still
  works.
- Bogus model path in the earlier deploy check returned 404, so 200s were real.

## Three defects found only by running it

1. **`location: "state"`.** An unverified pattern walked across a field boundary
   in `taskname="ResolveSpawnLocation" state=eCVS_UnstowPlayer(14)` and reported
   the player's location as `state`. Patterns now match quoted values only, plus
   a reject-list of log-structure tokens.
2. **A guess was overwriting a known answer.** The unverified branch was tested
   *before* the verified one, so a correct `SC_Frontend` "main menu" reading was
   being displaced by that garbage. A guess may now only fill a gap.
3. **Auto-detection selected the wrong window.** The title hint was a substring
   test, so it matched *this session's own terminal* — titled "Build Star Citizen
   data pipeline with three jobs" — and reported a confident match on a
   bystander. Now an exact-title test plus a denylist of shells, browsers and
   chat clients. `--window` is never second-guessed, so testing still works.

## THE QUESTION IS NOT YET ANSWERED — this is the honest status

The grabber exists and the capture path is proven. **But Star Citizen was not
running, so the game's own font at 1080p has not been photographed.** The open
question — *is the game font legible in a captured frame at Sleven's
resolution* — needs exactly one press with the game open.

Everything is in place for that: run `collector.exe`, alt-tab into the game,
press Ctrl+Alt+F9, and look at the PNG. The display here is **1920×1080**, which
is the harder case and the one the question is really about.

Reporting the tool as done and the question as still open, rather than implying
the build answered it.

## Notes

- `go.work` gained `./citizen-collector` (additive). Without it, builds from the
  repo root need `GOWORK=off`.
- `captures/` and the two `.exe` outputs are gitignored — the addendum forbids
  captures content leaving the machine, and the same rule applies to the repo.
- Test-run logs moved to `_to_delete/collector-test-logs-20260805/` per hard
  rule 1, not deleted.
- **Nothing staged or committed.** Awaiting go-ahead per hard rule 2.

**Next:** job 2 — the starmap join + route cost table.
