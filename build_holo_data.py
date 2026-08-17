#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_holo_data.py - hardpoint data for the holo viewer, generated not pasted.

Reads the derived fleet hardpoints and the model library that actually exists,
and emits testing/_src/holo_data.gen.js. Same pattern as build_keybind_modes.py
and build_kb_actions.py: one writer, no second copy of the data.

WHY `unit` AND NOT `pos_model` -- THE DECISION THIS FILE RESTS ON
=================================================================

The fleet dataset carries two positions per mount. `pos_model` is in the
MODEL's own units, and those units are not one thing:

    ~1 unit/metre  (typical)   162 ships   median 0.9747
    normalised / small           4 ships   Starlancer TAC 0.0093 ... 0.0953
    ~100 (centimetres)           1 ship    Asgard 101.16

A 10,000x span. Using `pos_model` would mean the page assuming its decode of a
.glb matches the measurement space the derivation used - and when that
assumption is wrong it is wrong SILENTLY: the markers simply sit somewhere
else, which looks like bad derivation rather than a unit error. This viewer has
already had that bug twice.

`unit` removes the assumption instead of relying on it. It is normalised
against the hull's own longest half-extent, so the page reconstructs a position
from the mesh IN FRONT OF IT rather than from a number somebody measured
elsewhere:

    world position = unit * (longest half-extent of the loaded mesh)

ONE SCALAR, ON EVERY AXIS. This was checked rather than assumed. The
pos_model/unit ratio for the 100i is 8.743, 8.757, 8.743 across x/y/z; for the
Asgard it is 2427.3, 2426.6, 2427.8. Identical per axis, so the normalisation
is a single scalar - the longest half-extent - and NOT a per-axis extent.
Multiplying by a per-axis half-extent would stretch every axis that is not the
longest, which is the one plausible-looking way to get this wrong.

AXIS ORDER IS NOT REMAPPED, DELIBERATELY. `frame` records which model axis is
lateral/up/length, and eight different conventions appear across the fleet. It
is a DESCRIPTION of the model's axes, not an instruction to permute them:
`unit` is already expressed in the model's own axis order, which is the order
three.js will load. Reordering here would break 137 ships to "fix" none.

WHAT THIS SCRIPT WILL NOT DO: GUESS WHICH HULL A HARDPOINT SET BELONGS TO

The fleet dataset resolves the model itself, so no manufacturer stripping or
suffix matching happens any more - the matcher this file used to carry became
unnecessary rather than being fixed. What remains is a check that the named
.glb is genuinely present in _deploy/models/. A ship whose model is missing is
reported in HOLO_UNMATCHED and carries no model, so the page can say what it
cannot show instead of offering an entry that 404s.
"""

import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FLEET = os.path.join(HERE, "data-layer", "derived", "holo-hardpoints",
                     "hardpoints_fleet.json")
MANIFEST = os.path.join(HERE, "data-layer", "derived", "holo-hardpoints",
                        "MANIFEST.json")
MODELS = os.path.join(HERE, "testing", "_deploy", "models")
OUT = os.path.join(HERE, "testing", "_src", "holo_data.gen.js")

# THE BENCH'S OWN OUTPUT, READ AS THE AUTHORITY ON SHIP DPS.
#
# The rule from Sleven: the viewer's number for a ship must EQUAL the loadout
# bench's number for the same ship. Two pages showing different DPS for one hull
# is the kind of contradiction a visitor notices immediately and never forgets.
#
# The cheapest way to guarantee that is not to compute the same thing twice
# carefully - it is to read the number the other page will show. So the ship
# totals below come out of loadout_data.gen.js, and the derived fleet dataset's
# own pilot_dps is used as a CHECK against it rather than as the source. If the
# two ever disagree this script refuses to emit, which is the only way a
# disagreement becomes visible before a visitor finds it.
BENCH = os.path.join(HERE, "testing", "_src", "loadout_data.gen.js")

# The ships recovered by joining a model file to mount data that was sitting
# under a different name. A SEPARATE dataset with its own writer - see
# merge_join below for why the viewer reads two files rather than one being
# rewritten by two programs.
JOIN = os.path.join(HERE, "data-layer", "derived", "holo-hardpoints-join",
                    "hardpoints_join.json")

# Marker positions for ships that share a hull with another ship and disagreed
# with it about where the hardpoints are. An OVERLAY, applied here at read time:
# neither dataset above is rewritten, and both keep their single writer.
ALIGN = os.path.join(HERE, "data-layer", "derived", "holo-hardpoints-align",
                     "alignment_overlay.json")

# The snapshot the bench was built from - the same one, deliberately. A weapon
# DPS read from a different patch than the ship total would be the same
# contradiction one level down.
SNAPSHOT = "20260801T204744Z"
SNAPDIR = os.path.join(HERE, "data-layer", "external-sources", "scunpacked-data",
                       "snapshots", SNAPSHOT)
SHIPS_JSON = os.path.join(SNAPDIR, "ships.json")
ITEMS_JSON = os.path.join(SNAPDIR, "ship-items.json")


def say(line):
    """stdout that survives a ship called tok.yaai.

    The pipeline has been broken four times by cp1252, and one of those was a
    diagnostic script printing a ship name. Xi'an and Banu names are not exotic
    in a Star Citizen dataset - San'tok.yai is in this very file.
    """
    sys.stdout.buffer.write((line + "\n").encode("utf-8", "backslashreplace"))


def norm_name(s):
    """Ship names, reduced to what two datasets can be compared on.

    The fleet dataset keys on the bare name ("100i"); the bench keys on the full
    one ("Origin 100i"). Nothing else about them differs, so the comparison is a
    suffix match on letters and digits - and it is required to be UNIQUE, below,
    because a match that could be two ships is not a match.
    """
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def load_bench():
    """The ship totals the loadout bench shows, read out of its generated file.

    Returns {normalised name: {"n": display, "dps":, "sdps":, "alpha":}}.
    """
    with io.open(BENCH, "r", encoding="utf-8") as fh:
        js = fh.read()
    m = re.search(r"const LOADOUT_SHIPS=(\{.*?\});\n", js, re.S)
    if not m:
        sys.exit("Could not find LOADOUT_SHIPS in %s.\nRefusing to emit ship DPS "
                 "that has not been checked against the bench." % BENCH)
    out = {}
    for rec in json.loads(m.group(1)).values():
        cig = rec.get("cig") or {}
        out.setdefault(norm_name(rec.get("n")), {
            "n": rec.get("n"),
            "dps": cig.get("dps"),
            "sdps": cig.get("sdps"),
            "alpha": cig.get("alpha"),
        })
    return out


def bench_for(name, bench):
    """The bench record for one fleet ship, or None - and never a guess.

    A name that matches two bench ships returns None rather than picking one.
    Silently taking the first would be exactly the kind of near-enough join this
    project keeps finding months later.
    """
    n = norm_name(name)
    hits = [v for k, v in bench.items() if k == n or k.endswith(n)]
    if len(hits) == 1:
        return hits[0]
    return None


def load_port_weapons():
    """Per ship, the guns fitted to each top-level hardpoint port.

    The fleet dataset carries the MOUNT on each hardpoint ("VariPuck S3 Gimbal
    Mount") and the guns only as an unattributed list, so a gun cannot be tied
    to a mount from it alone - there are 14 WeaponGun entries across 1798
    hardpoints. The snapshot's loadout tree does carry the link: every entry
    records `Path`, and Path[0] is the top-level port the fleet dataset keys on.

    Returns {normalised ship name: {port: [{"name":, "dps":, "size":}]}}.
    """
    with io.open(ITEMS_JSON, "r", encoding="utf-8") as fh:
        items = json.load(fh)
    by_ref = {}
    for it in items:
        st = it.get("stdItem") or {}
        w = st.get("Weapon") or {}
        dmg = (w or {}).get("Damage") or {}
        rec = {
            "name": st.get("Name") or it.get("name"),
            # SUSTAINED, matching the bench's own weapon cards exactly. DpsTotal
            # is the burst figure and flatters anything with a small magazine -
            # the trap the aggregation finding documents.
            "dps": dmg.get("Sustained") if isinstance(dmg, dict) else None,
            "size": it.get("size"),
        }
        for key in (it.get("className"), it.get("ClassName"), it.get("reference"),
                    it.get("UUID")):
            if key:
                by_ref[str(key).lower()] = rec

    with io.open(SHIPS_JSON, "r", encoding="utf-8") as fh:
        ships = json.load(fh)

    out = {}
    for s in ships:
        ports = {}

        def walk(node):
            for e in node or []:
                if not isinstance(e, dict):
                    continue
                typ = e.get("Type") or ""
                if typ.startswith("WeaponGun"):
                    path = e.get("Path") or []
                    port = path[0] if path else e.get("HardpointName")
                    ref = None
                    for key in (e.get("ClassName"), e.get("UUID")):
                        if key and str(key).lower() in by_ref:
                            ref = by_ref[str(key).lower()]
                            break
                    if port and ref and ref.get("dps") is not None:
                        ports.setdefault(port, []).append(ref)
                walk(e.get("Loadout"))

        walk(s.get("Loadout"))
        if ports:
            out.setdefault(norm_name(s.get("Name")), ports)
    return out


def port_weapons_for(name, table):
    n = norm_name(name)
    hits = [v for k, v in table.items() if k == n or k.endswith(n)]
    if len(hits) == 1:
        return hits[0]
    return {}


def guns_for_port(gun_by_port, port):
    """The guns on one port, trimmed for the wire. [] when there are none."""
    out = []
    for g in gun_by_port.get(port or "", []):
        out.append({"name": g.get("name"), "dps": round(float(g["dps"]), 1),
                    "size": g.get("size")})
    return out


def merge_join(fleet):
    """Add the ships recovered by build_hardpoint_join.py.

    TWO DATASETS, ONE VIEWER, AND NO SECOND WRITER. hardpoints_fleet.json keeps
    its single writer (place_fleet.py); the recovered ships live in their own
    file and are merged here, at read time, where a collision is visible.

    The key a recovered ship gets says what it IS:

      - resolved BY MAPPING - the model is that ship under a shorter file name,
        so it takes the ship's real name: Aurora_CL -> "Aurora Mk I CL".
      - resolved BY RULE - the model is an EDITION or a paint of another hull,
        so it keeps its own identity: "Caterpillar Best In Show Edition 2949",
        borrowing the base hull's hardpoints without pretending to be it.

    A key that already exists is REFUSED rather than overwritten. Silently
    replacing a placed ship with a recovered one would be the second-writer
    defect wearing a different hat.
    """
    if not os.path.exists(JOIN):
        return fleet, {"merged": 0, "alias": {}, "note": "no join dataset present"}
    with io.open(JOIN, "r", encoding="utf-8") as fh:
        joined = json.load(fh)

    merged, collisions, alias = 0, [], {}
    for stem, rec in sorted(joined.items()):
        base = rec.get("resolved_from") or stem
        key = base if rec.get("resolved_by") == "mapping" else stem.replace("_", " ")
        if key in fleet:
            collisions.append([stem, key])
            continue
        fleet[key] = rec
        alias[stem] = key
        merged += 1
    if collisions:
        for stem, key in collisions:
            say("  COLLISION: %s would overwrite %r - refused" % (stem, key))
        sys.exit("%d recovered ship(s) collide with ships already placed. Refusing "
                 "to emit: one of the two is wrong about which hull it is, and "
                 "picking silently is how a Gladius ends up wearing somebody "
                 "else's hardpoints." % len(collisions))
    return fleet, {"merged": merged, "alias": alias}


def apply_alignment(fleet, alias):
    """Move markers onto the positions their own hull already uses elsewhere.

    THE OVERLAY IS APPLIED, NOT MERGED. Every entry names a ship and a port that
    exists, and a port it does not recognise is a hard failure rather than a
    silent skip: an overlay that quietly matched nothing would leave the pages
    disagreeing while reporting that it had fixed them.
    """
    if not os.path.exists(ALIGN):
        return fleet, {"moved": 0, "note": "no alignment overlay present"}
    with io.open(ALIGN, "r", encoding="utf-8") as fh:
        overlay = json.load(fh)

    moved, unknown = 0, []
    for key, ports in overlay.items():
        # A RECOVERED SHIP IS KEYED BY ITS MODEL STEM IN THE OVERLAY and by the
        # name it was merged under here - "M2_Hercules" against "M2 Hercules
        # Starlifter". The alias map from merge_join is the only thing that
        # knows both, so it does the translating rather than a second guess at
        # the naming rule.
        rec = fleet.get(key) or fleet.get(alias.get(key, ""))
        if rec is None:
            unknown.append(key)
            continue
        by_port = {h["port"]: h for h in rec["hardpoints"]}
        for port, pos in ports.items():
            h = by_port.get(port)
            if h is None:
                unknown.append("%s / %s" % (key, port))
                continue
            h["unit"] = pos["unit"]
            h["pos_model"] = pos["pos_model"]
            moved += 1
    if unknown:
        for u in unknown[:20]:
            say("  OVERLAY names something that is not here: %s" % u)
        sys.exit("%d overlay entr(ies) matched nothing. Refusing to emit: an "
                 "overlay that silently matches nothing reports a fix it did not "
                 "make." % len(unknown))
    return fleet, {"moved": moved}


def main():
    with io.open(FLEET, "r", encoding="utf-8") as fh:
        fleet = json.load(fh)
    fleet, join_note = merge_join(fleet)
    fleet, align_note = apply_alignment(fleet, join_note.get("alias") or {})

    bench = load_bench()
    guns = load_port_weapons()
    unnamed = []

    available = {os.path.basename(p)
                 for p in glob.glob(os.path.join(MODELS, "*.glb"))}
    if not available:
        sys.exit("NO MODELS FOUND in %s. Refusing to emit a dataset that would\n"
                 "report every ship as unmatched - that is a missing library,\n"
                 "not 167 missing ships." % MODELS)

    ships, unmatched, no_points = {}, [], []
    for name, rec in fleet.items():
        model = rec.get("model") or ""
        points = rec.get("hardpoints") or []
        if model not in available:
            unmatched.append((name, model, len(points)))
            continue
        if not points:
            # Kept and displayable - a hull with no mounts in the derivation is
            # a fact about the ship, and the viewer already says so in words.
            no_points.append(name)
        # A RECOVERED EDITION LOOKS UP ITS BASE HULL'S NUMBERS.
        #
        # "Caterpillar Best In Show Edition 2949" is not a row on the bench and
        # never will be; the hull it is an edition of is. resolved_from carries
        # that name, and using it is the same claim the hardpoints already make -
        # same hull, same fit, same figures.
        lookup = rec.get("resolved_from") or name
        b = bench_for(lookup, bench)
        if b is None:
            unnamed.append("%s (looked up as %r)" % (name, lookup))
        gun_by_port = port_weapons_for(name, guns)

        ships[name] = {
            "model": model,
            "display": name,
            # WHAT THE PILOT CAN FIRE, taken from the bench's own output.
            #
            # null is a real answer and is NOT zero. 24 of these 167 hulls have
            # no pilot-fired weapon at all - Hammerhead, Caterpillar, Retaliator,
            # the Cyclones - and CIG publishes no figure for them. Zero would
            # read as "this ship does no damage", which is a claim the data never
            # made; the page says the number is not available instead.
            "dps": (b or {}).get("dps"),
            "sdps": (b or {}).get("sdps"),
            "alpha": (b or {}).get("alpha"),
            # ONLY WHAT THE PAGE RENDERS. The full record - pos_model, port,
            # type, dps, alpha, manufacturer, the frame - stays in
            # hardpoints_fleet.json, which is the dataset. Copying all of it
            # here would put 1798 mounts' worth of unrendered fields on the
            # wire and make this file a second home for data that has one.
            "points": [{
                "where": p.get("where"),
                "kind": p.get("kind"),
                "pilot": p.get("pilot"),
                "unit": p.get("unit"),
                "items": [{"name": it.get("name"), "size": it.get("size")}
                          for it in (p.get("items") or [])],
                # THE GUNS FITTED TO THIS MOUNT, from the same snapshot the
                # bench reads. Absent - not empty, not zero - when this port
                # holds no gun, which is most of them: a countermeasure launcher
                # and a missile rack are hardpoints too.
                "guns": guns_for_port(gun_by_port, p.get("port")),
            } for p in points],
        }

    # ---- THE TWO PAGES MUST AGREE, AND THAT IS CHECKED HERE ---------------
    #
    # The viewer's DPS for a ship comes from the bench's output. The derived
    # fleet dataset carries its own pilot_dps, from ship_specs.json - a
    # DIFFERENT read of the same game data. So the two are compared, and a
    # disagreement stops the build.
    #
    # This is the whole reason the check exists rather than a note saying they
    # should match: two pages disagreeing about one ship's damage is the kind of
    # contradiction a visitor notices immediately and never forgets, and it
    # would be invisible from either page alone.
    if unnamed:
        sys.exit("%d ship(s) could not be matched to a bench record: %s\n"
                 "Refusing to emit DPS that has not been checked against the "
                 "page it must agree with. A name that matches two bench ships "
                 "counts as unmatched - picking one would be a guess."
                 % (len(unnamed), ", ".join(sorted(unnamed)[:12])))

    disagreed = []
    for name, rec in fleet.items():
        if name not in ships:
            continue
        mine = ships[name]["dps"]
        theirs = rec.get("pilot_dps")
        if mine is None and theirs is None:
            continue
        if mine is None or theirs is None or abs(float(mine) - float(theirs)) > 0.51:
            disagreed.append((name, mine, theirs))
    if disagreed:
        for n, a, b_ in disagreed[:20]:
            say("  DISAGREEMENT %-28s bench=%r derived=%r" % (n, a, b_))
        sys.exit("%d ship(s) have a different pilot DPS in the bench and in the "
                 "derived fleet dataset.\nRefusing to emit. One of the two is "
                 "wrong and the viewer must not pick a side silently."
                 % len(disagreed))

    # Every emitted point must have a usable `unit`, or the page would place it
    # at the origin and it would read as a mount inside the cockpit. Checked
    # rather than trusted, because the dataset is generated by another tool.
    bad = []
    for name, s in ships.items():
        for p in s["points"]:
            u = p["unit"]
            if not (isinstance(u, list) and len(u) == 3
                    and all(isinstance(v, (int, float)) for v in u)):
                bad.append((name, p["where"], u))
    if bad:
        for name, where, u in bad[:20]:
            say("  BAD unit: %-28s %-30s %r" % (name, where, u))
        sys.exit("%d hardpoint(s) have no usable `unit`. Refusing to emit a "
                 "dataset\nthat would silently draw them at the ship's centre."
                 % len(bad))

    with io.open(MANIFEST, "r", encoding="utf-8") as fh:
        manifest = json.load(fh)

    out = [
        "/* GENERATED by build_holo_data.py - do not hand edit.",
        "   Source: data-layer/derived/holo-hardpoints/hardpoints_fleet.json",
        "   and the .glb files actually present in _deploy/models/.",
        "",
        "   HOLO_UNMATCHED lists hardpoint sets whose model is not in the",
        "   library. They are carried through DELIBERATELY rather than dropped,",
        "   so the page can say what it cannot show instead of quietly showing",
        "   less. */",
        "",
        "const HOLO_SHIPS=%s;" % json.dumps(ships, separators=(",", ":"),
                                            sort_keys=True, ensure_ascii=False),
        "const HOLO_UNMATCHED=%s;" % json.dumps(
            [{"name": n, "model": m, "count": c} for n, m, c in unmatched],
            separators=(",", ":"), ensure_ascii=False),
        "/* HOW TO PLACE A MARKER. Emitted by the generator so the page never",
        "   has to assume a unit system - the two bugs this viewer has already",
        "   had were both an assumption about units made in the wrong place.",
        "",
        "     'unit'  position is normalised to the hull's longest HALF-extent.",
        "             The page multiplies by that one scalar, measured from the",
        "             mesh it has actually loaded:",
        "",
        "                 world = unit * (max(bbox size) / 2)",
        "",
        "             ONE scalar on every axis, not a per-axis extent - the",
        "             ratio is identical across x/y/z, so a per-axis multiply",
        "             would stretch everything that is not the longest axis.",
        "",
        "   This dataset spans 10,000x in model scale (0.0093 to 101.16 model",
        "   units per metre), which is exactly why the page must not be handed",
        "   a fixed multiplier. Any future dataset states its own convention",
        "   here rather than inheriting this one. */",
        "const HOLO_PLACEMENT=%s;" % json.dumps({"mode": "unit"}),
        "/* Every position in HOLO_SHIPS is DERIVED. CIG's own position field is",
        "   null for all 25,150 ports in ship_specs.json - re-verified on this",
        "   dataset. See FINDING_fixed-hardpoints-derived. */",
        "const HOLO_DERIVED_NOTE=%s;" % json.dumps(
            "Positions are derived from the ship's own geometry and port naming, "
            "not read from the game files. CIG's position field is null for every "
            "mount, so there is nothing authoritative to read. Treat these as "
            "close, not exact."),
        "/* What the DERIVATION itself measured, carried through from the",
        "   dataset's manifest rather than restated here. */",
        "const HOLO_DERIVATION=%s;" % json.dumps(
            {"produced_by": manifest.get("produced_by"),
             "verified": manifest.get("verified", {})},
            separators=(",", ":"), ensure_ascii=False),
        "",
    ]
    with io.open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out))

    total_hp = sum(len(s["points"]) for s in ships.values())
    say("wrote %s  (%.1f KB)"
        % (os.path.relpath(OUT, HERE), os.path.getsize(OUT) / 1024.0))
    say("  displayable: %d ships, %d hardpoints"
        % (len(ships), total_hp))
    say("  alignment overlay: %s" % json.dumps(align_note))

    # THE DPS COVERAGE, COUNTED AND MADE TO SUM.
    #
    # Two numbers that add up to the fleet size is the difference between "most
    # ships have it" and a statement somebody can check. A ship in neither bucket
    # would mean the emit dropped it silently.
    with_dps = sum(1 for s in ships.values() if s.get("dps") is not None)
    without = sum(1 for s in ships.values() if s.get("dps") is None)
    say("  pilot DPS: %d ships carry it, %d say it is not available, %d + %d = %d"
        % (with_dps, without, with_dps, without, with_dps + without))
    if with_dps + without != len(ships):
        sys.exit("The DPS buckets do not sum to the ship count. A ship is in "
                 "neither, which means this report is not describing what was "
                 "emitted.")
    armed = sum(1 for s in ships.values()
                for p in s["points"] if p.get("guns"))
    say("  per-hardpoint: %d mount(s) carry a gun with its own DPS" % armed)
    if no_points:
        say("  %d displayable ship(s) have NO mounts in the derivation: %s"
            % (len(no_points), ", ".join(sorted(no_points)[:8])
               + (" ..." if len(no_points) > 8 else "")))
    for name, model, n in unmatched:
        say("  %-30s -> NO MODEL IN LIBRARY (%r)   %2d hardpoints NOT displayable"
            % (name, model, n))
    say("  unmatched: %d of %d" % (len(unmatched), len(fleet)))


if __name__ == "__main__":
    main()
