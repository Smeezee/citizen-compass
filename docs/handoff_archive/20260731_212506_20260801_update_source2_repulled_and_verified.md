# Update — source 2 re-pulled with the fixed script; all five gates passed

Snapshot `20260801T042157Z` landed and finalized. Source 2's "complete" status
is now **earned** rather than assumed.

## Counts — actual, not assumed

| endpoint | records | previous run | match | bytes | elapsed |
|---|---:|---:|:--:|---:|---:|
| `/api/v2/ships.json` | **156** | 156 | YES | 501,057 | **1.84s** |
| `/api/labels.json` | **63,375** | 63,375 | YES | 6,706,738 | **2.95s** |

Ships: 156 unique `ClassName`, 0 duplicates. Labels: 63,375 unique keys.
Both landed on the **first attempt** — no retries, no 429, no 5xx.

Both endpoints returned **byte-identical** content to the previous run: same
SHA-256 *and* same ETag, compared against the values recorded in the previous
run's **manifest** (a provenance record, not a snapshot — the old snapshot's
files were not read). Expected for a static dataset last modified 2022-11-16.

## Timing — the 180s timeout was measured, and the comment corrected

The comment claimed this source would be "at least as slow as one page of
vehicles (42.6s)". **That estimate was wrong by more than an order of
magnitude** — measured worst case is 2.95s, because these are static files
served with an ETag, not query-backed API pages.

The code comment now states the measurement instead of the assumption. 180s is
retained (~60x the measured worst case): it costs nothing on a healthy response
and still bounds a hung request — but it is now justified by measurement.

Timing was not previously recorded at all, so `elapsed_seconds` was added to the
script's per-attempt and per-response metadata. These are the first real
timings ever captured for this source.

## Historical-data caveat — carried forward

Recorded in the manifest as `label` and `historical_data_caveat`:
**"Historical legacy schema - not evidence of current game state."** Both
endpoints carry `Last-Modified: Wed, 16 Nov 2022 20:52:36 GMT`. This dataset
predates current game state by years.

## Gates, in order

| # | gate | result |
|---|---|---|
| 1 | files present | PASS — 4 files, none zero-byte |
| 2 | JSON parses | PASS — all 3 .json parsed individually |
| 3 | file-type inspection | PASS — all 4 by magic bytes, no executables/archives |
| 4 | malware scan | PASS — MpCmdRun ScanType 3 `-DisableRemediation`, exit 0, no threats |
| 5 | content-indicator scan | PASS — **fixed** script, 4/4 files, coverage complete |

Gate 5 used the fixed `integrity_scan.py`. The old version would have skipped
`_pull_stderr.log` entirely while still reporting PASS. One domain found:
`scunpacked.com` (4 occurrences), allowlisted.

Gate 4 note: this run confirms `report_only_mode_confirmed: true`. The previous
run recorded **false** — its `Set-MpPreference` attempt failed on a non-elevated
session. `-DisableRemediation` on the scan command needs no elevation.

## Post-scan integrity

4 files / 7,209,605 bytes before **and** after. Zero missing, added, or altered.
**CONFIRMED — Real-Time Protection altered nothing.**

## Finalized

Renamed `20260801T042157Z.partial` -> **`20260801T042157Z`** only after all five
gates passed. The malware scan preceded the rename.

## Old snapshot status — PROPOSAL ONLY, not applied

`20260731T031754Z` is recorded as `"snapshot_status": "complete"`. That status
was assigned by a script that performed no verification: it wrote every response
body to its final filename before examining `resp.status_code`, had no retry or
rate-limit handling, and its `main()` returned `None`, so the process exited 0
regardless of what came back. **An error page would have been saved as
ships.json and reported as a successful landing.**

**Nothing in the old manifest was modified.** Its acquisition record stands
exactly as written, and the old snapshot was not read, globbed, or touched.

**Proposed, for Sleven to decide:** change the old snapshot's `snapshot_status`
from `complete` to a value marking it as never verified, and point it at this
run as its successor.

Worth being precise about what this run does and does not establish: the old
snapshot's bytes match this run byte for byte, which is good evidence they are
the genuine upstream bytes. That does **not** retroactively make the old run
verified — it makes *this* run verified.

## Artifacts

- Snapshot: `data-layer/external-sources/scunpacked.com/snapshots/20260801T042157Z`
- Manifest: `data-layer/external-source-manifests/20260801T042157Z/02_scunpacked-com_manifest.json`
  (per-file SHA-256 + byte sizes, script SHA-256, gate script SHA-256, attempt
  counts, measured timings)
- Gate report, pre/post-scan hash sets, and `_build_manifest.py` alongside it

No snapshot belonging to sources 1 or 3, and no existing source 2 snapshot, was
read, merged, globbed or finalized against.

Nothing committed. Nothing pushed.
