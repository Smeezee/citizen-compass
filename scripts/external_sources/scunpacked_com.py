"""
Retrieval script for scunpacked.com (source 2 of the 2026-07-31 external
data landing run). Pulls exactly two documented endpoints, nothing else:
  - /api/v2/ships.json
  - /api/labels.json

This is "Historical legacy schema - not evidence of current game state" -
see this source's manifest for the full caveat. Does not crawl for sibling
endpoints; if other endpoints are noticed they are reported, not pulled.

Usage: python scunpacked_com.py <output-dir>
Writes each endpoint's raw response body to <output-dir>/<name>.json and
prints a JSON summary per request to stdout for the caller to fold into the
source manifest. Exits non-zero if any endpoint did not land cleanly.

Hardening 2026-08-01, audit finding CC-07. This script previously had no HTTP
status check, no retry and no rate-limit handling: it wrote resp.content to the
final filename before looking at resp.status_code, so an error page would be
saved as <name>.json and counted as data. Source 2 was marked "complete" on the
strength of a script that verified none of it. The fixes below mirror
api_star_citizen_wiki.py rather than inventing separate patterns:
  - a response earns its final filename only after status/content-type/parse
  - Timeout and ConnectionError are retryable against a max_retries ceiling
  - Retry-After is parsed in both RFC 7231 forms and clamped
  - per-response byte size, sha256, attempt count and attempt log are recorded
"""
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import requests

BASE = "https://scunpacked.com"
ENDPOINTS = [
    ("ships", "/api/v2/ships.json"),
    ("labels", "/api/labels.json"),
]
USER_AGENT = "citizen-compass-data-landing/1.0 (+https://github.com/Smeezee/citizen-compass)"
REQUEST_DELAY_SECONDS = 1.0  # polite delay between the two requests

# Per-request timeout. Was 30s, set with no measurement behind it.
#
# No timing measurement exists for THIS source - probing it would mean a pull,
# which is out of scope for this change - so this value is not derived from an
# observed worst case the way the sibling script's is. It matches
# api_star_citizen_wiki.py's 180s deliberately: /api/v2/ships.json is a single
# whole-collection document rather than a paginated page, so it is reasonable to
# expect it to be at least as slow as one page of vehicles, which measured
# 42.6s. 180s is headroom, not a measurement, and is recorded as such.
REQUEST_TIMEOUT_SECONDS = 180

# Ceiling on any server-supplied Retry-After. A hostile or buggy value (or an
# HTTP-date far in the future) must not park the run for hours.
MAX_RETRY_AFTER_SECONDS = 60


def parse_retry_after(raw: str, default: int = 5) -> int:
    """Parse a Retry-After header into a bounded number of seconds.

    RFC 7231 7.1.3 allows TWO forms: delta-seconds ("120") and an HTTP-date
    ("Wed, 21 Oct 2015 07:28:00 GMT"). Calling int() straight on the raw header
    raises ValueError on the HTTP-date form, which would kill the run at the
    worst possible moment - while the upstream is already asking us to back off.
    Both forms are handled here, anything unparseable falls back to `default`,
    and the result is clamped to [0, MAX_RETRY_AFTER_SECONDS].
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


def get_with_retry(url: str, max_retries: int = 5) -> "tuple[requests.Response, list]":
    # Retrying the SAME url a few times with backoff is not a substitution (no
    # different endpoint, no approximation) - it's the documented-correct way to
    # ride out a genuinely flaky upstream.
    #
    # Timeout and ConnectionError are retryable. GET is idempotent, so
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
                url, headers={"User-Agent": USER_AGENT},
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
    # final attempt produced a 429/5xx, return it - the write gate below is what
    # decides it is not data.
    if attempts and attempts[-1]["outcome"] == "exception":
        # Carry the attempt log out with the exception so the caller can record
        # how many tries it actually took rather than assuming the ceiling.
        last_exc.attempts_log = attempts
        raise last_exc
    return resp, attempts


def fetch(name: str, path: str, out_dir: Path, max_retries: int = 5) -> dict:
    url = BASE + path

    try:
        resp, attempt_log = get_with_retry(url, max_retries=max_retries)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        exhausted_log = getattr(e, "attempts_log", [])
        return {
            "endpoint": path,
            "url": url,
            "attempts": len(exhausted_log),
            "attempt_log": exhausted_log,
            "written_to_disk": False,
            "file_path": None,
            "error": f"retry ceiling exhausted on {type(e).__name__}: {str(e)[:200]}; body NOT saved",
        }

    meta = {
        "endpoint": path,
        "url": resp.url,
        "attempts": len(attempt_log),
        "attempt_log": attempt_log,
        "status_code": resp.status_code,
        "redirects": [r.url for r in resp.history],
        "content_type": resp.headers.get("Content-Type"),
        "content_length_header": resp.headers.get("Content-Length"),
        "etag": resp.headers.get("ETag"),
        "last_modified": resp.headers.get("Last-Modified"),
        "byte_size": len(resp.content),
        "sha256": hashlib.sha256(resp.content).hexdigest(),
        # Set only once the body has earned a final filename.
        "written_to_disk": False,
        "file_path": None,
    }

    # A response earns its final filename only after passing all three checks
    # below. Writing first and validating afterwards is the CC-07 defect: an
    # error page saved as <name>.json is a file that looks like data, is named
    # like data, and is not data. A rejected response is recorded as an error
    # here and is never written to the snapshot; the excerpt is for diagnosis.
    def reject(reason: str) -> dict:
        meta["error"] = f"{reason}; body NOT saved"
        meta["rejected_body_first_200_chars"] = resp.text[:200]
        return meta

    if resp.status_code != 200:
        return reject(f"non-200 status ({resp.status_code})")

    content_type = resp.headers.get("Content-Type") or ""
    if "json" not in content_type.lower():
        return reject(f"non-JSON Content-Type ({content_type!r})")

    try:
        json.loads(resp.content)
    except Exception as e:
        return reject(f"failed to parse JSON: {e}")

    out_path = out_dir / f"{name}.json"
    out_path.write_bytes(resp.content)
    meta["written_to_disk"] = True
    meta["file_path"] = str(out_path)
    return meta


def main() -> int:
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for index, (name, path) in enumerate(ENDPOINTS):
        if index:
            time.sleep(REQUEST_DELAY_SECONDS)
        print(f"Fetching {name} from {BASE}{path} ...", file=sys.stderr)
        results.append(fetch(name, path, out_dir))
    print(json.dumps(results, indent=2))

    # Fail closed: an endpoint that did not land is a failed run, not a quiet
    # partial success. Source 2 was previously marked "complete" on the strength
    # of a script that always exited 0 regardless of what came back.
    rejected = [r for r in results if not r["written_to_disk"]]
    if rejected:
        print(f"{len(rejected)} of {len(results)} endpoint(s) did not land: "
              f"{', '.join(r['endpoint'] for r in rejected)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
