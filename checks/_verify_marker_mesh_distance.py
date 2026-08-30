#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Is each marker actually near the ship's surface - measured in 3D, not on screen.

RULE16: INDEPENDENT - the distance is computed against vertices decoded from the
    hull's own .glb, which is a different artifact from loadout_marker.gen.js
    where the marker positions live. Neither file can see the other.

WHY THIS EXISTS AND WHAT IT REPLACES
====================================
`offhull.py` photographs a ship twice and asks whether a hull pixel lies within
14px of each dot. That measures VISIBILITY, and I recorded it as POSITION.

A concave hull shows the background through its own gaps, so a mount in a
recess, a wing root or between two arms is photographed against empty space and
called adrift. There is no camera angle that fixes it - the gap is real.

On 2026-08-29 it flagged the Vanduul Glaive's `Gun nose left` at 5.488 units and
PASSED `Gun nose right` at 5.481 - a mirrored pair, seven thousandths of a unit
apart, split across the verdict because of which side faced the camera. It also
flagged the Storm AA's port 4, the second-closest of only four markers on that
vehicle, and never mentioned the Corsair's `Cheek weapon right`, which is
farther out than two of the three Corsair mounts it did flag.

docs/FINDING_the-off-hull-test-flagged-one-gun-of-a-matched-pair-2026-08-29.md

WHAT IT MEASURES
================
For each hull with both markers and a model: decode the mesh, put every marker
into model space the same way the page does - centre + unit * (longest extent /
2) - and take the distance to the nearest real vertex.

A MARKER IS JUDGED AGAINST ITS OWN HULL, NEVER AGAINST THE FLEET. Hulls differ
enormously in how tightly their markers sit: the Storm AA's four are all within
0.57 units, the Corsair's thirty-eight have a median of 2.56. One fleet-wide
threshold would condemn every Corsair mount and clear every Glaive one. The
outlier rule is therefore relative: MAD above the hull's own median, with a
floor so a hull whose markers are all identical cannot manufacture an outlier
out of rounding.

FAIL CLOSED ON WHAT IT CANNOT READ. A hull whose mesh will not decode is
reported as unmeasured and named. It is never counted as clean.

Rule 15: the marker file is opened utf-8 with errors=replace; meshes are bytes.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

try:
    import numpy as np
except ImportError:
    print("NOT PERFORMED - numpy is not installed, so no distance can be "
          "computed. Nothing below was measured.")
    sys.exit(2)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPLOY = os.path.join(ROOT, "testing", "_deploy")
MARKER = os.path.join(DEPLOY, "loadout_marker.gen.js")
MODELJS = os.path.join(DEPLOY, "loadout_model.gen.js")
MODELS = os.path.join(DEPLOY, "models")
HELPER = os.path.join(ROOT, "checks", "_dracopos.mjs")

# THE OUTLIER RULE. k * MAD above the hull's own median, never below FLOOR.
# 6 rather than 3: at 3 the Corsair reports a third of its own mounts, because
# its distribution is genuinely wide rather than because those mounts are wrong.
# The Glaive's pair clears 6 by a factor of four.
K_MAD = 6.0
FLOOR_FRACTION = 0.04     # of the hull's longest extent

SELFTEST = "--self-test" in sys.argv


def load_marker_sets():
    txt = open(MARKER, encoding="utf-8", errors="replace").read()
    out = {}
    for m in re.finditer(r'"([A-Za-z0-9_\.\'-]+)":\[\[', txt):
        cls = m.group(1)
        i = m.end() - 2
        j = txt.find("]],", i)
        seg = txt[i:(j if j > 0 else len(txt))]
        rows = re.findall(
            r'\["([^"]+)",(-?[\d.eE-]+),(-?[\d.eE-]+),(-?[\d.eE-]+),"(\w+)"\]',
            seg)
        if rows:
            out[cls] = [(p, float(x), float(y), float(z), w)
                        for p, x, y, z, w in rows]
    return out


def model_for():
    txt = open(MODELJS, encoding="utf-8", errors="replace").read()
    m = re.search(r"=\s*(\{[\s\S]*?\})\s*;", txt)
    return json.loads(m.group(1)) if m else {}


def vertices(glb_path):
    """(array, None) or (None, reason). Never raises for a bad model."""
    fd, tmp = tempfile.mkstemp(suffix=".f32")
    os.close(fd)
    try:
        r = subprocess.run(["node", HELPER, glb_path, tmp],
                           capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=180)
        if r.returncode != 0:
            why = (r.stderr or "").strip().splitlines()[-1:] or ["exit %d" % r.returncode]
            return None, why[0][:80]
        a = np.fromfile(tmp, dtype=np.float32)
        if a.size < 9:
            return None, "decoded %d floats" % a.size
        return a.reshape(-1, 3), None
    except FileNotFoundError:
        return None, "node is not on PATH"
    except subprocess.TimeoutExpired:
        return None, "decode timed out"
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass


def measure(pts, marks, nudge=None):
    """Distance from every marker to the nearest vertex, in model units."""
    mn = pts.min(0)
    mx = pts.max(0)
    centre = (mn + mx) / 2.0
    span = float((mx - mn).max())
    half = np.float32(span / 2.0)
    out = []
    for (pid, x, y, z, prov) in marks:
        u = np.array([x, y, z], dtype=np.float32)
        if nudge and pid == nudge[0]:
            u = u + np.float32(nudge[1])
        p = centre + u * half
        best = np.inf
        for k in range(0, len(pts), 200000):
            c = pts[k:k + 200000] - p
            best = min(best, float(np.sqrt((c * c).sum(1)).min()))
        out.append((pid, prov, best))
    return out, span


def outliers(rows, span):
    d = np.array([r[2] for r in rows])
    med = float(np.median(d))
    mad = float(np.median(np.abs(d - med))) or 1e-9
    cut = max(med + K_MAD * mad, span * FLOOR_FRACTION)
    return [r for r in rows if r[2] > cut], med, cut


def main():
    for f in (MARKER, MODELJS):
        if not os.path.exists(f):
            print("NOT PERFORMED - no %s. Nothing has been built." % f)
            return 2
    if not os.path.exists(HELPER):
        print("NOT PERFORMED - %s is missing; the meshes cannot be read."
              % HELPER)
        return 2

    marks = load_marker_sets()
    models = model_for()
    todo = [c for c in sorted(marks)
            if models.get(c)
            and os.path.exists(os.path.join(MODELS, models[c]))]
    if not todo:
        print("NOT PERFORMED - no hull has both markers and a model file "
              "on disk.")
        return 2

    # A DECODER PROBE BEFORE THE WORK, so "the decoder is absent" is one clear
    # sentence rather than 250 identical failures.
    _p, why = vertices(os.path.join(MODELS, models[todo[0]]))
    if _p is None and why in ("NO_DRACO", "node is not on PATH"):
        print("NOT PERFORMED - %s. The hull meshes are Draco-compressed and "
              "cannot be read without it, so no marker was measured. "
              "`npm i draco3d` in the repo root." % why)
        return 2

    print("marker mesh distance: %d hull(s) with a model" % len(todo))
    print()
    bad = {}
    unread = []
    seen = 0
    for cls in todo:
        pts, why = vertices(os.path.join(MODELS, models[cls]))
        if pts is None:
            unread.append((cls, why))
            continue
        rows, span = measure(pts, marks[cls])
        seen += len(rows)
        odd, med, cut = outliers(rows, span)
        if odd:
            bad[cls] = (odd, med, cut, span)

    for cls, (odd, med, cut, span) in sorted(bad.items()):
        print("  %-34s median %.3f  cut %.3f  span %.1f"
              % (cls, med, cut, span))
        for pid, prov, d in sorted(odd, key=lambda r: -r[2]):
            print("       port %-16s %-4s %8.3f units  %5.1f%% of length"
                  % (pid, prov, d, 100.0 * d / span))

    print()
    print("  %d marker(s) measured on %d hull(s); %d flagged on %d hull(s)"
          % (seen, len(todo) - len(unread), sum(len(v[0]) for v in bad.values()),
             len(bad)))
    if unread:
        print("  %d hull(s) COULD NOT BE READ and are not counted as clean:"
              % len(unread))
        for cls, why in unread:
            print("     %-34s %s" % (cls, why))

    if SELFTEST:
        return selftest(marks, models, todo)

    # Reporting, not refusing: an outlier here is a question about a mount, and
    # this file flags and never moves anything - the auditor rule.
    if unread:
        print()
        print("FAIL - a hull whose mesh could not be read is not a clean hull.")
        return 1
    print()
    print("PASS - every hull was measured. %d marker(s) sit far enough from "
          "their hull to be worth a look; see the list above." % 
          sum(len(v[0]) for v in bad.values()))
    return 0


def selftest(marks, models, todo):
    """RULE 12. Displace one marker and require this control to notice."""
    print()
    print("SELF-TEST")
    cls = None
    for c in todo:
        if len(marks[c]) >= 6:
            cls = c
            break
    if cls is None:
        print("  no hull with enough markers to test on.")
        return 0
    pts, why = vertices(os.path.join(MODELS, models[cls]))
    if pts is None:
        print("  could not read %s: %s" % (cls, why))
        return 0

    rows, span = measure(pts, marks[cls])
    odd0, _m, _c = outliers(rows, span)
    victim = min(rows, key=lambda r: r[2])[0]
    print("  negative control: %s is clean at %s" % (victim, cls))

    ok = True
    for push in (0.25, 0.6):
        rows2, span2 = measure(pts, marks[cls], nudge=(victim, push))
        odd2, _m2, _c2 = outliers(rows2, span2)
        caught = any(r[0] == victim for r in odd2)
        print("  push %-5s %-20s %s" % (push, victim,
                                        "caught" if caught else "NOT CAUGHT"))
        ok = ok and caught

    if ok:
        print()
        print("SELF-TEST PASSED - a displaced marker is detected.")
        print("Exiting NON-ZERO on purpose: the suite requires a control's "
              "self-test to be rejected. This is the GOOD outcome.")
        return 9
    print()
    print("SELF-TEST FAILED - this is not currently a control.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
