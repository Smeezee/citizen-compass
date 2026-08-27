# FINDING — went through all 65 real collector captures, the auto log, and the settings file. One real, currently-live privacy leak found; the known crash confirmed against the actual data.

    from      C3 (Cowork), 2026-08-08
    for       Sleven + C1
    ask       "Will you actually check the collector? and go through all of the data."
    method    Staged and read every file directly — all 65 capture JSON sidecars,
              the full 12,935-line collector-auto.log, collector-selftest-results.txt,
              collector-settings.txt, README.md. PNG screenshots were NOT staged/reviewed
              this pass — noted as not-checked in §5.

---

## 1. What's actually in `captures/` right now

**65 real capture sidecars**, `20260806T031239Z_0001.json` through `20260808T011759Z_0065.json`.
Composition, read directly, not assumed:

- **Window captured:** 59 `starcitizen.exe` (real game captures), 6 `duckduckgo.exe`
  (sequences 1-6, all in the first 3 minutes on 2026-08-06 — a browser window
  matched during early self-test before the game was running, harmless), 1 `claude.exe`
  (sequence 7 — **already known and already documented as a positive proof**, see §4).
- **Capture method:** 61 `wgc`, 4 `dxgi`, 1 `gdi` — the WGC→DXGI→GDI fallback chain has
  actually fired in practice, not just in theory.
- **Trigger:** 16 `interval`, 15 `state_change:gamerules`, 15 `event:client_spawned`,
  6 `event:loading_screen`, 4 `once`, 3 `hotkey`, 7 with no trigger field (earliest captures,
  predate the field).
- **Install detected:** both `LIVE\Game.log` and `PTU\Game.log` paths appear across the set —
  install-following is exercised for real, not just claimed.
- **Capture duration:** 115ms-4,184ms, average 1.28s. Nothing pathological.
- **Variant:** 60 `master`, 6 `crew`.

**Sequence numbers are per-process-lifetime, not a stable ID — confirmed with a real
duplicate, not inferred.** Two different files are both named `..._0013.json`
(`20260807T010309Z_0013.json` and `20260807T010648Z_0013.json`, six minutes apart) because
the process restarted between them and its in-memory counter restarted at the same point.
This is the concrete artifact behind what `CURRENT-STATE.md` already describes ("capture
totals across that session run 0,1,2,3... and start over") — not a new bug, just the actual
file-level evidence of it. **Anything that ever indexes captures by sequence number alone
will collide; the filename's timestamp prefix is what actually makes each one unique.**

## 2. The known crash — cross-checked against the real log, one small precision correction

`CURRENT-STATE.md` already documents `fatal error: too many callback functions` firing
42 times on 2026-08-07, ~14m4s cadence, root-caused to `syscall.NewCallback` in
`winapi.go:EnumTopWindows`, fixed in source per CF-01/CF-02 but **not yet rebuilt/run on
Windows**. I counted independently from the raw log rather than trusting the existing
number: **42 occurrences, confirmed exactly.** Durations: 36 of the 42 at 14m4s, 3 at 14m2s,
1 at 14m0s, 1 at 17m28s, 1 at 27m42s (the metronome isn't perfectly uniform, but it's
consistently ~14 minutes). One small correction worth logging: the existing doc says the
cadence ran "from 08:34 to 20:50" — the actual first `too many callback functions` crash in
the log is timestamped **07:09:39**, about 85 minutes earlier than currently written. Doesn't
change the diagnosis or the fix, just the stated start time.

**This is not new information — it's independent confirmation that the existing account is
accurate**, which matters given Sleven's ask was to actually check, not take the doc's word
for it.

## 3. NEW — a real, currently-live leak: the numeric player ID is in 60% of today's captures

This is the one genuinely new finding from this pass, and it's a different code path than
the privacy work already done and already audited (`gamelog_mine.go` / `mine_gamelogs.py`,
which passed a real audit with a negative control — see `FINDING_gamelog-archive-is-a-mine.md`
§5). That audit covers the **separate mining pipeline's output files.** It does not cover
the live capture tool's own JSON sidecars, which is a different piece of code
(most likely inside `gamelog.go`'s location-resolution logic) writing directly into
`captures/*.json` right now.

**What's happening, read straight from the files:** every sidecar carries a `game_log` block.
When the location parser can confidently match a known pattern, `location` is filled and
`location_candidates` is absent — clean, matches the README's stated design ("location is
reported honestly or not at all"). **But when it can't match, the sidecar's
`game_log.location_candidates[]` array is populated with raw, unredacted lines copied
straight out of `Game.log`.** The README documents this as deliberate — it's meant to be the
"here's what the parser saw but couldn't confidently use" diagnostic, the intended path from
an UNVERIFIED pattern to a VERIFIED one.

**The problem: those raw lines aren't privacy-neutral.** Every one of the 39 sidecars (out of
65 — 60%) that has a `location_candidates` array contains, without exception, a line like:

    <Notice> <ResolveSpawnLocation Location Not Found> Could not resolve initial spawn
    location from spawning module for player id: [204354536218], setting spawn zone
    location zonehost to solar system fallback

**39 of 39 files with `location_candidates` carry this line — 100%, not occasional.** The
number in `player id: [...]` is a real, persistent numeric identifier — I found exactly two
distinct values across the whole dataset (`204354536218` on the earlier captures, sequences
1-24, then a clean switch to `855480118723` from sequence 31 onward, holding constant for
the rest of the set). That's consistent with a per-login/session identifier tied to whoever
was playing, not a throwaway value — and it is being written to disk, in plain text, in the
majority of today's real captures.

**Scope of the leak, checked directly, not assumed:** I scanned every sidecar for handle-shaped
tokens (`Name[digits]`, the shape other players' handles take in `Game.log`), IP addresses, and
chat-line markers. **None found.** The other ~1,131 raw lines dumped into `location_candidates`
across the 39 files are harmless asset-loading noise (`StatObjLoad` lines naming `.cgf` model
paths). **The leak is narrow and specific: one field, one root cause, one identifier type** —
but it's real, it's in the data on disk right now, and it doesn't go through the FORBIDDEN-list
stripping (`playerId`, `shopId`, `sessionId`, `shardId`, `nickname`, `geid`, etc.) that the
mining pipeline already applies to its own output. The standing project rule — "strip before
the file exists, not filter afterwards," and explicitly "`playerId` is stripped even though
it is Sleven's own" — isn't being met by this specific field in the live capture tool.

**This is a finding, not a fix — flagging for whoever picks up the collector's privacy work
next (already a listed blocker in `CURRENT-STATE.md`'s crew-build gate) rather than proposing
code.** The two options that occur to me, for Code to weigh: strip/hash any digit run following
`player id:` before the line is added to `location_candidates`, or apply the same
allow-list-only philosophy the miner uses (never copy a raw line at all, only named fields) to
whatever produces this array. Not deciding which — that's a design call, same as everything
else this project keeps out of C3's hands.

## 4. Confirmed, not new: the `claude.exe` capture (sequence 7)

Already documented in `claude/audit-collector-actual-state-2026-08-06.md` as a **positive**
result — proof the process-restriction guard correctly labels a non-game window when
`--allow-any-window` (master-only) is used: `"how_found": "NOT the game process (claude.exe)
- permitted only by --allow-any-window"`. Read the actual sidecar directly this pass and it
matches what's already on record exactly. No new concern here — just confirming the existing
account holds up against the real file.

## 5. What I did not check

- **The 65 PNG screenshots themselves were not staged or reviewed this pass** — only the
  JSON sidecars and the four top-level text files. `CURRENT-STATE.md` already flags
  "screenshots have no masking" as open; I have not independently verified what's actually
  visible in the images (chat overlays, other players' names on-screen, etc.) — that would
  need the PNGs staged separately, which I can do next if useful.
- Whether the two `player id` values (§3) correspond to two different real-world accounts or
  one account's ID changing between sessions — I only have the numbers, not a way to attribute
  them to anything further, and stopping there is the right line (an identifier is an
  identifier regardless of whose it is, per the standing rule).
- Did not open or modify anything in `citizen-collector/` — read-only, per the standing
  one-writer rule; C1/Code own that folder.

## Bottom line

Went through all of it: 65 real captures, the full auto log, the selftest results, the
settings file. The already-documented crash checks out exactly against the raw log (42
crashes, ~14 min cadence, one minor timestamp correction). The already-documented `claude.exe`
capture checks out as the known positive test, not a new concern. **The one thing this pass
surfaces that wasn't already on record: a real, currently-unstripped numeric player identifier
sitting in 60% of today's actual capture files**, via a code path the existing privacy audit
didn't cover because it audited a different pipeline. Worth folding into the same crew-build
privacy blocker already tracked in `CURRENT-STATE.md`, since it's the same class of problem
the existing blocker names, just a different place it's happening.
