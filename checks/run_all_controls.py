#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_all_controls.py - run every control in checks/, back to back, and report.

H9 of the 2026-08-20 order: "Re-run every control in checks/. H7 changes
behaviour at the engine that every session-opening check inherits."

WHY THIS EXISTS AS A FILE RATHER THAN A COMMAND SOMEBODY TYPES
==============================================================
The G9 sweep was 31 controls run by hand, one at a time, and the list of which
ones exist lived in the ledger entry afterwards. That is a list nobody can
re-derive: a control added next week is not in it, and a sweep that silently
skipped one would look exactly like a sweep that ran it.

So the list is DISCOVERED, not typed. Every checks/_verify_*.py and
checks/_verify_*.mjs is found on disk and run. A new control is swept the day
it lands, with nobody having remembered anything.

FAIL CLOSED. A control that cannot be run - missing interpreter, import error,
crash before its first assertion - is reported as NOT RUN and counted against
the sweep. It is never reported as passed. "We could not look" and "we looked
and it was fine" are different answers and this project does not let them
collapse into one.

--self-test runs every control that supports --self-test in its inverted mode
and requires each to exit NON-ZERO, which is what proves the sweep is capable
of reporting a failure at all.

Rule 15: every open states its encoding.

Usage:
  python checks/run_all_controls.py
  python checks/run_all_controls.py --self-test
  python checks/run_all_controls.py --only find,preservation
"""

import argparse
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Controls whose --self-test uses the OTHER convention: they plant specific
# harness defects and exit 0 when they CATCH all of them, rather than inverting
# every assertion and exiting 1.
#
# That is arguably the better design - it names the failure modes instead of
# flipping every boolean - and it was already noted in the G9 sweep. So it is
# recorded here as a convention rather than reported as a failure every time.
#
# BUT NOT TAKEN ON TRUST. A zero exit is only accepted when the output actually
# shows the planted defects being caught. Otherwise "exit 0" would excuse a
# harness whose self-test had stopped doing anything at all, which is the exact
# thing a self-test exists to rule out.
SELF_TEST_ZERO_MEANS_CAUGHT = {
    "_verify_shop_schema_db.py": [
        "SELF-TEST PASSED",
        "a refusal case the database will happily ACCEPT",
        "a refusal case rejected by the WRONG constraint",
        "an acceptance case the database REJECTS",
    ],
}

# Controls that need something this sweep cannot provide on its own. Named
# with the reason, so "skipped" is never mistaken for "passed".
NEEDS = {
    "_verify_find_deployed.mjs":
        "fetches the DEPLOYED origin - it is a statement about the live site, "
        "not about this working tree",
    "_verify_deployed_links.mjs":
        "sweeps the DEPLOYED origin for dead links - same reason, and it makes "
        "~450 network requests, so it is opt-in rather than part of every run",
}


def discover():
    out = []
    for name in sorted(os.listdir(HERE)):
        if not name.startswith("_verify_"):
            continue
        if name.endswith(".py") or name.endswith(".mjs"):
            out.append(name)
    return out


def command_for(name, self_test):
    path = os.path.join(HERE, name)
    if name.endswith(".mjs"):
        node = shutil.which("node")
        if node is None:
            return None, "node is not on PATH"
        cmd = [node, path]
    else:
        cmd = [sys.executable, path]
    if self_test:
        cmd.append("--self-test")
    return cmd, None


def supports_self_test(name):
    with open(os.path.join(HERE, name), "r", encoding="utf-8",
              errors="replace") as fh:
        return "--self-test" in fh.read()


def main():
    ap = argparse.ArgumentParser(description="Run every control in checks/.")
    ap.add_argument("--self-test", action="store_true",
                    help="run each control's inverted mode and require a "
                         "non-zero exit from every one of them.")
    ap.add_argument("--only", default="",
                    help="comma-separated substrings; run only matching "
                         "controls.")
    ap.add_argument("--timeout", type=float, default=900.0)
    ap.add_argument("--include-deployed", action="store_true",
                    help="also run controls that need the deployed site.")
    args = ap.parse_args()

    wanted = [w.strip() for w in args.only.split(",") if w.strip()]
    controls = discover()
    if wanted:
        controls = [c for c in controls if any(w in c for w in wanted)]

    passed, failed, skipped, not_run = [], [], [], []
    started = time.time()

    print("sweep: %d control(s) discovered in checks/%s"
          % (len(controls), "  [--self-test: every one must FAIL]"
             if args.self_test else ""))
    print("")

    for name in controls:
        if name in NEEDS and not args.include_deployed:
            skipped.append((name, NEEDS[name]))
            print("  SKIP  %-42s %s" % (name, NEEDS[name]))
            continue
        if args.self_test and not supports_self_test(name):
            skipped.append((name, "no --self-test mode"))
            print("  SKIP  %-42s no --self-test mode" % name)
            continue

        cmd, why = command_for(name, args.self_test)
        if cmd is None:
            not_run.append((name, why))
            print("  NOTRUN %-41s %s" % (name, why))
            continue

        t0 = time.time()
        try:
            proc = subprocess.run(cmd, cwd=ROOT, capture_output=True,
                                  text=True, timeout=args.timeout)
            code = proc.returncode
            tail = (proc.stdout or "").strip().splitlines()[-1:] or [""]
        except subprocess.TimeoutExpired:
            not_run.append((name, "timed out after %.0fs" % args.timeout))
            print("  NOTRUN %-41s timed out after %.0fs"
                  % (name, args.timeout))
            continue
        except Exception as exc:                 # pragma: no cover - reported
            not_run.append((name, "%s: %s" % (type(exc).__name__, exc)))
            print("  NOTRUN %-41s %s: %s" % (name, type(exc).__name__, exc))
            continue

        secs = time.time() - t0
        combined = (proc.stdout or "") + (proc.stderr or "")
        if args.self_test and name in SELF_TEST_ZERO_MEANS_CAUGHT:
            markers = SELF_TEST_ZERO_MEANS_CAUGHT[name]
            missing = [m for m in markers if m not in combined]
            ok = code == 0 and not missing
            if not ok and missing:
                print("        (expected markers not found: %s)"
                      % "; ".join(missing))
        else:
            ok = (code != 0) if args.self_test else (code == 0)
        if ok:
            passed.append(name)
            print("  ok    %-42s exit %d  %5.1fs  %s"
                  % (name, code, secs, tail[0][:60]))
        else:
            failed.append((name, code, combined[-4000:]))
            print("  FAIL  %-42s exit %d  %5.1fs" % (name, code, secs))

    print("")
    print("=" * 70)
    print("%d ok, %d failed, %d skipped, %d NOT RUN, in %.0fs"
          % (len(passed), len(failed), len(skipped), len(not_run),
             time.time() - started))
    if args.self_test:
        print("(--self-test: 'ok' means the control exited non-zero with its "
              "expectations inverted, which is the correct outcome.)")
    for name, code, out in failed:
        print("\n--- %s (exit %d) ---" % (name, code))
        print(out.strip()[-1200:])
    for name, why in not_run:
        print("NOT RUN: %s - %s" % (name, why))

    # A SWEEP THAT SWEPT NOTHING IS NOT A CLEAN SWEEP.
    #
    # Without this, a discover() that returned an empty list - a renamed
    # directory, a changed prefix, a --only typo - prints "0 ok, 0 failed" and
    # exits 0. That is the shape of every silent success in this project's
    # history: a glob that matched nothing, a main() that returned None, a gate
    # that returned 0 unconditionally. The sweep must be able to say "I did not
    # look" and it must not say it quietly.
    if not passed and not failed:
        print("")
        print("NOTHING WAS SWEPT. %d control(s) matched and none of them ran."
              % len(controls))
        print("This is reported as a FAILED sweep, never as a clean one.")
        return 1

    # A control that could not be run counts against the sweep. Reporting a
    # green sweep with something unrun is the exact failure this project calls
    # SILENT SUCCESS.
    return 1 if (failed or not_run) else 0


if __name__ == "__main__":
    sys.exit(main())
