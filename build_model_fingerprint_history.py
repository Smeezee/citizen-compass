#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_model_fingerprint_history.py - what the model WAS, kept forever.

    order   docs/WORKORDER_historian-foundations-2026-08-16.md §1 (C3, 2026-08-16)
    pair    roadmap-watcher/history.go - the same defect, the same treatment,
            the same column names

THE DEFECT
==========

`data-layer/derived/model-fingerprints/model_fingerprints.json` holds ONE
current fingerprint per model. It can say a .glb no longer matches. It cannot
say what it looked like last month, and it never could, because each rebuild
overwrites the last.

C3 said it plainly about their own file: "Mine. Same defect, and I built it that
way three days ago without thinking it through."

WHY IT IS URGENT WHILE THE THING IT SERVES IS NOT
=================================================

The value is entirely in elapsed time and it CANNOT BE BACKFILLED. A ship
rework that lands next month can only be compared against a measurement taken
before it. Nobody outside this project can run this check at all - it is the one
Constellation-rework tripwire we have - and every week without a history is a
week that can never be asked about.

WHAT THIS WRITES
================

`model_fingerprint_history.jsonl`, append-only, one row per model per run:

    at, kind, subject, name, fingerprint, source     <- shared with the watcher
    file, sha256, bytes, verts, extent, measured_by  <- this side's own fields

The first six are deliberately identical to the roadmap watcher's rows so a
later query can read both as one time series. That is the order's only design
constraint.

THE FINGERPRINT IS THE SHA256 OF THE FILE, and the row carries it in full as
well as in the shared `fingerprint` column, so a row is self-sufficient: nothing
here needs another file to be interpreted in ten years.

VERTEX COUNTS AND BOUNDING BOXES ARE OPTIONAL AND MARKED
========================================================

The hash and the byte size are read from the file every run and are always
present. Geometry needs the model decoded (testing/_src/decode_glb_points.js),
which is not always available - so each row records `measured_by` as "file" or
"file+geometry" and NEVER carries a geometry field it did not measure. A row
that says nothing about vertices is honest; a row that says 0 would be a lie
that outlives everyone who could correct it.

Rule 15: encodings stated.
"""

import glob
import hashlib
import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, "testing", "_deploy", "models")
OUTDIR = os.path.join(HERE, "data-layer", "derived", "model-fingerprints")
HISTORY = os.path.join(OUTDIR, "model_fingerprint_history.jsonl")
SNAPSHOT = os.path.join(OUTDIR, "model_fingerprints.json")

GEO = os.environ.get("CC_GEO_DIR", "")


def say(line):
    sys.stdout.buffer.write((line + "\n").encode("utf-8", "backslashreplace"))


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:            # binary: no encoding, rule 15
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def geometry_for(stem):
    """Vertex count and extent, if this model has been decoded. None otherwise."""
    if not GEO:
        return None
    p = os.path.join(GEO, stem + ".json")
    if not os.path.exists(p):
        return None
    with io.open(p, "r", encoding="utf-8") as fh:
        g = json.load(fh)
    return {
        "verts": g.get("count"),
        "extent": [round(g["max"][k] - g["min"][k], 3) for k in range(3)],
    }


def read_history(path):
    """Every row. A bad line is skipped and COUNTED, never fatal - this file may
    be years old when a power cut catches it mid-write."""
    if not os.path.exists(path):
        return [], 0
    rows, bad = [], 0
    with io.open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except ValueError:
                bad += 1
    return rows, bad


def append_observations(path, rows):
    """APPEND ONLY. Opened "a", never "w".

    That mode is the entire guarantee, and it is the property to preserve if
    anything in this file is ever edited: no code path here opens this file for
    writing in any other way.
    """
    with io.open(path, "a", encoding="utf-8", newline="\n") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
        fh.flush()
        os.fsync(fh.fileno())      # the copy that cannot be rebuilt
    return len(rows)


def main():
    source = "manual"
    for a in sys.argv[1:]:
        if a.startswith("--source="):
            source = a.split("=", 1)[1]

    files = sorted(glob.glob(os.path.join(MODELS, "*.glb")))
    if not files:
        sys.exit("NO MODELS FOUND in %s.\nRefusing to append a run that measured "
                 "nothing - an empty observation is indistinguishable from every "
                 "model having vanished." % MODELS)

    if not os.path.isdir(OUTDIR):
        os.makedirs(OUTDIR)

    previous, bad = read_history(HISTORY)
    last_by_subject = {}
    for r in previous:
        last_by_subject[r.get("subject")] = r

    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    rows, changed, geometry_rows = [], [], 0
    for path in files:
        stem = os.path.basename(path)[:-4]
        digest = sha256_of(path)
        row = {
            "at": now,
            "kind": "model",
            "subject": stem,
            "name": stem,
            "fingerprint": digest[:16],
            "source": source,
            "file": os.path.basename(path),
            "sha256": digest,
            "bytes": os.path.getsize(path),
            "measured_by": "file",
        }
        geo = geometry_for(stem)
        if geo:
            row.update(geo)
            row["measured_by"] = "file+geometry"
            geometry_rows += 1
        rows.append(row)

        was = last_by_subject.get(stem)
        if was and was.get("sha256") != digest:
            changed.append((stem, was.get("sha256", "")[:12], digest[:12],
                            was.get("at")))

    n = append_observations(HISTORY, rows)

    say("appended %d observation(s) to %s" % (n, os.path.relpath(HISTORY, HERE)))
    say("  %d model(s) | %d with geometry | source=%s"
        % (len(files), geometry_rows, source))
    if bad:
        say("  %d unreadable line(s) already in the history - skipped, not "
            "discarded" % bad)
    if not previous:
        say("  THIS IS THE FIRST RUN. Every row is a baseline, not news - a "
            "history starts today and answers questions from tomorrow.")
    elif changed:
        say("  %d MODEL(S) CHANGED since the last run:" % len(changed))
        for stem, old, new, when in changed:
            say("    %-40s %s -> %s   (last seen %s)" % (stem, old, new, when))
    else:
        say("  no model changed since the previous run - and that IS the "
            "observation, recorded rather than assumed.")

    # The snapshot C3 produced stays exactly as it is. It is a different
    # artifact with a different writer, and this does not touch it.
    if os.path.exists(SNAPSHOT):
        say("  (%s untouched - it has its own writer)"
            % os.path.relpath(SNAPSHOT, HERE))
    return 0


if __name__ == "__main__":
    sys.exit(main())
