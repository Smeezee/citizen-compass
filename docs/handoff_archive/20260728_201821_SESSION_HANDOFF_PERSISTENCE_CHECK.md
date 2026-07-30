# CITIZEN COMPASS — SESSION HANDOFF: 24/7 PERSISTENCE CHECK (IN PROGRESS)

**Purpose:** short continuation record — mid-investigation into whether
`inbox_watcher.py` is actually running 24/7 in the background. Not
resolved yet, see below.

---

## GOAL

Confirm `inbox_watcher.py` runs continuously and silently (survives
reboot/logoff, no visible window), not just manually in a PowerShell
window someone keeps open.

## WHAT WE FOUND

`pipeline_log.txt` shows **seven separate "Watcher started" lines
throughout the session** (17:16, 17:32, 17:37, 18:25, 19:28, 19:50,
20:11), every one lining up with a manual `python inbox_watcher.py`
run in a foreground PowerShell window. There is **no gap in the log
corresponding to the machine reboot** that just happened — meaning as
of the last log line seen, there was no evidence yet of an automatic,
scheduled restart.

**However**, right after the reboot, a check turned up something
important:
```
Get-Process python,pythonw -ErrorAction SilentlyContinue
```
showed a **`pythonw` process already running (PID 2760)**, and:
```
Get-CimInstance Win32_Process -Filter "ProcessId = 2760" | Select-Object ProcessId, CommandLine
```
confirmed it's running:
```
"C:\Program Files (x86)\Python311-32\pythonw.exe" inbox_watcher.py
```
That's a silent, no-console-window process — exactly the shape of a
working background setup. This directly contradicts what the log
showed (no fresh start line, no reboot-aligned gap).

## OPEN QUESTION — NOT YET ANSWERED

Need to reconcile: is this `pythonw` process...
(a) started by a genuine Task Scheduler task or startup shortcut,
    actually proving 24/7 persistence works, but possibly logging
    failed silently or wrote somewhere unexpected, OR
(b) something that predates the reboot and never actually got killed
    (would be unusual — a real reboot kills all processes — but not
    yet ruled out), OR
(c) a Task Scheduler task DOES exist (maybe from the original
    inbox-automation session's `SETUP_INSTRUCTIONS.md`, which was
    fully rewritten since and not re-inspected this session) and IS
    firing correctly — in which case the persistence goal may already
    be met and just needed this check to confirm it.

## NEXT STEPS (pick up here)

1. Run `Get-Process -Id 2760 | Select-Object Id, StartTime` — if the
   start time lines up with right after the reboot/login, that's strong
   evidence (b) is false and this is a real scheduled start.
2. Run `Get-Content C:\Users\david\citizen-compass\pipeline_log.txt -Tail 10`
   (fresh read, not a stale open Notepad window) to see if newer log
   lines exist that weren't visible in the earlier check.
3. Check whether a Task Scheduler entry actually exists:
   ```powershell
   Get-ScheduledTask | Where-Object {$_.TaskName -like "*inbox*" -or $_.TaskName -like "*watcher*"}
   ```
   This will settle definitively whether persistence is configured via
   Task Scheduler, or whether PID 2760 is running for some other
   reason (e.g. a Startup folder shortcut, a registry Run key, or a
   leftover process).
4. Once the mechanism is identified, confirm it actually logs correctly
   going forward — drop one more test file into `inbox\` and check
   `pipeline_log.txt` updates in real time without any manual
   PowerShell window open.
5. If no scheduled task/startup entry is found at all (i.e. PID 2760
   turns out to be unexplained), stop it and set up Task Scheduler from
   scratch, silent (`pythonw.exe`), trigger "at log on."

## STATUS SUMMARY FOR NEXT SESSION

- Feature itself (image OCR → transcription → doc filing) — confirmed
  working, done, documented in the prior handoff
  (`SESSION_HANDOFF_IMAGE_OCR_v2.md`)
- 24/7 persistence — **unresolved**, actively being investigated,
  contradictory evidence found (see above), next steps listed above
  pick up exactly where this session left off
