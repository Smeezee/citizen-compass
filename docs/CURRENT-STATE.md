# Citizen Compass — Current State

**Authoritative as of 2026-08-29 midday.** Everything in this file is true now.
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

Free, non-commercial fan-made Star Citizen reference.
*"Know where to buy, before you fly."* CC BY-NC 4.0, credit "Built by Sleven".
Operates under CIG's Fan Kit Agreement — **non-commercial only**, no ads,
donations or paid access while Fan Kit assets are in use.

    live      citizencompass.netlify.app        hand-deployed on Netlify
    testing   citizencompasstesting.citizencompass-contact.workers.dev
              Cloudflare Workers, one command, PASSWORD-GATED
    repo      github.com/Smeezee/citizen-compass
    local     C:\Users\david\citizen-compass

**`LIVE.md` at the repo root is the only authority on what is actually public.**
Nothing enters it on the strength of a build, a passing check, or a deploy to
testing — only what a stranger with no password can load, verified by loading it.
As of 2026-08-27 the public site is **v0.3.9, 254 ships, stamped
"Compiled/updated: 2026-07-30"**. The testing site is far ahead of it.

**Going live is OFF the queue** until Sleven raises it himself. He has said
plainly the site is not ready. Do not push it, do not build a case for it, do not
put it back on a list.

---

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
- **C1** — Cowork. Writes orders into `inbox/`, owns `NEXT.md` and `LIVE.md`,
  owns the loadout page source and the hardpoint pipeline. The only Cowork
  session authorised to write to the repository.
- **C3** — Cowork research. Reads and verifies source data, produces findings and
  work orders. May write derived data and docs; not git, not the database, not
  Code's build tooling.
- **CIC** — Claude in Chrome. Reads the open web. **Its output is a claim until
  someone verifies it locally.**
- **Code** — Claude Code, on the Windows machine. Executes. Owns
  `testing/_src/build_deploy.py` and the check suite.

**A work order that exists in the claude.ai project but not in the repo has not
been delivered.** Code reads the repo. Anything Code must act on goes in
`inbox/`. **C3 reads the project**, so an order for C3 goes in both.

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

1. **Nothing commits, pushes, or deploys to the live site without Sleven's
   explicit go-ahead.** Never `git add -A`.
2. **NO FUZZY MATCHING**, anywhere, in anything. Exact equality or refuse.
3. **Rule 12 — every check needs a control that could have failed it.** A check
   that cannot fail is not a check.
4. **Rule 14 — one writer per artifact.** When a second writer is possible, make
   it impossible rather than discouraged.
5. **Rule 16 — a check must draw its truth from a different source than the
   thing it checks**, or be labelled UNPROVEN.
6. **Every data row carries `last_verified_patch`** and the front end flags
   unverified data.
7. **Ambiguity is refused, not resolved by picking.** Two things claiming one
   name are both dropped and both named.
8. **Read the clock from the machine** (UTC−5), never estimate it.
9. Rights questions are CLOSED (`RULING_rights-questions-are-settled-2026-08-14`).
   Credentials are CLOSED (`RULING_credentials-are-rotated-2026-08-15`). Do not
   re-raise either.
10. Screenshots are internal working material. **A frame may contain a name.
    Nothing derived from that frame ever may.**
11. Do not fetch anything under `/media/` on robertsspaceindustries.com — the
    single rule in their robots.txt.

---

## What is built and working

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

**Armour and shields.** Armour resolves through each ship's own `Loadout`;
**eight** distinct damage-multiplier profiles. **Every shield in the game is
identical** — 73 items, one Absorption profile. Energy absorption is fixed at
1.00; physical is a **range, 0 to 0.45**, and what moves it along that range is
not established. Do not publish 45% as a value.

**Patch data: the 4.10 snapshot is on the machine and in use**
(`snapshots/20260827T225641Z`, 318 ship classes). The hardpoint placement scales
against 4.10 lengths as of 2026-08-27. Weapon findings written before that date
are 4.9 and say so.

---

## What is open

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

- Shop and price data has never been verified against the game.

**Sleven's alone**

- Whether and when the site goes live.
- Every legal, Fan Kit and trademark question.

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

*C1, updated 2026-08-29 midday. Split out of a 13,571-word document that had to be read in full
to be trusted. If this one ever needs that again, it has failed.*
