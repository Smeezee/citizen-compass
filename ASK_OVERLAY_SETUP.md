# Setting up the Ask Overlay (hotkey desktop assistant)

Two new files, both go into `C:\Users\david\citizen-compass`:

- **`ask_engine.py`** — the actual "brain": searches your local project
  files first, falls back to a web search, then asks your local
  `qwen3:14b` (via Ollama) to answer in plain English. Tested standalone
  in a sandbox against mock ship data — confirmed it correctly finds the
  right files for a matching question, correctly finds nothing for a
  gibberish question, and fails honestly (rather than crashing or
  guessing) if Ollama isn't reachable.
- **`overlay_app.py`** — the actual popup window + global hotkey. This is
  the GUI shell only; all it does is call `ask_engine.ask_question()` and
  display the result.

## 1. Install dependencies

```powershell
pip install keyboard pillow
```

(`tkinter`, used for the popup window, ships with standard Windows Python
already — nothing to install for that part.)

## 2. Quick test of the search/answer logic by itself (recommended first)

Before touching the hotkey/GUI part at all, confirm the core logic works
against your real project data:

```powershell
cd C:\Users\david\citizen-compass
python ask_engine.py "what weapons does the arrow have"
```

You should see something like:
```
[local] from your project files: <filename(s)>
<an actual answer from qwen3:14b>
```

If it instead says `Ollama unreachable`, check that Ollama is actually
running (`ollama list` in PowerShell should show `qwen3:14b`) before
moving on.

Try a query you know isn't in your files yet, to confirm the web
fallback path fires:
```powershell
python ask_engine.py "what is the latest Star Citizen patch version"
```

## 3. Run the actual overlay

```powershell
pythonw.exe overlay_app.py
```

Using `pythonw.exe` instead of `python.exe` means no console window
appears — it runs silently in the background.

Press **Ctrl+Shift+Space** from anywhere on your desktop. A small dark
popup window should appear near the top-center of your screen. Type a
question, press Enter, and the answer should appear in the box below
after a moment (it's calling Ollama, so allow a few seconds).

Press **Escape** to hide the window again — it stays running in the
background, ready for the next Ctrl+Shift+Space.

## 4. Making it start automatically (optional, same pattern as the watcher)

Once you've confirmed it works, you can register this in Task Scheduler
the same way `inbox_watcher.py` is set up — a task that runs
`pythonw.exe overlay_app.py` at login. Ask if you want help setting that
task up specifically; the steps are the same shape as what you already
did for the inbox watcher.

## Known limitations / things to watch

- **Hotkey conflicts:** if `Ctrl+Shift+Space` is already used by another
  program (some IMEs, some games), change the `HOTKEY` variable near the
  top of `overlay_app.py` to something else, e.g. `"ctrl+alt+q"`.
- **Admin rights:** if the hotkey doesn't fire while a specific window
  (e.g. a game running as Administrator) has focus, try running
  `overlay_app.py` as Administrator too — Windows won't let a
  lower-privilege process's global hotkey interrupt a higher-privilege
  window.
- **Web search scraping:** the web fallback uses a lightweight,
  no-API-key scrape of DuckDuckGo's HTML results. It's not as robust as
  a real search API — if DuckDuckGo changes their page layout, this could
  stop returning results (it'll fail gracefully and just say "nothing
  found," not crash). If you get a real search API key later (Bing,
  SerpAPI, etc.) this is a good thing to upgrade.
- **Local search is keyword-based, not semantic** — it looks for your
  question's important words appearing in filenames or file content
  under `docs\`, `tests\testing-site\ships\`, and `data-layer\`. Good
  enough for "what does the Arrow have," works less well for very
  indirect phrasing. Worth knowing as a current limitation, not a bug.
- **Voice input is not included** — you asked for typing-only in v1, so
  this is text-only for now. Adding voice later means adding a
  speech-to-text step (Windows' built-in one, or a local Whisper model)
  before the text reaches `ask_engine.ask_question()` — the rest of the
  pipeline wouldn't need to change.
