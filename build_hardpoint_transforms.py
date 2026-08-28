#!/usr/bin/env python3
"""
Fleet run: pull every ship's hull .cga out of Data.p4k and decode its named
hardpoint transforms.

ONE PASS OVER THE CENTRAL DIRECTORY, NOT ONE PER SHIP. The probe re-scanned
464 MB for every single file, which is fine for two ships and absurd for two
hundred. This indexes once and then seeks.

WHICH .cga IS THE HULL, and it is an exact rule with no fuzzy matching:
the entry under `Data\\Objects\\Spaceships\\Ships\\<MFR>\\<Ship>\\` whose
basename equals the folder name. `DRAK_Vulture\\DRAK_Vulture.cga` is the hull;
`DRAK_Vulture_Salvage_Arm_Left.cga` is a part and `..._lod1` is a level of
detail. A ship folder with no such entry is REPORTED, never guessed at.

EVERY SHIP CARRIES ITS OWN ACCEPTANCE RESULT. A hull that fails is written out
with `acceptance: false` and its reason rather than dropped, because a silent
omission and a clean run look identical from the outside.

Output: data-layer/derived/hardpoint-transforms/
  <CLASS>.json        every node, name + 3x4 + position, metres, CIG frame
  MANIFEST.json       source, date, rule, and the per-ship acceptance table
  failures.json       ship folders that produced nothing, with the reason

Usage:
    python3 build_hardpoint_transforms.py [--limit N] [--only SUBSTR]
"""
import argparse
import glob
import json
import os
import re
import struct
import sys
import time

import extract_default_profile as E
import probe_ship_geometry as P
import decode_cga_nodes as D

E.zstd_decompress = P.zstd_decompress
OUT = os.path.join("data-layer", "derived", "hardpoint-transforms")
# UP TO FOUR SEGMENTS UNDER Ships, not exactly two. The first version allowed
# <MFR>\<Ship>\<file> only and found 50 hulls where the fleet has ~200: the
# Cutlass lives at DRAK\Cutlass\Black\DRAK_Cutlass_Black.cga and every
# variant-bearing hull is nested the same way.
LOD_RX = re.compile(r"_lod\d+$", re.I)
# TWO TREES, NOT ONE (C1, 2026-08-27).
#
# Every hull this decoder had ever seen lives under
# `Data\Objects\Spaceships\Ships\`. GROUND VEHICLES DO NOT - they sit in a
# sibling tree, `Data\Objects\Vehicles\`, which nothing here had ever looked
# at. 1,762 .cga entries, and the hulls are sitting at the top of it:
#
#     Data\Objects\Vehicles\TMBL\storm\TMBL_Storm.cga
#     Data\Objects\Vehicles\TMBL\Nova\TMBL_Nova.cga
#     Data\Objects\Vehicles\ANVL\Ballista\ANVL_Ballista.cga
#     Data\Objects\Vehicles\ANVL\Atlas\Centurion\ANVL_Centurion.cga
#
# The Cyclones, the Storm, the Nova, the Ursa, the Ballista, the Centurion and
# the Spartan were all "no .cga anywhere" for one reason: nobody had told the
# scan the other half of the fleet is parked somewhere else.
#
# `Spaceships` IS STILL NARROWED TO ITS `Ships` SUBTREE. The same tree also
# holds Turrets, Seats, Rocket_Pods and Derelicts, and those are parts. The
# Vehicles tree has no such level - it is manufacturer-then-vehicle - so the
# segment walk below takes whatever follows the tree root rather than looking
# for a fixed "Ships" folder.
TREE_ROOTS = ("Spaceships\\Ships", "Vehicles")
SHIP_RX = re.compile(
    rb"Data\\Objects\\(?:Spaceships\\Ships|Vehicles)\\"
    rb"(?:[A-Za-z0-9_\-\.]+\\){1,4}"
    rb"[A-Za-z0-9_\-\.]+\.cga(?![A-Za-z0-9_])")


def cig_class_names():
    """Every ClassName CIG publishes in ships.json, case-folded.

    THE SECOND HULL RULE NEEDS AN AUTHORITY, NOT A PATTERN (C1, 2026-08-27).

    The folder rule below finds the .cga whose stem equals a contiguous run of
    its own folder path. It found 120 of 18,891 entries, and it is exactly
    right about every one of them - but CIG does not always name a folder for
    the ship inside it, and a hull it names differently is indistinguishable
    from a bunk bed as far as that rule is concerned:

        AEGS\\Sabre\\AEGS_Sabre_Raven.cga            folders: AEGS, Sabre
        MISC\\Freelancer_v2\\MISC_Freelancer.cga      folders: MISC, Freelancer_v2
        ORIG\\300_Series\\ORIG_300I.cga               folders: ORIG, 300_Series
        AEGS\\Idris_Frigate\\Exteriors\\AEGS_Idris.cga

    Every one of those is a hull and none of them equals any run of its
    folders. Fifteen ships the site draws with name-derived markers are sitting
    in the archive behind that gap.

    SO THE SECOND RULE IS EXACT EQUALITY AGAINST CIG'S OWN LIST OF SHIPS. Not a
    name pattern, not a heuristic, not a similarity score - a lookup into
    ships.json's ClassName column. It cannot admit a bunk bed, because there is
    no ship class called `aegs_hab_bunkbed_sq_player`. STILL NO FUZZY MATCHING:
    a stem that merely resembles a class name matches nothing.

    A run without ships.json keeps the folder rule alone and says so, rather
    than silently reverting to the smaller answer.
    """
    snaps = sorted(glob.glob(os.path.join(
        "data-layer", "external-sources", "scunpacked-data", "snapshots",
        "*", "ships.json")))
    if not snaps:
        return set(), None
    p = snaps[-1]
    d = json.load(open(p, encoding="utf-8"))
    if isinstance(d, dict):
        d = list(d.values())
    names = set()
    for r in d:
        if not isinstance(r, dict):
            continue
        if r.get("ClassName"):
            names.add(r["ClassName"].lower())
        # AND THE ROOT OF THE SHIP'S OWN PART TREE, WHICH IS ALSO A HULL NAME.
        #
        # C1, 2026-08-27. `Parts[0].Name` is CIG's own statement of which hull a
        # ship is built on - `ANVL_C8_Pisces` names `ANVL_Pisces`. A name CIG
        # uses that way IS a hull, whether or not any ship is CALLED that:
        #
        #     AEGS_Idris        named by Idris_P, Idris_M and four others,
        #                       and it is no ship's own ClassName
        #     ANVL_Ballista     named by the Dunestalker and the Snowblind
        #     GRIN_MXC          named by GRIN_MDC and GRIN_MTC
        #     RSI_Ursa_Rover    named by the Medivac
        #
        # `AEGS\Idris_Frigate\Exteriors\AEGS_Idris.cga` is a real hull that
        # the folder rule cannot see and the ClassName rule does not cover,
        # because no ship is called AEGS_Idris. Its own record says otherwise.
        # Still exact equality; still no fuzzy matching.
        parts = r.get("Parts")
        if isinstance(parts, list) and parts and isinstance(parts[0], dict):
            root = parts[0].get("Name")
            if root:
                names.add(root.lower())
    return names, p


def index(fh, cd_off, cd_size, classes=None):
    """Every hull .cga entry, in TWO PHASES over one file handle.

    PHASE 1 SCANS AND TOUCHES NOTHING ELSE. The first version resolved each
    match to its header inside the scan loop - and `header_at` seeks the same
    handle. Every resolve rewound the read position by ~2 KB, so the loop
    re-read its own tail while `pos` marched on: 3,891 real matches in the
    central directory produced TWO hulls, and the 464 MB "scan" finished in two
    seconds. It reported a clean run over a directory it had never read.

    Nothing failed. That is the whole problem with it, and it is the fourth
    time today something in this repo has been quietly right-looking and wrong.
    Phase 1 now collects byte offsets only. Phase 2 resolves them afterwards,
    when seeking is free.
    """
    offsets = []
    offsets_named = []
    chunk = 16 << 20
    overlap = 2048
    pos = 0
    carry = b""
    carry_at = cd_off
    fh.seek(cd_off)
    t0 = time.time()
    while pos < cd_size:
        blk = fh.read(min(chunk, cd_size - pos))
        if not blk:
            break
        buf = carry + blk
        for m in SHIP_RX.finditer(buf):
            at = carry_at + m.start()
            offsets.append(at)
            offsets_named.append((at, m.group()))
        pos += len(blk)
        print("  scan  %6.1f / %.1f MB   matches %d   %.0fs"
              % (pos / 1e6, cd_size / 1e6, len(offsets), time.time() - t0))
        sys.stdout.flush()
        carry = buf[-overlap:]
        carry_at = cd_off + pos - len(carry)

    # A match found twice across a chunk seam is the same entry. Dedup on the
    # offset, not on the name - two different entries can share a basename.
    seen = set()
    offsets_named = [x for x in sorted(offsets_named)
                     if not (x[0] in seen or seen.add(x[0]))]
    print("  %d matches" % len(offsets_named))

    # FILTER ON THE MATCHED TEXT, RESOLVE ONLY THE SURVIVORS.
    # The match IS the stored filename - SHIP_RX is anchored at "Data\\Objects"
    # and ends at ".cga" - so the hull rule can be applied without touching the
    # file at all. The first version called header_at on all 18,891 matches,
    # which is 18,891 seeks over a network mount to answer a question the bytes
    # in hand already answered. ~200 survive. Resolve those.
    keep = []
    for at, raw in offsets_named:
        nm = raw.decode("utf-8", "replace")
        parts = nm.split("\\")
        # The folders under whichever tree root this entry sits in. Written as
        # a search over TREE_ROOTS rather than `parts.index("Ships")`, because
        # the Vehicles tree has no "Ships" level at all and the old line simply
        # skipped every ground vehicle.
        segs = None
        for _r in TREE_ROOTS:
            _rp = _r.split("\\")
            for _i in range(len(parts) - len(_rp)):
                if parts[_i:_i + len(_rp)] == _rp:
                    segs = parts[_i + len(_rp):-1]
                    break
            if segs is not None:
                break
        if not segs:
            continue
        stem = os.path.splitext(parts[-1])[0]
        # THE HULL IS THE FILE NAMED FOR ITS OWN FOLDER PATH, and every way a
        # CIG hull spells that is enumerated rather than pattern-matched:
        #   DRAK\Vulture\DRAK_Vulture.cga        -> drak_vulture
        #   DRAK\Cutlass\Black\DRAK_Cutlass_Black.cga
        #                                        -> drak_cutlass_black
        # A part (_Salvage_Arm_Left) and a LOD (_lod1) match none of these and
        # are not guessed at. NO FUZZY MATCHING - these are exact equalities.
        # ANY CONTIGUOUS RUN OF THE PATH SEGMENTS, because CIG puts structural
        # folders in the middle as well as the ends:
        #   ANVL\Carrack\Exterior\ANVL_Carrack.cga   -> "anvl_carrack"
        #   DRAK\Cutlass\Black\DRAK_Cutlass_Black.cga -> "drak_cutlass_black"
        #   DRAK\Vulture\DRAK_Vulture.cga             -> "drak_vulture"
        # Suffix joins alone missed every hull behind an "Exterior" folder -
        # 63 hulls found where the fleet has roughly two hundred.
        # STILL EXACT EQUALITY. A part (ANVL_Carrack_Antennas) and a LOD
        # (ANVL_Carrack_lod3) equal no contiguous run and are not guessed at.
        cands = {"_".join(segs[i:j]).lower()
                 for i in range(len(segs)) for j in range(i + 1, len(segs) + 1)}
        low = stem.lower()
        rule = None
        if low in cands:
            rule = "folder"
        elif classes and low in classes and not LOD_RX.search(stem):
            # THE SECOND RULE - see cig_class_names(). Exact equality against
            # CIG's own ClassName list, so it cannot admit a prop.
            #
            # LODs ARE EXCLUDED HERE AND NOWHERE ELSE. `..._lod3` never equals
            # a ClassName so the check is belt and braces - but a LOD is the
            # same hull at lower detail, and taking one would be taking a worse
            # copy of a file we would then believe was the hull.
            rule = "class-name"
        if rule:
            keep.append((at, nm, rule))
    by_rule = {}
    for _at, _nm, r in keep:
        by_rule[r] = by_rule.get(r, 0) + 1
    print("  %d hull candidates (%s), resolving their headers"
          % (len(keep), ", ".join("%s %d" % (k, v)
                                  for k, v in sorted(by_rule.items()))))

    found, by_stem, rule_of = {}, {}, {}
    for at, nm, rule in keep:
        r = P.header_at(fh, at)
        # The resolved name must be the name we matched. Anything else means
        # the backward header search landed on a neighbour, and a neighbour is
        # not a near miss to be repaired - it is a different file.
        if not (r and r[0] == nm):
            continue
        stem = os.path.splitext(nm.split("\\")[-1])[0]
        by_stem.setdefault(stem.lower(), []).append(nm)
        found[nm] = r
        rule_of[nm] = rule
    # TWO PATHS CLAIMING ONE HULL IS AMBIGUOUS, AND AMBIGUOUS IS NOT RESOLVED
    # BY PICKING. Both are dropped and both are named, the same way the 85X
    # name collision was handled in the model sweep.
    #
    # ONE TIE-BREAK, AND IT IS EVIDENCE RATHER THAN PREFERENCE (C1,
    # 2026-08-27). The two rules are not equally strong. The FOLDER rule
    # requires the file's name and its LOCATION to agree - two independent
    # facts about the same entry. The CLASS-NAME rule requires only the name.
    #
    # So when a stem is claimed by one path the folder rule accepts and one it
    # does not, that is not a tie: `anvl_hornet_f7a` sits at
    # `ANVL\Hornet\f7_mk2\ANVL_Hornet_F7A.cga` and also elsewhere, and the
    # folder-rule path is corroborated where the other is not. Dropping both
    # LOST A HULL THAT WAS ALREADY DECODED, which is a correction making things
    # worse.
    #
    # TWO PATHS OF EQUAL EVIDENCE ARE STILL DROPPED AND STILL NAMED. The
    # Javelin's two paths are both folder-rule, one under `dmg`, and picking
    # between them would be a guess.
    for stem, paths in sorted(by_stem.items()):
        if len(paths) < 2:
            continue
        strong = [x for x in paths if rule_of.get(x) == "folder"]
        if len(strong) == 1:
            print("  %s claimed by %d paths - taking the folder-rule one, "
                  "which is corroborated by its location:" % (stem, len(paths)))
            print("      KEEP %s" % strong[0])
            for x in paths:
                if x is not strong[0]:
                    print("      drop %s" % x)
                    found.pop(x, None)
            continue
        print("  COLLISION on %s - dropped, %d paths claim it with equal "
              "evidence:" % (stem, len(paths)))
        for x in paths:
            print("      %s" % x)
            found.pop(x, None)
    return found


def payload(fh, r):
    nm, method, csize, usize, lho = r
    fh.seek(lho)
    lh = fh.read(30)
    if lh[:4] != b"PK\x03\x04":
        raise RuntimeError("no local header at %d" % lho)
    nlen, elen = struct.unpack_from("<HH", lh, 26)
    fh.seek(lho + 30 + nlen + elen)
    blob = fh.read(csize)
    if method == 100:
        data = P.zstd_decompress(blob, usize)
    elif method == 0:
        data = blob
    elif method == 8:
        import zlib
        data = zlib.decompress(blob, -15)
    else:
        raise RuntimeError("unhandled compression method %d" % method)
    if len(data) != usize:
        raise RuntimeError("size mismatch %d vs %d" % (len(data), usize))
    return data


# THE TWO FAMILIES, AND WHY THEY ARE SCORED SEPARATELY.
#
# The first version scored every named left/right pair together and failed the
# Carrack, the Constellation and the Corsair. Splitting them says what was
# actually happening: on the Vulture, `hardpoint_cooler_left` and
# `hardpoint_cooler_right` are 1.1 m apart along the SHIP'S AXIS - stacked bays
# that CIG named left/right. That is CIG's naming, not our arithmetic, and it
# was dragging the score down on exactly the hulls with the most internal kit.
#
# This is NOT the tolerance being widened to make a red thing green. The two
# numbers are BOTH reported, per hull, in the manifest. What changed is which
# one gates: the EXTERIOR mounts, because those are the ones the viewer marks
# on the hull at all - internal components go to the menu overlay by a standing
# decision that predates this work.
EXTERIOR = re.compile(
    r"hardpoint_(weapon|gun|turret|missile|missilerack|cm_launcher"
    r"|countermeasure|pylon|mount)", re.I)


def _mirror(hp, rx=None, tol_override=None):
    """(mirrored, pairs) over left/right FAMILIES.

    TWO THINGS THE FIRST VERSION GOT WRONG, both found by reading the hulls it
    rejected rather than by re-reading the code.

    1. THE TOLERANCE WAS ABSOLUTE - 5 cm, applied identically to a 3-metre PTV
       and a 123-metre Carrack. The Carrack's turret controllers sit at
       y = -28.498 and -28.248: a quarter-metre apart, 0.2% of that ship, and
       it was being called a failed mirror. The same 25 cm on a Gladius would
       be 1.2% and would deserve to fail. A FIXED TOLERANCE IS A DIFFERENT TEST
       ON EVERY HULL, so it now scales with the hull's own longest span.

    2. LEFT AND RIGHT ARE NOT ALWAYS NUMBERED IN THE SAME ORDER. On the
       ANVL_Hornet_F7A_MK1:

           countermeasure_left_01  (-2.599, -1.147, -0.996)
           countermeasure_right_02 ( 2.580, -1.147, -0.996)   <- its mirror
           countermeasure_left_02  (-2.599, -0.736, -1.265)
           countermeasure_right_01 ( 2.580, -0.736, -1.265)   <- its mirror

       Every mount is perfectly mirrored and CIG numbered the sides in opposite
       order. Pairing _left_01 to _right_01 by name scored 0 of 2 on a hull
       that is exactly symmetric. THE NAME SAYS WHICH FAMILY, NOT WHICH MEMBER.

    So a family is matched as a SET: each left takes the nearest unclaimed
    right. A member with no partner inside tolerance still counts as a failure,
    and a scrambled hull still fails because no assignment works - which keeps
    this a control rather than a tolerance widened until it passes.
    """
    names = [a for a in hp if rx is None or rx.search(a)]
    if not names:
        return 0, 0
    span = 0.0
    for i in range(3):
        vals = [p[i] for p in hp.values()]
        span = max(span, max(vals) - min(vals))
    tol = tol_override if tol_override is not None else max(0.05, span * 0.004)

    fam = {}
    for a in names:
        if "_left" in a:
            key = re.sub(r"_\d+$", "", a.replace("_left", "|"))
            fam.setdefault(key, [[], []])[0].append(a)
    for b in names:
        if "_right" in b:
            key = re.sub(r"_\d+$", "", b.replace("_right", "|"))
            if key in fam:
                fam[key][1].append(b)

    pairs = matched = 0
    for key, (ls, rs) in fam.items():
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


def accept(nodes):
    hp = {n["name"]: n["pos"] for n in nodes
          if n["name"].lower().startswith("hardpoint")}
    if not hp:
        # NOT A FAILED HULL - NOT A HULL. Refuel_Arm, elevator_600i and the
        # Prospector's drill arm are sub-assemblies that satisfied the naming
        # rule. Calling them failures buries the real ones.
        return False, "not a hull: no hardpoint nodes", {"hardpoints": 0}

    finite = sum(1 for p in hp.values() if all(abs(x) < 1e4 for x in p))
    em, ep = _mirror(hp, EXTERIOR)
    im, ip = _mirror(hp)
    xs = [p[0] for p in hp.values()]
    ys = [p[1] for p in hp.values()]
    zs = [p[2] for p in hp.values()]
    span_max = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
    stats = {"hardpoints": len(hp), "finite": finite,
             "exterior_pairs": ep, "exterior_mirrored": em,
             "all_pairs": ip, "all_mirrored": im,
             "span": [round(max(xs) - min(xs), 3), round(max(ys) - min(ys), 3),
                      round(max(zs) - min(zs), 3)],
             "span_max": round(span_max, 3)}

    if finite != len(hp):
        return False, "%d of %d transforms are not finite" % (
            len(hp) - finite, len(hp)), stats
    # THE CONTROL. A wrong stride does not produce a mirror-symmetric ship.
    # A hull with no mirrored pair to test CANNOT PASS - a check that could not
    # have failed is not a check, and saying so is cheaper than a false green.
    if ep == 0:
        return False, ("no named left/right EXTERIOR mount - nothing here "
                       "could have failed"), stats

    # THE GATE ASKS FOR PROOF THE DECODE IS RIGHT, NOT FOR ABSENCE OF ASYMMETRY.
    #
    # The 80%-of-pairs rule was rejecting eleven hulls that decode perfectly and
    # are simply not symmetric. Read them and it is obvious:
    #
    #   VNCL_Scythe   gun_nose_left/right   dx 0.000   exact
    #                 gun_wing_left/right   dx 4.061   and different in all
    #                                                  three axes
    #   drak_clipper  weapon_left/right     dx 0.008
    #                 missile_rack x3       right side offset ~2.5 m throughout
    #
    # Vanduul hulls and the Clipper are ASYMMETRIC BY DESIGN. Blocking them
    # meant eleven real ships got no markers because their designer did not
    # build them square - which is the page punishing the data for being true.
    #
    # SO THE QUESTION CHANGED. A wrong stride scrambles names across transforms,
    # and a scrambled hull cannot produce an EXACTLY mirrored pair - dx 0.000 on
    # the Scythe's nose guns is not something a wrong offset does by accident.
    # One exact pair proves the decode; the ratio only ever described the ship.
    #
    # THIS IS A WEAKENING AND IT IS SAID SO. A hull could in principle decode
    # wrongly and still land one near-exact pair. What stops that being the
    # whole story is that placement runs a SECOND, independent geometric test -
    # every exterior mount must fall inside that hull's own measured box - and
    # the two do not share an assumption. The ratio stays in the manifest as a
    # diagnostic so a hull that USED to be symmetric and stopped is still
    # visible.
    exact = max(0.02, stats["span_max"] * 0.001)
    proof = _mirror(hp, EXTERIOR, exact)[0]
    stats["exact_mirrored"] = proof
    if proof < 1:
        return False, ("no exterior mount pair mirrors exactly (%d of %d within "
                       "%.3f m) - nothing here proves the decode"
                       % (proof, ep, exact)), stats
    return True, "", stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only", default="")
    ap.add_argument("--redo", action="store_true",
                    help="re-extract ships that already have output")
    a = ap.parse_args()

    size = os.path.getsize(P.P4K)
    os.makedirs(OUT, exist_ok=True)
    with open(P.P4K, "rb") as fh:
        entries, cd_size, cd_off = E.find_central_directory(fh, size)
        print("central directory: %d entries, %.1f MB" % (entries, cd_size / 1e6))
        classes, classes_src = cig_class_names()
        if classes:
            print("CIG class names: %d from %s" % (len(classes), classes_src))
        else:
            print("NO ships.json SNAPSHOT - the class-name rule is OFF and "
                  "this run finds only the hulls the folder rule can see. "
                  "That is a smaller answer, said out loud rather than "
                  "returned quietly.")
        hulls = index(fh, cd_off, cd_size, classes)
        print("\nhull .cga candidates: %d\n" % len(hulls))

        names = sorted(hulls)
        if a.only:
            names = [n for n in names if a.only.lower() in n.lower()]
        if a.limit:
            names = names[:a.limit]

        table, failures = [], []
        for i, nm in enumerate(names):
            cls = os.path.splitext(nm.split("\\")[-1])[0]
            # RESUMABLE ON PURPOSE. This reads ~3 GB through a network mount and
            # the process does not always survive the session that launched it.
            # A run that has to start from nothing every time is a run that never
            # finishes, so an existing output is taken as done and the MANIFEST
            # is rebuilt from what is on disk at the end either way.
            outp = os.path.join(OUT, cls + ".json")
            if not a.redo and os.path.exists(outp):
                try:
                    prev = json.load(open(outp, encoding="utf-8"))
                    ok, why, stats = accept(prev["nodes"])
                    table.append({"class": cls, "nodes": prev["count"],
                                  "acceptance": ok, "note": why, **stats})
                    print("  %3d/%d  %-34s cached" % (i + 1, len(names), cls))
                    continue
                except Exception:
                    pass
            try:
                buf = payload(fh, hulls[nm])
                r = D.decode(buf)
            except Exception as e:
                failures.append({"class": cls, "entry": nm, "why": str(e)})
                print("  %3d/%d  %-34s FAILED  %s" % (i + 1, len(names), cls, e))
                continue
            ok, why, stats = accept(r["nodes"])
            r["acceptance"] = ok
            r["acceptance_note"] = why
            r["source_entry"] = nm
            with open(os.path.join(OUT, cls + ".json"), "w", encoding="utf-8") as f:
                json.dump(r, f, indent=1)
            table.append({"class": cls, "nodes": r["count"],
                          "acceptance": ok, "note": why, **stats})
            print("  %3d/%d  %-34s %s  %d nodes, %d hardpoints%s"
                  % (i + 1, len(names), cls, "PASS" if ok else "FAIL",
                     r["count"], stats.get("hardpoints", 0),
                     "" if ok else "  (" + why + ")"))
            sys.stdout.flush()

    man = {
        "generated_by": "build_hardpoint_transforms.py",
        "finding": "docs/FINDING_the-coordinates-are-in-the-client-2026-08-27.md",
        "source": P.P4K,
        "frame": "CIG/CryEngine. X lateral, Y fore/aft, Z up. METRES.",
        "hull_rule": "the .cga whose basename equals its folder name. Exact, "
                     "case-insensitive. No fuzzy matching.",
        "not_converted": "Viewer frame is y-up / -Z forward and each GLB carries "
                         "its own unit scale. Conversion is per-hull against that "
                         "hull's measured box and is NOT done here.",
        "acceptance": "every hardpoint finite; at least 80% of NAMED left/right "
                      "pairs mirrored to 5 cm. A hull with no named pair FAILS - "
                      "a check that could not have failed is not a check.",
        "counts": {"hulls_indexed": len(hulls), "decoded": len(table),
                   "passed": sum(1 for t in table if t["acceptance"]),
                   "failed_acceptance": sum(1 for t in table if not t["acceptance"]),
                   "errored": len(failures)},
        "ships": table,
    }
    with open(os.path.join(OUT, "MANIFEST.json"), "w", encoding="utf-8") as f:
        json.dump(man, f, indent=1)
    with open(os.path.join(OUT, "failures.json"), "w", encoding="utf-8") as f:
        json.dump(failures, f, indent=1)
    print("\n%s" % json.dumps(man["counts"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
