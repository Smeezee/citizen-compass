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

For each of vehicles/items/manufacturers, paginates with page[size]=200
sequentially (no parallel requests), saves every page as its own file
(<collection>_page_<N>.json), stops when the response's own
meta.last_page is reached, and honors HTTP 429 with Retry-After.
Prints a JSON summary per collection to stdout for the manifest.
"""
import json
import sys
import time
from pathlib import Path

import requests

BASE = "https://api.star-citizen.wiki/api"
COLLECTIONS = ["vehicles", "items", "manufacturers"]
PAGE_SIZE = 200
USER_AGENT = "citizen-compass-data-landing/1.0 (+https://github.com/Smeezee/citizen-compass)"
REQUEST_DELAY_SECONDS = 1.5


def get_with_retry(url: str, params: dict, max_retries: int = 5) -> requests.Response:
    # Observed live during this run: the /vehicles endpoint intermittently
    # returns a transient HTML 500 ("System Malfunction") at page[size]=200
    # - 2 of 3 manual attempts failed, 1 succeeded, same params each time.
    # Retrying the SAME endpoint/params a few times with backoff is not a
    # substitution (no different endpoint, no approximation) - it's the
    # documented-correct way to ride out a flaky upstream.
    for attempt in range(max_retries):
        resp = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=60)
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", "5"))
            print(f"  429 received, honoring Retry-After={retry_after}s (attempt {attempt + 1})", file=sys.stderr)
            time.sleep(retry_after)
            continue
        if 500 <= resp.status_code < 600:
            backoff = 3 * (attempt + 1)
            print(f"  {resp.status_code} received, retrying in {backoff}s (attempt {attempt + 1}/{max_retries})", file=sys.stderr)
            time.sleep(backoff)
            continue
        return resp
    return resp


def pull_collection(name: str, version: str, out_dir: Path) -> dict:
    url = f"{BASE}/{name}"
    page = 1
    pages_meta = []
    total_records = 0
    last_page = None
    terminated_normally = False

    while True:
        params = {"version": version, "page[size]": PAGE_SIZE, "page[number]": page}
        resp = get_with_retry(url, params)
        page_path = out_dir / f"{name}_page_{page}.json"
        page_path.write_bytes(resp.content)

        meta_entry = {
            "page": page,
            "url": resp.url,
            "status_code": resp.status_code,
            "content_type": resp.headers.get("Content-Type"),
            "etag": resp.headers.get("ETag"),
            "last_modified": resp.headers.get("Last-Modified"),
            "byte_size": len(resp.content),
            "file_path": str(page_path),
        }

        if resp.status_code != 200:
            meta_entry["error"] = f"non-200 status, stopping pagination for {name}"
            pages_meta.append(meta_entry)
            break

        try:
            body = resp.json()
        except Exception as e:
            meta_entry["error"] = f"failed to parse JSON: {e}"
            pages_meta.append(meta_entry)
            break

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
        "pages": pages_meta,
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
