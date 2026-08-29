# OWNERS — one writer per artifact, in a form a program can read

    maintained by  C1
    why            rule 14 says: "one writer per artifact. When a second writer
                   is possible, make it impossible rather than discouraged."
                   Until 2026-08-28 the list lived in prose, in a section of
                   `NEXT.md` headed NOT CODE'S. Prose is discouragement.

**On 2026-08-27 at 22:10 and 22:15 Code's drift detection fired on C1's writes
to `testing/_src/cc_viewer.js` and `testing/_src/loadout.src.html`.** Both files
were already C1's, in `NEXT.md` and in `CURRENT-STATE.md`, and had been for
weeks. **Nothing was actually in conflict.** Two sessions were reading two
different prose lists and one of them was reading a list Code's tooling could not
see at all.

That is the whole failure: **ownership was written down in a place programs do
not read.** This file is the place they do.

---

## THE RULE THIS FILE ENFORCES

A path appears **exactly once**. The session named beside it is the only one that
writes it. Anyone else who needs it changed **asks the owner** — through
`inbox/` for Code, through `NEXT.md` for C1 — and does not edit it, not even
"just this once", not even when the edit is obviously right.

**A path that is not in this file has no declared owner.** That is not
permission; it is a gap, and finding one is worth reporting.

---

## C1 — Cowork. The only Cowork session that writes to the repository.

    NEXT.md
    LIVE.md
    OWNERS.md
    testing/_src/loadout.src.html
    testing/_src/cc_viewer.js
    checks/_verify_panel_dismiss.mjs
    checks/_verify_placement_gate.py
    checks/_verify_stage_still.mjs
    checks/_verify_marker_provenance.py
    checks/_verify_marker_note.mjs
    checks/_verify_swap_loop.mjs
    checks/_verify_marker_census.py
    checks/marker_census.json
    checks/_verify_identical_options.mjs
    checks/_verify_marker_spread.py
    decode_cga_nodes.py
    probe_ship_geometry.py
    extract_p4k_entry.py
    build_hardpoint_transforms.py
    build_hardpoint_placement.py
    build_hardpoint_overlay.py
    build_crafting_demand.py
    data-layer/derived/hardpoint-transforms/
    data-layer/derived/hardpoint-placement/
    data-layer/derived/holo-hardpoints/
    data-layer/derived/holo-hardpoints-align/
    data-layer/derived/crafting-demand/

## CODE — Claude Code, on the Windows machine.

    testing/_src/build_deploy.py
    build_find_data.py
    testing/_src/_disc.css
    checks/run_all_controls.py
    checks/sweep_gate.py
    checks/file_checks.py
    scripts/deploy_testing.ps1
    scripts/deploy_live.ps1

**Everything else under `checks/` is Code's by default** except the files named
under C1 above. Code wrote the suite; C1 contributes controls and names them here
when it does.

## A NOTE ON `data-layer/derived/holo-hardpoints/`, CLAIMED 2026-08-29

**It was unowned until Code reported it**, and it is the one directory where
rule 1 was not followed: `loadout_marker.pre-C1-20260828.js` was DELETED from
the working tree rather than moved to `_to_delete/`. Neither session can say
which of them did it. **That is the argument for the claim, not against it** —
an unowned directory is where that happens.

**C1 claims it, with a caveat that has to travel with it:** its main file,
`hardpoints_fleet.json`, has a single writer — `place_fleet.py` — **and that
script is not in this repository.** So C1 owns what happens to the directory
without being able to regenerate its contents. **Nothing in here is deleted;
superseded files move to `_to_delete/` like everything else.**

`docs/PROPOSAL_the-marker-pipeline-is-four-layers-deep-2026-08-27.md` proposes
retiring the file to a named fallback. That decision is Sleven's and is not made.

## SLEVEN — his alone, and not by convention.

    every legal, Fan Kit and trademark decision
    whether and when the site goes live
    attribution text and its placement

**No session edits these. Rule 8.**

---

## WHAT THIS FILE IS NOT

**It is not a lock.** Nothing stops a session writing to a path it does not own;
the filesystem has no idea who anyone is. What this file removes is the excuse —
after it, an unowned write is a decision somebody made against a list they could
have read, not a misunderstanding between two prose documents.

**It does not settle who SHOULD own something.** It records who does. Moving a
path between owners is a decision, it goes in a dated `docs/DECISION_*`, and this
file is edited to match afterwards.

---

## THE CHECK

`checks/_verify_owners.py` holds this file to its own rule: every path exists,
no path is claimed twice, and the prose list in `NEXT.md` agrees with it. If the
two disagree, **this file wins and `NEXT.md` is corrected**, because a program
can read this one.

— C1, 2026-08-28
