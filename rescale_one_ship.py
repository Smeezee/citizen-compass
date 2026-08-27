"""
A3 - rescale ONE named model, headless, and report its bounds before and after.

    blender --background --python rescale_one_ship.py -- <in.glb> <out.glb> <factor>

WHY ONE AND NOT THE FLEET. rescale_all_ships.py exists and walks sc-ships/
wholesale. A3 is a single hull with a known, measured defect - the Anvil
Asgard's model was never converted out of centimetres and measures about 101x
its stated size. A fleet pass to fix one ship is a mass mutation looking for an
excuse, and this repo has already paid for one of those.

REFUSES A LIVE SESSION, same as rescale_all_ships.py and for the same reason:
bpy.app.background is False when this is running inside a connected GUI Blender,
and nothing here should touch a scene somebody has open.

IT PRINTS THE BOUNDS BOTH WAYS. The point of the exercise is a number that can
be checked against the game's stated dimensions afterwards, not a file that is
merely different.
"""
import sys

import bpy

if not bpy.app.background:
    raise SystemExit(
        "REFUSING TO RUN: this must be invoked headless, as its own process:\n"
        "  blender --background --python rescale_one_ship.py -- <in> <out> <f>\n"
        "bpy.app.background is False, so this is a connected/interactive "
        "session and clearing it would destroy whatever is open there.")

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
if len(argv) < 3:
    raise SystemExit("usage: -- <in.glb> <out.glb> <factor>")
src, dst, factor = argv[0], argv[1], float(argv[2])
if not (factor > 0):
    raise SystemExit("factor must be positive")


def bounds():
    """World-space bounding box over every mesh in the scene."""
    lo = [float("inf")] * 3
    hi = [float("-inf")] * 3
    seen = 0
    for ob in bpy.context.scene.objects:
        if ob.type != "MESH":
            continue
        seen += 1
        for c in ob.bound_box:
            w = ob.matrix_world @ type(ob.location)(c)
            for i in range(3):
                lo[i] = min(lo[i], w[i])
                hi[i] = max(hi[i], w[i])
    if not seen:
        raise SystemExit("no mesh objects in the scene - nothing to measure")
    return lo, hi, seen


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)

lo, hi, n = bounds()
before = [hi[i] - lo[i] for i in range(3)]
print("meshes      : %d" % n)
print("before      : %.3f x %.3f x %.3f" % tuple(before))

# THE SCALE IS BAKED INTO THE VERTICES, NOT LEFT ON THE NODE, and that
# distinction is the whole of this step.
#
# Scaling the object and exporting writes a node transform. three.js honours
# it, so the VIEWER would have rendered the hull at the right size - and
# decode_glb_points.js reads raw POSITION accessors and ignores node
# transforms, so hull-geometry, every derived marker and the A4 auditor would
# all still have measured 4,856. The page would have looked fixed while every
# number behind it stayed wrong. Measured, not guessed: the first run of this
# script exported exactly that file and the decoder read the old box back.
for ob in bpy.context.scene.objects:
    if ob.parent is None:
        ob.scale = (ob.scale[0] * factor, ob.scale[1] * factor,
                    ob.scale[2] * factor)
        ob.location = (ob.location[0] * factor, ob.location[1] * factor,
                       ob.location[2] * factor)
bpy.context.view_layer.update()

bpy.ops.object.select_all(action="SELECT")
bpy.context.view_layer.objects.active = next(
    (o for o in bpy.context.scene.objects if o.type == "MESH"), None)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.context.view_layer.update()

lo, hi, _n = bounds()
after = [hi[i] - lo[i] for i in range(3)]
print("factor      : %g" % factor)
print("after       : %.3f x %.3f x %.3f" % tuple(after))

# THE SCALE MUST HAVE LANDED. A transform that silently did nothing would
# export a file that looks new and is not - which is the shape of defect this
# project keeps finding, so it is asserted rather than assumed.
for i in range(3):
    want = before[i] * factor
    if want > 0 and abs(after[i] - want) / want > 0.001:
        raise SystemExit(
            "RESCALE DID NOT TAKE on axis %d: expected %.4f, measured %.4f. "
            "Nothing was written." % (i, want, after[i]))

bpy.ops.export_scene.gltf(
    filepath=dst, export_format="GLB", export_draco_mesh_compression_enable=True,
    export_apply=True)
print("written     : %s" % dst)
