"""
Ship Component Schema Builder — Citizen Compass data-layer tool

Splits a ship's data into the "clickable 3D hardpoint" set (weapons, missiles,
turrets — physically-mounted, positioned in the viewer) versus the "loadout
menu" set (power plant, coolers, shield, quantum drive, and other systems
that are picked from a menu, not clicked on the model).

Reuses hardpoint_organizer.categorize_hardpoint() for the physical-hardpoint
split rather than reimplementing that logic.

Inputs:
    tests/testing-site/ships/<slug>/hardpoints.json   (Blender-exported
        positions, has "type" per hardpoint — the physical/clickable set)
    data-layerrawhardpoints/ship_specs.json            (scraped ship-spec
        dump; each ship's "components" list is the source for components.json,
        after excluding entries whose type is itself a physical hardpoint
        category, since those are already covered by the hardpoints_*.json
        files)

Output, per ship, in data-layer/processed/hardpoints_by_type/<slug>/:
    hardpoints_weapons.json
    hardpoints_missiles.json
    hardpoints_turrets.json
    components.json

Usage:
    python build_ship_component_schema.py <slug> <ship_specs_slug>

    e.g. python build_ship_component_schema.py arrow anvl-arrow

The two slugs are passed separately because the viewer's ship-folder slug
("arrow") and ship_specs.json's slug ("anvl-arrow") don't always match.
"""

import json
import sys
from pathlib import Path

from hardpoint_organizer import categorize_hardpoint

PROJECT_ROOT = Path(__file__).resolve().parent
SHIPS_DIR = PROJECT_ROOT / "tests" / "testing-site" / "ships"
SHIP_SPECS_PATH = PROJECT_ROOT / "data-layerrawhardpoints" / "ship_specs.json"
OUT_ROOT = PROJECT_ROOT / "data-layer" / "processed" / "hardpoints_by_type"

# Component types that are themselves physical/clickable hardpoints, already
# represented in the hardpoints_*.json files -- excluded from components.json
# so nothing is duplicated between the two.
PHYSICAL_COMPONENT_TYPES = {"turrets", "weapons", "missiles"}


def load_physical_hardpoints(viewer_slug: str):
    path = SHIPS_DIR / viewer_slug / "hardpoints.json"
    if not path.exists():
        raise FileNotFoundError(f"No viewer hardpoints file at {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    by_category = {"weapons": [], "turrets": [], "missiles": [], "components": []}
    for hp in data.get("hardpoints", []):
        by_category[categorize_hardpoint(hp)].append(hp)

    return data.get("ship_name", viewer_slug), data.get("ship_slug", viewer_slug), by_category


def load_components(specs_slug: str):
    if not SHIP_SPECS_PATH.exists():
        raise FileNotFoundError(f"No ship specs file at {SHIP_SPECS_PATH}")
    with open(SHIP_SPECS_PATH, "r", encoding="utf-8") as f:
        ships = json.load(f)

    match = next(
        (s["data"] for s in ships if s.get("data", {}).get("slug") == specs_slug),
        None,
    )
    if match is None:
        raise ValueError(f"No ship_specs.json entry with slug '{specs_slug}'")

    all_components = match.get("components", [])
    menu_components = [c for c in all_components if c.get("type") not in PHYSICAL_COMPONENT_TYPES]
    physical_counts = {
        t: sum(c.get("quantity", 1) for c in all_components if c.get("type") == t)
        for t in PHYSICAL_COMPONENT_TYPES
    }
    return match.get("name", specs_slug), match.get("slug", specs_slug), menu_components, physical_counts


def build(viewer_slug: str, specs_slug: str):
    ship_name, ship_slug, physical = load_physical_hardpoints(viewer_slug)
    specs_name, _specs_slug, menu_components, physical_counts_from_specs = load_components(specs_slug)

    out_dir = OUT_ROOT / viewer_slug
    out_dir.mkdir(parents=True, exist_ok=True)

    files_written = {}
    for category, filename in (
        ("weapons", "hardpoints_weapons.json"),
        ("missiles", "hardpoints_missiles.json"),
        ("turrets", "hardpoints_turrets.json"),
    ):
        payload = {"ship_name": ship_name, "ship_slug": ship_slug, "hardpoints": physical[category]}
        out_path = out_dir / filename
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
        files_written[filename] = payload

    components_payload = {"ship_name": specs_name, "ship_slug": ship_slug, "components": menu_components}
    components_path = out_dir / "components.json"
    with open(components_path, "w", encoding="utf-8") as f:
        json.dump(components_payload, f, indent=2)
    files_written["components.json"] = components_payload

    # Flag any mismatch between the two data sources rather than silently
    # papering over it -- they come from different pipelines and can disagree.
    discrepancies = []
    for category in PHYSICAL_COMPONENT_TYPES:
        viewer_count = len(physical[category])
        specs_count = physical_counts_from_specs.get(category, 0)
        if viewer_count != specs_count:
            discrepancies.append(
                f"{category}: viewer hardpoints.json has {viewer_count}, "
                f"ship_specs.json components list says {specs_count}"
            )

    return out_dir, files_written, discrepancies


def main():
    if len(sys.argv) != 3:
        print("Usage: python build_ship_component_schema.py <viewer_slug> <ship_specs_slug>")
        print("  e.g.  python build_ship_component_schema.py arrow anvl-arrow")
        return

    viewer_slug, specs_slug = sys.argv[1], sys.argv[2]
    out_dir, files_written, discrepancies = build(viewer_slug, specs_slug)

    print(f"Done. Wrote 4 files to {out_dir}\n")
    for filename, payload in files_written.items():
        key = "hardpoints" if "hardpoints" in payload else "components"
        print(f"  {filename}: {len(payload[key])} entries")

    if discrepancies:
        print("\nDiscrepancies between the two data sources (not auto-reconciled):")
        for d in discrepancies:
            print(f"  - {d}")


if __name__ == "__main__":
    main()
