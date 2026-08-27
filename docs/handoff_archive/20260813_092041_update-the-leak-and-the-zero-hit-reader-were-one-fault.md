# Update — §5a done by UNIFYING, not muting. C1's "probably one fault" was right, and §1 had already found it.

`gamelog.go`, new `leak_selftest.go`. Builds, vets, formats clean.

## The two symptoms are one line

The sidecar parser's first location pattern was:

```go
{"RequestLocationInventory", regexp.MustCompile(`RequestLocationInventory[^\n]*?\bname="([^"]+)"`), 1},
```

That is the **`name="` form** - the exact pattern §1 measured as **never
appearing in 1038 RequestLocationInventory lines across 235 archived logs.**

So the parser's first attempt, on the subsystem that fires most often, could
never match. It fell through every remaining guess, found nothing, and attached
forty raw lines. Every in-world capture, for months.

Meanwhile the burst path reads `reMineLocation` -
`requested inventory for Location\[([^\]]+)\]` - **Verified, 1029 of 1038
matches** - which is why it named `AsteroidClusterBase_Nyx_Social_Keeger_002` in
the same second the sidecar wrote `null`.

**C1's hunch in §2 of the erratum was exactly right: one fault, two symptoms.**
§1's answer and §5's leak are the same defect seen from opposite ends - one
consumer of those lines reported an honest zero, the other quietly haemorrhaged.

## What I changed

**The parser now borrows the verified pattern**, the same way `auto.go` already
borrows it. One definition in `gamelog_mine.go`, three consumers: the miner, the
capture trigger, and this parser. A second copy would drift, and the day CIG
changes the format one copy would keep matching and hide the other's failure.

Verified patterns are tried first and cannot be displaced by a guess - the rule
this file already had, now with something in the verified list to enforce it
against. The dead `name="` pattern is gone from the guesses.

## And the payload is replaced anyway — this is the part I want to argue for

The erratum treats muting as the fallback if unification is not cheap. It was
cheap, so I did the unification. **I removed the raw-line payload as well**, and
that is deliberate rather than belt-and-braces:

Closing the leak by making the parser succeed means **the leak returns the
moment it fails.** A log that starts mid-session, a future CIG rename, a capture
taken before the first terminal is opened - any of those and forty raw lines are
back in the sidecar. A payload that cannot leak is a property. A payload that
only leaks when something else breaks is a coincidence.

The diagnostic survives without a byte of log text:

```json
"location_patterns_tried": ["RequestLocationInventory-Location[]", "OnClientSpawned-zone", ...],
"location_candidate_lines": 4
```

That answers the only question the raw lines were ever used for - *which matcher
should I be looking at* - and the file header now points at
`LIVE/logbackups` for the actual lines, which is where these patterns were
confirmed from in the first place and where reading them costs nothing.

## Verified against real identifiers, both directions

`leak_selftest.go`. Every fixture line is a real shape from the archive,
**including the real identifiers** - a leak test built from invented data proves
only that invented data does not leak.

```
[ok] LEAK: an in-world sidecar carries NO player id, handle or third-party id
[ok] LEAK: and no raw log line - no timestamp-and-[Notice] text at all
[ok] an in-world sidecar reports a NON-NULL location
[ok] and it is the location the burst path names, from the VERIFIED pattern
[ok] the menu case still resolves, and still leaks nothing
[ok] LEAK: an UNPARSEABLE in-world log still leaks nothing
[ok] and it still says which matchers were tried, so the gap is diagnosable
[ok] NEGATIVE CONTROL: every identifier IS present in the source log
```

The last one exists because without it the leak checks would pass against a
fixture that never contained a handle - a leak test that cannot detect a leak.
The unparseable case matters most: that is precisely where the payload used to
be attached.

Rule 12, both mutations caught, `gamelog.go` restored byte-for-byte:

```
PASS  M1 put the raw-line payload back
PASS  M2 remove the verified pattern - the parser stops resolving in-world
```

**M2 is the interesting one.** Take the verified pattern away and the location
goes null again - which demonstrates the single-fault claim rather than just
asserting it.

## Acceptance, so far

```
1  no sidecar carries an id or a raw line   PASS in test; needs a real session to confirm
2  in-world sidecar reports a non-null location, or says why with no log text   PASS
3  the 364 existing sidecars                NEXT
4  renderer in every game_log block         NEXT
5  Alt+F3 uses the existing burst           DONE, shipped in 6dde2bd
```

Next: the 364 existing files, then §6's export guard.
