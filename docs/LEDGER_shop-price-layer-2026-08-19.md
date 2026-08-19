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

A3  DONE  5b62eae  `item_categories` exists AND holds all 100 rows.
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

A4  DONE  40254f0  `shop_items` exists. Migration c5f93160bd87, additive.
    *** THIS IS THE ONE PLACE I HAVE NOT DONE AS THE ORDER SAYS. ***
    A4 specifies "uuid UNIQUE (the join key)". That constraint CANNOT BE
    CREATED against this data, and joining on uuid would do the exact damage
    §3.2 exists to prevent. Measured against 20260801T235530Z:
      7,728 item rows, 7,728 distinct UEX `id`   <- a perfect key, 0 collisions
      5,566 rows carry a uuid; 2,162 (27.98%) carry NONE
      5,356 distinct uuids, of which 120 are SHARED BY MORE THAN ONE ITEM
      worst case TEN different items on one uuid
    The shared ones are different products, not duplicate rows:
    7bd374e9-... is worn by "Attrition-4 Repeater" AND "BRRA LaserCannon AP
    Automated Turret", in two different categories. 0cced6b1-... is worn by
    "Jericho", "Jericho X" and "Jericho XL".
    Joining prices on uuid MERGES DISTINCT PRODUCTS, and loses others:
      items with >=1 price row, joined on id:   2,798
      items with >=1 price row, joined on uuid: 2,424   (374 lost, 13%)
    SO: `uex_id` is the key and the upsert target; `uuid` is kept, indexed and
    exposed but is never identity. Same call CC-12 made for
    components.class_name - the key is the field that is actually unique, and
    a unique constraint over a nullable column is the hole, not the fix.
    §3.2's real instruction, "never join on display name", is untouched.
    CONTROL: duplicate uex_id OBSERVED refused by uq_shop_items_uex_id. The
    order's own stated control passes - two items sharing a display name both
    import and stay distinct, and so does a third. Plus the two cases that
    justify the deviation: two different items sharing one uuid are both
    accepted, and an item with no uuid at all is accepted.
    REVERSES CHEAPLY: the uuid column is there and indexed; C3 enumerates the
    120 collisions; making it the key is a constraint plus a re-run.
    MEASURED, correcting a figure in the order: display-name collisions are
    7 of 7,721 item names, worst case 2 records - not "up to 12". Terminal
    names: 20 of 803 collide, worst case 2. The 12 may be true of something
    else in this project, but it is not true of items or terminals here.
    MEASURED, and it changes B5: 44 of the 100 category files carry
    `data: null`. NOT a failed pull - all 100 returned HTTP 200 with envelope
    status "ok", and the pull manifest's own record_count totals 7,728, which
    matches an independent recount exactly. Those 44 categories are genuinely
    empty. So B5's denominator is 7,728 items across 56 non-empty files, not
    "~99 category files" of data.

A6  DONE  c762a01  `snapshots` exists AND both existing snapshots are rows.
    Built BEFORE A5 rather than after, because A5's UNIQUE(item, terminal,
    snapshot) cannot reference a table that does not exist yet. Not a
    decision, just the dependency order.
    Migration ca347e657da7 (additive), plus import_uex_snapshots.py.
    ACCEPTANCE, both rows present:
      20260801T235530Z  captured 2026-08-01 23:55:30  113 json files  33,771 rows
      20260806T033315Z  captured 2026-08-06 03:33:15    5 json files   3,142 rows
    Row counts are MEASURED by opening every file, not copied from each
    snapshot's own _pull_summary.json. If they were copied, this table would
    record what the pull believed it wrote rather than what is on disk, and
    the one question it exists to answer would be answered by the wrong
    witness.
    It found something on the way through and reported it rather than
    smoothing it over: commodities_status.json holds `data` as a dict, not a
    list. That is a legitimate shape for a status lookup. It is recorded in
    `notes` and counted as unknown - NOT silently counted as zero, because
    "this endpoint returned nothing" and "this file is not the shape I
    expected" are different facts.
    captured_at is parsed from the directory name and left NULL if it will not
    parse. Filling it with the insert time would put a fabricated provenance
    date on a preservation record. The control OBSERVES a NULL captured_at
    being accepted, so that path is known to work rather than assumed.
    DRY RUN PROVEN BY BEHAVIOUR: 0 rows, --dry-run reported "inserted 2",
    0 rows still. Then the real run, then a third run reporting inserted 0.
    CONTROL: duplicate (source, snapshot_key) OBSERVED refused by
    uq_snapshots_source_key; the same snapshot_key under a different source
    OBSERVED accepted, which is what proves the key is on the pair.
    FIXED IN PASSING: the control's "left nothing behind" sweep assumed every
    shop table has a uex_id column. snapshots does not. It now asks
    information_schema which marker column each table actually has - a sweep
    that errored, or worse checked nothing, would have reported a clean
    rollback it never verified.

A5  DONE  b823c56  `item_prices` exists. Migration 2b99ac053efa, additive.
    ACCEPTANCE: the unique key exists and is on (shop_item_id, terminal_id,
    snapshot_id) - NOT (item, terminal). Keying without the snapshot would
    make a second pull an UPDATE and destroy the history the table exists to
    keep, which is §3.4 turned from an intention into a structure.
    Indexed on item, terminal, snapshot, price_buy, price_sell,
    uex_price_id and source_date_modified.
    DECIDED-BY-DEFAULT, and it is the second real call of this run: UEX writes
    price_buy = 0 to mean "this terminal does not sell this", not "it sells
    for nothing". Stored as 0 the site would render "0 aUEC", a false
    statement about a real shop. §3.1 already rules the display side - blank
    means no data - so the storage agrees with it: 0 becomes NULL on the way
    in, and the untouched source values are kept in `detail` so the
    transformation is reversible and auditable. MEASURED FIRST: zero rows in
    the snapshot have both sides absent, so this never blanks a row entirely.
    Reverses cheaply - the raw values are in `detail`.
    CONTROL, all OBSERVED firing:
      duplicate (item, terminal, snapshot) -> uq_item_prices_item_terminal_snapshot
      negative buy   -> ck_item_prices_price_buy_non_negative
      negative sell  -> ck_item_prices_price_sell_non_negative
      neither side   -> ck_item_prices_has_at_least_one_side
      orphan item / terminal / snapshot -> the three FKs, each named
    And the acceptances that stop those being vacuous: buy-only accepted,
    sell-only accepted, a price of exactly 0 accepted (the constraint is
    non-NEGATIVE, not non-zero - an off-by-one there would silently drop
    every genuinely free item), and THE APPEND-ONLY CASE - same item, same
    terminal, different snapshot, accepted. That last one is the whole point
    of the table and it is now observed working rather than assumed.
    NOT YET PROVEN: "re-running the same snapshot inserts zero new rows" is
    B3's control, on the importer. Recorded as outstanding.

A7  DONE  <pending>  Hard constraints complete, and every one of them has now
    been WATCHED REFUSING a row. 16 refusals observed, each asserted against
    the NAME of the constraint that did the rejecting - "an error was raised"
    would also be satisfied by a misspelled column, and would make a missing
    constraint look enforced. 15 acceptances observed alongside them, so no
    constraint can be a CHECK(false) and pass.
    The full refusal set: uq_terminals_uex_id, uq_item_categories_uex_id,
    uq_shop_items_uex_id, uq_snapshots_source_key,
    uq_item_prices_item_terminal_snapshot,
    ck_item_prices_price_buy_non_negative,
    ck_item_prices_price_sell_non_negative,
    ck_item_prices_has_at_least_one_side, ck_locations_kind_valid,
    ck_terminals_confidence_valid, and six orphan FKs -
    item_prices -> shop_items / terminals / snapshots,
    shop_items -> item_categories, terminals -> locations,
    locations -> locations.
    AND THE HARNESS ITSELF IS PROVEN, which is the half that usually gets
    skipped. `--self-test` plants three defects and confirms the harness
    catches each: (1) a "bad" row the database actually accepts, which is
    exactly what a MISSING constraint looks like from inside a checker;
    (2) a bad row rejected by a DIFFERENT constraint than claimed - without
    the name assertion this would pass and hide a missing constraint whose
    row happened to trip a NOT NULL; (3) a legitimate row being rejected,
    the inverse half breaking. All three are caught. The harness has an
    executed failure path, not an assumed one.

--- PHASE A COMPLETE. Schema exists; A3 and A6 also hold real rows. -----------
