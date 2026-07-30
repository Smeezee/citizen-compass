"""
Citizen Compass — Image handling for inbox_watcher.py

Drop-in module: import into inbox_watcher.py and call handle_image_file()
from the main dispatch logic whenever a .png/.jpg/.jpeg/.bmp/.webp shows up
in inbox/.

WHAT IT DOES NOW:
  Screenshot of text (chat log, terminal output, error message, notes) ->
  OCR'd TWICE with different preprocessing (raw vs. contrast-enhanced) and
  cross-checked against each other, since running the identical config
  twice would just repeat the same possible error rather than actually
  verifying anything -> if the two passes agree, saved as a .md and handed
  back into the SAME inbox/ folder so it flows through the existing .md
  classification logic in inbox_watcher.py unchanged (handoff doc / update
  doc / plain doc). If the two passes DISAGREE, nothing is auto-filed --
  both transcriptions and the original image are filed to
  _needs_review/ocr_discrepancies/ for a human to sort out. The original
  image is archived, never deleted, in either case.

  Confirmed-transcribed images (the "agreed" case) are also subject to a
  retention policy: cleanup_aged_confirmed_screenshots() recycles (Recycle
  Bin, never a permanent delete) any confirmed screenshot older than
  SCREENSHOT_RETENTION_DAYS past its confirmed-transcribed date. This is
  wired into inbox_watcher.py's main loop as a periodic check. It only ever
  touches files in the confirmed-images archive folder -- nothing that
  hasn't cleared the cross-check lands there in the first place, so nothing
  unconfirmed is ever a candidate for cleanup.

WHAT IT STUBS FOR LATER:
  Screenshot/photo with little or no readable text (a ship render, a UI
  mockup, anything that's "a picture of a thing" rather than "a picture of
  words") -> routed to _needs_review/images/ instead of the generic
  _needs_review/, and see analyze_image_content() below for where a local
  vision model (e.g. Ollama + llava/qwen2-vl) gets wired in later.

ROUTING RULE:
  Neither OCR pass clears TEXT_WORD_THRESHOLD words -> content image,
                                                        stubbed for future
                                                        vision analysis
  At least one pass clears it, and the two passes AGREE               ->
      treated as a confirmed text screenshot
  At least one pass clears it, but the two passes DISAGREE            ->
      flagged to _needs_review/ocr_discrepancies/, nothing auto-filed

Requires: pytesseract (pip install pytesseract), Pillow (pip install pillow),
Send2Trash (pip install Send2Trash), and the Tesseract OCR engine itself
installed and on PATH.
  Windows: https://github.com/UB-Mannheim/tesseract/wiki  (installer .exe)
  after installing, either add its folder to PATH, or set
  pytesseract.pytesseract.tesseract_cmd to the full exe path (see
  TESSERACT_CMD_OVERRIDE below) if it's not auto-detected.
"""

import difflib
import re
from pathlib import Path
from datetime import datetime, timedelta

try:
    import pytesseract
    from PIL import Image, ImageOps, ImageEnhance
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

try:
    import send2trash
    RECYCLE_AVAILABLE = True
except ImportError:
    RECYCLE_AVAILABLE = False

# If Tesseract isn't on PATH on the Windows box, uncomment and set this:
# import pytesseract
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSERACT_CMD_OVERRIDE = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff")

# Below this many OCR'd words, treat the image as "content" (a photo of a
# ship, a render, a diagram with no real body text) rather than "a
# screenshot of text". Tuned loosely -- a genuine text screenshot (chat log,
# terminal, error dialog, notes app) will clear this easily; a mostly-visual
# image with maybe a UI label or two won't. Checked against the BETTER of
# the two OCR passes, so a bad preprocessing pass on a genuine text
# screenshot doesn't wrongly demote it to "content".
TEXT_WORD_THRESHOLD = 8

# Two OCR passes are considered to agree if their normalized text similarity
# (difflib ratio, whitespace-collapsed) is at least this. Below it, we don't
# guess which pass is right -- it gets flagged for a human instead.
AGREEMENT_SIMILARITY_THRESHOLD = 0.92

OCR_DISCREPANCY_DIR_NAME = "ocr_discrepancies"

# How long a CONFIRMED (cross-check agreed) screenshot image sits in the
# archive before it's eligible to be recycled. Only ever applies to images
# that reached the confirmed-archive folder -- see cleanup_aged_confirmed_screenshots().
SCREENSHOT_RETENTION_DAYS = 14

_TIMESTAMP_PREFIX_RE = re.compile(r"^(\d{8}_\d{6})_")


def _ensure_tesseract_configured():
    if TESSERACT_CMD_OVERRIDE and OCR_AVAILABLE:
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD_OVERRIDE


def is_image_file(path: Path) -> bool:
    return path.suffix.lower() in IMAGE_EXTENSIONS


def _ocr_pil_image(image):
    """Runs Tesseract on an already-loaded PIL image. Returns extracted
    text (str, possibly empty), or None on failure. Internal helper shared
    by the single-pass and cross-checked entry points."""
    if not OCR_AVAILABLE:
        return None
    _ensure_tesseract_configured()
    try:
        return pytesseract.image_to_string(image).strip()
    except Exception:
        return None


def _preprocess_enhanced(image):
    """A deliberately different preprocessing pass from 'raw' -- grayscale,
    autocontrast, and a sharpen pass. Standard OCR-accuracy preprocessing,
    and different enough from the raw pass that the two runs can actually
    catch each other's mistakes instead of just repeating the same read."""
    gray = image.convert("L")
    contrasted = ImageOps.autocontrast(gray)
    return ImageEnhance.Sharpness(contrasted).enhance(2.0)


def ocr_image(path: Path):
    """Single-pass OCR on the raw image, no cross-check. Kept for manual/
    standalone use (e.g. ad-hoc testing from a Python shell) -- the actual
    inbox pipeline uses ocr_image_cross_checked() instead. Returns the
    extracted text (str, possibly empty), or None if OCR itself failed
    (missing dependency, corrupt file, etc.) -- callers must treat None as
    'could not process', not as 'no text found'."""
    if not OCR_AVAILABLE:
        return None
    try:
        return _ocr_pil_image(Image.open(path))
    except Exception:
        return None


def ocr_image_cross_checked(path: Path):
    """Runs OCR twice on the same image -- once on the raw image, once on a
    contrast-enhanced version -- and cross-checks the two results, since
    running the identical config twice would just repeat the same possible
    error rather than actually verifying anything.

    Returns a dict:
        {
            "agreed": bool,
            "text": str or None,       # the transcription to use, only set when agreed
            "raw_text": str or None,
            "enhanced_text": str or None,
            "similarity": float,       # 0.0-1.0 normalized text similarity
        }

    "text" is intentionally None when the two passes disagree -- the caller
    must not guess which version is correct.
    """
    empty_result = {"agreed": False, "text": None, "raw_text": None, "enhanced_text": None, "similarity": 0.0}
    if not OCR_AVAILABLE:
        return empty_result

    _ensure_tesseract_configured()
    try:
        image = Image.open(path)
        raw_text = _ocr_pil_image(image)
        enhanced_text = _ocr_pil_image(_preprocess_enhanced(image))
    except Exception:
        return empty_result

    if raw_text is None or enhanced_text is None:
        return {**empty_result, "raw_text": raw_text, "enhanced_text": enhanced_text}

    norm_raw = " ".join(raw_text.split()).lower()
    norm_enhanced = " ".join(enhanced_text.split()).lower()
    similarity = (
        difflib.SequenceMatcher(None, norm_raw, norm_enhanced).ratio()
        if (norm_raw or norm_enhanced) else 1.0
    )
    agreed = similarity >= AGREEMENT_SIMILARITY_THRESHOLD

    return {
        "agreed": agreed,
        "text": enhanced_text if agreed else None,
        "raw_text": raw_text,
        "enhanced_text": enhanced_text,
        "similarity": round(similarity, 4),
    }


def analyze_image_content(path: Path):
    """STUB for future vision-model analysis (e.g. 'identify the weapons on
    this ship and where they're mounted'). Not implemented yet -- wire in a
    call to a local vision model here (Ollama + llava/qwen2-vl, or similar)
    when that's ready. Must return None on any failure, same contract as
    ocr_image, so callers always have a safe fallback (just file the image)."""
    return None


def handle_image_file(path: Path, inbox_dir: Path, image_archive_dir: Path,
                       needs_review_dir: Path, log):
    """Main entry point. Call this from inbox_watcher.py's dispatch logic
    for any file where is_image_file(path) is True.

    Returns a dict describing what happened, so inbox_watcher.py's existing
    post-processing (e.g. triggering generate_handoff.py) can decide whether
    a new .md now needs to flow through the doc pipeline:

        {"action": "transcribed", "md_path": Path(...), "confirmed_image_path": Path(...)}
        {"action": "discrepancy", "image_path": Path(...), "report_path": Path(...), "similarity": float}
        {"action": "content_stub", "archived_path": Path(...)}
        {"action": "failed", "reason": "..."}

    Never deletes the original image -- always archives it first. Only the
    "transcribed" (cross-check agreed) case lands in image_archive_dir --
    that folder is treated elsewhere (see cleanup_aged_confirmed_screenshots)
    as containing ONLY confirmed screenshots, so nothing unconfirmed is ever
    a retention-cleanup candidate.
    """
    image_archive_dir.mkdir(parents=True, exist_ok=True)
    needs_review_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archived_path = image_archive_dir / f"{timestamp}_{path.name}"
    try:
        path.replace(archived_path)
    except Exception as e:
        log(f"Could not archive image {path.name}: {e}")
        return {"action": "failed", "reason": str(e)}

    if not OCR_AVAILABLE:
        log(f"OCR unavailable (pytesseract/Pillow not installed) — "
            f"filed {path.name} to {needs_review_dir} without transcription")
        fallback_path = needs_review_dir / archived_path.name
        archived_path.replace(fallback_path)
        return {"action": "failed", "reason": "ocr_unavailable"}

    result = ocr_image_cross_checked(archived_path)

    if result["raw_text"] is None and result["enhanced_text"] is None:
        log(f"OCR failed on {path.name} (both passes) — filing to {needs_review_dir} for manual review")
        fallback_path = needs_review_dir / archived_path.name
        archived_path.replace(fallback_path)
        return {"action": "failed", "reason": "ocr_error"}

    raw_word_count = len((result["raw_text"] or "").split())
    enhanced_word_count = len((result["enhanced_text"] or "").split())
    best_word_count = max(raw_word_count, enhanced_word_count)

    if best_word_count < TEXT_WORD_THRESHOLD:
        # Neither pass found meaningful text -> likely a content photo
        # (ship render, mockup, etc). Stub for future vision analysis
        # rather than a full pipeline today.
        vision_result = analyze_image_content(archived_path)
        if vision_result:
            # Not reachable yet since analyze_image_content() always
            # returns None for now -- left in place so wiring in a real
            # vision model later requires no changes to this dispatch logic.
            log(f"Vision analysis produced a description for {path.name}")
            return {"action": "content_analyzed", "archived_path": archived_path,
                    "description": vision_result}

        content_review_dir = needs_review_dir / "images"
        content_review_dir.mkdir(parents=True, exist_ok=True)
        final_path = content_review_dir / archived_path.name
        archived_path.replace(final_path)
        log(f"{path.name} had little/no OCR text ({best_word_count} words, best of 2 passes) — "
            f"treated as a content image, filed to {content_review_dir} "
            f"(vision analysis not yet implemented)")
        return {"action": "content_stub", "archived_path": final_path}

    if not result["agreed"]:
        # Text screenshot, but the raw and enhanced OCR passes disagree --
        # don't guess which is right. File both versions for a human.
        discrepancy_dir = needs_review_dir / OCR_DISCREPANCY_DIR_NAME
        discrepancy_dir.mkdir(parents=True, exist_ok=True)
        final_image_path = discrepancy_dir / archived_path.name
        archived_path.replace(final_image_path)

        report_path = discrepancy_dir / f"{timestamp}_{path.stem}_DISCREPANCY.md"
        report_path.write_text(
            f"<!-- OCR cross-check disagreement for {path.name}, "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. "
            f"Similarity score: {result['similarity']} "
            f"(agreement threshold: {AGREEMENT_SIMILARITY_THRESHOLD}). "
            f"Original image kept at: {final_image_path.name} in this same folder. -->\n\n"
            f"# OCR cross-check disagreement — needs manual review\n\n"
            f"## Raw-pass transcription\n\n{result['raw_text'] or '(no text)'}\n\n"
            f"## Enhanced-pass transcription\n\n{result['enhanced_text'] or '(no text)'}\n\n"
            f"Neither version was auto-filed. Compare against the original image "
            f"({final_image_path.name}) and manually drop a corrected .md into "
            f"inbox/ if you want this processed further.\n",
            encoding="utf-8",
        )
        log(f"OCR cross-check disagreement on {path.name} "
            f"(similarity {result['similarity']:.2f} < {AGREEMENT_SIMILARITY_THRESHOLD}) — "
            f"both versions filed to {discrepancy_dir} for manual review, nothing auto-filed")
        return {
            "action": "discrepancy",
            "image_path": final_image_path,
            "report_path": report_path,
            "similarity": result["similarity"],
        }

    # Agreed -- treat as a confirmed text screenshot, exactly as the single-
    # pass version used to, but using the cross-checked text and noting the
    # agreement in the dropped .md.
    md_name = f"screenshot_{timestamp}_ocr.md"
    md_path = inbox_dir / md_name
    # NOTE: keep this comment free of the words "handoff" or "session
    # archive" (even inside a path) -- generate_handoff.is_handoff_doc()
    # scans the first 500 chars for those as heading hints, and a stray
    # match here would misclassify every OCR'd screenshot as a full
    # handoff document instead of a plain doc.
    md_content = (
        f"<!-- OCR transcription of {archived_path.name}, "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. "
        f"Cross-checked: raw vs. contrast-enhanced passes agreed "
        f"(similarity {result['similarity']:.2f}). "
        f"Original image kept at: {archived_path.name} (see image archive folder). -->\n\n"
        f"{result['text']}\n"
    )
    md_path.write_text(md_content, encoding="utf-8")
    log(f"Transcribed {path.name} ({best_word_count} words, cross-check similarity "
        f"{result['similarity']:.2f}) -> {md_name}, dropped back into inbox/ for normal doc processing")
    return {"action": "transcribed", "md_path": md_path, "confirmed_image_path": archived_path}


# ---- RETENTION / CLEANUP -------------------------------------------------

def _confirmed_at_from_filename(filename: str):
    """Parses the leading YYYYMMDD_HHMMSS timestamp this pipeline always
    prefixes confirmed-image filenames with. Returns None if it doesn't
    match (e.g. a file placed there some other way), in which case the
    caller should fall back to filesystem mtime."""
    m = _TIMESTAMP_PREFIX_RE.match(filename)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), "%Y%m%d_%H%M%S")
    except ValueError:
        return None


def cleanup_aged_confirmed_screenshots(image_archive_dir: Path, retention_days=SCREENSHOT_RETENTION_DAYS, log=print):
    """Recycles (Recycle Bin -- never a permanent delete) confirmed
    screenshot images once they've sat for more than retention_days past
    their confirmed-transcribed date.

    Only ever touches files directly in image_archive_dir. Under this
    pipeline's routing (see handle_image_file above), that folder holds
    ONLY images whose OCR cross-check agreed and were filed with
    confidence -- disagreements go to _needs_review/ocr_discrepancies/
    instead, and non-text "content" images go to _needs_review/images/.
    Nothing unconfirmed, and nothing that isn't a raw OCR screenshot image,
    is ever a candidate here: no 3D models, no data files, no other
    document types.

    The transcribed TEXT is never touched -- only the original image, once
    it's done its job and aged out. Returns the list of filenames recycled.
    """
    if not RECYCLE_AVAILABLE:
        log("⚠ Send2Trash not installed — skipping screenshot retention pass "
            "(refusing to permanently delete as a substitute)")
        return []
    if not image_archive_dir.exists():
        return []

    cutoff = datetime.now() - timedelta(days=retention_days)
    recycled = []
    for f in sorted(image_archive_dir.iterdir()):
        if not f.is_file():
            continue
        confirmed_at = _confirmed_at_from_filename(f.name) or datetime.fromtimestamp(f.stat().st_mtime)
        if confirmed_at >= cutoff:
            continue
        try:
            send2trash.send2trash(str(f))
            age_days = (datetime.now() - confirmed_at).days
            log(f"Recycled aged confirmed screenshot: {f.name} "
                f"(confirmed {confirmed_at.strftime('%Y-%m-%d')}, {age_days} days ago)")
            recycled.append(f.name)
        except Exception as e:
            log(f"Could not recycle {f.name}: {e}")
    return recycled


if __name__ == "__main__":
    import sys

    dry_run = "--dry-run" in sys.argv
    archive_dir = Path(__file__).resolve().parent / "docs" / "handoff_archive" / "images"

    if dry_run:
        print(f"[dry run] Checking {archive_dir} for confirmed screenshots older than "
              f"{SCREENSHOT_RETENTION_DAYS} days (nothing will be recycled)...")
        if not RECYCLE_AVAILABLE:
            print("Send2Trash not installed -- the real run would skip cleanup entirely.")
        if archive_dir.exists():
            cutoff = datetime.now() - timedelta(days=SCREENSHOT_RETENTION_DAYS)
            for f in sorted(archive_dir.iterdir()):
                if not f.is_file():
                    continue
                confirmed_at = _confirmed_at_from_filename(f.name) or datetime.fromtimestamp(f.stat().st_mtime)
                flag = "WOULD RECYCLE" if confirmed_at < cutoff else "keep"
                print(f"  [{flag}] {f.name} (confirmed {confirmed_at.strftime('%Y-%m-%d')})")
    else:
        recycled = cleanup_aged_confirmed_screenshots(archive_dir)
        print(f"Done. Recycled {len(recycled)} aged confirmed screenshot(s).")
