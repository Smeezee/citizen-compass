"""
Retrieval script for api.star-citizen.wiki (source 3 of the 2026-07-31
external data landing run).

Pulls ONLY: vehicles, items, manufacturers, and the game-version record
itself - nothing else, per this run's documented scope. The OpenAPI spec
and /api/game-versions/default are fetched separately, before this script
runs, so the exact pinned version code can be passed in here explicitly
and used on every single request - it never floats or defaults per-page.

Usage:
  python api_star_citizen_wiki.py <output-dir> <pinned-version-code>

For each of vehicles/items/manufacturers, paginates sequentially (no parallel
requests) at that collection's own page size (see PAGE_SIZE_OVERRIDES), stops
when the response's own meta.last_page is reached, and honors HTTP 429 with
Retry-After. A response is only written to <collection>_page_<N>.json once it
has been confirmed to be a 200, with a JSON content type, and a parseable body
- see pull_collection. Prints a JSON summary per collection to stdout for the
manifest.
"""
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import requests

BASE = "https://api.star-citizen.wiki/api"
COLLECTIONS = ["vehicles", "items", "manufacturers"]
PAGE_SIZE = 200

# Per-collection page size. Default is PAGE_SIZE; only listed collections differ.
#
# vehicles=50: page[size]=200 returns HTTP 500 (an HTML error page, not JSON) on
# the vehicles endpoint. Probed 2026-07-31 against version 4.9.0-LIVE.12232306,
# one request per page size, no retries: size 20 -> HTTP 200, valid JSON, 20
# records; size 50 -> HTTP 200, valid JSON, 50 records; size 200 -> HTTP 500,
# text/html error page. The endpoint is not down - the page size is the fault.
# items and manufacturers are unaffected and deliberately stay at 200, where
# they already pull cleanly; there is no reason to make them pay for this.
PAGE_SIZE_OVERRIDES = {
    "vehicles": 50,
}
USER_AGENT = "citizen-compass-data-landing/1.0 (+https://github.com/Smeezee/citizen-compass)"
REQUEST_DELAY_SECONDS = 1.5

# Per-request timeout. Was 60s, which was too tight to be safe: the 2026-07-31
# probe measured vehicles pages at page[size]=50 taking 42.6 seconds, leaving
# under 30% headroom. A single slow response would then raise Timeout, and
# (before this change) Timeout was not caught in get_with_retry - so one slow
# page killed the whole run mid-pull. 180s gives a comfortable margin over the
# measured worst case; genuinely hung requests are still bounded.
REQUEST_TIMEOUT_SECONDS = 180

# Ceiling on any server-supplied Retry-After. A hostile or buggy value (or an
# HTTP-date far in the future) must not park the run for hours.
MAX_RETRY_AFTER_SECONDS = 60


def parse_retry_after(raw: str, default: int = 5) -> int:
    """Parse a Retry-After header into a bounded number of seconds.

    RFC 7231 7.1.3 allows TWO forms: delta-seconds ("120") and an HTTP-date
    ("Wed, 21 Oct 2015 07:28:00 GMT"). The previous code called int() straight
    on the raw header, which raises ValueError on the HTTP-date form and would
    have crashed the run at the worst possible moment - while the upstream was
    already asking us to back off. Both forms are handled here, anything
    unparseable falls back to `default`, and the result is clamped to
    [0, MAX_RETRY_AFTER_SECONDS].
    """
    if raw is None:
        return default
    raw = raw.strip()
    if not raw:
        return default
    try:
        seconds = int(raw)
    except ValueError:
        try:
            when = parsedate_to_datetime(raw)
        except (TypeError, ValueError, IndexError):
            return default
        if when is None:
            return default
        if when.tzinfo is None:
            when = when.replace(tzinfo=timezone.utc)
        seconds = int((when - datetime.now(timezone.utc)).total_seconds())
    return max(0, min(seconds, MAX_RETRY_AFTER_SECONDS))


def get_with_retry(url: str, params: dict, max_retries: int = 5) -> "tuple[requests.Response, list]":
    # Retrying the SAME endpoint/params a few times with backoff is not a
    # substitution (no different endpoint, no approximation) - it's the
    # documented-correct way to ride out a genuinely flaky upstream.
    #
    # Correction 2026-07-31, amended 2026-08-01: an earlier version of this
    # comment described the /vehicles HTML 500 at page[size]=200 as
    # "intermittent" and "transient", inferred from 2-of-3 manual attempts
    # failing, and treated retrying as the answer. That framing was wrong.
    #
    # The amendment matters: the fix comment first called the failure
    # "deterministic", which overstated the evidence by one data point. The full
    # record at page[size]=200 is 1 success in ~14 known attempts - run 1: 5/5
    # failed; run 2: 5/5 failed; run 1's manual curl tests: 2 of 3 failed, 1
    # SUCCEEDED; the 2026-07-31 probe: 1/1 failed. So it is near-deterministic,
    # not absolute, and the manifest's single recorded success is real rather
    # than a contradiction. Either way retrying 200 was never the answer, since
    # 20 and 50 both return valid JSON - see PAGE_SIZE_OVERRIDES.
    #
    # Retry stays for real transients (429s, genuine upstream blips); it is not
    # a fix for a bad request parameter.
    #
    # Timeout and ConnectionError are retryable here too. GET is idempotent, so
    # re-issuing the identical request is safe - it cannot double-create
    # anything upstream. They count against the SAME max_retries ceiling as
    # 429/5xx: a slow or dropped response costs an attempt, not the run. If the
    # ceiling is exhausted by exceptions the last one is re-raised, so the
    # failure still surfaces - but it surfaces having tried, not on first blip.
    attempts = []
    resp = None
    last_exc = None

    for attempt in range(max_retries):
        is_last = attempt == max_retries - 1
        try:
            resp = requests.get(
                url, params=params, headers={"User-Agent": USER_AGENT},
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            last_exc = e
            backoff = 3 * (attempt + 1)
            attempts.append({
                "attempt": attempt + 1,
                "outcome": "exception",
                "exception_type": type(e).__name__,
                "exception_message": str(e)[:200],
                "waited_seconds_before_next": None if is_last else backoff,
            })
            print(f"  {type(e).__name__} on attempt {attempt + 1}/{max_retries}"
                  f"{'' if is_last else f', retrying in {backoff}s'}", file=sys.stderr)
            if is_last:
                break
            time.sleep(backoff)
            continue

        last_exc = None
        if resp.status_code == 429:
            retry_after = parse_retry_after(resp.headers.get("Retry-After"))
            attempts.append({
                "attempt": attempt + 1,
                "outcome": "http_429",
                "status_code": 429,
                "retry_after_header": resp.headers.get("Retry-After"),
                "waited_seconds_before_next": None if is_last else retry_after,
            })
            print(f"  429 received, honoring Retry-After={retry_after}s (attempt {attempt + 1})", file=sys.stderr)
            if is_last:
                break
            time.sleep(retry_after)
            continue
        if 500 <= resp.status_code < 600:
            backoff = 3 * (attempt + 1)
            attempts.append({
                "attempt": attempt + 1,
                "outcome": "http_5xx",
                "status_code": resp.status_code,
                "waited_seconds_before_next": None if is_last else backoff,
            })
            print(f"  {resp.status_code} received, retrying in {backoff}s (attempt {attempt + 1}/{max_retries})", file=sys.stderr)
            if is_last:
                break
            time.sleep(backoff)
            continue

        attempts.append({
            "attempt": attempt + 1,
            "outcome": "response",
            "status_code": resp.status_code,
            "waited_seconds_before_next": None,
        })
        return resp, attempts

    # Ceiling exhausted. If the final attempt died with an exception there is no
    # response to hand back, so re-raise it rather than inventing one. If the
    # final attempt produced a 429/5xx, return it - the caller's write gate is
    # what decides it is not data.
    if attempts and attempts[-1]["outcome"] == "exception":
        # Carry the attempt log out with the exception so the caller can record
        # how many tries it actually took rather than assuming the ceiling.
        last_exc.attempts_log = attempts
        raise last_exc
    return resp, attempts


def pull_collection(name: str, version: str, out_dir: Path) -> dict:
    url = f"{BASE}/{name}"
    page_size = PAGE_SIZE_OVERRIDES.get(name, PAGE_SIZE)
    page = 1
    pages_meta = []
    total_records = 0
    last_page = None
    terminated_normally = False

    while True:
        params = {"version": version, "page[size]": page_size, "page[number]": page}
        try:
            resp, attempt_log = get_with_retry(url, params)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            # get_with_retry exhausted its ceiling on network errors. Record it
            # and stop THIS collection - don't let it kill the whole run and
            # discard collections that already landed cleanly.
            exhausted_log = getattr(e, "attempts_log", [])
            pages_meta.append({
                "page": page,
                "url": url,
                "page_size_used": page_size,
                "written_to_disk": False,
                "file_path": None,
                "attempts": len(exhausted_log),
                "attempt_log": exhausted_log,
                "error": (f"retry ceiling exhausted on {type(e).__name__}: {str(e)[:200]}"
                          f"; body NOT saved, stopping pagination for {name}"),
            })
            break

        meta_entry = {
            "page": page,
            "url": resp.url,
            "page_size_used": page_size,
            "attempts": len(attempt_log),
            "attempt_log": attempt_log,
            "status_code": resp.status_code,
            "content_type": resp.headers.get("Content-Type"),
            "etag": resp.headers.get("ETag"),
            "last_modified": resp.headers.get("Last-Modified"),
            "byte_size": len(resp.content),
            "sha256": hashlib.sha256(resp.content).hexdigest(),
            # Set only once the body has earned a final filename.
            "written_to_disk": False,
            "file_path": None,
        }

        # A response earns its final filename only after passing all three
        # checks below. Writing first and validating afterwards is what put an
        # HTML 500 error page on disk as vehicles_page_1.json in the runs of
        # 2026-07-31 - a file that looks like data, is named like data, and is
        # not data. A rejected response is recorded as an error here and is
        # never written to the snapshot; the excerpt is for diagnosis only.
        def reject(reason: str) -> None:
            meta_entry["error"] = f"{reason}; body NOT saved, stopping pagination for {name}"
            meta_entry["rejected_body_first_200_chars"] = resp.text[:200]
            pages_meta.append(meta_entry)

        if resp.status_code != 200:
            reject(f"non-200 status ({resp.status_code})")
            break

        content_type = (resp.headers.get("Content-Type") or "")
        if "json" not in content_type.lower():
            reject(f"non-JSON Content-Type ({content_type!r})")
            break

        try:
            body = resp.json()
        except Exception as e:
            reject(f"failed to parse JSON: {e}")
            break

        page_path = out_dir / f"{name}_page_{page}.json"
        page_path.write_bytes(resp.content)
        meta_entry["written_to_disk"] = True
        meta_entry["file_path"] = str(page_path)

        record_count = len(body.get("data", [])) if isinstance(body.get("data"), list) else (1 if body.get("data") else 0)
        meta_entry["record_count"] = record_count
        total_records += record_count

        meta = body.get("meta", {}) or {}
        last_page = meta.get("last_page", meta.get("pagination", {}).get("last_page") if isinstance(meta.get("pagination"), dict) else None)
        meta_entry["response_meta"] = meta
        pages_meta.append(meta_entry)

        if not last_page or page >= last_page or record_count == 0:
            terminated_normally = bool(last_page) and page >= (last_page or page)
            break

        page += 1
        time.sleep(REQUEST_DELAY_SECONDS)

    return {
        "collection": name,
        "pinned_version": version,
        "page_size_used": page_size,
        "pages": pages_meta,
        "pages_written_to_disk": sum(1 for p in pages_meta if p["written_to_disk"]),
        "pages_rejected": sum(1 for p in pages_meta if not p["written_to_disk"]),
        "max_attempts_on_any_page": max((p.get("attempts", 1) for p in pages_meta), default=0),
        "total_records": total_records,
        "last_page_reported": last_page,
        "pages_fetched": len(pages_meta),
        "pagination_terminated_normally": terminated_normally,
    }


def main():
    out_dir = Path(sys.argv[1])
    version = sys.argv[2]
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for name in COLLECTIONS:
        print(f"Pulling {name} @ version={version} ...", file=sys.stderr)
        results.append(pull_collection(name, version, out_dir))
        time.sleep(REQUEST_DELAY_SECONDS)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
