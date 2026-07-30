# CITIZEN COMPASS — SESSION HANDOFF: IMAGE/OCR INTEGRATION (COMPLETE)

**Purpose:** consolidated record of the image-screenshot-transcription
feature, fully built, bug-fixed, and confirmed working on the real machine
this session. Covers only this feature — for the base inbox-automation
layer, see the earlier handoff doc; for the broader Citizen Compass
project, see `CITIZEN_COMPASS_HANDOFF.md` / `LATEST_HANDOFF.md`.

---

## STATUS: FEATURE CONFIRMED WORKING END-TO-END

Drop a screenshot into `inbox\` and it now:
- Gets OCR'd via Tesseract
- If it has real text (chat log, notes, terminal output, error dialog):
  transcribed to a `.md` file, dropped back into `inbox\`, and picked up
  by the existing doc classification logic — filed to `docs\` as a plain
  doc
- If it has little/no text (a render, mockup, photo): filed to
  `_needs_review\images\`, parked for a future vision-analysis step (not
  yet built)
- Original image is never deleted — archived to
  `docs\handoff_archive\images\`

This was verified on the real Windows machine with a real 498-word
screenshot (a chat window + code editor). Transcription quality: prose
paragraphs came through nearly perfect (a few missing spaces); a dense
code block with line numbers came through rougher (a few misspelled
words, stray line-number digits bleeding in from the editor gutter) —
usable to know what the code says, not reliable enough to copy-paste and
run without a glance-check. Some UI icons/buttons got misread as garbage
characters (harmless noise, easy to ignore).

## BUG FOUND AND FIXED THIS SESSION

The transcription `.md`'s auto-generated header comment originally
included the phrase "archived at .../handoff_archive/..." —
`generate_handoff.is_handoff_doc()` scans for the substring `"HANDOFF"`
as a heading hint, so every transcribed screenshot was being
misclassified as a full handoff document (which would have wrongly
replaced the PROJECT NOTES section of `LATEST_HANDOFF.md`) instead of
filing as an ordinary doc. Fixed by rewording the header comment.
Confirmed fixed on the real machine: the test screenshot above correctly
landed in `docs\`, not in the handoff archive as a notes replacement.

## FILES CHANGED/ADDED

- **`image_handling.py`** (new) — OCR + routing logic. Lives in
  `C:\Users\david\citizen-compass`.
- **`inbox_watcher.py`** (modified) — added one dispatch branch inside
  `classify_and_route()`, calling into `image_handling`. No other
  existing logic touched.

## KNOWN SIDE ISSUE (not fixed, not blocking)

Dropping a `.zip` whose extracted files collide with existing filenames
works correctly (files saved safely with a `__timestamp` suffix, nothing
overwritten) — but archiving the original zip afterward can fail on
Windows with:
```
[WinError 32] The process cannot access the file because it is being
used by another process
```
This is a Windows file-lock race in `handle_zip()` (extracts into a temp
folder inside `inbox\`, then immediately tries to move the original zip
— Windows/antivirus can briefly hold a lock right after extraction).
Not fixed. If zip drops become routine, this is worth hardening with a
retry-with-backoff around the `shutil.move`/`shutil.rmtree` calls.

## PERSISTENCE / 24-7 STATUS — NEEDS ACTION, NOT YET CONFIRMED

**This is the important open item.** As of this session, `inbox_watcher.py`
has only been run manually, in the foreground, in a PowerShell window kept
open by hand:
```powershell
cd C:\Users\david\citizen-compass
python inbox_watcher.py
```
This does **not** survive closing the window, logging off, or rebooting.
`SETUP_INSTRUCTIONS.md` (from the original inbox-automation session)
documents how to register it in Windows Task Scheduler to run
automatically at login via `pythonw.exe` (no visible window, survives
reboot) — **it is not confirmed whether this step was ever actually
completed.** Next session should either confirm the Task Scheduler task
already exists and is enabled, or walk through creating it from scratch
using `SETUP_INSTRUCTIONS.md`, then verify persistence by checking
`pipeline_log.txt` for a fresh "Watcher started" line after an actual
log-off/log-on or reboot cycle — that's the only real confirmation that
it survived, a running foreground window is not sufficient evidence.

**Standing preference going forward:** background automation like this
should be set up to run continuously (surviving reboot/logoff), not just
manually started in a terminal window — worth applying the same
Task-Scheduler-style setup to any future automation built for this
project.

## HOW TO DIAGNOSE A DROPPED FILE (for reference)

The PowerShell window running `inbox_watcher.py` is the only live
diagnostic surface — there is no separate viewer. Every line also gets
appended to `pipeline_log.txt` in the project root, so that file is the
place to check if the window itself isn't open. Four possible outcomes
for a dropped image:
- `Transcribed <filename> (N words) -> ...` — OCR worked, `.md` created
- `<filename> had little/no OCR text (N words) ... vision analysis not
  yet implemented` — OCR ran fine, correctly filed as a content image
- `OCR unavailable (pytesseract/Pillow not installed) ...` — Python
  packages not importable
- `OCR failed on <filename> ...` — OCR threw an error (e.g. couldn't
  find the Tesseract binary — check `TESSERACT_CMD_OVERRIDE` in
  `image_handling.py` if this comes up)

## NEXT STEPS

1. **Confirm or set up 24/7 persistence via Task Scheduler** — this is
   the top open item, see above.
2. Optional cleanup: delete `bigboys.zip` from `inbox\` if still sitting
   there un-archived, and the two stray duplicate `.py` files it
   produced (`image_handling__20260728192926.py`,
   `inbox_watcher__20260728192926.py`).
3. Longer-term: harden `handle_zip()` against the Windows file-lock race
   if zip drops become routine.
4. Further out: implement `analyze_image_content()` in
   `image_handling.py` for real vision-model analysis (ship/weapon
   identification from photos) — the routing hook is already in place,
   unused until built.
