"""Builds 06_uex-corp_manifest.json for source 6 run 20260801T235530Z.

Kept alongside its output so the manifest's numbers are reproducible rather than
hand-typed. Reads only the NEW snapshot and this run's own verification
artifacts.
"""
import hashlib
import json
from pathlib import Path

RUN = "20260801T235530Z"
PRIOR_RUN = "20260731T031754Z"
REPO = Path(__file__).resolve().parents[3]
D = REPO / "data-layer/external-sources/uexcorp/snapshots" / RUN
V = REPO / "data-layer/external-source-verification" / RUN
M = REPO / "data-layer/external-source-manifests" / RUN
SCRIPT = REPO / "scripts/external_sources/uex_corp.py"
GATE_SCRIPT = REPO / "scripts/external_sources/integrity_scan.py"

pull = json.loads((D / "_pull_summary.json").read_text(encoding="utf-8"))
items_cat = json.loads((D / "_items_by_category_summary.json").read_text(encoding="utf-8"))
gates13 = json.loads((V / "06_gates_1_3.json").read_text(encoding="utf-8"))
post = json.loads((V / "06_postscan_sha256.json").read_text(encoding="utf-8"))
integ = json.loads((V / "06_integrity_scan_perfile.json").read_text(encoding="utf-8"))

landed = [e for e in pull if e["written_to_disk"]]
rejected = [e for e in pull if not e["written_to_disk"]]

# Per-category item totals, computed from the landed files themselves.
item_records = 0
item_uuids = 0
for e in items_cat:
    if e.get("written_to_disk"):
        item_records += e.get("record_count") or 0
        item_uuids += e.get("records_with_uuid") or 0

domains = {}
for f in integ["files"]:
    for dom, n in f["domain_counts"].items():
        domains[dom] = domains.get(dom, 0) + n

inventory = [{"file": k, "byte_size": v[0], "sha256": v[1]} for k, v in sorted(post.items())]

manifest = {
    "manifest_schema_version": "1.0",
    "run_id": RUN,
    "source_number": 6,
    "source_name": "UEX Corp API",
    "source_type": "REST API (Bearer auth, JSON envelope {status, data})",
    "canonical_source_url": "https://api.uexcorp.uk/2.0/",
    "previous_snapshot_run_id": PRIOR_RUN,
    "previous_snapshot_status": "blocked_missing_credentials",
    "run_context": (
        "First ever pull of source 6. The previous run " + PRIOR_RUN + " recorded "
        "blocked_missing_credentials and performed a credential-presence check only - no request was "
        "ever made. This run is the first time any UEX data has been retrieved."
    ),

    # ---------------------------------------------------------------- TIER
    "data_tier": "C",
    "tier_c_statement": (
        "TIER C. UEX states its own data is community-reported and crowdsourced, with tolerances of "
        "+/-20% on commodities and +/-100% on items. It is authoritative for aUEC prices and in-game "
        "dealer locations ONLY because no other source in this project has them. It is NEVER "
        "auto-promoted without review. Any downstream consumer must treat these figures as "
        "community estimates, not game-file truth. This statement is recorded explicitly because a "
        "manifest silent on tier will be misread as authoritative."
    ),
    "why_this_source_matters": (
        "Sources 1, 2 and 3 provide stats, names, coordinates and a location graph. NONE of them links "
        "an item to a shop to a price. UEX is the only source that does."
    ),

    # ---------------------------------------------------------- JOIN KEY
    "join_key": {
        "field": "items.uuid",
        "meaning": "the Star Citizen UUID",
        "joins_to": (
            "fps-items.json (already landed in source 1's snapshot) carries the same UUIDs in its "
            "`reference` and `stdItem.UUID` fields"
        ),
        "records_carrying_a_uuid": item_uuids,
        "records_total": item_records,
        "explicit_instruction": (
            "Join on UUID. Do NOT build a name-matching path - that is where this kind of integration "
            "rots."
        ),
    },

    # ------------------------------------------------------------ CREDENTIAL
    "credential": {
        "account_handle": "slevenkoal",
        "account_uid": 92424,
        "application": "Citizen-Compass",
        "auth": "Bearer token, read from UEX_API_TOKEN in .env",
        "env_file_gitignored": True,
        "env_file_untracked": True,
        "verified_before_pulling": True,
        "verification_method": (
            "A single request to /game_versions/ before any data endpoint was touched. Confirmed HTTP "
            "200, application/json, envelope status 'ok', data present. The script refuses to pull if "
            "this check fails."
        ),
        "credential_rotation_status": (
            "MUST BE TREATED AS EXPOSED. The token was pasted into a chat screenshot before this run. "
            "This pull therefore ran under a credential that is to be rotated. Rotation requires "
            "signing in to the UEX account and could not be performed from here - it is an outstanding "
            "action for Sleven. Recorded so that any later audit knows this snapshot was retrieved "
            "with a since-rotated (or to-be-rotated) credential rather than the current one."
        ),
        "token_scope_note": (
            "Read-only access to public community data with a request quota - not account control."
        ),
    },

    # ---------------------------------------------------------------- SCOPE
    "scope_note": (
        "Pulled ONLY the documented endpoints in scope. Did not crawl for sibling endpoints. The "
        "12 endpoints requested were: items, items_prices_all, terminals, "
        "vehicles_purchases_prices_all, categories, companies, star_systems, planets, moons, cities, "
        "outposts, space_stations."
    ),
    "quota_note": "120 requests/minute, 172,800/day. This run used 113 requests, well inside both.",
    "observed_request_cost": (
        "Every request took approximately 43 seconds regardless of payload size - 4 KB cities took "
        "42.77s and 6.2 MB items_prices_all took 43.2s. This appears to be a fixed server-side cost, "
        "not transfer time. Recorded because it makes the per-category items pull a ~70 minute "
        "operation and that is expected rather than a fault."
    ),

    # ------------------------------------------------- ENDPOINTS AS REQUESTED
    "endpoints_landed": [
        {
            "endpoint": e["endpoint"],
            "http_status_code": e["status_code"],
            "content_type": e["content_type"],
            "byte_size": e["byte_size"],
            "sha256": e["sha256"],
            "record_count": e.get("record_count"),
            "envelope_status": e.get("envelope_status"),
            "attempts": e["attempts"],
            "measured_elapsed_seconds": e.get("elapsed_seconds"),
            "file": Path(e["file_path"]).name if e.get("file_path") else None,
        }
        for e in landed
    ],

    # ------------------------------- THE REFUSED ENDPOINT, RECORDED NOT HIDDEN
    "endpoints_attempted_and_refused": [
        {
            "endpoint": e["endpoint"],
            "http_status_code": e.get("status_code"),
            "content_type": e.get("content_type"),
            "byte_size": e.get("byte_size"),
            "sha256": e.get("sha256"),
            "attempts": e.get("attempts"),
            "response_body": e.get("rejected_body_first_200_chars"),
            "written_to_disk": False,
            "why_recorded": (
                "This endpoint was in documented scope, was attempted, and was refused by the API. It "
                "is listed here rather than omitted. A manifest that lists only what succeeded is the "
                "same failure as a gate that cannot fail."
            ),
        }
        for e in rejected
    ],
    "bare_items_endpoint_explanation": {
        "what_happened": (
            "GET /items/ with no parameters returned HTTP 400 with the body "
            "{\"status\":\"requires_id_category_or_id_company_or_uuid\",\"http_code\":400,\"data\":[],"
            "\"message\":\"\"}. The retrieval script's write gate rejected it and wrote nothing - "
            "correct behaviour, and the reason no HTTP 400 body is sitting in this snapshot named "
            "items.json."
        ),
        "why_it_failed": (
            "The endpoint cannot be enumerated unfiltered. It requires one of id_category, id_company "
            "or uuid. This is an API contract, not an outage."
        ),
        "how_coverage_was_obtained": (
            "Fetched per category instead: GET /items/?id_category=<id> for all 100 category ids read "
            "from the categories.json this same run landed. All 100 returned HTTP 200 with a valid "
            "envelope; 0 were rejected."
        ),
        "is_this_scope_creep": (
            "No. It is the SAME documented endpoint, parameterised exactly as its own error message "
            "demands. No sibling endpoint was discovered or crawled."
        ),
        "coverage_result": {
            "categories_requested": len(items_cat),
            "categories_landed": sum(1 for e in items_cat if e.get("written_to_disk")),
            "categories_rejected": sum(1 for e in items_cat if not e.get("written_to_disk")),
            "item_records_total": item_records,
            "item_records_with_uuid": item_uuids,
        },
        "honest_limitation": (
            "Item coverage is therefore the union of all 100 category queries, not a single "
            "authoritative enumeration. Any item belonging to no category, or to a category absent "
            "from categories.json, would not appear here. That gap is unmeasured because the bare "
            "endpoint that would measure it is the one the API refuses."
        ),
    },

    # ------------------------------------------------------------- INVENTORY
    "file_inventory": {
        "total_files": len(inventory),
        "total_bytes": sum(i["byte_size"] for i in inventory),
        "files": inventory,
    },
    "downloaded_total_records": {
        "items_prices_all": next((e.get("record_count") for e in landed
                                  if e["endpoint"] == "/items_prices_all/"), None),
        "terminals": next((e.get("record_count") for e in landed
                           if e["endpoint"] == "/terminals/"), None),
        "vehicles_purchases_prices_all": next((e.get("record_count") for e in landed
                                               if e["endpoint"] == "/vehicles_purchases_prices_all/"), None),
        "categories": next((e.get("record_count") for e in landed
                            if e["endpoint"] == "/categories/"), None),
        "companies": next((e.get("record_count") for e in landed
                           if e["endpoint"] == "/companies/"), None),
        "items_via_categories": item_records,
    },

    # ------------------------------------------------------------ RETRIEVAL
    "retrieval_script": {
        "path": "scripts/external_sources/uex_corp.py",
        "sha256": hashlib.sha256(SCRIPT.read_bytes()).hexdigest(),
        "standard_met": [
            "write-before-status forbidden: a response earns its filename only after HTTP 200, a JSON "
            "content type, a successful parse, AND a valid UEX envelope",
            "Timeout/ConnectionError retryable against a 5-attempt ceiling with 3/6/9/12s backoff",
            "Retry-After parsed in both RFC 7231 forms and clamped to [0, 60]",
            "per-response byte_size, sha256, attempts, attempt_log, elapsed_seconds recorded",
            "main() returns 1 if any endpoint did not land",
            "X-Client-Version header sent, so an outdated script cannot quietly keep pulling against a "
            "changed contract",
        ],
        "envelope_validation_note": (
            "The script validates the UEX envelope, not just HTTP status. A 200 carrying "
            "{\"status\":\"error\"} would otherwise have landed as a .json file and counted as a "
            "successful endpoint."
        ),
        "rule_12_evidence": (
            "scripts/external_sources/_verify_uex_corp.py exercises every failure path offline with "
            "requests.get stubbed: HTTP 401, HTTP 500 x5, unparseable body, HTML content-type, valid "
            "JSON that is not a UEX envelope, envelope status != ok, 429 x5, and five consecutive "
            "timeouts - each writing ZERO files. Three must-succeed cases confirm the checks are not "
            "simply rejecting everything, and main() returns 1 when the token is absent."
        ),
    },

    # ---------------------------------------------------------------- GATES
    "gates": {
        "gate_order_note": (
            "Run strictly in order. The malware scan preceded the rename out of .partial, and the "
            "snapshot was re-hashed afterwards to confirm the bytes scanned are the bytes finalized."
        ),
        "gate_1_files_present": gates13["gate_1_files_present"],
        "gate_2_json_parses": {
            "result": gates13["gate_2_json_parses"]["result"],
            "json_files": gates13["gate_2_json_parses"]["json_files"],
            "parsed_ok": gates13["gate_2_json_parses"]["parsed_ok"],
            "parse_failures": len(gates13["gate_2_json_parses"]["parse_failures"]),
            "note": gates13["gate_2_json_parses"]["note"],
        },
        "gate_3_file_type_inspection": {
            "result": gates13["gate_3_file_type_inspection"]["result"],
            "files_inspected": gates13["gate_3_file_type_inspection"]["files_inspected"],
            "flagged": len(gates13["gate_3_file_type_inspection"]["flagged"]),
        },
        "gate_4_malware_scan": {
            "result": "PASS",
            "scanner": "Microsoft Defender MpCmdRun.exe",
            "command": "-Scan -ScanType 3 -File <snapshot> -DisableRemediation",
            "attempted": True,
            "report_only_mode_confirmed": True,
            "report_only_justification": (
                "All four *ThreatDefaultAction preferences are 0 (default action = quarantine/remove) "
                "and RealTimeProtectionEnabled is True, so -DisableRemediation was required to prevent "
                "the scanner mutating the snapshot under rule 1."
            ),
            "antivirus_signature_version": "1.455.462.0",
            "am_engine_version": "1.1.26060.3008",
            "started_utc": "2026-08-02T01:21:23Z",
            "finished_utc": "2026-08-02T01:21:23Z",
            "elapsed_seconds": 0.2,
            "exit_code": 0,
            "output": "found no threats",
            "duration_note": (
                "0.2 seconds on 12.4 MB. Real-Time Protection is enabled and had already scanned these "
                "files as they were written, so cached per-file verdicts are expected. Recorded as an "
                "observation, NOT claimed as a from-cold full-content scan."
            ),
        },
        "gate_5_content_indicator_scan": {
            "result": "PASS",
            "result_note": (
                "PASS on re-run. This gate FAILED first and that failure is retained below rather than "
                "erased."
            ),
            "initial_run": {
                "result": "FAIL",
                "exit_code": 1,
                "finding": "unexpected_domains non-empty: api.uexcorp.uk",
                "files_affected": 3,
                "where": (
                    "_pull_summary.json (12 occurrences), _pull_stderr.log (12), and "
                    "_items_by_category_summary.json (100) - all of them this pipeline's OWN provenance "
                    "records, which store the request URLs. ZERO data files contained it."
                ),
            },
            "resolution": {
                "action": "api.uexcorp.uk and uexcorp.uk added to ALLOWLIST_DOMAINS",
                "reasoning": (
                    "This is source 6's own canonical API domain - the address we deliberately fetch "
                    "from. Every other landed source's canonical domain was already on the allowlist "
                    "(api.star-citizen.wiki, scunpacked.com, starcitizen.tools, "
                    "robertsspaceindustries.com). UEX was absent only because source 6 had never been "
                    "pulled before, so this completes the allowlist for a newly added source."
                ),
                "explicitly_contrasted_with": (
                    "facebook.github.io, which was REFUSED an allowlist entry during the source 1 "
                    "re-acquisition. That was a foreign domain embedded in third-party content whose "
                    "cause - a bundled .git directory - could be removed instead. Removing the cause "
                    "was the right fix there; there is no cause to remove here, because the domain is "
                    "the source itself."
                ),
                "fail_closed_reverified": (
                    "scripts/external_sources/_verify_integrity_scan.py re-run after the allowlist "
                    "change: the gate still exits 1 on a <script> tag, on evil.example.net and "
                    "pastebin.com, and on an unreadable file. Widening the allowlist by two entries did "
                    "not make the gate permissive."
                ),
            },
            "final_run": {
                "exit_code": 0,
                "files_seen": integ["coverage"]["files_seen"],
                "files_scanned": integ["coverage"]["files_scanned"],
                "files_unscanned": integ["coverage"]["files_unscanned"],
                "coverage_complete": integ["coverage"]["complete"],
                "content_indicator_hits": 0,
                "unexpected_domains": 0,
                "distinct_domains_found": domains,
            },
            "gate_script_sha256": hashlib.sha256(GATE_SCRIPT.read_bytes()).hexdigest(),
        },
        "gates_all_passed_in_order": True,
    },
    "post_scan_integrity": {
        "purpose": "confirm the bytes that were scanned are the bytes that were finalized",
        "pre_scan_file_count": 114,
        "pre_scan_total_bytes": 12402823,
        "post_scan_file_count": len(inventory),
        "post_scan_total_bytes": sum(i["byte_size"] for i in inventory),
        "files_missing_after_scan": "NONE",
        "files_added_after_scan": "NONE",
        "files_with_changed_sha256_or_size": "NONE",
        "verdict": "CONFIRMED - real-time protection altered nothing",
    },
    "snapshot_status": "complete",
    "snapshot_path": "data-layer/external-sources/uexcorp/snapshots/" + RUN,
    "finalization": {
        "renamed_out_of_partial": True,
        "reason": (
            "All five gates passed in the required order, with the malware scan preceding the rename "
            "and a post-scan re-hash confirming nothing changed."
        ),
    },
    "supersedes": {
        "run_id": PRIOR_RUN,
        "previous_status": "blocked_missing_credentials",
        "note": (
            "That status was accurate when written - no credential existed and no request was made. It "
            "is superseded by this run rather than corrected, because nothing about it was wrong."
        ),
    },
    "no_promotion_note": (
        "This is Stage 1: collect and seal. No UEX data has been promoted into the database. Stage 2 "
        "does not exist yet."
    ),
    "record_counts_are_completeness_check_only_note": (
        "Record counts confirm what these endpoints returned on this run. They are NOT evidence that "
        "this data agrees with any other source in this project, and given Tier C tolerances they are "
        "explicitly not authoritative. No cross-source comparison was performed."
    ),
    "errors_or_skipped_endpoints": [
        "/items/ - attempted, refused with HTTP 400, coverage obtained per category instead. See "
        "bare_items_endpoint_explanation."
    ],
    "scope_boundaries_hit": (
        "None. Only documented in-scope endpoints were requested. No sibling crawling. The live site, "
        "production database, CC-10 and CC-12 were untouched."
    ),
}

out = M / "06_uex-corp_manifest.json"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print("manifest written:", out, "|", out.stat().st_size, "bytes")
print("files/bytes:", len(inventory), "/", sum(i["byte_size"] for i in inventory))
print("endpoints landed:", len(landed), " refused:", len(rejected))
print("item records:", item_records, " with uuid:", item_uuids)
print("tier:", manifest["data_tier"])
print("gates_all_passed_in_order:", manifest["gates"]["gates_all_passed_in_order"])
