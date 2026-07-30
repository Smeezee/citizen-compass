"""
Hardpoint Organizer — Citizen Compass data-layer tool

Reads raw per-ship hardpoint JSON files (as exported from Blender / your
current pipeline) and writes an organized, categorized copy of each into
processed/hardpoints_by_type/.

Usage (run from your citizen-compass project root, e.g.
C:\\Users\\david\\citizen-compass):

    python hardpoint_organizer.py

Expects:
    data-layer/raw/hardpoints/*.json      (input — untouched)
Writes:
    data-layer/processed/hardpoints_by_type/<slug>_organized.json
"""

import json
from pathlib import Path

RAW_DIR = Path("data-layer/raw/hardpoints")
PROCESSED_DIR = Path("data-layer/processed/hardpoints_by_type")


def categorize_hardpoint(hardpoint: dict) -> str:
    """Categorize a hardpoint by its 'type' field."""
    hp_type = hardpoint.get("type", "").lower()

    if "turret" in hp_type:
        return "turrets"
    if "missile" in hp_type or "launcher" in hp_type:
        return "missiles"
    if "gun" in hp_type:
        return "weapons"
    return "components"


def process_ship_hardpoints(json_file: Path) -> dict:
    """Read one ship's raw hardpoint file and organize it by category."""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    organized = {
        "ship_name": data.get("ship_name", json_file.stem),
        "ship_slug": data.get("ship_slug", json_file.stem),
        "categories": {
            "weapons": [],
            "turrets": [],
            "missiles": [],
            "components": [],
        },
    }

    for hp in data.get("hardpoints", []):
        category = categorize_hardpoint(hp)
        organized["categories"][category].append(hp)

    organized["total_hardpoints"] = sum(
        len(v) for v in organized["categories"].values()
    )

    return organized


def main():
    if not RAW_DIR.exists():
        print(f"✗ Raw hardpoints folder not found: {RAW_DIR.resolve()}")
        print("  Create it and drop your ship *_hardpoints.json files inside.")
        return

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    files = sorted(RAW_DIR.glob("*.json"))
    if not files:
        print(f"✗ No JSON files found in {RAW_DIR.resolve()}")
        return

    for json_file in files:
        try:
            organized = process_ship_hardpoints(json_file)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"✗ Skipped {json_file.name}: {e}")
            continue

        out_path = PROCESSED_DIR / f"{organized['ship_slug']}_organized.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(organized, f, indent=2)

        print(f"✓ {organized['ship_name']} — {organized['total_hardpoints']} hardpoints")

    print(f"\nDone. {len(files)} ship file(s) processed into {PROCESSED_DIR.resolve()}")


if __name__ == "__main__":
    main()
