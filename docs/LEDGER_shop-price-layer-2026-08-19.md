# LEDGER — shop and price layer, 2026-08-19

    order   docs/ORDER_shop-and-price-layer-RUN-CONTINUOUSLY-2026-08-19.md
    rule    APPEND ONLY. One line per item, written the moment it finishes.
            Never rewrite an earlier line. This is the resume point after a
            compaction and the thing to read instead of a conversation.

    format  <item>  DONE|BLOCKED  <sha>  <what exists now that did not before>

---

L0  START  2026-08-19  the ledger exists before item A1, per §4.

L1  NOTE   2026-08-19  CREDENTIAL EXPOSURE, SELF-INFLICTED. While checking for a
    database URL I printed `.env` to the transcript and masked only the DB
    password. The UEX_API_TOKEN and CLOUDFLARE_API_TOKEN were shown in full.
    Nothing was sent anywhere, but they are now in a conversation log.
    RECOMMEND ROTATING BOTH. My mistake, reported rather than quietly noted.

L2  NOTE   2026-08-19  Environment measured before item A1: postgres reachable on
    localhost:5432, database `citizen_compass`, 19 public tables. The repo venv
    (venv/Scripts/python.exe) carries sqlalchemy 2.0.51, psycopg2 and alembic;
    the system pythons carry none of them, so every DB command in this run uses
    the venv interpreter explicitly.

L3  NOTE   2026-08-19  BACKUP, per rule 4, and it did NOT pass first time.
    `Backup-CitizenCompass.ps1` blocked on an interactive PGPASSWORD prompt and
    was torn down at exit 58 with NO DATABASE DUMP TAKEN - git bundle and
    working-tree copy had succeeded, so it looked like progress. Re-ran with
    PGPASSWORD supplied from .env (not printed, per L1) and -NonInteractive
    -SkipMirror: bundle verified 42.4MB, 10,337 files copied, Postgres dump
    259.8KB written AND restore-tested. Exit 0.
    The restore test warns "returned 232 ships, expected 254". Investigated
    rather than waved through: the LIVE database holds 232 ships, the restore
    returned 232, so the dump is faithful and `expected 254` is a stale
    constant in the backup script. NOT FIXED - out of scope, and it is a
    warning that will now fire on every backup, which Sleven should decide
    about deliberately.

A1  DONE  e2b397d  `locations` exists: one self-referential table for every
    level UEX names, with kind+uex_id unique, denormalised star_system_id and
    planet_id for the "everything in Stanton" filter, JSONB `detail`, and a
    materialised `resolved_path`. app/locations.py resolves a UEX terminal
    record to its most specific NAMEABLE level and walks parents to a readable
    string. Migration 9df170bd1cf2, reviewed for destructive ops before
    applying (upgrade() is purely additive).
    ACCEPTANCE: a terminal record resolves - 'Area 18, ArcCorp, Stanton'.
    CONTROL, both halves: checks/_verify_location_hierarchy.py 31 assertions,
    and it has been OBSERVED FAILING under three deliberate mutations - a
    level rendering as literal "None", whitespace names passing through, and a
    resolver that returns nothing for everything (that third mutant is what
    catches a vacuously-passing check). checks/_verify_location_hierarchy_db.py
    proves the same through the real table in a rolled-back transaction, and
    OBSERVES the kind constraint and the (kind,uex_id) unique key each
    REFUSING a bad insert - plus the inverse, that the same uex_id under a
    different kind is still allowed, which is what proves the key is on the
    pair and not on uex_id alone.
    DECIDED-BY-DEFAULT: `orbit` and `poi` are declared kinds but are NOT
    resolvable - the 20260801T235530Z snapshot holds no orbits.json and no
    pois.json, so those ids can be read but never named. Rather than guess a
    name (rule 11) or drop the id, the resolver steps past them to the deepest
    level it CAN name, and the raw ids are preserved in `detail`. Reverses
    cheaply: pull those two endpoints, import them, remove them from
    RESOLVABLE_KINDS' exclusion, re-run the importer.

A2  DONE  c49cd1d  `terminals` exists: uex_id UNIQUE, the four different
    names UEX ships per terminal (name/fullname/nickname/displayname - they
    are not interchangeable and picking one now would be a guess about a UI
    that does not exist), code, type, location FK + denormalised
    star_system_id + materialised resolved_path, company_name, is_available,
    source_date_modified as a real indexed timestamp (C5 buckets on it),
    JSONB detail, last_verified_patch. Migration fb37274717f7, additive only.
    CONTROL: checks/_verify_shop_schema_db.py OBSERVES the database refusing a
    duplicate uex_id, and names the constraint that did it - "an error was
    raised" would also be satisfied by a typo, which proves nothing. The
    inverse half is there too: two terminals with different uex_ids both
    insert, so the constraint is not simply rejecting everything.
    MEASURED, not assumed: all 823 terminals resolve to a nameable location -
    zero fall through to "no resolvable level". Terminal types are
    item 479, commodity 161, fuel 98, vehicle_rent 32, commodity_raw 23,
    refinery 21, vehicle_buy 9.
    DECIDED-BY-DEFAULT: `type` is indexed but NOT constrained to those seven
    values. A CHECK there would stop the importer dead the day UEX adds an
    eighth type, on a row that stores perfectly well. §3.8 already rules this
    shape - import and flag, do not skip - so an unknown type becomes an
    auditor finding, not an import failure. Reverses cheaply: add the CHECK.
    NOT YET PROVEN: the "823 rows import" half of A2's acceptance is B1's
    work. Recording that as outstanding rather than implying it is done.

A3  DONE  <pending>  `item_categories` exists AND holds all 100 rows.
    Migration e6b3d0ad40b4 (additive only), plus import_uex_categories.py -
    this loader lives at A3 rather than phase B because A3's acceptance is
    stated in rows, not DDL.
    ACCEPTANCE: 100 rows, 21 sections, grouping correctly - General 33,
    Utility 11, Clothing 10, Vehicle Weapons 8, Systems 7, Armor 6,
    Miscellaneous 5, Data 3, then 13 sections of 1-2.
    IDEMPOTENT, observed: second run reports inserted 0, updated 0,
    unchanged 100.
    DRY RUN PROVEN BY BEHAVIOUR, not by reading the code (rule 12): counted
    0 rows, ran --dry-run, it reported "would insert 100", counted 0 rows
    again from a separate connection. The flag is a check that the write path
    did not run, and it has now been observed not running.
    CONTROL: duplicate category uex_id OBSERVED refused by
    uq_item_categories_uex_id. Inverse half present, including the specific
    case that a category flagged is_game_related=0 is ACCEPTED and not
    refused - §3.8 says those are imported and flagged, and a constraint that
    quietly rejected them would enforce the opposite of the ruling.
    MEASURED, and this one is worth Sleven's attention: 48 of the 100
    categories carry is_game_related = 0. That is not a handful of oddities,
    it is nearly half the taxonomy, and it means "hide non-game categories"
    is a much bigger display decision than the flag's name suggests. All 48
    are imported and flagged per §3.8; none are skipped.
