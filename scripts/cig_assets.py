#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cig_assets.py - the register of which assets came from Cloud Imperium Games.

A4. THE OFF SWITCH BEGINS HERE.
===============================
Sleven's commitment is that if Cloud Imperium Games have a problem, the content
comes down. A promise that cannot be executed in ten minutes is not a promise,
and the thing that makes it executable is knowing WHICH FILES to remove without
having to work it out under pressure.

SO THE SOURCE IS A FIELD ON A RECORD, NOT A FILENAME AND NOT A FOLDER.

Folders get reorganised. Prefixes get dropped by a build step nobody remembered
was there. A `models/cig/` directory survives exactly until the first person who
tidies up. A field in a register survives, and it can carry the date, the URL it
came from and a note about what it is - none of which fits in a filename.

    {
      "assets": [
        {"file": "Redeemer.glb", "kind": "model", "source": "cig-holoviewer",
         "added": "2026-08-22", "origin": "https://robertsspaceindustries.com/...",
         "note": "hull only"}
      ]
    }

`source` is the field the takedown reads. Anything whose source is in
`CIG_SOURCES` comes down when the switch is pulled; everything else stays.

NOTHING IS REGISTERED YET, AND THAT IS CORRECT. No RSI holoviewer asset has
been fetched - the order that built this forbids fetching one until
reconnaissance comes back. This file is the half of the promise that has to
exist BEFORE the first asset lands, so that there is never a minute in which
CIG-sourced content sits on this site without a way to remove it.

Rule 15: every open states its encoding.
"""

import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
# CC_CIG_REGISTER points the register somewhere else. This exists so the
# takedown and the mark guard can be exercised as REAL RUNS against a fixture
# register - a procedure that is only ever described is not a control. It is
# read at call time, not import time, so a test can set it around one call.
_DEFAULT_REGISTER = os.path.join(REPO, "data-layer", "cig_assets.json")


def register_path():
    return os.environ.get("CC_CIG_REGISTER") or _DEFAULT_REGISTER


# Kept as a module attribute for callers that read it directly; the functions
# below all go through register_path() so the override cannot be bypassed by
# forgetting to pass one.
REGISTER = _DEFAULT_REGISTER

# The sources whose assets the takedown removes. A set rather than one string
# because "came from CIG" may later need to distinguish the holoviewer from the
# Fan Kit, which carry different permissions.
CIG_SOURCES = {"cig-holoviewer", "cig-fankit-restricted"}

# Where a built asset of each kind lives inside the deploy directory.
KIND_DIRS = {
    "model": "models",
    "image": "images",
    "font": "fonts",
}


def _empty():
    return {"schema": 1, "assets": []}


def load(path=None):
    """The register. A missing file is an EMPTY register, not an error - that is
    the honest state before the first asset arrives, and it must not stop a
    build."""
    path = path or register_path()
    if not os.path.exists(path):
        return _empty()
    with io.open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict) or not isinstance(data.get("assets"), list):
        raise ValueError(
            "%s is not a valid asset register - it must be an object with an "
            "`assets` list. Refusing to guess at its contents, because the "
            "thing that reads it decides what gets deleted." % path)
    return data


def save(data, path=None):
    path = path or register_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=1, sort_keys=True, ensure_ascii=False)
        fh.write("\n")


def tagged(path=None):
    """Every asset whose source makes it subject to takedown."""
    return [a for a in load(path).get("assets", [])
            if a.get("source") in CIG_SOURCES]


def untagged(path=None):
    """Every registered asset that is NOT subject to takedown.

    Present so the takedown can prove what it LEFT ALONE, which is the half
    that catches a script that just deletes everything.
    """
    return [a for a in load(path).get("assets", [])
            if a.get("source") not in CIG_SOURCES]


def tagged_count(path=None):
    return len(tagged(path))


def deploy_paths(asset, deploy_dir):
    """Where this asset actually sits in a built site."""
    sub = KIND_DIRS.get(asset.get("kind"))
    if not sub or not asset.get("file"):
        return []
    return [os.path.join(deploy_dir, sub, asset["file"])]


def register(file, kind, source, origin=None, note=None, path=None):
    """Add one asset. Used by whatever lands assets, and by the tests.

    Refuses an unknown `kind`, because an asset filed under a kind the takedown
    does not know about is an asset the takedown will not find - which is a
    silent hole in the exact promise this file exists to keep.
    """
    if kind not in KIND_DIRS:
        raise ValueError(
            "unknown asset kind %r - the takedown would not know where to look "
            "for it. Known kinds: %s" % (kind, ", ".join(sorted(KIND_DIRS))))
    if not file:
        raise ValueError("an asset must have a file name")
    data = load(path)
    for a in data["assets"]:
        if a.get("file") == file and a.get("kind") == kind:
            a.update({"source": source, "origin": origin, "note": note})
            save(data, path)
            return a
    rec = {"file": file, "kind": kind, "source": source}
    if origin:
        rec["origin"] = origin
    if note:
        rec["note"] = note
    data["assets"].append(rec)
    save(data, path)
    return rec
