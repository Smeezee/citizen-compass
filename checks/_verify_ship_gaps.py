# -*- coding: utf-8 -*-
"""Rule 12 control on scripts/enumerate_ship_gaps.py (E14 / W4).

WHAT THIS HAS TO PROVE, AND WHY THE OBVIOUS CHECK WOULD NOT
===========================================================
The enumerator's whole job is to say WHICH JOIN a ship fell out of. A control
that asserted "Nautilus appears in the RSI list" would pass on an enumerator
that had the six names typed into it, which is the SILENT SUCCESS this project
names in rule 12 - a check that reports PASS because it never actually looked.

So this drives `analyse()` on CONSTRUCTED input where the answer is known by
construction, one synthetic ship per branch of the join chain, and then plants
the real defect on the real dataset:

    --mutate-drop-match   take a ship that HAS a page out of
                          ship_resolution's matched list and require the
                          enumerator to move it page -> RSI. If it does not,
                          the enumerator is not reading the gate at all.
    --mutate-no-pledge    take a ship that falls to RSI and remove its
                          pledge_url. It must be reclassified "plain", not
                          silently kept in the RSI bucket.
    --self-test           invert one assertion. Must exit 1. A control whose
                          failure path has never executed is an untested gate.

THE NEGATIVE CONTROL is a real ship that passes every join - named here, not
implied - so a change that broke the chain for EVERYONE would be caught rather
than read as "the gaps went away".

Rule 15: every open states its encoding.
"""
import argparse
import copy
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "scripts"))
import enumerate_ship_gaps as E  # noqa: E402

# A ship that survives all four joins. Named, not inferred: if the chain breaks
# fleet-wide this row is what notices.
NEGATIVE_CONTROL = "Reclaimer"

# W4's six. Eclipse is deliberately in a different bucket from the other five
# and this control is what keeps that distinction honest.
FIVE = ["Nautilus", "Vulcan", "Crucible", "Legionnaire", "Liberator"]
ODD_ONE_OUT = "Eclipse"

FAILS = []
CHECKS = [0]


def ck(label, got, want):
    CHECKS[0] += 1
    ok = got == want
    if not ok:
        FAILS.append("%s: got %r, want %r" % (label, got, want))
    print("  %-58s %s" % (label, "ok" if ok else "FAIL  got=%r want=%r"
                          % (got, want)))


def synth():
    """One ship per branch, with the answer fixed by construction.

    Nothing here is read off disk, so a passing run proves the classifier
    itself - not that today's data happens to look right.
    """
    return dict(
        ships=[
            {"id": 1, "name": "Whole", "manufacturer": "M",
             "pledge_url": "https://x/1"},
            {"id": 2, "name": "NoGameFile", "manufacturer": "M",
             "pledge_url": "https://x/2"},
            {"id": 3, "name": "NoGameFileNoPledge", "manufacturer": "M",
             "pledge_url": None},
            {"id": 4, "name": "NoBench", "manufacturer": "M",
             "pledge_url": "https://x/4"},
            {"id": 5, "name": "NoFolder", "manufacturer": "M",
             "pledge_url": "https://x/5"},
            {"id": 6, "name": "NoGlb", "manufacturer": "M",
             "pledge_url": "https://x/6"},
            {"id": 7, "name": "NoMarkers", "manufacturer": "M",
             "pledge_url": "https://x/7"},
        ],
        res={"matched": [
            {"site": "Whole", "file": "cls_whole.json"},
            {"site": "NoBench", "file": "cls_absent.json"},
            {"site": "NoFolder", "file": "cls_nofolder.json"},
            {"site": "NoGlb", "file": "cls_noglb.json"},
            {"site": "NoMarkers", "file": "cls_nomarkers.json"},
        ], "no_game_file": [{"site": "NoGameFile"},
                            {"site": "NoGameFileNoPledge"}]},
        bench={"CLS_Whole": {"slots": [{"t": "g", "h": 0}, {"t": "g", "h": 1}]},
               "CLS_NoFolder": {"slots": [{"t": "g", "h": 0}]},
               "CLS_NoGlb": {"slots": [{"t": "g", "h": 0}]},
               "CLS_NoMarkers": {"slots": [{"t": "g", "h": 0},
                                           {"t": "g", "h": 1},
                                           {"t": "g", "h": 1}]}},
        hp_names=["port_a", "port_b"],
        types={"g": {"t": "WeaponGun"}},
        cc={"1": "Whole", "5": None, "6": "NoGlb", "7": "NoMarkers"},
        have={"Whole.glb", "NoMarkers.glb"},
        mark={"CLS_Whole": [["1", 0, 0, 0], ["2", 0, 0, 0]]},
        model={"CLS_Whole": "Whole.glb"},
        folders={},
        fleet={"Whole": {"model": "Whole.glb"}},
    )


def by_name(rows):
    return {r["name"]: r for r in rows}


def section_synthetic():
    print("1. THE CLASSIFIER, on input whose answer is fixed by construction")
    r = by_name(E.analyse(synth()))

    ck("Whole - all four joins survive: has a page", r["Whole"]["page"], True)
    ck("Whole - has a model", r["Whole"]["model"], True)
    ck("Whole - is not sent to RSI", r["Whole"]["rsi"], False)
    ck("Whole - markers counted", r["Whole"]["markers"], 2)
    ck("Whole - weapon ports counted", r["Whole"]["ports"], 2)
    ck("Whole - no failure reason", r["Whole"]["why"], None)

    ck("NoGameFile - join 1 fails: no page", r["NoGameFile"]["page"], False)
    ck("NoGameFile - falls through to RSI", r["NoGameFile"]["rsi"], True)
    ck("NoGameFile - reason names the gate",
       r["NoGameFile"]["why"], "no game file")
    ck("NoGameFile - markers are 0, not missing",
       r["NoGameFile"]["markers"], 0)

    ck("NoGameFileNoPledge - no pledge url: plain, not RSI",
       (r["NoGameFileNoPledge"]["rsi"], r["NoGameFileNoPledge"]["plain"]),
       (False, True))

    ck("NoBench - game file resolved, bench has no record",
       r["NoBench"]["why"], "game file resolved, no bench record")
    ck("NoBench - a resolved name is still not a page",
       r["NoBench"]["page"], False)

    ck("NoFolder - CC_MODELS has no folder",
       r["NoFolder"]["why"], "no model folder mapped (CC_MODELS)")
    ck("NoFolder - page yes, model no",
       (r["NoFolder"]["page"], r["NoFolder"]["model"]), (True, False))

    ck("NoGlb - folder mapped, file never built",
       r["NoGlb"]["why"], "model folder mapped, no .glb built")

    ck("NoMarkers - page and model both, markers zero",
       (r["NoMarkers"]["page"], r["NoMarkers"]["model"],
        r["NoMarkers"]["markers"]), (True, True, 0))
    ck("NoMarkers - ports still counted, so coverage is 0 of 3",
       r["NoMarkers"]["ports"], 3)
    print()


def section_real(D):
    print("2. W4 ON THE REAL DATASET - one cause for five, a different one for"
          " Eclipse")
    rows = by_name(E.analyse(D))

    for n in FIVE:
        r = rows.get(n)
        if r is None:
            ck("%s present in the site list" % n, False, True)
            continue
        ck("%-13s no page, RSI link, no markers - ONE cause" % n,
           (r["page"], r["rsi"], r["markers"], r["why"]),
           (False, True, 0, "no game file"))

    e = rows.get(ODD_ONE_OUT)
    ck("Eclipse HAS a page - so it is not the five's cause",
       e["page"], True)
    ck("Eclipse HAS a model built and shipped", e["model"], True)
    ck("Eclipse is NOT sent to RSI", e["rsi"], False)
    # RE-BASELINED 2026-08-27 BY THE SESSION THAT CHANGED THE DATA (C1).
    #
    # This said `e["markers"] == 0` and it was right when it was written: the
    # Eclipse had a page and a model and NO hardpoint markers, which is what
    # made it the odd one out - the five have no game file at all, a different
    # cause entirely, and that distinction is the section's whole point.
    #
    # THE ECLIPSE'S GAP IS NOW CLOSED. `hardpoints_fleet.json` still has no
    # record for it - `place_fleet.py`, that file's only writer, is not in this
    # repository - so it was reached another way: an ADDITIVE client record
    # built from CIG's own decoded transforms. It has markers now.
    #
    # THE ASSERTION WAS NOT SIMPLY FLIPPED TO 10. A control that says "however
    # many there are" is not a control. What is asserted is the thing the
    # section exists to distinguish, and it can still fail in both directions:
    #
    #   the Eclipse has markers          -> its gap is closed, and a regression
    #                                       that lost them would fail here
    #   the five still have NONE         -> their cause is different and
    #                                       untouched, asserted above
    #
    # If a future change gives the five markers without a game file, or takes
    # the Eclipse's away, this fails. That is what it is for.
    ck("Eclipse's marker gap is CLOSED - it has markers now, from the additive "
       "client records rather than from hardpoints_fleet.json",
       e["markers"] > 0, True)
    ck("Eclipse's weapon ports are known, so it is thin data not no data",
       e["ports"] > 0, True)

    nc = rows.get(NEGATIVE_CONTROL)
    ck("NEGATIVE CONTROL %s survives every join" % NEGATIVE_CONTROL,
       (nc["page"], nc["model"], nc["rsi"], nc["markers"] > 0),
       (True, True, False, True))
    print()


def section_direction_b(D):
    print("3. BOTH DIRECTIONS ARE ACTUALLY COMPUTED")
    rows = E.analyse(D)
    orphan, unbuilt = E.reverse(D, rows)
    ck("direction B returns a list, not None", isinstance(orphan, list), True)
    ck("every orphan .glb really is on disk",
       all(f in D["have"] for f in orphan), True)
    ck("no orphan is claimed by any site row",
       set(orphan) & {r["glb"] for r in rows if r["glb"]}, set())
    # PLANTED: a model nobody can reach must show up. If direction B is a
    # hard-coded list or a stub, this is what catches it.
    D2 = dict(D)
    D2["have"] = set(D["have"]) | {"__planted_orphan__.glb"}
    o2, _ = E.reverse(D2, E.analyse(D2))
    ck("a planted unreachable model is REPORTED",
       "__planted_orphan__.glb" in o2, True)
    print()


def mutate_drop_match(D):
    """Plant the real defect: the negative control loses its game-file match.

    The mutated dataset is then handed to the UNCHANGED section_real, which
    must go red. If it still passes, section_real is not reading the gate.
    """
    D = copy.deepcopy(D)
    D["res"]["matched"] = [r for r in D["res"]["matched"]
                           if r["site"] != NEGATIVE_CONTROL]
    return D


def mutate_no_pledge(D):
    """Plant the real defect: a ship that falls to RSI loses its pledge_url,
    so the RSI bucket it is asserted to be in must no longer hold it."""
    D = copy.deepcopy(D)
    for s in D["ships"]:
        if s["name"] == FIVE[0]:
            s["pledge_url"] = None
    return D


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mutate-drop-match", action="store_true")
    ap.add_argument("--mutate-no-pledge", action="store_true")
    a = ap.parse_args(argv)

    print("CONTROL - scripts/enumerate_ship_gaps.py (E14 / W4)")
    print()
    section_synthetic()

    if a.self_test:
        print("SELF-TEST - one assertion inverted on purpose. Must exit 1.")
        ck("inverted: Whole must NOT have a page",
           by_name(E.analyse(synth()))["Whole"]["page"], False)
        print()
    else:
        D = E.load()
        if a.mutate_drop_match:
            print("MUTATED: %s removed from ship_resolution's matched list."
                  % NEGATIVE_CONTROL)
            print("The assertions below are UNCHANGED and must now go red.")
            print()
            D = mutate_drop_match(D)
        elif a.mutate_no_pledge:
            print("MUTATED: %s's pledge_url removed. UNCHANGED assertions "
                  "must now go red." % FIVE[0])
            print()
            D = mutate_no_pledge(D)
        section_real(D)
        section_direction_b(D)

    print("%d assertions, %d failed" % (CHECKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAIL %s" % f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
