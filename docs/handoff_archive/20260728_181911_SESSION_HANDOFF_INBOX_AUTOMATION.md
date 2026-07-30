# CITIZEN COMPASS — SESSION HANDOFF: INBOX AUTOMATION BUILD

**Purpose of this file:** a compiled record of what got built and figured
out in this chat session, so it can be pasted into a new AI conversation
(or read by future-you) without losing context. Covers only the inbox
automation work — for the broader Citizen Compass project (Arrow viewer,
hardpoint data, Docker/Ollama stack), see `CITIZEN_COMPASS_HANDOFF.md` /
`LATEST_HANDOFF.md` in the project folder.

---

## WHAT WAS BUILT THIS SESSION

Three files, all designed to work together, sitting in
`C:\Users\david\citizen-compass`:

1. **`inbox_watcher.py`** — a background process that watches one folder
   called `inbox`. Anything dropped in there — any file, any name, no
   sorting required beforehand — gets inspected and automatically filed to
   the right place:
   - raw hardpoint/weapon JSON → data-layer raw folder, **and**
     auto-categorized into turrets/missiles/weapons/components
   - viewer hardpoint placement JSON (has x/y/z positions) → straight into
     the matching ship's viewer folder
   - `.glb`/`.blend` 3D models → matched to a ship folder by filename
   - `.py` scripts → project root
   - `.md` docs → `docs/`, unless they look like a handoff/session-archive
     doc, in which case they get archived and adopted as the current
     project notes (see below)
   - anything unrecognized → `_needs_review/`, never silently discarded

2. **`generate_handoff.py`** — builds `LATEST_HANDOFF.md`, a single
   always-current file combining live project stats (health score, ship
   counts, data counts, pulled from `ccpp.py`) with the notes from
   whichever handoff doc was most recently dropped into `inbox/`. Can be
   run any time on its own (`python generate_handoff.py`) for an on-demand
   refresh, or it fires automatically after every file the watcher
   processes. Tries to compress dropped handoff docs using the local
   Ollama model (`qwen3:14b` at `localhost:11434`); falls back cleanly to
   showing the raw text if Ollama isn't reachable — check
   `pipeline_log.txt` to see which happened, never assume.

3. **`SETUP_INSTRUCTIONS.md`** — step-by-step setup guide, including how to
   make the watcher start automatically at Windows login via Task
   Scheduler (same pattern already working for the mcpo filesystem tool).

**All three were tested in a sandboxed Linux copy of the project structure,
not on the real Windows machine** — every classification rule (hardpoint
data, viewer placements, models, docs, handoff docs, unrecognized files)
was confirmed working end-to-end there, including the handoff archiving +
`LATEST_HANDOFF.md` regeneration. The one thing that could **not** be
tested in the sandbox is the real Ollama compression call, since no Ollama
server was reachable there — it correctly fell back to raw text and logged
the connection failure, but whether it actually succeeds against the real
`qwen3:14b` on the Windows box is still unverified.

**You already have all three files downloaded** from earlier in this chat
— look for `inbox_watcher.py`, `generate_handoff.py`, and
`SETUP_INSTRUCTIONS.md` in your Downloads folder (or wherever your browser
saves chat downloads) and move them into
`C:\Users\david\citizen-compass` if you haven't already.

---

## CURRENT STATUS (mid-setup, in progress)

- `pip install watchdog` — **done, confirmed successful**
  (`Successfully installed watchdog-6.0.0`)
- Python installation on this machine: 32-bit Python 3.11 at
  `C:\Program Files (x86)\Python311-32\python.exe`
- Hit an issue where `inbox_watcher.py` existed as an empty **folder**
  instead of the actual script file (likely created by accident before the
  real file was saved/moved in) — this caused a
  `can't find '__main__' module` error when trying to run it
- Fix in progress: delete the folder (`rmdir /s /q inbox_watcher.py`),
  confirm it's gone (`dir inbox_watcher.py` → "File Not Found"), then
  re-download the real files from this chat and move them into
  `C:\Users\david\citizen-compass`, confirming with `dir *.py` that both
  `inbox_watcher.py` and `generate_handoff.py` show up with a real file
  size (not `<DIR>`)

## NEXT STEPS ONCE THE FILE-VS-FOLDER ISSUE IS FIXED

1. Run `python inbox_watcher.py` — should print "Watcher started" and
   "Now watching for new files"
2. Drop a test file into the `inbox` folder that gets created, confirm it
   moves somewhere sensible and a line appears in `pipeline_log.txt`
3. Stop the test run (Ctrl+C), then set it up in Task Scheduler to start
   automatically at login (`pythonw.exe`, argument `inbox_watcher.py`,
   start-in folder `C:\Users\david\citizen-compass`) — full click-by-click
   steps are in `SETUP_INSTRUCTIONS.md`
4. Confirm it survives a log-off/log-on cycle by checking
   `pipeline_log.txt` for a fresh "Watcher started" line
5. Once confirmed alive, test a real handoff doc drop and check whether the
   Ollama compression actually fires (look for "Handoff compressed via
   local Ollama model" vs. "Local AI compression unavailable" in
   `pipeline_log.txt`) — this is the one piece still unverified on the real
   machine

## KNOWN QUIRKS / THINGS TO WATCH

- Both a regular `cmd` window and a PowerShell window have been used
  interchangeably this session — PowerShell opened with PSReadLine
  disabled ("screen reader detected" warning), which doesn't affect any of
  this, just cosmetic
- If commands get pasted and accidentally merge onto one line (happened
  once already, producing a bogus `pip install watchdogpython` command),
  that's a paste issue, not a script problem — just re-type the two
  commands on separate lines
