#!/usr/bin/env python3
"""
Decode the node table of a CIG `#ivo` .cga / .cgf and emit named hardpoint
transforms.

THIS IS THE THING THE PROJECT HAS BEEN MISSING. `place_hardpoints.py` states,
correctly, that all 53,651 `position` fields in the UNPACKED game data are
null. They are not null in the shipped client - the game has to know where to
put a gun - and this reads them.

FORMAT, ESTABLISHED BY MEASUREMENT AND NOT BY ASSUMPTION
--------------------------------------------------------
Container: `#ivo`, version 0x0900, a 16-byte header (magic, version, chunk
count, chunk-table offset) then a chunk table of 16-byte entries
(typeHash u32, version u32, offset u64).

Two chunks matter:

  0xC201973C  the name table.
              u32 nodeCount, u32 stringBytes, padding to 32, then
              (nodeCount + 1) 16-byte records, then the packed
              null-terminated names.
              THE +1 IS REAL: the first record is a null entry. On the Vulture
              the table is 4592 bytes = 287 records where the header says 286
              nodes, and the name blob parses to exactly 286 names. That the
              declared count and the parsed count agree is the check that this
              offset is right rather than merely plausible.

  0x70697FDA  the node array.
              64-byte header, then nodeCount records of 208 bytes each,
              then a second copy of the name blob.
              Within a record:
                +16   3x4 row-major transform, translation in column 4.
                      METRES. Rows are unit length - that is how the stride
                      was found.
                +64   a second 3x4. Parent-relative; DO NOT USE IT for
                      placement (it fails the mirror test at 40/71 where the
                      first passes at 58/71).
                +128  u16 node index. Across the Vulture's 286 records these
                      are a PERMUTATION OF 0..285 - every value present,
                      every value distinct. That bijection is what makes the
                      join to the name table a proof rather than a guess.
                +130  the same index again.

HOW THE STRIDE WAS FOUND, recorded because the method is the point.
Not by reading a spec - there is none. Every 4-byte offset in the chunk was
tested for a 3x4 whose three rotation rows are unit length and whose
translation is finite and under 300 m. The gap histogram of the 1,430 hits has
one non-trivial mode: 144, occurring 285 times, in a chunk declaring 286 nodes.
Group starts sit 208 apart. 48 + 286*208 = 59,536, and the name blob begins at
64,939 - the records end before the strings, with room for nothing else.

AXES. CryEngine: X lateral, Y fore/aft, Z up. Confirmed on the Vulture, not
assumed: hardpoints span 12.90 m laterally against a published 21.5 m beam
(inboard of the wingtips), 30.61 m fore/aft against 38 m of length, 6.69 m
vertically against 10 m of height. Every span is smaller than the hull and in
the right proportion. A transposed axis would not produce that.

THIS EMITS METRES IN CIG'S FRAME AND NOTHING ELSE. Converting to the viewer's
y-up / -Z-forward frame and to the GLB's unit scale is a separate job that must
be done per hull against that hull's own measured box - there is no global
constant and this file does not pretend there is one.

Usage:
    python3 decode_cga_nodes.py <file.cga> [--json OUT] [--all]
"""
import argparse
import json
import math
import os
import struct
import sys

NAME_CHUNK = 0xC201973C
NODE_CHUNK = 0x70697FDA
REC = 208
MAT = 16
IDX = 128


class DecodeError(Exception):
    pass


def chunks(buf):
    if buf[:4] != b"#ivo":
        raise DecodeError("not an #ivo container (magic %r)" % buf[:4])
    _magic, ver, n, tbl = struct.unpack_from("<4sIII", buf, 0)
    out = []
    for i in range(n):
        t, v, off = struct.unpack_from("<IIQ", buf, tbl + i * 16)
        end = struct.unpack_from("<IIQ", buf, tbl + (i + 1) * 16)[2] \
            if i + 1 < n else len(buf)
        out.append((t, v, off, end))
    return ver, out


def decode(buf):
    ver, ch = chunks(buf)
    name_c = next((c for c in ch if c[0] == NAME_CHUNK), None)
    node_c = next((c for c in ch if c[0] == NODE_CHUNK), None)
    if not name_c:
        raise DecodeError("no name chunk 0x%08X" % NAME_CHUNK)
    if not node_c:
        raise DecodeError("no node chunk 0x%08X" % NODE_CHUNK)

    _t, _v, no, ne = name_c
    count, strbytes = struct.unpack_from("<II", buf, no)
    # The records are (count + 1) of 16 bytes, starting at +32.
    str_at = no + 32 + (count + 1) * 16
    blob = buf[str_at:str_at + strbytes]
    names = [x.decode("utf-8", "replace") for x in blob.split(b"\x00") if x]
    if len(names) != count:
        raise DecodeError(
            "the header declares %d nodes and the name blob parses to %d. "
            "Refusing to emit a table from an offset that does not check out."
            % (count, len(names)))

    _t, _v, do, de = node_c
    base = do + 48
    if base + count * REC > de:
        raise DecodeError("node records would run past the chunk (%d needed, "
                          "%d available)" % (count * REC, de - base))

    by_index = {}
    for k in range(count):
        o = base + k * REC
        idx = struct.unpack_from("<H", buf, o + IDX)[0]
        if idx in by_index:
            raise DecodeError("node index %d appears twice - the index field "
                              "is not the join key it looked like" % idx)
        by_index[idx] = struct.unpack_from("<12f", buf, o + MAT)
    if sorted(by_index) != list(range(count)):
        raise DecodeError("the node indices are not a permutation of 0..%d, "
                          "so the join to the name table is not sound"
                          % (count - 1))

    nodes = []
    for i, nm in enumerate(names):
        m = by_index[i]
        rows_unit = all(0.98 < math.sqrt(sum(x * x for x in m[r * 4:r * 4 + 3]))
                        < 1.02 for r in range(3))
        nodes.append({
            "name": nm, "index": i,
            "pos": [m[3], m[7], m[11]],
            "matrix": list(m),
            "rows_unit": rows_unit,
        })
    return {"version": ver, "count": count, "nodes": nodes}


def acceptance(nodes, label):
    """The tests were written into FINDING_the-coordinates-are-in-the-client
    BEFORE the decode worked. They are run here unchanged."""
    hp = {n["name"]: n["pos"] for n in nodes
          if n["name"].lower().startswith("hardpoint")}
    print("  hardpoint nodes: %d of %d" % (len(hp), len(nodes)))
    if not hp:
        print("  NOT PERFORMED - no hardpoint nodes in %s" % label)
        return False

    finite = sum(1 for p in hp.values() if all(abs(x) < 1e4 for x in p))
    print("  T1 finite transforms                 %d / %d" % (finite, len(hp)))

    pairs = [(n, n.replace("_left", "_right")) for n in hp
             if "_left" in n and n.replace("_left", "_right") in hp]
    mirrored, offenders = 0, []
    for a, b in pairs:
        pa, pb = hp[a], hp[b]
        if (abs(pa[0] + pb[0]) < 0.05 and abs(pa[1] - pb[1]) < 0.05
                and abs(pa[2] - pb[2]) < 0.05):
            mirrored += 1
        else:
            offenders.append((a, pa, b, pb))
    print("  T2 named left/right pairs mirrored   %d / %d" % (mirrored, len(pairs)))
    for a, pa, b, pb in offenders:
        print("       not mirrored: %-36s (%7.3f,%7.3f,%7.3f)"
              % (a, *pa))
        print("       %-50s (%7.3f,%7.3f,%7.3f)" % ("", *pb))

    xs = [p[0] for p in hp.values()]
    ys = [p[1] for p in hp.values()]
    zs = [p[2] for p in hp.values()]
    print("  T3 extent, metres, CIG frame")
    print("       lateral  %8.3f .. %8.3f   span %6.2f" % (min(xs), max(xs), max(xs) - min(xs)))
    print("       fore/aft %8.3f .. %8.3f   span %6.2f" % (min(ys), max(ys), max(ys) - min(ys)))
    print("       up       %8.3f .. %8.3f   span %6.2f" % (min(zs), max(zs), max(zs) - min(zs)))

    # T2 IS THE CONTROL AND IT HAS TO BE ABLE TO FAIL. A wrong stride does not
    # produce a mirror-symmetric ship, so a low score here is the signal that
    # the decode is wrong - not something to widen the tolerance for.
    return finite == len(hp) and (not pairs or mirrored / len(pairs) >= 0.8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--json", help="write the full node table here")
    ap.add_argument("--all", action="store_true",
                    help="print every node, not only the hardpoints")
    a = ap.parse_args()

    buf = open(a.path, "rb").read()
    try:
        r = decode(buf)
    except DecodeError as e:
        print("DECODE REFUSED: %s" % e)
        return 2

    print("%s  version 0x%04X  %d nodes" % (os.path.basename(a.path),
                                            r["version"], r["count"]))
    bad = [n["name"] for n in r["nodes"] if not n["rows_unit"]]
    if bad:
        print("  %d nodes whose rotation rows are not unit length: %s"
              % (len(bad), bad[:5]))
    ok = acceptance(r["nodes"], a.path)
    print()
    for n in sorted(r["nodes"], key=lambda n: n["name"]):
        if a.all or n["name"].lower().startswith("hardpoint"):
            print("  %-44s (%8.3f,%8.3f,%8.3f)" % (n["name"], *n["pos"]))
    if a.json:
        os.makedirs(os.path.dirname(a.json) or ".", exist_ok=True)
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(r, f, indent=1)
        print("\nwrote %s" % a.json)
    print("\nACCEPTANCE: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
