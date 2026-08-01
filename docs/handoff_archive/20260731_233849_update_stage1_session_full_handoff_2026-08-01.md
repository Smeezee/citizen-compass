# UPDATE — Stage 1 session handoff (source 1 closeout through CC-12/CC-10)

Full session record. Three commits made on `main`, **none pushed**. Database
untouched except read-only SELECTs inside an explicit
`SET TRANSACTION READ ONLY`. Live site untouched.

---

## 1. Source 1 manifest closed out — commit `124640f`

Snapshot `20260731T041451Z` (scunpacked-data, ~29,000 files). All five gates
have now been performed, months of them retroactively:

- `verify_snapshot_v2.py` run to completion — all 28,993 files hashed, all
  28,959 JSON files given a parse verdict. Coverage went from 40 files sampled
  (0.14%) to 100%.
- Report-only Defender scan performed (`MpCmdRun.exe -DisableRemediation`).
  `Start-MpScan` as originally specified was **not** run: all four
  `*ThreatDefaultAction` prefs are `0` (quarantine/remove) with RTP on, so it
  would have been free to mutate the snapshot under CLAUDE.md rule 1.
- v1 (08:10:15Z) and v2 (23:34:44Z) SHA256SUMS bracket the AV scan (16:19:12Z)
  and are identical across all 28,993 lines — proving nothing was altered
  rather than assuming it.

`protocol_compliance: "ordering_violated"` is recorded permanently. The folder
was renamed out of `.partial` **before** its malware scan, and that cannot be
retroactively satisfied. The manifest's acquisition block still says
`malware_scan.attempted: false` and `report_only_mode_confirmed: false`, which
**contradicts** the later `post_acquisition_verification` block. That
contradiction is deliberate and must not be reconciled — it is the record of
what went wrong. The guarantee this snapshot carries is "verified clean now",
not "never finalized while unverified".

---

## 2. CC-05 SOLVED — and the earlier diagnosis was WRONG

Two runs recorded the source 3 `/vehicles` failure as a persistent upstream
fault. **That conclusion is superseded.** A read-only probe at three page sizes,
one request each, pinned version `4.9.0-LIVE.12232306`:

| page[size] | HTTP | Content-Type | records | bytes |
|---:|---:|---|---:|---:|
| 20 | 200 | application/json | 20 | 1,652,791 |
| 50 | 200 | application/json | 50 | 3,271,789 |
| 200 | **500** | text/html | — | 40,622 |

The endpoint was never down. **The page size was the fault.** Do not inherit
the earlier manifests' "persistent upstream fault" / "intermittent" conclusion
as fact — it is superseded by measurement.

### 2a. Correction to a correction — the CC-05 citation is NOT fabricated

The 2026-07-31 cowork entry states the CC-05 provenance was invented, on the
grounds that run 1's manifest records only manual tests at `page[size]=200`.
**That correction is itself wrong.** It quotes `collections[0].failure_reason`
and stops there. The same manifest
(`external-source-manifests/20260731T031754Z/03_star-citizen-wiki-api_manifest.json`)
records verbatim, under `scope_boundaries_hit`:

> "...rather than silently dropping to a smaller size that manual testing
> showed was more reliable (**page[size]=20 succeeded on a manual test**)"

The citation exists. It is in a different field from the one that was checked.
**No amendment is needed.** Both fields are accurate; they describe different
tests.

### 2b. Correction to MY OWN wording — "deterministic" overstates it

I described the 200 failure as deterministic on the strength of one probe
request. The full record does not support that word:

- run 1: 5/5 attempts at 200 -> 500
- run 2: 5/5 attempts at 200 -> 500
- run 1 manual curl: 3 attempts at 200 -> 2 failed, **1 succeeded**
- probe: 1 attempt at 200 -> 500

That is 1 success in ~14 known attempts at `page[size]=200`. Overwhelmingly
reproducible, **not strictly deterministic**. The comment now in
`api_star_citizen_wiki.py` says "deterministic" and overstates the evidence by
one data point. Flagged for correction; **not silently edited**, because the
run-3 manifest that quotes the same wording is sealed.

This also dissolves the "unresolved contradiction" raised in the cowork entry:
the manifest's one recorded success at 200 and the probe's failure at 200 are
**both true**. The fault is near-deterministic at 200, not absolute.

---

## 3. `api_star_citizen_wiki.py` — four fixes

- **Per-collection page size.** `PAGE_SIZE_OVERRIDES = {"vehicles": 50}`;
  default stays 200 so items and manufacturers, which pull cleanly, are not
  made to pay for a defect affecting one collection.
- **Write-before-status.** A response earns its final filename only after
  `status == 200` AND a JSON content type AND a successful parse. Previously the
  body was written first — which is how an HTML 500 page landed on disk named
  `vehicles_page_1.json` and was counted as data.
- **Timeout 60s -> 180s**, against a measured 42.6s worst case (under 30%
  headroom before). `Timeout` and `ConnectionError` are now retryable against
  the same `max_retries=5` ceiling; previously an uncaught `Timeout` would kill
  the whole run mid-pull.
- **Retry-After.** `int()` was called straight on the raw header. RFC 7231
  permits an HTTP-date form, on which `int()` raises `ValueError` — **the run
  would have died at the exact moment the server was asking us to back off.**
  Both forms now parse, clamped to `[0, 60]`, garbage falls back to 5s.

---

## 4. `integrity_scan.py` — the gate had never scanned non-JSON files

`main()` globbed `*.json`. Every non-JSON file in **every snapshot this gate has
ever run against** — captured HTTP response headers, `openapi.yaml`, run logs —
was silently skipped while the script exited 0 and the gate reported **PASS**.

**This is not specific to one run.** Any earlier snapshot finalized on the
strength of this gate was finalized on incomplete coverage. Source 1's
`20260731T041451Z` has not been re-gated with the fixed script — open item.

Second, independent defect: `URL_RE` swallowed trailing punctuation into the
netloc, so `https://starcitizen.tools)` produced the host `starcitizen.tools)`,
which failed an allowlist that *does* contain `starcitizen.tools`. A false
positive manufactured entirely by the scanner.

**Fixes:** recursive walk of every file; byte-level reads so any type is
scannable; an unreadable file is reported UNSCANNED and **fails** the gate
rather than passing by omission; a `coverage` block; `trim_url()` stripping
trailing punctuation (unbalanced parens only); and `example.com`,
`api.example.com`, `opensource.org`, `a.nel.cloudflare.com` added to the
allowlist with inline reasons.

Regression-checked with fixtures — the gate still exits 1 on a real finding and
has **not** become always-pass: `<script>` in JSON -> 1; unexpected domain in a
`.txt` (invisible to the old glob) -> 1; unreadable file -> 1 with
`coverage.complete: false`.

---

## 5. Source 3 re-landed — `20260801T021731Z`, finalized

| collection | downloaded | API meta.total | match | page size | pages |
|---|---:|---:|:--:|---:|---:|
| vehicles | **295** | 295 | YES | 50 | 6 |
| items | 12,283 | 12,283 | YES | 200 | 62 |
| manufacturers | 152 | 152 | YES | 200 | 1 |

75 files, 85,674,557 bytes. Every page 200/`application/json` on the **first
attempt** — no 429, no 5xx, no retries. **Zero pages rejected by the write
gate.**

Version pin checked, not asserted: 12,578 records carry `.version`, **0** differ
from the pin. Non-pin versions appear only in `data[].loaner[].version` and
`data[].uex_prices.*.game_version` (1,311 entries at `4.8.2-LIVE.12030094`) —
embedded third-party data, not version float. **Stage 2 note: the UEX price data
in this snapshot is one game version stale.**

Gates 1-4 passed. **Gate 5 failed**, the folder was held at `.partial`, the gate
script was fixed (section 4), gate 5 was re-run and passed on its own, and only
then was the folder renamed. The initial failure and all 7 findings are retained
in the manifest — not erased. Ordering compliance **satisfied**, unlike source 1.

An earlier `page[size]=50`-globally run was aborted and quarantined at
`20260801T015346Z.partial.aborted__pagesize50` — renamed aside, never merged or
deleted. It no longer ends in `.partial`, so a `*.partial` glob will not see it;
**a `snapshots/*` glob still would.**

---

## 6. CC-07 — `scunpacked_com.py` hardened, commit `e1d60c9`

The script called `out_path.write_bytes(resp.content)` **before** any reference
to `resp.status_code`. No retry, no rate-limit handling, `timeout=30`. And
`main()` returned `None`, so the process **exited 0 unconditionally** — no
endpoint outcome could ever have failed a run.

Fixed against `api_star_citizen_wiki.py` as the reference implementation: same
write gate, same retry/backoff, same Retry-After parsing, per-response
`byte_size`/`sha256`/`attempts`/`attempt_log`, and `main()` now returns 1 if any
endpoint did not land.

---

## 7. Source 2 re-pulled — `20260801T042157Z`, finalized

| endpoint | records | previous | match | bytes | **measured elapsed** |
|---|---:|---:|:--:|---:|---:|
| `/api/v2/ships.json` | 156 | 156 | YES | 501,057 | **1.84s** |
| `/api/labels.json` | 63,375 | 63,375 | YES | 6,706,738 | **2.95s** |

Both first attempt. Both **byte-identical** to the previous run — matching
SHA-256 *and* ETag, compared against the previous run's **manifest** (a
provenance record); the old snapshot's files were never read.

All five gates passed in order; post-scan re-hash confirmed RTP altered nothing.
Historical caveat carried forward: `Last-Modified: Wed, 16 Nov 2022 20:52:36
GMT` — **not evidence of current game state.**

**The 180s timeout estimate was wrong by more than an order of magnitude.** It
had been reasoned as "at least as slow as one vehicles page (42.6s)"; measured
worst case is 2.95s, because these are static ETag-served files, not
query-backed pages. The comment now states the measurement. 180s retained as
~60x headroom, now justified by data rather than analogy.

---

## 8. Old source 2 snapshot marked `superseded`

`20260731T031754Z` was `snapshot_status: "complete"` — assigned by the
unconditional-exit-0 script above. Changed to **`superseded`**, append-only:
one field changed, everything recording the acquisition run untouched, snapshot
files untouched.

`superseded` = *the data is genuine, but the run's verification cannot be
trusted; a later verified run replaces it.* `failed` would have been as
inaccurate as `complete`.

Byte-identity establishes the old bytes are genuine upstream bytes. It does
**not** retroactively verify the old run — that snapshot is trustworthy by
inheritance, never by its own process.

Its `report_only_mode_confirmed: false` stays and is correct: it records
`Set-MpPreference` failing on a non-elevated session, **not** a scan failure.

**New file:** `docs/EXTERNAL_SOURCE_STATUS_VOCABULARY.md`. The project had **no
canonical definition** of the snapshot status vocabulary anywhere in `docs/` or
code — the values existed only as strings across manifests. That gap is now
documented rather than papered over.

---

## 9. CC-12 and CC-10 — investigated read-only, NOT implemented

**CC-12.** Both findings accurate and current; live DB and `models.py` agree, no
drift. `components.class_name` is nullable under `uq_components_class_name`
(Postgres allows unlimited NULLs, so the "natural key importers upsert on" is
unconstrained). `ships` has **only** `ships_pkey` — no unique constraint on
`(name, manufacturer_id)`.

Data is **clean**: components 8 rows, 0 NULL / 0 blank / 0 duplicate
`class_name`; ships 232 rows, 0 duplicate `(name, manufacturer_id)`. **Nothing
to resolve — this is the cheapest the fix will ever be.**

Proposed: `class_name` NOT NULL, add `uq_ships_name_manufacturer_id`, and a
deterministic `CC_SYNTH_<type>_<slug>` fallback plus a
`class_name_is_synthetic` boolean so a synthetic key is never presented as real.
The ALTERs succeed today; the real breakage is **behavioural** — importers that
insert a component without `class_name` start raising `NotNullViolation`.

**CC-10.** All five detail classes confirmed on bare `Base`; the live tables
have **zero** provenance columns. `last_verified_patch` is **not** in
`VerifiableMixin` — inheriting the mixin alone would not supply the field the
described failure mode turns on.

Tested rather than assumed: adding `VerifiableMixin` naively yields primary key
`['component_id', 'id']` — a composite PK — and **`create_all()` does not
raise**. The breakage is silent. Proposed instead: split out a
`ProvenanceMixin` (everything except `id`); additive, no existing table changes.
No checker breaks either way.

---

## Git ground truth (a prior entry asserted two conflicting versions)

`git rev-list --count origin/main..main` = **6**. Unpushed:

```
e1d60c9  Harden scunpacked_com.py against audit finding CC-07
e2a3907  Fix integrity_scan coverage defect, add per-collection page size, land source 3
124640f  Fix duplicate index, make pipeline gates fail closed, verify source 1 snapshot
55ac44d  Add headless Blender script to rescale sc-ships/ models
db18e02  Fix registry_sync_check crashing on non-ASCII ship names
84d9592  Add missing_or_corrupt_3d_model checker for sc-ships/
```

`origin/main` is at `41d216a`. **Nothing has been pushed.** The "17 commits
reached origin" claim is not supported by the local ref.

---

## Open decisions

1. **Re-gate source 1** (`20260731T041451Z`) with the fixed `integrity_scan.py`.
   Its gate 5 pass came from the version that skipped non-JSON files.
2. **Correct the "deterministic" wording** in `api_star_citizen_wiki.py`
   (section 2b) — 1 success at 200 is on record.
3. **CC-12 / CC-10** — both are written proposals awaiting a decision.
4. **Push, or not.** 6 commits sit unpushed; no push authorization has been
   given.
5. **`_verify_integrity_scan.py` and `_verify_scunpacked_com.py`** were
   committed as the evidence the gates fail closed. Remove if unwanted in-repo.

## Not done, deliberately

No push. No migration, no schema change, no database write. No existing
snapshot other than source 2's status field was modified. Nothing deleted
anywhere — the aborted run was renamed aside, not removed.
