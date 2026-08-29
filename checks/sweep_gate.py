#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sweep_gate.py - a payload no sweep has passed cannot be uploaded.

RULE16: INDEPENDENT - the verdict is read from a receipt the SWEEP wrote and
compared against a fingerprint recomputed here from the payload on disk. The
deploy scripts contribute neither: they run this and read its exit code. The
thing under test - "is this payload swept and clean" - cannot be answered by
the payload agreeing with itself, because the fingerprint is taken from the
bytes and the verdict from a different program's record of running 98 controls.

Q10, 2026-08-27. THE PROBLEM IT CLOSES, in the queue's own words:

    controls that exist                    98
    controls the deploy actually gates on   4

And it had already bitten. The sweep found 14 failures at 22:15 on 2026-08-27
and the site was built and deployed repeatedly that same evening. The controls
existed, they were red, and nothing stopped anything. **A suite that cannot stop
a deploy is documentation.**

WHY A RECEIPT RATHER THAN RUNNING THE SWEEP ON EVERY DEPLOY
===========================================================
The full sweep takes 613 seconds. Ten minutes on every upload is how a gate gets
switched off by whoever is in a hurry, and a gate that gets switched off is
worth less than one that is merely slow.

So the sweep runs once and leaves a receipt naming the payload it swept. The
deploy compares that fingerprint against the payload it is about to upload. Swept
and unchanged, it goes; changed since, it does not. **The cost lands on the
sweep, once, instead of on every deploy, always.**

WHAT THE FINGERPRINT COVERS, AND WHAT IT DELIBERATELY DOES NOT
==============================================================
Every non-model file in the payload, by path, size and sha256. Models are
covered by COUNT AND TOTAL BYTES rather than content: 258 files and 456 MB of
geometry would take minutes to hash on every deploy, and the failure this has to
catch - a dropped or truncated models folder - moves both numbers. A model
swapped for another of exactly the same size is the gap, and it is named here
rather than left to be discovered.

FAIL CLOSED, IN EVERY DIRECTION
================================
    receipt missing       refused - no sweep has been run against this payload
    fingerprint differs   refused - the payload changed after the sweep
    result not clean      refused, naming the red controls
    receipt unreadable    refused - an unreadable receipt is not a passing one
    a partial sweep       refused - --only swept a subset, which is not a sweep
    a --self-test sweep   refused - inverted expectations are not a clean result
    this gate cannot run  refused by the caller - reported as NOT CHECKED

Rule 15: every open states its encoding.

Usage:
    python checks/sweep_gate.py --fingerprint <payload-dir>
    python checks/sweep_gate.py --check <payload-dir>      exit 0 / 1 / 2
"""

import argparse
import hashlib
import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
RECEIPT = os.path.join(HERE, ".last_sweep.json")

MODEL_EXT = ".glb"


def fingerprint(payload_dir):
    """One string standing for the whole payload. Raises if it cannot look."""
    if not os.path.isdir(payload_dir):
        raise IOError("payload directory does not exist: %s" % payload_dir)
    h = hashlib.sha256()
    files, models, model_bytes = [], 0, 0
    for root, _dirs, names in os.walk(payload_dir):
        for n in sorted(names):
            p = os.path.join(root, n)
            rel = os.path.relpath(p, payload_dir).replace(os.sep, "/")
            if n.lower().endswith(MODEL_EXT):
                models += 1
                model_bytes += os.path.getsize(p)
                continue
            with open(p, "rb") as fh:
                digest = hashlib.sha256(fh.read()).hexdigest()
            files.append((rel, os.path.getsize(p), digest))
    for rel, size, digest in sorted(files):
        h.update(("%s|%d|%s\n" % (rel, size, digest)).encode("utf-8"))
    h.update(("models|%d|%d\n" % (models, model_bytes)).encode("utf-8"))
    if not files:
        raise IOError("no non-model files found in %s - refusing to fingerprint "
                      "an empty payload" % payload_dir)
    return h.hexdigest()


def write_receipt(payload_dir, *, passed, failed, skipped, not_run,
                  partial, self_test, seconds, deployed_only=()):
    """Called by run_all_controls.py when a sweep finishes. ONE writer.

    The receipt records what the sweep SAW, including the reasons it would not
    count as clean. Deciding whether that is good enough is `--check`'s job, so
    a future change to the rule does not need the sweep re-run.
    """
    rec = {
        "fingerprint": fingerprint(payload_dir),
        "payload_dir": os.path.relpath(payload_dir, REPO).replace(os.sep, "/"),
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "seconds": round(seconds, 1),
        "passed": len(passed),
        "failed": sorted(failed),
        "skipped": sorted(skipped),
        "not_run": sorted(not_run),
        "partial": bool(partial),
        "self_test": bool(self_test),
        # FAILURES THAT ARE ABOUT THE LIVE SITE, NOT THIS PAYLOAD.
        #
        # The three --include-deployed controls answer a different question, and
        # one of them - "the served ship page is byte-identical to the one just
        # built" - CANNOT be green until the deploy that makes it so has
        # happened. Counting it against the gate would mean the deploy is
        # blocked by the absence of the deploy.
        #
        # Found on 2026-08-28 by running the sweep the way Sleven asked for it,
        # `--include-deployed`, which nothing had done before. `check()` reports
        # these and does not block on them.
        "deployed_only": sorted(deployed_only),
    }
    with io.open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)
        fh.write("\n")
    return rec


def check(payload_dir):
    """0 clean and current, 1 refused with a reason, 2 could not verify."""
    try:
        want = fingerprint(payload_dir)
    except Exception as exc:
        print("sweep   : COULD NOT FINGERPRINT the payload (%s). Reported as "
              "NOT CHECKED, never as clean." % exc)
        return 2

    if not os.path.exists(RECEIPT):
        print("sweep   : NO SWEEP RECEIPT at %s."
              % os.path.relpath(RECEIPT, REPO))
        print("          No control sweep has been run against this payload, so")
        print("          94 of the 98 controls have not looked at what is about")
        print("          to be uploaded. Run:")
        print("")
        print("              venv\\Scripts\\python.exe checks\\run_all_controls.py")
        return 1

    try:
        with io.open(RECEIPT, "r", encoding="utf-8") as fh:
            rec = json.load(fh)
    except Exception as exc:
        print("sweep   : the sweep receipt could not be read (%s). An "
              "unreadable receipt is not a passing one." % exc)
        return 2

    if rec.get("self_test"):
        print("sweep   : the last sweep ran with --self-test, which INVERTS "
              "every expectation.")
        print("          That is not a clean result, it is a proof that the "
              "controls can fail.")
        return 1

    if rec.get("partial"):
        print("sweep   : the last sweep was PARTIAL (--only), so most controls "
              "did not run.")
        print("          A subset is not a sweep. Run it without --only.")
        return 1

    if rec.get("fingerprint") != want:
        print("sweep   : THE PAYLOAD CHANGED SINCE THE LAST SWEEP.")
        print("          swept   %s" % (rec.get("fingerprint") or "?")[:32])
        print("          current %s" % want[:32])
        # THE %s WAS ON THE LINE ABOVE AND THE % OPERATOR ON THIS ONE, so this
        # branch printed "swept at %s." and then raised TypeError. Found on
        # 2026-08-28 by Sleven running the deploy while a sweep was rebuilding
        # the payload - the first time this path had ever executed.
        #
        # It failed CLOSED, which is the safe direction, but it refused by
        # CRASHING rather than by deciding. An exception here is
        # indistinguishable from a considered refusal, and on the success path
        # the same mistake would have blocked every deploy in the project.
        print("          swept at %s. Re-run the sweep against what is actually"
              % (rec.get("at") or "an unrecorded time"))
        print("          about to be uploaded.")
        return 1

    live = set(rec.get("deployed_only") or [])
    bad = [n for n in (list(rec.get("failed") or [])
                       + list(rec.get("not_run") or [])) if n not in live]

    # REPORTED WHETHER OR NOT THEY BLOCK. A deployed-site failure is real
    # information - the served site is behind, or is broken - and hiding it here
    # would be the silent success this whole file exists against.
    if live:
        print("sweep   : %d control(s) failed ABOUT THE LIVE SITE rather than "
              "about this payload:" % len(live))
        for name in sorted(live):
            print("          LIVE     %s" % name)
        print("          These do not block: one of them asserts the SERVED page")
        print("          matches the one just built, which no action before a")
        print("          deploy can make true. Deploying is their remedy, and")
        print("          re-running with --include-deployed afterwards is how")
        print("          you find out whether it worked.")

    if bad:
        print("sweep   : the last sweep of THIS payload was not clean.")
        for name in bad:
            where = "FAILED" if name in (rec.get("failed") or []) else "NOT RUN"
            print("          %-8s %s" % (where, name))
        print("          A control that could not be run is counted against the")
        print("          sweep, never as a pass.")
        return 1

    print("sweep   : %d control(s) green against this exact payload (%s)"
          % (rec.get("passed", 0), rec.get("at")))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--fingerprint", metavar="DIR")
    ap.add_argument("--check", metavar="DIR")
    a = ap.parse_args(argv)
    if a.fingerprint:
        try:
            print(fingerprint(a.fingerprint))
            return 0
        except Exception as exc:
            print("could not fingerprint: %s" % exc)
            return 2
    if a.check:
        return check(a.check)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
