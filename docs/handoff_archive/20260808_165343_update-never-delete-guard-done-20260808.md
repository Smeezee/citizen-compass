# Update — never-delete guard is in and proven; record gap closed (2026-08-08)

Two things: the preservation rule from
`WORKORDER_preservation-model-and-never-delete-rule.md` §3 is implemented, and
this closes a ~3.5 hour gap in the handoff record.

## The rule is enforced by construction

`app/preservation.py` blocks row removal on 15 preserved tables at **two**
layers, because blocking one is worth nothing:

- Core/SQL — `DELETE`, `DELETE ... WHERE`, `TRUNCATE`, including raw text and
  lowercase
- ORM — `session.delete()` and cascade deletes at flush

A wholesale "replace" is DELETE-then-INSERT, so blocking DELETE catches the
loader shape §3 warns about.

**Installed at engine creation in `app/database.py`, not in each importer.**
Wiring it per-importer works right up until somebody writes a new one. Every
consumer of that engine now inherits it, including code that does not know the
rule exists. `import_ship_components.py` also installs it explicitly, so the
intent is visible at the point of use.

`pipeline_check_results` is deliberately NOT preserved — it is an append-only
observation log that is meant to be flushed and archived, and guarding it would
break `checks_flush_fallback.py`.

## Rule 12 — 15 assertions, every case run twice

`checks/_verify_never_delete_guard.py`. The guard's claim is "a preserved row
cannot be removed", so a refused delete proves nothing on its own — it might
have failed for an unrelated reason. Every case runs **with the guard and
without it**:

```
guard installed  DELETE / DELETE WHERE / TRUNCATE / lowercase  -> all refused, row survives
guard removed    the same DELETE                               -> row GONE
```

That second line is the proof. Plus: a non-preserved table still deletes
normally (the guard is targeted, not a blanket ban), **DDL is untouched** so
alembic and the e2e harness still work, and `app.database.engine` is confirmed
guarded on import — checked by behaviour, because an import that silently
no-ops looks identical to one that worked.

Runs against TEMP tables shadowing the real ones; `public.ships` row count
asserted unchanged throughout. No destructive statement reached a real table.

## Two defects found in my own guard while proving it

**1. Half a guard, installed silently.** `before_flush` is a Session event and
does not exist on an Engine. The first version registered it on the target and
swallowed the failure with a bare `except`, so passing an Engine installed the
Core half only — the ORM path stayed open while the code read as covered. The
ORM test caught it. It now binds to the Session class explicitly.

**2. A test helper that disarmed production.** `remove_never_delete_guard()`
removed every listener process-wide. The verification called it to disarm its
own throwaway engine and silently disarmed `app.database.engine` too — a test
that turns off the live guard is worse than the defect the guard prevents. It
is now target-scoped.

Both are the same shape as the six silent-success cases already on record, and
neither would have shown up without the negative control.

## What this does NOT do

It makes the loss impossible; it does not yet make the absence **visible**.
`status`, `last_seen_patch`, `first_seen_patch`, `successor_id`,
`removal_note` and `evidence_tier` (§4) are a schema migration against the real
database — that needs a verified backup under hard rule 4 and an explicit
go-ahead, so it is not done here.

That ordering is deliberate: **a row that is still there can be marked later; a
row that is gone cannot be recovered.** The deadline was on the deletion half.

So §3 acceptance is met in part — the row survives — and the `status=retired`
half waits on the migration.

## Record gap this closes

`LATEST_HANDOFF.md`'s newest entry was **13:04** while nine documents were
created between **14:18 and 16:37** — holoviewer, fankit, hologram,
preservation, importer-audit and commlink prompts and findings, none of them
mentioned in it.

Not a pipeline fault: the watcher is healthy (PID 8856, update #260 at 16:38)
and correctly classified those as docs rather than updates. No update was
filed. Recording it here so the next session does not read 13:04 as current, as
I nearly did.

## State

- Nothing committed or pushed — no go-ahead given for either work order.
- Working tree: guard + verification are new; `citizen-collector/` untouched
  per the sole-writer note.
- Auditor after the change: 14 findings, **0 DEFECT**.
- Queued next: `docs/prompt-code-holoviewer-all-ships.md`.
