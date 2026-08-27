# ORDER — The queue. Work this top to bottom.

**C1, 2026-08-27 12:52 local. For Code. This supersedes nothing; it sequences
what is already ordered and adds what is not.**

**Sleven:** *"I keep just letting Code pick his work because you're not giving
me stuff for him."*

That is on me. Code has been choosing well — M4 beat its brief, the scale fix
came with a control that fails on the real defect, P4e/P4f is the best check
written today — but choosing is not his job and picking from an ambiguous board
costs him time at the start of every unit. **This is the board.**

**Work it in order.** Anything blocked, say so and take the next one. Report
before starting anything that writes, per rule 5.

---

## Q1 — DEPLOY. Nothing else until this is up.

The payload at `testing/_deploy` is built and correct and **has not been
uploaded**. Sleven cannot see any of it.

What is sitting in it, unseen:

- **The real hardpoint positions.** 510 markers now sit exactly on CIG's own
  coordinates. Verified in the built `loadout_marker.gen.js`: the Vulture's
  left nose gun reads `-0.20294`, which is the client-overlay value, not the
  derived one it replaced.
- **P1e** — the tab bar dismisses the picker.
- **The scale fix** — all 19 imported models at ratio 1.000.

Run the two browser checks against the built payload first —
`_verify_panel_dismiss.mjs` with all four mutators and
`_verify_settings_revision.mjs` with both. **`--mutate-stagescope` should be
observable now that section 2 can pass; if it still comes back identical to
baseline, say so and hold rather than reporting it as caught.**

Then deploy, and verify on the served origin the way you did last time.

## Q2 — MEASURE THE MARKERS ON THE DEPLOYED PAGE

The 510 number is measured in a generated file, not in a browser. **A marker
that is correct in the data and invisible on the page is not fixed.**

On the deployed site, on the **Aegis Gladius** — named because its four wing
mounts are the clearest test in the fleet — read back the rendered marker
positions and assert they match `alignment_overlay_client.json`.

**The control:** the same assertion must FAIL when the build runs with
`alignment_overlay_client.json` renamed away. That file being absent is the
documented revert, so this control is free and it proves the check is looking
at the overlay rather than at coincidence.

## Q3 — REGENERATE THE OVERLAY AFTER YOUR RESCALE, AND USE IT AS A CHECK

    python3 build_hardpoint_overlay.py

Seconds, no p4k access. `pos_model` follows the new model scales.

**The `unit` values must come out IDENTICAL.** Position and normaliser both
derive from the same bounding box, so a rescale cancels. **If a hull's `unit`
values move, something scaled the geometry and the box by different amounts** —
that is a free check on your scale fix and it costs one diff.

## Q4 — THE DEPLOY GATE, per my ruling of 11:57

Browser checks gate the **deploy**, not the build. `deploy_testing.ps1` runs
`_verify_panel_dismiss.mjs` and `_verify_settings_revision.mjs` against
`testing/_deploy` and refuses to upload if either is red.

**With an override that has to be typed and that prints what it is ignoring.**
Sleven overrode a red check this morning and was right to. That has to stay
possible and it has to stay loud. Flag shape is yours; the printing is not
optional.

## Q5 — `deploy_testing.ps1:304`, per my ruling of 11:57

Replace the `cc-ship::after` marker with `id="cc-panel"`. The old marker is in
no build and has not been for some time, so item 2 of the checklist has been
unfailable — and an instruction that always fails teaches the operator to skip
it. Leave `kb_overlay.inc.html` alone; that orphan is a separate question.

## Q6 — `build_holo_data.py` HAS NOT RUN SINCE 17 AUGUST

It exits in `merge_join`:

    7 recovered ship(s) collide with ships already placed
    ATLS, C8R_Pisces, Khartu-Al, M50, MDC, ROC, ROC-DS

**Not from your M5 import** — `hardpoints_fleet.json` predates it by ten hours.
`holo_data.gen.js` is stamped 08-17, so the holo page has been served from a
ten-day-old generation and nobody noticed, because `build_deploy.py` does not
call this generator.

**Report what the collision actually is before fixing it.** Two records claiming
one hull is ambiguous, and the refusal is correct behaviour; the question is
which of the two is wrong, and that may be a Sleven call rather than yours.

## Q7 — THE DISCLOSURE BAR

`ORDER_the-disclosure-bar-2026-08-27.md`, D1 and D2. Ordered this morning,
unstarted. Sleven approved the pattern and asked for it site-wide.

**Now larger than when it was written.** 19 models arrived today from a third
party, and every one needs its provenance visible under
`RULING_community-practice-is-the-standard-2026-08-22.md`. **And the hardpoints
changed meaning:** a marker that was derived from a mount name and a marker that
is CIG's own transform are not the same claim, and the page must not present
them as one. `placed_from` is on every hardpoint record now — `client` where the
position is CIG's. Use it.

## Q8 — THE ROADMAP WATCHER, R0 FIRST

`AMENDS_roadmap-watcher-board-1-is-wrong-2026-08-27.md`. R0 is find the real
board; the rest is blocked behind it and R0 is cheap.

---

## NOT YOURS — so you do not pick them up

    testing/_src/loadout.src.html          C1
    testing/_src/cc_viewer.js              C1
    checks/_verify_panel_dismiss.mjs       C1
    decode_cga_nodes.py                    C1
    probe_ship_geometry.py                 C1
    extract_p4k_entry.py                   C1
    build_hardpoint_transforms.py          C1
    build_hardpoint_placement.py           C1
    build_hardpoint_overlay.py             C1
    data-layer/derived/hardpoint-*         C1
    alignment_overlay_client.json          C1

`testing/_src/build_deploy.py` is **YOURS**. I added one block to it at 12:47
and handed it straight back; move or rewrite that block as you see fit.

---

*C1, 2026-08-27.*
