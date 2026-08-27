# Update — the roadmap watcher is built, running against the live endpoint, and the baseline is taken.

`roadmap-watcher/` - new Go module, 7 files. Builds, vets, formats clean, 8 tests
green. **Not committed** (rule 2).

## It works, and here is it working

```
board 1 (Release View): 823 cards, 3 matching "Constellation", 801 KB
board 2 (Squadron 42):  116 cards, 0 matching "Constellation", 206 KB
BASELINE TAKEN: 3 watched card(s) recorded as the starting point.
                Nothing here is new - it is what is on the board today.
  baseline: Merlin/Constellation Docking       [Release View]
  baseline: RSI Constellation Phoenix          [Release View]
  baseline: RSI Constellation Taurus           [Release View]
```

Second run, immediately after:

```
no change. checked boards [1 2] for "Constellation"; the GraphQL progress
tracker was NOT checked (stage 2 off), so this is not a statement about the
whole roadmap | trigger=manual
```

**That caveat is on every single result**, per §6 - while stage 1 runs alone the
watcher must never let a partial check read as a complete one.

## Three things the order asked me to find out, answered

**1. `boards/1` is not the only board.** Board 2 is "Squadron 42" (116 cards, 0
Constellation). Boards 3 and 4 return 91 bytes of nothing. The watcher polls 1
and 2 and names the surface on every line, so the question does not have to stay
answered to stay safe.

**2. There are THREE Constellation cards, not one.** §4 keys on "beyond the one
known card"; built that way it would have fired twice on its first run on cards
years old, and then been muted. The baseline is stored as data - a fourth card
is the signal.

**3. THE CONDITIONAL REQUEST DOES NOT WORK.** The order said try it, do not
assume. I tried:

```
board 1: 801 KB, no validators offered
board 2: 206 KB, no validators offered
```

**RSI sends neither `ETag` nor `Last-Modified`**, so there is nothing to send
back and every poll is a full download. The code sends validators whenever it
has them and logs which case happened, so if RSI starts offering them it will
start saving bandwidth without anyone changing anything. At 6 polls a day of
~1 MB that is ~6 MB/day, which is why the cadence floor matters.

## What is refused rather than corrected

`interval_hours` below 2 is an **error, not a clamp**. The order rules hourly out
explicitly; a settings file that says one thing while the program does another
is the defect shape this project keeps finding.

A corrupt state file is **refused, not reset**. Silently starting over would
re-baseline against today's board and throw away the history the tool exists to
hold - while reporting success.

## The manual check is the same code path

`-check` and the timer both call `runOnce()`. Not a separate script, not a debug
mode. The only difference is a string in the record saying which triggered it,
because a hand-run that can disagree with the scheduled one is useless for
checking on the scheduled one.

`-status` prints what is known and polls nothing.

## Tests - 8, and proven able to fail

```
first run takes a baseline and reports nothing new
A NEW CONSTELLATION CARD IS DETECTED          <- the entire point
an edited card is caught by the fingerprint
updateDate never triggers anything            <- the trap in §4
roadmap dates parse (RFC-1123, not ISO)
boards do not shadow each other
a corrupt state file is refused rather than reset
too aggressive a cadence is refused
```

Rule 12: breaking the detection - making it never report a new card, the
tripwire that says "no change" forever - fails two of them. Restored, green.

Go tests rather than a `-selftest`, because `watcher-go` already uses Go tests
and this is the same kind of thing.

## Stage 2

Built, not scheduled, behind `stage2_enabled`. Turning it on is Sleven's call
per the order's staged rollout. **I have not exercised the GraphQL endpoint** -
the no-session claim is CIC's and remains unverified, which §9 already flags as
load-bearing. It will be found out on the first run after he flips the flag.

## Housekeeping

`go.work` gained the module. A `.gitignore` keeps the binary, the state and the
settings out - state is a record of what THIS machine has seen, and committing
it would hand a fresh clone somebody else's idea of what is already on the board.

**Third stale `.git/index.lock` this session** - 0 bytes, 32 minutes old, no git
process. Moved aside per rule 1 like the others. Three in one day is a pattern
rather than bad luck; something is taking the lock and not releasing it, and it
is worth finding out what.

Next: the inbox watcher's overwrite behaviour, which is §7 of this very order.
