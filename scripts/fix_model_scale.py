"""Put the imported models into the same space as every other ship.

FINDING THIS FIXES (recorded 2026-08-27)
========================================
15 of the 19 Fleetyards imports landed at the wrong size. Measured through the
site's own viewer, longest-axis extent, against ships known to be right:

    Arrow 17.79   Hammerhead 116.30   Caterpillar 111.56      <- correct
    Pitbull 0.001   Tyilui 0.007   Hermes 0.01   Odin 0.07     <- not

The cause is not a bad file. `rescale_all_ships.py` MEASURES NOTHING - it forces
every object's scale to 0.01 and bakes that in. That is right for the 234 models
already here because of how they were authored, and meaningless for anything
else. The imports arrived at object scales of 1.0, 24.8, 0.0576, 1.21 and 0.165.

THE RULE THIS APPLIES, AND THE EVIDENCE FOR IT
==============================================
Scale each model so its largest real dimension equals the ship's largest
published dimension. Both sides are axis-independent, so nothing has to assume
which way round a model is built - which matters, because the imported models do
not share the length-along-Z convention the existing fleet does.

The published figures come from the SAME Fleetyards record the model came from,
so there is no join to get wrong.

Validated against five ships that were already correct - measured_max divided by
published_max:

    Caterpillar 1.001   Hammerhead 1.011   Arrow 1.031
    Gladius 0.941       100i 0.920

So published_max predicts the true size to within about 8% on models known to be
right. That is the accuracy of the target, and it is stated rather than implied.

WHAT IT DOES
============
For each ship: measure sc-ships/<folder>/model.glb in Blender, scale by
published_max / measured_max, write model_scaled.glb, Draco-compress, install.
Then RE-MEASURE the deployed file in a real browser and refuse to call it done
until the number comes back right.

The previous model_scaled.glb and deployed .glb are MOVED ASIDE into
_to_delete/, never deleted (rule 1).

Dry run is the default (rule 5).

Usage:
    python scripts/fix_model_scale.py                # dry run
    python scripts/fix_model_scale.py --write
    python scripts/fix_model_scale.py --write --only Pitbull,Tyilui
"""

import argparse
import datetime
import glob
import json
import os
import shutil
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AVAIL = os.path.join(REPO, "data-layer", "derived", "model-availability")
MANIFEST = os.path.join(AVAIL, "import_manifest.json")
SC_SHIPS = os.path.join(REPO, "sc-ships")
DEPLOY_MODELS = os.path.join(REPO, "testing", "_deploy", "models")
COMPRESSOR = os.path.join(REPO, "testing", "_tools", "cc-compress.cjs")
BLENDER_SIDE = os.path.join(REPO, "scripts", "_blender_scale_to_spec.py")
BLENDER = r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"


# HARD RULE 15'S OTHER HALF: THE WAY OUT NEEDS AN ENCODING TOO.
#
# Rule 15 makes every open() state encoding="utf-8". stdout is the same problem
# wearing different clothes - on Windows it defaults to cp1252, and this script
# PRINTS SHIP NAMES. It died partway through its own dry run on San'tok.yai,
# whose folder is spelled with a macron:
#
#     UnicodeEncodeError: 'charmap' codec can't encode character 'ā'
#
# That is the tok.yai case CLAUDE.md names as "a shipping product, not an edge
# case", and the answer is not to avoid printing the name.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


class ScaleError(RuntimeError):
    pass


def log(m):
    print(m, flush=True)


def published():
    """largest published dimension per ship, from the same record the model
    came from."""
    raws = sorted(glob.glob(os.path.join(AVAIL, "_raw", "*.json")))
    if not raws:
        raise ScaleError("no Fleetyards snapshot in %s/_raw" % AVAIL)
    with open(raws[-1], encoding="utf-8") as fh:
        fy = {i["slug"]: i for i in json.load(fh)}
    with open(MANIFEST, encoding="utf-8") as fh:
        man = json.load(fh)
    out = []
    for s in man["ships"]:
        rec = fy.get(s["slug"])
        if not rec:
            raise ScaleError("no Fleetyards record for %s" % s["slug"])
        m = rec.get("metrics") or {}
        dims = [d for d in (m.get("length"), m.get("beam"), m.get("height")) if d]
        if not dims:
            # Rule 11: an honest gap, not an invented number.
            raise ScaleError(
                "%s has no published dimensions in its Fleetyards record, so "
                "there is nothing to scale it to. Not guessing one." % s["ship"])
        out.append({"ship": s["ship"], "folder": s["folder"],
                    "deploy_name": s["deploy_name"], "slug": s["slug"],
                    "length": m.get("length"), "beam": m.get("beam"),
                    "height": m.get("height"), "target_max": max(dims)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--only", default=None)
    ap.add_argument("--source", choices=("raw", "scaled"), default="raw",
                    help="which file to measure and scale. 'raw' = model.glb, "
                         "for ships with no prior model_scaled.glb. 'scaled' = "
                         "model_scaled.glb, for ships whose MARKERS were derived "
                         "against that geometry - see the comment at build_jobs.")
    ap.add_argument("--from-list", dest="from_list", default=None,
                    help="JSON array of {ship, folder, deploy_name, target_max}. "
                         "Used to rescale ships that were NOT part of the "
                         "Fleetyards import - the pre-existing fleet.")
    args = ap.parse_args()

    run_id = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if args.from_list:
        # THE SAME RULE, A DIFFERENT POPULATION.
        # The import manifest only knows the 19 ships that came from Fleetyards.
        # The fleet audit found the same defect in models that were already here,
        # so the list comes in from outside rather than the rule being copied
        # into a second script.
        with open(args.from_list, encoding="utf-8") as fh:
            ships = json.load(fh)
        for s in ships:
            for k in ("ship", "folder", "deploy_name", "target_max"):
                if not s.get(k):
                    raise ScaleError("list entry missing %r: %r" % (k, s))
    else:
        ships = published()
    if args.only:
        want = set(s.strip() for s in args.only.split(","))
        ships = [s for s in ships if s["ship"] in want]
    if not ships:
        raise ScaleError("no ships selected")

    stage = os.path.join(SC_SHIPS, "_stage_scalefix_%s" % run_id)
    attic = os.path.join(REPO, "_to_delete", "pre_scale_fix_%s" % run_id)

    log("=" * 74)
    log("SCALE FIX   run %s" % run_id)
    log("MODE: %s" % ("WRITE" if args.write else "DRY RUN - nothing will be written"))
    log("=" * 74)
    log("\n  %-28s %10s   %s" % ("ship", "target m", "from published L/B/H"))
    for s in ships:
        # A supplied list carries the target and need not carry the three
        # dimensions it was derived from, so they are printed when present and
        # the line still tells the truth when they are not.
        lbh = ("%s / %s / %s" % (s["length"], s["beam"], s["height"])
               if s.get("length") else
               "target supplied in %s" % os.path.basename(args.from_list or ""))
        log("  %-28s %10.2f   %s" % (s["ship"], s["target_max"], lbh))

    # WHICH FILE IS SCALED IS NOT A DETAIL - IT DECIDES WHETHER THE MARKERS
    # SURVIVE.
    #
    # Marker `unit` values are stored normalised against the hull's longest
    # half-extent and relative to its bbox centre. A uniform rescale cancels in
    # both - but only if the geometry being scaled is the geometry the markers
    # were derived against.
    #
    # On 2026-08-27 the 12 pre-existing ships were scaled from model.glb and
    # `_verify_holo_placement.py` failed: San'tok.yai's fitted offset moved
    # 29.6%, Vulture's 8.5%, Polaris's 3.3%. model_scaled.glb is NOT always
    # model.glb resized - it has its own history - so scaling the original moved
    # the hull out from under its own markers. All 12 were reverted.
    #
    # The 19 Fleetyards imports are the other case: the import created both
    # files from one source and no markers predate them, so 'raw' is right there
    # and 'scaled' would be circular.
    src_name = "model.glb" if args.source == "raw" else "model_scaled.glb"
    log("\nsource: %s per ship" % src_name)
    jobs = []
    for s in ships:
        src = os.path.join(SC_SHIPS, s["folder"], src_name)
        if not os.path.exists(src):
            raise ScaleError("no %s - nothing to rescale from" % os.path.relpath(src, REPO))
        jobs.append({"folder": s["folder"], "in": src,
                     "out": os.path.join(stage, s["folder"], "model_scaled.glb"),
                     "target_max": s["target_max"]})

    log("\n-- measure and scale in Blender " + ("" if args.write else "(DRY RUN)"))
    if not args.write:
        log("  would import each sc-ships/<folder>/model.glb, measure its world")
        log("  bounding box, scale by target_max / measured_max, and write")
        log("  %s/<folder>/model_scaled.glb" % os.path.relpath(stage, REPO))
        log("\n-- compress, then move the current files aside and install (DRY RUN)")
        for s in ships:
            log("  would move aside  %s -> %s"
                % (os.path.join("sc-ships", s["folder"], "model_scaled.glb"),
                   os.path.relpath(os.path.join(attic, s["folder"],
                                                "model_scaled.glb"), REPO)))
            log("  would move aside  %s -> %s"
                % (os.path.join("testing", "_deploy", "models", s["deploy_name"]),
                   os.path.relpath(os.path.join(attic, "models", s["deploy_name"]), REPO)))
        log("\nNothing written. Re-run with --write to proceed.")
        return 0

    for j in jobs:
        os.makedirs(os.path.dirname(j["out"]), exist_ok=True)
    job_file = os.path.join(stage, "_jobs.json")
    with open(job_file, "w", encoding="utf-8") as fh:
        json.dump(jobs, fh, indent=1)

    p = subprocess.run([BLENDER, "--background", "--python", BLENDER_SIDE, "--", job_file],
                       capture_output=True, text=True, timeout=7200)
    log((p.stdout or "")[-3000:])
    if p.returncode != 0:
        raise ScaleError("Blender exited %d: %s" % (p.returncode, (p.stderr or "")[-800:]))
    with open(job_file + ".result.json", encoding="utf-8") as fh:
        res = {r["folder"]: r for r in json.load(fh)}
    bad = [r for r in res.values() if r.get("status") != "OK"]
    if bad:
        raise ScaleError("Blender could not scale %d ship(s), refusing to install "
                         "any of them: %s"
                         % (len(bad), [(b["folder"], b["status"]) for b in bad]))

    log("\n-- compress")
    out_dir = os.path.join(stage, "_compressed")
    p = subprocess.run(["node", COMPRESSOR, stage, out_dir],
                       capture_output=True, text=True, timeout=7200, cwd=REPO)
    log((p.stdout or "")[-1500:])
    if p.returncode != 0:
        raise ScaleError("compressor exited %d: %s" % (p.returncode, (p.stderr or "")[-800:]))

    log("\n-- move the current files aside (rule 1: aside, never deleted) and install")
    for s in ships:
        pairs = [
            (os.path.join(SC_SHIPS, s["folder"], "model_scaled.glb"),
             os.path.join(stage, s["folder"], "model_scaled.glb"),
             os.path.join(attic, s["folder"], "model_scaled.glb")),
            (os.path.join(DEPLOY_MODELS, s["deploy_name"]),
             os.path.join(out_dir, s["deploy_name"]),
             os.path.join(attic, "models", s["deploy_name"])),
        ]
        for live, new, old in pairs:
            if not os.path.exists(new):
                raise ScaleError("stage produced no %s" % os.path.relpath(new, REPO))
            if os.path.exists(live):
                os.makedirs(os.path.dirname(old), exist_ok=True)
                shutil.move(live, old)
            shutil.copy2(new, live)
        log("  %-28s factor %.6f  %.3f -> %.3f m"
            % (s["ship"], res[s["folder"]]["factor"],
               res[s["folder"]]["before_max"], res[s["folder"]]["after_max"]))

    report = {
        "generated_by": "scripts/fix_model_scale.py",
        "run_id": run_id,
        "rule": ("largest model dimension set equal to the largest published "
                 "dimension, from the same Fleetyards record the model came from. "
                 "Axis-independent on both sides."),
        "validation": ("published_max / measured_max on five ships known to be "
                       "correct: Caterpillar 1.001, Hammerhead 1.011, Arrow 1.031, "
                       "Gladius 0.941, 100i 0.920 - so the target is good to "
                       "about 8%"),
        "previous_files_moved_to": os.path.relpath(attic, REPO),
        "source_list": args.from_list or "import_manifest.json",
        "scaled_from": src_name,
        "ships": [dict(s, **{k: res[s["folder"]].get(k)
                             for k in ("factor", "before_max", "after_max",
                                       "before_size", "after_size")})
                  for s in ships],
    }
    report_name = ("scale_fix_report.json" if not args.from_list
                   else "scale_fix_report_%s.json" % run_id)
    with open(os.path.join(AVAIL, report_name), "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=1)
    # Was hardcoded to "scale_fix_report.json" while the write above used
    # report_name, so a --from-list run reported writing a file it had not
    # touched. Harmless to the data and a lie in the output, which is worse
    # than it sounds in a project that reads its own logs as evidence.
    log("\nwrote %s" % os.path.relpath(os.path.join(AVAIL, report_name), REPO))
    log("\nNOT DONE YET: re-measure the deployed files in a real browser before "
        "believing any of this. checks/_verify_model_scale.mjs")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ScaleError as e:
        print("SCALE FIX FAILED: %s" % e, file=sys.stderr)
        sys.exit(2)
