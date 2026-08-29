#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A2: the "Made By The Community" mark, and the build's refusal without it.

RULE16: INDEPENDENT - it RUNS THE REAL BUILD as a subprocess against a fixture and
then inspects the resulting image with PIL, which is neither the build's
code nor its opinion. The refusal half is driven the same way: take the
mark away and the build has to stop.
The pattern, said once because several controls in this repo share it:
driving a real program as a SUBPROCESS with input this file constructed,
and judging the exit code and the printed refusal, is independent. The
tool cannot pass by agreeing with itself, because what must be refused was
decided here and nothing is imported from it.

THE NEGATIVE CONTROL IS THE LOAD-BEARING ONE. The order says so plainly:

    "Assert that an image composited WITHOUT the mark is REFUSED by the build.
    Without that, 'the mark is applied' also passes on a build that applies
    nothing."

So the two halves below RUN THE REAL BUILD, as a subprocess, against a fixture
register - not a copy of the guard, not the guard's inner function, and not a
description of what the build would do. `testing/_src/build_deploy.py` is
executed exactly as a deploy executes it, and its exit status is the assertion:

    unmarked image registered as CIG-sourced  ->  build MUST fail
    marked image registered as CIG-sourced    ->  build MUST succeed

Both halves are required. The first alone passes on a build that refuses
everything; the second alone passes on a build that refuses nothing.

The fixture register is pointed at by CC_CIG_REGISTER so the real register is
never touched. The fixture IMAGE is written into testing/_deploy/images/,
because that is where the guard genuinely looks - and it is moved to
_to_delete/ afterwards rather than removed (hard rule 1).

Rule 15: every open states its encoding.

Usage:  venv/Scripts/python.exe checks/_verify_community_mark.py
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

import community_mark as cm  # noqa: E402

DEPLOY = os.path.join(REPO, "testing", "_deploy")
IMAGES = os.path.join(DEPLOY, "images")
BUILD = os.path.join(REPO, "testing", "_src", "build_deploy.py")
TMP = os.path.join(REPO, "_to_delete", "a2_mark_fixtures")

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


# ---------------------------------------------------------------------------
print("--- the mark file itself ---")
try:
    mp = cm.mark_path("white")
    record(os.path.exists(mp), "the Fan Kit mark is readable", mp)
except FileNotFoundError as exc:
    print("NOT PERFORMED: %s" % exc)
    print("The mark cannot be located, so nothing below can be measured. This "
          "is reported as NOT PERFORMED and never as a pass.")
    sys.exit(2)

os.makedirs(TMP, exist_ok=True)

# A base image that is not already marked. One of the site's own thumbnails, so
# the fixture is the same kind of thing the guard will meet in production.
base_src = os.path.join(IMAGES, "100i.webp")
if not os.path.exists(base_src):
    print("NOT PERFORMED: %s is not built, so there is no image to test "
          "against." % base_src)
    sys.exit(2)

base = os.path.join(TMP, "base.png")
shutil.copyfile(base_src, base)

# ---------------------------------------------------------------------------
print("\n--- the detector separates marked from unmarked ---")
marked = os.path.join(TMP, "marked.jpg")
cm.apply_mark(base, marked)
s_un, s_mk = cm.mark_score(base), cm.mark_score(marked)
record(s_un < cm.MARK_THRESHOLD,
       "an unmarked image scores below the threshold",
       "%.4f < %.2f" % (s_un, cm.MARK_THRESHOLD))
record(s_mk >= cm.MARK_THRESHOLD,
       "the same image, marked, scores above it",
       "%.4f >= %.2f" % (s_mk, cm.MARK_THRESHOLD))
record(s_mk - s_un > 0.5,
       "and the two are separated by a wide margin, not a hair",
       "gap %.4f" % (s_mk - s_un))
notes.append("detector: unmarked %.4f, marked %.4f, threshold %.2f"
             % (s_un, s_mk, cm.MARK_THRESHOLD))

# ---------------------------------------------------------------------------
print("\n--- CIG's requirements, measured on the output ---")
from PIL import Image  # noqa: E402

bi, mi = Image.open(base), Image.open(marked)
mk = Image.open(cm.mark_path("white"))
info = cm.apply_mark(base, marked)
w, h = info["mark_size"]
px, py = info["pos"]

record(abs((w / h) - (mk.width / mk.height)) < 0.01,
       "NOT DISTORTED: the mark keeps its own aspect ratio",
       "%dx%d vs source %dx%d" % (w, h, mk.width, mk.height))
record(px + w <= bi.width and py + h <= bi.height
       and px > bi.width * 0.5 and py > bi.height * 0.5,
       "IN THE CORNER: placed in the lower-right quadrant, fully inside",
       "at (%d,%d) in %dx%d" % (px, py, bi.width, bi.height))
record(min(w, h) >= cm.MARK_MIN_PX * 0.9
       and w >= min(bi.size) * cm.MARK_FRACTION * 0.9,
       "A LEGIBLE SIZE: at least the configured fraction of the short side",
       "%dpx wide on a %dpx short side" % (w, min(bi.size)))
record(cm.OPACITY >= 0.50,
       "NO LESS THAN 50%% OPACITY: composited at %d%%" % (cm.OPACITY * 100))

# The opacity floor refuses rather than trusting its caller.
try:
    cm.apply_mark(base, os.path.join(TMP, "illegal.jpg"), opacity=0.25)
    record(False, "an opacity below CIG's floor is REFUSED",
           "0.25 was accepted and an image was written")
except ValueError:
    record(True, "an opacity below CIG's floor is REFUSED, not clamped")

# NOT FLIPPED and NOT RECOLOURED: the mark's own pixels, in their own order.
# Correlate the marked corner against the mark and against the mark flipped;
# the upright one must win, which a flipped or mirrored paste could not do.
_orig_mark_path = cm.mark_path


def _score_against(img):
    """Correlate the marked corner against a TRANSFORMED mark."""
    tp = os.path.join(TMP, "mark_transform.png")
    img.save(tp)
    cm.mark_path = lambda variant="white": tp
    try:
        return cm.mark_score(marked)
    finally:
        cm.mark_path = _orig_mark_path


# The margin is 0.05, set from measurement and not from taste. The mark is a
# near-circular badge, so a LEFT-RIGHT MIRROR still correlates at 0.880 against
# the upright 0.990 - a gap of 0.11, and the tightest of the four. The vertical
# and rotational transforms fall to 0.54..0.60. Asserting a large margin here
# would be asserting something about this mark that is not true.
_transforms = [("mirrored left-right", Image.FLIP_LEFT_RIGHT),
               ("flipped top-bottom", Image.FLIP_TOP_BOTTOM),
               ("rotated 180", Image.ROTATE_180),
               ("rotated 90", Image.ROTATE_90)]
_scores = [(nm, _score_against(mk.transpose(t))) for nm, t in _transforms]
_worst = max(_scores, key=lambda x: x[1])
record(all(s_mk > sc + 0.05 for _nm, sc in _scores),
       "NOT FLIPPED OR REVERSED: the corner matches the mark UPRIGHT better "
       "than any of its four transforms",
       "upright %.4f vs %s" % (s_mk, ", ".join(
           "%s %.4f" % (nm, sc) for nm, sc in _scores)))
notes.append("orientation: upright %.4f beats the closest transform (%s "
             "%.4f) by %.4f" % (s_mk, _worst[0], _worst[1], s_mk - _worst[1]))

# ---------------------------------------------------------------------------
print("\n--- THE LOAD-BEARING CONTROL: the real build, run twice ---")


def run_build(env_register):
    env = dict(os.environ)
    env["CC_CIG_REGISTER"] = env_register
    # A CIG-sourced asset also switches on A3's contact requirement, so without
    # this the build fails on the MISSING CONTACT and never reaches the mark
    # guard at all. The first run of this control did exactly that and scored a
    # PASS on "the build refused" - refused for the wrong reason. That is the
    # silent-success shape this project exists to catch, so the check now
    # supplies a contact and asserts on WHICH refusal it got.
    env.setdefault("CC_TAKEDOWN_CONTACT", "a2-control@example.invalid")
    return subprocess.run(
        [sys.executable, BUILD],
        cwd=os.path.join(REPO, "testing", "_src"),
        env=env, capture_output=True, text=True, encoding="utf-8",
        errors="replace")


def write_register(path, file_name):
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"schema": 1, "assets": [
            {"file": file_name, "kind": "image", "source": "cig-holoviewer",
             "added": "2026-08-22", "note": "A2 control fixture"}]},
            fh, indent=1)
        fh.write("\n")


fixture_name = "_a2_mark_fixture.webp"
fixture_out = os.path.join(IMAGES, fixture_name)
reg_bad = os.path.join(TMP, "register_unmarked.json")
reg_good = os.path.join(TMP, "register_marked.json")

try:
    # --- NEGATIVE: an UNMARKED image, registered as CIG-sourced. -----------
    shutil.copyfile(base_src, fixture_out)          # deliberately unmarked
    write_register(reg_bad, fixture_name)
    r = run_build(reg_bad)
    said = "MADE BY THE COMMUNITY MARK MISSING" in (r.stdout + r.stderr)
    record(r.returncode != 0 and said,
           "an image composited WITHOUT the mark is REFUSED by the build, AND "
           "refused for THAT reason - not for some other failure that happened "
           "to stop the build first",
           "exit %d, named the mark: %s" % (r.returncode, said))
    notes.append("negative control: real build exited %d on an unmarked "
                 "CIG-sourced image" % r.returncode)

    # --- POSITIVE: the same image, marked. --------------------------------
    cm.apply_mark(base_src, os.path.join(TMP, "fixture_marked.png"))
    # save as the name the register points at, marked this time
    Image.open(os.path.join(TMP, "fixture_marked.png")).save(
        fixture_out, "WEBP", quality=90)
    write_register(reg_good, fixture_name)
    r2 = run_build(reg_good)
    record(r2.returncode == 0,
           "the SAME image, marked, is ACCEPTED - so the guard is not simply "
           "refusing everything",
           "exit %d: %s" % (r2.returncode,
                            (r2.stdout + r2.stderr).strip().splitlines()[-1:]
                            and (r2.stdout + r2.stderr).strip()
                            .splitlines()[-1][:70] or ""))
    record("community mark: 1 CIG-sourced image(s), all carry it" in r2.stdout,
           "and reports having checked it")
    notes.append("positive control: real build exited %d on the marked image"
                 % r2.returncode)
finally:
    # Hard rule 1: moved aside, never deleted.
    if os.path.exists(fixture_out):
        shutil.move(fixture_out, os.path.join(TMP, fixture_name))
    # Rebuild once more with the REAL register so _deploy is left exactly as a
    # normal build leaves it, not carrying a fixture's state.
    env = dict(os.environ)
    env.pop("CC_CIG_REGISTER", None)
    subprocess.run([sys.executable, BUILD],
                   cwd=os.path.join(REPO, "testing", "_src"),
                   env=env, capture_output=True, text=True)

# ---------------------------------------------------------------------------
print("")
if notes:
    print("MEASURED, for the ledger:")
    for n in notes:
        print("  - " + n)
    print("")

print("REPORTED, NOT FIXED (hard rule 8 - Fan Kit compliance is Sleven's):")
print("  - 241 ship thumbnails in images/ do not carry the mark. Their")
print("    provenance (docs/workorder-image-provenance-and-renders.md) says the")
print("    upstream pack is governed by terms naming 'Made by the Community',")
print("    and equally that it is NOT established whether any individual image")
print("    is a CIG asset, a screenshot or a render. Marking all 241 is a bulk")
print("    mutation (rule 5) on a compliance question (rule 8), and Part 2 of")
print("    that work order plans to replace them with our own renders anyway.")
print("")

if failures:
    print("FAILED: %d of %d" % (len(failures), passed + len(failures)))
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("PASSED: %d assertions." % passed)
sys.exit(0)
