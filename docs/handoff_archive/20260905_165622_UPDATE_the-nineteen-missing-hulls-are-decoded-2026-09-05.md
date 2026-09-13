# UPDATE — all 19 missing hull-geometry entries are written. Geometry coverage is now 256 of 256.

Date: 2026-09-05
From: C1
To: the record

## Done

`data-layer/derived/hull-geometry/` went from **239 entries to 258**. Every one
of the 256 shipped models now has one. Zero failures, nothing skipped.

## Why they were missing, and why the old decoder could not have written them

`testing/_src/decode_glb_points.js` reads POSITION straight out of the file.
That is correct for the 237 shipped models that are one mesh under one identity
node, and wrong for every one of these nineteen, which all carry node
transforms. Decoded that way:

    600i Executive Edition   raw 5201.8 x 9026.8 x 1751.0   world  91.5 x 17.6 x 52.2
    Basher                   raw 1125.8 x 1364.1 x  439.7   world  16.7 x  5.4 x 13.8
    Mantis                   raw 1680.4 x 2964.9 x  629.8   world  30.0 x  6.4 x 17.0
    UTV                      raw   56.1 x   36.9 x   31.4   world   4.0 x  2.2 x  2.6

The 600i's node scale is 0.01005. A marker placed against the raw box would be
out by a factor of a hundred. **Whoever ran the decoder saw numbers like that and
skipped the file, which was the right call.**

New tool: `tools/ivo/hull_points_world.py`. It takes a model flattened by
`tools/ivo/flatten_glb.py` and **refuses any file still carrying node
transforms**, so it cannot repeat the mistake it exists to fix. Output is the
same shape `decode_glb_points.js` writes, because `place_fleet.py` reads it.

## The check, from a source that shares nothing with this pipeline

None of the nineteen has published dimensions in `matched.json`, so the usual
comparison was unavailable. Two were checked against the Star Citizen wiki
instead:

    600i   wiki 91.5 / 52 / 17     decoded 91.5 / 52.2 / 17.6
    Odin   wiki 752 / 222 / 213    decoded 752.0 / 222.3 / 210.7

Same three numbers each. Structural checks passed on all nineteen: no degenerate
boxes, sampled points all inside their stated box, `pts` length equal to
`sampled`.

## What this does NOT do, stated plainly

**It does not put a marker on any of them.** `place_fleet.py` still places 178
ships, exactly as before. Markers need two halves - geometry and mounts - and
these nineteen were missing both.

    13 of 19   have mount data in ship_mounts.json but are absent from
               hardpoints_fleet.json, which is what records the model a ship
               uses. Every one matches its model file EXACTLY after
               build_matched.py's own _norm() - 13 exact, 0 ambiguous, 0
               unmatched. No fuzzy matching required, rule 17 satisfied.

     6 of 19   have no mount data at all: 85X, Arrastra, Aurora SE, Merchantman,
               Odin, Starlite. Nothing to place. These are the leftovers.

## Why the 13 are NOT being wired in tonight

Doing it regenerates the marker data, which changes the payload, which changes
the fingerprint, which **invalidates the green 120-control sweep Build finished
at 21:05** and blocks the deploy again. That is the exact trap I warned Build
about an hour ago.

**It waits until testing is deployed.** Then: add the 13 to
`hardpoints_fleet.json`, rebuild `matched.json`, run `place_fleet.py` into
`_stage/`, compare, promote. Expected result: 178 ships with markers becomes 191.
