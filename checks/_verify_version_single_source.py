#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_verify_version_single_source.py - the version is written in exactly one place.

I4's control, in its own words: "change the version in the one place, rebuild,
confirm every rendered occurrence changed. A grep that finds the old number
anywhere fails the check."

So that is what this does. It sets VERSION to a probe number that appears
nowhere in this project, runs set_version.py --set, REBUILDS THE DEPLOY PAYLOAD
FOR REAL, and then greps the built pages for the old number. Not a simulation
of a release - the actual build, producing the actual artifact.

WHY THE GREP IS THE ASSERTION AND NOT THE SUBSTITUTION COUNT
============================================================
Counting substitutions proves only that the places this script knows about were
rewritten. The defect being guarded against is a place nobody knew about - a
number typed into a fifth file, a comment quoting it, a page nobody remembered
was built from a different source. Only a grep over the built output can find
one of those, so the grep is what decides.

IT MUTATES THE REPO, AND IT PUTS IT BACK
=========================================
VERSION, static/preview.html and releases/latest.html are snapshotted BYTE FOR
BYTE before anything is touched and rewritten from those snapshots in a finally
block. The restoration is then VERIFIED - the bytes are compared - and a failed
restore is reported as a loud failure naming the files, never as a pass. If you
ever see that message, the repo is mid-surgery and needs looking at.

The payload is rebuilt one last time from the restored sources, so _deploy is
left holding the TESTING payload exactly as it was found.

STATED LIMIT: this needs the database and node, because the build does. If the
build cannot run, this reports NOT PERFORMED and exits non-zero. It never
reports a pass it did not earn.

`--self-test` inverts every expectation and must exit 1.

Rule 15: every open states its encoding.
"""

import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SELFTEST = "--self-test" in sys.argv

# A number that appears nowhere in this project, so a stray match is a real
# match rather than a coincidence with a library version or a patch number.
PROBE = "77.88.99"

# The pages the build produces. index.html is the only one that renders a
# version today - the others are checked anyway, because "no other page shows
# the version" is a fact worth having a check for rather than an assumption.
BUILT_PAGES = ["index.html", "find.html", "keybinds.html", "loadout.html",
               "holo.html", "download.html", "stick-test.html"]

SNAPSHOT_FILES = ["VERSION", "static/preview.html", "releases/latest.html"]

_passed = []
_failed = []


def check(label, got, want=True):
    expected = (not want) if SELFTEST else want
    ok = bool(got) == bool(expected)
    (_passed if ok else _failed).append(label)
    print("  %s  %s" % ("PASS" if ok else "FAIL", label))
    return ok


def read(rel):
    with open(os.path.join(ROOT, rel), "r", encoding="utf-8", newline="") as fh:
        return fh.read()


def write(rel, text):
    with open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def run(args, what):
    proc = subprocess.run(args, capture_output=True, text=True, cwd=ROOT)
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        print("     %s exited %d:" % (what, proc.returncode))
        for line in out.strip().splitlines()[-12:]:
            print("       " + line)
    return proc.returncode, out


def built(page):
    path = os.path.join(ROOT, "testing", "_deploy", page)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8", newline="") as fh:
        return fh.read()


def main():
    py = sys.executable
    setver = os.path.join(ROOT, "set_version.py")
    build = os.path.join(ROOT, "testing", "_src", "build_deploy.py")

    if not os.path.exists(setver):
        print("NOT PERFORMED: set_version.py is missing. Reported as not "
              "performed, never as passed.")
        return 1

    print("\n1. THE ONE PLACE EXISTS, AND IT IS THE ONLY PLACE ANYONE TYPES")
    original = {rel: read(rel) for rel in SNAPSHOT_FILES}
    start_version = original["VERSION"].strip()
    check("VERSION holds a version (%s)" % start_version,
          re.match(r"^\d+\.\d+\.\d+$", start_version))
    code, out = run([py, setver, "--check"], "set_version.py --check")
    check("every rendered occurrence already agrees with VERSION", code == 0)
    check("and the check names each location it looked at rather than just "
          "saying ok",
          "static/preview.html" in out and "releases/latest.html" in out)

    # The build must be runnable, or nothing below means anything.
    print("\n2. THE BUILD RUNS AND THE PAYLOAD CARRIES THE CURRENT VERSION")
    code, out = run([py, build], "build_deploy.py")
    if code != 0:
        print("NOT PERFORMED: the build failed, so the rebuild half of this "
              "control could not run. This needs PostgreSQL and node, and it "
              "is reported as not performed rather than as passed.")
        return 1
    index = built("index.html")
    check("the built index.html renders the current version",
          index is not None and ("v" + start_version) in index)

    ok_restore = True
    try:
        # ---------------------------------------------------------------
        print("\n3. CHANGE IT IN THE ONE PLACE, AND REBUILD")
        code, out = run([py, setver, "--set", PROBE], "set_version.py --set")
        check("set_version.py accepts the new number", code == 0)
        check("and reports which files it wrote", "wrote" in out or "ok " in out)
        check("VERSION now holds it", read("VERSION").strip() == PROBE)

        code, out = run([py, build], "build_deploy.py after the version change")
        check("the build succeeds with the new version", code == 0)

        # ---------------------------------------------------------------
        print("\n4. THE GREP - EVERY RENDERED OCCURRENCE CHANGED")
        stale = []
        moved = []
        for page in BUILT_PAGES:
            text = built(page)
            if text is None:
                continue
            if ("v" + start_version) in text:
                stale.append(page)
            if ("v" + PROBE) in text:
                moved.append(page)
        check("NO built page still carries the old number anywhere"
              + (" (found in %s)" % ", ".join(stale) if stale else ""),
              not stale)
        check("and the new number is rendered (%s)" % ", ".join(moved) or "none",
              bool(moved))

        # The source files too - a build reads them, so an old number left in
        # one is an old number that comes back on the next build.
        src_stale = [rel for rel in ("static/preview.html", "releases/latest.html")
                     if ("v" + start_version) in read(rel)]
        check("neither page SOURCE still carries the old number"
              + (" (found in %s)" % ", ".join(src_stale) if src_stale else ""),
              not src_stale)

        # ---------------------------------------------------------------
        print("\n5. AND THE GATE FIRES WHEN THEY DISAGREE")
        # A hand-edit to one page, of exactly the kind this whole item exists
        # to make impossible. The build must refuse.
        tampered = read("releases/latest.html").replace(
            "<title>Citizen Compass v" + PROBE + "</title>",
            "<title>Citizen Compass v1.2.3</title>", 1)
        check("the tamper actually changed the file - otherwise the assertion "
              "below is checking nothing",
              tampered != read("releases/latest.html"))
        write("releases/latest.html", tampered)
        code, out = run([py, setver, "--check"], "set_version.py --check (tampered)")
        check("set_version.py --check catches a page that disagrees", code != 0)
        check("and names the file and both numbers",
              "releases/latest.html" in out and "1.2.3" in out and PROBE in out)
        code, out = run([py, build], "build_deploy.py (tampered)")
        check("and the BUILD refuses rather than shipping it", code != 0)
        check("and says what to do about it, in one place",
              "set_version.py --set" in out)
    finally:
        # ---------------------------------------------------------------
        print("\n6. PUTTING THE REPO BACK")
        for rel, text in original.items():
            write(rel, text)
        for rel, text in original.items():
            if read(rel) != text:
                ok_restore = False
                print("  RESTORE FAILED: %s does not match its snapshot" % rel)
        if ok_restore:
            print("  restored: %s" % ", ".join(SNAPSHOT_FILES))
        code, _ = run([py, build], "build_deploy.py (restoring the payload)")
        if code != 0:
            ok_restore = False
            print("  RESTORE FAILED: the payload could not be rebuilt from the "
                  "restored sources. testing/_deploy is left holding a payload "
                  "built from a PROBE version.")

    check("the repo was put back exactly as it was found", ok_restore)
    check("and VERSION is the number this control started with",
          read("VERSION").strip() == start_version)
    check("and the rebuilt payload carries it again",
          (built("index.html") or "").count("v" + start_version) > 0)
    check("and carries no trace of the probe number",
          "v" + PROBE not in (built("index.html") or ""))

    print("\n%d passed, %d failed" % (len(_passed), len(_failed)))
    if _failed:
        print("FAILED:")
        for f in _failed:
            print("  " + f)
    if SELFTEST:
        print("\n--self-test: expectations were inverted, so a non-zero exit "
              "is the correct outcome.")
    return 1 if _failed else 0


if __name__ == "__main__":
    sys.exit(main())
