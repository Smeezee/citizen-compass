# UPDATE — Overnight queue complete: real-DB status, CRUD API, auditor, E2E harness, viewer wired (2026-07-30, continued)

Full run of the approved overnight queue (Postgres real-DB proof, generic CRUD API,
data-integrity auditor, E2E test harness, Aquila/Gladius investigation), plus the two
mid-run corrections (real-DB downgrade restricted to disposable clones; don't rebuild
the already-existing viewer scaffolding). Addendum batch #2 (Cutlass Black fix + broader
auditor/checker rollout) was explicitly told to wait until this reported done here — it
has NOT been started yet, see "Next" at the bottom.

## Step 1 — Real database proof: BLOCKED, confirmed with a real network test, not skipped

The queue's premise was "`.env` has `DATABASE_URL` set, so you have direct access this
time." Tested it directly before touching anything: a raw TCP connect from the device
bridge to `127.0.0.1:5432` returned `Connection refused`, and a connect to `8.8.8.8:53`
(open internet) returned `Network is unreachable`. This is the same platform limitation
as last session, now re-confirmed with an actual test rather than assumed. Neither the
device bridge nor this cloud sandbox can reach your real local Postgres or the internet
at your machine at all.

**Consequence:** `alembic upgrade head` / `import_ship_components.py` have still never
been run against your real `citizen_compass` database. Everything below was validated
against a scratch Postgres in my own cloud sandbox (as last session), never your real DB.

**Your exact next step to close this out** (2 commands, once you're at a terminal with
real DB access):
```
alembic upgrade head
python import_ship_components.py
```
Take a backup first since you now have real access and I don't:
```
pg_dump -Fc citizen_compass > citizen_compass_backup_$(date +%Y%m%d).dump
```
Restore procedure if ever needed: `pg_restore -d citizen_compass --clean citizen_compass_backup_<date>.dump`
(only ever needed if something goes wrong - the migration is additive, it doesn't touch
existing tables).

## Step 2 — Generic CRUD/router-factory: DONE, real code committed, tested in scratch

Per `docs/ARCHITECTURE_DECISIONS.md` section 3 (LOCKED). New files:
- `app/routers/component_factory.py` - owns pagination, deterministic ordering,
  the 4 universal filters (manufacturer/size/grade/confidence), the `Page` envelope,
  id-or-class_name detail lookup with a real 404.
- `app/routers/weapons.py`, `missiles.py`, `turrets.py` - thin per-category wrappers
  with their own real, named, documented FastAPI query params for category-specific
  filters (damage_type/fire_mode, guidance_type, manned).
- `app/schemas.py` - added `Page[T]`, `ComponentBaseOut`, `WeaponOut`, `MissileOut`,
  `TurretOut` (1:1 mirror of actual model columns, no speculative fields).
- `app/main.py` - wired the 3 new routers in.

Endpoints live: `GET/{identifier} for /api/v1/weapons`, `/api/v1/missiles`, `/api/v1/turrets`.

**Real bug found by actually running it, not just import-checking:** `Component` had no
`verified_patch` relationship at all (only the raw `last_verified_patch` FK column) -
`Ship` has the equivalent relationship, this one was just missing. Crashed every
serializer the first time they ran against real data. Fixed in `app/models.py`, with a
regression test.

**Deliberately NOT done:** did not retrofit the new `Page`/pagination envelope onto the
existing `/api/v1/ships`, `/api/v1/dealers`, `/api/v1/manufacturers` endpoints, even
though the architecture doc mentions eventually doing so - that's already-live behavior
outside tonight's explicit scope. **Flagging this for your call**, not deciding it
myself: do you want those three retrofitted to the same envelope, and if so, on what
timeline (it's a breaking response-shape change for anything already consuming them)?

**Tests:** `tests/test_component_routers.py` (17 tests: envelope shape, category
isolation, deterministic ordering, pagination bounds, all filter types, 404s including
cross-category and huge-integer identifiers, 422 validation, existing endpoints
unaffected, OpenAPI). All passing against scratch Postgres.

## Step 3 — Data-integrity auditor: DONE, real code committed, tested in scratch

`audit_ship_components.py`. Findings-only (never repairs data), per
`docs/ARCHITECTURE_DECISIONS.md` section 4 (LOCKED). Checks source-vs-processed-vs-DB
coverage, relational integrity (broken FKs, cross-category detail mismatches, missing
detail rows, duplicate natural keys, invalid confidence/size values), and re-runs the
importer twice to catch drift. Every finding is exactly one of `DEFECT` / `WARNING` /
`LIMITATION` / `PASS`. Outputs both JSON and a human-readable .txt to `logs/` (gitignored
- only the script is committed).

**Real result against the actual imported Arrow data:** 0 DEFECTs, 5 LIMITATIONs (all
expected: unresolved manufacturer prefixes GATS/FSKI/TALN, partial port-tree coverage -
8 of 53 port entries imported so far, by design per the staged-pipeline decision), 2
PASSes.

**Tests:** `tests/test_audit_ship_components.py` - verifies the auditor actually flags
an injected cross-category-detail-mismatch and a missing-detail-row as DEFECTs, and
does NOT flag a well-formed component. (A findings-only tool that never finds anything
real is worse than useless - it looks like a safety net that isn't one.)

## Step 4 — E2E test harness: DONE, real code committed, passes clean

`run_e2e_test.py`. Creates its own throwaway Postgres database (name derived from
whatever `DATABASE_URL` is configured, credentials never hardcoded - so this can't
silently target the wrong server when it's eventually run in your real environment),
applies all migrations, seeds a small deterministic 5-category fixture (independent of
the real Arrow data), runs the auditor, exercises 8 representative endpoint calls via
FastAPI's TestClient, re-seeds to prove idempotency, downgrades to base and back to head
to prove reversibility, runs `alembic check`, drops the database. **Full run passed
clean this session.**

This is also where tonight's addendum #1 correction now lives structurally: destructive
migration testing (downgrade/re-upgrade) only ever happens against this disposable
per-run database going forward - never the real one, and it never did this session
anyway since the real DB was unreachable.

`requirements-dev.txt` added (pytest, httpx) - separate from `requirements.txt` so
Railway's production install doesn't pull test tooling.

## Step 5 — Viewer parity + Aquila/Gladius: DONE (parity), investigated + honestly blocked (data)

**Viewer parity (per the mid-run addendum):** confirmed `64f2ee6`'s shared module
(`tests/testing-site/shared/hardpoint-viewer.js`) already existed - did not rebuild it.
Verified real behavioral parity before wiring it in, using headless Chromium
(Playwright, available in my sandbox) with mouse coordinates computed from the actual
camera projection matrix - a genuine simulated user interaction, not a code-reading
guess. Compared hover-highlight, click-to-open popup, rack-configuration swap,
missile-total recompute, and the turret/gun popup path field-by-field between the
original inline-script Arrow page and a copy wired to the shared module.

**This caught 2 real regressions** from the original extraction: two hardcoded
provenance-note strings had been reworded - one silently dropped
"(arrow_api_raw.json)", the other dropped a trailing sentence about buy-location data.
Fixed both; while fixing the first, also generalized it (`rackSourceLabel` option
instead of a hardcoded Arrow filename - a "shared" module hardcoding one ship's
filename would have been wrong for the next ship). Re-ran the full comparison after the
fix: **PARITY CONFIRMED**, zero differences, zero console errors either page. Wired the
shared module into `arrow/index.html` for real (commit `367ea74`) - HTML/CSS unchanged,
only the ~230-line inline scene script replaced with a ~20-line call into the engine.

**Aquila/Gladius real data:** confirmed (again) neither ship has any raw port-tree data.
Investigated the source: `arrow_api_raw.json`'s own embedded metadata reveals exactly
where Arrow's data came from - `api.star-citizen.wiki`, resource type "vehicle", the
open-source `StarCitizenWiki/API` project (confirmed via `WebSearch`, which works fine
in this session). The URL pattern is `https://api.star-citizen.wiki/api/vehicles/{slug}`
(Arrow's slug: `anvl-arrow`) - likely slugs for the other two are `aegs-gladius` and
something like `crus-constellation-aquila`, not yet confirmed.

**Real, precise blocker (not a data-sourcing question, a tool-availability one):**
`WebFetch` itself requires a live per-request approval prompt in this session that
nobody was there to answer - tried 3 times against 2 different domains
(`api.star-citizen.wiki` and `starcitizen.tools`), all timed out identically. This isn't
domain-specific and isn't something more retries would fix. **This needs you present**:
either (a) approve the `WebFetch` prompt once when you're at the session live so I can
pull both ships' data the same way Arrow's was pulled, or (b) you pull
`https://api.star-citizen.wiki/api/vehicles/aegs-gladius` and the Aquila's equivalent
yourself (browser or curl) and drop the JSON into `data-layer/raw/<ship>/`, same
convention as Arrow - either path, no data was invented in the meantime.

## Commits this run (all local, none pushed)

```
367ea74 Wire shared hardpoint-viewer engine into Arrow, verified byte-for-byte
2515fc8 Add Ship Items data-integrity auditor + isolated E2E test harness
3fcd75f Add generic CRUD router factory for Ship Items (weapons/missiles/turrets)
```
(on top of the 11 commits already local from earlier tonight). **14 commits ahead of
`origin/main` now, still all local** - flagging again since it's been sitting a while,
not something I'll push without you saying so.

`git status`: clean working tree.

One cosmetic note: the router-factory commit's message has a small gap where a
backtick-quoted phrase got eaten by an unescaped-backtick shell quoting mistake on my
end (bash command substitution) - message reads "Component had no relationship at all"
instead of "no `verified_patch` relationship". Content is otherwise intact and not
misleading; didn't amend it since amending isn't something I do without you asking.

## Test results summary

23 pytest tests, all passing (17 router tests + 3 auditor tests + 3 schema/importer
regression tests) - against scratch Postgres, not your real DB (see Step 1). Full
`run_e2e_test.py` pass: clean. Auditor run against real imported Arrow data: 0 defects.

## Decisions that need you

1. Should `/api/v1/ships`, `/dealers`, `/manufacturers` get retrofitted to the new
   `Page` envelope (the architecture doc mentions it eventually)? Left alone tonight,
   your call on timing since it's a breaking shape change.
2. `ARCHITECTURE_DEEP_REVIEW.md` scope question - still untouched, exactly as flagged,
   not decided by me.
3. Aquila/Gladius real data - needs you present for one `WebFetch` approval, or a
   manual pull, per Step 5 above.

## Next / addendum #2 status

Addendum #2 (Cutlass Black slug/label/turret-size/rack-data fix + broader
auditor/checker rollout across data-integrity, ops-health, security, code-quality,
external-reachability categories) was received mid-run with explicit instructions to
**hold until this queue reported done here** - which is now. **Not started yet.** Will
begin it next, working in the same small-validated-stages/git-lock-workaround pattern,
starting with the Cutlass Black fix (needs the same real-source-data verification
approach as Arrow for the turret-size question - same `WebFetch` limitation above may
apply there too, will report honestly if so rather than guess S5 from the unverified
note).
