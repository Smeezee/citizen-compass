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
import io, os, sys

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
