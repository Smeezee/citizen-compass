#!/usr/bin/env python3
"""Is there a .cga in Data.p4k for the ship-page classes that have no decoded
hardpoints - and if so, why did the hull rule not take it?

NO FUZZY MATCHING. The only test applied is EXACT EQUALITY between a rejected
.cga's stem and a class name the ship page actually uses, case-folded. A file
that is merely similar to a class name is not reported as that class's hull.

Reads only. Writes nothing.

    python3 probe_missing_hull_cga.py
"""
import json
import os
import re
import sys

import extract_default_profile as E
import probe_ship_geometry as P

E.zstd_decompress = P.zstd_decompress

SHIP_RX = re.compile(
    rb"Data\\Objects\\Spaceships\\Ships\\"
    rb"(?:[A-Za-z0-9_\-\.]+\\){1,4}"
    rb"[A-Za-z0-9_\-\.]+\.cga(?![A-Za-z0-9_])")
LOD = re.compile(r"_lod\d+$", re.I)


def classes_needing_hardpoints():
    """Ship-page classes whose drawn markers are not on CIG coordinates."""
    src = open("testing/_src/loadout_data.gen.js", encoding="utf-8").read()
    LS = json.loads(re.search(r"^const LOADOUT_SHIPS=(.*);$", src, re.M).group(1))
    LHP = json.loads(re.search(r"^const LOADOUT_HP=(.*);$", src, re.M).group(1))
    LT = json.loads(re.search(r"^const LOADOUT_TYPES=(.*);$", src, re.M).group(1))
    msrc = open("testing/_src/loadout_model.gen.js", encoding="utf-8").read()
    M = json.loads(re.search(r"^const LOADOUT_MODEL=(.*?);$", msrc,
                             re.M | re.S).group(1))
    D = "data-layer/derived/"
    fleet = json.load(open(D + "holo-hardpoints/hardpoints_fleet.json",
                           encoding="utf-8"))
    cl = json.load(open(D + "holo-hardpoints-align/fleet_records_client.json",
                        encoding="utf-8"))
    al = json.load(open(D + "holo-hardpoints-align/alignment_overlay_client.json",
                        encoding="utf-8"))
    merged = dict(fleet)
    merged.update(cl)
    by_model = {}
    for k, v in merged.items():
        mf = (v or {}).get("model")
        if mf:
            by_model.setdefault(mf, k)
    cig = {}
    for k, ports in al.items():
        cig.setdefault(k, set()).update(ports)
    for k in cl:
        cig.setdefault(k, set()).update(h["port"] for h in cl[k]["hardpoints"])
    W = {"WeaponGun", "Turret", "MissileLauncher", "WeaponDefensive",
         "WeaponMining", "BombLauncher", "SalvageHead", "TractorBeam",
         "EMP", "Missile", "Bomb"}
    need = []
    for cls, rec in LS.items():
        mf = M.get(cls)
        if not mf:
            continue
        key = by_model.get(mf)
        wn = {LHP[s["h"]] for s in rec["slots"]
              if (LT.get(s["t"]) or {}).get("t") in W}
        if not wn:
            continue
        if key is None:
            need.append(cls)
            continue
        hp = {h["port"] for h in (merged[key].get("hardpoints") or [])}
        drawn = wn & hp
        if not drawn or not (drawn & cig.get(key, set())):
            need.append(cls)
    return need


def main():
    need = classes_needing_hardpoints()
    want = {c.lower(): c for c in need}
    print("ship-page classes with no CIG hardpoints: %d" % len(need))

    have = {os.path.splitext(f)[0].lower()
            for f in os.listdir("data-layer/derived/hardpoint-transforms")
            if f.endswith(".json") and f not in ("MANIFEST.json",
                                                 "failures.json")}

    size = os.path.getsize(P.P4K)
    with open(P.P4K, "rb") as fh:
        entries, cd_size, cd_off = E.find_central_directory(fh, size)
        names, seen = [], set()
        chunk, overlap = 16 << 20, 2048
        pos, carry, carry_at = 0, b"", cd_off
        fh.seek(cd_off)
        while pos < cd_size:
            blk = fh.read(min(chunk, cd_size - pos))
            if not blk:
                break
            buf = carry + blk
            for m in SHIP_RX.finditer(buf):
                at = carry_at + m.start()
                if at not in seen:
                    seen.add(at)
                    names.append(m.group().decode("utf-8", "replace"))
            pos += len(blk)
            carry = buf[-overlap:]
            carry_at = cd_off + pos - len(carry)
    print("%d .cga entries under Ships" % len(names))

    # EXACT EQUALITY, and LODs excluded because a LOD is the same hull at lower
    # detail - taking one would be taking a worse copy of a file we would then
    # believe was the hull.
    hit = {}
    for nm in names:
        stem = os.path.splitext(nm.split("\\")[-1])[0]
        if LOD.search(stem):
            continue
        low = stem.lower()
        if low in want:
            hit.setdefault(low, []).append(nm)

    print("\nCLASSES WITH AN EXACTLY-NAMED .cga IN THE ARCHIVE: %d of %d"
          % (len(hit), len(need)))
    already = [k for k in hit if k in have]
    fresh = sorted(k for k in hit if k not in have)
    print("  of those, already decoded: %d" % len(already))
    print("  NOT decoded, one path:     %d"
          % sum(1 for k in fresh if len(hit[k]) == 1))
    print("  NOT decoded, ambiguous:    %d"
          % sum(1 for k in fresh if len(hit[k]) > 1))

    print("\nreachable now (exact name, single path, not yet decoded):")
    for k in fresh:
        if len(hit[k]) == 1:
            print("   %-34s %s" % (want[k], hit[k][0]))
    amb = [k for k in fresh if len(hit[k]) > 1]
    if amb:
        print("\nambiguous - two or more paths claim the name, NOT resolved:")
        for k in amb:
            print("   %s" % want[k])
            for p in hit[k]:
                print("        %s" % p)

    miss = sorted(c for c in need if c.lower() not in hit)
    print("\nNO exactly-named .cga anywhere: %d" % len(miss))
    for c in miss[:30]:
        print("   %s" % c)
    if len(miss) > 30:
        print("   ... and %d more" % (len(miss) - 30))
    return 0


if __name__ == "__main__":
    sys.exit(main())
