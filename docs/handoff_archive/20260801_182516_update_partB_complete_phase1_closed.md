# UPDATE — PART B COMPLETE: source 6 landed and gated. Phase 1 is closed.

Snapshot `20260801T235530Z` is finalized. All five gates passed in order.

## Credential

Verified with **one request** to `/game_versions/` before any data endpoint was
touched — HTTP 200, `application/json`, envelope `status: "ok"`, data present.
The script refuses to pull if that check fails.

`.env` confirmed **gitignored and untracked**. Token: 40 hex chars, no stray
whitespace, `DATABASE_URL` intact.

I also fixed a defect in my own script before running it: its docstring claimed
the token was "loaded from `.env`" but nothing loaded it. It would have refused
to run on a token that was present. Fixtures re-run green after the fix.

## What landed

114 files, 12,402,823 bytes.

| endpoint | records |
|---|---:|
| `items_prices_all` | **23,734** |
| `terminals` | 823 |
| `vehicles_purchases_prices_all` | 288 |
| `companies` | 311 |
| `planets` | 324 |
| `outposts` | 117 |
| `categories` | 100 |
| `star_systems` | 96 |
| `moons` | 73 |
| `space_stations` | 60 |
| `cities` | 5 |
| **items, via 100 category queries** | **7,728 (5,566 with a UUID)** |

## The refused endpoint — recorded, not smoothed over

`GET /items/` returned **HTTP 400**:

```json
{"status":"requires_id_category_or_id_company_or_uuid","http_code":400,"data":[],"message":""}
```

The write gate rejected it and wrote nothing — which is why no HTTP 400 body is
sitting in the snapshot named `items.json`.

Coverage was obtained by fetching the **same documented endpoint** per category:
`/items/?id_category=<id>` for all 100 ids read from the `categories.json` this
run landed. All 100 returned HTTP 200 with a valid envelope; **0 rejected**.

This is not sibling-crawling — it is the endpoint parameterised exactly as its
own error message demands. The manifest records the attempt, the refusal, the
body, and how coverage was obtained.

**Honest limitation, also in the manifest:** item coverage is the union of 100
category queries, not a single authoritative enumeration. An item belonging to
no category would not appear. That gap is unmeasured, because the endpoint that
would measure it is the one the API refuses.

## Gates, in order

| # | gate | result |
|---|---|---|
| 1 | files present | PASS — 114 files, 0 zero-byte, 0 read errors |
| 2 | JSON parses | PASS — **113/113** parsed individually, 0 failures |
| 3 | file-type inspection | PASS — 114 inspected, 0 flagged |
| 4 | malware scan | PASS — MpCmdRun ScanType 3 `-DisableRemediation`, exit 0 |
| 5 | content-indicator scan | **PASS on re-run** — failed first, see below |

**Post-scan integrity:** 114 files / 12,402,823 bytes before **and** after. 0
missing, 0 added, 0 changed. The bytes scanned are the bytes finalized.

Gate 4 took 0.2s on 12.4 MB — RTP had already scanned these files as they were
written, so cached verdicts are expected. Recorded as an observation, not
claimed as a from-cold scan.

## Gate 5 failed first, and why the fix is not a whitewash

Initial run: **exit 1**, `unexpected_domains` non-empty — `api.uexcorp.uk`, in 3
of 114 files. All three are this pipeline's **own provenance records**
(`_pull_summary.json`, `_pull_stderr.log`, `_items_by_category_summary.json`),
which store request URLs. **Zero data files contained it.**

Added `api.uexcorp.uk` and `uexcorp.uk` to `ALLOWLIST_DOMAINS`. The reasoning,
recorded in both the code and the manifest: this is source 6's own canonical API
domain, and every other landed source's canonical domain was already on that
list (`api.star-citizen.wiki`, `scunpacked.com`, `starcitizen.tools`,
`robertsspaceindustries.com`). It was absent only because source 6 had never
been pulled.

**Deliberately contrasted with `facebook.github.io`**, which was refused an
allowlist entry during the source 1 re-acquisition. That was a foreign domain
inside third-party content whose cause — a bundled `.git` directory — could be
removed instead. There is no cause to remove here, because the domain *is* the
source.

**Fail-closed re-verified after the change:** the gate still exits 1 on a
`<script>` tag, on `evil.example.net` and `pastebin.com`, and on an unreadable
file. Two allowlist entries did not make it permissive.

## Tier C — stated explicitly

Recorded in the manifest as `data_tier: "C"` with a full statement. UEX declares
its own data community-reported and crowdsourced, with tolerances of **±20% on
commodities and ±100% on items**. Authoritative for aUEC prices and dealer
locations *only* because nothing else has them. **Never auto-promoted without
review.** Stated explicitly because a manifest silent on tier gets read as
game-file truth.

## Join key — recorded

`items.uuid` is the Star Citizen UUID. **5,566 of 7,728** item records carry
one. It joins directly to `reference` and `stdItem.UUID` in the already-landed
`fps-items.json`. The manifest carries the explicit instruction: **join on UUID,
do not build a name-matching path.**

## Credential rotation — outstanding, and it is yours

The token was pasted into a chat screenshot, so it must be treated as exposed.
**I could not rotate it** — that requires signing in to the UEX account. The
manifest records that this pull ran under a credential to be rotated, so a later
audit knows this snapshot was retrieved with a since-rotated one.

**Action for Sleven:** regenerate the token in the UEX account, then replace
`UEX_API_TOKEN` in `.env`.

## Correction to the status brief

The brief said Part B had stopped with 22 category files and "no data missing".
In fact the pull was **still running** when I resumed — PID 34692 was writing
`items_category_62.json` 26 seconds before I looked, and **39 of 100 categories
were still unfetched**. Gating then would have sealed an incomplete snapshot
*and* run the pre/post-scan hash comparison against a directory being actively
written, making the integrity check meaningless. I waited for it to finish; it
completed all 100 with 0 rejections.

## PHASE 1 IS COMPLETE

This is the first time that is true, and it is true now because source 6's gates
passed — not because the work was declared done.

- Source 1 (scunpacked-data) — complete, re-acquired without `.git`
- Source 2 (scunpacked.com) — complete
- Source 3 (api.star-citizen.wiki) — complete
- Source 4 — correctly ruled out, self-blocked on provenance
- Source 5 — correctly ruled out, not directly downloadable
- **Source 6 (UEX Corp) — complete**

Five sources collected, two correctly ruled out.

No data promoted into the database. This is Stage 1: collect and seal. Stage 2
does not exist yet.
