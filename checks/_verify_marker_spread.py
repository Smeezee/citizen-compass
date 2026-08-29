# -*- coding: utf-8 -*-
"""Do a hull's dots spread across the hull, or sit in a heap in the middle?

RULE16: INDEPENDENT - the hull's real size is read HERE, out of the .glb's own
binary header, and compared against the emitted marker positions. The model file
is not written by this project at any stage: it is the artist's mesh. So the
question "do these dots cover this ship" is settled by the ship, not by the
pipeline agreeing with itself.

WHAT IT CATCHES, AND WHY NOTHING ELSE DID.

Every existing control asks whether a marker is CORRECT. This one asks whether
the set of them is PLAUSIBLE. On 2026-08-28 the ship page was showing, on ten
hulls, every mount piled into a single cluster the size of a cockpit - the
Tiburon's seventeen dots in one clump, the Xian Scout's four on top of each
other - and **every one of them was labelled `cig`, telling the visitor these
were CIG's own published coordinates.** Confidently wrong is worse than absent.

    containment      passed: a heap in the middle IS inside the hull box
    the mirror       passed: a heap is still symmetric about the centreline
    provenance       passed: the labels matched where the numbers came from
    the census       passed: no hull LOST markers

**Four green controls and a heap of dots.** Each was asking a real question and
none of them was this one. It took photographing all 295 ships to see it.

THE CAUSE, recorded so the fix is not mistaken for a tolerance change. The scale
rule is *CIG's Length against the hull box's fore/aft extent*, and fore/aft is
taken to be the GLB's Z axis. **19 of 258 models are not in that orientation** -
their Y extent exceeds their Z, which is to say they measure taller than they
are long. The Mantis is 1680 x 2965 x 630. A ship is not that shape. On those
hulls the scale is computed against the wrong axis and every mount collapses
toward the origin.

TWO SIGNALS HAVE TO AGREE, AND THE FIRST DRAFT USED ONLY ONE.

That draft refused on spread alone at 0.5, and named the Caterpillar, the
Retaliator and the Eclipse. **All three were wrong.** Their screenshots show
dots running nose to tail exactly where the guns are. Two faults: it measured
only TOP-LEVEL mounts when the page draws one dot per MOUNT ROOT including
children, and 0.5 sat in a crowded band rather than an empty one.

Measured on what is actually drawn, the populations separate - but by 0.047,
which is not enough to hang a verdict on:

    heaped hulls    0.100 .. 0.446      healthy hulls   0.493 .. 1.756

**So spread alone never refuses anything.** A hull is refused only when a low
spread coincides with the independent cause: a MODEL that measures taller than
it is long, read from the mesh file. Every genuinely broken hull carries both.
The three false positives carry neither - their models are the ordinary shape.

    low spread + odd model    refused. Two sources agreeing.
    low spread alone          reported, never refused. Small ship, or a
                              genuinely compact loadout.
    odd model alone           reported. The Railen and Pitbull sit here and
                              their dots are fine.

**Four dots minimum**: two mounts close together on a small hull is a real ship,
and a rule that fired on it would be measuring hull size.

RULE 12 - THE CONTROLS. `--self-test` collapses a healthy hull's markers toward
the origin and requires this to catch it, then spreads a broken hull's out and
requires the complaint to stop. A check that only ever fires one way is half a
check. Its exit code is inverted per the suite's convention.
"""
import json
import os
import re
import struct
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKER = os.path.join(REPO, "testing", "_deploy", "loadout_marker.gen.js")
MODELS_JS = os.path.join(REPO, "testing", "_deploy", "loadout_model.gen.js")
MODELS = os.path.join(REPO, "testing", "_deploy", "models")

MIN_SPREAD = 0.47
MIN_DOTS = 4
SELFTEST = "--self-test" in sys.argv


def glb_extent(path):
    """The mesh's own bounding extent, read from the GLB's JSON chunk.

    Not from `hull-geometry`, not from a manifest - from the file the browser
    downloads. If this ever disagrees with a recorded box, the recorded box is
    the thing to doubt.
    """
    with open(path, "rb") as fh:
        head = fh.read(20)
        if len(head) < 20 or head[:4] != b"glTF":
            return None
        jlen = struct.unpack_from("<I", head, 12)[0]
        raw = fh.read(jlen)
    try:
        g = json.loads(raw.decode("utf-8", "replace"))
    except Exception:
        return None
    mn = [float("inf")] * 3
    mx = [float("-inf")] * 3
    for m in g.get("meshes") or []:
        for p in m.get("primitives") or []:
            ai = (p.get("attributes") or {}).get("POSITION")
            if ai is None:
                continue
            a = (g.get("accessors") or [])[ai]
            if not a.get("min") or not a.get("max"):
                continue
            for i in range(3):
                mn[i] = min(mn[i], a["min"][i])
                mx[i] = max(mx[i], a["max"][i])
    if mn[0] == float("inf"):
        return None
    return [mx[i] - mn[i] for i in range(3)]


def load():
    src = open(MARKER, encoding="utf-8", errors="replace").read()
    marks = json.loads(src[src.find("{", src.find("=")):].rstrip().rstrip(";"))
    mods = json.loads(re.search(
        r"=\s*(\{[\s\S]*?\});",
        open(MODELS_JS, encoding="utf-8", errors="replace").read()).group(1))
    return marks, mods


def spread_of(ms):
    """Spread of the dots the page ACTUALLY DRAWS.

    renderMarkers draws one marker per mount root and picks the shallowest
    member of it, so that is what is measured here - re-implemented from the
    emitter's documented rule rather than imported. Measuring top-level mounts
    instead made the Retaliator look like a heap when nine dots are spread
    across it on screen.
    """
    by = {}
    for m in ms:
        if len(m) < 5:
            continue
        by.setdefault(str(m[0]).split(".")[0], []).append(m)
    drawn = []
    for _r, g in by.items():
        g.sort(key=lambda m: (len(str(m[0]).split(".loadout.")), str(m[0])))
        drawn.append(g[0])
    if len(drawn) < MIN_DOTS:
        return None, len(drawn)
    s = 0.0
    for i in (1, 2, 3):
        v = [m[i] for m in drawn]
        s = max(s, max(v) - min(v))
    return s, len(drawn)


def evaluate(marks, odd_models=frozenset(), model_of=None):
    """(refused, watch, ok). Refusal needs BOTH signals."""
    refused, watch, ok = [], [], []
    for cls, ms in marks.items():
        s, n = spread_of(ms)
        if s is None:
            continue
        row = (cls, round(s, 3), n)
        if s >= MIN_SPREAD:
            ok.append(row)
        elif model_of and (model_of.get(cls) in odd_models):
            refused.append(row)
        else:
            watch.append(row)
    for lst in (refused, watch):
        lst.sort(key=lambda r: r[1])
    return refused, watch, ok


def main():
    for p in (MARKER, MODELS_JS):
        if not os.path.exists(p):
            print("NOT PERFORMED - missing %s" % p)
            return 2
    marks, mods = load()

    # THE ORIENTATION SURVEY, from the mesh files themselves. Reported every
    # run whether or not anything fails: a model that is taller than it is long
    # is the upstream cause, and it is worth seeing before the symptom.
    odd = []
    for f in sorted(set(v for v in mods.values() if v)):
        e = glb_extent(os.path.join(MODELS, f))
        if e and e[1] > e[2]:
            odd.append((f, [round(x, 1) for x in e]))
    print("models measuring TALLER than they are LONG: %d of %d"
          % (len(odd), len(set(v for v in mods.values() if v))))
    for f, e in odd[:6]:
        print("   %-30s X=%-9s Y(up)=%-9s Z(len)=%s" % (f, e[0], e[1], e[2]))
    if len(odd) > 6:
        print("   ... and %d more" % (len(odd) - 6))
    print()

    if SELFTEST:
        return selftest(marks)

    oddset = set(f for f, _e in odd)
    refused, watch, ok = evaluate(marks, oddset, mods)
    print("hulls drawing %d+ dots: %d" % (MIN_DOTS, len(refused) + len(watch) + len(ok)))
    if ok:
        print("   healthy spread runs from %.3f upward" % min(r[1] for r in ok))
    print()
    if watch:
        print("WORTH A LOOK - %d hull(s) draw tightly but their model is the "
              "ordinary shape, so one signal only. NOT refused:" % len(watch))
        for cls, s, n in watch:
            print("     %-38s spread %.3f across %d dots" % (cls, s, n))
        print()
    if refused:
        print("REFUSED - %d hull(s) heap their dots AND sit on a model that "
              "measures taller than it is long. Two signals, same conclusion:"
              % len(refused))
        for cls, s, n in refused:
            print("     %-38s spread %.3f across %d dots  %s"
                  % (cls, s, n, mods.get(cls, "?")))
        print()
        print("This is a SCALE fault, not a position fault: the scale rule "
              "measures CIG's Length against the model's Z axis, and on these "
              "models Z is not the long axis. Do not fix it by widening this "
              "rule.")
        print("FAIL")
        return 1
    print("PASS - no hull heaps its dots on a mis-oriented model.")
    return 0


def _copy(marks):
    return {k: [list(m) for m in v] for k, v in marks.items()}


def selftest(marks):
    ok_flag = True
    heaps, watch, ok = evaluate(marks)
    print("clean run: %d heap(s), %d watch, %d healthy"
          % (len(heaps), len(watch), len(ok)))

    heaps = heaps + watch
    if not ok:
        print("CONTROL CANNOT RUN - no healthy hull to collapse.")
        return 0

    # COLLAPSE a healthy hull. It must be caught.
    victim = max(ok, key=lambda r: r[1])[0]
    m1 = _copy(marks)
    for m in m1[victim]:
        for i in (1, 2, 3):
            m[i] = round(m[i] * 0.05, 5)
    h1, _w1, _o1 = evaluate(m1, {"x"}, {victim: "x"})
    caught = any(c == victim for c, _s, _n in h1)
    print("collapse %-34s %s" % (victim, "caught" if caught else "NOT CAUGHT"))
    ok_flag = ok_flag and caught

    # SPREAD a heap out. The complaint must stop for that hull.
    if heaps:
        fixed = heaps[0][0]
        m2 = _copy(marks)
        for j, m in enumerate(m2[fixed]):
            for i in (1, 2, 3):
                m[i] = round((j % 2 * 2 - 1) * 0.9, 5)
        h2, _w2, _o2 = evaluate(m2, {"x"}, {fixed: "x"})
        gone = not any(c == fixed for c, _s, _n in h2)
        print("spread   %-34s %s" % (fixed, "complaint stops" if gone
                                     else "STILL COMPLAINS - one-way check"))
        ok_flag = ok_flag and gone
    else:
        print("no heap in the data to spread - that half is UNEXERCISED, "
              "which is not a pass")
        ok_flag = False

    print()
    if ok_flag:
        print("SELF-TEST PASSED - it catches a collapse and stops complaining "
              "when one is fixed.")
        print("Exiting NON-ZERO on purpose: the suite requires a control's "
              "self-test to be rejected. This is the GOOD outcome.")
        return 9
    print("SELF-TEST FAILED - this is not currently a control.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
