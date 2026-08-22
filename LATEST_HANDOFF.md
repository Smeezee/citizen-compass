# LATEST_HANDOFF.md — Update #579 — 2026-08-22 4:19 PM

---

# CITIZEN COMPASS — LATEST HANDOFF

Copy/paste this whole file into a new AI conversation for instant context. It's regenerated automatically — always the most current snapshot available.

---

## CURRENT STATE (auto)

**Generated:** 2026-08-22 16:19:03 (auto-regenerated every time a file lands in inbox/ or this script runs — don't hand-edit this section)

**Project health score:** 35/100
- Data completeness: 0%
- Viewer progress: 50%
- Documentation: 100%

**Ships:** 2 complete viewers / 4 total (50%)
- Complete: arrow, cutlass-black
- In progress / not started: constellation-aquila, gladius

**Data layers:**
- data-layer: 60732 files (10648.37 MB)

**Scripts:** 37  |  **3D models:** 723  |  **Docs:** 1049

---

## RECENT UPDATES (append-only, newest first)

### 2026-08-22 16:18:37 — update_a2_community_mark.md

# Update - A2, the "Made By The Community" mark

A2 done. Applier, pixel-level detector, and a build that refuses to finish while
a CIG-sourced image is missing the mark.

- `scripts/community_mark.py` composites the Fan Kit mark bottom-right at 70%,
  following the hologram-concept precedent rather than inventing a second
  approach. CIG's prohibitions are structural, not commented: one scale factor
  for both axes so it cannot be distorted, never transposed so it cannot be
  flipped, its own pixels copied so it cannot be recoloured, nothing drawn on
  top. Below CIG's 50% opacity floor it raises instead of clamping.

- MY FIRST DETECTOR WAS WRONG, and measuring it is what found that. The obvious
  statistic - "is the corner brighter where the mark is opaque" - scored 5.36 on
  a mid-grey fixture against 57 and 68 on dark and light ones. The mark is not a
  flat silhouette: 72% of it is opaque and that region averages luminance 113,
  mid grey. It would have reported the mark MISSING on exactly the mid-tone
  images a ship render actually produces. Replaced with correlation against the
  mark's own structure: marked 0.968-0.999, unmarked at most 0.021.

- The negative control RUNS THE REAL BUILD, not a copy of the guard: an unmarked
  CIG-sourced image makes build_deploy.py exit 1; the same image marked makes it
  exit 0.

- THAT CONTROL SCORED A FALSE PASS ON ITS FIRST RUN. Registering a CIG asset
  also trips A3's contact gate, so the build failed before ever reaching the
  mark guard - and "an image without the mark is refused" went green. Refused,
  but for the wrong reason. It now supplies a contact and asserts which refusal
  it got. Ninth silent-success instance logged.

## Reported, not fixed - hard rule 8

The 241 ship thumbnails already on the site do not carry the mark.
`docs/workorder-image-provenance-and-renders.md` establishes that the upstream
pack is governed by terms naming "Made by the Community", and equally that it is
NOT established whether any individual image is a CIG asset, a screenshot or a
render. Marking all 241 is a bulk mutation of the site's whole visual surface
(rule 5) on a Fan Kit compliance question (rule 8 - report it, do not fix it),
and Part 2 of that same work order plans to replace every one of them with our
own renders. That is Sleven's decision, not one I take silently.

The mark file itself is NOT committed to the repo - it is read from the Fan Kit
on disk or from CC_FANKIT_DIR. Copying a CIG asset into a public git repo is a
separate decision from the one already taken.

Next: A4, the off switch - the item the order says matters most.

### 2026-08-22 15:58:15 — update-order-attribution-received-20260822155811.md

# Update — ORDER received: the attribution furniture and the off switch. Starting A1.

`docs/ORDER_the-attribution-and-the-off-switch-2026-08-22.md`. A1-A6 in order,
appending to the ledger per item with the sha.

Scope: the verbatim trademark notice as ONE constant in always-visible chrome on
every page; the Made By The Community mark with a refusal for images that lack
it; the source-and-contact notice driven from config with a loud build failure
if absent; THE OFF SWITCH (tag at the data layer, one command, exercised for
real, docs/TAKEDOWN.md); measure the static-asset exposure and REPORT ONLY; then
sweep, deploy, verify from the served bytes.

Explicitly NOT doing: fetching, downloading or touching any RSI asset, and no
scaffolding "ready for later" for that. A5 is measured and reported, not fixed.

A4 is the one that matters and I will spend the time there.

### 2026-08-22 13:33:13 — update-P-run-complete-20260822133309.md

# Update — one-screen run COMPLETE. P1-P8 all DONE. Deployed and pushed.

URL: https://citizencompasstesting.citizencompass-contact.workers.dev
Version c3d8559f.

## Page height, before and after

|            | before  | after | viewport |
|------------|--------:|------:|---------:|
| 1920x1080  | 1,952px | 995px |    1,080 |
| 1366x768   | 1,891px | 683px |      768 |

Both fit with 85px spare. **Nothing had to be cut** — what made it fit is the
three columns and their internal scroll, not shrinking. Type went down one
step, 16px to 15px.

## What the marker click turned out to be

**The click was never broken.** Before changing anything I drove the real path:
captured the delegated handler, built the element a browser would hand it,
dispatched. `sel` went to the right slot and the picker rendered 4,919 chars,
every time. There is no raycasting in the page — the markers are DOM buttons —
so the suspected cause could not apply.

**The picker rendered ~1,050px down a 1,952px page.** Sleven clicked, the page
updated correctly, and the part that changed was below the fold. That is the
same defect P6 reports for `Try another alongside` — one defect filed as two.

Rotation is still a contributing factor and I haven't pretended otherwise: 19px
targets that move, and a browser only fires `click` when mousedown and mouseup
share an element. I can't test that without a browser and haven't claimed it.

## One thing worth flagging

My own measuring tool silently measured the wrong thing **three times** while I
was writing it. It now applies media queries per viewport and asserts its own
correctness before reporting any number.

### 2026-08-22 13:15:15 — update-order-one-screen-received-20260822131511.md

# Update — ORDER received: the ship page fits on one screen. Starting P1.

`docs/ORDER_the-ship-page-fits-on-one-screen-2026-08-22.md`. RUN CONTINUOUSLY,
items P1-P8, appending to the same ledger.

Scope: three columns (components / model / readout), a bounded viewer, a
compaction pass, a visible stop-rotation control, the marker-click bug, the
second build appearing where the eye is, and the whole thing fitting 1920x1080
without scrolling. Then sweep, deploy, verify.

NOT in scope and I will not touch: the material/lighting render pass, hardpoint
marker POSITIONS (ruled settled), and the two shared-viewer greps.

Starting with P5's diagnosis before the layout work, because if the marker click
turns out to be "the picker updates below the fold" then P1 and P7 are its fix
and I should know that before I move anything.

### 2026-08-22 12:23:00 — update-erratum-fixed-20260822122256.md

# Update — ERRATUM fixed, §4 audit done, deployed and verified

URL: https://citizencompasstesting.citizencompass-contact.workers.dev
Version 4cdc686b. Commits c7fa846, b4e22d4, and the deploy record.

**The count, from the served page: 229 → 27.** 221 name cells now reach the ship
page, 27 reach RSI, 6 reach nowhere. The 229 is not an estimate — `--prove`
restores the original function and the check reports exactly 229.

**27, not 33.** 33 ships have no ship page; 27 have a pledge_url to fall back
to, six have neither and render plain. 27 + 6 = 33.

**Fixed at source, not at the glyph.** The build decides per record what the
cell is; `nameCellHtml()` reads it. `decorate()`, its observer, its two guessed
timers and the whole text-matching scaffolding are gone. The link data was also
being injected after `buildMatrix()` had already run — it now arrives before the
ship records.

**§4 audit: 208 driven, 38 grep-only.** Most greps are correct (absences, and
rule 8's text). One was the erratum's shape — **N4**, which greped for a guard
rather than proving it. Driven now: one load per ship, none per tab. The feature
was sound. N1's weak control hid a broken feature and N4's hid a working one,
and a weak control cannot tell you which you have.

**Found in my own harness:** the DOM stub never reflected `textContent` into
`innerHTML`, which is how the page's `escapeHtml` is built — so it returned ""
for everything and the cells I was reading had blank names. The harness now
asserts `escapeHtml` works before reading anything through it.

### 2026-08-22 12:07:22 — update-erratum-rsi-received-20260822120718.md

# Update — ERRATUM received: every ship name still opens RSI. Fixing first.

`docs/ERRATUM_ship-names-still-go-to-RSI-2026-08-22.md`. This is mine and it is
serious: N1's whole purpose is defeated and there is currently NO route to any
ship page. Sleven found it in ten seconds.

The cause is exactly as C1 diagnosed: `decorate()` matches on the cell's own
text, `nameCellHtml()` appends a link glyph, so `td.textContent.trim()` is
"Redeemer 🔗", `CC_LOOKUP` misses, and the function silently bails leaving the
RSI anchor it was born with. 229 of 254 rows.

**And my N12 control could not have failed.** It asserted `shipPageUrl` and
`loadout.html#` appear in the bytes. They do. The feature still does not work.
That is the seventh instance of this shape in this project's log and I wrote it.

Fixing at source per §2 — one writer, no observer, no timers, no text matching —
then the §4 audit of the rest of the N-run, then deploy and verify by COUNTING
served name cells that point at RSI. Must be 33, not 229.

### 2026-08-22 01:40:04 — update-N-run-complete-20260822014000.md

# Update — one-ship-page run COMPLETE. N1-N12 all DONE. Deployed and pushed.

9 commits, `c221d18..5632384`. No item BLOCKED. Ledger appended per item.

URL: https://citizencompasstesting.citizencompass-contact.workers.dev
Version f6507a7d. NOT the live site.

## The headline

**index.html: 1,622,716 → 410,219 bytes. A 75% cut.** Three.js, OrbitControls,
GLTFLoader, the DRACO decoder and its wasm — about 1.07 MB of vendor payload
downloaded to look at a table — are gone, along with the ship panel, its viewer
and 46 dead CSS rules.

## The N2 checklist, ticked

In-game price, pledge price, sold at, RSI link, confidence, record number,
notes, status, role, manufacturer, model folder, related ships — all on the ship
page, each asserted by name against the rendered HTML.

**One field never existed:** the site's `last_verified_patch` is null on all 254
records, so index rendered "not recorded" for every ship in the fleet. The ship
page states the snapshot's patch instead.

## What I nearly got wrong

33 ships have no ship page and **27 of those carry a pledge_url**. Replacing
their name cell would have left those rows with no link at all. They keep RSI
and say why.

## The N8 control, run for real

A fixed port was given a fitment rule — what the generator does when a port says
`Editable` — and nothing else was touched. It moved out of the collapsed group,
the count dropped 36→35, and flipping it back put it where it was.

## Arguing with N10, as asked

I built the quiet end deliberately: a 3px edge, a small delta chip, one 0.22s
pop, gone in 2.2s. Nothing blocks, queues or animates the value itself. **The
boundary is the twentieth swap** — anything that has to be waited out becomes an
obstacle. If it still reads as too much, the dial is `CHANGED_MS`, and setting
it to 0 leaves the page working exactly as it does minus the mark.

### 2026-08-22 01:08:20 — update-order-one-ship-page-received-20260822010816.md

# Update — ORDER received: one ship page, and it opens quiet. Starting N1.

`docs/ORDER_one-ship-page-and-the-quiet-default-2026-08-22.md`. RUN
CONTINUOUSLY, items N1-N12, appending to the same ledger. Supersedes
`ORDER_one-ship-page-not-two-2026-08-22.md`, which I read but never started —
ignoring it.

Scope: retire the index ship panel and its viewer, move the whole Acquisition
block onto the ship page without dropping a field, one build by default with
`Try another alongside`, kill the doubled readout, fold fixed ports into a
closed disclosure driven by `Editable` and never by a type list, correct the
false "nothing here is estimated" claim about marker positions, make the first
swap unmissable, one-click return to stock, sweep, deploy to testing, push.

Not doing: no welcome modal or tour, no new page, no live deploy, no
`git add -A`, and no re-exporting or hand-placing models.

Starting N1.

### 2026-08-21 23:59:13 — update-testing-deployed-20260821235909.md

# Update — testing site DEPLOYED and verified; ruling folded in

URL: https://citizencompasstesting.citizencompass-contact.workers.dev
Version 9618dd8d. NOT the live site. Commits 3156e6b, c221d18.

**The ruling is now a LOCKED entry in `docs/ARCHITECTURE_DECISIONS.md`**: every
run that changes what the site serves ends by deploying to testing, no
permission; the live site stays Sleven's alone.

**The deploy guard refused the first attempt and was right** — four new
generated files weren't in its allow-list, because the build derived its list
from PAGES while the standalone guard carried a hand-mirrored copy. Its own
comment had predicted that drift. Fixed by construction: the list now lives in
`testing/_src/deploy_pages.py` and both sides import it.

**Verified from the served bytes, and then beyond grepping**: I ran the served
page's own six script blocks against the four served data files. 316 ships,
1,200 hull markers, 305 engineering hulls, five tabs rendered with Crew
correctly absent, 19,796 characters of build column and 18 readout values.
`<script src="cc_viewer.js">` present; all five generated files sha256-identical
to what the build wrote.

**Found, not mine:** the password gate is on `index.html` only — `/loadout`,
`/find`, `/keybinds`, `/holo`, `/download` and `/stick-test` all serve 200
ungated. Pre-existing. On the punch list and beside the standing rule, because
"private preview" is doing real work in that rule's reasoning.

Sweep after everything: 42 ok, 1 NOT PERFORMED (pre-existing), 2 skipped.
Pushing now.

### 2026-08-21 23:55:21 — update-ruling-testing-deploys-20260821235517.md

# Update — RULING received: testing deploys are automatic

`docs/RULING_testing-deploys-are-automatic-2026-08-22.md`. Standing, not
just this run. Folding into `docs/ARCHITECTURE_DECISIONS.md` now, then
re-running the full deploy sequence so the served bytes match the final tree.

He is right about the cost and it is worth recording that I caused it: L1-L17
and M0-M6 finished and sat undeployed. Work that is not on the testing site has
not been delivered — the review surface is the deliverable, not the commit.

Note: I deployed once already this turn on his direct instruction. Since then I
changed the deploy guard's allow-list mechanism, so I am re-running dry run ->
guard -> deploy -> verify rather than assuming the earlier deploy still
describes the tree.

### 2026-08-21 23:44:21 — update-deploy-testing-requested-20260821234417.md

# Update — testing deploy requested, starting

Sleven asked for the testing site to be deployed now: dry run first, then the
real deploy, then verification from the served bytes that loadout.html carries
cc_viewer.js and the tab shell.

NOT the live site. Following docs/RELEASING-THE-SITE.md section 5: rebuild
(default, no --live), -WhatIf, then the real run.

### 2026-08-21 23:17:42 — update-run-complete-20260821231738.md

# Update — ship page run COMPLETE. L1-L17 and M0-M6 all DONE. Pushed.

15 commits, `c27588d..6209c8d`, pushed to main. Ledger appended per item.
No item is BLOCKED.

**Not done, as instructed:** the live site was not deployed and no release was
cut. `git add -A` was never used — every commit names its paths.

## The report the order asked for

**L1 types the scan selected:** 27, derived not transcribed. Size 431 KB → 3,551
KB raw; **37.3 KB → 274.8 KB gzipped.** The growth is scope: 25,875 ports now
instead of ~4,300 slots of five types, because L4 says a fixed port is shown.

**L3 named examples, from the rendered HTML:** the Avenger Stalker's right-wing
missile rack OFFERS the Aegis Eclipse 20xS3 bomb rack; the Retaliator 64xS3
front rack (size 5) is ABSENT entirely from that size-3 port.

**L3, argued with as asked — 99.4% yes.** CompatibleTypes + the size window
decides fitment for 7,633 of 7,681 ports where CIG's own fitted part can be
checked against the port's own rule. The 48 failures are CIG disagreeing with
itself. Two traps that would have shipped silently: enforcing `SubTypes`
literally empties every quantum picker on the site (253 ports), and `$editable`
is a pseudo-subtype that emptied the Origin M80's power-plant picker.

**L5, the 77 untagged armour items:** the question has a different shape.
`RequiredTags` is not the attachment mechanism — 0 of 210 armour items carry
one. Armour attaches through the ship's own Loadout and resolves for all 305
records that have an armour port. The 11 without are 9 exosuits plus the
**Greycat PTV** and the **Aegis Idris-P**.

**L6 in words:** on the Avenger Stalker, fitting a Revenant Gatling raises DPS,
alpha, EM and power draw and LOWERS total mass.

**L8 negative half:** yes — breaking cc_viewer.js leaves BOTH pages with no
viewer.

**Punch list:** three things block going live — nothing in the shop layer is
verified (0 of 7,932 against 26,657 price rows), the live worker 404s, and
nobody has opened the ship page in a browser.

**Addendum §2, argued with as invited:** per-layer loading saves 4.4 KB of 274.8
KB (1.6%). Per-SHIP loading would take the page to ~14 KB (95%). Measured, not
built — 316 files and a deploy-guard change is a decision, not mine to take.

## What I think is wrong

Nothing in the order was wrong in substance. Two figures did not reproduce and I
used mine: `unchecked_hull` is **0**, not 21, and L5's tagged/untagged armour
split does not exist in this snapshot at all.

**The thing I would raise:** `Name` vs `ClassName` bit three separate times in
this one run — my livery check, my own diagnostic, and the ship dropdown. The
addendum was right to promote it, and I have written it into the punch list as a
class of defect with places to look.

### 2026-08-21 23:13:13 — update-L15-L17-M1-M6-20260821231309.md

# Update — L15, L16, L17 and M1-M6 done; final sweep running

Commits 6fe4575 (L15), a2c822e (L16), 502f9e2 (M1-M4 + L17). M5/M6 staged.

**M1's network trace found a bug nothing else could have.** A top-level `const`
in a classic script is a global LEXICAL binding, not a property of `globalThis`.
The lazy loader read `undefined` after a perfectly successful load, decided the
file had failed, re-fetched it on every open, and rendered "loading the
engineering layer" forever. Nothing about the page looked broken. Only counting
fetches showed it. Layers now register themselves into `window.CC_LAYERS`.

**Arguing with the addendum's §2, as invited, with numbers.** Per-layer loading
saves 4.4 KB of a 274.8 KB page — 1.6%. The weight is in the SHIPS, not the
layers: one ship's complete bundle is 10.1 KB gz median, so loading one ship
instead of 316 would take the page to ~14 KB. A 95% cut against 1.6%. Not built
— it is 316 generated files and touches the deploy guard's allowed list, which
is a decision rather than an oversight. Recorded with the numbers.

**M2:** 678 relays / 1,419 fuse slots on 305 hulls — the addendum's figures
reproduce, including Idris-P 15/37 and Vulture 1/2. Counts come from the actual
child ports, not the `RELAY_Nslot` label. No empty positions, asserted by
counting bars against the data on a hull with relays of differing sizes.

**L17's three sweep failures were all investigated**, not adjusted around: a
stale build the drift check correctly caught, a by-design seam taught to it and
proven both ways, and a check whose local API was simply not running (started
it; 18/18).

Final sweep running now, then push.

### 2026-08-21 22:50:01 — update-L10-L14-done-20260821224957.md

# Update — L10 through L14 DONE

L10 commit f37c882, L11-L14 in the commit above.

**L10.** 1,200 hull markers on 157 hulls, bound to the game's own `PortId`.
`selectPort()` is the only place the page selects a port — asserted both by
comparing marker-opened and list-opened pickers byte for byte, and by counting
the selection paths in the source. 14 ambiguous points were dropped rather than
assigned to whichever of two ports came first.

**L11.** The pledge link travels with the ship. Asserted on both sides — a link
that left without arriving is not a move. All 221 matrix rows resolve.

**L12.** The link carries ship, both builds and the open tab. All 20 changed
ports round-trip, not one.

**L13.** CIG-vs-summed is a badge on the stat, not a footnote a column move
could separate from its number.

**L14.** Three named examples: Origin M80 (no model), 33 unbuilt ships, Aegis
Eclipse (no mount data). The Stingray's absence is asserted.

102 assertions on the page control, 23 on the viewer control. Starting L15.

### 2026-08-21 22:39:55 — update-L8-L9-done-20260821223951.md

# Update — L8 and L9 DONE

Commit 66b5363.

**L8.** The 3D viewer is now `testing/_src/cc_viewer.js` and nothing else. In
the shipped bytes `new THREE.WebGLRenderer` appears once, in the module, zero
times in either page. The negative half runs on every invocation, not behind a
flag: break the module and BOTH pages come back with no viewer.

**The extraction paid for itself immediately.** `build_deploy.py` injected the
DRACO decoder with a bare `.replace` anchored on a line the extraction moved. A
`.replace` that misses is silent — it would have shipped a build with every
model failing to decode, reporting success. It also rewrote the whole 25-line
load callback, holding a second copy of the material setup and the staleness
guard. Both are now single asserted seams. A third guard (the TDZ hoist) fired
too and stopped the build rather than shipping a page that throws on load.

**L9.** The model is on `loadout.html`, laid out to the addendum's tabbed shape
from the start rather than retrofitted. 201 of 221 linked ships carry one; the
other 20 get L14 case 1's honest sentence.

**Also caught by the build's own gate:** a port holding a fitted gun but
declaring no `CompatibleTypes` was being dropped — six of the Javelin's
twenty-two cannons. Our pilot-DPS sum had gone 275/275 → 272/275. Fixed and back
to 275/275.

**Third encounter with the name-vs-identity defect:** hardpoint names are NOT
unique within a ship — 287 of 316 hulls, 11,283 slots, and the RSI Polaris has
thirty ports called `MEC`. `PortId` is unique across all 57,759. Every slot now
carries it, which is what L10 needs.

Starting L10.

### 2026-08-21 22:20:40 — update-M0-section0-audit-20260821222036.md

# Update — addendum §0 audited against L1-L7. Nothing was keyed on Name.

Every emitted table is keyed on ClassName, className, a port rule, a
RequiredTags string or an array index. Not one touches a display name. All 316
records survive; a Name-keyed build would have lost 29.

§0's control passes: `AEGS_Hammerhead` (226 ports, 9 crew) and
`AEGS_Hammerhead_GS` (223, 8) both come through, and the control asserts they
DIFFER rather than only that there are two.

**One real defect the collision does cause, now fixed.** Joining correctly is
not enough — the ship dropdown rendered "Aegis Hammerhead" twice, identically.
Shared names now carry the distinguishing part of the ClassName, derived from
the key and applied only to the 22 names that need it.

**And I hit this class of defect independently at L7**, before the addendum
arrived: my own livery check keyed on display name and merged
`DRAK_Caterpillar` with `DRAK_Caterpillar_Boarded`. Two encounters in one run.

Continuing to L8, building it to the addendum's tabbed shape.

### 2026-08-21 22:18:40 — update-addendum-received-20260821221836.md

# Update — ADDENDUM received mid-run, auditing L1-L7 against §0 now

`docs/ADDENDUM_ship-page-tabs-and-the-name-collision-2026-08-22.md`. Folds into
the run. M-items go in after L17.

Two things arrive with it:
1. **§0** — 22 display names duplicated across 51 records. Auditing every L1-L7
   output for a `Name` key before I go further.
2. **§1/§2** — the ship page is tabbed layers with per-layer lazy loading. Read
   before L9, as instructed; L8 and L9 will be built to that shape rather than
   retrofitted.

L1-L7 are DONE and committed (703c164, f858214, 9d86082, b602193, 63a3865,
fdaa586). The audit result goes in the ledger before I start L8.

### 2026-08-21 22:13:55 — update-L6-done-20260821221351.md

# Update — L6 DONE, the full readout

Five stats and two budgets became twenty-odd stats plus power pools and the
armour signal multipliers. Mass is carried and moves on a swap.

Named acceptance, found by searching rather than by hoping: on the Aegis
Avenger Stalker, fitting a Revenant Gatling raises DPS, alpha, EM and power
draw and lowers total mass — four readouts, two directions, one click.

Two fields that would have put a wrong number on the page: a cargo grid states
no SCU (`InventoryOccupancy` is how much room the grid takes up, 0 for all 143
of them — capacity is the dimensions in 1.25m units), and power pools use -1
for "no cap".

67 assertions. Starting L7.

### 2026-08-21 22:11:05 — update-L5-done-20260821221101.md

# Update — L5 DONE, armour and the matchup

Commit b602193.

**Correcting the order's premise, with measurement.** `RequiredTags` is not how
armour attaches — 0 of 210 armour items carry a top-level one, so the "133
tagged / 77 not" split does not reproduce in this snapshot. Armour attaches
through the ship's own `Loadout`, at a port whose Type is `Armor`. It resolves
for 305 of 316 records with no partial resolution. The 11 without are 9 exosuits
plus the **Greycat PTV** and the **Aegis Idris-P** — those two are a real gap and
go on the punch list.

**Survivability is not one number**, and the page now says which: 10 distinct
damage-multiplier profiles, plus signal multipliers, deflection, penetration
resistance and the ship's own `PenetrationMultiplier`.

**The control's second half needed a new panel.** `Damage.Dps` splits a weapon
across the same six channels armour resists, so the page now computes effective
DPS against the armour profiles actually in the data. Named: the PyroBurst
Scattergun does 166 DPS against an Eclipse-like hull and 139 against a
Hammerhead-like one — same gun, 17% apart. The panel says in words that this is
a matchup, not a rating.

`app/models.py` still has no hull-resistance dimension — on the L16 punch list.

Controls: 59 assertions, self-test and mutate both behave. Starting L6.

### 2026-08-21 22:08:17 — update-L3-L4-done-20260821220813.md

# Update — L3 and L4 DONE

Commit 9d86082 (ledger entry staged for the next commit).

**L3.** The picker read `P[k].t===slot.t && P[k].s===slot.s` — every part of the
type, on every ship. It now reads the port's own CompatibleTypes + size window.
Both halves named from the RENDERED HTML: the Avenger Stalker's right-wing
missile rack offers 16 parts including the Aegis Eclipse bomb rack; the
Retaliator 64xS3 front rack (size 5) is absent entirely, not greyed. All 21
editable ports on that hull sweep clean.

**Arguing with L3, as asked: 99.4% yes.** CompatibleTypes + the size window
decides fitment cleanly for 7,633 of 7,681 ports where CIG's own fitted part can
be checked against the port's own declared rule. The 48 that fail are CIG
disagreeing with itself. Two traps that would have shipped silently:
`SubTypes` enforced literally empties every quantum picker on the site (253
ports), and `$editable` is a pseudo-subtype that emptied the Origin M80's power
plant picker.

**L4.** Fixed ports render, name the part in them, contribute to totals (proven
by removing them and watching em/pw/mass move), and open no picker. The
`last_verified_patch` override is data, and the control plants one and confirms
it lands.

Control `checks/_verify_ship_page.mjs` drives the page's own script in a vm and
reads the HTML. 53 assertions. Proven by inversion AND by planting the real
defect — widening `fitsFor` back fires 5 assertions.

Starting L5.

*(+348 older update(s) — full history in docs/handoff_archive/_updates_log.md)*

---

## PROJECT NOTES (from most recent full handoff doc)

# HANDOFF — the master order is filed, and nothing was lost to the credit cutoff

    from    C1, 2026-08-10
    for     Code, and the next session that reads LATEST_HANDOFF.md
    basis   Sleven: "All the stuff that was supposed to be done on the website
              didn't get pushed before I ran out of weekly credits. Weekly
              credits are back up now. Now move."

---

## 1. The premise was wrong, and that matters more than the fix

Sleven believed work was lost when his weekly credits ran out. **Verified
against the repo, not reasoned about:**

```
git log --oneline origin/main..HEAD          -> EMPTY (zero unpushed commits)
grep -c "listening" testing/_deploy/keybinds.html   -> 12
grep -c "listening" testing/_src/keybinds.src.html  -> 12
```

**Everything committed is on `origin/main`. The rebind flow is live on the
deployed page.** Commit history confirms it: `9dc7acf` (keybind page reads and
writes a real profile), `f8b501c` (you can now change a binding), `2e24515`
(exporter checks), `6a4edbf` (three days of collector work). All pushed.

**What actually happened:** four fix orders were written and filed to `docs/`
and Code never ran them. That's the entire gap. Nothing was lost; four things
were queued and never picked up. Whoever reports back to Sleven should say this
explicitly — he is otherwise going to keep looking for a phantom problem.

## 2. What's now in the queue

`docs/prompt-code-MASTER-clear-the-queue-2026-08-10.md` — filed via `inbox/`,
watcher confirmed at 10:59:26. It is the run order for everything outstanding
and it **carries Sleven's explicit go-ahead to commit, push AND deploy** at the
end, which is unusual and is stated plainly in the document.

It sequences four existing orders (deliberately by reference, not restated — one
writer per artifact, hard rule 14):

- `docs/prompt-code-holo-viewer-fixes-and-fleet-2026-08-10.md`
- `docs/prompt-code-keybind-rebind-joystick-2026-08-10.md`
- `docs/prompt-code-keybinds-search-and-navkeys-2026-08-10.md`

plus two things not previously ordered: landing the fonts, and the collector
shortcut-ordering fix.

**Two source facts re-verified so Code doesn't have to re-establish them:**
joystick rebind genuinely is absent (lines 1786 and 1795 are the only two
`commit(...)` calls, both `'kb1_' + ...`), and `#kbbq` genuinely has no
`stopPropagation` guard (declared 1555, read into `elQ` 1594, no guard anywhere
near it) unlike `#q` which has one.

## 3. Fonts — the licence question is closed, and I made the scope call

Five files staged and verified on disk at `data-layer/derived/fonts-ofl/`;
`testing/_deploy/fonts/` still holds only the placeholder `README.txt`.

C3 read the actual `LICENSE` file inside each font's real distribution package —
Saira Condensed, Rajdhani and Chakra Petch are all genuine SIL OFL 1.1,
redistribution permitted with `OFL.txt` travelling alongside. That closes the
"confirm the licence before shipping" condition.

**Scope call, made by C1 rather than stalling the order, and flagged as C1's:**
SC fonts on chrome only (headings, tab labels, panel titles, buttons — `.cc-ui`),
**not** on the 691-row action table. Reason: `_layer.src.html` already ships a
five-mode accessibility font switcher including Atkinson Hyperlegible, scoped
`*:not(.cc-ui):not(.cc-ui *)`. Marking the whole keybind panel `.cc-ui` would
make the densest small-text screen on the site the one screen that ignores a
low-vision reader's setting, and Saira Condensed is a condensed face, which makes
that strictly worse. This is C3's recommendation in
`docs/RULING_holo-viewer-models-keybind-overlay-and-fonts-2026-08-09.md` §3,
adopted. **Chrome-only first and widening later is a one-line change; shipping
everywhere and discovering the accessibility hole later is a regression somebody
has to notice first.** Sleven can overrule it knowingly.

## 4. Sleven's shortcuts are currently broken and only he can fix them

The investigation run on 2026-08-09 overwrote his real Desktop and Start Menu
`Citizen Collector.lnk` files, pointing them at a scratch folder. The rule-6
guard correctly blocked repointing them from inside a session. He's been told:
repoint both to the real `citizen-collector\collector.exe`, or delete both and
let the next real launch recreate them. **`DesktopSim` is deliberately still in
place so they launch something rather than dangling — do not remove it until he
confirms the shortcuts are fixed.**

## 5. Still Sleven's alone, unanswered, and deliberately not guessed

- **Cutlass Black "Best In Show" airframe** — same as base or not. `MANUAL_MATCHES`
  stays empty. A guess produces 15 wrong markers that look as confident as right
  ones.
- **Publishing a collector release / installing `gh`** — not authorised. The
  update-feed 404 is currently the *safe* state; a feed pointing at a nonexistent
  asset turns a clean "no update found" into a failed download on every install
  every six hours.
- **Cloud-upload R2 bucket + Worker + key** — account-level, offered, unanswered.
- **UEX token, PostgreSQL password, Cloudflare token** — all three still
  unrotated after exposure.
- **CIG description-rights question** — 5,344 item descriptions still cannot ship.

