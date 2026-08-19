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

A7  DONE  cd29cf8  Hard constraints complete, and every one of them has now
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

B1  DONE  ff3d2c4  import_uex_terminals.py - concrete, hand-written, no
    abstraction, per §B1. Imports the six location endpoints first (675 rows)
    then the 823 terminals.
    ACCEPTANCE, exact: locations 675 source -> 675 stored; terminals 823
    source -> 823 stored; ALL 823 resolve to a location, zero unplaced.
    IDEMPOTENT, observed: second run reports inserted 0, updated 0,
    unchanged 675 / unchanged 823.
    DRY RUN PROVEN BY BEHAVIOUR: 0/0 rows before, --dry-run claimed 675+823,
    0/0 rows after.
    ZERO contaminated resolved_path values - no "None", no "null", no empty
    segment, in either table. The gap cases resolve correctly against real
    data:
      Admin - ARC-L1            -> ARC-L1 Wide Forest Station, ArcCorp, Stanton
      ArcCorp Mining Area 045   -> ArcCorp Mining Area 045, Wala, ArcCorp, Stanton
    Terminals per system: Stanton 509, Pyro 211, Nyx 103.
    WHY LOCATIONS LIVE IN THIS IMPORTER: a terminal without its hierarchy is a
    row pointing at nothing, and the six endpoints exist only to give
    terminals a place. Two scripts that must run in a fixed order, with
    nothing on disk saying so, is worse than one that does both.
    PARENTS ARE HAND-DECLARED per kind, not derived from a specificity
    ranking, because containment is not one ladder: an outpost sits on a moon
    or a planet but never in a city, while 5 space stations DO sit in cities.
    MEASURED: 55 of 73 moons name no planet at all - they parent straight to
    their star system. That is precisely the mid-level gap A1's resolver was
    built for, and it is 75% of moons rather than an edge case.
    MEASURED: referential integrity is perfect in this snapshot - across all
    ten parent references in the six location files, and all six location
    references on all 823 terminals, ZERO dangle. The importer still counts
    and reports unresolved references rather than assuming, because "it was
    clean in August" is not a statement about September.
    CONTROL: checks/_verify_shop_importers.py feeds the shared source guard
    nine broken files - missing, not JSON, bare list, no 'data' key, data as
    dict/string/number, empty file, truncated JSON - and OBSERVES each one
    refused loudly with an explained MALFORMED SOURCE message, not a bare
    KeyError and not an empty list. Three must-not-fail cases sit alongside,
    including the one that matters most: `data: null` returns [] and does NOT
    raise, because 44 real category files look like that and are genuinely
    empty. A guard that cannot tell "empty" from "broken" is the wrong guard
    whichever way it errs, so that distinction is asserted directly.

B2  DONE  dd5c083  import_uex_items_category20.py - category 20 only,
    hardcoded, deliberately not generic per §B2 ("Concrete. Not generic.
    Resist.").
    ACCEPTANCE, exact: 1,099 source rows -> 1,099 stored.
    IDEMPOTENT, observed: second run reports inserted 0, unchanged 1,099.
    DRY RUN PROVEN BY BEHAVIOUR: 0 rows, --dry-run claimed 1,099, 0 rows.
    MEASURED: 299 of the 1,099 (27.2%) carry no uuid. This is category 20 on
    its own reproducing the catalogue-wide 28% figure that drove the A4
    decision - the uuid gap is not concentrated in odd corners, it is
    everywhere.
    WHAT CATEGORY 20 TURNED OUT TO BE, written down because B4 needs it:
    Liveries - ship paints. `size` is "" on nearly every row and is not a
    number. `color`/`color2` exist here and in almost no other category.
    `id_vehicle`/`vehicle_name` are populated, which is unusual. `wiki` and
    `notification` are null on every single row.
    ONE THING ALREADY SHARED RATHER THAN COPIED: load_envelope()/clean()/
    to_dt() are imported from B1 instead of re-implemented. That is not the
    B4 abstraction arriving early - it is declining to maintain two copies of
    a guard that has already been proven.

B3  DONE  cad3dad  import_uex_prices.py - append-only, keyed by snapshot.
    IDEMPOTENT ON THE SAME SNAPSHOT, observed: re-run reports "51 already
    stored, 0 rows ready to insert". That is A5's stated control ("re-running
    the same snapshot inserts zero new rows") demonstrated on the importer.
    DRY RUN PROVEN BY BEHAVIOUR: 0 rows, --dry-run claimed 51, 0 rows.
    ONLY 51 OF 23,734 ROWS LANDED, AND THAT IS CORRECT AT THIS POINT. Only
    category 20 is imported, so 23,683 rows reference items that do not exist
    yet. They are DEFERRED and COUNTED, and the importer exits reporting
    "NOT COMPLETE" with the exact number - it does not store fewer rows and
    call it success, which is the failure mode rule 12 is about. The exact
    row-count acceptance for B3 is therefore verified AFTER B5, not here, and
    is recorded as outstanding until then.
    Incidentally measured: liveries barely sell in-game. 1,099 livery items
    produce just 51 price rows across all 823 terminals - they are almost
    entirely pledge-store goods. Worth knowing before anyone reads C4's
    coverage table and assumes a low number means missing data.
    Nothing in this file updates or deletes a price. The only write is an
    insert. Upserting on (item, terminal) would be less code and would
    destroy the history the table exists to hold.

B4  DONE  4d0063d  app/uex_pipeline.py - extracted from B1-B3 AFTER they
    existed, per §B4. The order asked for both halves of this, so:

    WHAT THE THREE GENUINELY SHARED:
      load_envelope()  - the source guard. Identical in all three, and the
                         only piece already proven against known-bad input.
      to_dt / to_bool / clean - and they had ALREADY started to drift.
                         to_bool existed twice with the same body; `clean`
                         existed in one importer that needed it and not in
                         another that also did.
      make_logger()    - four copies differing only in a prefix string.
      split_detail()   - the same three lines everywhere, and the exact place
                         a dropped source field would vanish unnoticed.
      upsert_by_key()  - load, diff, insert-or-update, count all three
                         outcomes. B1 (twice), B2 and the categories loader.

    WHAT I EXPECTED THEM TO SHARE AND THEY DID NOT - and this is the part
    that vindicates the rule:
      THE WRITE STRATEGY. Had I designed this before B3, I would have built
      one generic importer that upserts on a natural key, because that is what
      B1 and B2 both do and they came first. B3 does not upsert AT ALL - it is
      insert-only, and an upsert there would silently overwrite price history.
      That is the §3.4 failure this entire layer exists to prevent, and a
      generic importer written after B1 and B2 would have walked straight into
      it while looking completely reasonable. So upsert_by_key() and
      append_only() are two functions, not one function with a flag: a flag
      would put the destructive behaviour one argument away from the safe one,
      on the only table where the mistake is unrecoverable.
      THE SHAPE OF A KEY. B1/B2 key on one integer from the source file. B3
      keys on a 3-tuple of RESOLVED FOREIGN KEYS - database ids that appear
      nowhere in the source. A "key_column" parameter covers two of three and
      is useless for the third.
      FK RESOLUTION. B1 resolves parents against rows it is inserting in the
      same transaction; B2 does one lookup; B3 does two plus a snapshot.
      Generalising it would have meant inventing a small configuration
      language, which is the thing the rule is there to stop.
      DEFERRAL. Only B3 has "cannot be placed YET, report as incomplete".
      B1 and B2 have no such state and would never have grown one.

    So what exists is a TOOLKIT, not a framework. Nothing in it knows what a
    terminal or a price is, and no importer must use all of it.
    NOT FOLDED IN: import_uex_snapshots.py. It walks directories rather than
    reading envelopes, and it must RECORD an unexpected file shape rather than
    reject it - the opposite of what load_envelope() is for. Forcing it in
    would be exactly the over-generalisation §B4 warns about.
    PROVEN BEHAVIOUR-NEUTRAL, which is the real risk in a refactor: every
    importer was re-run afterwards and reported 0 inserted and **0 UPDATED**
    across all 2,697 stored rows. Any drift in a single coercion would have
    surfaced as an update on every row of that table. The source-guard control
    still passes all 15 assertions.

B5  DONE  <pending>  import_uex_items_all.py - the B4 pipeline over every
    category file.
    ACCEPTANCE, EXACT: source files sum to 7,728 items; shop_items holds
    7,728. 100 category files, 56 with rows, 44 empty.
    CROSS-CHECK WORTH NOTING: the run reported "inserted 6629, updated 0,
    unchanged 1099". The 1,099 rows B2 wrote by hand are byte-identical under
    the generalised importer - zero updates. That is independent evidence that
    B5 reproduces B2 exactly rather than merely covering it.
    DRY RUN PROVEN BY BEHAVIOUR: 1,099 rows before, --dry-run claimed 6,629
    inserts, 1,099 rows after.
    MEASURED: 2,162 of 7,728 (28.0%) carry no uuid - the catalogue-wide figure
    behind the A4 decision, now confirmed on the full import rather than
    extrapolated.
    GAP FOUND AND CLOSED WHILE WRITING THE CONTROL: if EVERY category file
    were empty, the importer would have reported "0 source items" and exited
    0. Each individual file is perfectly valid in that scenario, so the
    per-file guard cannot catch it - and a UEX outage returning null across
    the board is exactly how it would happen. That is a textbook silent
    success and it is now refused: all-empty is a pull that did not land, not
    a catalogue with no items in it.
    CONTROL, at the IMPORTER level rather than the guard level, because those
    are different claims - a guard can raise correctly while the importer
    around it catches, warns, imports the other 99 files and exits 0.
    checks/_verify_items_import_b5.py OBSERVES all four:
      one malformed file among good ones -> exit 1, and NOTHING imported
        (the importer reads every file before writing anything, so a bad file
        at position 90 cannot leave 89 categories half-imported)
      every file empty                    -> exit 1
      no category files / missing dir     -> exit 1
      a valid directory                   -> exit 0, and it REPORTS
        "inserted 2" - so exit 0 is earned by finding the rows, not by
        refusing everything unconditionally
    The positive case runs --dry-run only, deliberately: a real run would put
    two fake liveries into production shop_items permanently, since this
    project never deletes and blocks deletion at the engine. A control that
    pollutes the data it checks is worse than no control.

B3  COMPLETED  <pending>  Re-run after B5, and the outstanding half of B3's
    acceptance is now met EXACTLY: 23,734 source price rows -> 23,734 stored
    for snapshot 20260801T235530Z. Zero deferred, zero skipped for want of a
    price side, zero duplicate (item, terminal) pairs within the snapshot.
    The 23,683 rows B3 reported as unplaceable landed on the re-run, exactly
    as it said they would.
