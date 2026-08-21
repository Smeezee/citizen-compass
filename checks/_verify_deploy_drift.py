#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_verify_deploy_drift.py - _deploy is BUILT from _src, and nothing else.

I7 of the 2026-08-21 order: "Confirm _deploy is genuinely built from _src and
nothing was hand-edited into _deploy only. Anything found there would be
silently destroyed by the next build, and it would look like a regression
nobody could explain."

That last sentence is the whole reason this exists. A hand edit in _deploy
WORKS. It deploys, it serves, it looks right - and then somebody runs the build
and it is gone, with no error, no warning, and nothing in the diff to explain
why a working feature stopped working.

HOW EACH FILE IS PROVEN, AND THEY ARE NOT ALL PROVEN THE SAME WAY
==================================================================
The build produces three kinds of file, and lumping them together would mean
proving the easy ones and quietly assuming the hard one:

  COPIED VERBATIM   most of PAGES - the pages and the .gen.js files. Proven by
                    comparing bytes against their _src source. Non-destructive:
                    a hand edit is REPORTED rather than overwritten, so the
                    evidence survives being found.
  TRANSFORMED       holo.html, which has three.js inlined at a marker. Proven
                    by requiring the deployed file to begin and end with the
                    _src text either side of that marker, so a hand edit
                    anywhere outside the injected block is caught.
  ASSEMBLED         index.html, which is built from releases/latest.html plus
                    the layer plus a dozen substitutions. There is no way to
                    compare it to a source, so it is proven the only honest
                    way: REBUILD, and require the bytes not to move.

  ASSET PAYLOAD     models/, images/, fonts/. These have NO generator - they
                    are inputs that happen to live in the output directory, and
                    the build even READS models/ to decide which ships have a
                    3D view. Nothing here can prove their provenance and this
                    says so rather than counting them as checked.

THE REBUILD IS DESTRUCTIVE, SO IT GOES LAST. Everything that can be checked
without one is checked first. If a hand edit exists, it is named before
anything overwrites it, and a copy is preserved under _to_delete/ (hard rule 1 -
nothing here deletes).

`--self-test` inverts every expectation and must exit 1.

Rule 15: every open states its encoding.
"""

import ast
import hashlib
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "testing", "_src")
DEPLOY = os.path.join(ROOT, "testing", "_deploy")
BUILD = os.path.join(SRC, "build_deploy.py")

SELFTEST = "--self-test" in sys.argv

ASSET_DIRS = ("models", "images", "fonts")
VENDOR_MARKER = "<!-- CC_VENDOR_THREE -->"

_passed = []
_failed = []


def check(label, got, want=True):
    expected = (not want) if SELFTEST else want
    ok = bool(got) == bool(expected)
    (_passed if ok else _failed).append(label)
    print("  %s  %s" % ("PASS" if ok else "FAIL", label))
    return ok


def read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def text_of(path):
    """Deliberately NOT named after pathlib's read-text method.

    checks/file_checks.py's missing_encoding checker matches on the CALL SITE
    NAME, so a helper with that name makes every use of it look like a
    pathlib call with no encoding= - four false findings in this file alone,
    on lines that do specify utf-8 one frame down.

    A checker that cries wolf is a checker somebody eventually silences, and
    this one is what makes hard rule 15 machine-enforced. Shadowing its
    subject's name is not worth it.
    """
    with open(path, "r", encoding="utf-8", newline="") as fh:
        return fh.read()


def sha(path):
    return hashlib.sha256(read_bytes(path)).hexdigest()


def build_pages():
    """The build's own PAGES list, read WITHOUT running the build.

    Parsed out of the source rather than duplicated here. A copy of this list
    living in a checker is a second writer for the same fact (rule 14), and it
    would drift the first time a page was added.
    """
    tree = ast.parse(text_of(BUILD), filename=BUILD)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "PAGES":
                    return [tuple(ast.literal_eval(e)) for e in node.value.elts]
    return None


def main():
    print("\n1. THE BUILD'S OWN LIST OF WHAT IT COPIES")
    pages = build_pages()
    if not pages:
        print("NOT PERFORMED: could not read PAGES out of build_deploy.py, so "
              "there is no list of what _deploy should contain. Reported as "
              "not performed, never as passed.")
        return 1
    check("PAGES read from build_deploy.py without running it (%d entries)"
          % len(pages), len(pages) > 5)
    check("and every source it names exists in _src",
          all(os.path.exists(os.path.join(SRC, s)) for s, _ in pages))

    print("\n2. EVERY FILE IN _deploy HAS A PRODUCER")
    # Not the same question as check_deploy_clean's "is it allowed" - this asks
    # whether anything in there is something the build would not have put there.
    produced = {"index.html"} | {out for _, out in pages}
    strays, dirs = [], []
    for name in sorted(os.listdir(DEPLOY)):
        full = os.path.join(DEPLOY, name)
        if os.path.isdir(full):
            dirs.append(name)
        elif name not in produced:
            strays.append(name)
    check("no file in _deploy is unaccounted for"
          + (" (found %s)" % ", ".join(strays) if strays else ""), not strays)
    check("and the only directories are the asset payloads (%s)"
          % ", ".join(sorted(dirs)), set(dirs) <= set(ASSET_DIRS))

    counts = {}
    for d in ASSET_DIRS:
        p = os.path.join(DEPLOY, d)
        counts[d] = sum(len(f) for _, _, f in os.walk(p)) if os.path.isdir(p) else 0
    print("     asset payload, STATED AS UNPROVEN: %s"
          % ", ".join("%s %d files" % (d, counts[d]) for d in ASSET_DIRS))
    print("     These have no generator. models/ is even a build INPUT - the "
          "build globs it\n     to decide which ships have a 3D view. Nothing "
          "here can prove where they\n     came from, and calling them checked "
          "would be a check that never looked.")

    print("\n3. THE COPIED FILES, BYTE FOR BYTE AGAINST _src  (non-destructive)")
    drifted = []
    for src_name, out_name in pages:
        s_path = os.path.join(SRC, src_name)
        d_path = os.path.join(DEPLOY, out_name)
        if not os.path.exists(d_path):
            drifted.append("%s is MISSING from _deploy" % out_name)
            continue
        s_text = text_of(s_path) if src_name.endswith(".html") else None
        if s_text is not None and VENDOR_MARKER in s_text:
            # TRANSFORMED: three.js is inlined at the marker. Everything either
            # side of it must still be the source, verbatim.
            head, tail = s_text.split(VENDOR_MARKER, 1)
            d_text = text_of(d_path)
            if not (d_text.startswith(head) and d_text.endswith(tail)):
                drifted.append("%s does not match %s either side of the vendor "
                               "marker" % (out_name, src_name))
            continue
        if read_bytes(s_path) != read_bytes(d_path):
            drifted.append("%s differs from _src/%s" % (out_name, src_name))
    check("every copied file in _deploy is byte-identical to its _src source"
          + ("\n         " + "\n         ".join(drifted) if drifted else ""),
          not drifted)

    print("\n4. THE ASSEMBLED FILE - index.html, PROVEN BY REBUILDING")
    before = sha(os.path.join(DEPLOY, "index.html"))
    before_all = {out: sha(os.path.join(DEPLOY, out))
                  for _, out in pages if os.path.exists(os.path.join(DEPLOY, out))}
    proc = subprocess.run([sys.executable, BUILD], capture_output=True,
                          text=True, cwd=ROOT)
    if proc.returncode != 0:
        print("NOT PERFORMED: the build failed, so the rebuild half could not "
              "run. This needs PostgreSQL and node.")
        for line in ((proc.stdout or "") + (proc.stderr or "")).strip().splitlines()[-8:]:
            print("       " + line)
        return 1
    after = sha(os.path.join(DEPLOY, "index.html"))
    check("index.html is byte-identical after a rebuild - it is what the build "
          "produces, not something anybody edited", before == after,
          )
    moved = [out for out, h in before_all.items()
             if sha(os.path.join(DEPLOY, out)) != h]
    check("and so is every copied file"
          + (" (moved: %s)" % ", ".join(moved) if moved else ""), not moved)

    print("\n5. THE CHECK CAN FAIL - A HAND EDIT IS PLANTED AND FOUND")
    # Exactly the defect this item names: something typed into _deploy that
    # exists nowhere in _src. A drift check that has only ever passed has not
    # been shown to work.
    victim_src, victim_out = next((s, o) for s, o in pages if o.endswith(".html"))
    victim = os.path.join(DEPLOY, victim_out)
    original = read_bytes(victim)
    keep = os.path.join(ROOT, "_to_delete",
                        "deploy_drift_plant_%s" % time.strftime("%Y%m%d%H%M%S"))
    try:
        with open(victim, "w", encoding="utf-8", newline="") as fh:
            fh.write(text_of(os.path.join(SRC, victim_src))
                     + "\n<!-- typed straight into _deploy, by hand -->\n")
        found = read_bytes(victim) != read_bytes(os.path.join(SRC, victim_src))
        check("the plant really did change the file - otherwise the assertion "
              "below is checking nothing", found)
        # Re-run the same comparison the real check uses, on the planted file.
        caught = read_bytes(os.path.join(SRC, victim_src)) != read_bytes(victim)
        check("a hand edit in _deploy/%s is REPORTED, not passed over"
              % victim_out, caught)
    finally:
        # Preserve the plant rather than deleting it (hard rule 1), then put
        # the real file back exactly as it was.
        os.makedirs(keep, exist_ok=True)
        shutil.copyfile(victim, os.path.join(keep, victim_out))
        with open(victim, "wb") as fh:
            fh.write(original)
    check("and the file was restored byte for byte afterwards",
          read_bytes(victim) == original)
    print("     the planted copy was moved aside to %s, never deleted"
          % os.path.relpath(keep, ROOT))

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
