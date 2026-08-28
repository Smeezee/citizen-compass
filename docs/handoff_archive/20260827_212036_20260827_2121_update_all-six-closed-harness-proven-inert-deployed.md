# Update — All six closed. The harness change is measured inert across 19 controls, and it is deployed.

**2026-08-27 21:21 local · Code (background session)** — closing out
*"suppress the duplicates, then run the remaining six"*.
Version `6c31ef0c-bf32-48e9-acb3-0bffcb294245`.

## The harness change, measured rather than argued

I said the deferred-timer change was designed to be inert unless a control calls
`flushTimers()`. **Designed to be is not measured to be**, so I ran every control
that imports `checks/_loadout_harness.mjs`:

    19 ok, 0 failed, 1 skipped (_verify_picker_deployed.mjs - network, opt-in)

    column_split · damage_readout · flight_blades · inline_picker ·
    label_cold_start · label_threshold · label_tracking · labels · look_panel ·
    marker_absence · marker_coverage · marker_response · palette ·
    panel_findable · part_rows · ship_page · sorts · spin_default · stage_panel

## Built and deployed

    gate passed: _verify_holo_placement.py (checks) and (self-proof)
    inline JS parses: _layer.src.html (13 blocks), keybinds.src.html (4 blocks)
    12 marker(s) gave up a position shared with a lower PortId
    disclosure CSS: ... index.html, keybinds.html, loadout.html, find.html
    deploy guard: safe to deploy

4 browser checks GREEN, **2 files uploaded** - `loadout.html` this time as well
as the markers, which is the theme tokens and the `setSel` refactor reaching the
page. Served check: Drake Buccaneer 9 dots, 9 visible, model loaded.
`_verify_deployed_links.mjs` SWEEP CLEAN with its canary.

## One number moved that is not mine

    client hardpoint overlay: 1720 -> 1693 port(s) moved onto CIG positions
    matched no weapon port:   3927 -> 3609

**C1 rewrote the client overlay at 21:10:48**, between my last deploy and this
build. Fewer ports are moved by the overlay and far more of them now match a
weapon port, which reads as the overlay getting more selective rather than
smaller. Recorded because a number changing under a deploy should never be
found later in a diff - it is C1's change, not the suppression's. Hull markers
are unchanged at **6,412 on 271 hulls**.

## THE SWEEP'S 14, FINAL

    _verify_deploy_guards.py        40/3  -> 56/0     me
    _verify_deploy_drift.py         11/1  -> 12/0     me
    _verify_hardpoint_alignment.py  FAIL  -> exit 0   me - and 4b ran for the first time ever
    _verify_hardpoint_join.py       FAIL  -> exit 0   me
    _verify_broken_checker_e2e.py   11/1  -> 10/0     me - and two vacuous passes closed
    _verify_model_resolution.py     22/1  -> 23/0     me
    _verify_g3_matcher_delta.py      8/1  -> 10/0     me
    _verify_dim.mjs                 42/1  -> 43/0     me
    _verify_ship_page.mjs          241/1  -> 242/0    me
    _verify_stage_panel.mjs         51/1  -> 54/0     me
    _verify_rule16_labels.py        closed by C1
    _verify_ship_gaps.py            closed by C1
    _verify_placer_candidates.py    C1: P1's output, not the overlay - unclaimed
    _verify_child_markers.py        BLOCKED, below

**Twelve of fourteen closed. Not one was a regression in shipped behaviour** -
they were stale expectations, a fixture that predated a gate, an env var nobody
set, a harness that discarded deferred work, and two genuine page defects the
controls were right about (two theme tokens that never dimmed, three places
building one selection object).

## Still blocked, and it is the same blocker

`_verify_child_markers.py`. The coincident-marker half is closed - **section 3
is green, 0 markers on top of another.** What remains is the baseline: nobody
has said the Retaliator's new mirrored quad is RIGHT rather than tidier, and
re-taking the snapshot now bakes those four in. **One word and it is done in
the same sitting.**

## Also outstanding, from earlier

`docs/FINDING_the-live-deploy-script-has-neither-gate-...` - `deploy_live.ps1`
still has neither the build-receipt gate nor the browser-check gate. Waiting on
a go-ahead, not on me.

Nothing committed, nothing pushed, live site untouched.
