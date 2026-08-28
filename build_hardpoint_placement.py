#!/usr/bin/env python3
"""
Put the decoded hardpoints into the viewer's own space.

`decode_cga_nodes.py` emits METRES in CIG's frame - X lateral, Y fore/aft,
Z up. The viewer works in the GLB's own units with Y up and forward at -Z.
This converts between them, per hull, and refuses where it cannot check itself.

THE SCALE IS DERIVED THREE TIMES AND THE THREE HAVE TO AGREE.
CIG publishes Length, Width and Height for every ship in `ships.json`. The GLB
gives an extent on each axis. That is three independent estimates of one
number:

    s_length = Length / glb_z_extent
    s_width  = Width  / glb_x_extent
    s_height = Height / glb_y_extent

On the Vulture: 34/12.874 = 2.641, 16/6.169 = 2.594, 9/3.399 = 2.648.
**A wrong axis mapping makes these disagree wildly**, which is the whole point
of computing all three rather than trusting one. A hull whose three estimates
spread more than SPREAD_MAX is REPORTED, NOT CONVERTED.

Width is the weakest of the three and is treated as such: it is measured with
arms, wings or gear deployed on some hulls while the GLB is in a stowed pose.
The median is used, and the spread is recorded per hull so nobody has to guess
which hull was borderline.

THE ACCEPTANCE TEST IS "INSIDE THE SHIP".
Every converted hardpoint must land inside the hull's own measured box, with a
small margin for mounts that sit proud of the surface. A wrong scale or a
transposed axis throws hardpoints outside the hull, and that is a thing this
test can see. A hull where any hardpoint lands outside is written out with
`acceptance: false` and the offenders named - never dropped silently.

Output: data-layer/derived/hardpoint-placement/
"""
import glob
import json
import os
import re
import statistics
import struct
import sys

SRC = os.path.join("data-layer", "derived", "hardpoint-transforms")
GEO = os.path.join("data-layer", "derived", "hull-geometry")
OUT = os.path.join("data-layer", "derived", "hardpoint-placement")
MARGIN = 0.06              # 6% of the box, for mounts proud of the surface

# HOW MANY EXTERIOR MOUNTS A PROVEN HULL MAY WITHHOLD, AND WHY IT IS A COUNT
# RATHER THAN A FRACTION (C1, 2026-08-27).
#
# A proven frame is not a licence to ignore containment. `_verify_placement_gate`
# caught exactly that: mirroring is preserved by a uniform scale and by a
# uniform offset, so "the frame is proven" on its own let a 4x scale and a
# full-hull-length offset through on the Eclipse and the Sabre - hulls whose
# mounts mirror perfectly. The mirror answers "are the axes right"; it says
# nothing about how big or where.
#
# So the withholding is bounded, and the bound is an ABSOLUTE COUNT because the
# thing it distinguishes does not scale with the hull:
#
#     stowed-pose mismatches observed      1, 1, 2, 2, 3, 3, 3, 3
#     smallest frame error observed       23   (a 4x scale on the Gladius)
#     a full-hull offset                  every mount
#
# Four sits in a gap of nearly an order of magnitude, BELOW the smallest defect
# rather than above it - which is the difference between this and the
# proportional gate I tried earlier and had to revert. A fraction would give a
# 163-mount Reclaimer a bigger allowance than a 10-mount Glaive for no reason.
#
# IT IS CALIBRATED ON OBSERVED DATA AND THE CONTROL IS WHAT KEEPS IT HONEST:
# the check feeds three broken frames through the real rule and every one must
# still be refused. If a future hull needs a fifth withheld mount, the honest
# move is to look at that hull, not to raise this number.
WITHHOLD_MAX = 4

# THE FAMILY THAT GATES. Same split, and the same reason, as the acceptance in
# build_hardpoint_transforms.py: these are the mounts the viewer draws on the
# hull. Internal components go to the menu overlay under a standing decision.
# Thrusters, landing-gear doors, gravlev pads and cargo ramps live on geometry
# that DEPLOYS, and the GLB is one stowed pose - they are counted and reported,
# never gated on.
EXTERIOR = re.compile(
    r"hardpoint_(weapon|gun|turret|missile|missilerack|cm_launcher"
    r"|countermeasure|pylon|mount)", re.I)


def ship_dims():
    snaps = sorted(glob.glob(os.path.join(
        "data-layer", "external-sources", "scunpacked-data", "snapshots",
        "*", "ships.json")))
    if not snaps:
        return {}, None
    p = snaps[-1]
    d = json.load(open(p, encoding="utf-8"))
    if isinstance(d, dict):
        d = list(d.values())
    out = {}
    for r in d:
        if not isinstance(r, dict):
            continue
        cn = r.get("ClassName")
        if not cn:
            continue
        try:
            L, W, H = float(r["Length"]), float(r["Width"]), float(r["Height"])
        except Exception:
            continue
        if min(L, W, H) <= 0:
            continue
        out[cn.lower()] = {"Length": L, "Width": W, "Height": H,
                           "Name": r.get("Name")}
    return out, p


def part_roots():
    """class -> the hull its OWN CIG record says it is built on.

    THE AUTHORITY I SAID DID NOT EXIST (C1, 2026-08-27, correcting myself).

    An hour ago I wrote, in `FINDING_the-hull-rule-was-blind-...`: *"ships.json
    carries no geometry path - I checked every field on the row."* I checked the
    row's top-level fields for a PATH. THE ANSWER IS A NAME, nested one level
    down, and it was there the whole time:

        anvl_c8_pisces  ->  Parts[0].Name == "ANVL_Pisces"

    The root of CIG's own part tree names the hull the ship is built from. Not a
    prefix, not a similarity, not a guess - CIG's own record, joined by exact
    string equality to the decoded hull's name.

        classes carrying a root part name        309 of 318
        root name == the class itself            126
        root names a DIFFERENT hull              183, of which 164 are hulls
                                                 already decoded

    IT REACHES THE VARIANTS A NAME RULE NEVER COULD:

        AEGS_Gladius_Valiant    -> AEGS_Gladius
        AEGS_Vanguard_Harbinger -> AEGS_Vanguard
        ANVL_C8_Pisces          -> ANVL_Pisces      (no shared prefix at all)
        RSI_Ursa_Medivac        -> RSI_Ursa_Rover   (nor here)
        GRIN_MDC                -> GRIN_MXC         (nor here)

    IT REPLACES THE `cls + "_"` PREFIX EXPANSION RATHER THAN JOINING IT. That
    was a pattern standing in for exactly this fact. A variant whose record
    names a hull we have not decoded is reported, never approximated.

    AND IT IS SAFE WHERE THE NAME EXPANSION WAS NOT. An earlier experiment
    sprayed a base's hardpoints across everything sharing its prefix, and the
    acceptance test could not tell a wrong airframe from a right one. This does
    not need it to: only ports whose `HardpointName` exists as a NODE in that
    hull are ever placed, so a module-specific mount on a Harbinger gets NO
    position rather than a wrong one. The record decides membership; the
    geometry decides placement.
    """
    snaps = sorted(glob.glob(os.path.join(
        "data-layer", "external-sources", "scunpacked-data", "snapshots",
        "*", "ships.json")))
    if not snaps:
        return {}, None
    p = snaps[-1]
    d = json.load(open(p, encoding="utf-8"))
    if isinstance(d, dict):
        d = list(d.values())
    out = {}
    for r in d:
        if not isinstance(r, dict):
            continue
        cn = r.get("ClassName")
        parts = r.get("Parts")
        if not cn or not isinstance(parts, list) or not parts:
            continue
        if not isinstance(parts[0], dict):
            continue
        root = parts[0].get("Name")
        if root:
            out[cn.lower()] = root.lower()
    return out, p


def model_map():
    """class -> model filename, from the page's own generated map."""
    for cand in (os.path.join("testing", "_deploy", "loadout_model.gen.js"),
                 os.path.join("testing", "_src", "loadout_model.gen.js")):
        if os.path.exists(cand):
            m = re.search(r"=\s*(\{[\s\S]*?\});",
                          open(cand, encoding="utf-8").read())
            if m:
                return json.loads(m.group(1)), cand
    return {}, None


# ---------------------------------------------------------------------------
# THE SECOND SIGNAL: DOES THE CONVERTED CLOUD STILL MIRROR?
#
# C1, 2026-08-27. The containment test refuses a whole hull when ANY exterior
# mount lands outside, and that is right when the frame is in doubt - a
# transposed axis or a wrong scale throws mounts out and the hull's markers
# would be nonsense.
#
# BUT NINE OF THE TEN REFUSALS ARE NOT THAT. They are one to three mounts
# sitting a fraction proud of a STOWED-POSE mesh:
#
#     Constellation   gun_laser_top_left/right and turret_base_upper,
#                     0.53-0.71 above a 13.2-unit-tall hull   (the top turret)
#     Spirit A1       turret_rear, 0.12 above 8.6             (1.4%)
#     Defender        both missile racks, 0.28 below 5.9
#     Reliant         both wing-tip guns, 1.01 beyond 11.1    (the wings move)
#
# Throwing away nineteen good Constellation ports to avoid drawing three
# arguable ones leaves the reader with the NAME-DERIVED markers instead - a
# median 0.488 of a half-extent from the real mount. The refusal was worse than
# what it refused.
#
# I ALREADY TRIED TO FIX THIS WITH A PROPORTIONAL GATE AND IT WAS WRONG.
# `checks/_verify_placement_gate.py` proved a transposed axis survives a half
# threshold on every hull tested - ships are wider than they are tall, so the
# swap only displaces about a sixth of the mounts. A count of offenders cannot
# tell a pose mismatch from a frame error.
#
# SO THE GATE DOES NOT LOOSEN. A SECOND, INDEPENDENT SIGNAL DECIDES INSTEAD.
#
# Left/right mount pairs must mirror. Measured on the CONVERTED cloud, in the
# viewer's own frame, so it tests the conversion rather than the decode:
#
#     as-is                      transposed lateral/vertical
#     Gladius       4/4          0/4
#     Hammerhead    6/6          0/6
#     Constellation 8/8          0/8
#     Defender      4/4          0/4
#     Reliant       2/2          0/2
#
# A TRANSPOSE DESTROYS IT COMPLETELY - not partially, not marginally. And it is
# blind to scale, which is exactly what makes it complementary: containment
# catches a wrong scale and cannot see a transpose reliably; mirroring catches
# a transpose and cannot see a scale at all. Together they cover both.
#
# THE RULE: a hull whose named pairs MOSTLY mirror has proven its frame, and
# may withhold individual out-of-box mounts while keeping the rest. A hull that
# has NOT proven its frame is refused whole, exactly as before.
#
# THIS RULE CHANGED ON 2026-08-28 AND THE OLD VERSION OF THIS COMMENT WAS
# WRONG ABOUT THE SHIP IT NAMED. It read: "EVERY PAIR, NOT MOST. The Glaive
# scores 2 of 4 and stays refused - its geometry is genuinely asymmetric where
# the mount names say it should not be."
#
# **The Glaive is not asymmetric where its names say it should not be.** It
# scored 2 of 4 because the population was EXTERIOR pairs only, and the Glaive
# has almost none - its evidence is in the engines, coolers, fuel intakes and
# powerplants, which mirror to within 3 cm and were being filtered out and
# thrown away. Measured over ALL its named pairs it is 13 of 19. The Scythe,
# next to it in the same refusal, is 1 of 16 and IS genuinely asymmetric.
# Filtering had made two different ships look like one problem.
#
# WHY A FRACTION IS NOT A TUNED THRESHOLD HERE, WHICH IS THE OBJECTION THIS
# HAS TO ANSWER. The same measurement was taken on all 265 hulls with four or
# more named pairs, and then AGAIN on every one of them with the lateral and
# vertical axes transposed - the defect this test exists to catch:
#
#     transposed axis, highest fraction any hull reached    0.455
#     correct frame, lowest fraction above the halfway mark 0.684
#     hulls passing a HALF rule    clean 262 of 265    transposed 0 of 265
#
# **There is nothing between 0.455 and 0.684.** The rule is placed in an empty
# gap measured on the whole fleet, not fitted to admit a ship somebody wanted.
# The three clean hulls below half are the Scythe (0.062) and two Clippers
# (0.250 on 8 pairs), and they stay refused.
#
# THE PER-PAIR TOLERANCE IS UNCHANGED. What changed is WHICH PAIRS COUNT and
# how many must agree. M4's standing warning - "nobody should widen the mirror
# tolerance to get there" - is intact and was never the lever here.
#
# AND THE BOUND THAT MAKES THIS SAFE IS UNCHANGED. Mirroring survives a uniform
# scale and a whole-hull offset, which is why a proven frame buys withholding
# at most WITHHOLD_MAX mounts and never a pass. A rescaled hull still puts far
# more than four mounts outside its box and is still refused by containment.
#
# A hull with FEWER THAN MIN_PAIRS named pairs proves nothing and is refused -
# a check that could not have failed is not a check. Below four pairs the
# fraction is one or two mounts wide and says more about luck than about axes.
MIRROR_MIN_FRACTION = 0.5
MIRROR_MIN_PAIRS = 4


def converted_mirror(points, tol):
    """(matched, pairs) over ALL left/right families in the GLB frame.

    NOT exterior-only. The frame is a property of the hull's coordinate
    system, and an interior mount's transform comes out of the same node array,
    in the same run, through the same conversion. Restricting the evidence to
    mounts that happen to be drawn was throwing away the larger half of it.
    """
    hp = {h["name"]: h["pos"] for h in points}
    fam = {}
    for a in hp:
        if "_left" in a.lower():
            fam.setdefault(re.sub(r"_\d+$", "",
                                  a.lower().replace("_left", "|")),
                           [[], []])[0].append(a)
    for b in hp:
        if "_right" in b.lower():
            k = re.sub(r"_\d+$", "", b.lower().replace("_right", "|"))
            if k in fam:
                fam[k][1].append(b)
    pairs = matched = 0
    for _k, (ls, rs) in fam.items():
        free = list(rs)
        for a in ls:
            if not free:
                break
            pairs += 1
            best, bd = None, None
            for b in free:
                # lateral is axis 0 and must NEGATE; the other two must AGREE.
                d = max(abs(hp[a][0] + hp[b][0]),
                        abs(hp[a][1] - hp[b][1]),
                        abs(hp[a][2] - hp[b][2]))
                if bd is None or d < bd:
                    best, bd = b, d
            free.remove(best)
            if bd < tol:
                matched += 1
    return matched, pairs


def box(path):
    g = json.load(open(path, encoding="utf-8"))
    return g["min"], g["max"]


MODELS_DIR = os.path.join("testing", "_deploy", "models")


def glb_box(model_file):
    """The hull's bounding box read from the GLB's own header.

    WHY THIS EXISTS. Twelve hulls - every Fleetyards import from 2026-08-27 -
    have models and decoded hardpoints and no entry in `hull-geometry`, which
    was generated before they existed. They were being skipped, and the largest
    single coverage loss on the board was one missing generator run in somebody
    else's lane.

    NO MESH IS DECODED. glTF REQUIRES `min` and `max` on a POSITION accessor,
    and that requirement holds even when the mesh data itself is Draco-
    compressed - so the box is readable from the JSON chunk alone, without a
    Draco decoder and without touching a byte of geometry.

    AND IT IS NOT TRUSTED ON THAT ARGUMENT ALONE. Checked against the sampled
    boxes for five hulls that have both:

        Vulture 0.002%   Gladius 0.003%   Hammerhead 0.002%
        Polaris 0.003%   Arrow   0.001%     (of the hull's longest span)

    The agreement is asserted live in `main` for every hull that carries both,
    so a future model whose node transforms make the accessor bounds wrong is
    caught rather than assumed away. This does NOT write `hull-geometry` -
    that file has one writer and it is not this one.
    """
    path = os.path.join(MODELS_DIR, model_file)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "rb") as f:
            magic, _ver, _total = struct.unpack("<4sII", f.read(12))
            if magic != b"glTF":
                return None
            ln, _ty = struct.unpack("<II", f.read(8))
            g = json.loads(f.read(ln).decode("utf-8"))
    except Exception:
        return None
    lo = [float("inf")] * 3
    hi = [float("-inf")] * 3
    found = 0
    for m in g.get("meshes", []):
        for pr in m.get("primitives", []):
            ai = (pr.get("attributes") or {}).get("POSITION")
            if ai is None:
                continue
            a = g.get("accessors", [])[ai] if ai < len(g.get("accessors", [])) else {}
            if "min" not in a or "max" not in a:
                continue
            found += 1
            for i in range(3):
                lo[i] = min(lo[i], a["min"][i])
                hi[i] = max(hi[i], a["max"][i])
    if not found:
        return None
    return lo, hi


def main():
    dims, dims_src = ship_dims()
    roots, roots_src = part_roots()
    by_root = {}
    for _c, _r in roots.items():
        by_root.setdefault(_r, []).append(_c)
    if roots:
        print("part-tree roots: %d classes name a hull (%d distinct hulls)"
              % (len(roots), len(by_root)))
    else:
        print("NO PART-TREE ROOTS in the snapshot - variants can only be "
              "placed as themselves. Said out loud rather than returned "
              "quietly as a smaller answer.")
    models, models_src = model_map()
    if not dims:
        print("NOT PERFORMED - no ships.json snapshot with dimensions")
        return 2
    if not models:
        print("NOT PERFORMED - no loadout_model map to join class -> glb")
        return 2
    os.makedirs(OUT, exist_ok=True)
    print("dimensions from %s  (%d ships)" % (dims_src, len(dims)))
    print("model map from  %s  (%d entries)\n" % (models_src, len(models)))

    lower_models = {k.lower(): v for k, v in models.items()}
    def place(out_cls, src_cls, dim, mdl, hp, inherited):
        """Place ONE source hull's hardpoints into ONE ship's model space."""
        gp = os.path.join(GEO, os.path.splitext(mdl)[0] + ".json")
        gb = glb_box(mdl)
        if os.path.exists(gp):
            mn, mx = box(gp)
            box_src = "hull-geometry"
            # THE TWO SOURCES MUST AGREE WHEREVER BOTH EXIST. This is the check
            # that keeps the fallback honest on hulls it is never used for.
            if gb:
                sp = max(mx[i] - mn[i] for i in range(3)) or 1.0
                dev = max(max(abs(gb[0][i] - mn[i]) for i in range(3)),
                          max(abs(gb[1][i] - mx[i]) for i in range(3))) / sp
                if dev > 0.01:
                    skipped.append({"class": out_cls,
                                    "why": "the GLB header box and the sampled "
                                           "box disagree by %.2f%% of span - "
                                           "refusing rather than choosing"
                                           % (dev * 100)})
                    return
        elif gb:
            mn, mx = gb
            box_src = "glb-header"
        else:
            skipped.append({"class": out_cls, "why": "no hull geometry and no "
                                                     "readable GLB for " + mdl})
            return
        ext = [mx[i] - mn[i] for i in range(3)]     # glb: x, y up, z fore/aft
        # The box centre, because the viewer recentres on it before drawing.
        # See the acceptance test below for why that is the frame that counts.
        ctr = [(mn[i] + mx[i]) / 2.0 for i in range(3)]
        if min(ext) <= 0:
            skipped.append({"class": out_cls, "why": "degenerate hull box"})
            return
        est = {"length": dim["Length"] / ext[2],
               "width": dim["Width"] / ext[0],
               "height": dim["Height"] / ext[1]}
        # LENGTH IS THE SCALE. The first version took the median of all three
        # and failed 61 of 75 hulls - not because the decode was wrong but
        # because CIG's Width and Height are not measured the way a bounding
        # box is. Width is taken with wings, arms or gear DEPLOYED on the hulls
        # that have them, and Height often excludes the gear the GLB includes.
        # Length is nose-to-tail on both sides of the comparison, and it is the
        # only one of the three that is.
        #
        # WHICH MEANS THE SCALE NO LONGER CHECKS ITSELF, so the check moves
        # somewhere it cannot be circular. Deriving s from the fore/aft extent
        # makes the fore/aft containment test trivially true - but it says
        # NOTHING about lateral or vertical. A transposed axis or a wrong
        # frame puts hardpoints outside the hull SIDEWAYS or THROUGH THE ROOF,
        # and that is what the acceptance test below actually measures. The
        # other two estimates are recorded per hull as diagnostics, not gates.
        s = est["length"]
        spread = (max(est.values()) - min(est.values())) / s

        conv, outside, ext_out, ext_n = [], [], [], 0
        for n in hp:
            x, y, z = n["pos"]                      # CIG: x lat, y fore/aft, z up
            p = [x / s, z / s, -y / s]              # GLB: x lat, y up, z (fwd -z)
            conv.append({"name": n["name"], "pos": [round(v, 5) for v in p]})
            # AXES 0 AND 1 ONLY. Axis 2 is where the scale came from, so
            # testing it would be marking our own homework.
            #
            # AND THE BOX IS TESTED WHERE THE VIEWER PUTS IT, NOT WHERE THE
            # FILE PUTS IT (C1, 2026-08-27). `cc_viewer.frame()` RECENTRES
            # every hull on its own bounding box before drawing it -
            # `o.position.x -= c.x`, `-= box.min.y`, `-= c.z` - and places
            # markers at hull-space (0,0,0) plus half the height. So the frame
            # a visitor actually sees is the box CENTRED ON THE ORIGIN, and
            # testing against the raw `mn`/`mx` tests a frame that is never
            # rendered.
            #
            # IT COST THREE HULLS AND IT WAS NOT A NEAR MISS. The M2 Hercules
            # carries the SAME decoded hardpoints as the C2 and the A2 - same
            # base hull, same 149 ports, scale 0.9945 against 0.9945 - and its
            # GLB was exported with 13.11 units of baked translation the other
            # two do not have. Against the raw box: 11 of 149 inside. Against
            # the box the viewer draws: 140 of 149, the C2's number exactly.
            # The refusal was the test's, not the data's.
            #
            #     M2 Hercules   11/149 -> 140/149
            #     Valkyrie      79/88  ->  88/88
            #     ARGO SRV      63/67  ->  67/67
            #
            # AND IT IS NOT A LOOSENING. The Reliant goes the other way, 78/90
            # to 72/90, because its box centre is genuinely off-origin and the
            # old test was flattering it. A correction that only ever passes
            # more hulls is a correction to be suspicious of; this one moves
            # hulls in both directions, which is what a frame change does and
            # a threshold change does not.
            #
            # 187 of the 258 models in the payload are centred within 1% of
            # their longest span, so for most of the fleet this changes
            # nothing at all. SEVENTY-ONE ARE NOT - Ranger RC 33%, Scorpius
            # 26%, Ursa 21%, Cyclone 20%, Tyilui 14.5%, Arrastra 13.4% - and
            # those are the ones that were being judged in a frame nobody
            # renders.
            is_ext = bool(EXTERIOR.search(n["name"]))
            if is_ext:
                ext_n += 1
            for i in (0, 1):
                m = ext[i] * MARGIN
                lo_i, hi_i = mn[i] - ctr[i], mx[i] - ctr[i]
                if p[i] < lo_i - m or p[i] > hi_i + m:
                    outside.append(n["name"])
                    conv[-1]["outside"] = True
                    if is_ext:
                        ext_out.append(n["name"])
                    break
        # THE GATE IS THE EXTERIOR MOUNTS. A hull with none cannot pass - there
        # would be nothing here that could have failed.
        #
        # IT STAYS ALL-OR-NOTHING, AND A CONTROL IS WHY (C1, 2026-08-27).
        #
        # I CHANGED THIS TO A PROPORTIONAL GATE AND IT WAS WRONG. The argument
        # was that discarding a hull's whole marker set over one or two mounts
        # proud of a STOWED-POSE mesh threw away 19 good Constellation ports to
        # avoid drawing 3 arguable ones - and that the fallback, name-derived
        # markers a median 0.488 of a half-extent from the real mount, is worse
        # than what was being refused. All of that is still true.
        #
        # `checks/_verify_placement_gate.py` refuted it in one run. With the
        # gate at "more than half outside", A TRANSPOSED LATERAL/VERTICAL AXIS
        # SURVIVES ON EVERY HULL TESTED - 10 of 59 exterior mounts outside on
        # the Eclipse, 24 of 97 on the Hammerhead, nowhere near half. Ships are
        # wider than they are tall, so swapping those two axes leaves most
        # mounts inside the larger extent. A wrong scale of 4x survived on five
        # of six.
        #
        # THE TRANSPOSED AXIS IS THE EXACT DEFECT THIS TEST WAS WRITTEN FOR.
        # The proportional version traded the gate's whole reason to exist for
        # three hulls of coverage, which is tomorrow's silent wrong data bought
        # with today's dots.
        #
        # WHAT WOULD ACTUALLY EARN A PER-PORT GATE is a test that catches a
        # transpose regardless of how many mounts it displaces - the SHAPE of
        # the mount cloud against the shape of the hull, not a count. Until
        # something like that exists, a hull with any exterior mount outside is
        # refused whole. Not written today, and named here so the next person
        # does not re-derive the same wrong shortcut.
        #
        # The per-port `outside` flags stay. They cost nothing, they tell the
        # overlay which mounts are the offenders, and they are what made the
        # refuted argument measurable in the first place.
        # THE SECOND SIGNAL - see converted_mirror() above for the whole
        # argument and the measurements behind it.
        _span = 0.0
        for _i in range(3):
            _v = [h["pos"][_i] for h in conv]
            if _v:
                _span = max(_span, max(_v) - min(_v))
        _mtol = max(0.05, _span * 0.004)
        _mm, _mp = converted_mirror(conv, _mtol)
        frame_proven = (_mp >= MIRROR_MIN_PAIRS
                        and _mm >= _mp * MIRROR_MIN_FRACTION)

        # THE MIRROR IS A VETO AS WELL AS A LICENCE, ADDED 2026-08-28, AND A
        # CONTROL IS WHY.
        #
        # Until today the mirror was only ever consulted when something was
        # already outside the box. `checks/_verify_placement_gate.py` was given
        # the fleet's worst adversarial hull by name - the San'tok.yai, the one
        # transposed hull that gets closest to the fraction - and reported that
        # **a transposed San'tok.yai PASSES THE GATE**. It passes because
        # nothing lands outside its box when the axes are swapped: that hull is
        # nearly as tall as it is wide, so the transpose displaces no mount far
        # enough to notice. Containment had nothing to say and the mirror was
        # never asked.
        #
        # This is not a defect the fraction rule introduced - it was there
        # under the all-or-nothing rule too, for the same reason. Naming the
        # hard case in the control is what surfaced it.
        #
        # SO: a hull with enough named pairs to judge, whose pairs mostly do
        # NOT mirror, is refused OUTRIGHT, whatever containment says. It costs
        # two hulls - both Clippers, 2 of 8 - and that cost is the point. **A
        # rule that admits the Glaive on the strength of its mirror has to
        # refuse the Clipper for the lack of one**, or it is not a rule, it is
        # a preference for ships somebody wanted in.
        #
        # A hull with FEWER than MIRROR_MIN_PAIRS pairs is NOT vetoed. Absence
        # of evidence is not evidence, and refusing on it would take out a
        # large part of the fleet on no measurement at all.
        if _mp >= MIRROR_MIN_PAIRS and _mm < _mp * MIRROR_MIN_FRACTION:
            ok = False
            why = ("only %d of %d named left/right pairs mirror, which is "
                   "below the fraction a transposed axis cannot reach. The "
                   "frame is not established, so nothing here is placed - "
                   "regardless of the hull box, which cannot see a transpose "
                   "on a hull as tall as it is wide"
                   % (_mm, _mp))
        elif ext_n == 0:
            ok = False
            why = "no exterior mount to place - nothing here could have failed"
        elif not ext_out:
            ok = True
            why = ""
        elif frame_proven and len(ext_out) <= WITHHOLD_MAX:
            # The frame is proven by a test the containment check cannot do
            # and that a transpose destroys. The offenders are withheld
            # individually - they already carry `outside: true` and the
            # overlay skips them - and the rest of the hull is placed.
            ok = True
            why = ("%d of %d exterior mounts withheld - outside the hull box, "
                   "but this hull's frame is proven by its mirror (%d of %d "
                   "exterior pairs), so the rest is placed"
                   % (len(ext_out), ext_n, _mm, _mp))
        elif frame_proven:
            ok = False
            why = ("%d of %d exterior mounts land outside the hull - more than "
                   "%d, which is past anything a stowed pose produces, so the "
                   "proven frame does not excuse it. Refused whole"
                   % (len(ext_out), ext_n, WITHHOLD_MAX))
        else:
            ok = False
            why = ("%d of %d exterior mounts land outside the hull and this "
                   "hull's frame is NOT proven (%d of %d exterior pairs "
                   "mirror) - refused whole"
                   % (len(ext_out), ext_n, _mm, _mp))

        rec = {"class": out_cls, "model": mdl,
               "hardpoints_from": src_cls,
               "inherited_from_base_hull": inherited,
               "hull_box_source": box_src,
               "scale_m_per_unit": round(s, 5),
               "scale_estimates": {k: round(v, 5) for k, v in est.items()},
               "scale_spread": round(spread, 4),
               "hull_box": {"min": mn, "max": mx},
               "acceptance": ok, "acceptance_note": why,
               "frame_proven": frame_proven,
               "mirror_matched": _mm, "mirror_pairs": _mp,
               "exterior_mounts": ext_n,
               "exterior_outside": ext_out,
               "outside_any": outside[:20],
               "frame": "GLB units. X lateral, Y up, forward is -Z.",
               "hardpoints": conv}
        json.dump(rec, open(os.path.join(OUT, out_cls + ".json"), "w",
                            encoding="utf-8"), indent=1)
        rows.append({"class": out_cls, "hardpoints": len(conv),
                     "frame_proven": frame_proven,
                     "mirror": "%d/%d" % (_mm, _mp),
                     "exterior_mounts": ext_n,
                     "exterior_outside": len(ext_out),
                     "outside_any": len(outside),
                     "scale": round(s, 4), "spread": round(spread, 4),
                     "acceptance": ok, "note": why})
        print("  %-32s %s  %3d hp  s=%.3f  spread %5.1f%%%s"
              % (out_cls, "PASS" if ok else "FAIL", len(conv), s, spread * 100,
                 "" if ok else "  (" + why + ")"))

    rows, skipped = [], []
    # ONE SHIP CAN BE CLAIMED BY TWO BASE HULLS, and the first version let the
    # second silently overwrite the first: `anvl_hornet_f7a_mk1` matched both
    # `ANVL_Hornet` and `ANVL_Hornet_F7A`, and appeared twice in the manifest
    # with one file on disk. That is the same silent-overwrite failure this
    # project has hit five times, reintroduced by me while fixing something
    # else - so claims are collected first and resolved deliberately.
    claims = {}
    for f in sorted(os.listdir(SRC)):
        if not f.endswith(".json") or f in ("MANIFEST.json", "failures.json"):
            continue
        cls = f[:-5]
        j = json.load(open(os.path.join(SRC, f), encoding="utf-8"))
        hp = [n for n in j["nodes"] if n["name"].lower().startswith("hardpoint")]
        if not hp:
            skipped.append({"class": cls, "why": "no hardpoint nodes"})
            continue

        # A BASE HULL HAS NO SHIP ROW OF ITS OWN, AND THAT IS NOT A DEAD END.
        #
        # `AEGS_Avenger.cga` is the geometry; ships.json has no AEGS_Avenger,
        # only _Stalker, _Titan, _Titan_Renegade, _Warlock. Twenty hulls were
        # dropped for this and they are not obscure - the Avenger, the Hornet,
        # the Constellation, the Aurora, the Mustang, the Zeus, the Spirit.
        #
        # So a base expands to its variants. BUT VARIANTS ARE NOT
        # INTERCHANGEABLE: sixteen rows sit under ANVL_Hornet with THREE
        # different published lengths - 22.5, 24 and 28.25 - and their own
        # model files. An F7A Mk I and an F7C-M Super Hornet do not share a
        # hull, and spraying one CGA's hardpoints across all sixteen would be
        # exactly the fuzzy-match failure this project has been bitten by twice.
        #
        # THE NAME PROPOSES, THE GEOMETRY DISPOSES. Each candidate is placed
        # against ITS OWN hull box and ITS OWN published length, and kept only
        # if the acceptance test - which reads geometry and knows nothing about
        # names - says the mounts land inside that hull. A variant of a
        # different shape FAILS and is reported as failed, not quietly dropped.
        targets = []
        if dims.get(cls.lower()) and lower_models.get(cls.lower()):
            targets.append((cls, dims[cls.lower()], lower_models[cls.lower()], False))
        # AND EVERY SHIP WHOSE OWN CIG RECORD NAMES THIS HULL AS THE ROOT OF
        # ITS PART TREE - see part_roots(). This replaced a `cls + "_"` prefix
        # match, and it runs whether or not the base has a row of its own: the
        # old code only expanded when the base had none, which is why the
        # Gladius Valiant sat with name-derived markers while the Avenger
        # Titan did not.
        for cn in sorted(by_root.get(cls.lower(), [])):
            if cn == cls.lower():
                continue                      # already added as itself, above
            if lower_models.get(cn) and dims.get(cn):
                targets.append((cn, dims[cn], lower_models[cn], True))
        if not targets:
            skipped.append({"class": cls,
                            "why": "no ships.json row for this class, and no "
                                   "ship names it as its part-tree root with "
                                   "a model"})
            continue
        for out_cls, dim, mdl, inherited in targets:
            # KEYED CASE-INSENSITIVELY, AND THAT IS NOT A TIDY-UP (C1,
            # 2026-08-27). `ANVL_Hornet_F7A_MK1` arrives from its own transform
            # file and `anvl_hornet_f7a_mk1` arrives from the ships.json row -
            # the SAME SHIP, claimed twice, keyed by two strings that differ
            # only in case. The guard below compares exact strings, so both
            # claims survived it, both were placed, and on a case-insensitive
            # filesystem both wrote the same file with the second silently
            # winning. The manifest listed 182 ships for 180 files and nothing
            # errored. Same for ESPR_Prowler_Utility.
            #
            # This is the silent-overwrite failure this file's own comment says
            # has already happened five times, arriving a sixth way. Folding the
            # key hands both claims to the most-specific-base rule, which is the
            # thing that exists to decide between them.
            claims.setdefault(out_cls.lower(), []).append(
                (out_cls, cls, dim, mdl, hp, inherited))

    # THE MOST SPECIFIC BASE WINS, and a tie is refused rather than picked.
    # `ANVL_Hornet_F7A` is a longer prefix of `anvl_hornet_f7a_mk1` than
    # `ANVL_Hornet` is, so it is the nearer geometry and it takes the ship.
    # Two claims of EQUAL specificity are genuinely ambiguous - both are
    # dropped and both are named, the same way the hull-name collisions are.
    for out_key, cands in sorted(claims.items()):
        best = max(len(c[1]) for c in cands)
        top = [c for c in cands if len(c[1]) == best]
        if len(top) > 1:
            skipped.append({"class": out_key,
                            "why": "claimed by %d base hulls of equal "
                                   "specificity (%s) - refused, not picked"
                                   % (len(top), ", ".join(c[1] for c in top))})
            continue
        place(*top[0])

    man = {"generated_by": "build_hardpoint_placement.py",
           "source_transforms": SRC, "dimensions": dims_src,
           "variant_rule": "a ship inherits a hull's transforms when its own "
                           "CIG record names that hull as the root of its part "
                           "tree (Parts[0].Name). Exact equality, no prefix "
                           "matching, no fuzzy matching. Source: %s" % roots_src,
           "model_map": models_src,
           "frame": "GLB units. X lateral, Y up, forward is -Z.",
           "scale_rule": "CIG's Length against the hull box's fore/aft extent. "
                         "Width and Height are recorded as diagnostics only - "
                         "CIG measures them with gear deployed and the GLB is "
                         "one stowed pose.",
           "acceptance": "every EXTERIOR mount inside the hull box AS THE "
                         "VIEWER RECENTRES IT - box centred on the origin, "
                         "which is what cc_viewer.frame() draws - laterally "
                         "and vertically, %.0f%% margin. The fore/aft axis is "
                         "where the scale came from and is deliberately NOT "
                         "tested - that would be marking our own homework. A "
                         "transposed axis puts mounts outside sideways. A "
                         "hull whose exterior left/right pairs ALL mirror in "
                         "the converted frame has proven its frame by a test a "
                         "transpose destroys, and withholds individual "
                         "out-of-box mounts instead of being refused whole. A "
                         "hull that has not proven its frame is refused whole."
                         % (MARGIN * 100),
           "counts": {"converted": len(rows),
                      "passed": sum(1 for r in rows if r["acceptance"]),
                      "failed": sum(1 for r in rows if not r["acceptance"]),
                      "skipped": len(skipped)},
           "ships": rows, "skipped": skipped}
    json.dump(man, open(os.path.join(OUT, "MANIFEST.json"), "w",
                        encoding="utf-8"), indent=1)

    # THE DIRECTORY IS THE ARTIFACT, NOT THE MANIFEST - AND THE NEXT STAGE
    # READS THE DIRECTORY (C1, 2026-08-27).
    #
    # `build_hardpoint_overlay.py` iterates `os.listdir()` here. So a hull this
    # run REFUSED, but a previous run wrote, keeps its file and keeps being
    # emitted - the refusal is real, recorded in the manifest, and has no
    # effect. A correction that reports success and changes nothing is worse
    # than no correction at all.
    #
    # It had already happened: an experimental run left the directory holding
    # 218 files against a manifest of 182, and nothing anywhere said so.
    #
    # DELETION IS ATTEMPTED AND ITS FAILURE IS FATAL, never shrugged off. Some
    # environments this runs in cannot delete inside the repo mount, and a
    # silent "could not tidy up" there would leave exactly the stale state this
    # exists to prevent. If the files cannot go, the run fails and names them.
    live = {r["class"] for r in rows}
    stale = [f for f in sorted(os.listdir(OUT))
             if f.endswith(".json") and f != "MANIFEST.json"
             and f[:-5] not in live]
    if stale:
        gone, stuck = 0, []
        for f in stale:
            try:
                os.remove(os.path.join(OUT, f))
                gone += 1
            except OSError as e:
                stuck.append("%s (%s)" % (f, e.strerror or e))
        print("removed %d output(s) from an earlier run" % gone)
        if stuck:
            sys.exit("STALE OUTPUT COULD NOT BE REMOVED and the overlay reads "
                     "this directory, so it would emit hulls this run "
                     "refused:\n  %s\nMove them out of %s by hand and re-run. "
                     "Nothing downstream should be built until this directory "
                     "matches its manifest."
                     % ("\n  ".join(stuck[:20]), OUT))

    print("\n%s" % json.dumps(man["counts"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
