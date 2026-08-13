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
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FLEET = os.path.join(HERE, "data-layer", "derived", "holo-hardpoints",
                     "hardpoints_fleet.json")
MANIFEST = os.path.join(HERE, "data-layer", "derived", "holo-hardpoints",
                        "MANIFEST.json")
MODELS = os.path.join(HERE, "testing", "_deploy", "models")
OUT = os.path.join(HERE, "testing", "_src", "holo_data.gen.js")


def say(line):
    """stdout that survives a ship called tok.yaai.

    The pipeline has been broken four times by cp1252, and one of those was a
    diagnostic script printing a ship name. Xi'an and Banu names are not exotic
    in a Star Citizen dataset - San'tok.yai is in this very file.
    """
    sys.stdout.buffer.write((line + "\n").encode("utf-8", "backslashreplace"))


def main():
    with io.open(FLEET, "r", encoding="utf-8") as fh:
        fleet = json.load(fh)

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
        ships[name] = {
            "model": model,
            "display": name,
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
            } for p in points],
        }

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
