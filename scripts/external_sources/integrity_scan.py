"""
Shared integrity/content-indicator scan used across all sources in the
2026-07-31 external data landing run (see the run's manifests for the
full spec this implements). Not a retrieval script itself - reused by
each source's finalize step before a snapshot can be renamed out of
.partial.

Checks, per file in a directory (EVERY file, recursively - not just *.json):
  - string values scanned for a narrow, specific set of active-content
    indicators (not a blanket "any HTML" flag)
  - embedded http(s) URLs collected and their domains compared against
    an explicit allowlist of expected SC-data-related domains

Usage: python integrity_scan.py <dir> [more-dirs...]
Prints a JSON report to stdout. Never modifies or deletes anything.

COVERAGE FIX 2026-08-01: this script used to glob "*.json" only. Every
non-JSON file in every snapshot it has ever gated - captured HTTP response
headers, openapi.yaml, run logs - was silently skipped, and the gate then
reported PASS having never looked at them. That is a gate reporting a pass it
did not earn, across every previous run of this pipeline, not just one.
It now walks every file recursively. A file that genuinely cannot be read is
reported as UNSCANNED and fails the gate; it is never counted as passed.
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

    # Added 2026-08-01, after the coverage fix below exposed non-JSON files that
    # had never been scanned. Each of these is documentation or transport
    # infrastructure, not a data source we are pulling from.

    # RFC 2606 reserved documentation domains. Reserved precisely so they cannot
    # resolve to a real destination. They appear in openapi.yaml's own example
    # request/response values (e.g. https://example.com/vehicles/arrow).
    "example.com",
    "api.example.com",

    # The MIT licence URL in openapi.yaml's info.license block
    # (https://opensource.org/licenses/MIT). A licence reference, not a fetch target.
    "opensource.org",

    # Cloudflare Network Error Logging endpoint. Appears in the captured HTTP
    # RESPONSE HEADERS (report-to / NEL), never in any data file. It is a
    # property of the CDN fronting api.star-citizen.wiki and is expected to
    # recur on every run that captures response headers.
    "a.nel.cloudflare.com",
}

# URL matching, then hostname extraction.
#
# The previous pattern was r"https?://[^\s\"'<>]+", which swallowed trailing
# punctuation into the netloc: prose like "see https://starcitizen.tools)" or a
# markdown link followed by a literal backslash-n in openapi.yaml produced
# netlocs such as "starcitizen.tools)" and "star-citizen.wiki).\n\n". Those then
# failed an allowlist that *does* contain starcitizen.tools - a false positive
# generated entirely by the scanner. Backslash and backtick are now excluded
# from the match (they terminate a URL in escaped-string and markdown contexts),
# and trailing punctuation is stripped before the host is parsed.
URL_RE = re.compile(r"https?://[^\s\"'<>\\`]+")

# Characters that may legally appear in a URL but are far more often sentence or
# markup punctuation when they sit at the very end of a match.
# NB: ")" is deliberately NOT in this set - it is handled separately below, so
# that a URL legitimately containing a balanced paren keeps it.
TRAILING_PUNCTUATION = ".,;:!?]}>’”"


def trim_url(url: str) -> str:
    """Strip trailing punctuation that is prose/markup, not part of the URL.

    A closing paren is only stripped when it is UNBALANCED, so a URL that
    legitimately contains one - e.g. a wiki link ending "_(disambiguation)" -
    keeps it.
    """
    previous = None
    while url != previous:
        previous = url
        url = url.rstrip(TRAILING_PUNCTUATION)
        if url.endswith(")") and url.count(")") > url.count("("):
            url = url[:-1]
    return url


def domain_of(url: str) -> str:
    try:
        return urlparse(trim_url(url)).netloc.lower()
    except Exception:
        return ""


def is_allowed(domain: str) -> bool:
    domain = domain.split(":")[0]  # strip port
    return any(domain == d or domain.endswith("." + d) for d in ALLOWLIST_DOMAINS)


def scan_file(path: Path) -> dict:
    # Read as bytes so ANY file type can be scanned, not just decodable text.
    # The indicator strings and URL pattern are pure ASCII, so they remain
    # detectable even in a file that is not valid UTF-8; decoding with
    # replacement cannot hide an ASCII match.
    try:
        raw = path.read_bytes()
    except OSError as e:
        # Cannot be read at all. Report it as UNSCANNED - never as clean.
        return {
            "file": str(path),
            "scanned": False,
            "unscanned_reason": f"read failed: {type(e).__name__}: {e}",
            "byte_size": None,
            "content_indicator_hits": {},
            "distinct_domains_found": [],
            "domain_counts": {},
            "unexpected_domains": {},
        }

    try:
        text = raw.decode("utf-8")
        encoding = "utf-8"
    except UnicodeDecodeError:
        text = raw.decode("utf-8", errors="replace")
        encoding = "not-valid-utf-8 (decoded with replacement; ASCII indicators still detectable)"

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
        "scanned": True,
        "encoding": encoding,
        "byte_size": len(raw),
        "content_indicator_hits": indicator_hits,
        "distinct_domains_found": sorted(domain_counts.keys()),
        "domain_counts": domain_counts,
        "unexpected_domains": unexpected_domains,
    }


def main() -> int:
    report = {"files": []}
    walk_errors = []
    for arg in sys.argv[1:]:
        d = Path(arg)
        if d.is_dir():
            # EVERY file, recursively. Not "*.json" - see the coverage note in
            # the module docstring. A file this gate does not look at must never
            # be able to sit inside a snapshot that the gate called clean.
            try:
                targets = sorted(p for p in d.rglob("*") if p.is_file())
            except OSError as e:
                walk_errors.append({"path": str(d), "error": f"{type(e).__name__}: {e}"})
                continue
        else:
            targets = [d]
        for f in targets:
            report["files"].append(scan_file(f))

    scanned = [e for e in report["files"] if e["scanned"]]
    unscanned = [e for e in report["files"] if not e["scanned"]]
    report["coverage"] = {
        "files_seen": len(report["files"]),
        "files_scanned": len(scanned),
        "files_unscanned": len(unscanned),
        "unscanned": [{"file": e["file"], "reason": e["unscanned_reason"]} for e in unscanned],
        "walk_errors": walk_errors,
        "complete": not unscanned and not walk_errors,
    }
    print(json.dumps(report, indent=2))

    # Fail closed on three distinct grounds: something was found, something
    # could not be read, or a directory could not be walked. A check that could
    # not be performed is reported as not performed and fails - it is never
    # allowed to pass by omission, which is exactly how the "*.json" glob let
    # unscanned files sit inside snapshots this gate had called clean.
    found_something = any(
        entry["content_indicator_hits"] or entry["unexpected_domains"]
        for entry in report["files"]
    )
    incomplete_coverage = bool(unscanned or walk_errors)
    return 1 if (found_something or incomplete_coverage) else 0


if __name__ == "__main__":
    sys.exit(main())
