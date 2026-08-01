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
prints a JSON line per request with status/headers/hash metadata to stdout
for the caller to fold into the source manifest.
"""
import hashlib
import json
import sys
import time
from pathlib import Path

import requests

BASE = "https://scunpacked.com"
ENDPOINTS = [
    ("ships", "/api/v2/ships.json"),
    ("labels", "/api/labels.json"),
]
USER_AGENT = "citizen-compass-data-landing/1.0 (+https://github.com/Smeezee/citizen-compass)"


def fetch(name: str, path: str, out_dir: Path) -> dict:
    url = BASE + path
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    out_path = out_dir / f"{name}.json"
    out_path.write_bytes(resp.content)
    sha256 = hashlib.sha256(resp.content).hexdigest()
    return {
        "endpoint": path,
        "url": url,
        "status_code": resp.status_code,
        "redirects": [r.url for r in resp.history],
        "content_type": resp.headers.get("Content-Type"),
        "content_length_header": resp.headers.get("Content-Length"),
        "etag": resp.headers.get("ETag"),
        "last_modified": resp.headers.get("Last-Modified"),
        "file_path": str(out_path),
        "byte_size": len(resp.content),
        "sha256": sha256,
    }


def main():
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for name, path in ENDPOINTS:
        results.append(fetch(name, path, out_dir))
        time.sleep(1)  # polite delay between the two requests
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
