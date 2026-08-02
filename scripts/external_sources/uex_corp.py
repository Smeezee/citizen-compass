"""
Retrieval script for the UEX Corp API (source 6 of the external data landing).

WHAT THIS SOURCE IS, AND IS NOT
-------------------------------
UEX is **Tier C**: community-reported and crowdsourced, with tolerances UEX
states itself as +/-20% on commodities and +/-100% on items. It is authoritative
for aUEC prices and in-game dealer locations only because nothing else has them,
and it is NEVER auto-promoted without review. Any manifest written from this
script must say so explicitly - a manifest silent on tier will be read as
game-file truth.

It is also the only source that links an item to a terminal to a price. Sources
1, 2 and 3 give stats, names, coordinates and a location graph; none of them
joins those three things.

THE JOIN KEY
------------
UEX `items.uuid` is the Star Citizen UUID, and the already-landed
`fps-items.json` carries the same UUIDs in `reference` and `stdItem.UUID`. Those
join directly. Do NOT build a name-matching path - that is where this kind of
integration rots.

Usage:
  python uex_corp.py <output-dir>

Requires UEX_API_TOKEN in the environment (loaded from .env). Writes each
endpoint's raw response body to <output-dir>/<name>.json and prints a JSON
summary per request to stdout for the manifest. Exits non-zero if any endpoint
did not land.

STANDARD THIS MEETS
-------------------
Every requirement below exists because it was a real defect somewhere in this
project:
  - write-before-status is forbidden: a response earns its final filename only
    after status 200, a JSON content type, and a successful parse
  - Timeout/ConnectionError retryable against a ceiling with backoff
  - Retry-After parsed in BOTH RFC 7231 forms and clamped (calling int() on the
    HTTP-date form raised ValueError and killed a run here, at the exact moment
    the server was asking us to back off)
  - per-response byte_size, sha256, attempts, attempt_log, elapsed_seconds
  - main() returns 1 if any endpoint did not land (a main() returning None is
    precisely how source 2 was marked "complete" on a run that verified nothing)
"""
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import requests

try:
    from dotenv import load_dotenv
    # The token lives in .env, which is gitignored and untracked. Without this
    # the script's own docstring ("loaded from .env") would be a lie and it
    # would refuse to run for a token that is actually present.
    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
except ImportError:  # dotenv is optional; a pre-exported env var still works
    pass

BASE = "https://api.uexcorp.uk/2.0"

# Documented endpoints in scope. Nothing else is pulled and no sibling endpoint
# is crawled for - the scope boundary is recorded in the manifest.
ENDPOINTS = [
    # item -> terminal -> price, the reason this source exists
    ("items", "/items/"),
    ("items_prices_all", "/items_prices_all/"),
    ("terminals", "/terminals/"),
    ("vehicles_purchases_prices_all", "/vehicles_purchases_prices_all/"),
    # foreign keys referenced by the above
    ("categories", "/categories/"),
    ("companies", "/companies/"),
    # location hierarchy, so a terminal address means something
    ("star_systems", "/star_systems/"),
    ("planets", "/planets/"),
    ("moons", "/moons/"),
    ("cities", "/cities/"),
    ("outposts", "/outposts/"),
    ("space_stations", "/space_stations/"),
]

USER_AGENT = "citizen-compass-data-landing/1.0 (+https://github.com/Smeezee/citizen-compass)"

# Sending a client version means an outdated script cannot quietly keep pulling
# against a changed contract.
CLIENT_VERSION = "1.0.0"

REQUEST_DELAY_SECONDS = 0.6  # quota is 120/min; this stays well inside it

# Per-request timeout. Not derived from a measurement for this source - no pull
# has ever run - so it is deliberate headroom, matching the sibling scripts,
# and is recorded as headroom rather than as an observed worst case.
REQUEST_TIMEOUT_SECONDS = 180

MAX_RETRY_AFTER_SECONDS = 60

EXIT_OK = 0
EXIT_FAILED = 1
EXIT_USAGE = 2


def parse_retry_after(raw, default=5):
    """Parse Retry-After into a bounded number of seconds.

    RFC 7231 7.1.3 allows delta-seconds ("120") and an HTTP-date
    ("Wed, 21 Oct 2015 07:28:00 GMT"). int() on the HTTP-date form raises
    ValueError. Both are handled; anything unparseable falls back to `default`;
    the result is clamped to [0, MAX_RETRY_AFTER_SECONDS].
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


def _headers(token):
    return {
        "Authorization": f"Bearer {token}",
        "User-Agent": USER_AGENT,
        "X-Client-Version": CLIENT_VERSION,
        "Accept": "application/json",
    }


def get_with_retry(url, token, max_retries=5):
    """Return (response, attempts). Raises the last exception if the ceiling is
    exhausted by Timeout/ConnectionError - having tried, not on the first blip.

    GET is idempotent, so re-issuing the identical request is safe.
    """
    attempts = []
    resp = None
    last_exc = None

    for attempt in range(max_retries):
        is_last = attempt == max_retries - 1
        started = time.monotonic()
        try:
            resp = requests.get(url, headers=_headers(token),
                                timeout=REQUEST_TIMEOUT_SECONDS)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            last_exc = e
            backoff = 3 * (attempt + 1)
            attempts.append({
                "attempt": attempt + 1,
                "outcome": "exception",
                "elapsed_seconds": round(time.monotonic() - started, 2),
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
        elapsed = round(time.monotonic() - started, 2)

        if resp.status_code == 429:
            retry_after = parse_retry_after(resp.headers.get("Retry-After"))
            attempts.append({
                "attempt": attempt + 1, "outcome": "http_429", "status_code": 429,
                "elapsed_seconds": elapsed,
                "retry_after_header": resp.headers.get("Retry-After"),
                "waited_seconds_before_next": None if is_last else retry_after,
            })
            print(f"  429 received, honoring Retry-After={retry_after}s "
                  f"(attempt {attempt + 1})", file=sys.stderr)
            if is_last:
                break
            time.sleep(retry_after)
            continue

        if 500 <= resp.status_code < 600:
            backoff = 3 * (attempt + 1)
            attempts.append({
                "attempt": attempt + 1, "outcome": "http_5xx",
                "status_code": resp.status_code, "elapsed_seconds": elapsed,
                "waited_seconds_before_next": None if is_last else backoff,
            })
            print(f"  {resp.status_code} received, retrying in {backoff}s "
                  f"(attempt {attempt + 1}/{max_retries})", file=sys.stderr)
            if is_last:
                break
            time.sleep(backoff)
            continue

        attempts.append({
            "attempt": attempt + 1, "outcome": "response",
            "status_code": resp.status_code, "elapsed_seconds": elapsed,
            "waited_seconds_before_next": None,
        })
        return resp, attempts

    if attempts and attempts[-1]["outcome"] == "exception":
        last_exc.attempts_log = attempts
        raise last_exc
    return resp, attempts


def fetch(name, path, out_dir, token, max_retries=5):
    url = BASE + path

    try:
        resp, attempt_log = get_with_retry(url, token, max_retries=max_retries)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        exhausted = getattr(e, "attempts_log", [])
        return {
            "endpoint": path, "url": url,
            "attempts": len(exhausted), "attempt_log": exhausted,
            "written_to_disk": False, "file_path": None,
            "error": f"retry ceiling exhausted on {type(e).__name__}: "
                     f"{str(e)[:200]}; body NOT saved",
        }

    meta = {
        "endpoint": path,
        "url": resp.url,
        "attempts": len(attempt_log),
        "attempt_log": attempt_log,
        "elapsed_seconds": attempt_log[-1].get("elapsed_seconds") if attempt_log else None,
        "status_code": resp.status_code,
        "content_type": resp.headers.get("Content-Type"),
        "etag": resp.headers.get("ETag"),
        "last_modified": resp.headers.get("Last-Modified"),
        "byte_size": len(resp.content),
        "sha256": hashlib.sha256(resp.content).hexdigest(),
        "written_to_disk": False,
        "file_path": None,
    }

    def reject(reason):
        meta["error"] = f"{reason}; body NOT saved"
        meta["rejected_body_first_200_chars"] = resp.text[:200]
        return meta

    # A response earns its final filename only after ALL of these pass.
    if resp.status_code != 200:
        return reject(f"non-200 status ({resp.status_code})")

    content_type = resp.headers.get("Content-Type") or ""
    if "json" not in content_type.lower():
        return reject(f"non-JSON Content-Type ({content_type!r})")

    try:
        body = json.loads(resp.content)
    except Exception as e:
        return reject(f"failed to parse JSON: {e}")

    # UEX wraps everything as {"status": "ok", "data": ...}. A 200 carrying a
    # non-ok envelope is an application-level failure and must not be written
    # as data - HTTP status alone is not sufficient here.
    if not isinstance(body, dict) or "data" not in body:
        return reject("response is not a UEX envelope (no 'data' key)")
    envelope_status = body.get("status")
    if envelope_status != "ok":
        return reject(f"UEX envelope status is {envelope_status!r}, not 'ok'")

    data = body["data"]
    meta["record_count"] = len(data) if isinstance(data, (list, dict)) else None
    meta["envelope_status"] = envelope_status

    out_path = out_dir / f"{name}.json"
    out_path.write_bytes(resp.content)
    meta["written_to_disk"] = True
    meta["file_path"] = str(out_path)
    return meta


def fetch_items_by_category(out_dir, token, max_retries=5):
    """Pull /items/ per category, because it cannot be pulled unfiltered.

    Discovered live 2026-08-01: GET /items/ with no parameters returns HTTP 400
    with {"status": "requires_id_category_or_id_company_or_uuid"}. The endpoint
    is in documented scope and carries the Star Citizen UUID that is this
    source's whole join value, so it is fetched the way the API requires -
    once per category id, read from the categories.json this same run landed.

    This is NOT crawling for sibling endpoints. It is the same documented
    endpoint, parameterised as its own error message demands.

    Each response passes the identical write gate as everything else; a rejected
    category response is recorded and never written.
    """
    cats_path = out_dir / "categories.json"
    if not cats_path.is_file():
        return [{
            "endpoint": "/items/", "url": BASE + "/items/",
            "written_to_disk": False, "file_path": None, "attempts": 0,
            "attempt_log": [],
            "error": "categories.json not present in the snapshot, so the "
                     "category ids required by /items/ are unknown; nothing fetched",
        }]

    cats = json.loads(cats_path.read_text(encoding="utf-8")).get("data") or []
    ids = [c["id"] for c in cats if isinstance(c, dict) and c.get("id") is not None]

    results = []
    for index, cat_id in enumerate(ids):
        if index:
            time.sleep(REQUEST_DELAY_SECONDS)
        url = f"{BASE}/items/?id_category={cat_id}"
        print(f"  items id_category={cat_id} ({index + 1}/{len(ids)}) ...", file=sys.stderr)
        try:
            resp, attempt_log = get_with_retry(url, token, max_retries=max_retries)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            exhausted = getattr(e, "attempts_log", [])
            results.append({
                "endpoint": f"/items/?id_category={cat_id}", "url": url,
                "id_category": cat_id,
                "attempts": len(exhausted), "attempt_log": exhausted,
                "written_to_disk": False, "file_path": None,
                "error": f"retry ceiling exhausted on {type(e).__name__}: "
                         f"{str(e)[:200]}; body NOT saved",
            })
            continue

        meta = {
            "endpoint": f"/items/?id_category={cat_id}",
            "url": resp.url,
            "id_category": cat_id,
            "attempts": len(attempt_log),
            "attempt_log": attempt_log,
            "elapsed_seconds": attempt_log[-1].get("elapsed_seconds") if attempt_log else None,
            "status_code": resp.status_code,
            "content_type": resp.headers.get("Content-Type"),
            "byte_size": len(resp.content),
            "sha256": hashlib.sha256(resp.content).hexdigest(),
            "written_to_disk": False,
            "file_path": None,
        }

        def reject(reason):
            meta["error"] = f"{reason}; body NOT saved"
            meta["rejected_body_first_200_chars"] = resp.text[:200]
            return meta

        if resp.status_code != 200:
            results.append(reject(f"non-200 status ({resp.status_code})"))
            continue
        ctype = resp.headers.get("Content-Type") or ""
        if "json" not in ctype.lower():
            results.append(reject(f"non-JSON Content-Type ({ctype!r})"))
            continue
        try:
            body = json.loads(resp.content)
        except Exception as e:
            results.append(reject(f"failed to parse JSON: {e}"))
            continue
        if not isinstance(body, dict) or "data" not in body:
            results.append(reject("response is not a UEX envelope (no 'data' key)"))
            continue
        if body.get("status") != "ok":
            results.append(reject(f"UEX envelope status is {body.get('status')!r}, not 'ok'"))
            continue

        data = body["data"]
        meta["record_count"] = len(data) if isinstance(data, list) else None
        meta["records_with_uuid"] = sum(
            1 for x in data if isinstance(x, dict) and x.get("uuid")
        ) if isinstance(data, list) else None
        meta["envelope_status"] = "ok"

        out_path = out_dir / f"items_category_{cat_id}.json"
        out_path.write_bytes(resp.content)
        meta["written_to_disk"] = True
        meta["file_path"] = str(out_path)
        results.append(meta)

    return results


def verify_credential(token):
    """One request, one endpoint, before pulling anything.

    Returns (ok, detail). Never writes to disk.
    """
    url = BASE + "/game_versions/"
    try:
        resp = requests.get(url, headers=_headers(token), timeout=REQUEST_TIMEOUT_SECONDS)
    except Exception as e:
        return False, f"{type(e).__name__}: {str(e)[:200]}"
    if resp.status_code != 200:
        return False, f"HTTP {resp.status_code}: {resp.text[:200]}"
    ctype = resp.headers.get("Content-Type") or ""
    if "json" not in ctype.lower():
        return False, f"non-JSON Content-Type {ctype!r}"
    try:
        body = resp.json()
    except Exception as e:
        return False, f"unparseable body: {e}"
    if body.get("status") != "ok" or "data" not in body:
        return False, f"unexpected envelope: {str(body)[:200]}"
    return True, f"HTTP 200, envelope status 'ok', data present ({ctype})"


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return EXIT_USAGE

    token = os.environ.get("UEX_API_TOKEN")
    if not token:
        print("UEX_API_TOKEN is not set. Refusing to run - a pull on an "
              "unverified credential is not attempted.", file=sys.stderr)
        return EXIT_FAILED

    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)

    print("Verifying credential with a single request before pulling ...", file=sys.stderr)
    ok, detail = verify_credential(token)
    print(f"  credential check: {'OK' if ok else 'FAILED'} - {detail}", file=sys.stderr)
    if not ok:
        print("Credential verification failed. Nothing was pulled.", file=sys.stderr)
        return EXIT_FAILED

    results = []
    for index, (name, path) in enumerate(ENDPOINTS):
        if index:
            time.sleep(REQUEST_DELAY_SECONDS)
        print(f"Fetching {name} from {BASE}{path} ...", file=sys.stderr)
        results.append(fetch(name, path, out_dir, token))

    print(json.dumps(results, indent=2))

    rejected = [r for r in results if not r["written_to_disk"]]
    if rejected:
        print(f"{len(rejected)} of {len(results)} endpoint(s) did not land: "
              f"{', '.join(r['endpoint'] for r in rejected)}", file=sys.stderr)
        return EXIT_FAILED
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
