#!/usr/bin/env python3
"""Does CIG's own vehicle record name the ship's geometry file?

ships.json carries no geometry path - every field on a row was checked. But
scunpacked is DERIVED from CIG's entity records, and a derivation can drop a
field the source has. If the raw record names the .cga, the 84 classes with no
decoded hull stop needing a guess.

Reads only. Prints what it finds.
"""
import os, re, sys, time
import extract_default_profile as E
import probe_ship_geometry as P
E.zstd_decompress = P.zstd_decompress

# Anything under the entity/vehicle record trees, plus the vehicle XMLs.
PATS = [
    (rb"Data\\Libs\\Foundry\\Records\\entities\\spaceships\\[^\x00]{0,120}?\.xml", "entity record"),
    (rb"Data\\Libs\\Foundry\\Records\\entities\\groundvehicles\\[^\x00]{0,120}?\.xml", "ground record"),
    (rb"Data\\Scripts\\Entities\\Spaceships\\[^\x00]{0,120}?\.xml", "script entity"),
    (rb"Data\\Libs\\Vehicles\\[^\x00]{0,120}?\.xml", "vehicle xml"),
]

def main():
    size = os.path.getsize(P.P4K)
    hits = {k: [] for _p, k in PATS}
    with open(P.P4K, "rb") as fh:
        entries, cd_size, cd_off = E.find_central_directory(fh, size)
        print("central directory: %d entries, %.1f MB" % (entries, cd_size / 1e6))
        pos, carry, carry_at = 0, b"", cd_off
        fh.seek(cd_off)
        t0 = time.time()
        while pos < cd_size:
            blk = fh.read(min(16 << 20, cd_size - pos))
            if not blk:
                break
            buf = carry + blk
            for pat, key in PATS:
                for m in re.finditer(pat, buf):
                    s = m.group().decode("utf-8", "replace")
                    if s not in hits[key]:
                        hits[key].append(s)
            pos += len(blk)
            carry = buf[-2048:]
            carry_at = cd_off + pos - len(carry)
        print("scanned in %.0fs" % (time.time() - t0))
    for _p, key in PATS:
        v = hits[key]
        print("\n=== %s : %d ===" % (key, len(v)))
        for s in sorted(v)[:12]:
            print("   ", s)
    return 0

if __name__ == "__main__":
    sys.exit(main())
