# Update — CC-07 fixed: scunpacked_com.py hardened (no pull, no commit)

Audit finding CC-07 confirmed by reading the script: `fetch()` called
`out_path.write_bytes(resp.content)` at line 36, **before** any reference to
`resp.status_code`. No retry, no rate-limit handling, `timeout=30`. Source 2 is
marked "complete" on the strength of a script that verified none of it.

Fixed against `api_star_citizen_wiki.py` as the reference implementation —
same patterns, not new ones. `+217 / -15`.

## FIX 1 — write-before-status

A response earns `<name>.json` only after all three checks pass, in order:
`status == 200`, Content-Type contains `json`, body parses. A rejected response
is recorded with `error` and `rejected_body_first_200_chars` and is **never**
written. `written_to_disk` and `file_path` (null until earned) make the outcome
explicit in the summary.

## FIX 2 — retry and timeout

- `Timeout` and `ConnectionError` caught and retried against `max_retries=5`
  with the same 3/6/9/12s backoff as the sibling script. Ceiling exhaustion
  re-raises the last exception, carrying its attempt log.
- `Retry-After` parsed in both RFC 7231 forms (delta-seconds and HTTP-date),
  clamped to `[0, 60]`, garbage falls back to 5s.
- Timeout raised 30s -> 180s.

**Honesty note on the timeout:** unlike the sibling script's 180s, this one is
**not** backed by a measurement — probing scunpacked.com would mean a pull, which
was out of scope. The comment in the code says so explicitly: 180s is headroom
chosen to match the sibling, reasoned from `/api/v2/ships.json` being a single
whole-collection document rather than a page. Recorded as headroom, not as an
observed worst case.

## FIX 3 — per-response metadata

`byte_size`, `sha256`, `attempts`, `attempt_log` (per-attempt outcome, exception
type, wait before next), on **every** response including rejected ones.

## Also changed — fail closed

`main()` now returns 1 if any endpoint did not land, and the script
`sys.exit`s on it. Previously it always exited 0 regardless of what came back,
which is how source 2 came to be marked complete.

## Verification — offline, `requests.get` and `time.sleep` stubbed, no network

`scripts/external_sources/_verify_scunpacked_com.py`, exit 0.

| case | files written | result |
|---|---:|---|
| HTML 500 (x5, ceiling exhausted) | 0 | rejected, first 200 chars kept |
| HTTP 200 + `application/json` + unparseable body | 0 | rejected |
| HTTP 200 + `text/html` | 0 | rejected |
| HTTP 200 + `application/json` + valid | 1 | written, sha256 + byte_size recorded |
| timeout attempt 1, then success | 1 | retried, 2 attempts, no crash |
| timeout + connection error, then success | 1 | 3 attempts logged |
| five consecutive timeouts | 0 | **raises** after 5, does not loop |
| 429 with `Retry-After: 7`, then success | 1 | honoured 7s wait |

Retry-After: 9 inputs incl. HTTP-date +5h -> 60, HTTP-date in past -> 0,
delta 9999 -> 60, negative -> 0, garbage/missing/empty -> 5. All within
`[0, 60]`, none raised.

## Status

**No pull performed.** No snapshot touched. Source 2's existing snapshot and
its "complete" status are untouched — note that status is still resting on the
old unverified pull, and re-landing source 2 with the fixed script is a separate
decision.

Not committed. Working tree only.
