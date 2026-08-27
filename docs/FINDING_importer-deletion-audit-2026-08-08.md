# FINDING — JOB 1. No importer deletes anything. The risk is the opposite of the one we specced for, and there is a hard blocker in the schema nobody has hit yet.

    from      C3 (Cowork), 2026-08-08
    for       C1 + Sleven (→ Code)
    ask       C1: "Find every path that can remove or overwrite a row, and report
              them by name... If you find nothing, say so and say what you searched for."
    method    Staged 25 source files into a workspace and searched there — the device
              mount is too slow for recursive grep and timed out twice at 45 s. Read the
              write paths directly rather than pattern-matching alone. Every pattern used
              was fired against a purpose-built decoy file first (§6).

---

## 0. Headline

**Nothing in the importers deletes a row. The Aurora Mk I will survive the next patch
import.** That is the good news and it is real, not assumed — the write paths were read,
not just grepped.

**But the failure mode we specced against was the wrong one.** Because nothing deletes AND
nothing marks absence, the Aurora Mk I will survive **still flagged `purchasable`, still
stamped `last_verified_patch = 4.9`, and indistinguishable from a ship that still exists.**

For a reference site that is a bad outcome. For a *preservation* site it is the worst one:
**the row is not lost, it is quietly turned into a lie.** Losing a fact is recoverable from a
snapshot. Publishing "you can buy this" about a ship CIG has deleted is not — it is the exact
failure the project already worries about with `NotForRelease` content, pointed the other way
in time.

## 1. What can delete or overwrite — the complete list, by name

**Database: nothing. Zero destructive statements.**

    seed.py                     get_or_create() at line 323: query one_or_none(),
                                setattr defaults onto the existing row, else construct
                                and session.add(). No delete branch exists.
    import_ship_components.py   upsert_component() line ~250: mutate existing or
                                session.add(). upsert_detail() line ~272: five branches,
                                each `session.get(...) or NewRow(...)` then session.merge().
                                No delete branch exists.

Both are **merge-only by construction**, not by convention. There is no code path in either
that removes a row, and no raw SQL anywhere in the staged set that does.

**Filesystem: one real destructive rebuild, deliberate and currently correct.**

    scripts/split_craft_pages.py:180  fresh(d) -> shutil.rmtree(d); os.makedirs(d)
                                      called at line 210 for BP_OUT
    scripts/split_craft_pages.py:252  a second, inline rmtree for IT_OUT

Its own docstring states the intent: *"Rebuild the output directory from scratch so a removed
blueprint cannot leave a stale page behind. A file that survives because it was written once
is exactly the orphan problem this project keeps finding."*

**That reasoning is correct today and becomes wrong the day preservation ships.** These are
*rendered output* directories rebuilt from `blueprint_index.json`; no source data is touched,
so today the rebuild only prevents orphan pages. **But the moment retired items need pages,
this function deletes them** — the retired blueprint is gone from the source, so its page is
never rewritten, and `rmtree` has already removed the old one. It is not a bug now. It is a
scheduled one. **Name it in the preservation work rather than discovering it later.**

    checks_flush_fallback.py:287      shutil.rmtree(tmp, ignore_errors=True)

Test-harness cleanup on a temp directory. Not a data path. Listed for completeness because
"I found three rmtree calls and only explained two" is not an audit.

## 2. THE BLOCKER — the database will actively reject `status = 'retired'`

`app/models.py:19`:

    SHIP_STATUSES = ("purchasable", "pledge_only")

enforced at line 118 by a real CHECK constraint, `ck_ships_status_valid`.

**The preservation model I wrote cannot be implemented as written.** Postgres will refuse the
insert. `retired`, `replaced`, `renamed`, `never_released` and `unknown` are all rejected by
the constraint that exists today.

**This is good news in the shape it takes** — it fails loudly at write time rather than
silently accepting a value nothing understands. But it means the lifecycle work has a
mandatory first step that is not optional and not skippable: **a migration widening
`SHIP_STATUSES` and the CHECK constraint.** Any plan that assumes a status column can just be
set is wrong.

Worth noting the same class of constraint does not exist on `components` — only `ships`
carries a status at all. Paints, items and locations have **no status column of any kind**,
so the retired-paint pilot in the preservation work order needs its column created, not
widened.

## 3. Nothing anywhere computes absence

Searched for `retired`, `removed`, `absent`, `disappear`, `missing_from`, `not_in_patch`,
`no_longer` across every staged file. **There is no set-difference step in this project.**
Nothing compares "rows currently in the database" against "entities present in this patch"
and acts on the gap.

The two near-misses, both pointing the wrong way:

    audit_ship_components.py:147   missing_from_db = processed - db      (spec'd but NOT imported)
    audit_ship_components.py:341   removed = before.keys() - after.keys() (diff logging only)

The first detects *under*-import — things the importer should have written and didn't. The
direction preservation needs is the reverse: things the database has that the new patch does
not. **That comparison does not exist, in either direction, at the patch level.**

**So the never-delete rule is already satisfied, and it was never the hard part.** The hard
part is the step after it, which is not written: mark what is gone.

## 4. The alembic guard is intact, and better than it needed to be

`alembic/env.py` — verified line by line:

- `EXCLUDED_TABLES` = `pipeline_check_results`, `pipeline_findings`, `pipeline_check_runs`.
- `include_object` is wired into **both** `run_migrations_offline()` (line 103) and
  `run_migrations_online()` (line 128). **This is the usual place this defect hides** — a
  guard applied to one path and not the other passes every test run in the mode you tested.
  Both are covered here.
- It also excludes **indexes** belonging to those tables (lines 74–76), not just the tables.
  An index-only autogenerate diff would otherwise still touch them.
- Named explicitly, never prefix-matched, with the reasoning written down: a `pipeline_*`
  pattern would silently adopt the next table someone adds, which is the failure being closed.

**Table ownership, stated as C1 asked:**

    app/models.py (15)   patches, systems, manufacturers, ships, dealers,
                         ship_dealer_listings, pledge_links, component_types, components,
                         weapon_details, missile_details, missile_rack_details,
                         gimbal_mount_details, turret_details, ship_registry
    schema-init/main.go (3)  pipeline_check_results, pipeline_findings, pipeline_check_runs
                             — all three CREATE TABLE IF NOT EXISTS, no DROP, no TRUNCATE,
                               no DELETE anywhere in that file

**And the guard cannot drift**, which is the part worth keeping: `checks/schema_checks.py`
parses `EXCLUDED_TABLES` out of `env.py` at runtime with a regex rather than holding its own
copy, then asserts every live table is claimed by exactly one authority — flagging both
*unclaimed* and *claimed by both*. One writer per artifact, applied to the ownership list
itself.

**One caveat I could not close, and it matters.** `schema_checks.py` compares against the
**live** database, so it only protects while it is actually running against a real connection.
This project has already been bitten once by exactly that (`run_checks.py` passing
`db_conn=None` unconditionally, stranding 874 findings in a fallback log). **I did not run the
checker and could not — no database access from this session.** A guard that is only live when
a checker runs is a guard whose status is unknown until someone runs it. Recommend Code
confirm it executes with a real connection before relying on any of §4.

## 5. What would have counted as dirty — so a clean result is checkable

Per C1's instruction. A hit on any of the following would have been a finding:

    raw SQL           DELETE FROM, TRUNCATE, DROP TABLE, DROP SCHEMA
    ORM bulk          query(...).delete(), .delete(synchronize_session=...), session.delete()
    dataframe         to_sql(..., if_exists="replace")
    filesystem        shutil.rmtree, os.remove, Path.unlink on a data directory
    rebuild-style     any table or store recreated from a snapshot rather than merged into

Found: **zero** in the database layer, **two** on the filesystem (both in
`split_craft_pages.py`, both on rendered output, both explained in §1), **one** in a test
harness.

## 6. Negative control — the search was proven to fire before the clean result was believed

A check that cannot fail is not a check, so the patterns were run against a decoy file built
to contain all five destructive shapes at once:

    DELETE FROM ships WHERE ...                              -> caught
    TRUNCATE TABLE components                                -> caught
    DROP TABLE pipeline_findings                             -> caught
    to_sql("ships", engine, if_exists="replace")             -> caught
    query(Ship).filter(...).delete(synchronize_session=...)  -> caught

All five detected. **The patterns fire when there is something to find, so the clean result on
the real repository is a real result and not a broken grep.** Decoy deleted afterwards.

## 7. Recommendation, in order

1. **Do not write a never-delete guard first. It is already true.** Writing one would produce
   a green test that proves nothing — the same vacuous-check shape logged four times on this
   project. If a guard is wanted, it belongs as a regression test *after* step 2, asserting
   the property that already holds.
2. **Widen `SHIP_STATUSES` and `ck_ships_status_valid` by migration.** Nothing in the
   preservation model can be built until this lands. This is the real first task.
3. **Build the set-difference step** — compare the database against each incoming patch and
   mark what is absent. This is the genuinely missing piece and it is where the effort is.
   **Its acceptance test needs a negative control:** a patch with an entity deliberately
   removed must flip that row's status; break the comparison and confirm the row stays
   `purchasable`, or the test proves nothing.
4. **Fix `split_craft_pages.py` before the first retired item gets a page**, not after. Either
   render retired items from a source that still contains them, or stop `rmtree`-ing and
   reconcile instead.
5. Add a status column to whatever will carry retired **paints** — it does not exist yet.

## 8. What I checked and what I did not

**Checked:** 25 staged files — `seed.py`, `import_ship_components.py`, `run_checks.py`,
`ccpp.py`, `audit_ship_components.py`, `rescale_all_ships.py`, `image_handling.py`,
`build_keybind_modes.py`, `build_ship_component_schema.py`, `checks_flush_fallback.py`,
`app/{models,database,main,schemas}.py`, `alembic/env.py`, `alembic.ini`,
`checks/{findings_store,lifecycle,db_checks,framework,schema_checks,source_checks}.py`,
`schema-init/main.go`, `scripts/{publication_filter,split_craft_pages}.py`.

**Did NOT check, and these are real gaps:**

- **`alembic/versions/*.py` — the six migration files themselves were not read.** Migrations
  legitimately contain `drop_table` in their downgrade paths; I did not verify that no
  *upgrade* path drops something. **This should be closed before the next migration runs.**
- **`app/routers/` was not staged or read.** API write paths were not audited. If any endpoint
  can delete, I did not see it.
- **Go code outside `schema-init/main.go`** — `watcher-go/`, `registry-builder/`, `pkg/` were
  not examined. `citizen-collector/` was deliberately untouched per the constraint.
- **PowerShell** — `Backup-CitizenCompass.ps1` and the `scripts/*.ps1` set were not audited
  for destructive operations. The project's own history with `robocopy /MIR` says that is
  worth someone's time.
- **The checker was not executed.** No database access from this session, so §4's protection
  is verified as *written*, not as *running*.
- Did not touch `citizen-collector/`, the testing site, or any site code.
- Placed no hardpoints and produced no data.
