"""
Citizen Compass — Inbox Watcher

Runs continuously in the background. Watches an `inbox/` folder inside the
project root. Anything dropped there — hardpoint JSON, ship spec JSON,
.glb/.blend models, .md docs, .py scripts, handoff-style documents, or
anything else — gets classified, moved to the right place in the project,
and logged. After each file, the CCPP health score is refreshed and
LATEST_HANDOFF.md is regenerated (requires ccpp.py and generate_handoff.py
in the same folder as this script).

Handoff-style docs (filename or heading mentions "handoff" or "session
archive") are archived untouched in docs/handoff_archive/ and become the
current "PROJECT NOTES" section of LATEST_HANDOFF.md — see
generate_handoff.py for how that's built.

.zip files are extracted automatically, and every file that comes out of
them is run back through this same classification logic (including nested
zips). The original .zip is then archived, untouched, in _zip_archive/ —
nothing about it is deleted, only unpacked.

Nothing is ever silently discarded: anything this script can't confidently
classify goes to _needs_review/ instead of being guessed at.

Setup:
    pip install watchdog
    python inbox_watcher.py

See SETUP_INSTRUCTIONS.md for running this automatically at login so you
never have to start it by hand.
"""

import json
import re
import shutil
import tempfile
import time
import sys
import zipfile
from pathlib import Path
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import generate_handoff
import image_handling

# ---- CONFIG -----------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent
INBOX_DIR = PROJECT_ROOT / "inbox"
NEEDS_REVIEW_DIR = PROJECT_ROOT / "_needs_review"
ZIP_ARCHIVE_DIR = PROJECT_ROOT / "_zip_archive"
LOG_FILE = PROJECT_ROOT / "pipeline_log.txt"
CCPP_FILE = PROJECT_ROOT / "citizen-compass.ccpp"

SHIPS_DIR = PROJECT_ROOT / "tests" / "testing-site" / "ships"
DOCS_DIR = PROJECT_ROOT / "docs"
MODELS_UNSORTED_DIR = PROJECT_ROOT / "models" / "_unsorted"

STABLE_CHECK_SECONDS = 1.0    # gap between size checks while a file is copying
STABLE_CHECKS_REQUIRED = 2    # size must be unchanged this many checks in a row

RETENTION_CHECK_INTERVAL_SECONDS = 24 * 60 * 60  # how often to sweep for aged confirmed screenshots


def _pick_raw_hardpoints_dir():
    """Use whichever raw-hardpoint folder convention already exists on disk."""
    flat = PROJECT_ROOT / "data-layerrawhardpoints"
    if flat.exists():
        return flat
    return PROJECT_ROOT / "data-layer" / "raw" / "hardpoints"


def _pick_raw_ships_dir():
    flat = PROJECT_ROOT / "data-layerrawships"
    if flat.exists():
        return flat
    return PROJECT_ROOT / "data-layer" / "raw" / "ships"


def _pick_raw_misc_dir():
    return PROJECT_ROOT / "data-layer" / "raw" / "misc"


def _pick_processed_hardpoints_dir():
    flat = PROJECT_ROOT / "data-layerprocessedhardpoints_by_type"
    if flat.exists():
        return flat
    return PROJECT_ROOT / "data-layer" / "processed" / "hardpoints_by_type"


# ---- LOGGING ------------------------------------------------------------

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ---- CLASSIFICATION -------------------------------------------------------

def known_ship_slugs():
    if not SHIPS_DIR.exists():
        return []
    return [p.name for p in SHIPS_DIR.iterdir() if p.is_dir()]


def guess_ship_slug(filename_stem, known_slugs):
    stem = filename_stem.lower().replace("_", "-")
    for slug in known_slugs:
        if slug in stem:
            return slug
    return None


def classify_and_route(path: Path):
    """Decide what a dropped file is and where it belongs.
    Returns (note, destination_path)."""
    ext = path.suffix.lower()

    if ext == ".py":
        return route_simple(path, PROJECT_ROOT, note="script")

    if ext == ".md":
        text = path.read_text(encoding="utf-8", errors="replace")
        if generate_handoff.is_handoff_doc(path, text):
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            note, dest = route_to(
                path,
                generate_handoff.HANDOFF_ARCHIVE_DIR / f"{stamp}_{path.name}",
                "handoff doc — archived",
            )
            generate_handoff.LATEST_RAW_PATH.write_text(text, encoding="utf-8")
            note += "; will fully replace PROJECT NOTES in LATEST_HANDOFF.md"
            return note, dest
        if generate_handoff.is_update_doc(path, text):
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            note, dest = route_to(
                path,
                generate_handoff.HANDOFF_ARCHIVE_DIR / f"{stamp}_{path.name}",
                "update doc — archived",
            )
            generate_handoff.append_update(text, path.name)
            note += "; appended to running updates log (nothing overwritten)"
            return note, dest
        return route_simple(path, DOCS_DIR, note="doc")

    if ext in (".glb", ".blend"):
        slug = guess_ship_slug(path.stem, known_ship_slugs())
        if slug:
            dest_dir = SHIPS_DIR / slug
            dest_name = "model.glb" if ext == ".glb" else path.name
            return route_to(path, dest_dir / dest_name, f"3D model matched to ship '{slug}'")
        return route_simple(path, MODELS_UNSORTED_DIR, note="3D model, no ship slug match")

    if ext == ".json":
        return classify_json(path)

    if ext == ".zip":
        return handle_zip(path)

    if image_handling.is_image_file(path):
        result = image_handling.handle_image_file(
            path=path,
            inbox_dir=INBOX_DIR,
            image_archive_dir=generate_handoff.HANDOFF_ARCHIVE_DIR / "images",
            needs_review_dir=NEEDS_REVIEW_DIR,
            log=log,
        )
        if result["action"] == "transcribed":
            # A new .md just landed back in inbox/ — the watchdog on_created
            # event for it will fire and get processed on its own, same as
            # any other dropped file, so nothing further to do here.
            return (
                f"image screenshot — OCR cross-check agreed (similarity "
                f"{result.get('similarity', 0):.2f}), .md dropped back into inbox/ for normal processing"
            ), result["md_path"]
        if result["action"] == "discrepancy":
            return (
                f"image screenshot — OCR cross-check DISAGREED (similarity "
                f"{result.get('similarity', 0):.2f}) — both transcriptions filed to "
                f"_needs_review/{image_handling.OCR_DISCREPANCY_DIR_NAME}/ for manual review, nothing auto-filed"
            ), result["image_path"]
        if result["action"] == "content_stub":
            return "image with little/no OCR text — filed for future vision analysis (not yet implemented)", result["archived_path"]
        return f"image processing failed ({result.get('reason', 'unknown')}) — filed to _needs_review/", NEEDS_REVIEW_DIR / path.name

    # Unknown type — never silently discard
    return route_simple(path, NEEDS_REVIEW_DIR, note=f"unrecognized extension '{ext}'")


def handle_zip(path: Path):
    """Extract a dropped zip, run every file that comes out of it back
    through classify_and_route (nested zips included), then archive the
    original zip untouched. Nothing inside is ever silently discarded —
    files that can't be classified still land in _needs_review/ same as
    always, just one level down from where they'd land if dropped loose."""

    extract_dir = Path(tempfile.mkdtemp(prefix=f"{path.stem}_", dir=str(INBOX_DIR)))
    try:
        with zipfile.ZipFile(path, "r") as zf:
            zf.extractall(extract_dir)
    except zipfile.BadZipFile as e:
        shutil.rmtree(extract_dir, ignore_errors=True)
        return route_simple(path, NEEDS_REVIEW_DIR, note=f"invalid zip ({e})")

    extracted_files = [p for p in extract_dir.rglob("*") if p.is_file()]

    if not extracted_files:
        shutil.rmtree(extract_dir, ignore_errors=True)
        return route_simple(path, NEEDS_REVIEW_DIR, note="zip was empty")

    sorted_count = 0
    failed_count = 0
    for f in extracted_files:
        try:
            note, dest = classify_and_route(f)
            log(f"    \u2713 (from {path.name}) {f.name} -> {dest} ({note})")
            sorted_count += 1
        except Exception as e:
            log(f"    \u2717 (from {path.name}) FAILED processing {f.name}: {e}")
            failed_count += 1

    shutil.rmtree(extract_dir, ignore_errors=True)

    summary = f"zip extracted — {sorted_count} file(s) sorted"
    if failed_count:
        summary += f", {failed_count} failed"
    summary += "; original archived here"

    return route_simple(path, ZIP_ARCHIVE_DIR, note=summary)


def classify_json(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return route_simple(path, NEEDS_REVIEW_DIR, note=f"invalid JSON ({e})")

    stem_lower = path.stem.lower()

    if isinstance(data, dict) and _looks_like_viewer_hardpoints(data):
        slug = data.get("ship_slug") or guess_ship_slug(stem_lower, known_ship_slugs())
        if slug:
            dest_dir = SHIPS_DIR / slug
            return route_to(path, dest_dir / "hardpoints.json", f"viewer hardpoint placements for '{slug}'")
        return route_simple(path, NEEDS_REVIEW_DIR, note="viewer hardpoint placements, no ship slug match")

    if isinstance(data, dict) and (
        "weapons_by_category" in data or "hardpoint" in stem_lower or "weapon" in stem_lower
    ):
        note, dest = route_simple(path, _pick_raw_hardpoints_dir(), note="raw hardpoint/weapon data")
        organize_result = auto_organize_hardpoint_file(dest, data)
        if organize_result:
            note += f"; auto-categorized -> {organize_result}"
        return note, dest

    if isinstance(data, dict) and "ship_slug" in data and "ship_name" in data:
        return route_simple(path, _pick_raw_ships_dir(), note="ship spec data")

    return route_simple(path, _pick_raw_misc_dir(), note="unclassified JSON, filed as misc — check if a new category is needed")


def _categorize_weapon_entry(entry_type: str) -> str:
    t = (entry_type or "").lower()
    if "turret" in t:
        return "turrets"
    if "missile" in t or "launcher" in t:
        return "missiles"
    if "gun" in t or "ballistic" in t or "energy" in t:
        return "weapons"
    return "components"


def auto_organize_hardpoint_file(raw_path: Path, data: dict):
    """Categorize a raw weapon/hardpoint file into turrets/missiles/weapons/
    components, matching the same logic as hardpoint_organizer.py, and write
    it to the processed folder. Returns the output path, or None if the file
    didn't have a recognizable weapons_by_category / hardpoints shape."""

    organized = {
        "ship_name": data.get("ship_name", raw_path.stem),
        "ship_slug": data.get("ship_slug", raw_path.stem),
        "categories": {"weapons": [], "turrets": [], "missiles": [], "components": []},
    }

    found_any = False

    # Shape A: {"weapons_by_category": {"Turrets": [...], "Missile & Bomb Racks": [...], ...}}
    wbc = data.get("weapons_by_category")
    if isinstance(wbc, dict):
        for group_name, items in wbc.items():
            if not isinstance(items, list):
                continue
            for item in items:
                found_any = True
                category = _categorize_weapon_entry(item.get("type", group_name))
                organized["categories"][category].append(item)

    # Shape B: {"hardpoints": [{"type": "...", ...}, ...]}
    hp_list = data.get("hardpoints")
    if isinstance(hp_list, list):
        for hp in hp_list:
            if isinstance(hp, dict):
                found_any = True
                category = _categorize_weapon_entry(hp.get("type", ""))
                organized["categories"][category].append(hp)

    if not found_any:
        return None

    organized["total_hardpoints"] = sum(len(v) for v in organized["categories"].values())

    out_dir = _pick_processed_hardpoints_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{organized['ship_slug']}_organized.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(organized, f, indent=2)

    return out_path


def _looks_like_viewer_hardpoints(data):
    hp_list = data.get("hardpoints")
    if not isinstance(hp_list, list) or not hp_list:
        return False
    first = hp_list[0]
    return isinstance(first, dict) and ("position" in first or "x" in first)


def route_simple(path: Path, dest_dir: Path, note=""):
    dest_dir.mkdir(parents=True, exist_ok=True)
    return route_to(path, dest_dir / path.name, note)


def route_to(path: Path, dest: Path, note=""):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        # never silently overwrite existing data
        stamp = datetime.now().strftime("%Y%m%d%H%M%S")
        dest = dest.with_name(f"{dest.stem}__{stamp}{dest.suffix}")
        note += " (name collision, kept both — old file untouched)"
    shutil.move(str(path), str(dest))
    return (note, dest)


# ---- STABILITY CHECK (wait for a file to finish copying) -------------------

def wait_until_stable(path: Path):
    last_size = -1
    stable_count = 0
    while stable_count < STABLE_CHECKS_REQUIRED:
        if not path.exists():
            return False
        try:
            size = path.stat().st_size
        except FileNotFoundError:
            return False
        if size == last_size:
            stable_count += 1
        else:
            stable_count = 0
            last_size = size
        time.sleep(STABLE_CHECK_SECONDS)
    return True


# ---- RESCAN / HEALTH SCORE ---------------------------------------------------

def rescan_and_score():
    sys.path.insert(0, str(PROJECT_ROOT))
    try:
        from ccpp import CitizenCompassPacket
    except ImportError:
        log("⚠ ccpp.py not found in project root — skipping health-score refresh")
        return

    packet = CitizenCompassPacket()
    packet.scan_project(PROJECT_ROOT)
    packet.save(str(CCPP_FILE))
    log(
        f"Health score refreshed: {packet.scores.get('overall_health', '?')}/100 "
        f"(data {packet.scores.get('data_completeness', '?')}%, "
        f"viewers {packet.scores.get('viewer_progress', '?')}%, "
        f"docs {packet.scores.get('documentation', '?')}%)"
    )


# ---- WATCHER ------------------------------------------------------------

class InboxHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            self.process(Path(event.src_path))

    def on_moved(self, event):
        if not event.is_directory:
            self.process(Path(event.dest_path))

    def process(self, path: Path):
        if not path.exists():
            return
        if not wait_until_stable(path):
            return
        try:
            note, dest = classify_and_route(path)
            log(f"\u2713 {path.name} -> {dest} ({note})")
        except Exception as e:
            log(f"\u2717 FAILED processing {path.name}: {e}")
            return
        rescan_and_score()
        try:
            generate_handoff.regenerate()
        except Exception as e:
            log(f"⚠ Could not refresh LATEST_HANDOFF.md: {e}")


def main():
    INBOX_DIR.mkdir(parents=True, exist_ok=True)
    log(f"Watcher started. Watching: {INBOX_DIR}")

    handler = InboxHandler()

    # Process anything already sitting in the inbox before we started watching
    for existing in sorted(INBOX_DIR.iterdir()):
        if existing.is_file():
            handler.process(existing)

    observer = Observer()
    observer.schedule(handler, str(INBOX_DIR), recursive=False)
    observer.start()
    log("Now watching for new files. Leave this running.")

    last_retention_check = 0  # 0 forces a first pass shortly after startup
    try:
        while True:
            time.sleep(5)
            if time.time() - last_retention_check >= RETENTION_CHECK_INTERVAL_SECONDS:
                try:
                    recycled = image_handling.cleanup_aged_confirmed_screenshots(
                        generate_handoff.HANDOFF_ARCHIVE_DIR / "images",
                        log=log,
                    )
                    if recycled:
                        log(f"Screenshot retention pass: recycled {len(recycled)} aged confirmed screenshot(s)")
                except Exception as e:
                    log(f"⚠ Screenshot retention pass failed: {e}")
                last_retention_check = time.time()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    log("Watcher stopped.")


if __name__ == "__main__":
    main()
