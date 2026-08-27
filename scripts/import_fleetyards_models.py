"""M5 - bring the Fleetyards models into the NORMAL pipeline.

Order: docs/ORDER_the-fifteen-are-not-missing-2026-08-27.md, M5a-M5e.
Input: data-layer/derived/model-availability/gap_fillable.json (written by M4).

THE NORMAL PATH, WHICH THIS USES RATHER THAN REPLACES
=====================================================
M5a says: "into the same pipeline the existing models go through. Not a special
case, not a side folder - if they cannot go through the normal path, that is a
defect in the normal path and it gets fixed instead."

That path, as it exists today:

    sc-ships/<Folder>/model.glb          the raw model
      -> rescale_all_ships.py            Blender, headless, target scale 0.01
    sc-ships/<Folder>/model_scaled.glb   what the compressor reads
      -> testing/_tools/cc-compress.cjs  Draco
    testing/_deploy/models/<SAFE>.glb    what the site serves
    CC_MODELS in testing/_src/_layer.src.html   record id -> folder

Every one of those tools is used here as-is. Nothing is reimplemented.

WHY A STAGING ROOT
------------------
rescale_all_ships.py takes a ships root and walks EVERY folder under it. Run
against the real sc-ships/ that is a 248-folder pass over 234 models that are
already correct - the exact shape of the 234-file in-place mutation hard rule 5
exists because of. So the new ships are built under

    sc-ships/_stage_fleetyards_<RUNID>/

and only the finished files are moved into place. The underscore prefix is this
project's own marker for not-content, so the ship checkers skip it.

DRY RUN IS THE DEFAULT AND THE WRITE PATH IS ONE FLAG
-----------------------------------------------------
Nothing is written without --write. Hard rule 5: any operation touching more
than ~10 files reports first and stops. This one touches roughly 80.

Rule 12's second half says a safety flag must be proven by BEHAVIOUR, not by
reading it. So --dry-run does not merely skip the writes: it records a
fingerprint of every path it would touch BEFORE and AFTER, and prints whether
anything actually changed. A dry run that changed something says so.

Usage:
    python scripts/import_fleetyards_models.py                 # dry run
    python scripts/import_fleetyards_models.py --write
    python scripts/import_fleetyards_models.py --write --only Mantis,PTV
    python scripts/import_fleetyards_models.py --stage-only    # fetch+stage only
"""

import argparse
import base64
import datetime
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import time
import urllib.error
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAP = os.path.join(REPO, "data-layer", "derived", "model-availability", "gap_fillable.json")
SHIP_GAPS = os.path.join(REPO, "data-layer", "derived", "ship-gaps", "ship_gaps.json")
SC_SHIPS = os.path.join(REPO, "sc-ships")
DEPLOY_MODELS = os.path.join(REPO, "testing", "_deploy", "models")
LAYER = os.path.join(REPO, "testing", "_src", "_layer.src.html")
COMPRESSOR = os.path.join(REPO, "testing", "_tools", "cc-compress.cjs")
RESCALE = os.path.join(REPO, "rescale_all_ships.py")
PROV_DIR = os.path.join(REPO, "data-layer", "derived", "model-availability")

BLENDER = r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
TARGET_SCALE = "0.01"
UA = "citizen-compass model import (unofficial fan site)"

# M5d. The order held the 85X back until a human confirmed the shape question.
#
# CLEARED BY SLEVEN, 2026-08-27, on this evidence: our site list has no
# "85X Limited" row at all. It has 85X / ORIG_85X / orig_85x, which joins
# Fleetyards orig-85x on the in-game class identifier AND on name, to one
# record. The collision C1 warned about is between two FLEETYARDS names
# (85x-limited 404s, 85x is a different record); our row is not the ambiguous
# side of it. He was shown that and said to include it.
#
# Left as a named, empty set rather than deleted: the next ship that needs
# holding goes here, and the reason above is the standard for clearing one.
HELD_BACK = set()

# The game build this project is currently working against. Recorded as
# CONTEXT, never as a claim: Fleetyards does not declare a game build for its
# holo assets, so "verified against this patch" is not something we can say.
PATCH_AT_IMPORT = "4.9.0-LIVE.12344265"

SAFE = lambda n: re.sub(r"[^A-Za-z0-9._-]+", "_", n)


class ImportError_(RuntimeError):
    pass


def log(m):
    print(m, flush=True)


def _same(a, b):
    """Byte-identical? Compared by digest, not by size - two different models
    of the same size is exactly the confusion not to introduce here."""
    if os.path.getsize(a) != os.path.getsize(b):
        return False
    h = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
    return h(a) == h(b)


# ------------------------------------------------------------------ fetching

def fetch(url, retries=3):
    last = None
    for attempt in range(retries):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                if r.status != 200:
                    raise ImportError_("HTTP %s for %s" % (r.status, url))
                return r.read()
        except urllib.error.URLError as e:
            last = e
            time.sleep(2 * (attempt + 1))
    raise ImportError_("failed after %d attempts: %r" % (retries, last))


def to_glb(raw, ext):
    """Return GLB bytes. A .glb passes through; a .gltf is packed into the
    binary container the rest of the pipeline expects.

    The Fleetyards .gltf files carry their whole buffer as a base64 data URI
    and reference no external file, so this is a container change and not a
    re-encode: the Draco-compressed mesh bytes are copied through untouched."""
    if ext == "glb":
        if raw[:4] != b"glTF":
            raise ImportError_("served .glb does not start with the glTF magic")
        return raw

    doc = json.loads(raw.decode("utf-8"))
    buffers = doc.get("buffers") or []
    if len(buffers) > 1:
        raise ImportError_("more than one buffer - not handled, and guessing "
                           "which is the mesh is exactly what not to do")
    blob = b""
    if buffers:
        uri = buffers[0].get("uri")
        if uri is None:
            raise ImportError_("buffer has no uri and this is not already a GLB")
        if not uri.startswith("data:"):
            raise ImportError_("buffer points at an EXTERNAL file (%s). This "
                               "importer only handles self-contained files; "
                               "fetching side-car buffers is a different job "
                               "and is not being guessed at here." % uri[:60])
        blob = base64.b64decode(uri.split(",", 1)[1])
        buffers[0].pop("uri", None)
        buffers[0]["byteLength"] = len(blob)

    js = json.dumps(doc, separators=(",", ":")).encode("utf-8")
    js += b" " * ((4 - len(js) % 4) % 4)
    blob += b"\x00" * ((4 - len(blob) % 4) % 4)

    out = bytearray()
    total = 12 + 8 + len(js) + (8 + len(blob) if blob else 0)
    out += b"glTF" + struct.pack("<II", 2, total)
    out += struct.pack("<I", len(js)) + b"JSON" + js
    if blob:
        out += struct.pack("<I", len(blob)) + b"BIN\x00" + blob
    if bytes(out[:4]) != b"glTF":
        raise ImportError_("built a container that is not a GLB")
    return bytes(out)


# ------------------------------------------------------------------ planning

def plan(only=None):
    with open(GAP, encoding="utf-8") as f:
        gap = json.load(f)
    with open(SHIP_GAPS, encoding="utf-8") as f:
        rows = {r["name"]: r for r in json.load(f)["rows"]}

    items, held = [], []
    for g in sorted(gap, key=lambda x: x["our_name"]):
        name = g["our_name"]
        if only and name not in only:
            continue
        if name in HELD_BACK:
            held.append({"ship": name, "why": "M5d - held until a human confirms "
                         "the shape question on the 85X / 85X Limited pair"})
            continue
        r = rows[name]
        folder = r.get("folder") or name
        items.append({
            "ship": name,
            "record_id": r.get("id"),
            "cls": r.get("cls"),
            "manufacturer": r.get("mfr"),
            "folder": folder,
            "folder_exists": os.path.isdir(os.path.join(SC_SHIPS, folder)),
            "needs_cc_models_entry": not r.get("folder"),
            "deploy_name": SAFE(folder) + ".glb",
            "slug": g["fleetyards"]["slug"],
            "url": g["holo"]["url"],
            "ext": g["holo"]["extension"],
            "src_bytes": g["holo"]["size_bytes"],
            "fy_uploaded_at": g["holo"]["uploaded_at"],
        })
    return items, held


def fingerprint(items, stage_root):
    """Every path this run could touch, and what is there now."""
    paths = [stage_root]
    for it in items:
        d = os.path.join(SC_SHIPS, it["folder"])
        paths += [d, os.path.join(d, "model.glb"), os.path.join(d, "model_scaled.glb"),
                  os.path.join(d, "MODEL_SOURCE.txt"),
                  os.path.join(DEPLOY_MODELS, it["deploy_name"])]
    paths.append(LAYER)
    out = {}
    for p in paths:
        try:
            st = os.stat(p)
            out[p] = "dir" if os.path.isdir(p) else "%d/%d" % (st.st_size, int(st.st_mtime))
        except OSError:
            out[p] = None
    return out


# ------------------------------------------------------------------- stages

def stage_fetch(items, stage_root, write):
    log("\n-- stage 1: fetch and stage as model.glb " + ("" if write else "(DRY RUN)"))
    for it in items:
        d = os.path.join(stage_root, it["folder"])
        target = os.path.join(d, "model.glb")
        if not write:
            log("  would fetch %-28s -> %s" % (it["slug"], os.path.relpath(target, REPO)))
            continue
        os.makedirs(d, exist_ok=True)
        raw = fetch(it["url"])
        glb = to_glb(raw, it["ext"])
        with open(target, "wb") as f:
            f.write(glb)
        it["sha256"] = hashlib.sha256(glb).hexdigest()
        it["glb_bytes"] = len(glb)
        log("  %-30s %8.2f MB -> %s" % (it["ship"], len(glb) / 1e6, it["folder"]))


def stage_rescale(stage_root, write):
    log("\n-- stage 2: Blender rescale to %s " % TARGET_SCALE
        + ("" if write else "(DRY RUN)"))
    cmd = [BLENDER, "--background", "--python", RESCALE, "--", stage_root, TARGET_SCALE]
    if not write:
        log("  would run: %s" % " ".join('"%s"' % c if " " in c else c for c in cmd))
        log("  (headless, its own process - rule 10. The script itself refuses "
            "to run in a connected session.)")
        return None
    if not os.path.exists(BLENDER):
        raise ImportError_("Blender not found at %s" % BLENDER)
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    tail = (p.stdout or "")[-2500:]
    log(tail)
    if p.returncode != 0:
        raise ImportError_("Blender exited %d: %s" % (p.returncode, (p.stderr or "")[-800:]))
    return tail


def stage_compress(stage_root, out_dir, write):
    log("\n-- stage 3: Draco compress " + ("" if write else "(DRY RUN)"))
    cmd = ["node", COMPRESSOR, stage_root, out_dir]
    if not write:
        log("  would run: %s" % " ".join(cmd))
        return None
    os.makedirs(out_dir, exist_ok=True)
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=3600, cwd=REPO)
    log((p.stdout or "")[-2500:])
    if p.returncode != 0:
        raise ImportError_("compressor exited %d: %s" % (p.returncode, (p.stderr or "")[-800:]))
    return p.stdout


def stage_install(items, stage_root, out_dir, write, run_id):
    log("\n-- stage 4: install into the real folders " + ("" if write else "(DRY RUN)"))
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    for it in items:
        src_dir = os.path.join(stage_root, it["folder"])
        dst_dir = os.path.join(SC_SHIPS, it["folder"])
        pairs = [(os.path.join(src_dir, "model.glb"), os.path.join(dst_dir, "model.glb")),
                 (os.path.join(src_dir, "model_scaled.glb"),
                  os.path.join(dst_dir, "model_scaled.glb"))]
        comp = os.path.join(out_dir, it["deploy_name"])
        pairs.append((comp, os.path.join(DEPLOY_MODELS, it["deploy_name"])))
        for s, d in pairs:
            if not write:
                log("  would copy %-52s -> %s" % (os.path.relpath(s, REPO),
                                                  os.path.relpath(d, REPO)))
                continue
            if not os.path.exists(s):
                raise ImportError_("stage produced no %s - refusing to install a "
                                   "partial ship" % os.path.relpath(s, REPO))
            if os.path.exists(d):
                # IDEMPOTENT, BUT ONLY WHERE IT IS ACTUALLY THE SAME FILE.
                # A run that dies partway (the 85X and Fury multi-user failure
                # on 2026-08-27 stopped this after one ship was already in)
                # must be re-runnable without hand-clearing state. Identical
                # bytes mean the work is already done, so it is skipped.
                # DIFFERENT bytes are never resolved by guessing which is
                # wanted - that raises and names both.
                if _same(s, d):
                    log("  already installed, identical: %s"
                        % os.path.relpath(d, REPO))
                    continue
                raise ImportError_(
                    "%s already exists and DIFFERS from what this run built "
                    "(%d bytes on disk vs %d staged). Not overwriting and not "
                    "guessing which is wanted. Move the existing one aside if "
                    "it should be replaced."
                    % (os.path.relpath(d, REPO), os.path.getsize(d),
                       os.path.getsize(s)))
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)
        note = os.path.join(dst_dir, "MODEL_SOURCE.txt")
        text = (
            "model.glb in this folder was fetched from the Fleetyards public API\n"
            "on %s, run %s.\n\n"
            "  source   : https://api.fleetyards.net/v1/models/%s\n"
            "  asset    : media.holo -> %s\n"
            "  sha256   : %s\n"
            "  bytes    : %s\n"
            "  uploaded : %s   (Fleetyards' own timestamp for the asset)\n\n"
            "last_verified_patch: NOT VERIFIED.\n"
            "Fleetyards does not declare a game build for its holo assets, so no\n"
            "patch can be claimed for this file without inventing one. The build\n"
            "this project was working against at import was %s. That is context,\n"
            "not a verification, and it is written this way deliberately.\n\n"
            "Attribution follows RULING_community-practice-is-the-standard-2026-08-22:\n"
            "credited to Cloud Imperium Games, unofficial fan site, working contact\n"
            "route, taken down on request. Nothing here changes that wording.\n"
            % (stamp, run_id, it["slug"], it.get("ext"), it.get("sha256", "?"),
               it.get("glb_bytes", "?"), it["fy_uploaded_at"], PATCH_AT_IMPORT))
        if not write:
            log("  would write %s" % os.path.relpath(note, REPO))
            continue
        # A MODEL_SOURCE.txt that is not ours records where somebody else's
        # model came from. Overwriting it would destroy that record.
        if os.path.exists(note):
            with open(note, encoding="utf-8") as f:
                existing = f.read()
            if "Fleetyards" not in existing:
                raise ImportError_(
                    "%s already exists and does not mention Fleetyards, so it "
                    "records a different provenance. Refusing to overwrite it."
                    % os.path.relpath(note, REPO))
        with open(note, "w", encoding="utf-8") as f:
            f.write(text)


def stage_cc_models(items, write):
    need = [i for i in items if i["needs_cc_models_entry"]]
    log("\n-- stage 5: CC_MODELS entries " + ("" if write else "(DRY RUN)"))
    if not need:
        log("  none needed")
        return
    with open(LAYER, encoding="utf-8") as f:
        src = f.read()
    m = re.search(r"const CC_MODELS = (\{.*?\});", src, re.S)
    if not m:
        raise ImportError_("CC_MODELS not found in %s" % LAYER)
    table = json.loads(m.group(1))
    for it in need:
        rid = str(it["record_id"])
        if rid in table:
            raise ImportError_("record %s already maps to %r - refusing to "
                               "repoint an existing ship" % (rid, table[rid]))
        if not write:
            log('  would add "%s": "%s"   (%s)' % (rid, it["folder"], it["ship"]))
            continue
        table[rid] = it["folder"]
    if not write:
        return
    ordered = {k: table[k] for k in sorted(table, key=lambda x: int(x))}
    new = json.dumps(ordered, ensure_ascii=False)
    src = src[:m.start(1)] + new + src[m.end(1):]
    with open(LAYER, "w", encoding="utf-8") as f:
        f.write(src)
    log("  CC_MODELS now holds %d entries" % len(ordered))


def write_manifest(items, held, run_id, write):
    man = {
        "generated_by": "scripts/import_fleetyards_models.py",
        "order": "docs/ORDER_the-fifteen-are-not-missing-2026-08-27.md (M5)",
        "run_id": run_id,
        "imported_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "source": "Fleetyards public API, media.holo",
        "pipeline": ["sc-ships/<folder>/model.glb",
                     "rescale_all_ships.py (Blender headless, scale %s)" % TARGET_SCALE,
                     "sc-ships/<folder>/model_scaled.glb",
                     "testing/_tools/cc-compress.cjs (Draco)",
                     "testing/_deploy/models/<SAFE>.glb"],
        "last_verified_patch": None,
        "last_verified_patch_note": (
            "NOT VERIFIED for any ship here. Fleetyards declares no game build for "
            "its holo assets. The project's build at import was %s; that is recorded "
            "as context and is not a verification." % PATCH_AT_IMPORT),
        "attribution": "RULING_community-practice-is-the-standard-2026-08-22 - unchanged, "
                       "and no attribution or licence text was edited by this script.",
        "ships": items,
        "held_back": held,
    }
    path = os.path.join(PROV_DIR, "import_manifest.json")
    if not write:
        log("\n  would write %s" % os.path.relpath(path, REPO))
        return
    with open(path, "w", encoding="utf-8") as f:
        json.dump(man, f, indent=1, ensure_ascii=False)
        f.write("\n")
    log("\n  wrote %s" % os.path.relpath(path, REPO))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="actually do it. Without this nothing is written.")
    ap.add_argument("--only", default=None, help="comma-separated ship names")
    ap.add_argument("--stage-only", action="store_true",
                    help="stop after fetch+rescale+compress; do not install")
    args = ap.parse_args()

    run_id = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    only = set(s.strip() for s in args.only.split(",")) if args.only else None
    items, held = plan(only)
    stage_root = os.path.join(SC_SHIPS, "_stage_fleetyards_%s" % run_id)
    out_dir = os.path.join(stage_root, "_compressed")

    log("=" * 74)
    log("M5 - FLEETYARDS MODEL IMPORT   run %s" % run_id)
    log("MODE: %s" % ("WRITE" if args.write else "DRY RUN - nothing will be written"))
    log("=" * 74)
    log("\n%d ship(s) to import, %d held back" % (len(items), len(held)))
    for h in held:
        log("  HELD  %-20s %s" % (h["ship"], h["why"]))
    log("")
    log("  %-30s %-22s %-8s %-9s %s" % ("ship", "folder", "new dir", "CC_MODELS", "deploy file"))
    for it in items:
        log("  %-30s %-22s %-8s %-9s %s" % (
            it["ship"], it["folder"], "no" if it["folder_exists"] else "YES",
            "add" if it["needs_cc_models_entry"] else "-", it["deploy_name"]))

    before = fingerprint(items, stage_root)

    stage_fetch(items, stage_root, args.write)
    stage_rescale(stage_root, args.write)
    stage_compress(stage_root, out_dir, args.write)
    if not args.stage_only:
        stage_install(items, stage_root, out_dir, args.write, run_id)
        stage_cc_models(items, args.write)
    write_manifest(items, held, run_id, args.write)

    after = fingerprint(items, stage_root)
    changed = [p for p in before if before[p] != after[p]]
    log("\n" + "=" * 74)
    if args.write:
        log("WRITE RUN. %d tracked path(s) changed." % len(changed))
    else:
        # Rule 12: prove the no-op by behaviour, not by reading the flag.
        if changed:
            log("DRY RUN CHANGED %d PATH(S). THAT IS A DEFECT IN THIS SCRIPT:" % len(changed))
            for p in changed:
                log("   %s" % os.path.relpath(p, REPO))
            return 3
        log("DRY RUN VERIFIED: %d tracked paths checked before and after, "
            "none changed." % len(before))
        log("Nothing has been written. Re-run with --write to proceed.")
    log("=" * 74)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ImportError_ as e:
        print("IMPORT FAILED: %s" % e, file=sys.stderr)
        sys.exit(2)
