"""
Shared integrity/content-indicator scan used across all sources in the
2026-07-31 external data landing run (see the run's manifests for the
full spec this implements). Not a retrieval script itself - reused by
each source's finalize step before a snapshot can be renamed out of
.partial.

Checks, per JSON file in a directory:
  - parses as valid JSON (already required before this runs, re-verified here)
  - string values scanned for a narrow, specific set of active-content
    indicators (not a blanket "any HTML" flag)
  - embedded http(s) URLs collected and their domains compared against
    an explicit allowlist of expected SC-data-related domains

Usage: python integrity_scan.py <dir-of-json-files> [more-dirs...]
Prints a JSON report to stdout. Never modifies or deletes anything.
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

INDICATORS = [
    "<script", "javascript:", "data:text/html", "onload=",
    "onerror=", "onclick=", "<iframe", "<object", "<embed",
]

ALLOWLIST_DOMAINS = {
    "robertsspaceindustries.com",
    "cdn.robertsspaceindustries.com",
    "star-citizen.wiki",
    "api.star-citizen.wiki",
    "starcitizen.tools",
    "scunpacked.com",
    "media.starcitizen.tools",
    "github.com",
    "raw.githubusercontent.com",
    "githubusercontent.com",
    "cstone.space",
    "finder.cstone.space",
    "fleetyards.net",
    "wiki.starcitizen.tools",
}

URL_RE = re.compile(r"https?://[^\s\"'<>]+")


def domain_of(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def is_allowed(domain: str) -> bool:
    domain = domain.split(":")[0]  # strip port
    return any(domain == d or domain.endswith("." + d) for d in ALLOWLIST_DOMAINS)


def scan_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")

    indicator_hits = {}
    for ind in INDICATORS:
        count = text.count(ind)
        if count:
            idx = text.find(ind)
            sample = text[max(0, idx - 40):idx + 60]
            indicator_hits[ind] = {"count": count, "sample": sample}

    urls = set(URL_RE.findall(text))
    domain_counts = {}
    unexpected_domains = {}
    for u in urls:
        d = domain_of(u)
        if not d:
            continue
        domain_counts[d] = domain_counts.get(d, 0) + 1
        if not is_allowed(d):
            unexpected_domains.setdefault(d, {"count": 0, "sample_urls": []})
            unexpected_domains[d]["count"] += 1
            if len(unexpected_domains[d]["sample_urls"]) < 3:
                unexpected_domains[d]["sample_urls"].append(u)

    return {
        "file": str(path),
        "byte_size": len(text.encode("utf-8")),
        "content_indicator_hits": indicator_hits,
        "distinct_domains_found": sorted(domain_counts.keys()),
        "domain_counts": domain_counts,
        "unexpected_domains": unexpected_domains,
    }


def main() -> int:
    report = {"files": []}
    for arg in sys.argv[1:]:
        d = Path(arg)
        targets = list(d.glob("*.json")) if d.is_dir() else [d]
        for f in targets:
            report["files"].append(scan_file(f))
    print(json.dumps(report, indent=2))

    # Fail closed: this script is a gate, so a scan that found something has
    # to stop the pipeline rather than let a `&&` chain promote the snapshot.
    failed = any(
        entry["content_indicator_hits"] or entry["unexpected_domains"]
        for entry in report["files"]
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
