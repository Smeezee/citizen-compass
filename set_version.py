#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
set_version.py - ONE source of truth for the site's version number.

I4 of docs/ORDER_the-public-site-needs-no-server-and-live-gets-a-deploy-script-2026-08-21.md.

THE DEFECT IS NOT A STALE STRING. IT IS THAT THERE WAS MORE THAN ONE.
=====================================================================
The version was written by hand in four rendered places - the <title> and the
header of static/preview.html, and the same two in releases/latest.html - plus
a comment in testing/_src/_layer.src.html that had gone stale at v0.3.9 while
everything else said v0.4.0. Today that comment was only a comment. The
mechanism is not: this project has ALREADY shipped a release whose source said
one number and whose feed said another, and nothing noticed, because there was
nothing that could.

So the number lives in ONE file - VERSION, at the repo root - and this script
is the ONLY thing that writes it anywhere else (rule 14). Nobody types a
version into an HTML file again.

    python set_version.py                 report where it is and whether they agree
    python set_version.py --check         non-zero if ANY location disagrees
    python set_version.py --set 0.4.1     write the new number everywhere

--check RUNS IN THE BUILD, and fails it closed. A page whose version disagrees
with VERSION never gets built, so the disagreement is caught before anything
can ship rather than by somebody noticing the header looks wrong.

WHAT IS DELIBERATELY NOT TOUCHED
================================
`releases/citizen-compass-v0.3.*.html` are ARCHIVED RELEASES. Their version
strings are correct history and rewriting them would be falsifying the record.
They are excluded by name, not by luck: the locations below are an explicit
list, and a location that matches nothing is a hard failure rather than a
silent skip - because a substitution that quietly matches nothing is exactly
the check that cannot fail.

testing/_deploy/index.html is NOT in the list either, and must not be: it is
BUILT from releases/latest.html, so writing to it would create a second writer
for a generated file. The build's own stamp step already requires the version
markup to be present, and refuses when it is not.

Rule 15: every open states its encoding.
"""

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
VERSION_FILE = os.path.join(HERE, "VERSION")

# Every rendered occurrence of the site's version, named explicitly.
#
#   (path, label, compiled pattern with the version as group 1)
#
# The pattern must capture ONLY the digits, so the surrounding markup is never
# rewritten - a substitution that can reshape the markup is a substitution that
# can break the build's stamp step, which keys on that same markup.
LOCATIONS = [
    ("static/preview.html", "title",
     re.compile(r"(?<=<title>Citizen Compass v)(\d+\.\d+\.\d+)(?=</title>)")),
    ("static/preview.html", "header",
     re.compile(r'(?<=<span class="version">v)(\d+\.\d+\.\d+)(?=</span>)')),
    ("releases/latest.html", "title",
     re.compile(r"(?<=<title>Citizen Compass v)(\d+\.\d+\.\d+)(?=</title>)")),
    ("releases/latest.html", "header",
     re.compile(r'(?<=<span class="version">v)(\d+\.\d+\.\d+)(?=</span>)')),
]

VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


def read_version():
    """The one number. Never inferred from a page - that is the wrong way round."""
    if not os.path.exists(VERSION_FILE):
        sys.exit("NO VERSION FILE at %s. This is the single source of truth "
                 "and nothing may guess it." % VERSION_FILE)
    with open(VERSION_FILE, "r", encoding="utf-8") as fh:
        raw = fh.read().strip()
    if not VERSION_RE.match(raw):
        sys.exit("VERSION does not hold a version: %r. Expected N.N.N." % raw)
    return raw


def scan():
    """What each declared location currently says.

    Returns (rows, problems). A location that matches NOTHING is a problem, not
    an absence: it means the markup moved and this script has quietly stopped
    covering it, which is the failure mode the whole file exists to close.
    """
    rows, problems = [], []
    for rel, label, pattern in LOCATIONS:
        path = os.path.join(HERE, rel)
        if not os.path.exists(path):
            problems.append("%s (%s): FILE MISSING" % (rel, label))
            rows.append((rel, label, None, 0))
            continue
        with open(path, "r", encoding="utf-8", newline="") as fh:
            text = fh.read()
        found = pattern.findall(text)
        if not found:
            problems.append(
                "%s (%s): the version markup this script targets is NOT "
                "PRESENT. The page moved and this location has stopped being "
                "covered - reported rather than skipped." % (rel, label))
            rows.append((rel, label, None, 0))
            continue
        if len(set(found)) > 1:
            problems.append("%s (%s): disagrees with itself: %s"
                            % (rel, label, ", ".join(sorted(set(found)))))
        rows.append((rel, label, found[0], len(found)))
    return rows, problems


def main():
    ap = argparse.ArgumentParser(
        description="One source of truth for the site's version number.")
    ap.add_argument("--check", action="store_true",
                    help="non-zero if any location disagrees with VERSION.")
    ap.add_argument("--set", dest="new",
                    help="write this version to VERSION and everywhere it is "
                         "rendered.")
    args = ap.parse_args()

    if args.new:
        if not VERSION_RE.match(args.new):
            sys.exit("NOT A VERSION: %r. Expected N.N.N." % args.new)
        with open(VERSION_FILE, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(args.new + "\n")
        print("VERSION -> %s" % args.new)

    version = read_version()
    rows, problems = scan()

    if args.new:
        # Written AFTER the scan above, so a location whose markup has moved is
        # reported before anything is rewritten rather than silently skipped.
        if any(p.endswith("stopped being covered - reported rather than "
                          "skipped.") or "FILE MISSING" in p for p in problems):
            sys.exit("REFUSING TO WRITE - a declared location could not be "
                     "found:\n  " + "\n  ".join(problems))
        for rel, label, pattern in LOCATIONS:
            path = os.path.join(HERE, rel)
            with open(path, "r", encoding="utf-8", newline="") as fh:
                text = fh.read()
            new_text, n = pattern.subn(version, text)
            if n == 0:
                sys.exit("REFUSING: %s (%s) matched nothing on the write pass "
                         "even though it matched on the scan. Nothing further "
                         "written." % (rel, label))
            if new_text != text:
                with open(path, "w", encoding="utf-8", newline="") as fh:
                    fh.write(new_text)
                print("  wrote %-24s %-7s (%d occurrence%s)"
                      % (rel, label, n, "" if n == 1 else "s"))
            else:
                print("  ok    %-24s %-7s already %s" % (rel, label, version))
        rows, problems = scan()

    print("VERSION = %s" % version)
    disagree = []
    for rel, label, found, count in rows:
        state = "MISSING" if found is None else (
            "ok" if found == version else "DISAGREES (%s)" % found)
        if found is not None and found != version:
            disagree.append("%s (%s) says %s, VERSION says %s"
                            % (rel, label, found, version))
        print("  %-24s %-7s %-4s %s"
              % (rel, label, "" if found is None else "x%d" % count, state))

    problems = problems + disagree
    if args.check:
        if problems:
            print("")
            sys.exit("VERSION MISMATCH - the site's version is written in more "
                     "than one place and they do not agree:\n  "
                     + "\n  ".join(problems))
        print("every rendered occurrence agrees with VERSION")
        return 0

    if problems:
        print("")
        print("PROBLEMS:")
        for p in problems:
            print("  " + p)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
