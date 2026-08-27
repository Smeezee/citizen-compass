# Update — §1-§4 verified. 414 ok, 2 FAIL, and both failures are the pre-existing pair. Stopped before committing.

## The confirming run

```
selftest FAIL (2 checks failed)
EXITCODE=1
414 ok, 2 FAIL
```

Both remaining failures are the ones that were there before I started:

```
[FAIL] sent-rows: first export carries the one pending row   rows=309
[FAIL] sent-rows: confirming marks exactly the exported row  marked=309
```

My two regressions are gone, and the checks that replaced them pass — including
both negative controls:

```
[ok] no interval setting -> whatever the built-in default is    sec=120
[ok] the built-in default is 120s (§2 - gated, then doubled)
[ok] interval_seconds is honoured                               sec=30
[ok] a setting that overrides the default is reported, not silent
       notes = [settings: interval_seconds = 30 comes from collector-settings.txt
                and overrides the built-in default of 120s. ...]
[ok] NEGATIVE CONTROL: a file that matches the default says nothing   notes = []
```

That last one matters more than it looks: without it, "this overrides the
default" is a line that would appear whether or not it were true.

## State of the four items

```
§1  location_inventory_name    ANSWERED - speculative, not stale; measured and recorded
§2  in-world gate + 120s       BUILT - 7 checks, each with a negative control
§3  hotkey burst               BUILT - 12 checks, 3 mutations, all caught
§4  miner timing               NOTHING BUILT, as ordered - and §4's premise corrected
§5  the privacy leak           HELD for C1's correction
§6  export guard               HELD - it is defined by §5
```

`go build`, `go vet` and `gofmt` clean across every file touched.

## Not committed

Rule 2. The order carries a go-ahead from C1 relaying Sleven, and Sleven chose
the §1-§4 scope in session — but neither is him saying "commit this", for this
change, in this session. The work is in the tree:

```
citizen-collector/auto.go               auto_selftest.go     burst_selftest.go
citizen-collector/gamelog.go            gamelog_mine.go      main.go
citizen-collector/mine_selftest.go      session_burst.go     hotkey_poll_selftest.go
9 files, +658 -37
```

Suggested split if the answer is yes — `git add` by path, never `-A`, per §7:

```
1  location_inventory_name: an expected zero, measured
      gamelog_mine.go, mine_selftest.go
2  the collector stops photographing the main menu
      auto.go, gamelog.go, auto_selftest.go, hotkey_poll_selftest.go
3  one press of the hotkey is a burst
      session_burst.go, auto.go(*), main.go, burst_selftest.go
```

`auto.go` carries §2 and §3 together, so it lands in whichever commit goes
first; I would put it with §2 and say so in the §3 message.

## The one thing I would ask C1 to look at in §5's correction

Nothing in §1-§4 touches the leak, but §1 turned up a clean example for it. The
line the location parser reads is:

```
<RequestLocationInventory> Player[<handle>] requested inventory for Location[Stanton4_NewBabbage]
```

The player's own handle is **stated by the log, on the same line**, in the
subsystem that feeds `location_candidates[]`. That is §5b's second point in
miniature: scrubbing by declared identity here is deleting a string the log
itself identified, not guessing what a name looks like. Offered as evidence, not
as a decision.
