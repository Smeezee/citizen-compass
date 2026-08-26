# -*- coding: utf-8 -*-
"""E14 / W4 - the enumeration. Both directions, every ship, no hand-checking.

WHY THIS EXISTS
===============
Sleven walked the ship list alphabetically on 2026-08-23 and filed nineteen
defect reports. Nineteen reports, six causes, and every one of them was a gap
that a machine could have listed in a second. `W1` of that order says it
outright: **do not have Sleven find the rest by hand.**

So this reports BOTH DIRECTIONS, always, in one pass:

  A. every ship in the SITE list that cannot show a model, and WHY
  B. every model on disk that no ship page reaches

Direction B is the one that gets forgotten, and it is the one that finds work
already paid for and not wired up - a `.glb` sitting in the folder that no
visitor can ever reach.

THE JOIN CHAIN, WHICH IS THE WHOLE FINDING
==========================================
A ship becomes "real" to the site by surviving four joins in a row. Any one of
them missing costs the ship its page, its model AND its hull markers at once -
which is why Sleven's "no hardpoints" reports and his "only links to RSI"
reports name the same ships. It reads as two bugs from the outside and it is
one gate:

    site record (releases/latest.html, by id)
      -> ship_resolution.json     matched[].site == display name   -> game file
      -> LOADOUT_SHIPS            file stem (lowercased) == ClassName
      -> CC_MODELS[id]            folder -> testing/_deploy/models/<folder>.glb
      -> hardpoints_fleet.json    model filename -> placed hardpoints

Fail join 1 and `nameCellHtml` has no `loadout.html#Class` to point at, so it
falls back to `pledge_url` and the visitor is sent to robertsspaceindustries
.com. The SAME failure means no ClassName, so no marker set is ever emitted.
One cause, two symptoms, five ships.

NO GUESSING. Rule 11. A ship that cannot be resolved is REPORTED as
unresolved and is never matched by similarity, prefix or edit distance. The
whole point of the artifact is that an honest gap is visible.

Rule 15: every open states its encoding.

Usage:
    venv/Scripts/python.exe scripts/enumerate_ship_gaps.py
    ... --json <path>   also write the machine-readable form
    ... --quiet         counts and headline lists only
"""
import argparse
import collections
import io
import json
import os
import re
import sys

# RULE 15 APPLIES TO stdout, NOT ONLY TO open(). This script prints ship
# names, and `tok.yai` is spelled San'tok.yāi with a macron - on Windows the
# console encoder is cp1252 and printing it raises UnicodeEncodeError, killing
# the report mid-list. The enumeration would then be BOTH wrong and loud, or
# worse, redirected to a file that ends where the first Xi'an ship began.
# Caught by a one-off diagnostic that did exactly that.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

SITE_PAGE = os.path.join(REPO, "releases", "latest.html")
RESOLUTION = os.path.join(REPO, "data-layer", "ship_resolution.json")
LAYER = os.path.join(REPO, "testing", "_src", "_layer.src.html")
MODELS_DIR = os.path.join(REPO, "testing", "_deploy", "models")
SHIPS_DIR = os.path.join(REPO, "sc-ships")
GEN_DIR = os.path.join(REPO, "testing", "_src")
FLEET = os.path.join(REPO, "data-layer", "derived", "holo-hardpoints",
                     "hardpoints_fleet.json")
PLACEMENT = os.path.join(REPO, "data-layer", "derived", "holo-hardpoints",
                         "placement_report.json")


def rd(path):
    with io.open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def rj(path):
    return json.loads(rd(path))


def grab(src, pattern, what, path, flags=re.S):
    """Pull one embedded JSON literal out of a page or a generated file.

    A missing block is fatal rather than an empty dict. An enumeration that
    silently reports "0 ships have markers" because a regex stopped matching
    is the SILENT SUCCESS failure this project names in rule 12: it would look
    like a catastrophic finding and it would be a broken reader.
    """
    m = re.search(pattern, src, flags)
    if not m:
        sys.exit("could not read %s out of %s. The enumeration would be wrong "
                 "in a way that looks like a finding. Nothing reported."
                 % (what, os.path.relpath(path, REPO)))
    return json.loads(m.group(1))


SAFE = lambda n: re.sub(r"[^A-Za-z0-9._-]+", "_", n)


def load(paths=None):
    """Every input, read once, with the same joins the build itself uses."""
    p = dict(site=SITE_PAGE, layer=LAYER, models=MODELS_DIR, ships=SHIPS_DIR,
             gen=GEN_DIR, fleet=FLEET, resolution=RESOLUTION)
    p.update(paths or {})

    site_src = rd(p["site"])
    ships = grab(site_src, r"const SHIPS\s*=\s*(\[.*?\]);", "the SHIPS array",
                 p["site"])
    cc = grab(rd(p["layer"]), r"const CC_MODELS = (\{.*?\});", "CC_MODELS",
              p["layer"])
    res = rj(p["resolution"])

    lo = rd(os.path.join(p["gen"], "loadout_data.gen.js"))
    lop = os.path.join(p["gen"], "loadout_data.gen.js")
    bench = grab(lo, r"^const LOADOUT_SHIPS=(.*);$", "LOADOUT_SHIPS", lop, re.M)
    hp_names = grab(lo, r"^const LOADOUT_HP=(.*);$", "LOADOUT_HP", lop, re.M)
    types = grab(lo, r"^const LOADOUT_TYPES=(.*);$", "LOADOUT_TYPES", lop, re.M)

    mark = grab(rd(os.path.join(p["gen"], "loadout_marker.gen.js")),
                r"LOADOUT_MARK=(\{.*\});", "LOADOUT_MARK", p["gen"])
    model = grab(rd(os.path.join(p["gen"], "loadout_model.gen.js")),
                 r"LOADOUT_MODEL=(\{.*?\});\n", "LOADOUT_MODEL", p["gen"])

    have = set()
    if os.path.isdir(p["models"]):
        have = {f for f in os.listdir(p["models"]) if f.endswith(".glb")}

    folders = {}
    if os.path.isdir(p["ships"]):
        for d in sorted(os.listdir(p["ships"])):
            fp = os.path.join(p["ships"], d)
            if not os.path.isdir(fp) or d.startswith("_"):
                continue
            folders[d] = sorted(os.listdir(fp))

    fleet = rj(p["fleet"]) if os.path.exists(p["fleet"]) else {}
    return dict(ships=ships, cc=cc, res=res, bench=bench, hp_names=hp_names,
                types=types, mark=mark, model=model, have=have,
                folders=folders, fleet=fleet)


WEAPONY = {"WeaponGun", "Turret", "MissileLauncher", "WeaponDefensive",
           "WeaponMining", "BombLauncher", "SalvageHead", "TractorBeam",
           "EMP", "Missile", "Bomb"}


def weapon_ports(rec, hp_names, types):
    """The ports a marker COULD be placed on - the same filter build_deploy
    applies. Counting every port instead would make the W3 coverage ratio
    flatter than the truth and hide the thin hulls."""
    out = []
    for sl in (rec or {}).get("slots", []):
        if (types.get(sl["t"]) or {}).get("t") in WEAPONY:
            out.append(hp_names[sl["h"]])
    return out


def analyse(D):
    ships, res = D["ships"], D["res"]
    stem_by_site = {r["site"]: r["file"].rsplit(".", 1)[0].lower()
                    for r in res.get("matched", [])}
    nogame = {r["site"]: r for r in res.get("no_game_file", [])}
    bench_by_stem = {k.lower(): k for k in D["bench"]}
    fleet_by_model = {(v or {}).get("model"): (k, v)
                      for k, v in D["fleet"].items() if (v or {}).get("model")}

    rows = []
    for s in ships:
        sid = str(s["id"])
        name = s["name"]
        stem = stem_by_site.get(name)
        cls = bench_by_stem.get(stem) if stem else None
        folder = D["cc"].get(sid)
        glb = SAFE(folder) + ".glb" if folder else None
        on_disk = bool(glb and glb in D["have"])
        marks = D["mark"].get(cls) if cls else None
        rec = D["bench"].get(cls) if cls else None
        ports = weapon_ports(rec, D["hp_names"], D["types"]) if rec else []
        fleet_name, fleet_rec = fleet_by_model.get(glb, (None, None))

        # WHY, in the order the joins actually fail. The first failing join is
        # the cause; anything after it is a consequence and must not be
        # reported as a second finding.
        if not stem:
            why = "no game file" if name in nogame else "unresolved name"
        elif not cls:
            why = "game file resolved, no bench record"
        elif not folder:
            why = "no model folder mapped (CC_MODELS)"
        elif not on_disk:
            why = "model folder mapped, no .glb built"
        else:
            why = None

        rows.append(dict(
            id=sid, name=name, mfr=s.get("manufacturer"),
            stem=stem, cls=cls, folder=folder, glb=glb if on_disk else None,
            page=bool(cls), model=on_disk,
            rsi=bool(not cls and s.get("pledge_url")),
            plain=bool(not cls and not s.get("pledge_url")),
            markers=len(marks) if marks else 0,
            ports=len(ports),
            fleet=fleet_name,
            why=why))
    return rows


def reverse(D, rows):
    """Direction B - a model on disk that no site row can reach."""
    used = {r["glb"] for r in rows if r["glb"]}
    orphan = sorted(f for f in D["have"] if f not in used)
    # And the raw library, which is a bigger set than what got built.
    built_folders = {r["folder"] for r in rows if r["folder"]}
    unbuilt = sorted(d for d, files in D["folders"].items()
                     if d not in built_folders
                     and any(f.endswith(".glb") for f in files))
    return orphan, unbuilt


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--site", default=SITE_PAGE)
    ap.add_argument("--fleet", default=FLEET)
    a = ap.parse_args(argv)

    D = load({"site": a.site, "fleet": a.fleet})
    rows = analyse(D)
    orphan, unbuilt = reverse(D, rows)

    n = len(rows)
    page = [r for r in rows if r["page"]]
    model = [r for r in rows if r["model"]]
    rsi = [r for r in rows if r["rsi"]]
    plain = [r for r in rows if r["plain"]]
    nomodel = [r for r in rows if not r["model"]]
    # PAGE AND MODEL, both. A row with no page has no ClassName, so it could
    # not have had markers either - counting it here would attribute one
    # cause's consequence to a second finding.
    pagemodel = [r for r in rows if r["page"] and r["model"]]
    nomark = [r for r in pagemodel if r["markers"] == 0]
    # THE SHARPEST NUMBER IN W4: the model is built and shipped, and the
    # visitor is still sent off-site because the ship has no game file.
    model_no_page = [r for r in rows if r["model"] and not r["page"]]

    print("=" * 74)
    print("E14 - SHIP GAP ENUMERATION.  %d ships in the site list" % n)
    print("=" * 74)
    print()
    print("DIRECTION A - site rows that cannot show a model, and why")
    print("  %3d have a ship page        %3d have a model on that page"
          % (len(page), len(model)))
    print("  %3d fall through to an RSI link   %3d render as a plain name"
          % (len(rsi), len(plain)))
    print()
    by_why = collections.OrderedDict()
    for r in nomodel:
        by_why.setdefault(r["why"], []).append(r)
    for why, group in by_why.items():
        print("  %-38s %3d" % (why, len(group)))
        if not a.quiet:
            for r in sorted(group, key=lambda x: x["name"]):
                tag = "RSI" if r["rsi"] else ("plain" if r["plain"] else "page")
                print("      %-44s %-5s %s" % (r["name"], tag, r["mfr"] or ""))
    print()

    print("DIRECTION B - models with no route from the site")
    print("  %3d built .glb reachable by no site row" % len(orphan))
    if orphan and not a.quiet:
        for f in orphan:
            print("      %s" % f)
    print("  %3d sc-ships folders with a model that was never built"
          % len(unbuilt))
    if unbuilt and not a.quiet:
        for d in unbuilt:
            print("      %s" % d)
    print()

    print("  THE OVERLAP W4 IS ABOUT: %d rows have a model built and shipped"
          % len(model_no_page))
    print("  and STILL send the visitor to RSI, because no game file means no")
    print("  ClassName, which means no ship page and no markers either.")
    if model_no_page and not a.quiet:
        for r in sorted(model_no_page, key=lambda x: x["name"]):
            print("      %-30s %s" % (r["name"], r["glb"]))
    print()

    print("MARKERS - hulls that have a page AND a model but no hardpoints")
    print("  %3d of %d rows with both" % (len(nomark), len(pagemodel)))
    skips = {}
    if os.path.exists(PLACEMENT):
        skips = dict(rj(PLACEMENT).get("skipped") or [])
    for r in sorted(nomark, key=lambda x: x["name"]):
        stem = os.path.splitext(r["glb"])[0] if r["glb"] else ""
        reason = skips.get(stem) or skips.get(r["name"])
        if reason is None:
            reason = ("not in hardpoints_fleet.json and not in the skip list"
                      if not r["fleet"] else "placed but no port name matched")
        print("      %-30s %s" % (r["name"], reason))
    print()

    print("W3 - marker coverage. ports with a marker / weapon ports total")
    withm = [r for r in rows if r["markers"] > 0 and r["ports"]]
    ratios = sorted(withm, key=lambda r: r["markers"] / float(r["ports"]))
    thin = [r for r in ratios if r["markers"] / float(r["ports"]) < 0.25]
    print("  %3d hulls have markers.  %d are under 25%% coverage"
          % (len(withm), len(thin)))
    if withm:
        med = sorted(r["markers"] / float(r["ports"]) for r in withm)
        print("  median coverage %.0f%%   range %.0f%% to %.0f%%"
              % (100 * med[len(med) // 2], 100 * med[0], 100 * med[-1]))
    for r in thin:
        print("      %-30s %3d of %3d   %4.0f%%"
              % (r["name"], r["markers"], r["ports"],
                 100.0 * r["markers"] / r["ports"]))
    print()

    if a.json:
        out = dict(counts=dict(site=n, page=len(page), model=len(model),
                               rsi=len(rsi), plain=len(plain),
                               no_model=len(nomodel), no_markers=len(nomark),
                               orphan_models=len(orphan),
                               unbuilt_folders=len(unbuilt)),
                   rows=rows, orphan_models=orphan,
                   unbuilt_folders=unbuilt)
        with io.open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
        print("wrote %s" % a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
