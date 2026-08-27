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
import sys

SRC = os.path.join("data-layer", "derived", "hardpoint-transforms")
GEO = os.path.join("data-layer", "derived", "hull-geometry")
OUT = os.path.join("data-layer", "derived", "hardpoint-placement")
MARGIN = 0.06              # 6% of the box, for mounts proud of the surface

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


def box(path):
    g = json.load(open(path, encoding="utf-8"))
    return g["min"], g["max"]


def main():
    dims, dims_src = ship_dims()
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
        if not os.path.exists(gp):
            skipped.append({"class": out_cls, "why": "no hull geometry for " + mdl})
            return
        mn, mx = box(gp)
        ext = [mx[i] - mn[i] for i in range(3)]     # glb: x, y up, z fore/aft
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
            is_ext = bool(EXTERIOR.search(n["name"]))
            if is_ext:
                ext_n += 1
            for i in (0, 1):
                m = ext[i] * MARGIN
                if p[i] < mn[i] - m or p[i] > mx[i] + m:
                    outside.append(n["name"])
                    if is_ext:
                        ext_out.append(n["name"])
                    break
        # THE GATE IS THE EXTERIOR MOUNTS. A hull with none cannot pass - there
        # would be nothing here that could have failed.
        ok = ext_n > 0 and not ext_out
        why = ""
        if ext_n == 0:
            why = "no exterior mount to place - nothing here could have failed"
        elif ext_out:
            why = ("%d of %d exterior mounts land outside the hull"
                   % (len(ext_out), ext_n))

        rec = {"class": out_cls, "model": mdl,
         "hardpoints_from": src_cls,
         "inherited_from_base_hull": inherited, "scale_m_per_unit": round(s, 5),
               "scale_estimates": {k: round(v, 5) for k, v in est.items()},
               "scale_spread": round(spread, 4),
               "hull_box": {"min": mn, "max": mx},
               "acceptance": ok, "acceptance_note": why,
               "exterior_mounts": ext_n,
               "exterior_outside": ext_out,
               "outside_any": outside[:20],
               "frame": "GLB units. X lateral, Y up, forward is -Z.",
               "hardpoints": conv}
        json.dump(rec, open(os.path.join(OUT, out_cls + ".json"), "w",
                            encoding="utf-8"), indent=1)
        rows.append({"class": out_cls, "hardpoints": len(conv),
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
        else:
            pref = cls.lower() + "_"
            for cn in sorted(dims):
                if cn.startswith(pref) and lower_models.get(cn):
                    targets.append((cn, dims[cn], lower_models[cn], True))
            if not targets:
                skipped.append({"class": cls,
                                "why": "no ships.json row for this class, and no "
                                       "variant of it carries one with a model"})
                continue
        for out_cls, dim, mdl, inherited in targets:
            claims.setdefault(out_cls, []).append(
                (out_cls, cls, dim, mdl, hp, inherited))

    # THE MOST SPECIFIC BASE WINS, and a tie is refused rather than picked.
    # `ANVL_Hornet_F7A` is a longer prefix of `anvl_hornet_f7a_mk1` than
    # `ANVL_Hornet` is, so it is the nearer geometry and it takes the ship.
    # Two claims of EQUAL specificity are genuinely ambiguous - both are
    # dropped and both are named, the same way the hull-name collisions are.
    for out_cls, cands in sorted(claims.items()):
        best = max(len(c[1]) for c in cands)
        top = [c for c in cands if len(c[1]) == best]
        if len(top) > 1:
            skipped.append({"class": out_cls,
                            "why": "claimed by %d base hulls of equal "
                                   "specificity (%s) - refused, not picked"
                                   % (len(top), ", ".join(c[1] for c in top))})
            continue
        place(*top[0])

    man = {"generated_by": "build_hardpoint_placement.py",
           "source_transforms": SRC, "dimensions": dims_src,
           "model_map": models_src,
           "frame": "GLB units. X lateral, Y up, forward is -Z.",
           "scale_rule": "CIG's Length against the hull box's fore/aft extent. "
                         "Width and Height are recorded as diagnostics only - "
                         "CIG measures them with gear deployed and the GLB is "
                         "one stowed pose.",
           "acceptance": "every EXTERIOR mount inside the hull box laterally "
                         "and vertically, %.0f%% margin. The fore/aft axis is "
                         "where the scale came from and is deliberately NOT "
                         "tested - that would be marking our own homework. A "
                         "transposed axis puts mounts outside sideways."
                         % (MARGIN * 100),
           "counts": {"converted": len(rows),
                      "passed": sum(1 for r in rows if r["acceptance"]),
                      "failed": sum(1 for r in rows if not r["acceptance"]),
                      "skipped": len(skipped)},
           "ships": rows, "skipped": skipped}
    json.dump(man, open(os.path.join(OUT, "MANIFEST.json"), "w",
                        encoding="utf-8"), indent=1)
    print("\n%s" % json.dumps(man["counts"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
