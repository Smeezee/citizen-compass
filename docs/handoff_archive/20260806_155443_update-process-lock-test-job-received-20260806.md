# Update: process-lock refusal test ordered (2026-08-06)

Received mid-session, logged on arrival before starting.

**The finding is correct and I accept it.** `--selftest` currently has four
checks — captures dir writable, blank detector in both directions, png encode,
win32 reachable. **None of them touch the process gate.** The gate at
`main.go:119` and the second guard at `main.go:187` read correctly, but reading
is not testing, and there is no artifact on disk showing a refusal was ever
exercised.

Capture 0007 is not evidence, also correct: it was taken **with**
`--allow-any-window`, so it proves the door opens when unlocked, not that it
stays shut when it is not.

Four checks to add to `--selftest`:

1. **Positive control** — `findGameWindow(allowAny=false)` must REFUSE a window
   titled "Star Citizen" whose process is not `StarCitizen.exe`. Create the
   condition rather than hoping for it. The error must NAME the refused process.
2. **Negative control** — the same call must ACCEPT a window whose process IS
   the game. Fake it at the `isGameProcess` boundary, without stubbing out the
   gate itself.
3. **The second guard** — `main.go:187` must be shown to fire independently.
   Two layers means two tests.
4. **Crew variant** — the crew build must be unable to set `allowAny` at all,
   not merely refuse it.

Then run `--selftest` on both builds and report output verbatim, marking which
checks are new. Any check that passes first time without having been seen to
fail gets broken deliberately, confirmed failing, and put back.

**No crew build is to be built, packaged or distributed until all four pass.**

## Sequencing

Job 4 (`--auto`) is in flight: `auto.go` and `auto_selftest.go` are written, and
`main.go` wiring is next. Both jobs modify `selftest()`, so I am finishing and
filing Job 4's wiring first rather than interleaving two sets of edits into the
same function. Starting this immediately after — nothing else comes between.
