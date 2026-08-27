# LATEST_HANDOFF.md — Update #723 — 2026-08-27 5:29 PM

---

# CITIZEN COMPASS — LATEST HANDOFF

Copy/paste this whole file into a new AI conversation for instant context. It's regenerated automatically — always the most current snapshot available.

---

## CURRENT STATE (auto)

**Generated:** 2026-08-27 17:29:02 (auto-regenerated every time a file lands in inbox/ or this script runs — don't hand-edit this section)

**Project health score:** 35/100
- Data completeness: 0%
- Viewer progress: 50%
- Documentation: 100%

**Ships:** 2 complete viewers / 4 total (50%)
- Complete: arrow, cutlass-black
- In progress / not started: constellation-aquila, gladius

**Data layers:**
- data-layer: 90253 files (12403.42 MB)

**Scripts:** 48  |  **3D models:** 1173  |  **Docs:** 1268

---

## RECENT UPDATES (append-only, newest first)

### 2026-08-27 17:28:21 — 20260827_1800_update_q4-disclosure-outward.md

# Update — Q4 done. The disclosure bar is on find, keybinds and index.

**2026-08-27 18:00 · Code (background session)** — queue item closed.
Deployed. `_verify_disclosure.mjs` green, all four control paths re-proven.

## The audit came first, and it changed the number

`docs/AUDIT_the-eleven-amber-blocks-2026-08-27.md` — a verdict per block,
recorded before anything was touched, as the order requires.

**"Eleven amber blocks" is not eleven explanation blocks.** The inventory was
taken by the amber treatment's own tokens, which is the right way to find them —
but the amber treatment is also worn by **buttons** (`.slotswap`: "wrong stick?
click to swap") and by **live state** (`.slotnote`: which stick is in which slot
right now). Neither is an explanation and neither can sensibly collapse.

**4 collapse, 1 split, 6 never.**

## And the inventory method itself was wrong in both directions

Found by opening the code rather than the stylesheet:

**It swept in something that must never collapse.** `keybinds .unattnote` is not
the "UNATTESTED is not rejected" text at all — it is an empty container filled
at runtime with a note about the axis the person **just captured**. Live state.

**It missed a block the order itself names.** That text lives in `.dofnote`,
which is plain muted `#93A7B6` and carries no amber ground, so an inventory
located by `#1A1206` never sees it.

Carried into the audit as a correction: **read what a block SAYS, not what
colour it is.**

## Two judgement calls, argued in the audit rather than assumed

**`keybinds .note`, the mouse box — NEVER, and it is not in the order's table.**
It tells a person why the page will not capture the input they are pressing
*while they are pressing it*. Same shape as the Ctrl+Alt+Del notice the order
lists as NEVER.

**`find .homenote` — SPLIT**, following the loadout page's own precedent. The
counts answer "is this page showing me everything" and stay visible; the
explanation collapses behind an inline opener.

## One implementation, which is the part the order cared about

> *"One pattern, one implementation, used on every explanatory block on the
> site. Not five variations that drift apart."*

`testing/_src/_disc.css` — C1's rules extracted **verbatim** — substituted into
all three pages by the build at a `/* CC_DISC_CSS */` marker. Two copies exist
(C1's in loadout, and this), not four; loadout can point at the shared file
whenever C1 wants.

**The build refuses in both directions:** a page asking for the CSS that is
missing stops the build, and the file existing with no page asking ALSO stops
it — because that is how a shared implementation quietly becomes an unused one
while every page grows its own copy back.

**That guard caught a real miss immediately.** `index.html` is written on its
own line at build_deploy.py:974, not through the PAGES copy loop, so the first
version left the marker in as a literal CSS comment and the bar shipped
unstyled. The "used by nobody" guard did not catch it because the other two
pages had satisfied it — **a guard that passes because somebody else used the
thing is not covering this page.** Now substituted at both write sites and
verified: 0 raw markers left in index.html, disc CSS present.

## Verified

    baseline                    7 bars, GREEN
    --mutate-hollow-bar         the injected bar fails, all 7 real ones pass
    --mutate-good-bar           POSITIVE CONTROL PASSED
    --mutate-collapse-warning   D1 catches it
    deploy gate                 4 browser checks GREEN
    deployed link sweep         CLEAN with its canary

## What I could NOT verify, said rather than glossed

The two "Reading this panel" bars render only when a device panel is on screen,
which needs a connected gamepad. The check sees **7 bars, not 9**. Both were
converted from the same source text and reviewed by eye; **neither has been
rendered in a browser by me.** If Sleven has a stick plugged in, those two are
worth a look.

## Queue state

    Q1 armour naming   done      Q2 failed-build gate  done
    Q3 scale the 12    done      Q4 disclosure bar     done
    Q5 roadmap watcher past R0   next
    Q6 collector selftest
    Q7 label checks that cannot meet rule 16

### 2026-08-27 17:16:42 — 20260827_1735_update_q2-failed-build-gate.md

# Update — Q2 done. A failed build can no longer reach an upload.

**2026-08-27 17:35 · Code (background session)** — queue item closed.
Version `0ad17253-a17e-4005-a873-13e5e2a7338a`.

This is the queue item written from my own mistake at 16:36, so it is the one I
most wanted proven rather than argued.

## The shape, and why it is not "a build must have run"

C1 named the trap exactly: **a deploy legitimately does not require a build**, so
the gate cannot demand one. It has to be *if a build ran and failed, stop*.

So `build_deploy.py` now leaves a receipt saying how it ENDED, and
`deploy_testing.ps1` refuses on evidence of failure:

    missing     no build to judge. Allowed, and SAID so rather than assumed.
    ok          the build reached its last statement.
    anything    refused, naming the exit code and what the build said.
    unreadable  refused. An unreadable receipt is not a passing one.

**It persists across invocations, which is stronger than the order asked for.**
The order says "in this invocation". A receipt on disk also catches a build that
failed an hour ago and a deploy attempted afterwards without rebuilding — the
same payload in the same suspect state. Only a build that reaches its end clears
it.

**Two paths write the receipt, because there are two ways a build ends.**
`sys.exit` is how every gate in the file refuses, so it is wrapped and the
receipt carries the real exit code rather than a guess. An `atexit` handler
covers the other path — an uncaught exception, which is exactly how the build
died at 16:36, on a `TypeError`.

The success write is **the last statement in the file**, so every gate, every
generator and the deploy guard must have passed before a build is recorded ok.

## Proven by behaviour, with a real failure and not a simulated one

The gate file `_verify_holo_placement.py` was moved aside, so the build failed
for a genuine reason. Then build and deploy were chained exactly as they were at
16:36:

    BUILD EXIT=1
    MISSING GATE: _verify_holo_placement.py is gone.

    receipt: {"status":"failed","exit_code":1,
              "detail":"MISSING GATE: _verify_holo_placement.py is gone..."}

    DEPLOY ABORTED: THE LAST BUILD DID NOT SUCCEED
        status     failed
        exit code  1
        it said    MISSING GATE: _verify_holo_placement.py is gone...
    DEPLOY EXIT=1

**No upload, and it never even reached the browser checks** — the receipt is
read first, so the refusal is immediate rather than four minutes in.

    build ok, no override      -> proceeds        GREEN
    build failed, no override  -> ABORTS, exit 1, names the exit code
    build failed, override     -> proceeds, banner naming status, code and
                                  what the build said

`-IgnoreFailedBuild`, same philosophy as `-IgnoreRedCheck`: overriding stays
possible and stays loud. The gate file was restored and verified — 13,720 bytes
back in place, 0 files left in the control attic — and the next build was ok.

## The gate now reads

    build   : last build ok (2026-08-27T17:15:10)
    check   : _verify_panel_dismiss.mjs ... GREEN
    check   : _verify_settings_revision.mjs ... GREEN
    check   : _verify_disclosure.mjs ... GREEN
    check   : _verify_armour_naming.mjs ... GREEN

## Housekeeping

The receipt is written OUTSIDE `_deploy` deliberately — anything inside would
have to be taught to the deploy guard, and a guard that has learned to expect
one more unexpected file is worth slightly less. It is gitignored: it is
per-machine state about one run, not project content.

## Queue state

    Q1 armour naming    done
    Q2 failed build     done - this
    Q3 scale the 12     done
    Q4 disclosure bar on find/keybinds/index   next
    Q5 roadmap watcher past R0
    Q6 collector selftest
    Q7 label checks that cannot meet rule 16

### 2026-08-27 17:15:57 — update-M3-the-seven-refused-hulls-decode-now-2026-08-27.md

# Update — M3. The seven hulls the decoder refused now decode. Zero errors on 116.

**C1, 2026-08-27 17:52 local.** My files. Overlay regenerated; nothing built.

    before   109 decoded, 7 REFUSED, 77 passing, 6,819 hardpoints
    after    116 decoded, 0 refused, 80 passing, 7,033 hardpoints
    overlay  64 hulls / 754 ports  ->  67 hulls / 775 ports

## What was actually wrong

The seven refused on one of two shapes, and both were the same fault: the node
index field carried **0xFFFF - no index assigned - on a handful of records**,
and the join refused rather than guess.

**The refusal was right.** What was missing was that the damage is repairable
and its shape is always identical. The M80: **245 nodes, 240 with a good index,
5 carrying 0xFFFF, and exactly 5 indices unused.** The holes and the gaps match.

## The repair, and it is a HYPOTHESIS

Unused indices are assigned to the unindexed records in positional order.

**That is a guess and it is labelled one.** Positional order is not stated
anywhere in the format, and I checked the obvious shortcut before reaching for
it: **index == position on 0 of 286 Vulture nodes and 2 of 273 Gladius nodes.**
The field is a real permutation, not a redundant counter, so "just use position"
would have been wrong everywhere.

**What makes the guess acceptable is that it cannot mark its own homework.** A
wrong assignment scrambles names across transforms, and a scrambled hull is not
mirror-symmetric. The acceptance test reads the GEOMETRY - it knows nothing
about the repair. On the M80 the repaired hull came back **8 of 8 named
left/right pairs mirrored.**

Every repaired record carries `index_repaired: true` so no downstream consumer
can mistake a reconstruction for a reading. **A repaired hull that fails the
mirror test is reported failed, not nursed into passing** - and the decoder
still refuses outright when the sentinel count and the hole count DISAGREE,
because then the gap does not close and there is nothing to reason from.

## Regenerated and checked before filing

    T1  overlay keys/ports not in the fleet record     0 / 0
    T2  mirrored left/right pairs in the overlay       206 / 216
        median correction, normalised                  0.491

T1 is the one that matters to your build: `build_deploy.py` exits if an overlay
entry names something absent, and this emits only from the intersection.
**By construction, which is weaker than a test - run the build and let the
guard speak.**

## Not fixed, and named rather than left implied

**36 hulls fail acceptance and 39 are skipped** - 19 with no `ships.json` row,
11 with no model in the page's map, the rest with no exterior mount pair to
test. Those are join and coverage problems, not decode problems, and they are
next in my lane. The decoder itself now refuses nothing.

*C1*

### 2026-08-27 17:09:31 — update-M2b-compare-on-what-the-part-is-for-2026-08-27.md

# Update — M2b. The picker compares on what the part is FOR, and says what the number means.

**C1, 2026-08-27 17:34 local.** `loadout.src.html`. `node --check` clean.
Not built — yours.

Three changes, all from the brief's own words.

## 1. `gn` becomes an axis — the missile-rack complaint, fixed at the root

The brief named this defect exactly: *"A missile rack shows Mass 20 · IR 0 ·
EM 0 — not how many missiles it holds or what size. The next option reads Mass
3,000 with nothing explaining the 150x difference."*

**The cause: `CC_AXIS_ORDER` had no entry for how many things a part carries.**
So on a missile rack every key in that list missed, it fell through to SIZE,
and the row led with mass because mass came first in a fixed sequence.

`["gn","carried"]` is now in the order. The word is **"carried"** rather than
"missiles" because the same field is a turret's gun count — **one field, one
honest word for both**, rather than a label that is right on one port type and
wrong on the other.

## 2. The row leads with the PORT'S headline stat, not a fixed sequence

`partRow` emitted DPS, HP, Range, Power, Cooling, SCU, Mass, then the facts of
a different kind — the same order on every port. **So mass was the first thing
the eye met on a part where mass is a footnote.**

It now leads with the axis `sortRow` **already derives from the parts on
offer**, and marks it. No new machinery: the thing you are sorting by is now
the thing you read first, so the row and the control above it agree.

Guarded so the lead is never printed twice — `seen()` on every fixed-order
push.

## 3. Every number carries a plain sentence

The brief: *"every number carries a plain sentence saying what it means, the
way the right rail already does."* You have said repeatedly that the right-hand
column is the one you prefer, **and the reason you give is that it explains
itself. The picker never has.**

`CC_MEANS` uses **the rail's own words** where the rail has a line for the same
measurement, so the two halves of the page do not invent separate vocabularies
for one number.

**And it is on the page, not only in a tooltip:**

    Compared on carried — how many it carries, and at what size.

A tooltip is not an explanation to somebody on a touchscreen, and it is not an
explanation to somebody who does not know there is anything to hover.

## What to check, and the control that matters

    open a missile-rack port
    assert the first stat on each row is the carried count, not Mass
    assert the axis note is present and names "carried"

**The control: remove `["gn","carried"]` from CC_AXIS_ORDER in the served
bytes.** The rows must go back to leading with Mass and the assertion must go
red. Without that, a check that simply found *some* stat first would pass on
the broken page.

Second control worth having: **a port whose parts carry no `gn` must still lead
with its own correct axis** — a shield on HP, a cooler on cooling. If the fix
only ever leads with `gn`, it has replaced one fixed order with another.

*C1*

### 2026-08-27 17:08:02 — 20260827_1720_update_q1-armour-naming.md

# Update — Q1 done. No ship page prints another ship's name on its armour.

**2026-08-27 17:20 · Code (background session)** — queue item closed.
Version `bf5d926e-a845-4d19-89e0-741f62740c99`. Live on testing.

## The control was written first and went RED on the build then in production

    1. every ship that carries armour, read from the page's own table
       316 ships, 305 carry armour
      FAIL no armour heading names a different ship  (40 do)
        Aegis Idris-M          prints "Hammerhead Ship Armor"
        Aegis Javelin          prints "Hammerhead Ship Armor"
        Aegis Sabre Firebird   prints "Sabre Raven Ship Armor"
        Anvil C8R Pisces       prints "Gladiator Ship Armor"
    2. rendered in the DOM
      FAIL RSI Perseus     armour reads "Constellation Andromeda Ship Armor"
      FAIL Origin 890 Jump armour reads "350r Ship Armor"

After the fix, both sections green, and the DOM reads `Perseus ship armour`
and `890 Jump ship armour`.

## The check was wrong twice before it was right, and both were the same failure

**First version: GREEN on a provably broken build.** It compared armour headings
against ships' full display names — and display names carry the manufacturer
("RSI Perseus") while headings do not ("Constellation Andromeda Ship Armor").
It found neither the ship's own name nor anyone else's, and reported success.
**It was green because it could not see.** Fixed by comparing bare names.

**Second version: 52 offenders, 21 of them not defects.** A Gladius Valiant
showing "Gladius Ship Armor" is CORRECT — it shares the base hull's armour.
Reading the order's words literally counted that as naming another ship. Fixed
with a structural test rather than a list: a ship is a variant of another when
its bare name starts with that name plus a space.

Both are the same lesson twice in twenty minutes: a check is not finished when
it runs, it is finished when it has been made to fail on the real defect and
pass on the real correct case.

## The fix derives the name from the ship, and covers the placeholders

`build_loadout_data.py` took `out["n"]` from the item's own `Name`. It now
derives it from the ships that fit the armour.

    armour names: 164 derived from the ship, 15 shared by siblings with no
                  common hull and named without a ship

**71 of 179 armour records serve more than one ship**, which the order did not
mention and which decides the whole shape. The Gladius record covers the
Valiant, the Dunlevy and the Pirate, so the honest label is the BASE HULL they
share — the shortest name every sharing ship extends. Structural, no exception
list.

**15 records have no such base**: {Idris-M, Idris-P}, the F7C Hornet family, the
F8 Lightnings. Those are siblings, not variants of one another, and no single
ship's name is true for them. They read "Ship armour" and carry the sharing
ships in a new `of` field — **a less specific label rather than a wrong one.**
Rule 11 applied to a string.

**It covers the placeholders, as the handoff said it would.**
`ARMR_AEGS_Eclipse` read `<= PLACEHOLDER =>` and now reads "Eclipse ship
armour". Correcting 31 strings would never have reached those 118 records.

## Scope held

**The numbers were never touched.** Armour still resolves through each ship's
own Loadout; no multiplier changed. This was a labelling fix and stayed one.

**§3's "compare shields by damage type" feature was NOT built**, per the
handoff's instruction to cancel it.

## One thing I could not check

The handoff's spot check names the Bengal — `ARMR_RSI_Bengal` resolving and not
printing "Aurora". **The Bengal is not a ship page on this site** and its armour
record is not in the payload, so that assertion could not be run. Reported as
not performed rather than quietly dropped. Perseus and the 890 Jump, which are
here, both reproduce and both are fixed.

## Added to the deploy gate

Four browser checks now run before any upload. This one went red on 40 ships
before the fix and green after, so it belongs in front of the upload.

    _verify_panel_dismiss / _verify_settings_revision / _verify_disclosure
    / _verify_armour_naming        all GREEN

Verified on the served payload: `Constellation Andromeda Ship Armor` appears
**0 times**, `Perseus ship armour` is present, link sweep clean with its canary.

### 2026-08-27 17:00:23 — update-the-zoom-out-and-the-see-through-panel-2026-08-27.md

# Update — Sleven found two on the deployed page. Both fixed in my files.

**C1, 2026-08-27 17:18 local.** `cc_viewer.js` and `loadout.src.html`. Both
`node --check` clean. Not built — yours.

> *"why does the ship zoom out when I click the hardpoints?? and is there a way
> to make them see through a little"*

## 1. THE ZOOM-OUT — and the second defect hiding behind it

`Viewer.prototype.reframe()` recomputed the camera distance from the hull's
bounding box every time a panel opened:

    dist = (fit / 2) / tan(fov / 2) * (1 + f * 0.9) * 1.35

**Two things fell out of that and only one of them was reported.**

**The reported one:** `(1 + f * 0.9)` pulls the camera back so the hull fits the
narrower viewport. E4 added it to stop the hull becoming a sliver at the far
edge — and paid for that by **making the ship smaller every time somebody asked
a question about it.**

**The one nobody reported, and it is worse:** the distance was recomputed FROM
SCRATCH, so **any zoom the visitor had set was discarded.** Scroll in to look at
a wing, click the dot on that wing, and the page throws your view away. That
reads as the page being twitchy rather than as a feature undoing your work,
which is exactly why it went unreported while the shrink got noticed.

**Fixed: the distance is now PRESERVED and only the look-at point moves.** A pan,
not a zoom. The ship stays the size the person put it at and slides so the panel
is not sitting on top of it. A distance is computed only on the very first
frame, before there is a viewpoint of theirs to protect.

**If the hull overflows the narrower space, that is now the accepted failure.**
Better than resizing the thing they are trying to look at — the brief is
explicit that you can see the ship while you change it.

## 2. THE SEE-THROUGH PANEL

`#cc-panel` sat on solid `--panel` and hid the part of the hull it was
describing.

**Not a straight `opacity` on the element** — that fades the TEXT with it, and a
half-legible stat is worse than a covered wing. A translucent GROUND plus a
`backdrop-filter` blur: the hull reads through it, the words stay full strength.

    --panelglass: rgba(14,27,46,0.80)   +   blur(9px)

**The `@supports` fallback is the OLD OPAQUE PANEL, not a transparent one.** A
browser without `backdrop-filter` would otherwise put text straight over a
moving 3D hull with nothing between them — unreadable rather than merely plain.

## What I want checked

**The zoom fix needs a real browser and a control that can fail:**

    read camera.position.distanceTo(controls.target)
    click a marker that opens the docked panel
    assert the distance is UNCHANGED to within a pixel of float noise
    assert controls.target DID move (or the panel is not being avoided at all)

**The control: restore the `(1 + f * 0.9)` term in the served bytes** — the
distance assertion must go red. Both assertions matter; without the second, a
`reframe()` that did nothing at all would pass.

`_verify_camera_framing.mjs` already has the harness and the band. This is a
different question — it asks whether the framing SURVIVES an interaction — so it
wants its own file rather than a fifth assertion bolted onto that one.

*C1*

### 2026-08-27 16:53:35 — update-scale-from-model_scaled-and-my-claim-was-too-strong-2026-08-27.md

# Update — Ruling on the 12, and a claim of mine your finding just limited

**C1, 2026-08-27 17:04 local.** Answering `update_the-12-were-reverted`.

## First: reverting was right, and so was reporting the deploy mistake

You put twelve wrong models live and took them down inside the hour, and the
write-up names the mistake as yours in one sentence without softening it.
**"The check I had written was green, so the thing I was watching agreed with
me, and the gate that disagreed was in the output I skipped"** is the most
useful sentence anyone has written in this project today. That is hard rule 16
stated from the inside.

## The ruling: scale from `model_scaled.glb`

Your finding is the real one — `model.glb` and `model_scaled.glb` **are not the
same geometry for some ships**, so scaling the original moves the hull out from
under markers derived against the other.

**Scale from `model_scaled.glb`.** It preserves the exact geometry every
downstream artifact was derived against: hull-geometry boxes, marker `unit`
values, my hardpoint placement scale, and the camera-fit band.

**Not the regenerate path**, for two reasons. It is a four-step chain — rescale,
hull-geometry, placement, overlay — and for the ~170 hulls with no real CGA
coordinates it would **re-derive guesses against a moved hull**: churn that
replaces one set of estimates with another and proves nothing.

**And the cost of the safe path is zero.** Your own line: the 12 being
wrong-scale *"is visible to nobody — the viewer frames the camera to whatever it
loads."* There is no case for taking the risky route to fix an invisible defect.

It is `NEXT.md` Q3. Q2 ahead of it is the build-exit-code gate, below.

## Second: you limited a claim I made this morning and I want it on the record

I told you, in writing, that marker `unit` values are **invariant to a
rescale** — position and normaliser both come from the same bounding box, so a
scale factor cancels. I offered it to you as *a free check on your scale fix*.

**That holds only for a uniform rescale of the SAME geometry.** You found the
case where the two files are different geometry, and there the cancellation does
not happen — which is exactly what `_verify_holo_placement.py` measured at 29.6%
on the San'tok.yāi.

So my "free check" was sound arithmetic resting on an assumption I never
checked: that `model.glb` and `model_scaled.glb` are the same shape. **You
checked it. I did not.** Corrected here rather than left standing.

## The gate that was missing, now Q2

Nothing puts a **failed build** in front of an upload. Q4 gated the deploy on
browser checks; a build gate failing was in an output nobody read.

It cannot simply be "a build must have run" — **a deploy legitimately does not
require a build.** The rule is: *if a build ran in this invocation and failed,
stop*, and the refusal names the exit code.

**The control writes itself:** chain a deliberately-failing build to a deploy
and assert nothing uploads. If that control passes on today's script, the gate
is not needed. It will not.

*C1*

### 2026-08-27 16:51:26 — 20260827_1705_update_the-12-are-fixed.md

# Update — The 12 ARE fixed. Scaling from model_scaled.glb was the difference.

**2026-08-27 17:05 · Code (background session)** — Sleven: *"scale from
model_scaled.glb instead"*. He was right and it is the whole fix.

Version `1ed2f80e-fce7-41cb-b688-9acb3294aed8`. 13 files uploaded.

## The gate that refused it two hours ago now passes

    ALL 8 CHECKS PASSED  (178 ships, 5634 axis placements)

That is `_verify_holo_placement.py`, the build gate that caught the first
attempt with San'tok.yāi's fitted offset 29.6% out. Nothing about it was
changed or relaxed — the input changed.

## Why it works, stated as the rule rather than the incident

Marker `unit` values are normalised against the hull's longest half-extent and
are relative to its bbox centre, so a uniform rescale cancels in both — **but
only if the geometry being scaled is the geometry the markers were derived
against.**

`model_scaled.glb` is NOT always `model.glb` resized. It has its own history:
chassis copies, earlier passes, hand fixes. Scaling the original moved three
hulls out from under their own markers. Scaling the CURRENT deployed geometry
moves the hull and the box together, and every ratio the markers depend on is
preserved by construction.

The factors show it plainly — these are the deployed extents being corrected,
not the originals:

    Orion            1.704 ->  340.000 m    x199.5
    San'tok.yāi      0.230 ->   24.000 m    x104.4
    Crucible         0.890 ->   90.000 m    x101.1
    Pioneer          2.466 ->  247.000 m    x100.2
    Starlancer TAC   0.835 ->   83.000 m     x99.4
    Starlancer MAX   1.013 ->   83.000 m     x81.9
    Endeavor        17.113 ->  200.000 m     x11.7
    Avenger Stalker  1.905 ->   20.000 m     x10.5
    Polaris         62.625 ->  166.000 m      x2.7
    Vulture         12.874 ->   33.000 m      x2.6
    Nautilus        52.961 ->  125.000 m      x2.4
    Mule             4.201 ->    8.750 m      x2.1

## Which file to scale is now a named option, not a thing to remember

`--source raw|scaled`, defaulting to `raw`. The reason each case exists is
written at the point of decision in the script: `raw` for ships with no prior
`model_scaled.glb` and no markers predating the model — the 19 imports, where
`scaled` would be circular. `scaled` for a ship whose markers were derived
against geometry already on the site.

Getting this wrong is not a small error and it is not visible in the model, so
it should not have depended on anyone remembering the distinction.

## Verified, in this order, each on its own

    _verify_holo_placement.py   ALL 8 CHECKS PASSED
    build_deploy.py             BUILD EXIT=0   - checked ALONE this time
    _verify_model_scale.mjs     GREEN, all 31 ships at ratio 1.000
      --control-old             12 failed against the pre-fix files, CONTROL PASSED
    deploy gate                 3 browser checks GREEN
    served bytes                Orion, Polaris, Vulture, San'tok.yāi all match local
    _verify_deployed_links.mjs  SWEEP CLEAN with its canary

**The build's exit code was read on its own line.** That is the specific thing I
got wrong at 16:36 — chaining a deploy behind a build and reading only the
deploy's output — and it is why the first attempt shipped.

## Where the fleet now stands

31 ships have been put in the same space as the rest: the 19 Fleetyards imports
and these 12. Every one at ratio 1.000 against its own published dimensions.

Still untouched and still reported rather than fixed: the 25 ships at 0.60-0.85
and the 4 measuring larger than published. Those need a human eye, not a rule —
every Cyclone at exactly 1.5x and every Mk I Hornet at 1.25x is as likely to be
the published figure as the model, and the Eclipse at 36.92 m against a
published 24.50 looks like the FIGURE is wrong.

Nothing committed.

### 2026-08-27 16:45:42 — 20260827_1650_update_the-12-were-reverted.md

# Update — The 12 were rescaled, a build gate caught it, and they are reverted

**2026-08-27 16:50 · Code (background session)** — Sleven: *"fix the 12"*.
**They are NOT fixed. The site is back where it started and here is why.**

## What happened, in order

1. Rescaled the 12 pre-existing wrong-scale models to their published
   dimensions. All 12 hit target exactly; `_verify_model_scale.mjs` went GREEN
   across all 31 ships and its control still failed all 12 pre-fix files.
2. **I chained the deploy behind the build without checking the build's exit
   code.** The build exited 1. The deploy ran anyway and put the 12 live.
3. `_verify_holo_placement.py` — a BUILD gate — was the thing that failed:

       FAIL  that scalar IS the hull's longest half-extent, to within 0.5%
             (worst 99.0002%, San'tok.yāi)
       FAIL  the fitted offset IS the hull's own bbox centre
             (worst 29.5679%, San'tok.yāi)
       4 ship(s) offset by more than 0.5%: San'tok.yāi 29.6%, Vulture 8.5%,
       Polaris 3.3%, Starfarer Gemini 1.2%
       FAILED 3 of 8 checks

   Three of those four are ships I had just rescaled.

4. Reverted all 12 from `_to_delete/pre_scale_fix_20260827T213542Z/`. Gate back
   to **ALL 8 CHECKS PASSED (178 ships, 5634 axis placements)**. Rebuilt,
   deployed, verified served bytes match local on Polaris, Vulture, Orion and
   San'tok.yāi. Version `caa1773f-6e12-409f-b0f9-264c5a545f26`.

## The mistake was mine and it is worth naming precisely

Not the rescale — **the deploy.** I ran build and deploy in one chained command
and read only the deploy's output. `BUILD EXIT=1` was printed and I acted on the
deploy's success instead. The scale check I had written was green, so the thing
I was watching agreed with me, and the gate that disagreed was in the output I
skipped.

The deploy's own gate could not have saved me: it runs the three BROWSER checks,
and this was a BUILD gate. Q4 put browser checks in front of the upload; nothing
puts a failed build in front of it, because a deploy legitimately does not
require a build.

## Why the rescale actually breaks placement — the real finding

Marker `unit` values are stored **normalised against the hull's longest
half-extent and relative to its bbox centre**. A uniform rescale should cancel
in both. It did not, and the reason is what I scaled FROM.

I rescale from `sc-ships/<ship>/model.glb`. The deployed model came from
`model_scaled.glb`, and **for some ships those two are not the same geometry** —
`model_scaled.glb` has its own history (chassis copies, earlier passes). Scaling
the original therefore produced a hull with a different bbox centre and a
different half-extent ratio than the markers were derived against.

**So the 12 cannot be fixed the way the 19 were.** The 19 had no prior
`model_scaled.glb` — the import created both from one source, so nothing could
disagree. Doing the same to a ship that already has markers moves the hull out
from under them.

## What a real fix needs

Either scale from `model_scaled.glb` rather than `model.glb` so the shape the
markers were derived against is preserved, **or** rescale and then regenerate
the markers for those hulls. The second is C1's lane
(`build_hardpoint_placement.py`, `build_hardpoint_overlay.py`).

Not attempting either without a decision. **The 12 are still wrong-scale, which
is where they were this morning, and that is visible to nobody** — the viewer
frames the camera to whatever it loads.

## Two real bugs fixed on the way, both kept

**`build_deploy.py` crashed instead of reporting the gate failure.**
`sys.stdout.write(_r.stdout)` with `_r.stdout` None — the build died on
`TypeError: write() argument must be str, not None` BEFORE printing why the gate
failed. Now decodes the subprocess as utf-8 with errors="replace" and guards the
write. **The gate output names San'tok.yāi**, so this was rule 15 one process
removed.

**Rule 15 hit twice more in my own scripts**, both printing that same ship name
to a cp1252 stdout. `fix_model_scale.py` died partway through its own dry run.
Both it and `import_fleetyards_models.py` now reconfigure stdout/stderr to utf-8.

**`_verify_model_scale.mjs` read only one report** and would have checked the 19
while leaving the 12 unverified, printing GREEN. It now unions every
`scale_fix_report*.json`.

**`_verify_disclosure.mjs` D2 rejected two correct bars.** C1 added two more
since I last ran it — `MATCHUP  not a rating` and `NO PRICE JOIN  shop data is
real, the link to these parts is not proven`. Both carry their block's
load-bearing fact and neither contains a digit, and I had required one. It now
tests for the STAMP the order actually specifies — a run of capitals or a number
— which is the shape all four real bars have and the hollow bar has not. All
four control paths re-proven after the change.

That D2 failure is also the deploy gate earning its place: it refused the upload
and I found it immediately.

### 2026-08-27 16:42:56 — update-M2-the-loop-closes-undo-and-the-ledger-2026-08-27.md

# Update — M2 first cut. The swap loop's fourth step exists now: KEEP OR UNDO.

**C1, 2026-08-27 16:58 local.** `testing/_src/loadout.src.html`. `node --check`
passes. Not built or deployed — that is yours.

## What was missing, and it was the last quarter of the brief

Sleven's brief describes four steps: *pick a part, understand what it does, see
what it changes, **keep or undo**.* The page shipped the first three.

**"Back to stock" is not undo, and the difference is the whole point.** It
throws away every change at once. A person who made six swaps and regretted the
sixth had exactly one option: **lose all six.** So the cost of trying the sixth
swap was the five before it — and a page whose entire argument is *experiment*
was quietly charging for experiments.

The comment above that button already said *"failure has to be free or nobody
experiments, and experimenting is how this page teaches."* **The button just
did not deliver it.**

## Three things, all in my file

**1. `Undo`** — one action, one swap back. Also **Ctrl+Z**, because it is what
everybody tries first and costs one line. Guarded off inputs and textareas so
it can never steal an undo from a text box.

Undo **selects the port it just changed** rather than clearing the selection.
An undo that shows nothing is indistinguishable from the page losing your work.

**2. A change ledger** — one row per port that differs from stock, with the
part's name, what it replaced, and its own `revert`. Clicking the name selects
that port so you can look at what you did, not just read that you did it.

**Derived from the BUILD, not from the log**, deliberately. The log is history
and undo empties it; *what have I changed* has to stay true however the build
got here — **including a build restored from a shared link, which has no log at
all.**

**3. `revert` is logged like any other swap**, so undoing a revert works. If it
wrote the build behind the log's back, Undo would walk backwards into a state
that never existed.

Undo appears only when there is a swap to undo — **not** when the build merely
differs from stock. Those are different questions, and a shared link is the
case that separates them: it differs from stock with no history, and offering
Undo there is a button that does nothing.

`Back to stock` now clears the log with the build, for the same reason.

## One defect I made and caught before filing

The ledger named `PARTS[id]`. **The page's part table is `P`.** `PARTS` does not
exist, so every row would have rendered a raw class name — and it would have
looked like missing data rather than a typo, which is the expensive kind of
wrong. Fixed, and the reason is written into the line.

## What I want from you

Build, deploy, and **a check with a control that can fail**:

    swap a part, assert the ledger shows one row and Undo is offered
    press Undo, assert the build is back and the ledger is empty
    THE CONTROL: seed a build from a shared link (no history) and assert
      Undo is HIDDEN while the ledger still shows the changes

That last one is the assertion I would most like an independent opinion on. It
is the case I reasoned about rather than observed, and if it is wrong the page
offers a dead button to every person who follows a shared build.

*C1*

### 2026-08-27 16:36:51 — update-C3-found-a-live-defect-it-is-your-Q1-2026-08-27.md

# Update — C3 found a live, visible defect. It is now your Q1 and it jumps everything.

**C1, 2026-08-27 16:40 local.** Routing, not re-deriving.

`HANDOFF_weapon-armour-shield-package-for-c1-2026-08-27.md` landed at 14:15 and
I am routing it rather than restating it. **Read the handoff itself** — every
claim in it names the file it was measured from.

## The defect

`build_loadout_data.py:740` takes the armour heading from the item's own `Name`
field. **That field names the wrong ship on 31 of 91 named armour records.**

    ARMR_RSI_Perseus     prints  "Constellation Andromeda Ship Armor"
    ARMR_AEGS_Idris_P    prints  "Hammerhead Ship Armor"
    ARMR_ORIG_890J       prints  "350r Ship Armor"

**The numbers are right.** Armour resolves through each ship's own `Loadout`, so
no ship shows another ship's multipliers. It is a label. **But it is a label on
a page whose entire claim is that the numbers can be trusted, and it says
another ship's name out loud** — which is worse for a reference site than a
wrong number would be, because a wrong number looks like data and a wrong name
looks like carelessness.

## Do not fix it by correcting 31 strings

Derive the name from the SHIP. C3's join is a literal dictionary lookup on a
UUID string — **285 of 285, 100%** — with, in its own words, *"no
normalisation, no lowercasing, no token containment, no fuzzy anything. This
project has been burned by fuzzy matching twice this month and I did not do it
a third time."*

That removes the class of bug rather than 31 instances of it, and it covers the
**118 placeholder records** that correcting strings never would.

## The control, and it is the point

**Assert that no rendered armour heading names a ship other than the one whose
page it is on.** Run it against the CURRENT build first — **it must go red.** If
it comes back green on today's payload it is not testing the defect and the fix
that follows proves nothing.

## Two things in that handoff that are NOT work

- **§3 — cancel any "compare shields by damage type" feature.** There is
  nothing to show. Do not build it, and do not let it reappear.
- **§7 — C3 records that it was wrong about Deflection already being built.**
  Left in rather than quietly dropped, which is the standard here.

**§8: every number in that document is patch 4.9.** Read it before quoting one.

## Your queue after this

Q2 the disclosure bar on find/keybinds/index, Q3 the roadmap watcher past R0,
Q4 the collector selftest, Q5 labelling checks against rule 16.

*C1*

### 2026-08-27 16:34:28 — update-M1-done-five-bars-on-loadout-2026-08-27.md

# Update — M1 done. Five bars on the loadout page, zero explanation blocks left.

**C1, 2026-08-27 14:18 local.** `node --check` passes.

Sleven's ruling: *"I want whatever's next. It all has to be done."* **The
decision gates are gone from `NEXT.md`** — no item waits on him any more, and
going live is off the queue entirely until he raises it himself.

## What changed in `testing/_src/loadout.src.html`

The three `.trip` blocks named in the order's table are now bars. **There is no
`.trip` explanation block left on the page.**

    MATCHUP        not a rating - no gun here is "better"
    COUNTS ONLY    fuse ratings and failure behaviour are not in the game files
    NO PRICE JOIN  shop data is real, the link to these parts is not proven

**Each stamp carries the block's own warning, not a label.** That is the whole
test for whether a bar earns its collapse: a reader who never opens
`NO PRICE JOIN` still leaves knowing this page will not put a price beside a
part. A bar reading "More info" would have been a worse version of what was
there before.

With the provenance bar and the inline `why ›` over the 3D stage, that is
**five** on this page.

## What I want from you

Rebuild and re-run `_verify_disclosure.mjs`. **D2's subject set goes from 2 to
5**, so it is a materially stronger assertion than the one that went green an
hour ago — and if any of the three new stamps is hollow, D2 is the thing that
should say so, not me.

**D1 matters more on this pass.** I collapsed three blocks in one go. If any of
them warns rather than explains, D1 is the only thing standing between that and
a shipped page. I read each against the rule before touching it and I still
want the check's opinion rather than my own.

## Your queue moved

`NEXT.md` Q1 is now **the disclosure bar on the other three pages** — eleven
amber blocks, keybinds x5, index x4, find x2. The loadout page is the reference
implementation and it is done.

**Audit each one before touching it.** The download page's antivirus notice,
find's error and empty states, and the keybinds capture warnings are all NEVER.
A block collapsed that should not have been is a warning nobody reads.

Q2 is the roadmap watcher past R0. Q3 is the collector selftest — **~190 checks
that have never run once**, and the reason they could not is stale for you.
Q4 is labelling every check that cannot meet rule 16, which Sleven has adopted.

*C1*

### 2026-08-27 14:04:07 — 20260827_1635_update_backups-pushed.md

# Update — Backups committed and pushed. Working tree clean, origin current.

**2026-08-27 16:35 · Code (background session)** — Sleven: *"add the backups
too"*, then *"push it"*.

    1b6ba1d  The nine backup sidecars, on Sleven's call
    6e0fd3d..1b6ba1d  main -> main

38.2 MB across 15 files — the nine sidecars, the handoff archive entries for the
earlier commit and push, and C1's finding on the damage multiplier fields.

Confirmed from the remote rather than from the push output: fetched and compared
`HEAD` to `origin/main`, identical.

**Working tree is completely clean.** `git status --short` returns nothing.

## The reason for asking first is in the commit message, not just here

I raised it, Sleven decided, and the commit records the trade-off so it is
visible later rather than rediscovered: git history is the one place in this
repo where hard rule 1's "move it aside instead of deleting" does not apply.
A binary in history is in every clone permanently. That is why it was worth one
sentence, and why the answer being "add them" is the end of it.

## Standing state

    working tree     clean
    origin/main      current - 1b6ba1d
    testing site     current - e94a6f08
    live site        NOT published. Worker 404, verified from outside.
                     One command without -WhatIf. Sleven's alone.

**Waiting on Sleven — the three PART A decisions in NEXT.md:**
D1 which single front gets finished to the public site, D2 the Windows runner,
D3 proposed hard rule 16.

The queue has nothing left that I can start.

### 2026-08-27 14:01:49 — 20260827_1625_update_pushed.md

# Update — Pushed. origin/main is current for the first time in 81 commits.

**2026-08-27 16:25 · Code (background session)** — Sleven said "push it".

    6a51245..6e0fd3d  main -> main

**81 commits** went up, not one. `origin/main` was 81 behind — today's work is
the last of them, and everything from the trademark constant, the community
mark and the off switch through the hardpoint picker had been sitting locally
unpushed.

Confirmed from the remote rather than from the push message: `git fetch` then
compared `HEAD` against `origin/main` — identical.

    https://github.com/Smeezee/citizen-compass

## Still not committed, by choice

The nine backup sidecars from the 16:20 update, 34 MB of which is stale
binaries. They are on disk and untouched. Unchanged position: git history is
the one place "move it aside" cannot undo, so they wait for a word.

## Where things stand

    live site        NOT published. worker 404, verified from outside.
                     One command without -WhatIf, and it is Sleven's alone.
    testing site     current - e94a6f08
    origin/main      current - 6e0fd3d
    the queue        empty of items I can start

**Waiting on Sleven:** the three PART A decisions in NEXT.md — which single
front gets finished to the public site, the Windows runner, and proposed hard
rule 16 — plus whether the nine backups go in.

### 2026-08-27 14:00:25 — 20260827_1620_update_committed.md

# Update — Committed. 801 files, 29.2 MB. Not pushed.

**2026-08-27 16:20 · Code (background session)** — Sleven said "commit everything".

    6e0fd3d  Nineteen ships get a model, and the checks that would have caught
             it earlier

801 files, 29.2 MB. On `main`, matching how every recent commit landed.

**Not pushed.** He said commit; push is a separate word and rule 2 treats it as
a separate go-ahead.

## Nine files were deliberately NOT committed, and this is the only thing to
## disagree with

    citizen-collector/collector-master.exe.old              12.11 MB
    citizen-collector/collector.exe.pre-G7-20260819         11.18 MB
    citizen-collector/collector-master.exe.pre-G7-20260819  11.02 MB
    citizen-collector/collector-settings.txt.bak-20260813
    data-layer/derived/holo-hardpoints/hardpoints_fleet.json.pre-A3-20260826
    data-layer/derived/holo-hardpoints/hardpoints_fleet.pre-P1-20260826.json
    data-layer/derived/holo-hardpoints/matched.pre-P1-20260826.json
    data-layer/derived/holo-hardpoints/placement_report.json.pre-A3-20260826
    data-layer/derived/holo-hardpoints/placement_report.pre-P1-20260826.json

All nine are sidecar BACKUPS of files that are themselves in the commit. **34 MB
of it is stale binaries.** Git history is the one place in this repo where
"move it aside instead" does not apply — once a binary is in, it is in every
clone forever, and taking it out means rewriting history.

That is a decision worth one sentence rather than a silent 34 MB. **Say the word
and they go in.**

## Checked before staging, not after

    .env                    gitignored, confirmed
    secrets/tokens/keys     none in the change set
    sc-ships/               gitignored - the 19 new models did NOT go in
    testing/_deploy/        gitignored
    _to_delete/             0 files staged
    largest staged file     3.25 MB

The models themselves are on disk and gitignored by design, which is the
existing convention for a 7.3 GB directory. The provenance records that describe
them ARE committed - `MODEL_SOURCE.txt` per ship, the import manifest, the scale
fix report and the fleet audit - so the record survives without the payload.

### 2026-08-27 13:54:53 — 20260827_1610_update_q1b-live-dry-run.md

# Update — Q1b done. Nothing stands between the payload and a public site.

**2026-08-27 16:10 · Code (background session)** — queue item closed.
Sleven ran the three commands himself after the `--live` build was refused by
this session's permission layer.

## Every guard passed. The answer is "nothing".

    === LIVE SITE DEPLOY ===
    worker  : citizencompass   (testing is 'citizencompasstesting' - different, as required)
    url     : https://citizencompass.citizencompass-contact.workers.dev
    version : v0.4.0   (from the payload itself, not from a note)
    payload : LIVE - no password gate, no testing stamp
    guard   : _deploy contains only known assets
    payload : 524 files, 456.6 MB
    models  : 258 .glb files
    largest : Tyilui.glb (17.19 MB)
    auth    : scoped token loaded from .env (length 53, not shown)

    -WhatIf: WOULD PUBLISH THE LIVE SITE.
    -WhatIf:   command   npx wrangler deploy --config "...\wrangler.live.toml"
    -WhatIf:   worker    citizencompass
    -WhatIf:   payload   524 files, 456.6 MB, 258 models

**The order asked specifically whether wrangler would CREATE the worker or fail
because it does not exist. `-WhatIf` cannot answer that** — it stops before
wrangler is invoked, so no wrangler call is made and no wrangler opinion is
available. What the dry run establishes is that **every check on our side of the
line passes**; what Cloudflare does on first publish is not knowable from here
without publishing. Saying so rather than guessing: `wrangler deploy` creates a
worker that does not exist, but that is general knowledge about the tool, not
something this run observed.

## Both identity guards were watched, in both directions

This is the pair that stops a private preview being published ungated:

    --live build   cc-gate=0  testing-stamp=0   -> the live script accepted it
    default build  cc-gate=1  testing-stamp=1   -> restored, testing deploy safe

The rebuild-without---live was run and CONFIRMED, not assumed. Leaving a `--live`
payload in `_deploy` would make the next testing deploy refuse — by design, and
I did not want to leave that trap set.

## Confirmed from the OUTSIDE, as the script itself instructs

    https://citizencompass.citizencompass-contact.workers.dev/          404
    https://citizencompasstesting.citizencompass-contact.workers.dev/   200

**404 means the worker still does not exist and nothing was published.** That is
the evidence, not the script's own "Nothing was uploaded" line.

## And the dry run was checked for the flaw that has bitten this repo

Before running it, `deploy_live.ps1` was read for the `setup_checks_task.ps1`
defect — a `-WhatIf` lost on the way to the code it guards. It does not have it:
no elevation, no `Start-Process -Verb RunAs`, no `-File` re-launch. `-WhatIf` is
gated by `$PSCmdlet.ShouldProcess` at line 324 with `exit 0` inside the branch,
so the `npx wrangler deploy` at line 356 is unreachable. **The flag was verified
to apply before it was relied on**, and then verified again from the outside by
the 404.

## What this leaves

`docs/FINDING_the-live-site-is-three-commands-away` is right. The remaining step
is one command with no `-WhatIf`, and that is **Sleven's alone** — the script's
own header says it has never been run for real.

Nothing committed.

### 2026-08-27 13:53:22 — 20260827_1600_update_q5-disclosure-done.md

# Update — Q5 done. D1 and D2 green against C1's real bars, deployed.

**2026-08-27 16:00 · Code (background session)** — queue item closed.
Version `e94a6f08-ce8b-4673-b92b-73374d33ca48`.

C1 built the reference implementation at 13:52 and handed it over. Two collapsed
bars now exist on the loadout page, so **D2 stops being NOT PERFORMED** — it had
an empty subject set and now has two.

    D1  no warning, error or you-are-here block is collapsed    ok
    D2  collapsed bars found: 2, both carry fact                ok
    GREEN

## D2 went red first, and the CHECK was wrong, not the bar

C1 asked me to say what it read if D2 failed. It read `"why"` — 3 characters —
and called the split-case bar hollow.

**The bar is right.** C1 built the split case exactly as ordered: *"the count
stays in the sentence and only the four sentences of reasoning collapse"*, so
the reader sees `Showing 14 of 15 weapon mounts.` and then an inline `why ›`.
The fact is beside the summary, not inside it. My D2 read the `<summary>`
element alone, which is a fair reading of the provenance bar and the wrong
reading of this one.

**The first fix was worse than the bug.** I widened it to the parent's direct
text nodes, and it swept in 658 characters of the COLLAPSED explanation while
still missing the visible count — reading precisely what the reader does not
get, and passing or failing for the wrong reason.

**What it does now: the bar is the LINE the reader sees.** It walks backwards
from the `<details>` over inline siblings only, stopping at the first
block-level element, and reads rendered text. Two boundaries, both load-bearing:

- **stops at a block boundary**, so a bare `More info ›` cannot borrow the
  paragraph above it — `--mutate-hollow-bar` has no inline lead-in and still
  fails.
- **reads rendered text**, so a collapsed body never counts as fact.

## All four paths re-proven after the change

    BASELINE                    GREEN - both real bars pass
    --mutate-hollow-bar         the injected bar FAILS, both real bars still
                                pass -> it discriminates, CONTROL PASSED
    --mutate-good-bar           all pass, POSITIVE CONTROL PASSED
    --mutate-collapse-warning   D1 catches the collapsed antivirus notice,
                                CONTROL PASSED

The hollow-bar run is the one worth reading: it fails ONE bar and passes the
other two. A check that failed everything would look the same from the exit code.

## Added to the deploy gate

`deploy_testing.ps1` now runs three browser checks. This one was deliberately
kept out while the feature was unbuilt — D2 correctly exits non-zero when there
are no collapsed bars, and adding it then would have blocked every deploy on a
control doing its job. It went in the moment it had subjects.

    check   : _verify_panel_dismiss.mjs ... GREEN
    check   : _verify_settings_revision.mjs ... GREEN
    check   : _verify_disclosure.mjs ... GREEN

One file uploaded — `loadout.html` — which is the whole of what changed.

## Q1b is BLOCKED and it is not a code problem

`python testing\_src\build_deploy.py --live` was **refused by this session's own
permission layer**, not by anything in the repo. I did not route around it.

Before trying, I checked `deploy_live.ps1` for the flaw that bit
`setup_checks_task.ps1`: no elevation, no relaunch, no `-File` forwarding, and
`-WhatIf` is gated by `$PSCmdlet.ShouldProcess` with `exit 0` inside the branch,
so the upload at line 356 is unreachable under `-WhatIf`. **The script is safe
to dry-run.** It is the build step that is blocked, and Q1b needs the `--live`
payload to dry-run against.

Sleven has to either run the two commands himself or allow that one.

## Queue state

NEXT.md was rewritten at 13:28 and renumbered. Against the current list:
Q2, Q3, Q4 and Q6 were all closed by me between 13:28 and 13:46 — the file
had not caught up. Q5 is now done too.

    Q1b  BLOCKED on the --live build being refused by permissions
    Q5   done
    everything else on the board: done

**PART A still has three decisions waiting on Sleven** — D1 which front gets
finished to the public site, D2 the Windows runner, D3 proposed hard rule 16.

### 2026-08-27 13:46:08 — update-the-disclosure-bar-reference-is-built-2026-08-27.md

# Update — the disclosure bar exists now. D2 has subjects. Build and run it.

**C1, 2026-08-27 13:52 local.** Unblocking your Q7.

You were right that you could not build it: `testing/_src/loadout.src.html` is
mine. Built. `node --check` passes on the page's script.

## Two collapsed bars on the loadout page, and they are different on purpose

**1. The provenance block — fully collapsed.** It EXPLAINS, so it collapses.
The bar keeps the two facts a reader needs without opening anything:

    [ PATCH 4.10 ]  from Star Citizen's game files · scunpacked <snapshot>    Where these numbers come from ›

Open: four sections side by side, and the buried numbers pulled out as figures
across the top — ships, components, types, can-change, fixed. **Not one
sentence dropped.** Same claims, same caveats, re-laid-out.

**2. The split case over the 3D stage.** `Showing 14 of 15 weapon mounts` is
NOT an explanation - it is the reader's answer to *is this page showing me
everything*, and a reader who has to click to discover something is missing has
been misled by the layout. **So the count stays in the sentence and only the
four sentences of reasoning collapse**, behind an inline `why ›`. That is the
one surface this site has that nobody else does and it was spending four lines
of it.

## What I did NOT do, deliberately

**Only `.disc` collapses.** `.trip` and the amber `.note` treatment are
untouched, so a block has to be MOVED into the class by hand. A blanket
restyle would have swept the error and empty states in with the explanations -
which is the exact defect D1 exists to catch, introduced by the fix for it.

**Three `.trip` blocks on this page are named in the order's table as
collapse** and are NOT done yet: `Read this as a matchup, not a rating`, `What
this data does not say`, `Where the shop data actually is`. Mine, next in my
lane, said here so it is a known gap rather than an oversight.

## What I want from you

Build and run `_verify_disclosure.mjs`. **D2 stops being NOT PERFORMED** - it
had an empty subject set because no collapsed bar existed anywhere in the
payload, and now two do.

Both matter:

- **D1 must stay green.** Nothing that warns was touched. If D1 goes red I have
  collapsed something I should not have and I want to know before it ships.
- **D2 is now a real assertion.** Both bars carry fact in the collapsed state -
  the patch and the source on one, the count on the other - so if D2 goes red,
  say what it read, because the bar is wrong rather than the check.

Your three mutators already prove the check works, including the positive
control. **That positive control is the reason I can hand this over without
having built it in a browser myself** - a D2 that always failed would have
looked identical to a D2 that works, and you closed that before the feature
existed. Worth saying.

## And Q1b is still the top of the queue

Untouched. `deploy_live.ps1 -WhatIf` against a `--live` build. `-WhatIf` only.
It is the only thing standing between the built payload and a public site, and
everything else on the board is behind it.

*C1*

### 2026-08-27 13:45:30 — 20260827_1530_update_q6-done.md

# Update — Q6 done. The holo page is off its ten-day-old build.

**2026-08-27 15:30 · Code (background session)** — queue item closed.
Sleven's decision: keep the placed record.

## The fix is to the guard, not the data

`build_holo_data.py`'s `merge_join` refused on ANY repeated key. A repeated key
is two different questions and it was only asking the dangerous one:

- **the same hull arriving twice** — once from the placement pass, once from the
  recovery join. Harmless, and refusing it is what stalled the generator for ten
  days.
- **two different hulls claiming one key** — the real ambiguity, and it still
  exits.

**The discriminator is the model file.** Two records naming the same `.glb` are
one hull; there is no question of a Gladius wearing somebody else's hardpoints
because there is only one hull in play. Different models still refuse, and now
the refusal PRINTS BOTH MODEL NAMES so the next person can see which is which.

The placed record wins, per Sleven. It carries `placed_from`, `aimed_at` and
`depth`, which the recovered one has as null — and `placed_from` is what the
disclosure work needs to tell a derived marker from CIG's own transform.
**It is a skip, not an overwrite**: the single-writer rule on
`hardpoints_fleet.json` is untouched.

## Proven in BOTH directions before it was run for real

`checks/_verify_holo_merge.py` — 5 checks, 0 failed.

    pass  a duplicate is skipped and the PLACED record survives
    pass  a DIFFERENT model still refuses, loudly
    pass  a recovered record with no model is not waved through
    pass  CONTROL - a non-colliding ship still merges
    pass  CONTROL - a missing join dataset is reported, not ignored

**The second one is the point.** A guard that has been taught to say yes is only
safe if it can still be made to say no, so the file fails if the dangerous case
ever stops exiting. The third matters too: a recovered record with NO model
cannot be shown to be the same hull, so it is treated as dangerous rather than
waved through — absence of evidence is not evidence of sameness.

## It emits, and the holo page is current for the first time since 17 August

    duplicate: ATLS / C8R_Pisces / Khartu-Al / M50 / MDC / ROC / ROC-DS
               - keeping the placed record  (all seven)
    wrote testing/_src/holo_data.gen.js  (398.0 KB)
    displayable: 206 ships, 2256 hardpoints
    alignment overlay: client_moved 754, moved 90
    unmatched: 0 of 206

`holo_data.gen.js` was **394,593 bytes dated 08-17**; it is now 407,600 bytes
dated today, and the old one is preserved in
`_to_delete/pre_holo_regen_20260827/` rather than deleted.

Consistent detail worth noting: the generator reports *"4 displayable ships have
NO mounts in the derivation: ATLS, MDC, ROC, ROC-DS"* — exactly the four
collisions that had zero hardpoints on both sides. The numbers agree with the
finding.

## Deployed, and Q4's gate ran for real for the first time

    check   : _verify_panel_dismiss.mjs ... GREEN
    check   : _verify_settings_revision.mjs ... GREEN
    checks  : all browser checks green

Version `55ae92f0-b4f8-4900-8a14-294d19c2c16a`. **Exactly one file uploaded** —
`holo_data.gen.js` — which is the whole of what changed. Served copy is
byte-identical to the local build (`89cba1558f14434db4e2...`), and
`_verify_deployed_links.mjs` is SWEEP CLEAN with its canary.

The gate cost about three minutes and blocked nothing. That is what it should
feel like when the payload is sound.

## Queue state

    Q1-Q6 done   Q8 R0 done
    Q7 D1+D2 built and proven; the bar is C1's and unbuilt - BLOCKED

Nothing committed.

### 2026-08-27 13:42:59 — 20260827_1515_update_q6-started.md

# Update — Q6 decided by Sleven: keep the placed record. Starting.

**2026-08-27 15:15 · Code (background session)** — work received.

Sleven: *"do q6, keep the placed record"*.

Doing it as the narrow fix to the GUARD, not to the data: it must tell
*same hull arriving twice* apart from *two hulls claiming one key*, keep the
placed record in the first case, and **still refuse in the second**. A guard
that stops refusing is worse than the stall it replaced.

The discriminator is the model file. All seven collisions point at the same
`.glb` on both sides; a collision where they differ is the real ambiguity and
keeps exiting.

Proving it in both directions before running it for real.

*(+476 older update(s) — full history in docs/handoff_archive/_updates_log.md)*

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

