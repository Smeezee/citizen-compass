# Update — rev 2 of the work order landed mid-build and named a silent-failure bug in code I had already written. Fixed, plus the routing fix Sleven approved.

## Rev 2 caught something I had the evidence for and misread

**§3A: errors arrive as HTTP 200.** My `FetchBoard` branched on
`resp.StatusCode != http.StatusOK` and then unmarshalled. RSI answers a dead or
failed board with:

```
HTTP 200
{"success":0,"code":"ErrInvalidObject","msg":"Specified board does not exist.","data":null}
```

That would have parsed into a Board with no releases and logged
**"0 cards, 0 matching Constellation"** - byte-for-byte identical to a genuine
clean negative, on a tripwire whose only job is not to miss something.

**I had the measurement and wrote down the wrong conclusion.** My own board
enumeration recorded *"board 3: 91 bytes"* and I filed it as "empty". It was the
error envelope. The bytes were in front of me.

Now it branches on `success`, and the error says so in words:
`board 3 answered HTTP 200 but the body says it FAILED ... This is NOT 'no cards
found'`. Verified against the live endpoint.

## Two more of my own bugs, both caught loudly rather than silently

Adding §3B's release context broke unmarshalling twice, and **both times the
fail-closed design turned a silent tripwire into a five-minute fix**:

```
board 1: poll FAILED (cannot unmarshal number into ... .released of type bool)
NOTHING WAS POLLED this pass - This is not 'no Constellation activity',
                              it is 'we did not look'.
```

1. `released` on a release is `1`/`0`, **not a bool**.
2. Cards carry their OWN numeric `released`, so tagging my derived field
   `json:"released"` made the decoder try to fill it. **A derived field that
   shares a name with an API field will be fed by the API whether you meant it
   or not.** Renamed to `release_name` / `is_released`.

Neither could have reached production quietly, because "we did not look" and
"nothing found" are different sentences in this tool. That distinction earned
its keep within an hour of being written.

## Rev 2, item by item

```
§3A  branch on the envelope, never the status code        FIXED + test + live check
§3B  store the release name and released state per card   DONE - baseline now reads
       "RSI Constellation Taurus, release 3.14, released=true [Release View]"
§6   no 304 path - do not build one                       REMOVED (mine was dead weight)
§6   leave Accept-Encoding unset, with a comment          DONE
§2   board enumeration closed, exactly two boards         matches what I measured
§4   watcher captures its own baseline                    already did this
§7   diff by card ID, hash per card, never updateDate     already did this
§9   surface named in every result                        already did this
```

Rev 2's §0 and my earlier findings agree independently on the two things rev 1
got wrong: three Constellation cards not one, and no working conditional
requests.

**13 tests, all green**, including two new ones for §3A - the error envelope, and
a NEGATIVE CONTROL that a genuinely empty board is *not* an error, without which
the first would be satisfied by a client that rejected everything. Rule 12:
restoring the status-code check fails the §3A test.

## The inbox watcher routing fix - approved and done

Sleven said yes. `updateHeadingHints` substring-matched `"UPDATE"` against the
title line, so `WORKORDER_rework-tripwire-build-spec` was filed as an update doc
because its title contains **"do NOT key on updateDate"**.

Now classification is by document-type PREFIX first - the convention this project
already uses everywhere - with title hints as an anchored fallback only when no
prefix is present.

## Still not committed

Rule 2. `roadmap-watcher/` (7 files + tests), `watcher-go/classify.go`,
`watcher-go/handoff.go`, `watcher-go/routeto_supersede_test.go`, and `go.work`.
