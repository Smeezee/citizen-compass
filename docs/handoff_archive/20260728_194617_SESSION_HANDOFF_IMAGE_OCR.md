# CITIZEN COMPASS — SESSION HANDOFF: IMAGE/OCR INTEGRATION

**Purpose:** continuation record for the image-screenshot-transcription work
built on top of the existing inbox automation (see the earlier
`CITIZEN_COMPASS_HANDOFF.md` / inbox-automation handoff for that base layer —
this doc only covers the image/OCR addition).

---

## GOAL

Drop a screenshot into `inbox\` and have it automatically:
- OCR'd if it's a screenshot of text (chat log, terminal output, notes,
  error dialog) -> transcribed to a `.md` file -> fed into the *existing*
  handoff/update/doc classification logic unchanged
- Filed separately (not lost) if it's mostly a photo/render/mockup with
  little or no text -> parked in `_needs_review\images\` for a future
  vision-model step (not yet built) that will eventually be able to answer
  things like "identify the weapons on this ship and where they're mounted"

## WHAT WAS BUILT

Two files, both tested end-to-end in a Linux sandbox before being handed
over (not just written blind):

1. **`image_handling.py`** — new module, self-contained. Exposes
   `is_image_file()` and `handle_image_file()`. Routes based on OCR word
   count: `TEXT_WORD_THRESHOLD = 8` words or more -> treated as a text
   screenshot, transcribed and written as a new `.md` back into `inbox\`.
   Fewer -> treated as a content image, filed to `_needs_review\images\`.
   Has a stub function `analyze_image_content()` for the future
   vision-model step — currently always returns `None`, wired into the
   dispatch path so adding real vision analysis later is a one-function
   change.

2. **`inbox_watcher.py`** — existing file, modified. Added an
   `image_handling.is_image_file(path)` branch inside `classify_and_route()`,
   placed after the `.zip` check and before the final "unrecognized
   extension" fallback. No other existing logic touched.

## BUG FOUND AND FIXED THIS SESSION

The first version of the transcription `.md`'s auto-generated header
comment included the text "archived at .../handoff_archive/..." — and
`generate_handoff.is_handoff_doc()` scans the first 500 characters of any
`.md` for the substring `"HANDOFF"` as a heading-hint. That meant every
transcribed screenshot was being misclassified as a full handoff document
(which would fully replace the PROJECT NOTES section of
`LATEST_HANDOFF.md`) instead of being filed as an ordinary doc. Fixed by
rewording the header comment to avoid that word. Verified fixed via a full
re-test: a transcribed screenshot now correctly lands in `docs\` as a plain
doc, not in the handoff archive as a PROJECT NOTES replacement.

## SETUP STATUS ON THE REAL MACHINE

- `pip install pytesseract pillow` — done, confirmed successful
- Tesseract OCR engine itself — installed via the UB-Mannheim Windows
  installer, confirmed working (`tesseract --version` prints
  `v5.5.3.20260724`), installed at
  `C:\Program Files\Tesseract-OCR\tesseract.exe`
- `image_handling.py` and `inbox_watcher.py` (updated versions) — copied
  into `C:\Users\david\citizen-compass`
- `TESSERACT_CMD_OVERRIDE` in `image_handling.py` — **needs
  re-confirmation.** It was set correctly once, but the corrected version
  of `image_handling.py` (sent after the handoff-doc bug fix above) reset
  this value back to `None` by default, and it is NOT CONFIRMED whether it
  was re-set to
  `TESSERACT_CMD_OVERRIDE = r"C:\Program Files\Tesseract-OCR\tesseract.exe"`
  after that replacement. **This is the leading suspect** for why a recent
  real-world test screenshot landed in `_needs_review\` instead of being
  transcribed — if the override is `None` and Tesseract isn't on PATH,
  `pytesseract` can't find the engine and OCR calls fail silently (handled
  gracefully by `image_handling.py`'s own error handling — it logs
  `"OCR unavailable"` or similar rather than crashing — but the net effect
  looks the same as this issue, so the log line is the only way to tell
  them apart, see "how to tell what happened" below).

## AN UNRESOLVED SIDE ISSUE (not blocking, but noted)

While testing, a `bigboys.zip` was dropped into `inbox\` (containing
outdated backup copies of `image_handling.py` and `inbox_watcher.py`,
apparently unintentionally). The existing `.zip` handling in
`inbox_watcher.py` extracted its contents correctly (saved safely as
`image_handling__<timestamp>.py` etc. due to the existing name-collision
protection — nothing was overwritten), but then failed to archive the
original zip file itself with:

```
[WinError 32] The process cannot access the file because it is being
used by another process: '...\inbox\bigboys.zip'
```

This is a Windows-specific race condition: `handle_zip()` extracts into a
temp folder created *inside* `inbox\` via `tempfile.mkdtemp(...)`, then
immediately tries to clean up and move the original zip — on Windows,
antivirus or Explorer can still hold a brief lock on files right after
extraction, which this sandbox (Linux) didn't surface. Not yet fixed. The
two stray duplicate `.py` files this produced
(`image_handling__20260728192926.py`, `inbox_watcher__20260728192926.py`)
are safe to delete — they're just extra copies, not needed.

## HOW TO TELL WHAT ACTUALLY HAPPENED TO A DROPPED SCREENSHOT

The PowerShell window running `inbox_watcher.py` is the source of truth —
there is no separate window or UI; log lines print there live AND get
written to `pipeline_log.txt` in the project root. Look for one of these
four outcomes after dropping an image:

- `Transcribed <filename> (N words) -> ...` — OCR worked, `.md` created
  and dropped back into `inbox\` for normal processing
- `<filename> had little/no OCR text (N words) ... filed to ...
  (vision analysis not yet implemented)` — OCR ran fine, just found too
  little text; correctly filed to `_needs_review\images\`, not a bug
- `OCR unavailable (pytesseract/Pillow not installed) — filed ...` —
  the Python packages themselves aren't importable
- `OCR failed on <filename> ... filed to ... for manual review` — OCR ran
  but threw an error (e.g. can't find the Tesseract engine binary — this
  is the one to watch for given the override-reset issue above)

If the PowerShell window was closed, restart it with:
```powershell
cd C:\Users\david\citizen-compass
python inbox_watcher.py
```
and re-check `pipeline_log.txt` for the relevant lines even if the window
itself was closed when the file was originally dropped — every line that
prints also gets appended there.

## NEXT STEPS

1. Confirm (open `image_handling.py` in Notepad) whether
   `TESSERACT_CMD_OVERRIDE` is currently set to the real path or reset to
   `None`. Re-set it if needed:
   ```python
   TESSERACT_CMD_OVERRIDE = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
   ```
2. Restart `inbox_watcher.py`, drop a real text screenshot into `inbox\`,
   and read the PowerShell log directly (see above) rather than only
   checking where the file landed — the log line tells you *which* of the
   four outcomes happened, the folder alone doesn't.
3. Once transcription is confirmed working, optionally clean up the two
   stray duplicate `.py` files from the `bigboys.zip` incident and delete
   `bigboys.zip` from `inbox\` if it's still sitting there un-archived.
4. Longer-term / not urgent: the `handle_zip()` Windows file-lock issue
   could be made more robust (e.g. retry-with-backoff on the
   `shutil.move`/`shutil.rmtree` calls) if zip drops become a regular
   workflow — not fixed yet, only documented here.
5. Further out: implement `analyze_image_content()` in
   `image_handling.py` for real vision-model analysis (e.g. via Ollama +
   a vision model like `llava`/`qwen2-vl`) to support "identify the
   weapons on this ship and where they're placed" — the routing hook is
   already in place, unused until this is built.
