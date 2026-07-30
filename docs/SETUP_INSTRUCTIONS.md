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

Put these two files directly in `C:\Users\david\citizen-compass\` (same
folder as your existing `ccpp.py` — the watcher imports it to refresh the
health score after every file):

- `inbox_watcher.py`
- (your existing `ccpp.py` — don't need to replace it, the watcher just
  needs it to already be there, which it already is)

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
- It doesn't touch `CITIZEN_COMPASS_HANDOFF.md` — that still needs manual
  updates. Automating that too is a reasonable next step if you want it.
