#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_verify_holo_placement.py - proves the holo viewer's placement rule against
every ship in the fleet and against the actual .glb files.

THE RULE THE VIEWER IMPLEMENTS
==============================

    load():          unitScale = max(bbox size) / 2      # longest half-extent
                     model is recentred on its bbox centre
    placeMarkers():  world = unit * unitScale

So the claim being tested is:

    pos_model  ==  unit * (longest half-extent)  +  (bbox centre)

MEASURED, NOT ASSUMED - AND THE FIRST VERSION OF THIS FILE HAD IT WRONG.
It tested `pos_model / unit` as a pure ratio and the F7C Hornet Mk II failed by
39,000%. That was not a defect in the data; it was a defect in the hypothesis.
The Hornet's hull is not centred on its own origin - its bounding box centre
sits at (0, 1.338, 0.301) - and `unit` is centre-RELATIVE. Fitting the offset
as well as the scalar makes the Hornet agree to three decimal places, and it
also independently confirms the recentring step in load(), which had until then
simply been assumed to line up.

Two things are checked per ship, both against the mesh rather than the dataset's
own account of itself:

  1. ONE SCALAR ON EVERY AXIS. `s` fitted independently for x, y and z must
     agree. If `unit` were normalised per-axis, multiplying by a single number
     would squash two axes - the plausible-looking way to get this wrong.
  2. THAT SCALAR IS THE LONGEST HALF-EXTENT, and the fitted offset is the
     hull's own bbox centre, both read from the .glb.

Then a placement sweep: no marker may sit grossly outside its hull. The bug
this replaces put a marker 49 ship-lengths away, so "gross" is generous on
purpose and the worst real overshoot is REPORTED as a number rather than hidden
under whatever tolerance made it pass.

Bounds come from the POSITION accessors' declared min/max in the glTF JSON
chunk, which sits before any DRACO payload - so the true bounds are readable
without decoding geometry, which headless cannot do.

    python testing/_src/_verify_holo_placement.py
    python testing/_src/_verify_holo_placement.py --prove    # rule 12

Rule 15: encodings stated.
"""
import io
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FLEET = os.path.join(ROOT, "data-layer", "derived", "holo-hardpoints",
                     "hardpoints_fleet.json")
MODELS = os.path.join(ROOT, "testing", "_deploy", "models")

# A marker beyond this much of the hull's half-extent is a placement failure.
# The defect this guards against was 98x, not 1.05x - a mount sits on the skin
# and the positions are derived, so a few percent proud of the bounding box is
# expected. Anything approaching a whole hull is not.
GROSS = 1.10

failures = []
checks = 0


def say(line):
    """stdout that survives San'tok.yaai. cp1252 has broken this pipeline four
    times, once in a diagnostic script printing a ship name."""
    sys.stdout.buffer.write((line + "\n").encode("utf-8", "backslashreplace"))


def check(name, ok, detail=""):
    global checks
    checks += 1
    if ok:
        say("  PASS  " + name)
    else:
        failures.append(name)
        say("  FAIL  " + name + (("\n          " + detail) if detail else ""))


def gltf_json(path):
    """The JSON chunk of a .glb, without decoding any geometry."""
    with io.open(path, "rb") as fh:                 # binary: takes no encoding
        if fh.read(12)[:4] != b"glTF":
            return None
        while True:
            hdr = fh.read(8)
            if len(hdr) < 8:
                return None
            length, kind = struct.unpack("<II", hdr)
            payload = fh.read(length)
            if kind == 0x4E4F534A:                  # 'JSON'
                return json.loads(payload.decode("utf-8"))


def hull_box(model):
    """(centre, half_extents) from every POSITION accessor's declared min/max.

    Node transforms are not applied. That is not a silent shortcut: the checks
    below compare this against a scalar and an offset fitted independently from
    the dataset, so a hull whose nodes carried a scale or a translation would
    disagree loudly instead of passing.
    """
    path = os.path.join(MODELS, model or "")
    if not os.path.exists(path):
        return None
    doc = gltf_json(path)
    if not doc:
        return None
    lo = [float("inf")] * 3
    hi = [float("-inf")] * 3
    used = set()
    for m in doc.get("meshes") or []:
        for prim in m.get("primitives") or []:
            a = (prim.get("attributes") or {}).get("POSITION")
            if a is not None:
                used.add(a)
    for i in used:
        a = (doc.get("accessors") or [])[i]
        if "min" not in a or "max" not in a:
            continue
        for k in range(3):
            lo[k] = min(lo[k], float(a["min"][k]))
            hi[k] = max(hi[k], float(a["max"][k]))
    if any(v == float("inf") for v in lo):
        return None
    return ([(hi[k] + lo[k]) / 2.0 for k in range(3)],
            [(hi[k] - lo[k]) / 2.0 for k in range(3)])


# An axis whose mounts all sit at nearly the same place cannot be fitted, and
# the answer you get from trying is rounding noise. `pos_model` is stored to 3
# decimals and `unit` to 5, so a slope taken across a `unit` range of 0.004 -
# the Nox Kue's x axis, where all five mounts are on the centreline - is
# meaningless. Requiring 15% of the hull's half-extent of spread makes the
# stored precision irrelevant to the result.
MIN_SPREAD = 0.15

# `pos_model` is stored to three decimal places, so every fitted number carries
# at least this much absolute uncertainty. On a hull 0.115 units long that is a
# far bigger fraction than on one 46 units long, which is why a single
# percentage cannot serve both ends of a 10,000x fleet.
POS_ROUNDING = 0.0005

# `unit` is stored to five decimal places. On a small hull the pos_model
# rounding above dominates; on the Asgard, whose half-extent is 2,427 model
# units, it is negligible and THIS is the whole error - which is why the first
# version of the floor rejected the Asgard at 0.0006% against a computed
# 0.0002%. Both terms are real and the floor needs both. Omitting one is not a
# tolerance being too tight, it is an error source being left out.
UNIT_ROUNDING = 0.000005

# A centre offset above this is reported by name. Above CENTRE_FAIL it is a
# failure. The gap between them is deliberate: there is exactly one ship in the
# fleet in that band and it should stay visible rather than silently pass.
CENTRE_REPORT = 0.005
CENTRE_FAIL = 0.02


def fit(xs, ys):
    """Least squares y = s*x + c over a WELL-CONDITIONED axis.

    Returns None when the axis cannot support a fit, so the caller can count
    and report the exclusion rather than average noise into the answer.
    """
    n = len(xs)
    if n < 4:
        return None
    if max(xs) - min(xs) < MIN_SPREAD:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    if den < 1e-12:
        return None
    s = sum((xs[i] - mx) * (ys[i] - my) for i in range(n)) / den
    return s, my - s * mx


def main(prove=False):
    with io.open(FLEET, "r", encoding="utf-8") as fh:
        fleet = json.load(fh)

    axis_spread = []          # (spread, ship)
    scalar_err = []           # (relative error vs longest half-extent, ship)
    centre_err = []           # (offset error as a fraction of hull size, ship)
    overshoot = []            # (ratio, ship, mount)
    fitted = 0
    boxed = 0
    used_axes = 0
    skipped_axes = []
    no_model = []

    for name, rec in fleet.items():
        pts = [p for p in (rec.get("hardpoints") or [])
               if p.get("unit") and p.get("pos_model")]
        box = hull_box(rec.get("model"))
        if box is None:
            no_model.append(name)
            continue
        boxed += 1
        centre, half = box
        longest = max(half)

        # ---- the placement sweep, exactly as the viewer computes it --------
        for p in pts:
            u = p["unit"]
            scale = longest * (3.0 if prove else 1.0)   # --prove: wrong scalar
            for k in range(3):
                r = abs(u[k] * scale) / max(half[k], 1e-9)
                overshoot.append((r, name, p.get("where")))

        # ---- one scalar, and it is the longest half-extent -----------------
        ss, cc, ranges = [], [], []
        for k in range(3):
            us = [p["unit"][k] for p in pts]
            f = fit(us, [p["pos_model"][k] for p in pts])
            if f is None:
                skipped_axes.append((name, "xyz"[k]))
                continue
            ss.append(f[0])
            cc.append(f[1] - centre[k])
            ranges.append(max(us) - min(us))
        used_axes += len(ss)
        if len(ss) < 2:
            # One axis cannot disagree with itself, so it says nothing about
            # whether the normalisation is per-axis. Counted, not silently
            # dropped.
            continue
        fitted += 1
        if prove:                       # --prove: pretend it is per-axis
            ss[1] *= 1.5
        # THE TOLERANCE THIS SHIP'S OWN NUMBERS CAN SUPPORT. A slope fitted
        # across a `unit` range R on a hull of half-extent L cannot be known
        # better than POS_ROUNDING / (R * L). Four times that is the floor
        # below which a disagreement means nothing.
        r_min = max(min(ranges), 1e-9)
        floor = 4.0 * (POS_ROUNDING / max(r_min * longest, 1e-9)
                       + UNIT_ROUNDING / r_min)
        spread = (max(ss) - min(ss)) / max(abs(max(ss)), 1e-9)
        axis_spread.append((spread / max(floor, 1e-9), name, spread, floor))
        scalar_err.append((abs(sum(ss) / len(ss) - longest) / max(longest, 1e-9), name))
        centre_err.append((max(abs(d) for d in cc) / max(longest, 1e-9), name))

    say("\n== coverage ==")
    check("every ship in the fleet has a model whose bounds could be read",
          not no_model,
          "%d without: %s" % (len(no_model), ", ".join(sorted(no_model)[:6])))
    check("the fit ran on a real number of ships, not a handful",
          fitted >= 150, "fitted %d of %d" % (fitted, len(fleet)))
    check("and on most of the axes, so exclusions cannot hollow it out",
          used_axes >= 400,
          "used %d axis fits, skipped %d as too ill-conditioned to mean anything"
          % (used_axes, len(skipped_axes)))
    say("        %d axis fits used, %d skipped (mounts too clustered on that "
        "axis to fit)" % (used_axes, len(skipped_axes)))
    check("a real number of marker placements were computed",
          len(overshoot) >= 3000,
          "%d axis placements - a check that looked at nothing is not a check"
          % len(overshoot))

    say("\n== pos_model == unit * (longest half-extent) + (hull centre) ==")
    worst = max(axis_spread) if axis_spread else (0, None, 0, 1)
    check("the scalar fitted for x, y and z agrees to within what each ship's "
          "own stored precision can resolve",
          worst[0] <= 1.0,
          "worst is %s at %.4f%%, against a rounding floor of %.4f%% - "
          "a per-axis normalisation would make one multiplier wrong on two axes"
          % (worst[1], worst[2] * 100, worst[3] * 100))
    say("        closest to its own noise floor: %s, %.4f%% measured vs "
        "%.4f%% resolvable" % (worst[1], worst[2] * 100, worst[3] * 100))
    es, en = max(scalar_err) if scalar_err else (0, None)
    check("and that scalar IS the hull's longest half-extent, to within 0.5%% "
          "(worst %.4f%%, %s)" % (es * 100, en), es < 0.005,
          "the viewer multiplies by max(bbox size)/2 - if that is not the "
          "normalisation constant, every marker is misplaced by the ratio")
    ec, ecn = max(centre_err) if centre_err else (0, None)
    check("and the fitted offset IS the hull's own bbox centre (worst %.4f%%, %s)"
          % (ec * 100, ecn), ec < CENTRE_FAIL,
          "load() recentres the model on its bbox centre; if `unit` were not "
          "centre-relative, every off-centre hull would be wrong by the offset")
    named = sorted((e for e in centre_err if e[0] > CENTRE_REPORT), reverse=True)
    say("        %d ship(s) offset by more than %.1f%% of hull size%s"
        % (len(named), CENTRE_REPORT * 100, ":" if named else " - none"))
    for e, n in named:
        say("          %5.3f%%  %s" % (e * 100, n))

    say("\n== no marker is grossly misplaced ==")
    overshoot.sort(reverse=True)
    gross = [o for o in overshoot if o[0] > GROSS]
    check("no marker sits beyond %.2fx its hull's half-extent" % GROSS,
          not gross,
          "%d over; worst %.2fx on %s / %s"
          % (len(gross), gross[0][0], gross[0][1], gross[0][2]) if gross else "")
    say("        worst five, reported rather than hidden by the tolerance:")
    for r, n, w in overshoot[:5]:
        say("          %5.3fx  %-28s %s" % (r, n, w))

    say("")
    if failures:
        say("FAILED %d of %d checks" % (len(failures), checks))
        return 1
    say("ALL %d CHECKS PASSED  (%d ships, %d axis placements)"
        % (checks, boxed, len(overshoot)))
    return 0


if __name__ == "__main__":
    if "--prove" in sys.argv:
        say("--prove: feeding the checks input that MUST fail "
            "(per-axis normalisation, and a 3x wrong scalar).")
        if main(prove=True) == 0:
            say("\nPROOF FAILED: known-bad input passed, so these checks are "
                "not checking anything.")
            sys.exit(1)
        say("\nPROOF OK: known-bad input is rejected.")
        sys.exit(0)
    sys.exit(main())
