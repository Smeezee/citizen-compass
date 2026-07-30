# Inbox Watcher — Setup (Windows)

This is the "dump everything in one folder, it sorts itself out automatically"
piece. It's a Python script (`inbox_watcher.py`) that watches an `inbox/`
folder inside your project and files anything dropped there.

**[UNKNOWN]** whether it runs cleanly on your machine — this was only tested
in a Linux sandbox against a synthetic copy of your folder structure, not on
your actual Windows box or your real 232-ship data. Test it on a few files
before trusting it with the real dataset.

---

## 1. Files to place

Put these three files directly in `C:\Users\david\citizen-compass\` (same
folder as your existing `ccpp.py` — both scripts import it to refresh the
health score):

- `inbox_watcher.py`
- `generate_handoff.py`
- (your existing `ccpp.py` — don't need to replace it)

## 2. Install the one dependency

```
pip install watchdog
```

## 3. Test it manually first

```
cd C:\Users\david\citizen-compass
python inbox_watcher.py
```

You should see:
```
[timestamp] Watcher started. Watching: C:\Users\david\citizen-compass\inbox
[timestamp] Now watching for new files. Leave this running.
```

Drop a test file into the `inbox` folder it just created and watch the
console — you should see a line showing where it got filed. Check
`pipeline_log.txt` in the project root for the same thing, since that log
persists after you close the window.

Press `Ctrl+C` to stop it once you're satisfied it's working.

## 4. What it does with each file type

| Dropped file | Goes to | Notes |
|---|---|---|
| `*.json` with `hardpoints: [{position:...}]` | `tests/testing-site/ships/<slug>/hardpoints.json` | matched by ship slug in filename or a `ship_slug` field |
| `*.json` with `weapons_by_category` or "hardpoint"/"weapon" in the filename | raw hardpoint data-layer folder | **and** immediately auto-categorized into turrets/missiles/weapons/components in the processed folder |
| `*.json` with `ship_slug` + `ship_name` and no hardpoints | ship-spec data-layer folder | |
| any other `.json` | `data-layer/raw/misc/` | flagged in the log as unclassified — check if it needs a new rule |
| `.glb` / `.blend` | `tests/testing-site/ships/<slug>/model.glb`, matched by filename | falls back to `models/_unsorted/` if no ship slug matches |
| `.md` | `docs/` | |
| `.py` | project root | so `ccpp.py`'s scan picks it up |
| anything else | `_needs_review/` | never guessed at, never silently dropped |

If a destination file already exists, the incoming one is renamed with a
timestamp instead of overwriting — nothing gets silently replaced.

After every file, it re-runs your existing `ccpp.py` scan logic and updates
`citizen-compass.ccpp`, and logs the refreshed health score.

## 4b. The always-current handoff file

Every time anything is processed — a file drop *or* a manual run — it also
regenerates **`LATEST_HANDOFF.md`** in the project root. That's the file to
open or copy/paste whenever you need a fresh AI onboarded. It always has two
parts:

- **CURRENT STATE (auto)** — health score, ship/viewer counts, data file
  counts, pulled fresh from `ccpp.py` every single time. Never hand-edit
  this part, it's overwritten on every run.
- **PROJECT NOTES** — the body of the most recent handoff-style document
  you dropped into `inbox/` (anything named or headed like a "handoff" or
  "session archive"). The raw file is archived, untouched, in
  `docs/handoff_archive/` first — nothing is ever lost, only the copy shown
  in `LATEST_HANDOFF.md` may be shortened.

**"Compressed":** if your local Ollama (`qwen3:14b`) is running and
reachable at `localhost:11434`, the dropped handoff gets compressed into a
tight bullet-point briefing. **[UNKNOWN]** whether this actually works on
your machine — it was only tested against a sandbox with no Ollama running,
where it correctly detected the connection failure and fell back to
showing the raw text unmodified (logged plainly, not hidden). When you try
it for real, check `pipeline_log.txt` for either "Handoff compressed via
local Ollama model" or "Local AI compression unavailable" — don't assume
compression happened just because the file updated.

**Quick command, no file drop needed:** you can also just run

```
python generate_handoff.py
```

any time to force a fresh `LATEST_HANDOFF.md` — useful right before you
paste it into a new AI conversation, without waiting for the watcher to
notice anything.

**First run:** if you haven't dropped any handoff doc yet but
`CITIZEN_COMPASS_HANDOFF.md` already exists in the project root, it seeds
`LATEST_HANDOFF.md` from that automatically (read-only — your original file
isn't touched or moved).

## 5. Run it automatically at login (so you never start it by hand)

This uses the same Task Scheduler approach that's already working for your
mcpo task.

1. Open **Task Scheduler** → **Create Task** (not "Basic Task" — you want
   the full dialog so you can set "Run whether user is logged on or not"
   if you want it, though "at log on" is usually enough here).
2. **General tab:** name it `Citizen Compass Inbox Watcher`. Check
   "Run only when user is logged on" (simplest option — matches how you're
   likely running things now).
3. **Triggers tab → New:** Begin the task **At log on**.
4. **Actions tab → New:**
   - Program/script: `pythonw.exe` (the "w" variant runs without a console
     window popping up — use `python.exe` instead if you want to see the
     window for now, while you're still trusting it)
   - Add arguments: `inbox_watcher.py`
   - Start in: `C:\Users\david\citizen-compass`
5. Save. Log off and back on (or right-click the task → **Run**) to confirm
   it starts. Check `pipeline_log.txt` for the startup line to confirm it's
   actually alive — don't just assume the task running means the script is
   working.

## 6. Stopping / restarting

If you used `pythonw.exe`, there's no window to close — end it from Task
Manager (look for `pythonw.exe`) or disable the scheduled task, then run it
again after making changes.

## Known limitations (as-built, not yet solved)

- **[UNKNOWN]** how it behaves with very large files (e.g. sizeable `.blend`
  files) — the "wait until file size is stable" check should handle slow
  copies fine, but wasn't tested against anything bigger than a few bytes.
- It only watches the top level of `inbox/`, not subfolders — drop files
  directly in, not in subfolders within it.
- The "auto-categorize weapons" step reuses the same type-matching rules as
  your existing `hardpoint_organizer.py` (turret/missile/gun keyword
  matching). If a weapon type doesn't match any keyword, it falls into
  "components" by default — same behavior as the original script, not a new
  bug.
- It doesn't touch `CITIZEN_COMPASS_HANDOFF.md` — your original stays as-is.
  `LATEST_HANDOFF.md` is the new "always current" file to use going
  forward; treat the old one as a frozen reference point if you like.
- The Ollama compression call uses `qwen3:14b` at `localhost:11434` — if
  you ever switch which model is your "manager" model, update
  `OLLAMA_MODEL` near the top of `generate_handoff.py` to match. If Ollama
  is slow or under load, the call can take a while — `OLLAMA_TIMEOUT_SECONDS`
  (120s default) is there so it doesn't hang forever if something's wrong.
