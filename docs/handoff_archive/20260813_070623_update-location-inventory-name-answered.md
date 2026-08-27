# Update — §1 answered. `location_inventory_name` is not stale and is not waiting on Sleven. It is speculative, and its zero is now a measured expectation.

The order offered two possible answers and it turned out to be a third, so this
is the evidence rather than the conclusion alone.

## Measured against the real archive

`LIVE/logbackups`, 235 logs, 2024-09 to 2025-11:

```
RequestLocationInventory lines             1038   across 146 of 235 logs
... carrying name="..." anywhere              0
... matching the verified Location[...]    1029
... the remaining 9                           INVALID_LOCATION_ID
```

The real line, with the handle removed:

```
<RequestLocationInventory> Player[...] requested inventory for Location[Stanton4_NewBabbage] [Team_CoreGameplayFeatures][Inventory]
```

**There is no `name="` on it. There never has been.** So the pattern is not
stale — CIG has renamed nothing here — and it is not covering something Sleven
has not done. It was written for a line shape that has no evidence of ever
existing in this subsystem.

## The 9 that match neither pattern are correct behaviour

```
<RequestLocationInventory> Player[...] requested Location[INVALID_LOCATION_ID] doesn't have inventory.
```

That is the game saying a place has no inventory. It is not a location, and it
is correctly never recorded as one. Worth knowing, because it is the one thing a
well-meaning "fix" to this reader would start capturing.

## What I did

**Left the reader in place** and turned its zero from an open suspicion into a
recorded expectation, in both places a reader would look: the extractor table's
`Note` (which is what the collector prints) and beside the regex itself. Both
carry the counts and the date, so nobody re-runs this investigation in six
months.

It costs one regex per matching line and would catch the form if CIG ever writes
it. `Verified: false` stays false — it has still never matched anything.

**A warning went in beside it**: do not "fix" this by loosening the pattern. The
quoted-value rule that the three unverified patterns share is what stops a
location being invented out of two adjacent fields — the `taskname="ResolveSpawnLocation"
state=eCVS_UnstowPlayer(14)` line once produced a location called "state". A
looser version of *this* pattern would match the player handle sitting on the
same line.

## Asserted, so a change is visible

Two checks added to the mine selftest, both passing:

```
[ok] mine: a location the game says has no inventory is not recorded as a location
[ok] mine: the verified Location[...] reader is what fires, not the name= variant
          Location[] hits 1, name= hits 0
```

## Incidental, and it belongs to the held §5

That line carries `Player[<handle>]` in the same subsystem the location parser
reads. It is a clean example of §5b's second point — **the log states the
player's own handle, so scrubbing by declared identity is a string deletion
rather than a guess about what a name looks like.** Recording it as evidence for
C1's correction. Not acting on it.
