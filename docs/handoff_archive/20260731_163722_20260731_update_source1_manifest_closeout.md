# Update — 2026-07-31: source 1 manifest closed out, snapshot released from quarantine

Pre-check passed, Part A clean, Part B applied. Nothing committed or pushed.
Nothing deleted.

## Pre-check — the strictness fixes did not overshoot

FIX 2, duplicate index still gone:

```
['ix_components_component_type_id', 'ix_components_manufacturer_id']
=== exit code: 0 ===
```

(Requires `venv\Scripts\python.exe`; bare `python` has no sqlalchemy.)

FIX 3, both gates still exit ZERO on clean input — neither became always-fail:

```
integrity_scan.py              CLEAN input -> exit=0
finalize_star_citizen_wiki.py  CLEAN input -> exit=0
```

Together with the earlier dirty-input runs (exit=1 on indicator hit, bad
domain, parse error) both scripts discriminate correctly.

## Part A — re-verification with v2

`verify_snapshot_v2.py` 2.0.0 run unmodified, 23:29Z-23:34:44Z, exit 0.

- `coverage.inspection_complete` — **true**
- `coverage.incomplete_reasons` — **[]** (empty)
- `findings.link_like_entries` — **0**
- `findings.extension_content_mismatch` — **0**
- `findings.json_parse_failures` — **0**
- `Compare-Object` v1 vs v2 SHA256SUMS — **returned nothing**, 28993 identical
  lines each

No stop condition triggered. Also 0 read errors, 0 walk errors, 0 changed/
appeared/vanished, empty indicator_totals and unexpected_domain_totals.

**One honest caveat, recorded in the manifest rather than smoothed over:**
28957 of 28959 JSON files got a full strict parse. The other 2 exceed the
64 MiB threshold and got a streaming bracket-balance check only — logged as
`structural_only`, which is NOT the same as parse-validated.

The v1 baseline (08:10Z) and v2 re-verification (23:34Z) bracket the malware
scan (16:19Z), so the identical hashes also prove the AV pass altered nothing.

## Part B — manifest updated, append-only

`data-layer/external-source-manifests/20260731T041451Z/01_scunpacked-data_manifest.json`

**Changed — exactly one field:**

```
- "snapshot_status": "partial",
+ "snapshot_status": "complete",
```

**Added — two top-level keys appended after `scope_boundaries_hit`:**

- `"protocol_compliance": "ordering_violated"` + `protocol_compliance_note`
- `"post_acquisition_verification": [ ... ]` — a list, one entry, covering
  performed_utc, current path + rename history, integrity_scan_v1,
  integrity_scan_v2, hash_manifest with the Compare-Object cross-check,
  malware_scan, post_scan_integrity, and gates_now_satisfied.

**Verified unchanged** (the acquisition-run record, left intact):

```
integrity_scan.malware_scan.attempted            : False
integrity_scan.malware_scan.report_only_mode...  : False
snapshot_path      : .../snapshots/20260731T041451Z
json_parse_check   : "sampled, not exhaustive: 40 of 28,959 ..."
domain_scan        : "not run this pass due to time budget ..."
status_reasoning   : present, untouched
```

Manifest re-parses as valid JSON.

The note is explicit that the discrepancy between the acquisition block
(`attempted: false`) and the later scan block is deliberate and must not be
reconciled — it *is* the record of what went wrong.

**Folder renamed** `20260731T041451Z.partial` -> `20260731T041451Z`.
Rename only. Re-counted immediately after: 28993 files, 6069879130 bytes,
both still matching baseline.

## What this snapshot now claims, precisely

All five gates have been performed and all five passed. The ordering violation
is permanent and is now recorded in the manifest itself rather than only in
`status_reasoning`. The guarantee is **"verified clean now"**, not "never
finalized while unverified".

Worth carrying forward: `verify_snapshot_v2.py` states in its own header that
it is not antivirus. Gate 4 is satisfied by the separate MpCmdRun pass, not by
v2 — the manifest says so explicitly so a future reader doesn't mistake the
integrity scan for an AV scan.

## Still open

`20260731T031754Z.partial` (the failed original run) is untouched, and the
stray `20260731T041451Z.partial.fsck_output.log` still sits beside the
now-renamed folder — its name no longer matches any folder. Neither touched;
flagging, not fixing.

## State

Working tree only. No commits, no pushes. Database, pipeline, live site
untouched.
