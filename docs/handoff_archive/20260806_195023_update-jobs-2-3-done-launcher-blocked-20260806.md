# Update: Jobs 2 and 3 done. Launcher BLOCKED on WO-UI-01.

**2026-08-06.** Committed as `8594ed3`, **not pushed** (no go-ahead for this
change). Both binaries rebuilt and verified - `selftest PASS`.

## Job 2 - `--gamelog`

`FindGameLog` derives from the captured window's process image, then scans LIVE,
PTU, EPTU, TECH-PREVIEW **in that order**. In `--auto` the log resolves at
startup *before any window exists*, so the derivation never applies and the scan
always wins - which on this machine means **LIVE, every time**.

`--gamelog <path>` forces it, and **fails closed**: an unreadable path returns
nothing and says why rather than falling through to the scan. Falling back would
quietly resume watching LIVE - the exact defect the flag exists to prevent.

The path **and the reason it was chosen** now print at every `--auto` start, to
console and to `collector-auto.log`. The reason matters as much as the path:
`found by scanning known install locations` is the line that warns someone they
are about to watch LIVE by default.

## Job 3 - heartbeat, plus the staleness warning

`collector-auto.log` was written **only on capture**, so through a quiet stretch
a running collector and a dead one produced identical evidence: nothing.

Now every 3 minutes: `alive: watching <path>, N bytes read since last line, M
captures total`. Emitted whether or not a game window exists, because "no game
running" is itself a state worth reading back.

And when a window **is** open while the log has not grown in 5 minutes, that is
reported once per stall, with the fix named. A game running and writing nothing
to the log being watched means the wrong file is being watched.

## Proven by mutation (hard rule 12)

| mutation | result |
|---|---|
| refusal branch disabled | bad `--gamelog` resolved to `C:\Program Files\...\LIVE\Game.log` -> **[FAIL]** |
| heartbeat suppressed | **[FAIL]** heartbeat appears once the interval passes |
| staleness suppressed | **[FAIL]** staleness warning fires on a dead log |

The clock is injected, so a 3-minute heartbeat and a 5-minute stall are tested in
milliseconds. A test taking eight minutes would not get run.

### Two of my own checks were broken, and the mutants found them

1. "warning names the fix" searched the **whole log** for `--gamelog`. The
   startup line contains it, so the check passed **without ever reading the
   warning**. Now requires both strings on the same line.
2. The "clears when growing" step advanced the clock *past* the staleness
   threshold again, so it asserted that a **correct** second warning was a bug.

Also fixed a real inconsistency the dump exposed: the heartbeat said
`(no log resolved yet)` one line below a startup line that had just resolved
one.

## LAUNCHER - blocked, deliberately

**WO-UI-01 is not in this repo.** No file, no reference in `docs/`, `inbox/` or
the handoff archive. What I have is a launcher spec sent in chat, and **the two
addenda contradict it** on three points:

| | chat spec | addenda |
|---|---|---|
| version | selector, "before starting" | **auto-detect** |
| controls | `[START] [STOP]` | **no start/stop** |
| toolkit | **raw Win32 only**, no toolkit | **WebView2 bundled** is fine |

Two of the four acceptance tests I was given are written against START and the
version selector. Building now means building from what looks like a superseded
draft.

**Sleven chose: drop WO-UI-01 into `inbox/` and build from that.** Confirmed for
when it lands: **WebView2, bundled**; selftest output goes to **both** an
attached parent console and a log file.

### Flagged for whoever writes WO-UI-01

Addendum 2 requires the GUI subsystem (`-H=windowsgui`), and such a binary has
**no stdout**. `--selftest` would print to nowhere - including the packager's own
"run the extracted exe with `--selftest`, assert exit 0" verification. Hence the
both-console-and-file decision above; it needs to be in the work order rather
than discovered during the build.

Also: nothing rebuilds these exes automatically. A launcher that shells out to a
stale binary would show RUNNING while running the wrong code - the same class of
lie its own "status from reality" rule exists to prevent. Worth closing inside
that job.

## Current state

- Jobs 1, 2, 3: **done**. Job 1 pushed; Jobs 2-3 committed awaiting go-ahead.
- Unpushed: `8594ed3`.
- Launcher: **waiting on WO-UI-01 in `inbox/`**.
