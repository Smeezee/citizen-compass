# UPDATE — fixed the elevation flaw at its source: `setup_watcher_task.ps1`

This was the origin of the defect. `setup_checks_task.ps1` was copied from this
file and inherited it; I fixed the copy and left the original, calling it
"outside this order" and its parameters "inert". **That reasoning was wrong.**
The defect is not about parameters — it is that the script has no working dry
run at all, and this is the more dangerous of the two.

## Why this one mattered more

`setup_watcher_task.ps1` runs `Unregister-ScheduledTask` followed by
`Register-ScheduledTask` against the **inbox watcher — the sole writer of
`LATEST_HANDOFF.md`**. A "dry run" that is not dry tears down and rebuilds a
live service, and this project has already lost ~37,000 characters per
regeneration to two writers on one file. Leaving it was leaving a loaded
version of the exact failure that cost a day to diagnose.

## One subtlety worth stating

I added `-TaskName` while fixing this. Before, the name was hardcoded, so a real
run could only ever replace the existing task. **With a parameter, a second
watcher under a different name is now possible where it was not before** — which
makes forwarding the argument on elevation load-bearing rather than cosmetic. It
is forwarded, and `-WhatIf` refuses to elevate at all.

Also removed a `Read-Host "Press Enter to close"` from the "exe not found" error
path, which would have hung any non-interactive run.

## Proven by behaviour, from OUTSIDE the script

The script's own "Nothing was changed" line is not evidence. Scheduler state was
captured before and after and diffed.

**`setup_watcher_task.ps1 -WhatIf`:**

| | before | after |
|---|---:|---:|
| total scheduled tasks | 226 | 226 |
| diff rows (Name/Path/State/Action) | — | **0** |
| tasks matching `inbox_watcher` | 1 | **1** |
| watcher process PID | 21764 | **21764** |
| `LATEST_HANDOFF.md` bytes | 107978 | 107978 |

**The unchanged PID is the strongest single fact here** — the watcher was never
stopped, so nothing was torn down and rebuilt.

**`setup_checks_task.ps1 -WhatIf`** — re-proven the same way, because I had only
shown it echoing its parameters, which is the script talking about itself. Run
with a **deliberately different** `-TaskName 'CC Leak Probe Task' -At 04:44`, so
a leak would appear as a brand-new task in the diff rather than quietly
overwriting the existing one:

- 226 tasks before, 226 after, **0 diff rows**
- probe task exists: **False**
- tasks invoking `run_checks`: **exactly 1**

## Blast radius confirmed independently

Grepped every `.ps1` for `RunAs` / `Start-Process` rather than taking the count
on trust. Three hits, in two files: `setup_checks_task.ps1:87` and
`setup_watcher_task.ps1:65`, both now using the forwarding array, plus
`setup_watcher_task.ps1:25`, which is the comment documenting the old line.
`Backup-CitizenCompass.ps1` and `run_checks_scheduled.ps1` do not elevate.
That is the whole surface, and it is closed.

Both files parse with 0 errors, and the watcher script's real registration path
(`Unregister` → `Register` → `Start`) is intact at lines 112/115/128.

## The general rule, already recorded

CLAUDE.md now carries this under hard rule 12: a safety flag that silently does
not apply is a check that cannot fail, in the same class as `main()` returning
`None`. **Prove the flag by behaviour** — run the dry run, then confirm from the
outside that nothing changed.
