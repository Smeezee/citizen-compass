# UPDATE — Task 2 work order received, in progress (intake filed late)

## Filed late — rule 13 trigger 1 missed

CLAUDE.md rule 13 requires an `inbox/` update **when work arrives**, before
starting it: *"Being handed a work order is exactly this moment."* I received
`docs/workorder-task2-source1-reacquisition.md`, read it, and began executing —
confirming `git lfs version`, starting the clone, and writing the pointer gate —
without filing this first. Filing it now, mid-task, which is exactly the
situation the rule exists to prevent.

## What was received

`docs/workorder-task2-source1-reacquisition.md` — Task 2, re-acquire source 1
without `.git`. The file that had been missing; Task 2 was correctly held until
it arrived. It carries explicit commit-and-push authority for its own scope only.

## What it decided, and why it matters

Re-acquire rather than edit the sealed snapshot. `.git` holds nothing the
manifest lacks — `git_head_commit`, branch, commit date and origin URL are
already banked in `01_scunpacked-data_manifest.json`. What remains is liability.
Two points I had not considered and that settle the question:

- **Git mutates its own internals on read** — index refresh, gc, repack. A hash
  manifest covering `.git` would drift with nobody touching the data, producing
  a sealed snapshot that fails its own integrity check for no real reason. That
  teaches everyone to ignore the alarm.
- Removing `.git` from a finalized snapshot would mutate a sealed snapshot to
  enforce the rule about not mutating sealed snapshots.

Explicitly forbidden: adding an allowlist entry for `facebook.github.io`. Once
`.git` is gone it goes with it, and gate 5 keeps full sensitivity on real data.

## Corrections to what I had reported

The work order sharpens two things I got roughly right but imprecisely:

- `ships/*-raw.json` in `.gitattributes` matches **zero files**. `ships/` holds
  316 files, none with a `-raw` suffix. The pattern is vestigial upstream. I had
  implied both LFS patterns were live.
- The genuinely LFS-tracked file is **`items.json`, 128,570,490 bytes** — one
  file, not a class of them.

## Progress so far

1. **`git lfs version` confirmed BEFORE cloning**, as required. `git-lfs/3.7.1`
   works in both Bash and PowerShell here (`C:\Program Files\Git\cmd\git-lfs.exe`).
   The Cowork-side failure does not apply to this shell. No stale
   `.git/index.lock`; repo clean at `cf57eee`.
2. **Clone running** into
   `data-layer/external-sources/scunpacked-data/snapshots/20260801T204744Z.partial`.
   ~829 MB so far of an expected ~5.8 GB. `items.json` not yet materialised.
   Neither existing snapshot touched.
3. **Pointer gate written and proven** —
   `scripts/external_sources/lfs_pointer_scan.py`. Scans every file for the
   `version https://git-lfs.github.com/spec/v1` signature, reading only the
   first 200 bytes so it does not load a 128 MB file to check it, and separately
   asserts `items.json` exists, clears a byte floor, and parses as JSON.

   Exercised against known-bad input per rule 12, all four failure paths
   confirmed to execute: a pointer stub is caught and reports its intended size
   128,570,490; real JSON *under* the floor fails, so size is enforced
   independently of JSON validity; a missing expected file fails rather than
   passing by omission; known-good passes.

   That second case matters — a stub is valid UTF-8 and would pass an "is it
   text?" check, and a truncated real file would pass a "does it parse?" check.

## Still to do

Pointer scan -> capture git metadata -> strip `.git` -> five gates in order ->
re-hash after the malware scan -> manifest -> supersede `20260731T041451Z` ->
commit and push.

**If the pointer scan finds a stub, the acquisition has FAILED**: the snapshot
stays `.partial`, nothing is finalized, nothing is committed, and I report it.

CC-10 and CC-12 untouched. Nothing under `testing/` will be committed except
`_layer.html` and `build.py`.
