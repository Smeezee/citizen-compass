#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""takedown.py - remove every CIG-sourced asset from the built site.

    venv\\Scripts\\python.exe scripts\\takedown.py --yes

A4. THE OFF SWITCH.

Sleven's commitment was "if they have a problem, then we take it down". A
promise you cannot execute in ten minutes is not a promise. This is the ten
minutes.

WHAT IT DOES, in order:

 1. Reads the register (data-layer/cig_assets.json) for every asset whose
    `source` is a CIG source. THE TAG IS A FIELD ON A RECORD, not a filename
    convention and not a folder, because folders get reorganised and a
    `models/cig/` directory survives exactly until the first person who tidies
    up.
 2. MOVES each one out of the built site into _to_delete/takedown_<stamp>/.
    Moved, not deleted - hard rule 1, and it also means a takedown made in a
    panic is recoverable if it turns out to have been wider than intended.
 3. Stamps `removed` on each record. THIS IS WHAT MAKES THE REMOVAL DURABLE.
    The file being absent is not enough: the next build, or the next model
    sync, would put it straight back. The stamp is what the build reads.
 4. Rebuilds the site, so what is published no longer references what was
    pulled. A page whose model was withdrawn says the model was removed at the
    rights holder's request - it does not show a broken canvas and it does not
    silently render an empty box.

WHAT IT DOES NOT DO: deploy. The rebuild is local. Uploading is a separate,
deliberate act - see docs/TAKEDOWN.md, which names it as step 2.

--dry-run prints exactly what would move and changes NOTHING. The dry run is
proven by behaviour rather than by reading this sentence: the control in
checks/_verify_takedown.py runs it and then asserts from the outside that every
file is still in place and the register is byte-identical.

Rule 15: every open states its encoding.
"""

import argparse
import datetime
import io
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import cig_assets  # noqa: E402

DEPLOY = os.path.join(REPO, "testing", "_deploy")
BUILD = os.path.join(REPO, "testing", "_src", "build_deploy.py")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Remove every CIG-sourced asset from the built site.")
    ap.add_argument("--dry-run", action="store_true",
                    help="print what would be removed and change nothing")
    ap.add_argument("--yes", action="store_true",
                    help="required for a real run, so it cannot happen by "
                         "accident")
    ap.add_argument("--deploy-dir", default=DEPLOY)
    ap.add_argument("--register", default=None,
                    help="override the register (used by the control)")
    ap.add_argument("--no-build", action="store_true",
                    help="skip the rebuild (used by the control)")
    args = ap.parse_args(argv)

    reg = args.register or cig_assets.register_path()
    assets = cig_assets.tagged(reg)
    keep = cig_assets.untagged(reg)

    print("register        : %s" % reg)
    print("CIG-sourced     : %d asset(s)" % len(assets))
    print("NOT CIG-sourced : %d asset(s) - these are NOT touched" % len(keep))

    if not assets:
        print("\nNothing is tagged as CIG-sourced, so there is nothing to "
              "remove.\nThis is a real result, not a failure: the register is "
              "the record, and it is empty.")
        return 0

    if not args.dry_run and not args.yes:
        print("\nRefusing to run without --yes. Add it when you mean it, or "
              "use --dry-run.")
        return 2

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    attic = os.path.join(REPO, "_to_delete", "takedown_%s" % stamp)

    moved, absent = [], []
    for a in assets:
        for f in cig_assets.deploy_paths(a, args.deploy_dir):
            rel = os.path.relpath(f, args.deploy_dir)
            if not os.path.exists(f):
                absent.append(rel)
                continue
            if args.dry_run:
                moved.append(rel)
                continue
            dest = os.path.join(attic, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.move(f, dest)
            moved.append(rel)

    verb = "WOULD MOVE" if args.dry_run else "MOVED"
    print("\n%s %d file(s) out of the built site:" % (verb, len(moved)))
    for m in moved:
        print("    %s" % m)
    if absent:
        print("\n%d registered file(s) were already not in the build - "
              "reported, not hidden:" % len(absent))
        for m in absent:
            print("    %s" % m)

    if args.dry_run:
        print("\nDRY RUN - nothing was moved, nothing was stamped, nothing was "
              "rebuilt.")
        return 0

    print("\nmoved to: %s" % attic)
    print("(moved, not deleted - hard rule 1, and a panic takedown stays "
          "recoverable)")

    today = datetime.date.today().isoformat()
    stamped = 0
    for a in assets:
        if cig_assets.mark_removed(a["file"], a["kind"], today, reg):
            stamped += 1
    print("\nstamped `removed: %s` on %d record(s) - this is what makes the "
          "removal survive the next build" % (today, stamped))

    if args.no_build:
        print("\n--no-build: the site was NOT rebuilt.")
        return 0

    print("\nrebuilding the site so nothing published still points at what was "
          "pulled...")
    env = dict(os.environ)
    if args.register:
        env["CC_CIG_REGISTER"] = args.register
    r = subprocess.run([sys.executable, BUILD],
                       cwd=os.path.join(REPO, "testing", "_src"),
                       env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    sys.stdout.write(r.stdout)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        print("\nTHE REBUILD FAILED. The assets ARE removed from the built "
              "site and the register IS stamped - that part is done and is "
              "what matters most. But the site was not rebuilt, so DO NOT "
              "DEPLOY until this is resolved.")
        return 1

    print("\nDONE. Removed from the built site and rebuilt.")
    print("The site still works: any page whose model was pulled now says it "
          "was removed at the rights holder's request.")
    print("\nNEXT, AND IT IS A SEPARATE DELIBERATE STEP - the removal is only "
          "local until you deploy:")
    print("    powershell -File scripts\\deploy_testing.ps1")
    return 0


if __name__ == "__main__":
    sys.exit(main())
