# Update — source 3 re-run ABORTED, retrieval script fixed

The page[size]=50 re-run started earlier was stopped on instruction, before it
finished. Two defects were identified with it.

## 1. Run stopped

Background pull terminated. Confirmed no retrieval process survives — the only
remaining `python.exe` instances are the pre-existing blender-mcp servers,
unrelated to this run. Nothing from this run was finalized.

## 2. Aborted output quarantined

Renamed, not deleted, not merged:

```
data-layer/external-sources/api.star-citizen.wiki/snapshots/20260801T015346Z.partial.aborted__pagesize50
```

Contents (10 files, exactly as the interrupted run left them):

| file | bytes |
|---|---:|
| game_version_default.json | 162 |
| game_version_default.headers | 1,038 |
| openapi.yaml | 710,528 |
| openapi.headers | 1,002 |
| vehicles_page_1.json | 3,271,789 |
| vehicles_page_2.json | 2,177,479 |
| vehicles_page_3.json | 2,739,271 |
| vehicles_page_4.json | 2,495,267 |
| _pull_stderr.log | 52 |
| _pull_summary.json | 0 (script only prints at the end; never reached) |

It reached 4 of 6 vehicle pages. `items` and `manufacturers` were never started.
The directory no longer ends in `.partial`, so a finalizer globbing `*.partial`
will not see it. **A finalizer globbing `snapshots/*` still would** — worth
knowing before any future finalize step is pointed at this source.

## 3–5. Script fixes (`scripts/external_sources/api_star_citizen_wiki.py`)

**PAGE_SIZE reverted to 200.** Confirmed by assertion.

**Per-collection override added.** `PAGE_SIZE_OVERRIDES = {"vehicles": 50}`, with
the reason recorded in a comment next to it (probe of 2026-07-31: 200 -> HTTP
500 text/html; 20 and 50 -> HTTP 200 valid JSON). Resolution verified:

```
vehicles       -> 50
items          -> 200
manufacturers  -> 200
```

**Write-before-status bug fixed.** A response now earns its final filename only
after passing three checks in order: `status == 200`, Content-Type contains
`json`, and the body parses. A rejected response is recorded as an error and
never written to the snapshot.

**Also added per PROBLEM 2:** `sha256` per response, alongside the `byte_size`
that was already recorded. Plus `page_size_used`, `written_to_disk`,
`file_path` (null until written), and collection-level
`pages_written_to_disk` / `pages_rejected`.

**One judgement call to review:** a rejected response contributes
`rejected_body_first_200_chars` to the JSON summary — diagnosis only, matching
how the probe reported. No rejected body reaches disk as a file. Say if you'd
rather it record nothing of the body at all.

**One comment corrected:** `get_with_retry` claimed the vehicles 500 was
"intermittent" and "transient", inferred from 2-of-3 manual attempts. The probe
disproved that — it is deterministic at page[size]=200. The comment now records
the correction rather than the disproven claim. Retry logic itself unchanged.

## Verification (offline — `requests.get` stubbed, no network)

| case | files on disk | written | rejected |
|---|---|---:|---:|
| HTTP 500, text/html | none | 0 | 1 |
| HTTP 200, application/json, unparseable body | none | 0 | 1 |
| HTTP 200, text/html | none | 0 | 1 |
| HTTP 200, application/json, valid | `vehicles_page_1.json` | 1 | 0 |

All assertions passed; no rejected response reached disk.

## Separate defect found, NOT fixed (not in scope, flagging only)

`get_with_retry` uses `timeout=60`. The probe measured vehicles at
page[size]=50 taking **42.6 s**. That is a 17-second margin. If upstream is
slower under load, `requests` raises `Timeout`, which `get_with_retry` does not
catch — the whole script would crash mid-pull rather than retry. Six vehicle
pages each ~43 s means this is likely to be hit eventually. Recommend raising
the timeout and wrapping the request in try/except before the next real pull.
Not changed, since it wasn't asked for.

## Status

No pull started. Nothing committed. Waiting.
