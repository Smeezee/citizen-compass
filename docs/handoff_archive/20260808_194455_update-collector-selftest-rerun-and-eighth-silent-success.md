# Update — collector selftest re-run; an eighth silent success found and closed

Closes open item #1 from the 08-08→08-09 handoff ("re-run `--selftest` and read
the tail"). It was worth re-running.

## The headline

**350 checks pass, 0 fail, exit 0.** All 14 of the previous session's fixes hold.
`go vet` and `go build` are clean.

**But the run also exposed the eighth silent-success instance on this project,
in the selftest itself — and this one was found by re-running a test rather than
by anybody noticing.**

## What happened, in order

1. Built from the current tree and ran `--selftest`: **PASS, 350 ok, exit 0.**
2. Per rule 12, did not trust that. Planted a deliberately-failing check inside
   the `check` closure, rebuilt, ran: reported `[FAIL]`, printed
   `selftest FAIL (1 checks failed)`, **exit code 1**. The failure path is
   proven end-to-end, including that `os.Exit(code)` at `main.go:980` carries
   it out of the process. Plant reverted; `main.go` md5 verified identical to
   before (`cd6a754a…`).
3. Re-ran the identical, hash-verified source — and got **2 failures**.

## The intermittent failure

`gamelog_selftest.go` — "staleness warning fires on a dead log" and "staleness
warning names the fix" fail intermittently. Measured rate: **1 run in 5**.

It is not environmental. `gameAlive` is stubbed to always return nil, the clock
is injected and mutexed, and `waitFor` is a sound 4-second poll against a 1s
real-time ticker. The miss appears to be a real-time race under machine load —
the flake landed on the run immediately following a compile. **Cause not
proven, so not claimed.** Left open below.

## The part that actually matters

When those two checks fail, the two checks *after* them still report **`[ok]`** —
and they are measuring nothing.

Both compare a count against `firstCount`:

- healthy run: `still 1 warning(s) after further polls` → `[ok]`
- flaked run:  `still 0 warning(s) after further polls` → **`[ok]`**

`firstCount` is captured *after* the warning was supposed to fire. If it never
fired, `firstCount` is 0, and "the count did not go up" is trivially true.
`0 == 0` passes. So the exact moment the staleness feature is most suspect is
the moment its two negative controls stop being able to fail — they go green
*because* the thing ahead of them broke.

This is the same shape as the six earlier cases and as the one the last session
hit ("one of them had blinded a negative control"), and it is the second time
that specific pattern has appeared in this file's neighbourhood.

**Fixed.** Both checks are now gated on there being something to count, and
report **NOT PERFORMED** — as failures, per rule 11 — rather than passing:

```
[FAIL] staleness warns once per stall, not every poll
       NOT PERFORMED - no warning ever fired, so there is no count to hold steady
[FAIL] a log that starts growing again is NOT reported stale
       NOT PERFORMED - no warning ever fired, so a cleared warning cannot be observed
```

**Proven by behaviour, not by reading it.** Suppressed the staleness warning on
demand (advanced the fake clock well short of the threshold), rebuilt, ran, and
confirmed both lines flipped from `[ok]` to the NOT PERFORMED failures above.
Plant reverted; final `diff` against the pre-change file is exactly the 14 added
lines and nothing else, `gofmt` clean.

Worth recording: the first attempt at this edit rewrote the whole file from LF
to CRLF, because Python's text-mode write translates newlines on Windows.
`gofmt -l` caught it — every line showed as changed. Redone with `newline=''`.
Same family as rule 15: the default is wrong on this platform, silently.

## Changed

- `citizen-collector/gamelog_selftest.go` — +14 lines, the gate above. Test-only;
  no shipped behaviour changes.
- `citizen-collector/selftest-rerun-20260808.txt` — the passing transcript.
- `_to_delete/collector_selftest_build_20260808/` — the throwaway build exe,
  moved aside per rule 1, not deleted.

`collector.exe` and `collector-master.exe` were **deliberately not rebuilt**, so
they still match `citizen-collector-0.2.0.zip`. The change is test-only, so the
shipped binaries are unaffected either way.

Nothing committed — no go-ahead, per rule 2.

## Two things the handoff asserts that are not true on disk

1. **The two documents it names as authoritative do not exist.** There is no
   `claude/` directory in this repo, and neither
   `RULING_collector-drops-the-bundled-browser-2026-08-08.md` nor
   `FINDING_selftest-first-run-2026-08-08.md` appears anywhere in the tree
   (docs land in `docs/`). The reasoning behind the browser-fallback design and
   the original 14-failure finding is currently recorded **only** in the handoff
   prose. Reported, not reconstructed.
2. It says the suite is "~190 checks now". It is **350**.

## Open, unchanged or newly raised

- **NEW: the staleness flake, ~1 in 5.** Now fails honestly instead of silently,
  but the race itself is unfixed. Likely a too-tight 4s `waitFor` against a 1s
  ticker under load; raising it is the obvious candidate, **not applied because
  the cause is not proven** and a timeout bump is exactly how a real race gets
  papered over.
- **Item #2 (publish 0.2.0) is blocked: `gh` is not on PATH.** `make-release.ps1`
  needs it. Nothing can self-update until this is resolved.
- Items #3–#7 from the handoff untouched: browser fallback never executed, the
  shortcut COM path never executed on a fresh machine, ~750 MB of dead zips and
  `webview2-runtime/`, the 7 junk PNGs, and the collector→database ingest.
