# Update: second-pass verification, findings, and corrections — 2026-08-01

From Claude-01 (Cowork session, back on Sonnet). Everything below was checked directly against files and git on this machine this session — nothing here is taken from a report.

## fps-items.json and starmap.json — now inspected

Both were previously flagged as uninspected in `data-layer/external-sources/scunpacked-data/snapshots/20260731T041451Z/`.

- **fps-items.json (48 MB)** — 5,420 FPS gear records. Personal weapons, weapon attachments, every armor slot (helmet, torso, legs, arms, undersuit, backpack), clothing, consumables, deployables. 5,190 of 5,420 have real names; the rest are placeholder/debug rows. Each record carries size, grade, dimensions, mass, manufacturer, and classification via a nested `stdItem` block. This is a genuine full weapon-and-armor stats catalogue. **No price field, no shop/location reference.**
- **starmap.json (3.0 MB)** — 2,054 location entities, 1,995 with real names. Richer metadata than `starmap_positions.json`: jurisdiction, affiliation, radar contact type, and an `Amenities` list (277 locations have one) naming service categories like "Hangar (L)" or "Vehicle Services." **No x/y/z coordinates at all** — those only live in `starmap_positions.json`.

**Conclusion: the item-inventory-by-location gap is still open.** Coordinates exist. Service categories per location exist. Full item stats exist. Nothing links a specific item to a specific shop at a specific price. UEX (source 6) is still the only path to that, and it hasn't been pulled yet.

## CC-07 — further along than recorded, not yet closed

`scripts/external_sources/scunpacked_com.py` was read in full. It already fails closed: every response is checked (status code, content-type, JSON parse) before being written, rejected responses are never saved, 429s honour `Retry-After` with clamping, and `main()` returns 1 if any endpoint didn't land.

Ran its test harness, `_verify_scunpacked_com.py` (no network, all fakes): **all assertions passed, exit code 0.**

This fix is already committed locally as `e1d60c9 Harden scunpacked_com.py against audit finding CC-07` — **but not pushed to origin**, and there are further uncommitted edits to the same two files sitting on top of that commit right now.

CC-07 as originally written up ("no status check, no retry, no rate-limit handling") is fixed in code. What's not done yet: using this fixed script to pull a fresh source-2 snapshot and re-status source 2 honestly. Don't close CC-07 in any tracking doc until that re-pull happens.

## The "gate scripts always return 0" claim — checked, mostly wrong

Two files were named: `finalize_scunpacked_com.py` and `finalize_star_citizen_wiki.py`.

- `finalize_scunpacked_com.py` **does not exist anywhere in this repo.** Confirmed with a full-tree search. There's nothing by that name to fix.
- `finalize_star_citizen_wiki.py` was read in full. It already returns 1 if any snapshot page failed to parse, 0 otherwise — with a comment explicitly calling this out as a fail-closed gate. It is not buggy.

No action needed here. Whatever produced this claim was stale.

## CC-16 — resolved with real numbers

Ran directly:

```
git status
git log origin/main..main --oneline
git log main..origin/main --oneline
```

**Ground truth: local `main` is 6 commits ahead of `origin/main`, 0 commits behind.** The 6 unpushed commits are the CC-07 hardening, the integrity_scan.py coverage fix, the source-1 gate fixes, the rescale script, the registry_sync non-ASCII fix, and the missing/corrupt 3D model checker.

Neither previous claim (17 commits reached origin; 4+ ahead unpushed) was exactly right. This resolves CC-16 — no need to re-check unless more commits land.

**Also worth knowing right now (not committed by this session, no push made — that's still your or Claude Code's call):**

- Modified but uncommitted: `.gitignore`, `CLAUDE.md`, `LATEST_HANDOFF.md`, several manifest/report JSONs under `data-layer/external-source-manifests/` and `external-source-verification/`, `releases/latest.html`, `run_e2e_test.py`, `static/preview.html`, plus further edits to `scunpacked_com.py` / `_verify_scunpacked_com.py` on top of the CC-07 commit.
- Untracked, never committed: `Backup-CitizenCompass.ps1`, a new manifest folder `20260801T042157Z`, two new raw data folders (`constellation-aquila`, `gladius`), a new docs file, several `docs/handoff_archive/*.md` entries, and the entire `testing/` folder built last session.
- All 6 local commits are ready to push — `git push origin main` — as soon as someone with real network access (Claude Code, or you directly) runs it. This Cowork session's bridge into this machine has no network access by design, so it can't push.

## DB backup redundancy — still blocked, and it's a decision, not an engineering task

Checked `C:\cc-backup\` — two folders exist, `20260730-231753` and `20260730-233853` (the 502.3 MB one that verified clean). **Neither is connected to this Cowork session**, so this session can't copy or move them without you granting folder access first.

Even with access, copying to another folder on the same machine doesn't fix the actual risk — both backups are already in one building. Real redundancy needs either the offsite account (Backblaze B2 recommendation is still on record, ~$0.28/month, not set up yet) or a genuinely separate physical device. Neither exists yet. This is waiting on your decision, not on more engineering.

## What this session did and didn't touch

Read-only against the live repo, snapshots, and git. Made zero commits and zero pushes, per standing rule (no commit or push without explicit go-ahead). `CURRENT-STATE.md` in the claude.ai project has been updated with all of the above in full detail — this file is the same information for the machine-side channel.
