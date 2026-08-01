# Update — 2026-07-31: exhaustive read-only verification of scunpacked-data snapshot

Overnight verification job completed. Read-only throughout. Nothing committed,
renamed, moved, or deleted. Database, pipeline, and live site untouched.

## Target

Folder found: `20260731T041451Z.partial`
(under `data-layer/external-sources/scunpacked-data/snapshots/`)

The un-suffixed `20260731T041451Z` does not exist — this is the folder renamed
earlier on 2026-07-31. Left exactly where it is.

## Run

Command, exactly as specified, no added flags:

```
python scripts\external_sources\verify_snapshot.py "data-layer\external-sources\scunpacked-data\snapshots\20260731T041451Z.partial" --out "data-layer\external-source-verification\20260731T041451Z"
```

`scripts/external_sources/verify_snapshot.py` was run unmodified. Ran once,
start to finish, no interruption and no resume: 08:04:07Z to 08:10:15Z
(~6 minutes, ~80 files/s, faster than the 30-min-to-hours estimate).
Exit code 0.

## Reported numbers (from verification-report.json)

Coverage:

- `coverage.inspection_complete` — **true**
- `coverage.files_inspected` — **28993**
- `coverage.json_files_found` — **28959**
- (`files_enumerated` 28993, `files_unreadable` 0, `json_files_parsed_ok` 28959)

Findings:

- `findings.json_parse_failures` — **0**
- `findings.extension_content_mismatch` — **0**
- `findings.files_with_active_content_indicators` — **0**
- `findings.files_with_unexpected_domains` — **0**
- `findings.read_errors` — **0**
- `findings.walk_errors` — **0**
- (`findings.duplicate_hash_groups` — 2)

Full blocks, both empty:

```json
"indicator_totals": {},
"unexpected_domain_totals": {}
```

Every list under `detail` is empty — no paths to report:
`read_errors`, `json_parse_failures`, `extension_content_mismatch`,
`files_with_active_content_indicators`, `files_with_unexpected_domains`,
`walk_errors` are all `[]`.

Totals recorded: 28993 files, 6,069,879,130 bytes, 28959 json, 34 non-json,
33 git-internal.

The 2 duplicate hash groups (from `duplicates.json`):

```
bc3b5627...de062  ->  items.json
                      .git/lfs/objects/bc/3b/bc3b5627...de062
cba4981a...9f59a  ->  .git/logs/HEAD
                      .git/logs/refs/heads/master
                      .git/logs/refs/remotes/origin/HEAD
```

## Scope note — what this run did NOT do

Per fail-closed: this closes the per-file hash gap, the exhaustive JSON-parse
gap, the file-type gap, and the domain/indicator gap. It did **not** run an
antivirus/malware scan — `verify_snapshot.py` makes no AV call. The manifest's
`malware_scan.attempted: false` therefore still stands and remains unaddressed.

## Artifacts written (all outside the snapshot)

`data-layer/external-source-verification/20260731T041451Z/`

- `verification-report.json` (1,790 B)
- `SHA256SUMS.txt` (3,267,861 B — per-file hashes, previously nonexistent)
- `journal.jsonl` (8,581,563 B — untruncated per-file records)
- `duplicates.json` (376 B)
- `verify.log` (10,943 B)

## State

No decision taken on the snapshot folder's `.partial` status — that call comes
after review of these results. Stopping here as instructed.
