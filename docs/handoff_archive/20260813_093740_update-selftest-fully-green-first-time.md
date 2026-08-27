# Update — `selftest PASS`, 436 ok, 0 FAIL. First fully green run, and the two long-standing failures are gone for a real reason.

```
selftest PASS
EXITCODE=0
436 ok, 0 FAIL
```

## The pre-existing pair is fixed, not silenced

```
[ok] sent-rows: first export carries the one pending row    rows=1 keys=1
[ok] sent-rows: confirming marks exactly the exported row   marked=1
```

Those read `rows=309` for as long as anyone has run this on Sleven's machine.

The test seeded a temp store with one row and asserted the export carried
exactly that row - but `BuildExport` calls `MineAll`, which calls
`MineTargets()`, which walks real drive letters. So the entire 235-log archive
was mined into the temp folder and the checks found 309 rows where they had
planted 1.

**It passed only on a machine with no Star Citizen installed.** That is worse
than a plainly broken test: the natural reading is "that one always fails here",
and a check nobody believes has stopped being a check. Its own comment claimed
it bypassed the scan - the bypass was one call level above where the scan
happens.

The seam is `var mineTargets = MineTargets`, the same injection shape
`autoDeps` already uses for `findLog` and `now`. Production always uses the real
one; only the selftest replaces it, and it restores it in a defer.

**It can still fail.** With the scan stubbed out, a broken seed or a broken
export gives 0 rows and the check goes red - it asserts the export carries what
was planted, which is what it always claimed to assert and could never actually
test.

## State of the collector order

```
§1  location_inventory_name    ANSWERED, pushed 7d12ace
§2  in-world gate + 120s       BUILT, pushed b75a94a
§3  hotkey burst               BUILT, pushed 6dde2bd
§4  miner timing               NOTHING BUILT, premise corrected, pushed b75a94a
§5  the leak                   BUILT - unified, not muted. NOT COMMITTED
§6  export guard               BUILT with negative control. NOT COMMITTED
NEW renderer in the sidecar    BUILT, matcher corrected. NOT COMMITTED
```

Uncommitted, 6 files plus one new script:

```
citizen-collector/gamelog.go          the parser fix + the renderer field
citizen-collector/gamelog_mine.go     the [VK] correction + the mineTargets seam
citizen-collector/export.go           the privacy guard
citizen-collector/leak_selftest.go    NEW - 20 checks
citizen-collector/main.go             registration
citizen-collector/sent_rows_selftest.go   isolation
scripts/scrub_sidecars.py             NEW - dry-run only
```

## Two decisions outstanding

1. **The 401 sidecars.** Dry run printed, nothing written. `--apply` backs up to
   `_to_delete/` and verifies every copy before touching anything. They are
   already contained by §6 either way.
2. **Committing §5/§6.**

## What still cannot be claimed

Acceptance 1 of the revised list says *verified by grepping a fresh captures
folder after a real session, not by reading code.* **That has not happened and
cannot happen without playing the game.** What exists is the same assertion
against real log shapes carrying real identifiers, with a negative control
proving those identifiers are findable when present.

The renderer field, the location fix and the guard have all been exercised
against fixtures built from the archive - not against a live session.
