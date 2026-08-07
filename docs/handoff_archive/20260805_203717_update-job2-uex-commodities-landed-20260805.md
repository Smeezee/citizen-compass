# Update — job 2 of 4: UEX commodity endpoints called. "Screenshots are the only route" is REFUTED.

**When:** 2026-08-05

## The headline

**UEX serves commodity prices, and it always would have.** The 1 Aug pull never
asked. Searching that snapshot's `_pull_summary.json` for `commodit` returns
nothing — the gap was in the **request list**, not in the API. Every plan since
has rested on an assertion that was never tested.

New sealed snapshot: `data-layer/external-sources/uexcorp/snapshots/20260806T033315Z`

## Row counts per endpoint

| Endpoint | Result | Rows |
|---|---|---|
| `/commodities/` | **200** | **204** |
| `/commodities_prices_all/` | **200** | **2,597** |
| `/commodities_raw_prices_all/` | **200** | **335** |
| `/commodities_status/` | **200** | legend dict (buy/sell status codes) |
| `/commodities_averages/` | **400** | requires `id_commodity` |
| `/commodities_prices_history/` | **400** | requires `id_terminal` |

The two 400s are **parameter requirements, not permission failures** —
`{"status":"missing_id_commodity","message":"Commodity not provided"}` and
`{"status":"missing_id_terminal","message":"Terminal not specified"}`. The
credential was verified against `/game_versions/` before the run and the other
four returned 200. Same shape as the bare `/items/` endpoint this source already
documents. Neither body was written to disk — write-before-status held.

Coverage: **2,597 price rows across 123 commodities × 135 terminals.**

## The freshness question — timestamp, NOT game_version

**Prices carry `date_added` and `date_modified` (Unix epoch). There is no
`game_version`, `patch` or `build` field on any commodity price row.**

| | days |
|---|---|
| min / p25 / median | 0 / 0 / **1** |
| p75 / p90 | 4 / 9 |
| max | 509 |

Buckets: **1,389 rows ≤1 day**, 883 ≤7d, 320 ≤30d, 3 ≤90d, 2 >365d.
Newest row `2026-08-06T03:07:17Z` — **eight minutes before the pull**. Oldest
`2025-03-14`.

**So coverage and freshness are both genuinely good — but they are not patch
provenance.** Without a game_version a price cannot be attributed to a patch. A
row nine days old may straddle a patch boundary and nothing in the data says so.
That is the distinction the work order asked for, and it cuts both ways:

- **Against the collector's price role:** UEX already has broad, near-live
  commodity prices. Screenshotting shops to obtain a number UEX refreshed an
  hour ago is redundant.
- **For it:** the collector can stamp `patch` and `build` on every observation —
  the grabber already does, read from `Game.log`. That is precisely what UEX
  cannot supply. The defensible role is **patch-attributed** observation, not
  price coverage.

I am reporting that trade-off rather than deciding it — "may delete a build" is
Sleven's call.

## Gating, as source 6 was gated

`verify_snapshot_v2.py 2.0.0`, **inspection_complete: true** — 6 files, 0 JSON
parse failures, 0 ext/content mismatches, 0 active-content hits, 0 read errors,
0 walk errors, 0 duplicate hashes, 0 changed during run. SHA256 for every file.

Two "unexpected domain" flags: `api.uexcorp.uk` appearing in `_pull_summary.json`
and `_pull_stderr.log` — files **this pull wrote itself**, not downloaded
payload. Benign, and recorded in the manifest rather than suppressed.

Manifest:
`data-layer/external-source-manifests/20260806T033315Z/06_uex-corp_commodities_manifest.json`
— **data_tier C**, UEX's own ±20% commodity tolerance stated.
**Nothing promoted to the database.**

## A silent failure found and fixed in uex_corp.py

The script's docstring said the token was "loaded from .env". The
`python-dotenv` import was wrapped in `try/except ImportError` with a **bare
pass** — and python-dotenv is **not installed** in this interpreter. So `.env`
was never read, and the script reported *"UEX_API_TOKEN is not set. Refusing to
run."* while the token sat in `.env` the whole time.

That is a silent failure reported as a different, plausible failure: the message
sent a reader hunting for a missing credential that was never missing, while the
real cause was swallowed by the bare `pass`.

Fixed by parsing `.env` directly — removing the dependency rather than adding
one, which also avoids installing a package outside the repo (hard rule 6) — and
by making the failure name which step failed and whether `.env` exists. The
existing `_verify_uex_corp.py` fixture suite still passes.

## Credential handling

Token went from `.env` into the request header and nowhere else. **Not printed,
logged, echoed, or written into any snapshot or manifest file.** I confirmed its
presence by length only (40 chars).

**Standing warning, repeated because it is independent of this job: that token
was exposed in a screenshot and has still not been rotated.** It should be
rotated at UEX regardless of this work order — I cannot do that from here.

## Not done

`/commodities_averages/` and `/commodities_prices_history/` need per-commodity
and per-terminal parameterisation — 123 and 135+ requests respectively. The
precedent exists (`fetch_items_by_category`). Not attempted in this run; flagged
rather than silently skipped.

**Nothing staged or committed.**

**Next:** job 3 — the unreleased-content filter, which the work order flags as a
possible live defect.
