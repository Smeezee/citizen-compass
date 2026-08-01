# UPDATE — Task 2 COMPLETE: source 1 re-acquired without `.git`, all five gates passed

Snapshot `20260801T204744Z` is finalized. Every step of the work order executed
in the required order. About to commit and push under its explicit authority.

## The LFS trap — cleared, and proven rather than assumed

**`git lfs version` confirmed BEFORE cloning**, as required — `git-lfs/3.7.1`,
working in both Bash and PowerShell (`C:\Program Files\Git\cmd\git-lfs.exe`).
The Cowork-side absence does not apply to this shell.

The clone reported `Filtering content: 100% (1/1)` — the smudge filter resolving
exactly one tracked file. **That was treated as consistent-with, not proof-of.**

**Pointer scan — the actual evidence:**

| | |
|---|---:|
| files scanned for the pointer signature | **28,993** |
| pointer stubs found | **0** |
| unreadable files | 0 |

**Positive assertion on `items.json`:** exists `True`, actual **128,570,490
bytes** against a 104,857,600 floor, `parses_as_json` **True**, passed **True**.
Recorded with its result so a future reader can see the check ran.

The gate was exercised against known-bad input before being trusted, per rule
12. `lfs_pointer_scan.py --self-test` builds a real pointer stub and confirms
all four failure paths execute: stub detected and its intended size reported;
real JSON *under* the floor fails, so size is enforced independently of JSON
validity; a missing expected file fails rather than passing by omission;
known-good passes. That second case matters — a stub is valid UTF-8 and would
pass an "is it text?" check.

Work order's two corrections both independently verified: `ships/*-raw.json`
matches **zero** files, and `git lfs ls-files` returns exactly one entry,
`items.json`.

## Provenance captured BEFORE stripping

| field | value |
|---|---|
| git_head_commit | `4764726896973204a798325ed0f9ed7253e995e5` |
| git_branch | `master` |
| git_commit_date | 2026-07-16T14:46:09+02:00 |
| git_origin_url | `https://github.com/StarCitizenWiki/scunpacked-data.git` |
| origin URL exact match | **true** |
| head subject | `4.9.0-LIVE.12232306` |

**Head commit is identical to the previous snapshot's**, so upstream has not
moved — this is the same upstream state re-acquired cleanly, not newer data.
The head subject matching source 3's pinned game version is recorded as an
observation only; no cross-source comparison was performed.

## `.git` stripped — moved, not deleted

1.6 GB / 33 files moved to `_to_delete/20260801T204744Z_source1_git` per rule 1.
Verified absent from the snapshot and preserved in `_to_delete`.
`.gitattributes` deliberately retained — it is upstream repository *content*,
not git internals.

## Five gates, in order

| # | gate | result |
|---|---|---|
| 1 | files present | **PASS** — `.git` absent, 0 zero-byte, 0 read errors |
| 2 | JSON parses | **PASS** — **28,959 / 28,959** parsed individually, 0 failures |
| 3 | file-type inspection | **PASS** — 28,960 inspected, **0 flagged** |
| 4 | malware scan | **PASS** — exit 0, no threats, **44.4 s** |
| 5 | content-indicator scan | **PASS** — 28,960 scanned, 0 unscanned, coverage complete |

**Gate 3 contrast:** the previous snapshot carried four active Git LFS hooks and
stock git hook samples — shell scripts with `#!` shebangs — inside `.git`. Zero
executable signatures remain.

**Gate 4 is worth calling out.** 44.4 seconds of genuine scanning across 4.3 GB.
Every previous Defender scan in this project finished sub-second on cached
Real-Time Protection verdicts, and each was flagged as an observation rather
than claimed as a from-cold scan. This one measurably worked.

**Gate 5 result:** 0 content-indicator hits, 0 unexpected domains, and **0
distinct domains found at all** — the snapshot contains no http(s) URLs
whatsoever. Every URL in the previous snapshot (`github.com` x4,
`facebook.github.io` x1) lived inside `.git`. **No allowlist entry was added.**
The finding was resolved by removing its cause, not by widening the gate.

## Post-scan integrity

28,960 files / 4,482,004,723 bytes before **and** after the malware scan. Every
file re-hashed; 0 missing, 0 added, 0 changed. **The bytes that were scanned are
the bytes that were finalized.** CONFIRMED.

## Finalized

Renamed `20260801T204744Z.partial` -> **`20260801T204744Z`**, only after all
five gates passed. 28,960 files, 4.3 GB.

## Previous snapshot marked superseded

`20260731T041451Z`: `complete` -> `superseded`. Append-only — diff is **+20/-2**,
the two removals being the status field and a closing bracket regaining a comma.
**`protocol_compliance: "ordering_violated"` is preserved**, as is the
deliberate contradiction between its acquisition block and its later
post-acquisition verification. Its files were not touched.

It is superseded, not repudiated: its data is genuine at a verified upstream
commit, and its provenance fields are precisely what made this re-acquisition
verifiable against it.

Vocabulary already covers this use (case (a), amended earlier today) — no
further extension needed.

## Artifacts

- Snapshot: `data-layer/external-sources/scunpacked-data/snapshots/20260801T204744Z` (gitignored)
- Manifest: `data-layer/external-source-manifests/20260801T204744Z/01_scunpacked-data_manifest.json`
- Verification: git metadata capture, gates 1-3 report, LFS pointer scan, post-scan hashes
- New tool: `scripts/external_sources/lfs_pointer_scan.py` with its self-test

Excluded as regenerable: the 10.6 MB per-file integrity report and the 3.7 MB
pre-scan hash baseline. The **post-scan** hash set stays tracked, so the
finalized bytes remain re-verifiable from the repo.

## Boundaries

Live site, production database, CC-10 and CC-12 untouched. Nothing under
`testing/` involved. Retry budget unused — the clone succeeded first attempt.
