# Update — source 3 full pull landed; 4 of 5 gates pass, folder stays .partial

Run `20260801T021731Z`. All three collections landed complete and match the
API's own totals exactly. The snapshot is NOT finalized: gate 5 did not pass
across all files. Folder remains `.partial`, which is a correct outcome.

## Counts — all match, zero rejections, zero retries

| collection | downloaded | API meta.total | match | page size | pages | max attempts | rejected |
|---|---:|---:|:--:|---:|---:|---:|---:|
| vehicles | 295 | 295 | YES | 50 | 6 | 1 | 0 |
| items | 12,283 | 12,283 | YES | 200 | 62 | 1 | 0 |
| manufacturers | 152 | 152 | YES | 200 | 1 | 1 | 0 |

- Every page: HTTP 200, `application/json`, first attempt. No 429s, no 5xx, no
  timeout or connection retry anywhere in the run.
- **Zero pages rejected by the write gate.** The vehicles page-size fix worked:
  6 clean pages where the previous two runs produced an HTML 500 error page.
- Items and manufacturers matched last run's 12,283 / 152 — confirmed from this
  run's own responses, not assumed.
- Final: **75 files, 85,674,557 bytes.**

## Version pin — checked, not asserted

Pin `4.9.0-LIVE.12232306`, fetched first and used on every request.

- 12,578 records carry a top-level `.version`; **0** differ from the pin.
- Non-pin versions appear only in `data[].loaner[].version` (embedded loaner
  vehicles, own version) and `data[].uex_prices.*.game_version` (1,311 entries
  at `4.8.2-LIVE.12030094`). Both are properties of embedded third-party data,
  not version float. **Stage 2 note: the UEX price data here is one game
  version stale.**

## Gates, in order

| # | gate | result |
|---|---|---|
| 1 | files present | PASS — 6/6, 62/62, 1/1, contiguous; no zero-byte files |
| 2 | JSON parses | PASS — all 71 .json parsed individually, not sampled; 0 failures |
| 3 | file-type inspection | PASS — all 75 by magic bytes; no executables/archives; 0 mismatches |
| 4 | malware scan | PASS — Defender MpCmdRun, ScanType 3, `-DisableRemediation`, exit 0, no threats |
| 5 | content-indicator scan | **FAIL** |

Gate 4 detail: signatures 1.455.449.0, engine 1.1.26060.3008, report-only
confirmed (all four `*ThreatDefaultAction` are 0 and RTP is on, so
`-DisableRemediation` was mandatory). Scan reported start and finish in the
same second — RTP had already scanned these files as they were written, so
cached verdicts are expected. Recorded as an observation, not claimed as a
from-cold full-content scan.

## Post-scan integrity — RTP altered nothing

| | pre-scan | post-scan | delta |
|---|---:|---:|---:|
| file count | 75 | 75 | 0 |
| total bytes | 85,674,557 | 85,674,557 | 0 |

Every file SHA-256'd immediately before and immediately after the scan. Zero
missing, zero added, zero changed hashes or sizes. **CONFIRMED.**

## Why gate 5 failed

`integrity_scan.py` globs `*.json` only — 71 of 75 files. Over those it exited
**0**: zero indicator hits, zero unexpected domains, one domain found
(`api.star-citizen.wiki`, 141 occurrences).

Running the **same** `scan_file()` logic over the 4 non-JSON files returned
non-empty `unexpected_domains`:

- `game_version_default.headers`, `openapi.headers` -> `a.nel.cloudflare.com`
  (Cloudflare Network Error Logging endpoint, in captured HTTP response
  headers, not in any data file)
- `openapi.yaml` -> `example.com`, `api.example.com` (RFC 2606 documentation
  domain, in the spec's own examples), `opensource.org` (MIT licence link), and
  four entries that are allowlisted domains with trailing markdown punctuation
  swallowed into the netloc by `URL_RE` — `starcitizen.tools)`,
  `star-citizen.wiki).\n\n`, `docs.star-citizen.wiki)\n\n`,
  `api.star-citizen.wiki` + backtick. Scanner artifacts, not real domains.

**No active-content indicator was found in any file.** Every finding is
explainable and none is an unexpected third-party data source. That is an
argument for updating `ALLOWLIST_DOMAINS` and tightening `URL_RE` — it is not
authority to call a failing gate passed. Fail closed: **not renamed.**

## Decision needed from Sleven

Gate 5 is failing on scanner precision, not on evidence of a problem. Options,
none taken:

1. Add `a.nel.cloudflare.com`, `example.com`, `api.example.com`,
   `opensource.org` to `ALLOWLIST_DOMAINS`.
2. Tighten `URL_RE` so trailing `)`, backtick and newline are not captured into
   the netloc — this alone clears 4 of the 7.
3. Scope gate 5 to data files only and record headers/spec as out of scope.

Once decided and re-run clean, the rename off `.partial` is a one-step follow-up.

## Artifacts

- Manifest: `data-layer/external-source-manifests/20260801T021731Z/03_star-citizen-wiki-api_manifest.json`
  (per-file SHA-256 + byte size for all 75 files, script SHA-256
  `a89a60d8...`, resolved page size per collection, per-page attempt counts).
- Gate reports, pre/post-scan hash sets, and `_build_manifest.py` alongside it.
- Snapshot: `.../snapshots/20260801T021731Z.partial` — untouched since the scan.
- `20260731T041451Z.partial` and `20260801T015346Z.partial.aborted__pagesize50`
  were not read, merged, globbed or finalized against at any point.

Nothing committed. Nothing pushed.
