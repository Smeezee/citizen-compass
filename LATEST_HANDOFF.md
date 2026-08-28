# LATEST_HANDOFF.md — Update #784 — 2026-08-27 9:46 PM

---

# CITIZEN COMPASS — LATEST HANDOFF

Copy/paste this whole file into a new AI conversation for instant context. It's regenerated automatically — always the most current snapshot available.

---

## CURRENT STATE (auto)

**Generated:** 2026-08-27 21:46:48 (auto-regenerated every time a file lands in inbox/ or this script runs — don't hand-edit this section)

**Project health score:** 35/100
- Data completeness: 0%
- Viewer progress: 50%
- Documentation: 100%

**Ships:** 2 complete viewers / 4 total (50%)
- Complete: arrow, cutlass-black
- In progress / not started: constellation-aquila, gladius

**Data layers:**
- data-layer: 119492 files (13785.50 MB)

**Scripts:** 52  |  **3D models:** 1179  |  **Docs:** 1339

---

## RECENT UPDATES (append-only, newest first)

### 2026-08-27 21:46:02 — 20260827_2159_update_the-live-dry-run-and-a-clean-round-trip.md

# Update — The live dry run, in full. All gates green, nothing published, and the testing payload came back byte for byte.

**2026-08-27 21:59 local · Code (background session)** — Sleven chose the dry
run. Testing version `bbd2a7d7-7979-4980-8984-7f1e9dec042c`.

## What the live script says with a real LIVE payload in front of it

    === LIVE SITE DEPLOY ===
    build   : last build ok (2026-08-27T21:43:00)
    worker  : citizencompass   (testing is 'citizencompasstesting' - different, as required)
    url     : https://citizencompass.citizencompass-contact.workers.dev
    version : v0.4.0   (from the payload itself, not from a note)
    payload : LIVE - no password gate, no testing stamp
    guard   : _deploy contains only known assets
    check   : _verify_panel_dismiss.mjs ... GREEN
    check   : _verify_settings_revision.mjs ... GREEN
    check   : _verify_disclosure.mjs ... GREEN
    check   : _verify_armour_naming.mjs ... GREEN
    checks  : all browser checks green
    payload : 524 files, 456.7 MB
    models  : 258 .glb files
    largest : Tyilui.glb (17.19 MB)
    auth    : scoped token loaded from .env (length 53, not shown)

    -WhatIf: WOULD PUBLISH THE LIVE SITE.
    -WhatIf:   worker    citizencompass
    -WhatIf:   payload   524 files, 456.7 MB, 258 models
    Nothing was uploaded.

**Both gates I added an hour ago ran on the live path for the first time, on the
real payload, and both passed** - the receipt read and accepted, four browser
checks driven against the very bytes that would have gone out. Two hours ago
this script ran neither.

## Confirmed from the OUTSIDE, which is what the script itself insists on

    https://citizencompass.citizencompass-contact.workers.dev/   ->  HTTP 404

**The worker still does not exist. Nothing was published.** The public site is
exactly as it was.

## The round trip, measured rather than assumed

`--live` rewrites the same directory the testing site publishes, so the risk was
never the dry run - it was leaving the public build sitting in `testing/_deploy`.
I hashed every non-model file before starting and compared after the rebuild:

    files before 266 | now 266 | identical 266
    DIFFERENT: none - the testing payload is byte-for-byte what it was

Redeployed testing to prove the path still works after the round trip:
**"No updated asset files to upload"** - exactly right, because the payload never
actually changed. The served page carries its password gate, and
`_verify_deployed_links.mjs` is SWEEP CLEAN with its canary.

## What this told us that the control could not

`_verify_deploy_guards.py` proves the gates refuse bad input against throwaway
trees. **This is the first time the live script has been driven end to end
against the real 456 MB payload**, and the useful new fact is that it gets all
the way through - the guard, four real browser checks, the file and size
ceilings, the credential load - and stops exactly where it is supposed to.

**The version it reports, `v0.4.0`, it read out of the payload itself.** Worth
saying because a version taken from a note is the kind of thing that is right
until the day it is not.

## Where it leaves going live

One command away, and that command is Sleven's:

    python testing\_src\build_deploy.py --live
    powershell -ExecutionPolicy Bypass -File .\scripts\deploy_live.ps1
    python testing\_src\build_deploy.py          <- put testing back
    powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1

**The first real run CREATES the worker** rather than updating one, since the
name 404s today. That remains his to do, and nothing about tonight changes it.

Probe files moved to `_to_delete/probes-2026-08-27/`, never deleted. Nothing
committed, nothing pushed, live site untouched.

### 2026-08-27 21:42:52 — 20260827_2156_update_dry-run-only-doing-it-now.md

# Update — Sleven chose the dry run. Doing it, and recording what has to come back afterwards.

**2026-08-27 21:56 local · Code (background session)**

    python testing/_src/build_deploy.py --live
    deploy_live.ps1 -WhatIf
    python testing/_src/build_deploy.py
    deploy_testing.ps1

**PUBLIC SITE: untouched. The worker stays 404.**

The step that needs proving is the last two: `--live` rewrites the same
directory the testing site publishes, so the testing payload has to come back
**byte for byte**, not approximately. Hashing every non-model file in
`testing/_deploy` before I start so the restore is a measurement rather than an
assumption.

### 2026-08-27 21:41:00 — 20260827_2154_update_the-live-deploy-refuses-and-the-worker-does-not-exist.md

# Update — I ran it. It refused, correctly, and the live worker returns 404. Stopping to ask before the two steps that would change that.

**2026-08-27 21:54 local · Code (background session)** — Sleven: *"well run it"*.

## I ran it. Here is what it said

    powershell -File .\scripts\deploy_live.ps1 -WhatIf

    === LIVE SITE DEPLOY ===
    build   : last build ok (2026-08-27T21:32:11)
    worker  : citizencompass   (testing is 'citizencompasstesting' - different, as required)
    url     : https://citizencompass.citizencompass-contact.workers.dev
    LIVE DEPLOY ABORTED: THIS PAYLOAD CARRIES THE PRIVATE-PREVIEW PASSWORD GATE.

**The gate I added an hour ago is working**: `build : last build ok` is the new
receipt gate reading the receipt and passing it. What stopped the run is the
payload-identity refusal that has been there since 2026-08-21.

**Nothing was published. The dry run never reached the point of trying.**

## Two facts that stand between here and a live site

**1. `testing/_deploy` is the TESTING payload.** It carries the private-preview
password gate and the `testing 2026-08-28` stamp. Publishing it would lock every
visitor out behind a password they were never given, which from outside reads as
an outage rather than a mistake. The script says so and refuses.

To publish I would first have to run:

    python testing\_src\build_deploy.py --live

That **strips the password gate and the testing stamp**, and it rewrites the
same directory the testing site publishes. Until it is rebuilt without `--live`,
`deploy_testing.ps1` will refuse - deliberately, each script refuses the other's
payload. So it is not one command, it is: build live, publish, rebuild testing,
redeploy testing.

**2. The live worker does not exist.**

    https://citizencompass.citizencompass-contact.workers.dev/   ->  HTTP 404

`deploy_live.ps1`'s own header says only Sleven creates it. A `wrangler deploy`
against a name that does not exist would **create the public site**, which is
the one thing that file reserves to him by name.

## So I have stopped, and this is why rather than an excuse

*"Run it"* cannot execute as given: the script refuses, correctly. Getting past
that needs a step Sleven did not name (`--live`), which disables the testing
deploy until reverted, and a `wrangler deploy` that would **create** the public
site rather than update it.

**This is the only action in this repo that cannot be taken back**, and Sleven's
recorded position at 14:10 today was that the site is not ready. He may well
have changed his mind - that is entirely his to change - but I am not going to
infer it from three words when the cost of being wrong is a public site nobody
meant to publish.

Asking now, with the exact sequence written out, rather than after.

Nothing built, nothing published, nothing committed, live site untouched.

### 2026-08-27 21:39:55 — 20260827_2152_update_asked-to-run-the-live-deploy.md

# Update — Asked to run `deploy_live.ps1` for real. Gathering the facts before touching anything.

**2026-08-27 21:52 local · Code (background session)** — Sleven: *"well run it"*,
straight after I said the script has never been run for real.

This is the one action in this repo that cannot be taken back, so I am writing
down what I check before I do anything, not after.

**Nothing has been published. Nothing has been built. This note is the pause.**

### 2026-08-27 21:38:42 — 20260827_2148_update_the-live-deploy-script-has-both-gates.md

# Update — `deploy_live.ps1` has both gates, and the control that proves them went in with them. 56 -> 83 assertions.

**2026-08-27 21:48 local · Code (background session)** — Sleven: *"add the gates
to deploy_live.ps1"*. The finding from 20:34 is closed.

## What went in

**1. The build receipt gate**, checked first, before the payload identity checks
and long before the browser checks, so a refusal is immediate rather than four
minutes in:

    missing     no build to judge. Allowed, and SAID so rather than assumed.
    ok          the build reached its last statement.
    anything    refused, naming the status and the exit code.
    unreadable  refused. An unreadable receipt is not a passing one.

Override: `-IgnoreFailedBuild`, which prints a banner saying it is publishing to
the PUBLIC SITE from a build that did not succeed.

**2. The browser-check gate**, the same four checks on the same bytes - both
scripts publish `testing\_deploy`, so a check that passed before Sleven reviewed
the testing site is a check against the very payload going public. A missing
check FILE is refused as NOT CHECKED. Override: `-IgnoreRedCheck '<name>'`,
which names one check rather than waving the gate through.

**Both escape hatches came across, and so did the reason they are not `-Force`.**
A gate with no documented way past it gets bypassed by editing the script, and
then the bypass is invisible.

**And the `-File` normalisation came with them.** Under `powershell -File`,
`-IgnoreRedCheck 'a.mjs','b.mjs'` arrives as the single string `"a.mjs,b.mjs"`
and a `-contains` test is false for both names. That defect was found in the
testing script by RUNNING the three paths; it is not repeated here.

## The control went in at the same time, which was the whole point

Section 9 (**the live gates**) and section 10 (**the receipt, on BOTH scripts**).
**56 -> 83 assertions, 0 failed**, `--self-test` still exits 1.

    9.  deploy_live.ps1 REFUSES a missing browser check FILE / names it /
        never said it would publish
        REFUSES a RED check / names it / quotes the LIVE override / never
        said it would publish
        -IgnoreRedCheck publishes past it / says OVERRIDE and PUBLIC SITE /
        reaches the dry run
        but a DIFFERENT check name does not wave the red one through

    10. BOTH scripts REFUSE a failed build / name the exit code / never reach
        the dry run / -IgnoreFailedBuild gets past it, loudly / then reaches it
        BOTH scripts REFUSE an UNREADABLE receipt

**Section 10 covers the testing script too.** Q2's DONE-WHEN was satisfied there
this evening but only ever proven by me typing it at a prompt. It is now
asserted on every run, on both sides.

## Proven by behaviour, including against the gate's own absence

Every assertion drives the REAL script with `-WhatIf` against throwaway trees -
a genuinely absent check file, a check that genuinely exits 1, a planted failed
receipt, a receipt that is not JSON.

And the load-bearing one, because "it refused" is not the same as "the gate is
what refused". I copied the live script with the browser-check block cut out and
ran the same RED-check fixture through both:

    WITHOUT the gate: exit=0   reached the dry run=True
    WITH    the gate: exit=1   reached the dry run=False

**Without it, a red check publishes to the public site and reports success.**
That is the defect the finding described, measured rather than argued - and it
means section 9 would catch the gate being removed again. The probe copy went to
`_to_delete/probes-2026-08-27/`, never deleted.

## One more thing, in the file's own header

The header claimed this script was a mirror of the testing one, *"and every one
of those differences is a refusal"*. That sentence was untrue for a day. It now
lists both gates - **and says the gap existed**, rather than tidying it away:

> THE LAST TWO IN THAT LIST ARRIVED LATE ... for a day the rehearsal ran four
> browser checks and read the build receipt while the performance did neither.

## What I did NOT do

**`deploy_live.ps1` has still never been run for real, and I did not run it.**
Everything above is `-WhatIf` against temp directories with an obviously fake
token. The live worker was never contacted. Only Sleven publishes the public
site.

Nothing committed, nothing pushed, live site untouched.

### 2026-08-27 21:34:29 — 20260827_2140_update_adding-the-gates-to-deploy-live.md

# Update — Sleven: *"add the gates to deploy_live.ps1"*. Starting, with the constraint that matters written down first.

**2026-08-27 21:40 local · Code (background session)** — the go-ahead I asked for
at 22:55 in `docs/FINDING_the-live-deploy-script-has-neither-gate-...`.

## What I am adding

Both blocks, lifted from `deploy_testing.ps1` with their escape hatches:

1. **The build receipt gate** plus `-IgnoreFailedBuild`. Refuses when the last
   build did not succeed, and names the status and the exit code.
2. **The browser-check gate** plus `-IgnoreRedCheck '<name>'`. Refuses a RED
   check and refuses a MISSING check file, and the override names one check
   rather than waving the gate through.

**Every escape hatch comes across with them.** A gate with no documented way past
it gets bypassed by editing the script, and then the bypass is invisible.

## And the control comes with them, in the same sitting

`_verify_deploy_guards.py` asserts these behaviours for the testing script only.
**Adding the gates without extending the control would give the live script a
guard nobody has ever seen fail** - rule 12's untested gate wearing a reassuring
name, which is the exact defect I wrote the finding about. Section 8 gets the
live script alongside the testing one, driven with a missing check, a red check
and a failed receipt.

## What I will NOT do

**I will not run `deploy_live.ps1` for real.** Its own header says it never has
been, the worker may not exist, and only Sleven publishes the public site.
Everything below is `-WhatIf` against throwaway project trees in a temp
directory - nothing uploaded, nothing in the repo touched, an obviously fake
token in the fixture's `.env`.

Nothing committed, nothing pushed, live site untouched.

### 2026-08-27 21:33:36 — 20260827_2135_update_child-markers-rebaselined-and-suppression-made-final.md

# Update — `_verify_child_markers.py` is green: 16 assertions, 0 failed. And it caught my own suppression within the hour.

**2026-08-27 21:35 local · Code (background session)** — Sleven: *"the retaliator
quad is right, re-baseline it"*. Version `bca57a21-70c0-4354-99a4-fcc624941b53`.

## Done, and here is exactly what moved

**The pin.** The old four are kept in the file next to the new four, because a
pin nobody can audit is not a pin:

    was  23 [-0.03755, -0.02334, -0.95564]   now  23 [-0.15708, -0.06014, 0.55639]
         24 [ 0.053,   -0.00648, -0.97809]        24 [-0.17993, -0.06014, 0.55639]
         39 [ 0.01037, -0.0012,  -0.98118]        39 [ 0.15711, -0.06014, 0.55639]
         40 [-0.00836,  0.01415, -0.96836]        40 [ 0.1799,  -0.06014, 0.55639]

The comment records that **the symmetry is evidence, not proof, and is not what
authorised this** - Sleven's word is, quoted in the file.

**The baseline.** `loadout_marker.pre-C1-20260827.js`, taken by re-running the
real build with `CC_NO_INHERIT=1`. The old `pre-C1-20260826` snapshot went to
`_to_delete/child-marker-rebaseline-2026-08-27/`, not overwritten.

**The dangerous step, and how it was checked.** `CC_NO_INHERIT=1` runs the REAL
build, so it overwrote the shipped marker file with the 2,139-marker BEFORE
state. I copied the shipped file aside first and confirmed the normal rebuild
restored it **byte for byte**:

    57e30d97f4c0b45f3ead22028583648edf52b7aecb4b3a70663de3c8178ebb8b   before
    57e30d97f4c0b45f3ead22028583648edf52b7aecb4b3a70663de3c8178ebb8b   after

Derived-data mtimes were read either side. C1 did not write during it, so the
BEFORE and AFTER differ by the inheritance pass and nothing else - which is the
whole point of the snapshot.

## THE CONTROL CAUGHT MY OWN CHANGE, AND IT WAS RIGHT

First run after re-baselining, two failures left:

    no hull changed without having a nested eligible port to inherit from
      got ['C.O. HoverQuad', 'Mirai Pulse LX']

**That is the marker suppression I shipped an hour ago.** I dropped the upper
port of each coincident pair and let the inheritance pass put it back, nudged
0.006 aside - and I said so in the 21:38 note and offered to change it.

The control's objection is the better argument, and it is two arguments:

- **A re-placed TOP-LEVEL port is not an inherited child.** The inheritance pass
  is for a gun inside a turret taking its turret's position. Using it to
  re-place a port that had its own position is a different mechanism wearing the
  same counter.
- **The nudged dot claims a position CIG does not give.** It says "this port is
  six centimetres that way" when two independent sources say the two mounts are
  in one place. Every other marker on that page is CIG's own coordinate or an
  honestly-derived child of one.

**So the suppression is now final: the upper PortId gets no marker at all.** Same
answer this build already gives for an ambiguous name, and the list still
reaches every port.

    hull markers  6412 -> 6400 on 271 hulls      (exactly the 12)
    inherited     4273 -> 4261
    Drake Buccaneer on the served page: 9 dots -> 8

**Sleven: this is the change I said would be one line if you preferred it. I
made it because the control disagreed with the other reading, not because you
asked - say if you would rather have the nudged dot back.**

## Proven it can still fail - all four, on demand

    --mutate-drop-children   exit 1   the Retaliator gained markers: FAIL
    --mutate-stack           exit 1   two markers share a position: FAIL
    --mutate-move-pinned     exit 1   PortId 23 got [-0.15707,...] want [-0.15708,...]
    --self-test              exit 1

`--mutate-move-pinned` is the one that matters here: it nudges by 0.00001 and is
caught **against the NEW pin**, so the re-baselined values are genuinely what is
being defended and not a comment.

## Re-verified after the change

    _verify_deploy_drift.py     12 passed, 0 failed
    _verify_marker_absence.mjs  ok      _verify_marker_coverage.mjs  ok
    _verify_marker_response.mjs ok      _verify_stage_panel.mjs      ok
    _verify_ship_page.mjs       ok

Deployed to testing, 4 browser checks GREEN, deploy guard clean, 1 file uploaded.

## THE SWEEP'S 14 IS NOW 13 CLOSED

The only one left is `_verify_placer_candidates.py`, which C1 says belongs to
`place_fleet.py`'s own output rather than to the overlay - **and place_fleet.py
is not in this repo**, so I cannot close it and will not claim to.

Still outstanding and not mine to decide: `deploy_live.ps1` has neither the
build-receipt gate nor the browser-check gate
(`docs/FINDING_the-live-deploy-script-has-neither-gate-...`).

Nothing committed, nothing pushed, live site untouched.

### 2026-08-27 21:28:16 — 20260827_2131_update_rebaselining-child-markers.md

# Update — Sleven: *"the retaliator quad is right, re-baseline it"*. Starting, and saying what I am about to overwrite before I do.

**2026-08-27 21:31 local · Code (background session)** — the decision that was
blocking `_verify_child_markers.py`.

## Two things have to move, not one

1. **`PINNED`** - four Retaliator coordinates hard-coded in the control as
   "correct before this work". Sleven has now said the new mirrored quad is
   right, so these become the new four.
2. **`BEFORE`** - `data-layer/derived/holo-hardpoints/loadout_marker.pre-C1-20260826.js`,
   the snapshot taken by re-running the real build with `CC_NO_INHERIT=1`. It
   predates the CIG overlay, so today it measures the overlay rather than the
   inheritance pass, which is C1's diagnosis and I agree with it.

## The order, and the risk in it

`CC_NO_INHERIT=1` runs the REAL build, so it overwrites the shipped
`loadout_marker.gen.js` and the whole `_deploy` payload with the BEFORE state.
**A re-baseline that leaves the no-inherit build on disk would ship a page with
4,273 fewer markers.** So:

    1. copy the current shipped marker file aside
    2. move the old baseline into _to_delete/ - not overwritten, rule 1
    3. build with CC_NO_INHERIT=1, capture the BEFORE
    4. rebuild normally and CHECK the marker file is byte-identical to (1)
    5. only then update the control

**And I will record the derived-data mtimes either side.** C1 rewrote the client
overlay at 21:10:48 tonight, mid-deploy. If it moves between my two builds the
BEFORE and AFTER differ by more than the inheritance pass and the snapshot is
worthless - that has to be checked, not hoped.

Nothing committed, nothing pushed, live site untouched.

### 2026-08-27 21:20:36 — 20260827_2121_update_all-six-closed-harness-proven-inert-deployed.md

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

### 2026-08-27 21:18:14 — 20260827_2126_update_the-three-browser-controls-and-a-harness-that-ate-deferred-work.md

# Update — The last three of the six are green, and one of them was the harness lying to every control that uses it.

**2026-08-27 21:26 local · Code (background session)** — the browser half of
*"run the remaining six"*.

## `_verify_dim.mjs` — 42/1 -> 43/43, exit 0

    FAILED: and neither side declares a token the other does not  css 58 vs engine 56

Named the two, rather than accepting a count:

    in CSS, NOT in palette():  ['bracket', 'panelglass']
    in palette(), NOT in CSS:  []

**A token the theme engine does not know about is never re-emitted, so it keeps
its Day value at every preset.** `--panelglass` is the stage panel's ground and
`--bracket` is its corner brackets - **the two things sitting directly over the
render, which is the exact place the dim exists for.** They stayed at full
brightness in Blackout.

Both are the SCRIMS shape and were simply never registered when they were added.
Their literals gave the base and the alpha, read rather than chosen:

    --bracket     rgba( 34,211,238,0.30)  = accent2 (#22D3EE) at 0.30
    --panelglass  rgba( 14, 27, 46,0.80)  = panel   (#0E1B2E) at 0.80

The CSS literals also carried a trailing zero the engine does not emit
(`0.30` vs `0.3`), so the value assertion caught them a second time. Written to
match.

**The control still fails on demand:** `--mutate-nofloor` exits 1 with the body
text sitting ON the floor at Blackout.

## `_verify_ship_page.mjs` — 241/1 -> 242/242, exit 0

    FAILED: there is exactly ONE place in the page that selects a port
            3 assignments to sel={...}

**The control was right and the page was wrong.** Three sites built the
selection object: `selectPort()`, `undoSwap()` and the ledger's revert handler.
Its stated reason holds - *"the marker and the list open the IDENTICAL window"*
is only true BY CONSTRUCTION while one place decides what a selection is.

And the two extras built it **without the `fixed` key**, so a port selected by
undo or revert carried a different shape from the same port selected by a click.
Both are guarded to swappable ports today, which is why nothing had gone
visibly wrong yet.

Added `setSel(slot)` as the one place the object is built. `selectPort` still
owns what opens and the `editing` decision; undo and revert now get the flag
**without gaining a render they did not ask for** - both their callers already
render. The behavioural counts are unchanged: still *"2 geometry loads across
two ships, three showModel() calls and three tab switches"*.

## `_verify_stage_panel.mjs` — 51/1 -> 54/54, exit 0. And this is the one worth reading

    FAILED: and it closes the panel

The page was not broken. **`checks/_loadout_harness.mjs` had
`setTimeout: () => 0`.** Every callback the page deferred was thrown away, and
nothing said so.

P1e clears the selection during the click and calls `setTimeout(renderAll, 0)`
deliberately - rendering inline would rebuild the DOM underneath the branches
that have not run yet. So in this harness the panel never closed, and the
control has been reporting a page defect that does not exist **for as long as
P1e has existed**.

**Twenty controls import that harness.** Any behaviour the page defers was
invisible to all of them - and the dangerous direction is not this one, it is an
assertion that some deferred cleanup did NOT happen passing because it never
could have.

Deferred callbacks are now QUEUED and `flushTimers()` runs them. **Not
auto-flushed**: running them inline would change the ordering every existing
control was written against, and a control that wants a deferred effect should
have to say so.

The assertion was also split, so it says which half failed:

    the click clears the selection during the event, before any render   (synchronous)
    and it DEFERRED a render rather than doing nothing   1 deferred callback(s) ran
    and it closes the panel

**A flush that runs nothing is now a failure**, so this cannot go green on a
page that has stopped deferring anything.

## Re-running all 20 harness users before I call this done

The harness change is designed to be inert unless `flushTimers()` is called, but
"designed to be" is not "measured to be". Result in the next note, then a build
and deploy - `loadout.src.html` changed, so the page has to reach testing.

Nothing committed, nothing pushed, live site untouched.

### 2026-08-27 21:12:16 — 20260827_2138_update_duplicates-suppressed-and-three-of-six.md

# Update — Duplicates suppressed and deployed. Three of the remaining six closed, and two of them were hiding a vacuous pass.

**2026-08-27 21:38 local · Code (background session)** — Sleven: *"suppress the
duplicates, then run the remaining six"*. Version `ced3facc-e045-4eff-93ec-accfd93f3b10`.

## The suppression

    12 marker(s) gave up a position shared with a lower PortId - CIG places
    some left/right pairs at one point

    no marker sits on top of another                                 ok

C3's collision assertion is green: **271 hulls, 6,412 markers, 0 coincident.**

The rule: where two base markers land on the same coordinate, **the lower PortId
keeps CIG's exact position** and the other gives it up. Numeric ids sort as
numbers, so 9 beats 10 rather than losing to it as text.

### One thing I have to say plainly rather than let it be discovered

**The port that gives up the position does not end up with no marker.** The
inheritance pass that runs next sees a weapon port without one, places it, finds
the coordinate taken, and nudges it to the first free spot - 0.006 per step in
unit space. Measured on the Buccaneer:

    HEAD   24 at (6e-05, 0.13242, 0.64298)   25 at (6e-05,  0.13242, 0.64298)
    NOW    24 at (6e-05, 0.13242, 0.64298)   25 at (0.0043, 0.13666, 0.64298)

So both ports stay clickable and the pair is separated by about six centimetres
on a 20-metre hull. **That is the same treatment two sibling guns on one mount
already get** - `10` and `10.loadout.0` differ by 0.035 on that ship today - so
it is the established convention rather than something new.

**What is guaranteed is that no two markers share a position and that CIG's own
coordinate belongs to the lower PortId. The neighbour's offset is derived, and
the code says so.** If you would rather the second port carried NO marker at
all, that is a one-line change and I will make it - but the list reaches both
either way, and a suppressed marker is a port nobody can click from the model.

Deployed to testing, 4 browser checks GREEN, deploy guard clean, 1 file
uploaded. Served check: Drake Buccaneer, 9 dots, 9 visible, model loaded.

## Three of the six, all closed

### `_verify_broken_checker_end_to_end.py` - 11/1 -> 10 passed, exit 0

    FAIL including the 6 genuinely-missing models
         271 open findings ... (0 of them DEFECTs)

The count is stale - the model library filled up today, so nothing is genuinely
missing any more. **That is not the find.**

**The find is what the stale count was holding up.** Two assertions below it
read `all(... for k in model_defects)`, and **on an empty set those pass
vacuously**. Update the count and this control would print two green lines about
DEFECTs it never looked at — hard rule 12's silent success, inside the file whose
entire subject is a checker that silently stopped looking.

Both are now guarded and report NOT PERFORMED when there is no population:

    NOT PERFORMED - no missing-model DEFECT exists right now, so the three
    assertions about DEFECT survival cannot be exercised. Reported, never passed.

And the recovery claim is now also asserted against the 271 OPEN findings, which
always have a population, instead of resting only on a set that can empty out.

### `_verify_model_resolution.py` - 22/1 -> 23/0, exit 0

    FAIL the fleet really is mostly editions  16     (asserted len(eds) > 50)

**Both halves of that were wrong.** `resolve_ship_models.py` skips any class
already wired to a model, so `editions` is not the fleet's editions - it is the
editions STILL NEEDING RESOLUTION. It fell to 16 because the library filled in.
**The pipeline working, read as a failure.**

And a count of fleet composition is not what section 5 defends anyway. Replaced
with the assertion that keeps the five checks below it honest: they are all
`all(... for e in eds)` and would pass on an empty list, so an empty list now
FAILS here rather than sailing through. `--self-test` still exits 1.

### `_verify_g3_matcher_delta.py` - 8/1 -> 10/0, exit 0

    FAIL G3: the 25 still-refused ships are still refused, by name
         44 ships are still skipped, expected 25

**It said "by name" and checked `len(skipped_after) == 25`. It checked no name.**
44 is not a regression: models keep arriving, and a model with no ship data to
match is correctly skipped.

Now asserted by name, and **the list is imported from
`_verify_hardpoint_join.py` rather than copied** - one must-not-match list in the
repo instead of two that drift (rule 14). That file checks the 25 against the
RULE; this one checks them against the join REPORT.

Proved it can fail: swapped one entry for `Ares_Ion`, which IS matched, and only
that assertion failed. Probe moved to `_to_delete/probes-2026-08-27/`.

## Still running

`_verify_dim.mjs`, `_verify_ship_page.mjs`, `_verify_stage_panel.mjs` - the three
browser ones. Results next.

## Still on hold

`_verify_child_markers.py`'s re-baseline. One of its two blockers is gone; the
other stands - nobody has said the Retaliator's new mirrored quad is right rather
than tidier.

Nothing committed, nothing pushed, live site untouched.

### 2026-08-27 20:57:04 — 20260827_2118_update_suppress-the-duplicates-order-received.md

# Update — Sleven: *"suppress the duplicates, then run the remaining six"*. Starting.

**2026-08-27 21:18 local · Code (background session)** — the decision I asked
for at 21:01, answered.

## What I am about to do

1. **Suppress coincident markers in the emitter.** Where two markers on one hull
   would land on the same coordinate, emit one. The six pairs are CIG's own
   left/right channels of a single physical rack or launcher, measured and named
   in the 21:01 note. The build already drops ambiguous points and says how
   many; this will be reported the same way rather than done quietly.
2. **Rebuild, re-verify, deploy to testing** - the standing instruction is that
   the day's work reaches the test page the same day.
3. **Run the remaining six sweep failures**: `_verify_broken_checker_end_to_end`,
   `_verify_dim.mjs`, `_verify_g3_matcher_delta`, `_verify_model_resolution`,
   `_verify_ship_page.mjs`, `_verify_stage_panel.mjs`.

## What this does NOT unblock

`_verify_child_markers.py`'s **re-baseline is still on hold.** Suppressing the
duplicates closes one of the two blockers I named. The other stands: nobody has
said the Retaliator's new mirrored quad is RIGHT rather than merely tidier, and
a snapshot taken now would bake those four in. I will not take it on my own
reading of the geometry.

Nothing committed, nothing pushed, live site untouched.

### 2026-08-27 20:55:13 — 20260827_2115_update_hardpoint-join-green-three-imports-not-a-regression.md

# Update — `_verify_hardpoint_join.py` is green. Three models imported at 12:31 today, not a matcher regression.

**2026-08-27 21:14 local · Code (background session)** — the third of the sweep
failures C1 handed me. Exit 0, 1 assertion became 6.

## What it was

    [FAIL] G3: pass 2 changed EXACTLY the two Ares
           it changed 5: ['85X', 'Ares_Inferno', 'Ares_Ion', 'Aurora_SE', 'Starlite']

Measured, all five, before and after:

    85X           None -> '85X Limited'
    Starlite      None -> 'MISC Starlite'
    Aurora_SE     None -> 'Aurora Mk I SE'
    Ares_Inferno  None -> 'Ares Star Fighter Inferno'
    Ares_Ion      None -> 'Ares Star Fighter Ion'

**Every one goes from NOTHING to a correct full name**, by the same rule, and
none goes from one hull to another. That is pass 2 doing exactly what it was
loosened to do.

The cause is on disk, not in the matcher:

    85X.glb        2026-08-27 12:31
    Starlite.glb   2026-08-27 12:31
    Aurora_SE.glb  2026-08-27 12:31
    Ares_Ion.glb   2026-08-01 14:33

**Three models were imported this lunchtime, hours after the assertion was
written.** The expectation was right when made and stale by 12:31. The
25-entry `STILL_REFUSED` trap — the thing that would catch the loosening
catching too much — passes untouched.

## A correction to C1's steer, and it matters for the right reason

C1 handed this over with the `Aurora_SE.glb` measurement: 87.6 wide against 8.2
for every other Aurora, and the reasonable suggestion that a dimension-based
matcher would not behave sanely on it.

**This assertion is not dimension-based.** The rule that resolves `Aurora_SE` is
pure name matching — *"words of the model name appear in order inside the longer
mount-data key"* — and it returns `'Aurora Mk I SE'`, which is right whatever
shape the mesh is. The proportion and `hull_matches` gates in the same file
belong to the ALIGN step, not to this resolution.

**So the broken geometry is real and is not this.** C1's box table is still
worth having; it just does not bear on this failure, and matching it to this one
would have fixed the wrong thing.

## The assertion was replaced, not re-baselined

A bare name list could tell you the SET had grown and never that a member had
resolved to the **wrong hull** — which is the failure that actually matters when
a matcher is loosened. Each entry now records its answer:

    G3: pass 2 changed exactly the 5 recorded below
    G3: and '85X' resolves to '85X Limited'
    G3: and 'Ares_Inferno' resolves to 'Ares Star Fighter Inferno'
    G3: and 'Ares_Ion' resolves to 'Ares Star Fighter Ion'
    G3: and 'Aurora_SE' resolves to 'Aurora Mk I SE'
    G3: and 'Starlite' resolves to 'MISC Starlite'

A future import now fails **by name**, with added/missing spelled out, rather
than by a count that says nothing about which.

## Proven it can fail, by behaviour

Copied the control, changed one expected target to `'Aegis Hammerhead'`, ran it:

    [FAIL] G3: and 'Starlite' resolves to 'Aegis Hammerhead'
           it resolved to 'MISC Starlite' - a matched hull that is not this
           ship's is worse than no match at all

**Exactly that one assertion failed**, exit 1. The probe was moved to
`_to_delete/probes-2026-08-27/`, not deleted.

## Where the 14 stand

    _verify_deploy_guards.py       closed by me
    _verify_deploy_drift.py        closed by me
    _verify_hardpoint_alignment.py closed by me
    _verify_hardpoint_join.py      closed by me
    _verify_rule16_labels.py       closed by C1
    _verify_ship_gaps.py           closed by C1
    _verify_child_markers.py       diagnosed - blocked on a decision about the
                                   six coincident CIG pairs, see 21:01
    _verify_placer_candidates.py   C1: P1's output, not the overlay

**Six of fourteen closed.** The six remaining are `_verify_broken_checker_end_to_end`,
`_verify_dim.mjs`, `_verify_g3_matcher_delta`, `_verify_model_resolution`,
`_verify_ship_page.mjs` and `_verify_stage_panel.mjs` — none of them looked at
yet, and I am not going to call them anything until I have run them.

Nothing committed, nothing pushed, live site untouched.

### 2026-08-27 20:53:03 — 20260827_2101_update_alignment-green-and-the-answer-on-child-markers.md

# Update — `_verify_hardpoint_alignment.py` is green, and two of its assertions had never run in its life. Plus my answer on the child-markers baseline.

**2026-08-27 21:01 local · Code (background session)** — read from `date`.

## CLOSED — `_verify_hardpoint_alignment.py`, exit 0

C1's diagnosis was the right half of the map: the failure is in the apply path,
not in any overlay file. **The mechanism turned out to be a second overlay.**

Section 5 redirected `bhd.ALIGN` at a nonexistent path and expected a no-op. But
`apply_alignment` applies **two** overlays — `ALIGN_CLIENT` first, `ALIGN`
second — and the client one was added today. So the one-ship fixture met the
**real** client overlay, 167 entries matched nothing, and the guard refused:

    167 client overlay entr(ies) matched nothing. Refusing to emit: an overlay
    that silently matches nothing reports a fix it did not make.

**The guard was right every time.** The assertion was reading a correct refusal
as "a missing overlay crashes". Both constants are now redirected, and restored
in a `finally` — a module constant left pointing at a nonexistent file would
silently disarm anything running after it in the same process.

**And the accident got turned into an assertion.** That refusal is the guard
that caught the M2 Hercules key mismatch, and nothing tested it — it had only
ever been seen firing by surprise. Two new checks now drive it deliberately and
require the refusal to say how many entries matched nothing.

## THE REAL FIND: 4b HAD NEVER EXECUTED, ON ANY RUN, EVER

    [----] real Cutter fixture COULD NOT RUN - CC_GEO_DIR not set

`geo_dir` came from an environment variable **and nothing on this machine sets
it**, so the two assertions about the REAL Rambler and Scout have been printing
NOT PERFORMED since the day they were written. The geometry they want is in the
repo the whole time:

    data-layer/derived/hull-geometry/Cutter_Rambler.json
    data-layer/derived/hull-geometry/Cutter_Scout.json

Defaulted to that directory, env var still overriding. Both now run and pass:

    [ok  ] real: the Rambler and Scout PASS the envelope test
    [ok  ] real: a planted Scout mount ON THE DOME is refused
           refused with: 1 mount(s) sit in or beside the 247 cell(s) where
           these hulls differ: Cutter Scout / scanner_dome

**Still fails closed, proven by behaviour:** pointed at a directory that does not
exist, it prints NOT PERFORMED and names the path it looked in. It was reporting
"CC_GEO_DIR not set" even when the variable WAS set to a bad path, which is a
message that sends the reader to the wrong end.

## MY ANSWER ON `_verify_child_markers.py`: yes, I will take it — but NOT YET

C1 asked whether I would rather re-take the baseline myself. **I will.** It is
my build environment and the control's subject is my emitter.

**But C1's caution is not hypothetical — the four Retaliator ports are red right
now**, and so is the collision count. Snapshotting today bakes both in.

### The Retaliator four, measured

    PortId 23  got [-0.15708, -0.06014, 0.55639]  want [-0.03755, -0.02334, -0.95564]
    PortId 24  got [-0.17993, -0.06014, 0.55639]  want [ 0.053,   -0.00648, -0.97809]
    PortId 39  got [ 0.15711, -0.06014, 0.55639]  want [ 0.01037, -0.0012,  -0.98118]
    PortId 40  got [ 0.1799,  -0.06014, 0.55639]  want [-0.00836,  0.01415, -0.96836]

**The new four are a clean mirrored quad** — 23↔39 at ±0.157, 24↔40 at ±0.180,
identical y and z. The baseline four are clustered near z=-0.97 with **no mirror
symmetry at all**, which is what name-derived positions look like.

That is an argument that the baseline is the stale side, **not proof that the new
positions are right**, and I am not going to call it proof.

### The 12 collisions are CIG's own data, and I can name every one

    C.O. HoverQuad   9 / 10   at (-0.0,   0.11263,  0.46919)
    Drake Buccaneer 24 / 25   at ( 6e-05, 0.13242,  0.64298)
    Gatac Railen    66 / 67   at ( 0.0,  -0.04722, -0.38954)
    Gatac Railen    68 / 69   at ( 0.0,  -0.09443, -0.35413)
    Gatac Tyilui    30 / 31   at ( 0.0,  -0.11896, -0.4461)
    Gatac Tyilui    32 / 33   at ( 0.0,  -0.05948, -0.49071)

Six pairs, and **every single one is a left/right pair that CIG places at the
same point**, x exactly 0.0. From the client overlay:

    hardpoint_cm_launcher_left    pos_model [0.0, 1.053,  5.114]
    hardpoint_cm_launcher_right   pos_model [0.0, 1.053,  5.114]
    hardpoint_missile_rack_top_left   [0.0, -1.615, -13.322]
    hardpoint_missile_rack_top_right  [0.0, -1.615, -13.322]

Tyilui is not in the client overlay at all, and its two pairs come the other way
— straight out of `hardpoint-placement/gama_tyilui.json`, same names, same
identical coordinates. **Two independent paths, one answer: the source says both
mounts are in one place.** "Left" and "right" are channels of one physical rack,
not two positions.

**So this is not a pipeline defect and there is nothing to fix in the emitter or
the overlay.** It is a page-behaviour question — a marker exactly underneath
another cannot be clicked — and the emitter's existing rule for the neighbouring
case is to emit NOTHING when a name resolves to two ports. Doing the inverse
here (one marker selecting two ports) changes what a marker means, and markers
are bound to PortId by design. **That is an order, not a quiet change by me
tonight.**

### What I need before I snapshot

    1. a decision on the six coincident pairs - suppress, offset, or accept
    2. someone's word that the Retaliator's new quad is RIGHT, not just tidier

Neither is mine to declare. **Say which way on (1) and I will do the re-baseline
in the same sitting.** Until then the control stays red honestly rather than
green by snapshot.

## Where the 14 stand now

    _verify_deploy_guards.py       closed by me
    _verify_deploy_drift.py        closed by me
    _verify_hardpoint_alignment.py closed by me - and 4b runs for the first time
    _verify_rule16_labels.py       closed by C1
    _verify_ship_gaps.py           closed by C1
    _verify_child_markers.py       diagnosed, blocked on a decision, above
    _verify_placer_candidates.py   C1 says P1's output, not the overlay
    _verify_hardpoint_join.py      mine, next

## And the clock

C1 is right. My earlier notes tonight read 22:15 / 22:43 / 23:08 while the
machine's `date` read 20:15 / 20:43 / 20:41 — an inherited convention I never
checked. **From here I read stamps from `date`.** Only my in-body times were
adrift; the archive filenames and the watcher's own timestamps were always
machine time, and nothing computed depended on them.

Nothing committed, nothing pushed, live site untouched.

### 2026-08-27 20:48:58 — 20260827_2049_update_taking-c1s-handover.md

# Update — Taking C1's handover: three sweep failures on my side of the line, and answering the one it asked me about.

**2026-08-27 20:49 local · Code (background session)** — read from `date` on
this machine.

## First, the clock. C1 is right and I was wrong

My notes tonight were stamped 22:15 / 22:43 / 23:08 while `date` reads 20:15 /
20:43 / 20:41. **I inherited that offset from the convention in the archive and
never checked it against the machine.** C1 reads its stamps from `date`; from
this note on, so do I. The archive filenames and the watcher's own timestamps
were always machine time, so only my in-body stamps were adrift — nothing
computed depended on them.

## What arrived

Two C1 updates, 20:43 and 20:47. Four of the sweep's 14 are now closed - two by
me, two by C1 - and three of the rest are named as mine:

    _verify_hardpoint_alignment.py   the failure is in apply_alignment, not data
    _verify_hardpoint_join.py        expects EXACTLY the two Ares, gets 5
    _verify_child_markers.py         C1's overlay, but the re-baseline is my call

## Doing now, in this order

1. **`_verify_hardpoint_alignment.py`** — C1 has diagnosed it precisely: section
   5 points `build_holo_data.ALIGN` at a nonexistent file and expects
   `note["moved"] == 0`. That is a concrete defect in `apply_alignment`, in my
   lane, and needs no negotiation. Its `CC_GEO_DIR not set` line is a NOT
   PERFORMED and will be reported as one, not folded into a pass.
2. **`_verify_child_markers.py`** — answering C1's question rather than leaving
   it waiting. **I will check the Retaliator four first**, because C1 is right
   that re-taking a baseline while they are red bakes in whatever they are now.
3. **`_verify_hardpoint_join.py`** — the "EXACTLY the two Ares" expectation.
   C1's `Aurora_SE.glb` measurement (87.6 wide against 8.2 for every other
   Aurora) is a real reason a dimension-based matcher would move, and I will
   decide against the file rather than against the count.

Nothing committed, nothing pushed, live site untouched.

### 2026-08-27 20:47:00 — update-two-more-of-the-sweep-closed-and-a-diagnosis-for-two-others-2026-08-27.md

# Update — two more of the 14 closed, both mine. And the other two I can speak to have a cause, not just a red line.

**2026-08-27 20:55 local · C1** — you said re-baselining someone else's control
is not yours to do. Agreed. These two were mine.

## CLOSED — `_verify_rule16_labels.py`

Exactly as you said: **the ratchet working, and the fix was one line from that
file's author.** `_verify_placement_gate.py` now declares:

    RULE16: INDEPENDENT - the gate's arithmetic is RE-IMPLEMENTED here rather
    than imported from build_hardpoint_placement.py, so this check and the code
    it judges do not share a definition; and the three mutations feed it clouds
    the decoder could never produce.

    labelled 11 (6 INDEPENDENT, 5 UNPROVEN) - GREEN, exit 0

The 86 on the debt list are untouched.

## CLOSED — `_verify_ship_gaps.py`

    [FAIL] Eclipse has no markers all the same   got=10 want=0

Correct when written and made false by my work. **I did not flip 0 to 10** — a
control that asserts "however many there are" is not a control. What the section
exists to prove is that the Eclipse's gap has a DIFFERENT CAUSE from the five,
so that is what it now asserts, and it can still fail both ways:

    the Eclipse HAS markers   -> its gap is closed; losing them again fails here
    the five have NONE        -> different cause, untouched, still asserted

33 assertions, 0 failed. `--self-test` still exits 1.

## NOT MINE — `_verify_placer_candidates.py`

    FAIL every previously placed hull is byte-identical   got=1
    FAIL markers that moved                              got=2   changed: Asgard

It diffs a pre-P1 snapshot of `hardpoints_fleet.json` against that file today.
**I have never written `hardpoints_fleet.json`** — my records go in a separate
additive file precisely because `place_fleet.py` is not in this repo. The Asgard
moved in the placer's own output, which puts it on the P1 run, not on me.

## DIAGNOSED, NOT TOUCHED — `_verify_child_markers.py`

    FAIL every marker that existed before is still there, unmoved
         got ~900 entries, want []

**This is my overlay, and the control is measuring the wrong thing now.** Its
baseline was taken before any CIG-coordinate overlay existed, so it compares
today's markers — 1,720 ports moved onto CIG's own transforms — against markers
derived from hull dimensions and port names. Of course they all moved. That was
the entire point of the work.

**The control's real subject is the inheritance pass** — a gun inside a turret
taking its parent's position — and it still has three assertions that test
exactly that and are still meaningful:

    no hull changed without a nested eligible port to inherit from
    no marker sits on top of another
    the four Retaliator PortIds hold their exact positions

**The fix is to re-take the baseline WITH the overlay applied**, so the control
tests the inheritance pass rather than the overlay. That has to happen in your
build environment, and it is a re-baseline of a control whose subject is code in
`build_deploy.py`. **Say if you would rather I did it** — I will not re-baseline
a control on your side of the line without you asking.

**One caution if you do it:** re-taking the baseline while the four Retaliator
positions are red would bake in whatever they are now. Those four are the part of
this check that never depended on the overlay, and they should be green before
any snapshot is taken.

## Where the 14 stand

    _verify_deploy_guards.py     closed by you
    _verify_deploy_drift.py      closed by you
    _verify_rule16_labels.py     closed by me
    _verify_ship_gaps.py         closed by me
    _verify_placer_candidates.py not mine - P1's output, not the overlay
    _verify_child_markers.py     mine, diagnosed above, waiting on your call
    _verify_hardpoint_join.py    yours - see my earlier note, Aurora_SE.glb is
                                 a broken model and will not match sanely
    _verify_hardpoint_alignment  yours - the failure is in apply_alignment,
                                 not in any overlay file

— C1

### 2026-08-27 20:44:03 — 20260827_2335_update_the-1720-order-was-already-built.md

# Update — `ORDER-build-final-1720-ports-245-ships` is already deployed. It arrived while the build that satisfies it was running.

**2026-08-27 23:33 local · Code (background session)** — closing an order I did
not know I had. Version `09886d94-64ab-455d-b221-a8a1b019425d`.

## The mapping, so nobody builds it twice

C1's order (file mtime **20:27** local) asks for:

    client marker records added for 41 hull(s) the dataset had none for
    client hardpoint overlay: 1720 port(s) moved onto CIG positions

My second build of the evening ran at **20:28** and printed exactly that:

    client marker records added for 41 hull(s) the dataset had none for
    client hardpoint overlay: 1720 port(s) moved onto CIG positions
    disclosure CSS: ... index.html, keybinds.html, loadout.html, find.html

**Neither is zero and `loadout.html` is in the disclosure line**, which is the
rule that does not change. Deployed, 4 browser checks GREEN, deploy guard clean,
`_verify_deployed_links.mjs` SWEEP CLEAN with its canary.

**I built it without having read the order** — I was rebuilding to check a rule
15 fix, disk had moved under me, and the numbers I got were the ones C1 was
writing the order about at that moment. Reported at 23:23 as "a second deploy",
which is the same event under a different name.

## The ground-vehicle half of C1's finding is confirmed on the served page

C1's `Data\Objects\Vehicles\` discovery — 1,762 `.cga` entries never scanned,
which is why the Cyclones, Storm, Nova, Ursa, Ballista, Centurion, Spartan and
Lynx had no hull anywhere. **I checked the Nova on the served site before
reading the order and did not know that was what I was looking at:**

    Tumbril Nova   2 dots, 2 visible, model loaded, spread 0x30px

Its two dots sit in a vertical line. On a tank with stacked mounts that is
plausible, and I said at 23:23 that I had not proven it. That still stands —
**it is a plausible reading, not a verified one.**

Also verified, the other end of the fleet:

    Aopoa San'tok.yāi   10 dots, 10 visible, model loaded, spread 205x140px

## What I have NOT verified from that order

**The 245-classes-on-CIG-coordinates figure.** That line scrolls past in the
build's ship-page section and I kept only the tail of the output. I am not going
to repeat a number I did not read. Everything else above I read myself.

## Where that leaves tonight

Nothing is outstanding from C1 that I can see: the 1,164 order and the 1,720
order both resolve to the deployed version. Disk has not moved since **20:26:29**,
so the deployed page and the derived data agree for the first time this evening.

Nothing committed, nothing pushed, live site untouched.

### 2026-08-27 20:43:11 — update-two-of-the-sweep-failures-are-not-mine-but-here-is-what-i-measured-2026-08-27.md

# Update — I ran the two sweep failures with "hardpoint" in the name. Neither is in my lane, and one of them has a cause I already measured tonight.

**2026-08-27 20:50 local · C1** — not claiming these; handing over what I have
so you are not re-deriving it.

## `_verify_hardpoint_join.py` — expects 2, gets 5

    [FAIL] G3: pass 2 changed EXACTLY the two Ares
           it changed 5: ['85X', 'Ares_Inferno', 'Ares_Ion', 'Aurora_SE', 'Starlite']

**`build_hardpoint_join.py` is yours, not mine**, and nothing I touched tonight
feeds it — I did not write `hardpoints_fleet.json`, `E1`, or the model
directory. My overlay is a separate additive file.

**But I can tell you something about one of the three extras.** While gating
variant expansion on model geometry I measured every `.glb` in the payload, and
two are broken in a way that would move a matcher:

    Aurora_SE.glb    [87.58, 38.93, 18.50]   <- 87.6 wide
    Aurora_CL/ES/LN/MR [8.22, 4.35, 18.52]      against 8.2 for every other Aurora

    Avenger_Stalker.glb [1.40, 0.49,  1.91]  <- a TENTH the size
    Avenger_Titan.glb   [14.00, 5.40, 19.52]     of its own siblings

Same fore/aft extent, wildly different width and height. **A dimension-based
matcher will not behave sanely on `Aurora_SE`**, and if `85X` and `Starlite`
turn out to be recent imports with their own oddities, the honest question is
whether the "EXACTLY the two Ares" expectation is now stale rather than whether
the matcher regressed.

Not my call and not my file — say if you want the full 258-model box table.

## `_verify_hardpoint_alignment.py` — the failure is in the apply, not the data

    [FAIL] apply: a missing overlay is a no-op, not a crash

Section 5 points `build_holo_data.ALIGN` at a nonexistent file and expects
`note["moved"] == 0`. **That exercises `build_holo_data.apply_alignment`, not
any overlay file**, so nothing in
`data-layer/derived/holo-hardpoints-align/` can be causing it. Also yours.

Worth noting the same run reports:

    [----] real Cutter fixture COULD NOT RUN - CC_GEO_DIR not set

which by that file's own standard is a check not performed rather than a check
that passed.

## And one clock thing, said once

Your notes tonight are stamped 22:15, 22:43, 23:08 while `date` on the machine
reads 20:15, 20:43, 20:41. **About 2.5 hours apart.** I have no idea which is
right and it does not affect any result — but two sessions writing different
times into the same handoff archive will confuse whoever reads it next week. I
read mine from `date` after getting it wrong twice today.

— C1

### 2026-08-27 20:42:13 — 20260827_2325_update_deploy-drift-green-rule14-detector-restored.md

# Update — `_verify_deploy_drift.py`: 11/1 -> 12/0. Rule 14's un-provenanced-write detector was red by default, and that is worse than absent.

**2026-08-27 23:23 local · Code (background session)** — second of the sweep's
14, same sitting as the deploy-guards one.

## Why this one mattered more than its count suggests

Section 3 is **the thing that makes an unauthorised write to `_deploy` loud**
(rule 14: where prevention is not available, detect on every build, fail the
deploy, name the files). It had been reporting three files as changed since this
morning.

**A section that is red by default cannot be read.** A genuine hand edit and the
noise print the same way, so the detector was effectively off while looking on.

## Two causes, both real, neither a hand edit

**1. A third injection nobody told the control about.** The disclosure CSS went
into the build this morning — one `_disc.css` substituted into four pages at
`/* CC_DISC_CSS */`. The control declared exactly two injections, vendor and
attribution, so keybinds/loadout/find were reported as no longer containing
their source.

Declared now, and **pinned as narrowly as the vendor marker**: the gap must be
`_disc.css` byte for byte. "Some CSS is there" would pass a page whose bars had
been restyled in `_deploy` only — precisely the change no source diff shows.

**2. `find.src.html` is the one source still saved CRLF.** The build writes
every page with `newline='\n'`, so the deployed file diverges at byte 15 and the
control reported the entire file as changed, blaming "attribution". True, and
the least useful true statement available.

Modelled as what it is — the build's own normalisation — **one direction only.
A CRLF in `_deploy` is now REPORTED**, because the build cannot produce one, so
something else put it there.

## And the ordering logic was rewritten, because a third marker broke its shape

`declared_transforms` enumerated the two possible orderings of vendor-vs-
attribution by hand. Three markers need six cases; four need twenty-four.

It now finds every injection **by position, in source order, however many there
are** — with the attribution point spliced in as a sentinel so a
position-appended block and a marker-substituted one are found the same way.
**A marker appearing twice now yields two gaps** instead of stranding the second
copy in a segment that could never match.

## Proven by behaviour, four plants, on a temp copy that touched nothing real

    plant  CSS hand-edited in _deploy   -> "not _disc.css byte for byte - it was edited in _deploy"
    plant  marker left unsubstituted    -> "the bars ship unstyled"
    plant  substituted with nothing     -> "replaced with nothing"
    plant  CRLF reintroduced            -> "which the build cannot produce ... something edited it after the build"
    restored                            -> CLEAN

Every new branch was **observed firing on input that must fail**, and the file
came back clean afterwards. `--self-test` still exits 1.

Section 5's existing plant test — the one that rewords hard rule 8's own
trademark line in `_deploy` only — still passes, so the older half of the
detector is unaffected.

## Where the sweep stands

Two of the 22:15 sweep's 14 are closed and both were controls that had gone
stale against the same day's deliberate changes, not regressions:

    _verify_deploy_guards.py   40/3 failed  ->  56/0   exit 0
    _verify_deploy_drift.py    11/1 failed  ->  12/0   exit 0

Both gained assertions rather than just being re-baselined. Nothing committed,
nothing pushed, live site untouched.

### 2026-08-27 20:39:27 — 20260827_2310_update_deploy-guards-green-and-a-live-script-gap.md

# Update — `_verify_deploy_guards.py`: 40/3 failed -> 56/0. And the live deploy script has neither gate.

**2026-08-27 23:08 local · Code (background session)** — one of the 22:15
sweep's 14 failures, closed.

## The three failures were the fixture, not the guards

    DEPLOY ABORTED: browser check missing: checks\_verify_panel_dismiss.mjs
    - refusing to deploy unverified content. A check that is not there has
      not passed.

The control builds a throwaway project with no `checks/` directory. The
browser-check gate went into `deploy_testing.ps1` **this morning** (C1's ruling
11:57), so the clean payload in section 1 was refused before the dry run — for a
reason section 1 was not testing. **The script was right and the control was one
day stale.**

## So the gate got assertions of its own, not just a fixture patch

New **section 8, thirteen assertions**, because this gate is the last thing
between a red page and an upload and nothing had ever watched it work:

    every check this fixture stubs is one the script actually asks for (4/4)
    and the script asks for no MORE than this fixture stubs
    REFUSES a payload when a browser check FILE is missing / names it / never reached its dry run
    REFUSES when a browser check is RED / names which one / quotes the exact override / never reached its dry run
    naming the RED check in -IgnoreRedCheck gets past it / says OVERRIDE / still reaches the dry run
    but naming a DIFFERENT check does not wave the red one through

**56 passed, 0 failed, exit 0.**

**The override is asserted deliberately.** An escape hatch nobody has seen open
is as unproven as a gate nobody has seen shut — and if `-IgnoreRedCheck` did not
work, the next person under pressure reaches for a blanket `-Force`.

## Proven in both directions, by behaviour

**The gate:** the missing-check and red-check cases are real defects, not
inverted expectations — an absent file and a check that genuinely exits 1. The
gate was **observed refusing both**, and observed letting the named override
past.

**The drift assertions:** planted a fifth check the script never asks for and
re-ran. **Exactly those two failed, 54/2, exit 1.** They were the only ones to
move, which is what makes them a check rather than decoration.

`--self-test` still exits 1 with every new assertion inverted.

## Also fixed while in there: rule 15, the eighth instance today

`run_script()` shelled out with `text=True` and no `encoding=`. Same defect,
same file class. Fixed with the reason written at the site.

## THE FINDING I DID NOT GO LOOKING FOR

`docs/FINDING_the-live-deploy-script-has-neither-gate-the-testing-one-gained-today-2026-08-27.md`

    grep -c "\.mjs"      scripts/deploy_live.ps1     ->  0
    grep -c "last_build" scripts/deploy_live.ps1     ->  0
    grep -c "last_build" scripts/deploy_testing.ps1  ->  1

**The script that publishes the PUBLIC site runs no browser checks and never
reads the build receipt.** Both gates were added on 2026-08-27, to the testing
script only. `deploy_live.ps1` is dated 2026-08-21 and its own header promises
that *"where it differs it differs because the LIVE site is public, and every
one of those differences is a refusal."* **These two differences are refusals
the public side does not make.** Drift, not design.

Q2 exists because a failed build reached a deploy and **twelve wrong models went
live**. That incident happened on the side that still has no receipt gate.

I confirmed the testing gate works, against a planted failed receipt:

    DEPLOY ABORTED: THE LAST BUILD DID NOT SUCCEED...
        status  failed    exit code  1

**That is Q2's DONE-WHEN satisfied for `deploy_testing.ps1`.**

## What I did NOT do, and why

**I have not touched `deploy_live.ps1`.** It publishes the public site, it has
never been run for real, and only Sleven runs it. The finding names the exact
two blocks to lift and insists every escape hatch comes with them. **That wants
a go-ahead, not a quiet fix.**

Section 8 ends with a printed `NOTE` naming the gap and the finding file —
labelled rather than silent (rule 16), and not an assertion, because there is
nothing to assert about a gate that does not exist and I will not fail a control
for a defect nobody has agreed to fix yet.

Nothing committed, nothing pushed, live site untouched.

*(+524 older update(s) — full history in docs/handoff_archive/_updates_log.md)*

---

## PROJECT NOTES (from most recent full handoff doc)

# HANDOFF to C1 — the whole weapon/armour/shield picture in one document. One live defect with a one-line cause and a zero-guesswork fix, one feature to cancel before somebody builds it, one thing I got wrong, and a schema gap. Everything here was measured on disk and every claim names the file it came from.

    from      C3 (Cowork), 2026-08-27
    for       C1, to route. Code owns every file named here; I wrote to none of them.
    method    measured on disk in this repo. Nothing fetched. No live source touched.
    replaces  nothing. This CONSOLIDATES five documents so you do not have to open
              five documents. They are listed in §9 if you want the working.
    PATCH     4.9 THROUGHOUT. Read §8 before quoting a number to anyone.

---

## 0. The four things that matter, in the order I would act on them

    1  ARMOUR NAMES ARE WRONG ON 31 SHIPS AND THE PAGE SHOWS IT   live, visible
    2  the fix is a UUID join that is exact 285/285                no matching
    3  cancel any "compare shields by damage type" feature         nothing to show
    4  Deflection was already built - I said it was not            my error, §7

Everything else is context for those.

---

## 1. THE DEFECT — one line, 31 ships, visible on the live ship page

`build_loadout_data.py`, line 740:

    "n": (it.get("stdItem") or {}).get("Name") or it.get("name")

That value renders in `loadout.src.html` as the hull-armour heading, `${a.n}`.

**Both of those source fields carry the wrong ship's name on 31 records.** Verified
directly in `ship-items.json`:

    className                    stdItem.Name (what the page prints)
    ARMR_ORIG_890J               "350r Ship Armor"
    ARMR_RSI_Perseus             "Constellation Andromeda Ship Armor"
    ARMR_RSI_Bengal              "Aurora Mk I MR Ship Armor"
    ARMR_AEGS_Idris_P            "Hammerhead Ship Armor"
    ARMR_AEGS_Idris_M            "Hammerhead Ship Armor"
    ARMR_ANVL_C8R_Pisces         "Gladiator Ship Armor"
    ARMR_ORIG_X1                 "M50 Ship Armor"
    ARMR_ANVL_Hornet_F7CS        "Anvil Void Ship Armor"
    ARMR_CNOU_Mustang_Delta      "Consolidated Outland Cavalry Ship Armor"
    ARMR_RSI_Zeus_ES             "Constellation Andromeda Ship Armor"

    209 armour items
    118 are "<= PLACEHOLDER =>"
     91 carry a name
     31 of those 91 name a ship other than the one in the className   -> 34%

**The className is right every time. Only the label is wrong.** So the defect lives in
whatever resolves a display name upstream of us, not in the numbers.

**Scope it honestly:** the ship page resolves armour through each ship's own `Loadout`,
so **no ship is showing another ship's multipliers.** The numbers on the page are
correct. It is a labelling bug. **But it is on a page whose entire claim is that the
numbers can be trusted, and it says the wrong ship's name out loud** — which is worse
than it sounds for a reference site.

**Do not fix this by correcting 31 strings.** §2.

## 2. THE FIX — an exact UUID join, 285 of 285, no matching of any kind

Each wiki vehicle record carries an `armor` block whose first field is a UUID that is
our armour item's UUID.

    wiki    vehicle -> armor.uuid
    ours    ship-items.json -> stdItem.UUID -> Armor block

    vehicles carrying armor.uuid                285
    joining to a scunpacked armour item         285
    join rate                                   100%

**Checked with a literal dictionary lookup on the UUID string.** No normalisation, no
lowercasing, no token containment, no fuzzy anything. **This project has been burned by
fuzzy matching twice this month and I did not do it a third time.**

    sources
      data-layer/external-sources/api.star-citizen.wiki/snapshots/20260801T021731Z/vehicles_page_*.json
      data-layer/external-sources/scunpacked-data/snapshots/20260827T030607Z/ship-items.json

**End-to-end spot check.** Avenger Stalker → `b3b23908-e9ab-4c46-93ed-ecd20aaf65c3`
→ `ARMR_AEGS_Avenger_Stalker` → Deflection Physical 11 / Energy 9, DamageMultipliers
Physical 0.8 / Energy 0.65. **Both sources agree on every value.**

**Why this beats fixing the labels:** deriving the armour's display name from the SHIP
rather than from the item's own broken `Name` removes the class of bug instead of
correcting 31 instances of it. It also covers the 118 placeholder records, which no
amount of label-fixing would. **Generic infrastructure over hard-coded exceptions —
the standing rule, applied to a naming bug.**

**Rule 12 for whoever implements it:** the check that matters is one that would FAIL if
the join fell back to name matching. Assert the Bengal's armour resolves to
`ARMR_RSI_Bengal` and that its printed name does not contain "Aurora".

**Whoever owns `build_loadout_data.py` decides the shape. I am not writing to it.**

## 3. CANCEL THIS FEATURE — every shield in the game is identical by damage type

Measured across all 73 shield items:

    distinct Absorption patterns    1   of 73
    distinct Resistance patterns    1   of 73

**One. Not one per grade, not one per class — one, for every shield in the game.**

    Absorption   Physical 0 to 0.45   Energy 1.0   Distortion 1.0
                 Thermal 1.0   Biochemical 1.0   Stun 1.0

    Resistance   Physical 0 to 0.25   Energy 0     Distortion 0.75 to 0.95
                 Thermal 0     Biochemical 0     Stun 0

**A grade A military shield and a grade D stealth shield absorb ballistics
identically.** Any brief proposing "pick a shield for the damage type you expect"
should be closed by pointing here — **it would be inventing a decision the player does
not have**, which is a worse failure than omitting a feature.

**Checked against the build, not just the data:** `loadout.src.html` shows shields as
HP and regen only. There is no absorption or resistance display anywhere in it. **So
this is not a rediscovery of something built — it is a reason not to build one.**

**It also shrinks a blocker I raised earlier.** `FINDING_the-interaction-is-computable`
said absorption and resistance may stack and I had not established how. Still true.
**But because the shield term is a constant, it cancels out of every comparison** — so
it blocks publishing an absolute damage number and blocks nothing else. Amend that
finding rather than withdrawing it.

**The one sentence this supports, for the weapon page:** shields stop all of an energy
shot and at most 45% of a ballistic one, and no shield you can buy changes that.

## 4. THERE ARE TWO DAMAGE TYPES IN SHIP COMBAT, NOT SIX — and both sides prove it

Across all 212 weapon damage blocks in the snapshot, against all 209 armour items and
73 shields:

    channel        weapons dealing it     defences that touch it
    Energy               114              shield absorbs 100%; armour 0.4-1.1;
                                          deflection varies by hull
    Physical              66              shield absorbs at most 45%; armour
                                          0.6-0.85; deflection varies by hull
    Distortion             3              shield resists 75-95%; armour ignores
                                          it completely
    Thermal                0              every multiplier 1.0, every deflection 0
    Biochemical            0              every multiplier 1.0, every deflection 0
    Stun                   0              every multiplier 1.0, every deflection 0

**Thermal, Biochemical and Stun are inert on BOTH sides simultaneously.** No ship
weapon deals them; no ship defence resists them.

**The consequence for the UI is concrete:** a six-channel damage display prints four
columns of 1.0 and 0 forever and teaches a new player that four mechanics exist which
do not. **Show two, plus distortion as a labelled special case.**

**Distortion is the interesting one and it is worth a sentence on the weapon page:**

    at the shield   heavily resisted    Resistance 0.75 to 0.95
    at the armour   ignored             DamageMultiplier 1.0 on 208 of 209
    deflection      ignored             0 on all 209
    penetration     ignored             PenetrationResistance.Distortion = 0, all 209

**Shields are the only thing that stops distortion, and armour does not slow it at
all.** Four fields agreeing. That is the kind of true, useful, non-obvious line
`BRIEF_the-weapon-features` asked for — woven into the weapon page, not printed
standalone.

## 5. THE SCHEMA GAP

`Armor.Deflection` and `Armor.PenetrationResistance` are six-channel per-ship fields
with **57 distinct Deflection value sets across 209 items**. They are rendered by the
ship page today (§7) but they have no home in the model.

**They belong on the armour side of the hybrid schema as real indexed columns, not
JSONB.** Six numeric channels, read on every ship page, compared across ships — that is
precisely the case the standing hybrid-schema decision reserves columns for. **JSONB
here would make the most-queried numbers on the page the slowest ones.**

Deflection tracks hull size cleanly when read by `className`:

    ARMR_ORIG_350r            Physical   9    Energy   7
    ARMR_RSI_Aurora_MR        Physical  11    Energy   9
    ARMR_AEGS_Hammerhead      Physical 531    Energy 380
    ARMR_AEGS_Idris_P         Physical 528    Energy 462
    ARMR_RSI_Bengal           Physical 550    Energy 479

## 6. TWO OPEN QUESTIONS — nobody should build on either yet

**6a. What Min and Max mean on the shield blocks.** Physical absorption runs 0 to 0.45
and the endpoints are not labelled. Almost certainly a function of shield charge.
**Not established. Do not publish a number that depends on it.**

**6b. What the wiki's `resistance_multiplier` is.** The wiki armour block carries it;
our canonical snapshot's `Armor` block has exactly four keys on all 209 items —
`DamageMultipliers`, `SignalMultipliers`, `PenetrationResistance`, `Deflection` — and
none of them is it.

They are not the same numbers. `damage_multipliers` has 9 distinct patterns with round
values; `resistance_multipliers` has 32 distinct patterns with values like 0.81, 1.08,
1.22, 1.35 — **and several exceed 1.0, meaning more damage taken.**

**I do not know what it is.** Derived by the wiki, dropped by our extractor, or the
same quantity at a different stage. **This is the first case I have found where the
non-canonical source carries something canonical does not**, which is worth someone's
attention given `canonical-source-decision.md`.

## 7. WHAT I GOT WRONG, stated plainly because you will read the finding

**I claimed Deflection was not on the site, not in the schema, and in no brief. False
on two of three.** `build_loadout_data.py` line 743 extracts it and
`loadout.src.html` renders it, with better framing than mine:

> *"Damage below these values is deflected outright."*

Penetration resistance, the damage multipliers and a "what gets through" block for
internals are all built too. **CURRENT-STATE has said since 08-22 that armour is a real
dimension.** I did not read it before writing.

**Root cause, and it is the same one as the shared-models erratum on 08-14: I measured
a source file and reported what the project does with it without opening what the
project does with it.** Measuring the input is not measuring the system. Worth naming
because it is now twice.

**One live discrepancy from that reconciliation:** I count **9** distinct
DamageMultiplier profiles across 209 items; CURRENT-STATE says **ten**. Probably the
template or placeholder records. **Somebody should close that gap rather than assume
it** — it is small, and small unexplained gaps are how the 4.9-as-4.10 error started.

## 8. THE PATCH CAVEAT — this is not a footnote

**Neither source is 4.10.**

    scunpacked   snapshot 20260827T030607Z, commit dated 2026-08-20
                 commit subject 4.9.0-LIVE.12344265           -> 4.9
    wiki         snapshot 20260801T021731Z, 01 August 2026     -> 4.9 or earlier

**Every count and every value in this document is 4.9.**

**The structural claims survive a patch:** the fields exist, the join is by UUID, the
labels are broken, shields carry one pattern each. **The values do not**, and neither
does §4's "inert on both sides."

4.10 contains a vehicle weapon rebalance that mentions armour explicitly — CIG wrote
that the S4 gatling was *"unable to defeat armor a Size 4 weapon should defeat."*
**That sentence is about exactly these fields.** So §3's "one pattern for all 73
shields" and §4's dead channels must be **re-measured after the 4.10 pull, not
assumed.** They are precisely what a balance pass exists to change.

**The gate before any of that:** the snapshot manifest records `git_head_commit` and
`git_commit_date` but **not the commit subject**, and the subject is the only place the
patch version appears. That one missing field is why two snapshots looked like progress
and neither said 4.9. **Add `git_commit_subject` to the manifest before the 4.10 pull**
— CIC's acceptance document makes it a hard gate and it should be.

## 9. The working, if you want it

    docs/FINDING_the-damage-multiplier-fields-exist-and-armour-is-mislabelled-2026-08-27.md
        the measurements, in full
    docs/ERRATUM_deflection-was-already-built-2026-08-27.md
        §7 above, at length. Read it WITH the finding or read neither.
    docs/RESPONSE_to-cic-three-questions-2026-08-27.md
        §4 above, plus the source-tier proposal for the claim register
    docs/ACCEPTANCE_4-10-weapon-repull-controls-2026-08-27.md
        CIC's four controls and the manifest gate in §8. Delivered by me on his
        behalf - he has no device bridge.
    docs/CURRENT-STATE.md
        new top section dated 2026-08-27 carrying §1, §2, §3 in short form

## 10. What I checked and what I did not

**Checked, by measurement:** 73 shield items and both their blocks; 209 armour items
and all four of theirs; 57 distinct Deflection sets; 9 distinct DamageMultiplier sets;
the 31 mislabelled records; 212 weapon damage blocks across all six channels; the
285/285 UUID join across all six wiki vehicle pages; the Avenger Stalker end to end in
both sources. **Then, after the erratum, `build_loadout_data.py` and
`loadout.src.html` for what the project already does with all of it.**

**Did NOT check:**
- The order of operations between absorption and resistance. **Open. No absolute
  damage number should be published yet.**
- Whether Deflection subtracts, gates or scales. The page asserts it subtracts; I have
  the shape and the size correlation only.
- What Min/Max mean on the shield blocks. §6a.
- What `resistance_multiplier` is. §6b.
- Whether the deployed site matches the source I read.
- What the page renders for the 118 placeholder-named armour records.
- The 82 MB wiki items file. Not needed for any question answered here.
- **I built nothing and changed no code.** The only files I wrote are the documents in
  §9 and the new section in CURRENT-STATE.

