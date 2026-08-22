"""
Rebuild `matched.json` - place_fleet.py's input - from what IS in this repo.

WHY THIS EXISTS
===============
`place_fleet.py` was written and run in a cloud sandbox on 2026-08-10. It read
`/home/claude/fleet/matched.json` and `/home/claude/fleet/geo`. The sandbox is
gone, neither file was ever in this repo, and `hardpoints_fleet.json` is the
committed OUTPUT of a run nobody can reproduce.

That was tolerable while nothing needed re-deriving. B5 needs a BEFORE and an
AFTER, which means the derivation has to run again, here.

Both inputs turn out to be recoverable:

  geometry   235 hulls were decoded into data-layer/derived/hull-geometry/ on
             2026-08-22 while answering the G3 matcher control. That is the
             same thing /home/claude/fleet/geo held, produced by this repo's
             own vendored DRACO decoder.
  matched    `ship_mounts.json` carries every field place_fleet.py reads except
             the model filename, and `hardpoints_fleet.json` records which
             model each ship was matched to. Joining them reconstructs the
             input exactly.

AND THE JOIN IS CHECKED RATHER THAN ASSUMED. Every one of the 167 ships in
hardpoints_fleet.json is present in ship_mounts.json, and for every one of them
the mount count equals the hardpoint count - so nothing was filtered between
matched.json and the placement, and this reconstruction is not quietly a
different input wearing the same name.

THE REAL PROOF IS DOWNSTREAM. Running the UNCHANGED place_fleet.py against this
file must reproduce the committed hardpoints_fleet.json. If it does not, the
reconstruction is wrong and any before/after measured against it is worthless -
which is a thing to report, not to paper over.

THE PARENT CHAIN, WHICH IS THE POINT OF B5.
`ship_mounts.json` has no parent field: it is a flat list, and the flatten that
produced it dropped the tree. So the parent hardpoint name is read here,
straight out of the scunpacked snapshot's `ships.json`, whose `Loadout[]` IS
the tree. A mount with no parent gets an explicit null rather than a missing
key - "no parent" and "we did not look" must not be the same value.

Rule 15: every open states its encoding.

Usage:
    venv/Scripts/python.exe data-layer/derived/holo-hardpoints/build_matched.py
    ... --out <path>        default: matched.json beside this script
"""
import argparse
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
MOUNTS = os.path.join(HERE, "ship_mounts.json")
FLEET = os.path.join(HERE, "hardpoints_fleet.json")
SNAPDIR = os.path.join(REPO, "data-layer", "external-sources",
                       "scunpacked-data", "snapshots")


def read_json(path):
    with io.open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def newest_snapshot():
    """The snapshot build_loadout_data.py reads, chosen the same way: newest.

    Named rather than hardcoded so this cannot silently drift onto a different
    snapshot from the one the ship page was built from.
    """
    if not os.path.isdir(SNAPDIR):
        return None
    snaps = sorted(d for d in os.listdir(SNAPDIR)
                   if os.path.isdir(os.path.join(SNAPDIR, d)))
    return os.path.join(SNAPDIR, snaps[-1]) if snaps else None


def parent_names(ships_json):
    """{ship ClassName: {hardpoint name: parent hardpoint name or None}}.

    ONE LEVEL, FROM A REAL PARENT. The order is explicit that this is not to be
    extended into guessing from siblings or anything else, so what is recorded
    is exactly the immediate parent's HardpointName and nothing inferred.

    A name is not unique within a ship - the Polaris has thirty ports called
    MEC - so a name that appears more than once with DIFFERENT parents is
    recorded as None rather than as one of them. A coin toss dressed as data is
    worse here than an absence, because the absence just means the child's own
    name has to carry the position, which is the behaviour that already exists.
    """
    out = {}
    for s in ships_json:
        cls = s.get("ClassName")
        if not cls:
            continue
        seen = {}

        def walk(node, parent_hp):
            for entry in node or []:
                if not isinstance(entry, dict):
                    continue
                hp = entry.get("HardpointName")
                if hp:
                    if hp in seen and seen[hp] != parent_hp:
                        seen[hp] = "\x00CONFLICT"
                    elif hp not in seen:
                        seen[hp] = parent_hp
                walk(entry.get("Loadout"), hp or parent_hp)

        walk(s.get("Loadout"), None)
        out[cls] = {k: (None if v == "\x00CONFLICT" else v)
                    for k, v in seen.items()}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=os.path.join(HERE, "matched.json"))
    args = ap.parse_args()

    for p in (MOUNTS, FLEET):
        if not os.path.exists(p):
            sys.exit("MISSING INPUT: %s\nNothing was written." % p)

    mounts = read_json(MOUNTS)
    fleet = read_json(FLEET)

    snap = newest_snapshot()
    ships_json = None
    if snap and os.path.exists(os.path.join(snap, "ships.json")):
        ships_json = read_json(os.path.join(snap, "ships.json"))
        print("snapshot          :", os.path.basename(snap))
    else:
        print("snapshot          : NOT FOUND - parent names will be null")

    parents = parent_names(ships_json) if ships_json else {}
    # THE BRIDGE IS THE SLUG, NOT THE DISPLAY NAME.
    #
    # ships.json is keyed by ClassName; ship_mounts.json by display name and a
    # slug. Matching on the ship's own `Name` field looked obvious and joined
    # 18 of 167 - because ships.json's Name is the marketing name ("ATLS Orange
    # Line") and ship_mounts.json's key is the short one ("Hammerhead"). The
    # slug is the same string in both worlds up to punctuation:
    # aegs-hammerhead -> AEGS_Hammerhead. That joins 278 of 278.
    #
    # Recorded because an 18-of-167 join is exactly the kind of thing that
    # would have shipped as "parents are mostly null, upstream must not have
    # them" if the count had not been printed.
    by_class = {}
    for s in (ships_json or []):
        cls = (s.get("ClassName") or "")
        if cls and cls in parents:
            by_class[cls.lower()] = parents[cls]

    matched, no_parent_map, with_parent, total_mounts = {}, [], 0, 0
    for name, rec in fleet.items():
        src = mounts.get(name)
        if not src:
            sys.exit("ship in hardpoints_fleet.json but not ship_mounts.json: "
                     "%s\nThe reconstruction would be missing its mounts. "
                     "Nothing was written." % name)
        pmap = by_class.get((src.get("slug") or "").replace("-", "_").lower())
        if pmap is None:
            no_parent_map.append(name)
            pmap = {}
        out_mounts = []
        for mt in src["mounts"]:
            total_mounts += 1
            par = pmap.get(mt.get("port"))
            if par:
                with_parent += 1
            m2 = dict(mt)
            m2["parent"] = par or None   # EXPLICIT null, never a missing key
            out_mounts.append(m2)
        entry = dict(src)
        entry["mounts"] = out_mounts
        entry["model"] = rec["model"]
        entry["bare"] = rec.get("bare") or name
        matched[name] = entry

    with io.open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"matched": matched}, fh, separators=(",", ":"))

    print("ships             :", len(matched))
    print("mounts            :", total_mounts)
    print("mounts with a parent hardpoint:", with_parent)
    if no_parent_map:
        print("ships with NO parent map found in ships.json:",
              len(no_parent_map))
        for n in no_parent_map[:8]:
            print("   ", n)
    print("written           :", args.out)


if __name__ == "__main__":
    main()
