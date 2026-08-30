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
    checks/_verify_display_names.py
    checks/_verify_no_agent_traces.py
    checks/_verify_marker_mesh_distance.py
    checks/_dracopos.mjs
    build_loadout_data.py
    build_hardpoint_overlay.py
    testing/_src/_layer.src.html
    testing/_src/keybinds.src.html
    testing/_src/device_engine.js
    testing/_src/kb_overlay.inc.html
    checks/_verify_us_spelling.py
    releases/latest.html
    static/preview.html
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

## A NOTE ON `build_loadout_data.py`, CLAIMED 2026-08-29

**It was unowned.** It writes `loadout_data.gen.js`, which is the ship page's
entire data layer, and neither C1 nor Code was named against it. That is the
second ownership gap found this week by the same route: going to change a file
and finding nobody's name on it.

**C1 claims it** because the ship page and its data are already C1's, and a
generator whose only consumer is C1's page should not have a different writer.
**Code is the one to say if that is wrong** - it is claimed, not seized, and
this note is the notification.

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

## A NOTE ON THE PAGE-COPY FILES, CLAIMED 2026-08-30 — AND ON WHAT I GOT WRONG

    testing/_src/_layer.src.html        injected into every page
    testing/_src/keybinds.src.html      the keybind tester
    testing/_src/device_engine.js       the device panel, one writer
    testing/_src/kb_overlay.inc.html    the overlay's copy of the same panel

**All four were unowned. That is the fourth gap found the same way in three
days: going to change a file and finding nobody's name on it.** Three of the
four were found by C1, which says the gap is systemic, not a run of bad luck.

**AND THE FIRST VERSION OF THIS NOTE, WRITTEN AN HOUR EARLIER, WAS WRONG.** It
said `_layer.src.html` and `keybinds.src.html` *"share code by copy"* and that
*"today's US-spelling pass had to be applied twice, by hand."* Both halves are
false and the truth is better: **`device_engine.js` is the single writer of the
device panel, and `inject_engine.py` copies it into both hosts on every build,
between fixed boundary markers, with a `node --check` gate that refuses to
inject code that does not parse.** Rule 14 was already satisfied here before
anyone claimed anything. I wrote a finding about duplication into a file whose
job is to record ownership, without reading the script that manages it.

**HOW IT SURFACED, WHICH IS THE ARGUMENT FOR THE CLAIM.** The hand edit to the
two hosts was silently reverted by a build - correctly, because the hosts are
generated in that region and the master had not changed. Nothing warned; the
edit simply stopped existing. **An unowned generated region is where that
happens**, and it is why the master is claimed here rather than the hosts alone.

**`testing/_src/inject_engine.py` IS STILL UNOWNED AND IS NOT CLAIMED HERE.**
It is build tooling, `build_deploy.py` calls it, and `build_deploy.py` is
Code's. **It is reported, not taken** - the natural owner is Code and that is
Code's call to make.

**Code is the one to say if any of these claims is wrong.** They are claimed,
not seized, and this note is the notification.

## A NOTE ON THE LIVE SITE'S TWO FILES, CLAIMED 2026-08-30 — AND THEY DISAGREE

    static/preview.html      286,228 bytes    the master, per CLAUDE.md
    releases/latest.html     205,362 bytes    the mirror, and the one PUBLISHED

**`CLAUDE.md` says the live site is served from `static/preview.html` mirrored
into `releases/latest.html`, by manual Netlify Drop.** The two are 80,866 bytes
and 33 diff lines apart. **The mirror is what the public gets, so on the live
site the master is not the master.**

They differ in exactly two places, and one of them is not a session's to settle:

    fonts    the MASTER embeds four faces as base64 and calls nothing.
             The MIRROR - the live file - @imports them from
             fonts.googleapis.com, so every visitor's browser contacts Google.
    legal    the MASTER carries an extra paragraph the live file does not:
             "This site is not endorsed by or affiliated with the Cloud
             Imperium or Roberts Space Industries group of companies..."

**THE LEGAL DIFFERENCE IS RULE 8 AND IS NOT TOUCHED.** The live file is not
bare - it carries its own unofficial-site disclaimer and a trademark bar. What
it does not carry is the master's SECOND paragraph. **Whether that paragraph
belongs on the public site is Sleven's decision alone**, and no session
reconciles it.

**BOTH FILES ARE CLAIMED SO THAT THE DIVERGENCE STOPS BEING ACCIDENTAL.** The
2026-08-30 patch-banner correction was applied to BOTH, identically, and the
diff is still 33 lines — deliberately. **Syncing them is a decision, not a
tidy-up, and it was not made here.**

**They were unowned, which is the fifth gap in three days.**

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
