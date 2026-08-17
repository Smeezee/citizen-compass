#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prove the history KEEPS things, and that both halves share one shape.

Hard rule 12, and the order names the check itself:

    "the check that matters is one proving a CHANGED card produces two rows
     with different fingerprints and BOTH SURVIVE. A history that has never been
     observed retaining anything is the same category of thing it exists to
     prevent."

The roadmap watcher's half is proved by `go test ./roadmap-watcher`. This proves
the model-fingerprint half the same way, and then checks the one thing neither
side can check alone: that the two logs carry the SAME COLUMN NAMES, which is
the only design constraint the order imposes.

Run:  python checks/_verify_fingerprint_history.py

Rule 15: encodings stated.
"""

import io
import json
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import build_model_fingerprint_history as H  # noqa: E402

failures = []


def check(name, ok, detail):
    if ok:
        print("  [ok  ] %s" % name)
    else:
        failures.append(name)
        print("  [FAIL] %s\n         %s" % (name, detail))


def fake_model(path, body):
    with open(path, "wb") as fh:            # binary, no encoding - rule 15
        fh.write(body)


def run_against(tmp, source):
    """One observation run over a throwaway model folder."""
    H.MODELS = os.path.join(tmp, "models")
    H.OUTDIR = tmp
    H.HISTORY = os.path.join(tmp, "model_fingerprint_history.jsonl")
    H.SNAPSHOT = os.path.join(tmp, "does_not_exist.json")
    H.GEO = ""
    argv = sys.argv
    sys.argv = ["x", "--source=" + source]
    # CAPTURE WHAT IT SAYS, without silencing it into a black hole: the report
    # text is itself checked below. sys.stdout.buffer is read-only, so the
    # module's own say() is swapped instead of the stream.
    said = []
    real_say = H.say
    try:
        H.say = lambda line: said.append(line)
        H.main()
    finally:
        H.say = real_say
        sys.argv = argv
    return chr(10).join(said)


def main():
    print("the fingerprint history, driven with input that must fail it")
    print()

    tmp = tempfile.mkdtemp(prefix="cc-fphist-")
    try:
        os.makedirs(os.path.join(tmp, "models"))
        glb = os.path.join(tmp, "models", "Constellation_Taurus.glb")

        # ---- THE CHECK THAT MATTERS -----------------------------------
        fake_model(glb, b"glTF-as-it-was")
        run_against(tmp, "scheduled")
        fake_model(glb, b"glTF-after-the-rework")     # the ship is reworked
        report = run_against(tmp, "scheduled")

        rows, bad = H.read_history(H.HISTORY)
        check("a changed model produces TWO rows and both survive",
              len(rows) == 2 and bad == 0,
              "got %d row(s), %d unreadable - the second run overwrote the "
              "first, which is the defect this closes" % (len(rows), bad))
        if len(rows) == 2:
            check("the two rows carry DIFFERENT fingerprints",
                  rows[0]["sha256"] != rows[1]["sha256"],
                  "both say %s - the change was not recorded" % rows[0]["sha256"][:12])
            check("the FIRST row still says what the model was",
                  rows[0]["sha256"] ==
                  __import__("hashlib").sha256(b"glTF-as-it-was").hexdigest(),
                  "the history is being rewritten under us")
            check("and the change is REPORTED, not only stored",
                  "CHANGED since the last run" in report,
                  "a history nobody is told about is a history nobody reads")

        # EVERY ROW CARRIES ITS OWN CONTEXT.
        for i, r in enumerate(rows):
            check("row %d is self-sufficient" % i,
                  all(r.get(k) for k in ("at", "kind", "subject", "name",
                                         "fingerprint", "source", "file",
                                         "sha256")) and r.get("bytes"),
                  "missing fields: %r" % r)

        # ---- A RUN THAT CHANGES NOTHING STILL RECORDS -----------------
        run_against(tmp, "scheduled")
        rows3, _ = H.read_history(H.HISTORY)
        check("a run where nothing changed still appends",
              len(rows3) == 3,
              "got %d rows - the archive would have holes exactly where a model "
              "sat still, and 'was it the same in June?' becomes unanswerable"
              % len(rows3))

        # ---- NEGATIVE CONTROL: THE RETENTION CHECK CAN FAIL -----------
        #
        # Everything above asserts rows survive. If the assertion could not
        # detect a row that did NOT survive, it would pass on a file being
        # overwritten every run - the exact failure being fixed, wearing a green
        # tick. So destroy one the way a rewriting writer would.
        keep = rows3[-1]
        with io.open(H.HISTORY, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(keep, sort_keys=True) + "\n")
        rows4, _ = H.read_history(H.HISTORY)
        check("NEGATIVE CONTROL: the same check DETECTS a destroyed history",
              len(rows4) == 1,
              "it still reports %d rows after the file was truncated to one - "
              "the check cannot tell a kept history from a destroyed one"
              % len(rows4))

        # ---- A RUN THAT MEASURED NOTHING IS REFUSED -------------------
        shutil.rmtree(os.path.join(tmp, "models"))
        os.makedirs(os.path.join(tmp, "models"))
        stopped = False
        try:
            run_against(tmp, "scheduled")
        except SystemExit:
            stopped = True
        check("NEGATIVE CONTROL: a run that found no models REFUSES to append",
              stopped,
              "it appended an empty observation, which is indistinguishable "
              "from every model having vanished")

        # ---- ONE SHAPE ACROSS BOTH HALVES -----------------------------
        #
        # The order's only design constraint: the roadmap watcher and the model
        # fingerprints must be readable "as one time series". Neither side can
        # check that alone, so it is checked here, against the Go source.
        go = io.open(os.path.join(ROOT, "roadmap-watcher", "history.go"),
                     encoding="utf-8").read()
        block = go[go.index("type Observation struct"):go.index("\n}", go.index(
            "type Observation struct"))]
        go_cols = set(re.findall(r'json:"([a-z_]+)"', block))
        py_cols = set(rows3[0].keys()) if rows3 else set()
        spine = {"at", "kind", "subject", "name", "fingerprint", "source"}
        check("both halves carry the shared spine %s" % sorted(spine),
              spine <= go_cols and spine <= py_cols,
              "watcher is missing %s, models are missing %s"
              % (sorted(spine - go_cols), sorted(spine - py_cols)))
        check("NEGATIVE CONTROL: the column reader actually read something",
              len(go_cols) >= 8,
              "found only %d columns in the Go struct, so the check above "
              "passed by reading nothing" % len(go_cols))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if failures:
        print("VERIFY FAILED (%d)" % len(failures))
        for f in failures:
            print("  - %s" % f)
        return 1
    print("VERIFY PASSED - a changed model keeps both rows, a destroyed history "
          "is detected, and both halves share one shape")
    return 0


if __name__ == "__main__":
    sys.exit(main())
