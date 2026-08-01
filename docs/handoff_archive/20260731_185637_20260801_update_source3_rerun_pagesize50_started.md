# Update — source 3 re-run at page[size]=50 started

Following the read-only probe that showed `page[size]=200` is the fault (not the
endpoint), `PAGE_SIZE` in `scripts/external_sources/api_star_citizen_wiki.py:29`
was changed `200` -> `50` and source 3 is being re-run.

## Run

- run_id: `20260801T015346Z`
- snapshot dir: `data-layer/external-sources/api.star-citizen.wiki/snapshots/20260801T015346Z.partial`
- Landed into `.partial` and it **stays** there until the gates run, in order.
  This is the correction to the source 1 ordering violation — no rename before
  the scan this time.

## Preliminary requests (complete)

| file | status | bytes | sha256 |
|---|---:|---:|---|
| game_version_default.json | 200 | 162 | `4ed896a1c01e360df36716247f9a25a765c76c0173347017d530a9eeef2ad406` |
| openapi.yaml | 200 | 710,528 | `8b259bb9a44c1355e87228f1708a2913ad2d80298dce7d3da2c0ee984498a589` |

- Pinned version: `4.9.0-LIVE.12232306` — identical code to the previous two runs.
- The openapi.yaml hash is **byte-identical** to run `20260731T041451Z`, so the
  spec has not changed between runs.
- game_version_default.json's hash differs from the prior run only because
  `meta.processed_at` differs (`2026-07-31 19:37:48` vs `2026-07-30 19:37:32`).
  The `data` block is unchanged.

## Known cost of this change

`PAGE_SIZE` is global, so `items` drops from 62 requests to ~246 for the same
12,283 records. It worked fine at 200; it is only slower at 50. Flagged as a
side effect of the requested change, not a problem with the data. If this
becomes annoying, the fix is a per-collection page size rather than a global
constant — not done, since it wasn't asked for.

## Status

Pull running in background. Vehicles started. Not yet complete — no counts to
report and none will be guessed. Gates (integrity scan, malware scan, finalize)
have NOT run yet. Nothing committed.
