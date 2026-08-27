#!/usr/bin/env python3
"""
Emit the real hardpoint positions as an ALIGNMENT OVERLAY.

WHY AN OVERLAY AND NOT A NEW PIPELINE. `build_holo_data.py` already reads
`data-layer/derived/holo-hardpoints-align/alignment_overlay.json` and replaces
a port's position with what it finds there - and it **sys.exits if any overlay
entry matches nothing**, because "an overlay that silently matches nothing
reports a fix it did not make". That is exactly the injection point this work
needs, already built and already refusing to lie. Nothing in the build changes.

THE JOIN IS AN EXACT STRING EQUALITY AND THAT IS THE WHOLE TRICK.
`ships.json` gives every port a `HardpointName`, and it is the SAME STRING as
the node name in CIG's own geometry:

    HardpointName        hardpoint_weapon_nose_left
    .cga node name       hardpoint_weapon_nose_left

So the port a reader clicks and the transform the game uses to place the gun
are joined on CIG's own identifier. No fuzzy matching, no name similarity, no
vocabulary translation.

ONLY WHAT CAN BE CHECKED IS EMITTED:
  - only hulls whose placement passed its own acceptance test
  - only ports the fleet record already carries, so the overlay's own
    match-or-die guard has nothing to trip on
  - `was` records the position being replaced, so the change is auditable and
    the size of it is measurable rather than asserted

Output: data-layer/derived/holo-hardpoints-align/alignment_overlay_client.json
        (written BESIDE the hand-made overlay, never over it)
"""
import json
import math
import os
import re
import statistics
import sys

FLEET = os.path.join("data-layer", "derived", "holo-hardpoints",
                     "hardpoints_fleet.json")
PLACE = os.path.join("data-layer", "derived", "hardpoint-placement")
ALIGN = os.path.join("data-layer", "derived", "holo-hardpoints-align")
OUT = os.path.join(ALIGN, "alignment_overlay_client.json")
MODELS = os.path.join("testing", "_src", "loadout_model.gen.js")


def main():
    if not os.path.exists(FLEET):
        print("NOT PERFORMED - no %s" % FLEET)
        return 2
    fleet = json.load(open(FLEET, encoding="utf-8"))
    M = json.loads(re.search(r"=\s*(\{[\s\S]*?\});",
                             open(MODELS, encoding="utf-8").read()).group(1))
    lm = {k.lower(): v for k, v in M.items()}
    by_model = {}
    for k, r in fleet.items():
        if r.get("model"):
            by_model.setdefault(os.path.splitext(r["model"])[0].lower(), k)

    overlay, report = {}, []
    for f in sorted(os.listdir(PLACE)):
        if not f.endswith(".json") or f == "MANIFEST.json":
            continue
        cls = f[:-5]
        j = json.load(open(os.path.join(PLACE, f), encoding="utf-8"))
        if not j.get("acceptance"):
            report.append({"class": cls, "emitted": 0,
                           "why": "placement did not pass: " + j.get("acceptance_note", "")})
            continue
        mdl = lm.get(cls.lower())
        key = by_model.get(os.path.splitext(mdl)[0].lower()) if mdl else None
        if not key:
            report.append({"class": cls, "emitted": 0,
                           "why": "no fleet record for this hull"})
            continue

        mn, mx = j["hull_box"]["min"], j["hull_box"]["max"]
        # THE SAME DEFINITION THE BUILD USES: normalised to the hull's longest
        # HALF-extent. Taken from build_holo_data.py's own header rather than
        # re-invented.
        H = max((mx[i] - mn[i]) / 2.0 for i in range(3))
        if H <= 0:
            continue
        ours = {h["name"]: [c / H for c in h["pos"]] for h in j["hardpoints"]}

        rec = fleet[key]
        theirs = {h["port"]: h for h in rec.get("hardpoints") or []}

        # pos_model IS NOT IN THE SAME UNITS ON EVERY HULL - the marker file's
        # own comment puts the fleet's spread at 10,000x in model units per
        # metre. So the scale back out of unit-space is taken from THIS HULL'S
        # OWN existing pair, never from a constant. A hull that offers no pair
        # to derive it from emits no pos_model rather than a guessed one.
        ratios = []
        for p, h in theirs.items():
            u, pm = h.get("unit"), h.get("pos_model")
            if not (u and pm):
                continue
            for i in range(3):
                if abs(u[i]) > 0.05:
                    ratios.append(pm[i] / u[i])
        Hm = statistics.median(ratios) if ratios else None

        ports, moved = {}, []
        for name, u in ours.items():
            h = theirs.get(name)
            if h is None or not h.get("unit"):
                continue                      # not a port this ship exposes
            was = h["unit"]
            entry = {"unit": [round(v, 5) for v in u], "was": was}
            if Hm is not None:
                entry["pos_model"] = [round(v * Hm, 3) for v in u]
            ports[name] = entry
            moved.append(math.dist(u, was))
        if not ports:
            report.append({"class": cls, "emitted": 0,
                           "why": "no port name shared with the fleet record"})
            continue
        overlay[key] = ports
        report.append({"class": cls, "fleet_key": key, "emitted": len(ports),
                       "median_move": round(statistics.median(moved), 4),
                       "max_move": round(max(moved), 4),
                       "pos_model": Hm is not None})

    os.makedirs(ALIGN, exist_ok=True)
    json.dump(overlay, open(OUT, "w", encoding="utf-8"), indent=1)
    man = {
        "generated_by": "build_hardpoint_overlay.py",
        "finding": "docs/FINDING_the-coordinates-are-in-the-client-2026-08-27.md",
        "join": "exact equality between ships.json HardpointName and the .cga "
                "node name. No fuzzy matching.",
        "units": "unit = normalised to the hull's longest HALF-extent, the same "
                 "definition build_holo_data.py uses. pos_model is scaled back "
                 "out using THIS hull's own existing unit/pos_model pair.",
        "not_applied": "This file is written BESIDE alignment_overlay.json and "
                       "nothing reads it yet. Wiring it in is a separate, "
                       "reversible step.",
        "counts": {"hulls": len(overlay),
                   "ports": sum(len(v) for v in overlay.values())},
        "hulls": report,
    }
    json.dump(man, open(os.path.join(ALIGN, "MANIFEST_client_overlay.json"),
                        "w", encoding="utf-8"), indent=1)
    em = [r for r in report if r.get("emitted")]
    print("hulls with real positions: %d" % len(overlay))
    print("ports replaced:            %d" % man["counts"]["ports"])
    if em:
        meds = [r["median_move"] for r in em]
        print("median move, normalised:   %.3f  (1.0 = the hull's longest half-extent)"
              % statistics.median(meds))
        print("\nlargest corrections:")
        for r in sorted(em, key=lambda r: -r["median_move"])[:10]:
            print("  %-28s %3d ports  median %.3f  worst %.3f"
                  % (r["class"], r["emitted"], r["median_move"], r["max_move"]))
    skipped = [r for r in report if not r.get("emitted")]
    print("\nnot emitted: %d hulls" % len(skipped))
    import collections
    for w, c in collections.Counter(
            r["why"].split(":")[0] for r in skipped).most_common():
        print("  %-44s %d" % (w, c))
    print("\nwrote %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
