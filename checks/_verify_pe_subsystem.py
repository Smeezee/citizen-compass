#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G7: read the PE subsystem byte off the collector, with a reader proven to

RULE16: INDEPENDENT - the byte is read out of the built binary by a reader this
file proves first, against executables whose value is known because they
were made here. The collector is never asked what subsystem it was linked
for; the file is.
distinguish 2 from 3.

WHY AN INDEPENDENT READER
=========================

`citizen-collector/build.ps1` already reads the subsystem byte and refuses to
finish if it is not 2. That is the right design and it is why this defect
cannot ship again. But "the build script said 2" is the build script grading
its own homework, and the whole history of this bug is a claim about a build
flag that nobody ever checked against the artifact:

    Seven source files said the program is built -H windowsgui. No build
    command anywhere passed it. Both shipped binaries carried subsystem 3.
    Everyone read the comment and believed it. The comment was the defect.

So this reads the bytes again, from a second implementation, in a different
language.

AND THE READER ITSELF IS PROVEN
===============================

A reader that returned 2 for everything would "confirm" every binary ever
built. So this does not only read the GUI binaries - it builds a deliberately
CONSOLE binary into a scratch directory (outside the repo, never installed,
never released) and requires the reader to come back with 3. A check that
cannot produce the failing value has not established the passing one.

Run: venv/Scripts/python.exe checks/_verify_pe_subsystem.py

Rule 15: binary mode takes no encoding and is correct as written.
"""

import os
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COLLECTOR = REPO / "citizen-collector"

SUBSYSTEM_NAMES = {2: "WINDOWS_GUI (no console)", 3: "WINDOWS_CUI (console)"}


def pe_subsystem(path):
    """The Subsystem field of a PE optional header, read from the file.

    Layout, so the offsets are not magic: e_lfanew at 0x3C points at the PE
    signature; the signature is 4 bytes; the COFF header is 20; Subsystem sits
    68 bytes into the optional header that follows.
    """
    with open(path, "rb") as fh:          # binary mode - no encoding, rule 15
        fh.seek(0x3C)
        pe_offset = struct.unpack("<I", fh.read(4))[0]
        fh.seek(pe_offset)
        if fh.read(4) != b"PE\0\0":
            raise ValueError("not a PE file: %s" % path)
        fh.seek(pe_offset + 4 + 20 + 68)
        return struct.unpack("<H", fh.read(2))[0]


def main():
    passed, failed = 0, []

    def record(ok, label, detail=""):
        nonlocal passed
        if ok:
            passed += 1
            print("  ok   %s" % label)
        else:
            failed.append(("%s %s" % (label, detail)).strip())
            print("  FAIL %s %s" % (label, detail))

    # ---- THE READER MUST BE ABLE TO SAY 3 --------------------------------
    print("--- the reader is proven against a binary that MUST be console ---")
    scratch = Path(tempfile.mkdtemp(prefix="cc_pe_control_"))
    console_exe = scratch / "console_control.exe"
    build = subprocess.run(
        ["go", "build", "-o", str(console_exe), "."],
        cwd=str(COLLECTOR), capture_output=True, text=True, timeout=900,
    )
    if build.returncode != 0 or not console_exe.exists():
        failed.append(
            "NOT PERFORMED - could not build the console control binary, so "
            "the reader is UNPROVEN and the numbers below are not evidence. "
            "go build said: %s" % (build.stderr or "")[:300])
    else:
        got = pe_subsystem(console_exe)
        record(got == 3,
               "a build with NO -H=windowsgui reads back as 3 (%s)"
               % SUBSYSTEM_NAMES.get(got, got),
               "it read %r - a reader that cannot produce 3 cannot confirm 2"
               % got)
        print("       (control binary left in %s - outside the repo, never "
              "installed, never released)" % scratch)

    # ---- AND NOW THE REAL ARTIFACTS --------------------------------------
    print("\n--- the built collectors ---")
    for name in ("collector.exe", "collector-master.exe"):
        path = COLLECTOR / name
        if not path.exists():
            failed.append("NOT PERFORMED - %s does not exist, so nothing was "
                          "read. Run citizen-collector/build.ps1 -Both first."
                          % name)
            continue
        got = pe_subsystem(path)
        record(got == 2,
               "%s reads back subsystem %d - %s"
               % (name, got, SUBSYSTEM_NAMES.get(got, "unknown")),
               "it is %d. Subsystem 3 means Windows opens a console for every "
               "launch, and closing that console kills the collector." % got)

    print("\n" + "=" * 62)
    if failed:
        print("FAILED %d of %d:" % (len(failed), passed + len(failed)))
        for x in failed:
            print("  -", x)
        return 1
    print("All %d assertions passed." % passed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
