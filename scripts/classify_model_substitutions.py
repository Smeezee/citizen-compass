# -*- coding: utf-8 -*-
"""P2: which site rows render a hull that is not their own, decided by MESH.

WHY NAME COMPARISON IS NOT ENOUGH, AND WHY I ALMOST SHIPPED A WRONG ANSWER
=========================================================================
Sixteen site rows render a model folder whose name differs from the row's own
ship. The obvious reading is "sixteen ships are showing the wrong hull". It is
wrong, and it is wrong in BOTH directions:

  `A2 Hercules Starlifter` renders the folder `A2 Hercules`. Same ship, two
  labels. Nothing to fix.

  `Ballista Dunestalker` renders the base `Ballista` while a folder called
  `Anvil Ballista Dunestalker` sits on disk with its own model.glb. That looks
  exactly like the Cutlass Black defect - and the two files are BYTE-IDENTICAL,
  md5 1c939472048aacbce4c38bec7df19372. Pointing the row at its "own" folder
  would add a megabyte of duplicate payload and change nothing a visitor sees.

  `Cutlass Black` rendered `Cutlass Black Best In Show Edition 2949`, which the
  order calls a skin substituted for the base hull. It is byte-identical too.
  The picture was never wrong. What that mapping DID cost was the hardpoints:
  no `Cutlass_Black` geometry existed, so the placer could not see the ship at
  all. Repointing it is right, and "the visitor was shown a paint job" is not
  the reason.

  `Gladius` rendered `Gladius Valiant`. Those meshes DIFFER. That one really
  was the wrong hull.

So the classification here is made on the CONTENT of the files, never on how
close two names look. Rule 11: an unresolved row is reported unresolved.

THE THREE VERDICTS
    identical-mesh    the row's own folder exists and its mesh is byte-for-byte
                      the file already being rendered. Not a substitution.
    no-own-folder     no folder carries this row's name. The rendered folder is
                      simply what the library calls this hull.
    STAND-IN          the row's own folder exists and its mesh DIFFERS from
                      what is rendered. This is the defect. It must be fixed,
                      or declared in data-layer/model_substitutions.json with a
                      reason, and never left silent.

Rule 15: every open states its encoding.

Usage:
    venv/Scripts/python.exe scripts/classify_model_substitutions.py
    ... --json <path>
"""
import argparse
import hashlib
import io
import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import enumerate_ship_gaps as E  # noqa: E402

SHIPS_DIR = os.path.join(REPO, "sc-ships")
DECLARED = os.path.join(REPO, "data-layer", "model_substitutions.json")


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def md5(path):
    h = hashlib.md5()
    with io.open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def mesh_of(folder):
    """The scaled mesh a folder would contribute, or None.

    model_scaled.glb is what the compressor reads, so it is what a difference
    between two folders actually means. Comparing model.glb instead would call
    two folders different when the rescale had made them the same.
    """
    for fn in ("model_scaled.glb", "model.glb"):
        p = os.path.join(SHIPS_DIR, folder, fn)
        if os.path.exists(p):
            return md5(p), fn
    return None, None


def own_folder(name, folders):
    """The folder that IS this ship, by exact normalised name or by exactly one
    maker-prefixed or edition-suffixed extension of it. Ambiguity is refused -
    two candidates means we do not know, and guessing is what rule 11 forbids.
    """
    n = norm(name)
    exact = [f for f in folders if norm(f) == n]
    if len(exact) == 1:
        return exact[0], "exact"
    pre = [f for f in folders if norm(f).endswith(n) and norm(f) != n]
    if len(pre) == 1:
        return pre[0], "maker-prefixed"
    suf = [f for f in folders if norm(f).startswith(n) and norm(f) != n]
    if len(suf) == 1:
        return suf[0], "edition-suffixed"
    cands = pre + suf
    if cands:
        return None, "ambiguous (%d candidates)" % len(cands)
    return None, "none"


def classify(D=None):
    D = D or E.load()
    rows = E.analyse(D)
    folders = [f for f in sorted(os.listdir(SHIPS_DIR))
               if os.path.isdir(os.path.join(SHIPS_DIR, f))
               and not f.startswith("_") and not f.startswith(".")]
    out = []
    for r in rows:
        if not r["folder"] or norm(r["folder"]) == norm(r["name"]):
            continue
        own, how = own_folder(r["name"], folders)
        rendered_md5, _ = mesh_of(r["folder"])
        if own is None:
            verdict, own_md5 = "no-own-folder", None
        else:
            own_md5, _ = mesh_of(own)
            if own_md5 is None:
                verdict = "no-own-folder"
            elif own_md5 == rendered_md5:
                verdict = "identical-mesh"
            else:
                verdict = "STAND-IN"
        out.append(dict(name=r["name"], renders=r["folder"], own=own,
                        found_by=how, verdict=verdict,
                        rendered_md5=rendered_md5, own_md5=own_md5))
    return out, rows


def orphans(D, rows):
    """Direction B, with a reason attached to every one.

    "Built and orphaned" must not remain a silent state - so each unreachable
    file is matched back to a folder and to whether the site lists that ship at
    all. A file nobody can reach because the ship is not on the site is a
    different thing from one nobody can reach by mistake.
    """
    orph, _ = E.reverse(D, rows)
    names = {norm(r["name"]) for r in rows}
    out = []
    for f in orph:
        stem = f[:-4]
        listed = norm(stem) in names
        out.append(dict(
            file=f,
            reason=("a site row carries this ship's name but renders a "
                    "different folder - INVESTIGATE"
                    if listed else
                    "no site row carries this ship - it is an edition or "
                    "variant the ship list does not publish")))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    a = ap.parse_args(argv)

    D = E.load()
    subs, rows = classify(D)
    orph = orphans(D, rows)

    declared = {}
    if os.path.exists(DECLARED):
        declared = {d["name"]: d for d in E.rj(DECLARED).get("declared", [])}

    print("=" * 74)
    print("P2 - SITE ROWS RENDERING A FOLDER THAT IS NOT THEIR OWN NAME")
    print("     verdict decided on the MESH, never on how close two names look")
    print("=" * 74)
    for v in ("STAND-IN", "identical-mesh", "no-own-folder"):
        g = [s for s in subs if s["verdict"] == v]
        print("\n%-16s %d" % (v, len(g)))
        for s in sorted(g, key=lambda x: x["name"]):
            tail = ""
            if v == "STAND-IN":
                tail = "  own=%s%s" % (s["own"],
                                       "  DECLARED" if s["name"] in declared
                                       else "  *** UNDECLARED ***")
            elif v == "identical-mesh":
                tail = "  own=%s  md5 %s" % (s["own"], (s["own_md5"] or "")[:12])
            print("    %-28s renders %-34s%s" % (s["name"], s["renders"], tail))

    print("\n%s" % ("=" * 74))
    print("BUILT AND UNREACHABLE - %d files, each with a reason" % len(orph))
    for o in orph:
        print("    %-44s %s" % (o["file"], o["reason"]))

    if a.json:
        with io.open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(dict(substitutions=subs, orphans=orph), fh,
                      indent=1, sort_keys=True, ensure_ascii=False)
        print("\nwrote %s" % a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
