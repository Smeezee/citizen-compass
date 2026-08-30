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

# RULE 15'S OTHER HALF - AND THIS SWEEP NEEDED BOTH.
#
# Reading the child's output with the platform default was one fault; WRITING
# it back out is the other, and fixing only the first moved the crash rather
# than removing it:
#
#   run_all_controls.py line 217, print(out.strip()[-1200:])
#   UnicodeEncodeError: 'charmap' codec can't encode character 'ā'
#
# That is the a-macron in San'tok.yai, which CLAUDE.md names as "a shipping
# product, not an edge case". A sweep that cannot print a ship's name cannot
# report on the ship.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

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
    "_verify_picker_deployed.mjs":
        "drives the DEPLOYED ship page - B8's acceptance, and a statement "
        "about the served site rather than about this working tree. It also "
        "clicks all 1,200 hull markers over the wire",
}


import sweep_gate  # noqa: E402  (same directory)

REPO = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))


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
            # RULE 15, ONE PROCESS REMOVED - AND IT STOPPED THE SWEEP DEAD.
            #
            # `text=True` with no encoding decodes the child's output with the
            # platform default, which on Windows is cp1252. The controls print
            # SHIP NAMES: San'tok.yai carries a macron, the Yeng'tu and the
            # "Shredder" carry curly quotes. On 2026-08-27 this killed
            # subprocess's reader thread with a UnicodeDecodeError and the sweep
            # stopped after 14 of 96 controls:
            #
            #   Exception in thread Thread-11 (_readerthread)
            #   ... cp1252.py ... charmap_decode
            #
            # It failed loudly rather than silently, which is the safe
            # direction - but it means the full suite could not be run at all.
            proc = subprocess.run(cmd, cwd=ROOT, capture_output=True,
                                  text=True, encoding="utf-8",
                                  errors="replace", timeout=args.timeout)
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

        # EXIT 2 MEANS "I COULD NOT LOOK", WHICH IS NEITHER A PASS NOR A FAIL.
        #
        # Until 2026-08-29 this classifier had two outcomes - zero or FAIL - and
        # NOT RUN was reachable only when the runner could not launch the
        # process at all. A control that STARTS, finds its resource absent and
        # says so had no exit code that meant what it was saying, so it printed
        # as a defect.
        #
        # Two controls were already trying: _verify_community_mark.py exits 2
        # with "NOT PERFORMED ... never as a pass", and _verify_panel_dismiss.mjs
        # exits 2 when Chromium is missing. C1 found it by running the suite on
        # a Linux VM with no PostgreSQL, no Chromium and no PowerShell: twelve
        # DB controls, nine browser controls and deploy_guards all reported FAIL
        # with nothing broken. Read that cold and you go hunting twenty defects
        # that do not exist.
        #
        # NOTHING HERE IS MADE TO PASS. not_run already counts against the
        # sweep (see the return at the end), goes into the receipt, and
        # sweep_gate refuses on it in as many words: "a control that could not
        # be run is counted against the sweep, never as a pass." The only thing
        # that changes is which true sentence gets printed.
        #
        # AND IT APPLIES UNDER --self-test TOO, which is the half that would
        # have bitten. There, ok = (code != 0), so a control that could not look
        # would have been counted as having CAUGHT the planted defect. That is
        # the silent success this suite exists against, wearing the colours of
        # the test that is supposed to find it.
        if code == 2:
            why = next((l.strip() for l in combined.splitlines()
                        if "NOT PERFORMED" in l),
                       (tail[0] or "exit 2 with no reason given").strip())
            not_run.append((name, why))
            print("  NOTRUN %-41s exit 2  %5.1fs  %s"
                  % (name, secs, why[:60]))
            continue

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

    # Q10: THE RECEIPT. Written here because this is the sweep, and the sweep is
    # the only thing that knows what it saw.
    #
    # It records the failures AND the reasons a sweep would not count as clean -
    # partial, self-test - rather than deciding. Deciding is sweep_gate.py's job,
    # so the rule can change without every sweep needing to be re-run.
    #
    # A receipt that cannot be written is REPORTED and does not silently make the
    # sweep look unreceipted-but-fine. It also does not fail an otherwise good
    # sweep: the deploy gate refuses on a missing receipt anyway, which is the
    # safe direction.
    try:
        rec = sweep_gate.write_receipt(
            os.path.join(REPO, "testing", "_deploy"),
            passed=passed,
            failed=[n for n, _c, _o in failed],
            skipped=[n for n, _w in skipped],
            not_run=[n for n, _w in not_run],
            # WHICH FAILURES ARE ABOUT THE LIVE SITE RATHER THAN THIS PAYLOAD.
            # The three NEEDS controls answer a different question, and one of
            # them - "the served page is byte-identical to the one just built" -
            # CANNOT be green before the deploy that makes it so. Recorded here
            # so sweep_gate can report them without deadlocking the deploy that
            # is their own remedy.
            deployed_only=[n for n in NEEDS
                           if n in [x for x, _c, _o in failed]
                           or n in [x for x, _w in not_run]],
            partial=bool(wanted),
            self_test=bool(args.self_test),
            seconds=time.time() - started)
        print("")
        # NAMES THE PATH IT ACTUALLY WROTE. It used to print sweep_gate.RECEIPT
        # unconditionally, so a --only run announced the full receipt's path
        # while writing over it - the message and the act disagreeing is how
        # the Q30 clobber stayed invisible for a day.
        _rpath = sweep_gate.receipt_path(bool(wanted), bool(args.self_test))
        print("sweep receipt: %s  (%d passed, %d failed, payload %s)"
              % (os.path.relpath(_rpath, REPO), rec["passed"],
                 len(rec["failed"]), rec["fingerprint"][:16]))
        if _rpath != sweep_gate.RECEIPT:
            print("               this was a %s run, so it did NOT touch %s"
                  % ("--self-test" if args.self_test else "--only",
                     os.path.relpath(sweep_gate.RECEIPT, REPO)))
    except Exception as exc:                     # pragma: no cover - reported
        print("")
        print("SWEEP RECEIPT NOT WRITTEN: %s: %s" % (type(exc).__name__, exc))
        print("The deploy gate refuses on a missing receipt, so this fails "
              "closed rather than quietly.")

    # A control that could not be run counts against the sweep. Reporting a
    # green sweep with something unrun is the exact failure this project calls
    # SILENT SUCCESS.
    return 1 if (failed or not_run) else 0


if __name__ == "__main__":
    sys.exit(main())
