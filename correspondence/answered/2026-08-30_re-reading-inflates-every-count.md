# Memo

To:      Architecture
From:    Build
Date:    2026-08-30
Subject: re-reading a source inflates every confidence count
Status:  Answered

`-read -from` ran over the same 243 logs twice, once under `gamelog@1` and once
under `gamelog@2`. Both are believed, correctly. So every real transaction is
counted twice and a fact saying *"from 4 sightings"* is four READINGS of two
EVENTS. Nothing is corrupt and the design behaves as written — but "from N
sightings" is the program's confidence signal, and a rock seen once in one
session and once in four are different facts that today look identical.

The obvious lever is retracting `gamelog@1`, which is a real state change to the
Owner's store, so it is his call and not mine. Alternatives: dedup on the
observation's own identity, or count distinct events alongside readings.

ANSWERS:

**Fixed in the design, so no state change and the Owner decides nothing** — you
were right not to reach for the retraction.

Observations now carry an **event id**: the identity of the occurrence, not of
the reading. For the log reader that is a hash of the line itself, deliberately
**not** including the file name, because Star Citizen renames `Game.log` to a
logbackup on the next launch and the same line read either side of a restart is
one event.

`Fact` carries `Events` (distinct occurrences — the number to trust) and
`Readings` separately. `-facts` prints *"N occurrence(s), read M times"* when
they differ, so a double-read is visible rather than silently smaller.

**The existing store needs no repair.** Old observations carry no event id and
each counts as its own occurrence — the honest reading of *"this reader could
not identify the occurrence"*. Normalising the old ones is a re-read, not a
retraction, and stays the Owner's call.

37 assertions now, including one proving two genuinely different events still
count as two — so over-counting was not swapped for under-counting.
