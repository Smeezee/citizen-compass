# Update — all three review points answered. The first one I answered differently from how it was asked, and the measurement is why.

**2026-08-30 09:00 UTC / 2026-08-30 04:00 local · Code (background session)**

**First, a correction: `b9de329` was already pushed when the review arrived.**
These land as a follow-up, not in that commit.

## 1. THE NAME RISK IS REAL. `nameclass.go` IS THE WRONG INSTRUMENT FOR IT.

The concern is right: `hud_target` can be a player-piloted ship, so a caller
could hand the store a real handle and it would land in `pairs.jsonl` verbatim.

**I measured `ClassifyName` against real labels before wiring it in, and it
fails in both directions:**

    CST-313 Castillo   SWAP - treated as a person     legitimate item label
    MRX                SWAP                            legitimate
    M2C Swarm          SWAP                            legitimate
    Gladius            SWAP                            legitimate
    Hull armor         SWAP                            legitimate
    VariPuck S7        SWAP                            legitimate

    xX_Pilot_Xx        KEEP - "NPC role vocabulary"    A HANDLE. KEPT.
    Jane Doe           KEEP - "mission NPC (spaced)"   handle shape. KEPT.

**It is tuned for names the game LOG writes** - NPC archetypes, asset ids,
pseudonyms - not for arbitrary on-screen text. Routing labels through it would
have swapped six of ten real item labels **and still passed the exact handle
shape the review is worried about.** It would have made the store useless while
leaving the hole open, and it would have looked like a fix.

**So the allowlist does the work, which is what it is for: `hud_target` is off
it.** The constant stays defined so the refusal names something real and so
re-admitting it is a deliberate edit with the measurement in front of whoever
makes it.

    [ok] hud_target is DEFINED but NOT recordable - it can show a person
    [ok] and a hud_target pair is refused in practice, not just on paper

**To re-admit it, something must be able to tell a ship's name from a handle.
`ClassifyName` cannot. That is a real item, not a line change.**

## 2 AND 3. BOTH CORRECT, BOTH FIXED, APPEND-ONLY INTACT

**O(n) per write.** `load()` re-read and re-parsed the whole index on every
`StorePair` - O(n^2) over a store designed to grow for months, on a machine that
is also running a game. State is now folded **once at open** and maintained in
memory.

**Quadratic bytes.** Attaching a view re-appended the entry with every prior
view: the tenth sighting rewrote nine views to record one. A `PairDelta` is now
appended instead - key plus one view - and `foldFromDisk` folds deltas onto the
entry they name, in file order.

    [ok] a third view appends a DELTA - one view's worth, not the entry again
         3 view(s), index grew 173 bytes

**Told apart by SHAPE, not by a type field** - a delta carries a view and no
label - so a file written before this change folds identically.

**The file is still only ever appended to**, and the assertion that proves it is
unchanged and still passes.

## STILL ABSENT FROM THE CREW BINARY

    StorePair     crew 0  master 2      PairDelta     crew 0  master 1
    NewPairStore  crew 0  master 1      foldFromDisk  crew 0  master 1

    master --selftest exit 0     crew --selftest exit 0

The `nameclass` probe is parked in `_to_delete/probes-20260830/`.
