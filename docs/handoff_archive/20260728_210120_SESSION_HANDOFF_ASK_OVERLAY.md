# CITIZEN COMPASS — SESSION HANDOFF: ASK OVERLAY (TROUBLESHOOTING)

**Purpose:** fast continuation record — the desktop hotkey "Ask" overlay
is built and partially tested, but not yet confirmed running. Pick up
exactly here.

---

## WHAT THIS FEATURE IS

Global hotkey (Ctrl+Shift+Space) pops up a small dark window near the
top of the screen. Type a question, it searches local project files
first, falls back to a web search if nothing local matches, then asks
the local Ollama model (qwen3:14b) to answer using whatever context was
found. Typing only for now (voice input intentionally deferred).

## FILES (already in C:\Users\david\citizen-compass)

- **`ask_engine.py`** — the actual search+ask logic. **CONFIRMED WORKING**
  on the real machine:
  ```
  python ask_engine.py "what weapons does the arrow have"
  ```
  correctly found `hardpoints.json` (real ship data) ranked above
  unrelated docs, and got a real, honest answer back from Ollama
  ("hardpoint types are listed, but no specific weapon names are in the
  data" — an accurate reflection of what's actually in the files, not a
  bug).
- **`overlay_app.py`** — the popup window + hotkey shell. **NOT YET
  CONFIRMED WORKING.** This is the open item.

## BUG ALREADY FOUND AND FIXED THIS SESSION

`search_local_files()` originally had no ranking — any file mentioning a
keyword anywhere in its body text counted equally, so generic docs that
happened to mention "arrow" once in passing (e.g. describing data-flow
arrows in an architecture doc) crowded out the real ship-specific
`hardpoints.json` before it ever got sent to Ollama. Fixed by ranking
matches: a match in the ship's own folder name (e.g.
`ships/arrow/hardpoints.json`) outranks a filename match, which outranks
a plain body-text mention. Verified fixed on real data.

## CURRENT BLOCKER: overlay_app.py won't start

Sequence of what's been tried:
1. `pythonw.exe overlay_app.py` — returned immediately, no error (but
   `pythonw` never shows errors, so this proves nothing either way)
2. Checked `Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'"`
   afterward — only showed the **existing** `inbox_watcher.py` process
   (PID 2760, already running as a scheduled task). No second process
   for `overlay_app.py` ever appeared.
3. First attempt had a stray trailing backslash
   (`pythonw.exe overlay_app.py\`) which likely broke it — retried clean,
   still no second process appeared.
4. **Not yet tried:** running with visible `python.exe` instead of
   `pythonw.exe`, specifically to force any startup error to actually
   print instead of being silently swallowed. This is the very next step.

## NEXT STEP (do this first)

```powershell
cd C:\Users\david\citizen-compass
python.exe overlay_app.py
```

Two possible outcomes:
- **An error/traceback prints** — paste it back, that tells us exactly
  what's broken (likely candidates: `keyboard` or `pillow` not actually
  installed despite the pip command, a tkinter issue, or a permissions
  problem registering the global hotkey)
- **Nothing prints and the terminal just hangs (cursor doesn't return)**
  — that's actually correct behavior, means it's running. In that case,
  leave that window open and press **Ctrl+Shift+Space** to test the
  hotkey and popup.

## OTHER OPEN NOTES FROM THIS SESSION (lower priority, not blocking)

- Three near-duplicate `hardpoints.json` files exist for the Arrow ship
  (`hardpoints.json`, `hardpoints__20260728174803.json`,
  `hardpoints__20260728175011.json`) — leftover from earlier zip-drop
  testing. Safe to clean up later, not urgent.
- Admin rights may be needed for the global hotkey to register — if
  `python.exe overlay_app.py` runs with no error but Ctrl+Shift+Space
  still does nothing, try re-running from an **Administrator** PowerShell
  window instead.
- If `Ctrl+Shift+Space` conflicts with something else on the system,
  the hotkey can be changed by editing the `HOTKEY` variable near the top
  of `overlay_app.py`.

## STATUS SUMMARY

- `ask_engine.py` (search + Ollama logic) — done, confirmed working,
  ranking bug fixed
- `overlay_app.py` (hotkey + popup window) — built, not yet confirmed
  running; next step is forcing visible errors with `python.exe` instead
  of `pythonw.exe`
- Inbox watcher / OCR transcription / 24-7 persistence — all previously
  confirmed working (see earlier handoffs), unaffected by this work
