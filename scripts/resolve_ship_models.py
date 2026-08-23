#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
H2 / H3 / H5 - which ship each model file belongs to, and which ships have no
geometry anywhere.

WHY THIS EXISTS
===============
    316  ships in the data
    235  .glb model FILES on disk
    201  ships wired to a model
    115  ships rendering NOTHING
     40  model files wired to no ship at all

Forty models we already own, pointing at nobody - including Liberator, Kraken,
Galaxy, Nautilus, Orion, Pioneer, Endeavor, Hull_D and Hull_E. That is a
NAME-MATCHING FAILURE, NOT A MISSING ASSET, and it is the same defect that hid
the Ares Inferno for a week.

NO FUZZY MATCHING. NONE. ANYWHERE.
==================================
This is the standing rule of the order and it has already produced four
confident wrong pairs on this exact data: Dragonfly Black -> Yellowjacket,
E1 Spirit -> C1 Spirit, G12a -> 125a, Zeus MR -> Zeus ES. In the real pipeline
that bolts the wrong hull onto four ships and nothing catches it.

So there are exactly three ways a pair can be made here, in this order, and
nothing else is tried:

    1. EXACT match on the normalised display name
    2. EXACT match on the normalised ClassName
    3. EDITION -> its BASE HULL, where "edition of" is decided STRUCTURALLY:
       ClassName A is an edition of ClassName B when A starts with B plus an
       underscore. DRAK_Caterpillar_Pirate is an edition of DRAK_Caterpillar
       because of how the strings are built, not because somebody read them.

Normalising is lowercasing and dropping non-alphanumerics. `Hull_D` and
`hull d` are the same string; `Zeus_Mk_II_MR` and `Zeus_Mk_II_ES` are not, and
no amount of similarity will make them so. A file that matches nothing STAYS
ORPHANED AND IS REPORTED.

AND EVERY PAIR IS CHECKED ON MANUFACTURER, INDEPENDENTLY.
A Drake file matched to an Aegis ship is wrong however good the name looked.
The manufacturer is not used to FIND the pair - it is used to refuse one.

Rule 15: every open states its encoding.

Usage:
    venv/Scripts/python.exe scripts/resolve_ship_models.py
        [--write]    also write data-layer/model_overrides.json
        [--json P]   write the full report to P
"""
import argparse
import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "testing", "_src")
MODELS_DIR = os.path.join(ROOT, "testing", "_deploy", "models")
SNAPDIR = os.path.join(ROOT, "data-layer", "external-sources",
                       "scunpacked-data", "snapshots")
FANKIT = os.path.join(os.path.expanduser("~"), "Downloads",
                      "Fankit_2025_11_19", "Fankit_2025_11_19",
                      "02_HOLOVIEWERS")
OVERRIDES = os.path.join(ROOT, "data-layer", "model_overrides.json")


def read(path):
    with io.open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def norm(s):
    """Lowercase, alphanumerics only. Canonicalising, NOT fuzzy.

    Two strings either reduce to the same thing or they do not. Nothing here
    scores a similarity, measures an edit distance or picks a best candidate -
    those are the operations that produced the four wrong pairs.
    """
    return re.sub(r"[^a-z0-9]+", "", str(s or "").lower())


def newest_snapshot():
    if not os.path.isdir(SNAPDIR):
        return None
    d = sorted(x for x in os.listdir(SNAPDIR)
               if os.path.isdir(os.path.join(SNAPDIR, x)))
    return os.path.join(SNAPDIR, d[-1]) if d else None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    gen = read(os.path.join(SRC, "loadout_data.gen.js"))
    SHIPS = json.loads(re.search(r"^const LOADOUT_SHIPS=(.*);$",
                                 gen, re.M).group(1))
    mm = read(os.path.join(SRC, "loadout_model.gen.js"))
    WIRED = json.loads(re.search(r"^const LOADOUT_MODEL=(.*);$",
                                 mm, re.M).group(1))

    files = sorted(os.path.basename(p)
                   for p in glob.glob(os.path.join(MODELS_DIR, "*.glb")))
    used = set(WIRED.values())
    orphans = [f for f in files if f not in used]

    snap = newest_snapshot()
    mfr_of = {}
    if snap and os.path.exists(os.path.join(snap, "ships.json")):
        for s in json.loads(read(os.path.join(snap, "ships.json"))):
            cls = s.get("ClassName")
            if cls:
                mfr_of[cls] = (s.get("Manufacturer") or {}).get("Name") \
                    if isinstance(s.get("Manufacturer"), dict) \
                    else s.get("Manufacturer")

    def ship_mfr_raw(cls):
        return (SHIPS.get(cls, {}).get("m") or mfr_of.get(cls) or "").strip()

    def ship_mfr(cls):
        return ship_mfr_raw(cls)

    # ---------------------------------------------------------- the indexes
    #
    # AND THE CANONICALISATION THAT MAKES ANY OF THIS WORK, which is the whole
    # defect in one line: THE MODEL FILES ARE BARE SHIP NAMES AND THE SHIP
    # RECORDS ARE NOT. `Kraken.glb` against "Drake Kraken"; `Hull_D.glb`
    # against "MISC Hull D". A first pass matching the two raw strings resolved
    # ZERO of the 40 orphans, which is exactly how forty models we own came to
    # be pointing at nobody.
    #
    # STRIPPING A KNOWN PREFIX IS NOT FUZZY MATCHING. The manufacturer is an
    # independent field on the ship record; removing that exact string from the
    # front of that ship's own name is canonicalisation, the same kind of
    # operation as lowercasing. Nothing here scores a similarity or picks a
    # best candidate. Two strings reduce to the same thing or they do not.
    #
    # AND IT MAKES COLLISIONS POSSIBLE, so collisions are REFUSED. Two
    # manufacturers can both have a "Ranger"; a stem that reduces to more than
    # one ship is reported AMBIGUOUS and left orphaned, never assigned to
    # whichever came first.
    def bare_name(cls):
        n = SHIPS.get(cls, {}).get("n") or ""
        m = ship_mfr_raw(cls)
        if m and norm(n).startswith(norm(m)):
            return norm(n)[len(norm(m)):]
        return norm(n)

    def bare_class(cls):
        # ClassName carries a maker CODE rather than a name: DRAK_Kraken.
        parts = str(cls).split("_", 1)
        return norm(parts[1]) if len(parts) == 2 else norm(cls)

    by_name, by_class = {}, {}
    for cls, sh in SHIPS.items():
        for key in {norm(sh.get("n")), bare_name(cls)}:
            if key:
                by_name.setdefault(key, []).append(cls)
        for key in {norm(cls), bare_class(cls)}:
            if key:
                by_class.setdefault(key, []).append(cls)
    # A key that reduces to several ships is poison, not a match.
    for d in (by_name, by_class):
        for k in list(d):
            d[k] = sorted(set(d[k]))

    def mfr_agrees(cls, stem):
        """The pair is REFUSED unless the file's own name carries the ship's
        manufacturer, or carries no manufacturer at all.

        Independent of the thing that made the match: a Drake file matched to
        an Aegis ship is wrong however good the name looked. Where the file
        name says nothing about a maker - `Kraken.glb` - there is nothing to
        disagree with, and that is recorded as `unstated` rather than counted
        as agreement.
        """
        m = ship_mfr(cls)
        if not m:
            return "no-ship-manufacturer"
        n = norm(stem)
        makers = {norm(x) for x in
                  {ship_mfr(c) for c in SHIPS} if x}
        found = [x for x in makers if x and x in n]
        if not found:
            return "unstated"
        return "agree" if norm(m) in n else "DISAGREE"

    # The ships CIG has not built. They carry a name and a maker and NOTHING
    # else, which is exactly why a model for one cannot be wired to anything.
    UNREL = {}
    for u in json.loads(re.search(r"^const LOADOUT_UNRELEASED=(.*);$",
                                  gen, re.M).group(1)):
        if isinstance(u, dict) and u.get("n"):
            UNREL[norm(u["n"])] = u

    resolved, unresolved, unreleased_hit = [], [], []
    for f in orphans:
        stem = f[:-4]
        hit, how = None, None
        cands = by_name.get(norm(stem)) or []
        if len(cands) == 1:
            hit, how = cands[0], "exact display name"
        elif len(cands) > 1:
            unresolved.append((f, "AMBIGUOUS: %d ships share that name (%s)"
                               % (len(cands), ", ".join(cands[:3]))))
            continue
        if not hit:
            cands = by_class.get(norm(stem)) or []
            if len(cands) == 1:
                hit, how = cands[0], "exact ClassName"
            elif len(cands) > 1:
                unresolved.append((f, "AMBIGUOUS on ClassName"))
                continue
        if not hit:
            # A THIRD ANSWER, AND IT IS THE COMMON ONE.
            #
            # Most of these files are not mis-named - they are models for ships
            # CIG HAS NOT BUILT. `Crucible`, `Endeavor`, `Expanse`, `Genesis`,
            # `Odyssey`, `Kraken`, `Galaxy`, `Orion`, `Pioneer`: concept hulls
            # with no entry in ships.json at all, because they have no
            # components to describe. There is no ship page to wire them to.
            #
            # Calling that "unresolved" alongside a genuine name mismatch would
            # blur the two most useful facts apart from each other, so it gets
            # its own bucket and its own sentence.
            un = UNREL.get(norm(stem))
            if un:
                unreleased_hit.append((f, un))
                continue
            # AND THE NEAR MISSES GO TO A HUMAN, NOT TO THE PIPELINE.
            #
            # The order names six pairs that "match by eye" -
            # Caterpillar_Pirate_Edition, Hammerhead_Best_In_Show_Edition_2949
            # and so on. They do NOT match exactly: the file says "Edition" and
            # the ship does not. Under the no-fuzzy-matching rule they are
            # refused, and refusing them is the right call, because "by eye" is
            # what produced Dragonfly Black -> Yellowjacket.
            #
            # What is useful is to SAY WHICH SHIP a person should look at. That
            # is printed as a suggestion, is never written to the overrides,
            # and is never counted as resolved.
            sug = [c for c in SHIPS
                   if bare_name(c) and (bare_name(c) in norm(stem)
                                        or norm(stem) in bare_name(c))]
            sug = [c for c in sug if norm(ship_mfr(c)) and not WIRED.get(c)]
            unresolved.append((f, "no exact match" + (
                "; a human should look at " + ", ".join(sorted(sug)[:3])
                if sug else "; nothing close enough to name")))
            continue
        agree = mfr_agrees(hit, stem)
        if agree == "DISAGREE":
            unresolved.append(
                (f, "REFUSED: name matched %s but the manufacturer disagrees "
                    "(%s)" % (hit, ship_mfr(hit))))
            continue
        if WIRED.get(hit):
            unresolved.append((f, "matched %s, which already has %s"
                               % (hit, WIRED[hit])))
            continue
        resolved.append({"file": f, "cls": hit, "how": how,
                         "mfr": ship_mfr(hit), "mfr_check": agree})

    # ------------------------------------------------- H3: editions -> base
    classes = sorted(SHIPS)
    editions = []
    for cls in classes:
        if WIRED.get(cls):
            continue
        base = None
        for other in classes:
            if other != cls and cls.startswith(other + "_"):
                if base is None or len(other) > len(base):
                    base = other
        if base:
            own = next((r for r in resolved if r["cls"] == cls), None)
            editions.append({
                "cls": cls, "base": base,
                "base_model": WIRED.get(base),
                "own_model": own["file"] if own else None,
                "mfr_ok": norm(ship_mfr(cls)) == norm(ship_mfr(base)),
            })

    # ------------------------------------------------------ H4: the Fan Kit
    fankit = []
    if os.path.isdir(FANKIT):
        for p in sorted(glob.glob(os.path.join(FANKIT, "*.ctm"))):
            stem = os.path.splitext(os.path.basename(p))[0]
            cands = by_name.get(norm(stem)) or []
            fankit.append({
                "file": os.path.basename(p),
                "cls": cands[0] if len(cands) == 1 else None,
                "why": ("exact display name" if len(cands) == 1
                        else ("AMBIGUOUS" if cands else "no exact match")),
                "already_has_model": bool(cands and WIRED.get(cands[0])),
            })

    # --------------------------------------------- H5: the honest remainder
    have = dict(WIRED)
    for r in resolved:
        have[r["cls"]] = r["file"]
    for e in editions:
        if e["own_model"]:
            have[e["cls"]] = e["own_model"]
        elif e["base_model"]:
            have.setdefault(e["cls"], e["base_model"])
    fan_for = {f["cls"] for f in fankit if f["cls"] and not f["already_has_model"]}
    missing = []
    for cls in classes:
        if cls in have or cls in fan_for:
            continue
        missing.append({"cls": cls, "name": SHIPS[cls].get("n"),
                        "mfr": ship_mfr(cls),
                        "ports": len(SHIPS[cls].get("slots") or [])})

    # ------------------------------------------------------------- report
    print("=" * 70)
    print("H2 - THE ORPHAN MODEL FILES")
    print("=" * 70)
    print("model files on disk        : %d" % len(files))
    print("wired to a ship already    : %d" % len(used))
    print("ORPHANED                   : %d" % len(orphans))
    print("  resolved by exact match  : %d" % len(resolved))
    print("  a ship CIG HAS NOT BUILT : %d" % len(unreleased_hit))
    print("  left unresolved          : %d" % len(unresolved))
    print()
    for r in resolved:
        print("  %-46s -> %-28s  %s" % (r["file"], r["cls"], r["how"]))
    print()
    print("  MODELS FOR SHIPS THAT DO NOT EXIST IN THE GAME DATA.")
    print("  Not mis-named - there is no ship page to wire them to:")
    for f, u in unreleased_hit:
        print("    %-46s %s (%s)" % (f, u.get("n"), u.get("m")))
    print()
    print("  UNRESOLVED - reported, never guessed:")
    for f, why in unresolved:
        print("    %-46s %s" % (f, why))

    print()
    print("=" * 70)
    print("H3 - EDITIONS AND THEIR BASE HULLS")
    print("=" * 70)
    own = [e for e in editions if e["own_model"]]
    base = [e for e in editions if not e["own_model"] and e["base_model"]]
    none = [e for e in editions if not e["own_model"] and not e["base_model"]]
    print("editions with NO model of their own : %d" % len(editions))
    print("  ...that have their OWN file       : %d  (that file wins)" % len(own))
    print("  ...taking their base hull's model : %d" % len(base))
    print("  ...whose base has no model either : %d" % len(none))
    for e in own[:12]:
        print("    OWN   %-34s %s" % (e["cls"], e["own_model"]))
    for e in base[:12]:
        print("    BASE  %-34s <- %s (%s)"
              % (e["cls"], e["base"], e["base_model"]))
    bad = [e for e in editions if not e["mfr_ok"]]
    print("  editions whose manufacturer differs from their base: %d" % len(bad))
    for e in bad[:6]:
        print("    %s vs %s" % (e["cls"], e["base"]))

    print()
    print("=" * 70)
    print("H4 - THE FAN KIT LIBRARY")
    print("=" * 70)
    if not os.path.isdir(FANKIT):
        print("NOT PERFORMED: no Fan Kit at %s" % FANKIT)
    else:
        print("%d .ctm models found" % len(fankit))
        for f in fankit:
            tag = ("already has a model" if f["already_has_model"]
                   else ("-> " + f["cls"] if f["cls"] else f["why"]))
            print("  %-40s %s" % (f["file"], tag))

    print()
    print("=" * 70)
    print("H5 - SHIPS WITH NO GEOMETRY IN ANY OF THE THREE LIBRARIES")
    print("=" * 70)
    print("THIS IS THE NUMBER. %d ships." % len(missing))
    print()
    for m in sorted(missing, key=lambda x: (x["mfr"] or "", x["name"] or "")):
        print("  %-34s %-26s %3d ports" % (m["name"], m["mfr"], m["ports"]))

    report = {"orphans": orphans, "resolved": resolved,
              "unreleased": [{"file": f, "ship": u.get("n"), "mfr": u.get("m")}
                             for f, u in unreleased_hit],
              "unresolved": [{"file": f, "why": w} for f, w in unresolved],
              "editions": editions, "fankit": fankit, "missing": missing}
    if args.json:
        with io.open(args.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(report, fh, indent=1)
        print("\nreport written to", args.json)

    if args.write:
        ov = {}
        for r in resolved:
            ov[r["cls"]] = {"model": r["file"], "how": r["how"],
                            "source": "orphan file, exact match"}
        for e in editions:
            if e["own_model"]:
                ov[e["cls"]] = {"model": e["own_model"], "how": "own file",
                                "source": "edition with its own export"}
            elif e["base_model"] and e["mfr_ok"]:
                ov[e["cls"]] = {"model": e["base_model"],
                                "how": "base hull " + e["base"],
                                "source": "shared hull"}
        with io.open(OVERRIDES, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(ov, fh, indent=1, sort_keys=True)
        print("\n%d overrides written to %s" % (len(ov), OVERRIDES))

    return 0


if __name__ == "__main__":
    sys.exit(main())
