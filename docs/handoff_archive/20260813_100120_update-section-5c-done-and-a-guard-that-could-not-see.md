# Update — §5c done: 394 sidecars rewritten in place, 0 leaking. And the export guard could not see a single real file until I checked it against one.

## The near-miss, first, because it is the important part

My export guard passed seven checks and **could not have caught a real leaking
sidecar.**

Go's `encoding/json` HTML-escapes `<`, `>` and `&` by default. So a raw log line
on disk reads:

```
"<2026-08-07T00:54:33.801Z> [Notice] <ResolveSpawnLocation...
```

There is **no literal `<` in any sidecar this program has ever written.**
Confirmed against a real capture:

```
does the file contain a literal <   ->  False
does the file contain <        ->  True
```

My raw-log-line rule matched `<\d{4}-...` against the file's bytes. It matched
nothing, ever. **The test passed because I hand-wrote the fixture JSON with a
literal `<`** - I tested the guard against a shape the collector does not
produce.

**What it actually cost, stated precisely rather than dramatically:** the 401
files on disk were caught anyway, by the `location_candidates` key rule. What was
broken was the *general* rule - the catch-all for a raw line in a field nobody
has thought of. Proven both directions before fixing:

```
on-disk bytes: {"game_log":{"some_future_field":"<2026-08-13T00:40:37.000Z> ..."}}
OLD rule matches: false
NEW guard refuses it: sidecar carries a raw log line (timestamp and channel)
```

**The fix is not a bigger regex.** Matching both spellings would work today and
break on the next encoder change. The guard now **decodes** the sidecar and walks
every key and every string value - escaping becomes the decoder's problem, and
unknown fields are still visited, which was the whole reason for scanning bytes.
Raw-byte scanning stays as the fallback for a file that will not parse, because
"I could not read it" must never mean "it is fine".

**And the fixture is now produced by `encoding/json`**, not hand-written, with a
check asserting the escaping is really present - so this cannot silently come
back.

## The scrub refused to claim success, and it was right

First `--apply` run: **rewritten 0, STILL LEAKING 394.**

Cause: `location_reason` in every affected sidecar reads *"no location pattern
matched; see location_candidates[] for the raw lines that looked relevant"* - so
a blunt substring rule matched the **description** of the field, not the field.
Strip the array and the file still failed. Forever.

`location_candidates` is a **key**. A value naming it is prose. The rules now
split - key rules on keys, value rules on values - in both the guard and the
scrubber, because the scrubber's promise is that "clean" means the same thing in
both places. Narrowing it is safe rather than convenient: the payload it guards
against is caught by the raw-log-line value rule independently.

That split also freed 7 files that had only ever tripped on prose.

## §5c, done as the decision directs

```
backed up 394 file(s) to _to_delete/sidecars_before_scrub_20260813_095930 (verified)
rewritten:  394
re-scan:    449 sidecars, 449 clean, 0 leaking
```

Rewritten in place, `location_candidates` stripped, **every other field kept** -
`location_reason` and all 14 `game_log` fields survive. Not deleted, per the
decision: `export.go` refuses a PNG with no sidecar, so deleting would bin 394
captures' provenance.

Verified independently of my own code:

```
204354536218        0 files
playerGEID          0 files
orphaned PNGs       0 of 449
```

## The one handle that survived, chased rather than glossed

`Sleven-K` still appears in **one** file: `gamelog-dataset.json`, which the
scrubber deliberately skips.

That is **by design and consent says so**: *"WHAT IS KEPT ON YOUR OWN DISK -
Everything it notices, including player names it saw in the log... It is kept
as-is so the names can be checked before they are removed."*

It sits at index 1 (Victim) of a death key, which `ScrubForExport` runs through
the scrubber. **I verified the claim rather than the code path**, against the
real file:

```
local store DOES contain the handle (by design, per consent)
after ScrubForExport: handle is GONE, 210 person(s) pseudonymised
```

So the local store keeps it, the export removes it, and the decision's rule -
*scrubbing happens on the machine, before anything is sent* - holds.

## What I will not claim

"Zero identifiers in the captures folder" would be false. The **sidecars** are
clean, all 449 of them. `gamelog-dataset.json` holds real handles on purpose and
is scrubbed at the export boundary.

And acceptance 1 still wants a grep of a fresh folder **after a real session**.
This was a grep of the existing folder after a rewrite - stronger than a fixture,
still not the thing that was asked for, and it needs the game played.
