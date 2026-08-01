"""
Post-processing helper for the api.star-citizen.wiki snapshot (source 3).
Not a retrieval script - run after api_star_citizen_wiki.py to compute
per-collection completeness/fingerprint stats for the manifest.

Usage: python finalize_star_citizen_wiki.py <snapshot-dir>
"""
import hashlib
import json
import sys
from pathlib import Path


def fp(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()[:16]


def analyze_collection(snapshot_dir: Path, name: str) -> dict:
    pages = sorted(snapshot_dir.glob(f"{name}_page_*.json"), key=lambda p: int(p.stem.rsplit("_", 1)[1]))
    all_records = []
    page_details = []
    response_top_level_keys = None
    response_meta_last = None
    parse_errors = []

    for p in pages:
        raw = p.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        try:
            body = json.loads(raw)
        except Exception as e:
            parse_errors.append({"file": str(p), "error": str(e)})
            page_details.append({"file": str(p), "byte_size": len(raw), "sha256": sha, "parse_error": str(e)})
            continue
        if response_top_level_keys is None and isinstance(body, dict):
            response_top_level_keys = sorted(body.keys())
        data = body.get("data", []) if isinstance(body, dict) else []
        if isinstance(data, list):
            all_records.extend(data)
        response_meta_last = body.get("meta") if isinstance(body, dict) else None
        page_details.append({
            "file": str(p), "byte_size": len(raw), "sha256": sha,
            "record_count": len(data) if isinstance(data, list) else (1 if data else 0),
        })

    uuids = [r.get("uuid") for r in all_records if isinstance(r, dict) and r.get("uuid")]
    record_keys = sorted(all_records[0].keys()) if all_records and isinstance(all_records[0], dict) else []

    return {
        "collection": name,
        "page_count": len(pages),
        "page_details": page_details,
        "parse_errors": parse_errors,
        "total_records": len(all_records),
        "unique_primary_key_count": len(set(uuids)),
        "duplicate_primary_key_count": len(uuids) - len(set(uuids)),
        "primary_key_field_assumed": "uuid",
        "response_top_level_keys": response_top_level_keys,
        "response_structure_fingerprint": fp(response_top_level_keys) if response_top_level_keys else None,
        "record_structure_top_level_keys": record_keys,
        "record_structure_fingerprint": fp(record_keys) if record_keys else None,
        "reported_total_records": response_meta_last.get("total") if isinstance(response_meta_last, dict) else None,
        "reported_last_page": response_meta_last.get("last_page") if isinstance(response_meta_last, dict) else None,
    }


def main() -> int:
    snapshot_dir = Path(sys.argv[1])
    report = {}
    for name in ["vehicles", "items", "manufacturers"]:
        report[name] = analyze_collection(snapshot_dir, name)
    print(json.dumps(report, indent=2))

    # Fail closed: this script is a gate, so a page that didn't parse has to
    # stop the pipeline rather than let a `&&` chain promote the snapshot.
    failed = any(report[name]["parse_errors"] for name in report)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
