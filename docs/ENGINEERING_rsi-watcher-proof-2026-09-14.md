# OPS — RSI watcher proof
**Date:** 2026-09-14  
**Status:** DONE

## Task
- **Name:** `Citizen Compass RSI Watcher`
- **Command (registered):** `rsi-watcher\rsi-watcher.exe -check`
- **Working dir:** `rsi-watcher\`
- **Triggers:** Daily repeating hourly + AtLogOn
- **Register:** Elevated Ops under Owner GO (hard rule 6 lifted). `rsi-watcher/_ops_register_result.txt` → REGISTER_OK. State Ready.

## Manual prove
- `rsi-watcher.exe -check` / `-status`: feeds [devtracker 18, comm-link 25, patchbot 12]; LIVE 4.10.0; PTU 4.10.1 (12578875).
- State: `sc-brain/plumbing/state/rsi-watcher-state.json`
- Shelf: `sc-brain/cig-firehose/`

## Scheduled / remote fire prove (required)
- `schtasks /Run /TN "Citizen Compass RSI Watcher"` → SUCCESS, **LastTaskResult=0**, LastRunTime set.
- Parent process of scheduled launch: **svchost.exe** (Task Scheduler host).
- App outcome: `last_run_by=scheduled`, `last_good_scheduled` set, `-status` not STALE.
- How: `parent_windows.go` tags `-check` as scheduled when parent is taskeng/svchost/taskhost*; also supports explicit `-from-task`. `setup_rsi_watcher_task.ps1` updated to register `-check -from-task` on next re-register (optional).

## DONE
Register + manual + schtasks remote fire + scheduled state path all green.