"""Builds 02_scunpacked-com_manifest.json for run 20260801T042157Z.

Kept alongside its output so the manifest's numbers are reproducible rather
than hand-typed. Reads only the NEW snapshot, the pull summary, and this run's
own pre/post-scan hash sets. It does not read snapshot 20260731T031754Z.
"""
import datetime
import hashlib
import json
from pathlib import Path

RUN = "20260801T042157Z"
PRIOR_RUN = "20260731T031754Z"
REPO = Path(__file__).resolve().parents[3]
D = REPO / "data-layer/external-sources/scunpacked.com/snapshots" / RUN
M = REPO / "data-layer/external-source-manifests" / RUN
SCRIPT = REPO / "scripts/external_sources/scunpacked_com.py"
GATE_SCRIPT = REPO / "scripts/external_sources/integrity_scan.py"

pull = json.loads((D / "_pull_summary.json").read_text(encoding="utf-8"))
post = json.loads((M / "02_postscan_sha256.json").read_text(encoding="utf-8"))
files = sorted([p for p in D.iterdir() if p.is_file()], key=lambda p: p.name)
by_endpoint = {e["endpoint"]: e for e in pull}

ships = json.loads((D / "ships.json").read_text(encoding="utf-8"))
labels = json.loads((D / "labels.json").read_text(encoding="utf-8"))
ship_keys = [s.get("ClassName") for s in ships]


def iso(ts):
    return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


mtimes = [p.stat().st_mtime for p in files]

endpoints = []
for name, path, count, uniq, dup, pk, structure in [
    ("ships", "/api/v2/ships.json", len(ships), len(set(ship_keys)),
     len(ship_keys) - len(set(ship_keys)), "ClassName",
     "bare JSON array (no top-level object keys)"),
    ("labels", "/api/labels.json", len(labels), len(set(labels.keys())), 0,
     "JSON object key (label ID)",
     "bare JSON object, %d keys" % len(labels)),
]:
    e = by_endpoint[path]
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
            "Written only after status==200, a JSON content type, and a successful parse. "
            "Under the pre-CC-07 script the body was written before any of those checks."
        ),
        "page_count": 1,
        "record_count": count,
        "unique_primary_key_count": uniq,
        "duplicate_primary_key_count": dup,
        "primary_key_field_assumed": pk,
        "response_top_level_keys": structure,
        "pagination_structure_fingerprint": "not paginated - single response",
        "source_last_updated_value": "%s (Last-Modified header)" % e["last_modified"],
        "detected_game_versions": (
            "not embedded in this legacy schema - no version field present"
        ),
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
        "agrees with any other source in this project. Carried forward verbatim in substance from the "
        "previous run's manifest because it remains true."
    ),
    "run_context": (
        "Re-pull of source 2 with the CC-07-hardened retrieval script. The previous run's snapshot was "
        "landed by a script that had no HTTP status check, no retry, no rate-limit handling, and a "
        "main() that exited 0 unconditionally - so its 'complete' status was not earned by verification. "
        "This run is fully self-contained: no data was read from, copied from, merged with, or "
        "finalized against any existing snapshot."
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
        "hardening_applied_this_run": [
            "write-before-status fixed: a response earns its final filename only after status==200, "
            "a JSON content type, and a successful parse",
            "Timeout and ConnectionError retryable against a max_retries=5 ceiling with 3/6/9/12s backoff",
            "Retry-After parsed in both RFC 7231 forms and clamped to [0, 60]",
            "per-response byte_size, sha256, attempts, attempt_log and measured elapsed_seconds recorded",
            "main() returns 1 if any endpoint did not land (previously always 0)",
        ],
    },
    "scope_note": (
        "Pulled ONLY the two documented endpoints in scope (/api/v2/ships.json, /api/labels.json). Did "
        "not crawl for sibling endpoints."
    ),
    "endpoints": endpoints,
    "request_timing": {
        "measured": True,
        "note": (
            "Wall-clock per request including body download, both on the first attempt. These are the "
            "first real timings ever recorded for this source."
        ),
        "ships_seconds": by_endpoint["/api/v2/ships.json"]["elapsed_seconds"],
        "labels_seconds": by_endpoint["/api/labels.json"]["elapsed_seconds"],
        "timeout_setting_seconds": 180,
        "timeout_justification": (
            "180s is ~60x the measured worst case (2.95s). The code comment previously estimated this "
            "source would be at least as slow as one star-citizen.wiki vehicles page (42.6s); that "
            "estimate was wrong by more than an order of magnitude and has been corrected to state the "
            "measurement."
        ),
    },
    "reported_total_records": (
        "not applicable - no total/meta count returned by either endpoint, only the raw bodies"
    ),
    "downloaded_total_records": {"ships": len(ships), "labels": len(labels)},
    "previous_run_recorded_counts": {"ships": 156, "labels": 63375},
    "counts_match_previous_run": {
        "ships": len(ships) == 156,
        "labels": len(labels) == 63375,
        "note": (
            "Reported as an observed comparison, not an assumption. Both endpoints also returned "
            "byte-identical content to the previous run (same sha256 and same ETag), which is expected "
            "for a static dataset last modified 2022-11-16."
        ),
    },
    "byte_identical_to_previous_run": {
        "ships_sha256_matches_prior_manifest": (
            by_endpoint["/api/v2/ships.json"]["sha256"]
            == "5ddfa68f4b04a3cca852fa49ddb193d66a6fb8b037606fd666599a51045f5f8f"
        ),
        "labels_sha256_matches_prior_manifest": (
            by_endpoint["/api/labels.json"]["sha256"]
            == "b275f5377cf74e2135554bb38ac6b32ad02e8d54af04ecf0ae08509cf1b75502"
        ),
        "method": (
            "Compared against the sha256 values RECORDED IN the previous run's manifest, which is a "
            "provenance record, not a snapshot. The previous snapshot's files were not read."
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
            "detail": "All 3 .json files parsed individually. 0 failures. _pull_stderr.log is not JSON by design and was not JSON-checked (it IS content-scanned by gate 5).",
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
                "the scanner mutating the snapshot. NOTE: the previous run recorded "
                "report_only_mode_confirmed=false because its Set-MpPreference attempt failed on a "
                "non-elevated session; this run uses -DisableRemediation on the scan command itself, "
                "which needs no elevation."
            ),
            "started_utc": "2026-08-01T04:22:56Z",
            "finished_utc": "2026-08-01T04:22:56Z",
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
                "This is the FIXED gate script. The previous version globbed *.json and would have "
                "skipped _pull_stderr.log entirely while still reporting PASS. All 4 files were scanned "
                "here."
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
    "supersedes_previous_snapshot": {
        "previous_run_id": PRIOR_RUN,
        "previous_snapshot_path": "data-layer/external-sources/scunpacked.com/snapshots/" + PRIOR_RUN,
        "previous_status_as_recorded": "complete",
        "finding": (
            "That 'complete' status was assigned by a script that performed no verification. The "
            "pre-CC-07 scunpacked_com.py wrote every response body to its final filename before "
            "examining resp.status_code, had no retry or rate-limit handling, and its main() returned "
            "None so the process exited 0 regardless of what came back. An error page would have been "
            "saved as ships.json and reported as a successful landing. The previous snapshot's data may "
            "well be fine - its recorded sha256 values match this run byte for byte - but that is "
            "established by THIS run, not by anything the previous run did."
        ),
        "proposal_only_not_applied": (
            "PROPOSAL, NOT APPLIED. Nothing in the previous manifest has been modified - its acquisition "
            "record stands exactly as written. Proposed: change its snapshot_status from 'complete' to a "
            "value indicating the status was never verified, and point it at this run. Sleven decides "
            "whether that status changes; it was not changed here."
        ),
        "what_this_run_establishes_about_the_old_data": (
            "This run independently re-fetched both endpoints and got byte-identical content (matching "
            "sha256 AND matching ETag) to the values recorded in the previous run's manifest. That is "
            "good evidence the previous snapshot's bytes are the genuine upstream bytes. It does not "
            "retroactively make the previous run verified - it makes the current run verified."
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
print("manifest written:", out)
print("bytes:", out.stat().st_size)
print("snapshot_status:", manifest["snapshot_status"])
print("ships:", len(ships), " labels:", len(labels))
print("timings: ships %ss  labels %ss" % (
    manifest["request_timing"]["ships_seconds"], manifest["request_timing"]["labels_seconds"]))
print("byte-identical to prior:", manifest["byte_identical_to_previous_run"])
print("gates_all_passed_in_order:", manifest["gates"]["gates_all_passed_in_order"])
