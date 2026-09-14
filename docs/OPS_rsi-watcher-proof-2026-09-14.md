# RSI watcher — DONE / PARTIAL proof (2026-09-14 post-reboot)

**Ops check after machine reboot.** Manual path proven. Scheduled automation waits on Owner (rule 6).

## DONE (manual / feeds)
| Check | Result |
|---|---|
| `rsi-watcher.exe -status` | All three sources configured; known ids: DT 18, CL 25, PB 12; LIVE 4.10.0 / PTU 4.10.1 |
| `rsi-watcher.exe -check` | `read [devtracker comm-link patchbot]; failed []; build read true` → CHECKED, NOTHING NEW |
| State | `sc-brain/plumbing/state/rsi-watcher-state.json` updated last_ok |
| Cards | Baseline correctly wrote no flood; prior proof card `sc-brain/cig-firehose/comm-link/21315.json` |
| Settings | Live `rsi-watcher/rsi-watcher-settings.json` (gitignored); example in repo |
| Setup script | `setup_rsi_watcher_task.ps1` present |

## PARTIAL (automation)
| Check | Result |
|---|---|
| Scheduled task | **Not registered.** `-WhatIf` prints WOULD register “Citizen Compass RSI Watcher” hourly + AtLogOn; **nothing changed**. |
| Status STALE | Expected until Owner runs real register (hard rule 6). |

## Owner one-liner (elevated only)
From `C:\Users\david\citizen-compass`, elevated PowerShell:

```powershell
.\setup_rsi_watcher_task.ps1
```

(Re-run `-WhatIf` first anytime.) Do **not** ask Ops to elevate this.

## Not done here
- Claude hourly shutdown (wait until scheduled proof green)
- Committing remaining untracked `rsi-watcher/*.go` if Code has not (Build owns that commit)

*Operations, 2026-09-14.*
