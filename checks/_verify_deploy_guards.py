#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
_verify_deploy_guards.py - the two deploy scripts refuse each other's payload.

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


def check(label, got, want=True):
    expected = (not want) if SELFTEST else want
    ok = bool(got) == bool(expected)
    (_passed if ok else _failed).append(label)
    print("  %s  %s" % ("PASS" if ok else "FAIL", label))
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


def make_project(tmp, *, gate=True, stamp=True, live_name="citizencompass",
                 extra_file=None, models=True, index=True):
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
    return proj


def run_script(script, proj):
    """Run one of the real deploy scripts with -WhatIf. Returns (code, output)."""
    proc = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", os.path.join(ROOT, "scripts", script),
         "-ProjectPath", proj, "-WhatIf"],
        capture_output=True, text=True, cwd=ROOT,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


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
