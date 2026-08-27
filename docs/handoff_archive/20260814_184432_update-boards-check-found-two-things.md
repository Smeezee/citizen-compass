# Update — the five-minute check §9 asked for found two things, and one of them would have made the watcher cry wolf on day one.

## 1. `boards/1` is NOT the only board

```
board 1  820,799 bytes  "Release View"   39 releases, 823 cards
board 2  211,224 bytes  "Squadron 42"    10 releases, 116 cards
board 3       91 bytes  empty
board 4       91 bytes  empty
```

Board 2 is the Squadron 42 campaign roadmap. **It carries zero Constellation
cards today** - measured, not assumed - so stage 1 on board 1 is not currently
missing anything. But the board exists, it is real, and §6's "name the surface in
every result" now has a second surface to name.

## 2. THERE ARE THREE CONSTELLATION CARDS, NOT ONE

The order's §4 keys on *"does any deliverable whose title contains Constellation
exist, **beyond the one known card**"*. On Release View today:

```
RSI Constellation Phoenix       release 3.3
Merlin/Constellation Docking    release 3.13
RSI Constellation Taurus        release 3.14    <- the one the order knows about
```

**A watcher built to the order as written fires on its first run**, twice, on
cards that have been sitting there for years. Then it gets muted, and the real
signal arrives to an alert nobody reads.

The baseline is the three, recorded as data rather than as a number in a comment,
so a fourth is the signal.

## 3. `updateDate` is EMPTY on all three

The order warns not to trigger on `updateDate` because the API said 2024 while
the UI said 2021. On these cards the field is empty entirely. Still stored, still
never triggered on - the warning stands, and now for a second reason.

**`data.last_updated` is a board-level Unix timestamp** (1786570355 on Release
View, 1611779127 on Squadron 42). That is a real change signal at board scope and
worth storing, though the per-card payload hash is the one that localises a
change.

## What I have not established

Whether a Constellation gold-standard card would appear on the Squadron 42 board
at all. It has none now and the board is campaign-scoped, but "it currently has
none" is not "it never would". The watcher checks both boards and names which one
each result came from, so the question does not need answering to be safe.
