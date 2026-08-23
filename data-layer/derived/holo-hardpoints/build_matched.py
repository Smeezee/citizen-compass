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
import re
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


# The port types place_fleet.py knows how to place. Taken from its own KIND
# map rather than invented here, so the two cannot drift into disagreeing about
# what a weapon port is.
WEAPONY = ("Turret", "MissileLauncher", "WeaponDefensive", "WeaponGun",
           "TurretBase")


def pretty(hp):
    """`hardpoint_weapon_left_upper` -> `Weapon left upper`.

    The same shape ship_mounts.json's `where` field uses, so a reconstructed
    child port reads identically to a top-level one that came from the flatten.
    """
    s = re.sub(r"^\$", "", str(hp or "")).replace("_", " ").strip()
    s = re.sub(r"^hardpoint\s*", "", s, flags=re.I).strip()
    return (s[:1].upper() + s[1:]) if s else "Port"


def tree_ports(ships_json):
    """EVERY weapon port in every hull's Loadout tree, WITH ITS ANCESTRY.

    THIS IS THE DEFECT THIS FUNCTION EXISTS TO FIX, and it is worth stating
    exactly, because the order describes it the other way round.

    `ship_mounts.json` - the flatten C3 produced on 2026-08-10 and the only
    mount source the placement has ever had - contains ONLY TOP-LEVEL PORTS.
    Measured across ships.json: 2,555 weapon ports are top-level and 2,374 are
    CHILDREN, and not one of the 2,374 has ever reached place_fleet.py.

    So the turret guns were never "falling to the hull-centre default". They
    were not in the dataset at all. The Hammerhead has zero placed ports named
    `hardpoint_class_2` and zero points on the None target - because its 24
    turret guns are children of children and the flatten dropped them.

    The parent is not lost at the record write and not lost when place_fleet
    reads it. It is lost one step earlier than either: the ports themselves are
    absent, so there is nothing for a parent to be attached to.

    ANCESTRY, NOT JUST A PARENT. Each port carries:
        parent   its immediate parent's HardpointName, or null
        chain    every ancestor, outermost first
        turret   the OUTERMOST TurretBase ancestor, or null
    A gun inside a turret sits three deep - turret_side_back_right ->
    hardpoint_weapon_left_upper -> hardpoint_class_2 - and only the outermost
    of those says where on the ship it is. See place_fleet's inherit rule for
    why one level is not merely insufficient here but actively wrong.
    """
    out = {}
    for s in ships_json:
        cls = s.get("ClassName")
        if not cls:
            continue
        rows = []

        def walk(node, chain, turret):
            for entry in node or []:
                if not isinstance(entry, dict):
                    continue
                hp = entry.get("HardpointName")
                ty = (entry.get("Type") or "").split(".")[0]
                if hp and ty in WEAPONY:
                    rows.append({
                        "port": hp,
                        "where": pretty(hp),
                        "type": ty,
                        "size": entry.get("MaxSize") or entry.get("MinSize"),
                        "portid": entry.get("PortId"),
                        "parent": chain[-1] if chain else None,
                        "chain": list(chain),
                        "turret": turret,
                        "depth": len(chain),
                        "stock": entry.get("ClassName"),
                    })
                nxt = chain + ([hp] if hp else [])
                # The OUTERMOST turret wins: once inside one, everything below
                # belongs to it, however many mounts sit in between.
                t2 = turret if turret else (hp if ty == "TurretBase" else None)
                walk(entry.get("Loadout"), nxt, t2)

        walk(s.get("Loadout"), [], None)
        out[cls] = rows
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=os.path.join(HERE, "matched.json"))
    # THE CHILDREN ARE OFF BY DEFAULT, AND THAT IS A MEASURED TRADE, NOT AN
    # OVERSIGHT. Including them is what makes B5's turret inheritance fire at
    # all - it gains 160 markers on 5 more hulls - and it also takes fleet
    # crowding from 60 markers on 9 hulls to 216 on 21 by the proximity
    # metric, and 117/19 to 451/34 by the placement report's own. B6's
    # acceptance is that crowding must not get worse, and four numbers out of
    # four say it would.
    #
    # So the mechanism ships proven and switched off, the switch is one flag,
    # and the decision to take the trade is somebody's to make with the
    # numbers in front of them rather than mine to make by default.
    ap.add_argument("--with-children", action="store_true",
                    help="include child ports - turret guns and their mounts - "
                         "so B5's turret inheritance has something to fire on. "
                         "Gains 160 markers; costs crowding. Off by default.")
    ap.add_argument("--only-placed", action="store_true",
                    help="restrict to the 167 hulls already in "
                         "hardpoints_fleet.json instead of every candidate. "
                         "Reproduces the old input set.")
    args = ap.parse_args()

    for p_ in (MOUNTS, FLEET):
        if not os.path.exists(p_):
            sys.exit("MISSING INPUT: %s\nNothing was written." % p_)

    mounts = read_json(MOUNTS)
    fleet = read_json(FLEET)

    snap = newest_snapshot()
    if not (snap and os.path.exists(os.path.join(snap, "ships.json"))):
        sys.exit("NO SNAPSHOT. ships.json is where the port TREE lives, and "
                 "without it every child port and every parent link is "
                 "unavailable. Refusing to write a top-level-only input while "
                 "claiming to have looked. Nothing was written.")
    ships_json = read_json(os.path.join(snap, "ships.json"))
    print("snapshot          :", os.path.basename(snap))

    tree = tree_ports(ships_json)
    by_class = {(k or "").lower(): v for k, v in tree.items()}

    # ------------------------------------------------------------ candidates
    # THE 7 SKIPPED HULLS HAD NOWHERE TO BE SKIPPED FROM.
    #
    # The first version of this file built its input from hardpoints_fleet.json
    # - the 167 hulls that had ALREADY BEEN PLACED. So the proportion gate in
    # place_fleet.py ran against a set from which every refusal had already
    # been removed, and reported `skipped: 0`. A gate that cannot refuse
    # anything is not a gate, and this one reported a clean run for exactly
    # that reason.
    #
    # The candidate set is now every hull that has mount data AND a decoded
    # hull, which is what the sandbox run started from. The gate gets its
    # refusals back and reports them by name.
    geo_dir = os.environ.get("CC_GEO_DIR") or os.path.join(
        REPO, "data-layer", "derived", "hull-geometry")
    have_geo = set()
    if os.path.isdir(geo_dir):
        have_geo = {f[:-5] for f in os.listdir(geo_dir) if f.endswith(".json")}

    model_of = {name: rec["model"] for name, rec in fleet.items()}
    if not args.only_placed:
        # Ships in ship_mounts.json whose slug names a decoded hull. EXACT
        # match on the slug's own stem - no fuzzy matching anywhere near this.
        for name, rec in mounts.items():
            if name in model_of:
                continue
            slug = (rec.get("slug") or "")
            stem = slug.split("-", 1)[-1].replace("-", "_")
            for cand in (stem, stem.title(), slug.replace("-", "_")):
                if cand in have_geo:
                    model_of[name] = cand + ".glb"
                    break

    matched, stats = {}, {"top": 0, "child": 0, "turret_child": 0,
                          "no_tree": [], "no_geo": []}
    for name, src in mounts.items():
        model = model_of.get(name)
        if not model:
            continue
        stem = model[:-4]
        if stem not in have_geo:
            stats["no_geo"].append(name)
            continue
        rows = by_class.get((src.get("slug") or "").replace("-", "_").lower())
        if rows is None:
            stats["no_tree"].append(name)
            rows = []

        # THE TOP-LEVEL LIST IS TAKEN FROM ship_mounts.json UNCHANGED, and
        # ONLY the children are added from the tree.
        #
        # The first version of this re-derived the top level from ships.json
        # as well, filtered to weapon types. Measured, that DROPPED 518 PORTS
        # that the placement had been carrying - 138 weapon regen pools, 118
        # regen-pool-turrets, 29 weapon racks, four cm_launchers and more.
        # Some of those arguably are not hull-mounted weapons, but deciding
        # that is a different job from fixing a dropped parent, and doing both
        # in one change would have shipped a silent loss inside a fix.
        #
        # So: nothing that was in the input leaves it. The children arrive
        # alongside, carrying the ancestry the flatten never had.
        out_mounts = []
        for mt in src["mounts"]:
            m2 = dict(mt)
            m2["parent"] = None
            m2["chain"] = []
            m2["turret"] = None
            m2["depth"] = 0
            m2["from"] = "flatten"
            out_mounts.append(m2)
            stats["top"] += 1

        if args.with_children:
            for r in rows:
                if not r["depth"]:
                    continue          # top level already came from the flatten
                stats["child"] += 1
                if r["turret"]:
                    stats["turret_child"] += 1
                out_mounts.append({
                    "port": r["port"], "where": r["where"],
                    "type": r["type"], "size": r["size"],
                    "item": {"name": None, "type": None, "size": r["size"],
                             "mfr": None},
                    "parent": r["parent"], "chain": r["chain"],
                    "turret": r["turret"], "depth": r["depth"],
                    "from": "tree",
                })

        entry = dict(src)
        entry["mounts"] = out_mounts
        entry["model"] = model
        entry["bare"] = (fleet.get(name) or {}).get("bare") or name
        matched[name] = entry

    with io.open(args.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"matched": matched}, fh, separators=(",", ":"))

    print("ships             :", len(matched),
          "(was 167 in the placed set)" if not args.only_placed else "")
    print("mounts, top-level :", stats["top"], "(from the 2026-08-10 flatten, "
          "unchanged)")
    print("mounts, CHILDREN  :", stats["child"],
          "- of which inside a turret:", stats["turret_child"])
    if not args.with_children:
        print("                    (children OFF by default - see the comment "
              "on --with-children)")
    if stats["no_tree"]:
        print("ships with NO tree in ships.json (flat list used):",
              len(stats["no_tree"]))
        for n in stats["no_tree"][:8]:
            print("   ", n)
    if stats["no_geo"]:
        print("ships named a model with no decoded hull:", len(stats["no_geo"]))
    print("written           :", args.out)


if __name__ == "__main__":
    main()
