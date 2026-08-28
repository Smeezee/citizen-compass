#!/usr/bin/env python3
"""What the hull rule is REJECTING, and is any of it a hull?

`build_hardpoint_transforms.py` indexed 116 hulls out of a fleet of ~250 ships,
and 96 of the ship page's classes still carry name-derived markers. The hull
rule is an exact one - the .cga whose stem equals some contiguous run of its
folder path - so anything CIG spells differently is dropped as a part.

This does not decode anything and does not write to the transforms directory.
It reads the same central directory, applies the same rule, and prints what
falls on the other side of it, grouped so the shape is visible.

    python3 probe_hull_rule_rejects.py
"""
import collections
import os
import re
import sys
import time

import extract_default_profile as E
import probe_ship_geometry as P

E.zstd_decompress = P.zstd_decompress

SHIP_RX = re.compile(
    rb"Data\\Objects\\Spaceships\\Ships\\"
    rb"(?:[A-Za-z0-9_\-\.]+\\){1,4}"
    rb"[A-Za-z0-9_\-\.]+\.cga(?![A-Za-z0-9_])")

# Names that are obviously not a whole hull. Used ONLY to make the reject list
# readable - nothing is decided by it.
PART_HINT = re.compile(
    r"(_lod\d|_damage|_dst|_interior|_int_|_cockpit|_seat|_door|_hatch|_ramp"
    r"|_gear|_wing_|_flap|_thruster|_engine|_nozzle|_turret|_gun|_weapon"
    r"|_antenna|_light|_glass|_panel|_arm|_bay|_elevator|_ladder|_prop"
    r"|_debris|_shard|_piece|_module_|_hologram|_screen|_decal|_col$|_proxy)",
    re.I)


def main():
    size = os.path.getsize(P.P4K)
    with open(P.P4K, "rb") as fh:
        entries, cd_size, cd_off = E.find_central_directory(fh, size)
        print("central directory: %d entries, %.1f MB" % (entries, cd_size / 1e6))
        names, seen = [], set()
        chunk, overlap = 16 << 20, 2048
        pos, carry, carry_at = 0, b"", cd_off
        fh.seek(cd_off)
        t0 = time.time()
        while pos < cd_size:
            blk = fh.read(min(chunk, cd_size - pos))
            if not blk:
                break
            buf = carry + blk
            for m in SHIP_RX.finditer(buf):
                at = carry_at + m.start()
                if at in seen:
                    continue
                seen.add(at)
                names.append(m.group().decode("utf-8", "replace"))
            pos += len(blk)
            carry = buf[-overlap:]
            carry_at = cd_off + pos - len(carry)
        print("  scanned in %.0fs, %d .cga entries under Ships"
              % (time.time() - t0, len(names)))

    kept, rejected = [], []
    for nm in names:
        parts = nm.split("\\")
        if "Ships" not in parts:
            continue
        segs = parts[parts.index("Ships") + 1:-1]
        if not segs:
            continue
        stem = os.path.splitext(parts[-1])[0]
        cands = {"_".join(segs[i:j]).lower()
                 for i in range(len(segs)) for j in range(i + 1, len(segs) + 1)}
        (kept if stem.lower() in cands else rejected).append((nm, segs, stem))

    print("\nRULE ACCEPTS %d, REJECTS %d" % (len(kept), len(rejected)))

    # A reject that looks like a hull: no part/LOD marker in the name, and its
    # stem STARTS WITH a contiguous run of its folders - i.e. it is named for
    # this ship and then something more. That is the shape a variant has.
    look = []
    for nm, segs, stem in rejected:
        if PART_HINT.search(stem):
            continue
        low = stem.lower()
        runs = ["_".join(segs[i:j]).lower()
                for i in range(len(segs)) for j in range(i + 1, len(segs) + 1)]
        best = max((r for r in runs if low.startswith(r + "_")),
                   key=len, default=None)
        if best:
            look.append((best, low[len(best) + 1:], nm))

    print("REJECTS THAT LOOK LIKE A HULL OF THEIR OWN: %d" % len(look))
    suf = collections.Counter(s for _b, s, _n in look)
    print("\nby trailing part of the name, most common first:")
    for s, n in suf.most_common(40):
        print("   %-34s %d" % (s, n))

    print("\nfirst 45, in full:")
    for base, s, nm in sorted(look)[:45]:
        print("   %-26s + %-22s  %s" % (base, s, nm))
    return 0


if __name__ == "__main__":
    sys.exit(main())
