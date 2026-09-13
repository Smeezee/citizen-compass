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


# THE WORKING FIGURE. SIXTY MINUTES, AND IT IS A REPORT LINE, NOT A GATE.
#
# Sleven set it on 2026-09-08 by refusing to set a real one, and the reason is
# worth keeping next to the number: the sweep moved 79% in a day - 1,606s over
# 123 controls to 2,871s over 125 - and nobody noticed, because the receipt
# recorded a total and nothing else. Any ceiling picked before the composition
# was known would be "a guess wearing a decision's clothes". 3600 sits above the
# worst run we have with room to spare, FOR NO BETTER REASON THAN THAT, which is
# exactly why it is provisional and why it must never stop a deploy.
#
# WHY IT IS PRINTED BY THE PROGRAM RATHER THAN REMEMBERED BY A PERSON. The order
# says "cross it and say so". A human comparing 2,871 against 3,600 at the end of
# a 48-minute run is precisely the repeatable manual step rule 26 says to remove,
# and it is the step that already failed once - the 79% move was there to be seen
# and nobody saw it.
#
# ONLY A FULL SWEEP IS JUDGED. A --only run or a --self-test run is a subset by
# construction; comparing its runtime to a whole-suite figure would be comparing
# two different things, and the receipt keeps them apart for the same reason.
SWEEP_WORKING_FIGURE_SECONDS = 3600.0


def sweep_runtime_note(elapsed, full=True):
    """The report line, as a pure function so it can be tested without a sweep.

    Returns the line to print, or None when there is nothing to say. It never
    decides anything: the caller prints it and the exit code is untouched.
    """
    if not full:
        return None
    if elapsed <= SWEEP_WORKING_FIGURE_SECONDS:
        return None
    over = elapsed - SWEEP_WORKING_FIGURE_SECONDS
    return ("OVER THE WORKING FIGURE: %.0fs (%.1f min) against %.0fs (%.0f min), "
            "%.0fs over. REPORTED, NOT GATED - this does not stop a deploy and is "
            "not a failure. The figure is provisional and the receipt's per-control "
            "timings are what a real ceiling gets set from."
            % (elapsed, elapsed / 60.0, SWEEP_WORKING_FIGURE_SECONDS,
               SWEEP_WORKING_FIGURE_SECONDS / 60.0, over))


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


# ---------------------------------------------------------------------------
# ONE SWEEP AT A TIME, AND IT IS MATCHED ON WHAT A PROCESS EXECUTES.
#
# `checks/.last_sweep.json` is a SINGLE RECEIPT and it is what authorises a
# deploy: `sweep_gate.py` compares the fingerprint in it against the payload
# about to be uploaded. That protects against a STALE receipt. It does NOT
# protect against a SECOND SWEEP finishing later and replacing a good receipt
# with one taken against different bytes - after which the gate would happily
# pass a payload nothing had swept.
#
# That is rule 14, and the artifact is the one that says whether we may ship.
#
# THIS IS NOT HYPOTHETICAL. On 2026-09-04 two sweeps ran at once: one started
# from this repo's venv and one under the system python, seconds apart. The
# first symptom was a sweep that had been running an hour and fifty minutes
# where the usual run is fifteen. It was noticed by a human wondering why, not
# by anything here.
#
# NO LOCK FILE. A pid file goes stale the moment a sweep is killed - which is
# exactly what happened that day, twice - and then either refuses every future
# sweep or has to be overridden by hand, which teaches everyone to override it.
# Instead this asks the operating system which processes are running THIS FILE
# right now. Nothing to leave behind and nothing to clean up.
#
# Rule 14's own words: match on what a task EXECUTES rather than what it is
# called, so it cannot be evaded by invoking a different interpreter or copying
# the file to a different name.
#
# IF THE ENUMERATION ITSELF FAILS it says so LOUDLY and continues, because a
# sweep that cannot run at all is worse than two that might. It is never
# silent: "we could not look" and "we looked and it was clear" print
# differently, which is the distinction this whole suite exists to hold.
# ---------------------------------------------------------------------------
def _other_sweeps_running():
    """Return a list of (pid, cmdline) for OTHER live processes running this
    file, or None if the question could not be asked."""
    import os
    import subprocess
    me = os.getpid()
    # MY OWN ANCESTORS ARE NOT ANOTHER SWEEP, AND ON WINDOWS THERE ARE ALWAYS
    # SEVERAL. `venv\Scripts\python.exe` is a LAUNCHER: it spawns the real
    # interpreter as a child, so os.getpid() is the child and the venv process
    # is its parent. Every sweep therefore shows up as TWO python processes -
    # one under the venv path, one under the base install - plus the shell that
    # typed the command, whose command line also carries the file name.
    #
    # This is not a detail. On 2026-09-04 I read exactly that pair - same
    # second, one venv and one "system" - as two sessions sweeping at once, and
    # reported it as a collision. It was one sweep wearing two pids.
    mine = {me}
    try:
        import subprocess as _sp
        _q = ("Get-CimInstance Win32_Process | ForEach-Object "
              "{ \"$($_.ProcessId) $($_.ParentProcessId)\" }")
        _o = _sp.run(["powershell", "-NoProfile", "-Command", _q],
                     capture_output=True, text=True, timeout=30).stdout
        parent = {}
        for _l in _o.splitlines():
            _b = _l.split()
            if len(_b) == 2 and _b[0].isdigit() and _b[1].isdigit():
                parent[int(_b[0])] = int(_b[1])
        _p = me
        for _ in range(12):
            _p = parent.get(_p)
            if not _p or _p in mine:
                break
            mine.add(_p)
    except Exception:
        pass
    try:
        if os.name == "nt":
            # THE QUERY MUST NOT CONTAIN THE STRING IT IS LOOKING FOR.
            # The first version filtered inside PowerShell with
            # `-like '*run_all_controls*'`, so the powershell.exe running the
            # query carried the marker in its OWN command line and matched
            # itself - the guard refused every sweep including the first one.
            # Listing everything and filtering in Python keeps the marker out
            # of the query process entirely.
            ps = ("Get-CimInstance Win32_Process | ForEach-Object "
                  "{ \"$($_.ProcessId)`t$($_.CommandLine)\" }")
            out = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps],
                capture_output=True, text=True, timeout=30).stdout
        else:
            out = subprocess.run(["ps", "-eo", "pid=,args="],
                                 capture_output=True, text=True,
                                 timeout=30).stdout
    except Exception:
        return None
    found = []
    for line in out.splitlines():
        line = line.strip()
        if not line or "run_all_controls" not in line:
            continue
        head = line.replace("\t", " ").split(None, 1)
        if not head:
            continue
        try:
            pid = int(head[0])
        except ValueError:
            continue
        if pid in mine:
            continue
        found.append((pid, head[1] if len(head) > 1 else ""))
    return found


def _refuse_if_sweep_running(allow):
    import sys as _sys
    others = _other_sweeps_running()
    if others is None:
        print("SWEEP-LOCK NOT PERFORMED - could not ask the OS which processes "
              "are running.\n"
              "  Continuing, because a sweep that cannot run is worse than two "
              "that might.\n"
              "  This line is the whole of the warning: nothing else will "
              "mention it.")
        return
    if not others:
        return
    print("ANOTHER SWEEP IS ALREADY RUNNING - refusing to start a second one.")
    for pid, cmd in others:
        print("  pid %-8s %s" % (pid, cmd[:110]))
    print("")
    print("checks/.last_sweep.json is a single receipt and it is what")
    print("authorises a deploy. Two sweeps finishing minutes apart would each")
    print("overwrite it, and the surviving one would name whichever payload its")
    print("own run happened to see.")
    print("")
    print("Wait for it to finish, or if you are certain it is dead:")
    print("    python checks/run_all_controls.py --allow-concurrent")
    if not allow:
        _sys.exit(2)
    print("--allow-concurrent was passed. Proceeding anyway.")


# ---------------------------------------------------------------------------
# ONE CONTROL IS FOUR TIMES SLOWER THAN THE WHOLE REST OF THE SUITE.
#
# `_verify_broken_checker_end_to_end.py` was reported NOT RUN three times on
# 2026-09-06 and the first two were blamed on CPU contention. It was measured
# rather than blamed the third time:
#
#     alone, quiet machine, timed          687s
#     the global allowance                 900s
#     margin                               213s, 24%
#     next-slowest control in the suite    179s
#
# So it is not an occasional accident. The control genuinely runs for eleven
# and a half minutes - nearly 4x the next slowest thing here - and the 900s
# default was sized for a suite where nothing else comes close. Any co-tenant,
# including another session's work on the same machine, spends that 213s and
# the run is discarded after eleven minutes of real work.
#
# THIS DOES NOT WEAKEN THE GATE. A timeout catches a HUNG control, and 1800s
# still catches one; it only stops discarding a control that was going to
# finish. A timeout still produces NOT RUN, and NOT RUN still blocks the sweep
# and the deploy exactly as FAILED does (see the exit-code note above). The
# number is set from the measurement and the measurement is written beside it,
# rather than being raised until the red went away.
SLOW_CONTROLS = {
    "_verify_broken_checker_end_to_end.py": 1800.0,
}


def main():
    ap = argparse.ArgumentParser(description="Run every control in checks/.")
    ap.add_argument("--self-test", action="store_true",
                    help="run each control's inverted mode and require a "
                         "non-zero exit from every one of them.")
    ap.add_argument("--only", default="",
                    help="comma-separated substrings; run only matching "
                         "controls.")
    ap.add_argument("--timeout", type=float, default=900.0)
    ap.add_argument("--allow-concurrent", action="store_true",
                    help="start even if another sweep is running. "
                         "Only when you are certain the other is dead - "
                         "two sweeps race for checks/.last_sweep.json, "
                         "which is what authorises a deploy.")
    ap.add_argument("--include-deployed", action="store_true",
                    help="also run controls that need the deployed site.")
    args = ap.parse_args()
    _refuse_if_sweep_running(args.allow_concurrent)

    wanted = [w.strip() for w in args.only.split(",") if w.strip()]
    controls = discover()
    if wanted:
        controls = [c for c in controls if any(w in c for w in wanted)]

    passed, failed, skipped, not_run = [], [], [], []
    # PER-CONTROL SECONDS, CARRIED INTO THE RECEIPT.
    #
    # Sleven's order, 2026-09-08. The sweep runtime moved 79% in a day -
    # 1,606s over 123 controls to 2,871s over 125 - and nobody noticed,
    # because the receipt recorded a total and nothing else. A ceiling
    # cannot be set on a number whose composition is unknown; his words
    # were that any figure would be "a guess wearing a decision's
    # clothes".
    #
    # THIS MEASURES NOTHING NEW. `secs` below is already computed and
    # already printed on every result line. It is only being kept.
    timings = {}
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
            _limit = SLOW_CONTROLS.get(name, args.timeout)
            # THE CHILD WRITES WHAT THE PARENT READS. This side decodes UTF-8,
            # but a child with no console fell back to cp1252 and CRASHED on
            # its own print() - the 18:07 sweep on 2026-09-12 went red because
            # _verify_correspondence.py printed a letter subject containing
            # U+2192. Telling the child to write UTF-8 makes both ends agree.
            proc = subprocess.run(cmd, cwd=ROOT, capture_output=True,
                                  text=True, encoding="utf-8",
                                  errors="replace", timeout=_limit,
                                  env=dict(os.environ, PYTHONIOENCODING="utf-8"))
            code = proc.returncode
            tail = (proc.stdout or "").strip().splitlines()[-1:] or [""]
        except subprocess.TimeoutExpired:
            not_run.append((name, "timed out after %.0fs" % _limit))
            print("  NOTRUN %-41s timed out after %.0fs"
                  % (name, _limit))
            continue
        except Exception as exc:                 # pragma: no cover - reported
            # Timed even when it threw. A control that dies after ten
            # minutes is exactly the kind this receipt exists to find,
            # and recording nothing for it would hide the worst case.
            timings[name] = round(time.time() - t0, 2)
            not_run.append((name, "%s: %s" % (type(exc).__name__, exc)))
            print("  NOTRUN %-41s %s: %s" % (name, type(exc).__name__, exc))
            continue

        secs = time.time() - t0
        timings[name] = round(secs, 2)
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
    elapsed = time.time() - started
    print("%d ok, %d failed, %d skipped, %d NOT RUN, in %.0fs"
          % (len(passed), len(failed), len(skipped), len(not_run), elapsed))
    note = sweep_runtime_note(elapsed, full=not wanted and not args.self_test)
    if note:
        print(note)
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
            seconds=time.time() - started,
            timings=timings)
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

    # B1, THE RECORD AUDIT, REBUILT AFTER EVERY FULL SWEEP (Sleven's ruling,
    # 2026-09-12: after the sweep, not on the beat, no watcher swap). It is
    # report-only: whatever it finds, or if it cannot run at all, THIS sweep's
    # result and receipt are unchanged. Partial and --self-test runs skip it.
    # B2, THE ROUTER, RIDES THE SAME RUN (--route, Architecture's enable of
    # 2026-09-13): it files letters into inbox/ from B1's result and never gates.
    if not wanted and not args.self_test:
        import subprocess as _sp
        try:
            _ra = _sp.run([sys.executable, os.path.join(REPO, "checks", "record_audit.py"), "--route"],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=600, cwd=REPO)
            _lines = _ra.stdout.strip().splitlines() or ["(no output)"]
            if _ra.returncode == 0:
                for _l in _lines:
                    if _l.startswith(("record audit:", "B2 router:", "FILED ", "  NEW for")):
                        print(_l)
            else:
                print("record audit: FAILED (exit %d) - %s - the sweep result is unaffected"
                      % (_ra.returncode, (_ra.stderr.strip().splitlines() or [_lines[-1]])[-1][:200]))
        except Exception as _exc:                # noqa: BLE001 - reported, never gates
            print("record audit: NOT RUN (%s: %s) - the sweep result is unaffected"
                  % (type(_exc).__name__, _exc))

    # A control that could not be run counts against the sweep. Reporting a
    # green sweep with something unrun is the exact failure this project calls
    # SILENT SUCCESS.
    return 1 if (failed or not_run) else 0


if __name__ == "__main__":
    sys.exit(main())
