# Citizen Compass

## Guiding architecture document

**[docs/PHASE2_VISION.md](docs/PHASE2_VISION.md) is the authoritative long-term vision and architecture specification for this project.** All Phase 2+ work — automated data sync, the interactive ship/paint/equipment viewers, data modeling, automation pipelines — should stay consistent with it. Read it before proposing significant new architecture, data structures, or features. Do not deviate from its guiding principles (build in stages, architecture before features, simplicity first, document everything) unless the user explicitly says otherwise for a specific task.

## What's here

This repo currently contains two distinct systems sharing one folder:

- **The production app** (live): FastAPI + PostgreSQL backend (`app/`, `alembic/`), static frontend (`static/`), deployed to Railway + Netlify. See `README.md`.
- **A desktop automation / "AI brain" system** (in development, per Phase 2 vision above): `inbox_watcher.py` (auto-files dropped data via a Task Scheduler background process), `image_handling.py` (OCR pipeline with dual-pass cross-checking), `generate_handoff.py` (maintains `LATEST_HANDOFF.md`), `ccpp.py` (project health-scoring), `hardpoint_organizer.py` / `build_ship_component_schema.py` (ship hardpoint/component data schema), `data-layer/` (ship data).

`LATEST_HANDOFF.md` at the project root is auto-regenerated and reflects current project state — check it for a fresh snapshot. `docs/handoff_archive/` holds dated session handoff records.

## Standing rule: keep LATEST_HANDOFF.md current, always

After completing any meaningful step or phase of work, and any time you stop
for any reason — a denied permission, waiting on a decision, finishing one
section of a multi-phase task, or genuinely being idle with nothing left to
do — drop a small `.md` file into `inbox/` (filename or heading containing
"update") summarizing what just happened: what was completed, what's
blocked and why, or what you're waiting on. The watcher picks this up
automatically and appends it to `LATEST_HANDOFF.md`'s Recent Updates
section.

For multi-phase work you have permission to run through in order, still
stop after each individual section to log an update — don't wait until the
entire multi-phase task is done to report anything. The goal: at any
moment, `LATEST_HANDOFF.md` reflects genuinely current status, never more
than one completed step behind, so it can be checked without wondering if
it's stale.

## Known caveats worth knowing before touching related code

- `inbox_watcher.py`'s `log()` (and `generate_handoff.py`'s) can crash silently on Unicode symbols (`✓`, `✗`, `⚠`) when running under `pythonw.exe` with no console attached — the `print()` call fails before the file write, and the exception isn't fully guarded. Not yet fixed as of this writing.
- `data-layer*` folders exist in both a flat, non-standard naming (`data-layerrawhardpoints/`, etc.) and the proper nested structure (`data-layer/raw/...`) that most scripts expect — not yet reconciled.
