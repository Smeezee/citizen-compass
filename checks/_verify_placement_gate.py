# -*- coding: utf-8 -*-
"""Does the placement acceptance gate still refuse a broken frame?

RULE16: INDEPENDENT - the gate's arithmetic is RE-IMPLEMENTED here rather than
imported from build_hardpoint_placement.py, so this check and the code it judges
do not share a definition; and the three mutations feed it clouds the decoder
could never produce. Its inputs are the placement OUTPUT plus deliberately
broken copies of it, never the placer's own verdict. If the two implementations
ever disagree, that disagreement is the finding.

RULE 12: a check that cannot fail is not a check. On 2026-08-27 the gate went
from all-or-nothing ("any exterior mount outside -> refuse the hull") to
proportional ("more than half outside -> refuse; a few -> withhold those
ports"). After that change 148 of 148 hulls passed and NOTHING in the fleet
refused anything. A gate with no failing case in the data is indistinguishable
from a gate that has been switched off, and the only honest way to tell them
apart is to hand it something that must fail.

THREE CONTROLS, EACH A DIFFERENT WAY THE PLACEMENT CAN BE WRONG:

  1. TRANSPOSED AXIS   - lateral and vertical swapped. This is the specific
                         defect the acceptance test was written for.
  2. WRONG SCALE       - every position multiplied by four.
  3. BAKED OFFSET      - the whole cloud shifted by one full hull length,
                         which is the M2 Hercules' historical failure mode
                         (14 of 15 outside before its frame was corrected).

AND ONE NEGATIVE CONTROL, which is the half that catches a gate stuck on
"refuse": the UNMODIFIED hull must still pass. A check that refuses everything
proves nothing either.

The arithmetic here is a deliberate re-implementation of the gate rather than
an import of it. Importing build_hardpoint_placement.py would make this test
agree with the code by construction - rule 16, a check must draw its truth from
somewhere other than the thing it checks. If the two ever disagree, that
disagreement is the finding.

    run:  python checks/_verify_placement_gate.py
"""
import json
import os
import re
import sys

PLACE = os.path.join("data-layer", "derived", "hardpoint-placement")
MARGIN = 0.06
WITHHOLD_MAX = 4
# Re-stated here, not imported, for the same reason the gate is re-implemented:
# a check that reads its own threshold out of the code under test agrees with
# it by construction and cannot notice it being changed.
MIRROR_MIN_FRACTION = 0.5
MIRROR_MIN_PAIRS = 4
# Copied from the placement script's own EXTERIOR pattern deliberately - if it
# drifts there, this check stops selecting the same mounts and says so.
EXTERIOR = re.compile(
    r"(hardpoint|turret|missile|rack|weapon|gun|mount|wing|nose|tail|"
    r"top|bottom|left|right|front|back|rear|side)", re.I)


def gate(points, box_min, box_max):
    """(passed, n_exterior, n_outside) for one hull's converted points."""
    ext = [box_max[i] - box_min[i] for i in range(3)]
    ctr = [(box_min[i] + box_max[i]) / 2.0 for i in range(3)]
    n = out = 0
    for h in points:
        if not EXTERIOR.search(h["name"]):
            continue
        n += 1
        p = h["pos"]
        for i in (0, 1):
            m = ext[i] * MARGIN
            if p[i] < box_min[i] - ctr[i] - m or p[i] > box_max[i] - ctr[i] + m:
                out += 1
                break
    # THE RULE, IN TWO PARTS.
    #
    # It was briefly proportional ("more than half outside refuses") and this
    # check is what refuted that - a transposed axis displaces only 10 of 59
    # mounts on the Eclipse, so half is a threshold the defect walks straight
    # through. A COUNT OF OFFENDERS CANNOT TELL A POSE MISMATCH FROM A FRAME
    # ERROR and no threshold on it ever will.
    #
    # So the count did not loosen. A SECOND, INDEPENDENT SIGNAL was added:
    # exterior left/right pairs must all mirror in the converted frame. A
    # transpose destroys that completely (0 of N on every hull tested) and a
    # wrong scale does not touch it - which is exactly the complement of what
    # containment can see.
    #
    #   frame proven  -> out-of-box mounts are withheld individually
    #   not proven    -> any mount outside refuses the whole hull
    #
    # Both halves are controlled below.
    #
    # AND A PROVEN FRAME IS NOT A LICENCE TO IGNORE CONTAINMENT. Mirroring
    # survives a uniform scale and a uniform offset, so "proven" alone let a 4x
    # scale and a full-hull-length offset through on the Eclipse and the Sabre.
    # This check caught that too. The withholding is bounded by an absolute
    # count: pose mismatches run 1-3, the smallest frame error observed is 23.
    m, pr = mirror(points)
    proven = pr >= MIRROR_MIN_PAIRS and m >= pr * MIRROR_MIN_FRACTION
    # THE VETO, re-implemented alongside the licence. A hull with enough pairs
    # to judge, whose pairs mostly do not mirror, is refused whatever
    # containment says - because containment cannot see a transpose on a hull
    # as tall as it is wide, which is how the San'tok.yai survived one.
    if pr >= MIRROR_MIN_PAIRS and m < pr * MIRROR_MIN_FRACTION:
        return False, n, out
    return (n > 0 and (out == 0 or (proven and out <= WITHHOLD_MAX))), n, out


def mirror(points):
    """(matched, pairs) over exterior left/right families, GLB frame.

    Re-implemented rather than imported, for the same reason as the gate
    itself: a check that imports the code it checks agrees with it by
    construction.
    """
    # ALL named pairs, not exterior only - matching the rule change of
    # 2026-08-28. The span used for the tolerance is taken over the same
    # population that is being judged, as it is in the placer.
    hp = {h["name"]: h["pos"] for h in points}
    if not hp:
        return 0, 0
    span = 0.0
    for i in range(3):
        v = [p[i] for p in hp.values()]
        span = max(span, max(v) - min(v))
    tol = max(0.05, span * 0.004)
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
                d = max(abs(hp[a][0] + hp[b][0]),
                        abs(hp[a][1] - hp[b][1]),
                        abs(hp[a][2] - hp[b][2]))
                if bd is None or d < bd:
                    best, bd = b, d
            free.remove(best)
            if bd < tol:
                matched += 1
    return matched, pairs


def load(cls):
    with open(os.path.join(PLACE, cls + ".json"), encoding="utf-8") as fh:
        return json.load(fh)


MUTATORS = [
    ("transposed axis (lateral <-> vertical)",
     lambda p: [p[1], p[0], p[2]]),
    ("wrong scale (x4)",
     lambda p: [p[0] * 4.0, p[1] * 4.0, p[2] * 4.0]),
]


def main():
    if not os.path.isdir(PLACE):
        print("NOT PERFORMED - no placement directory. Run "
              "build_hardpoint_placement.py first.")
        return 2

    files = [f[:-5] for f in sorted(os.listdir(PLACE))
             if f.endswith(".json") and f != "MANIFEST.json"]
    if not files:
        print("NOT PERFORMED - no placed hulls to test.")
        return 2

    # Test on hulls with a decent number of exterior mounts, so a single
    # borderline port cannot decide the result either way.
    subjects = []
    for cls in files:
        j = load(cls)
        _ok, n, _o = gate(j["hardpoints"], j["hull_box"]["min"],
                          j["hull_box"]["max"])
        if n >= 8:
            subjects.append((cls, j, n))
        if len(subjects) >= 6:
            break
    if not subjects:
        print("NOT PERFORMED - no hull carries 8 or more exterior mounts.")
        return 2

    # THE FLEET'S WORST ADVERSARIAL CASE, BY NAME, ADDED 2026-08-28.
    #
    # Six hulls taken in directory order are six hulls that happen to be first.
    # When the fraction rule was measured across all 265 hulls with four or
    # more named pairs, the highest a TRANSPOSED hull reached was **0.455, on
    # the San'tok.yai** - every other transposed hull came in at 0.20 or below.
    # That single hull is most of the safety margin in a 0.5 rule, and a
    # control that does not look at it is measuring the easy part of the
    # distribution.
    #
    # It is pinned here rather than rediscovered, so that if a future decode
    # pushes it past 0.5 this control says so instead of a nightly sweep
    # quietly continuing to pass on six other ships.
    for _hard in ("XNAA_SanTokYai", "VNCL_Glaive", "VNCL_Scythe"):
        if _hard in files and not any(c == _hard for c, _j, _n in subjects):
            _j = load(_hard)
            _ok, _n, _o = gate(_j["hardpoints"], _j["hull_box"]["min"],
                               _j["hull_box"]["max"])
            subjects.append((_hard, _j, _n))

    failures = []
    # THE NEGATIVE CONTROL RUNS ON HULLS THE PLACER ACCEPTED, NOT ON ALL OF
    # THEM - and the distinction was learned by getting it wrong. When the
    # Scythe was pinned in as a hard subject it landed in this loop too, and
    # reported "the gate refuses an UNMODIFIED hull, so it would refuse
    # everything". The Scythe IS refused, on purpose, and has been all along.
    # **A hull the placer rejects is not evidence that the gate rejects
    # everything.** The refused ones are exercised below, where being refused
    # is what they are there to demonstrate.
    print("NEGATIVE CONTROL - an ACCEPTED hull, unmodified, must PASS")
    for cls, j, n in subjects:
        if not j.get("acceptance"):
            print("  %-34s skipped   the placer refuses this hull; it is a "
                  "named negative below" % cls)
            continue
        ok, ne, out = gate(j["hardpoints"], j["hull_box"]["min"],
                           j["hull_box"]["max"])
        state = "pass" if ok else "REFUSED"
        print("  %-34s %-8s %d of %d exterior outside" % (cls, state, out, ne))
        if not ok:
            failures.append("%s: the gate refuses a hull the PLACER accepted, "
                            "so this check and the code it judges disagree "
                            "about the same hull" % cls)

    # AND THE OTHER HALF, WITHOUT WHICH THE SKIP ABOVE IS A HOLE: a hull the
    # placer refused must be refused here too. Skipping them silently would
    # let this control pass over a gate that had stopped refusing anything.
    print("\nNAMED NEGATIVES - a hull the placer REFUSED must be refused here")
    _neg = 0
    for cls, j, n in subjects:
        if j.get("acceptance"):
            continue
        _neg += 1
        ok, ne, out = gate(j["hardpoints"], j["hull_box"]["min"],
                           j["hull_box"]["max"])
        print("  %-34s %-8s %d of %d exterior outside"
              % (cls, "PASSED" if ok else "refused", out, ne))
        if ok:
            failures.append("%s: the placer refuses this hull and the gate "
                            "here admits it - one of the two has drifted"
                            % cls)
    if not _neg:
        failures.append("no refused hull was among the subjects, so the "
                        "negative half of this section proved nothing")

    for label, fn in MUTATORS:
        print("\nCONTROL - %s must be REFUSED" % label)
        for cls, j, n in subjects:
            pts = [{"name": h["name"], "pos": fn(h["pos"])}
                   for h in j["hardpoints"]]
            ok, ne, out = gate(pts, j["hull_box"]["min"], j["hull_box"]["max"])
            state = "PASSED" if ok else "refused"
            print("  %-34s %-8s %d of %d exterior outside"
                  % (cls, state, out, ne))
            if ok:
                failures.append("%s survived %s - the gate did not fire"
                                % (cls, label))

    print("\nCONTROL - a baked offset of one hull length must be REFUSED")
    for cls, j, n in subjects:
        mn, mx = j["hull_box"]["min"], j["hull_box"]["max"]
        span = max(mx[i] - mn[i] for i in range(3))
        pts = [{"name": h["name"],
                "pos": [h["pos"][0], h["pos"][1] + span, h["pos"][2]]}
               for h in j["hardpoints"]]
        ok, ne, out = gate(pts, mn, mx)
        state = "PASSED" if ok else "refused"
        print("  %-34s %-8s %d of %d exterior outside" % (cls, state, out, ne))
        if ok:
            failures.append("%s survived a full-hull-length offset" % cls)

    # ------------------------------------------------------------------
    # THE RULE CHANGED ON 2026-08-28 AND THIS IS THE CONTROL OVER THE CHANGE.
    #
    # `frame_proven` went from "every exterior pair mirrors" to "at least half
    # of ALL named pairs mirror". The old rule could not be met by a hull whose
    # symmetric evidence is interior - the Glaive scored 2/4 on exteriors and
    # 13/19 on everything, and was refused for asymmetry it does not have.
    #
    # A FRACTION INVITES EXACTLY ONE OBJECTION: that it was fitted to admit a
    # ship somebody wanted in. So the separation is re-measured HERE, on every
    # subject, rather than quoted from the run that motivated it. **A
    # transposed hull must not reach the fraction. A clean hull must.** If
    # those two populations ever overlap, the rule is unsafe and this says so
    # by name rather than by drifting.
    print("\nTHE FRACTION HAS TO SEPARATE THE TWO POPULATIONS, and this "
          "re-measures\nthat rather than trusting the run that chose it")
    for cls, j, _n in subjects:
        cm, cp = mirror(j["hardpoints"])
        tm, tp = mirror([{"name": h["name"],
                          "pos": [h["pos"][1], h["pos"][0], h["pos"][2]]}
                         for h in j["hardpoints"]])
        cf = cm / cp if cp else 0.0
        tf = tm / tp if tp else 0.0
        print("  %-34s clean %.3f   transposed %.3f   (rule %.2f)"
              % (cls, cf, tf, MIRROR_MIN_FRACTION))
        # THE "CLEAN MUST REACH IT" HALF APPLIES ONLY TO HULLS THE PLACEMENT
        # ACCEPTED, AND THE FIRST VERSION OF THIS GOT IT WRONG.
        #
        # It asserted that EVERY hull here clears the fraction - and the Scythe
        # does not, at 0.062. That was read as "the rule refuses good hulls".
        # It is not a good hull: the Scythe is the one ship in the fleet whose
        # frame nobody has established, which is exactly why it is refused.
        # **A hull under dispute cannot be used as evidence that the rule
        # rejects hulls unfairly** - that is assuming the conclusion.
        #
        # So the positive half is scoped to hulls the placer accepted, and the
        # Scythe appears below as a NAMED NEGATIVE instead: it must NOT be
        # frame-proven, and if it ever becomes so without new evidence, that is
        # the rule having drifted.
        _acc = j.get("acceptance")
        if _acc and cp >= MIRROR_MIN_PAIRS and cf < MIRROR_MIN_FRACTION:
            failures.append("%s: an ACCEPTED hull falls below the fraction, "
                            "so the placer and this rule disagree about the "
                            "same hull" % cls)
        if cls == "VNCL_Scythe" and cf >= MIRROR_MIN_FRACTION:
            failures.append("VNCL_Scythe reaches the fraction. It is the "
                            "fleet's one genuinely asymmetric hull and the "
                            "named negative for this rule - if it now passes, "
                            "either the decode changed or the rule has been "
                            "loosened, and neither should happen quietly")
        if tp >= MIRROR_MIN_PAIRS and tf >= MIRROR_MIN_FRACTION:
            failures.append("%s: a TRANSPOSED hull reaches the fraction, so "
                            "the rule no longer catches the defect it exists "
                            "for" % cls)

    print("\nTHE SECOND SIGNAL ON ITS OWN - a transpose must destroy the "
          "mirror,\nand a wrong scale must NOT (that is what makes them "
          "complementary)")
    for cls, j, _n in subjects:
        clean = mirror(j["hardpoints"])
        tr = mirror([{"name": h["name"],
                      "pos": [h["pos"][1], h["pos"][0], h["pos"][2]]}
                     for h in j["hardpoints"]])
        sc = mirror([{"name": h["name"],
                      "pos": [c * 4.0 for c in h["pos"]]}
                     for h in j["hardpoints"]])
        print("  %-34s as-is %d/%-3d transposed %d/%-3d scaled %d/%d"
              % (cls, clean[0], clean[1], tr[0], tr[1], sc[0], sc[1]))
        if clean[1] and tr[0] == clean[0]:
            failures.append("%s: a transpose left the mirror unchanged, so "
                            "the second signal is not independent" % cls)
        if clean[1] and sc != clean:
            failures.append("%s: a uniform scale moved the mirror, so it is "
                            "not the scale-blind signal it is relied on to be"
                            % cls)

    print()
    if failures:
        for f in failures:
            print("FAILED: %s" % f)
        print("\n%d control(s) did not behave as required." % len(failures))
        return 1
    print("OK - the gate passes clean hulls and refuses all three broken "
          "frames, on %d hull(s)." % len(subjects))
    return 0


if __name__ == "__main__":
    sys.exit(main())
