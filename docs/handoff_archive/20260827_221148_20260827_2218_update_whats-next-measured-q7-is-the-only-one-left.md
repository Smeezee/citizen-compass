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
