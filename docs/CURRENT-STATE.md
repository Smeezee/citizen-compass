> SUPERSEDED 2026-09-12 - this file is NO LONGER the project's current state.
> `BOOT.md` at the repository root is, generated from the file tree by the inbox
> watcher every ten minutes. This file is kept for history and is not updated.

    superseded-by  BOOT.md
    superseded-on  2026-09-12
    reason         Sleven's ruling. A desk that read this file, NEXT.md, LIVE.md and
                   OWNERS.md at boot spent about 115,000 tokens before doing any
                   work, measured in
                   claude/FINDING_the-automation-is-not-the-expense-the-boot-read-is-2026-09-12.md
    what changed   what this file WAS for - telling a desk what is true right now.
                   Its ownership is unchanged and nothing in it is deleted. It is a
                   deep file now: BOOT.md points into it, and a desk opens it when a
                   job needs this file, never to find out what is current.
    note           DO NOT create a second file with a state name to carry this
                   banner. checks/file_checks.py check 1 would fire on it, and every
                   C1 boot prompt says a file by that name is a finding, not a
                   source.

# Citizen Compass — Current State

> **THIS FILE WAS THE SOURCE UNTIL 2026-09-12. IT IS NOT NOW — see the banner above.**
> **`BOOT.md` is the one current page. There is still only one, and this is not it.**
>
> `claude/CURRENT-STATE.md` in the claude.ai project is a MIRROR of this file,
> regenerated from it. **Never edit the mirror.** An edit there is lost on the
> next mirror and, worse, is believed in the meantime.
>
> The root `CURRENT-STATE.md` is gone — it was a 2026-08-02 note about which URL
> is which, wearing a name that claimed to be project state, and on 2026-09-07 it
> cost a nineteen-finding audit produced from the wrong file. It now lives at
> `docs/NOTE_which-url-is-which-2026-08-02.md`, which is what it always was.
>
> **One document, one writer (C1), one direction.** Sleven, 2026-09-08:
> *"when it makes sense to everything be put in the same place and all the newest
> information read from the same place"* — it does, and it is.


**Authoritative as of 2026-09-08.** Everything in this file is true now.
Nothing in it is history, and there is no "later section wins" rule any more,
because there are no later sections — **the whole document is the current
state.**

**The 13,571-word version that used to live here is
`docs/STATE-ARCHIVE-through-2026-08-27.md`, verbatim and complete.** Read it only
to answer *why was it done that way*. Never to find out what is true. Where it
disagrees with this file, it loses.

**Rule for keeping this document worth reading: it does not grow by appending.**
A fact that stops being true is edited or deleted here, and the reasoning goes in
a dated `docs/FINDING_*` or `docs/DECISION_*`. This file is a snapshot, not a
log.

---

## The project

### THE NAME IS APPROVED BY CIG AND IS NOT A QUESTION — recorded 2026-09-09

**"Citizen Compass" has already been approved by CIG.** Sleven's words, recorded so
nobody rediscovers it: *"It is settled and it was settled before tonight."*

**It came up because he was looking at buying `citizencompass.com`.** A domain under
that name carries no naming risk.

**Why it earns a line here rather than living in the mail:** the name is
load-bearing in more places than anyone would check before asking — the repository,
the credit line on every page, and **the takedown contact address created
specifically for the Fan Kit**. A session that talks itself into a rename is
proposing to change all of that.

**Rights, Fan Kit and trademark are his alone and they are CLOSED.** This line does
not reopen them; it writes down an answer that already existed.

**The domain itself is not bought and nobody acts on it.** His purchase, his
account, not urgent. One domain covers the live and testing sites, because
subdomains cost nothing once it is owned.


Free, non-commercial fan-made Star Citizen reference.
*"Know where to buy, before you fly."* CC BY-NC 4.0, credit "Built by Sleven".
Operates under CIG's Fan Kit Agreement — **non-commercial only**, no ads,
donations or paid access while Fan Kit assets are in use.

    live      citizencompass.netlify.app        hand-deployed on Netlify
    testing   citizencompasstesting.citizencompass-contact.workers.dev
              Cloudflare Workers, one command, PASSWORD-GATED
    repo      github.com/Smeezee/citizen-compass
    local     C:\Users\david\citizen-compass

**THE TAKEDOWN CONTACT IS `citizencompass.contact@gmail.com`.** It is set as
`CC_TAKEDOWN_CONTACT` in `.env` and it is the address printed on every page that
shows CIG content. **It was never written down anywhere in this repository until
2026-09-04** - Sleven created it for exactly this purpose and a session had to ask
him for it, which is the failure this line exists to stop happening twice. It is not
a secret; it is published on the site by design.

**`LIVE.md` at the repo root is the only authority on what is actually public.**
Nothing enters it on the strength of a build, a passing check, or a deploy to
testing — only what a stranger with no password can load, verified by loading it.
As of 2026-08-27 the public site is **v0.3.9, 254 ships, stamped
"Compiled/updated: 2026-07-30"**. The testing site is far ahead of it.

**Going live is OFF the queue** until Sleven raises it himself. He has said
plainly the site is not ready. Do not push it, do not build a case for it, do not
put it back on a list.

---

## What time is it where Sleven is

**Run `python tools/sleven_clock.py` before stating any time to him.** It prints
his local time, UTC, and the offset.

**A Cowork session cannot read his Windows clock** — the shell it reaches is a
Linux VM running in UTC. Sessions have quoted UTC at a man looking at a wall
clock, more than one C1 has done it, and on 2026-09-06 he said what it costs:
*"you say one time, and it's a different time... it messes with my head."*

**The offset is measured, not stored.** The inbox watcher names every archived
handoff from the Windows clock while the filesystem records the mtime in UTC;
the gap between them is the live offset. It re-derives every run, so it follows
him between Arizona and Minnesota and through daylight saving with nobody
remembering to update a number. A stored offset would have been wrong the week
he drives to the beet harvest.

**It refuses rather than guessing.** No handoff to measure against, or the last
five disagreeing, and it exits and says so. Ask him the time; do not estimate one.

**And do not give him durations.** "About thirty minutes" is a number nobody
measured, and he plans his day around it. Say what a thing is waiting on, then
tell him when it is actually done.

## Stack and where things are

PostgreSQL + FastAPI + JS, scaled for 50k–100k+ entries. Background automation
migrating to Go for single-binary, headless, bitness-independent reliability.

    testing/_src/          page sources; the build reads these
    testing/_deploy/       the built payload the deploy script uploads
    data-layer/derived/    generated data, each folder with a MANIFEST.json
    data-layer/external-sources/scunpacked-data/snapshots/
    checks/                verification scripts
    inbox/                 anything Code must act on goes HERE, not the project
    docs/                  findings, decisions, orders, handoff archive

**The build is machine-bound and this is proven, not assumed.** It reads
PostgreSQL through `build_find_data.py -> app/database.py`, and PostgreSQL lives
on Sleven's Windows machine. A Cowork session cannot build, and a Cowork session
that tries gets `ModuleNotFoundError: No module named 'sqlalchemy'`.

    python testing/_src/build_deploy.py
    powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1

`scripts/deploy_live.ps1` with `wrangler.live.toml` is a separate script for a
separate worker. **Neither touches Netlify**, which is where the live site is
today.

---

## Session roles

- **Sleven** — gathers data, runs commands, owns every legal, Fan Kit and
  trademark decision. Those are his alone.
- **C1** — Cowork. Writes orders into `inbox/`, owns `NEXT.md`, `LIVE.md`,
  `OWNERS.md`, `docs/UX_DOCTRINE.md` and this file, owns the loadout page source
  and the hardpoint pipeline. **The only Cowork session that writes repository
  ARTIFACTS** — C5 writes memos into `inbox/` and nothing else.
- **C5** — Cowork audit, named by Sleven 2026-09-08 (proposed as C2; renamed
  because "C2" already means the C2 Hercules in this project). Read-only review: doctrine
  audits, project audits, findings, and review of another session's material
  before it reaches the acting project head. **Writes nothing in the repository
  except memos dropped in `inbox/`**; its audits go to the claude.ai project.
  Verifies claims against the repository rather than against prior documents.
  Holds no artifact and owns no path.
- **C3 / Design — ONE SEAT, ONE ROW.** Merged 2026-09-12 after Design found the
  same seat carrying two rows with different lanes. Cowork design and research.
  Reads and verifies source data, proposes shapes and rankings, produces findings
  and work orders. Has a tray as of 2026-09-08. Charter:
  `claude/CHARTER-C3-design-and-imagination.md`, which binds the codename to the
  design function — two rows for one charter was the defect.
  **What it may write is `OWNERS.md`, not this line.** Not git, not the database,
  not Code's build tooling.
  **The old "Design" row said "holds no artifact" and that contradicted
  `OWNERS.md` on the day it was written** — that file names
  `five-main-pages.html`, `slipway.html` and `deck-sifter-yard.html` as C3's.
  Both rows read fine alone; only reading them against `OWNERS.md` finds it.
  **THE 2026-09-08 SELF-STOP IS SPENT AND WAS LIFTED 2026-09-12.** The condition
  was *nothing further until something is measured*; six things were measured
  between 09-08 and 09-10 and three of them contradicted this desk's own design.
  **The conduct was never out of order** — measuring does not violate a stop on
  unmeasured output. The stale thing was this sentence. Recorded rather than
  deleted, because a stop that vanishes reads as a stop that was ignored.
- **CIC** — Claude in Chrome. Reads the open web. **Its output is a claim until
  someone verifies it locally.**
- **Code** — Claude Code, on the Windows machine. Executes. Owns
  `testing/_src/build_deploy.py` and the check suite.
- **THE ADJUTANT** — established by Sleven 2026-09-08, seat above C1, and it works
  across every project rather than this one. It speaks for him and hears for him:
  it turns what he said by voice into something a desk can execute, and sends it
  **in his name**. **To every desk except C5, this desk does not exist** — orders
  arrive from Sleven and replies go back to Sleven. **Its tray is the owner tray,
  `correspondence/open/owner/`.** No new tray was built and none is needed.
  Charter: `CCDesk-logs/ADJUTANT.md`.

**Six desks have mailing paths: architecture, build, research, audit, design,
owner.** A new desk gets one when it is created, not when somebody asks whether it
wants one — Sleven's ruling, 2026-09-08. A desk that cannot be written to is half a
desk.

**The desk logs moved 2026-09-08 and are now PROJECT-first:**
`CCDesk-logs/<project>/<year>/<month>/<date>/<desk>.md`. It used to be day-first,
which is how pages get written but not how anybody reads them, and it left a desk
working two projects in one day nowhere to put the second.

**A work order that exists in the claude.ai project but not in the repo has not
been delivered.** Code reads the repo. Anything Code must act on goes in
`inbox/`. **C3 reads the project**, so an order for C3 goes in both.

**Four ownership gaps have now been found the same way** - going to change a
file and finding nobody's name on it. `build_loadout_data.py`,
`holo-hardpoints/`, and on 2026-08-30 the page-copy set: `_layer.src.html`,
`keybinds.src.html`, `device_engine.js`, `kb_overlay.inc.html`. All claimed by
C1, all claimed rather than seized, all notified in `OWNERS.md`. **The rate says
the gap is systemic, not bad luck.**

**`OWNERS.md` is the machine-readable list of who writes what**, and it replaced
a prose list that lived in two documents and drifted. `checks/_verify_owners.py`
holds it to its own rule and fails if `NEXT.md` grows a second copy. Rule 14 is
one writer per artifact, and the ownership list is an artifact.

**C1 can run 32 of the 33 harness-based page controls** — measured 2026-08-28,
not inferred. Node is in the Cowork VM; what is absent is Playwright, the served
site, PostgreSQL and PowerShell. A control C1 files unrun must now name which of
those four it needs. See
`docs/FINDING_c1-can-run-the-page-controls-2026-08-28.md`.

---

## The hard rules

**THE RULES LIVE IN `CLAUDE.md`. THERE IS NO LIST HERE ANY MORE.**

This file used to carry its own numbered eleven. `CLAUDE.md` carried a
different fifteen. **Both had a rule 8** — here it was "read the clock", there
it was the Fan Kit rule — so two sessions could quote their own file correctly
and flatly contradict each other. That happened, to Sleven, on 2026-09-02.

**Everything that was here is now in `CLAUDE.md` as rules 16 to 23**, and rules
1 to 15 there were left untouched so the hundred check files citing rule 12,
rule 14 and rule 16 by number still mean what they say.

**If you are about to add a rule to this file: don't.** Add it to `CLAUDE.md`.

Where the old numbers went, so an old citation can still be read:

    old 1  commits and pushes need a go-ahead, never git add -A   -> rule 2
    old 2  NO FUZZY MATCHING                                      -> rule 17
    old 3  every check needs a control that could fail            -> rule 12
    old 4  one writer per artifact                                -> rule 14
    old 5  truth from a different source, or UNPROVEN             -> rule 16
    old 6  every row carries last_verified_patch                  -> rule 20
    old 7  ambiguity is refused, not resolved by picking          -> rule 19
    old 8  read the clock, never estimate                         -> rule 18
    old 9  rights and credentials are CLOSED                      -> rule 23
    old 10 a frame may contain a name, nothing derived from it    -> rule 21
    old 11 do not fetch /media/ on robertsspaceindustries.com     -> rule 22


---

## What is built and working

**THE NEW FRONT PAGE, 2026-09-06.** Sleven rejected five designs from the previous
C1 and two more from this one before approving this shape: cards, grouped by
manufacturer A–Z with ships A–Z inside each, every card the same height, and
**every fact on the face of the card** — his words, *"it's not simple to get the
information"*, is what killed the version before it. Source generated to
`testing/_src/next.src.html`; it publishes as `next.html` BESIDE the current
`index.html`, on his ruling: put it up beside, then rewire it properly.
Order at `docs/ORDER_put-the-new-front-page-up-beside-the-old-one-2026-09-06.md`.

**RSI price sweep, 2026-09-06, CIC.** The store's default view is filtered to
what is on sale — 70 ships. Unfiltered is 183. **The two sets are disjoint, 253
total**, so anyone sweeping the page they land on collects a third of the store
and never learns the rest exists. On-sale tiles print the list price, not a
discount: 37 of 38 comparable rows matched our pre-sale figures.

Joined by exact name: 225 matched, **145 prices agreed, 9 had drifted, 70 we
simply did not hold.** Applied through `price_corrections.json` with the source
and read date per row. **The front page went from 167 priced cards to 237.**
Pass 2 added no prices — 173 of 173 matrix prices were character-identical to
Pass 1 — but it added **parentage across 56 families**, which existed nowhere in
this project before that day.

CIC withdrew its own earlier stop memo: the matrix tab is lazily mounted and a
wide viewport is not enough, the page has to be scrolled before the control
exists. It filed that as a defect and named the pattern — three times in a week
it recorded an absence measured with an instrument it had not finished
operating. **The mirror of rule 12 is not in the rule book: before recording an
absence, prove the instrument can show a presence. Raised to Sleven, not
enacted.**


**The ship page** — `testing/_deploy/loadout.html`. The bench and the 3D model
as tabbed layers. There is no `ship.html` and there will not be one. The page has
no opinion: no build modes, no presets. Every part the game allows at a port is
offered and the visitor decides. The component catalogue is **derived, not
written** — 27 types, discovered by scanning ports, so a port CIG opens in a
future patch appears with no code change. Editability is **per port, per ship**,
never per type.

**Hardpoints on CIG's own coordinates.** Decoded out of `Data.p4k` — the `#ivo`
container, chunk `0x70697FDA`, 208-byte records, transforms in metres — and
joined to the page's ports by CIG's own `HardpointName`, exact string equality.

    transforms   153 hulls decoded
    placement    284 converted, 277 passed, 7 refused
    overlay      166 hulls / 1,693 ports, plus 41 whole records for hulls the
                 marker dataset has none for
    ship page    2,026 mounts on CIG coordinates, 113 name-derived
                 244 classes with every top-level mount on CIG coordinates
                 21 mixed (88 derived mounts between them)
                 6 with none

**Counted from `testing/_deploy/loadout_marker.gen.js` — the file the browser
loads — not from a manifest.** The previous numbers here (245 / 20) were carried
forward from the pipeline's manifests and were wrong at the last step: 335
CIG-published mounts reached the page labelled as estimates, and the "20" counted
hulls the hardpoint rule could not reach, several of which have no model on the
page at all. Fixed and controlled 2026-08-28 —
`docs/FINDING_the-page-called-335-cig-mounts-estimates-2026-08-28.md`.

**Every dot carries its own provenance** (`cig`, `est` or `anc`, Q9) and
`checks/_verify_marker_provenance.py` holds it to that in both directions: no
mount on a CIG coordinate may be called an estimate, and no mount called CIG may
sit anywhere else.

The 6 at that build were `VNCL_Glaive`, `VNCL_Scythe`, `GRIN_MTC`,
`MISC_Starfarer_Gemini`, `TMBL_Cyclone_MT` and `TMBL_Cyclone_TR`.

**These counts move on the next build, and here is which way.** The frame proof
changed on 2026-08-28: **the Glaive is placed** (it was never asymmetric — the
mirror was discarding the mounts that prove its frame), and **both Drake
Clippers are refused**, because a hull whose named pairs mostly do not mirror is
now refused outright rather than only when something falls outside its box.
Containment cannot see a transposed axis on a hull as tall as it is wide.

Separately, hulls the hardpoint rule cannot reach at all — which is not the same
list, because several have no model on the ship page and so no markers to miss:
the ARGO ATLS family (a **power suit**, filed under `Characters\PowerSuit`),
four GRIN mining vehicles (no exterior mount at all), the Javelin (two paths of
equal evidence, one under `dmg`), and the MOTH. See
`docs/FINDING_the-hull-rule-was-blind-to-the-ships-cig-does-not-name-a-folder-for-2026-08-27.md`.

**THERE ARE TWO PLACEMENT WRITERS AND THE CONTAINMENT GATE ONLY SEES ONE.**
`hardpoints_fleet.json` is written by `place_fleet.py` — the script four
documents and two build scripts said was **not in this repository**. It is at
`data-layer/derived/holo-hardpoints/place_fleet.py`, 32,861 bytes, dated 23
August, and it runs. Nothing was ever lost; nobody ran `ls`.
`docs/ERRATUM_place-fleet-py-was-in-the-repo-all-along-2026-08-29.md`.

Its `resolve_frame()` already solves the orientation problem by matching the
hull's **proportions** against CIG's published dimensions rather than assuming
an axis, and refuses above a calibrated error. It agrees with the pipeline on
every hull that works and disagrees on every hull that was heaped.

    1,878 mounts in hardpoints_fleet.json
       43 outside the unit box
       33 of those aimed at a MEASURED extremity, all by 2.7-3.4%

**Those 33 are not the Defender's defect and must not be treated as one.**
`place_fleet.py` aims an extremity mount at the hull's own outermost vertex and
normalises by the longest half-extent, so a nose gun lands at 1.0 by
construction and the few percent over is a normalisation artifact of a real
vertex. The Defender's 1.32 was a fixed-fraction guess aimed at nothing.
**A gate at exactly 1.0 would refuse points sitting on the hull's own skin.**
`MARGIN = 0.06` separates them correctly — checked against the data. **Do not
tighten it.**

**How a variant finds its hull:** CIG's own record says so —
`Parts[0].Name` is the hull the ship is built on. `ANVL_C8_Pisces -> ANVL_Pisces`.
Exact equality. **This replaced a name-prefix rule; do not reintroduce one.**

**TEN SHIPS WERE DRAWING EVERY DOT IN A HEAP, LABELLED AS CIG'S OWN
COORDINATES — found 2026-08-28 by photographing all 295 ships, and fixed.** The
scale rule matches CIG's Length to the model's Z extent, and 19 of 258 models
measure taller than they are long, so the scale came off the wrong axis. The
Tiburon drew all 17 of its dots in one clump. **Four green controls let it
through** — containment (a heap is inside the box), the mirror (a heap is
symmetric), provenance (the labels were honest about the source) and the census
(nothing was lost). Every control asked whether a marker was CORRECT; none asked
whether the set was PLAUSIBLE.

**Placement now refuses a model whose orientation it cannot establish**, losing
those hulls' CIG dots rather than keeping wrong ones — including four whose dots
looked convincing, because their scale came off the same wrong axis and looking
right is not proof. `checks/_verify_marker_spread.py` holds it, reading the
hull's real size out of the mesh file.
`docs/FINDING_the-dots-were-in-a-heap-2026-08-28.md`.

**Every dot has been tested against a clean silhouette of its own ship.** Each
hull is shot twice — once with markers, once with them hidden — and every
marker's screen position measured against the ship's outline. **1,912 of 2,193
dots land exactly on the hull; p90 is 1px.** Ten did not, on four hulls.

**Seven of the ten are now accounted for.** The acceptance test only ever
measured two of three axes; its comment argued that testing the fore/aft axis
would be marking our own homework because that is where the scale came from.
**That reasoning was wrong** — the scale comes from the model's box against
CIG's published Length, not from any mount position. 26,273 mounts measured, 93
outside fore/aft, 7 of them actually drawn:

    BANU_Defender 50/51   1.32494 "cig"  ->  REMOVED
    MISC_Hull_C   34     -1.27827 "cig"  ->  -1.00356 "est"
    ORIG_m80      4 mounts, already refused for orientation

**The Hull C outcome is the one to understand.** Its nose turret was not
deleted — the CIG position was withheld, the mount fell back to a name-derived
estimate, and the page now labels it `est`. A dot 1.28 half-extents off the nose
had been presented as CIG's own placement.

**Three remain: the Drake Corsair (3 of 15), the Tumbril Storm AA and the
Glaive.** Those sit INSIDE the box and still miss the mesh, which means the box
is not the hull. **Do not widen the acceptance test to make them pass.**
`docs/FINDING_four-hulls-draw-a-dot-in-empty-space-2026-08-29.md` and
`docs/FINDING_two-placement-writers-and-the-port-i-named-wrong-2026-08-29.md`.

**Every ship has been photographed with its dots on.** 295 hulls loaded in a
real browser, 2,309 markers drawn, 0 failures — 26 ships show no dots and 25
carry at least one estimated dot. That is the last unmeasured thing about the
hardpoint work: the coordinates were proven, and now the RENDERING is too.
**Ships with no hardpoints are deferred by Sleven until the rest is finished.**

**The suite is 106 controls and one is red on purpose.** Code's 2026-08-29
sweep — the first in this repo that could not be perturbed by its own drift
control, because `_verify_deploy_drift.py` no longer rebuilds the artifacts the
other controls read — returned **104 ok, 2 failed, 0 skipped, 0 NOT RUN**. One
of the two, `_verify_marker_census.py`, is now green: the Banu Defender's
`10 -> 8` is declared with its reason. The other, `_verify_child_markers.py`,
is **correctly refusing three intended changes** and is the only thing gating a
deploy. See `NEXT.md` Q27.

**THE SWEEP CANNOT SAY "I COULD NOT LOOK".** `run_all_controls.py` classifies
`code == 0` as pass and everything else as FAIL; NOT RUN is reachable only when
it cannot launch the process at all. Two controls already exit **2** to mean
NOT PERFORMED — `_verify_community_mark.py` and `_verify_panel_dismiss.mjs` —
and both print as FAIL. Run from a machine without PostgreSQL, Chromium or
PowerShell, 20+ controls report FAIL when nothing is wrong.
`docs/FINDING_the-sweep-cannot-say-i-could-not-look-2026-08-29.md`, queued as
Q29. **Fail-closed is not affected — `failed` and `not_run` both refuse the
deploy.** Only the printed sentence is wrong.

**The bench works as a loop, and it is now proven as one.** Pick a mount, fit a
part, see what moved, keep or undo — every step driven by a click through the
page's own handler in `checks/_verify_swap_loop.mjs`, 27 assertions. **Undo is a
step, not a reset:** after two swaps one undo returns the first part. The
existing coverage set the build directly and stepped over the whole interaction.

**A swap moves at least one readout figure on 773 of 813 ports** (25 ships,
measured 2026-08-28). Guns, missiles, turrets, coolers, shields, power plants,
radars and quantum drives all respond. **An earlier claim here that no swap
moves anything was wrong** — twice over: a search capped at the first eight
ports per ship, which are never guns, and a boolean compared to a string.

**Three part types genuinely show nothing** — flight blades, salvage heads and
most bomb racks — because CIG publishes no figure on which their options differ.
All three Avenger flight blades are identical on every field.

**The page now says so** (Sleven's call, 2026-08-28): where every option on a
port is identical on every published figure, the picker states it and tells the
reader to pick on looks or price. **A mount carrying child ports is excluded** —
a missile rack's real difference is one level down, so claiming its options are
identical would be true of our data and false on screen.
`checks/_verify_identical_options.mjs` holds it both ways: the line must appear
where the options match and must NOT appear where they do not.

**THE MODEL GAP IS FIVE, NOT TWENTY-FOUR, AND HAS BEEN SINCE 27 AUGUST.**
Re-measured 2026-09-04 with `scripts/enumerate_ship_gaps.py`: **254 site rows, 249
can show a model, 5 cannot.** All 19 ships the August reports called fillable were
imported that same afternoon and are on disk, built, deployed and mapped in
CC_MODELS. `ship_gaps_report.txt` and `model_availability_report.txt` are both dated
2026-08-27 and were written before that import ran; a whole plan was drafted against
their stale numbers on 2026-09-04. **Regenerate or date-stamp them.**

The five with no model anywhere: **CSV-FM, RAPTOR, Starlancer BLD** (no game file, so
no ship page - they render as a plain name), **F7C-M Hornet Heartseeker Mk II** and
**Gladius Dunlevy** (ship page exists, and L14 case 1 already gives them the honest
"no model" panel).

**WE DESTROYED 56 SHIPS' UV MAPS OURSELVES AND HAVE NOW RESTORED THEM.**
`cc-compress.cjs` ran Draco with the library default `quantizeTexcoord: 12`. Draco
quantises across the min..max present, so a few junk vertices at +/-226,000 (Carrack)
or +/-5.3e7 (Polaris) collapsed every real coordinate into one bucket. The
Constellation Andromeda shipped with **95 distinct UV pairs across 551,174
vertices**; the Carrack with **6**. The sources were fine - we broke them.

`testing/_tools/cc-uvfix-compress.cjs` (C1) clamps UVs to a percentile band,
**refuses to clamp when the band does not fit** rather than mangling a map it cannot
save, and quantises at 16 bits. Position/normal/colour/generic quantisation is
untouched, so the geometry is the same shape it was. Verified by
`testing/_tools/verify_uvfix.cjs` (RULE 16 - reads both finished files off disk, not
the compressor's own report):

    258 files, 0 errors
      restored ....... 56      unchanged ...... 17
      sharper ....... 124      worse ...........  0
      never had one .. 61      fleet UV detail 5,521,187 -> 15,687,214

Deployed to `testing/_deploy/models/`; the 258 previous files preserved in
`_to_delete/models_pre_uvfix_20260904T033923Z/`. Nothing committed or pushed.
`docs/FINDING_we-destroyed-56-uv-maps-ourselves-and-have-now-restored-them-2026-09-04.md`.

**NO MODEL IN THIS PROJECT HAS EVER HAD A TEXTURE, AND NONE EVER WILL FROM A PUBLIC
SOURCE.** 0 of 258 `.glb` contain an image; that is true of RSI's `.ctm` too. CIG's
actual paint exists in one place outside CIG: `Data.p4k`. Two ways to make a hull
read as painted anyway are built and rendered - **triplanar projection** (a generated
plating sheet projected in world space) and **procedural** (no image at all, panel
lines and wear computed in the shader). **Neither needs a UV map**, so both work on
the 61 hulls that have none. Awaiting Sleven's pick.
`docs/DESIGN_two-ways-to-paint-a-hull-with-no-texture-2026-09-04.md`.

**ONLY TWO MODELS IN THE FLEET CAN TAKE CIG'S PAINT, NOT NINETEEN.** Measured
2026-09-04 across all 256 deployed `.glb` by reading each one's material list:

    single material, cannot be part-painted ..... 239
    hull + glass only ............................ 15
    CIG's real material split ..................... 2   85X, Fury

The Cutlass Black is **1 mesh, 1 node, 1 material named `Default`**, against 58
sub-materials in CIG's own `DRAK_Cutlass_Black_Exterior.mtl`. There is nowhere to put
57 of them. This is not a shader problem - the parts do not exist in the file. C1's
earlier "~19 multi-part models" was a guess stated as a count and is withdrawn.
CIG's colours DO join by exact material name where the names survive: 232 matched on
the 85X.
`docs/FINDING_i-said-nineteen-ships-could-take-cigs-paint-it-is-two-2026-09-04.md`.

**THE FLATTENING IS NOT OURS AND THERE IS NO BETTER THIRD-PARTY SOURCE.** Read from
the untouched Fleetyards downloads in `sc-ships/_stage_fleetyards_20260827T170401Z/`,
before compression, scale fix or UV fix: they arrived flat. All 17 multi-material
ships came from that one 2026-08-27 batch; the 2026-07-31 Hugging Face pack is 100%
single-material blobs. The 85X and the Fury are two lucky files, not a source.

**THE PER-PART MODELS ARE IN THE GAME INSTALL, AND WE ALREADY DECODE HALF THE
FORMAT.** `DRAK_Cutlass_Black.cga` (10.6 MB) and `.cgam` (11.4 MB) pulled from
`Data.p4k`; the `.cga` declares **209 nodes** against our 1. `decode_cga_nodes.py` ran
on it unmodified, first try: 160 hardpoints, 160/160 finite transforms, extents 21.17 m
beam and 33.66 m length against CIG's published 21.5 and 34. **The container, the name
table `0xC201973C` and the node array `0x70697FDA` are already decoded in this repo.**
The gap is one chunk - `0x58de1772`, 10.4 MB, the mesh: vertices, indices, and the
per-subset material ID. Two maintained open-source projects already convert it to
glTF/GLB with materials - **Cryengine-Converter** v2.0.0 (2026-03-07, GPL-2.0) and
**StarBreaker** v0.3.2 (2026-05-19). **Not run, not downloaded, not authorised.** This
would also fix the see-through hulls, the 85X/Fury duplication, the Constellation
landing gear, the outdated Freelancer airframe and the 113 name-derived hardpoint
markers, because all of them come from shipping somebody else's flattened export.
**The Fan Kit question on converting client assets is Sleven's alone and is not
C1's to argue.**
`docs/FINDING_the-ships-with-parts-are-on-his-own-drive-2026-09-05.md`.

**CIG'S MATERIAL FILE IS NOT THE PAINT ON MOST HULLS.** Surveyed 2026-09-05:
1,363 ship `.mtl` entries indexed from `Data.p4k`; **72** resolved to a hull's base or
exterior material file by exact rule (basename equals a contiguous run of its own folder
path, or that plus `_Exterior`; a livery is a repaint and not a candidate; the other
1,291 are skipped and counted, never guessed).

    DIFFUSE IS THE PAINT      names all agree ....... 14
    DIFFUSE IS NOT THE PAINT  names disagree ........ 29
    no colour-stating names, cannot tell ........... 29
    could not read ................................. 11

**The control is that a material whose NAME states a colour must compute to that
colour**, and it fails loudly: `painted_metal_white` on the Cutlass Black computes to
`#3D2F17`, a dark brown, and `painted_metal_grey` and `painted_metal_dgrey` are
byte-identical. The failure mode is overwhelmingly `Diffuse="1,1,1"` - a white
multiplier with the real colour in a texture we do not have.

**CIG stores LINEAR and the sRGB conversion is pinned, not chosen:** 85X `Grey` 0.6939
linear converts to `#D9D5D4`, the value already rendered and accepted for that ship;
read as sRGB it would be `#B1B1B1`.

**Thirteen of the fourteen passes rest on 1-3 material names each** - the Hornet F7C-R
has 59 materials and one states a colour. Only the 85X has actually been rendered and
looked at. Treat the 14 as *not yet disproven*, not as proven.

**This is the load-bearing qualifier on the conversion plan.** A geometry-only
conversion gives a correctly-divided ship in the WRONG COLOURS, which is worse than a
flat blob because it looks deliberate. **The conversion must bring textures, not just
meshes**, and that must be checked on one converted hull before anything scales.
**The idea of picking a single dominant hull colour per ship out of the `.mtl` is
retired** - on most hulls there is no such value in the file, and on a single-material
ship there is no principled way to choose one of 58 (rule 19).
`docs/FINDING_cigs-material-file-is-not-the-paint-on-most-hulls-2026-09-05.md`.

**THE `#ivo` MESH FORMAT IS DECODED, AND IT NOW WORKS ON SIX SHIPS.** On
Sleven's go-ahead 2026-09-05, CIG's `.cgam` files are read out of `Data.p4k` from
the bytes up, with no third-party tool, and built into glTF with CIG's own
material split:

                      subsets   vertices   triangles   median edge
    Cutlass Black         176    326,737     273,157      0.084 m
    Vulture               624  1,257,859   1,204,583      0.029 m
    Gladius               457    334,609     339,426      0.053 m
    Prospector            419    371,900     402,646      0.045 m
    Arrow                 180    146,658     138,088      0.034 m
    300i                  220    145,955     128,003      0.038 m

All 30 bytes/vertex, positions on the 16-byte stream, at most one triangle
dropped. Four rendered and recognisably the right ship. Against the site's
current **1 mesh, 1 material "Default"** per hull. **The Prospector - the worst
see-through hull in the fleet - comes out solid from the client.**

    header     chunk 0xB8757777: streamCount, vertexCount, indexCount,
               subsetCount, then two bounding boxes at +24
    subsets    48-byte records from +168: u16 node, u16 materialId, u32
               indexOffset, indexCount, vertexOffset, group, vertexCount
    indices    16-bit; absolute vertex = subset `group` + value
    streams    [u32 typeHash][u32 elementSize], chained from the index buffer's
               end; sizes sum to 30 bytes/vertex
    positions  the 16-byte stream, 3 x s16 over the first bounding box

**THE BUG THAT MATTERED, AND ITS LESSON.** The first decoder read the header as
12 bytes, `[0][hash][elementSize]`. The leading zero was padding that happened to
sit there on the Cutlass Black; on the Vulture the preceding word is the tail of
the index buffer, so the chain was not found, the wrong region was read as
positions, and the output was a blob **while every declared total agreed
exactly**. The decoder now carries no ship-specific constant, and **the position
stream is chosen by GEOMETRY - smallest median triangle edge through the index
buffer, refused above 0.5 m - because that is the only gate the file cannot pass
by being internally consistent.** Containment in the bounding box cannot do it:
any 16-bit stream passes that once scaled.

**NOT DONE.** Materials are only partly named - every hull past the Cutlass draws
on more than one `.mtl` (Gladius 104 materials, 33 named; Vulture 173, 64 named);
the rest fall back to grey and are reported, not guessed. Three of nine ships
tried could not be located by name at all (Aurora MR, Constellation Andromeda,
Freelancer) - lookup problems, not decode problems. Normals, UVs, tangents and
vertex colours are still undecoded, three of the four streams. Colour is still in
textures we do not have, so every hull is grey. **No check exists that would
catch a bad model without a human looking at it, so this does not yet run over
256.** Nothing deployed, committed, or shown to a visitor.
`tools/ivo/ivo_mesh.py`, `tools/ivo/batch_probe.py`, outputs in `_work/ivo/`.
`docs/FINDING_the-ivo-mesh-format-is-decoded-2026-09-05.md`.

**THE FREELANCER REDESIGN IS CONFIRMED FROM THE SHIPPED CLIENT, 2026-09-05.**
Sleven's recollection was that the stairs under the Freelancer's nose are gone.
They are. CIG's own folder for it is **`Data\Objects\Spaceships\Ships\MISC\
Freelancer_v2\`** - the version is in the folder name - and the current hull's
`.cga` names every way into the ship:

    SideDoor_A / SideDoor_Ext / SideDoor_Root
    hardpoint_seat_access_sidedoor
    hardpoint_door_airlock       hardpoint_door_rear
    ladder_01 .. ladder_05

**There is no front ramp and no nose stairs node anywhere in the file.** You
board through the side door and the rear. Our four Freelancer models still show
the old nose stairs, so they are the pre-v2 airframe - which makes this the one
marked defect that is also wrong on the LIVE site, not just the inspector.
Confirmed from the game client, not from a fan source; CIC was not needed.

**Replacements can be built:** `MISC_Freelancer`, `_DUR`, `_MAX`, `_MIS` all sit
in `Freelancer_v2\` and the base hull already converts (180 subsets, 135,960
vertices, 141,548 triangles). Its `.mtl` is one of the entries that fails
extraction with "no local header" - a ZIP64 offset case that also blocked 11
hulls in the material survey and is worth fixing once.

**SLEVEN'S RULING 2026-09-05 - DEPRIORITISED, DO NOT RAISE AGAIN:** the landing
gear sitting deployed on the five Constellations, and the Constellation lift
sticking out. His words: *"that's just the way the models are... not a game
changer... just a pet peeve."* Fix only if it falls out of other work. **The
three framing marks (ATLS, ATLS GEO, Reliant Kore) he confirmed do need doing** -
*"they're just a little too close, back up a little bit."*

**NINE HULLS ON THE TEST SITE ARE NOW BUILT FROM THE GAME CLIENT** (2026-09-05,
on Sleven's go-ahead). `X1`, `X1_Force`, `X1_Velocity`, `Freelancer`,
`Freelancer_DUR/MAX/MIS`, `85X`. Converted with `tools/ivo/ivo_mesh.py`, Draco'd
with the existing `cc-uvfix-compress.cjs`, installed into
`testing/_deploy/models/`. Originals in
`_to_delete/models_pre_client_swap_20260905T053243/`. All 256 re-checked after
every swap: every one a valid GLB. **Not yet swept or deployed.**

**NO RESCALING IS NEEDED AND THAT IS MEASURED.** The Cutlass Black from the
client comes out 26.146 x 10.035 x 35.722 against the deployed model's
26.146 x 10.236 x 35.717 - same space, same axis order, metres for metres. Four
of the six first swaps matched their old extents to within 0.5%.

**THE TWO THAT DID NOT MATCH ARE THE TWO THAT WERE WRONG:**

    Freelancer   old 24.89 x 8.10 x 32.17   new 22.58 x 7.81 x 36.71
    85X          old 10.10 x 5.28 x 13.09   new 10.10 x 2.66 x 13.09

The base Freelancer was 4.5 m too short - and DUR/MAX/MIS already matched v2, so
only the base was still the old airframe, which is exactly the one Sleven
noticed. The 85X was **exactly twice** its correct height: the duplicate copy, in
a number. Both confirmed by render - one 85X, and a Freelancer with no nose
stairs.

**AND THE X1s WERE ALL THE WRONG BODY.** Old `X1` and `X1_Force` were the SAME
FILE, both 1.24 m wide - which is the width WITH the Velocity's fins. The site
showed the finned Velocity body for all three. Now: X1 and Force are the bare
hull (1.05 m), Velocity is hull + fins + nose cone + thruster, composed by
`tools/ivo/merge_glb.py`. **No transforms applied, and measured not assumed** -
the fins convert to x +/-0.53..0.62 against a hull spanning +/-0.53. The merger
REFUSES a part whose box falls outside the hull's.

**TWO TOOL BUGS FOUND AND FIXED.** `cc-uvfix-compress.cjs` wrote its temp file as
`dst + '.part'`, and gltf-transform picks output FORMAT from the extension - so
it emitted glTF JSON plus an orphan `.bin` and renamed the JSON to `.glb`. Six
hulls came out at 32 KB for 164,000 triangles, which is the only reason anyone
looked. **The 256 shipped models were checked and none were damaged.** Temp name
now keeps `.glb`. Separately, the ~40% triangle drop in compression is CORRECT:
the X1's source carries 151,544 degenerate triangles of 333,088, and the
compressor kept exactly the 181,544 non-degenerate ones.

**THE GROUND VEHICLES ARE REFUSED, WITH THE MEASUREMENT.** CIG's record names
every Cyclone variant's hull as `TMBL_Cyclone` and the TR's module as
`TMBL_Cyclone_Module_Turret` - **and no file of that name exists in the
archive**. Every module was converted and added to the base; nothing matches what
is deployed (closest 0.40 m out, worst 1.11 m), and the bare hull is NARROWER
(3.07) than every deployed variant (3.20-3.76), so those carry wheels too. The
wheels are separate files and are NOT reliably in ship space - the front pair
converts across the centreline - so they need their `wheelFL/FR/BL/BR` node
transforms, which are in the hull's `.cga` and are not yet applied. **Swapping
the bare hull in would delete the TR's turret and its wheels. No Cyclone is
touched.** **THE CENTURION IS THE RIGHT SHIP AND ITS MARK IS CLEARED.** CIG's record: `Role: Anti-Air`, *"built on Anvil's popular Atlas Platform... short-range anti-aircraft operations"*, with an `ANVL_Centurion_Remote_Top_Turret` and eight named wheel hardpoints. The deployed model is a wheeled Atlas hull with a radar dish and a multi-barrel top turret - it matches. **It looked wrong because the Centurion and the Ballista share the chassis**: 6.75 x 5.25 x 16.65 against 6.74 x 5.36 x 16.72, within 0.11 m on every axis, differing only above the deck (dish and gun against missile rails). Genuinely different files - 510,022 triangles against 325,975. The bare CIG chassis at 6.28 x 4.42 x 16.71 agrees on length to 6 cm and is smaller by exactly what wheels and a turret add. **Replace nothing.** `docs/FINDING_the-centurion-is-the-right-ship-2026-09-05.md`.71 against the deployed 6.75 x 5.25 x 16.65, but its four
wheels are separate files as well. **Both parked, not guessed at.**

**THE WHEEL PLACEMENT MOSTLY WORKS, AND MY FIRST REPORT OF IT WAS WRONG.**
Merged as-is the wheels are invisible - base plus all four gives
3.07 x 1.89 x 5.47 against a deployed 3.76 x 2.31 x 5.68, the width does not
move, and the render shows no wheels. So they are in the part's own frame, and
`tools/ivo/place_part.py` takes each vertex back to CIG's frame, applies the
hull's node 3x4 and brings it forward.

**I then called that a failure on the strength of bounding boxes measured with a
BROKEN READER, and that is withdrawn.** The reader ignored `byteStride`: it read
n*3 contiguous floats from a bufferView holding interleaved POSITION+NORMAL+UV
and got a mixture of three attributes. The deployed Cyclone came back as
**4.71 x 4.71 x 4.71 - a perfect cube**, which is what a scrambled read looks
like and should have been caught on sight. Correct is 3.76 x 2.31 x 5.68. Fixed
in the measuring tool and in the renderer, which carried the same bug.

**Read properly, the deployed Cyclone is ground truth for where wheels belong**
(rule 16 - the correct model is a different source from the part files). Four
clusters outside the hull's half-width, ~5,100 points each:

    front pair   x -1.73  z -2.02        x +1.73  z -2.02
    rear pair    x -1.73  z +2.12        x +1.73  z +2.12

`place_part.py` puts the wheel centres at x +/-1.63 z -2.08 front and
x +/-1.95 z +2.09 rear - **within 0.10 to 0.22 m of truth.** The transform is
substantially right. What is wrong is that the part files carry suspension
geometry reaching further outboard, so the assembled box comes out 4.68 wide
against 3.76. **That is a content question, not a placement failure**, and the
earlier claim that the node transform "double-counts" an offset already in the
file is not supported by these numbers.

Still parked, for a better reason than before: **it is close, it is unfinished,
and no ship on the site needs it.**

**There is no user-facing cost.** Sleven looked and said the Cyclone is fine on
both pages, and it is - the deployed ones carry their wheels and modules. What
failed was REPLACING them from the client, not the ships themselves.

`tools/ivo/`: `ivo_mesh.py`, `merge_glb.py`, `build_hull.py`, `build_batch.py`,
`find_hulls.py`. `testing/_tools/_decompress.cjs` decodes a deployed Draco model
back to plain glTF so old and new can be compared outside a browser.

**ALL FOUR SEE-THROUGH MARKS ARE CLOSED BY THE VIEWER, NOT BY THE MODELS.**
`cc_viewer.js` has `CC_SEE_THROUGH_HULLS = []`, so `ccHullSide()` returns
`DoubleSide` for **every** ship and the solid/hull/depth materials all take it.
**A face drawn from both sides cannot be seen through**, so the failure is
structurally impossible for all 256 hulls whatever the model does. Build
confirmed it from the other end on the X1: 169 materials, all double-sided, none
single-sided - *"the cause is absent, not masked."*

**Cyclone TR is therefore CLOSED with no model work** - decompressed and
rendered, it is a complete four-wheeled buggy with its turret, solid throughout.
**The Cyclone and Centurion wheel work is retired as unnecessary**; it existed
only to enable a replacement that is not needed. `tools/ivo/place_part.py` stays
because it is correct; nothing depends on it.

**The X1 rebuilds are still worth having but for a different reason than the one
that motivated them**: old `X1` and `X1_Force` were the same file and both wore
the Velocity's fins. That was real and is fixed. The see-through was not.

**C1's error, recorded:** the viewer fix went in 2026-09-04, before the fleet
walk was triaged. Every hour after that spent on see-through geometry was spent
on a solved problem, and one grep would have caught it.
`docs/FINDING_the-see-through-marks-are-closed-by-the-viewer-not-the-models-2026-09-05.md`.

**THE FURY'S DEFECT IS REAL AND MEASURED, AND MY REPLACEMENT WAS WORSE.** The
deployed model is **one ship in pieces** - the hull with large detached chunks
floating metres off it - not two copies. Box: **9.35 x 6.15 x 8.57 deployed
against 3.72 x 3.53 x 6.11 from CIG's own hull**, two and a half times too wide.
`Fury_LX` is off the same way, less badly. **C1's "301 doubled pairs" is
withdrawn for the second time**; Build's 36 was right and the real cause is
scatter.

**The rebuild from `MISC_Fury.cgam` came out NOT A FURY** - one connected object
at the right overall size with a chimney-like column off the top and spiky
fragments through the body. **Reverted.** Payload fingerprint is back to
`675bc38080d1421b3334`, the one Build swept, so its sweep still stands.

**And every number said the replacement was fine:** correct extents, one
connected object, 396,251 triangles, valid compressed GLB. **A model can pass
every check we have and still not be the ship** - the third time today after the
Vulture blob and the 32 KB file.

**THE FURY IS NOT FIXED. I FIXED IT, PUBLISHED IT, AND THEN FOUND I HAD
MEASURED IT IN A COORDINATE SPACE THAT DOES NOT EXIST. REVERTED.**

The deployed Fury carries **1,518 nodes - 957 translations, 604 rotations, 35
scales** - and each of its 406 meshes sits in its own local frame until that tree
places it. **I read the POSITION accessors straight out of the buffer and
clustered them.** A hundred local frames piled into one array looks exactly like
a ship surrounded by floating wreckage, so that is what I reported: "five
unplaced loadout assemblies", named by material, measured to the centimetre, and
20% of the ship removed on the strength of it. The renders I sent Sleven were
drawn in the same wrong space by a renderer with the same hole.

**`testing/_deploy/models/Fury.glb` is back to 9,433,280 bytes, sha256
`bd5e19c392a0cefab764`. Build's sweep still stands. The order was withdrawn:
`inbox/ORDER_withdraw-the-fury-fix-i-measured-in-the-wrong-space-2026-09-05.md`.**

**What caught it** was writing a *cheaper* version of the same test - one reading
only the glTF JSON - which had to compose the node tree to get world boxes, and
then disagreed with the number I had been quoting all day. The same error was one
step from a second published wrong thing: **the 600i measured 5,201 x 9,026 x
1,751 m** in raw space and I was ready to call it a fleet-wide defect. Its node
scale is 0.01005. It is a 52-metre ship.

**IN WORLD SPACE THE FURY HAS NO FLOATING GEOMETRY AT ALL.** It is 6.76 x 3.18 x
5.60 m and **99.6% of it is one connected body**. Its mark stays open and the
cause is unknown again.

**TWO NEW TOOLS EXIST SO THIS CANNOT RECUR.** `tools/ivo/flatten_glb.py` bakes
the node tree into the vertices; anything reading its output is in world space by
construction, and it self-checks by requiring raw and world to match on a model
whose nodes are all identity. `mesh/render.py` now **REFUSES** a file whose nodes
carry transforms rather than drawing it wrongly - it fires on the Fury, 1,094 of
1,518 nodes.

**THREE ATTEMPTS TO FIND BROKEN MODELS FROM GEOMETRY ALONE ALL FAILED, AND THE
REASON IS STRUCTURAL: A HARD-SURFACE SHIP IS LEGITIMATELY THOUSANDS OF SEPARATE
SHELLS.** Grid connectivity at 0.15 m made the Cutlass Black **2,300 pieces**,
largest holding 13%, and reported "82% of the ship is outside its own body" -
that is vertex spacing, not a defect. Triangle connectivity, which is the correct
algorithm, gave **2,108 pieces** on the same ship: right answer, useless signal.
Primitive bounding boxes fired on nothing, including the one model known to be
wrong. **There is no structural signature that separates a ship from a heap. Do
not build one.**

**WHAT DOES WORK IS AN OUTSIDE REFERENCE.**
`data-layer/derived/holo-hardpoints/matched.json` carries CIG's published
length/width/height for **186 ships**. `tools/ivo/check_dimensions.py` compares
each model's world box against it: **136 of 185 are within 20% on their two
largest axes.** It scores only the two largest **because the published height is
measured with the landing gear DOWN** - on all three axes 100 ships "fail" and
every failure is the same retracted-gear shape. The 71 shipped models with no
published dimensions at all are listed by the tool; the Fury is one of them.

**MARKERS: 178 SHIPS -> 191, HARDPOINTS 1,878 -> 2,015.** Every one of the 256
shipped models now has a `hull-geometry/` entry (239 -> 258). The 13 that gained
markers: 600i Executive Edition, 85X Limited, Aurora Mk II, Basher, Fury, Hermes,
MISC Starlite, Mantis, PTV, Pitbull, Tiburon, Tyilui, UTV.

**Purely additive, and that is the control: all 178 ships that already had
markers are byte-identical. 13 added, 0 lost, 0 changed.** `build_matched.py`'s
own check also passed - all 178 resolve to the SAME model file under its four
exact rules, no fuzzy matching anywhere.

**Why they were missing:** they had mount data and no decoded hull, because
`decode_glb_points.js` reads POSITION raw and every one of them carries node
transforms. Read that way the 600i measures **5,201 x 9,026 x 1,751 m** against a
node scale of 0.01005 on a 91.5 m ship. `tools/ivo/hull_points_world.py` writes
the placed geometry and **refuses any file still carrying node transforms**.
Checked against the Star Citizen wiki, which shares nothing with this pipeline:
600i decoded 91.5 / 52.2 / 17.6 against wiki 91.5 / 52 / 17; Odin decoded
752.0 / 222.3 / 210.7 against wiki 752 / 222 / 213.

**Two the gate now refuses and should stay refused:** the M80, whose published
11.5 x 11 x 3.5 does not match its 32.0 x 5.1 x 17.6 model and looks like another
ship's figures, and the MOTH, which has no published dimensions. Reported, not
worked around.

**RULE 25 IS IN CLAUDE.md.** Scope is a list, not a memory: an OUT OF SCOPE list
that must be checked before editing any file, plus - the half that matters - when
the assigned work stalls, file the stall and STOP rather than substituting easier
work. Written because the `#ivo` decoder failed all day on 2026-09-05 and every
hour it failed C1 moved to something that produced clean numbers instead and
reported those as progress. The inspector and the contact sheets are on the list.

**THE EIGHT HULLS I DECODED OUT OF CIG'S FILES THIS MORNING HAVE THE RIGHT
VERTICES AND THE WRONG TRIANGLES. THEY ARE OUT OF THE PAYLOAD.**

Measured against the site's own Gladius, which shares no code and no bytes with
my decoder:

    the site's Gladius   416,502 tris     936.3 m2
    my Gladius           339,426 tris   4,316.7 m2      4.6x the surface

Both are the same ship to within centimetres of bounding box - 17.0 x 5.6 x 19.8
against 17.4 x 5.1 x 19.7 - which is exactly why the silhouette looked right and
every count I checked agreed. **It is a tail, not a systemic misread:** median
triangle edge 3 cm, but p99 1.41 m against the reference's 0.63 m and max 6.91 m
on a 19.8 m ship. Drop every triangle with an edge over 1 m and the area lands at
**917.8 m2 against 936.3, keeping 92.8% of the triangles.** About **7% of my
triangles span the hull instead of tiling it.**

Independently, open edges - unique edges used by exactly one triangle,
degenerates removed, welded at 2 mm: **Vulture 0.63%, Arrow 5.92%, Cutlass
7.42%** from the site's pipeline, against **my Freelancer 78.09%, my X1 65.70%,
my Gladius 67.71%.** Reverted and measured the same way: Freelancer 4.18%, X1
2.29%, 85X 10.72%.

**`85X, Freelancer x4, X1, X1_Force, X1_Velocity` are back to the sc-ships build.
Mine are kept in `_work/ivo/_mine_held_back/`. The payload fingerprint changed
again; Build has the order.** This buys back the defects Sleven marked - the
plain Freelancer is the pre-v2 airframe at 32.2 m again, X1 and X1 Force are the
same file again - and that is the right trade: **a known catalogued wrong model
beats an unverified one**, and a hull with 7% of its triangles thrown across
itself would be marked on the next walk, correctly.

**AND IT MAY UNBLOCK THE DEPLOY.** The holo placement gate was failing because
the fit was stale against these eight hulls. With them reverted their geometry is
what it was when the fit was made, so the gate may go green on its own. Build has
been asked to check that before doing any re-decode work.

**A STRIP READING IS NOT THE ANSWER AND WAS ALMOST PUBLISHED AS ONE.** Open edges
collapse from 78% to 20% if CIG's index buffer is read as a triangle strip, which
looked decisive. It is not: CIG's descriptor states an index count divisible by
three, and so does every one of the 176-plus subsets independently, which does
not happen to a strip - and the strip reading puts the Gladius at **12,564 m2**,
thirteen times the reference and three times worse than what I have. The list
reading is right. **The index BASE is wrong on about 7% of triangles** and that
is the open work.

**TWO REAL FIXES TO THE DECODER, AND IT STILL DOES NOT PRODUCE A SHIP.**

**The material id was the wrong half of the subset record.** The first u16 is the
material; I had it as the second. The proof comes from a different file: the
companion `.cga` carries chunk **0x83353333**, which nothing in this project had
opened - 128 bytes of material path, a u32 count at +128, then the ids at +164.
On the X1 the count is **44 and the 44 ids listed are exactly the distinct values
of the subset record's first u16, element for element.** Read the old way the
field gives 169 distinct values on a ship whose material file has 93 entries.
The Gladius now reports **25 materials that read as a ship** - `glass_ext`,
`primary_hardsurface`, `metal_steel`, `pom`, `decals`, `rubber_red` - against 104
unnamed ids before.

**And the model does not use the .mtl that shares its folder name.** It names its
own, in that same chunk: the X1's is `ORIG_X1_A` (93 sub-materials, against 34 in
`ORIG_X1.mtl`), the Freelancer's is `misc_freelancer_mis_ext` **under
`Freelancer_v2`**, the Cyclone's is `tmbl_cyclone_base`. New tool:
`tools/ivo/material_file.py`.

**BUT RENDERED, THE DECODED GLADIUS IS NOT A GLADIUS** - a flat shredded sheet of
overlapping planar fragments. Everything measurable checks out and it is still
not a ship: positions are **the only reading that reproduces CIG's declared box**
17.397 x 19.686 x 5.141 (unsigned, float16 and offsets +2/+4/+6/+8 each collapse
an axis to zero); `grp` beats every alternative index base whole-ship, 7.21% long
triangles and ONE index out of range against 16.87% and 32,848 for `vo`; the
subset walk still hits all three declared totals.

**AND THE 4.6x AREA WAS NEVER A CONTROL.** The site's Gladius has 416,502
triangles, CIG's file has 339,427 - different meshes of the same ship, whose
surfaces are not required to match. I spent hours treating that number as proof
of a fault. **The render is the evidence. The area is not.**

**The proxy-skip finding is withdrawn with it.** "`Proxy` is 1,696.9 m2, 35% of
the model, drawn into the hull" was computed with the material field the wrong
way round. With it right, **the Gladius uses no proxy material at all** - its 25
ids start at 3, and 0/1/2 are the proxy entries it never references. The
`Shader="NoDraw"` skip stays in the converter because it is CIG's own flag and
costs nothing, but on these ships it now skips zero subsets.

**I EMPTIED `tools/ivo/ivo_mesh.py` WITH A BAD FILE WRITE AND REBUILT IT.** The
rebuild is verified against the figures the old one printed: 457 subsets,
334,609 vertices, 1,018,281 indices, streams 16+4+8+2, positions +2,058,688
stride 16, median edge 0.0531 m - identical. It was recoverable only because
those numbers were written down. **`tools/ivo/` is not in git** - untracked, not
ignored. That is the finding under the finding.

**AND THE LEAD TO FIX IT, WHICH IS A GOOD ONE.** The excess area is not spread
evenly - it splits cleanly by the subset table's `node` field. Sorting the
Gladius's 25 nodes by how fine their triangles are and adding the areas up:

    node 30  median edge 0.021 m      2.7 m2   running     2.7
    node 29              0.043       67.3      running    71.5
    node 25              0.066      538.3      running   621.7
    node 11              0.082      308.6      running   962.3   <- reference is 936.3
    node 16              0.136     1015.1      running  1977.3
    node 21              0.303     1332.2      running  4123.6
    ... 17 more nodes, 4,316.7 m2 in total

**The eight finest nodes ARE the ship** - 962 m2 against the site's 936, using
207,178 of the 339,426 triangles. The other seventeen are 3,350 m2 of something
else sitting in the same place. **The base is not the bug:** `grp` beats every
alternative whole-ship (7.21% long triangles and one index out of range, against
16.87% and 32,848 for `vo`). What is unfinished is deciding which nodes belong
in a hull. Their names are in the companion `.cga` and, for the X1, carry no LOD,
proxy, damage or shadow marker - they read as hardpoints and body parts - so the
answer is not a name filter and is not yet known.

**MY OWN TWO NUMBERS FOR ONE THING, AGAIN.** I quoted 7.29% and 20.48% open
edges for the same geometry in the same hour, because one run divided by edge
slots (three per triangle) and the other by unique edges. There is now one
definition, in `_work/floaters/openedge.py`, and its docstring says which.

**AND A RULE I HAD TO LEARN TWICE IN ONE DAY: A RENDER IS NOT EVIDENCE OF
DETACHMENT. A DISTANCE IS.** Having just been caught by the Fury, I looked at a
grey render of the Mantis, saw its tail plates apparently floating free, and
filed "the Mantis's canopy glass is detached" to Build as the day's one real
find. False-coloured by material, **the glass is at the nose, on the hull.**
Measured - triangle connectivity over welded corners, **473 pieces**, distance
from each to the nearest vertex of everything else - **the largest twelve are
every one within 11 cm of the rest of the ship.** Nothing on the Mantis is
adrift; the plates hang on spars too thin to read at that resolution. Struck in
`inbox/ADDENDUM_the-mantis-is-fine-i-read-a-picture-again-2026-09-05.md`. The
renderer has no shadows and no perspective cue at ship scale, so from here:
measure the distance, print it, and only then look at the picture to understand
what the number means.

**The 3D viewer** — `testing/_src/cc_viewer.js`, shared by index and the ship
page. Break it and both pages fail. It recentres every hull on its own bounding
box before drawing, which is the frame everything downstream must be measured in.

**`/find` and the shop layer** — reads a generated file, not an API. **None of it
is verified against the game** (`shop_items_verified: 0`) and that is the largest
thing standing between testing and a live site.

**The collector** — builds, sends, and its selftest runs: **575 checks, 0
failed**, on Windows, 2026-08-27. The upload key in the feed is published on
purpose — a revocable channel identifier, not a secret. **Do not make the R2
bucket public. Do not add a list, read or delete route to the Worker. Do not
remove `send_url`/`send_key` from `collector-settings.txt`. Do not auto-send.
Nothing is deleted that the server has not confirmed receiving.**

**The page speaks the game's words, and a control keeps it that way.**
`checks/_verify_us_spelling.py` judges every page source against CIG's own
`labels.json` from the pinned snapshot - not against a word list somebody typed.
24 British/American pairs the game decides for American are enforced; the ones
it does not decide are named and left alone. **`grey` is deliberately NOT
enforced: ship liveries say Grey (141) and only clothing says Gray (14), so the
ship spelling wins.** It was "corrected" to `gray` on 2026-08-30 and put back.
Sleven's rule is not "write American" - it is *"the words we use need to match
the ones that the players would see in game."*

**A hover glossary, once, for every page.** `_layer.src.html` carries the table
(21 sourced terms), the CSS and the mechanism; the ship page names WHERE and
WHICH terms are safe (`GLOSS_ON_PARTS`). It decorates the live DOM after render
rather than marking up `partRow`, so the string `checks/_verify_part_rows.mjs`
matches is byte-for-byte unchanged. Hover, tap, keyboard focus and Escape all
work. `#stats` is deliberately excluded - every row there already carries its
own `title`/`aria-label` from `EXPLAIN`, and two tooltips on one row is worse
than one. The same control asserts every term the page turns loose has a
definition behind it.

**`Alpha strike` is now `Alpha damage`** across all six places it appeared -
players and calculators say alpha damage; *alpha strike* is a US Navy and
MechWarrior phrase.

**THE DEVICE PANEL IS GENERATED INTO ITS HOSTS AND A HAND EDIT WILL VANISH.**
`device_engine.js` is the single writer; `inject_engine.py` copies it into
`_layer.src.html` and `keybinds.src.html` on every build, between fixed
boundary markers, behind a `node --check` gate. A hand fix to either host was
silently reverted by a build on 2026-08-30 - correctly, and with no warning.
**Fix the master, then inject.** `inject_engine.py` is still unowned; the
natural owner is Code.

**Armour and shields.** Armour resolves through each ship's own `Loadout`;
**eight** distinct damage-multiplier profiles. **Every shield in the game is
identical** — 73 items, one Absorption profile. Energy absorption is fixed at
1.00; physical is a **range, 0 to 0.45**, and what moves it along that range is
not established. Do not publish 45% as a value.

**Patch data: TWO HALVES OF THE SITE ARE PINNED TO DIFFERENT PATCHES, and the
old sentence here hid it.** Precisely:

    the ship page's data layer   snapshot 20260801T204744Z, stamped 4.9
    the hardpoint placement      scales against 4.10 lengths (since 08-27)
    the 4.10 snapshot on disk    20260827T225641Z, COMPLETE - counted
    the game                     Live Version 4.10.0, PTU empty

`build_loadout_data.py` hard-pins `SNAPSHOT` and `LAST_VERIFIED_PATCH`, on
purpose. **The 4.10 pull is two lines, is not blocked, and is queued as Q46
awaiting Sleven's go-ahead** - it brings in the Kruger S65 Stingray and will
produce correct refusals where CIG fixed two of their own class-name typos.
`docs/FINDING_the-4-10-pull-is-two-lines-and-here-is-exactly-what-changes-2026-08-30.md`.
Weapon findings written before 2026-08-27 are 4.9 and say so.

---

## What is open

### THE PUBLIC SITE IS FROZEN AND WILL BE REPLACED WHOLE — HIS RULING 2026-09-11

**The live site is not repaired. It is replaced, entire, by the test site on the day of
the swap.** So nothing is fixed on it in the meantime and no republish happens as its own
job.

**HE KNOWS IT CARRIES FALSE CLAIMS UNTIL THEN AND HAS MADE THAT CALL DELIBERATELY.** The
invented RAPTOR sentence — *"Flight-ready... Referral-program reward only (50 referrals
required)"* about a ship with no game file, no model, and a deliberate April Fools origin
— and a "LIVE 4.9.0" banner for a patch the game left in August. **Both stay public until
the swap. Do not re-raise either; it is ruled.**

**THE FIX IS ALREADY ON DISK AND COSTS NOTHING TO HOLD.** `releases/latest.html` and
`static/preview.html` both had the RAPTOR note emptied 2026-09-11, verified by content,
with the Scythe's separate and legitimate referral sentence left untouched. **If a
republish ever happens for another reason, the sentence goes with it.**
**Those two files are NOT downstream of `seed.py` or `testing/index.html`** — both of
those were corrected hours earlier and the sentence survived. `releases/latest.html` is
itself a source; the deployed index is built from it. **This chain has three origins, not
one.**

**WHAT THE RULING CHANGES FOR EVERY OTHER DESK: every gap between the two sites is now a
RELEASE BLOCKER.** The public page disappears on swap day and takes its features with it.
`NEXT.md` marks them — the Development Progress prose, the patch-notes link, the route to
`/find`, the dealer grid, the per-ship RSI links, and the category coverage.

### THE OUTSIDE REVIEW — FIVE RUNS, AND EVERY CONFIRMED FINDING GETS FIXED

**An outside reviewer with no knowledge of this project read the served site across five
runs on 2026-09-11.** Results at `claude/RESULT_comet-run-1..5-*.md`. **63 findings, 54
CONFIRMED**, filed as `NEXT.md` Q62 (runs 3 and 4) and the run 5 block inside Q55.

**His ruling: fix all of them, then the review runs again** — same five runs, freshly
checked answer key, every old ID marked fixed / still there / changed, new findings on
new IDs. **Done means deployed and read back, not fixed in the file.**

**The four worst, in his order:** the category buttons return **7 of 29** ground vehicles
and 34 ships have no career at all, so no button ever shows them; one ship shows **two
real-money prices** across two pages; the card and the ship page **disagree on role**; and
**the ship page shows less than the card that linked to it.**

**THREE REVIEWERS INDEPENDENTLY FOUND THE SAME PATCH BADGE** claiming a price came from
the game files while the panel beneath says prices are not in the game files. **That is
the strongest signal in the set and it is first in the order.**

**THE TRUST FINDING IS THE ONE TO UNDERSTAND.** The reviewer judged a first-time visitor
would trust the PUBLIC site more, because it puts one price and a *"Confirmed —
starcitizen.tools 4.9.0"* tag in the same row. **That trust is false: 4.9.0 is stale, and
the same site calls the Idris-P price confirmed while its own Legend says it is in
conflict.** So the rule for the per-row confidence note: **carry over WHERE the public
site puts trust — beside the price, no clicks — and never WHAT it claims.** A confidence
note that is present and wrong is worse than absent.

**THE CADENCE PROBLEM, RAISED WITH HIM, NOT ASSUMED.** About sixty entries, a
**1,885-second** sweep, and a deploy gate that refuses any payload whose fingerprint does
not match its sweep receipt. **Deployed one at a time that is over thirty hours of sweep
alone.** The resolution is not to batch the fixes — one commit per item is what makes a
failure have one cause — but to **fix one at a time and deploy in groups.** Until he
answers, that is how the work proceeds.

### THE FEEDBACK ROUTE IS RULED — KEEP, ON THE PAGE

**His words: *"I want to have that permanently, or at least for a while, right on the
page."*** Not behind a link, and it clears after each note so one person can send several.

**Destination ruled 2026-09-11 on architecture's recommendation: a plain HTML form — no
iframe, no third-party script — posting to the testing site's own Worker.** That Worker
already serves the site, so it is not new infrastructure. **It does NOT go in the
collector's R2 bucket and adds no route to the collector's Worker** — that standing rule
is untouched. Netlify Forms is the answer for a static live site and is not built.
**Placement and wording went to outside research; nothing else waits on it.**

**THE ZERO SUBMISSIONS PROVE NOTHING EITHER WAY and the record should say so.** The site
is password-gated with a handful of invited visitors; that population produces zero
whether the form is buried or prominent. **His conclusion — that placement was the
problem — is right on the shape of the old route (a link out, to a third-party page,
three decisions before typing) and does not need the zero.** The consequence: **the
success test cannot be "submissions went up."** It is a test note submitted and read back
from wherever it lands.

### THE `editions.json` FOLD — TWO SHIP COUNTS EXPLAINED, ONE QUESTION LEFT

**253 against 254 is not a missing ship.** `build_next_frontpage.py:74` drops any row
named as a `from_row` in `editions.json`, and that file has exactly one entry: **Valkyrie
Liberator folded onto Valkyrie as "Liberator Edition", $375.** The card renders the
edition line and search finds it by full name.

**It read as a missing ship twice in one day** — once from the testing inventory, once
from the run 5 comparison — **because a card count cannot see a row folded into another
card.**

**Measured from the published page's own SHIPS array:** `releases/latest.html` carries
**254 entries, 254 unique, no duplicates**, including `Liberator`, `Valkyrie` and
`Valkyrie Liberator` as three separate rows, plus **six other edition-style ships carried
separately** — 600i Executive, Avenger Titan Renegade, C8X Pisces Expedition, Carrack
Expedition, F8C Lightning Executive, Gladius Pirate.

**So the fold is applied to exactly one of seven similar ships**, and the other six
survive as cards by arithmetic rather than assumption. **A rule applied once is a rule
nobody can predict. The one open question is his and is in his tray.**

**And his own caveat on the fold is live:** *"Sleven's call that the two are the same
hull. Not yet checked against CIG spec data."* **Routed to Build as research rather than
returned to him** — `Parts[0].Name` is how a variant finds its hull and that rule is
already proven on exact equality.

### THE AUTOMATION FREEZE — HIS RULING 2026-09-11. READ THIS BEFORE ANY WAKE WORK.

**THE WAKE SYSTEM STOPS AT CONTAINMENT.** No brakes, no doorbell, no activation, and
nothing queued ahead of the front page to extend it. **His ruling, following Echo's
answer:** freezing is safe precisely because the switch is absent and the watcher is
not connected to the launcher, so the unfinished system cannot begin waking desks by
itself. **The risk of a freeze is future staleness, not present execution.**

**WHAT THE FREEZE DOES NOT COVER: the mail service that is already running.** Defects
in the watcher and the reply path are not frozen — they stay on the queue, behind the
front page. The freeze is on EXTENDING the wake system, not on repairing what runs.

**Frozen state, from `logs/wake_log.jsonl` rather than from any memo:**

    switch          ABSENT. C:\Users\david\.cc-control\automation.switch does not
                    exist. Last five refusals are all reason "switch_off".
    watcher         running, NOT connected to the launcher.
    finished        step 1 (the launcher's two modes), step A (answer routing,
                    swapped and verified), containment (proved 2026-09-11 03:19).
    not built       the brakes (specified only), the doorbell (designed only),
                    the adjutant tray (specified only), sections 9 and 10 of the
                    answer spec (requirements only).

**RECHECK BEFORE ANYONE RESTARTS IT** — the specs will have gone stale under the
freeze and none of this may be assumed:

1. **The brakes spec's runaway wall against real measurement.** `MAX_BUDGET_USD = 2.00`
   was set as "about ten times the worst honest run". **The 26-second containment probe
   came to 0.527 by the same client-side estimate — the wall is under four times one
   probe, not ten times a working wake.** The margin claim is wrong; the figure may or
   may not be. Re-derive it from tokens on the first three real wakes.
2. Every containment flag re-proved on the current CLI version, not assumed from
   2.1.266.
3. The watcher-to-launcher connection, which has never existed and is last by design.
4. `protected_folders.txt` still has exactly one reader — the launcher has never heard
   of it.

**Build writes one archive entry after Q54** with the running watcher version, the
switch state, the finished steps and the recheck list. **That entry, not this section,
is the thing a restart reads first.**

### CONTAINMENT IS PROVED — CORRECTED 2026-09-11 AGAINST THE PAYLOAD FILE

**The record said the path allowance was unproven. That was wrong, and this desk wrote
it.** Corrected on his ruling and confirmed from `logs/wake_payload_probe_20260910-221939.json`,
which this desk had not read when it wrote the original.

**The containment probe, run 20260911T031909Z, carried the allowance:**

    --tools           Read,Glob,Grep,Write
    --allowedTools    Read,Glob,Grep,Edit(inbox/_replies/**)

    inbox/_replies/_probe.md                     WRITTEN
    _probe_outside.txt (repo root)               REFUSED, nothing on disk
    inbox/Citizen Compass AI Brain/_probe_...    REFUSED, nothing on disk

**`permission_denials` in the payload names both refused calls as `tool_name: "Write"`.
The one that succeeded was also a `Write`, and it is not in that list.** The only thing
separating them is the path. **So the allowance did the selecting** — without it, the
in-allowance write would have hit the same approval wall as the other two and would be
in the denial list with them.

**The two together contained.** The allowance permits inside its path; no-prompt mode
denies everything it does not match, automatically, because there is no approval
surface.

**WHAT IS STILL UNTESTED, EXACTLY:** the allowance refusing a write BY ITSELF, with an
approver present. With somebody able to answer a prompt, a path outside the allowance
would prompt rather than auto-deny, and nobody has seen whether the allowance refuses
before that prompt or after it. **No wake runs with an approver, so the gap is not
load-bearing today.** It becomes load-bearing the moment one does.

**AND A MEASURED FACT THE DESIGN DEPENDS ON: an `Edit(...)` allow-list entry governed a
`Write` call.** `Edit(inbox/_replies/**)` permitted `Write` to a file in that path.
**An allow-list written in terms of `Edit(...)` is therefore broader than it reads**,
and any containment argument that leans on the tool name rather than the path is
unsound. Measured, not assumed.

**Why the earlier reading was wrong, because the shape repeats:** two different runs
were collapsed into one claim. The 16:43 audit wake genuinely carried no `--tools` and
no `--allowedTools` — true of that run, and it is where "no write-path restriction of
any kind" comes from. **The containment probe eight hours later is a different command
with the allowance present, and the conclusion from the first was generalised over the
second without anybody re-reading the log.**

### THE USAGE BLOCK IS LOGGED — CLOSED 2026-09-11

**`wake_usage` records are in `logs/wake_log.jsonl` now**, with `input_tokens`,
`output_tokens`, `cache_creation_input_tokens`, `cache_read_input_tokens`, `num_turns`,
and a `payload_file` pointer to the full response. **The "parsed, printed and thrown
away" defect is fixed and nothing in the record should still say it is open.**

**First real figures, one 26-second five-turn probe:**

    input 66   output 1,663 (583 thinking)   cache created 44,149   cache read 85,602

**Cache read is 85,602 against 66 input tokens on a five-turn run.** That is the 304,000
finding measured rather than derived, and it confirms the shape: the prefix is what
costs, multiplied by the request count. **Nothing is tuned — the freeze covers this
too — but the measurement now exists and the levers can be judged against it when the
freeze lifts.**

### THE TEST SITE MAY BE UNFINISHED. IT MAY NOT SAY ANYTHING FALSE. — HIS RULING 2026-09-11

**His words: "the test site may be unfinished, but it may not say anything false."
That standard applies to every page, not one footer.**

An incomplete feature on a password-gated testing site is legitimate. **A claim about
data verification that is not true is not**, because a reviewer reads it and assumes
the missing information exists somewhere they cannot see. **Q54 holds until the footer
is honest**; Build has that letter. Restoring the full confidence information is Q55
and is not a condition of the swap.

### AUTOMATION — STEP A IS IN AND PROVED ON THE LIVE TREE, 2026-09-11

**AN ANSWER GOES BACK TO THE SENDER.** Spec
`claude/SPEC_an-answer-goes-back-to-the-sender-2026-09-10.md`, sections 1–8 **BUILT,
swapped and verified on the live tree.** A memo carrying `Status: Answered` routes to
the tray of the desk in its **`From:`** line, not its `To:` — an answer to a letter
Build sent lands in Build's tray. `Closed`/`Done` go to `correspondence/answered/`, as
does an answer a desk wrote to itself. An unrecognised `From:` is refused to
`_needs_review/` rather than guessed (rule 19).

**THE DATE RULE — STANDING, HIS, 2026-09-11. NO DESK TYPES A DATE INTO A FILENAME.**
A new original letter carries **no date**; the watcher stamps it. A reply **preserves
the filename it received, exactly, character for character.**

**The reason is mechanical, not tidiness: the supersede is keyed to the filename.** A
desk that strips or re-types the date produces a second open copy that never clears,
and the tray then holds a letter that is not open. This desk had been stripping the
prefix on every reply all day and relying on re-stamping. **Proved the same day on a
Build letter** — the coalesce memo below superseded its open copy exactly, and the
answered copy landed in Build's tray.

`watcher-go/memo.go` only **fills a gap** in the date prefix and never corrects a
wrong one, so a wrongly-typed date is permanent. **Two-date filenames exist as
fixtures on disk** (`2026-08-30_2026-08-31_…`, `2026-09-08_20260908_…`) and the check
for them is with Build.

**THE ONE STALE PRE-RULE COPY WAS CLOSED 2026-09-12 AND THE DECISION TO LEAVE IT IS
REVERSED.** `2026-09-11_memo_architecture_intake-tray-rotations-…` sat Open in the
architecture tray with its answered copy dated `2026-09-10` in the owner tray. **The
reason for leaving it was that filing a second answer under a mismatched date would be
worse than a stale copy — and that weighed both costs in the ARCHIVE's terms when only
one of them lands there.**

    a duplicate in answered/   costs nothing. The archive is a RECORD.
    a stale letter in open/    costs a read at every boot, forever. The tray is a
                               WORK QUEUE and an Open letter is a claim that
                               something is owed.

**All three jobs in it had been done for a day** — the adjutant tray spec, the rotations
ruling he made himself, and the export design — **and this desk re-verified all three
today before concluding that.** That is the recurring price the original decision did not
count. **Closed as a superseded duplicate with the mismatch declared; two files now sit
in `answered/` for one exchange and that cost is paid once.**

**The rule that generalises: a stale copy is only cheap in a folder nobody works.**

**THE EXPORT BOUNDARY IS INVERTED — CONTENT REFUSAL IS WITHDRAWN.**
`claude/DESIGN_the-curated-export-2026-09-11.md`, sections 5A–5E.

**A refusal is a deny-list, and a deny-list permits everything it was not taught.**
His two examples proved it: the exclusion is a concept, not a string (the Looking
Project also calls itself the Lens, the Machine, the looking machine, the shape
reader), and the path refusal already walks past `.cc-control\` with no drive letter.
Over prose, failing closed would mean allow-listing English. **There is no version of
this that works, and patching it would have made the list longer without changing the
direction in which it fails.**

    the boundary   C:\Users\david\.cc-control\export.allow
    one line       <relative path>   <sha256 at the moment he approved it>

**In the control folder beside the switch, for the same reason: no desk can write it,
so no desk can grant itself an export.** His hand only. A document whose content
changed since approval **drops out**, and the manifest says it dropped and why. **The
cost is real — the export lags, and every edit to an exported document needs his word
again.** Recommended anyway on his own sentence: *four documents I trust rather than
forty I have to think about.* **The one open question is his: drop-on-edit, or stay
current and take a report instead.**

**The in-document marker is DROPPED** — this desk's own mechanism, withdrawn. Two
mechanisms for one decision is the second-source-of-truth defect, and its premise
("the decision belongs with the person who knows") is refuted by his four examples,
which are four authors who did not know.

**The refusals survive as a report-only tripwire and are never the reason anything is
safe.** The manifest says *the tripwire did not fire*, never *the document is clean.*
**Purpose is understanding and review, never ship data. Correspondence is excluded —
the reason is FORM: a letter is addressed to somebody, a document in `claude/` is
written to be read cold.** And the general rule out of his fourth example: **nothing
that describes the machine's defences is exportable — the brakes spec, the doorbell
design, the ACL audit, and the export design itself. The document that defines the
boundary must never cross the boundary it defines.**

**THE SEVENTH DESK — SPECIFIED, NOT ORDERED.** `claude/SPEC_the-adjutant-tray-2026-09-11.md`.
Five things move together: the procedure (`correspondence/README.md`), the tray, the
router (`memoTrays`), the checker (`checks/_verify_correspondence.py` +
`memo_desks_match_procedure_test.go`), **and a build-and-swap, because the router is a
compiled binary.** It rides with the fix for the `memoTrays` typed-map vs
derived-desk-list collision.

**TWO REQUIREMENTS IN THE ANSWER SPEC, BEHIND CONTAINMENT, NOT TO RIDE WITH STEP B.**

**§9 — a renamed answer is a protocol error, reported, never silent.**

**§10 — THE REPLY PATH NEVER COALESCES.** `pendingInboxFiles()` counts top-level files
only, `inbox/_replies/` is a subdirectory, so replies count as zero pending and every
reply pays the full `rescanAndScore()` + `regenerateHandoff()` tail — about seventy
seconds, ten replies being ten full runs. **Coalescing exists for a CORRECTNESS reason
— a slow tray means acting on an order already withdrawn — and under the doorbell
replies are the highest-volume traffic in the system.**

**The cause is a proxy error and the code's own comment has always said so:** the
comment says *the protected subdirectories under `inbox/` are not a work queue* and the
code says `if !e.IsDir()`. **"Is a directory" was a stand-in for "is protected", and
the proxy held only while every subdirectory happened to be protected.** `_replies/`
is the first one that is not.

    count top-level files, PLUS files in any subdirectory that is NOT protected

**Derived from `protected_folders.txt`, which the watcher already loads and already has
`isProtected()` for.** No new list, no second special case. **`maxCoalesced = 10`
already bounds the permanent-busy failure the old comment feared** — a stray folder
makes every operation defer ten times and then run, slower not stuck — **so no detector
is to be added.** The fix **depends on `_replies/` never being protected**, which
`checks/_verify_reply_path.py` holds.

**THE RECURRING DEFECT SHAPE, NAMED 2026-09-11: A RULE KEYED TO A PROXY RATHER THAN TO
THE THING ITSELF.** The date prefix standing in for a letter's identity;
`!e.IsDir()` standing in for "is protected". Both held until the first case where the
proxy and the thing came apart. **It sits beside the older shape this project keeps
paying for — a system that reports what it managed to do and not what it failed to
do.**

**STILL OPEN, WITH BUILD** (the mail-service items only; everything wake-side is
frozen): the two-date filename check; **the watcher periodic rescan** — Windows
`ReadDirectoryChangesW` discards the whole buffer on overflow and the documented
recovery is to re-enumerate, while our watcher sweeps once at startup and only logs the
error, **so a letter can be lost silently**; the launcher reading
`protected_folders.txt`; the seven RSI price corrections; the URL report-only
control; the third sweep receipt. **The launcher and the brakes are frozen.**

**WITH HIM — BOTH EARLIER QUESTIONS ARE NOW RULED.** Containment is proved and the
wake system is frozen; drop-on-change is his ruling and is written into section 5F of
the export design. **What is still his and only his:** the export allow-list, its
folder, group and ACL — hard rule 6 keeps permission changes outside the repository
off this desk — and the claude.ai project instruction that tells sessions to save to
the cloud. **And the named list of process cuts, in his tray, awaiting a yes or no.**

**`device_bash` is down on every Cowork desk and the cause is external:** a Windows
update released 2026-09-08 stops the workspace mounting the connected folders. Every
file operation is stage-and-commit until it is fixed. **Not ours, not actionable
here, and it is why bridge-write verification now matters** — see
`claude/FINDING_a-bridge-write-is-verified-by-size-...-2026-09-11.md`.

**A CORRECTION THIS DESK OWES ITSELF: `device_commit_files` WRITES WERE NOT SILENTLY
FAILING.** It reports `written` and the file lands seconds to minutes later; a staged
read in between serves a stale snapshot. This desk told Build its writes had failed and
had to withdraw it. **Working rule: write, wait, verify by content or size, force-retry
if needed.**

### AUTOMATION — TWO MORE OF HIS REQUIREMENTS TAKEN, 2026-09-10

Design: `claude/DESIGN_the-doorbell-the-job-number-and-the-punch-card-2026-09-10.md`,
**on disk, sections 17, 18 and 19 added.** The claude.ai project copy is a mirror.

**BLOCKED MUST NOT LOOK LIKE IDLE.** A desk that stops writes `blocked_on` and
`clears_by` on its stamp; the blocker routes to the desk that can clear it and
reaches Sleven only when `clears_by` is OWNER. **"Go" does not clear a blocker** —
the desk stops again on the same one. `state` is DERIVED from the lock, the tray and
the last stamp, never written, because a written `state` is a status file with two
entries.

**RULED — `clears_by` is a CLOSED list** (the desk list already derived from the tray
folders; unrecognised value goes to `_needs_review/`). **`blocked_on` is a free string
with a typed prefix** — `path:` `job:` `desk:` `decision:`. Three of the four can be
tested for existence, which is what lets something other than a person say a blocker
has cleared. `decision:` implies `clears_by: OWNER`. Unrecognised prefix is refused,
not guessed.

**The refusal to wake is on RE-WAKING THE BLOCKED DESK, not on moving the job** —
without that the rule deadlocks the thing it exists to unblock.

**THE ROLL CALL IS DERIVED, NEVER STORED** — locks, stamps, trays, `blocked_on`, and
the age of the last output beside every WORKING desk. **It must also report the
watcher's heartbeat age**, or a dead watcher reads as "every desk is idle". It is the
Adjutant's job at the start of a conversation, and it is not a wake.

**THE SWITCH lives outside every folder a desk can write to** — same reason as the
presence marker: a switch a desk can write is a switch a desk can turn back on. **Its
OFF state shows in the roll call**, or "off" and "idle" look identical.

**THE HEADLESS CONDITION IS MET AS HE WROTE IT.** Four runs, seen by him, filed at
`claude/VERIFIED_four-headless-runs-and-the-flag-set-that-would-have-wasted-the-night-2026-09-10.md`.
**AMENDED, from `logs/wake_log.jsonl` rather than from anybody's memo.** A real wake
ran on the Windows machine at 16:43:55 UTC, ended 16:45:18, exit 0, 81 seconds, and
the reply reached his tray. A containment probe and a second letter ran at 17:35.
**That closes the flag set on 2.1.266 and the inbox path on Windows separators.**

**AND THE LOG CHANGES THE READING OF RUN A.** The command that succeeded carried NO
`--tools` and NO `--allowedTools` — `--restricted`, `--permission-prompts none`, a
deny-list, and `--add-dir <repo root>`. **So THAT wake had no write-path restriction
of any kind.** **CORRECTED 2026-09-11 — this was then generalised into "containment is
the open hole" and that is wrong.** The containment probe is a different command with
the allowance present, and it passed. See the correction at the top of this section.

**Run A's Write was DENIED on Linux with that same flag shape.** The two commands
differ in two ways, not one: the platform, and `--add-dir`, which Run A did not carry.
**`--add-dir` is the likelier explanation and it is NOT asserted** — the test is Run
A's exact flags plus `--add-dir` on the replica. **Recorded as unexplained.**

**OPEN FINDING — `protected_folders.txt` has exactly one reader.** The watcher honours
it at any depth; the launcher has never heard of it. **Corrected the same day: the
live rule is not `Edit(inbox/**)` — that wake had no write-path rule at all.**
**The launcher's gap is still real and is now FROZEN with the rest of the wake work**;
it goes on the restart checklist, not on a queue.

### THE BRAKES ARE SPECIFIED — `claude/SPEC_the-brakes-2026-09-10.md`, ON DISK

Step 2, and it answers his five questions. `run_id` and a version field on every
wake-log record; the switch; the per-desk lock; the two ceilings; the spend stop.
**The wake log is the counter and there is no second counter.**

Decisions in it the design had left open: the day is `America/Chicago` midnight to
midnight, not UTC; the fifteen minutes is a rolling window, not a clock quarter; **a
containment probe and its letter are ONE wake**, counted by `run_id`; the lock is
taken by the launcher, never the watcher, so a hand-typed wake takes one too; a stale
lock is reported once, never cleared, and is read by the Adjutant AND the nightly
auditor.

**A letter held by a ceiling would have been lost** — a wake follows a filing and
nothing rescans the trays. Fixed with a `wake_withheld` record the watcher replays
from; never a tray scan. **And the two ceilings are different instruments:** the
fifteen-minute window is a throttle that self-clears, the daily twenty is a stop for
the day.

**RULED — ONE master switch, not per-desk.** A per-desk switch has a state that can be
wrong in a way one switch cannot, and a desk switched off individually looks exactly
like a desk with nothing to do. Cost stated: stopping one broken desk stops all four.

### THE DOLLAR FRAMING IS WITHDRAWN — HIS RULING, AND THE ERROR WAS THIS DESK'S

**He is on a subscription; `ANTHROPIC_API_KEY` is not set; there is no bill.**
`total_cost_usd` is a client-side estimate for somebody paying per call, and
Anthropic's own documentation says the figure is not relevant for billing on Pro or
Max. **This desk multiplied it by twenty and put a forty-dollar day in front of him.**

**The unit is tokens against his allowance.** `MAX_BUDGET_USD = 2.00` stands as a
RUNAWAY WALL set by architecture from measurement — about ten times the worst honest
run — not a budget he picks from a price. **Reported to him: input, output, cache
created, cache read.** `total_cost_usd` stays in the record, out of the report.
**Daytime Code has no measurement, so it has no cap, so Code is not woken.**

### THE 304,000 — `claude/FINDING_the-304000-is-the-rules-file-read-once-per-tool-call-2026-09-10.md`

**First finding: nobody can re-check it.** `wake_log.jsonl` records
`"usage_parsed": true` and not one token count — parsed, printed, thrown away. The
sweep-timing defect again. **Nothing is tuned until the block is logged.**

**The number is not one context.** `cache_read` is cumulative across requests; every
tool call is another request re-reading the whole prefix. ~22,000-token prefix × ~14
requests ≈ 304,000. Derived, not measured.

**Cache reads DO count against his allowance — discounted, not free.** So the prefix
is what matters, because it is multiplied by the request count.

**Three levers, none to be touched before three wakes are measured:** CLAUDE.md is
30,248 of the prompt file's 33,601 bytes (624 of 699 lines) and is re-read every
request — Anthropic's guidance is under 200 lines, and Build already wrote a correct
six-bullet subset and then appended the whole file under it; **extended thinking is on
by default, billed as output tokens, and nobody has looked at it**; and a cache miss
reprocesses the full prefix, lifetime one hour, **which puts the fifteen-minute window
in tension with the allowance**.

### THE CHAIN IS A CONVENTION AND HE WANTS IT TO BE A RULE

me → architecture → Build → architecture → ... → him after bounded rounds. **He is
taking the design to an outside desk first**; architecture supplied the collisions
only. The six: **four punches is TWO rounds under the chain, not four**; the card and
the chain are two clocks on one escalation and the round must be the authority; a
route needs the ordered hop list the card does not keep; the owner-tray punch
exemption is already a route rule in disguise; **the chain closes the new-file dodge
and the three-desk circle the card could not**; and **a route rule that governs every
letter would make desk-to-desk findings illegal** — the rule must separate a JOB,
which travels the chain, from a LETTER, which does not.

### RSI PRICES AND THE STICK PANELS — RULED 2026-09-10, QUEUED BEHIND AUTOMATION

From CIC's letter of 2026-09-10, all read off RSI's own store twice, four days apart.

**Seven of ours are wrong and go to RSI's number:** Cutlass Steel 235, Cutlass Blue
175, Cutlass Black 110, Cutlass Red 135, Sabre 175, Herald 85, Cutter Rambler 50.
**The source is RSI, not the aggregator** — the aggregator agreeing is a coincidence
of two readings of one page.

**The Retaliator does NOT move.** Ours is $175 and right; there is one Retaliator
product on the store and "Bomber" returns zero results, so the $275 is attached to a
product RSI does not sell under that name. **Reason goes into
`price_corrections.json`** so it is not re-opened.

**Those seven rows carry `last_verified_patch` and the other 247 do not** —
deliberate; Q61 records all 254 unmarked, and the three-state card mark exists so
"Checked" and "Awaiting check" can both be true on one page.

**SCHEMA REQUIREMENT (architecture's, not built):** a price records WHICH SURFACE it
was read from. The Herald has no price on its own ship page at all; the split was
measured on 39 of 80 single-ship pages. Without it a re-check reports a false red.

**URL rule, queued as report-only:** family segment lowercase (136/136), ship segment
verbatim from the name (253/253). `/pledge/Standalone-Ships/` is a real 404, not a
redirect. The `?search=` endpoint appears to ignore the sale filter — **recorded as
unexplained; the disjoint finding stands and is confirmed against the paginated list,
never the search.**

**RULED — nothing in this project keys a control's identity to its HID button
number.** VKB and VIRPIL both renumber in-device and VKB's own manual tells owners to;
WinWing does not, recorded as a measured negative. **Shift state is what kills it** —
one physical control reporting several numbers by mode cannot be stored as a table at
all. The picture is what the pilot clicks, not what we label. **Recorded in the
Looking Project's own record; only a pointer stays here.**


### THE STANDING RULES SLEVEN ADDED 2026-09-08 — read these before working a tray

**WHEN HE SAYS "INBOX", THE TRAY IS WORKED TO EMPTY.** Every letter gets ANSWERED
(answer written into the memo, moved to `correspondence/answered/`), STILL OPEN WITH
A WRITTEN REASON, or SUPERSEDED. **A letter with no stated blocker is not open, it is
ignored.** His limit matters as much as the rule: *a letter answered badly is worse
than one answered late*, and naming what a letter waits on counts as working it.
**It is not triggered by him** — every tray is read at boot, before the desk says
anything to him.

**A PROBLEM IN ANOTHER DESK'S WORK GOES BACK TO THAT DESK**, with the reason and the
suggested fix. Not fixed quietly, not brought to him. **It comes to him only if
fixing it would change what he actually asked for** — a technical problem goes to the
desk, a changed intention goes to him.

**AN AUDIT PASS IS NOT A WARRANTY.** A defect found in already-audited work still
goes back to the desk that made it, and the audit desk is told what its pass missed.
His proof: the audit desk cleared a duplicated doctrine sentence as cosmetic, and the
leftover copy preserved exactly the rule the amendment was written to kill. **An
audit desk that is never contradicted is not being read.**

**THE THIRD STATE — RETURNED. Ruled, not built.** A badly answered letter is the
same file moving from `answered/` back into the answering desk's tray with a dated
round appended, never a new file and never renamed. It does **not** go through
`inbox/` — the watcher renames anything dropped there and the thread would be lost.
A return with no stated reason is a new question. **Three rounds and it stops being
correspondence: that is two desks disagreeing, and that case goes to him** with its
own history attached.

**C1's boot prompt now exists** at `claude/PROMPT_boot-a-new-c1.md` and carries all
of the above.

### THE TRAY WAS WORKED TO EMPTY 2026-09-08 — 41 letters

Full record: `claude/RULINGS_the-tray-worked-to-empty-2026-09-08.md`. One letter left
open (sweep composition, waiting on two more receipts). **The rulings a later session
is most likely to trip over:**

- **`design/ANGLES.md` is a DECLARED SHARED ARTIFACT** — the only exception to hard
  rule 14. Additive only, every addition names its desk, C1 owns the frame. The
  sixty-angles method is BINDING on every desk and deliberately does **not** move
  into `docs/ARCHITECTURE_DECISIONS.md`.
- **A browser-driven visual check may be a registered checker.** Three registered,
  unchanged, on the auditor schedule. **An eye flags and never fixes, ten eyes feed
  one board, and an eye never gates a deploy.** The other eighteen wait on a measured
  runtime.
- **The open-edge indicator is retired for new-pipeline hulls, and the export does
  not weld to make it read better.**
- **Nothing from a community price aggregator is promoted into the site.** The 14 real
  disagreements go back to RSI's own store.
- **The stick-panel idea is our own photographs only** and nothing is designed until
  the HID remap question is measured.
- **Ship models have no UV map at all** — every vertex (0,0), empty upstream at RSI.
  Textures cannot be applied to them by anybody. The 2026-08-07 finding saying
  otherwise is **retracted, not corrected**.


**THE FRONT PAGE REWIRING — Job B, ordered 2026-09-06, not started.** The one that
matters, and the reason it matters is worse than it looks:

**CORRECTED 2026-09-06 — C1 said the generator was thrown away and it was not.**
`./build_frontpage_data.py` is in the repo root, 5,270 bytes, since 2026-08-30,
its docstring naming C1 as its writer. **It is UNTRACKED**, which is why a search
reported it absent. Code found it in two minutes and proved it regenerates
`frontpage_data.json` byte for byte — 1,836,783 bytes, identical sha — testing
against a copy rather than touching C1's file. **Code refused to rebuild it and
was right to**: a rewrite against a disproved premise would have been a second
writer on C1's artifact and risked silently changing 254 rows.

**B0 IS DONE — committed 2026-09-08 as `c8ab1d0`**, five files, 888 lines:
`build_frontpage_data.py` and the four in `tools/frontpage/`. Pushed, and the
remote sha read back off `origin` rather than trusted from an exit code.
`main-page-concepts/` still has no `MANIFEST.json`.

**And the eight-day jam behind it:** nothing had been committed since 2026-08-30
because a git process died and left `.git/index.lock`. Three sessions read that
as rule-2 discipline. `docs/handoff_archive/` has the record.

Behind it: the three hand-maintained override files (`price_corrections.json`,
`editions.json`, and the picture map — `sleven_thumbs.json` is RETIRED, replaced
by `card_pictures.json` from `tools/frontpage/build_card_pictures.py`, which reads
several raw folders each carrying its own credit and REFUSES a folder whose
manifest states none) that exist only because the snapshot cannot
be regenerated, and each of which is a second writer — rule 14. Then the schema
from CIC's sweep (`ship_family` + `family_id`, three-state `price_status`,
`name_alias`), then the page as a real source page instead of a 2.4 MB blob with
every picture inlined, then the deliberate retirement of the
`releases/latest.html` assembly path and its exact-string guards.

**Sleven's name decisions, waiting on him.** About twenty ships the store spells
differently than we do (*Aurora MR* against *Aurora Mk I MR*), the ambiguous
`Dragonfly` (the store sells a Black and a Yellowjacket; we hold one row) and
`600i Executive Edition` (the store does not sell it at all), and seven store
hulls absent from our list entirely. Listed in
`data-layer/raw/ship-images-from-sleven/NAME-DECISIONS.txt`. **None were joined.
Rule 17 forbids the matching and rule 19 refuses the ambiguity.**

**Pictures: 6 ships still show a ghost or nothing** — F7C-M Hornet Heartseeker
Mk II, CSV-FM, MOTH, Genesis Starliner, RAPTOR, Starlancer BLD. **Counted off the
rendered page, from the cards that actually draw the NO IMAGE box.** The figure
here said 19 for two days after it stopped being true. Sleven closes these by hand,
saving RSI store pages; intake is automatic from a connected folder. Done so far:
Arrow, Gladius, Odin, Tiburon, Valkyrie Liberator. **Eight have no store page in
either view** — the three ATLS IKTI variants, CSV-FM, F7C-M Hornet Heartseeker
Mk II, Gladius Dunlevy, RAPTOR, Starlancer BLD — so there is nothing for him to
save and those gaps stay open. That is the correct outcome, not a failure.
**The earlier claim that C1 could render these from the 3D models we hold was
false** and is corrected on file: those ghost pictures ARE that render, untextured,
and re-running it produces the same ghost.


**Blocked on a measurement, not on effort**

- **Effective damage against a chosen ship** — the whole chain is in the data and
  the arithmetic is trivial, but shields carry both `Absorption` and
  `Shield.Resistance` and **nobody has established whether they stack**.
  Publishing a confident wrong number here is worse than publishing DPS.
  `Shield.Resistance` is NOT `Durability.Resistance`; those are different blocks
  and one was closed in place of the other.
- ~~The Glaive and the Scythe~~ — **closed 2026-08-28.** The Glaive was never
  asymmetric; the mirror was filtering out the mounts that prove its frame. It
  is in, at 13 of 19 named pairs. The Scythe is 1 of 16, genuinely asymmetric,
  and stays refused for a reason that is now measured rather than assumed. The
  tolerance was not touched. `docs/FINDING_the-glaive-was-never-asymmetric-2026-08-28.md`.

**Owned by C1, not started**

- **THIRTY SHIPS HAVE A MODEL BUILT AND SHIPPED THAT NO VISITOR CAN REACH.** They
  send the visitor to robertsspaceindustries.com instead, because no game file means
  no ClassName, which means no ship page. Arrastra, Crucible, E1 Spirit, Endeavor,
  Expanse, F7C-M Super Hornet Heartseeker Mk I, G12/G12a/G12r, Galaxy, Genesis
  Starliner, Hull D, Hull E, Kraken, Kraken Privateer, Legionnaire, Liberator,
  Merchantman, Mustang Alpha Vindicator, Nautilus, Odin, Odyssey, Orion, Pioneer,
  Ranger CV/RC/TR, Valkyrie Liberator, Vulcan, Zeus Mk II MR. The work is paid for
  and thrown away. This is a routing problem, not a data problem, and L14 case 2
  already carries the wording for a page with a model and no loadout. **Raised
  2026-09-04, not authorised.**
- **Five ships Fleetyards lists that the site has no row for** - S-65 Stingray,
  Dragonfly Yellowjacket, Nox Kue, Dragonfly Starkitten Edition, Bengal (the Bengal
  has no holo model at all). Yellowjacket and Nox Kue already have a built `.glb`
  reachable by no row. **THREE ARE NOW UNHELD (2026-09-06):** CIC read S-65
  Stingray $175, Dragonfly Yellowjacket $40 and Nox Kue $45 live off CIG's own
  store, which is what the hold required. Their aUEC dealer price is a different
  field from a different place and remains unverified, so those rows go up with a
  USD price and an empty aUEC. **Starkitten Edition and Bengal stay HELD** - checked
  against the full 253 and not in the store at all.
- Which paint treatment the fleet gets, and the manufacturer table behind it.
- Shop and price data has never been verified against the game.

**Sleven's alone**

- Whether and when the site goes live.
- Every legal, Fan Kit and trademark question.

---

**THE REBUILD EXISTS AND IS TWO THIRDS OF ITS FOUNDATION — `collector2/`,
updated 2026-09-08.** 2,778 lines of Go. In the store: **2,925 observations from
247 archived game logs going back to January 2024.**

    gamelog@3   104 payouts   289 shop transactions   32 rocks
    gamelog@1   retracted, rows KEPT on disk, no longer counted
    gamelog@2   retracted, same

**EVERY OBSERVATION SO FAR CAME FROM THE GAME LOG. THE SCREEN READER HAS WRITTEN
ZERO.** That half does not exist yet.

**And every payout figure this store produced before 2026-09-08 was void.** The
reader's pattern was case-sensitive on `Notification`, so it matched 312 UI
redraws and **none of the 104 real events** — it was not over-counting, it had
never once recorded the moment money arrived. Keyed now on `(occurred,
notification_id)`, the game's own printed values, exact equality. `occurred` is
required; `at` is INGEST time and was wrong by up to nine months.

**The re-mine was the first real test of "a better reader re-reads old nights"** —
the archive's whole justification, never once exercised until now. It passed:
2,925 read back, 2,500 skipped from readers no longer believed.

---

**THE FACT STORE THE COLLECTOR NEEDS IS 80% ALREADY IN THIS DATABASE.** Sleven
asked for the screen-reading collector to be designed from the ground up; the
ground-up design was going to be a new `facts` table and that would have been a
duplicate. `snapshots` + `item_prices` already IS an append-only fact store whose
unique key includes `snapshot_id` so a second pull adds rows rather than
overwriting, and `snapshots.source` was written generic on purpose - its own
comment anticipates non-UEX writers.

**The real gap is that `item_prices` needs ids and the collector reads STRINGS.**
`shop_item_id` and `terminal_id` are NOT NULL foreign keys. A reading of
`TITANIUM` cannot become a row without something turning that string into an id,
and rule 17 forbids doing it by similarity. So a reading that does not resolve has
nowhere to go, and both available outcomes - drop it or force it - are wrong.

**Two tables and one resolver close it**, ordered 2026-09-06:
`observations` (strings, verbatim, append-only, no image column and no path
column - rule 21 made structural), `observation_links` (the resolution kept
separate from the reading, UNIQUE per observation, `method IN ('exact')`), and an
exact-equality resolver whose zero-match outcome is a normal permanent state, not
an error. Two exact matches is refused and reported, never picked (rule 19).
`docs/DESIGN_the-fact-store-is-mostly-already-built-2026-09-06.md`,
`docs/ORDER_the-observations-table-and-the-exact-resolver-2026-09-06.md`.

**THE OLD COLLECTOR'S TRIGGERS ARE WRONG AND THAT IS MEASURED.** 756 PNGs and 757
JSON sidecars in `citizen-collector/captures/`, mostly 1920x1080, captured via
`wgc`. **426 of the 756 are labelled `terminal_open` or `terminal_scroll` and the
ones opened show a seat interior, a chat window and the quit-to-desktop dialog.
Not one shows a shop panel.** It predicts the moment to snap and predicts wrong.

**But the font question is answered and the answer is yes.** Legible content read
straight off the captures includes `Zone: DRAK Vulture 761884332511`,
`IRON (ORE) 722.3m`, `98% H-FUEL / 19% Q-FUEL`, and the entire debug overlay -
which prints patch `4.9.188.23497`, build, server, player location and
UniverseTime **on the frame**, so provenance for every reading is free.
**Player names are visible in chat, which is why chat is not a readable panel.**

**THE COLLECTOR'S MOST VALUABLE HALF IS ALREADY BUILT AND IT IS NOT THE CAMERA.**
`citizen-collector/gamelog_mine.go` (71 KB, the largest file in the program) reads
Star Citizen's own `Game.log` and its `logbackups` archive - **no OCR, no shape
table, no panel table, and it cannot be misread.** CIG renames rather than
overwrites, so a new install starts from however long that player has been
playing. It matches on PAYLOAD SHAPE, never on the emitting class name, which is
why it survived CIG renaming `CEntityComponentShopUIProvider` to
`CEntityComponentShoppingProvider` between 4.9 and 4.10 - and found three
transaction families nobody knew existed.

Counted from `captures/gamelog-dataset.json`, schema 3, 2026-08-18, tool 0.3.3:

    ship_classes ........ 992      equipment_seen ...... 542
    quantum_routes ....... 57      contracts_seen ....... 55
    locations ............ 44      subsystems ........... 71
    deaths .............. 131      shop_class_names ..... 18
    builds ............... 34      mission_payouts ...... 16
    sent_txn_keys ....... 308

**The 308 transactions carry `shopName`, `itemName`, `client_price`, `quantity`
and `currencyType`, and were SENT and cleared rather than stored anywhere
queryable.** So the log miner is the first writer that should land in
`observations`, and the screen reader's job is what the log does NOT emit - a
shelf price nobody bought, a stock level, a panel walked past - not a second
worse copy of what the log already says.

**AND IT ALREADY GIVES THE RESOLVER ITS TEST DATA.** 992 ship class names and 542
equipment names against `shop_items` is a real exact-match rate measurable now,
with no reading half built.

**C1'S §5 NAME CHECK WAS THE ONE MECHANISM THIS PROJECT HAD ALREADY FORBIDDEN,
IN WRITING, THREE WEEKS EARLIER.** The order asked for a CHECK constraint
refusing a handle-SHAPED string. `gamelog_mine.go:211` carries **THE GOVERNING
RULE FOR EVERYTHING DERIVED FROM ANYTHING - Sleven, 2026-08-13**: handles look
like ordinary words, so any heuristic either misses real ones or eats legitimate
shop and item names, and **both failures are silent**. The comment predicts this
exact error by name - *"writing 'a quick scrubber for the OCR output' will feel
like the reasonable thing to do"* - and C1 walked into it on the first attempt.
**Corrected to an allow-list in the shape of `mineTxnKeep`: a rectangle not named
in the panel table is never read, and a field not named is never written. Chat,
contacts, party and friends are never named.**
`docs/ADDENDUM_the-log-miner-is-the-first-writer-and-my-name-check-was-the-forbidden-filter-2026-09-06.md`.

**SLEVEN'S RULING 2026-09-06: IT IS A REBUILD, AND THE PROVEN PARTS ARE CARRIED
IN.** His words: *"it's a complete rebuild because we're gonna be building a
program, not a set of things working in the background... we're gonna take the
basic things that did work with the collector, and we're gonna redesign them into
this more advanced program that will grow."* So: new program structure, and the
log miner, WGC capture, consent gate, scrub, service install and the selftest
discipline are carried in as designed modules rather than rewritten. **The
trigger layer is the part that dies** - 426 of 756 frames mislabelled, not one
showing a shop panel. The old program is 27,822 lines of Go across 92 files, 37
of them selftests.

**WHAT IS CARRIED IN, AND IT IS MEASURED NOT ASSUMED: 575 selftest checks, 0
failed** (Windows, 2026-08-27), working Windows.Graphics.Capture (756 frames),
service install, autostart, scrub, export, and the log miner above.
**What is provably wrong is the trigger layer alone**, and it is not carried in.

**SLEVEN'S RULING 2026-09-06 ON CONSENT: THERE IS NONE, AND THAT IS DELIBERATE.**
His words: *"There doesn't need to be any consent on the collector right now. at
all because the collector is gonna be rebuilt on only my computer. Once I finish
building it, then we will reevaluate all the consent it needs and figure out how
to properly do it before it's ever shipped to anybody."*

So the consent gate is **NOT** carried into the rebuild as a working module. It
is deferred, whole, to be designed fresh when the collector is finished and
before it reaches anybody but him. The 2,838-character text, the 2,600 assertion
at `consent_selftest.go:225` and `consentVersion = 4` are all **retired with the
old program** rather than fixed. **The memo asking Sleven to trim or raise the
limit is closed by this ruling; neither was the answer.**

**The risk this creates, and it is C1's to hold:** a program with no consent, on
one machine, is correct today and becomes a shipping defect the moment anything
leaves that machine. "We will figure it out before it ships" is an intention, and
an intention cannot fail. **A suggestion, not a requirement:** the build could
refuse to produce a distributable artifact — installer, signed binary, public
download — while consent is unresolved, as a build failure rather than a warning.
**Sleven has not accepted this and it is not decided.**

**THE REBUILD IS STILL BEING DESIGNED — 2026-09-06.** C1 wrote the ruling above
as though it settled the design and Sleven corrected it immediately: *"Don't rule
anything as set in stone. The collector's rebuild is still being designed. I know
we have agreed upon foundation pieces, but everything else is still being
designed."* **Agreed foundations and open design are separated in
`docs/DESIGN_the-fact-store-is-mostly-already-built-2026-09-06.md`.** The
paragraphs above this one are the foundations. Everything else about the
collector is open and Sleven is designing it. **No session closes any of it.**

---

**THE SWEEP IS GREEN AND TESTING IS DEPLOYED - 2026-09-06 02:09.**

    120 ok, 0 failed, 3 skipped, 0 NOT RUN, in 1885s
    fingerprint 53676ee77da95f1f
    Version ID de3a43f1-f3cd-4b5b-bba5-ea408f992337, 524 files, 517.9 MB

**Deployed WITHOUT rebuilding first, on purpose:** a rebuild changes the payload
fingerprint and invalidates the sweep receipt, so the gate would then refuse.
The sweep ran against this exact payload. **One file changed on the wire -
`/loadout_marker.gen.js`** - which is the markers re-fitted by the `hull_box()`
correction on seven hulls. No `-IgnoreSweep`. Netlify untouched.

**Verified from SERVED BYTES, and the shipped file checked independently by C1
rather than read off Code's report (rule 16): sha256 `a6cf733fa0584764`,
289,793 bytes, served and local identical.** Title reads *"Citizen Compass
v0.4.0 - testing 2026-09-06"*. **Nothing committed, nothing pushed** - 385 files
modified in the working tree, awaiting Sleven's go-ahead (rule 2).

**THE FIVE CHECKS, AND WHO CLOSED WHAT.** Code re-pinned
`_verify_g3_matcher_delta.py` and `_verify_stage_floor.mjs` **to NAMES rather
than counts** - a count moves whenever a hull is decoded, so it goes red for
something that is not a defect and the fix each time is to type a bigger number.
He split `_verify_hardpoint_join.py` in two and proved both halves by mutation,
and declared the 7 box-fix hulls by name in `_verify_placer_candidates.py` after
catching himself matching them by SUBSTRING - his own rule 17 violation, redone
against `matched.json` on exact equality.

C1 closed her two. `_verify_marker_census.py`: **8 declarations removed**, six
restored to baseline exactly and two now ABOVE it (Tiburon 57 -> 65, Mantis
12 -> 18) where `compare()` never routed them to `declared` at all. **Not
rebaselined** - that would absorb the Perseus's 40 torpedo ports and four
vanished hulls. Six still fire, untouched.

**`_verify_child_markers.py` IS NOW SPLIT BY PROVENANCE AND THE HALF THAT
MATTERS GOT STRICTER.** Every marker that moved is `est`; **not one `cig`
coordinate moved anywhere in the fleet**, and the Polaris's 21 held exactly. So
pinning eleven coordinate triples was the wrong shape - an estimate is
RECOMPUTED by design when the box changes. The rule is now **"NO MARKER LABELLED
`cig` MOVED - and nothing may excuse one"**, checked BEFORE any exception so no
entry can reach it, plus a named `REESTIMATED` hull list that refuses an entry
firing on nothing. Both new assertions proven able to fail: `--mutate-move-cig`
moves a `cig` coordinate on a hull that IS in the exception list, and goes red.
**`_verify_child_markers.py` and `_fixtures_markers/` were on nobody's list -
the FIFTH ownership gap found the same way - and are now claimed in OWNERS.md.**

**THE SAN'TOK.YAI'S ESTIMATED HANDEDNESS IS REVERSED AND NOBODY HAS ESTABLISHED
WHICH IS RIGHT.** All ten of its `est` markers moved and nine are a MIRROR ACROSS
X (port 26 -0.90584 -> +0.90610; port 42 -0.69813 -> +0.69836). Two pairs
exchanged places: port 44's new position is **0.0059** from where 69 was, port
57's is **0.00039** from where 46 was. Allowed - it has no `cig` markers at all,
being one of the four refused for orientation on 2026-08-28 - but recorded in
full in the control rather than waved through.

**C1 WAS WRONG THREE TIMES TODAY AND A CHECK CAUGHT EACH ONE.** (1) "G3 gains 5
ships" - it gains 3; 85X and Starlite arrived with regenerated GEOMETRY, and
`_verify_hardpoint_join.py`'s EXPECTED map was quoted as a measurement. (2) "the
5% pure-white threshold is vacuous, nothing ships within 3x of it" - **14 hulls
are at or above 5%, max 9.21% on the Dragonfly Yellowjacket**, confirmed through
the control's own code path. The 1.63% in that file is ONE hull, the Liberator,
read as a fleet range. **Section 5 tests one hull and prints as if it tested the
fleet.** (3) the §5 name-shape CHECK constraint, see the collector section.
`docs/ERRATUM_the-threshold-was-never-vacuous-i-read-one-hull-as-the-fleet-2026-09-06.md`.

**The negative control now runs on the Liberator** - the hull `cc_viewer.js:447`
names as the one the E7b floor decision was made about: 1.63% shipped, **8.34%
with the pre-pass removed**. The within-hull comparison is sound where a fleet
comparison is not, because the 80,000-point sample cap decimates hulls by factors
of **1.0 to 79.4** and that confound cancels only within one hull. Code's ratio
test went in as its OWN control (5.1x, floor 2x), not as a replacement, and he
reported that all three of his new assertions stay green under `--mutate-prepass`
because `sNo` is modelled arithmetic that never asks the viewer whether a
pre-pass exists - section 4 is what proves that. **He found his own new work
wanting in the same update that shipped it.**

**A CONTROL THAT READS A BUILD ARTEFACT IT DOES NOT REBUILD REPORTS ON WHATEVER
THE LAST BUILD LEFT.** `_verify_child_markers.py` passed at 00:36 and failed at
01:07 with no data change: controls run in alphabetical order, and three later
ones run builds. **Its green was worth nothing** - it agreed with itself about an
artefact nobody had regenerated. Queued, not patched, because the general shape
is a question about sweep ordering and not one declaration.

**QUEUE, none of it touched:** the 14 hulls over 5% (render defect or sampling
artefact - unanswered); section 5's one-hull scope; the ordering dependency;
`_verify_placer_candidates.py` raising a bare `FileNotFoundError` where NOT
PERFORMED belongs.

---

**THE 5% PURE-WHITE THRESHOLD MEASURES THE SAMPLING STRIDE, NOT THE RENDER.**
Ran the control unmodified once per hull, 150 hulls, `CC_GEO_DIR` pointed at each
alone. **It is not 14 hulls over the threshold. It is 50 of 150**, and which ones
fail is decided by `stride = count / sampled` - the every-Nth-vertex the geometry
file was decimated at:

    stride 1   n=  5   over 5%:  4  (80%)      stride 5   n= 14   over 5%: 0  ( 0%)
    stride 2   n= 29   over 5%: 20  (69%)      stride 6   n= 15   over 5%: 2  (13%)
    stride 3   n= 34   over 5%: 19  (56%)      stride 7   n= 18   over 5%: 2  (11%)
    stride 4   n= 19   over 5%:  1  ( 5%)      stride 8   n=  7   over 5%: 2  (29%)

**80% to 0%, monotonically.** And correcting for it REVERSES the verdict - raw
mean depth 16.0 for the failing group against 11.0 for the passing one, but
stride-corrected **42.2 against 56.5**: the flagged hulls are physically the LESS
dense ones.

**The second factor is aspect ratio.** Section 5 bins into a fixed 320x320 grid
normalised by the hull's LONGEST axis, so a long thin ship piles into few cells:
the **Caterpillar is the worst in the fleet at 20.88%, covering 2,198 px of
102,400**, and all three Caterpillar variants return byte-identical figures
because they are the same mesh. That is a shape, not a defect.

**`w < 5` as a per-hull absolute claim is therefore not sound and must not be
applied fleet-wide** - two hulls of identical real brightness differ 2.5x by
stride alone. **Within one hull it is completely sound**, stride and projection
cancelling exactly, **which is the regime Code's Step B negative control uses -
Liberator 1.63% shipped against 8.34% with the pre-pass removed - so that control
is correct and unaffected.** Code was right to refuse to call the 14 a defect and
right that his own correction was wrong: multiplying by the stride fixes
comparability but leaves calibration unanchored, which is why it put 187 hulls
over a threshold the visibly-not-white site refutes. **Comparability and
calibration are two problems and only one is arithmetic.**

**FIX, QUEUED NOT DONE:** make `cell[i]` stride-invariant; re-derive the
threshold from the Liberator as a MULTIPLE rather than a bare percentage (a bare
5% has no provenance - nobody can say where it came from, which is how it
survived measuring the wrong thing); keep the absolute per-hull assertion OFF
until then. **Not touched tonight - the sweep receipt is what holds the deploy
open.** 108 hulls unscanned and not claimed. Code's 14 against this 50 is
unresolved and worth one look before either is quoted.
`docs/FINDING_the-5-percent-threshold-measures-the-sampler-not-the-render-2026-09-06.md`.

**THE FRONT PAGE IS STILL THE SPREADSHEET BECAUSE C1 NEVER QUEUED THE WALL.**
`docs/SPEC_the-front-page-becomes-the-wall-2026-08-31.md` was written six days
ago, marked "NOT QUEUED", and **appears nowhere in `NEXT.md`.** Nothing failed to
deploy - the sweep ran green against this exact payload and 523 of 524 files were
already on the server. **The site looks unchanged because everything since
2026-08-31 has been hardpoints, models and controls.**

**AND THE OLD PAGE IS PRINTING WRONG PRICES ON 47 SHIPS RIGHT NOW.** Verified in
the served build:

    "name":"100i", "auec_price":1089270,
    "dealers":["New Deal","Astro Armada"], "confidence":"verified"

    ship_dealer_prices.json:  New Deal 1,089,270   Astro Armada 1,146,600

**One price beside two shops, wrong for one of them by 57,330 aUEC, and the row
is labelled `verified`.** The 890 Jump is out by 3,267,800. **The corrected data
has been on disk since 2026-08-31** - `data-layer/derived/ship-prices/
ship_dealer_prices.json`, 63 ships, exact mapping to our five dealer names, zero
unmapped, zero conflicts - and nothing reads it.

**Ordered 2026-09-06 in three steps that each ship alone:** per-dealer prices
into `SHIPS[]` with `auec_price` kept as the CHEAPEST (an absent price and a
copied one are different facts - do not spread one across shops); then **the
control that has never existed** - nothing anywhere checks that a ship's stated
price is the price at the dealer printed beside it, which is why this survived in
plain sight; then the empty state for the 9 ships with no picture.
**`data-layer/derived/ship-thumbs/` is cited by the spec and is NOT on disk** -
find it or declare it gone before the wall is planned. The wall itself gets its
own order; the map tab stays on hold pending CIC.
`docs/ORDER_the-front-page-is-still-the-spreadsheet-and-it-is-printing-wrong-prices-2026-09-06.md`.

---

## Reading order for a new session

1. **This document.**
2. `NEXT.md` — the live queue. C1 is its only writer.
3. `LIVE.md` — what is actually public.
4. The newest entries in `docs/handoff_archive/`.
5. `RECOVERY.md` — what lives off the machine.
6. `docs/STATE-ARCHIVE-through-2026-08-27.md` — **only** for why something was
   done the way it was.

---

**The roadmap watcher answers R3 already and throws the answer away.**
`GET /api/roadmap/v1/boards/1` returns `data.description` = *"Live Version:
4.10.0 ▪ Latest Roadmap Roundup: 08/26/2026 ▪ PTU Version: ø"*. `board.go`'s
`Board.Data` struct does not declare `description`, so Go discards it at
unmarshal. **And the watcher has never run on its own schedule**
(`last_good_scheduled_run` is empty) and is filtered to `"watch":
"Constellation"`, which is why its baseline holds three cards. Q5 re-scoped to
four items in priority order; R3 is third because it is the least valuable.
`docs/FINDING_r3-is-a-struct-field-the-watcher-already-downloads-2026-08-30.md`.

---

## 2026-09-12 — FOUR RULINGS OUT OF THE ARCHITECTURE TRAY

**1. `design/ANGLES.md` IS ADDITIVE AGAIN. THE WITHDRAWAL WAS THE ERROR.**
On 2026-09-08 the shared-artifact exception was recorded as withdrawn in
`OWNERS.md`, on the grounds that Sleven had moved the METHOD out to
`CCDesk-logs/ANGLES.md`. **The method moved; the reason for the exception did
not.** What stayed behind is the project-specific questions and the standing
riders, and every one of those is generated by a desk's own incident — so the
file still invites every writer, which is the condition the exception existed
for. **Restored and scoped in `OWNERS.md`:** any desk may ADD a question, a pair
or a rider with an incident behind it; nothing is removed without saying why; C1
owns the frame and the removals and is still the rule-14 owner. **Found because
Design wrote to the file under its own first-line rule while `OWNERS.md` said
they could not. The file and `OWNERS.md` disagreed in writing for four days.**

**2. Q63.5C SPLITS. THE MOUNT JOIN IS PERFECT AND THE PRICE JOIN DOES NOT
EXIST.** Build measured both halves: 19,579 of 19,579 stock components resolve
through `LOADOUT_SHIPS[].slots[]` into `LOADOUT_PARTS[]` — zero unresolved, 318
of 318 ships carrying slot lists, 32 component types with stock fittings. **And
not one of the 3,292 parts carries a price or shop field of any kind.** The old
entry said "component filtering has no join", which was a true statement about
PRICE applied to the word COMPONENTS. *Mount* filtering is buildable and is
folded into the 35-row lookup job — it can answer for 219 of 253 cards and would
be silent about the same 34 rows that break T-003, P20, P28 and P30. *Price*
filtering becomes its own entry and is a Research acquisition question, not a
queue item.

**3. THE NO-EXPLAINING-AROUND-A-DEFECT RULE IS GENERAL, NOT ABOUT HELP TEXT.**
Written in `claude/DESIGN_the-help-control-2026-09-12.md` §4 as a rule for help
panels. Its first application outside help text is refusing a component filter
that declares its own coverage — *"filters on 219 of 253 ships"*. **A caveat that
makes a listed defect tolerable is a permanent apology for something already
ordered fixed.** The rule now covers filter caveats, empty-state copy, tooltips
and legends equally.

**4. A CONFIDENCE NUMBER MUST BE INDEPENDENCE-WEIGHTED OR MUST NOT EXIST.**
`citizen-collector/merge.go` ships
`func (o Observation) Confidence() int { return len(o.Contributors) }` in a file
whose own header argues against picking winners. **Contributors are not
independent** — several people running the same exporter against the same UI
share one failure mode, so the number reads three and the evidence is one.
**Material for whoever designs the merge half of the collector rebuild**, whose
design is Sleven's and open; not a patch to a program being replaced.

**5. FIVE OF THE SIX RESEARCH ITEMS ARE CLOSED AND EVERY ANSWER CHANGED ITS OWN
QUESTION.** CIC read RSI's own store and patch-notes material today and closed items 1, 3
and 4; item 5 closed on Build's measurement; item 6 was Echo's. **Only the keybinds page
remains.**

    item 5   "is component filtering possible" -> it is TWO questions with
             opposite answers
    item 4   the roles AND the list of ships with none -> 253 of 253, and the
             SECOND LIST CAME BACK EMPTY, which deleted a design branch
    item 1   cosmetic or functional for eight -> seven answered, and the two
             that did not fit exposed a gap in HIS TEST, not in the evidence
    item 3   removal was the default -> the evidence REVERSED it
    item 6   corrected the premise the help design rested on

**Five for five. The standing instruction that follows: bring back the split, the empty
set or the reversal when you find one. An answer that fits its question exactly is the
least likely outcome on this board.**

**And joining CIC's answer to our own source found a defect nobody was looking for.** The
old front page's PTU link has a staleness gate whose own comment says *"each new PTU BUILD
gets a NEW thread"* while the code compares major.minor only — **it records the build and
never compares it**, so today it serves build 12368639's notes while the live thread is
4.10.1 build 12625701. **Not repaired — that page is being replaced — and written into
Q55.C-015 so the replacement cannot inherit it.**

**THE SHAPE UNDER FOUR OF THE FIVE IS THE SAME ONE AGAIN: A RULE KEYED TO A
PROXY.** "The method moved" for "the reason moved"; "component filtering" for
"the component-to-price join"; contributor count for independence; and major.minor for
"this is the current PTU thread". That is eight instances in a fortnight, with the date
prefix for identity, `!e.IsDir()` for "is protected", `s.hull` for "has a ship page" and
a character count for "truncates".

**It has stopped being worth recording as a coincidence.** Eight instances, every one
found by a different desk on a different surface, and in six of them **the correct rule
was written down in a comment, a docstring or a header beside the code that implements a
weaker one.** The proxy is not what a desk reaches for when it does not know the rule —
**it is what a desk writes down when it does know it.**

**And one pair added to `design/ANGLES.md`'s list:** a file's own header is a
claim about its behaviour and nothing checks it. Three live examples —
`merge.go`, `checks/_verify_correspondence.py` (its docstring says *ANSWERED with
nothing under an ANSWERS: line*, the code requires `ANSWERS:` for everything in
`answered/`), and the help design's own withdrawn premise.

---

## 2026-09-12, SECOND PASS — THE TRAY REFILLED ELEVEN TIMES AND HERE IS WHAT IT CHANGED

**SIX OF SIX RESEARCH ITEMS ARE NOW CLOSED.** The keybinds page is **CURRENT for
4.10.0-hotfix by content** though built on the 4.9 profile: 1,028 of 1,028 actions
identical, 50 of 50 actionmaps, zero bindings added or removed, and the entire difference
is a malformed line in CIG's own file plus a trailing newline. **Build used a byte diff
rather than an action count, which is what makes it an answer** — a matching action count
says nothing about a binding moving inside them.

**Q55.P15 RULED: STAMP, THEN LINK, THEN PRODUCER.** The stamp blocks the link; the producer
does not. **What the stamp buys is the failure MODE** — unstamped, the next patch that
moves a binding makes the page silently wrong; stamped, it makes the page visibly old. **A
page that can go visibly stale is linkable.** Four keybinds paths claimed by C1 in
`OWNERS.md`, and the finding that travels with them: **nothing in the repository produces
`keybinds_site.json`** — a hand-made link in the chain that cannot be re-run.

**THE QUANTUM SENTINEL, AND THE SILENT SCOPE SWITCH UNDER IT.** All 59 quantum drives carry
`qt: 340282300000000014807478566912` — float32 max, a "no limit" sentinel imported as a
measurement. **Repaired AT IMPORT, and the repaired value is ABSENT, not large** — a clamp
would be this desk inventing a range CIG never published. **And the missile rack is
innocent: `renderStats()` returns CIG's figure only while the build is stock, so quantum
range breaks when you leave stock, not when you fit a rack.** The bigger half: **the same
switch governs sustained DPS and effective HP, which do not go absurd — they quietly change
what they MEASURE and stay plausible.** A number that goes absurd gets reported; one that
changes scope while looking right gets quoted. **The card states which number it is showing,
always, and the badge to do it already exists — this is a wiring defect, not a build.**

**THREE MAIL REPAIRS ORDERED, AND THEY ARE NOT FROZEN.** His ruling: defects in the running
mail service are not frozen; the freeze stops the wake system. **The `From:` parenthetical;
the returned answer that cannot be cleared from the sender's tray; and a close with no
disposition marker REFUSED AT FILING TIME rather than caught by a sweep.** That last is the
ruling and it is none of the three options Build offered — all three left the catch at sweep
time, where the cost is a blocked deploy hours later instead of a bounce and a one-line fix.
**Not the owner typing a marker (that puts a formatting step on him) and not the control
reading his signed close (a format-sniffing rule is how a check starts passing what it
should read — and Build set out to report one closing style and found two in the same
pass).**

**A FILE CITED IN FOUR DOCUMENTS DOES NOT EXIST, AND IT BLOCKED A JOB.**
`claude/CIC_rsi-official-ship-roles-2026-09-12.md` — absent 31 minutes after the memo
announcing it, against a measured bridge lag of ninety seconds. **Build refused to join the
six roles quoted inline and call it the answer.** Second instance of
`claude/FINDING_the-documents-are-not-on-disk-and-the-memos-announcing-them-are-2026-09-10.md`
and the first to cost work. Routed to Research with the first question being **whether that
desk can write into the repository at all** — if it cannot, asking again produces the same
nothing.

**THE PACKAGE SHAPE IS THREE RELATIONSHIPS, NOT TWO.** Edition-or-paint folds; a true
variant keeps its own card; a package gets a "Packages containing this ship" section with
exact contents and links. **Every ship in the package carries the line. No price, ever. No
label saying "buy" or "available".** And the correction that changes the build order: **the
RSI link is NOT the identity** — a local record with a verification status, the link hanging
off it as dated evidence. **24 rows carry no store link and they are disproportionately the
edition rows the design depends on**, so link-as-identity would have been built and then
found unbuildable on exactly the rows it was for.

**63 OF 179 PURCHASABLE SHIPS CARRY A PRICE PER DEALER.** The other 116 show one in-game
price beside a list of shops. **That is the defect the project exists to fix, 116 rows of
it, and it is now the largest honesty defect on the board by row count.**

**THE RULES-FILE SPLIT IS PROPOSED, NOTHING EDITED.**
`claude/PROPOSAL_the-rules-file-split-2026-09-12.md`. **The test cuts no rules — it
separates rules from their EVIDENCE.** 624 lines is about 370 lines of rule and 230-250 of
incident. **The core comes out at 26 rules in ~95 lines, no number moved.** And the file's
first line — *"Read the Hard Rules below"* — points at a block that does not contain rules
24, 25 and 26, which are the three about dealing with Sleven.

**ECHO CANNOT BE THE DESIGN DESK AND THE BLIND REVIEWER.** Two letters two hours apart are
one decision. **An outside design desk can tell you what to build and cannot tell you
whether you already built it** — the glossary, `merge.go`, `editions.json`, the 318 ships'
dimensions and the 924 paint records are all things we already had while designing them
again. **So the clerk is not overhead; it is the half of the desk that cannot move.**

**AND THE PATTERN UNDER FIVE MEASUREMENT ERRORS THIS WEEK, IN HIS WORDS:** *the front page's
data is a narrow projection of a much richer dataset, and we keep reading the projection and
calling it the project.* The width gap, the paint gap, 35-versus-34 hull-less rows, P20 five
times too big, Q58's character count. **Now its own rider in `design/ANGLES.md`, because the
general form had been on that list four days and stopped none of them.**

---

*C1, updated 2026-09-12 second pass - six of six research items closed, the quantum
sentinel, the mail repairs, and the rules-file split proposed.
Previously updated 2026-09-12 - the architecture tray worked to empty: the ANGLES
restoration, the Q63.5C split, and the C3/Design rows merged.
Previously updated 2026-09-11 - step A is in and proved, the date rule, and the export
boundary inverted to an allow-list.
Previously updated 2026-09-10 - the doorbell, the brakes and the wake rules.
Previously updated 2026-09-05 - the paint ceiling is two ships, and the source is the game install.
Previously updated 2026-09-04 - models, UV maps and the paint work.
Previously updated 2026-08-30 morning. Split out of a 13,571-word document that had to be read in full
to be trusted. If this one ever needs that again, it has failed.*
