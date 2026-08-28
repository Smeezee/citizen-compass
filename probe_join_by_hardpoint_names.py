#!/usr/bin/env python3
"""Can a class with no decoded hull be matched to one by its hardpoint NAMES?

WHY THIS AND NOT A NAME GUESS. 91 ship-page classes still carry name-derived
markers, and for 82 of them there is no .cga anywhere named for the class.
Their geometry exists - `ANVL_Pisces.cga` is in the archive while the ship page
calls the ship `ANVL_C8_Pisces`; `ANVL_Lightning_F8.cga` is there while the
class is `ANVL_Lightning_F8C` - but nothing in CIG's data says which hull
belongs to which class, and ships.json carries no geometry path.

Guessing from the names is the fuzzy matching this project has banned twice.

SO THE TEST IS STRUCTURAL. Every port on the ship page carries CIG's own
`HardpointName`, and that string IS the node name inside the .cga. If every one
of a class's weapon-port names appears in exactly ONE decoded hull, that hull
holds that class's mounts - established by CIG's own identifiers rather than by
how the file happens to be named.

    all names present in exactly one hull   -> a candidate
    present in more than one                -> AMBIGUOUS, reported, never picked
    present in none                         -> no candidate

Reads only. Writes nothing. Decides nothing.

    python3 probe_join_by_hardpoint_names.py
"""
import json
import os
import re
import sys

D = "data-layer/derived/"
TR = D + "hardpoint-transforms"
W = {"WeaponGun", "Turret", "MissileLauncher", "WeaponDefensive",
     "WeaponMining", "BombLauncher", "SalvageHead", "TractorBeam",
     "EMP", "Missile", "Bomb"}


def main():
    src = open("testing/_src/loadout_data.gen.js", encoding="utf-8").read()
    LS = json.loads(re.search(r"^const LOADOUT_SHIPS=(.*);$", src, re.M).group(1))
    LHP = json.loads(re.search(r"^const LOADOUT_HP=(.*);$", src, re.M).group(1))
    LT = json.loads(re.search(r"^const LOADOUT_TYPES=(.*);$", src, re.M).group(1))
    msrc = open("testing/_src/loadout_model.gen.js", encoding="utf-8").read()
    M = json.loads(re.search(r"^const LOADOUT_MODEL=(.*?);$", msrc,
                             re.M | re.S).group(1))

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

    need = {}
    for cls, rec in LS.items():
        mf = M.get(cls)
        if not mf:
            continue
        wn = {LHP[s["h"]] for s in rec["slots"]
              if (LT.get(s["t"]) or {}).get("t") in W}
        if not wn:
            continue
        key = by_model.get(mf)
        if key is not None:
            hp = {h["port"] for h in (merged[key].get("hardpoints") or [])}
            drawn = wn & hp
            if drawn and (drawn & cig.get(key, set())):
                continue
        need[cls] = wn
    print("classes with no CIG hardpoints and at least one weapon port: %d"
          % len(need))

    hulls = {}
    for f in sorted(os.listdir(TR)):
        if not f.endswith(".json") or f in ("MANIFEST.json", "failures.json"):
            continue
        j = json.load(open(os.path.join(TR, f), encoding="utf-8"))
        hulls[f[:-5]] = {n["name"] for n in j["nodes"]}
    print("decoded hulls to test against: %d" % len(hulls))

    one, many, none = [], [], []
    for cls, wn in sorted(need.items()):
        hit = [h for h, names in hulls.items() if wn <= names]
        if len(hit) == 1:
            one.append((cls, hit[0], len(wn)))
        elif hit:
            many.append((cls, hit, len(wn)))
        else:
            # How close does the best hull get? Diagnostic only.
            best, cov = None, 0
            for h, names in hulls.items():
                c = len(wn & names)
                if c > cov:
                    best, cov = h, c
            none.append((cls, best, cov, len(wn)))

    print("\nEVERY WEAPON PORT PRESENT IN EXACTLY ONE HULL: %d" % len(one))
    for cls, h, n in one:
        print("   %-38s -> %-30s (%d ports)" % (cls, h, n))

    print("\nPRESENT IN MORE THAN ONE - AMBIGUOUS, NOT PICKED: %d" % len(many))
    for cls, hs, n in many[:20]:
        print("   %-38s %d ports, claimed by %d: %s"
              % (cls, n, len(hs), ", ".join(sorted(hs)[:4])))

    print("\nNO HULL CONTAINS ALL OF THEM: %d" % len(none))
    print("   (best partial coverage shown - diagnostic, not a candidate)")
    for cls, h, c, n in sorted(none, key=lambda r: -(r[2] / max(r[3], 1)))[:20]:
        print("   %-38s %2d/%-2d in %s" % (cls, c, n, h))
    return 0


if __name__ == "__main__":
    sys.exit(main())
