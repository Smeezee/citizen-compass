# UPDATE — Ship Items schema + importer shipped, viewer generalization scoped (2026-07-30, overnight)

Resumed from the 2026-07-29 handoff's three open items. Sleven was asleep; proceeded on
judgment per his standing instruction, did not decide the one item he flagged as his call.

## 1. Postgres schema + importer for weapons/missiles/turrets (PRIMARY — done, locally verified)

Built the "Ship Items" domain locked in `docs/ARCHITECTURE_DECISIONS.md` (Class Table
Inheritance): `component_types` lookup table + `components` base table + 5 typed detail
tables (`weapon_details`, `missile_details`, `missile_rack_details`, `gimbal_mount_details`,
`turret_details`), all wired to the existing `VerifiableMixin` provenance pattern
(verification_source/confidence).

- `app/models.py` — new `ComponentType`, `Component`, `WeaponDetail`, `MissileDetail`,
  `MissileRackDetail`, `GimbalMountDetail`, `TurretDetail` classes.
- `alembic/versions/219446ebce6a_*.py` — migration creating all 6 new tables + indexes,
  seeding `component_types` with the 5 categories.
- `import_ship_components.py` — hand-curated importer (per the "2-3 real importers before
  generalizing" staged-pipeline decision), populating 8 real Arrow components sourced from
  `data-layer/raw/arrow/arrow_api_raw.json`'s actual port tree, cross-checked against
  `docs/HARDPOINT_MOUNT_TYPES.md`. Upserts on `class_name`, idempotent on re-run.
- Commit: `bf22494`.

**Honesty note on verification:** all of this was tested against a scratch PostgreSQL
instance in my own cloud sandbox (upgrade/downgrade/re-upgrade cycle, `alembic check` clean,
importer dry-run + real + re-run, full `app.main` import with routers still boots clean). It
has **NOT** been run against the real project database — this session's tools can't reach
`localhost:5432` on your machine from the cloud container, and the device bridge has no
network access at all. First real run against your actual dev DB is the first thing to do
when you're back: `alembic upgrade head` then `python import_ship_components.py`. Read the
importer's inline notes before trusting it blind — 3 manufacturer prefixes (GATS, FSKI,
TALN) and a couple of stat fields were deliberately left `None` because I couldn't confidently
identify them, not because they don't matter.

## 2. Viewer pattern generalization (SECONDARY — scoped down, real blocker found)

Checked `constellation-aquila` and `gladius` before touching anything: neither has a
`hardpoints.json`, and `data-layer/raw/` only has `arrow` and `misc` — there is no raw
port-tree data for either ship. Wiring the Arrow's hover/rack-selector pattern into them
tonight would mean inventing hardpoint positions, which is exactly the kind of guess this
project's evidence standard rules out. Did not do that.

What I did instead: extracted the reusable engine (scene setup, hover/click raycasting,
rack-config popup, missile-total calculator) out of `arrow/index.html` into
`tests/testing-site/shared/hardpoint-viewer.js` (`createHardpointViewer()`, parameterized).
Commit: `64f2ee6`.

**Deliberately left undone, for good reason:** did NOT wire this into `arrow/index.html`
itself, and did NOT touch that file at all. This session has no way to render WebGL or take
a screenshot to visually confirm the swap is behaviorally identical — the working Arrow demo
was judged not worth risking on a blind refactor. `arrow/index.html` is untouched and still
the known-good reference.

**Real next step for this task** (not done tonight, needs you or a session with browser
verification): (a) wire the shared module into `arrow/index.html`, look at it in a browser,
confirm parity; (b) pull real port-tree data for constellation-aquila and gladius the same
way it was done for the Arrow (their raw API pull → `data-layer/raw/<ship>/`), then the
shared engine can actually be used on them.

## 3. ARCHITECTURE_DEEP_REVIEW.md scope question

Left exactly as flagged, per explicit instruction. Not touched, not decided.

## Also worth knowing

- 9 commits are now sitting local-only, ahead of `origin/main` (was 8, +1 tonight). Not
  pushed — wasn't asked to, flagging again since it's been sitting a while.
- Could not confirm whether `inbox_watcher.exe` is currently running from this session (no
  Windows process/task-scheduler visibility from the device bridge) — if it's down, this
  update file will just sit in `inbox/` until it's restarted; check `logs/inbox_watcher.log`
  for the last "Watcher started" line when you're back.
