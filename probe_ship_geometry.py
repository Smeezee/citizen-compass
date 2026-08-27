#!/usr/bin/env python3
"""
HP-PROBE - what does Data.p4k actually carry for ONE ship, and does any of it
hold a hardpoint transform?

THIS IS A PROBE. It reads, it measures, it prints. It writes no catalogue data
and it claims nothing it has not decoded. That distinction is the whole reason
this file exists separately from an importer: the last three attempts at a
binary format in this repo each produced a plausible table from a wrong offset.

WHY IT IS BEING RUN AT ALL. Every hull marker on the site is derived from the
mount's NAME, snapped to the nearest vertex in a named region, because
`place_hardpoints.py` measured the alternative and wrote it down: "All 53,651
`position` fields in the game data are null." That is true of the UNPACKED data
this project has been working from. It has never been checked against the
shipped client, which is where the transforms would have to live for the game
itself to place a gun.

Reuses the ZIP64 + zstd path proven in extract_default_profile.py, with two
substitutions and no third change:
  - the archive path, because this runs against the mounted LIVE install
  - zstd through the system libzstd.so rather than Git for Windows' DLL
"""
import ctypes
import ctypes.util
import io
import os
import re
import struct
import sys

import extract_default_profile as E

P4K = os.environ.get("CC_P4K") or os.path.expanduser(
    "~/mnt/StarCitizen/LIVE/Data.p4k")

# ---------------------------------------------------------------- zstd, linux
_z = ctypes.CDLL(ctypes.util.find_library("zstd") or "libzstd.so.1")
_z.ZSTD_decompress.restype = ctypes.c_size_t
_z.ZSTD_decompress.argtypes = [ctypes.c_void_p, ctypes.c_size_t,
                               ctypes.c_void_p, ctypes.c_size_t]
_z.ZSTD_isError.restype = ctypes.c_uint
_z.ZSTD_isError.argtypes = [ctypes.c_size_t]


def zstd_decompress(blob, expect):
    out = ctypes.create_string_buffer(expect)
    n = _z.ZSTD_decompress(out, expect, blob, len(blob))
    if _z.ZSTD_isError(n):
        raise RuntimeError("zstd refused the frame (code %d)" % n)
    if n != expect:
        raise RuntimeError("zstd produced %d bytes, the header said %d" % (n, expect))
    return out.raw[:n]


E.zstd_decompress = zstd_decompress


def find_all(fh, cd_off, cd_size, pattern, limit=4000):
    """Every central-directory offset whose filename matches `pattern`.

    Matched against the RAW central directory bytes, so a hit is a byte offset
    that still has to be resolved back to a real header - never treated as a
    filename on its own."""
    rx = re.compile(pattern if isinstance(pattern, bytes)
                    else pattern.encode('utf-8'), re.I)
    hits = []
    chunk_size = 8 << 20
    overlap = 1024
    pos = 0
    carry = b""
    carry_at = cd_off
    fh.seek(cd_off)
    while pos < cd_size and len(hits) < limit:
        chunk = fh.read(min(chunk_size, cd_size - pos))
        if not chunk:
            break
        buf = carry + chunk
        for m in rx.finditer(buf):
            hits.append(carry_at + m.start())
            if len(hits) >= limit:
                break
        pos += len(chunk)
        if pos % (160 << 20) < chunk_size:
            print("    scanned %6.1f / %.1f MB  hits %d"
                  % (pos / 1e6, cd_size / 1e6, len(hits)))
            sys.stdout.flush()
        carry = buf[-overlap:]
        carry_at = cd_off + pos - len(carry)
    return hits


def header_at(fh, near):
    """Resolve a raw byte offset back to its central-directory header.

    Returns (name, method, csize, usize, lho) or None. Refuses rather than
    guesses when the signature is not found - a header invented here would
    produce a confident, wrong file list."""
    back = 2048
    start = max(0, near - back)
    fh.seek(start)
    win = fh.read(back + 1024)
    sig = win.rfind(b"PK\x01\x02", 0, near - start)
    if sig < 0:
        return None
    h = win[sig:sig + 46]
    if len(h) < 46:
        return None
    method = struct.unpack_from("<H", h, 10)[0]
    csize, usize = struct.unpack_from("<II", h, 20)
    nlen, elen, clen = struct.unpack_from("<HHH", h, 28)
    lho = struct.unpack_from("<I", h, 42)[0]
    name = win[sig + 46:sig + 46 + nlen]
    if len(name) < nlen:
        fh.seek(start + sig + 46)
        name = fh.read(nlen)
    extra_at = start + sig + 46 + nlen
    fh.seek(extra_at)
    extra = fh.read(elen)
    p = 0
    while p + 4 <= len(extra):
        xid, xsz = struct.unpack_from("<HH", extra, p)
        body = extra[p + 4:p + 4 + xsz]
        if xid == 0x0001:
            q = 0
            if usize == 0xFFFFFFFF and q + 8 <= len(body):
                usize = struct.unpack_from("<Q", body, q)[0]; q += 8
            if csize == 0xFFFFFFFF and q + 8 <= len(body):
                csize = struct.unpack_from("<Q", body, q)[0]; q += 8
            if lho == 0xFFFFFFFF and q + 8 <= len(body):
                lho = struct.unpack_from("<Q", body, q)[0]; q += 8
        p += 4 + xsz
    try:
        nm = name.decode("utf-8", "replace")
    except Exception:
        nm = repr(name)
    return (nm, method, csize, usize, lho)


def main():
    pattern = sys.argv[1] if len(sys.argv) > 1 else r"[Vv]ulture[^\x00]{0,60}"
    if not os.path.exists(P4K):
        print("NOT PERFORMED - no archive at %s" % P4K)
        return 2
    size = os.path.getsize(P4K)
    print("archive %s  %.1f GB" % (P4K, size / 1e9))
    with open(P4K, "rb") as fh:
        entries, cd_size, cd_off = E.find_central_directory(fh, size)
        print("central directory: %d entries, %.1f MB at %d"
              % (entries, cd_size / 1e6, cd_off))
        print("scanning for /%s/ ..." % pattern)
        hits = find_all(fh, cd_off, cd_size, pattern)
        print("raw hits: %d" % len(hits))
        seen = {}
        for h in hits:
            r = header_at(fh, h)
            if not r:
                continue
            seen[r[0]] = r
        print("resolved to %d distinct entries\n" % len(seen))
        rows = sorted(seen.values(), key=lambda r: -r[3])
        by_ext = {}
        for nm, method, csize, usize, lho in rows:
            ext = os.path.splitext(nm)[1].lower() or "(none)"
            by_ext[ext] = by_ext.get(ext, 0) + 1
        print("BY EXTENSION")
        for ext, n in sorted(by_ext.items(), key=lambda kv: -kv[1]):
            print("  %-10s %5d" % (ext, n))
        print("\nLARGEST 60")
        for nm, method, csize, usize, lho in rows[:60]:
            print("  %10d  m%-3d  %s" % (usize, method, nm))
    return 0


if __name__ == "__main__":
    sys.exit(main())
