# Update — job 1 of 4: window matcher now process-only, proven in both directions

**When:** 2026-08-05

rev 5 §3 defect. `citizen-collector` now captures **`StarCitizen.exe` and
nothing else**. Both variants build clean, `go vet` clean under both tags.

## What changed

**Title is no longer authority.** The gate is the process image name, checked
before any title is consulted. Title survives only as a *hint* for choosing
among that process's own windows — it can narrow the candidate set, never widen
it to another process.

**My earlier fix was replaced, not kept.** I had tightened the title test to
exact-match plus a denylist of bystanders. That was wrong in kind and the new
instruction is right:

- exact-title is **still title-as-authority** — any window can be titled "Star
  Citizen", a browser tab included;
- a denylist **fails open**. It stops the programs someone thought of and
  silently permits every one they did not.

Process matching is a whitelist and **fails closed**: an unknown program is
refused by default rather than captured by default.

**`--allow-any-window` is absent from the crew build, not disabled.**
`registerBenchFlags()` lives in the variant files — `variant_master.go`
registers `--allow-any-window` and `--window`; `variant_crew.go` registers
nothing and returns `(false, "")`. There is no code path in the crew binary that
can set `allowAny`. A flag that exists but defaults to false can be re-enabled
later by an edit, a config file or an env var; one that is not compiled in
cannot.

There is also a redundant post-selection guard that re-checks the chosen window's
process. It cannot fire today — it exists so a future edit to the selection
logic cannot quietly reintroduce the defect.

## Proven, five checks

| Check | Result |
|---|---|
| `collector.exe --allow-any-window` | **exit 2** — *flag provided but not defined* |
| `collector.exe --window ...` | **exit 2** — not defined either |
| `collector.exe --once`, browser titled "Citizen Compass" on screen | **exit 1**, refuses, naming all 8 refused processes |
| `collector-master.exe --allow-any-window --window Claude` | **exit 0**, captures |
| `collector-master.exe --window Claude` (no flag) | **exit 1**, refuses the same window |

The last two are the pair that matters: the same binary, the same target
window, differing only by the flag — so the flag is demonstrably what permits
it, and its absence is demonstrably what refuses it.

The refusal message names every rejected process and count
(`claude.exe x2, windowsterminal.exe x2, discord.exe x1, ...`) rather than just
saying "not found", which would invite someone to reach for a title match again.

**One honest note on my first attempt at check 4:** it failed, and I did not
report it as a pass. The DuckDuckGo window I had used earlier was closed — it
was absent from the refused-process list, which is how I spotted it. Re-ran
against a window that was actually open and it passed.

## Correction to the defect report

Capture 0006 came from an explicit `--window "DuckDuckGo"` during my backend
bench-testing, not from title auto-detection. The defect was real regardless and
was found the same evening by different means: auto-detection selected **this
session's own terminal**, titled "Build Star Citizen data pipeline with three
jobs". The fix stands either way.

**Nothing staged or committed.**

**Next:** job 2 — the UEX commodity endpoints. Token goes from `.env` to the
request header and nowhere else; it will not appear in chat, a log, or any file
I write. Separately noted: that token was exposed in a screenshot and still
needs rotating at UEX, independent of this job.
