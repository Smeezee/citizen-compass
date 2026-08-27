#!/usr/bin/env python3
"""
Pull ONE named entry out of Data.p4k and write it to disk, decompressed.

Same ZIP64 + zstd path as extract_default_profile.py. Nothing installed, no
third-party tool. Separate from probe_ship_geometry.py because a probe that
prints and an extractor that writes are different responsibilities and mixing
them is how a probe quietly becomes an importer.

  python3 extract_p4k_entry.py "Data\\Objects\\...\\DRAK_Vulture.cga" /tmp/out.cga
"""
import os
import struct
import sys

import extract_default_profile as E
import probe_ship_geometry as P

E.zstd_decompress = P.zstd_decompress


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    want = sys.argv[1].replace("/", "\\").encode("utf-8")
    out = sys.argv[2]
    size = os.path.getsize(P.P4K)
    with open(P.P4K, "rb") as fh:
        entries, cd_size, cd_off = E.find_central_directory(fh, size)
        # EXACT NAME, NOT A PREFIX. The first version of this scanned for the
        # first occurrence of the name as a substring and pulled
        # DRAK_Vulture.cgaM when asked for DRAK_Vulture.cga - a 45 MB file that
        # decompressed cleanly, reported success, and was the wrong file. A
        # plausible result is not a correct one.
        import re as _re
        hits = P.find_all(fh, cd_off, cd_size,
                          _re.escape(want) + rb"(?![A-Za-z0-9_])")
        r = None
        for h in hits:
            cand = P.header_at(fh, h)
            if cand and cand[0].encode("utf-8") == want:
                r = cand
                break
        if not r:
            print("NOT FOUND as an exact entry name: %s  (%d near hits)"
                  % (want.decode(), len(hits)))
            return 1
        nm, method, csize, usize, lho = r
        print("entry %s\n  method %d  csize %d  usize %d  lho %d"
              % (nm, method, csize, usize, lho))
        fh.seek(lho)
        lh = fh.read(30)
        if lh[:4] != b"PK\x03\x04":
            print("no local header at the offset the central directory gave - "
                  "stopping rather than reading an arbitrary region")
            return 1
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
        print("unhandled compression method %d - not guessing" % method)
        return 1
    if len(data) != usize:
        print("SIZE MISMATCH: got %d, header said %d" % (len(data), usize))
        return 1
    with open(out, "wb") as f:
        f.write(data)
    print("wrote %s  %d bytes\n  first 32: %r" % (out, len(data), data[:32]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
