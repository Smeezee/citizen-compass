# WORK ORDER — Task 2: re-acquire source 1 without `.git`

This is the file that never arrived. Task 2 was correctly held. Here it is.

**You have explicit go-ahead to commit and push for this task's scope.** Nothing outside it.

Everything in the "verified facts" section below was read directly off disk in a Cowork session on 2026-08-01. It is not inference — do not re-derive it, but do re-verify anything you are about to depend on.

---

## Why this task exists

Snapshot `20260731T041451Z` contains a live `.git` directory — 33 files, four active Git LFS hooks, a working remote. The re-gate correctly failed gate 5 on `facebook.github.io` inside a stock `fsmonitor-watchman.sample`, and correctly changed nothing.

**Decision: re-acquire without `.git`. Do not edit the sealed snapshot.**

1. `.git` holds nothing the manifest lacks. `01_scunpacked-data_manifest.json` already records `git_head_commit` = `4764726896973204a798325ed0f9ed7253e995e5`, `git_branch` = `master`, `git_commit_date`, `git_origin_url`, and `git_origin_url_verified_exact_match: true`. The provenance is banked. What remains is liability.
2. Removing `.git` from a finalized snapshot would mutate a sealed snapshot — breaking the rule in order to enforce it.
3. **Git mutates its own internals on read** — index refresh, gc, repack. A hash manifest covering `.git` internals drifts with nobody touching the data. A sealed snapshot that fails its own integrity check for no real reason is worse than no check, because it teaches everyone to ignore the alarm.
4. Once `.git` is gone, `facebook.github.io` goes with it. **Do not add an allowlist entry.** Gate 5 keeps full sensitivity on real data.

The hooks were verbatim stock Git LFS hooks, nothing injected. Reading them rather than guessing was the right call. The objection is not that they are malicious — it is that executable code should not live inside something defined as inert data.

---

## THE LFS TRAP — read this before writing any clone command

Verified on disk 2026-08-01. This is the part that can silently produce a snapshot that looks complete and is not.

`.gitattributes` in the snapshot root contains exactly two lines:

```
ships/*-raw.json filter=lfs diff=lfs merge=lfs -text
items.json filter=lfs diff=lfs merge=lfs -text
```

**What that means in practice:**

- `ships/*-raw.json` currently matches **zero files**. `ships/` holds 316 files, none with a `-raw` suffix, smallest 11,421 bytes. The pattern is vestigial upstream.
- **`items.json` is genuinely LFS-tracked, and it is 128,570,490 bytes.** In the current snapshot it resolved correctly — it begins `[{ "className": "Entity_D`, which is real JSON, not a pointer.

**The failure mode:** a clone that does not resolve LFS produces, in place of that 128 MB file, a pointer stub of roughly 130 bytes reading:

```
version https://git-lfs.github.com/spec/v1
oid sha256:<hash>
size 128570490
```

File count is unchanged. Directory structure is unchanged. Nothing is missing. The snapshot looks complete and **the largest single dataset in source 1 has been replaced by a text file describing itself.**

**`git lfs` is NOT available in every environment on this machine.** In the Linux side used by the Cowork bridge, `git lfs version` returns *"git: 'lfs' is not a git command."* It evidently was available when the original clone ran. Confirm `git lfs version` succeeds in whatever shell you actually run the clone from, **before** cloning — not after.

### Required gate — a positive test, not an assumption

Add this as an explicit check. Per hard rule 12, a check that cannot fail is not a check, so this one has to be able to fail and has to be exercised.

Scan **every file in the snapshot** for the pointer signature — the first bytes being `version https://git-lfs.github.com/spec/v1`. Do not scan only small files, do not scan only `items.json`, and do not infer from file size alone.

- **Any pointer stub found → the acquisition FAILED.** Leave the snapshot at `.partial`. Do not finalize, do not write a `complete` status, do not commit. Report it.
- Assert positively that `items.json` is over 100 MB and parses as JSON. Record the assertion and its result in the manifest, so a future reader can see the check ran rather than trusting that it did.

Record the LFS handling explicitly in the manifest: whether LFS was resolved, how, the tool version, and the result of the pointer scan. A snapshot whose manifest is silent about LFS cannot be distinguished later from one where nobody checked.

---

## Sequence

Ordering matters at two points. Both are called out.

1. **Confirm `git lfs version` works** in the shell you are about to clone from. If it does not, stop and report — do not clone and hope.
2. **Clone** `https://github.com/StarCitizenWiki/scunpacked-data.git` into a new snapshot directory with a new run ID, landing as `.partial`.
3. **Resolve LFS.** Confirm by the pointer scan above, not by assuming the clone did it.
4. **Capture git metadata into the manifest** — head commit, branch, commit date, origin URL, exact-match verification — matching the fields the previous manifest used.
5. **Now strip `.git`.** After capture, before finalization. Reversing these two loses the provenance permanently.
6. **Run all five gates in order**, same sequence as the source-2 re-land: files present → JSON parses → file-type inspection → Defender scan with `-DisableRemediation` → content-indicator scan. Malware scan precedes the rename out of `.partial`.
7. **Re-hash after the scan** and confirm nothing changed — the bytes that were scanned must be the bytes that get finalized. Source 3's `20260801T021731Z` did this correctly; match that standard.
8. Gate 5 should now pass with **zero** unexpected domains. If it does not, stop and report — do not rationalise past it. Explaining a failing gate is not the same as passing it.
9. **Write a manifest that earns its status** rather than assuming it, to the standard of `0ae0514`.
10. **Mark `20260731T041451Z` as `superseded`**, using the same vocabulary and reasoning as the source-2 supersession. Its data is genuine; its process did not verify what we now check for. Touch `snapshot_status` only — every field recording what happened during the original acquisition stands unchanged, and that snapshot's files are not modified.
11. Confirm `docs/EXTERNAL_SOURCE_STATUS_VOCABULARY.md` covers this use of `superseded`; extend it if not.
12. **Commit and push.**

---

## Hard boundaries

- Do not touch the live site — `static/preview.html`, `releases/latest.html`, anything deployed.
- Do not touch the production database. **CC-10 and CC-12 remain untouched** — they need an explicit yes from Sleven and are excluded from unattended work.
- Do not modify any existing finalized snapshot's files. Manifest status fields may be corrected by appending; data may not.
- Do not add an allowlist entry for `facebook.github.io`.
- Do not commit anything under `testing/`. `.gitignore` now excludes `testing/_deploy/`, `testing/_models/`, `testing/_tools/` and `testing/index.html` — `testing/_deploy` alone is 344 MB of compressed ship models. `testing/_layer.html` and `testing/build.py` are source and should be committed.
- A 5.8 GB clone that fails midway: clean up the partial per existing convention, report, **retry at most twice**.

**If blocked, or if something needs a decision:** write what you found to `inbox/`, stop, and report. A stopped task with a clear note is a good outcome. An improvised one is not.

---

## Known environment issue that will waste your time otherwise

The Cowork device bridge cannot unlink files, so any `git` command run through it leaves a `.git/index.lock` that git could not clean up. That blocks the next git operation with *"Another git process seems to be running in this repository."*

Several were created and moved aside to `_to_delete/` during the 2026-08-01 Cowork session, and the repo was left clean — `git rev-parse HEAD` and `origin/main` both return `cf57eeed05f4b6d3c86a0a2063a0952a22ba49cb`, 0 ahead, 0 behind. If you hit that error and no git process is actually running, this is why, and moving the lock aside is the fix.

---

## After this task

Source 1 closed leaves only **source 6 (UEX)** before Stage 1 is genuinely complete and Stage 2 becomes specifiable for the first time.

UEX token is obtained — handle `slevenkoal`, UID 92424, app `Citizen-Compass`, ACTIVE. Write it to `.env` as `UEX_API_TOKEN=`, confirm `.env` is gitignored, and verify with a single request before any pull. Base URL `https://api.uexcorp.uk/2.0/{resource}/`, Bearer auth, 120 req/min. Record it as **Tier C** in the manifest — UEX states its own data is community-reported, with tolerances of ±20% on commodities and ±100% on items. It is the only source for aUEC prices and in-game dealer locations, and it is never auto-promoted without review.

The token was exposed in a chat screenshot. Regenerate it once the pull completes.
