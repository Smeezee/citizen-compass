# UPDATE — source 2 re-landed and verified; Task 2 STOPPED (spec not received)

Work order with revised priorities. Tasks 1 and 3 skipped as instructed. Task 2
stopped with a blocker note. Source 2 re-land completed and green.

## SKIPPED as instructed

- **Task 1 — model compression.** Not started.
- **Task 3 — line endings.** Not started.

## STOPPED — Task 2 (source 1 re-acquisition without `.git`)

**The work order is not in this repo.** The document referencing "Task 1 model
compression / Task 2 source 1 re-acquisition / Task 3 line endings" was never
received. `session-addendum-2026-08-01.md` is also still missing — not in
`inbox/`, not anywhere in the tree.

The only work-order-shaped document present is
`docs/handoff_archive/20260731_234952_update_for_claude_code_next_actions_2026-08-01.md`,
whose five items are push / sort-working-tree / mark-FIX-3-done / close-CC-07 /
DB-backup. **Different document, different numbering.** Task 2 there is not
source 1 re-acquisition. I could not do "Task 2 as written" because I have never
seen it written.

Stopped rather than guessed, per the boundary rule. It is a 5.8 GB acquisition of
~29,000 third-party files and getting it wrong is expensive.

### What I established anyway, because it changes how the task must be done

**Source 1 uses Git LFS.** Verified read-only against the existing snapshot:

- `.gitattributes` marks `ships/*-raw.json` and `items.json` as
  `filter=lfs diff=lfs merge=lfs`
- `.git/lfs` holds **123 MB** of LFS objects
- the working-tree files are **real data, not pointer stubs** — `items.json` is
  125 MB of actual JSON, so LFS smudge ran during the original clone

**This is a SILENT SUCCESS trap (new CLAUDE.md rule 12).** A re-acquisition done
the obvious way — GitHub tarball/zip download, or `git clone` on a machine
without `git-lfs` — returns **130-byte pointer stubs** for those paths. They are
valid text, they have the right filenames, they pass a JSON-shaped smell test at
a glance, and the acquisition reports success. The snapshot would be quietly
worthless.

### Decisions needed before Task 2 can run

1. **Acquisition method.** `git clone --depth 1` with `git-lfs` present, then
   move `.git` aside — or something else? A tarball route must be rejected
   outright unless LFS pointers are resolved separately.
2. **Verification that LFS materialised.** Whatever method is used, the run must
   prove `items.json` and `ships/*-raw.json` are real data, not pointers, before
   the snapshot is finalised. Under rule 12 this check must be shown to fail on
   a pointer stub.
3. **What happens to the existing snapshot** `20260731T041451Z` — superseded and
   kept, or moved to `_to_delete/`? It is 5.8 GB. **Never deleted**, per rule 1.
4. **`.git` disposal.** "Without `.git`" means moving it to `_to_delete/`, not
   removing it.

Nothing was downloaded, moved, or deleted. Source 1 is exactly as it was.

## DONE — source 2 re-landed: `20260801T171748Z`

### Counts (actual, not assumed)

| endpoint | records | prior runs | match | bytes | measured elapsed |
|---|---:|---:|:--:|---:|---:|
| `/api/v2/ships.json` | **156** | 156 | YES | 501,057 | **2.19s** |
| `/api/labels.json` | **63,375** | 63,375 | YES | 6,706,738 | **3.16s** |

Ships: 156 unique `ClassName`, 0 duplicates. Labels: 63,375 unique keys. Both
landed on the **first attempt** — no retries, no 429, no 5xx.

**Third independent acquisition, byte-identical again** — matching SHA-256 *and*
ETag on both endpoints, across three separate days. Compared against the values
recorded in the earlier **manifests** (provenance records); no earlier
snapshot's files were read.

### Historical caveat — recorded

`Last-Modified: Wed, 16 Nov 2022 20:52:36 GMT`. Recorded in the manifest as
`label` and `historical_data_caveat`: **not evidence of current game state.**

### Gates, in order

| # | gate | result |
|---|---|---|
| 1 | files present | PASS — 4 files, none zero-byte |
| 2 | JSON parses | PASS — all 3 .json parsed individually |
| 3 | file-type inspection | PASS — all 4 by magic bytes, nothing flagged |
| 4 | malware scan | PASS — MpCmdRun ScanType 3 `-DisableRemediation`, exit 0 |
| 5 | content-indicator scan | PASS — 4/4 scanned, coverage complete, 1 domain (`scunpacked.com`), allowlisted |

**Post-scan integrity:** 4 files / 7,209,605 bytes before **and** after, every
file re-hashed. 0 missing, 0 added, 0 changed. **RTP altered nothing.**

Renamed off `.partial` only after all five passed. Malware scan preceded the
rename throughout.

### Manifest

`data-layer/external-source-manifests/20260801T171748Z/02_scunpacked-com_manifest.json`
— per-file SHA-256 and byte sizes, retrieval script SHA-256, gate script
SHA-256, attempt counts, measured timings, plus `_build_manifest.py` so the
numbers are reproducible rather than hand-typed.

## Old source 2 snapshot marked superseded — and a vocabulary problem worth knowing

`20260801T042157Z` moved `complete` -> `superseded`. Append-only: diff is
**+19/-2**, and the two removed lines are the status field itself and the former
last field regaining a trailing comma. No acquisition record, count, hash,
timing or gate result touched. Its files were not touched.

**This required amending the vocabulary, and the reason matters.** The original
definition of `superseded` — written for `20260731T031754Z` — required that the
superseded run *"did not, or could not, verify what it retrieved"*. That did not
describe `20260801T042157Z`, which was landed by the hardened script and passed
all five gates honestly. Under the original wording **no status fitted it**:
`complete` would imply it is still current, `failed` would libel good data.

`docs/EXTERNAL_SOURCE_STATUS_VOCABULARY.md` now defines `superseded` by **which
snapshot to use**, covering both an unverified run being replaced and a properly
verified one being replaced. Why a given snapshot was superseded lives in its
appended note, which is where the two cases are distinguished — and they are
distinguished explicitly, so this one is not mistaken for a verification
failure.

Current source 2 state:

| run | status |
|---|---|
| `20260731T031754Z` | superseded (never verified) |
| `20260801T042157Z` | superseded (verified, simply replaced) |
| `20260801T171748Z` | **complete — current** |

## Boundaries respected

Live site, production database, CC-10, CC-12 and `C:\cc-backup\` were not
touched. Nothing outside this list was started.
