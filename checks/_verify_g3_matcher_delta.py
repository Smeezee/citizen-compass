#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""G3's acceptance number, isolated: what did the MATCHER change, and only it?

WHY THIS EXISTS AND WHY IT IS SEPARATE
======================================

G3's acceptance is "placed goes 29 -> 31, skipped goes 39 -> 37". Re-running
the build and reading the new counts CANNOT establish that, and the first
attempt proved it: the run came back 35 placed / 8 refused / 25 skipped.

The reason is that two things changed at once. The matcher gained a second
pass, AND the decoded geometry the build reads was regenerated - the previous
run's geometry directory was missing twelve models, which is why twelve ships
were skipped for "no decoded geometry" rather than for any name reason. Twelve
ships changing category for a reason that has nothing to do with G3 makes the
before/after counts unreadable.

So this does not compare against a remembered number. It runs the SAME BUILD,
over the SAME GEOMETRY, TWICE - once with the two-pass matcher and once with
pass 1 alone - and diffs the two reports. Everything except the matcher is held
constant, by construction rather than by assumption, and what comes out is the
matcher's contribution and nothing else.

That is also the honest way to report a number to Sleven that does not match
the one the order predicted: show the experiment that separates the causes,
rather than the count that mixes them.

READS data-layer/derived/hull-geometry/ by default, CC_GEO_DIR overriding
it, and says NOT PERFORMED rather than passing quietly when there is no
geometry to read -
this check cannot run without decoded geometry, and a check that reports
success having not looked is the failure mode this project names SILENT
SUCCESS.

Run: CC_GEO_DIR=<geo> venv/Scripts/python.exe checks/_verify_g3_matcher_delta.py

Rule 15: encodings stated.
"""

import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "..")
sys.path.insert(0, REPO)

REPORT = os.path.join(REPO, "data-layer", "derived", "holo-hardpoints-join",
                      "join_report.json")
OUT = os.path.join(REPO, "data-layer", "derived", "holo-hardpoints-join",
                   "hardpoints_join.json")
MANIFEST = os.path.join(REPO, "data-layer", "derived", "holo-hardpoints-join",
                        "MANIFEST.json")

failures = []


def check(name, ok, detail=""):
    if ok:
        print("  [ok  ] %s" % name)
    else:
        failures.append(name)
        print("  [FAIL] %s\n         %s" % (name, detail))


def read_report():
    with io.open(REPORT, "r", encoding="utf-8") as fh:
        return json.load(fh)


def counts(report):
    return {k: len(v) for k, v in report.items()}


class _Sink(object):
    """Somewhere for the build's own chatter to go.

    It has a `.buffer`, because build_hardpoint_join.say() writes UTF-8 bytes
    straight to `sys.stdout.buffer` rather than through the text layer - which
    is the right call on Windows, where the console codepage would mangle a
    ship called tok.yai, and the reason this needs more than a StringIO.
    """

    def __init__(self):
        self.buffer = io.BytesIO()

    def write(self, text):
        self.buffer.write(text.encode("utf-8", "backslashreplace"))
        return len(text)

    def flush(self):
        pass


def run_build(quiet=True):
    """Run the build in-process and return the report it wrote."""
    import build_hardpoint_join as B

    saved_out = sys.stdout
    if quiet:
        sys.stdout = _Sink()
    try:
        rc = B.main()
    finally:
        sys.stdout = saved_out
    if rc != 0:
        raise SystemExit("the build returned %r - nothing can be concluded" % rc)
    return read_report()


def main():
    # THE REPO NOW HAS A STANDARD PLACE FOR DECODED GEOMETRY, so the check no
    # longer has to be told where it is.
    #
    # This reported NOT PERFORMED on every scheduled run since it was written,
    # because nothing in the sweep set CC_GEO_DIR. Honest, and useless: a check
    # that has never once executed is not protecting anything, and a permanent
    # skip in a green sweep is a line people stop reading.
    #
    # `data-layer/derived/hull-geometry/` is where decode_glb_points.js writes
    # and where build_matched.py already looks by default - the same fallback,
    # spelled the same way, so the check and the build cannot end up reading
    # different geometry. The environment variable still wins when set.
    #
    # NOT PERFORMED remains the answer when there is genuinely nothing to read.
    # That path is unchanged: it now fires on an empty or absent directory
    # rather than on an unset variable.
    geo = os.environ.get("CC_GEO_DIR") or os.path.join(
        REPO, "data-layer", "derived", "hull-geometry")
    have = (os.path.isdir(geo)
            and any(f.endswith(".json") for f in os.listdir(geo)))
    if not have:
        print("NOT PERFORMED - no decoded geometry at %s, so the build cannot "
              "read any hull and this check cannot look at anything." % geo)
        print("Regenerate it with:")
        print("  node testing/_src/decode_glb_points.js <dir> "
              "testing/_deploy/models/*.glb")
        print("Reported as NOT PERFORMED, never as passed.")
        return 2
    os.environ["CC_GEO_DIR"] = geo
    print("geometry: %s (%d decoded hulls)"
          % (geo, sum(1 for f in os.listdir(geo) if f.endswith(".json"))))

    import build_hardpoint_join as B

    # The build writes three real artifacts. Put them back exactly as found, so
    # an experiment cannot leave the repo holding the losing arm of its own
    # A/B - which would be a second writer on an artifact by accident.
    stash = tempfile.mkdtemp(prefix="cc_g3_delta_")
    for path in (REPORT, OUT, MANIFEST):
        if os.path.exists(path):
            shutil.copy2(path, os.path.join(stash, os.path.basename(path)))

    print("G3: the matcher's contribution, with geometry held constant")
    print()

    try:
        print("  running the build with PASS 1 ONLY (the matcher as it was) ...")
        two_pass = B.resolve_by_rule
        B.resolve_by_rule = B._resolve_by_rule_pass1_only
        try:
            before = run_build()
        finally:
            B.resolve_by_rule = two_pass

        print("  running the build with BOTH PASSES (the matcher as it is) ...")
        after = run_build()
    finally:
        for path in (REPORT, OUT, MANIFEST):
            src = os.path.join(stash, os.path.basename(path))
            if os.path.exists(src):
                shutil.copy2(src, path)
        print("  (artifacts restored to their pre-experiment state from %s)"
              % stash)

    cb, ca = counts(before), counts(after)
    print()
    print("  %-18s %8s %8s %8s" % ("bucket", "pass 1", "both", "delta"))
    for k in sorted(set(cb) | set(ca)):
        print("  %-18s %8d %8d %+8d" % (k, cb.get(k, 0), ca.get(k, 0),
                                        ca.get(k, 0) - cb.get(k, 0)))
    print()

    # ---- THE ACCEPTANCE, AS A DELTA RATHER THAN AN ABSOLUTE ---------------
    check("G3: the second pass places exactly 2 more ships",
          ca.get("placed", 0) - cb.get("placed", 0) == 2,
          "placed moved by %+d (%d -> %d). Two is the right answer; more means "
          "the loosening caught ships it was not for."
          % (ca.get("placed", 0) - cb.get("placed", 0),
             cb.get("placed", 0), ca.get("placed", 0)))

    check("G3: and skips exactly 2 fewer",
          cb.get("skipped", 0) - ca.get("skipped", 0) == 2,
          "skipped moved by %+d (%d -> %d)"
          % (ca.get("skipped", 0) - cb.get("skipped", 0),
             cb.get("skipped", 0), ca.get("skipped", 0)))

    check("G3: it refuses no more than before - a name match that then fails "
          "the shape check would show up here",
          ca.get("refused", 0) == cb.get("refused", 0),
          "refused moved %d -> %d" % (cb.get("refused", 0), ca.get("refused", 0)))

    placed_before = {row[0] for row in before["placed"]}
    placed_after = {row[0] for row in after["placed"]}
    gained = sorted(placed_after - placed_before)
    lost = sorted(placed_before - placed_after)

    check("G3: the two ships gained are the two Ares, by name",
          gained == ["Ares_Inferno", "Ares_Ion"],
          "gained %s" % (gained,))
    check("G3: and NOTHING was lost - the second pass cannot take a ship away "
          "from the first",
          lost == [], "lost %s" % (lost,))

    skipped_after = {row[0] for row in after["skipped"]}
    check("G3: the 25 still-refused ships are still refused, by name",
          len(skipped_after) == 25,
          "%d ships are still skipped, expected 25: %s"
          % (len(skipped_after), sorted(skipped_after)))

    # ---- AND THE PAIRS THAT DID CHANGE STILL FACED EVERY GUARD -----------
    #
    # Being placed is not the same as being placed safely. A ship that got in
    # by name and then skated past the shape check would be exactly the "wrong
    # 25" failure wearing the right count.
    by_stem = {row[0]: row for row in after["placed"]}
    for stem in ("Ares_Inferno", "Ares_Ion"):
        row = by_stem.get(stem)
        check("G3: %s was placed with a real mount count and a measured shape "
              "error, not waved through" % stem,
              row is not None and row[1] > 0 and isinstance(row[2], float),
              "its placed row is %r" % (row,))

    print()
    if failures:
        print("VERIFY FAILED (%d)" % len(failures))
        for f in failures:
            print("  -", f)
        return 1
    print("VERIFY PASSED - with geometry held constant, the second pass moves "
          "exactly two ships and they are the two it was written for.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
