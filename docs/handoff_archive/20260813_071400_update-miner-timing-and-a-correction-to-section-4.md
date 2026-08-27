# Update — §4: built nothing, as instructed. But §4's stated reason is half wrong, and the code now records what actually happens.

## The instruction was right; the premise behind it was not

§4 says the miner already runs "on entering and exiting the game", cites two log
timestamps, and says build nothing.

**There is no mine on entry.** `MineAll` has exactly three callers in the whole
program:

```
ui.go:356      the game-exit hook (the windowed mode people actually use)
main.go:1236   the game-exit hook (--auto)
export.go:95   BuildExport, so a SEND never ships a stale file
```

And no startup pass can be hiding in the exit hook, because `gameWasAlive` is a
plain `bool`. Its zero value is **false**, so the running -> gone transition
cannot fire at launch. If the game is already running when the collector starts,
the flag simply flips to true and nothing is mined until the game closes.

The two timestamps in the order are consistent with two game exits in one
evening, or an exit plus an export. They do not evidence an entry mine.

## Why this changes nothing about what to build

**Mining on entry would be a no-op by construction.** Between one exit pass and
the next launch, nothing can have been appended to the archive that the exit
pass did not already read. That is precisely why the real run reports

```
mine: 244 logs read (0 unreadable), 0 new rows, 308 total
```

and why the collector says *"nothing new this pass. That is normal after a
session with no trading"* rather than looking broken.

So: **nothing built, exactly as ordered.** But I was not willing to write a code
comment asserting a startup mine that does not exist. A comment that sends the
next reader hunting for code nobody wrote is worse than no comment — it is the
same defect as a check that reports a pass it never performed, just in prose.

## What went into the code

A note on `onGameExit` saying: do not add a timer, asked and answered
2026-08-13; mining is driven by exactly two events, this one and an export; there
is deliberately no startup pass and here is why it would be a no-op; and mining
on exit beats a timer on its merits, because the session's log is complete at
that moment and gets read once in full rather than repeatedly while half-written.

That is what §4 asked for — the reasoning sitting where somebody would go to
"improve" it — with the factual half corrected.

## If C1 disagrees

The one case where an entry mine would earn its keep is a log that changed
outside the collector: a machine where the archive was copied in, or a first run
on somebody else's PC. That is a crew-build scenario, which is gated behind §5
anyway. Flagging it as a question rather than acting on it.
