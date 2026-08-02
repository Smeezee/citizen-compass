# For Claude Code — next actions, verified this session (2026-08-01)

From Claude (Cowork session). Ground truth below was pulled directly from `git status`/`git log` and by reading the actual script files this session. Nothing here is secondhand.

## 1. Push — nothing to resolve first

```
git push origin main
```

Local `main` is 6 commits ahead of `origin/main`, 0 behind (verified this session — resolves the CC-16 contradiction in the transport dump). The 6 commits: CC-07 hardening on `scunpacked_com.py`, the `integrity_scan.py` coverage fix, source-1 gate fixes, the ship rescale script, the `registry_sync_check` non-ASCII fix, and the missing/corrupt-3D-model checker. Just push them.

## 2. Sort the working tree — Sleven's/your call, not mine

Modified but uncommitted: `.gitignore`, `CLAUDE.md`, `LATEST_HANDOFF.md`, several manifest/report JSONs under `data-layer/external-source-manifests/` and `external-source-verification/`, `releases/latest.html`, `run_e2e_test.py`, `static/preview.html`, plus further edits to `scunpacked_com.py` / `_verify_scunpacked_com.py` on top of the already-committed CC-07 fix.

Untracked, never added: `Backup-CitizenCompass.ps1`, a new manifest folder `20260801T042157Z`, two new raw folders (`constellation-aquila`, `gladius`), a new docs file, several `docs/handoff_archive/*.md` entries, and the whole `testing/` folder built in Cowork. Review and commit what's wanted before it piles up further.

## 3. FIX 3 in `LATEST_HANDOFF.md` — mark it done

It's listed as "make `integrity_scan.py` and `finalize_star_citizen_wiki.py` exit non-zero on findings, NOT yet run." Both scripts were read in full this session — both already fail closed correctly (`integrity_scan.py` returns 1 on any content hit, unexpected domain, or unscanned/unwalked file; `finalize_star_citizen_wiki.py` returns 1 on any parse failure). This is already fixed in the working tree, just not pushed. Update the handoff entry instead of re-doing the work.

## 4. Close CC-07 for real

The fix is written and its test harness (`_verify_scunpacked_com.py`) passes clean, no network, all assertions. What's not done: run `scunpacked_com.py` against a fresh source-2 pull, put it through the five gates in order, and re-status source 2 honestly in the manifest. That's the actual remaining work — the code fix alone doesn't close it.

## 5. Not a code task right now — flagging so it doesn't get lost

DB backup redundancy is blocked on Sleven, not on engineering. Two backup folders exist at `C:\cc-backup\20260730-231753` and `20260730-233853` (502.3 MB, hash-verified). Real redundancy needs an offsite account (Backblaze B2 recommendation is on record, not set up) or a genuinely separate device — a same-machine copy doesn't fix the actual risk.
