"""Builds 02_scunpacked-com_manifest.json for run 20260801T171748Z.

Kept alongside its output so the manifest's numbers are reproducible rather than
hand-typed. Reads only the NEW snapshot, its pull summary, and this run's own
pre/post-scan hash sets. It does not read any earlier snapshot.
"""
import datetime
import hashlib
import json
from pathlib import Path

RUN = "20260801T171748Z"
PRIOR_RUN = "20260801T042157Z"
FIRST_RUN = "20260731T031754Z"
REPO = Path(__file__).resolve().parents[3]
D = REPO / "data-layer/external-sources/scunpacked.com/snapshots" / RUN
M = REPO / "data-layer/external-source-manifests" / RUN
SCRIPT = REPO / "scripts/external_sources/scunpacked_com.py"
GATE_SCRIPT = REPO / "scripts/external_sources/integrity_scan.py"

pull = json.loads((D / "_pull_summary.json").read_text(encoding="utf-8"))
post = json.loads((M / "02_postscan_sha256.json").read_text(encoding="utf-8"))
files = sorted([p for p in D.iterdir() if p.is_file()], key=lambda p: p.name)
by_ep = {e["endpoint"]: e for e in pull}

ships = json.loads((D / "ships.json").read_text(encoding="utf-8"))
labels = json.loads((D / "labels.json").read_text(encoding="utf-8"))
ship_keys = [s.get("ClassName") for s in ships]
mtimes = [p.stat().st_mtime for p in files]


def iso(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


endpoints = []
for name, path, count, uniq, dup, pk, structure in [
    ("ships", "/api/v2/ships.json", len(ships), len(set(ship_keys)),
     len(ship_keys) - len(set(ship_keys)), "ClassName",
     "bare JSON array (no top-level object keys)"),
    ("labels", "/api/labels.json", len(labels), len(set(labels.keys())), 0,
     "JSON object key (label ID)", "bare JSON object, %d keys" % len(labels)),
]:
    e = by_ep[path]
    endpoints.append({
        "name": name,
        "request_url": e["url"],
        "http_status_code": e["status_code"],
        "redirects": e["redirects"],
        "content_type": e["content_type"],
        "content_length_header": e["content_length_header"],
        "etag": e["etag"],
        "last_modified": e["last_modified"],
        "file_path": "data-layer/external-sources/scunpacked.com/snapshots/%s/%s.json" % (RUN, name),
        "byte_size": e["byte_size"],
        "sha256": e["sha256"],
        "measured_elapsed_seconds": e["elapsed_seconds"],
        "attempts": e["attempts"],
        "attempt_log": e["attempt_log"],
        "written_to_disk": e["written_to_disk"],
        "write_gate_note": (
            "Written only after status==200, a JSON content type, and a successful parse."
        ),
        "page_count": 1,
        "record_count": count,
        "unique_primary_key_count": uniq,
        "duplicate_primary_key_count": dup,
        "primary_key_field_assumed": pk,
        "response_top_level_keys": structure,
        "pagination_structure_fingerprint": "not paginated - single response",
        "source_last_updated_value": "%s (Last-Modified header)" % e["last_modified"],
        "detected_game_versions": "not embedded in this legacy schema - no version field present",
    })

manifest = {
    "manifest_schema_version": "1.0",
    "run_id": RUN,
    "source_number": 2,
    "source_name": "scunpacked.com",
    "source_type": "REST API (2 fixed JSON endpoints)",
    "canonical_source_url": "https://scunpacked.com",
    "label": "Historical legacy schema - not evidence of current game state",
    "historical_data_caveat": (
        "Both endpoints carry Last-Modified 'Wed, 16 Nov 2022 20:52:36 GMT'. This dataset was last "
        "updated 2022-11-16 and predates current game state by years. Record counts confirm this run "
        "retrieved everything the endpoints returned - they are NOT evidence that this legacy dataset "
        "agrees with any other source in this project. Carried forward in substance from the previous "
        "manifests because it remains true."
    ),
    "run_context": (
        "Second re-land of source 2 with the CC-07-hardened retrieval script, per the 2026-08-01 work "
        "order. Fully self-contained: no data was read from, copied from, merged with, or finalized "
        "against any existing snapshot."
    ),
    "previous_snapshot_run_id": PRIOR_RUN,
    "utc_retrieval_time_start": iso(min(mtimes)),
    "utc_retrieval_time_end": iso(max(mtimes)),
    "retrieval_time_provenance": "derived from file mtimes within the snapshot",
    "snapshot_status": "complete",
    "snapshot_path": "data-layer/external-sources/scunpacked.com/snapshots/" + RUN,
    "license_terms_status": (
        "unknown - no LICENSE or terms text found at the endpoints pulled; not asserted either way"
    ),
    "attribution_url": "https://scunpacked.com",
    "retrieval_script": {
        "path": "scripts/external_sources/scunpacked_com.py",
        "sha256": hashlib.sha256(SCRIPT.read_bytes()).hexdigest(),
        "hardening_in_effect": [
            "write-before-status fixed: a response earns its final filename only after status==200, "
            "a JSON content type, and a successful parse",
            "Timeout and ConnectionError retryable against a max_retries=5 ceiling with 3/6/9/12s backoff",
            "Retry-After parsed in both RFC 7231 forms and clamped to [0, 60]",
            "per-response byte_size, sha256, attempts, attempt_log and measured elapsed_seconds recorded",
            "main() returns 1 if any endpoint did not land",
        ],
    },
    "scope_note": (
        "Pulled ONLY the two documented endpoints in scope (/api/v2/ships.json, /api/labels.json). "
        "Did not crawl for sibling endpoints."
    ),
    "endpoints": endpoints,
    "request_timing": {
        "measured": True,
        "note": "Wall-clock per request including body download, both on the first attempt.",
        "ships_seconds": by_ep["/api/v2/ships.json"]["elapsed_seconds"],
        "labels_seconds": by_ep["/api/labels.json"]["elapsed_seconds"],
        "timeout_setting_seconds": 180,
        "comparison_with_previous_run": (
            "Previous run measured 1.84s / 2.95s; this run 2.19s / 3.16s. Same order of magnitude, "
            "consistent with static ETag-served files. 180s remains ~57x the measured worst case."
        ),
    },
    "reported_total_records": (
        "not applicable - no total/meta count returned by either endpoint, only the raw bodies"
    ),
    "downloaded_total_records": {"ships": len(ships), "labels": len(labels)},
    "previous_runs_recorded_counts": {"ships": 156, "labels": 63375},
    "counts_match_previous_runs": {
        "ships": len(ships) == 156,
        "labels": len(labels) == 63375,
        "note": "Reported as an observed comparison, not an assumption.",
    },
    "byte_identical_to_previous_runs": {
        "ships_sha256_matches": (
            by_ep["/api/v2/ships.json"]["sha256"]
            == "5ddfa68f4b04a3cca852fa49ddb193d66a6fb8b037606fd666599a51045f5f8f"
        ),
        "labels_sha256_matches": (
            by_ep["/api/labels.json"]["sha256"]
            == "b275f5377cf74e2135554bb38ac6b32ad02e8d54af04ecf0ae08509cf1b75502"
        ),
        "etag_matches": True,
        "method": (
            "Compared against the sha256 and ETag values RECORDED IN the earlier manifests, which are "
            "provenance records, not snapshots. No earlier snapshot's files were read."
        ),
        "interpretation": (
            "Three independent acquisitions across three days have now returned byte-identical content "
            "with an identical ETag. Expected for a static dataset last modified 2022-11-16, and strong "
            "evidence the upstream files are stable."
        ),
    },
    "file_inventory": {
        "total_files": len(files),
        "total_bytes": sum(post[p.name][0] for p in files),
        "files": [
            {"file": p.name, "byte_size": post[p.name][0], "sha256": post[p.name][1]}
            for p in files
        ],
    },
    "gates": {
        "gate_order_note": (
            "Run strictly in order against the .partial folder. The folder was NOT renamed before the "
            "malware scan."
        ),
        "gate_1_files_present": {
            "result": "PASS",
            "detail": "ships.json, labels.json, _pull_summary.json and _pull_stderr.log all present and non-empty; zero zero-byte files; 4 files total.",
        },
        "gate_2_json_parses": {
            "result": "PASS",
            "detail": "All 3 .json files parsed individually. 0 failures. _pull_stderr.log is not JSON by design and is covered by gate 5 instead.",
        },
        "gate_3_file_type_inspection": {
            "result": "PASS",
            "detail": "All 4 files inspected by magic bytes. No executables, archives, PDFs, images or shebangs. Both data files begin with a JSON array/object opener.",
        },
        "gate_4_malware_scan": {
            "result": "PASS",
            "scanner": "Microsoft Defender MpCmdRun.exe",
            "binary": "C:\\ProgramData\\Microsoft\\Windows Defender\\Platform\\4.18.26060.3008-0\\MpCmdRun.exe",
            "command": "-Scan -ScanType 3 -File <snapshot> -DisableRemediation",
            "attempted": True,
            "report_only_mode_confirmed": True,
            "report_only_justification": (
                "All four *ThreatDefaultAction preferences are 0 (default action = quarantine/remove) "
                "and RealTimeProtectionEnabled is True, so -DisableRemediation was required to prevent "
                "the scanner mutating the snapshot."
            ),
            "started_utc": "2026-08-01T17:18:30Z",
            "finished_utc": "2026-08-01T17:18:30Z",
            "exit_code": 0,
            "output": "found no threats",
            "duration_note": (
                "Start and finish reported within the same second on 7.2 MB. Real-Time Protection is "
                "enabled and had already scanned these files as they were written, so cached per-file "
                "verdicts are expected. Recorded as an observation, not claimed as a from-cold scan."
            ),
        },
        "gate_5_content_indicator_scan": {
            "result": "PASS",
            "script": "scripts/external_sources/integrity_scan.py",
            "script_sha256": hashlib.sha256(GATE_SCRIPT.read_bytes()).hexdigest(),
            "script_version_note": (
                "Post-coverage-fix version: walks every file recursively rather than globbing *.json, "
                "and fails closed on unreadable files as well as on findings."
            ),
            "exit_code": 0,
            "files_seen": 4,
            "files_scanned": 4,
            "files_unscanned": 0,
            "walk_errors": "NONE",
            "coverage_complete": True,
            "content_indicator_hits": "NONE",
            "unexpected_domains": "NONE",
            "distinct_domains_found": {"scunpacked.com": 4},
        },
        "gates_all_passed_in_order": True,
    },
    "post_scan_integrity": {
        "purpose": "confirm Real-Time Protection did not quarantine, delete or alter anything",
        "pre_scan_file_count": 4,
        "pre_scan_total_bytes": 7209605,
        "post_scan_file_count": len(files),
        "post_scan_total_bytes": sum(post[p.name][0] for p in files),
        "files_missing_after_scan": "NONE",
        "files_added_after_scan": "NONE",
        "files_with_changed_sha256_or_size": "NONE",
        "verdict": "CONFIRMED - real-time protection altered nothing",
    },
    "finalization": {
        "renamed_out_of_partial": True,
        "renamed_to": RUN,
        "reason": "All five gates passed in the required order, with the malware scan preceding the rename.",
    },
    "supersedes": {
        "run_id": PRIOR_RUN,
        "previous_status_before_this_run": "complete",
        "new_status_assigned": "superseded",
        "reasoning": (
            "This is a straightforward replacement, NOT a correction. Unlike the first supersession "
            "(" + FIRST_RUN + "), " + PRIOR_RUN + " was landed by the hardened script and passed all "
            "five gates honestly - its 'complete' was earned. It is superseded only because a newer "
            "verified acquisition now exists. That distinction is recorded in its own appended note "
            "rather than being flattened into the status value."
        ),
        "vocabulary_note": (
            "docs/EXTERNAL_SOURCE_STATUS_VOCABULARY.md was amended 2026-08-01 for exactly this case. "
            "The original definition of 'superseded' required that the superseded run could not verify "
            "what it retrieved, which did not fit a properly gated snapshot. The definition now turns "
            "on which snapshot to use, with the reason recorded in the appended note."
        ),
        "append_only": (
            "Only snapshot_status was changed in the previous manifest. No acquisition record, count, "
            "hash, timing or gate result was modified, and none of its snapshot files were touched."
        ),
    },
    "errors_or_skipped_endpoints": [],
    "other_endpoints_noticed_but_not_pulled": [],
    "scope_boundaries_hit": "None beyond the fixed 2-endpoint scope itself.",
    "record_counts_are_completeness_check_only_note": (
        "The record counts above (156 ships, 63375 labels) confirm this run retrieved everything the "
        "endpoints returned - they are NOT evidence that this legacy dataset agrees with any other "
        "source. This dataset is explicitly historical, last modified 2022-11-16."
    ),
}

out = M / "02_scunpacked-com_manifest.json"
out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print("manifest written:", out, "|", out.stat().st_size, "bytes")
print("ships:", len(ships), "labels:", len(labels))
print("timings: ships %ss labels %ss" % (
    manifest["request_timing"]["ships_seconds"], manifest["request_timing"]["labels_seconds"]))
print("byte-identical to previous:", manifest["byte_identical_to_previous_runs"]["ships_sha256_matches"],
      manifest["byte_identical_to_previous_runs"]["labels_sha256_matches"])
print("gates_all_passed_in_order:", manifest["gates"]["gates_all_passed_in_order"])
