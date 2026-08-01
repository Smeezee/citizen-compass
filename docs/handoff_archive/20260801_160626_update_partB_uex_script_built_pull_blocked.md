# UPDATE — PART B: UEX script written and proven; pull BLOCKED on the token

The script half of Part B is done and tested. The pull half cannot start.

## Written: `scripts/external_sources/uex_corp.py`

Meets the standard the other retrieval scripts now meet. Every requirement below
exists because it was a real defect elsewhere in this project:

- **Write-before-status forbidden.** A response earns its final filename only
  after HTTP 200, a JSON content type, a successful parse, **and** a valid UEX
  envelope. Rejected responses are never written.
- **`Timeout`/`ConnectionError` retryable** against a 5-attempt ceiling with
  3/6/9/12s backoff; exhaustion re-raises carrying its attempt log.
- **`Retry-After` parsed in both RFC 7231 forms**, clamped to `[0, 60]`, with a
  fallback for garbage.
- Per-response `byte_size`, `sha256`, `attempts`, `attempt_log`,
  `elapsed_seconds`, `record_count`.
- **`main()` returns 1 if any endpoint did not land**, and returns 1 rather than
  attempting anything if `UEX_API_TOKEN` is absent.
- Sends `X-Client-Version`, so an outdated script cannot quietly keep pulling
  against a changed contract.

**One check beyond the brief.** UEX wraps everything as
`{"status": "ok", "data": ...}`. A 200 carrying `status: "error"`, or no `data`
key, is an application-level failure. HTTP status alone is not sufficient here,
so the envelope is validated before anything is written — otherwise an error
envelope would land as a `.json` file and count as a successful endpoint.

## Rule 12 — the failure paths were executed, not assumed

`scripts/external_sources/_verify_uex_corp.py`, offline, `requests.get` stubbed.

**Must-fail cases, each writing zero files:**

| case | result |
|---|---|
| HTTP 401 (the credential case) | rejected |
| HTTP 500 x5, ceiling exhausted | rejected |
| unparseable body behind 200 + JSON content-type | rejected |
| 200 with HTML content-type | rejected |
| 200, valid JSON, **not** a UEX envelope | rejected |
| 200, envelope shape, `status != "ok"` | rejected |
| 429 x5 with `Retry-After`, ceiling exhausted | rejected, all 5 logged as `http_429` |
| five consecutive timeouts | rejected, 5 attempts recorded |

**Must-succeed cases** — without these, eight rejections would be equally
consistent with a script that rejects everything:

| case | result |
|---|---|
| 200 + valid envelope | written, `record_count` 1, sha256 + byte_size + elapsed recorded |
| 429 then success | recovered, waited exactly the 7s the header asked for |
| timeout then success | recovered, 2 attempts |

Retry-After: 8 inputs including HTTP-date +5h -> 60, past date -> 0, `9999` ->
60, garbage -> 5. All within `[0, 60]`, none raised.

`main()` with no token returned **1** and attempted nothing.

## BLOCKED: the token value does not exist on disk

`.env` is **gitignored** (`.gitignore:4`) **and untracked** — both confirmed,
not just the first.

`UEX_API_TOKEN` is absent. Searching `docs/`, `inbox/`, `scripts/` and `.env`
found exactly two occurrences of the string `UEX_API_TOKEN=`, and both are
**instruction text**:

- `docs/workorder-finish-phase1.md:49`
- `docs/workorder-task2-source1-reacquisition.md:111`

Both read "write it to `.env` as `UEX_API_TOKEN=`" with nothing after it. The
account metadata was supplied — handle `slevenkoal`, UID 92424, app
`Citizen-Compass`, ACTIVE — but **the secret itself was never provided in any
message or file I can see.**

I will not invent a token (rule 11), and the work order itself forbids beginning
a pull on an unverified credential.

## What unblocks it

Paste the token. Then the remaining work is short and already built:

1. Write it to `.env` as `UEX_API_TOKEN=...`
2. `uex_corp.py` runs its own single-request credential check first and refuses
   to pull if it fails
3. Pull the 12 in-scope endpoints
4. Five gates in order, malware scan before the rename, re-hash after
5. Manifest recording **Tier C** explicitly, the `items.uuid` join key, the
   scope boundary, and that the pull ran under a since-rotated credential
6. Regenerate the token, since it was exposed in a screenshot

## Scope recorded for the manifest when it runs

12 documented endpoints, no sibling crawling: `items`, `items_prices_all`,
`terminals`, `vehicles_purchases_prices_all`, `categories`, `companies`,
`star_systems`, `planets`, `moons`, `cities`, `outposts`, `space_stations`.

**Join key:** UEX `items.uuid` is the Star Citizen UUID and matches `reference`
/ `stdItem.UUID` in the already-landed `fps-items.json` — a direct UUID join. No
name-matching path will be built.

**Tier C**, to be stated explicitly in the manifest: community-reported,
UEX-stated tolerances of ±20% on commodities and ±100% on items. Authoritative
for aUEC prices and dealer locations only because nothing else has them. Never
auto-promoted without review.

## Phase 1 status

**NOT complete, and I am not calling it complete.** Source 6 has not been
pulled. Another AI already declared Phase 1 done while source 6 had never been
started — that is exactly the claim this note exists to avoid repeating.

Moving to Part C.
