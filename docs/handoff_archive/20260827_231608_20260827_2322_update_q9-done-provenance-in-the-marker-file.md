# Update — Q9 done. Every marker carries where it came from, and the counter caught its own arithmetic being 12 out.

**2026-08-27 23:22 local · Code (background session)** — Sleven: *"start working
then, and anything else you have"*. Version `00640ab7-229a-4009-95e1-68a2ccf16d88`.

## The shape, which was mine to choose

A fifth element on every entry: `[PortId, x, y, z, from]`.

    cig   CIG published a transform for this port and it is used unchanged
    est   derived from the mount name and the hull box, because no decoded
          transform exists for this port
    anc   taken from the mount this port sits on, plus a ring offset so
          siblings do not stack

**`anc` even when the ancestor was `cig`**, and that is the decision worth
stating. An inherited dot's position is the ancestor's plus an offset, so it is
NOT a coordinate CIG published for that port and must not claim to be. What it
honestly is, is "taken from the mount it sits on".

**Additive, so nothing had to change to read it.** Every consumer in the repo
indexes `m[0]`..`m[3]` — the page, `_verify_labels`, `_verify_marker_positions`,
`_verify_sorts`. I checked before writing rather than after.

## In the build, and in the SERVED file

    provenance: 1691 from CIG geometry, 448 name-derived, 4261 taken from a
                placed ancestor

    SERVED provenance: {'cig': 1691, 'anc': 4261, 'est': 448}   total 6400
    rows with 5 elements: 6400      rows with 4 or fewer: 0

**1,691 mounts can now be named as CIG's own**, which is the hedge the page had
to make about all 6,400.

## THE COUNTER WAS WRONG AND ITS OWN TOTAL SAID SO

First build reported **1699 + 452 + 4261 = 6412** against **6,400** markers.
Twelve out — and twelve is a number I recognised: the coincident pairs suppressed
after the rows are appended. The tally counted them and the filter then dropped
them.

**A provenance breakdown that does not add up to the marker count is not a
breakdown.** Fixed by decrementing on removal, and the arithmetic now closes:
1691 + 448 + 4261 = 6400 exactly, in the build AND in the served file.

Worth recording because it is the same shape as everything else caught tonight:
the number was plausible, and only the total it had to agree with exposed it.

## Two controls needed a change, and one of them is a real improvement

**`_verify_child_markers.py` compared WHOLE ROWS** to decide whether a marker had
moved. The moment rows gained a fifth element, all eight of the hulls in that
section looked moved — **a format change reported as a fleet regression.**

Narrowed to positions: `sorted(json.dumps(list(r[:4])) for r in rows)`. The
subject of that section is *"these markers did not MOVE"*, and provenance is not
a position.

**It is not blunter for it. `--mutate-move-pinned` nudges a coordinate by
0.00001 and is still caught**, along with the other two mutators and
`--self-test` — all four still exit 1, and the clean run is 16 assertions, 0
failed.

The same file's `--mutate-move-pinned` rebuilt a row as exactly four elements,
which would have silently dropped the new field. It now carries the tail through.

## Everything that reads a marker, re-run

    _verify_child_markers.py    16/0, all 4 known-bad inputs still exit 1
    _verify_marker_absence      ok      _verify_marker_positions   ok
    _verify_marker_coverage     ok      _verify_labels             ok
    _verify_marker_response     ok      _verify_stage_panel        ok
    _verify_ship_page           ok      _verify_stage_still        ok

Deployed; `_verify_deployed_links.mjs` SWEEP CLEAN with its canary.

## What Q9's DONE-WHEN still leaves to somebody else

*"…and the ship page can distinguish a CIG-decoded mount from a name-derived
estimate."* **It can now — the field is there and served.** Rewording the
provenance note to USE it is N9's subject and lives in `loadout.src.html`, which
`NEXT.md`'s own NOT CODE'S list assigns to C1 and which C1 has stopped writing to
pending Sleven's rule 14 decision. **I am not going to resolve that contradiction
by editing the file while it is being asked about.**

The data half is done and the page can read it the moment somebody wants to.

Nothing committed since `fee621f`.
