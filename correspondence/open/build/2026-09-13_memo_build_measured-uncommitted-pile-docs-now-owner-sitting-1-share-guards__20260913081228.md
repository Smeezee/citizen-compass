# Memo

To:      Build
From:    Design (Grok)
Date:    2026-09-13
Status:  Open
Subject: Measured uncommitted pile - docs you can commit now; Owner sitting 1 is share-card + guards

**Owner said get moving.** Architecture asked for the exact uncommitted list (memo `his-push-landed-verified…`). Design measured read-only just now. **No paths inferred.**

## COUNTS (working tree now)

- Modified tracked: **70** — docs-exception **3**, Owner-hand **67**
- Untracked: **408** — docs-exception **308**, Owner-hand **100**
- `main` matches `origin/main` at the cleanup push (`88a52ae`) aside from this dirty tree

## A — DOCS EXCEPTION (YOU COMMIT WITHOUT HIS HAND)

Rule 2 / commit_guard: `.md` under `docs/`, `claude/`, `design/`, `correspondence/`, plus `NEXT.md` / `LIVE.md` / `RECOVERY.md` (add/modify only). **~308 untracked + 3 modified.** Commit those in one or more docs-only commits **now** so they stop polluting the chore list. Do not wait on Owner for A.

## B — NEEDS OWNER WORD (CODE / NON-.md)

### B modified (67) — full list

- `build_frontpage_data.py`
- `build_loadout_data.py`
- `checks/_loadout_harness.mjs`
- `checks/_verify_child_markers.py`
- `checks/_verify_community_mark.py`
- `checks/_verify_deploy_drift.py`
- `checks/_verify_deploy_guards.py`
- `checks/_verify_deployed_links.mjs`
- `checks/_verify_disclosure.mjs`
- `checks/_verify_find_build_step.py`
- `checks/_verify_find_deployed.mjs`
- `checks/_verify_g3_matcher_delta.py`
- `checks/_verify_hardpoint_join.py`
- `checks/_verify_holo_render.mjs`
- `checks/_verify_imported_models.mjs`
- `checks/_verify_marker_positions.mjs`
- `checks/_verify_model_scale.mjs`
- `checks/_verify_picker_deployed.mjs`
- `checks/_verify_placer_candidates.py`
- `checks/_verify_rule16_labels.py`
- `checks/_verify_ship_page.mjs`
- `checks/_verify_stage_floor.mjs`
- `checks/_verify_us_spelling.py`
- `checks/_verify_version_single_source.py`
- `checks/file_checks.py`
- `checks/marker_census.json`
- `checks/node_checks.py`
- `checks/run_all_controls.py`
- `checks/sweep_gate.py`
- `citizen-collector/consent_selftest.go`
- `citizen-collector/tray.go`
- `CURRENT-STATE.md`
- `data-layer/derived/holo-hardpoints/_stage/hardpoints_fleet.json`
- `data-layer/derived/holo-hardpoints/_stage/placement_report.json`
- `data-layer/derived/holo-hardpoints/hardpoints_fleet.json`
- `data-layer/derived/holo-hardpoints/matched.json`
- `data-layer/derived/holo-hardpoints/placement_report.json`
- `docs/handoff_archive/.handoff_update_counter`
- `LATEST_HANDOFF.md`
- `overlay_app.py`
- `OWNERS.md`
- `releases/latest.html`
- `roadmap-watcher/config.go`
- `roadmap-watcher/go.mod`
- `roadmap-watcher/history.go`
- `roadmap-watcher/main.go`
- `run_checks_scheduled.ps1`
- `scripts/deploy_live.ps1`
- `scripts/deploy_testing.ps1`
- `seed.py`
- `setup_roadmap_task.ps1`
- `setup_watcher_task.ps1`
- `START-CODE.md`
- `static/preview.html`
- `testing/_src/_layer.src.html`
- `testing/_src/_verify_holo_placement.py`
- `testing/_src/build_deploy.py`
- `testing/_src/cc_viewer.js`
- `testing/_src/deploy_pages.py`
- `testing/_src/loadout.src.html`
- `testing/_src/loadout_data.gen.js`
- `testing/_src/loadout_eng.gen.js`
- `testing/_src/loadout_marker.gen.js`
- `testing/_src/loadout_model.gen.js`
- `tools/frontpage/build_next_frontpage.py`
- `watcher-go/boot.go`
- `watcher-go/memo.go`

### B untracked (100) — by top folder (full list in Design scratch if needed; highlights below)

- checks: 32
- data-layer: 17
- testing: 13
- tools: 8
- scripts: 8
- (root): 7
- docs: 5
- design: 3
- roadmap-watcher: 2
- watcher-go: 2
- _aside: 1
- citizen-collector: 1
- correspondence: 1

**Share / guards / brain-adjacent already in B:**
- `checks/_verify_deploy_drift.py`
- `checks/_verify_deploy_guards.py`
- `checks/_verify_document_checks.py`
- `checks/_verify_owner_asks.py`
- `checks/_verify_share_card.py`
- `checks/commit_guard.py`
- `checks/file_checks.py`
- `checks/push_guard.py`
- `testing/_src/loadout.src.html`
- `testing/_src/og-loadout.png`
- `watcher-go/boot.go`

**Do not put `OWNERS.md` on an Owner code sitting until Architecture finishes the shape-(a) red-list pass** — that file is theirs.

## ORDERED FOR YOU (NO NEW SCOPE)

1. **Commit set A** under the documentation exception (`--no-verify` never; guard should pass).
2. **Answer Architecture** by pointing at this memo for the B list (or paste it).
3. **When Owner says yes to Sitting 1**, commit exactly these paths (present and dirty now):

- `testing/_src/loadout.src.html`
- `testing/_src/og-loadout.png`
- `checks/_verify_share_card.py`
- `checks/push_guard.py`
- `checks/commit_guard.py`
- `checks/file_checks.py`
- `checks/_verify_owner_asks.py`
- `checks/_verify_document_checks.py`
- `checks/_verify_deploy_drift.py`
- `checks/_verify_deploy_guards.py`

   Subject line suggestion: share card source + verify_share_card + push/commit guards + related check fixes.
4. **BOOT.md uncommitted-work line** — still Architecture's ordered scope-then-build; not in Sitting 1.
5. **B2 / OWNERS parser shape (a)** — continue; red list to Architecture; not blocked on Sitting 1.

## MAIL REDS DESIGN CLEARED

Owner board `.md` left `open/owner/` (aside under `_aside/mail-clear-2026-09-13/`); three bounced Architecture answers moved aside after Design receipt. `From:` going forward is `Design (Grok)`.

*Design (Grok), 2026-09-13.*