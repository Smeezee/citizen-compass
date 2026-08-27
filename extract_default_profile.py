#!/usr/bin/env python3
"""
C4 - re-extract defaultProfile.xml from the LIVE Data.p4k, per
docs/workorder-keybind-01-extraction-done.md section 2.

MUST BE RE-RUN ON EVERY PATCH. Default bindings change, and nothing else in
this repo notices when they have.

NO THIRD-PARTY TOOL AND NOTHING INSTALLED. Read the ZIP64 central directory,
find the entry, decompress the zstd frame, decode the CryXmlB binary header.

THE ZSTD IS A LIBRARY, NOT THE CLI THE WORK ORDER ASSUMED. That work order
says "zstd and unzstd are already on the machine". Neither is on PATH here and
there is no zstandard module in the venv. What IS here is msys-zstd-1.dll,
shipped with the Git for Windows this repo already uses, called through
ctypes. Same guarantee - nothing installed - but the claim needed correcting
rather than repeating.

IT DOES NOT OVERWRITE THE PREVIOUS EXTRACTION. Output is named by the build it
came from, so 4.9 and 4.10 sit side by side. C5's diff needs both sides, and
data-layer/processed/defaultProfile.plain.xml IS the 4.9 left-hand one.
"""
import ctypes
import datetime
import hashlib
import io
import json
import os
import struct
import sys

LIVE = r"C:\Program Files\Roberts Space Industries\StarCitizen\LIVE"
P4K = os.path.join(LIVE, "Data.p4k")
MANIFEST_ID = os.path.join(LIVE, "build_manifest.id")
OUT_DIR = os.path.join("data-layer", "processed")
WANT = b"defaultProfile.xml"
# THE MINGW64 BUILD, NOT THE MSYS ONE NEXT DOOR. Git for Windows ships both:
#   usr\bin\msys-zstd-1.dll      Cygwin/MSYS runtime - SEGFAULTS from CPython
#   mingw64\bin\libzstd.dll      native Win64 - works
# The MSYS one LOADS and answers ZSTD_versionNumber correctly, because that
# returns a constant and touches nothing. The first real call crashes the
# interpreter, because the Cygwin runtime it needs was never initialised in an
# MSVC-built process. That is a textbook silent-success trap: the cheap probe
# passes and the thing you actually need takes the process down.
ZSTD_DLL = r"C:\Program Files\Git\mingw64\bin\libzstd.dll"


def die(msg):
    print("STOPPED: " + msg)
    sys.exit(1)


def read_build():
    with io.open(MANIFEST_ID, encoding="utf-8") as f:
        return json.load(f)["Data"]


def find_central_directory(fh, size):
    tail_len = min(1 << 16, size)
    fh.seek(size - tail_len)
    tail = fh.read(tail_len)
    loc = tail.rfind(b"PK\x06\x07")
    if loc < 0:
        die("no ZIP64 end-of-central-directory locator - not a ZIP64 container")
    _disk, z64_off, _total = struct.unpack_from("<IQI", tail, loc + 4)
    fh.seek(z64_off)
    hdr = fh.read(56)
    if hdr[:4] != b"PK\x06\x06":
        die("ZIP64 EOCD signature missing at the offset the locator gave")
    # ZIP64 EOCD layout: 24 = entries on this disk, 32 = total entries,
    # 40 = size of central directory, 48 = offset of central directory.
    # Reading from 24 shifts every field by one and yields a "central
    # directory" of 1.4 MB whose offset is really its size - which finds
    # nothing and looks like a missing entry rather than a bad parse.
    entries = struct.unpack_from("<Q", hdr, 32)[0]
    cd_size, cd_off = struct.unpack_from("<QQ", hdr, 40)
    return entries, cd_size, cd_off


def scan_for_entry(fh, cd_off, cd_size, want):
    """Chunk-scan rather than holding 463 MB of central directory in memory."""
    chunk_size = 4 << 20
    overlap = 512
    pos = 0
    carry = b""
    carry_at = cd_off
    fh.seek(cd_off)
    while pos < cd_size:
        chunk = fh.read(min(chunk_size, cd_size - pos))
        if not chunk:
            break
        buf = carry + chunk
        i = buf.find(want)
        if i >= 0:
            return carry_at + i
        pos += len(chunk)
        print("          scanned %5.1f / %.1f MB" % (pos / 1e6, cd_size / 1e6))
        sys.stdout.flush()
        carry = buf[-overlap:]
        carry_at = cd_off + pos - len(carry)
    return -1


def parse_central_header(fh, name_at, want):
    back = 1024
    start = max(0, name_at - back)
    fh.seek(start)
    win = fh.read(back + len(want) + 8)
    sig = win.rfind(b"PK\x01\x02", 0, name_at - start)
    if sig < 0:
        die("found the name but no central header signature before it")
    h_at = start + sig
    fh.seek(h_at)
    h = fh.read(46)
    method = struct.unpack_from("<H", h, 10)[0]
    csize, usize = struct.unpack_from("<II", h, 20)
    nlen, elen, _clen = struct.unpack_from("<HHH", h, 28)
    lho = struct.unpack_from("<I", h, 42)[0]
    name = fh.read(nlen)
    extra = fh.read(elen)
    # ZIP64 extra carries only the fields that were 0xFFFFFFFF, in this order.
    p = 0
    while p + 4 <= len(extra):
        xid, xsz = struct.unpack_from("<HH", extra, p)
        body = extra[p + 4:p + 4 + xsz]
        if xid == 0x0001:
            q = 0
            if usize == 0xFFFFFFFF:
                usize = struct.unpack_from("<Q", body, q)[0]
                q += 8
            if csize == 0xFFFFFFFF:
                csize = struct.unpack_from("<Q", body, q)[0]
                q += 8
            if lho == 0xFFFFFFFF:
                lho = struct.unpack_from("<Q", body, q)[0]
                q += 8
        p += 4 + xsz
    return {"name": name.decode("utf-8", "replace"), "method": method,
            "csize": csize, "usize": usize, "local": lho}


def read_payload(fh, ent):
    fh.seek(ent["local"])
    lh = fh.read(30)
    if lh[:4] != b"PK\x03\x04":
        die("local header signature missing at the offset the central dir gave")
    nlen, elen = struct.unpack_from("<HH", lh, 26)
    fh.seek(ent["local"] + 30 + nlen + elen)
    return fh.read(ent["csize"])


def zstd_decompress(blob, expect):
    if not os.path.exists(ZSTD_DLL):
        die("no zstd library on this machine at " + ZSTD_DLL)
    lib = ctypes.CDLL(ZSTD_DLL)
    lib.ZSTD_decompress.restype = ctypes.c_size_t
    lib.ZSTD_decompress.argtypes = [ctypes.c_void_p, ctypes.c_size_t,
                                    ctypes.c_char_p, ctypes.c_size_t]
    lib.ZSTD_isError.restype = ctypes.c_uint
    lib.ZSTD_isError.argtypes = [ctypes.c_size_t]
    out = ctypes.create_string_buffer(expect)
    n = lib.ZSTD_decompress(out, expect, blob, len(blob))
    if lib.ZSTD_isError(n):
        die("zstd refused the frame")
    if n != expect:
        die("zstd produced %d bytes, the directory said %d" % (n, expect))
    return out.raw[:n]


def decode_cryxml(buf):
    if buf[:8] != b"CryXmlB\x00":
        die("not CryXmlB - got %r" % buf[:16])
    (flen, node_off, node_n, attr_off, attr_n,
     child_off, child_n, str_off, str_size) = struct.unpack_from("<9I", buf, 8)

    # THE FOUR SELF-CHECKS, ASSERTED. A wrong endianness or offset produces
    # garbage that still parses, which is the whole reason these exist.
    checks = [
        ("nodeTable + nodeCount*28 == childTable",
         node_off + node_n * 28, child_off),
        ("childTable + childCount*4 == attrTable",
         child_off + child_n * 4, attr_off),
        ("attrTable + attrCount*8 == stringTable",
         attr_off + attr_n * 8, str_off),
        ("stringTable + stringDataSize == fileLength",
         str_off + str_size, flen),
    ]
    for label, got, want in checks:
        print("  %-5s %s  (%d vs %d)"
              % ("ok" if got == want else "FAILED", label, got, want))
    if any(g != w for _l, g, w in checks):
        die("the CryXmlB table layout did not check out - refusing to emit "
            "something that parsed into garbage")

    def s(off):
        e = buf.index(b"\x00", str_off + off)
        return buf[str_off + off:e].decode("utf-8", "replace")

    nodes = []
    for i in range(node_n):
        (tag, content, na, nc, _parent, fa, fc, _r) = struct.unpack_from(
            "<IIHHIIII", buf, node_off + i * 28)
        nodes.append({"tag": s(tag), "text": s(content), "na": na, "nc": nc,
                      "fa": fa, "fc": fc})
    attrs = []
    for i in range(attr_n):
        k, v = struct.unpack_from("<II", buf, attr_off + i * 8)
        attrs.append((s(k), s(v)))
    children = (list(struct.unpack_from("<%dI" % child_n, buf, child_off))
                if child_n else [])

    def esc(t):
        return (t.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))

    out = []

    def emit(i, depth):
        n = nodes[i]
        pad = "  " * depth
        a = "".join(' %s="%s"' % (k, esc(v))
                    for k, v in attrs[n["fa"]:n["fa"] + n["na"]])
        kids = children[n["fc"]:n["fc"] + n["nc"]]
        if not kids and not n["text"]:
            out.append("%s<%s%s/>" % (pad, n["tag"], a))
            return
        out.append("%s<%s%s>%s" % (pad, n["tag"], a, esc(n["text"])))
        for c in kids:
            emit(c, depth + 1)
        out.append("%s</%s>" % (pad, n["tag"]))

    sys.setrecursionlimit(10000)
    emit(0, 0)
    return "\n".join(out) + "\n", node_n, attr_n


def main():
    build = read_build()
    tag = "%s.%s" % (build["Branch"].replace("sc-alpha-", ""),
                     build["RequestedP4ChangeNum"])
    print("install : %s  change %s  version %s"
          % (build["Branch"], build["RequestedP4ChangeNum"], build["Version"]))

    size = os.path.getsize(P4K)
    print("archive : %.1f GB" % (size / 1e9))
    with io.open(P4K, "rb") as fh:
        entries, cd_size, cd_off = find_central_directory(fh, size)
        print("zip64   : %d entries, central directory %.1f MB at %d"
              % (entries, cd_size / 1e6, cd_off))
        at = scan_for_entry(fh, cd_off, cd_size, WANT)
        if at < 0:
            die("no defaultProfile.xml in the central directory")
        ent = parse_central_header(fh, at, WANT)
        print("entry   : %s" % ent["name"])
        print("          method %d, compressed %d -> %d"
              % (ent["method"], ent["csize"], ent["usize"]))
        if ent["method"] != 100:
            die("compression method %d, expected 100 (ZStandard)" % ent["method"])
        blob = read_payload(fh, ent)

    if blob[:4] != b"\x28\xb5\x2f\xfd":
        die("not a raw zstd frame - magic is %r" % blob[:4])
    raw = zstd_decompress(blob, ent["usize"])

    print("CryXmlB self-checks:")
    text, node_n, attr_n = decode_cryxml(raw)

    out_xml = os.path.join(OUT_DIR, "defaultProfile.%s.plain.xml" % tag)
    with io.open(out_xml, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    man = {
        "extracted_utc": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_archive": P4K,
        "archive_bytes": size,
        "game_branch": build["Branch"],
        "game_version": build["Version"],
        "p4_change": build["RequestedP4ChangeNum"],
        "build_date_stamp": build["BuildDateStamp"],
        "entry_path": ent["name"],
        "compression_method": ent["method"],
        "compressed_bytes": ent["csize"],
        "uncompressed_bytes": ent["usize"],
        "cryxml_nodes": node_n,
        "cryxml_attributes": attr_n,
        "output_bytes": len(text.encode("utf-8")),
        "output_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "zstd_library": ZSTD_DLL,
        "method": "docs/workorder-keybind-01-extraction-done.md section 2",
    }
    out_man = os.path.join(OUT_DIR, "defaultProfile.%s.MANIFEST.json" % tag)
    with io.open(out_man, "w", encoding="utf-8", newline="\n") as f:
        json.dump(man, f, indent=2)
        f.write("\n")
    print("written : %s (%d bytes)" % (out_xml, man["output_bytes"]))
    print("written : %s" % out_man)
    print("nodes   : %d, attributes %d" % (node_n, attr_n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
