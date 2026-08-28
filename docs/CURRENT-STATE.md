# Citizen Compass — Current State

**Authoritative as of 2026-08-27 evening.** Everything in this file is true now.
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
`inbox/`.

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
    overlay      167 hulls / 1,720 ports
    ship page    245 classes with every marker on CIG coordinates
                 20 with none, each for a written reason

The 20 are: the ARGO ATLS family (a **power suit**, filed under
`Characters\PowerSuit`), four GRIN mining vehicles (no exterior mount at all),
three Cyclone variants, the Javelin (two paths of equal evidence, one under
`dmg`), the Glaive and Scythe (**asymmetric ships, not a bug**), the MOTH and the
Starfarer Gemini. See
`docs/FINDING_the-hull-rule-was-blind-to-the-ships-cig-does-not-name-a-folder-for-2026-08-27.md`.

**How a variant finds its hull:** CIG's own record says so —
`Parts[0].Name` is the hull the ship is built on. `ANVL_C8_Pisces -> ANVL_Pisces`.
Exact equality. **This replaced a name-prefix rule; do not reintroduce one.**

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
- **The Glaive and the Scythe** need a frame proof that does not assume the ship
  is symmetrical. Do not widen the mirror tolerance to get there.

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

*C1, 2026-08-27. Split out of a 13,571-word document that had to be read in full
to be trusted. If this one ever needs that again, it has failed.*
