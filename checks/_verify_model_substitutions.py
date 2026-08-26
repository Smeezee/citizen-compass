# -*- coding: utf-8 -*-
"""Rule 12 control on P2 - no site row renders another ship's hull in silence.

WHAT WENT WRONG, AND WHAT ALMOST WENT WRONG IN THE FIX
======================================================
Four site rows rendered a model that was not their own, because a stand-in was
wired in while the base hull was missing and nothing re-checked it once the
hull arrived. `Gladius` rendered `Gladius Valiant`. `Valkyrie Liberator`
rendered the base `Valkyrie`. Arrow and Constellation Aquila rendered nothing
at all.

THE FIX NEARLY SHIPPED ITS OWN WRONG ANSWER. Sixteen rows render a folder whose
NAME differs from the row's, and the obvious move is to repoint all sixteen.
Measured on the meshes:

    Ballista Dunestalker -> Ballista   md5 1c939472...  IDENTICAL
    Ballista Snowblind   -> Ballista   md5 1c939472...  IDENTICAL
    Cutlass Black        -> the Best In Show skin       IDENTICAL
    Gladius              -> Gladius Valiant             DIFFERENT

Three of those four "substitutions" are the same bytes under another name.
Repointing them would add duplicate payload and change nothing a visitor sees.
So this control decides on CONTENT, never on how close two names look, and the
verdict it enforces is computed from md5 sums of the source meshes.

WHAT IT REFUSES TO ACCEPT: a row whose own hull exists on disk with a DIFFERENT
mesh from the one being rendered, and which is not declared. That is a wrong
answer delivered confidently, and it must be impossible to reach by accident.

PROVEN AGAINST KNOWN-BAD INPUT:
    --mutate-standin   repoints Gladius back at Gladius Valiant in the loaded
                       CC_MODELS. A real stand-in, undeclared. Must go red.
    --mutate-unnamed   strips the reason off an orphaned model, so "built and
                       unreachable" becomes a silent state again.
    --self-test        inverts an expectation. Must exit 1.

Rule 15: every open states its encoding.

Usage: venv/Scripts/python.exe checks/_verify_model_substitutions.py
       [--self-test] [--mutate-standin] [--mutate-unnamed]
"""
import argparse
import io
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "scripts"))
import enumerate_ship_gaps as E          # noqa: E402
import classify_model_substitutions as C  # noqa: E402

DECLARED = os.path.join(REPO, "data-layer", "model_substitutions.json")

# Named, not inferred. If a change breaks the whole mapping these are the rows
# that notice, and they are the two the order calls out by name.
KEEP_OWN = {"Gladius Valiant": "Gladius Valiant",
            "Gladius Pirate": "Gladius Pirate Edition"}

FAILS, CHECKS = [], [0]


def ck(label, got, want):
    CHECKS[0] += 1
    ok = got == want
    if not ok:
        FAILS.append("%s: got %r, want %r" % (label, got, want))
    print("  %-62s %s" % (label, "ok" if ok else "FAIL got=%r want=%r"
                          % (got, want)))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mutate-standin", action="store_true")
    ap.add_argument("--mutate-unnamed", action="store_true")
    a = ap.parse_args(argv)

    D = E.load()
    if a.mutate_standin:
        # The real defect, put back: the Gladius row points at the Valiant,
        # whose mesh genuinely differs. Nothing declares it.
        gid = next((str(s["id"]) for s in D["ships"]
                    if s["name"] == "Gladius"), None)
        if gid is None or D["cc"].get(gid) != "Gladius":
            print("MUTATION DID NOT APPLY - the Gladius row does not currently "
                  "render its own hull, so restoring the stand-in proves "
                  "nothing.")
            return 1
        D["cc"][gid] = "Gladius Valiant"
        print("*** MUTATED: the Gladius row renders Gladius Valiant again - a "
              "different mesh, undeclared. ***\n")

    subs, rows = C.classify(D)
    orph = C.orphans(D, rows)
    if a.mutate_unnamed:
        for o in orph:
            o["reason"] = ""
        print("*** MUTATED: the orphaned models lost their reasons - 'built "
              "and unreachable' is a silent state again. ***\n")

    declared = {}
    if os.path.exists(DECLARED):
        with io.open(DECLARED, "r", encoding="utf-8") as fh:
            declared = {d["name"]: d for d in json.load(fh).get("declared", [])}

    print("1. NO SILENT STAND-IN - decided on the mesh, not on the name")
    stand = [s for s in subs if s["verdict"] == "STAND-IN"]
    ident = [s for s in subs if s["verdict"] == "identical-mesh"]
    noown = [s for s in subs if s["verdict"] == "no-own-folder"]
    print("     %d rows render a differently-named folder: %d identical mesh, "
          "%d no own folder, %d STAND-IN"
          % (len(subs), len(ident), len(noown), len(stand)))
    undeclared = [s for s in stand if s["name"] not in declared]
    for s in undeclared:
        print("     *** %s renders %s; its own hull %s has a DIFFERENT mesh"
              % (s["name"], s["renders"], s["own"]))
    ck("no row renders a different ship's mesh undeclared", len(undeclared), 0)

    print("\n2. THE VERDICTS ARE COMPUTED, NOT ASSUMED")
    ck("something was actually classified", len(subs) > 0, True)
    bad = [s for s in ident if s["own_md5"] != s["rendered_md5"]]
    ck("every 'identical-mesh' verdict really has matching md5 sums",
       len(bad), 0)
    bad2 = [s for s in ident if not s["own_md5"]]
    ck("and none of them reached that verdict on a missing file", len(bad2), 0)
    bal = next((s for s in subs if s["name"] == "Ballista Dunestalker"), None)
    ck("the Ballista Dunestalker is measured, not guessed at",
       bal and bal["verdict"], "identical-mesh")
    if bal:
        print("     Ballista Dunestalker: own %s == rendered %s"
              % (bal["own_md5"][:12], bal["rendered_md5"][:12]))

    print("\n3. THE FOUR ROWS THE ORDER NAMES NOW RENDER THEIR OWN HULLS")
    for nm, want in (("Arrow", "Arrow"),
                     ("Constellation Aquila", "Constellation Aquila"),
                     ("Cutlass Black", "Cutlass Black"),
                     ("Gladius", "Gladius"),
                     ("Valkyrie Liberator", "Valkyrie Liberator Edition")):
        r = next((x for x in rows if x["name"] == nm), None)
        ck("%-22s renders %s" % (nm, want), r and r["folder"], want)

    print("\n4. NEGATIVE CONTROL - fixing a base hull did not steal a "
          "variant's model")
    for nm, want in KEEP_OWN.items():
        r = next((x for x in rows if x["name"] == nm), None)
        ck("%-22s still renders its own %s" % (nm, want),
           r and r["folder"], want)
    val = next((x for x in rows if x["name"] == "Valkyrie"), None)
    ck("the base Valkyrie still renders the base Valkyrie",
       val and val["folder"], "Valkyrie")

    print("\n5. BUILT AND UNREACHABLE IS NEVER A SILENT STATE")
    print("     %d built .glb files no site row reaches" % len(orph))
    nameless = [o for o in orph if not (o["reason"] or "").strip()]
    ck("every unreachable model carries a reason", len(nameless), 0)
    if nameless:
        print("     nameless: %s" % ", ".join(o["file"] for o in nameless[:6]))
    ck("the Valkyrie Liberator Edition is no longer among them",
       any(o["file"] == "Valkyrie_Liberator_Edition.glb" for o in orph), False)

    if a.self_test:
        print("\nSELF-TEST - one expectation inverted on purpose. Must exit 1.")
        ck("inverted: there must be at least one undeclared stand-in",
           len(undeclared) > 0, True)

    print("\n%d assertions, %d failed" % (CHECKS[0], len(FAILS)))
    for f in FAILS:
        print("  FAIL %s" % f)
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
