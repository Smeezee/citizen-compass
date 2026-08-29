#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_verify_deploy_guards.py - the two deploy scripts refuse each other's payload.

RULE16: INDEPENDENT - it runs the REAL scripts as subprocesses and reads only
their exit codes and their printed refusals. Nothing is imported from
them and no verdict of theirs is taken on trust. The payload markers are
spelled out here rather than copied out of the scripts, the browser-check
list is named here with a drift assertion against the script's own array,
and every input is one this control constructed: an absent check file, a
check that genuinely exits 1, a receipt planted as failed, a receipt that
is not JSON.

I2 of the 2026-08-21 order. The live site got a deploy script for the first
time, and it publishes THE SAME DIRECTORY the testing site publishes - because
Sleven reviews the testing site and then that exact payload goes live. Two
build directories would mean the thing reviewed and the thing shipped were
never the same bytes.

What separates the two payloads is two things the build puts in or leaves out:

    python testing/_src/build_deploy.py           gate + "testing <date>" stamp
    python testing/_src/build_deploy.py --live    neither

So each script has to REFUSE the other one's payload, and those refusals are
the whole safety of the arrangement:

  * deploy_live.ps1 refuses a payload carrying the private-preview password
    gate. Publishing that to the public site would lock every visitor out
    behind a password they were never given, and from the outside it reads as
    an outage rather than a mistake - so nobody would report it.
  * deploy_live.ps1 refuses a payload carrying the testing stamp, which on the
    live site is simply false.
  * deploy_testing.ps1 refuses a payload carrying NEITHER, because that is the
    live build, and publishing it to the testing URL would leave the private
    preview open to anyone who knows the address.
  * deploy_live.ps1 refuses to publish under the TESTING worker's name. The
    worker name IS the subdomain: a wrong one does not fail, it creates a
    SECOND site at a second URL and reports complete success. This project has
    already done that once.

A GUARD THAT HAS NEVER BEEN OBSERVED REFUSING IS NOT A GUARD (rule 12). So
this runs the REAL scripts - not a re-implementation, not a copy of their
regexes - with -WhatIf, against tiny throwaway project trees built in a temp
directory, one per defect. Nothing is uploaded, nothing in the repo is touched,
and no real credential is used: the temp .env carries an obvious fake, which is
enough because -WhatIf returns before wrangler is ever invoked.

WHAT THIS DOES NOT PROVE, stated rather than glossed: it does not prove a real
deploy works. The live worker does not exist yet and only Sleven creates it.
What it proves is that the refusals fire, and that a clean payload gets all the
way to the dry run and reports what it would publish.

`--self-test` inverts every expectation and must exit 1.

Rule 15: every open states its encoding.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SELFTEST = "--self-test" in sys.argv

_passed = []
_failed = []


def check(label, got, want=True, detail=""):
    """The detail is PRINTED ON FAILURE, which it was not until 2026-08-28.

    A failing assertion whose evidence is thrown away costs a debugging cycle
    every time: the crash assertion below reported "a traceback is not a
    decision" and named neither the script nor the traceback, and finding out
    which run it meant took a separate probe.
    """
    expected = (not want) if SELFTEST else want
    ok = bool(got) == bool(expected)
    (_passed if ok else _failed).append(label)
    print("  %s  %s" % ("PASS" if ok else "FAIL", label))
    if not ok and detail:
        print("        %s" % str(detail)[:400])
    return ok


def read(path):
    with open(path, "r", encoding="utf-8", newline="") as fh:
        return fh.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


# The two markers the guards key on, spelled here exactly as the shipped build
# spells them. They are NOT copied out of the scripts - if the build ever stops
# emitting these, the fixtures stop resembling the real payload and the
# assertions below start failing, which is the right way round.
GATE_MARKUP = '<div id="cc-gate">\n  <div class="box">gate</div>\n</div>'
STAMP_TITLE = "<title>Citizen Compass v0.4.0 - testing 2026-08-21</title>"
PLAIN_TITLE = "<title>Citizen Compass v0.4.0</title>"
STAMP_HEAD = ('<h1>Citizen Compass <span class="version">v0.4.0 '
              '<span style="opacity:.6;font-weight:400">testing '
              '2026-08-21</span></span></h1>')
PLAIN_HEAD = '<h1>Citizen Compass <span class="version">v0.4.0</span></h1>'

# THE BROWSER CHECKS THE DEPLOY SCRIPT DEMANDS. Added 2026-08-27, after this
# control started failing three assertions for a reason that was nothing to do
# with the guards: its throwaway project has no `checks/` directory, so the
# browser-check gate - added to deploy_testing.ps1 the same day - refused the
# payload before the dry run was ever reached. The script was right and the
# fixture was stale.
#
# STUBS, AND WHY THAT IS NOT "TESTING THE STUB" HERE. The deploy guard above is
# copied real, because the guard is what section 5 puts under test. These are
# not: what is under test here is the DEPLOY SCRIPT'S GATING - that it refuses a
# missing check, refuses a red one, and lets a green one past. A real browser
# check would drive Chromium for a minute against a payload that is one fake
# index.html, and would prove nothing extra about the gate.
#
# NAMED HERE RATHER THAN PARSED OUT OF THE SCRIPT. If the script's list grows
# and this one does not, section 8's first assertion says so BY NAME, instead of
# leaving somebody to read "browser check missing" and guess which end is wrong.
BROWSER_CHECKS = (
    "_verify_panel_dismiss.mjs",
    "_verify_settings_revision.mjs",
    "_verify_disclosure.mjs",
    "_verify_armour_naming.mjs",
)


def _load_sweep_gate():
    """The REAL module, imported once. Its fingerprint() is the same code the
    deploy runs, which is the point: a fixture that computed its own would be
    asserting that two implementations agree rather than that one works."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_sg_for_fixture", os.path.join(ROOT, "checks", "sweep_gate.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_project(tmp, *, gate=True, stamp=True, live_name="citizencompass",
                 extra_file=None, models=True, index=True,
                 browser_checks=True, red_check=None, receipt=None,
                 sweep="clean"):
    """A throwaway project tree shaped exactly like the real one.

    Tiny on purpose - the scripts walk every file in the payload, and 350 MB of
    real models would make this control slow enough that somebody eventually
    switches it off.
    """
    proj = os.path.join(tmp, "proj")
    deploy = os.path.join(proj, "testing", "_deploy")
    os.makedirs(os.path.join(deploy, "models"), exist_ok=True)

    if index:
        body = (
            "<html><head>" + (STAMP_TITLE if stamp else PLAIN_TITLE) +
            "</head><body>" +
            (GATE_MARKUP if gate else "") +
            (STAMP_HEAD if stamp else PLAIN_HEAD) +
            "</body></html>")
        write(os.path.join(deploy, "index.html"), body)

    if models:
        write(os.path.join(deploy, "models", "Hammerhead.glb"), "not really a glb")

    if extra_file:
        write(os.path.join(deploy, extra_file), "surprise")

    write(os.path.join(proj, "testing", "wrangler.toml"),
          'name = "citizencompasstesting"\naccount_id = "x"\n'
          '[assets]\ndirectory = "./_deploy"\n')
    write(os.path.join(proj, "wrangler.live.toml"),
          'name = "%s"\naccount_id = "x"\n'
          '[assets]\ndirectory = "./testing/_deploy"\n' % live_name)

    # The real guard, copied rather than stubbed: the scripts run it as a
    # subprocess and fail closed if it is missing, so a stub would be testing
    # the stub.
    os.makedirs(os.path.join(proj, "testing", "_src"), exist_ok=True)
    # THE GUARD AND EVERYTHING IT IMPORTS. `check_deploy_clean.py` derives its
    # allow-list from `deploy_pages.py` (rule 14 - one list, imported by both
    # the build and the guard, so they cannot drift). Copying the guard alone
    # left the import unresolvable, the guard subprocess died, and the deploy
    # script FAILED CLOSED - which is correct behaviour and looked like three
    # unrelated assertion failures until somebody read why.
    #
    # Copied rather than stubbed, for the same reason the guard itself is: a
    # stub would be testing the stub.
    for _dep in ("check_deploy_clean.py", "deploy_pages.py"):
        shutil.copyfile(os.path.join(ROOT, "testing", "_src", _dep),
                        os.path.join(proj, "testing", "_src", _dep))

    # An obviously fake token. -WhatIf returns before wrangler is invoked, so
    # this is never used for anything - but without SOMETHING here the scripts
    # would fall through to `npx wrangler whoami` and the test would depend on
    # whatever credential happens to be on this machine.
    write(os.path.join(proj, ".env"),
          "CLOUDFLARE_API_TOKEN=fake-token-for-a-dry-run-only-0000000000\n")

    # The browser-check gate's inputs. `browser_checks=False` leaves the
    # directory absent entirely - the "a check that is not there has not passed"
    # case. `red_check` names one that exits non-zero.
    if browser_checks:
        for _name in BROWSER_CHECKS:
            _red = (_name == red_check)
            write(os.path.join(proj, "checks", _name),
                  'console.log("stub check %s%s");\nprocess.exit(%d);\n'
                  % (_name, " - RED ON PURPOSE" if _red else "", 1 if _red else 0))

    # The build receipt. `receipt=None` writes none, which both scripts treat as
    # "no build to judge" and SAY so rather than assume - that is the normal
    # case for publishing a payload reviewed on the testing site days earlier.
    if receipt is not None:
        write(os.path.join(proj, "testing", "_src", ".last_build.json"),
              json.dumps(receipt))

    # THE SWEEP GATE (Q10), copied real rather than stubbed - it is what the
    # deploy runs, and a stub would be testing the stub. Its receipt path is
    # relative to its OWN location, so a copy inside the fixture reads a
    # fixture receipt and the repo's real one is never touched.
    os.makedirs(os.path.join(proj, "checks"), exist_ok=True)
    shutil.copyfile(os.path.join(ROOT, "checks", "sweep_gate.py"),
                    os.path.join(proj, "checks", "sweep_gate.py"))
    if sweep is not None:
        _sg = _load_sweep_gate()
        try:
            _fp = _sg.fingerprint(os.path.join(proj, "testing", "_deploy"))
        except Exception:
            # THE DELIBERATELY-EMPTY PAYLOADS. Section 6 builds a project with
            # no index.html, and fingerprint() refuses an empty payload - which
            # is correct, and means there is no receipt to write. Those scripts
            # refuse at the entry-point check long before the sweep gate, so
            # the section still tests what it says it does.
            return proj
        _rec = {"fingerprint": _fp, "at": "2026-08-27T23:00:00", "seconds": 1.0,
                "payload_dir": "testing/_deploy", "passed": 98, "failed": [],
                "skipped": [], "not_run": [], "partial": False,
                "self_test": False}
        if sweep == "red":
            _rec["failed"] = ["_verify_planted_red.py"]
        elif sweep == "notrun":
            _rec["not_run"] = ["_verify_planted_unrunnable.py"]
        elif sweep == "stale":
            _rec["fingerprint"] = "0" * 64
        elif sweep == "partial":
            _rec["partial"] = True
        elif sweep == "selftest":
            _rec["self_test"] = True
        elif sweep == "unreadable":
            write(os.path.join(proj, "checks", ".last_sweep.json"),
                  "{ this is not json")
            return proj
        write(os.path.join(proj, "checks", ".last_sweep.json"),
              json.dumps(_rec))
    return proj


_ALL_OUTPUT = []


def run_script(script, proj, extra=()):
    """Run one of the real deploy scripts with -WhatIf. Returns (code, output).

    `extra` appends further switches - section 8 uses it for -IgnoreRedCheck,
    because an override that has never been observed working is as unproven as
    a gate that has never been observed refusing.
    """
    proc = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", os.path.join(ROOT, "scripts", script),
         "-ProjectPath", proj, "-WhatIf"] + list(extra),
        # Rule 15: the child prints ship names. text=True with no encoding
        # decodes it as cp1252 and the reader thread dies, returning
        # returncode=0 with stdout=None - a success shape with no output.
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=ROOT,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    # EVERY OUTPUT IS KEPT so the control can assert that no run REFUSED BY
    # CRASHING. On 2026-08-28 sweep_gate.py raised TypeError on the
    # payload-changed branch - the deploy was correctly stopped, but by an
    # exception rather than by a decision, and `code != 0` cannot tell those
    # apart. A gate that crashes on its refusal path would crash on its success
    # path the day the same mistake lands there.
    _ALL_OUTPUT.append((script, out))
    return proc.returncode, out


def main():
    live_src = read(os.path.join(ROOT, "scripts", "deploy_live.ps1"))
    test_src = read(os.path.join(ROOT, "scripts", "deploy_testing.ps1"))

    print("\n0. BOTH SCRIPTS AND BOTH CONFIGS EXIST, AND THE NAMES DIFFER")
    live_cfg = read(os.path.join(ROOT, "wrangler.live.toml"))
    test_cfg = read(os.path.join(ROOT, "testing", "wrangler.toml"))

    def name_of(cfg):
        for line in cfg.splitlines():
            line = line.strip()
            if line.startswith("name") and "=" in line:
                return line.split("=", 1)[1].strip().strip('"')
        return None

    live_name, test_name = name_of(live_cfg), name_of(test_cfg)
    check("wrangler.live.toml names a worker (%r)" % live_name, bool(live_name))
    check("testing/wrangler.toml names a worker (%r)" % test_name, bool(test_name))
    check("and the two names are DIFFERENT - one URL each",
          live_name and test_name and live_name != test_name)
    check("the live config says which URL it publishes to",
          "workers.dev" in live_cfg and live_name in live_cfg)
    check("and the live script cannot reach Netlify - it names no netlify "
          "command", "netlify deploy" not in live_src.lower()
          and "netlify-cli" not in live_src.lower())
    check("nor can the testing script", "netlify deploy" not in test_src.lower()
          and "netlify-cli" not in test_src.lower())
    check("and the testing script points at the live one, so somebody reading "
          "either finds the other", "deploy_live.ps1" in test_src)
    check("both scripts name the doc that says which publishes which",
          "RELEASING-THE-SITE.md" in live_src and "RELEASING-THE-SITE.md" in test_src)

    tmp = tempfile.mkdtemp(prefix="ccdeployguards-")
    try:
        # ---------------------------------------------------------------
        print("\n1. THE TESTING PAYLOAD (gate + stamp)")
        proj = make_project(tmp, gate=True, stamp=True)
        code, out = run_script("deploy_testing.ps1", proj)
        check("deploy_testing.ps1 accepts it and reaches its dry run", code == 0)
        check("and says the payload is the TESTING one", "payload : TESTING" in out)
        check("and reports what it WOULD run", "-WhatIf: would run" in out)
        check("and states plainly that nothing was uploaded",
              "Nothing was uploaded" in out)

        code, out = run_script("deploy_live.ps1", proj)
        check("deploy_live.ps1 REFUSES it", code != 0)
        check("and names the password gate as the reason",
              "PASSWORD GATE" in out)
        check("and tells the reader how to rebuild for live",
              "--live" in out)
        check("and never got as far as saying it would publish",
              "WOULD PUBLISH" not in out)

        shutil.rmtree(proj)

        # ---------------------------------------------------------------
        print("\n2. THE LIVE PAYLOAD (neither)")
        proj = make_project(tmp, gate=False, stamp=False)
        code, out = run_script("deploy_live.ps1", proj)
        check("deploy_live.ps1 accepts it and reaches its dry run", code == 0)
        check("and says the payload is the LIVE one", "payload : LIVE" in out)
        check("and reports what it WOULD publish", "WOULD PUBLISH" in out)
        check("and names the worker and the URL it would publish to",
              live_name in out and "workers.dev" in out)
        check("and reads the version out of the payload itself",
              "version : v0.4.0" in out)
        check("and states plainly that nothing was uploaded",
              "Nothing was uploaded" in out)
        check("and tells the reader to confirm that from the OUTSIDE",
              "404" in out)

        code, out = run_script("deploy_testing.ps1", proj)
        check("deploy_testing.ps1 REFUSES it", code != 0)
        check("and names the missing gate as the reason",
              "NO PRIVATE-PREVIEW PASSWORD GATE" in out)

        shutil.rmtree(proj)

        # ---------------------------------------------------------------
        print("\n3. A STAMPED BUT UNGATED PAYLOAD - the OTHER live refusal")
        # Proves the two live refusals are two refusals rather than one that
        # happens to catch both cases.
        proj = make_project(tmp, gate=False, stamp=True)
        code, out = run_script("deploy_live.ps1", proj)
        check("deploy_live.ps1 REFUSES it", code != 0)
        check("and names the TESTING STAMP, not the gate",
              "testing <date>" in out and "PASSWORD GATE" not in out)
        shutil.rmtree(proj)

        # ---------------------------------------------------------------
        print("\n4. THE LIVE CONFIG NAMING THE TESTING WORKER")
        proj = make_project(tmp, gate=False, stamp=False,
                            live_name="citizencompasstesting")
        code, out = run_script("deploy_live.ps1", proj)
        check("deploy_live.ps1 REFUSES a live config naming the testing worker",
              code != 0)
        check("and says so in as many words",
              "NAMES THE TESTING WORKER" in out)
        check("and it refuses BEFORE looking at the payload, so the name is "
              "checked even when everything else is right",
              "payload : LIVE" not in out)
        shutil.rmtree(proj)

        # ---------------------------------------------------------------
        print("\n5. AN UNKNOWN FILE IN THE PAYLOAD - the guard that earned its "
              "keep at H3")
        proj = make_project(tmp, gate=False, stamp=False,
                            extra_file="notes-to-self.txt")
        code, out = run_script("deploy_live.ps1", proj)
        check("deploy_live.ps1 REFUSES a payload with an undeclared file",
              code != 0)
        check("and names the file", "notes-to-self.txt" in out)
        shutil.rmtree(proj)

        proj = make_project(tmp, gate=True, stamp=True,
                            extra_file="notes-to-self.txt")
        code, out = run_script("deploy_testing.ps1", proj)
        check("and so does deploy_testing.ps1 - the same guard on the same bytes",
              code != 0)
        shutil.rmtree(proj)

        # ---------------------------------------------------------------
        print("\n6. A PAYLOAD THAT LOST ITS MODELS, AND ONE WITH NO ENTRY POINT")
        # A deploy that silently dropped the models folder still serves a page
        # that looks completely correct.
        proj = make_project(tmp, gate=False, stamp=False, models=False)
        code, out = run_script("deploy_live.ps1", proj)
        check("deploy_live.ps1 REFUSES a payload with no models", code != 0)
        check("and says the models folder is missing", ".glb" in out)
        shutil.rmtree(proj)

        proj = make_project(tmp, gate=False, stamp=False, index=False)
        code, out = run_script("deploy_live.ps1", proj)
        check("deploy_live.ps1 REFUSES a payload with no index.html", code != 0)
        check("and says it will not publish a site with no entry point",
              "entry point" in out)
        shutil.rmtree(proj)

        # ---------------------------------------------------------------
        print("\n8. THE BROWSER-CHECK GATE - missing, red, and overridden")
        # Added 2026-08-27. The gate went into deploy_testing.ps1 that morning
        # and this control did not know about it: every fixture lacked a
        # `checks/` directory, so section 1's clean payload was refused for a
        # reason section 1 was not testing. Rather than only stop that, the gate
        # now gets assertions of its own - it is the last thing standing between
        # a red page and an upload.

        # DRIFT, NAMED. If the script gains a fifth check and BROWSER_CHECKS
        # does not, every other assertion here would fail with "browser check
        # missing" and no clue which end was stale.
        named_in_script = [n for n in BROWSER_CHECKS if n in test_src]
        check("every check this fixture stubs is one the script actually asks "
              "for (%d/%d)" % (len(named_in_script), len(BROWSER_CHECKS)),
              len(named_in_script) == len(BROWSER_CHECKS))
        # Counted inside the $browserChecks array only. A flat count over the
        # whole file picks up the three .mjs names in its own comments, which
        # would make this assertion pass or fail for reasons unrelated to the
        # list it is about.
        _open = test_src.find("$browserChecks = @(")
        _arr = test_src[_open:test_src.find(")", _open)] if _open >= 0 else ""
        script_asks = _arr.count(".mjs'")
        check("and the script asks for no MORE than this fixture stubs "
              "(script names %d, fixture stubs %d)"
              % (script_asks, len(BROWSER_CHECKS)),
              _open >= 0 and script_asks == len(BROWSER_CHECKS))

        # A CHECK THAT IS NOT THERE HAS NOT PASSED.
        proj = make_project(tmp, gate=True, stamp=True, browser_checks=False)
        code, out = run_script("deploy_testing.ps1", proj)
        check("deploy_testing.ps1 REFUSES a payload when a browser check FILE "
              "is missing", code != 0)
        check("and names the missing check", "_verify_panel_dismiss.mjs" in out)
        check("and never reached its dry run", "-WhatIf: would run" not in out)
        shutil.rmtree(proj)

        # A RED CHECK STOPS THE UPLOAD.
        proj = make_project(tmp, gate=True, stamp=True,
                            red_check="_verify_disclosure.mjs")
        code, out = run_script("deploy_testing.ps1", proj)
        check("deploy_testing.ps1 REFUSES when a browser check is RED", code != 0)
        check("and names which one", "_verify_disclosure.mjs" in out and "RED" in out)
        check("and tells the reader the exact override, check name included",
              "-IgnoreRedCheck '_verify_disclosure.mjs'" in out)
        check("and never reached its dry run", "-WhatIf: would run" not in out)

        # AND THE OVERRIDE WORKS, LOUDLY. An escape hatch nobody has seen open
        # is as unproven as a gate nobody has seen shut - and if it did not
        # work, the next person would reach for a blanket -Force instead.
        code, out = run_script("deploy_testing.ps1", proj,
                               extra=["-IgnoreRedCheck", "_verify_disclosure.mjs"])
        check("naming the RED check in -IgnoreRedCheck gets past it", code == 0)
        check("and it says OVERRIDE rather than passing quietly",
              "OVERRIDE" in out and "going live unfixed" in out)
        check("and still reaches the dry run", "-WhatIf: would run" in out)
        # The override is per-check, not a master key.
        code, out = run_script("deploy_testing.ps1", proj,
                               extra=["-IgnoreRedCheck", "_verify_panel_dismiss.mjs"])
        check("but naming a DIFFERENT check does not wave the red one through",
              code != 0)
        shutil.rmtree(proj)

        # ---------------------------------------------------------------
        print("\n9. THE SAME TWO GATES ON THE PUBLIC SIDE")
        # Both gates went into deploy_live.ps1 on 2026-08-27, on Sleven's
        # go-ahead, after this control's section 8 was written and a NOTE here
        # recorded that the live script had neither.
        #
        # THE CONTROL HAD TO COME WITH THEM IN THE SAME SITTING. A gate nobody
        # has ever seen refuse is rule 12's untested gate wearing a reassuring
        # name - and on the public side that is the one place this project
        # cannot take a mistake back. Every assertion below drives the REAL
        # script with -WhatIf; nothing is published and the live worker is never
        # contacted.
        #
        # The live payload carries NEITHER the gate nor the stamp, which is what
        # deploy_live.ps1 accepts - so these fixtures differ from section 8's in
        # exactly that way and in no other.
        LIVE_DRY = "-WhatIf: WOULD PUBLISH THE LIVE SITE."

        proj = make_project(tmp, gate=False, stamp=False, browser_checks=False)
        code, out = run_script("deploy_live.ps1", proj)
        check("deploy_live.ps1 REFUSES a payload when a browser check FILE is "
              "missing", code != 0)
        check("and names the missing check", "_verify_panel_dismiss.mjs" in out)
        check("and never said it would publish", LIVE_DRY not in out)
        shutil.rmtree(proj)

        proj = make_project(tmp, gate=False, stamp=False,
                            red_check="_verify_disclosure.mjs")
        code, out = run_script("deploy_live.ps1", proj)
        check("deploy_live.ps1 REFUSES when a browser check is RED", code != 0)
        check("and names which one",
              "_verify_disclosure.mjs" in out and "RED" in out)
        check("and quotes the LIVE override, not the testing one",
              "deploy_live.ps1 -IgnoreRedCheck '_verify_disclosure.mjs'" in out)
        check("and never said it would publish", LIVE_DRY not in out)

        code, out = run_script("deploy_live.ps1", proj,
                               extra=["-IgnoreRedCheck", "_verify_disclosure.mjs"])
        check("naming the RED check in -IgnoreRedCheck publishes past it",
              code == 0)
        check("and it says OVERRIDE, and says PUBLIC SITE while doing it",
              "OVERRIDE" in out and "PUBLIC SITE" in out)
        check("and reaches the dry run", LIVE_DRY in out)
        code, out = run_script("deploy_live.ps1", proj,
                               extra=["-IgnoreRedCheck", "_verify_panel_dismiss.mjs"])
        check("but naming a DIFFERENT check does not wave the red one through",
              code != 0)
        shutil.rmtree(proj)

        # ---------------------------------------------------------------
        print("\n10. THE BUILD RECEIPT, ON BOTH SCRIPTS")
        # Q2's DONE-WHEN: a build that exits non-zero cannot be followed by an
        # upload in the same invocation, and the refusal names the exit code.
        # The incident behind it - twelve wrong models - happened on the LIVE
        # side, which is why both are asserted here rather than only the one
        # that had the gate first.
        FAILED = {"status": "failed", "exit_code": 1,
                  "at": "2026-08-27T21:00:00", "detail": "planted by this control"}
        for script, dry in (("deploy_testing.ps1", "-WhatIf: would run"),
                            ("deploy_live.ps1", LIVE_DRY)):
            live = script.endswith("live.ps1")
            proj = make_project(tmp, gate=not live, stamp=not live,
                                receipt=FAILED)
            code, out = run_script(script, proj)
            check("%s REFUSES a payload whose last build FAILED" % script,
                  code != 0)
            check("  and names the exit code, not just the failure",
                  "exit code" in out and "1" in out)
            check("  and never reached its dry run", dry not in out)
            code, out = run_script(script, proj, extra=["-IgnoreFailedBuild"])
            check("  and -IgnoreFailedBuild gets past it", code == 0)
            # WHITESPACE-COLLAPSED, because the two banners wrap the same
            # sentence at different points - the testing one breaks between
            # "did NOT" and "succeed". Asserting the raw string would be
            # asserting the line width.
            flat = " ".join(out.split())
            check("  loudly, saying the build did NOT succeed",
                  "OVERRIDE" in flat and "did NOT succeed" in flat)
            check("  and then reaches the dry run", dry in out)
            shutil.rmtree(proj)

            # A receipt that cannot be read is not a passing one.
            proj = make_project(tmp, gate=not live, stamp=not live)
            write(os.path.join(proj, "testing", "_src", ".last_build.json"),
                  "{ this is not json")
            code, out = run_script(script, proj)
            check("%s REFUSES an UNREADABLE build receipt" % script, code != 0)
            check("  and says an unreadable receipt is not a passing one",
                  "unreadable receipt is not a passing one" in out)
            shutil.rmtree(proj)

        # ---------------------------------------------------------------
        print("\n11. THE OTHER 94 CONTROLS - THE SWEEP GATE (Q10)")
        # Until 2026-08-27 the deploy gated on 4 controls out of 98. The sweep
        # found 14 failures at 22:15 that day and the site was deployed
        # repeatedly that evening, because nothing connected the two.
        #
        # THE DONE-WHEN IS "A DELIBERATELY-REDDENED CONTROL STOPS A DEPLOY",
        # so that is asserted directly: a receipt naming a failed control, and
        # the deploy has to refuse. Not a paraphrase of it.
        for script, dry, live in (("deploy_testing.ps1", "-WhatIf: would run", False),
                                  ("deploy_live.ps1", LIVE_DRY, True)):
            g = not live
            proj = make_project(tmp, gate=g, stamp=g, sweep="red")
            code, out = run_script(script, proj)
            check("%s REFUSES a payload whose sweep had a RED control" % script,
                  code != 0)
            check("  and names the control that was red",
                  "_verify_planted_red.py" in out)
            check("  and never reached its dry run", dry not in out)
            shutil.rmtree(proj)

            # NOT RUN IS NOT A PASS. A control that could not execute is the
            # silent-success shape this project keeps finding, so it must stop a
            # deploy exactly as a failure does.
            proj = make_project(tmp, gate=g, stamp=g, sweep="notrun")
            code, out = run_script(script, proj)
            check("  REFUSES when a control could not be RUN, not just failed",
                  code != 0)
            check("  and names it", "_verify_planted_unrunnable.py" in out)
            shutil.rmtree(proj)

            # THE PAYLOAD CHANGED AFTER THE SWEEP. This is the case the receipt
            # exists for - a sweep that passed something else is not a sweep of
            # this.
            proj = make_project(tmp, gate=g, stamp=g, sweep="stale")
            code, out = run_script(script, proj)
            check("  REFUSES when the payload changed since the sweep", code != 0)
            check("  and says so rather than blaming a control",
                  "CHANGED SINCE THE LAST SWEEP" in out)
            shutil.rmtree(proj)

            proj = make_project(tmp, gate=g, stamp=g, sweep=None)
            code, out = run_script(script, proj)
            check("  REFUSES when NO sweep has been run at all", code != 0)
            check("  and tells the reader the command that fixes it",
                  "run_all_controls.py" in out)
            shutil.rmtree(proj)

            proj = make_project(tmp, gate=g, stamp=g, sweep="partial")
            code, out = run_script(script, proj)
            check("  REFUSES a PARTIAL sweep - a subset is not a sweep", code != 0)
            shutil.rmtree(proj)

            proj = make_project(tmp, gate=g, stamp=g, sweep="selftest")
            code, out = run_script(script, proj)
            check("  REFUSES a --self-test sweep - inverted is not clean",
                  code != 0)
            shutil.rmtree(proj)

            proj = make_project(tmp, gate=g, stamp=g, sweep="unreadable")
            code, out = run_script(script, proj)
            check("  REFUSES an UNREADABLE receipt", code != 0)
            shutil.rmtree(proj)

            # AND IT LETS A SWEPT, CLEAN PAYLOAD THROUGH. A gate that refuses
            # everything is not a gate either, and every section above this one
            # depends on this being true.
            proj = make_project(tmp, gate=g, stamp=g, sweep="clean")
            code, out = run_script(script, proj)
            check("  and a clean sweep of THIS payload gets through", code == 0)
            check("  saying how many controls vouched for it",
                  "control(s) green against this exact payload" in out)

            # The override, loud.
            proj2 = make_project(tmp, gate=g, stamp=g, sweep="red")
            code, out = run_script(script, proj2, extra=["-IgnoreSweep"])
            check("  -IgnoreSweep gets past a red sweep", code == 0)
            check("  and says OVERRIDE rather than passing quietly",
                  "OVERRIDE" in out)
            # make_project always builds at tmp/proj, so proj2 IS proj - the
            # second call overwrote the first. One removal, not two.
            shutil.rmtree(proj2, ignore_errors=True)

        crashed = [(sc, o) for sc, o in _ALL_OUTPUT if "Traceback" in o]
        # THE THIRD POSITIONAL IS `want`, NOT `detail`. Passing the evidence
        # there set want="" whenever nothing had crashed, so the assertion
        # INVERTED: it failed exactly when it should have passed and would have
        # passed on a real crash. Caught the same afternoon it was written,
        # by the detail printing as empty on a failure that named no run.
        check("no deploy-script run in this control refused by CRASHING - a "
              "traceback is not a decision",
              not crashed,
              detail="; ".join("%s: %s" % (sc, o[o.index("Traceback"):][:80])
                               for sc, o in crashed[:2]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # -------------------------------------------------------------------
    print("\n7. THE BUILD'S OWN --live FLAG")
    proc = subprocess.run(
        [sys.executable, os.path.join(ROOT, "testing", "_src", "build_deploy.py"),
         "--liv"], capture_output=True, text=True, cwd=ROOT)
    out = (proc.stdout or "") + (proc.stderr or "")
    check("a MISSPELLED --live is refused rather than ignored", proc.returncode != 0)
    check("and the build says which argument it did not understand",
          "--liv" in out and "UNKNOWN ARGUMENT" in out)
    check("and it refused before building anything", "written:" not in out)

    bd = read(os.path.join(ROOT, "testing", "_src", "build_deploy.py"))
    check("the build declares a LIVE mode", "LIVE = '--live' in sys.argv" in bd)
    check("the gate is skipped in live mode, not merely documented as skipped",
          "if LIVE:" in bd and "NO password gate" in bd)
    check("and so is the stamp", "NOT stamped" in bd)

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
