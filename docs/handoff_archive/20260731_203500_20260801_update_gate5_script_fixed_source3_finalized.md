# Update — integrity_scan.py coverage defect fixed; source 3 finalized

Gate 5 was failing on scanner defects, not on the data. The gate script was
fixed, re-run, passed on its own, and snapshot `20260801T021731Z` is now
finalized.

## Record counts (re-reported)

| collection | downloaded | API meta.total | match | page size | pages |
|---|---:|---:|:--:|---:|---:|
| **vehicles** | **295** | **295** | **YES** | 50 | 6 |
| items | 12,283 | 12,283 | YES | 200 | 62 |
| manufacturers | 152 | 152 | YES | 200 | 1 |

Zero pages rejected by the write gate. 75 files, 85,674,557 bytes.

## The real defect

`integrity_scan.py` globbed `*.json`. Every non-JSON file in **every snapshot
this gate has ever run against** was silently skipped while the script exited 0
and the gate reported PASS. That is a gate reporting a pass over files it never
opened — across all previous runs of this pipeline, not just this one.

**Any earlier snapshot finalized on the strength of this gate was finalized on
incomplete coverage.** Worth deciding separately whether the source 1 snapshot
(`20260731T041451Z`) should be re-gated with the fixed script.

A second, independent defect: `URL_RE` swallowed trailing punctuation into the
netloc, so `https://starcitizen.tools)` yielded the host `starcitizen.tools)`,
which failed an allowlist that *does* contain `starcitizen.tools`. A false
positive manufactured entirely by the scanner.

## Fixes

**FIX 1 — coverage.** `main()` now walks every file recursively, not `*.json`.
`scan_file()` reads bytes so any file type can be scanned, decoding non-UTF-8
with replacement (indicator strings and the URL pattern are ASCII, so matches
cannot be hidden). A file that cannot be read is reported **UNSCANNED and fails
the gate** — never counted as passed. New `coverage` block reports
`files_seen` / `files_scanned` / `files_unscanned` / `walk_errors` / `complete`,
and the exit code fails on incomplete coverage as well as on findings.

**FIX 2 — URL_RE.** Now excludes backslash and backtick; `trim_url()` strips
trailing punctuation before the host is parsed. A closing paren is stripped only
when unbalanced, so `.../Ship_(disambiguation)` survives intact.

**FIX 3 — allowlist.** `example.com`, `api.example.com`, `opensource.org`,
`a.nel.cloudflare.com` added, each with an inline comment recording why.

**Explicitly not done:** gate 5 was not scoped to data files with headers/spec
marked out of scope. That would have made the coverage defect permanent by
design.

## Fail-closed regression check

Fixtures in `scripts/external_sources/_verify_integrity_scan.py`. The gate has
**not** become always-pass:

| fixture | expected | result |
|---|---|---|
| `<script>` in a JSON file | exit 1 | exit 1 |
| unexpected domain in a `.txt` (invisible to old glob) | exit 1 | exit 1 |
| unreadable file | exit 1, coverage incomplete | exit 1, `complete: false` |
| known-good, 6 files (5 non-JSON, 1 nested, 1 binary) | exit 0, 6/6 scanned | exit 0, 6/6 |

The 11 URL cases cover the exact strings that failed here, plus
`evil.example.net` and `pastebin.com/raw/abcd)` which must still be **rejected**
— and are. Under the old glob, the known-good fixture would have scanned 2 of 6
files.

## Gate 5 re-run — PASS on its own

```
exit code 0 | files_seen 75 | files_scanned 75 | files_unscanned 0
walk_errors NONE | coverage complete TRUE
content_indicator_hits NONE | unexpected_domains NONE
```

9 distinct domains, all allowlisted: api.star-citizen.wiki (149),
example.com (3), star-citizen.wiki (3), a.nel.cloudflare.com (2),
robertsspaceindustries.com (2), docs.star-citizen.wiki (1), api.example.com (1),
starcitizen.tools (1), opensource.org (1). All 75 files valid UTF-8.

## Finalized

Before renaming, all 75 files were re-hashed against the post-malware-scan set:
0 missing, 0 added, 0 changed. **The bytes that were scanned are the bytes that
were finalized.**

Renamed `20260801T021731Z.partial` -> **`20260801T021731Z`**.
`snapshot_status`: `partial` -> `complete`.

**Ordering compliance: SATISFIED.** Unlike source 1, this snapshot was never
renamed before its malware scan. Order was gates 1-4 pass -> gate 5 fail -> hold
at `.partial` -> fix script -> gate 5 pass -> rename.

## The initial failure is preserved, not erased

The manifest retains `gate_5.initial_run` with all 7 findings, the reported-PASS
that could not be trusted, the two script defects, what was changed, and
`snapshot_status_history` showing `partial` -> `complete`. Both integrity scan
reports are kept: `03_integrity_scan_report.json` (original, JSON-only) and
`03_integrity_scan_report_v2_fixed_script.json` (fixed, all 75 files).

Manifest: `data-layer/external-source-manifests/20260801T021731Z/03_star-citizen-wiki-api_manifest.json`
(32,789 bytes; per-file SHA-256 + byte size for all 75 files, retrieval script
SHA-256, gate script SHA-256 `a2e10488...`, resolved page size per collection,
per-page attempt counts).

`20260731T041451Z.partial` and `20260801T015346Z.partial.aborted__pagesize50`
were not read, merged, globbed or finalized against.

Nothing committed. Nothing pushed.
