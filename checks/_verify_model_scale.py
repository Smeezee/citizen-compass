#!/usr/bin/env python3
"""
A4 - THE MODEL SAYS ONE SIZE AND THE GAME SAYS ANOTHER. Report every hull

RULE16: INDEPENDENT - two sources that were produced by different pipelines are
put against each other: the .glb's own measured bounding box and the
published dimension for that ship. Neither number can be made right by
the other being wrong, which is exactly why the disagreement is the
finding.
where they disagree.

WHY THIS EXISTS. The Anvil Asgard's model measures 4,856 x 3,388 x 1,333 while
the game files state 48 x 38 x 12 metres - about 100x on every axis, because
that model was never converted out of centimetres. Nobody caught it by looking.
It surfaced only because the camera fit loop ran away on it and the page went
black, and it had been publishing a wrong length for as long as it had been on
the site.

THE ASGARD IS ALONE IN THE BAND THAT CRASHED THE CAMERA. There is no reason to
believe it is alone in the band that merely lies. A hull 20% wrong renders
perfectly and tells every visitor a false number.

IT FLAGS. IT NEVER RESCALES. Standing rule: an auditor reports and a pipeline
fixes. Nothing here writes to a model, to hull-geometry, or to the catalogue.

WHAT IS COMPARED, AND THE HONEST LIMITS OF IT
=============================================
The model's bounding box comes from data-layer/derived/hull-geometry/, which is
decoded from the .glb the visitor actually loads. The stated size is `dim` -
[Length, Width, Height] - carried from the game files into the loadout data.

AXES ARE MATCHED BY SIZE, NOT BY NAME. `dim` is Length/Width/Height; the model
frame is X lateral, Y up, Z forward. Rather than assume a mapping and be wrong
about it, both triples are SORTED and compared largest-to-largest. That answers
"is this model the right SIZE" and deliberately does not answer "is it the
right way up" - a different question, and one this check does not claim.

A hull is reported when the ratio between the two longest axes falls outside
the band, and separately when the three axis ratios disagree with each other,
which is the signature of a model that is not merely mis-scaled but a different
shape from the record.

Usage: python checks/_verify_model_scale.py [--json] [--self-test]
"""
import io
import json
import os
import re
import sys

# RULE 15, APPLIED TO THE OTHER END OF THE PIPE. Every file here is opened
# utf-8, and this still died printing a ship's NAME: Windows gives stdout
# cp1252, which cannot encode the a-macron in `tok.yai`. That is the same
# defect the rule is about - a text stream with the platform default on it -
# and a checker that crashes while reporting a finding has lost the finding.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
GEO = os.path.join(REPO, "data-layer", "derived", "hull-geometry")
DATA = os.path.join(REPO, "testing", "_src", "loadout_data.gen.js")
MODELS = os.path.join(REPO, "testing", "_src", "loadout_model.gen.js")

# A model within this band of its stated size is not reported. Wide, because a
# bounding box includes antennas and landing gear the published figure may not,
# and because a check that cries wolf is one nobody reads.
LO, HI = 0.60, 1.60
# The three axis ratios must agree with each other within this factor, or the
# model is a different SHAPE and not merely a different size.
SHAPE_TOL = 2.0

SELFTEST = "--self-test" in sys.argv
AS_JSON = "--json" in sys.argv


def read_js_object(path, name):
    s = io.open(path, encoding="utf-8").read()
    m = re.search(re.escape(name) + r"\s*=\s*(\{.*?\});", s, re.S)
    if not m:
        print("STOPPED: no %s in %s" % (name, os.path.relpath(path, REPO)))
        sys.exit(2)
    return json.loads(m.group(1))


def main():
    if not os.path.isdir(GEO):
        print("STOPPED: no hull geometry at %s - NOT PERFORMED, not passed"
              % os.path.relpath(GEO, REPO))
        return 2
    ships = read_js_object(DATA, "LOADOUT_SHIPS")
    models = read_js_object(MODELS, "LOADOUT_MODEL")

    rows, skipped_no_dim, skipped_no_geo = [], 0, 0
    for cls, rec in ships.items():
        dim = rec.get("dim")
        f = models.get(cls)
        if not f:
            continue
        if not (isinstance(dim, list) and len(dim) == 3
                and all(isinstance(v, (int, float)) and v > 0 for v in dim)):
            skipped_no_dim += 1
            continue
        gp = os.path.join(GEO, os.path.splitext(f)[0] + ".json")
        if not os.path.exists(gp):
            skipped_no_geo += 1
            continue
        try:
            g = json.load(io.open(gp, encoding="utf-8"))
        except Exception:
            skipped_no_geo += 1
            continue
        mn, mx = g.get("min"), g.get("max")
        if not (isinstance(mn, list) and isinstance(mx, list)):
            skipped_no_geo += 1
            continue
        size = sorted((mx[i] - mn[i] for i in range(3)), reverse=True)
        if not all(v > 0 for v in size):
            skipped_no_geo += 1
            continue
        stated = sorted((float(v) for v in dim), reverse=True)
        ratios = [size[i] / stated[i] for i in range(3)]
        r = ratios[0]
        spread = max(ratios) / min(ratios) if min(ratios) > 0 else 1e9
        rows.append({
            "class": cls, "name": rec.get("n") or cls, "model": f,
            "model_size": [round(v, 1) for v in size],
            "stated_dim": [round(v, 1) for v in stated],
            "ratio": round(r, 3), "axis_ratios": [round(v, 3) for v in ratios],
            "shape_spread": round(spread, 3),
            "scale_flag": not (LO <= r <= HI),
            "shape_flag": spread > SHAPE_TOL,
        })

    rows.sort(key=lambda x: -abs(1.0 - x["ratio"]))
    scale_bad = [x for x in rows if x["scale_flag"]]
    shape_bad = [x for x in rows if x["shape_flag"] and not x["scale_flag"]]

    if AS_JSON:
        print(json.dumps({"band": [LO, HI], "shape_tolerance": SHAPE_TOL,
                          "compared": len(rows), "findings": scale_bad + shape_bad,
                          "all": rows}, indent=1))
        return 0

    print("=" * 70)
    print("A4 - the model's bounding box against the game's stated dimensions")
    print("=" * 70)
    print("compared      : %d hulls" % len(rows))
    print("skipped       : %d with no stated dim, %d with no decoded geometry"
          % (skipped_no_dim, skipped_no_geo))
    print("band          : %.2f - %.2f of stated, longest axis" % (LO, HI))
    print("shape spread  : flagged above %.1fx disagreement between axes"
          % SHAPE_TOL)
    print()
    if rows:
        mid = rows[len(rows) // 2]["ratio"]
        print("median ratio  : %.3f" % mid)
    print()

    print("--- SCALE: the model is not the size the game says it is ---")
    if not scale_bad:
        print("  none")
    for x in scale_bad:
        print("  %-28s %-22s model %s  stated %s  = %.2fx"
              % (x["name"][:28], x["model"], x["model_size"], x["stated_dim"],
                 x["ratio"]))

    print()
    print("--- SHAPE: the axes disagree with each other ---")
    if not shape_bad:
        print("  none")
    for x in shape_bad:
        print("  %-28s axis ratios %s  spread %.2fx"
              % (x["name"][:28], x["axis_ratios"], x["shape_spread"]))

    print()
    n = len(scale_bad) + len(shape_bad)
    print("%d finding(s). THIS AUDITOR FLAGS AND NEVER RESCALES." % n)

    # SELF-TEST: the check must be able to report something. Feeding it a hull
    # scaled by 100 has to produce a finding, or the band above is decoration.
    if SELFTEST:
        print()
        print("--- self-test: a planted 100x hull must be reported ---")
        if not rows:
            print("  NOT PERFORMED - nothing was compared")
            return 2
        probe = dict(rows[len(rows) // 2])
        planted = [v * 100.0 for v in probe["model_size"]]
        stated = probe["stated_dim"]
        r = planted[0] / stated[0]
        caught = not (LO <= r <= HI)
        print("  %s at 100x -> ratio %.1f -> %s"
              % (probe["name"], r, "REPORTED" if caught else "MISSED"))
        shrunk = [v / 100.0 for v in probe["model_size"]]
        r2 = shrunk[0] / stated[0]
        caught2 = not (LO <= r2 <= HI)
        print("  %s at 1/100x -> ratio %.4f -> %s"
              % (probe["name"], r2, "REPORTED" if caught2 else "MISSED"))
        unchanged = probe["ratio"]
        caught3 = LO <= unchanged <= HI
        print("  %s unchanged -> ratio %.3f -> %s"
              % (probe["name"], unchanged,
                 "not reported, correctly" if caught3 else "REPORTED - the "
                 "band rejects a hull it should accept"))
        if not (caught and caught2 and caught3):
            print("  SELF-TEST FAILED")
            return 1
        print("  self-test passed: the band reports both directions and "
              "accepts the middle")
    return 0


if __name__ == "__main__":
    sys.exit(main())
