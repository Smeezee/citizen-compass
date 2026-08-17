#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_hardpoint_alignment.py - the same hull, in the same place, on every page.

    ordered by  Sleven, 2026-08-16: "run the alignment overlay across all 31 pairs"
    finding     docs/FINDING_hardpoint-name-join-2026-08-16.md
    ruling      DECISION_shared-hulls-are-fine-unless-the-shape-differs

WHAT THIS FIXES
===============

Ships that share an identical set of hardpoint ports are the same hull, and the
ruling says the same hull has its hardpoints in the same places. The deployed
data does not agree with itself about that. Measured across the 196 ships now in
the viewer, in 19 groups the members disagree by more than 0.15 in unit space:

    1.569  A2 / C2 / M2 Hercules          (mine)
    1.484  Glaive vs Vanduul Scythe       (C3's)
    1.421  Vanguard Harbinger / Hoplite / Warden - median 0.948, the whole set
    0.951  MISC Reliant Kore / Mako / Sen / Tana
    0.847  MISC Freelancer vs Freelancer MAX

1.0 in unit space is a hull half-length. A visitor flipping between a Harbinger
and a Warden sees the same hull with its guns somewhere else, and neither page
admits it.

THE CAUSE IS NOT A BUG IN EITHER RUN. A wing or a flat spine is a large surface,
so "snap to the nearest vertex" is badly under-determined ALONG it: two meshes a
few per cent apart send the same target a long way apart. It is inherent to the
rule, it is in C3's original batch and in my recovered ships equally, and no
rerun changes it - re-placing the Gladius Valiant from scratch reproduced its
stored positions to 0.114.

HOW A GROUP DECIDES WHERE ITS MARKERS GO
========================================

By CONSENSUS, not by seniority. The reference is the group's MEDOID - the member
whose placement is closest to all the others. Picking the first alphabetically,
or the "base" ship, would be an arbitrary choice dressed as a principle; the
medoid is the placement the group already mostly agrees on.

Every other member is then aligned to it, and NEVER by copying coordinates: the
medoid's position is a TARGET which is re-snapped to that ship's own vertices.
Meshes differ by several per cent, so a copied position can float off the hull,
and a marker in mid-air is a worse defect than the one being fixed.

WHAT IT WILL NOT DO
===================

  - It does not touch a group that already agrees within 0.15. 54 of the 73
    same-port-set pairs are in that state and are left exactly alone. That
    includes the Gladius Pirate and Valiant, whose placement Sleven checked
    against RSI's own art and confirmed.
  - It does not rewrite hardpoints_fleet.json. That file has one writer,
    place_fleet.py. This is an OVERLAY, applied by build_holo_data.py at read
    time, and every moved marker is listed with where it was and where it went.
  - It does not move a marker it cannot re-snap. A ship whose geometry is not
    decoded is reported, not guessed at.

Rule 15: encodings stated.
"""

import io
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FLEET = os.path.join(HERE, "data-layer", "derived", "holo-hardpoints",
                     "hardpoints_fleet.json")
JOIN = os.path.join(HERE, "data-layer", "derived", "holo-hardpoints-join",
                    "hardpoints_join.json")
OUTDIR = os.path.join(HERE, "data-layer", "derived", "holo-hardpoints-align")
OUT = os.path.join(OUTDIR, "alignment_overlay.json")
REPORT = os.path.join(OUTDIR, "alignment_report.json")
MANIFEST = os.path.join(OUTDIR, "MANIFEST.json")

GEO = os.environ.get("CC_GEO_DIR", "")

# A group is left alone below this. 0.15 in unit space is 7.5% of the hull's
# longest dimension - about a marker's own width on screen. Above it the
# difference is visible as "the same ship with its guns somewhere else".
TOLERANCE = 0.15

sys.path.insert(0, HERE)
from build_hardpoint_join import (  # noqa: E402
    from_unit, push_out, to_unit, dist2, hull_matches,
)


def say(line):
    sys.stdout.buffer.write((line + "\n").encode("utf-8", "backslashreplace"))


def read_json(path, what):
    if not os.path.exists(path):
        sys.exit("MISSING INPUT: %s\n(%s)\nNothing was written." % (path, what))
    with io.open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def unit_dist(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def worst_between(a_hps, b_hps):
    by = {h["port"]: h for h in b_hps}
    ds = [unit_dist(h["unit"], by[h["port"]]["unit"])
          for h in a_hps if h["port"] in by]
    return max(ds) if ds else 0.0


def median_between(a_hps, b_hps):
    by = {h["port"]: h for h in b_hps}
    ds = sorted(unit_dist(h["unit"], by[h["port"]]["unit"])
                for h in a_hps if h["port"] in by)
    return ds[len(ds) // 2] if ds else 0.0


def main():
    if not GEO or not os.path.isdir(GEO):
        sys.exit("SET CC_GEO_DIR to the folder written by\n"
                 "  node testing/_src/decode_glb_points.js <dir> <models...>\n"
                 "Nothing was written. Without vertices a marker cannot be "
                 "re-snapped, and an overlay that copied coordinates blind is "
                 "exactly what this refuses to be.")

    fleet = read_json(FLEET, "the hardpoints placed by place_fleet.py")
    join = read_json(JOIN, "the hardpoints recovered by build_hardpoint_join.py")

    ships = {}
    for src, data in (("fleet", fleet), ("join", join)):
        for k, v in data.items():
            if v.get("hardpoints"):
                ships[k] = {"src": src, "rec": v}

    def geo_for(key):
        model = ships[key]["rec"].get("model") or ""
        p = os.path.join(GEO, model[:-4] + ".json") if model else ""
        return read_json(p, "geometry for " + key) if p and os.path.exists(p) else None

    # SHARING A PORT LIST IS NOT SHARING A HULL, and that turned out to be the
    # whole story.
    #
    # The first version of this grouped ships by port set alone and tried to
    # align every group. It refused 15 of 26 candidates because the reference
    # position landed nowhere near the other ship's surface - which is not a
    # snapping problem, it is those two ships not being the same shape:
    #
    #     MISC Reliant Kore vs Mako      bounding boxes differ by 53.9%
    #     L-21 Wolf vs L-22 Alpha Wolf   28.2%
    #     Cyclone MT vs TR               25.8%
    #     MISC Freelancer vs MAX         20.7%
    #     Glaive vs Vanduul Scythe       18.7%
    #     A2 Hercules vs C2/M2           11.8%
    #     Vanguard Harbinger vs Hoplite  12.4%
    #
    # Those ships carry the same port NAMES on different hulls, so their markers
    # SHOULD sit in different places and the disagreement was never an error.
    # Sleven's own ruling says it in the title: shared hulls are fine unless the
    # shape differs.
    #
    # So each port-set group is split into MESH-IDENTICAL clusters first - the
    # same 2% bounding-box bar the join uses to tell a Gladius from a Hammerhead
    # - and alignment happens only inside a cluster.
    groups = {}
    for k, s in ships.items():
        groups.setdefault(frozenset(h["port"] for h in s["rec"]["hardpoints"]), []).append(k)

    overlay, report = {}, {"aligned": [], "left_alone": [], "no_geometry": [],
                           "refused": [], "different_hulls": []}

    clusters = []
    for members in sorted(groups.values(), key=lambda m: sorted(m)):
        if len(members) < 2:
            continue
        gs = {k: geo_for(k) for k in sorted(members)}
        pending = [k for k in sorted(members)]
        found = []
        while pending:
            head = pending.pop(0)
            same = [head]
            rest = []
            for k in pending:
                if gs[head] is not None and gs[k] is not None \
                        and hull_matches(gs[head], gs[k])[0]:
                    same.append(k)
                else:
                    rest.append(k)
            pending = rest
            found.append(same)
        if len(found) > 1:
            report["different_hulls"].append([sorted(members),
                                              [sorted(c) for c in found]])
        for c in found:
            if len(c) > 1:
                clusters.append(sorted(c))

    for members in clusters:
        hps = {k: ships[k]["rec"]["hardpoints"] for k in members}
        spread = max(worst_between(hps[a], hps[b])
                     for i, a in enumerate(members) for b in members[i + 1:])
        if spread <= TOLERANCE:
            report["left_alone"].append([members, round(spread, 3)])
            continue

        # THE MEDOID. The member closest to all the others, by median marker
        # distance - median rather than worst, so one badly-snapped marker does
        # not decide which placement the whole group adopts.
        def cost(k):
            return sum(median_between(hps[k], hps[o]) for o in members if o != k)
        ref = min(members, key=cost)
        ref_by = {h["port"]: h for h in hps[ref]}

        for k in members:
            if k == ref:
                continue
            d = worst_between(hps[k], hps[ref])
            if d <= TOLERANCE:
                report["left_alone"].append([[k, ref], round(d, 3)])
                continue
            g = geo_for(k)
            if g is None:
                report["no_geometry"].append([k, ref, round(d, 3)])
                continue

            pts, mn, mx = g["pts"], g["min"], g["max"]
            n = len(pts) // 3
            size = math.sqrt(sum((mx[i] - mn[i]) ** 2 for i in range(3)))
            moved, worst_move, worst_off = {}, 0.0, 0.0
            for h in hps[k]:
                want = ref_by.get(h["port"])
                if not want:
                    continue
                tgt = from_unit(want["unit"], mn, mx)
                bi, bd = -1, None
                for i in range(n):
                    dd = dist2(pts, i, tgt[0], tgt[1], tgt[2])
                    if bd is None or dd < bd:
                        bd, bi = dd, i
                snapped = [pts[bi * 3], pts[bi * 3 + 1], pts[bi * 3 + 2]]
                newp = push_out(snapped, mn, mx)
                u = to_unit(newp, mn, mx)
                worst_move = max(worst_move, unit_dist(u, h["unit"]))
                # ON THE HULL, MEASURED. push_out lifts 1.2%; anything much
                # beyond that is a marker floating, which is the failure this
                # is meant to prevent rather than introduce.
                # distance from the SNAPPED point to the vertex it snapped to
                # is zero by construction; what is measured is the lift.
                worst_off = max(worst_off, math.sqrt(
                    sum((newp[i] - snapped[i]) ** 2 for i in range(3))) / size * 100)
                moved[h["port"]] = {"unit": u,
                                    "pos_model": [round(float(c), 3) for c in newp],
                                    "was": h["unit"]}
            # The marker IS a vertex of this hull plus the 1.2% lift, so this
            # cannot normally fire. It is here because "it cannot fire" is what
            # was said about several checks in this project that later did.
            if worst_off > 3.0:
                report["refused"].append([k, ref,
                    "a marker ended %.1f%% of hull size from this ship's own "
                    "surface, which should be impossible after snapping to it"
                    % worst_off])
                continue
            overlay[k] = moved
            report["aligned"].append([k, ref, len(moved), round(d, 3),
                                      round(worst_move, 3), round(worst_off, 2)])

    if not os.path.isdir(OUTDIR):
        os.makedirs(OUTDIR)
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(overlay, fh, separators=(",", ":"), ensure_ascii=False, sort_keys=True)
        fh.write("\n")
    with io.open(REPORT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    with io.open(MANIFEST, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({
            "dataset": "holo-hardpoints-align",
            "produced_by": "build_hardpoint_alignment.py",
            "what_this_is": "An OVERLAY of marker positions for ships that share a "
                            "hull with another ship and disagreed with it about "
                            "where the hardpoints are.",
            "why_an_overlay": "hardpoints_fleet.json has one writer, place_fleet.py, "
                              "and hardpoints_join.json has another. This changes "
                              "neither; build_holo_data.py applies it at read time.",
            "reference_choice": "the group medoid - the member closest to all the "
                                "others by median marker distance",
            "tolerance": TOLERANCE,
            "counts": {"ships_moved": len(overlay),
                       "groups_left_alone": len(report["left_alone"]),
                       "refused": len(report["refused"]),
                       "no_geometry": len(report["no_geometry"])},
        }, fh, indent=1, ensure_ascii=False)
        fh.write("\n")

    say("wrote %s" % os.path.relpath(OUT, HERE))
    say("  %d ship(s) aligned, %d group/pair(s) left alone, %d refused, "
        "%d without geometry"
        % (len(overlay), len(report["left_alone"]), len(report["refused"]),
           len(report["no_geometry"])))
    say("")
    say("  %-34s %-26s %5s %7s %7s" % ("ship", "aligned to", "mkrs", "was", "moved"))
    for k, ref, cnt, was, mv, off in sorted(report["aligned"], key=lambda r: -r[3]):
        say("  %-34s %-26s %5d %7.3f %7.3f" % (k[:34], ref[:26], cnt, was, mv))
    for k, ref, d in report["no_geometry"]:
        say("  NO GEOMETRY: %s (would align to %s, %.3f apart)" % (k, ref, d))
    for row in report["refused"]:
        say("  REFUSED: %s -> %s: %s" % tuple(row))
    return 0


if __name__ == "__main__":
    sys.exit(main())
