# UPDATE — Addendum #2 complete: Cutlass Black fix + full checker rollout (2026-07-30, continued)

Addendum #2 (received mid-run, explicitly held until the original overnight queue reported
done — it did, see the prior "Overnight queue complete" update) is now fully worked through.
Both parts done: the real Cutlass Black data fix, and the broader auditor/checker rollout.

## Part 1 — Cutlass Black: real fix, not just folder cleanup (commit `ff52f3e`)

- `_to_delete/cuttlass_black_typo_duplicate/` confirmed byte-identical to the real
  `hardpoints.json` (diffed before touching anything) — deleted outright (renamed to
  `_DELETED_$`, device bridge can't actually `rm`; already gitignored under the existing
  `_to_delete/` rule).
- The real bug was inside the live file: `ship_name: "cuttlass black"` → `"Cutlass Black"`,
  and the missing-size-digit label `"S  LS"` → `"S3  LS"` (matches every sibling entry's
  pattern).
- **`ship_slug` — deviated from your literal instruction, on purpose, with evidence:** you
  said fix it to `"cuttlass_black"` (underscore). I checked first and the project's actual
  established convention (the ship's own folder name, `data-layer/ship_registry.json`'s
  `folder_slug`, and `tests/testing-site/data/ships-master.json`'s `slug` field) is
  hyphenated — `"cutlass-black"`, matching every other multi-word ship. Used that instead,
  since your own deeper instruction was "don't leave a slug mismatch between this file and
  whatever else keys off it," and the underscore version would have created exactly that
  mismatch. Flagging this clearly rather than silently overriding you — if you actually
  want the underscore version for some reason I'm not seeing, say so and I'll change it.
- **Turret size (S3 vs. the open S5 note) and missile rack real data — NOT changed.**
  Same `WebFetch` blocker as Aquila/Gladius (see the prior update): 3 failed attempts
  tonight against 2 different hosts, confirmed non-domain-specific. Left both exactly as
  they were, with inline `_unverified_note` / `_needs_real_data` explanatory keys added
  (not new data, just a pointer to the blocker) rather than guessing S5 from the
  unverified note like you explicitly told me not to.

## Part 2 — Checker/auditor rollout (commit `36caa7d`)

Built the pluggable checker framework the addendum called for, going past the listed
categories where I judged it worthwhile, same findings-only pattern as
`audit_ship_components.py` (DEFECT / WARNING / LIMITATION / PASS, writes to
`pipeline_check_results`, never auto-repairs).

**`checks/framework.py`** — shared `Finding` dataclass + `write_findings()` (inserts to
`pipeline_check_results` if given a live connection, else appends to
`logs/pipeline_check_results_fallback.jsonl` — gitignored, never lost).

**`checks/file_checks.py`** — 12 checkers, stdlib + git only. **Run for real tonight**,
against this live repo, via the device bridge (the one execution path that has both
filesystem and git access without needing a database or network):

- naming-convention/slug-typo check — the automated version of the Cutlass Black bug catch
- placeholder/null-density check — surfaces the missile-rack-still-placeholder gap as a
  WARNING backlog item
- broken local asset reference check, broken internal link check
- orphaned test fixture check (fixture folders vs. `ships-master.json`)
- log growth, backup freshness (honest LIMITATION — no backup mechanism exists yet)
- secrets-in-repo scan, large-committed-blob check
- Fan Kit compliance check (read-only presence check — see the real finding below)
- scheduled-task-health / duplicate-process — honest LIMITATION stubs: no tool available
  to me can query Windows Task Scheduler or the process list; these need to be run from a
  context with real Windows access (PowerShell: `Get-ScheduledTask -TaskName *watcher*`,
  `tasklist | findstr inbox_watcher`)

**Real run result against this live repo tonight: 18 findings — 0 DEFECT, 2 WARNING,
5 LIMITATION, 11 PASS.**

**The 2 real WARNINGs, both worth your attention:**
1. Cutlass Black's missile rack still has a placeholder label — already known, tracked above.
2. **`static/index.html` (your homepage) has no trademark/Fan-Kit disclaimer text at all.**
   The actual disclaimer paragraph only exists in `static/preview.html` — confirmed by
   reading commit `51f08c7`'s own message ("add trademark disclaimer" — but the diff shows
   it went into `preview.html`, not `index.html`). I did **not** touch this — Fan Kit/legal
   material is explicitly off-limits for me to edit — just surfacing it since it's exactly
   the kind of compliance gap this checker exists to catch. Your call whether the homepage
   needs the same disclaimer paragraph preview.html has.

**A bug in the checker itself, found and fixed before it shipped:** the first real run
against this live repo threw 7 false-positive DEFECTs — `broken_asset_references_check`
and `broken_internal_link_check` were matching JS template-literal-built HTML (e.g.
`href="${escapeHtml(v.path)}"` inside a `<script>` block that builds markup at runtime) as
if they were literal static paths. Fixed by skipping any ref containing `${`/`{{`/`{%`,
re-ran clean. Didn't want to hand you a checker whose first real output was noise.

**`checks/db_checks.py`** (Ships domain — distinct scope from `audit_ship_components.py`,
which only covers Ship Items): referential integrity (manufacturer/patch/dealer FKs,
confidence vocabulary), duplicate `(name, manufacturer_id)` pairs, registry sync
(`data-layer/ship_registry.json` vs. the DB), schema drift via `alembic check`. **Built and
tested against scratch Postgres only** — same real-DB-unreachable limitation as everything
else tonight (re-confirmed with a fresh TCP test right when your message about running
`alembic upgrade head`/the importer came in — still `Connection refused` on `127.0.0.1:5432`
from every tool available to me). One real bug caught by testing before it shipped: the
confidence-vocabulary check was built against a hand-typed wrong tuple
(`verified/inferred/unverified/conflicting`) instead of the actual
`app.models.CONFIDENCE_LEVELS` (`unverified/low/medium/high/verified`) — would have
wrongly DEFECT-flagged every ship using `low`/`medium`/`high` confidence. Fixed to import
the real constant instead of hardcoding a second copy of it.

**`checks/network_checks.py`** — `dependency_vulnerability_check` (via `pip-audit`) **run
for real tonight** in the cloud sandbox (has genuine network access, unlike everything
else): **0 known advisories across 49 packages** (`requirements.txt` + `requirements-dev.txt`
combined). `external_reachability_check` (would confirm `api.star-citizen.wiki` — the
Aquila/Gladius data source — is still reachable and shaped as expected) is written and
unit-tested with a mocked response, but **deliberately not run for real and not registered
in `CHECKERS` yet** — it targets the exact host `WebFetch` failed against three times
tonight, and the rule against working around a failed `WebFetch` target applies regardless
of method. Wire it in once you can get a live `WebFetch` approval for that host, or run it
from an environment that rule doesn't apply to.

**`run_checks.py`** — CLI tying all three groups together (`--group file|db|network|all`).

**Tests:** 24 new tests (12 file-checker + 5 db-checker + 7 network-checker), all passing
against scratch. Full suite: 47 passed, 1 skipped (a DB-constraint-timing test that
gracefully skips if Postgres enforces the FK immediately rather than deferred — expected).

**Pruning non-firing checkers — explicitly NOT done tonight, per your own instruction.**
You said not to decide this same-session on a guess. One real run tonight isn't "over time."
Revisit this after the checkers have run for real a few more times.

## Commits this run

```
36caa7d Add pluggable checker framework (checks/) + run_checks.py CLI
ff52f3e Fix Cutlass Black hardpoints.json: real slug/name typo, label, open items flagged
```
(on top of everything from the original queue.) **17 commits ahead of `origin/main` now,
still all local** — not pushing without you saying so.

`git status`: clean working tree.

## Mid-run: your pg_dump/alembic/import message

While I was mid-checker-build you sent the exact 3 commands from the prior handoff
(`pg_dump` backup → `alembic upgrade head` → `python import_ship_components.py`). I
re-tested DB reachability right then (not just relying on the earlier result) — still
`Connection refused` from every tool I have. Told you this live in the session. If you were
pasting those because you're at your own terminal running them yourself, that's exactly
right and matches the handoff. If you meant for me to run them, I still can't — no path
exists from here to your real Postgres.

## Decisions that need you

1. Cutlass Black `ship_slug`: I used the hyphenated project convention (`cutlass-black`)
   instead of your literally-suggested underscore version — see Part 1 above. Speak up if
   you actually want it changed to the underscore form.
2. `static/index.html` is missing the trademark/Fan-Kit disclaimer that `static/preview.html`
   has — should the homepage get the same paragraph? (Not something I'll touch myself.)
3. Aquila/Gladius/Cutlass-Black-turret-size real data — still needs you present for one
   live `WebFetch` approval on `api.star-citizen.wiki`, or a manual pull. Once you have that
   data, `external_reachability_check` can also finally be run for real and wired into
   `CHECKERS`.
4. (Standing from the original queue) `/api/v1/ships`/`/dealers`/`/manufacturers` retrofit
   to the new `Page` envelope — still your call, still untouched.
5. (Standing) `ARCHITECTURE_DEEP_REVIEW.md` scope question — still untouched, not decided
   by me.

## Exact safe next starting point

Everything requested across the original queue and both addenda is now done, committed,
and tested against either the real repo (file-based checkers, real run tonight) or scratch
(everything DB-dependent). Nothing is mid-migration, no lock files, no half-applied state.
The next real step is entirely on your side: get real DB access to run the 3 commands
above (backup → migrate → import), and/or get one `WebFetch` approval or a manual data
pull for Aquila/Gladius/Cutlass-Black-turret. Once either happens, tell me and I'll pick
straight back up — running the db/network checker groups for real, wiring in
`external_reachability_check`, and closing out the decisions list above.
