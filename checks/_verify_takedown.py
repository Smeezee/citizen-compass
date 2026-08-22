#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A4: the off switch, executed - not described.

    "A takedown script nobody has ever executed is a script that fails the
    first time it is needed, which is the worst possible time."

So this RUNS scripts/takedown.py. Not a copy of its logic, not an import of one
helper - the script, as a subprocess, with arguments, exactly as a person in a
hurry would run it.

THE FIXTURE CONTAINS BOTH KINDS OF ASSET, and that is the whole design:

    tagged   (source: cig-holoviewer)      -> MUST be gone
    untagged (source: scunpacked, own)     -> MUST SURVIVE

The second is the load-bearing one. A script that simply deletes everything
passes "the tagged assets are gone" perfectly. The order says so, and it is the
assertion this file exists for.

THE DRY RUN IS PROVEN BY BEHAVIOUR, not by reading the code: it is executed and
then every file is checked from the outside to still be there, with the register
byte-identical. A "report-only" switch that has never been observed to no-op is
a check that the destructive path will not run, wearing a reassuring name.

WHAT THIS TOUCHES IN THE REAL REPO, and how it puts it back. The last section
runs the REAL build against a fixture register so that "the site still builds"
means the actual site. That build moves the named ship's model out of
testing/_deploy/ (correctly - it is stamped removed). The finally block moves it
back and rebuilds with the real register, and ASSERTS the restore happened
rather than assuming it.

Rule 15: every open states its encoding. Hard rule 1: nothing is deleted; the
takedown moves things to _to_delete/.

Usage:  venv/Scripts/python.exe checks/_verify_takedown.py
"""

import io
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "scripts"))

TAKEDOWN = os.path.join(REPO, "scripts", "takedown.py")
BUILD = os.path.join(REPO, "testing", "_src", "build_deploy.py")
DEPLOY = os.path.join(REPO, "testing", "_deploy")
TMP = os.path.join(REPO, "_to_delete", "a4_takedown_fixture")

# A real ship, so "the site still builds" is measured against the real site.
REAL_CLASS = "AEGS_Avenger_Stalker"
REAL_MODEL = "Avenger_Stalker.glb"

passed = 0
failures = []
notes = []


def record(ok, label, detail=""):
    global passed
    if ok:
        passed += 1
        print("  ok   %s" % label)
    else:
        failures.append(("%s %s" % (label, detail)).strip())
        print("  FAIL %s %s" % (label, detail))


def run(args, env_extra=None):
    env = dict(os.environ)
    env.update(env_extra or {})
    return subprocess.run([sys.executable] + args, cwd=REPO, env=env,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace")


# ---------------------------------------------------------------------------
# The fixture: a miniature built site with tagged AND untagged assets in it.
# ---------------------------------------------------------------------------
fx_deploy = os.path.join(TMP, "_deploy")
fx_reg = os.path.join(TMP, "register.json")
for sub in ("models", "images", "fonts"):
    os.makedirs(os.path.join(fx_deploy, sub), exist_ok=True)

TAGGED = [("Redeemer.glb", "model", "cig-holoviewer"),
          ("Polaris.glb", "model", "cig-holoviewer"),
          ("hero_shot.webp", "image", "cig-fankit-restricted")]
UNTAGGED = [("Hammerhead.glb", "model", "scunpacked"),
            ("Gladius.glb", "model", "scunpacked"),
            ("own_render.webp", "image", "own-render"),
            ("Orbitron.ttf", "font", "ofl-fonts")]
KIND_DIR = {"model": "models", "image": "images", "font": "fonts"}


def fx_path(name, kind):
    return os.path.join(fx_deploy, KIND_DIR[kind], name)


for name, kind, _src in TAGGED + UNTAGGED:
    with io.open(fx_path(name, kind), "w", encoding="utf-8") as fh:
        fh.write("fixture bytes for %s\n" % name)

with io.open(fx_reg, "w", encoding="utf-8", newline="\n") as fh:
    json.dump({"schema": 1, "assets": [
        {"file": n, "kind": k, "source": s, "added": "2026-08-22"}
        for n, k, s in TAGGED + UNTAGGED]}, fh, indent=1)
    fh.write("\n")

print("fixture: %d tagged, %d untagged, in %s"
      % (len(TAGGED), len(UNTAGGED), os.path.relpath(fx_deploy, REPO)))

# ---------------------------------------------------------------------------
print("\n--- the dry run must change NOTHING, and that is checked from "
      "outside ---")
before = io.open(fx_reg, "r", encoding="utf-8").read()
r = run([TAKEDOWN, "--dry-run", "--deploy-dir", fx_deploy,
         "--register", fx_reg, "--no-build"])
record(r.returncode == 0, "the dry run completes", "exit %d" % r.returncode)
record(all(os.path.exists(fx_path(n, k)) for n, k, _ in TAGGED + UNTAGGED),
       "after --dry-run EVERY file is still in place, tagged included",
       "this is the flag proven by behaviour, not by reading it")
record(io.open(fx_reg, "r", encoding="utf-8").read() == before,
       "and the register is byte-identical - nothing was stamped")
record("WOULD MOVE 3 file(s)" in r.stdout,
       "and it reported exactly what it would have moved",
       r.stdout.strip().splitlines()[-1][:60] if r.stdout.strip() else "")

# ---------------------------------------------------------------------------
print("\n--- a real run without --yes must refuse ---")
r = run([TAKEDOWN, "--deploy-dir", fx_deploy, "--register", fx_reg,
         "--no-build"])
record(r.returncode != 0 and all(
    os.path.exists(fx_path(n, k)) for n, k, _ in TAGGED),
    "no --yes, no removal - it cannot happen by accident",
    "exit %d" % r.returncode)

# ---------------------------------------------------------------------------
print("\n--- THE REAL RUN ---")
r = run([TAKEDOWN, "--yes", "--deploy-dir", fx_deploy, "--register", fx_reg,
         "--no-build"])
record(r.returncode == 0, "the takedown completes", "exit %d" % r.returncode)

gone = [n for n, k, _ in TAGGED if not os.path.exists(fx_path(n, k))]
record(len(gone) == len(TAGGED),
       "EVERY TAGGED ASSET IS GONE from the built site",
       "%d of %d removed" % (len(gone), len(TAGGED)))

survived = [n for n, k, _ in UNTAGGED if os.path.exists(fx_path(n, k))]
record(len(survived) == len(UNTAGGED),
       "EVERY UNTAGGED ASSET SURVIVES - the assertion that catches a script "
       "which just deletes everything",
       "%d of %d survived: %s" % (len(survived), len(UNTAGGED),
                                  ", ".join(survived)))

reg_after = json.loads(io.open(fx_reg, "r", encoding="utf-8").read())
stamped = [a["file"] for a in reg_after["assets"] if a.get("removed")]
record(sorted(stamped) == sorted(n for n, _, _ in TAGGED),
       "and exactly the tagged records carry a `removed` stamp - the half that "
       "makes the removal survive the next build",
       ", ".join(stamped))

# Hard rule 1: moved, not deleted.
attics = [d for d in os.listdir(os.path.join(REPO, "_to_delete"))
          if d.startswith("takedown_")]
record(bool(attics), "the removed files were MOVED to _to_delete, not deleted",
       ", ".join(attics[:3]))
notes.append("real run: %d tagged removed, %d untagged untouched, %d records "
             "stamped" % (len(gone), len(survived), len(stamped)))

# ---------------------------------------------------------------------------
print("\n--- and the site still builds, degraded and honest ---")
real_model = os.path.join(DEPLOY, "models", REAL_MODEL)
moved_real = os.path.join(REPO, "_to_delete", "takedown_reappeared", "models",
                          REAL_MODEL)
site_reg = os.path.join(TMP, "register_realship.json")
with io.open(site_reg, "w", encoding="utf-8", newline="\n") as fh:
    json.dump({"schema": 1, "assets": [
        {"file": REAL_MODEL, "kind": "model", "source": "cig-holoviewer",
         "added": "2026-08-22", "removed": "2026-08-22"}]}, fh, indent=1)
    fh.write("\n")

try:
    b = run([BUILD], {"CC_CIG_REGISTER": site_reg,
                      "CC_TAKEDOWN_CONTACT": "a4-control@example.invalid"})
    record(b.returncode == 0,
           "the site BUILDS with a model withdrawn - degraded, not broken",
           "exit %d" % b.returncode)
    record("TAKEDOWN IN EFFECT" in b.stdout,
           "and the build says a takedown is in effect")

    gen = io.open(os.path.join(REPO, "testing", "_src",
                               "loadout_model.gen.js"),
                  "r", encoding="utf-8").read()
    record(('"%s"' % REAL_CLASS) in gen.split("LOADOUT_WITHDRAWN")[-1],
           "the withdrawn ship is published in LOADOUT_WITHDRAWN", REAL_CLASS)
    body = gen.split("const LOADOUT_MODEL=")[1].split(";")[0]
    record(('"%s"' % REAL_CLASS) not in body,
           "and is NOT in the model map, so no URL to it can be built")

    page = io.open(os.path.join(DEPLOY, "loadout.html"), "r",
                   encoding="utf-8").read()
    record("taken down at the" in page and "rights holder" in page,
           "the served page says the model was removed at the rights "
           "holder's request - not 'no model yet', which would be untrue")
    record("v.cancel(); v.clear(); v.stop();" in page.split(
        "WITHDRAWN.has(shipId)")[-1][:400],
        "and it tears the viewer down rather than leaving a dead canvas")
    record(not os.path.exists(real_model),
           "the withdrawn model is no longer in the built site",
           REAL_MODEL)
    notes.append("build with a withdrawal: exit %d, %s withdrawn and the page "
                 "says why" % (b.returncode, REAL_CLASS))
finally:
    # Put the real site back exactly as it was, and PROVE it went back.
    if os.path.exists(moved_real) and not os.path.exists(real_model):
        shutil.move(moved_real, real_model)
    restored = os.path.exists(real_model)
    rb = run([BUILD], {"CC_TAKEDOWN_CONTACT": "a4-control@example.invalid"})
    record(restored and rb.returncode == 0,
           "the real site is restored: the model is back and it rebuilds "
           "clean",
           "model present %s, rebuild exit %d" % (restored, rb.returncode))
    gen = io.open(os.path.join(REPO, "testing", "_src",
                               "loadout_model.gen.js"),
                  "r", encoding="utf-8").read()
    record("const LOADOUT_WITHDRAWN=[];" in gen,
           "and nothing is left marked withdrawn")

# ---------------------------------------------------------------------------
print("")
if notes:
    print("MEASURED, for the ledger:")
    for n in notes:
        print("  - " + n)
    print("")

if failures:
    print("FAILED: %d of %d" % (len(failures), passed + len(failures)))
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("PASSED: %d assertions." % passed)
sys.exit(0)
