import bpy
import os
import sys
import shutil
import json
from datetime import datetime

# --- Hard safety guard: refuse to run against a live/interactive session ---
# bpy.app.background is True only when Blender was actually launched with
# --background. If this is False, we're running inside a connected/GUI
# session (e.g. invoked via blender-mcp's execute_blender_code against the
# live session) - clear_scene()'s read_factory_settings(use_empty=True)
# would wipe that scene on every one of the ~250 iterations below. Refuse
# outright rather than relying on always remembering to invoke this the
# right way.
if not bpy.app.background:
    raise SystemExit(
        "REFUSING TO RUN: this script must only be invoked headless via "
        "'blender --background --python rescale_all_ships.py -- ...' as its "
        "own separate process. bpy.app.background is False, meaning this is "
        "running inside a connected/interactive Blender session - continuing "
        "would call read_factory_settings(use_empty=True) up to ~250 times "
        "and wipe out whatever scene is currently open there."
    )

# Args after "--" when invoked via:
# blender --background --python rescale_all_ships.py -- <sc-ships dir> <target scale>
argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []

ships_root = argv[0] if len(argv) > 0 else "sc-ships"
target_scale = float(argv[1]) if len(argv) > 1 else 0.01
tolerance = 0.0001  # float comparison isn't exact after import/export round-trips

results = []
needs_review = []   # ships with a real problem - missing/corrupt/empty 3D file
secondary_notes = []  # lower-severity, non-blocking observations
chassis_copied = []    # auto-copied high-confidence chassis-share matches
chassis_ambiguous = []  # candidate siblings found, but not safe to auto-pick
chassis_no_candidate = []  # no sibling model exists locally at all

# Trim/edition-code suffixes that have PROVEN to mean a genuinely different
# hull, not just a livery - confirmed against real file sizes in this repo
# (Fury LX is 7,640,112 bytes vs Fury MX at 6,392,708 - different meshes).
# A single-word suffix matching this pattern is treated as unsafe to
# auto-copy even with only one candidate found.
TRIM_CODE_SUFFIX = __import__("re").compile(r"^[A-Z]{1,3}$")


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def get_mesh_scale_and_dims(objects):
    for obj in objects:
        if obj.type == 'MESH':
            return tuple(obj.scale), tuple(obj.dimensions)
    return None, None


ship_folders = sorted(
    d for d in os.listdir(ships_root)
    if os.path.isdir(os.path.join(ships_root, d))
)

# ---------------- Pre-pass: chassis cross-reference for ships with no model ----------------
ships_with_model = {d for d in ship_folders if os.path.isfile(os.path.join(ships_root, d, "model.glb"))}
ships_without_model = [d for d in ship_folders if d not in ships_with_model]

for ship_name in ships_without_model:
    candidates = [
        c for c in ships_with_model
        if c != ship_name and (c.startswith(ship_name) or ship_name.startswith(c))
    ]
    if not candidates:
        chassis_no_candidate.append({"ship": ship_name, "path": os.path.join(ships_root, ship_name)})
        continue

    sizes = {c: os.path.getsize(os.path.join(ships_root, c, "model.glb")) for c in candidates}

    if len(set(sizes.values())) == 1:
        source = min(candidates, key=len)
        confidence_reason = f"byte-identical to {len(candidates)} sibling(s): {sorted(sizes.keys())}"
    elif len(candidates) == 1:
        suffix = candidates[0][len(ship_name):].strip() if candidates[0].startswith(ship_name) else ship_name[len(candidates[0]):].strip()
        if TRIM_CODE_SUFFIX.match(suffix):
            chassis_ambiguous.append({
                "ship": ship_name, "path": os.path.join(ships_root, ship_name),
                "candidates": sizes,
                "reason": f"only candidate '{candidates[0]}' has a short trim-code-style suffix "
                          f"('{suffix}') - this repo has proof (Fury LX vs Fury MX) that this kind "
                          f"of suffix can mean a genuinely different hull, not just livery"
            })
            continue
        source = candidates[0]
        confidence_reason = f"single candidate '{source}', suffix does not look like a trim code"
    else:
        chassis_ambiguous.append({
            "ship": ship_name, "path": os.path.join(ships_root, ship_name),
            "candidates": sizes,
            "reason": f"{len(candidates)} candidates found with DIFFERENT sizes - likely different "
                      f"hulls, not just livery: {sizes}"
        })
        continue

    src_path = os.path.join(ships_root, source, "model.glb")
    dst_path = os.path.join(ships_root, ship_name, "model.glb")
    shutil.copyfile(src_path, dst_path)

    with open(os.path.join(ships_root, ship_name, "MODEL_SOURCE.txt"), "w") as f:
        f.write(
            f"model.glb in this folder was copied from sc-ships/{source}/model.glb on "
            f"{datetime.now().isoformat()} because they share the same base chassis "
            f"({confidence_reason}). Not ship-specific source art - if a real distinct "
            f"model for {ship_name} is ever sourced, replace this file and delete this note.\n"
        )

    chassis_copied.append({"ship": ship_name, "path": os.path.join(ships_root, ship_name),
                            "source": source, "reason": confidence_reason})
    ships_with_model.add(ship_name)
    print(f"[chassis cross-ref] {ship_name} <- {source} ({confidence_reason})")

chassis_explained = {i["ship"] for i in chassis_ambiguous} | {i["ship"] for i in chassis_no_candidate}

for ship_name in ship_folders:
    ship_dir = os.path.join(ships_root, ship_name)
    model_path = os.path.join(ship_dir, "model.glb")
    scaled_path = os.path.join(ship_dir, "model_scaled.glb")
    image_path = os.path.join(ship_dir, "image.webp")

    entry = {"ship": ship_name, "path": ship_dir, "status": None,
             "before_scale": None, "before_dimensions": None}

    if not os.path.isfile(model_path):
        entry["status"] = "MISSING - model.glb not found"
        results.append(entry)
        if ship_name not in chassis_explained:
            needs_review.append({
                "path": ship_dir, "file": "model.glb",
                "problem": "File does not exist in this ship's folder"
            })
        print(f"[{ship_name}] {entry['status']}")
        continue

    if os.path.getsize(model_path) == 0:
        entry["status"] = "CORRUPT - model.glb is 0 bytes (empty file)"
        results.append(entry)
        needs_review.append({
            "path": ship_dir, "file": "model.glb",
            "problem": "File exists but is empty (0 bytes) - no usable 3D data"
        })
        print(f"[{ship_name}] {entry['status']}")
        continue

    try:
        clear_scene()
        bpy.ops.import_scene.gltf(filepath=model_path)
    except Exception as e:
        entry["status"] = f"CORRUPT - model.glb failed to load: {e}"
        results.append(entry)
        needs_review.append({
            "path": ship_dir, "file": "model.glb",
            "problem": f"File exists but Blender could not import it: {e}"
        })
        print(f"[{ship_name}] {entry['status']}")
        continue

    scale, dims = get_mesh_scale_and_dims(bpy.context.scene.objects)
    entry["before_scale"] = scale
    entry["before_dimensions"] = dims

    if scale is None:
        entry["status"] = "MISSING - model.glb imported but contains no mesh data"
        results.append(entry)
        needs_review.append({
            "path": ship_dir, "file": "model.glb",
            "problem": "File loads in Blender but contains no mesh object - not a usable 3D model"
        })
        print(f"[{ship_name}] {entry['status']}")
        continue

    try:
        already_at_target = all(abs(s - target_scale) < tolerance for s in scale)

        if already_at_target:
            if not os.path.isfile(scaled_path):
                shutil.copyfile(model_path, scaled_path)
                entry["status"] = f"ALREADY {target_scale} - copied to model_scaled.glb"
            else:
                entry["status"] = f"ALREADY {target_scale} - model_scaled.glb already existed, left as-is"
        else:
            for obj in bpy.context.scene.objects:
                if obj.type in ('MESH', 'EMPTY'):
                    obj.scale = (target_scale, target_scale, target_scale)

            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

            bpy.ops.export_scene.gltf(filepath=scaled_path, export_format='GLB')

            after_scale, after_dims = get_mesh_scale_and_dims(bpy.context.scene.objects)
            entry["after_scale"] = after_scale
            entry["after_dimensions"] = after_dims
            entry["status"] = f"RESCALED {scale} -> {target_scale}, written to model_scaled.glb"

    except Exception as e:
        entry["status"] = f"ERROR - {e}"
        needs_review.append({
            "path": ship_dir, "file": "model.glb",
            "problem": f"Loaded fine but rescale/export step failed: {e}"
        })

    if not os.path.isfile(image_path):
        secondary_notes.append({
            "path": ship_dir, "file": "image.webp",
            "problem": "Preview image missing (does not block rescale, flagged for awareness)"
        })

    results.append(entry)
    print(f"[{ship_name}] {entry['status']}")

already_ok = [r for r in results if r["status"] and r["status"].startswith("ALREADY")]
rescaled = [r for r in results if r["status"] and r["status"].startswith("RESCALED")]
missing = [r for r in results if r["status"] and r["status"].startswith("MISSING")]
corrupt = [r for r in results if r["status"] and r["status"].startswith("CORRUPT")]
errored = [r for r in results if r["status"] and r["status"].startswith("ERROR")]

print("\n=== SUMMARY ===")
print(f"Total ships checked: {len(results)}")
print(f"Already at {target_scale}: {len(already_ok)}")
print(f"Rescaled: {len(rescaled)}")
print(f"Missing model file: {len(missing)}")
print(f"Corrupt/unreadable: {len(corrupt)}")
print(f"Other errors: {len(errored)}")
print(f"Missing preview image (secondary): {len(secondary_notes)}")
print(f"Chassis cross-ref - auto-copied (high confidence): {len(chassis_copied)}")
print(f"Chassis cross-ref - ambiguous (needs a human pick): {len(chassis_ambiguous)}")
print(f"Chassis cross-ref - no local candidate: {len(chassis_no_candidate)}")

timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

report_path = f"model_rescale_report__{timestamp}.json"
with open(report_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nFull report written to {report_path}")

if needs_review or secondary_notes or chassis_copied or chassis_ambiguous or chassis_no_candidate:
    review_dir = "_needs_review"
    os.makedirs(review_dir, exist_ok=True)
    review_path = os.path.join(review_dir, f"model_rescale_missing_assets__{timestamp}.md")

    with open(review_path, "w") as f:
        f.write(f"# Model Rescale — Missing/Corrupt 3D Assets\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        f.write(f"Run against: `{ships_root}` (target scale {target_scale})\n\n")

        if chassis_copied:
            f.write("## Chassis cross-reference — auto-copied (high confidence)\n\n")
            f.write("| Ship | Path | Copied from | Reason |\n|---|---|---|---|\n")
            for item in chassis_copied:
                f.write(f"| {item['ship']} | `{item['path']}` | {item['source']} | {item['reason']} |\n")
            f.write("\n")

        if chassis_ambiguous:
            f.write("## Chassis cross-reference — needs a human pick\n\n")
            f.write("| Ship | Path | Candidates (bytes) | Why it's ambiguous |\n|---|---|---|---|\n")
            for item in chassis_ambiguous:
                cand_str = ", ".join(f"{k} ({v})" for k, v in item["candidates"].items())
                f.write(f"| {item['ship']} | `{item['path']}` | {cand_str} | {item['reason']} |\n")
            f.write("\n")

        if chassis_no_candidate:
            f.write("## Chassis cross-reference — no local candidate\n\n")
            f.write("| Ship | Path |\n|---|---|\n")
            for item in chassis_no_candidate:
                f.write(f"| {item['ship']} | `{item['path']}` |\n")
            f.write("\n")

        if needs_review:
            f.write("## Needs review — model file missing, empty, or unreadable\n\n")
            f.write("| Path | File | Problem |\n|---|---|---|\n")
            for item in needs_review:
                f.write(f"| `{item['path']}` | {item['file']} | {item['problem']} |\n")
            f.write("\n")

        if secondary_notes:
            f.write("## Secondary notes — missing preview image (non-blocking)\n\n")
            f.write("| Path | File | Problem |\n|---|---|---|\n")
            for item in secondary_notes:
                f.write(f"| `{item['path']}` | {item['file']} | {item['problem']} |\n")
            f.write("\n")

    print(f"Needs-review report written to {review_path}")

    inbox_dir = "inbox"
    os.makedirs(inbox_dir, exist_ok=True)
    update_path = os.path.join(inbox_dir, "update_model_rescale_findings.md")

    with open(update_path, "w") as f:
        f.write(f"# UPDATE — Model rescale run found missing/corrupt 3D assets ({datetime.now().strftime('%Y-%m-%d')})\n\n")
        f.write(
            f"Ran the sc-ships/ rescale-to-{target_scale} pass across {len(results)} ship folders. "
            f"{len(already_ok)} were already correct, {len(rescaled)} got rescaled cleanly. "
            f"{len(needs_review)} ship(s) have a real problem with their model.glb (missing, empty, "
            f"or unreadable) and need real 3D source files before they can be rescaled or used.\n\n"
        )
        if chassis_copied:
            f.write(
                f"Chassis cross-reference auto-copied {len(chassis_copied)} model(s) from a sibling ship "
                f"that shares the same hull (livery/edition variants only, provenance noted in each "
                f"folder's MODEL_SOURCE.txt): "
                + ", ".join(f"{i['ship']} <- {i['source']}" for i in chassis_copied) + "\n\n"
            )
        if chassis_ambiguous:
            f.write(
                f"{len(chassis_ambiguous)} ship(s) have a candidate sibling model but NOT auto-copied - "
                f"the evidence wasn't strong enough (different file sizes between trim variants, proven "
                f"in this repo to mean different hulls): "
                + ", ".join(i["ship"] for i in chassis_ambiguous) + ". See the needs-review doc for candidates.\n\n"
            )
        if chassis_no_candidate:
            f.write(
                f"{len(chassis_no_candidate)} ship(s) have no sibling model anywhere in this repo, need "
                f"real source data: " + ", ".join(i["ship"] for i in chassis_no_candidate) + "\n\n"
            )
        if needs_review:
            f.write("Ships needing a new/replacement 3D model file:\n\n")
            for item in needs_review:
                f.write(f"- `{item['path']}` — {item['file']}: {item['problem']}\n")
            f.write("\n")
        if secondary_notes:
            f.write(f"Also missing a preview image only (cosmetic, non-blocking): {len(secondary_notes)} ship(s).\n\n")
        f.write(
            f"Full details: `{review_path}` (per-ship table) and `{report_path}` (machine-readable). "
            f"This is also now a permanent checker (`missing_or_corrupt_3d_model_check` in "
            f"checks/file_checks.py) so future audit runs catch this automatically going forward, "
            f"not just this one-off rescale pass.\n"
        )

    print(f"Inbox update written to {update_path} — will be folded into LATEST_HANDOFF.md on next regen")
else:
    print("No missing/corrupt assets found - no needs-review report or inbox update written.")
