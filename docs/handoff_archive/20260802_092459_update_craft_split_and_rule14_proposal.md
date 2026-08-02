# UPDATE — craft indexes split page-per-file; rule 14 enforcement proposal delivered

## The amendment's question, answered with the distribution

**Per-file splitting alone does NOT bring p99 into range. The source list needs
its own file.** Measured over all 1,597 rows:

| | p50 | p90 | p95 | **p99** | max | >20 KB |
|---|---:|---:|---:|---:|---:|---:|
| whole row, `sources` inline | 2,191 | 12,690 | 18,334 | **63,706** | 91,648 | 74 files |
| `sources` moved out | 1,868 | 2,311 | 2,962 | **3,040** | 3,284 | **0** |
| `sources` alone | 2 | 10,832 | 16,150 | 62,559 | 90,637 | 74 files |

C1 was right that a 7 KB mean with a 90 KB tail is two problems. It is worse
than that: **p99 is 63.7 KB, 29x the median.** Splitting per blueprint moves the
tail from one file to 74 of them; it does not remove it.

Moving `sources` out collapses the page distribution entirely — **nothing over
3.3 KB, zero files above 20 KB.**

**The 127-source blueprint specifically:** `BP_CRAFT_klwe_pistol_energy_01_mag`
is 91,648 bytes, of which **90,637 (99%) is the source list**. Split, its page
is **971 bytes** and the 86 KB source list is fetched only if someone opens it.
The four next-largest are Mining Lasers at ~80 KB, also 98% sources. The tail is
entirely sources, in every case.

**A finding the split surfaced: 873 of 1,597 blueprints (54.7%) have an EMPTY
source list.** So a sources file is written only where there is something to
write — **724 files instead of 1,597**. Writing empty ones would have added 873
requests that can only ever return `[]`.

## What now exists

```
blueprints/<key>.json          1,597 files   3.06 MB   page data, no sources
blueprints/sources/<key>.json    724 files   5.68 MB   lazy-loaded
items/<id>.json                5,344 files   1.87 MB
blueprints/_list.json                        254.7 KB  minimal listing
                               ----------
TOTAL                          7,666 files
```

**File budget: 7,666 craft + 480 existing = 8,146 against a 20,000 cap — 11,854
headroom (59% free).** Comfortably inside the arithmetic C2 already did.

**What a visitor downloads now:**

| | before | after |
|---|---:|---:|
| landing on the craft index | **10.91 MB** | 254.7 KB |
| opening a blueprint | (already loaded) | **1.7 KB** (p50), 3.0 KB worst |
| its source list | (already loaded) | 86 KB, **only if opened** |

The combined indexes stay exactly as they are — build artifacts for derivation,
never fetched by a browser.

**Verified by round-trip, not by file count:** the worst row was reassembled
from its page plus its sources file and compared to the original — `True`.
`blueprint_key` is unique across all 1,597 and needs no filename sanitisation;
same for all 5,344 item keys. Both checked before writing, not after.

`scripts/split_craft_pages.py` rebuilds its output directories from scratch each
run, so a removed blueprint cannot leave a stale page behind.

## A 7,666-file accident, closed before it happened

`data-layer/processed/.gitignore` covered the combined `*.json` files but **not
subdirectories**. The split created 7,666 untracked files that a single
`git add -A` would have swept into one commit — the same way another session's
work has been swept twice already tonight. Added `blueprints/` and `items/`;
untracked count under `processed/` is back to **0**.

## Rule 14 enforcement proposal — delivered

`docs/proposal-rule14-single-writer-enforcement.md`. **Proposal only, nothing
implemented**, per instruction.

The short version: the two previous fixes worked because each had a
**registration choke point** a guard could refuse at. File writes have none —
three sessions, one OS user, one machine. **I cannot make the write impossible,
and claiming otherwise would be the enforcement-that-isn't this project keeps
finding.** So the target is rule 14's own second clause: make an unacknowledged
write loud, and refuse to ship un-provenanced content.

Mechanism: a tracked `LAYER.lock` holding the last owner-acknowledged sha256;
the build refuses when disk disagrees and names both hashes; writes go through
one helper that updates file and lock atomically; the deploy re-checks **at
upload time, not at start** — the lesson from staging files I had verified
minutes earlier that changed in between; and a daily checker reports drift even
if nobody builds.

**All four of tonight's incidents would have stopped at the build.** None was
malice and none was a stale-mtime mistake — every one was a session editing a
copy it believed was current. Incident 3 is the clearest: a genuine improvement
that happened to carry an old version of one line, silently reverting a
committed fix.

Limits stated in the doc rather than glossed: it does not prevent the write, it
does not recover clobbered content (git does, which is why committing after
every edit is part of the workflow), and it adds a step to every legitimate
edit.

## Layer state — checked, and the tab has NOT come back

`_layer.src.html` changed again since my commit (`889e4ff1` → `95177c82`,
+82 lines) and `cc-lo-tab` appears once, which looked like a third regression.
**It is not.** The single occurrence is a comment recording why the id was
dropped from the dock's IDS array. Live element `<a id="cc-lo-tab">`: **0**.
Style rule `#cc-lo-tab`: **0**. `id="cc-kb"` 1, `cc-ship::after` 2, `cc-strip` 7
all intact.

That is C2's A3 fix, which C1 has already accepted and checksum-verified.
Committing it so it is not lost — but noting that it reached me as a disk write
rather than as an edit from C1, which is precisely the traffic the new workflow
is meant to end.

**No deploy performed** — the amendment did not ask for one, and the split
output is not wired into any page yet.
