#!/usr/bin/env python3
"""
Citizen Compass ship matcher / watcher.

Watches an "incoming" folder for finished ship builds. Each finished ship
is a subfolder containing at minimum:
    model.glb
    hardpoints.json   (must have a "ship_name" field)

For each new subfolder found, this script:
  1. Reads the candidate ship name from hardpoints.json's "ship_name" field
     (falls back to the folder name if that field is missing).
  2. Fuzzy-matches that name against the 232-ship master list in
     ../data/ships-master.json.
  3. If there's a single confident match, copies the folder into
     ../ships/<slug>/ and adds/updates an entry in
     ../data/viewers-manifest.json.
  4. If the match is ambiguous (multiple similarly-close candidates, e.g.
     "Aurora ES" vs "Aurora LN" vs "Aurora MR"), it does NOT guess — it
     logs the candidates and skips the folder so you can rename it and
     let the next pass pick it up.

Run modes:
    python match_ship.py            # scan once and exit
    python match_ship.py --watch    # scan, then keep polling every N seconds
    python match_ship.py --watch --interval 10

No third-party dependencies — stdlib only (difflib for fuzzy matching),
so it runs with a plain python.exe on Windows with nothing else installed.
"""

import argparse
import json
import re
import shutil
import sys
import time
from difflib import SequenceMatcher
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent.parent
INCOMING_DIR = SITE_ROOT / "incoming"
SHIPS_DIR = SITE_ROOT / "ships"
MASTER_LIST_PATH = SITE_ROOT / "data" / "ships-master.json"
MANIFEST_PATH = SITE_ROOT / "data" / "viewers-manifest.json"
PROCESSED_MARKER = ".matched"  # dropped into a folder once it's been filed

# How close a match needs to be (0-1) to auto-accept, and how much better
# than the second-best candidate it needs to be to avoid an ambiguous flag.
CONFIDENCE_THRESHOLD = 0.72
MARGIN_OVER_RUNNER_UP = 0.08


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def load_json(path: Path, default):
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_master():
    master = load_json(MASTER_LIST_PATH, [])
    if not master:
        print(f"[error] Master ship list not found or empty: {MASTER_LIST_PATH}")
        sys.exit(1)
    return master


def best_matches(candidate_name: str, master: list, top_n: int = 3):
    """Return top_n (ship_dict, ratio) pairs sorted by similarity, best first."""
    scored = []
    cn = candidate_name.lower().strip()
    for ship in master:
        ratio = SequenceMatcher(None, cn, ship["name"].lower()).ratio()
        scored.append((ship, ratio))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_n]


def extract_candidate_name(folder: Path) -> str:
    hp_path = folder / "hardpoints.json"
    if hp_path.exists():
        try:
            data = json.loads(hp_path.read_text(encoding="utf-8"))
            name = data.get("ship_name")
            if name:
                return name
        except (json.JSONDecodeError, OSError) as e:
            print(f"  [warn] couldn't read hardpoints.json in {folder.name}: {e}")
    # fall back to the folder name, cleaned up (underscores/dashes -> spaces)
    return folder.name.replace("_", " ").replace("-", " ")


def count_hardpoints(folder: Path) -> tuple[int, int]:
    """Returns (done, total). Total is unknown from the file alone, so we
    just report how many are present; edit TOTAL_HARDPOINTS_BY_SLUG below
    if you want per-ship totals tracked automatically."""
    hp_path = folder / "hardpoints.json"
    if not hp_path.exists():
        return (0, 0)
    try:
        data = json.loads(hp_path.read_text(encoding="utf-8"))
        return (len(data.get("hardpoints", [])), 0)
    except (json.JSONDecodeError, OSError):
        return (0, 0)


def process_folder(folder: Path, master: list, manifest: dict) -> bool:
    """Returns True if the folder was successfully matched and filed."""
    required = ["model.glb", "hardpoints.json"]
    missing = [f for f in required if not (folder / f).exists()]
    if missing:
        print(f"  [skip] {folder.name}: missing {missing}")
        return False

    candidate_name = extract_candidate_name(folder)
    matches = best_matches(candidate_name, master)
    top_ship, top_ratio = matches[0]
    runner_up_ratio = matches[1][1] if len(matches) > 1 else 0.0

    if top_ratio < CONFIDENCE_THRESHOLD:
        print(f"  [no match] '{candidate_name}' — best guess '{top_ship['name']}' "
              f"only {top_ratio:.2f} similarity. Skipping; rename and retry.")
        return False

    if (top_ratio - runner_up_ratio) < MARGIN_OVER_RUNNER_UP:
        print(f"  [ambiguous] '{candidate_name}' could be several ships:")
        for ship, ratio in matches:
            print(f"      {ratio:.2f}  {ship['name']}")
        print("      Rename the source folder to be more specific and retry.")
        return False

    # Confident single match
    slug = top_ship["slug"]
    dest = SHIPS_DIR / slug
    dest.mkdir(parents=True, exist_ok=True)
    for item in folder.iterdir():
        if item.name == PROCESSED_MARKER:
            continue
        target = dest / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)

    hp_done, _ = count_hardpoints(folder)
    manifest[slug] = {
        "path": f"ships/{slug}/index.html" if (dest / "index.html").exists()
                 else f"ships/{slug}/",
        "hardpoints_done": hp_done,
        "hardpoints_total": manifest.get(slug, {}).get("hardpoints_total", hp_done),
        "added": manifest.get(slug, {}).get("added", time.strftime("%Y-%m-%d")),
    }

    print(f"  [matched] '{candidate_name}' -> {top_ship['name']} "
          f"(slug: {slug}, similarity {top_ratio:.2f})")
    (folder / PROCESSED_MARKER).write_text(
        f"Matched to {top_ship['name']} ({slug}) at {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
        encoding="utf-8"
    )
    return True


def scan_once():
    master = load_master()
    manifest = load_json(MANIFEST_PATH, {})

    if not INCOMING_DIR.exists():
        print(f"[info] Creating incoming folder at {INCOMING_DIR}")
        INCOMING_DIR.mkdir(parents=True)
        return

    candidates = [p for p in INCOMING_DIR.iterdir()
                  if p.is_dir() and not (p / PROCESSED_MARKER).exists()]

    if not candidates:
        print("[scan] Nothing new to process.")
        return

    print(f"[scan] Found {len(candidates)} unprocessed folder(s) in incoming/")
    changed = False
    for folder in candidates:
        print(f"Processing: {folder.name}")
        if process_folder(folder, master, manifest):
            changed = True

    if changed:
        save_json(MANIFEST_PATH, manifest)
        print(f"[done] Updated {MANIFEST_PATH}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--watch", action="store_true",
                         help="Keep running, polling incoming/ on an interval.")
    parser.add_argument("--interval", type=int, default=15,
                         help="Seconds between scans in --watch mode (default: 15).")
    args = parser.parse_args()

    if args.watch:
        print(f"[watch] Polling {INCOMING_DIR} every {args.interval}s. Ctrl+C to stop.")
        try:
            while True:
                scan_once()
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n[watch] Stopped.")
    else:
        scan_once()


if __name__ == "__main__":
    main()
