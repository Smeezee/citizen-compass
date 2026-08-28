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
ADDED = os.path.join(ALIGN, "fleet_records_client.json")
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

    overlay, report, added = {}, [], {}
    for f in sorted(os.listdir(PLACE)):
        if not f.endswith(".json") or f == "MANIFEST.json":
            continue
        cls = f[:-5]
        j = json.load(open(os.path.join(PLACE, f), encoding="utf-8"))
        if not j.get("acceptance"):
            report.append({"class": cls, "emitted": 0,
                           "why": "placement did not pass: " + j.get("acceptance_note", "")})
            continue
        # PORTS THE PLACEMENT WITHHELD ARE NOT EMITTED (C1, 2026-08-27).
        # The acceptance gate is proportional now: a hull passes with one or
        # two mounts proud of a stowed-pose mesh, and those individual mounts
        # carry `outside: true`. Emitting them would put a marker where the
        # placement itself says the mount is not, which is worse than leaving
        # the port with no CIG position at all - it would look confirmed.
        # They are counted and named in the report rather than dropped quietly.
        #
        # AND A MOUNT AT EXACTLY (0,0,0) IS NOT A MOUNT (C1, 2026-08-27).
        #
        # A node whose transform is exactly the hull origin, to the last
        # decimal, is a node whose transform was never set - CIG's own identity
        # value - not a gun mounted at the dead centre of the ship. There is no
        # physically mountable exterior port at a hull's origin; the origin is
        # inside the hull.
        #
        # FOUND BY LOOKING, NOT BY THEORY: `Paladin /
        # hardpoint_remoteturret_middle` is a port the ship page DRAWS, and it
        # was being given [0.0, 0.0, 0.0] - a turret marker floating in the
        # middle of the hull, which is exactly the "hardpoints not set up" shape
        # Sleven has reported before.
        #
        #     overlay ports at the origin          27   1 of them drawn today
        #     added-record ports at the origin    318   0 drawn today
        #
        # The 318 are withheld too, even though nothing draws them yet. A record
        # that says "this gun is at the centre of the ship" is wrong data
        # whether or not anything reads it this week.
        #
        # TESTED ON THE VALUE THE PAGE ACTUALLY GETS, WHICH IS THE ROUNDED ONE.
        # My first attempt tested the raw `pos` for exact zero and left eleven
        # ports still sitting at the origin: `unit` is `pos / H0` rounded to 5
        # decimals, so a position of 1e-7 is not zero in `pos` and IS zero in
        # `unit`. Testing the input to a rounding step tells you nothing about
        # its output. It is the emitted number that reaches a reader, so it is
        # the emitted number that is checked.
        #
        # A mount genuinely close to the centreline keeps its position - it
        # rounds to something non-zero. Only a value that arrives at the reader
        # as exactly (0,0,0) is refused, and that port falls back to its derived
        # position rather than getting a confident wrong one.
        _all = j["hardpoints"]

        def _emits_origin(n, denom):
            return not any(round(c / denom, 5) for c in n["pos"])

        _mn0, _mx0 = j["hull_box"]["min"], j["hull_box"]["max"]
        H0 = max((_mx0[i] - _mn0[i]) / 2.0 for i in range(3)) or 1.0
        _held = [n["name"] for n in _all if n.get("outside")]
        _origin = [n["name"] for n in _all
                   if not n.get("outside") and _emits_origin(n, H0)]
        _held = _held + _origin
        _pts = [n for n in _all
                if not n.get("outside") and not _emits_origin(n, H0)]
        mdl = lm.get(cls.lower())
        key = by_model.get(os.path.splitext(mdl)[0].lower()) if mdl else None
        if not key:
            # NO MARKER RECORD EXISTS FOR THIS SHIP, AND ONE CANNOT BE MADE THE
            # NORMAL WAY. `hardpoints_fleet.json` has a single writer,
            # `place_fleet.py` - and THAT SCRIPT IS NOT IN THIS REPOSITORY. So
            # the file that decides which ships get hull markers at all cannot
            # be regenerated by anybody, and the nineteen ships imported on
            # 2026-08-27 are absent from it. That is why they show no dots.
            #
            # This does NOT write that file. It emits a SEPARATE additive one,
            # carrying only ships the fleet record does not have, built from
            # CIG's own transforms rather than from a name-derived guess - so
            # these arrive better-placed than the records they are joining, not
            # worse. Same pattern the alignment overlay already uses, and for
            # the same reason: one writer per artifact, and a second file is
            # reversible by deleting it.
            added[cls] = {
                "model": mdl,
                "record_source": "hardpoint-placement (CIG transforms)",
                "note": "added by build_hardpoint_overlay.py because "
                        "hardpoints_fleet.json has no record for this hull",
                "hardpoints": [{"port": n["name"], "unit": [round(c / H0, 5)
                                for c in n["pos"]]}
                               for n in _pts],
                "ports_withheld": _held,
            }
            report.append({"class": cls, "emitted": 0, "added_record": True,
                           "ports_added": len(_pts),
                           "ports_withheld": len(_held),
                           "ports_at_origin": len(_origin),
                           "why": "no fleet record - a new one was emitted"})
            continue

        mn, mx = j["hull_box"]["min"], j["hull_box"]["max"]
        # THE SAME DEFINITION THE BUILD USES: normalised to the hull's longest
        # HALF-extent. Taken from build_holo_data.py's own header rather than
        # re-invented.
        H = max((mx[i] - mn[i]) / 2.0 for i in range(3))
        if H <= 0:
            continue
        # Same guard against the SECOND denominator. This branch normalises by
        # `H` (this hull's own half-extent from the fleet record) rather than
        # `H0`, so a port can round to the origin here and not there.
        ours = {h["name"]: [c / H for c in h["pos"]] for h in _pts
                if not _emits_origin(h, H)}

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
    json.dump(added, open(ADDED, "w", encoding="utf-8"), indent=1)
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
