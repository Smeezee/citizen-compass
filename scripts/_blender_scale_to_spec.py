"""Blender side of the scale fix. Run headless, never against a live session.

    blender --background --python scripts/_blender_scale_to_spec.py -- <job.json>

The job file is a list of:
    {"folder": ..., "in": <model.glb>, "out": <model_scaled.glb>,
     "target_max": <metres>}

WHAT THIS DOES DIFFERENTLY FROM rescale_all_ships.py
====================================================
That script FORCES every object's scale to a constant (0.01) and bakes it. It
measures nothing. That is correct for the 234 models this project already had,
because of how they were authored, and it is wrong for anything authored to a
different convention - the Fleetyards imports came in at object scales of 1.0,
24.8, 0.0576, 1.21 and 0.165, and forcing 0.01 onto those produced hulls
ranging from 0.001 m to 91 m for ships that are 4 m to 752 m long.

This one MEASURES. It reads the model's actual bounding box, compares it to the
ship's published size, and scales by the ratio. No convention is assumed, so a
model authored in centimetres, metres or anything else lands in the same place.

WHY IT SCALES ONE NEW ROOT AND DOES NOT BAKE
--------------------------------------------
Everything in the file is parented to a single new empty at the world origin,
and that empty is scaled. One transform, above every object, applied once - it
cannot compound through a hierarchy and it cannot miss a branch. The glTF
exporter writes it as a node transform, which the viewer honours.

The result is verified by re-measuring the scene afterwards, and again in a real
browser by checks/_verify_model_scale.mjs, rather than by trusting this comment.
"""

import json
import sys

import bpy
from mathutils import Vector

if not bpy.app.background:
    raise SystemExit(
        "REFUSING TO RUN: this must be invoked headless via "
        "'blender --background --python scripts/_blender_scale_to_spec.py -- <job>'. "
        "bpy.app.background is False, so this is a connected session and "
        "clear_scene() would wipe whatever is open in it.")

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
if not argv:
    raise SystemExit("no job file given")

with open(argv[0], encoding="utf-8") as fh:
    jobs = json.load(fh)


def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def world_extent():
    """Largest world-space dimension across every mesh in the scene."""
    lo = Vector((float("inf"),) * 3)
    hi = Vector((float("-inf"),) * 3)
    seen = False
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        for corner in obj.bound_box:
            p = obj.matrix_world @ Vector(corner)
            for i in range(3):
                lo[i] = min(lo[i], p[i])
                hi[i] = max(hi[i], p[i])
            seen = True
    if not seen:
        return None, None
    size = (hi - lo)
    return max(size), tuple(size)


results = []
for job in jobs:
    entry = {"folder": job["folder"], "target_max": job["target_max"]}
    try:
        clear()
        bpy.ops.import_scene.gltf(filepath=job["in"])
        before, before_size = world_extent()
        if not before:
            entry["status"] = "ERROR - no mesh in the imported file"
            results.append(entry)
            continue
        entry["before_max"] = before
        entry["before_size"] = before_size

        factor = job["target_max"] / before
        entry["factor"] = factor

        # SCALE ONE NEW ROOT, NOT THE EXISTING ONES.
        #
        # The first version scaled every parentless object by the factor. That
        # is correct for a flat scene and it landed 18 of 19 ships exactly on
        # their target - and it put the 85X at 19.13 m when it wanted 14.00.
        # That ship has 985 objects and a hierarchy where scaling the roots
        # does not move everything by the same amount.
        #
        # Rather than work out which arrangement the 85X uses and hope the next
        # import uses one of the arrangements handled, everything is parented
        # to a single new empty at the world origin and THAT is scaled. One
        # transform, applied once, above every object in the file. It cannot
        # compound and it cannot miss a branch, whatever the source hierarchy
        # looks like.
        bpy.ops.object.empty_add(type="PLAIN_AXES", location=(0, 0, 0))
        root = bpy.context.object
        root.name = "CC_SCALE_ROOT"
        for obj in list(bpy.context.scene.objects):
            if obj is root or obj.parent is not None:
                continue
            keep = obj.matrix_world.copy()
            obj.parent = root
            obj.matrix_world = keep
        root.scale = (factor, factor, factor)
        bpy.context.view_layer.update()

        after, after_size = world_extent()
        entry["after_max"] = after
        entry["after_size"] = after_size

        bpy.ops.export_scene.gltf(filepath=job["out"], export_format="GLB")
        # The check that matters: did the scene actually end up the size asked
        # for. A 1% band is well inside the spread the published figures
        # themselves show against models known to be right (0.92 - 1.03).
        ok = abs(after - job["target_max"]) / job["target_max"] < 0.01
        entry["status"] = "OK" if ok else (
            "ERROR - scaled to %.4f but wanted %.4f" % (after, job["target_max"]))
    except Exception as exc:  # noqa: BLE001 - reported, not swallowed
        entry["status"] = "ERROR - %s" % exc
    results.append(entry)
    print("[%s] %s  %s -> %s" % (job["folder"], entry.get("status"),
                                 entry.get("before_max"), entry.get("after_max")),
          flush=True)

with open(argv[0] + ".result.json", "w", encoding="utf-8") as fh:
    json.dump(results, fh, indent=1)
print("wrote %s.result.json" % argv[0], flush=True)
