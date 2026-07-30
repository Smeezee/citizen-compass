# Wiring image_handling.py into inbox_watcher.py

`image_handling.py` is a standalone, tested module. It doesn't touch
`inbox_watcher.py` itself — you add a few lines to your existing
dispatch logic to call into it.

## 1. Install dependencies (Windows box)

```
pip install pytesseract pillow
```

Then install the actual Tesseract OCR engine (this is separate from the
Python package — `pytesseract` just talks to it):

- Download the Windows installer: https://github.com/UB-Mannheim/tesseract/wiki
- Run it, default install location is `C:\Program Files\Tesseract-OCR\`
- If `pytesseract` can't find it automatically, open `image_handling.py`
  and set:
  ```python
  TESSERACT_CMD_OVERRIDE = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
  ```

## 2. Drop `image_handling.py` into the project folder

Same folder as `inbox_watcher.py` and `generate_handoff.py`
(`C:\Users\david\citizen-compass`).

## 3. Add to `inbox_watcher.py`

Near your other imports:

```python
from image_handling import is_image_file, handle_image_file
```

Wherever your dispatch logic currently checks file type (the same place
that checks for `.glb`/`.blend`/`.py`/`.md` etc.), add an image branch
**before** the "unrecognized -> `_needs_review/`" fallback:

```python
if is_image_file(file_path):
    result = handle_image_file(
        path=file_path,
        inbox_dir=INBOX_DIR,                              # your existing inbox path
        image_archive_dir=PROJECT_ROOT / "docs" / "handoff_archive" / "images",
        needs_review_dir=NEEDS_REVIEW_DIR,                 # your existing _needs_review path
        log=log,                                           # your existing log function
    )
    if result["action"] == "transcribed":
        # a new .md just landed back in inbox/ — let your existing
        # watcher loop pick it up on its next pass (or, if your watcher
        # doesn't naturally re-scan, call your existing .md handling
        # logic directly on result["md_path"] here)
        pass
    continue  # image is handled either way, don't fall through to other rules
```

That's it. Everything else — OCR, routing, archiving, filing to
`_needs_review/images/` — is self-contained in the module.

## What happens now

- Screenshot with real text (chat log, terminal output, error dialog,
  typed notes) → OCR'd → saved as `screenshot_<timestamp>_ocr.md` back
  into `inbox/` → flows through your **existing** `.md` classification
  unchanged (becomes a handoff doc / update doc / plain doc depending on
  its content, exactly like a hand-typed `.md` would)
- Original image is never deleted — archived to
  `docs/handoff_archive/images/`
- Screenshot/photo with little or no readable text (ship render, mockup,
  anything that's mostly visual) → filed to `_needs_review/images/`,
  separate from your generic `_needs_review/`, so it's easy to find later
- If OCR itself isn't installed or fails, the image is filed to
  `_needs_review/` (or `_needs_review/images/`) rather than lost or
  crashing the watcher

## What's stubbed for later

`analyze_image_content()` in `image_handling.py` is a clearly marked stub
that currently always returns `None`. When you're ready to add "identify
the weapons on this ship and where they're mounted," that's the one
function to implement — swap in a call to a local vision model (Ollama
supports vision models like `llava` or `qwen2-vl` the same way it serves
`qwen3:14b` today). Nothing else in the dispatch logic needs to change —
the routing fork already sends low-text images to that function first,
before the `_needs_review/images/` fallback.

## Tuning note

`TEXT_WORD_THRESHOLD = 8` in `image_handling.py` controls the text vs.
content routing. Tested against a text-heavy mock screenshot (18 OCR'd
words → correctly routed as transcribable) and a text-free mock image
(0 words → correctly routed as content). If you find real screenshots
with sparse-but-real text (e.g. a short error popup) getting misrouted
to `_needs_review/images/`, lower this number.
