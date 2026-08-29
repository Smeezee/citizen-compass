# NEXT — the standing work queue

**One writer: C1.** Code never edits this file. Code reports completion in its
own handoff update, and every item's DONE-WHEN is written so anyone can tell it
is finished without asking C1.

**If C1 is mid-task, asleep, or wrong, the queue still advances.**

---

## HOW TO USE THIS

**Sleven:** *"check the updates"* or *"go"*.

**Code, after every unit of work:** read this file, take the FIRST item whose
DONE-WHEN is not satisfied and whose BLOCKED-BY is clear — **checking the
DONE-WHEN yourself, not assuming the file is current**. Report before writing,
rule 5. Do it. File the handoff. Come back.

**A stale queue is a normal condition, not an error.** If the top item is done
and this file has not caught up, say so and take the next one.

**If an item is wrong, ambiguous, or badly prioritised, say so and take the next
one.** Code has been right against C1 four times on 2026-08-27, most recently
proving Q3's premise was hollow. The list exists so Code does not have to build
it, not so it can overrule Code.

**Anything not on this list and not asked for by Sleven directly is a
suggestion, not work.**

---

# SLEVEN'S RULING, 2026-08-27 14:10 local

> *"I want whatever's next. It all has to be done."*

**There are no decision gates on this queue any more.** The three items that
were waiting on him are decided:

- **Which front gets finished** — all of them, in the order below. C1 does not
  ask again.
- **The Windows runner** — settled by doing. Run the collector selftest and
  find out what actually fails. It is Q3 on Code's list, not a question.
- **Hard rule 16** — adopted. A check draws its truth from a different source
  than the thing it checks, or it is labelled UNPROVEN and says what it could
  not reach.

**Going live is NOT on this queue and will not be raised again until Sleven
raises it.** He has said the site is not ready. He is the one who knows. C1
turned an outside session's recommendation into pressure and that was wrong.

---

# CODE'S QUEUE

## Q20 — COMMIT AND PUSH TODAY'S WORK. **SLEVEN SAID YES, 2026-08-29.**

**He was asked directly and answered yes.** That is the go-ahead rule 1 requires,
and it covers **committing and pushing to GitHub only** — not the live site,
which stays where it is.

    504 files uncommitted, everything since 1a1b4b7 yesterday morning

**NEVER `git add -A`.** Stage by path, the way you did for `1a1b4b7`.

**CHECKED BEFORE ASKING, so you do not have to re-derive it:**

    _to_delete/            gitignored - confirmed. It holds 5.2 GB, including
                           C1's model tarballs. It must not enter a commit.
    *.tgz, *.glb, models/  nothing of that kind is staged
    the only oddity        data-layer/derived/holo-hardpoints/
                           loadout_marker.pre-C1-20260829.js - your backup.
                           Your call whether it belongs in the history.

**AND ONE THING THAT WOULD HAVE STOPPED YOU DEAD.** C1's `git status` left a
`.git/index.lock` behind — the Cowork mount cannot delete files, so git could
not clean up after itself. It has been moved to `_to_delete/git-locks/`.
**If a git command ever fails with `Unable to create '.git/index.lock'`, that is
why, and moving the file is the fix.** C1 will stop running `git status` on that
mount.

**What is in this commit, in one line each** — the day is large and the message
should say so:

    the heap fix          10 hulls were drawing every dot in one clump, labelled
                          as CIG's own coordinates. Placement now refuses a model
                          it cannot orient. Root cause found and NOT fixed - see
                          the finding, it is a node-transform bug in glb_box.
    the deploy gate       proven on a real collision, then fixed twice: it
                          refused by crashing, and the control could not tell
    OWNERS.md             ownership became machine-readable; rule 14 enforced
    four new controls     marker provenance, marker census, marker spread,
                          identical options, swap loop
    Q7                    104 of 105 checks labelled for rule 16
    the contact sheet     295 ships photographed twice and every dot measured
                          against a clean silhouette of its own hull

**Verify after:** `git log --stat -1` names only files you expect, and nothing
under `_to_delete/`. **Nothing goes to the live site.** Going live is still off
the queue until Sleven raises it himself.

**ONE MORE PLACEMENT CHANGE LANDED AFTER THIS ITEM WAS WRITTEN — rebuild with
it.** The acceptance test now checks the FORE/AFT axis, which it never did.

The old comment said testing it "would be marking our own homework, because the
fore/aft axis is where the scale came from". **That reasoning is wrong.** The
scale comes from the MODEL'S BOX against CIG's published Length; it is not
derived from any mount position, so asking whether a mount lands beyond the nose
is a real question with an answer that is not true by construction. **A mount
can only leave the hull in three directions and one of them was unwatched.**

Measured across 26,273 mounts: 93 fall outside fore/aft, and **7 are EXTERIOR
mounts that actually get drawn.** The Banu Defender's two countermeasure
launchers sit at 1.32 of its own half-extent — confirmed by photograph, floating
in open space off the nose — plus the Hull C's nose turret and four on the M80,
which is already refused for orientation.

    cost   3 mounts withheld on 2 hulls. Both hulls still pass; the
           withholding is bounded by WITHHOLD_MAX exactly as before.
    gain   the last two of the four off-hull hulls found by photography

Derived data is regenerated and C1's five controls are green. **The deployed
marker file still carries the offending dots until you rebuild.**

## THE BOARD, RECONCILED 2026-08-28 EVENING — READ THIS FIRST

**The queue had gone stale enough to waste your time.** Eight items were finished
and still reading as open. This is the state of every one, checked rather than
remembered, against a sweep that ran **105 of 105 green with 0 skipped and 0 not
run**.

    OPEN, IN THE ORDER I WOULD DO THEM
      Q7    the last 23 rule-16 labels          81 of 104 done
      Q15   clearTimeout in _loadout_harness    one line
      Q5    roadmap watcher R1-R3               only R0 is done
      Q13   point drift detection at OWNERS.md
      Q3    STATUS UNKNOWN - its DONE-WHEN names
            `checks/_verify_holo_placement.py`, which does not exist.
            Say what happened to it before doing anything.

    DONE, DO NOT RE-DO
      Q1    armour naming        _verify_armour_naming.mjs green
      Q2    failed build blocked  superseded by Q10's gate, proven on a real collision
      Q4    disclosure bars       _verify_disclosure.mjs green
      Q6    collector selftest    575 checks, 0 failed, on Windows 2026-08-27
      Q8    stage-still + mutators  C1 ran it in a real browser
      Q9    placed_from in markers
      Q10   the deploy gate       and it caught a live collision today
      Q11   craft_data wired      it is in the deployed payload
      Q12   the 41 hulls verified C1 photographed all 295 ships, 0 failures
      Q14   N9 assertions removed _verify_ship_page.mjs 242 green
      Q16   the rebuild
      Q17   identical-options line  built, deployed, verified on the served site
      Q18   deployed-site controls  ran, 3 of 3 passed

**Q12 is closed by a contact sheet, not by a check.** Every ship with a model —
295 of them — was loaded in a real browser and photographed with its markers
showing. **2,309 dots, 0 failures. 26 ships show no dots and 25 have at least
one estimated dot.** Sleven has the sheet and is reviewing it. **Ships with no
hardpoints are DEFERRED by his instruction** — finish everything else first.

**Nothing here is committed.** 174 files, all of today. Committing is fine when
you reach a clean stopping point; pushing to the live site is not, and going
live is still off the queue until Sleven raises it.


### Q1 — 31 SHIPS PRINT ANOTHER SHIP'S NAME ON THEIR ARMOUR. LIVE AND VISIBLE.
**DONE-WHEN** the armour heading is derived from the SHIP, not from the item's
own `Name`, and no ship page prints an armour name naming a different ship.
**BLOCKED-BY** nothing. **This jumps the queue: it is on a page people look at.**

Source: `HANDOFF_weapon-armour-shield-package-for-c1-2026-08-27.md` (C3),
measured on disk, every claim naming its file.

`build_loadout_data.py:740` takes the armour's display name from the item's own
record, and **that field carries the wrong ship's name on 31 of 91 named armour
records - 34%.**

    ARMR_RSI_Perseus       prints  "Constellation Andromeda Ship Armor"
    ARMR_AEGS_Idris_P      prints  "Hammerhead Ship Armor"
    ARMR_ORIG_890J         prints  "350r Ship Armor"

**Scope it honestly: the NUMBERS ARE RIGHT.** The page resolves armour through
each ship's own `Loadout`, so no ship is showing another ship's multipliers.
It is a labelling bug. **But it is on a page whose entire claim is that the
numbers can be trusted, and it says the wrong ship's name out loud.**

**DO NOT FIX THIS BY CORRECTING 31 STRINGS.** Derive the name from the ship.
C3's join is a literal dictionary lookup on a UUID string - wiki
`vehicle.armor.uuid` against `stdItem.UUID` - **285 of 285, 100%, no
normalisation, no lowercasing, no token containment, no fuzzy anything.** It
also covers the 118 placeholder records, which correcting strings never would.

Spot check to reproduce before trusting it: Avenger Stalker →
`b3b23908-e9ab-4c46-93ed-ecd20aaf65c3` → `ARMR_AEGS_Avenger_Stalker` →
Deflection Physical 11 / Energy 9. Both sources agree on every value.

**The control: assert that no rendered armour heading names a ship other than
the one whose page it is on.** That check must go red on the current build -
if it does not, it is not testing the defect.

**Read §7 and §8 of the handoff before starting.** C3 records one thing it got
wrong (Deflection was already built) and that every number in it is **patch
4.9**. And §3 says to CANCEL any "compare shields by damage type" feature -
there is nothing to show. Do not build it.

### Q2 — A FAILED BUILD MUST NOT REACH A DEPLOY
**DONE-WHEN** a build that exits non-zero cannot be followed by an upload in
the same invocation, and the refusal names the build's exit code.
**BLOCKED-BY** nothing.

Found by Code on itself, 2026-08-27: build and deploy chained in one command,
`BUILD EXIT=1` printed, deploy read only its own output and put twelve wrong
models live. **The check Code had written was green, so the thing being watched
agreed with him, and the gate that disagreed was in the output he skipped.**

Q4 put the BROWSER checks in front of the upload. Nothing puts a FAILED BUILD
in front of it, **and a deploy legitimately does not require a build** - so the
gate cannot simply be "a build must have run". It has to be: *if a build ran in
this invocation and failed, stop.*

**The control: chain a deliberately-failing build to a deploy and assert the
upload does not happen.**

### Q3 — SCALE THE 12 FROM `model_scaled.glb`, NOT FROM `model.glb`
**DONE-WHEN** the 12 pre-existing wrong-scale models are at their published
dimensions AND `_verify_holo_placement.py` still passes all 8 checks.
**BLOCKED-BY** nothing. **C1 has ruled - see the reasoning below.**

Code's finding: he rescales from `sc-ships/<ship>/model.glb`, but the deployed
model came from `model_scaled.glb`, and **for some ships those two are not the
same geometry.** Scaling the original therefore produced a hull with a
different bbox centre and half-extent ratio than the markers were derived
against - San'tok.yai off by 29.6%, Vulture 8.5%.

**Scale from `model_scaled.glb`.** It preserves the exact geometry every
downstream artifact was derived against: the hull-geometry boxes, the marker
`unit` values, C1's hardpoint placement scale, and the camera-fit band. The
alternative - rescale then regenerate - is a four-step chain, and for hulls
with no real CGA coordinates it would re-derive GUESSES against a moved hull,
which is churn without gain.

**And the cost of the safe option is zero.** Code's own words: the 12 being
wrong-scale *"is visible to nobody - the viewer frames the camera to whatever
it loads."* There is no reason to take the risky path for an invisible defect.

### Q4 — THE DISCLOSURE BAR ON THE OTHER THREE PAGES
**DONE-WHEN** `_verify_disclosure.mjs` is green with every explanation block on
`find`, `keybinds` and `index` collapsed, and D1 still green.
**BLOCKED-BY** nothing.

The loadout page is the reference implementation and it is built and deployed.
**Eleven amber blocks remain** — keybinds x5, index x4, find x2.

**Audit each one against the rule before touching it, and record the verdict
per block.** Collapse a block that EXPLAINS. Never collapse one that WARNS,
reports an ERROR, or states WHAT THE VISITOR IS LOOKING AT. The download
page's antivirus notice, find's error and empty states, and the keybinds
capture warnings are all NEVER. **A block collapsed that should not have been
is a warning nobody reads.**

### Q5 — THE ROADMAP WATCHER, PAST R0
**DONE-WHEN** R1-R3 of `AMENDS_roadmap-watcher-board-1-is-wrong-2026-08-27.md`
are built and the watcher reports a real board state.
**BLOCKED-BY** nothing. R0 is done — the board is identified.

Key on card presence plus a payload hash. **Never on `updateDate`** — the API
returns Aug 2024 for a card the UI renders as Aug 2021.

### Q6 — RUN THE COLLECTOR SELFTEST. FIND OUT WHAT FAILS.
**DONE-WHEN** `go build` and `.\collector.exe --selftest` have been run and the
result is written down — pass, fail, or could-not-run with the reason.
**BLOCKED-BY** nothing.

**~190 checks have never been executed once.** That is why `capture_keys`
shipped dead in every build. The old reason was that no Claude session could
run a Windows binary — **that is stale for Code**, which ran
`venv\Scripts\python.exe` and `powershell` today.

**Do not write another collector check until these run.** If they cannot run,
the reason is the deliverable.

### Q19 — REBUILD ONCE MORE, AND ONE OPTIONAL FIX THAT IS YOURS
**DONE-WHEN** a rebuild has run against today's placement and
`_verify_marker_provenance.py` and `_verify_marker_spread.py` both exit 0.
**BLOCKED-BY** nothing. **Two controls are RED and both are stale-build, not
defects — read this before treating either as breakage.**

**WHAT HAPPENED.** Ten ships were drawing every hardpoint dot in a single clump
the size of a cockpit, and the page labelled all of them `cig` — CIG's own
published coordinates. The Tiburon put all seventeen in one heap.

**Four green controls let it through.** Containment passed, because a heap is
inside the box. The mirror passed, because a heap is symmetric. Provenance
passed, because the labels honestly described where the numbers came from. The
census passed, because nothing was lost. **It took photographing all 295 ships
to see it.**

The cause: the scale rule matches CIG's Length to the model's Z extent, and **19
of 258 models measure taller than they are long** — the Mantis is 1680 x 2965 x
630. On those the scale came off the wrong axis.

**Placement now refuses a model it cannot orient.** You rebuilt at 03:18 against
an earlier, two-signal version of that guard; it has since been made strict, so
the derived data no longer carries Pitbull, Railen, San'tok.yai, Reliant, M80 or
Starlite and **the deployed marker file still does.** That is the entire content
of both red controls. One rebuild clears them.

    python checks/_verify_marker_provenance.py    expect 0 after the rebuild
    python checks/_verify_marker_spread.py        expect 0 after the rebuild
    python checks/_verify_marker_spread.py --self-test   expect NON-ZERO

**Every marker loss is already declared in `checks/marker_census.json` with the
reason**, so the census will report them and not block you.

**ONE CONTROL OF YOURS NEEDS ITS BASELINE MOVED, AND ONLY YOU SHOULD DO IT.**
`_verify_child_markers.py` asserts *"every marker that existed before is still
there, unmoved"* and is now red, naming the Tiburon, the Railen, the Reliant
Kore, the Khartu-al, the San'tok.yai and the rest. **It is right.** Those markers
were removed on purpose — they were the heap — and its baseline predates the
removal.

C1 has not touched it. Re-baseline it against the rebuilt payload, and **read
the list it prints before you do**: every name on it should be one of the 16
orientation-refused hulls. If any other ship appears there, something else moved
and that is the finding, not the baseline.

**THE ROOT CAUSE IS FOUND AND DELIBERATELY NOT FIXED, WHICH IS WORTH YOUR
JUDGEMENT.** The placer reads the model's box from raw accessor bounds and
ignores node transforms; three.js applies them. On a rotated model the two are
different objects:

    Mantis.glb   raw accessor bounds   1680.4 x 2964.9 x 629.8
                 with node transform      30.0 x    6.4 x   17.0
    CIG's own dimensions                 30.0 /   17.0 /    7.5

The transformed box matches CIG's published Length and Width **exactly**. C1
implemented the transform and reverted it: applying node scale also changes the
box for every model carrying a `CC_SCALE_ROOT`, and the run that followed refused
the Vulture, the Polaris and the Starlancers — **200+ working hulls destabilised
to rescue 16.** It needs a change-and-compare loop across all 295 ships, which is
a session's work with a build in it, and the build is yours.

## THE OPTIONAL PART, AND IT IS GENUINELY YOURS

**The M80 and the Starlite heap on the page and pass the placer's own
measurement.** The placer measures every mount; the page draws one dot per mount
ROOT and picks the shallowest. A couple of outliers the visitor never sees push
the placer's number above the line.

**The right place for that test is the emitter, where PortIds exist** — the
grouping the page uses cannot be reconstructed from CIG node names in the
overlay, and I am not going to approximate it. That is `build_deploy.py`, which
is yours.

Roughly: group the emitted markers by `PortId.split(".")[0]`, take the shallowest
of each, and if a hull's drawn dots span less than 0.47 of it while its model
measures taller than it is long, drop that hull's CIG markers and let it fall
back to estimates. **`_verify_marker_spread.py` already computes exactly this**
and will tell you if you have it right.

**Take it or leave it.** The control catches them either way; the difference is
whether the sweep goes red or the build quietly does the right thing.

### Q7 — LABEL EVERY CHECK THAT CANNOT MEET RULE 16
**DONE-WHEN** every check in `checks/` either draws its truth from a real
source or carries an UNPROVEN label naming what it could not reach.
**BLOCKED-BY** Q6 for the collector's set.

Rule 16 is adopted. This is the cost of adopting it, and it makes the board
look worse before better — that is the point. A silent gap becomes a labelled
one.

**Standing at 2026-08-27 22:51: 29 labelled, 68 to go, 0 malformed.**

### Q8 — DONE 2026-08-28 BY C1, IN A REAL BROWSER. NOT YOURS ANY MORE.
**Do not run this. It has been run.** Clean and all three mutators, in headless
Chromium, on the 400i.

    clean                    13 of 13 assertions pass
    --mutate-pan             2 red - camera moved tx 0 -> 12.65, px 53.9 -> 66.5
    --mutate-alwaysright     2 red - a LEFT marker opened the panel right
    --mutate-opaque          2 red - hull alpha 1, material not transparent

**Each mutator went red in its own section and nowhere else.** The thing Sleven
asked for most plainly — *"I really want the ship to stop shifting"* — is now
proven, not asserted: the camera is byte-identical before and after a marker
click, and a second marker on a different mount does not move it either.

**HOW, because the reason C1 could not do this for two days was wrong in a way
worth writing down.** The blocker was never "no browser". It was three things
that each looked like the same wall:

    checks/.playwright-browsers holds a WINDOWS headless shell   cannot exec on Linux
    the Cowork VM's allowlist refuses cdn.playwright.dev         cannot download one
    C1's own container HAS Chromium, at a path and build number
      playwright will not find by itself                         cannot launch it

**One environment variable closed it.** `_verify_stage_still.mjs` now honours
`CC_CHROMIUM` (executable path) and `CC_NO_SANDBOX`. Unset, behaviour is
identical to before, so nothing about your runs changes.

    CC_CHROMIUM=/path/to/chrome CC_NO_SANDBOX=1 node checks/_verify_stage_still.mjs

**SEVEN OF THE NINE PLAYWRIGHT CONTROLS NOW RUN AWAY FROM YOUR MACHINE** and
all seven pass: `_verify_stage_still`, `_verify_armour_naming`,
`_verify_disclosure`, `_verify_settings_revision`, `_verify_panel_dismiss`,
`_verify_marker_positions`, `_verify_camera_framing` (34 assertions).

**The two that do not are honest about why:** `_verify_model_scale` and
`_verify_imported_models` need the whole 458 MB model library, not a sample.
Those stay yours until somebody decides that transfer is worth it.

**The other six checks launch Playwright with a hardcoded path and were run in
C1's sandbox with a symlink rather than by editing your files.** If you want
them portable too, the same two lines drop into each — C1 has not touched them.

### Q9 — PUT `placed_from` IN THE MARKER FILE — DONE, AND IT WAS WRONG ON 41 HULLS UNTIL 04:45
You built it and it works. **C1 then measured what it emitted and found the
field lying about 41 hulls**, which is on C1, not on you — the emitter reads
`placed_from` correctly and nothing was writing it for those records.

`build_deploy.py` stamps `placed_from` in one place: the loop that MOVES an
existing marker onto an overlay position. **41 hulls never enter that loop** —
they have no marker record to move a port on, so they arrive as whole records
through `fleet_records_client.json`, already on CIG's decoded coordinates, and
the stamp never touched them. 335 CIG-published mounts across 57 page classes
reached the visitor labelled `est`.

**Fixed in `build_hardpoint_overlay.py` (C1's file), not in yours.** It now
stamps `"placed_from": "client"` on the records it emits — the field you already
read. **No change to `build_deploy.py` and none wanted.**

Your rebuild has already picked it up. Measured on the emitted file:

    cig  1,691 -> 2,026        est  448 -> 113        anc  4,261 unchanged
    page classes with every top-level mount on CIG coords   205 -> 244
    page classes with none                                   45 -> 6

Full working: `docs/FINDING_the-page-called-335-cig-mounts-estimates-2026-08-28.md`.

### Q12 — DONE 2026-08-28 BY C1. ALL 295 SHIPS, NOT JUST THE 41.
**Do not run this.** Every ship with a model was loaded in headless Chromium and
photographed with its markers rendered — the served page, not a model of it.

    295 ships photographed    2,309 dots drawn    0 failures
    26 ships show no dots     25 have at least one estimated dot

Sleven has the contact sheet. **Ships with no hardpoints are DEFERRED on his
instruction** until everything else is finished — do not start on them.

The original text follows for the record.

### Q12 (ORIGINAL) — PUT THE 41 CLIENT-RECORD HULLS THROUGH THE BROWSER CONTROL
**DONE-WHEN** the 41 hulls that arrive through `fleet_records_client.json` have
been through `_verify_marker_positions.mjs` (or whatever it has become), and the
result is in a handoff by name.
**BLOCKED-BY** nothing. It needs a browser, which is on your machine.

**WHY.** `checks/_verify_marker_provenance.py` — new, green, self-test decisive
— proves every one of the 2,026 mounts the page calls CIG's **sits on its own
hull's CIG coordinate**. It proves nothing about whether that coordinate renders
where the mount actually is. `_verify_marker_positions.mjs` covers the 166
overlay hulls; **the 41 client-record hulls have never been through it**, and
they are exactly the ones whose provenance was wrong for a day.

That is not a caveat to file. It is the thing that would catch a 42nd hull
arriving mis-scaled with a confident `cig` label on every dot.

**Also run it once with the new control:**

    python checks/_verify_marker_provenance.py              expect exit 0
    python checks/_verify_marker_provenance.py --self-test  expect NON-ZERO

**The self-test's exit code is inverted on purpose** and the banner says so —
`run_all_controls.py --self-test` requires a non-zero exit from every control.
It returns 9 when both mutations are caught and **0 when a control has gone
inert**, which is the outcome to be alarmed by.

**ORDERING, so nobody reads this as a deadlock.** `sweep_gate.py` stops an
unswept payload from uploading, and a fresh control can only go green against a
freshly built payload. **Build, then sweep, then deploy.** If the sweep is run
against a stale `_deploy/`, this check reports the defect it was written for and
is correct to. Do not silence it to clear a board.

### Q13 — POINT YOUR DRIFT DETECTION AT `OWNERS.md`
**DONE-WHEN** whatever fired on 2026-08-27 at 22:10 and 22:15 reads
`OWNERS.md` to decide whether a write was a collision, and stays quiet for a
write by that path's declared owner.
**BLOCKED-BY** nothing.

**WHAT HAPPENED AND WHOSE FAULT IT WAS.** Your detector fired on C1's writes to
`testing/_src/cc_viewer.js` and `testing/_src/loadout.src.html`. **Both were
already C1's** — in `NEXT.md` and in `CURRENT-STATE.md`, for weeks. **Your
detector was right to fire and right by accident**: it had no way to know, and
neither list was in a form a program could read. That is C1's fault, not yours.

**Fixed.** `OWNERS.md` is now the single machine-readable manifest —
`## <OWNER>` headings, four-space-indented paths, one entry per path. The prose
list in `NEXT.md` is **deleted**, not duplicated, and
`checks/_verify_owners.py` fails if it grows back.

    python checks/_verify_owners.py              expect exit 0
    python checks/_verify_owners.py --self-test  expect NON-ZERO

It found two real problems on its first run: a path C1 had guessed at that does
not exist, and eleven entries where the prose list had fallen behind. That is
the whole argument for the file.

**If you disagree with an ownership line, say so in a handoff and do not edit
around it.** Moving a path between owners is a decision and goes in a dated
`docs/DECISION_*`.

### Q14 — DELETE THE THREE MARKER-NOTE ASSERTIONS FROM `_verify_ship_page.mjs` N9
**DONE-WHEN** the N9 block no longer asserts the marker note's wording, and the
suite is green again.
**BLOCKED-BY** nothing. **Two N9 assertions are RED right now and that is
deliberate — read this before treating it as breakage.**

**WHAT CHANGED AND WHY IT HAD TO.** The marker note said *"this page cannot yet
tell you which of the two you are looking at on this particular ship"* — for a
full day after **you built the field that answers it**. Q9 gives every dot its
own provenance. The note is now per-ship and exact:

    all CIG's     "All 7 dots on this model come from the game's own geometry."
    a mixture     "12 of the 18 dots ... The other 6 have no position ..."
    none          "This dot is estimated."

and the six estimated dots on the Hammerhead say so in their own tooltip and
accessible name. **No sentence on the page quotes a fleet-wide number any
more.** A reader is looking at one ship.

**THE TWO RED ASSERTIONS ARE N9 DEFENDING THE OLD WORDING**, correctly, because
nobody told it. They are:

    /cannot yet tell you which/          now false on every ship
    /name/ && /snapped/ && /estimate/    now only true on ships that HAVE an
                                         estimated dot, which the all-CIG test
                                         ship does not

**DELETE THOSE TWO, AND THE THREE ABOVE THEM** (`note.length > 200`,
`game's own geometry`, `not estimated`). All five now live in
`checks/_verify_marker_note.mjs`, which C1 owns, and which asserts more than
N9 did: it computes the expected counts from `loadout_marker.gen.js` by
re-implementing its grouping rule, so the page and the check reach the number
by two routes.

    node checks/_verify_marker_note.mjs                      17 pass
    node checks/_verify_marker_note.mjs --mutate-fleetwide   7 must go red
    node checks/_verify_marker_note.mjs --mutate-blind       7 must go red
    node checks/_verify_marker_note.mjs --self-test          NON-ZERO

**KEEP THE REST OF N9.** Its three "the old sentence is gone from everywhere"
greps are still doing real work and are not duplicated anywhere.

**WHY C1 DID NOT JUST EDIT YOUR FILE.** N9's own header says it was rewritten by
C1 on 2026-08-27 — one artifact, two writers, which is what `OWNERS.md` and Q13
exist to end. Doing it again to save you five minutes would have been the fourth
time this project paid for that habit.

**AND A CONTROL CAUGHT ITS OWN AUTHOR AGAIN, worth two lines.** The first draft
of `_verify_marker_note.mjs` tested the note's HTML with regexes that could not
cross a line break, because the note is an indented template literal. That
showed up as one honest red assertion — **and as a silent GREEN one**, in the
section asserting a phrase was ABSENT. A regex that can never match passes every
negative test in a file. Whitespace is flattened once, at the top, now.

### Q15 — `clearTimeout` IS MISSING FROM `_loadout_harness.mjs`
**DONE-WHEN** the harness's window stub carries a `clearTimeout` and
`node checks/_verify_swap_loop.mjs` stops reporting two NOT PERFORMED lines.
**BLOCKED-BY** nothing. It is one line.

The stub has `setTimeout` and not `clearTimeout`. `markChanges()` calls
`clearTimeout(changedTimer)` **only when a timer is already pending** — which
means only on the SECOND stat change in a session. **Every existing control
makes one change and stops, so nothing has ever reached that line.**
`_verify_swap_loop.mjs` makes several and does.

The undo itself is unaffected — the build reverts correctly — but the render
after it is cut short, so anything read from the DOM afterwards is stale. That
control reports those two assertions as **NOT PERFORMED rather than failed**,
because reporting a harness gap as a page defect sends somebody after a bug
that is not there.

    clearTimeout: () => {},        // or drop the id from `timers`

**Worth a moment before you write it:** if the stub instead REMOVED the pending
callback, `flushTimers()` would stop running a callback the page had cancelled —
which is closer to a browser and would catch a different class of defect. Your
file, your call; a no-op closes Q15 either way.

### Q16 — REBUILD: THE PLACEMENT MOVED, AND ONE CONTROL IS RED UNTIL YOU DO
**DONE-WHEN** `build_deploy.py` has run against today's placement and
`python checks/_verify_marker_provenance.py` exits 0.
**BLOCKED-BY** nothing. **Read this before treating the red as breakage.**

The frame proof changed (M4). Three hulls moved: **the Glaive is in**, both
**Clippers are out**. `build_hardpoint_overlay.py` has been re-run and the
derived files are current; the DEPLOYED marker file is not.

So `_verify_marker_provenance.py` is red, naming the Clippers: their dots are
still in `loadout_marker.gen.js` labelled `cig`, and the hull that justified
that label is now refused. **That is the check doing its job — the page is
claiming CIG provenance for a hull we no longer stand behind.** It clears on the
rebuild.

**Ordering, again, because `sweep_gate.py` makes it matter: build, then sweep,
then deploy.** A control written against a fresh payload cannot go green against
a stale one.

**A second control now guards this rebuild, and it is the one the pipeline
proposal asked for.** `checks/_verify_marker_census.py` holds a per-hull marker
count recorded BEFORE your rebuild, and refuses on any hull losing dots.

    python checks/_verify_marker_census.py              expect exit 0
    python checks/_verify_marker_census.py --self-test  expect NON-ZERO

**The two Clipper losses are already declared in `checks/marker_census.json`
with the reason**, so they print every run instead of blocking you — a declared
loss stays visible, an absorbed one does not. **Anything else that loses markers
is not declared and will stop the run. That is the point.** Do not rebaseline to
get past it; `--rebaseline` prints what it is about to absorb, and absorbing a
loss is how a hull goes missing for a month.

This closes the stated precondition of
`PROPOSAL_the-marker-pipeline-is-four-layers-deep-2026-08-27` §3 — *"a control
that counts markers before and after and refuses on any loss... the condition of
doing it at all."* **The collapse itself is still Sleven's decision and has not
been made.**

### Q18 — RUN THE THREE DEPLOYED-SITE CONTROLS. THAT IS THE WHOLE ITEM.
**DONE-WHEN** `python checks/run_all_controls.py --include-deployed` has been
run and the three deployed controls have reported a real verdict.
**BLOCKED-BY** nothing. **It has never been blocked by anything.**

    python checks/run_all_controls.py --include-deployed

**WHAT THIS ITEM SAID AN HOUR AGO WAS WRONG, TOP TO BOTTOM, AND THE ERROR IS
WORTH MORE THAN THE ITEM.**

It claimed the testing site sits behind Cloudflare Access, that three controls
had never run because they could not authenticate, and it sent Sleven into the
Cloudflare dashboard to create a service token. He went looking, could not find
the menus, and said so — which is the only reason this was caught.

**C1 read a 403 and inferred a lock without ever reading the response body.**
The body says:

    x-deny-reason: host_not_allowed
    Host not in allowlist: citizencompasstesting.citizencompass-contact.workers.dev.
    Add this host to your network egress settings to allow access.

**That is C1's own sandbox refusing to make the request. It never left the
building.** Nothing about the site, nothing about Cloudflare, nothing about the
password. The same wall is why `_verify_find_deployed.mjs` reports `fetch
failed` on the Cowork VM: that VM has its own allowlist too.

**And the three controls are not blocked at all.** They are in `NEEDS` in
`run_all_controls.py`, skipped unless `--include-deployed` is passed, **and the
reason is written right there** — they make ~450 network requests and click
1,200 markers over the wire, so they are opt-in rather than part of every sweep.
**Deliberate, documented, and C1 read past it.**

**Code's machine has ordinary internet.** One flag answers the question that
started all of this — *how much of what we built is actually on the test site* —
and no dashboard, no token, and no password is involved.

**THE LESSON, because this is the third time this week.** A number or a barrier
that gets repeated stops being examined. C1 saw "403", reached for the most
technical explanation available, wrote an order around it, and got a person to
go looking for menus that do not exist in his account. **The body of the
response said what was wrong in one sentence and nobody read it.** Read the
error before theorising about it.

### Q17 — BUILD AND DEPLOY THE IDENTICAL-OPTIONS LINE
**DONE-WHEN** the testing site shows it and
`node checks/_verify_identical_options.mjs` exits 0 against the built page.
**BLOCKED-BY** nothing. Page source is done and green; it needs a build.

**Sleven approved it directly on 2026-08-28.** Where every part a port offers is
identical on every figure CIG publishes, the picker now says so instead of
sitting silent:

> **These 3 are identical on every stat the game publishes.** Different names
> and makers, the same numbers all the way across — so this one is yours to
> pick on looks or on price.

Both surfaces carry it — the pane picker and the stage dock — from one function.

    node checks/_verify_identical_options.mjs                    10 pass
    node checks/_verify_identical_options.mjs --mutate-always    section C red
    node checks/_verify_identical_options.mjs --mutate-never     3 red
    node checks/_verify_identical_options.mjs --mutate-name      3 red
    node checks/_verify_identical_options.mjs --self-test        NON-ZERO

**A mount that carries other parts is excluded, and the control is why.** The
first build put the line on the Sabre's missile mount: 39 racks, all mass 20 at
size 4, identical by the part table — and named "Gatac Missile Rack 8xS1" and
"20xS3" on screen. A rack's real difference is its child ports, one level down.
**True of our data, visibly false to a player.** Ports with children now say
nothing.

**Everything else on the page is unchanged** — 35 harness controls run, 35
green, including `_verify_ship_page.mjs` and `_verify_swap_loop.mjs`.

### Q11 — WIRE `craft_data.gen.js` INTO THE BUILD (ONE LINE, PLUS A TAG)
**DONE-WHEN** a part in the ship page's picker that has a recipe shows its
craft time and materials, and one that has none shows nothing at all.
**BLOCKED-BY** nothing.

C1 built `build_crafting_demand.py` and the page code. **452 of the 3,283 parts
a reader can fit are craftable**, joined on CIG's own `Output.Class`,
case-folded, exact. The page function is already in `loadout.src.html` and
**returns an empty string when `CRAFT` is undefined**, so nothing changes until
you wire it and nothing breaks if you never do.

    deploy_pages.py    add craft_data.gen.js to PAGES
    loadout.src.html   a script tag before the page script
    build_deploy.py    python build_crafting_demand.py --emit-js=<path in _src>

**Shape is yours** — C1 has not touched `deploy_pages.py` or `build_deploy.py`
and will not while rule 14 is unsettled.

### Q10 — THE DEPLOY GATES ON 4 CONTROLS OUT OF 98
**DONE-WHEN** a payload with ANY red control cannot be uploaded, and the run
that proves it is a deliberately-reddened control that stops a deploy.
**BLOCKED-BY** nothing.

    controls that exist                             98
    controls the deploy actually gates on            4
      _verify_armour_naming · _verify_disclosure
      _verify_panel_dismiss · _verify_settings_revision

`run_all_controls.py` appears in `build_deploy.py` exactly once, **in a
comment.** It is not a gate anywhere.

**THIS ALREADY BIT AND NOBODY NOTICED.** On 2026-08-27 the sweep found **14
failures at 22:15**, and the site was built and deployed repeatedly that same
evening. The controls existed, they were red, and nothing stopped anything. A
suite that cannot stop a deploy is documentation.

**THE COST IS REAL AND IS YOURS TO DESIGN AROUND.** The sweep takes 613s. Ten
minutes on every deploy is not obviously right — caching the result against the
payload's own hash and refusing when the cache is stale is one answer, running
the fast subset on every deploy and the full sweep on a schedule is another.
**C1 is not going to pick; you own the deploy scripts and you have just spent a
day inside them.** What is not acceptable is 94 controls that cannot stop
anything.

**This is the most durable thing on the board.** Once a red control cannot ship,
that property holds for the life of the project without anyone remembering it.

---

# C3'S QUEUE

### R1 — TEN MINING PAGE DESIGNS
**DONE-WHEN** one document in `inbox/` carries ten concepts, each with the
seven fields the order names, ranked, with a first pick and a reason — plus the
separate list of what cannot be built yet and what it would need.
**BLOCKED-BY** nothing. Every figure the order quotes is on disk today.

Raised by Sleven: *"design 10 deeply detailed ideas on how to build a page for
mining... creative and somewhat interactive and easily used with a visually
appealing HUD."*

Full order: `docs/ORDER-C3-design-ten-mining-page-concepts-2026-08-28.md`.

**The three traps it names, because they have each already caught somebody:**
prices are a community source with 0 of 26,657 rows verified and CIG ships none
at all; `commodity_trade_locations.json` is tag-derived CAPABILITY and a
"Security Checkpoint" appears to trade all 109 commodities; and the site's
standard is that a page says what it does not know.

---

# C1'S QUEUE

### M17 — THE PAGE CALLED 335 CIG MOUNTS "ESTIMATES" — DONE 2026-08-28 04:48
**Found by re-measuring a number in `CURRENT-STATE.md` instead of quoting it.**
The document said 245 classes fully on CIG coordinates and 20 with none.
Counting the file the browser actually loads gave **205 and 45**. The gap was a
defect nobody had a check for.

`build_deploy.py` stamps `placed_from` only where the overlay MOVES an existing
marker. **41 hulls never enter that loop** — they arrive as whole records, on
CIG's decoded coordinates, and the stamp never reached them. Every top-level dot
on 57 page classes said `est`.

**Fixed in `build_hardpoint_overlay.py`, which is C1's**, by writing the field
Code's emitter already reads. **`build_deploy.py` untouched — rule 14 intact.**

    cig  1,691 -> 2,026     est  448 -> 113     anc  4,261 unchanged
    classes fully on CIG coordinates   205 -> 244        with none  45 -> 6

**New control, and it caught its own author first.** `_verify_marker_provenance.py`
asserts both directions — no dot on a CIG coordinate may be called an estimate,
no dot called CIG may sit anywhere else. **The first draft used one fleet-wide
coordinate set and produced 38 false positives** (Prowler, Starlancer TAC, every
Apollo and Zeus): `anc` child ports whose ring offset landed on a number that is
a CIG coordinate on a DIFFERENT ship. Now scoped per model file, `anc` excluded
by definition.

**Its `--self-test` asserts a delta, not a verdict**, because when the check was
written it was already red and a mutator that only has to make it fail would
have been inert — the same trap as `_verify_stage_still.mjs` the day before.
Relabelling every `cig` to `est` must produce EXACTLY 2,026 under-claims, and
does. **That is the strong result: all 2,026 are on their own hull's CIG
coordinate, and nothing is over-claimed.**

**What it does NOT prove:** that those coordinates render where the mount is.
The 41 client-record hulls have never been in a browser. **Q12.**

### M1 — THE THREE REMAINING EXPLANATION BLOCKS — DONE 2026-08-27
All converted to disclosure bars. Zero `.trip` blocks remain on the page and
the rule itself is gone (see M7).

### M2 — THE LOADOUT BENCH — IT WAS BUILT. WHAT WAS MISSING WAS ANY PROOF IT WORKS. DONE 2026-08-28
**This entry said "approved after seven prototypes and never built" and that was
wrong.** The loop Sleven asked for is in the page and has been: the picker, the
delta chips, the ledger with per-port revert, the swap log, undo on a button and
on a key. **Reading the source instead of the queue took four minutes.** The
entry had been carried forward unexamined, which is the same fault as the marker
numbers in M17.

**What was genuinely missing is that nothing drove it as a loop.**
`_verify_ship_page.mjs` N10 and N11 come closest and both set `A[slot]=alt`
**directly** — which proves the render paths and steps over the entire
interaction, because none of the click, log or undo code runs when the build is
written behind its back. **A page whose swap handler was deleted outright passes
N10 and N11.**

**`checks/_verify_swap_loop.mjs` — new, C1's, 27 assertions, green.** Every part
change is a click dispatched through the page's own delegated handler. It never
writes to `A[]` and never calls `logSwap` or `undoSwap` itself.

    1. selecting a port offers parts, including the ones it is about to fit
    2. a click fits it, logs exactly one entry, and moves NO other port
    3. the readout marks what moved - and stays silent when nothing did
    4. undo returns that port, empties the log, and withdraws itself
    5. after TWO swaps, ONE undo returns the FIRST part, not stock
    6. undo on an untouched build changes nothing and does not throw

**Section 5 is what the file is for.** Undo is a step, not a reset. A page that
treats it as "back to stock" is right on the first swap and wrong ever after,
and the first swap is the only one anybody tests by hand. `--mutate-undoreset`
plants exactly that bug and **fails exactly one assertion — that one.**
`--mutate-nolog` fails eight.

**THREE THINGS THIS FOUND ALONG THE WAY, all recorded in the file:**

- **A gap in the shared harness.** `_loadout_harness.mjs` has `setTimeout` and
  no `clearTimeout`. The page calls it only on the SECOND stat change in a
  session, so no control has ever reached that line. **Q15.**
- **Two assertions in this control were wrong before they were right**, and
  both were caught by running it: one read the picker from `#picker` when the
  chosen port docks to `#cc-panel`, and one demanded that every swap move a
  number — the swap it chose was between two racks with identical stats, and
  the page was correctly silent. **The assertion is two-sided now:** the mark
  must be there exactly when there is something to mark.
- **A "product observation" that was entirely my own bug — RETRACTED 2026-08-28.**
  This item said *"no alternative the picker OFFERS changes any number in the
  readout"* and it went to Sleven twice as a design question about the bench.
  **It was false.** Two faults, either of which alone caused it:
  the search walked only the first eight swappable ports per ship, and on every
  hull those are racks, missiles and turrets — **guns sit at position ten and
  were never reached**; and `changesANumber` compared `g(...)` to the STRING
  `"true"` when the harness returns a real boolean, so **it answered false on
  every port on every ship, forever.**

  **Measured properly: a swap moves at least one readout figure on 773 of 813
  ports across 25 ships.** Guns, missiles, turrets, coolers, shields, power
  plants, radars and quantum drives all respond, every port. **The bench does
  what it was built to do.**

  What is actually true, and it is small: **flight blades (12 ports), salvage
  heads (6) and most bomb racks show nothing — because CIG publishes no figure
  on which the options differ.** All three flight blades on the Avenger are
  em 0, ir 0, mass 35, power 4, size 1. Identical. The page is being honest.
  The only open question is whether it should SAY so.

### M3 — HARDPOINT COVERAGE — SUPERSEDED, see M8, M10, M11, M12, M13
This item's numbers are from before any of tonight's work and reading them now
would send someone after problems that no longer exist. **Current state: 245 of
the ship page's classes have every marker on CIG coordinates, 20 have none, and
each of those 20 has a written reason.** M13 carries the list.

### M8 — THE ACCEPTANCE TEST JUDGED THE WRONG FRAME — DONE 2026-08-27 20:15
`build_hardpoint_placement.py` measured mounts against the hull box **as the
file stores it**; `cc_viewer.frame()` recentres every hull on that box before
drawing it. **71 of 258 models are not centred on their own origin**, so those
were judged in a frame nobody renders. M2 Hercules 11/149 inside → 140/149, the
C2's number exactly, on identical decoded data. Four Constellation variants now
agree where one used to disagree.

Passed 138 → 139 (gained M2, Valkyrie, SRV; **lost Aquila and Spirit A1** —
their offsets were flattering them). Overlay 952 → 939 ports; new records 29 →
30 hulls / 2,612 ports.

**I also broke the gate and a check I had just written caught it.** Making it
proportional — refuse above half, withhold ports below — lets a **transposed
lateral/vertical axis pass on every hull tested**, because ships are wider than
they are tall and the swap only displaces about a sixth of the mounts. That is
the defect the gate exists for. Reverted, and the reasoning is recorded in the
source so nobody re-derives it.

New: `checks/_verify_placement_gate.py` — three broken frames plus a negative
control, no database, no browser. Exits 0.

**Two more defects found while looking, both silent:**
- The same ship placed twice under two spellings (`ANVL_Hornet_F7A_MK1` and
  `anvl_hornet_f7a_mk1`), the guard comparing exact strings, both writing the
  same file. Manifest said 182 ships for 180 files. Claims fold to lower case.
- **The overlay reads the placement DIRECTORY, not its manifest**, so a refused
  hull kept its file from an earlier run and kept being emitted. The run
  reconciles its directory now and exits fatally if it cannot — proven by a
  planted control, not asserted. 93 stale files moved to
  `_to_delete/hardpoint-placement-stale-2026-08-27/`.

**Final: overlay 93 hulls / 955 ports · client records 30 hulls / 2,612 ports ·
ship page 163 → 165 classes fully on CIG coordinates · 304 client markers, none
emitting zero.**

**Two broken models, not ours:** `Avenger_Stalker.glb` is a tenth the size of
its own siblings; `Aurora_SE.glb` is 87.6 wide against 8.2 for every other
Aurora.

### M10 — THE HULL RULE WAS BLIND TO 15 SHIPS — DONE 2026-08-27 19:45
`build_hardpoint_transforms.py` takes the `.cga` whose stem equals a contiguous
run of its own folders. **120 of 18,891 entries, and right about all 120** — the
archive is mostly bunk beds and dashboards. But CIG does not always name a
folder for the ship inside it:

    AEGS\Sabre\AEGS_Sabre_Raven.cga          MISC\Freelancer_v2\MISC_Freelancer.cga
    ORIG\300_Series\ORIG_300I.cga            AEGS\Idris_Frigate\Exteriors\AEGS_Idris.cga

**Second rule added: exact equality against CIG's own `ClassName` list in
ships.json.** An authority, not a pattern — it cannot admit a prop because
there is no ship class called `aegs_hab_bunkbed_sq_player`. Javelin and Basher
are ambiguous (two paths each, one under `dmg`) and are dropped and named.

    transforms  116 -> 135 hulls      placement 146 -> 160, 137 -> 150 passed
    overlay     93/955 -> 106/1,082   ship page 165 -> 181 classes on CIG coords

Newly real: the whole Freelancer family, Cutlass Black and Red, Constellation
Aquila and both Phoenixes, 300i, Sabre Raven, Vanguard Hoplite, Fury LX,
MPUV 1T.

**The 4.10 snapshot landed mid-run.** `build_hardpoint_placement.py` takes the
newest by design, so hulls are now scaled against 4.10 lengths and the
manifest's `dimensions` points there. Nobody chose it; the newest changed.
Acceptance still 150/160. Flagged to Code rather than left in a diff.

### M16 — CRAFT OR BUY — DATA AND PAGE DONE 2026-08-27 23:25
First of the economy features from `BRIEF_stop-being-a-better-list`.

**`build_crafting_demand.py`** reads CIG's 1,607 recipes — every one with a
craft time, a requirement tree and a dismantle yield — and emits four files
plus a page-ready `craft_data.gen.js`.

    ship-page parts that are craftable   452 of 3,283
    materials in the demand table         37
    Aslarite  856 recipes · Ouratite 495 · Laranite 353 · Tungsten 266

**Three rules written into the generator, not assumed:** the join is
`Output.Class` case-folded and exact (the display-name route is REFUSED — it
adds 34 and one is a different class sharing a name); SCU and item counts are
never summed; tier 0 only, because higher tiers double-count.

**The page line is inert until Code wires the data** — `craftLine()` returns an
empty string when `CRAFT` is undefined, so the page ships either way. Q11.

**Still homeless:** `CRAFT_DEMAND`, the fleet-wide mining answer. It wants a
page of its own and that is a bigger conversation than one line.

### M14 — SLEVEN'S THREE FIXES FROM THE LIVE PAGE — DONE 2026-08-27 22:45
He watched the deployed 400i and gave three instructions.

**1. The ship stops shifting.** The cause was `panelPlacement` preferring the
RIGHT, so the viewer panned the hull LEFT to make room. `setObstruction` still
records the coverage but no longer touches the camera; `reframe()` no longer
shifts.

**2. The panel opens on the marker's own side of the screen** — his rule, in
his words. Two stable rails, not a panel that lands somewhere new each time.
The old "never cover the marker" rule is retired deliberately: it is what forced
the panel to the far side, which is what forced the ship to move.

**3. The hull is see-through**, as a control rather than my taste.
`CC_HOLO.hullAlpha`, default 0.86, fourth slider labelled **See-through**. At
1.0 the material returns to genuinely opaque. Saves with the other appearance
keys; an older save without it simply gets the default, so nobody's settings
are discarded.

**And the page was lying about its own best work.** The provenance note still
said the dots are name-derived and "not measured from the model" — false for
1,693 mounts across 166 hulls. Rewritten to say the measured part is measured,
the fallback is still an estimate, and that it cannot yet tell you which this
ship's are. **Asked Code for the one field that fixes that**: `placed_from` as a
fourth element in `loadout_marker.gen.js`.

**Re-baselined, all mine:** `_verify_stage_panel`, `_verify_ship_page` (N9),
`_verify_marker_coverage`, `_verify_marker_absence`, `_verify_look_panel`.

### M15 — AND I CLOSED MY OWN RULE-12 GAP — DONE 2026-08-27 22:45
I reported that "the ship did not move" reports NOT PERFORMED in the script
harness, and said browser checks were Code's. **Wrong — `_verify_panel_dismiss`
is mine, so a sibling is too.**

New: `checks/_verify_stage_still.mjs`. Real Chromium, real 400i, reads the whole
camera before and after a click, clicks a second marker as well, and finds a
dot each side of centre to prove the panel rule both ways.

**`--mutate-pan` nearly shipped inert.** As two separate mutators both would
have passed — restoring the shift alone moves nothing on a click, and making
setObstruction call reframe alone re-centres on the centre. E4 is one defect and
is planted as one, with every edit required to apply.

**I have never run it** — no headless Chromium in the Cowork VM. It reports NOT
PERFORMED at the launch step. **The first real run is Code's**, and the mutators
are the part that matters.

### M12 — CIG'S OWN RECORD NAMES THE HULL — DONE 2026-08-27 20:30
I wrote in M9 that ships.json carries no geometry path and that I had checked
every field. **I checked for a PATH. The answer is a NAME, one level down.**

    anvl_c8_pisces  ->  Parts[0].Name == "ANVL_Pisces"

309 of 318 classes carry a part-tree root; 183 name a hull other than
themselves. It reaches what no name rule could — `ANVL_C8_Pisces ->
ANVL_Pisces`, `RSI_Ursa_Medivac -> RSI_Ursa_Rover`, `GRIN_MDC -> GRIN_MXC`.
**Replaced the `cls + "_"` prefix expansion**, and it is safe where the earlier
name-expansion was not: only ports whose HardpointName is a node in that hull
are placed, so a module-specific mount gets no position rather than a wrong one.

Root names fed back into the decoder too — a name CIG uses as a root IS a hull
name, which picked up `AEGS_Idris`. One collision needed a tie-break: a
folder-rule path (name AND location agree) beats a class-name-only one. Equal
evidence still drops both.

### M13 — HALF THE FLEET WAS IN A TREE NOBODY SCANNED — DONE 2026-08-27 20:32
`Data\Objects\Spaceships` 23,083 entries, scanned. **`Data\Objects\Vehicles`
1,762 entries, never.** Ground vehicles live there. Cyclone, Storm, Nova, Ursa,
Ballista, Centurion, Spartan, Lynx were all "no .cga anywhere" for that reason.

    transforms 116 -> 153 · placement 146 -> 284 converted, 137 -> 277 passed
    overlay    93/955 -> 167 hulls / 1,720 ports
    ship page  165 -> 245 classes fully on CIG coordinates · 91 -> 20 with none

**The 20 remaining, each with a reason:** ATLS family (a power suit, under
Characters\PowerSuit), GRIN MDC/MTC/ROC (no exterior mount at all), three
Cyclone variants (records name no decoded root), Javelin (two paths, equal
evidence), Glaive and Scythe (asymmetric), MOTH, Starfarer Gemini. **None is a
guess waiting to be taken.**

### M11 — NINE OF TEN REFUSALS WERE A POSE, NOT A FRAME — DONE 2026-08-27 19:58
Reading *which* mounts were outside settled it: the Constellation's three are
the top-turret mounts 0.53–0.71 above a 13.2-tall hull; the Reliant's are its
wing-tip guns and its wings move. Refusing the whole hull threw away 19 good
Constellation ports to avoid 3 arguable ones — **and the fallback was worse than
what was refused.**

**The gate did not loosen.** Second signal: exterior left/right pairs must all
mirror in the converted frame. **A transpose destroys it (0 of N on every hull);
a uniform scale does not touch it.** Complementary to containment by
construction, not by argument.

**The check refuted me again mid-build.** `out == 0 or proven` let a full-hull
offset and a 4x scale through on the Eclipse and Sabre — mirroring survives
both. Bounded by an absolute count of **4**: pose mismatches run 1–3, the
smallest frame error observed is 23. Below the defect, not above it — the
opposite of the proportional gate I had to revert.

    placement 146 -> 160 converted · 137 -> 157 passed · 3 failed
    overlay   93/955 -> 112 hulls / 1,164 ports
    ship page 165 -> 182 classes fully on CIG coordinates, 84 with none

**Still refused, each with a checkable reason:** ARGO_MPUV_Transport (no
exterior mount at all), VNCL_Glaive (2 of 4 pairs mirror), VNCL_Scythe (1 of 4).

**The two Vanduul are NOT a bug — they are asymmetric ships.** Looked at:
the Glaive's "right" missile rack sits at **negative X**, on the left side of
the hull, and its wing guns are 12.9 m apart fore-and-aft, while its nose guns
and countermeasures mirror exactly. **`VNCL_Blade` mirrors perfectly** on all
four pairs from the same decoder in the same run, so the decode is sound.

The cost is real — the Glaive loses 9 good ports over 1 mount outside — and it
is left that way deliberately: the mirror cannot prove the frame of a ship that
is not symmetric, "at least one pair" is unsafe (a transpose left 1 of 39
matching by accident on the Reclaimer), and anything between one and all is a
threshold on a four-pair sample. **What would settle it is a frame proof that
does not assume symmetry.** Written up so nobody hunts a decode bug that is not
there.

### M9 — THE UNREACHABLE 82 — RE-MEASURED 2026-08-28, AND THE PROBLEM IS NOT WHAT THIS ITEM SAYS
**Do not go looking for the 91 classes this item used to name.** It was written
before M10 and M11 landed and before the provenance defect was found, and its
numbers described a page that no longer exists.

**Counted today from the emitted marker file, which is what a visitor loads:**

    page classes with every top-level mount on CIG coordinates   244
    mixed, cig + derived                                          21   (88 mounts)
    no CIG mount at all                                            6

The six are `VNCL_Glaive` and `VNCL_Scythe` (asymmetric, placement correctly
refuses them — see M4), `GRIN_MTC`, `MISC_Starfarer_Gemini`, `TMBL_Cyclone_MT`,
`TMBL_Cyclone_TR`.

**What survives of this item, and it is worth keeping.** The structural
`HardpointName` join is still not refereed by anything, and the reason it was
stopped still stands: partial coverage looks convincing, containment is
one-sided, and **a wrong hull that is merely larger passes**. Nothing today
changed that. What changed is the price of leaving it alone: it now buys 88
mounts on 21 hulls instead of a third of the fleet, and **the 88 are labelled
`est` on the page and say so**, which is the honest outcome.

**Do not widen anything to close it.** If it is ever reopened, the entry cost is
a second independent signal that must agree with the structural one — not a
threshold.

### M4 — THE GLAIVE WAS NEVER ASYMMETRIC — DONE 2026-08-28
**The frame proof was filtering out the evidence that proves the frame.** The
mirror ran over EXTERIOR mounts only; the Glaive has almost no exterior named
pairs, and its engines, coolers, intakes and powerplants mirror to within 8.7 cm.
2 of 4 became **13 of 19** the moment the filter came off. The Scythe, refused in
the same sentence, is **1 of 16 and genuinely is asymmetric** — one explanation
had been covering two different ships.

**New rule: at least 4 named pairs, at least half mirrored.** A fraction invites
one objection — that it was fitted to let a wanted ship in — so it was measured
across all 265 hulls with 4+ pairs, and again on every one with the axes
transposed:

    transposed axis, highest fraction reached      0.455
    correct frame, lowest fraction above midpoint  0.684
    at a HALF rule    clean 262 of 265    transposed 0 of 265

**Nothing sits between 0.455 and 0.684.** The per-pair tolerance is untouched —
M4's own warning was never the lever.

**Then the control found something older.** Six subjects taken in directory
order are not adversarial, so the fleet's worst hull was pinned in by name — and
it reported that **a transposed San'tok.yai passes the gate.** Not the new rule's
doing: the mirror was only ever consulted when something was already outside the
box, and nothing leaves that hull's box when its axes swap, because it is nearly
as tall as it is wide. **The mirror is now a veto as well as a licence.**

    VNCL_Glaive                     refused -> passed, 1 mount withheld
    drak_clipper (x2)               passed  -> refused
    VNCL_Scythe                     refused -> refused, now for a measured reason
    60 hulls gained a proven frame  and not one changed verdict

**The two Clippers are the cost and the cost is the point.** A rule that admits
the Glaive on its mirror has to refuse the Clipper for the lack of one.

Full working: `docs/FINDING_the-glaive-was-never-asymmetric-2026-08-28.md`.

### M5 — `CURRENT-STATE.md` — SPLIT, DONE 2026-08-27 20:45
**It is no longer eleven days stale.** It was brought forward earlier today and
now leads with 08-27 material. The staleness half of this item is closed and I
am not going to keep claiming it.

**The structural half stands and is worse than the staleness was.** 13,554
words, ordered newest-first, opening with an instruction that everything below a
certain point is history. A reader cannot tell where that point is, so the only
safe read is all of it, every session, forever.

**One live number was wrong and is fixed rather than filed against.** Line 79
said *"ten distinct damage-multiplier profiles"* since 08-22. Three independent
counts say **eight** (`FINDING_both-open-questions-closed...`). Corrected in
place with the correction visible, not silently.

**DONE.** Split into two files, nothing deleted:

    docs/CURRENT-STATE.md                      1,487 words - only what is true
    docs/STATE-ARCHIVE-through-2026-08-27.md  13,801 words - the original, verbatim

The new one carries no "later section wins" rule because it has no later
sections. **It states its own maintenance rule: it does not grow by appending.**
A fact that stops being true is edited or deleted there, and the reasoning goes
in a dated `docs/FINDING_*` or `docs/DECISION_*`. A snapshot, not a log.

The archive's header names its own known-stale parts up front — the collector
section saying "none of it has run on Windows" when it passed 575 checks today,
and hardpoint numbers from before tonight — so nobody has to discover them.

Both written to the claude.ai project as well, since the project instructions
point new sessions at `claude/CURRENT-STATE.md`.

### M6 — THE SHIELD SENTENCE — DONE 2026-08-27 18:20, AND C3'S NUMBER WAS WRONG
C3 ranked *"a shield stops all of a laser's damage and only 45% of a
ballistic's"* first of six things to build, ahead of everything needing a
calculator. **The energy half is exact. The ballistic half is the top of a
range** — `Absorption.Physical` reads Minimum 0, Maximum 0.45, and Energy is the
only channel where the ends meet. Measured by me on 73 shield items, one profile
across all of them.

**And shields carry a second `Shield.Resistance` block** — physical 0–0.25,
distortion 0.75–0.95 — which is NOT the `Durability.Resistance` that
`FINDING_both-open-questions-closed` established as item durability. Different
block, different path. The effective-damage calculator stays blocked.

**Shipped the honest version** on the ship page under the armour matchup table,
stamped `SHIELDS · 4.9`, with the range as a range. Full working:
`docs/FINDING_the-45-percent-is-the-top-of-a-range-2026-08-27.md`.

### M7 — THE DISCLOSURE CSS IS ONE COPY AGAIN — DONE 2026-08-27 18:10
Code extracted my `.disc` rules into `testing/_src/_disc.css` for find, keybinds
and index, and left this page's copy alone because it is not Code's file —
noting loadout could point at the file whenever C1 wanted. **It wanted.** The
rules were diffed first (identical, line for line; only comments differed), then
replaced with the build's `/* CC_DISC_CSS */` marker. The dead `.trip` rule went
with it — zero elements carried the class.

---

# PART C — THE TWO PROPOSALS BEHIND D2 AND D3

## D2 — the Windows-runner premise is stale, and the correction changes the answer

`CRITIQUE_senior-analyst-review-2026-08-27` Finding 2 states that **no Claude
session in this project can run a Windows binary**, citing the 08-09 handoff,
and offers two options: build a scheduled runner, or stop writing unexecutable
checks.

**That was true of Cowork sessions and it is not true of Code.** On 2026-08-27
Code ran, on Sleven's Windows machine, in the ordinary course of work:

    venv\Scripts\python.exe testing\_src\build_deploy.py
    powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
    node checks\_verify_panel_dismiss.mjs        (headless Chromium)

Those are Windows binaries, executed by a Claude session, unattended, today.
**The blocker is real for C1 — the Cowork device bridge is a Linux VM with no
network — and it is not real for Code.** The critique is eighteen days old and
this changed underneath it.

**So the recommendation is neither of its options.** Option 1 proposes building
a runner that already exists in the form of Code. Option 2 concedes ground that
does not need conceding.

**C1 recommends: put the collector selftest on the queue as ordinary Code work,
and find out what actually fails.** `go build` plus `.\collector.exe --selftest`
is one queue item. If it runs, ~190 checks stop being theoretical and the
capture_keys class of defect becomes catchable by machine. If it does not run,
**the reason is a measurement rather than an eighteen-day-old inference**, and
option 2 becomes the honest fallback with evidence behind it.

**What the critique gets right, and it survives the correction:** ~190 checks
have never been executed, that is why a dead feature shipped, and nobody should
write another collector check until they run. That part stands.

## D3 — proposed HARD RULE 16

> **A check must draw its truth from a different source than the thing it
> checks.** A real browser, a real binary, a real archive, a real clock — not a
> model of one written by the same author on the same day. Where that is
> impossible, the check is labelled UNPROVEN and says what it could not reach.

**Three worked examples, all from this project's own record:**

1. **The dark site, 2026-08-26.** `_fitProjected()` moved the camera without
   aiming it. The stub camera in the harness **always looked at its target** —
   it modelled the fix. Twenty-three green checks stood over three days of a
   completely black site. `DECISION_the-checks-get-a-real-browser-2026-08-26`
   is this rule, discovered at the cost of an outage and scoped to browsers.
2. **`ui.go`.** Compiled clean — a file the product does not use.
3. **The callback control.** Asserted 50 calls consumed 50 slots. Go dedupes
   identical closures, so one slot was consumed and the control passed by
   agreeing with the same wrong model the code held.

**Why rule 12 is not enough.** *A check that cannot fail is not a check* catches
a vacuous assertion. All three above **could** fail — they simply could not fail
**for the real reason**, because the check and the code shared an assumption.
That is a different fault and it needs its own rule.

**What adopting it costs, said plainly:** several existing checks become
knowingly inadequate the day it is adopted, and the collector's entire suite is
in that set until D2 is settled. That is a feature — it converts a silent gap
into a labelled one — but it will make the board look worse before it looks
better.

---

## WHO WRITES WHAT — `OWNERS.md`

**The list that used to sit here is gone, and its absence is the point.**

On 2026-08-27 Code's drift detection fired on C1's writes to
`testing/_src/cc_viewer.js` and `testing/_src/loadout.src.html`. Both were
already C1's — here, and in `CURRENT-STATE.md`, and had been for weeks. Nothing
was in conflict. **Two sessions were reading two prose lists, and Code's tooling
could not read either.**

So the list moved to `OWNERS.md`, which a program can parse, and this section
became a pointer rather than a second copy. **Rule 14 is one writer per
artifact, and the ownership list is an artifact.**

`checks/_verify_owners.py` holds it to that: every owned path must exist, no
path may be claimed twice, and **this file must not enumerate paths again**. If
it starts to, the check fails and names the lines.
---

## RECENTLY CLOSED — context only, do not re-do

- **Deploy + P1e + the rescale** — deployed and verified 2026-08-27.
- **Markers on CIG's coordinates, proven in a browser** —
  `_verify_marker_positions.mjs`, green, control decisive.
- **The old Q3 was a hollow check and Code proved it.** C1 claimed re-running
  `build_hardpoint_overlay.py` after a rescale was a free check on the rescale.
  **It never opens a `.glb`** — the file is byte-identical because it cannot
  depend on model scale at all. C1's error, recorded rather than quietly
  dropped.
- **The RSI watcher write rate** — trigger prompt changed 2026-08-27 13:05
  local. A quiet or blocked hour now writes zero documents; only
  `watch-rsi-state.md` is overwritten. **A control is planted** in that state
  file: two real devposts were removed, so the next run must detect them and
  write exactly one document. If it writes none, change detection is broken and
  the change gets reverted.

---

*Maintained by C1. Last set 2026-08-28 04:48 UTC.*
