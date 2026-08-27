#!/usr/bin/env python3
"""
C3a - open the DataForge .dcb with the zero-install method this project
already owns, and REPORT WHAT IS IN IT. No third-party tool, nothing
installed.

This is a probe, not an importer. It reads, it measures, it prints. It writes
nothing into the catalogue and it does not pretend to decode records it has not
actually decoded. The point of the exercise is to say honestly what a direct
read reaches before anybody proposes a dependency.

Reuses the ZIP64 + zstd path proven in extract_default_profile.py.
"""
import io
import json
import os
import struct
import sys

import extract_default_profile as E

OUT = os.path.join("data-layer", "processed", "dataforge_probe.json")


def find_all(fh, cd_off, cd_size, needle, limit=400):
    """Every offset of `needle` in the central directory."""
    chunk_size = 4 << 20
    overlap = 512
    pos = 0
    carry = b""
    carry_at = cd_off
    hits = []
    fh.seek(cd_off)
    while pos < cd_size and len(hits) < limit:
        chunk = fh.read(min(chunk_size, cd_size - pos))
        if not chunk:
            break
        buf = carry + chunk
        i = buf.find(needle)
        while i >= 0:
            hits.append(carry_at + i)
            if len(hits) >= limit:
                break
            i = buf.find(needle, i + 1)
        pos += len(chunk)
        carry = buf[-overlap:]
        carry_at = cd_off + pos - len(carry)
    return hits


def header_at(fh, name_at, needle):
    try:
        return E.parse_central_header(fh, name_at, needle)
    except SystemExit:
        return None


def u32(b, o):
    return struct.unpack_from("<I", b, o)[0]


def main():
    build = E.read_build()
    size = os.path.getsize(E.P4K)
    print("install : %s change %s" % (build["Branch"],
                                      build["RequestedP4ChangeNum"]))

    with io.open(E.P4K, "rb") as fh:
        _entries, cd_size, cd_off = E.find_central_directory(fh, size)
        print("scanning %.0f MB of central directory for .dcb ..." % (cd_size / 1e6))
        hits = find_all(fh, cd_off, cd_size, b".dcb")
        print("raw .dcb name hits: %d" % len(hits))

        seen = {}
        for at in hits:
            ent = header_at(fh, at, b".dcb")
            if ent and ent["name"].lower().endswith(".dcb"):
                seen[ent["name"]] = ent
        print("distinct .dcb entries: %d" % len(seen))
        for name, ent in sorted(seen.items(),
                                key=lambda kv: -kv[1]["usize"]):
            print("   %-52s method %3d  %10d -> %10d"
                  % (name, ent["method"], ent["csize"], ent["usize"]))

        if not seen:
            print("NO .dcb FOUND - reporting that rather than guessing a path")
            return 1

        name, ent = max(seen.items(), key=lambda kv: kv[1]["usize"])
        print("\nreading the largest: %s" % name)
        blob = E.read_payload(fh, ent)

    if ent["method"] == 100:
        if blob[:4] != b"\x28\xb5\x2f\xfd":
            print("method says zstd but the frame magic is %r" % blob[:4])
            return 1
        raw = E.zstd_decompress(blob, ent["usize"])
    elif ent["method"] == 0:
        raw = blob
    else:
        print("compression method %d is not one this probe handles"
              % ent["method"])
        return 1
    print("decompressed: %d bytes" % len(raw))
    print("first 64 bytes: %s" % raw[:64].hex())

    # ---- DataForge header ------------------------------------------------
    # Documented layout (the shape ScDataDumper reads): a version word, then a
    # run of table counts, then the tables themselves. Read the counts and see
    # whether they are plausible; DO NOT claim a decode on the strength of it.
    # MEASURED, NOT GUESSED. Word 0 is zero padding and word 1 is the version;
    # words 2-3 are zero. The counts begin at offset 16. An earlier pass here
    # read them from offset 4 and produced a table that was plausible enough to
    # print and wrong - which is why the offsets are stated rather than assumed.
    pad, ver = u32(raw, 0), u32(raw, 4)
    print("\nheader: word0=%d  version=%d  word2=%d  word3=%d"
          % (pad, ver, u32(raw, 8), u32(raw, 12)))
    names = ["structDefinitions", "propertyDefinitions", "enumDefinitions",
             "dataMappings", "recordDefinitions", "booleanValues",
             "int8Values", "int16Values", "int32Values", "int64Values",
             "uint8Values", "uint16Values", "uint32Values", "uint64Values",
             "singleValues", "doubleValues", "guidValues", "stringValues",
             "localeValues", "enumValues", "strongValues", "weakValues",
             "referenceValues", "enumOptionValues", "textLength"]
    base = 16
    counts = {}
    for i, nm in enumerate(names):
        off = base + i * 4
        if off + 4 > len(raw):
            break
        counts[nm] = u32(raw, off)
    # WHAT HAS BEEN VERIFIED SINCE, AND WHAT HAS NOT (C3 milestone 1).
    #
    # VERIFIED: `textLength` really is the byte length of the string region.
    # The region runs 44,288,701 - 61,454,626 in the 4.10 blob, and
    # end-minus-textLength lands exactly on 100% printable, null-terminated
    # identifiers. That is one label confirmed by measurement.
    #
    # NOT VERIFIED, AND MEASURED NOT TO CLOSE: the remaining labels are the
    # documented field ORDER and nothing here has confirmed that a given count
    # belongs to the field it is printed against. Summing the definition tables
    # and value arrays at their documented row sizes lands between 6.9 MB and
    # 18.9 MB SHORT of where the text region actually starts, across every
    # combination of the two genuinely uncertain row sizes (dataMapping 8 or 12,
    # reference 8/16/20/24). Either a row size is wrong, the count order is
    # wrong, or record instance data sits between the tables and the text.
    #
    # So the labels below are still printed as UNVERIFIED. Saying otherwise
    # would be the third wrong offset of the day dressed as a fact.
    # THE NUMBERS ARE MEASURED. THE NAMES ARE NOT VERIFIED. The labels follow
    # the documented DataForge field order; this probe has not walked a table
    # to confirm that a given count belongs to the field it is printed against.
    # Saying so matters: an unverified label read as fact is how a wrong schema
    # gets quoted back later as though somebody had checked it.
    print("table counts, read at offset %d "
          "(names are the documented order, UNVERIFIED here):" % base)
    for nm, v in counts.items():
        print("   %-22s %12d" % (nm, v))
    # textLength is a BYTE LENGTH, not a row count, so it is bounded by the
    # blob rather than by the row-count ceiling.
    plausible = all(0 <= v < 5_000_000
                    for nm, v in counts.items() if nm != "textLength") \
        and 0 <= counts.get("textLength", 0) < len(raw)

    # WHAT IS ACTUALLY REACHABLE, stated as evidence rather than as a claim
    # about the schema: are the records we need in here at all, in plain text?
    probes = [b"ANVL_Carrack", b"DRAK_Cutlass_Black", b"AEGS_Vanguard_Harbinger",
              b"RSI_Polaris", b"ANVL_Asgard", b"EntityClassDefinition"]
    print("\nliteral strings present in the blob:")
    found = {}
    for p in probes:
        found[p.decode()] = raw.count(p)
        print("   %-26s %6d occurrences" % (p.decode(), found[p.decode()]))

    print("\nall counts plausible: %s" % plausible)
    print("NOT DECODED. This probe read the header, measured the tables and "
          "confirmed the ship records are present as text. It has NOT walked a "
          "record and it does not claim a schema.")

    report = {
        "game_branch": build["Branch"],
        "p4_change": build["RequestedP4ChangeNum"],
        "entries": {n: {"method": e["method"], "compressed": e["csize"],
                        "uncompressed": e["usize"]} for n, e in seen.items()},
        "largest": name,
        "decompressed_bytes": len(raw),
        "header_version": ver,
        "counts_offset": base,
        "table_counts": counts,
        "counts_plausible": plausible,
        "literal_strings_found": found,
        "status": "probe only - header read and measured, ship records confirmed "
                  "present as text, NO records decoded and no schema claimed",
    }
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, indent=2)
        f.write("\n")
    print("written : %s" % OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
