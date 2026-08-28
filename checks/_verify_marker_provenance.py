# -*- coding: utf-8 -*-
"""Does every dot the page calls an ESTIMATE actually deserve the word?

RULE16: INDEPENDENT - the two files compared here are written by two different
programs in two different languages of intent. `fleet_records_client.json` is
written by build_hardpoint_overlay.py (C1) out of decoded CIG transforms;
`loadout_marker.gen.js` is written by testing/_src/build_deploy.py (Code) out of
its own merge of the marker dataset, the overlay and the page's own port table.
This check asserts nothing about how either arrived at a number - it asks only
whether two numbers that ARE THE SAME NUMBER carry the same story. Neither file
can satisfy it by agreeing with itself, and the check imports no code from
either producer.

WHAT WENT WRONG, MEASURED 2026-08-28 ON THE DEPLOYED FILE.

`build_deploy.py` decides a marker's provenance with one expression:

    'cig' if _hp.get('placed_from') == 'client' else 'est'

and `placed_from` was stamped in exactly one place - the loop that walks
`alignment_overlay_client.json` and MOVES an existing marker onto a CIG
position. 41 hulls never enter that loop. They have no marker record at all, so
there is no marker to move; they arrive as whole records through
`fleet_records_client.json`, already on CIG's coordinates, and the stamp never
touches them. Every top-level dot on those 41 hulls was labelled `est`.

The positions were never wrong. The page was wrong ABOUT them, in the one field
that exists to tell a decoded mount from a guess - which is worse than saying
nothing, because it was added specifically so the page could stop hedging.

THE ASSERTION, BOTH WAYS. One direction alone is not a check here:

  A. NO UNDER-CLAIM - a marker whose x/y/z equals a client-record port's `unit`
     to 5 decimal places must be labelled `cig`. This is the defect above.
  B. NO OVER-CLAIM  - a marker labelled `cig` must sit on coordinates that
     appear in the client records or in the alignment overlay. A stamp applied
     without provenance behind it is the same failure pointing the other way,
     and it is the failure this fix could plausibly introduce.

Exact equality at the emitted precision. NO FUZZY MATCHING, and no tolerance:
both sides round to 5 dp before they are written, so anything but equality means
the number travelled through something that changed it.

RULE 12 - AND THE REASON THE OBVIOUS CONTROL WOULD HAVE BEEN WORTHLESS.

This check is RED the moment it is written, because the deployed marker file was
built before the stamp existed. That is not a broken check - it is the defect,
still standing, and it turns green when Code rebuilds and not before. Do not
silence it to make a board look clean.

But it means a mutator that only has to make the check FAIL proves nothing here:
the check already fails, so `--mutate-relabel` would have "passed" its control
while doing nothing at all. That is the same inert-mutator trap that nearly
shipped in `_verify_stage_still.mjs` on 2026-08-27, and it is why the control in
this file asserts a DELTA rather than a verdict.

  --self-test  runs the assertions three times over the same real data - clean,
               and once under each mutation - and requires each mutation to move
               the count it is aimed at, in the stated direction, by the stated
               amount. It is decisive whether the check is red or green.

               ITS EXIT CODE IS INVERTED, and that is the suite's convention,
               not a quirk of this file: `run_all_controls.py --self-test`
               requires a NON-ZERO exit from every control, because a control's
               self-test hands it data it MUST reject. So here:

                   non-zero  the mutations were caught. The control works.
                   zero      a mutation went unnoticed, or could not be
                             applied. THE CONTROL IS BROKEN.

               The banner says which happened in words, because an inverted
               exit code read at a glance is a defect waiting to be filed.

               relabel  every `cig` label rewritten to `est`. Under-claims must
                        rise by EXACTLY the number of markers that were labelled
                        `cig`, because every one of them was on a CIG coordinate
                        to begin with. Not "more" - exactly. A different number
                        means A is counting something other than what it says.
               forge    20 markers that are NOT on any CIG coordinate relabelled
                        `cig`. Over-claims must go from whatever they are to
                        exactly that plus 20.

               And the negative half: the clean run must not equal the mutated
               run in either case. A check that reports the same numbers with
               and without a mutation is switched off.
"""
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT = os.path.join(REPO, "data-layer", "derived", "holo-hardpoints-align",
                      "fleet_records_client.json")
OVERLAY = os.path.join(REPO, "data-layer", "derived", "holo-hardpoints-align",
                       "alignment_overlay_client.json")
MARKER = os.path.join(REPO, "testing", "_deploy", "loadout_marker.gen.js")
FLEET = os.path.join(REPO, "data-layer", "derived", "holo-hardpoints",
                     "hardpoints_fleet.json")
MODELS = os.path.join(REPO, "testing", "_src", "loadout_model.gen.js")

SELFTEST = "--self-test" in sys.argv


def _round(v):
    return tuple(round(float(c), 5) for c in v)


def load_markers():
    src = open(MARKER, encoding="utf-8", errors="replace").read()
    body = src[src.find("{", src.find("=")):].rstrip().rstrip(";")
    return json.loads(body)


def main():
    for p in (CLIENT, OVERLAY, MARKER):
        if not os.path.exists(p):
            print("NOT PERFORMED - missing %s" % p)
            return 2

    client = json.load(open(CLIENT, encoding="utf-8"))
    overlay = json.load(open(OVERLAY, encoding="utf-8"))
    fleet = json.load(open(FLEET, encoding="utf-8"))
    markers = load_markers()
    models = json.loads(re.search(r"=\s*(\{[\s\S]*?\});",
                                  open(MODELS, encoding="utf-8").read()).group(1))
    by_class = {k.lower(): os.path.splitext(v)[0].lower()
                for k, v in models.items() if v}

    # PER HULL, NOT FLEET-WIDE - AND THE FIRST DRAFT OF THIS CHECK GOT IT WRONG.
    #
    # Built as one global set of coordinates, assertion A reported 38 markers
    # across 19 hulls - Prowler, Starlancer TAC, every Apollo and Zeus variant -
    # as CIG mounts wearing the wrong label. Every one was a FALSE POSITIVE: an
    # `anc` child port whose ring offset happened to land on a number that is a
    # CIG coordinate on some OTHER ship. Normalised coordinates are small and
    # mirrored pairs are symmetric, so collisions across a 271-hull fleet are
    # expected, not surprising.
    #
    # A coordinate only means something inside the hull it belongs to. The set
    # is keyed by MODEL FILE, which is the join build_deploy.py itself uses -
    # `_by_file` - so this check and the emitter agree on what "the same hull"
    # means without either importing from the other.
    stamped = 0
    per_model = {}

    def _add(model, unit):
        if model:
            per_model.setdefault(model, set()).add(_round(unit))

    for k, rec in client.items():
        mdl = os.path.splitext(rec.get("model") or "")[0].lower() or None
        for h in rec.get("hardpoints") or []:
            _add(mdl, h["unit"])
            if h.get("placed_from") == "client":
                stamped += 1
    for k, ports in overlay.items():
        rec = fleet.get(k) or {}
        mdl = os.path.splitext(rec.get("model") or "")[0].lower() or None
        for pos in ports.values():
            _add(mdl, pos["unit"])

    print("client records : %d hulls, %d ports, %d carry placed_from=client"
          % (len(client), sum(len(r.get("hardpoints") or [])
                              for r in client.values()), stamped))
    print("overlay        : %d hulls, %d ports"
          % (len(overlay), sum(len(p) for p in overlay.values())))
    print("models carrying CIG coordinates: %d" % len(per_model))
    cig_coords = per_model


    if SELFTEST:
        return selftest(markers, cig_coords, by_class)

    under, over = [], []
    total = 0
    for cls, ms in markers.items():
        known = cig_coords.get(by_class.get(cls.lower()) or "", EMPTY)
        for m in ms:
            if len(m) < 5:
                continue
            total += 1
            p = _round(m[1:4])
            lab = m[4]
            # `anc` is excluded from A BY DEFINITION, not by convenience. The
            # emitter's own header: a child port takes its ancestor's mount plus
            # a ring offset, and is "NOT CIG's coordinate for this port even
            # when the ancestor was cig". Demanding it say `cig` would be
            # demanding a lie in the opposite direction.
            if lab == "est" and p in known:
                under.append((cls, m[0], lab))
            if lab == "cig" and p not in known:
                over.append((cls, m[0]))

    print("markers carrying a label: %d" % total)
    print()

    ok = True

    print("A. NO UNDER-CLAIM - a dot on a CIG coordinate must say so")
    if under:
        ok = False
        hulls = sorted({c for c, _, _ in under})
        print("   FAILED: %d marker(s) across %d hull(s) sit on a coordinate "
              "CIG published and are labelled otherwise." % (len(under),
                                                             len(hulls)))
        for c, port, lab in under[:12]:
            print("     %-44s port %-6s labelled %s" % (c, port, lab))
        if len(under) > 12:
            print("     ... and %d more" % (len(under) - 12))
        print("   Hulls: %s" % ", ".join(hulls[:14]))
    else:
        print("   passed")

    print()
    print("B. NO OVER-CLAIM - a dot that says CIG must be on a CIG coordinate")
    if over:
        ok = False
        print("   FAILED: %d marker(s) labelled cig sit on coordinates that "
              "appear in neither the client records nor the overlay."
              % len(over))
        for c, port in over[:12]:
            print("     %-44s port %s" % (c, port))
    else:
        print("   passed")

    print()
    if ok:
        print("PASS - every dot's label matches where its coordinate came from.")
        return 0
    print("FAIL")
    if under:
        print()
        print("If the hulls named above are the client-record ones, this is the "
              "known defect and the fix is already in "
              "build_hardpoint_overlay.py: the stamp is written, and the "
              "EMITTED file has not been rebuilt since. Re-run "
              "build_deploy.py. Do not edit the emitted file.")
    return 1


EMPTY = frozenset()


def _score(markers, cig_coords, by_class):
    """Return (under, over, cig_labelled) for a marker map. No printing.

    Same scoping rule as main(): a coordinate is only evidence inside the hull
    it belongs to, and `anc` is never an under-claim.
    """
    under = over = cig = 0
    for cls, ms in markers.items():
        known = cig_coords.get(by_class.get(cls.lower()) or "", EMPTY)
        for m in ms:
            if len(m) < 5:
                continue
            p = _round(m[1:4])
            if m[4] == "cig":
                cig += 1
                if p not in known:
                    over += 1
            elif m[4] == "est" and p in known:
                under += 1
    return under, over, cig


def _copy(markers):
    return {k: [list(m) for m in v] for k, v in markers.items()}


def selftest(markers, cig_coords, by_class):
    """RULE 12. Each mutation must move its own count by an exact amount."""
    ok = True
    c_under, c_over, c_cig = _score(markers, cig_coords, by_class)
    print("clean      under-claims %5d   over-claims %5d   labelled cig %5d"
          % (c_under, c_over, c_cig))

    m1 = _copy(markers)
    for ms in m1.values():
        for m in ms:
            if m[4] == "cig":
                m[4] = "est"
    r_under, r_over, _ = _score(m1, cig_coords, by_class)
    want = c_under + c_cig
    print("relabel    under-claims %5d   (must be exactly %d = %d + %d)"
          % (r_under, want, c_under, c_cig))
    if r_under != want:
        ok = False
        print("   CONTROL FAILED - assertion A is not counting the label.")
    elif c_cig == 0:
        ok = False
        print("   CONTROL INERT - nothing was labelled cig, so the mutation "
              "changed nothing. This is not a pass.")
    else:
        print("   control decisive")

    m2 = _copy(markers)
    n = 0
    for cls, ms in m2.items():
        known = cig_coords.get(by_class.get(cls.lower()) or "", EMPTY)
        for m in ms:
            if n >= 20:
                break
            if m[4] != "cig" and _round(m[1:4]) not in known:
                m[4] = "cig"
                n += 1
    f_under, f_over, _ = _score(m2, cig_coords, by_class)
    print("forge      over-claims  %5d   (must be exactly %d = %d + %d)"
          % (f_over, c_over + n, c_over, n))
    if n < 20:
        ok = False
        print("   CONTROL COULD NOT BE APPLIED - only %d candidate(s). A "
              "finding about the data, not a pass." % n)
    elif f_over != c_over + n:
        ok = False
        print("   CONTROL FAILED - assertion B is not checking provenance.")
    else:
        print("   control decisive")

    print()
    if ok:
        print("SELF-TEST PASSED - both controls move their own count by the "
              "exact amount and neither is inert.")
        print("Exiting NON-ZERO on purpose: a control's self-test must be "
              "rejected by the suite, which is how the suite tells a working "
              "control from a switched-off one. This is the GOOD outcome.")
        return 9
    print("SELF-TEST FAILED - a mutation was not caught, or could not be "
          "applied. This check is not currently a control and its green runs "
          "mean nothing until that is fixed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
