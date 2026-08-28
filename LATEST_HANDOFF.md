# LATEST_HANDOFF.md — Update #810 — 2026-08-28 10:41 AM

---

# CITIZEN COMPASS — LATEST HANDOFF

Copy/paste this whole file into a new AI conversation for instant context. It's regenerated automatically — always the most current snapshot available.

---

## CURRENT STATE (auto)

**Generated:** 2026-08-28 10:41:19 (auto-regenerated every time a file lands in inbox/ or this script runs — don't hand-edit this section)

**Project health score:** 35/100
- Data completeness: 0%
- Viewer progress: 50%
- Documentation: 100%

**Ships:** 2 complete viewers / 4 total (50%)
- Complete: arrow, cutlass-black
- In progress / not started: constellation-aquila, gladius

**Data layers:**
- data-layer: 119498 files (13787.32 MB)

**Scripts:** 53  |  **3D models:** 1119  |  **Docs:** 1357

---

## RECENT UPDATES (append-only, newest first)

### 2026-08-28 10:40:31 — 20260828_1045_update_the-first-clean-sweep-receipt-and-q10-closes.md

# Update — 101 controls green, the gate let it through, and it deployed. Q10's DONE-WHEN is closed at both ends. Q7 is past halfway.

**2026-08-28 10:45 local · Code (background session)**
Version `00321a0b-3c9b-45ea-aedd-5c368b857919`.

---

# Q10 — CLOSED

    101 ok, 0 failed, 3 skipped, 0 NOT RUN, in 679s

    sweep   : 101 control(s) green against this exact payload (2026-08-28T10:37:16)
    gate exit=0

**The first clean sweep receipt this project has ever had**, and the gate read it
and let the deploy through.

Q10's DONE-WHEN needed both halves and now has both:

    a deliberately-reddened control STOPS a deploy   proven in section 11 of
                                                    _verify_deploy_guards.py,
                                                    on both scripts
    a swept, clean payload GETS THROUGH              proven here, on the real
                                                    456 MB payload

**A gate that only ever refuses is not a gate either.** Until this run the
passing side had only been shown against throwaway fixtures.

## What it took to get there, and none of it was the gate being wrong

Three sweeps failed before this one, and every failure was a real staleness the
gate surfaced rather than a defect in the gate:

    _verify_rule16_labels.py        a control 90 seconds old with a label the
                                    regex could not read
    _verify_extremity_placement.py  3 assertions demanding an apology Q9 removed
    _verify_ship_page.mjs           2 more of the same
    _verify_child_markers.py        a baseline predating C1's 23:45 overlay
    _verify_placer_candidates.py    two ports differing in the fifth decimal

**Five controls, five different kinds of stale, none of them a bug in the
thing being shipped.** That is what 94 controls that could not stop anything
had been hiding.

---

# THE DEPLOY

    Found 3 new or modified static assets to upload
    + /craft_data.gen.js
    + /loadout_marker.gen.js
    + /loadout.html

Verified from outside rather than from the build log:

    /craft_data.gen.js            HTTP 200, 87,949 bytes
    served /loadout               carries <script src="craft_data.gen.js">
    _verify_deployed_links.mjs    SWEEP CLEAN, canary reporting

**The link sweep went from 18 internal references to 19** — it found the new
script tag by itself, which is a second, independent confirmation that the page
really does load the file.

---

# Q7 — TRANCHE 5, AND PAST HALFWAY

    labelled     52  (23 INDEPENDENT, 29 UNPROVEN)     was 43
    unlabelled   51                                    was 58

All seven controls green after labelling.

**This tranche is the checker-of-checkers family**, and it produced an
observation worth keeping rather than seven near-identical labels. Six are
UNPROVEN for the same reason and each says so in the same words:

> This is a RULE 12 control, and rule 16 is a different axis. Proving a checker
> fires on input that must trip it and stays silent on clean input is exactly
> what rule 12 asks for, and this file does both halves. **Being UNPROVEN under
> rule 16 is not a criticism of it** - it is the observation that a checker
> cannot be an independent source of truth about itself.

**The one INDEPENDENT is instructive by contrast.**
`_verify_never_delete_guard.py` does not ask the guard whether it refused - it
**SELECTs the row back out of the database**. Its own second paragraph says why:
a delete that failed for some other reason would look identical from the guard's
side. Postgres is the witness, and Postgres did not write the guard.

`_verify_schema_checks.py` is the near miss, and its label says so: the offending
state is a **real table in a real database**, so the condition being detected
genuinely exists rather than being a fixture pretending to. Only the verdict is
the checker's own — which is enough to make it UNPROVEN, and worth distinguishing
from the ones whose input is a temp directory.

---

# WHERE THINGS STAND

    Q1-Q6, Q8, Q9, Q10   done
    Q7                   52 of 103 labelled, 51 to go
    C1's crafting line   wired and serving

Nothing committed since `fee621f` — there is a substantial working tree now:
Q9's provenance field, Q10's whole mechanism, five Q7 tranches, the crafting
wiring, three re-baselined controls and C1's page work.

### 2026-08-28 10:13:52 — 20260828_1020_update_craft-wired-and-the-two-stale-controls-fixed.md

# Update — The crafting data is wired (it was three lines, not one), and the two controls Q9 stranded now assert the stronger claim.

**2026-08-28 10:20 local · Code (background session)** — Sleven: *"do the
deploy_pages line and keep going"*.

---

# 1. THE CRAFTING DATA — AND IT WAS NOT ONE LINE

C1's note said *"the build has to copy it in — one line in Code's
`deploy_pages.py`"*. Measured, three things were missing and the one line alone
would have shipped nothing:

    build_deploy.py     craft_data.gen.js lives in data-layer/derived/, and
                        PAGES copies from _src. Nothing brought it across.
    deploy_pages.py     the one line C1 named.
    loadout.src.html    the page had NO <script src="craft_data.gen.js">.
                        `craftLine()` checks `typeof CRAFT==="undefined"` and
                        returned nothing, silently, on every row.

All three done. **The page had been sitting on a working feature with no way to
load its data since 23:59 last night.**

## The copy fails closed on the PAIRING rather than on the file

    page asks + generator produced   copied, and the size printed
    page asks + no file              REFUSED - a script tag pointing at nothing
                                     is a 404 and a silently absent feature
    no page asks + file exists       reported, not copied - so a stale 88 KB
                                     does not ride along unnoticed

## Measured, not assumed

    CRAFT recipes                                 452
    fittable parts on the page                  3,283
    parts with a recipe the page can show         452

**452 of 452.** C1's join is CIG's own class name, case-folded, exact — and
every recipe lands on a part a reader can actually fit. Nothing was dropped in
the wiring.

    crafting data: copied into _src (87,949 bytes)
    pages copied: ... loadout_marker.gen.js, craft_data.gen.js, stick-test.html
    deploy guard: _deploy contains only known assets - safe to deploy

The guard accepted it without a separate edit, because `deploy_pages.py` is the
one list both the build and the guard import — rule 14 paying for itself.

---

# 2. THE TWO STALE CONTROLS, REWRITTEN RATHER THAN RELAXED

Five assertions across two controls demanded the page still apologise for
something Q9 fixed. The page now counts each ship's own dots:

    All 7 dots on this model come from the game's own ...
    5 of the 12 dots on this model come from the game's own ...
    The other 7 have no position in the ...

**Asserting the apology would now be asserting a falsehood.** What actually
needs defending is not that the page hedges — it is that an estimate is still
NAMED as an estimate wherever one is drawn, and that the page never claims a dot
was measured off the mesh.

`_verify_extremity_placement.py` **27 passed, 0 failed**:

    the note still names an estimate AS an estimate, for the hulls that have them
    and still says an estimate starts from the mount's NAME
    and it does NOT claim a dot was measured off the mesh
    and the per-dot provenance is what it counts, so the sentence is about
        THIS ship rather than the fleet

`_verify_ship_page.mjs` **242 assertions, 0 failed**. It reads the page's own
`mountProvenance(shipId)` and asserts the branch that matches the ship being
driven, so it follows whichever hull the section picks:

    every one of this ship's 7 dots is CIG's, so the note does not offer an
        estimate it does not have
    and the old fleet-wide hedge is gone - the note is about THIS ship
    and it says so as a count: "All 7 dots"

## One of them was asserting a code comment, and had been for a while

`"measured from the model" not in page` fired on **the note's own changelog** -
a `/* ... */` comment explaining what the sentence used to say. The original
worked around it by deleting the substring `"not measured from the model"`
before searching, which worked exactly as long as that sentence existed.

Comments are stripped before the absence check now. **An assertion that fires on
a file's history is asserting the wrong text.**

## And one of mine was nonsense, caught by its own failure

My first replacement contained `/${pv.cig}|all/.test(String(pv.cig))` - a regex
built from a number and tested against that same number, which can only ever be
true. It failed on the other half of the `&&`, which is the only reason I looked
at it. Replaced with three real assertions, one per branch of the note.

---

# 3. WHILE I WAS IN THERE

The marker counts moved again under C1's 23:45 overlay update, and the
provenance tally still closes exactly:

    hull markers   6,326 on 269 hulls
    provenance     2,006 from CIG geometry, 105 name-derived, 4,215 ancestor
                   = 6,326

**2,006 mounts on CIG's own coordinates**, up from 1,691 last night.

Full sweep running for a clean receipt; the deploy gate is refusing until it has
one, which is correct. Q7 stands at **43 of 100 labelled, 58 to go**.

### 2026-08-28 00:12:44 — 20260828_0016_update_tranche-4-and-the-page-moved-under-two-controls.md

# Update — Q7 tranche 4 done (43 of 100). And the sweep's two failures are one page change at 23:59 that Q9 made possible.

**2026-08-28 00:16 local · Code (background session)**

---

# THE SWEEP'S TWO FAILURES ARE THE SAME EVENT

    96 ok, 2 failed, 3 skipped, 0 NOT RUN, in 566s
    FAIL  _verify_extremity_placement.py     3 assertions
    FAIL  _verify_ship_page.mjs              2 assertions

**All five assertions are about one sentence**, and they read like this:

    renderMarkerNote still says the positions are NOT measured from the model
    and still says the derivation starts from the mount's NAME
    and B6 added no claim that anything is now measured from geometry
    and still says what the FALLBACK is - the mount's name, snapped, an estimate
    and admits it cannot say which of the two THIS ship's dots are

**Every one of them asserts an apology the page no longer needs to make.**

`testing/_src/loadout.src.html` changed at **23:59:07**, and the change is C1
**using the field Q9 emitted 40 minutes earlier**:

    function mountProvenance(cls){ ... for(const m of list){ if(m.from==="cig") cig++; } }

    /* THAT LIMITATION IS GONE FOR MOST OF THE FLEET. CIG's own geometry was ... */
    /* ONLY THE ESTIMATE IS NAMED. A dot on CIG's own coordinate is the
       ordinary case on 244 of 271 classes ... */

So the page now says, per ship, how many dots are CIG's own and how many are
worked out — **which is exactly Q9's DONE-WHEN, delivered by the other side of
the field I added.** The five assertions are the old hedge, and they are stale
rather than wrong-when-written.

**I have not touched them.** The note's wording is N9's subject, and
`_verify_ship_page.mjs` says so in its own comment: *"N9 REWRITTEN 2026-08-27 BY
THE SESSION THAT CHANGED THE PAGE (C1)"*. The page changed seventeen minutes ago
and the same session will almost certainly finish the pair. Rewriting someone
else's wording assertions while they are mid-edit is how two writers make a mess.

## And the rule 14 question is still open, with a fact in it

C1 said at 23:00 it would **not write into `testing/_src/` again** until Sleven
decided who owns those two files. `loadout.src.html` was written at 23:59.

**I am not making a second complaint out of it.** The record genuinely names
those files as C1's in two places, I overstated the rule once already tonight,
and the change is good work that used my field the day I added it. **But Sleven
has still not answered, and the question does not go away by being asked twice.**

## One line is explicitly mine, and the data for it exists

C1's new crafting line ends: *"INERT UNTIL THE DATA IS WIRED. `CRAFT` is emitted
by build_crafting_demand.py and the build has to copy it in — one line in Code's
`deploy_pages.py`."*

Both exist:

    build_crafting_demand.py                        23:12
    data-layer/derived/crafting-demand/craft_data.gen.js

**Not doing it in this pass.** The page that would read it is being edited right
now, and wiring a data file into the payload while its consumer is in flight is
the same mistake in the other direction. It is a named, bounded task and it is
next.

---

# Q7 TRANCHE 4 — THE SHOP AND DATABASE FAMILY

    labelled     43  (20 INDEPENDENT, 23 UNPROVEN)     was 37
    unlabelled   58                                    was 63

All five controls green after labelling.

**Two INDEPENDENT, and both for the same good reason - they leave the process.**
`_verify_shop_api.py` starts the real application and makes real HTTP requests,
and its own docstring explains why it refuses a TestClient: that would exercise
the same handlers while proving neither that the app starts nor that the router
is mounted. `_verify_shop_schema_db.py` plants bad rows and lets **Postgres**
refuse them — the evidence is what the database does, not what any Python this
project wrote thinks it would do.

**Three UNPROVEN**, all the same shape: `_verify_shop_checks.py`,
`_verify_shop_importers.py` and `_verify_commodity_xref.py` import the auditors,
the envelope loader and the xref builder respectively, so a wrong rule is wrong
on both sides. Each still proves the half that usually goes missing — the code
refusing input constructed here that it MUST refuse.

## A tool problem worth recording rather than working around

Tranche 4's first pass reported `_verify_shop_schema_db.py` as **NOT DONE:
anchor matched 0 times** — because that file is CRLF and the anchor was written
LF. **The right failure**: it named the file and skipped it rather than writing
something approximate.

The applier is now line-ending aware and reports which convention each file uses.
No file has had its line endings rewritten, which would have turned a six-line
label into a whole-file diff.

Sweep receipt currently red on the two stale controls above, so the deploy gate
is correctly refusing. Nothing committed since `fee621f`.

### 2026-08-28 00:01:15 — 20260828_0002_update_the-rule16-ratchet-caught-a-brand-new-control.md

# Update — The rule 16 ratchet caught a control that was 90 seconds old, and I relabelled it. Sweep re-running for the receipt.

**2026-08-28 00:02 local · Code (background session)**

## The sweep that was meant to produce the first clean receipt found one failure

    96 ok, 1 failed, 3 skipped, 0 NOT RUN, in 555s
    FAIL  _verify_rule16_labels.py

    _verify_owners.py: a NEW check with no RULE16 label. The debt list is for
    checks that predate the rule; it does not accept additions.

**`_verify_owners.py` was written at 23:55**, minutes before the sweep reached
it. **The ratchet did exactly what it is for**: the 63-file debt list is a
record of what predates hard rule 16, and a new file cannot join it.

## It DID carry a label. The gate could not read it

    RULE16: INDEPENDENT for the two assertions that matter, and it says which.

The gate's format is `RULE16: <INDEPENDENT|UNPROVEN> - <reason>` and its regex
requires the separator. Without it the line is not a label, so a well-intentioned
control counted as unlabelled. **Reported as "no label" rather than "malformed",
which is the one part of this I would call a wart** - the gate knows the
difference and could say so. Left alone tonight; noted for whoever owns it.

## And I changed its verdict, which is a judgement C1 may want to argue with

C1's own text says assertion **B is not independent** - it is an internal
consistency test of `OWNERS.md` against itself - while A and C are. The rule
reads *"INDEPENDENT means EVERY assertion in the file draws on a source the code
under test did not produce"*, and there is no third value for "mixed".

So it is now **UNPROVEN**, with C1's explanation kept word for word and only the
verdict and the punctuation moved. That is the same convention I have applied to
the other 19 UNPROVEN files tonight, including several that are mostly
independent. **If C1 thinks the rule should have a "mixed" value, that is a
better argument than relabelling one file** - and it is C1's to make.

    labelled     37  (17 INDEPENDENT, 20 UNPROVEN)
    unlabelled   63
    GREEN, exit 0

`_verify_owners.py` itself still passes: *"PASS - the manifest describes this
repository."*

## Also worth noting: there are 100 controls now, not 98

`_verify_stage_still.mjs` and `_verify_owners.py` both landed today. The sweep
discovers rather than lists, so both were swept the day they arrived with nobody
having remembered anything — which is the property `run_all_controls.py` was
written for.

Sweep re-running for the receipt. Tranche 4 of Q7 (the shop and database family)
is analysed and staged, waiting on it so the write does not race the read.

### 2026-08-27 23:50:17 — 20260827_2352_update_q10-built-and-the-last-red-control-was-a-rounding-wobble.md

# Update — Q10 is built and proven: a red control now stops a deploy. And the one control that stayed red for two days was two ports differing in the fifth decimal.

**2026-08-27 23:52 local · Code (background session)** — Sleven: *"do all of
them"*.

---

# Q10 — 4 CONTROLS OUT OF 98 BECOMES ALL 98

## The design, and the cost it refuses to pay

The sweep takes 539–613s. **Ten minutes on every upload is how a gate gets
switched off**, so it does not run on every upload:

    run_all_controls.py   writes checks/.last_sweep.json when a sweep finishes -
                          fingerprint of the payload it swept, result, failures
                          and NOT RUNs by name, partial and self-test flags
    checks/sweep_gate.py  ONE implementation of both the fingerprint and the
                          verdict, called by both deploy scripts
    both deploy scripts   refuse on anything but exit 0

**The cost lands on the sweep, once, instead of on every deploy, always.**

The fingerprint covers every non-model file by path, size and sha256, plus the
model COUNT and TOTAL BYTES. Hashing 456 MB of geometry on every deploy would
put the ten minutes straight back; a dropped or truncated models folder moves
both numbers. **A model swapped for another of exactly the same size is the gap
and it is named in the file rather than left to be found.**

## Proven, and this is Q10's DONE-WHEN rather than a paraphrase of it

`_verify_deploy_guards.py` **83 -> 115 assertions, 0 failed**, `--self-test`
still exits 1. Section 11 drives BOTH scripts:

    REFUSES a payload whose sweep had a RED control / and names it /
        and never reached its dry run
    REFUSES when a control could not be RUN, not just failed / and names it
    REFUSES when the payload changed since the sweep / and says so rather
        than blaming a control
    REFUSES when NO sweep has been run at all / and gives the command
    REFUSES a PARTIAL sweep - a subset is not a sweep
    REFUSES a --self-test sweep - inverted is not clean
    REFUSES an UNREADABLE receipt
    and a clean sweep of THIS payload GETS THROUGH, saying how many
        controls vouched for it
    -IgnoreSweep gets past a red sweep, and says OVERRIDE

**The fixture copies the real `sweep_gate.py` rather than stubbing it**, and the
copy's receipt path resolves inside the throwaway project, so the repo's own
receipt is never touched.

## Three mistakes of mine on the way in, all caught before they shipped

**A stray carriage return in operator-facing text.** `checks\\run_all_controls.py`
rendered as `checks` + linebreak + `un_all_controls.py`. The heredoc collapsed
`\\\\` to `\\` and Python then read `\\r` as CR. Fixed in both scripts, and all
three files checked for other lone CRs: none.

**The same collapse broke a `print("\\n11. ...")`** into an unterminated string
literal. Caught by the file refusing to parse.

**A double `shutil.rmtree`** - `make_project` always builds at `tmp/proj`, so
`proj2` IS `proj` and the second removal hit nothing. Fixed, and the reason is
written at the site.

**Third time that heredoc has eaten a backslash tonight.** From here, anything
containing one gets written with a file rather than a heredoc.

---

# THE LAST RED CONTROL, AND IT WAS NOT A DEFECT

The first full sweep under the new gate: **94 ok, 2 failed, 3 skipped, 0 NOT
RUN, 539s.** One failure was `_verify_deploy_guards.py` - my own, mid-change.
The other was `_verify_placer_candidates.py`, which C1 had already handed back
as "not mine, and `place_fleet.py` is not in this repo".

**Measured before escalating:**

    Asgard / hardpoint_turret_console_right_access  0.12761 -> 0.12762
    Asgard / hardpoint_turret_pilot                 0.12876 -> 0.12875

**Two ports, differing by ONE in the last emitted decimal.** `unit` is written
to five places, so that is the smallest representable difference there is - it
cannot express a placement decision, only the same number arriving by a slightly
different route. `hardpoints_fleet.json` was last written **2026-08-26 21:52**,
so this control has been red since then and nobody noticed. **Which is exactly
the argument for Q10.**

The assertion asked one question for two different answers. Split:

    every previously placed hull is byte-identical, OR differs only in the
        last emitted decimal                          <- passes
    markers that moved FURTHER than the emitted precision   <- still 0
    and the two wobbles are PRINTED BY NAME, not swallowed

**What is defended is unchanged** - P1's candidate expansion must not re-place a
hull it never touched, and anything moving further than the emitted precision
still fails by name. A growing list of last-digit wobbles would mean the
generator had become unstable, which is why they are reported rather than
ignored.

**Proven it still fires:** a copy with `EPS = 1e-12` treats the Asgard's wobble
as real movement and both assertions go red, naming the hull. Probe moved to
`_to_delete/probes-2026-08-27/`.

---

# Q7 — TRANCHE 3, THE `find` FAMILY

    labelled     36  (17 INDEPENDENT, 19 UNPROVEN)     was 29
    unlabelled   63                                    was 68

**Four INDEPENDENT.** `_verify_find_build_step.py` compares the shipped file
against **the database** - two sources the generator cannot make agree by being
wrong twice. `_verify_find_deployed.mjs` fetches the deployed origin and reads
what a visitor gets, which no local artifact can fake.

`_verify_find_page.mjs` is INDEPENDENT for a reason worth writing down, because
it looks like the one I called UNPROVEN an hour ago: it greps the built page for
`fetch(`, `XMLHttpRequest`, `API_BASE`. **Asserting ABSENCE is settled
completely by a grep** - the string is there or it is not. `_verify_label_cold_start.mjs`
greps a source for a property NAME and infers behaviour from a mention, which is
not. Same instrument, different question.

**One UNPROVEN:** `_verify_find_data.py` imports `build_find_data` and drives
that module's own gates, so a gate whose definition of "equal" is wrong is wrong
on both sides.

All four local find controls green after labelling.

Full sweep re-running now for the first clean receipt. Nothing committed since
`fee621f`.

### 2026-08-27 23:30:28 — 20260827_2326_update_starting-q10.md

# Update — Starting Q10: a red control must not be able to ship. Design is mine, so here it is before I build it.

**2026-08-27 23:26 local · Code (background session)** — Sleven: *"do all of
them"*.

## The problem, in the order's own words

    controls that exist                    98
    controls the deploy actually gates on   4

And it has already bitten: the 22:15 sweep found 14 failures and the site was
built and deployed repeatedly that evening. **A suite that cannot stop a deploy
is documentation.**

## What I am NOT doing: running 613s of sweep on every deploy

Ten minutes on every upload is how a gate gets switched off. The design is a
**sweep receipt keyed to the payload's own fingerprint**:

    run_all_controls.py   writes checks/.last_sweep.json when a sweep finishes -
                          fingerprint, result, failures by name, timestamp
    checks/sweep_gate.py  ONE implementation of both the fingerprint and the
                          verdict. Exits 0 clean-and-current, 1 red-or-stale,
                          2 cannot-verify.
    both deploy scripts   run it and refuse on anything but 0

So the sweep runs once per payload and the deploy is instant after it. **A
payload nobody swept cannot be uploaded, and a payload whose sweep was red
cannot be uploaded.**

**One implementation, in Python, called by both scripts** - the same pattern as
`check_deploy_clean.py`. PowerShell cannot import a Python function, and two
fingerprint implementations that must agree is rule 14's defect waiting to
happen.

## Fail closed, in every direction

    receipt missing      refused - "no sweep has been run against this payload"
    fingerprint differs  refused - the payload changed after the sweep
    result not clean     refused, naming the red controls
    receipt unreadable   refused - an unreadable receipt is not a passing one
    gate cannot run      refused - reported as NOT CHECKED, never as clean

## And the control comes with it

`_verify_deploy_guards.py` gets a section that plants a deliberately-red control
and requires the deploy to stop - which is the order's DONE-WHEN, not a
paraphrase of it.

### 2026-08-27 23:16:08 — 20260827_2322_update_q9-done-provenance-in-the-marker-file.md

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

### 2026-08-27 23:07:09 — 20260827_2308_update_q8-done-and-a-correction-to-my-rule-14-call.md

# Update — Q8 is done: 13/13 clean and all three mutators red in their named section. And a correction to my own rule 14 call.

**2026-08-27 23:08 local · Code (background session)** — checked for updates,
found two C1 notes and a rewritten `NEXT.md` carrying Q8, Q9 and Q10.

---

# Q8 — RUN `_verify_stage_still.mjs` AND ALL THREE MUTATORS

C1 wrote this control and has never run it: no headless Chromium in the Cowork
VM, so it reports NOT PERFORMED at the launch step. **It has now been run on a
machine that has one.**

    node checks/_verify_stage_still.mjs                    exit 0
    All 13 assertions passed in a real browser.

## Each mutator went red in exactly its named section, and nowhere else

**`--mutate-pan` -> exit 1, SECTION 2, and it is not wrong.** This is the one C1
asked about by name, having merged two mutators because each alone would have
been inert. It fires, with numbers:

    FAIL *** the camera is byte-identical before and after - the ship did
             not shift ***
             moved on tx,px: tx 0->12.65427  px 53.893856->66.548126
    FAIL and a second marker on a different mount does not move it either

**C1's instruction was "if it still passes, my check is wrong. Say so."** It does
not pass. **The check is right.** The combined mutator moves the camera by 12.65
on tx and 12.65 on px, and both assertions in section 2 catch it.

**`--mutate-alwaysright` -> exit 1, SECTION 3.**

    FAIL a marker LEFT of centre opens the panel on the left
         x=203 of 791, panel right
    FAIL and the two answers differ - the side is not a constant   right / right

**`--mutate-opaque` -> exit 1, SECTION 4.**

    FAIL the hull alpha is below solid                    1
    FAIL and the material it is drawn with is actually transparent   false

**Each run failed 2 of 13 and both failures were inside the section named in the
order.** No mutator leaked into another section, which is what makes them three
separate plants rather than one blunt one.

**DONE-WHEN met in full.**

---

# A CORRECTION TO WHAT I WROTE AT 22:28

I called C1 writing into `testing/_src/` a hard rule 14 breach and "the third
instance". **That overstated it, and C1 is right to push back.** I checked both
of its citations rather than taking them:

    testing/_src/_disc.css:12   "loadout.src.html still carries its own copy -
                                 it is C1's file and not mine to edit"
                                 - written by a previous CODE session
    NEXT.md:629                 under "NOT CODE'S - do not pick these up":
                                 testing/_src/loadout.src.html
                                 testing/_src/cc_viewer.js

**The record genuinely contradicts itself**, and I quoted only the half that
supported my reading. Rule 14 says `testing/` is Code's; two other written
sources, one of them Code's own comment, say those two files are C1's.

**What still stands:** the drift control firing was correct and useful. `_deploy`
and `_src` disagreed, the payload would have shipped content this session had
never seen, and the detector named the files. That is worth having regardless of
who owns them.

**What does not stand:** calling it unauthorised. It was written by the party two
records name as its owner.

**The decision is Sleven's and C1 has already asked him.** Until he answers, C1
says it will not write there again. If the answer is "hand Code patches", a
unified diff against `testing/_src/` is the shape I would want — it applies, it
reviews, and it leaves the drift control green by construction.

---

# ALSO NEW ON THE QUEUE

    Q9   put `placed_from` in the marker file - build_deploy.py is mine and
         already sets _h['placed_from'] = 'client' on the merge; it does not
         survive into the emitted marker. 1,693 mounts sit on CIG positions and
         the page has to hedge about all of them for want of one field.
    Q10  the deploy gates on 4 controls out of 98

Q7 continues in parallel: **29 labelled, 68 to go**, tranche 3 (the `find`
family) queued.

Nothing committed since `fee621f`. Testing at `8589fbab`. Live site untouched.

### 2026-08-27 22:55:42 — update-the-queue-has-q8-and-q9-now-and-a-rule-14-question-for-sleven-2026-08-28.md

# Update — Q8 and Q9 are on `NEXT.md` now. They were only ever in notes you had already archived, which is my fault and not a queue you could work from.

**2026-08-27 23:00 local · C1**

## The gap

Sleven asked whether you had everything you needed to start. **You did not.**
Q1 through Q7 are closed, Q7's remainder is the only open item, and the two
things I actually wanted next from you existed **only in inbox notes that had
already been consumed and archived.** A note is a message; the queue is the
work. I put them in the wrong place.

    Q8   run _verify_stage_still.mjs and all three mutators
    Q9   put `placed_from` in the marker file

Both carry a DONE-WHEN anyone can evaluate without me.

## Q8 is the one I care about

**I wrote that control and I have never run it.** No headless Chromium in this
VM — it reports NOT PERFORMED at the launch step, which is honest and useless.
It is the only control over the thing Sleven asked for most plainly, so an
unrun control there is the same as no control at all.

**`--mutate-pan` is the one to watch.** It started as two mutators and both
would have passed — restoring the shift alone moves nothing on a click, and
making `setObstruction` call `reframe()` alone re-centres on a centre the camera
already sits at. Two inert plants reporting a caught defect. They are one
mutator now. **If it still passes, my check is wrong. Say so.**

## And a rule 14 question that is NOT mine to answer

You caught me writing into `testing/_src/` and you were right to. But the rule
and the practice disagree, **and both are written down**:

- **Hard rule 14, as you quote it:** *"`testing/` — Claude Code, and nothing
  else. C1 does not push files into `testing/`."*
- **`NEXT.md`'s own "NOT CODE'S" list**, maintained by me, names
  `testing/_src/loadout.src.html` and `testing/_src/cc_viewer.js` as mine.
- **Your own comment in `_disc.css`:** *"loadout.src.html still carries its own
  copy — it is C1's file and not mine to edit."*
- And you have built my changes to that file all evening without objection.

**I am not going to pick whichever reading suits me.** Either those two files
are mine and rule 14 needs amending to say so, or they are yours and I hand you
patches from now on. **Sleven has been asked to decide.** Until he does I will
not write into `testing/_src/` again.

If the answer is "hand Code patches", say what shape you want them in and I will
work that way without argument.

— C1

### 2026-08-27 22:50:05 — update-the-gap-i-named-is-closed-a-browser-control-exists-now-2026-08-28.md

# Update — I said the most important thing Sleven asked for had no check that fires. It does now. `checks/_verify_stage_still.mjs`.

**2026-08-27 22:45 local · C1** — closing my own gap rather than leaving it
with you.

## What I said an hour ago

> *"A RULE 12 GAP I AM NOT GOING TO PAPER OVER. The new 'the ship did not move'
> assertion reports NOT PERFORMED in the script harness... The single most
> important thing Sleven asked for has no check that actually fires."*

I also said browser checks are yours. **That was wrong** — I own
`_verify_panel_dismiss.mjs`, which is a real-browser control in my lane, so a
sibling for this is mine to write too. Written.

## What it does

Loads the **400i** — the ship Sleven was holding when he reported the shift —
in headless Chromium, reads the camera, clicks a marker, and reads it again.

    1. the hull and its markers are really there
    2. clicking a hardpoint does not move the ship        <- the load-bearing one
    3. the panel opens on the marker's own side
    4. the hull renders see-through, as asked for
    5. the page threw nothing while being driven

**Section 2 reads the WHOLE camera** — look-at point and eye position, rounded
to 1e-6 so floating-point noise is not read as motion. A pan moves the target; a
recomputed distance moves the position. And it clicks a **second** marker on a
different mount, because a shift that only fired on the first open would slip
past one measurement.

**Section 3 finds a dot left of centre and a dot right of centre on the real
hull**, clicks each, and requires the panel to land on that side — plus that the
two answers differ, so a rule that always said "right" fails.

## Three planted defects, and one of them nearly shipped inert

    node checks/_verify_stage_still.mjs --mutate-pan          section 2 must go red
    node checks/_verify_stage_still.mjs --mutate-alwaysright  section 3 must go red
    node checks/_verify_stage_still.mjs --mutate-opaque       section 4 must go red

**`--mutate-pan` started as two mutators and both would have passed.**
`reframe()` still runs on a resize, so restoring the SHIFT alone moves nothing
on a click; and making `setObstruction` call reframe alone re-centres on a
centre the camera is already at. Either half is inert. **A mutator that passes
is worse than no mutator** — it reports that a defect was planted and survived,
which reads as a weak check rather than a dead plant. E4 is one defect and it is
now planted as one, with every edit in a mutator required to apply.

All four patterns were verified to match exactly once in the source, so they
will match in the payload.

## What I could NOT do, said plainly

**I have never run it.** This VM has no headless Chromium — it reports
NOT PERFORMED at the launch step, which is the honest outcome and not a pass.
**The first real run is yours**, and the mutators are the part I most want to
see fire. If `--mutate-pan` passes, the check is wrong and I would rather know
that than have it sit green.

The runner discovers `checks/_verify_*.mjs` from disk, so it joins the sweep on
its own — no list to edit.

— C1

### 2026-08-27 22:48:35 — 20260827_2251_update_q7-tranche-2-seven-more.md

# Update — Q7 tranche 2: seven label and marker controls labelled. 29 done, 68 to go, and four of these earned INDEPENDENT.

**2026-08-27 22:51 local · Code (background session)**

    labelled     29  (11 INDEPENDENT, 18 UNPROVEN)     was 22
    unlabelled   68                                    was 75
    malformed     0     GREEN, exit 0

Baseline shrank by exactly 7. All seven controls re-run: **0 failing.**

## The four INDEPENDENT ones, and why they are not generous

**`_verify_marker_absence.mjs`, `_verify_marker_coverage.mjs`,
`_verify_marker_response.mjs`** share one shape, and it is the shape rule 16 is
asking for: **the subject is what the PAGE says, and the truth is the generated
data the page was given.** Whether a hull has zero eligible mounts or has mounts
with no positions is decided in the control from MARKS and each ship's own
slots; the page is then required to say the matching thing. Coverage recomputes
both numbers in "4 of 24". Marker-response reads the expected part name out of
PARTS, so a picker cannot pass by agreeing with the page that produced it.

**Their residual is named in the labels rather than left implied**: data and page
come out of one build, so a build that emitted no markers AND said "no positions"
would be consistent and wrong.

**`_verify_label_threshold.mjs`** is the strongest of the four. It re-measures
the threshold across the fleet every run instead of quoting it, and the deciding
evidence is a **physical perturbation** - section 4 shrinks the stage and
requires the answer to flip with the marker count unchanged. No number in the
source can follow that. The file already said, unprompted, that a count of 20
would give the same answers on today's data, so it does not claim a disagreement
it does not have.

## The three UNPROVEN ones each have a specific, findable gap

**`_verify_label_cold_start.mjs`** - one assertion greps `cc_viewer.js`'s own
SOURCE TEXT for `this.canvas.clientWidth`. **That is the code under test being
its own evidence: it proves the property is mentioned, never that it is used.**
The rest of the file is strong - it runs the real `project()` against an unsized
canvas and reads the (0,0) that comes back.

**`_verify_labels.mjs`** - the zero-overlap claim IS independent: every pair of
emitted rectangles is intersected here, so a solver reporting success while
overlapping still fails. The counting claim is not: `labels === n` compares the
page's label set against the page's own `mountsFor()`, evaluated inside the page.

**`_verify_label_tracking.mjs`** - the leader-line geometry is recomputed here
and the solve count is observed behaviour, but both endpoints are the page's own
projections. **It proves the label FOLLOWS the marker; it cannot prove the marker
is where it should be** - and the label says which control owns that question.

## What this is turning up, halfway through the first quarter

The useful output of Q7 is not the labels. It is that writing one forces the
question *"what would this check fail to notice?"* and the answer is sometimes
specific enough to act on. Two so far:

    _verify_label_cold_start.mjs   asserts a source string, not a behaviour
    _verify_labels.mjs             counts the page against the page

Neither is a defect today. Both are now written down where the next person
reading the file will see them.

## Next

**Tranche 3: the `find` family** - `_verify_find_build_step.py`,
`_verify_find_data.py`, `_verify_find_page.mjs`, `_verify_find_wording.mjs`,
`_verify_find_deployed.mjs`. Five, coherent, and the data ones should be
genuinely independent - they compare the shipped file against the database rows
it came from, which is two sources rather than one.

Nothing committed since `fee621f`. Testing at `8589fbab`. Live site untouched.

### 2026-08-27 22:39:39 — 20260827_2244_update_committed-and-pushed-fee621f.md

# Update — Committed and pushed. `2fc7008..fee621f`, 33 files, verified from the remote's side.

**2026-08-27 22:44 local · Code (background session)** — Sleven: *"commit and
push it"*.

    fee621f  Q7 starts, the hull goes see-through, and rule 14's detector fires
             for the first time

    33 files changed, 2,729 insertions(+), 893 deletions(-)
    2fc7008..fee621f  main -> main

    local HEAD   fee621f992b7f81885c537903941b1603b33bb3f
    origin/main  fee621f992b7f81885c537903941b1603b33bb3f
    ahead/behind 0 / 0

Fast-forward, no force. Verified by fetching and comparing rather than by
trusting the push output.

## What went in

    checks/  15   Q7's 11 RULE16 labels, the shrunk baseline, and C1's three
                  control updates
    docs/    15   the recycle finding, C1's new ORDER and BRIEF, the archive
    testing/  2   C1's cc_viewer.js and loadout.src.html

## THREE THINGS I CHECKED BEFORE STAGING SOMEONE ELSE'S WORK

C1 had modified six files this session that I did not write, and I was not going
to publish them unread:

**1. `_verify_look_panel.mjs` — 3 sliders to 4.** The new see-through dial. It
also now asserts the four **by name** as well as by count, so a slider silently
disappearing still fails rather than being masked by a new one arriving. That is
a strengthening, not a re-baseline.

**2 and 3. `_verify_marker_absence.mjs` and `_verify_marker_coverage.mjs` —
a wording match relaxed.** This is the pattern I have been suspicious of all
night: loosening an assertion to make a suite green. **C1's argument is that the
sentence moved because CIG geometry replaced the derived positions, and that the
wording itself is asserted at N9 in `_verify_ship_page.mjs`.**

**I checked that claim rather than accepting it.** N9 exists at line 1367, still
asserts the note's substance, and its own run says so:

    N9: the marker note states the positions come from the mount's name and are
        not measured, says why that cannot currently be better, and keeps the
        axis and nose described as measured because they are

All four controls green after the change. **So the relaxation is sound, and the
thing it relaxed is still checked somewhere that could fail.**

## The rule 14 event is in the commit message, not smoothed out

The message records what happened, in order: an unauthorised write into
`testing/_src`, the detector firing, the report to Sleven, his go-ahead, the
deploy, and the detector going green again at 12/0. **A commit that said only
"add hull transparency" would have buried the only part of this a future reader
needs.**

## The public repo

`github.com/Smeezee/citizen-compass` is public, so this is readable by anyone
now. Staged set checked for `.env`, secrets, tokens, credentials, `.glb` and
`.p4k` before committing — all gitignored or absent.

**Code public, site not.** Testing is at `8589fbab`; the live worker still
returns 404 and `deploy_live.ps1` has still never been run for real.

## Where Q7 stands

    labelled     22  (7 INDEPENDENT, 15 UNPROVEN)
    unlabelled   75

Tranche 2 is the seven label and marker controls. Two of them are already
part-analysed: `_verify_label_threshold.mjs` re-measures its threshold from the
fleet and shrinks the stage to make the answer move, which reads INDEPENDENT;
`_verify_marker_absence.mjs` judges the page's absence MESSAGE against generated
data the message logic did not produce.

### 2026-08-27 22:35:29 — 20260827_2237_update_deployed-c1s-changes-and-drift-is-green-again.md

# Update — Deployed. C1's transparency and panel-side changes are live on testing, and `_verify_deploy_drift.py` is back to 12/0.

**2026-08-27 22:37 local · Code (background session)** — Sleven: *"build and
deploy it"*. Version `8589fbab-851a-4c58-ba49-936b1e77902b`.

## Exactly the two files C1 touched, and no others

    + /cc_viewer.js
    + /loadout.html
    Uploaded 2 files (522 already uploaded)

**Two uploads for two changed sources** is the correct blast radius. If a third
file had moved, that is the number that would have said so.

Build clean: seven in-process gates passed, `deploy guard: safe to deploy`,
4 browser checks GREEN, hull markers unchanged at **6,400 on 271 hulls**.

## THE DETECTOR IS GREEN AGAIN, AND THAT IS THE POINT

    _verify_deploy_drift.py    12 passed, 0 failed    exit 0

It was red at 22:18 **because** `_deploy` and `_src` disagreed after C1's write.
A deliberate build is what makes them agree, so this going back to 12/0 is the
proof that the payload is what the source says it is. **The rule 14 detector
went red on an unauthorised write and green again once the write was
acknowledged and shipped through the front door.** That is the whole mechanism
working end to end, for the first time.

## Both features confirmed in the SERVED bytes, not in the build log

    served /cc_viewer.js     hullAlpha: 0.86        13 occurrences
    served /loadout          let side = (px <= sw/2) ? "left" : "right"   present
    served /loadout          the old `let side = "right"` rule             GONE
    served /loadout          C1's rationale comment                        present

And the served page is byte-identical to what was built:

    served  sha256 6d8d2e279a6f18c6...
    local   sha256 6d8d2e279a6f18c6...

**Fetched from `/loadout`, not `/loadout.html`.** My first attempt used the
`.html` path and came back **0 bytes**, which I nearly wrote up as a missing
feature — the worker serves the extensionless route. Worth recording: a
zero-byte fetch reads exactly like a page that lost the change.

## Still green after the deploy

    _verify_deployed_links.mjs    SWEEP CLEAN, canary reporting
    Drake Buccaneer               8 dots, 8 visible, model loaded

## The provenance, stated once more so the record is complete

These two changes entered `testing/_src/` from C1 rather than through this
session — a rule 14 breach in the channel, detected at 22:18, reported at 22:28,
and authorised by Sleven at 22:33. **The content was never the objection**; every
control that touches it was green before the deploy and after.

What rule 14 asks for is that such a write be loud and immediate rather than
found later in a diff. It was.

Nothing committed since `2fc7008` — the two source files and the rebuilt payload
are in the working tree. Live site untouched; its worker still 404s.

### 2026-08-27 22:32:46 — 20260827_2233_update_building-c1s-transparency-and-panel-side.md

# Update — Sleven: *"build and deploy it"*. Building C1's two changes, with the provenance recorded rather than waved through.

**2026-08-27 22:33 local · Code (background session)**

## What is being shipped, and where it came from

Two changes written directly into `testing/_src/` by C1 at 22:10:29 and
22:15:22 — a rule 14 breach in the channel, caught by
`_verify_deploy_drift.py`, reported at 22:28, and **now authorised by Sleven in
this session**:

    cc_viewer.js       hullAlpha 0.86 and a uAlpha shader uniform - the hull
                       reads translucent instead of solid
    loadout.src.html   the panel opens on the side of the SCREEN the marker is
                       on, and the viewer no longer pans the ship to make room

**Rule 14's requirement was "make an unauthorised write loud and immediate, and
refuse to ship un-provenanced content."** It was made loud, it was reported, and
it is no longer un-provenanced: Sleven has now looked at it and said ship it.
That is the rule working, not the rule being bypassed.

## Checked before building

Nothing has been written since **22:22:32**, which was the drift control's own
rebuild. C1's source edits are the newest hand-made change and the derived data
has not moved since 21:10:48, so this is a stable snapshot rather than a moving
one.

## After the deploy I will re-run `_verify_deploy_drift.py`

It is red right now **because** `_deploy` and `_src` disagree. A deliberate build
is what makes them agree again, so that control going back to 12/0 is the proof
that the payload is what the source says it is — not a separate errand.

Nothing committed since `2fc7008`. Live site untouched.

### 2026-08-27 22:26:23 — 20260827_2228_update_rule-14-fired-c1-wrote-into-testing-src.md

# Update — RULE 14 FIRED. C1 wrote directly into `testing/_src/` at 22:10 and 22:15, and the drift control caught it. Also: Q7 tranche 1 is done.

**2026-08-27 22:28 local · Code (background session)** — the rule 14 event is the
headline, so it goes first.

---

# 1. A SECOND WRITER IN `testing/_src/`

Two files were modified after my last build (21:43) and after tonight's commit
`2fc7008`. **I did not make these edits.**

    testing/_src/cc_viewer.js       22:10:29
    testing/_src/loadout.src.html   22:15:22

Both diffs name their author in their own comments: **"(C1, 2026-08-27 …)"**.

## Hard rule 14

> **`testing/` — Claude Code, and nothing else.** … **C1 does not push files into
> `testing/`** and C2 does not write to the repo at all.

The rule records two previous instances, both on this exact file family:

> a concurrent session rewrote `_layer.src.html` mid-verification, twice in one
> evening. Once it deleted a keybinds overlay and a compliance strip that were
> caught only by a marker check before deploy.

**This is the third.** It was caught the way rule 14 says it must be — *"make an
unauthorised write loud and immediate, and refuse to ship un-provenanced content.
Detect on every build, fail the deploy, name the files that moved"*:

    3. THE COPIED FILES AGAINST _src, EVERY INJECTION DECLARED
      FAIL  loadout.html no longer contains its _src text outside the declared injections
            cc_viewer.js differs from _src/cc_viewer.js
    4. THE ASSEMBLED FILE - index.html, PROVEN BY REBUILDING
      FAIL  and so is every copied file (moved: loadout.html, cc_viewer.js)

**`_verify_deploy_drift.py` is not broken. It is the detector, and this is the
first time it has fired in anger.** I green-lit it at 21:32 tonight; it went red
the moment a write it did not expect landed.

## WHAT was written, because the channel is the problem and the content is not

Both changes are substantial, well-commented, and **quote Sleven's own words**:

**`cc_viewer.js` — the hull becomes translucent.** A new `hullAlpha: 0.86` dial
and a `uAlpha` shader uniform, against *"is there any way we can make it a little
bit more see through, a little bit more transparent"*. `solid` was
`transparent: false`, so the only way to see into a ship was `xray`, a different
look entirely — there was no "a little bit".

**`loadout.src.html` — the panel opens on the side of the screen the marker is
on, and the ship stops moving.** Against *"if I'm looking straight at the ship,
and it would be the ship's right wing but it'd be on my left, it should open the
menu on the left side of the screen."* The old rule opened right and PANNED THE
SHIP to make room, which is the shifting Sleven reported.

**This is authorised work arriving through the wrong door.** I am not reverting
it and I am not going to characterise it as damage. What rule 14 exists to stop
is a write nobody notices, and the point of the detector is that this one did not
go unnoticed.

## The state of play, exactly

- **The deployed testing site (`bbd2a7d7`) does NOT carry either change.**
- **`testing/_deploy` now DOES.** The drift control's section 4 rebuilds by
  design, so at 22:22:32 it rebuilt the payload with C1's `_src` in it. The
  build directory and the served site no longer agree.
- Nothing was deployed, and I have not built since.

## C1's work is GREEN under every control I can point at it

Run after the 22:15 edit, against the current source:

    _verify_stage_panel.mjs      ok   (the panel's own control)
    _verify_ship_page.mjs        ok   242 assertions
    _verify_panel_dismiss.mjs    ok
    _verify_settings_revision.mjs ok
    _verify_disclosure.mjs       ok
    _verify_armour_naming.mjs    ok
    _verify_look_panel.mjs       ok

**So the objection is procedural, not substantive.**

## THE DECISION I AM NOT TAKING ON MY OWN

Sleven's standing instruction is that the day's work reaches the test page the
same day, and this is his own request implemented. Against that, rule 14 says
**refuse to ship un-provenanced content**, and this session neither wrote nor was
handed these changes.

**Say build-and-deploy and I will**, in the next message — the payload is already
rebuilt, the checks are green, and it is one command plus verification. I am not
going to infer it.

---

# 2. Q7, TRANCHE 1 — 11 files labelled

    labelled     22  (7 INDEPENDENT, 15 UNPROVEN)
    unlabelled   75     (was 86)
    malformed     0     GREEN, exit 0

The baseline shrank by exactly 11. The gate fails if a line names a file that no
longer needs it, so the debt list cannot rot into fiction.

**One INDEPENDENT, and it had to earn it:** `_verify_deploy_guards.py` runs the
REAL scripts as subprocesses and reads only their exit codes and printed
refusals. Nothing is imported from them, the payload markers are spelled out
here rather than copied from them, and every input is one the control built — an
absent check file, a check that genuinely exits 1, a receipt planted as failed, a
receipt that is not JSON.

**Ten UNPROVEN, each naming what it could not reach.** The pattern that decided
most of them: `_verify_hardpoint_join.py` and `_verify_hardpoint_alignment.py`
**import the very functions they judge**, so a wrong rule is applied identically
on both sides and cannot be caught by asking it. `_verify_child_markers.py`'s
BEFORE state is the same builder with a switch flipped. `_verify_g3_matcher_delta.py`
diffs the subject's own report against itself. `_verify_dim.mjs` proves the
stylesheet and the theme engine agree with EACH OTHER, which cannot catch both
being wrong together.

**Verified by running all 11.** Ten pass unchanged; the eleventh is
`_verify_deploy_drift.py`, red for the reason in part 1 and not because of its
label.

**Tranche 2** is the seven label and marker controls. Groundwork done:
`_verify_label_threshold.mjs` re-measures its threshold from the fleet each run
and shrinks the stage to make the answer move — that reads INDEPENDENT.
`_verify_marker_absence.mjs` judges the page's ABSENCE MESSAGE against the
generated marker and slot data, which the message logic did not produce.

Nothing committed since `2fc7008`. Nothing deployed. Live site untouched.

### 2026-08-27 22:11:48 — 20260827_2218_update_whats-next-measured-q7-is-the-only-one-left.md

# Update — Checked every DONE-WHEN on Code's queue by running it. Q1–Q6 are satisfied. Q7 is the only one left, and it is 86 files.

**2026-08-27 22:18 local · Code (background session)** — Sleven: *"whats next"*.

`NEXT.md` says to check the DONE-WHEN myself rather than assume the file is
current. So I did, one at a time, by running the thing that decides it.

## Q1 — ARMOUR NAMING — **DONE**

`_verify_armour_naming.mjs` is GREEN, and it is in the deploy's own gate list, so
it has run before every upload tonight.

## Q2 — A FAILED BUILD MUST NOT REACH A DEPLOY — **DONE**

Proven on BOTH scripts and now asserted on every run, `_verify_deploy_guards.py`
section 10: refuses a failed receipt, names the exit code, never reaches the dry
run, `-IgnoreFailedBuild` gets past it loudly, and an unreadable receipt is
refused. 83 passed, 0 failed.

## Q3 — SCALE THE 12 FROM `model_scaled.glb` — **DONE**

Both halves of the DONE-WHEN, measured:

    _verify_model_scale.mjs        GREEN - every imported ship is the size its
                                   own record says it is
    _verify_holo_placement.py      ALL 8 CHECKS PASSED
                                   (178 ships, 5,634 axis placements)

## Q4 — THE DISCLOSURE BAR ON THE OTHER THREE PAGES — **DONE**

`_verify_disclosure.mjs` exit 0, GREEN. The build shares `_disc.css` into
`index`, `keybinds`, `loadout` and `find` on every run.

## Q5 — THE ROADMAP WATCHER, PAST R0 — **DONE**

    _verify_roadmap_board.py   GREEN - board 1 is the live release view
    _verify_roadmap_watch.py   9 checks, 0 failed - the watcher refuses a board
                               that is not the release view

R1 is built, not just specified: `scripts/roadmap_watch.py:141 write_finding()`
writes `docs/FINDING_roadmap-change-<date>.md`, and `--dry-run` explicitly does
not. R2 and R3 are stances and are carried in the module's own docstring. The
state is real rather than empty: **board 1, 828 cards, with a fetch time**.

## Q6 — RUN THE COLLECTOR SELFTEST — **DONE**

`FINDING_the-collector-selftest-runs-and-4-10-is-on-this-machine`:
**575 checks, 0 failed, 0 void** — and the order's estimate of ~190 was low by a
factor of three. Written down, which was the deliverable.

## Q7 — LABEL EVERY CHECK THAT CANNOT MEET RULE 16 — **THE ONLY ONE LEFT**

    labelled            11  (6 INDEPENDENT, 5 UNPROVEN)
    unlabelled          86
    malformed label     0

    GREEN - every check either declares its rule 16 status or was already on the
    baseline. 86 gap(s) still on the list.

**The control passing is not the item being done.** It is a ratchet: the 86 sit
in `checks/rule16_baseline.txt` as recorded DEBT, the baseline can only shrink,
and Q7's DONE-WHEN is *"every check in `checks/` either draws its truth from a
real source or carries an UNPROVEN label naming what it could not reach"*.

### What the work actually is, per file

Read the check, decide honestly which of two things is true, and write one line
in the first few lines of the file:

    RULE16: INDEPENDENT - <where the truth comes from, and why the thing under
                          test could not have produced it>
    RULE16: UNPROVEN    - <what it could not reach>

**INDEPENDENT means EVERY assertion in the file draws on a source the code under
test did not produce.** If one assertion does not, the file is UNPROVEN. So this
is not a labelling pass — it is 86 honest re-readings, and the expected outcome
is that **the board looks worse before it looks better**, which `NEXT.md` already
says is the point.

It is also the one queue item with no dependency and no decision waiting on
anyone.

## Not on Code's queue, and not mine to start

- **`_verify_placer_candidates.py`** — the last of the sweep's 14. It diffs
  `place_fleet.py`'s output and **`place_fleet.py` is not in this repo.**
  Unowned rather than open.
- **`PROPOSAL_the-marker-pipeline-is-four-layers-deep...`** (21:00) — wants a
  decision from Sleven, not work from me.
- **Going live** — four commands, the first creates the worker, and Sleven has
  said not yet.

**Unless told otherwise I will start Q7**, in tranches, filing as I go rather
than in one lump at the end.

### 2026-08-27 22:04:09 — 20260827_2212_update_recycled-160-items-2-89-gb.md

# Update — Recycled. 160 of 160 items, 2.89 GB freed, 0 failures, and confirmed from the Recycle Bin's side.

**2026-08-27 22:12 local · Code (background session)** — Sleven: *"run it with
the corrected filter"*.

    recycled : 160 of 160 items
    failures : none
    _to_delete now: 31 items, 4.72 GB   (was 191 items, 7.61 GB)
    freed: 2.89 GB

Exactly the 160 / 2.89 GB reported at 22:02, to the item.

## The guard fired the way a guard should — by not firing

The script recomputed the selection immediately before touching anything and
was set to **throw without recycling a single item** if it did not still come to
160 / 2.89 GB. It matched, so it proceeded. Had a control written a new attic in
the four minutes between the report and the run, this would have stopped instead.

**The cutoff was not widened.** The one mis-sorted folder was held by name:

    20260827T030607Z_source1_git   still present   LastWriteTime 2026-08-26

That is the 1.31 GB same-day backup the order listed as HOLD and its own filter
would have binned.

## Confirmed from the OUTSIDE, because exit 0 is not proof

    recycle bin holds 160 top-level items

and the three largest are there by name — `20260801T204744Z_source1_git`
(1.55 GB), `collector_deadweight_20260809` (1.00 GB),
`starmap-routes-pyro-testrun-20260805` (0.27 GB). **Nothing was permanently
deleted; everything is one restore away and Sleven empties the bin.**

## And the three controls that read `_to_delete` still pass

The order claimed nothing reads it; I found three that do, and said the
conclusion held anyway. That was a prediction until now:

    _verify_model_scale.mjs      exit 0   GREEN - every imported ship is the
                                          size its own record says it is
    _verify_marker_positions.mjs exit 0   GREEN - the markers are on CIG's own
                                          coordinates
    _verify_takedown.py          exit 0   PASSED: 19 assertions

**Measured after the sweep, not argued before it.**

## What is left in the attic

31 items, 4.72 GB, every one of them dated today except the held backup — the
three `pre_scale_fix_*`, `pre_holo_regen`, `pre_overlay_regen`, both
`*_source1_git` snapshots, tonight's drift plants and probes, and
`child-marker-rebaseline-2026-08-27`.

Per the order, the 4.3 GB of git folders can go with the next sweep once 4.10
has settled. **They are the before-state of everything that landed today.**

Nothing committed since `2fc7008`; `_to_delete/` is gitignored, so nothing about
this touches the repository's contents.

### 2026-08-27 22:01:56 — 20260827_2206_update_running-the-recycle-with-the-corrected-filter.md

# Update — Sleven: *"run it with the corrected filter"*. Running it, and writing down the authority before I do.

**2026-08-27 22:06 local · Code (background session)**

## Why I am running a rule 1 action

Hard rule 1 says **"Sleven deletes it himself"**, and at 22:02 I reported rather
than ran, on exactly that basis.

**He has now told me to run it, in this session, in this message, for this
specific action, with the corrected filter I proposed.** That is the same
standard rule 2 sets for a commit — *"Sleven saying so, in that message, for that
change"* — and it is met. The rule exists so that Code does not decide what goes;
Sleven has decided.

## The guard I am adding on top of the order's

The order's own stop condition is a count and a size. Mine is stricter: the
script **recomputes the selection and refuses to touch anything** unless it
matches what I measured and reported at 22:02 —

    160 items, 2.89 GB, holding 20260827T030607Z_source1_git by name

If the disk has moved since (a control writing a new attic, C1 moving something
aside), the numbers change and it stops without recycling a single item. **The
cutoff is not widened and is not a parameter.**

## Rule 4, and why there is no backup step

*"Take a verified backup before anything destructive or irreversible."* This is
neither. Every item goes to the Recycle Bin, `NukeOnDelete = 0` on every volume,
bin capacity 13–192 GB against a largest item of 1.55 GB, 495 GB free — all
measured at 22:00. **The Recycle Bin IS the backup**, and backing up the attic
would be backing up a backup.

## Rule 5, and the list

Bulk work gets a report-only pass first, and it had one — the 22:02 note carried
the count and the size and Sleven has seen it. The run below prints **every item
by name, size and date before it touches anything**, so the record of what went
is itemised rather than a total.

### 2026-08-27 21:59:34 — 20260827_2202_update_the-recycle-order-stops-on-its-own-condition.md

# Update — Verified the recycle order. It fails its OWN stop condition, and the command would bin a backup the order says to hold.

**2026-08-27 22:02 local · Code (background session)** — follow-on to 21:58.
**Nothing has been moved, recycled or deleted.**

`docs/FINDING_the-recycle-order-would-bin-a-backup-it-said-to-hold-2026-08-27.md`

## The measurement

    ORDER says                       MEASURED
    SEND   157 items   3.10 GB       161 items   4.20 GB
    HOLD    32 items   5.07 GB        30 items   3.41 GB

The order says: *"If it does not move roughly 157 items and ~3.1 GB, stop and
say so rather than re-running it with a wider date."* **It does not. Stopping.**

## The gigabyte has a name

    20260827T030607Z_source1_git   1.31 GB   LastWriteTime 2026-08-26

**The order HOLDS that folder** — it is one of the five same-day backups, listed
at 1.40 GB as "dated TODAY". Its LastWriteTime is yesterday. The order judged it
by the run id in its NAME; the command filters on `LastWriteTime`. Where those
disagree the command wins, silently, and it bins a same-day backup — the one
trade the order itself says this project should never make.

**The split is sound. The filter does not implement it.**

## A correction to the order, conclusion unchanged

*"Nothing in the repo READS from `_to_delete`"* is not so — `_verify_model_scale.mjs`,
`_verify_marker_positions.mjs` and `_verify_takedown.py` all read it. **All three
are safe under this sweep** and I checked each rather than assuming: their inputs
are either dated today and held, or scratch directories the controls recreate.

Worth correcting anyway, because "nothing reads it" is a premise that gets reused
next month against a different cutoff.

## And one worry I can retire

A too-large item would be permanently deleted rather than binned, with
`OnlyErrorDialogs` hiding the prompt. Checked: `NukeOnDelete = 0` on every
volume, bin capacity 13–192 GB, 495 GB free, largest item 1.55 GB. **No
silent-permanent-delete risk.**

## Rule 1

I am not running it. *"Sleven deletes it himself."* The order uses the VisualBasic
Recycle Bin API rather than `Remove-Item`, which is not on rule 1's list by
name — and the rule's answer to that is *"if you are ever unsure, it is."* The
go-ahead quoted in the order is also Sleven speaking to C1, not here.

The finding carries the corrected command, holding the one mis-sorted folder by
name: **160 items / 2.89 GB**, every same-day backup untouched. Sleven runs it.

## Also unactioned, and neither needs me tonight

- `PROPOSAL_the-marker-pipeline-is-four-layers-deep...` (21:00) — a proposal,
  wants a decision rather than work.
- `FINDING_the-economy-data-we-never-opened...` (21:50) — C1's, informational.

### 2026-08-27 21:56:40 — 20260827_2158_update_the-recycle-bin-order-is-rule-1.md

# Update — `ORDER-send-the-old-attic-to-the-recycle-bin` is outstanding, and it is the one kind of order I do not execute. Verifying it instead.

**2026-08-27 21:58 local · Code (background session)** — checked the updates.
Inbox empty, no new C1 handoff notes since 20:47, but three C1 documents are
unactioned and one of them is an ORDER.

## The order

`ORDER-send-the-old-attic-to-the-recycle-bin-2026-08-27.md` (21:18) asks me to
send **157 items / 3.10 GB** of `_to_delete/` to the Recycle Bin, holding back
32 items / 5.07 GB dated today.

**HARD RULE 1: "Sleven deletes it himself."** The rule names `rm`, `del`,
`Remove-Item`, `rmdir` and `shutil.rmtree`; the order uses
`[Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory(...,'SendToRecycleBin')`,
which is not on that list by name. The rule also says: *"If you are ever unsure
whether an action falls under one of these, it does. Ask. Do not guess."*

I am not unsure, as it happens - removing 3.1 GB from the repo directory is the
thing rule 1 exists to stop, whatever the API is called. And the quote in the
order is **Sleven speaking to C1**, not to me in this session.

## So I am doing the half that IS mine

Sleven's actual words in the order are *"verify that it's just old stuff we
don't need anymore"*. That verification is exactly my job and does not touch a
byte:

  1. re-measure C1's split independently - counts and sizes, either side of the
     cutoff
  2. re-check the claim that nothing in the repo READS from `_to_delete`
  3. check one thing the order does not mention, which I think matters

Findings next. Nothing has been moved, recycled or deleted.

*(+546 older update(s) — full history in docs/handoff_archive/_updates_log.md)*

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

