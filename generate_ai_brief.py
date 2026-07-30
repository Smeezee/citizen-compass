"""
AI Brief Generator — Citizen Compass data-layer tool

Scans your processed hardpoint data and writes a compact JSON briefing
you can paste into a fresh AI conversation to get it up to speed in
minutes instead of re-explaining the project each time.

Usage (run from your citizen-compass project root):

    python generate_ai_brief.py

Reads:
    data-layer/processed/hardpoints_by_type/*_organized.json
Writes:
    data-layer/exports/AI_BRIEF_COMPACT.json
"""

import json
from pathlib import Path
from datetime import datetime, timezone

PROCESSED_DIR = Path("data-layer/processed/hardpoints_by_type")
EXPORTS_DIR = Path("data-layer/exports")
TOTAL_SHIPS_TARGET = 452  # update if your target ship count changes


def load_processed_ships():
    ships = []
    if not PROCESSED_DIR.exists():
        return ships
    for f in sorted(PROCESSED_DIR.glob("*_organized.json")):
        with open(f, "r", encoding="utf-8") as fh:
            ships.append(json.load(fh))
    return ships


def generate_ai_brief():
    ships = load_processed_ships()
    ships_done = len(ships)

    by_category_totals = {"weapons": 0, "turrets": 0, "missiles": 0, "components": 0}
    sample_ship = None
    for ship in ships:
        for cat, items in ship.get("categories", {}).items():
            by_category_totals[cat] = by_category_totals.get(cat, 0) + len(items)
        if sample_ship is None:
            sample_ship = ship

    brief = {
        "briefing": {
            "version": "1.0",
            "generated": datetime.now(timezone.utc).isoformat(),
            "project": "Citizen Compass",
            "mission": "Build complete Star Citizen ship viewer, hardpoint reference, and compatibility database",
        },
        "data_summary": {
            "ships_with_hardpoints": ships_done,
            "total_ships_target": TOTAL_SHIPS_TARGET,
            "ships_remaining": max(TOTAL_SHIPS_TARGET - ships_done, 0),
            "by_category": by_category_totals,
        },
        "sample_ship": sample_ship,
        "what_needs_work": [
            f"Hardpoint data for {max(TOTAL_SHIPS_TARGET - ships_done, 0)} remaining ships",
            "Cross-reference hardpoint types with in-game data",
            "Verify component compatibility",
            "Complete 3D models for all ships",
        ],
        "data_format": {
            "hardpoint_types": [
                "missile_rack",
                "weapon_gun",
                "weapon_turret",
                "weapon_launcher",
            ],
            "position_format": {"x": "float", "y": "float", "z": "float"},
            "ship_fields": ["ship_name", "ship_slug", "hardpoints"],
        },
        "how_to_use": (
            "This briefing contains everything needed to work on Citizen Compass. "
            "Each hardpoint has a name, type, label, and 3D position. Ships are "
            "organized by slug (cutlass_black, arrow, etc.)."
        ),
    }

    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = EXPORTS_DIR / "AI_BRIEF_COMPACT.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(brief, f, indent=2)

    print(f"✓ AI Brief generated: {out_path.resolve()}")
    print(f"  {ships_done}/{TOTAL_SHIPS_TARGET} ships have hardpoint data")


if __name__ == "__main__":
    generate_ai_brief()
