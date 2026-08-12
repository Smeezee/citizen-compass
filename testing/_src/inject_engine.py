#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
inject_engine.py - device_engine.js is the only writer of the device panel.

The engine existed in three places: device_engine.js, keybinds.src.html and
_layer.src.html. Nothing kept them in step. Editing the master and rebuilding
produced a clean build, a passing deploy, and two hosts still running the old
code - the exact failure mode that has already cost this project a viewer
material fix and an overlay patch, both applied to a file nobody read.

This copies the master into both hosts between fixed boundary lines. It runs
from build_deploy.py, so drift cannot survive a build.

Rule 14: one writer per artifact. Rule 15: encodings stated.
"""
import io, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(HERE, "device_engine.js")
HOSTS  = ["keybinds.src.html", "_layer.src.html"]

START = "/* ================================================================\n   DEVICE PANEL rev 2"
END   = '  if(dev!=="KBM") renderDevice(); });'

engine = io.open(MASTER, encoding="utf-8").read().rstrip("\n")
if not engine.startswith(START):
    sys.exit("device_engine.js no longer starts with the boundary marker.\n"
             "Update START in inject_engine.py deliberately - do not let this\n"
             "script guess where the engine begins.")
if not engine.endswith(END):
    sys.exit("device_engine.js no longer ends with the boundary marker.\n"
             "Update END in inject_engine.py deliberately.")

# --------------------------------------------------------------------------
# SYNTAX GATE. Runs BEFORE the first write, and refuses everything on failure.
#
# WHY: this script is the single writer of the device panel, and it copies
# device_engine.js into BOTH hosts in one step. A syntax error in the source
# therefore becomes a syntax error on the keybind page AND the homepage at once
# - and on the homepage that is the site's own layer script, not just a panel.
# The existing marker checks refuse a structurally wrong input; they have no
# opinion on whether the payload is valid code.
#
# This happened for real on 2026-08-12: a newline landed inside a JS string
# literal, this script copied it into both hosts, build_deploy.py printed
# "safe to deploy" and exited 0. It was caught only because somebody happened to
# run `node --check` by hand. The guard removes the "happened to".
#
# FAIL CLOSED WHEN node IS ABSENT, deliberately. Warning and continuing would
# reproduce exactly that failure while appearing to have a guard - which rule 12
# names: a check that cannot fail is not a check. node is already a build
# dependency of this project (roundtrip.js and mutate.js run under it), so this
# adds no new tool, only a new moment it is required.
def _syntax_check(path, label):
    exe = shutil.which("node")
    if exe is None:
        sys.exit(
            "NODE NOT ON PATH, so " + label + " could not be syntax-checked.\n"
            "Refusing to inject rather than copy unchecked JavaScript into both "
            "hosts.\n"
            "This is a deliberate fail-closed: a guard that quietly skips itself "
            "is worse than no guard, because it manufactures confidence.\n"
            "Install node, or run the injection where it is available.")
    r = subprocess.run([exe, "--check", path], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        sys.exit(
            label + " IS NOT VALID JAVASCRIPT - nothing was written.\n\n" +
            (r.stderr or r.stdout or "").strip() +
            "\n\nBoth hosts are untouched. Fix the source and run again.")


_syntax_check(MASTER, "device_engine.js")

changed, same = [], []
for name in HOSTS:
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        sys.exit("HOST MISSING: %s - refusing to half-inject" % name)
    s = io.open(path, encoding="utf-8").read()

    if s.count(START) != 1:
        sys.exit("%s: START marker appears %d times, expected 1" % (name, s.count(START)))
    if s.count(END) != 1:
        sys.exit("%s: END marker appears %d times, expected 1" % (name, s.count(END)))

    a = s.index(START)
    b = s.index(END) + len(END)
    if b <= a:
        sys.exit("%s: END marker appears before START - boundaries are wrong" % name)

    new = s[:a] + engine + s[b:]
    if new == s:
        same.append(name); continue
    io.open(path, "w", encoding="utf-8", newline="\n").write(new)
    changed.append(name)

print("engine injected from device_engine.js (%d bytes)" % len(engine))
if changed: print("  updated:   " + ", ".join(changed))
if same:    print("  unchanged: " + ", ".join(same))
