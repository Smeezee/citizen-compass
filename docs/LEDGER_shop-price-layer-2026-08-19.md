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

B5  DONE  90ef4d0  import_uex_items_all.py - the B4 pipeline over every
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

B3  COMPLETED  90ef4d0  Re-run after B5, and the outstanding half of B3's
    acceptance is now met EXACTLY: 23,734 source price rows -> 23,734 stored
    for snapshot 20260801T235530Z. Zero deferred, zero skipped for want of a
    price side, zero duplicate (item, terminal) pairs within the snapshot.
    The 23,683 rows B3 reported as unplaceable landed on the re-run, exactly
    as it said they would.

B6  DONE  0ca407d  import_uex_commodities.py - 204 commodities and 2,923
    commodity price rows from 20260806T033315Z, into the SAME tables as items
    per §B6. Migration 250bdcd72ac3.
    *** SCHEMA CHANGE THIS FORCED, and it was not foreseeable from §B6 ***
    Commodities are numbered from 1 in an id space entirely separate from
    items, and 200 OF THE 204 COMMODITY IDS COLLIDE WITH ITEM IDS while
    meaning something completely different: id 1 is the "Omnisky III Cannon"
    as an item and "Agricium" as a commodity. uq_shop_items_uex_id would have
    refused the second of every pair. shop_items now carries `source_kind`
    and the key is (source_kind, uex_id). It is a WIDENING, not a relaxation -
    all 7,728 existing rows take the 'item' default and nothing that was
    unique stops being unique. Old and new constraints swap inside one
    migration, so there is no window where the table is unconstrained.
    The CHECK on source_kind was added to the migration BY HAND: alembic does
    not autogenerate CHECK constraints, so a constraint declared only in the
    model would silently never reach the database - the model would claim an
    invariant nothing enforces. Small, but the same family of defect.
    ANOTHER NAIL IN THE UUID QUESTION: not one of the 204 commodities carries
    a uuid. Had uuid been the join key, the entire commodity catalogue would
    have been unkeyable.
    ACCEPTANCE: 204 of 204 commodities. 2,923 of 2,932 price rows across the
    two price files. IDEMPOTENT, observed: re-run gives 0 and 0.
    THE 9 ROWS NOT STORED, each investigated rather than written off:
      6 are genuine duplicates IN THE SOURCE - 5 (commodity, terminal) pairs
        appear 2-3 times in commodities_prices_all.json. Four of the five are
        byte-identical repeats. THE FIFTH IS NOT: "Stims" at HUR-L5 appears
        twice with DIFFERENT sell prices, 5,800 and 4,900. Keeping the first
        occurrence is therefore a real choice and not a no-op.
        DECIDED-BY-DEFAULT: first occurrence wins, and the discrepancy is
        recorded here rather than resolved. Reverses cheaply - both rows are
        in the source file and nothing has been overwritten. It should
        probably become a C-phase finding; noting it as such.
      3 are raw-commodity rows with BOTH prices at 0 - Ammonia at HUR-L1 and
        HUR-L2, Quantum Fuel at HUR-L2. Not observations about anything, and
        ck_item_prices_has_at_least_one_side would refuse them anyway.
    WHAT WENT WHERE: scu_buy/scu_sell/scu_sell_stock, status_buy/status_sell,
    container_sizes and quality all go to `detail` per §B6. So do
    price_buy_avg and price_sell_avg - §3.1 forbids showing a blended average
    as if it were a price, and the cheapest way to guarantee that is for the
    average to not be in the column the site reads.
    commodities_raw_prices_all.json (335 rows) is imported too, flagged
    is_raw_commodity_price in `detail` - without that flag the refined and raw
    prices for one commodity are indistinguishable once stored.
    commodities_status.json is a LEGEND, not data (status codes 1-7 ->
    "Out of Stock (Empty)" ... "Maximum Inventory (Full)"). It is not
    duplicated onto 2,597 price rows.

--- PHASE B COMPLETE. -------------------------------------------------------
    locations 675 | terminals 823 | item_categories 100 | snapshots 2
    shop_items 7,932 (7,728 items + 204 commodities) | item_prices 26,657

C1  DONE  8b61f66  checks/shop_checks.py:price_outlier_check. Per category
    AND per side - buy and sell are never pooled, because a category bought at
    100 and sold at 20,000 makes a bimodal blob that flags nothing.
    JUDGED IN LOG SPACE, and that was changed AFTER the first real run rather
    than guessed. Run 1, linear, flagged 590 of 26,657 rows (2.2%), and
    reading them showed the detector was asking the wrong question: "Scourge
    Railgun Magazine, 5,888 aUEC, 16.8x the Attachments median of 350" is a
    perfectly ordinary expensive magazine. Game prices are MULTIPLICATIVE -
    a category genuinely spans 200 to 3,000,000 aUEC - so on a linear scale
    the whole upper half of any such category falls outside a fence built
    from its lower half. A detector that flags 590 ordinary rows is one
    nobody reads, which is worse than none. In log space: 205 rows, 0.77%.
    The linear number is left in the code as the evidence for the log one.
    Reports WARNING, never DEFECT: an expensive gun is not a confirmed error,
    and calling it one teaches the reader to ignore the word.
    Categories below 8 priced rows report LIMITATION, NOT pass - "we could
    not judge this" and "we judged it fine" are different answers.

C2  DONE  8b61f66  checks/shop_checks.py:orphan_check. Currently PASS on
    all four conditions: every price row resolves to a real item and a real
    terminal, every terminal has a location, every item has a category.
    THE HARD-ORPHAN BRANCH IS UNREACHABLE WHILE THE FOREIGN KEYS EXIST, which
    would normally make it exactly the kind of check rule 12 says not to
    trust. It is proven anyway - see C6.

C3  DONE  8b61f66  checks/shop_checks.py:name_collision_check.
    *** THE NUMBERS THE ORDER ASKED FOR ***
      item display names colliding WITHIN items:  7 of 7,721, worst case 2
      commodity display names colliding:          0 of 204 - all unique
      terminal names colliding:                  20 of 803, worst case 2
      names existing as BOTH item and commodity: 193
      uuids shared by >1 item:                   120, WORST CASE 10
      items carrying no uuid at all:           2,162 of 7,932
    So display-name collision is NOT the problem the order expected. "Up to
    12 records per display name" is not true here - it is 2. THE UUID IS THE
    PROBLEM, by an order of magnitude, which is the A4 finding arriving again
    from a different direction.
    The 193 item/commodity name overlaps are reported SEPARATELY and as
    LIMITATION, not lumped in: an "Agricium" item and an "Agricium" commodity
    are UEX describing one real thing through two endpoints, which is a
    completely different situation from two distinct guns sharing a name.
    Pooling them would have reported 200 collisions and buried the 7 that
    actually matter.
    The uuid finding is a DEFECT **in the source data**, explicitly not in
    this database - nothing here is broken by it and nothing is auto-fixed.

C5  DONE  8b61f66  checks/shop_checks.py:price_staleness_check.
      0-30 days     4,754  (17.8%)
      31-90 days   18,246  (68.4%)
      91-180 days   3,060  (11.5%)
      181-365 days    248   (0.9%)
      over a year     349   (1.3%)  -> WARNING, must be visibly flagged
      no source date at all: 0
      dated in the future:   0
    Measured against UEX's own date_modified, NOT the snapshot capture time.
    Those answer different questions: the snapshot says when we pulled, and
    date_modified says when a human last confirmed the price in game. A price
    pulled yesterday can be two years old, and it is the second number a
    player needs.

C4  DONE  8b61f66  checks/shop_checks.py:category_coverage_check.
    *** THIS IS THE TABLE. It answers the thruster/armour/fuel-tank
    question with numbers instead of an opinion, per §3.3. ***
    Driven from item_categories so ALL 100 categories appear - grouping
    the items instead would have silently omitted the 44 that hold none,
    and those are exactly the rows whose absence looks like an oversight.

       cat  section            category                    items  priced   cover  game
      --------------------------------------------------------------------------------
         1  Armor              Arms                          486     161   33.1%  y
         2  Armor              Backpacks                     150      26   17.3%  y
         7  Armor              Full Set                      109       0    0.0%  y
         3  Armor              Helmets                       670     201   30.0%  y
         4  Armor              Legs                          475     161   33.9%  y
         5  Armor              Torso                         476     161   33.8%  y
        82  Avionics           Flight Blade                   80      46   57.5%  y
        83  Avionics           Radar                          56      51   91.1%  y
        72  Clothing           Dresses                         0       0       -  N
        68  Clothing           Eyeware                        14       0    0.0%  y
         8  Clothing           Footwear                      307     237   77.2%  y
        15  Clothing           Full Set                        3       0    0.0%  N
         9  Clothing           Gloves                        131      57   43.5%  y
        10  Clothing           Hats                          187      79   42.2%  y
        11  Clothing           Jackets                       453     282   62.3%  y
        12  Clothing           Jumpsuits                       0       0       -  y
        13  Clothing           Legwear                       347     214   61.7%  y
        14  Clothing           Shirts                        367     186   50.7%  y
        36  Commodities        Commodities                   158       0    0.0%  N
        87  Commodities        Harvestables                   17       0    0.0%  N
        69  Consumable         Consumable                      0       0       -  y
       111  Data               Cards                           0       0       -  N
        37  Data               Points of Interest              0       0       -  N
       112  Data               Storage                         0       0       -  N
        75  Decorations        Decorations                    77      15   19.5%  y
       107  Flair              Surface                        31       2    6.5%  y
        91  General            Bounty Hunter                   0       0       -  N
        49  General            Construction                    0       0       -  N
        56  General            Datarunning                     0       0       -  N
        93  General            Delivery                        0       0       -  N
        92  General            ECN                             0       0       -  N
        71  General            Engineering                     0       0       -  N
        48  General            Exploration                     0       0       -  N
        54  General            Gunner                          0       0       -  N
        40  General            Hauling                         0       0       -  N
        94  General            Hauling                         0       0       -  N
        96  General            Maintenance                     0       0       -  N
        58  General            Mass Transit                    0       0       -  N
        44  General            Medical                         0       0       -  N
        55  General            Mercenary                       0       0       -  N
        97  General            Mercenary                       0       0       -  N
        41  General            Mining                          0       0       -  N
       100  General            Mining                          0       0       -  N
       101  General            Other                           0       0       -  N
        50  General            Private Pilot                   0       0       -  N
        51  General            Racing                          0       0       -  N
        98  General            Racing                          0       0       -  N
        42  General            Refining                        0       0       -  N
        45  General            Refueling                       0       0       -  N
        46  General            Repairing                       0       0       -  N
        99  General            Salvage                         0       0       -  N
        43  General            Salvaging                       0       0       -  N
        47  General            Scanning                        0       0       -  N
        57  General            Science                         0       0       -  N
        53  General            Security                        0       0       -  N
        95  General            Service Beacon                  0       0       -  N
        59  General            Tourism                         0       0       -  N
        52  General            Towing                          0       0       -  N
        39  General            Trading                         0       0       -  N
        20  Liveries           Liveries                     1099      19    1.7%  y
        16  Miscellaneous      Consumables                    13       8   61.5%  y
        65  Miscellaneous      Container                       9       8   88.9%  y
        62  Miscellaneous      Drinks                         55      42   76.4%  y
        63  Miscellaneous      Foods                         102      68   66.7%  y
        61  Miscellaneous      Miscellaneous                 325      31    9.5%  y
        74  Module             Module                         23      10   43.5%  y
        38  Other              Other                          41       0    0.0%  N
        60  Other              Other                           0       0       -  N
        17  Personal Weapons   Attachments                   170      76   44.7%  y
        18  Personal Weapons   Personal Weapons              388      81   20.9%  y
        86  Propulsion         Jump Modules                    3       3  100.0%  y
        81  Systems            Batteries                       0       0       -  N
        19  Systems            Coolers                        73      50   68.5%  y
        84  Systems            Gravity Generator               0       0       -  N
       103  Systems            Life Support Generator          3       0    0.0%  N
        21  Systems            Power Plants                   75      42   56.0%  y
        22  Systems            Quantum Drives                 57      45   78.9%  y
        23  Systems            Shield Generators              64      42   65.6%  y
        73  Technology         Mobiglas                       20      20  100.0%  y
        24  Undersuits         Undersuits                    199     105   52.8%  y
        64  Utility            Container                       8       4   50.0%  y
        25  Utility            Docking Collars                 7       7  100.0%  y
        26  Utility            External Fuel Tanks             8       8  100.0%  y
       109  Utility            Fabricator                      1       1  100.0%  y
        27  Utility            Fuel Nozzle                     0       0       -  N
        28  Utility            Gadgets                         6       6  100.0%  y
        29  Utility            Mining Laser Heads             17      16   94.1%  y
        30  Utility            Mining Modules                 27      26   96.3%  y
       110  Utility            Salvage Beams                   4       4  100.0%  y
        31  Utility            Scraper Beams                   4       4  100.0%  y
        67  Utility            Tractor Beams                   9       8   88.9%  y
        90  Vehicle Weapons    Bomb Racks                      8       8  100.0%  y
        70  Vehicle Weapons    Bombs                           3       3  100.0%  y
        32  Vehicle Weapons    Guns                          154      85   55.2%  y
        33  Vehicle Weapons    Missile Racks                  56      19   33.9%  y
        34  Vehicle Weapons    Missiles                       55      51   92.7%  y
        79  Vehicle Weapons    Point Defense Cannon           11       0    0.0%  y
        80  Vehicle Weapons    Torpedo Tubes                   2       0    0.0%  N
        35  Vehicle Weapons    Turrets                        35      19   54.3%  y
       102  Vehicles           Vehicles                        0       0       -  N
            Commodities        (no category FK)              204     147  72.1%  y
  
      TOTAL 2,945 of 7,932 priced (37.1%)
      categories at 100% coverage : 10
      categories partially covered: 37
      categories with items but NO prices: 9
        -> Commodities, Eyeware, Full Set, Full Set, Harvestables, Life Support Generator, Other, Point Defense Cannon, Torpedo Tubes
      categories with no items at all: 44

    THE THREE ANSWERS SLEVEN ASKED FOR, from the table above:

      FUEL TANKS   -> YES, comprehensively. "Utility / External Fuel Tanks",
                      8 items, 8 priced, 100% coverage. Not a gap at all.

      ARMOUR       -> YES. 2,366 armour items, 710 priced, roughly 30%
                      across Arms / Helmets / Legs / Torso, and 17% on
                      Backpacks. The one hole is "Armor / Full Set" - 109
                      items, ZERO priced. Sets appear to be a UEX grouping
                      rather than a thing a shop sells individually.

      THRUSTERS    -> THE QUESTION CANNOT BE ANSWERED FROM THIS SOURCE, and
                      that is the honest result rather than a "no". UEX has
                      NO thruster category among its 100, and NOT ONE of the
                      7,932 items has "thruster" anywhere in its name. The
                      nearest thing in the whole taxonomy is
                      "Propulsion / Jump Modules" (3 items, all priced).
                      So this is not "thrusters are not sold" - it is "UEX
                      does not model thrusters as a purchasable item at all",
                      and answering the original question needs a different
                      source, not a different query. Reported as a gap
                      (rule 11) rather than filled with a plausible zero.

    OTHER THINGS THE TABLE SAYS THAT ARE WORTH A LOOK:
      * Liveries: 1,099 items, 19 priced, 1.7%. Confirms the B3 observation
        - liveries are pledge-store goods, not in-game shop stock. A low
        number here is not missing data.
      * "Commodities / Commodities" (category 36) holds 158 ITEMS with zero
        prices, while the separate commodity import has 147 of 204 priced at
        72%. Those are two different UEX representations of commodities and
        only one of them carries prices. Worth Sleven deciding which the site
        should show; both are stored and neither is guessed at.
      * 44 categories hold no items whatsoever. All returned HTTP 200 with
        envelope "ok". They are genuinely empty, not failed pulls.
      * 10 categories are at 100% coverage, 37 partial, 9 have items but no
        prices at all.

C6  DONE  8b61f66  checks/_verify_shop_checks.py - the negative control for
    all five auditors, BOTH halves, 24 assertions.
    Silence is measured as a DELTA, not as an absolute, because these run
    against 26,657 real rows that already legitimately trip C1, C3 and C5.
    For each auditor: run it and assert the planted subject is ABSENT, plant
    exactly one row that must trip it, run again and assert the subject is
    PRESENT. That is stronger than "it produced findings" - an auditor that
    fires on everything fails the first assertion, one that fires on nothing
    fails the second.
      C1  a 999,999,999 aUEC price in a ~100 aUEC category   -> FIRED
      C2  a terminal with a NULL location                    -> FIRED
      C2  a price row whose item does not exist              -> FIRED as DEFECT
      C3  two items sharing a display name                   -> FIRED
      C3  two items sharing a uuid                           -> FIRED
      C4  a category with items and no prices                -> FIRED, as
          LIMITATION rather than DEFECT
      C5  a price dated in the future                        -> FIRED as DEFECT
      C5  a 1,200-day-old price moves the over-a-year bucket -> FIRED
    C2'S HARD-ORPHAN BRANCH NEEDED THE FOREIGN KEY REMOVED to be observable
    at all - A7's FK makes the condition impossible to create, so the branch
    could never fire and an unobservable branch is precisely what rule 12
    says not to trust. The control drops the key, plants the orphan, watches
    C2 catch it, and rolls back. Postgres DDL is transactional so the rollback
    restores it fully, and a killed process rolls back too. The script then
    CONFIRMS from pg_constraint that all three FKs are back, and fails loudly
    if not. Verified: all three present afterwards, zero planted rows left.
    *** C6 FOUND A REAL DEFECT IN C3, which is the entire point of doing it.
    C3's per-kind branch reported only "worst case 2 share X" - so a NEW
    collision was INVISIBLE unless it happened to become the worst one, and
    the reader was handed a number they could not act on. The control failed
    on exactly that. C3 now lists the colliding names. The auditor was fixed;
    the control was not weakened to match it. ***

    WIRED IN: run_checks.py --group db now runs all five. Verified against the
    real findings store - 185 findings written, 11 checkers ok, 0 errored.

--- PHASE C COMPLETE. ------------------------------------------------------

D1  DONE  e94ded1  app/routers/shop.py - list + filter + detail over
    ItemCategory, Terminal and ShopItem, mounted at /api/v1/shop.
    THE ENVELOPE IS LOCKED, AND THE RIGHT WAY TO LOCK IT WAS NOT TO INVENT
    ONE. §D1 says lock it "before there are three consumers" - `Page`
    (items/total/limit/offset) is ALREADY locked by ARCHITECTURE_DECISIONS
    section 3, and a second envelope for these endpoints would give the site
    two pagination conventions to remember, which is the thing locking one
    prevents. The full written contract is at the top of the shop section of
    app/schemas.py: `total` ignores limit/offset so a client can compute page
    count; `limit` echoes what was APPLIED not what was asked, so a clamped
    request is visible rather than looking like the end of the data; ordering
    ALWAYS carries a unique tiebreaker, because paginating an unordered query
    silently repeats and skips rows and looks fine until page 4.

D2  DONE  e94ded1  /api/v1/shop/items/{identifier}/prices - one item, every
    terminal selling it, with resolved location and buy/sell SEPARATE.
    §D2 SAYS "item uuid ->" AND THAT ENDPOINT CANNOT WORK AS WRITTEN, for the
    A4 reasons: 2,162 items have no uuid (unreachable) and 120 uuids are worn
    by up to 10 items (ambiguous). So the path segment accepts a uuid, a UEX
    id, or a prefixed key - "item:1" / "commodity:1" - plus ?source_kind=.
    FOUND BY TESTING THE RUNNING API, WHICH IS WHY §D DEMANDS IT: my first
    version resolved a bare uex_id against uex_id alone, ignoring source_kind.
    GET /items/1/prices matched BOTH "Omnisky III Cannon" (item 1) and
    "Agricium" (commodity 1) and 409'd with advice - "re-request by uex_id" -
    that was useless to someone who had just done exactly that. Reading the
    code would not have shown this; the running server did, immediately. The
    409 now detects WHICH kind of ambiguity it hit and gives the matching
    advice.
    AMBIGUITY IS A 409 WITH ALL CANDIDATES, NEVER A SILENT PICK. Returning
    the first match would be the quiet version of the same defect the uuid
    collision causes upstream, and this is the last layer that can catch it
    before it reaches a page.

D3  DONE  e94ded1  /api/v1/shop/terminals/{uex_id}/inventory - the reverse.
    Paginated, filterable by category and source_kind.

D4  DONE  e94ded1  /api/v1/shop/search - name/slug substring, category,
    section, source_kind, buy-price range, priced_only.
    Results carry a price RANGE (min/max buy and sell), never an average -
    §3.1, and the surest way to never render an average as a price is for the
    API to have no field for one. Verified: no key anywhere in the response
    contains "avg".
    min_price above max_price is REFUSED with 422 rather than returning an
    empty list. An empty list there reads as "nothing is priced in that
    range", which is a false statement about the data rather than about the
    query.

    CONTROL FOR ALL OF PHASE D: checks/_verify_shop_api.py, 36 assertions,
    against a REAL uvicorn on a spare port over real HTTP - not a TestClient.
    That distinction is the point: a TestClient exercises the same handlers
    but proves nothing about the app starting or the router actually being
    mounted in main.py, and both have been real failures.
    §D's stated control is checked against all THREE wrong answers by name,
    because only one of them is obvious:
      500 -> the handler crashed. Loud, at least.        NOT observed.
      200 with an empty list -> THE DANGEROUS ONE. It says "this item exists
          and nobody sells it" about a thing that does not exist. §3.6 makes
          "nobody sells this" a real displayable answer, which is precisely
          what makes confusing the two expensive.        NOT observed.
      404 with an explanatory body.                      OBSERVED, correct.
    Also observed: a garbage identifier 404s rather than 500s; an over-large
    limit is clamped AND the response says so; a search matching nothing
    returns an honest 200 with total 0.

E1  DONE  a2823b3  testing/_deploy/find.html no longer invents anything.
    The block commented "invented data" - 17 made-up items across 9 made-up
    shops - is GONE, along with every view that read from it. `const LOC`,
    `const SHOP` and `const ITEM` are all absent, asserted by the control.
    The page now calls /api/v1/shop. API base is overridable with
    ?api=http://127.0.0.1:8077 so the page can be driven against a local
    server without editing the file, which is how it was verified.
    KEPT UNTOUCHED: the CSS, the header, the MOCKUP banner (see E2), and the
    Fan Kit disclaimer and trademark footer. The rebuild script REFUSES to
    write if either the banner or "Cloud Imperium Rights LLC" is missing from
    the preserved head - rule 8 made structural rather than remembered.
    ALSO ADDED, and it would have been a silent failure otherwise: CORS
    middleware in app/main.py. The site is Netlify and the API is Railway -
    different origins - and nothing had ever fetched across that boundary
    before, because find.html used invented data. Without it the browser
    blocks every request and the page shows "we cannot reach the price data"
    while the API is perfectly healthy: an outage that is not one. Verified
    over real HTTP in BOTH directions - an allowed origin gets the header
    back, and https://evil.example.com gets no access-control headers at all.
    GET and OPTIONS only, no credentials; a method wildcard would advertise
    POST and DELETE on an API that serves neither.

E2  BLOCKED  a2823b3  THE MOCKUP BANNER STAYS. E2 permits removing it only
    after "fetching the deployed URL and confirming real rows come back - not
    after a successful build, not after a successful deploy."
    THE DEPLOYED API IS DOWN. https://citizen-compass-production.up.railway.app
    returns HTTP 502 "Application failed to respond" on /health, on /docs and
    on /api/v1/shop/categories, each after roughly 15 seconds. So the
    confirmation E2 requires cannot be made, and the banner is not touched -
    not removed, not reworded, not softened.
    I CHECKED WHETHER MY PUSH CAUSED IT rather than assuming not: the app
    imports cleanly with an unreachable DATABASE_URL (simulated), so the new
    router and models are not breaking the boot. The Procfile is unchanged
    since f8d612d. I cannot see Railway's own logs from here and I have NOT
    tried to work around the 502 (rule 9) - it is reported as the answer.
    WHAT WOULD UNBLOCK IT: the Railway service coming back up, then a single
    fetch of /api/v1/shop/search?q=omnisky returning real rows. At that point
    the banner comes off and nothing else needs to change.
    ONE THING I DID CHANGE, and it is not the banner: the home page explainer
    said "Seventeen invented items across nine invented shops". That
    described the DATA, and the data is now real, so leaving it would have
    been false in the other direction. It now says the page reads live data
    and that the banner stays until the deployed API is confirmed.
    DECIDED-BY-DEFAULT, reverses in one line if Sleven disagrees.

E3  DONE  a2823b3  Buy and sell are SEPARATE COLUMNS on both the item page
    and the terminal page. Asserted by the control: a Buy header and a Sell
    header both present, and no key or text matching average/blended/avg
    anywhere in the rendered output. A missing side renders as a dash marked
    "no data" - never as 0, and the control checks that no price cell
    contains a bare 0. Section 3.1 end to end: NULL in the database, no
    averaged field in the API, blank on the page.

E4  DONE  a2823b3  Every price row renders "snapshot 20260801T235530Z -
    reported N days ago", and anything with no last_verified_patch is
    visibly flagged "not verified against a patch" rather than shown as
    though it were confirmed. Rows older than 30 days get the `old` class so
    stale data looks stale. All three asserted by the control.

    CONTROL FOR PHASE E: checks/_verify_find_page.mjs, 30 assertions.
    It loads THE PAGE OWN SCRIPT verbatim out of find.html into a node vm
    with the few browser globals it touches, and calls its real view
    functions against the running API - so it tests the page, not a
    reimplementation of it. Nothing was installed to get a browser (rule 7).
    STATED PLAINLY RATHER THAN GLOSSED: this does NOT prove browser layout,
    CSS, or real browser CORS enforcement. Those are unverified and the
    control says so in its own output rather than letting a green run imply
    otherwise.
    THE E CONTROL PASSES: a search matching nothing shows an honest empty
    state - not a spinner, not filler - and an unreachable API produces a
    visible explained failure rather than a "Looking..." that never resolves.
    THE HARNESS ITSELF HAD A BUG AND IT MATTERED. First version set the hash
    without a leading "#", so location.hash.slice(1) ate the first character
    and EVERY route fell through to home(). The search test still "passed",
    because the home page hint text happens to contain the word "Omnisky". A
    control that green-lights the wrong page is worse than no control, and it
    was only caught by the other assertions failing around it. Fixed, and the
    reason is written into the file so it is not reintroduced.

--- PHASE E COMPLETE except E2, which is BLOCKED on the Railway 502. --------

E-FIX  d187217  I EDITED THE BUILD OUTPUT INSTEAD OF THE SOURCE, and caught
    it before it cost anything. testing/_deploy/ is gitignored (344 MB of ship
    models), so the E commit went through carrying only app/main.py, the
    control and the ledger - find.html was silently not in it. Chasing that
    down found the real problem: testing/_src/find.src.html is the TRACKED
    SOURCE, and testing/_src/build_deploy.py line 587 maps
    ('find.src.html', 'find.html') - so the next build would have overwritten
    the entire E1 rewrite with the invented-data version, and the symptom
    would have been the mockup coming back on its own.
    Confirmed it was a plain copy before fixing: _src/find.src.html was
    BYTE-IDENTICAL to the pre-edit _deploy/find.html, so nothing else had
    diverged and copying the edited file back to source is exact.
    The change now lives in testing/_src/find.src.html, which is tracked and
    committed. _deploy and _src are identical, and
    testing/_src/check_deploy_clean.py reports "_deploy contains only known
    assets - safe to deploy".
    THIS IS RULE 14 FROM THE INSIDE. One artifact, one writer - and the
    writer for _deploy/find.html is build_deploy.py, not me. Writing to the
    output rather than the input is the same defect as a second writer, just
    with the loss deferred to the next build instead of the next save.

F1  DONE  ee91865  The 39 skipped ships, grouped by cause. The order
    predicted "most of the 39 share two or three causes" and that is exactly
    right - there are TWO, and one of them subdivides usefully.

    12  NO DECODED GEOMETRY. Model-side, nothing to do with mount data:
        ATLS, ATLS_GEO, Clipper, Defender, Eclipse, Javelin, MDC, Nova,
        Pulse, Pulse_LX, ROC, ROC-DS

    27  "no mount-data key's words appear in this model's name". This is the
        group worth splitting, because the label makes all 27 look like the
        same naming problem and only TWO of them are:

        2  A REAL, FIXABLE MATCHER BUG - the mount data EXISTS:
             Ares_Inferno -> mount key "Ares Star Fighter Inferno"
             Ares_Ion     -> mount key "Ares Star Fighter Ion"
           The matcher requires every word of the KEY to appear in the MODEL
           name. "Star" and "Fighter" are in the key and not in the model
           stem, so it refuses a pair that is obviously correct. The test is
           DIRECTIONAL, and that is the actual defect. Two ships, one rule.

       25  NOT A NAMING PROBLEM AT ALL - there is no mount data under any
           name, so the join is correctly reporting absence:
             no mount key contains the word at all (15): Crucible, Endeavor,
               Expanse, G12, G12a, G12r, Galaxy, Genesis, Kraken,
               Kraken_Privateer, Legionnaire, Liberator, Nautilus,
               Nautilus_Solstice_Edition, Odyssey, Orion, Pioneer, Ranger_CV,
               Ranger_RC, Ranger_TR, Vulcan
             sibling variants exist but not THIS one (4):
               Hull_D and Hull_E   - only MISC Hull A, B and C have mount data
               Zeus_Mk_II_MR       - only Zeus Mk II CL and ES have it
               E1_Spirit           - only A1 Spirit and C1 Spirit have it
           These are mostly concept and unreleased ships. Reporting them as
           "skipped" is correct; there is nothing to join them to.

    SO THE ACTIONABLE NUMBER IS 2, NOT 39. Fixing the directional word-match
    recovers Ares Inferno and Ares Ion. The other 37 are waiting on decoded
    geometry (12) or on CIG shipping the ship (25). Not fixed, per §F1 - the
    grouping is the deliverable.

F2  DONE  ee91865  The 7 unchecked_hull entries. ONE cause, and the design
    is already right.
    WHAT IT MEANS: the model borrowed a base ship's mount data, and the hull
    check that would confirm "this really is the same hull" could not run
    because the BASE ship has no .glb on disk to compare against. The builder
    already reports this rather than counting it as passed - the log says
    "HULL CHECK NOT PERFORMED ... Reported, not counted as passed". That is
    rule 12 already being obeyed, and it is why these 7 are visible at all.
    IT SPLITS 4 / 3, and the halves want different things:

      4  THE BASE MODEL IS ON DISK, under a different stem than the mount key
         names. A naming-convention gap, fixable with a mapping:
           Anvil_Ballista_Dunestalker  -> base "Ballista Dunestalker"
           Anvil_Ballista_Snowblind    -> base "Ballista Snowblind"
               ... both could compare against `Ballista`, which IS on disk
           Caterpillar_Pirate_Edition  -> base "Caterpillar Pirate"
               ... `Caterpillar` IS on disk
           F7C-M_Super_Hornet_Heartseeker_Mk_I -> base "F7C-M Hornet
               Heartseeker Mk I" ... `F7C-M_Super_Hornet_Mk_I` IS on disk

      3  THE BASE MODEL GENUINELY IS NOT THERE. Verified by exact stem:
           Cutlass_Black  - absent (Cutlass_Red, _Steel, _Blue are present)
           Dragonfly      - absent (Dragonfly_Black, _Yellowjacket present)
           Gladius        - absent (Gladius_Valiant present)
         Nothing to compare against until those three base models are built.

    Not fixed, per §F2. Note that the 4 in the first group must not be
    mapped blindly: `Ballista` is the base hull and Dunestalker/Snowblind are
    paint variants, which is exactly the case
    docs/DECISION_shared-hulls-are-fine-unless-the-shape-differs-2026-08-14.md
    rules on - the mapping is what lets the check RUN, and the check may still
    refuse the pair. That is the point of running it.

F3  DONE  ee91865  The cc-pending panel, and what it would now need.

    FIRST, A CORRECTION TO THE ORDER: there is ONE such panel, not two. It is
    at testing/_src/_layer.src.html:569 and appears a second time only as its
    own build output in testing/_layer.html:570. The `.cc-pending` CSS rule
    two hundred lines earlier is a style, not a panel. Searching the whole
    testing tree for its text returns exactly those two, one of which is
    generated from the other.

    IT SAYS: "Hardpoint and component data is not in the site file yet. It
    lives in PostgreSQL and reaches this panel once the API is wired in."

    PHASE D WIRED AN API. IT IS NOT THIS PANEL'S API, and the panel would
    still be empty today. What it actually needs:

      1. AN ENDPOINT THAT DOES NOT EXIST. The panel fills `#cc-slots` with
         pilot weapons / missile racks / turrets / shield generators for ONE
         SHIP. Every endpoint that exists lists components by CATEGORY
         (/api/v1/weapons, /missiles, /turrets) or ships (/api/v1/ships).
         There is no /api/v1/ships/{id}/hardpoints. That is the Loadout
         System, Priority 9 in ARCHITECTURE_DECISIONS and deliberately
         deferred - so this panel is blocked on a decision, not on wiring.

      2. THE PANEL'S OWN TEXT IS WRONG, and this is the useful finding.
         "It lives in PostgreSQL" is only half true. The COMPONENTS are in
         PostgreSQL. The HARDPOINT SLOTS are not - app/models.py has no
         hardpoint or mount table at all, and says so: "Hardpoint/loadout
         mount references (Priority 9, not built yet)". The slot data lives
         in data-layer/derived/holo-hardpoints-join/hardpoints_join.json, on
         disk, outside the database. So "wire in the API" would not fill this
         panel even with an endpoint - the join output has to be imported
         into a real table first, which is a schema item nobody has written.

      3. CORS, WHICH PHASE E ALREADY FIXED. The panel would have failed
         silently in the browser regardless of any endpoint, because the site
         is Netlify and the API is Railway and nothing had ever crossed that
         boundary. That blocker is gone now.

    So the honest order of work for that panel is: import hardpoints_join.json
    into a real table, then build the ship-loadout endpoint, then wire the
    panel - and correct its text, because it currently tells the reader the
    data is somewhere it is not.

--- PHASE F COMPLETE. ------------------------------------------------------

SWEEP  273ea61  Ran every control written in this session, back to back,
    after the last item. That found a regression I had introduced and not
    noticed, which is the argument for running the sweep rather than trusting
    that each item was green when it was written.
    B6 replaced uq_shop_items_uex_id with uq_shop_items_source_kind_uex_id.
    checks/_verify_shop_schema_db.py was still asserting the OLD name, so it
    failed - the bad row was still being refused, just by a different
    constraint. THAT IS THE HARNESS WORKING. It names the constraint that
    must do the rejecting precisely so a swap like this is visible instead of
    silent; had it settled for "an error was raised", the rename would have
    passed unnoticed and the harness would have been asserting something it
    no longer checked.
    Updated, and the B6 widening now has its own cases: the same uex_id under
    a DIFFERENT source_kind is OBSERVED being accepted, and a source_kind
    that is not one is OBSERVED being refused by ck_shop_items_source_kind_valid.
    FINAL STATE OF EVERY CONTROL:
      _verify_location_hierarchy.py        31 assertions
      _verify_location_hierarchy_db.py      8 assertions
      _verify_shop_schema_db.py            39 assertions (17 refusals observed,
                                              16 acceptances observed)
      _verify_shop_schema_db.py --self-test PASSED - the harness fails on demand
      _verify_shop_importers.py            15 assertions
      _verify_items_import_b5.py           10 assertions
      _verify_shop_checks.py               24 assertions (C6, both halves)
      _verify_shop_api.py                  36 assertions against a real server
      _verify_find_page.mjs                30 assertions against a real server
      TOTAL 193 assertions, all passing.
    E2 re-checked at the end of the run: the deployed API still answers 502
    on /health and on /api/v1/shop/search. Still BLOCKED, banner still on.

=== ORDER 2: docs/ORDER_the-502-the-rulings-and-the-ship-panels-2026-08-19.md ===
    Same run, same ledger, per that order's header. Items G1-G9.

G1  DONE  a2005ad  An absent database URL no longer takes the app down.
    app/database.py had `os.environ["RAILWAY_DATABASE_URL"]` as its fallback -
    a KeyError AT IMPORT, so uvicorn never binds and every route 502s. Now the
    app boots unconfigured, /health answers 200 with
    {"status":"degraded","database":"unconfigured","checked":[both names]},
    and every database-backed route answers 503 carrying that same reason.
    One change did all the routes: get_db() raises DatabaseUnconfigured and
    main.py registers a handler for it, so all 20-odd Depends(get_db) routes
    inherit the 503 without being edited.
    THREE ANSWERS, NEVER TWO: unconfigured / unreachable / ok. A wrong URL is
    not made silent - it reads "unreachable" and names the host that failed.
    /health issues SELECT 1 rather than inferring health from a string being
    present in the environment, because a health check that does not touch the
    database is a check that cannot fail.
    DECIDED-BY-DEFAULT: /health returns HTTP 200 even when degraded. A non-200
    is what platform health checks restart on, and a restart loop turns a
    diagnosable degraded boot straight back into the uniform 502 this item
    exists to remove. The status is in the body where something can read it.
    Reverses in one line if Sleven wants 503.
    Also: the URL password is redacted out of driver error strings before they
    go over HTTP. /health is public and unauthenticated, and per L1 this run
    has already leaked one credential.

G2  DONE  a2005ad  One line at import to stderr naming which variable supplied
    the URL, or that none did. Once, not per request.
    DECIDED-BY-DEFAULT: stderr directly, not the logging module. At import time
    the root logger has no handlers, so an INFO record goes nowhere - a startup
    diagnostic that can be silently swallowed is precisely the failure G1
    exists to remove. stderr rather than stdout so scripts that emit parseable
    output on stdout stay clean; platform collectors capture both. One line to
    swap if a logger is wanted.

CONTROL  a2005ad  checks/_verify_degraded_database.py - 31 assertions, all
    passing. Three real subprocesses, three environments, three REQUIRED
    DIFFERENT answers:
      CASE 1 neither variable set  -> boots (returncode 0), /health 200
             degraded/unconfigured naming BOTH variables, db route 503 with
             the same reason in its body, /docs still 200, ONE startup line.
      CASE 2 real DATABASE_URL     -> /health ok, SELECT 1 came back, and the
             db route returned REAL ROWS. This is the load-bearing one: a
             degraded mode that never leaves degraded is worse than the crash.
      CASE 3 dead host             -> degraded/UNREACHABLE, not unconfigured,
             names the failing host, and does NOT echo the URL password back.
    --self-test inverts every assertion and exits 1. The failure path has run.
    NOTE ON THE CONTROL'S OWN TRAP, because it nearly was a silent success:
    the subprocesses set the variables to "" rather than unsetting them.
    app/database.py calls load_dotenv() and this repo HAS a .env with a real
    DATABASE_URL, so unsetting would let dotenv put it back and CASE 1 would
    have tested nothing while reporting green. Empty and unset take the
    identical branch, and CASE 0 asserts that equivalence against a cleared
    os.environ rather than assuming it.
    C1'S POINT IS CONFIRMED AND WORTH RESTATING: the previous test simulated an
    UNREACHABLE url. create_engine is lazy, so that case always booted fine and
    never could have caught this. CASE 3 now asserts that boot explicitly, so
    the distinction is written down in the harness rather than in a memory.

G3  DONE  0b8e700  The Ares matcher runs both ways, and the 25 are asserted BY
    NAME rather than by count.
    THE FIX: the rule was directional - every word of the mount-data KEY had to
    appear, in order, inside the MODEL name - so a key LONGER than the filename
    was refused. "Ares Star Fighter Inferno" vs Ares_Inferno went looking for
    "star" and "fighter" in a two-word name. Second pass added, run ONLY where
    the first found nothing: the model name's words inside the key, SHORTEST key
    winning (the mirror of longest winning in pass 1 - in both, the winner is
    the candidate with the fewest words the other side did not account for).
    WHY IT IS A FALLBACK AND NOT A WIDENING: loosening pass 1 would put every
    currently-resolving ship back in play. Running pass 2 only where pass 1
    found nothing makes the set of ships whose answer CAN change exactly the set
    that matched nothing. Structural, not a hope.
    THE ACCEPTANCE NUMBER DID NOT COME OUT AS 31/37 AND HERE IS WHY. Re-running
    the build gave 35 placed / 8 refused / 25 skipped. That is NOT the matcher
    over-reaching. Two things changed at once: the geometry directory had to be
    regenerated (it is 30MB of derived vertex data, not in the repo, and the
    previous run's copy was MISSING TWELVE MODELS - which is why twelve ships
    were skipped for "no decoded geometry", a cause no matcher touches). All 235
    models are now decoded via testing/_src/decode_glb_points.js.
    So the acceptance was established by EXPERIMENT rather than by comparing
    against a remembered number - checks/_verify_g3_matcher_delta.py runs the
    SAME BUILD over the SAME GEOMETRY twice, once per matcher, and diffs:
        bucket           pass 1    both   delta
        placed               33      35      +2
        skipped              27      25      -2
        refused               8       8      +0
        rule                 20      22      +2
    gained = exactly {Ares_Inferno, Ares_Ion}; lost = nothing. THE MATCHER'S
    CONTRIBUTION IS EXACTLY TWO. C1's "not 12" is satisfied and so is "not 27".
    THE 8 REFUSED are the newly-decodable ships failing the SHAPE check with
    measured errors - ATLS_GEO 0.51, Clipper 0.66, Defender 0.60, Eclipse 0.54,
    Nova 0.37, Pulse and Pulse_LX 0.53, and Javelin for having no published
    dimensions at all. That is the guard working on data it had never seen, not
    a regression. They are reported, not placed.

CONTROL  0b8e700  checks/_verify_hardpoint_join.py - 73 assertions, all passing
    (was 46). What is new:
      * The two Ares flipped from "must resolve to NOTHING" to "must resolve".
        THAT ASSERTION WAS ALWAYS WRONG and the build's own docstring said so
        in the same repo - it records that "Ares Inferno" and "Starfighter
        Inferno" ARE the same ship. Flipped deliberately and noted, not quietly
        relaxed.
      * All 25 must-not-match ships named individually. Where the list comes
        from, so it is checkable: 39 skipped = 12 "no decoded geometry" (a
        different cause) + 27 name refusals; 27 - 2 Ares = 25.
      * A whole-disk diff of old matcher vs new over all 235 models, requiring
        every changed answer to have moved FROM NOTHING - pass 2 can never
        override an answer pass 1 already gave.
    checks/_verify_g3_matcher_delta.py - 8 assertions, all passing. Reports NOT
    PERFORMED (exit 2) when CC_GEO_DIR is unset rather than passing quietly, and
    restores all three build artifacts afterwards so an A/B cannot leave the
    repo holding the losing arm of its own experiment.

G3-FINDING  0b8e700  PASS 2 INDEPENDENTLY DERIVES 11 OF THE 13 HAND-WRITTEN E1
    MAPPINGS - every Aurora, all three Hercules, the M50, the Mercury, the C8R
    Pisces - AND AGREES WITH ALL ELEVEN. E1 still wins because the build checks
    it first, so nothing about today's output depends on this.
    NOT ACTED ON. Deleting E1 entries is not what G3 asked for, and a mapping
    that agrees with the rule costs nothing while it agrees. But the rule now
    covers most of what E1 was written for, and that is worth knowing before
    anyone adds a fourteenth line by hand. The two it does NOT derive are
    600i_Explorer (pass 1 already had it) and Khartu-Al (a capitalisation the
    tokeniser already flattens) - so E1's remaining unique value is close to
    zero. Sleven's call, not mine.

G4  DONE  f9da271  C7 exists - the Stims conflict is now a CHECK rather than a
    line in this ledger, per R3.
    checks/shop_checks.py gains source_duplicate_check, registered in CHECKERS
    as "shop_source_duplicate". It reads the LANDED SOURCE FILES, not the
    database: by the time the rows reach item_prices the importer has already
    resolved the duplicate, so no database-side checker could ever see this.
    FIRES on a (item|commodity, terminal) pair listed more than once in ONE
    file at DIFFERING prices. DOES NOT FIRE on a byte-identical repeat, and
    that distinction is the whole design - four of the five repeats in the
    08-06 commodity file are byte-identical, so flagging them would bury the
    one that matters four deep. WARNING, never DEFECT: neither price is
    knowably the wrong one.
    ON REAL DATA RIGHT NOW: exactly one finding across every landed price file.
      20260806T033315Z/commodities_prices_all.json  WARNING
        'Stims' at 'HUR-L5' twice: buy 0 / sell 5800, buy 0 / sell 4900.
      20260801T235530Z/items_prices_all.json        PASS  23,734 rows, 0 repeats
    FLAG ONLY. It never resolves a conflict, never picks a price, never writes.

CONTROL  f9da271  checks/_verify_source_duplicate_check.py - 22 assertions, all
    passing; --self-test exits 1. Both halves per G4: a planted conflict fires
    it once and reports BOTH prices; a planted byte-identical repeat does not
    fire, and the PASS still SAYS the repeat was seen and dismissed rather than
    pretending the file was clean.
    THE MUST-NOT-FIRE CASES ARE THE LOAD-BEARING ONES, because the realistic
    failure of a duplicate detector is not missing a conflict - it is calling
    everything one:
      * same commodity, two DIFFERENT terminals, different prices  -> silent
        (that is the normal state of the universe)
      * two different commodities at one terminal                  -> silent
      * a repeat agreeing on buy/sell but differing on a rolling AVERAGE
        -> silent. An average is not a price and S3.1 forbids showing one as
        if it were, so a disagreement about one is not a conflict about
        anything a visitor sees.
    Also proven: it scans the ITEMS file and not only commodities; two
    snapshots do not contaminate each other and the clean one is named clean;
    a valid envelope whose `data` is null does not crash it; and NO SNAPSHOT
    DIRECTORY reports NOT PERFORMED, never PASS - the landed snapshots are
    gitignored, so on a fresh clone this checker sees nothing, and "saw
    nothing" reporting PASS is exactly SILENT SUCCESS.
    Separate file from _verify_shop_checks.py because C7 needs no database. It
    plants files in a temp directory, so it still runs where postgres does not.

G5  DONE  7146474  R1's commodity cross-reference exists. LINKED, NOT MERGED,
    NOTHING DELETED.
    New table shop_item_commodity_xref (migration d3115d32c70d, additive - one
    new table, no column touched on shop_items, nothing dropped). A TABLE and
    not a column because a link is not a property of either row; and not a
    merge because collapsing the two would destroy the evidence they DIFFER,
    which is the one thing this pair is informative about - the item side says
    "Aslarite (Raw)" and the commodity side says "Aslarite (Ore)".
    Backup taken first per rule 4: C:\cc-backup\20260819-220221, exit 0,
    0 failures, bundle verified 42.4MB, dump 1982.2KB and RESTORE-TESTED. The
    "232 ships, expected 254" warning is the pre-existing one from L3 - the
    live database genuinely holds 232 and the expectation constant is stale.
    MATCHED ON NAME, because there is nothing else: not one of the 204
    commodities carries a uuid and the two id spaces COLLIDE rather than
    correspond. Two tiers, recorded per row in match_method so dropping the
    weaker one is a WHERE clause rather than an argument:
        exact_name  156   identical once case and punctuation are normalised
        token_set     1   the same words reordered: "Raw Ice" / "Ice (Raw)"
    THE NUMBER R1 ASKED FOR - 157 of 158 linked, and THE ONE THAT DID NOT is:
        Boron
    That is the whole unmatched list. It is not a near-miss either: the
    commodity side has no name containing "oron" anywhere, so Boron exists as a
    category-36 item and does not exist as a commodity at all.
    THE OTHER DIRECTION, since it answers a different question: 47 of the 204
    commodities have NO item-side counterpart - Aphorite, Hadanite, the Kopion
    Horns, the Luminalia and Year-of-the-X gift items, and 40 more.
    AND THE POINT OF THE EXERCISE AS A NUMBER: 118 of the 157 links reach at
    least one price row. That is what a category-36 item gains by being linked,
    since not one of them carries a price of its own.
    DECIDED-BY-DEFAULT: the token_set tier exists at all. "Raw Ice" and "Ice
    (Raw)" are the same substance and a rule (same words, any order) catches it
    without guessing, but it IS a weaker claim than an identical name, so it is
    stored as a separate method rather than folded in. Reverses with
    DELETE ... WHERE match_method='token_set' - or by ignoring it in a query,
    which touches nothing at all.
    NO FUZZY MATCHING BEYOND THOSE TWO RULES. A wrong link would put one
    substance's prices under another substance's name, which is the same class
    of error as a Gladius wearing a Hammerhead's hardpoints. Ambiguity would be
    reported and NOT linked - same reasoning as the D2 409.

CONTROL  7146474  checks/_verify_commodity_xref.py - 27 assertions, all
    passing; --self-test exits 1.
      * The matcher driven BOTH ways. The load-bearing negative is
        "Aslarite (Raw)" vs "Aslarite (Ore)" under the TOKEN rule: if that ever
        collapses, every raw ore inherits its refined twin's prices. Also
        proven the rule is not collapsing everything to one key.
      * All four constraints OBSERVED REFUSING, each naming the constraint that
        must do the rejecting rather than settling for "an error was raised":
        uq_..._item, uq_..._commodity, ck_..._distinct, ck_..._method_valid,
        plus the foreign key. Two acceptance cases alongside, because every
        constraint could be CHECK(false) and the refusals would still pass.
      * R1's OWN REQUIREMENT, which is the half worth being careful about:
        158 category-36 items and 204 commodities still counted afterwards,
        every link pointing at one surviving ITEM and one surviving COMMODITY,
        and the item side still carrying ZERO prices - the link copied nothing
        across, which is what "link, do not merge" has to mean to be checkable.
    THE --dry-run FLAG WAS PROVEN BY BEHAVIOUR, not by reading it: row count
    before the dry run 0, after the dry run 0, after the real run 157.

L4  NOTE  2026-08-19  RULE 3, AND I DID IT BEFORE I CAUGHT IT. The first draft
    of _verify_commodity_xref.py ran `DELETE FROM shop_item_commodity_xref`
    against the REAL database, inside a transaction it then rolled back, so the
    unique constraints would collide with its own rows instead of production
    ones. It rolled back correctly and no data was lost - verified, 157 links
    still held afterwards.
    It was still a hard-rule-3 violation. The rule says never DELETE FROM a
    database this process did not create, and it makes NO exception for "inside
    a transaction I meant to roll back" - a script that dies between the DELETE
    and the rollback is exactly the accident the rule is written against.
    REWRITTEN: the control now seeds its own four throwaway shop_items rows at
    sentinel uex_ids and drives the constraints against those, the way
    _verify_shop_schema_db.py already did. No DELETE remains anywhere in it.
    Reported rather than quietly fixed, per rule 11.

G6  BLOCKED  (no commit - nothing changed, deliberately)  The deployed API is
    STILL 502. Fetched twice just now:
        GET https://citizen-compass-production.up.railway.app/api/v1/shop/search?q=omnisky
            -> HTTP 502 Bad Gateway, no body
        GET https://citizen-compass-production.up.railway.app/health
            -> HTTP 502 Bad Gateway, no body
    THE BANNER STAYS ON. No real rows came back, so nothing is removed. Not on
    a build, not on a deploy, not on a local server, not on a good feeling.
    testing/_deploy/find.html line 92 still reads
    "MOCKUP - prices and shops are invented" and I did not touch it.
    Not retried through curl, a proxy, a cache or an archive - rule 9. Two
    fetches, both 502, that is the answer.
    WHAT WOULD UNBLOCK IT: a deploy of the current main to Railway. Note that
    G1 CANNOT have fixed tonight's 502 by itself, because G1 is only in git -
    the running service is still the old code. What G1 buys is that the NEXT
    time this happens, /health answers instead of 502-ing, and says whether the
    fault is an absent variable or an unreachable database. Tonight it cannot
    tell us anything, because the process that would answer is the one that is
    not running.
    Which also means the two candidates from the order's S2 are still both
    live: a missing DATABASE_URL, or the service simply not running. I have no
    Railway access and did not look for any.

G7  DONE  a521689  THE COLLECTOR BUILDS, AND THE BYTE SAYS 2.
    `build.ps1 -Both` exit 0. Both binaries built clean off 9271f6d's 1,073
    lines of Win32 registry and shortcut code, which nobody had compiled.
      collector.exe          PE subsystem 2  WINDOWS_GUI (no console)
      collector-master.exe   PE subsystem 2  WINDOWS_GUI (no console)
    READ BY A SECOND READER, NOT TAKEN FROM THE BUILD SCRIPT. build.ps1 already
    reads the byte and refuses to finish if it is not 2 - right design, and it
    is why this cannot ship again - but that is the build script grading its own
    homework, and the whole history of this defect is a claim about a build flag
    nobody checked against the artifact. checks/_verify_pe_subsystem.py reads
    the bytes again in a different language.
    AND THE READER IS PROVEN. It builds a deliberately CONSOLE binary into a
    temp directory (outside the repo, never installed, never released) and
    requires the reader to return 3. A reader that returned 2 for everything
    would have "confirmed" every binary ever built, including the two broken
    ones that shipped.
    -selftest ON collector.exe: PASS. 0 failures across 584 checks.
    ONE THING WORTH KNOWING BEFORE SOMEBODY MISREADS IT, because I did for
    about a minute: running `collector.exe -selftest` from a shell prints
    NOTHING and exits 0. That is not a silent success - a subsystem-2 binary
    has no console, so the selftest writes collector-selftest-results.txt
    instead, 70KB of it, ending "selftest PASS". The empty terminal is the
    correct behaviour of the fix, not a symptom.
    NOTHING RELEASED, NOTHING INSTALLED, NOTHING PACKAGED. The previous
    collector.exe and collector-master.exe were COPIED ASIDE to
    *.pre-G7-20260819 before the rebuild rather than overwritten - rule 1
    applies to a build output as much as to anything else.

G7-FINDING  a521689  FOUR SELFTEST CHECKS ARE INTERMITTENT, AND AN INTERMITTENT
    CHECK IS NOT ONE. The console-subsystem control binary failed 5 checks on
    its FIRST run and 1 on its second. The one that repeats is correct and
    welcome: "CONSOLE: this binary is a GUI build (PE subsystem 2)" fails on a
    console build, which is the selftest's own subsystem guard firing on
    demand - a third independent confirmation that the guard works.
    The other four did not recur:
      staleness warning fires on a dead log
      staleness warning names the fix
      staleness warns once per stall, not every poll   (NOT PERFORMED)
      a log that starts growing again is NOT reported stale  (NOT PERFORMED)
    They pass in the real collector.exe and passed on the control's second run,
    so this is timing sensitivity in the staleness fixture, not a subsystem
    difference - nothing in that code path reads the subsystem. Reported, not
    fixed: touching the collector is explicitly out of scope for this run, and
    a check that passes or fails depending on how busy the machine is cannot be
    trusted in either direction. Worth an order of its own.
    A third run of the control selftest HUNG and was killed at 10 minutes,
    which may be the same fixture. Recorded as observed; not investigated,
    same scope reason.

G8  DONE  e78a71e  The Loadout panel stops saying "awaiting data" and the text
    above it stops being false.
    FIRST, A CORRECTION TO THE ORDER, and it is the same one F3 already made:
    there is ONE cc-pending panel, not two. G8's wording ("the two cc-pending
    panels") carried the original miscount forward. The `.cc-pending` CSS rule
    is a style, not a panel.
    SECOND, THE ORDER'S PREMISE WAS NOT QUITE RIGHT EITHER. G8 says "there is
    now an API to give it to them - wire them." There was not. F3's finding was
    that the hardpoint SLOTS were not in PostgreSQL at all - the components
    are, the slots were two derived JSON files on disk, and app/models.py had
    no hardpoint table of any kind. Wiring the shop API to this panel would
    have filled nothing. So the work was the whole chain, in the order F3 said:
    import, then endpoint, then panel, then text.
    WHAT NOW EXISTS:
      ship_hardpoints          2,195 slots across 202 models
      ship_hardpoint_coverage    235 models - 198 placed, 25 skipped,
                                 8 refused, 4 present-but-mountless
      GET /api/v1/ships/models/{model}/hardpoints
    Migration 71d65b7b4026, additive: two new tables, nothing dropped, no
    column added to anything that existed. Backup from G5 still current - no
    further destructive step was taken.
    THE COVERAGE TABLE IS THE HONEST HALF. Without it "we have not measured
    this hull" and "this hull has no mounts" are the same blank panel, and
    showing the same nothing for both is the polite version of making something
    up. Every absence carries the build's OWN reason, verbatim, so the panel
    can say why it is empty.
    KEYED BY MODEL, NOT BY SHIP. The positions were measured off a mesh; ships
    share meshes (that is the whole shared-hulls ruling); and the page already
    resolves ship -> model to load the 3D view. It asks with the key it is
    already holding, so NO new ship-to-model matching is invented anywhere.
    THIS IS NOT THE LOADOUT SYSTEM, and I checked before building rather than
    after. ARCHITECTURE_DECISIONS defers Priority 9 - specifically
    "compatibility rule placement" - deliberately. Nothing here expresses a
    compatibility rule and no slot carries a component FK. The locked decision
    says such a reference must point at the components BASE table's primary
    key; this shape takes that as an added column, not a rewrite.
    THREE ANSWERS, AND THEY STAY THREE: 200 with slots / 200 with none plus a
    reason / 404 for a model nobody has heard of. Collapsing the middle one
    into either neighbour is the entire failure the endpoint exists to avoid -
    a 404 for "no data" tells the page the ship does not exist, and a bare
    empty 200 gives it nothing to say.
    EDITED IN THE SOURCE, per rule 14: testing/_src/_layer.src.html, then
    rebuilt through build_deploy.py. The build's own gates passed, including
    its inline-JS parse of all 12 blocks and its deploy guard. testing/_deploy
    is gitignored so the built page is not in the commit - re-run the build.

CONTROL  e78a71e  checks/_verify_ship_hardpoint_panel.mjs - 16 assertions
    against a REAL running API, driving the G8 block sliced VERBATIM out of the
    BUILT page rather than a re-implementation.
    G8'S NAMED CONTROL, both halves of it:
      Kraken (no slot data) -> "No hardpoint data for this hull - neither this
      model's name nor any mount-data key contains the other's words in order."
      A sentence, carrying the build's own reason. NOT a spinner: the loading
      message is asserted GONE. NOT invented values: asserted against
      awaiting/pending/coming-soon/TBD/em-dash filler.
    And the distinctions that matter next to it:
      an UNKNOWN model reads differently from a known-but-unmeasured one
      a ship with no model folder says that, rather than querying for ''
      an UNREACHABLE API resolves to a sentence naming the API - not
        hypothetical, the deployed API has been 502 all evening
      no mount renders as "S0" - an unstated size is omitted, never zeroed
    STATED LIMIT, not glossed: this proves the panel's LOGIC and the HTML it
    produces. It does not prove layout, CSS, or a browser's CORS enforcement.
    Same limit and same reason as _verify_find_page.mjs - no browser on this
    machine and nothing was installed to get one (rule 7).

G9  DONE  (ledger commit)  SWEEP - every control in checks/ re-run back to
    back, 31 of them, WITH a live API server up so the HTTP and page controls
    ran for real rather than skipping.
    31 CONTROLS RUN, 0 NON-ZERO. Full list, in run order:
      _verify_absence_pass                 22 assertions
      _verify_broken_checker_end_to_end    12
      _verify_commodity_xref               27   (G5, new)
      _verify_degraded_database            31   (G1/G2, new)
      _verify_find_page.mjs                30   against the live server
      _verify_findings_store               36
      _verify_fingerprint_history          PASSED
      _verify_g3_matcher_delta              8   (G3, new)
      _verify_hardpoint_alignment          PASSED
      _verify_hardpoint_join               73   (G3, was 46)
      _verify_items_import_b5              10
      _verify_lifecycle                    PASSED
      _verify_location_hierarchy           31
      _verify_location_hierarchy_db         8
      _verify_missing_encoding             19   (7 bad caught, 11 good ignored)
      _verify_never_delete_guard           15
      _verify_node_checks                  PASSED
      _verify_pe_subsystem                  3   (G7, new)
      _verify_pull_and_clear               PASSED
      _verify_schema_checks                PASSED
      _verify_ship_configurations          PASSED
      _verify_ship_hardpoint_panel.mjs     16   (G8, new) against the server
      _verify_shop_api                     36   against a real HTTP server
      _verify_shop_checks                  24
      _verify_shop_importers               15
      _verify_shop_schema_db               39   (17 refusals, 16 acceptances)
      _verify_snapshot_shape               PASSED
      _verify_source_checks                24
      _verify_source_duplicate_check       22   (G4, new)
      _verify_testing_stamp                PASSED
      _verify_unreleased_content           PASSED
    G1 CHANGED THE ENGINE - app/database.py - which every check that opens a
    session imports. That is exactly the change that breaks things far away,
    and it is why this sweep mattered more than usual. Nothing broke. The
    degraded path is inert when a URL is present: engine, SessionLocal and the
    preservation guard are all constructed exactly as before.
    AND THE SWEEP ITSELF WAS PROVEN NOT TO BE A MASS SILENT SUCCESS. Every
    harness carrying a self-test was run in that mode:
      _verify_degraded_database     --self-test  exit 1  (assertions inverted)
      _verify_source_duplicate_check --self-test exit 1
      _verify_commodity_xref        --self-test  exit 1
      _verify_shop_schema_db        --self-test  exit 0 - DIFFERENT CONVENTION,
        not a defect: that one plants three specific harness defects (a refusal
        the database accepts, a refusal by the WRONG constraint, an acceptance
        the database rejects) and exits 0 when it CATCHES all three. Its output
        says so in as many words. Noted rather than "fixed" - it is arguably
        the better design, since it names the failure modes instead of flipping
        every boolean.

---

# H RUN - docs/ORDER_generated-price-data-and-the-guard-2026-08-20.md
# Same ledger, per the order. Appended below the G run, nothing above rewritten.

H1  DONE  <sha>  THE GENERATOR. build_find_data.py reads PostgreSQL and writes
    ONE file, testing/_src/find_data.gen.js, in the same style and place as
    holo_data.gen.js and loadout_data.gen.js.
    THE NUMBER THE ORDER ASKED FOR: 969.8 KB raw -> 188.7 KB GZIPPED.
    Under the 250 KB ceiling, and 18% over C1's measured 160 KB. The miss is
    explained rather than waved at, and it is not a shape change:
      * C1 measured 23,734 price rows. The database holds 26,657 - the extra
        2,923 are the commodity prices imported at B6 and cross-referenced at
        G5, which did not exist when C1 measured.
      * Every price row carries its SNAPSHOT INDEX, per R6. C1's stated row
        shape was (terminal, buy, sell).
      * Every terminal carries its resolved_path, so the page can name a place
        without a second lookup.
    I DID NOT SHARD IT. One file, as ruled.
    IT WENT OVER FIRST, AND I MEASURED RATHER THAN GUESSED WHY. The first
    render was 333.5 KB gzipped - a 108% miss, which by the order's own test
    means the shape changed, and it had: I had added the item UUID, which is
    not in H1's field list. 5,566 uuids of random hex are INCOMPRESSIBLE BY
    CONSTRUCTION and cost 138 KB gzipped on their own - 80% of the final file
    for a field no route uses. Every link on the page is keyed on
    (source_kind, uex_id), which is the actual database key, and the API still
    serves the uuid. Dropped from the file, and the docstring records the
    measurement so the next person does not re-add it and re-discover this.
    The second trim is not a trim at all: UEX's per-row last-modified date is
    127 distinct values across 26,657 rows, so the row carries an index into a
    date table instead of a 12-byte string. Same fact, a fifth of the bytes.
    NO GENERATION TIMESTAMP. Nothing in the output is read from a clock, so two
    runs against an unchanged database are byte-identical - that is H6's
    negative half and it is asserted on every run by --verify-stable, not left
    to be noticed a year later in a churning diff.

CONTROL  <sha>  checks/_verify_find_data.py - 34 assertions, and every gate is
    run against something that MUST fail it.
    H1'S NAMED CONTROL is "row counts in the file equal row counts in the
    database. Assert it." It is asserted, and then it is BROKEN ON PURPOSE
    three ways - one price row removed, one item removed, one terminal removed -
    and required to catch each and to NAME the table it caught. The count is
    taken by walking the emitted structure, not by reading back the number the
    collector remembered, so it cannot pass by comparing a variable with
    itself.
    THE SIZE CEILING IS PROVEN THE SAME WAY: run with --max-gzip-kb 1, the
    generator must refuse, must say TOO BIG, must report the actual number, and
    must have written NOTHING. A ceiling that has never fired is a number in a
    comment.
    THE STALENESS GATE TOO: a file on disk that does not match the database is
    caught, and so is a file that is absent entirely - reported as STALE rather
    than crashing on the open.
    --self-test inverts every expectation and exits 1.

H2  DONE  <sha>  FIND READS THE FILE. Every fetch() is gone from this page's
    read path. Search, the category filter and the price range all run in the
    browser over find_data.gen.js.
    WHAT IS GONE: API_BASE, the Railway hostname, the ?api= override, the four
    api() calls, the apiDown() handler and the "Looking..." placeholder that
    existed because a network round trip could be slow. None of it has a job
    any more - the answer is already in memory when the page loads.
    WHAT REPLACED IT: indexes built once at load. 7,932 items keyed by
    "item:1234" / "commodity:12" (the same route shape the API used, so no link
    changes), a lowercased name array for search, per-item aggregates, and a
    terminal -> rows map. Search ranks exact name, then prefix, then
    word-start, then substring - and the ranking is stated on the page rather
    than left as a mystery.
    THE FILTERS RIDE IN THE HASH, so a filtered search is a link somebody can
    send. #s/omnisky?c=12&min=100&max=5000.
    THE PAGE STILL HAS ONE FAILURE MODE AND IT SAYS SO: if find_data.gen.js is
    missing from the deploy, the page says exactly that. It does not render a
    blank screen, and it does not report it as a search that found nothing -
    those are different sentences and a visitor deserves the right one.

CONTROL  <sha>  checks/_verify_find_page.mjs, rewritten - 57 assertions, THE
    NETWORK BLOCKED THROUGHOUT.
    H2's named control is "with the network blocked after first load, search
    still works", so the network is blocked properly rather than hoped about:
    fetch, XMLHttpRequest, WebSocket, EventSource and navigator.sendBeacon are
    all replaced with functions that THROW. And then - because a blocker that
    does not block is precisely the silent success this project keeps
    finding - the harness CALLS the poisoned fetch itself and requires the
    throw. Without that, this suite would pass just as happily for a page that
    fetched.
    The page's own script is sliced out of the BUILT find.html and run against
    the shipped find_data.gen.js. No re-implementation.
    ONE REAL DEFECT FOUND IN THE CONTROL ITSELF AND FIXED RATHER THAN WORKED
    AROUND: "no fetch( in the page" was reading the page's own header comment,
    which says "every fetch() is gone", and failing the page for explaining
    itself. The fix strips comments for the code-shape assertions - and the
    stripper is ITSELF asserted, because a stripper that removed everything
    would also hide a real fetch somebody had commented out.
    ALSO PROVEN: the category filter and the price range actually narrow the
    set (7,932 -> 136 under 100 aUEC, 147 over 100,000, and the two are not the
    same set); every price row carries the snapshot date and not just the page
    header, counted row for row; a missing data file produces a sentence rather
    than a blank; and the MOCKUP banner and both pieces of legal text are still
    byte-for-byte present, because H3 has not happened yet.
    --self-test inverts every expectation and exits 1.

    STATED LIMIT, unchanged and not glossed: this proves the page's logic and
    the HTML it produces. It does not prove layout, CSS or real browser
    behaviour. There is no browser on this machine and none was installed
    (rule 7).

H3  DONE  <sha>  THE BANNER IS OFF, AND IT CAME OFF THE ONLY WAY IT WAS EVER
    ALLOWED TO: a fetch of the deployed URL that returned real rows.
    G6 was BLOCKED on this three days running. It is unblocked because the
    source changed, exactly as C1 predicted - not because Railway came back.
    Railway was never asked. The deployed page now carries its own data.
    THE SEQUENCE, in the order it happened, because the order is the evidence:
      1. Dry run first. deploy_testing.ps1 -WhatIf. Its deploy guard REFUSED -
         find_data.gen.js was an unknown file that would have been published.
         Correct refusal: check_deploy_clean.py keeps a standalone allow-list
         that does not derive from PAGES, by design, and it had not been told
         about the new file. Added, with the reason, beside the other entries.
      2. Second dry run: guard clean, 495 files, 350.7 MB, "Nothing was
         uploaded".
      3. THE -WhatIf NO-OP PROVEN FROM OUTSIDE, not read off the script.
         Fetched /find_data.gen.js from the deployed origin: HTTP 404. The dry
         run published nothing, and that is established by the served site
         rather than by the flag's own claim (rule 12, the setup_checks_task
         lesson).
      4. Real deploy. 3 files changed, 492 already uploaded.
      5. VERIFIED FROM THE SERVED BYTES. 26,657 price rows came back over
         HTTPS, and the page's own script - sliced out of the SERVED html, run
         against the SERVED data - rendered the Omnisky III Cannon at 6 named
         terminals with prices in aUEC and the snapshot date on every row.
      6. ONLY THEN the banner came off, and the page was deployed again.
    WHAT REPLACED IT is not a reassurance, it is the provenance: a badge
    reading "UEX player reports - snapshots taken 2026-08-01 and 2026-08-06",
    WRITTEN FROM THE DATA FILE rather than typed into the markup, so it cannot
    describe a snapshot the page is not holding. Its DEFAULT text - the one
    sitting in the HTML, shown if the data file fails to load - is "price data
    not loaded". The failure case makes no claim at all.
    RULE 8 UNTOUCHED. The Fan Kit disclaimer and the trademark footer were not
    edited, and both are asserted present in the SERVED bytes.

CONTROL  <sha>  checks/_verify_find_deployed.mjs - 21 assertions, every one of
    them against https://citizencompasstesting.citizencompass-contact.workers.dev
    over the wire. Nothing is read off local disk and there is NO FALLBACK to a
    local copy: if the fetch fails the harness reports NOT VERIFIED and exits
    non-zero, because "we could not look" must never be recorded as "we looked
    and it was fine".
    It does not accept a 200 as evidence - a mockup returns 200 too. It loads
    the served script, feeds it the served data, and requires a named item at a
    named terminal with a price and a snapshot date. --self-test inverts every
    expectation and exits 1.

H4  DONE  <sha>  SAY WHAT IS PROVABLE, AND NOT MORE. The order says this is the
    one item where the wording IS the deliverable, so it is not paraphrased
    into something smoother anywhere on the page.
    THE WORDS, in README-FOR-TESTERS.txt's voice - short sentences, addressed
    to the person reading, no salesmanship:
      "Star Citizen does not publish its prices. Players do.
       Somebody stood at that terminal, saw that number, and typed it into
       UEX. UEX rates how much it trusts each submission - that is why its
       records carry a quality score, averaged buy and sell figures and stock
       levels at all. Those are fields you only need when the numbers are
       estimates.
       So here is the whole of what this page can honestly say: UEX reported
       this price at this terminal in the snapshot taken on the date beside
       the row. Not "this is the price". We have not been into the game to
       check, and neither has UEX.
       A row can be out of date. A row can be wrong. The date next to it is
       how you tell, which is why every single row carries one rather than one
       date sitting at the top of the page."
    AND IT SITS ABOVE THE TABLE, NOT UNDER IT. It used to trail the page. A
    caveat a visitor has to scroll past the numbers to reach was written to be
    skipped, so the position is asserted rather than left to taste: the control
    fails if the caveat's offset is greater than the table's.
    A one-line version sits directly under the answer on every item and
    terminal page: "Every number below is what a player told UEX they saw at
    that terminal, on the date beside it. Nothing here is read out of the
    game."

CONTROL  <sha>  checks/_verify_find_wording.mjs - 29 assertions, and it is a
    SCANNER rather than a human read, because a human read passes once on the
    day somebody does it and this runs on every build.
    NINE FORBIDDEN CLAIMS, each carrying the sentence that must trip it, and
    EVERY PATTERN IS RUN AGAINST ITS OWN BAD EXAMPLE BEFORE IT IS POINTED AT
    THE PAGE. "Prices are read straight out of the game", "This is the official
    price", "Live prices, updated in real-time", "The average price across all
    shops is 2,900 aUEC" - all nine must be caught, and an honest sentence must
    NOT be. A wording checker whose patterns never match anything reports a
    clean page forever.
    A NEGATED MENTION IS NOT A CLAIM. The page says "Nothing here is read out
    of the game", which is the sentence H4 asked for; a scanner that failed the
    page for saying it would be pushing the page toward saying less.
    AND ONE REAL DEFECT IN THE SCANNER, FOUND AND FIXED RATHER THAN WORKED
    AROUND: inside a block comment that sentence wraps across lines with " * "
    through the middle of it, so the negation did not match and the forbidden
    pattern did. The page failed for containing exactly what it was told to
    contain. Fixed by flattening comment leaders before scanning - and the
    flattener is itself proven, with a forbidden sentence planted across a
    comment break that must still be caught.
    SIX REQUIRED SENTENCES, checked on the item page, the terminal page and
    the home page - so the caveat is not present on one route and missing on
    the next.
    STATED LIMIT: this catches the claims we know are wrong to make. A novel
    overclaim would pass. The answer to that is a new pattern here, not a claim
    that this is comprehension.

    AND THE WORDING NOW HAS ONE OWNER. The three H4 assertions that had been
    living in _verify_find_page.mjs were removed rather than updated. Two
    copies of the same claim in two suites drift the moment either is edited -
    the same one-writer problem as rule 14, applied to an assertion instead of
    a file. _verify_find_page.mjs keeps only the structural half: that the
    provable claim is present at all.

H5  DONE  <sha>  THE FILE THE PAGE READ, DOWNLOADABLE, WITH ITS CHECKSUM
    PRINTED BESIDE IT.
    AN INTERPRETATION, STATED RATHER THAN ASSUMED. R7 says "the raw snapshot".
    The UEX snapshot directories are several MB of JSON and are gitignored;
    what R7's own reason sentence asks for is that "a visitor can check every
    number against THE FILE THE PAGE ACTUALLY READ". So what is published is
    find_data.gen.js - the exact bytes the page loaded - not the upstream JSON.
    The page names the upstream snapshots it came from, so the chain is
    followable either way. If Sleven meant the UEX files themselves, that is a
    second download and a bigger deploy, and it is his call.
    THE CHECKSUM IS GENERATED, NEVER TYPED. build_find_data.py writes
    find_checksum.gen.js in the same pass, from the same bytes. A second file
    for one unavoidable reason: a file cannot contain its own sha256.
    AND --check REFUSES A STALE CHECKSUM. A correct data file beside a checksum
    describing the previous one is WORSE than no checksum - it tells a visitor
    the file was tampered with when it was not.
    IF THE CHECKSUM FILE FAILS TO LOAD, THE PAGE WITHHOLDS THE DOWNLOAD
    ENTIRELY and says why. Offering a file with no way to check it is the
    opposite of the point.
    The panel gives the commands: certutil -hashfile on Windows, sha256sum
    elsewhere. And it says why the file has a .js extension - that is how the
    page loads it without a server; the data inside is plain JSON and
    FIND_SCHEMA at the top says what every column means.

CONTROL  <sha>  checks/_verify_find_deployed.mjs, extended - now 27 assertions.
    H5's named control is "download it, hash it, confirm it matches what the
    page claims", so all three happen against the DEPLOYED origin:
      downloaded  993,157 bytes
      sha256      dce035da5b436b6180833ff0b127ae27485d101366c49eab4edefc9045040f5f
      page claims 993,157 bytes, same sha256
    DOWNLOADED AS BYTES, not re-encoded from a string. The last time this
    project compared a served file with a local one it compared a re-encoded
    string, produced a mismatch, and the mismatch was the check's fault rather
    than the deploy's.
    AND THE COMPARISON IS PROVEN ABLE TO FAIL: one byte in the middle of the
    downloaded buffer is flipped and the hash must stop matching. Without that
    this is a string compared with itself.
    ONE THING WORTH KNOWING: the first run after the deploy got HTTP 404 on
    find_checksum.gen.js and the harness refused - NOT VERIFIED, exit 1, "the
    banner stays on". The asset appeared a moment later. That is the harness
    behaving correctly on a propagation gap rather than papering over it, and
    it is recorded because a 404 that resolves on its own is exactly the kind
    of thing that gets quietly retried out of a ledger.

H6  DONE  <sha>  THE GENERATOR IS A BUILD STEP, NOT A THING SOMEBODY REMEMBERS.
    build_deploy.py runs build_find_data.py --verify-stable before anything is
    copied into _deploy, and refuses to build if it fails.
    WHAT THAT COSTS, SAID OUT LOUD RATHER THAN DISCOVERED LATER: the testing
    build now needs the database. Deliberate. The alternative is a build that
    skips its own data generation and still prints "safe to deploy", which is
    the same shape as a build that skips its own tests - and this build already
    refuses to run when node is absent, for the same reason.
    A REAL DEFECT FOUND AND CLOSED WHILE DOING IT: core.autocrlf is true on
    this machine, so git rewrites LF to CRLF on checkout. --check compares the
    bytes it would write against the bytes on disk, so on a fresh clone it
    would have reported STALE for a perfectly current file, on line endings
    alone. A stale-detector that fires on something it was not built to catch
    is one people learn to ignore, and then it is not a check. Closed with a
    .gitattributes pinning *.gen.js to eol=lf end to end. These files are
    machine-written and machine-read; there is nothing to gain from a
    platform-native ending.

CONTROL  <sha>  checks/_verify_find_build_step.py - 21 assertions, and it runs
    the REAL build four times rather than reasoning about it.
    BOTH HALVES OF H6'S NAMED CONTROL, and the negative half first because it
    is the one that is easy to skip:
      NEGATIVE - three builds with no database change, and the data file and
      the published checksum are BYTE-IDENTICAL every time. A generator that
      regenerated correctly AND stamped the time into its output would pass the
      positive half on every single run, forever, and churn git while doing it.
      POSITIVE - item_prices id=26, price_buy 23,500 -> 23,507. Rebuild. The
      file changed, the new value is in it, the checksum changed with it, and
      the checksum describes the NEW file rather than the old one.
    AND THAT THE BUILD RUNS THE GENERATOR AT ALL, proved by behaviour: damage
    is planted in find_data.gen.js, the build is run, and the damage must be
    gone. Grepping build_deploy.py for the filename would prove only that
    somebody typed the filename.
    AND THE STALE CASE, made real rather than simulated: the database is put
    back while the FILE is left as it was, so the file on disk genuinely
    disagrees with the database, and --check must refuse it and say STALE.
    WHAT IT DID TO THE DATABASE, stated plainly: one UPDATE, one column, one
    row, put back in a finally block. Not a DELETE, not a TRUNCATE, not a
    migration - none of the operations rule 3 forbids. The old value is read
    first and the restore SQL is printed before the change is made, so a
    harness that died mid-run leaves the fix on screen.
    THE RESTORE IS PROVEN, NOT MERELY ATTEMPTED: the final build must hash back
    to the baseline sha256 taken before anything was touched. If it does not,
    the harness says so and prints the SQL.

BACKUP  2026-08-20 16:46:54, per rule 4, taken BEFORE the first row change.
    Backup-CitizenCompass.ps1 -NonInteractive -SkipMirror. Failures: 0.
    Postgres dump 2.06 MB written and restore-tested, 44.8 MB git bundle,
    10,425 files hashed. The "restore returned 232 ships, expected 254"
    warning is the known one already investigated at L3 - the live database
    holds 232 ships and the 254 is a stale expectation in the checker, not a
    short dump. Mirrors to D: and E: skipped by request and reported as
    skipped, not as done.

H7  DONE  <sha>  THE NEVER-DELETE GUARD IS NO LONGER AN ALLOWLIST. Protection
    is the default; a table is unprotected only if it is named as ephemeral.
    WHAT WAS ACTUALLY UNGUARDED, confirmed rather than taken from the order:
    all nine tables C1 named - shop_items, item_prices, terminals, locations,
    item_categories, snapshots, shop_item_commodity_xref, ship_hardpoints,
    ship_hardpoint_coverage. 26,657 price rows and 2,195 hardpoint slots.
    THE EPHEMERAL LIST, and why each one is on it:
      pipeline_check_results  the auditor's append-only observation log. It is
      pipeline_check_runs     DESIGNED to be flushed and archived, and
      pipeline_findings       checks_flush_fallback.py exists to do it. A
                              finding is re-derived by re-running the checker.
      alembic_version         a POINTER to the current revision, not a record.
                              alembic rewrites it on every migration, so
                              guarding it would guard a value meant to change.
                              Worth knowing: alembic builds its own engine in
                              env.py, so this guard never sees those statements
                              anyway - the entry is here so the classification
                              is honest rather than accidental.
    AND ONE PREFIX, cc_scratch_, FOR HARNESS THROWAWAYS - with its risk stated
    in the code rather than buried: a prefix IS a bypass. Anyone naming a real
    table cc_scratch_prices loses its protection. That is closed for anything
    declared in app/models.py, because the classification checker treats a
    mapped table wearing the prefix as a DEFECT, and it is NOT closed for a raw
    SQL table nobody declared. The alternative was an edit to preservation.py
    for every harness temp table, and a guard that is annoying to work with is
    a guard people find ways around.
    BOTH LISTS STILL EXIST, DELIBERATELY. The guard needs only the ephemeral
    one. PRESERVED_TABLES is the CLASSIFICATION, and it exists so that
    "protected because somebody decided" and "protected because nobody looked"
    are different states. Today: 24 preserved, 4 ephemeral, 0 unclassified.

    THE ARGUMENT C1 ASKED FOR - I looked for a case where protect-by-default
    breaks something legitimate, and I found exactly one, in our own controls:
      checks/_verify_never_delete_guard.py had an assertion reading "a
      NON-PRESERVED table is NOT blocked", using a temp table called
      scratch_notes. It passed because scratch_notes was not on the old
      sixteen-name allowlist. Under the inversion scratch_notes is protected
      like every other unclassified name, and that assertion FAILED the moment
      the inversion landed.
      THAT IS THE INVERSION WORKING, not a case against it. The whole change is
      that an unnamed table is guarded rather than open. The assertion was
      asking the old question; it now asks the right one - an EPHEMERAL table
      is still deletable - and a second assertion was added beside it proving
      an unclassified one is refused.
    NOTHING ELSE BROKE. Every importer in this repo upserts; not one deletes
    rows. import_ship_hardpoints.py explicitly rewrites its own rows by UPDATE
    and says so. checks/findings_store.py reaches the pipeline_* tables through
    raw psycopg2, so the guard never saw them in the first place - the ephemeral
    entries are correctness rather than a rescue.

CONTROL  <sha>  checks/_verify_preservation_inversion.py - 45 assertions.
    H7's NAMED CONTROL, BOTH HALVES, in the order the order gives them:
      "a new table added to the models with no classification FAILS the check.
       Observe it failing." - a table is added to a THROWAWAY MetaData, the
       checker reports exactly one problem, and the message names the table and
       says it is protected anyway so nobody panics.
      "Then classify it and observe it pass." - classified, re-run, clean. And
       the real classification is asserted restored afterwards, so the harness
       cannot leave the project's own lists altered.
    AND THE GUARD IS PROVEN AT THE ENGINE, not by reading frozensets: real
    DELETE and TRUNCATE statements against TEMPORARY tables inside one
    connection. An unclassified name is refused; an ephemeral one goes through;
    DELETE-with-WHERE, lowercase delete and TRUNCATE are all refused; and with
    the guard REMOVED the same delete succeeds, which is what makes it
    load-bearing rather than coincidental.
    THREE MORE WAYS THE CLASSIFICATION CAN BE WRONG, each proven: a table in
    BOTH lists, a real mapped table wearing the ephemeral prefix, and a name in
    PRESERVED_TABLES that is no longer a table at all.
    NO REAL ROW IS TOUCHED. Temp tables only, rolled back, and the
    classification half runs on throwaway MetaData objects.
    --self-test inverts every expectation and exits 1.

CHECKER  <sha>  preservation_classification, registered in checks/db_checks.py
    and checks/schema_checks.py, so it runs with every session-opening check
    rather than only when somebody remembers this harness exists.

H7-FINDING  <sha>  THE E2E HARNESS FAILS AT STEP 7, AND IT IS NOT H7'S DOING.
    Run deliberately, because the order says to take care with it. Steps 1-6
    passed under the inverted guard - throwaway database created, migrations
    applied, importers run, API exercised - and NOT ONE preservation violation
    was raised. That is the answer H7 needed.
    Step 7, `alembic check`, fails: "Detected added table 'ship_registry'".
    PRE-EXISTING AND UNRELATED. ship_registry is declared in app/models.py and
    deliberately NOT in alembic/env.py's EXCLUDED_TABLES - env.py says so in as
    many words - but NO MIGRATION CREATES IT. Its DDL comes from
    registry-builder/main.go. So on a fresh database `alembic upgrade head`
    does not create it, autogenerate sees a table in the models that is not in
    the schema, and the drift check fails. Nothing in this run touched any of
    that.
    REPORTED, NOT FIXED. Deciding whether ship_registry gets a migration or
    joins EXCLUDED_TABLES is a schema-authority call - it is exactly the
    "one writer per artifact" question env.py's own comment is arguing about -
    and it is not in this order.
    ALSO WORTH KNOWING: run_e2e_test.py needs venv/Scripts on PATH. Without it
    the alembic subprocess raises FileNotFoundError at step 1. It cleaned up
    its throwaway database correctly both times.

H8  DONE  <sha>  THE STALENESS FLAKE, AND THE HANG - WHICH TURNED OUT TO BE A
    COMPLETELY DIFFERENT DEFECT AND A MUCH WORSE ONE.
    H8's amendment was right to promote the hang. Taking it seriously is what
    found it, and it is not in the staleness fixture at all.

    ---- SECTION 1: MEASURED FIRST, AS ORDERED ----
    citizen-collector/staleness_flake_test.go runs the REAL fixture in a loop
    under a per-run watchdog. A _test.go file: not in the shipped binary,
    nothing built into collector.exe, nothing installed.

      BEFORE, idle,   120 runs   38 failed   31.7%   0 hangs
      BEFORE, loaded,  60 runs    1 failed    1.7%   0 hangs
      AFTER,  idle,  2000 runs    0 failed    0.0%   0 hangs
      AFTER,  loaded, 2000 runs   0 failed    0.0%   0 hangs
      AFTER,  loaded, 1000 runs of the WHOLE entry point including its four
                                  new controls: 0 failed, 0 hangs

    DO THE FOUR FAIL TOGETHER OR SEPARATELY? TOGETHER, ALWAYS. 39 failing runs
    across the two before-measurements produced exactly ONE failure set, every
    time, all four names in it. Not once did "names the fix" fail while "fires"
    passed. So this is ONE defect with three dependants, the order was right
    about the shape, and the fix is one change.

    AND SECTION 2 WAS WRONG ABOUT LOAD, WHICH IS EXACTLY WHY SECTION 1 EXISTS.
    §2 predicts the flake gets worse under load: "a 1s ticker drifts and a
    goroutine may simply not be scheduled - and four seconds stops being
    enough." MEASURED, IT IS THE OTHER WAY ROUND - 31.7% idle against 1.7%
    loaded, a factor of nearly twenty in the direction nobody expected.
    I DID NOT CHASE THE MECHANISM AND I AM NOT GOING TO GUESS AT IT. What can
    be said is that "a busy machine misses a four-second window" does not
    explain a rate twenty times higher on an idle one, so §2's account of WHY
    is not established even though its account of WHAT (a fake clock racing a
    real ticker) plainly is. The fix removes the timing dependence entirely
    rather than widening it, which is why the after-measurement is decisive: if
    the cause had been something the deterministic driver does not touch, 2000
    clean runs would not have happened.

    ---- S1: THE LOOP'S OBSERVATION OF THE CLOCK IS NOW DETERMINISTIC ----
    autoDeps.pollNow is a test-only wake channel carrying an acknowledgement
    the loop CLOSES once that poll's body has finished - closed at the top of
    the next iteration, so every `continue` path through the body counts as
    completed. A signal that skipped the early exits would be worse than none:
    the fixture would wait for something that never arrives.
    cfg.PollSeconds is 3600 in the fixture, so the real ticker never fires and
    EVERY poll is requested. NO ASSERTION IN THE FIXTURE DEPENDS ON HOW MANY
    REAL SECONDS ELAPSE. The only remaining timeouts are watchdogs on the loop
    being alive at all, and hitting one is reported NOT PERFORMED with the
    reason (S3), never as a pass.
    A SIDE EFFECT WORTH THE SPACE: the fixture went from ~6 seconds a run to
    ~9 MILLISECONDS. 2000 runs now take 18 seconds. That is why the after
    numbers are 2000 and not 200 - a flake that reproduces once in three can be
    shown fixed by 2000 runs and cannot be by twenty.

    ---- S1's CONTROL, AND S2's TWO, ALL THREE OBSERVED FAILING ON DEMAND ----
    None of these four checks had ever been seen to fail. They break the LOOP,
    not the assertion: autoDeps.sabotage and autoDeps.stalenessAfter are
    test-only knobs, zero-valued in production, and the selftest asserts that
    default.
      S1  staleness window set to 1000h -> all four checks FAIL, and the two
          dependants report NOT PERFORMED rather than passing on 0 == 0.
      S2a warn on every poll -> "warns once per stall" FAILS, while "fires on a
          dead log" still PASSES, so the control proves the right thing.
      S2b growth clears the warned flag but not the clock -> "a log that starts
          growing again is NOT reported stale" FAILS.

    AND S2b TAUGHT ME SOMETHING ABOUT THE CHECK ITSELF. My first version of
    that sabotage skipped the whole reset - flag and clock. The check PASSED,
    because with staleWarned latched at true the loop stays silent and the
    count never moves. So: "a log that starts growing again is NOT reported
    stale" CANNOT, ON ITS OWN, DETECT A RESET THAT NEVER HAPPENS. It detects a
    reset that clears the flag without clearing the clock. That is written into
    the constant's comment rather than left for the next person to rediscover
    by watching a control fail to fire.

    ---- S3 ---- Every unreachable path reports NOT PERFORMED with the reason.
    ---- THE GATE AT firstCount == 0 IS UNTOUCHED, as ordered. The race under
    it is gone; the gate is not, because the gate is what makes a genuinely
    broken warning report honestly instead of green.

    ---- SECTION 5: THE HANG. IT RECURS, AND IT IS NOT A FLAKE ----
    It reproduced on the FIRST attempt and on every attempt after it. Six
    consecutive runs of a console control binary, all killed at 240 seconds.
    Not intermittent. Not the staleness fixture - the run died long before that
    section printed.
    NOT A DEADLOCK EITHER. A Go stack dump shows `goroutine [runnable]`, busy
    inside mineLineInto. It is unbounded WORK, not a wait.
    WHAT IT ACTUALLY IS: `-selftest` was reading the operator's entire Star
    Citizen log archive. mineTargets() scans C:, D:, E: and F: for every
    Game.log and every file in every logbackups folder. ON THIS MACHINE THAT IS
    243 FILES AND 208 MB. Two fixtures reached it:
      runMineSchemaSelftest             MineAll x3, to test a schema-version
                                        guard that needs no logs at all
      runSendIncludesCapturesSelftest   -> buildExport -> MineAll, by design
    MEASURED, back to back on the same machine:
      runMineSchemaSelftest    isolated 61ms      unisolated 240+ SECONDS
      whole selftest           isolated 13-15s    unisolated never returned
    SO "RAN FINE TWICE, HUNG THE THIRD TIME" WAS NEVER RANDOM. The duration is
    proportional to how much the person has played. It gets slower every
    session and eventually crosses whoever is watching's patience. That is what
    an intermittent hang looks like from outside when it is actually a straight
    line.
    AND IT IS NOT ONLY A SPEED PROBLEM. A selftest that reads a person's whole
    log archive is a surprise nobody asked for, whatever it does with the
    contents.

    FIXED BY CONSTRUCTION, NOT PER FIXTURE. isolateArchiveForSelftest() is
    installed once at the top of selftest() and restored on the way out. The
    second offender was only found because the first was fixed, and there is no
    reason to think there will not be a third - a rule that depends on every
    future fixture author remembering to stub a package variable is a
    convention, which is the same argument app/preservation.py makes about
    itself.
    AFTER: six consecutive full selftest runs, 13-15 seconds each, 574 checks
    each, IDENTICAL every time, one failure each - and that one failure is the
    CONSOLE subsystem check correctly refusing a console build, which is the
    control binary's entire purpose. Nothing else failed.

CONTROL  <sha>  runSelftestArchiveIsolationSelftest, in the collector's own
    selftest. Proven in both directions: the isolation is lifted and
    mineTargets() must return real files - 243 on this machine - then
    reinstated and it must return none. If a machine has no Star Citizen logs
    at all the first half is reported NOT PERFORMED, because an empty result
    would prove nothing about the isolation there.

    ---- S4: THE SWEEP FOR THE SAME PATTERN ELSEWHERE ----
    `grep -n "time.Sleep" citizen-collector/*_selftest.go`, classified. Per the
    order, REPORTED and not fixed - §1 measured only gamelog_selftest.go.
      SAME DEFECT, ASSERTS A NEGATIVE AFTER A BARE SLEEP - these can PASS
      because nothing ran, which is invisible:
        no_auto_capture_selftest.go:113,122  the worst of them. It asserts the
          collector took NO automatic captures. On a machine where the loop has
          not polled, that is true because nothing happened. This is the check
          that proves the collector never photographs anything on its own.
        hotkey_selftest.go:147  "no press means no receipt line", same shape.
      SAME DEFECT, BUT FAILS RATHER THAN PASSES - an annoyance, not a danger:
        mine_selftest.go:295,297  sleeps 1200ms then 2500ms and asserts the
          game-exit hook fired exactly once. A loop that never polled while the
          game was "alive" reports 0 and fails.
        activity_selftest.go:102,104  positive assertion after two sleeps.
      NOT THIS PATTERN, checked rather than assumed:
        hotkey_poll_selftest.go:181  the 450ms sleep is measuring a real-time
          dedup window, so real time is the subject rather than a proxy for it.
        hotkey_e2e_selftest.go:46 and gamelog_selftest.go:112 are backoffs
          inside polling loops, not assertions after a sleep.

H8-NOT-DONE  Deliberately: NO RELEASE CUT, NOTHING INSTALLED, AND THE REPO'S
    collector.exe / collector-master.exe WERE NOT REBUILT. Every measurement
    above used a console probe binary built into the scratchpad OUTSIDE the
    repo, exactly as _verify_pe_subsystem.py does. The shipped binaries are
    therefore now behind this source, and that is Sleven's call to close, not
    mine.

H9  DONE  <sha>  SWEEP. 36 controls, 36 ok, 0 failed, 0 skipped, 0 NOT RUN,
    in 180 seconds - WITH a live API server up so the HTTP and page controls
    ran for real, and WITH the deployed control included so the live site was
    checked too.
    H7 changed app/preservation.py, which every session that opens a database
    connection inherits. That is exactly the change that breaks things far
    away, and it is why this sweep mattered more than the last one. One thing
    broke, it was a control asking the old question, and it is written up under
    H7 rather than buried here.

    THE SWEEP IS NOW A FILE, NOT A LIST SOMEBODY TYPED. checks/run_all_controls.py.
    G9's sweep was 31 controls run by hand and the list of what exists lived in
    the ledger entry afterwards - a list nobody can re-derive, and one a control
    added next week is silently absent from. This DISCOVERS every
    checks/_verify_*.py and _verify_*.mjs on disk. A control added tomorrow is
    swept tomorrow with nobody having remembered anything.
    That is not a tidy-up. It is the same defect class as the allowlist H7 just
    inverted: a register that has to be maintained by hand fails silently and
    is discovered afterwards.

    AND THE SWEEP ITSELF HAS TO BE ABLE TO REPORT A FAILURE. It did, twice,
    for real, before either was fixed:
      _verify_g3_matcher_delta.py exited 2 - "NOT PERFORMED, CC_GEO_DIR is not
      set". Correct refusal, and the sweep counted it AGAINST the run rather
      than shrugging. Answered properly rather than excused: 235 models decoded
      through testing/_src/decode_glb_points.js and the control re-run for
      real. It passes, and it still says the two ships the second pass gains
      are the two Ares, by name.
      _verify_shop_schema_db.py --self-test exited 0, which my blanket "every
      self-test must exit non-zero" read as a failure. It is not: that harness
      plants three specific defects and exits 0 when it CATCHES all three, and
      G9 already noted the convention. Recorded in the sweep with its reason -
      and NOT taken on trust: a zero exit is only accepted when the output
      actually shows all three planted defects being caught, so a self-test
      that had quietly stopped testing anything would still be reported.
    AND AN EMPTY SWEEP IS A FAILED SWEEP. Without that, a discover() returning
    nothing - a renamed directory, a changed prefix, a typo in --only - prints
    "0 ok, 0 failed" and exits 0. That is the shape of every silent success in
    this project's history. Proven by running it with a filter that matches
    nothing: exit 1, "NOTHING WAS SWEPT".

    THE 36, in run order. Six are new this run:
      _verify_absence_pass              22 assertions
      _verify_broken_checker_end_to_end
      _verify_commodity_xref            27
      _verify_degraded_database         31
      _verify_find_build_step           21   (H6, new)
      _verify_find_data                 34   (H1, new)
      _verify_find_deployed.mjs         27   (H3/H5, new) against the LIVE site
      _verify_find_page.mjs             56   (H2, rewritten) network blocked
      _verify_find_wording.mjs          29   (H4, new)
      _verify_findings_store            36
      _verify_fingerprint_history       PASSED
      _verify_g3_matcher_delta           8   with geometry, for real
      _verify_hardpoint_alignment       PASSED
      _verify_hardpoint_join            PASSED
      _verify_items_import_b5           10
      _verify_lifecycle                 PASSED
      _verify_location_hierarchy        31
      _verify_location_hierarchy_db      8
      _verify_missing_encoding          19   (7 bad caught, 11 good ignored)
      _verify_never_delete_guard        16   (H7, one assertion rewritten)
      _verify_node_checks               PASSED
      _verify_pe_subsystem               3
      _verify_preservation_inversion    45   (H7, new)
      _verify_pull_and_clear            PASSED
      _verify_schema_checks             PASSED
      _verify_ship_configurations       PASSED
      _verify_ship_hardpoint_panel.mjs  16   against the live server
      _verify_shop_api                  36   against a real HTTP server
      _verify_shop_checks               24
      _verify_shop_importers            15
      _verify_shop_schema_db            39   (17 refusals, 16 acceptances)
      _verify_snapshot_shape            14
      _verify_source_checks             24
      _verify_source_duplicate_check    22
      _verify_testing_stamp             PASSED
      _verify_unreleased_content        19

    AND THE INVERSION PASS: every control carrying --self-test was run in that
    mode and required to FAIL. 10 ok, 0 failed, 26 skipped for having no
    --self-test mode. A suite of 36 green controls whose failure paths have
    never executed is 36 untested gates wearing a reassuring name.

    THE AUDITOR SUITE TOO. run_checks.py --group db: 13 checkers ok, 0 errored.
      schema_ownership                all 28 tables claimed by exactly one
                                      authority (24 in models.py, 3 externally
                                      owned, 1 alembic-internal)
      preservation_classification     PASS - 24 preserved, 4 ephemeral
    WITH ONE NICE MOMENT WORTH RECORDING: checker_health flagged
    preservation_classification as "never-reported - either it never ran, or it
    runs and says nothing" on the first pass, then cleared once it produced a
    finding. The auditor noticed a new checker before I told it about one.

---

    The I-run begins here. Order:
    docs/ORDER_the-public-site-needs-no-server-and-live-gets-a-deploy-script-2026-08-21.md
    Same ledger, same rules, appended rather than started fresh - per that
    order's `ledger` line.

I1  DONE  a05a021  THE PUBLIC SITE NOW NEEDS NO SERVER AT ALL. The ship page's
    Loadout panel was the last thing on it that called one.
    build_hardpoint_data.py generates testing/_src/hardpoint_data.gen.js from
    PostgreSQL - 235 models, 2,195 slots, positional arrays with kinds, stock
    item names, datasets and coverage reasons interned. Same discipline as H1:
    no generation timestamp, --verify-stable, --check, and a ceiling the
    generator ENFORCES. Run by build_deploy.py before anything is copied, so a
    stale copy cannot ship, and added to the deploy guard's allow-list in both
    places (the build passes PAGES in; the standalone guard keeps its own copy).
    SIZE, MEASURED: 149.0 KB raw -> 14.2 KB GZIPPED, against H1's 188 KB and a
    60 KB ceiling. No large miss to explain - the shape did not change.
    ACCEPTANCE: the slots in the file equal the slots in the database, counted
    out of the EMITTED structure rather than out of a number collect()
    remembered, so the gate cannot compare a variable with itself.
    THE CONTROL THAT MATTERS, and it passes: 35 assertions in
    checks/_verify_hardpoint_panel_offline.mjs, driving the panel's code AS
    SHIPPED (sliced out of the built _deploy/index.html, not the source) with
    fetch, XMLHttpRequest, WebSocket, EventSource and sendBeacon all replaced
    by throwers - and the poison proven live by calling it. 600i Explorer fills
    with all 15 of its mounts grouped, the provenance note names the mount count
    and the dataset, and no failure sentence and no spinner appears.
    THE FALLBACK IS KEPT AND IS PROVEN TO STILL BE THE FALLBACK.
    checks/_verify_ship_hardpoint_panel.mjs drives the same shipped code in a
    context with NO HP_DATA - which IS the "the file did not load" case - and
    now ASSERTS that rather than merely happening to be true: it requires
    HP_DATA to be absent from its own context and COUNTS the fetch calls the
    panel makes. Proven by planting `const HP_DATA={models:[]}` into a copy in
    _to_delete/: both new assertions fired, 5 of 18 failed, exit 1.
    checks/_verify_hardpoint_data.py, 41 assertions, runs every gate twice -
    once on real data, once on data damaged in the exact way the gate exists to
    catch: a dropped slot, a dropped model, a slot_count disagreeing with its
    own rows, an orphaned model_key, a 1 KB ceiling, a stale file, an absent
    file. --self-test exits 1.
    ONE RENDERER FOR BOTH PATHS (rule 14 applied to markup): the file's records
    are expanded into the SAME object the API returns and handed to one
    ccRenderHardpoints(), so the two cannot render differently.
    AND ONE model_key RULE. The API normalises with
    re.sub(r"[^a-z0-9]+", " ", raw.lower()).strip(); the page implements the
    same rule once, the generated file STATES it in HP_SCHEMA.model_key_rule,
    and the control checks the page's answer against the API's own imported
    function - including San'tok.yāi, which both spell "san tok y i".
    FOUND WHILE DOING IT, AND FIXED - it was already live on the API path since
    G8, so this is a fix to what the site shows rather than a difference
    between the two paths: 8 mounts (HoverQuad, X1, X1 Force) carry size 0, and
    167 carry '<= PLACEHOLDER =>' as their stock item name. That string is the
    GAME'S placeholder, not a component. The panel was printing "S0" and
    "<= PLACEHOLDER =>" to visitors as though they were a size and a fitted
    item. Neither is invented away - the mount is still listed and reads "not
    stated" when nothing is left to say - but a non-value is no longer
    displayed as a value. The match is anchored (^<=\s*PLACEHOLDER\s*=>$) so a
    real component whose name contains the word is not swallowed, and the
    control proves the suppression is narrow by requiring the 300i to still
    show real sizes and real item names.
    DECIDED-BY-DEFAULT: no published sha256 beside this file, unlike
    find_checksum.gen.js. That checksum exists because /find OFFERS its data
    file as a download and a visitor needs a way to check it; nothing offers
    this one. Cheap to reverse - it is one more render call in the same pass.
    DECIDED-BY-DEFAULT: a model MISSING from the file is answered from the file
    as "not in the hardpoint dataset yet" - the API's own 404 wording - rather
    than falling through to the network. Falling through would put a server
    back on the read path for exactly the hulls that need it least.

I2  DONE  0a4d5ed  THE LIVE SITE HAS A DEPLOY SCRIPT FOR THE FIRST TIME, and it
    has NOT been run. scripts/deploy_live.ps1 + wrangler.live.toml, mirroring
    the testing pair: the same check_deploy_clean.py guard on the same bytes,
    the same fail-closed treatment when the guard cannot run at all, the same
    payload sanity checks and Cloudflare ceilings, the same scoped-token
    handling, the same -WhatIf.
    THE ROOT DEFECT WAS NOT THAT LIVE IS BEHIND. It is that the live site had
    no button - three weeks of work sat unshipped because moving it was a
    manual act only one person knew.
    DIFFERENT WORKER, ITS OWN FILE, AND THE NAMES ARE CHECKED AGAINST EACH
    OTHER. citizencompass vs citizencompasstesting. The script reads `name` out
    of BOTH toml files and refuses when they match - structural, so it cannot
    be evaded by editing one file, and it refuses BEFORE looking at the payload
    so a perfect payload does not sail past it. Each config now states which
    URL it publishes to, in a comment, at the top.
    BOTH SCRIPTS PUBLISH testing/_deploy, deliberately: Sleven reviews the
    testing site and that exact payload goes live. Two build directories would
    mean the thing reviewed and the thing shipped were never the same bytes.
    The two payloads differ in exactly two things, and build_deploy.py --live
    omits both - the private-preview password gate and the "testing <date>"
    stamp. EACH SCRIPT REFUSES THE OTHER'S PAYLOAD, on the bytes about to be
    uploaded rather than on which flag somebody believes they used (rule 12,
    second half). deploy_testing.ps1 gained the inverse refusal in the same
    commit: without that half, a --live build left sitting in _deploy would
    publish an UNGATED private preview to the testing URL and report a clean
    deploy.
    -WhatIf ACCEPTANCE, RUN FOR REAL: against the live payload it exits 0 and
    reports worker citizencompass, url
    https://citizencompass.citizencompass-contact.workers.dev, 497 files,
    350.8 MB, 235 models, version v0.4.0 read out of the payload itself.
    THE CONTROL, AND IT IS THE ONE I2 NAMES - PROVEN FROM OUTSIDE, NOT FROM THE
    FLAG. After the dry run:
      https://citizencompass.citizencompass-contact.workers.dev/            404
      https://citizencompass.citizencompass-contact.workers.dev/index.html  404
      https://citizencompasstesting.citizencompass-contact.workers.dev/     200
    The worker still does not exist, so nothing was published, and the testing
    site was not touched on the way past.
    EVERY REFUSAL OBSERVED FIRING, BY HAND FIRST AND THEN AS A CONTROL:
      the testing payload offered to deploy_live.ps1  -> refused, names the gate
      the live payload offered to deploy_testing.ps1  -> refused, names the gate
      the testing name planted into wrangler.live.toml -> refused, names it
      (planted and restored; the restore is verified in the file)
    checks/_verify_deploy_guards.py, 43 assertions, runs THE REAL SCRIPTS with
    -WhatIf against tiny throwaway project trees - one per defect - so this is
    swept from now on rather than being something that was checked once by
    hand. Nothing uploaded, nothing in the repo touched, an obviously fake
    token in the temp .env. It covers both directions, both live refusals
    SEPARATELY (a stamped-but-ungated payload is refused for the stamp and NOT
    for the gate, which proves they are two refusals and not one), the name
    collision, an undeclared file, a payload with no models, a payload with no
    index.html, and the build's own refusal of a MISSPELLED --live.
    --self-test exits 1.
    WHAT THIS DOES NOT PROVE, said rather than glossed: that a real deploy
    works. The worker does not exist and only Sleven creates it.
    DECIDED-BY-DEFAULT: the live worker is named `citizencompass`, giving
    citizencompass.citizencompass-contact.workers.dev. Confirmed 404 before
    choosing it, so nothing is being trodden on. Cheap to reverse while it has
    never been deployed - one line - and expensive afterwards, which is exactly
    why it is written down here rather than left implicit.
    DECIDED-BY-DEFAULT: --live is a build flag rather than a second output
    directory. A second directory would be another 350 MB of models on disk and
    would let the reviewed payload and the shipped payload drift. The cost is
    that _deploy holds one of the two at a time, and that cost is paid by the
    two refusals above rather than by anybody remembering which build ran last.
    NOTHING HERE TOUCHES NETLIFY, and the control asserts neither script names
    a netlify command. citizencompass.netlify.app is still serving (200) and
    retiring it is a separate manual decision - written up in I3.
    RESTING STATE, left deliberately: _deploy holds the TESTING payload, gate
    present, stamped testing 2026-08-21.

I3  DONE  05f6a0c  docs/RELEASING-THE-SITE.md, written for somebody who is not
    the person who has been doing this by hand.
    THE ROOT DEFECT NAMED IN ITS OWN OPENING: not that live is behind, but that
    how to update it existed only in one head - so it stopped whenever that
    person was busy and nobody else could tell whether it had been followed.
    Ten sections: the two sites side by side with THREE ways to tell them apart
    (URL, password prompt, version string), which command publishes which, why
    both publish the same directory and what the two refusals do about it, what
    the deploy guard is and what to do when it stops you - including the
    2026-08-06 .wrangler leak that is why it runs inside the deploy and not
    only inside the build - the release run-through end to end, what ONLY
    SLEVEN CAN DO before the first live deploy, what to check afterwards, where
    everything lives, and what to do when something goes wrong.
    THE VERIFY SECTION LEADS WITH THE RIGHT SENTENCE: wrangler exiting 0 means
    the upload succeeded, not that the site works. Seven checks, and the second
    is "there is NO password prompt, in a clean browser context", because a
    gate on the public site looks like an outage from outside and nobody
    reports an outage as a mistake.
    IT ALSO WRITES DOWN THE THING NOBODY CAN AUTOMATE: after the Cloudflare
    live site is up there will be TWO public URLs until somebody takes
    citizencompass.netlify.app down by hand, in the Netlify dashboard. Nothing
    in this repo can do that or check it, so it is a numbered step rather than
    an assumption.
    Section 6 - what changes when live flips - is filled in by I5.

I4  DONE  6ef55fc  THE VERSION NUMBER IS WRITTEN IN ONE PLACE. VERSION at the
    repo root holds it; set_version.py is the only thing that writes it
    anywhere else; build_deploy.py runs `set_version.py --check` and FAILS
    CLOSED, so a page whose header disagrees with VERSION is never built.
    WHAT WAS ACTUALLY WRONG, and it was not the stale comment: the number was
    typed by hand in FOUR rendered places - the title and the header of
    static/preview.html and of releases/latest.html - plus a comment in
    _layer.src.html quoting a fifth, stale at v0.3.9 while everything else said
    v0.4.0. The comment was harmless. The mechanism is not, and this project
    has already shipped a release whose source said one number and whose feed
    said another with nothing able to notice.
    MEASURED RATHER THAN ASSUMED: static/preview.html (286,228 bytes) and
    releases/latest.html (205,362 bytes) are NOT the same file, despite
    CLAUDE.md describing one as mirrored into the other - preview.html carries
    inlined @font-face payloads the release copy does not. So both really did
    need writing, and a script that only wrote one would have looked correct.
    THE COMMENT NOW STATES NO VERSION AT ALL, deliberately - it explains the
    defect without quoting a number, so a grep for a stale one finds nothing
    there to find. The first draft of that comment DID quote both numbers and
    they shipped into the built page; caught by the control below, which is
    what it is for.
    NOT TOUCHED, BY NAME RATHER THAN BY LUCK: releases/citizen-compass-v0.3.*
    are archived releases. Their version strings are correct history and
    rewriting them would be falsifying the record. testing/_deploy/index.html
    is not a location either - it is BUILT, and writing to it would create a
    second writer for a generated file (rule 14).
    A LOCATION THAT MATCHES NOTHING IS A HARD FAILURE, not a silent skip. If
    the markup moves, set_version.py says that location has stopped being
    covered and refuses to write - a substitution that quietly matches nothing
    is precisely the check that cannot fail.
    THE CONTROL IS THE GREP THE ORDER ASKS FOR, NOT A SUBSTITUTION COUNT.
    checks/_verify_version_single_source.py, 20 assertions: set VERSION to
    77.88.99, run the real build, and require that NO built page carries the
    old number anywhere - counting substitutions would only prove the places
    the script already knows about, and the defect being guarded against is a
    place nobody knew about. Then it hand-tampers one page's title and
    requires BOTH set_version.py --check AND the build to refuse, naming the
    file and both numbers.
    IT MUTATES THE REPO AND PUTS IT BACK: VERSION, static/preview.html and
    releases/latest.html are snapshotted byte for byte, restored in a finally,
    and THE RESTORATION IS VERIFIED by comparing bytes - a failed restore is
    reported loudly and by name, never as a pass. The payload is rebuilt from
    the restored sources so _deploy is left exactly as it was found. Confirmed
    afterwards by hand: VERSION 0.4.0, --check clean, built page carrying
    v0.4.0 twice and the probe number nowhere.
    --self-test exits 1, and leaves the repo restored too.

I5  DONE  ebb3a07  WHAT CHANGES WHEN LIVE FLIPS - measured by fetching the live
    site, not remembered. Written into section 6 of docs/RELEASING-THE-SITE.md
    and summarised here.
    THE FINDING THAT REFRAMES THE WHOLE RELEASE: releases/latest.html is
    BYTE-IDENTICAL to the page being served live right now except for the
    version string. Two lines differ - the <title> and the header. The ship
    matrix, all 254 ships, the 233 RSI links, the text, the layout: identical.
    So "three weeks behind" does not mean the page drifted. It means everything
    since v0.3.9 is ADDED ON TOP of an unchanged page, or is a new page beside
    it. That is a much easier release to approve than it sounded.
    THE NUMBERS, both sides:
      live now   1 file, 205 KB, one page, v0.3.9, no models, no other paths -
                 /find /keybinds /loadout /holo /download /stick-test and
                 /models/Hammerhead.glb all 404 on citizencompass.netlify.app,
                 checked one by one
      would ship 497 files, 350.8 MB, v0.4.0, seven pages, 235 .glb models
                 (341.8 MB), 241 images (4.0 MB), 6 font files (0.1 MB, OFL,
                 with the licence shipped beside them), 15 files at the root
                 (4.9 MB). Every one of those seven paths returns 200 on the
                 testing site today.
    WHAT A RETURNING VISITOR WOULD NOTICE, ten items, in the order they would
    hit them. THE FIRST ONE IS THE DISRUPTIVE ONE AND SLEVEN SHOULD BE TOLD
    ABOUT IT BEFORE HE APPROVES, not after: ship names in the matrix stop being
    links straight to RSI and instead open an in-page ship view, with the RSI
    link offered inside that view. Anybody who has been clicking through to RSI
    meets this on their first click. It is a build decision, not a deploy
    decision, so it can be changed before the flip - and it cannot be changed
    after without a second release.
    Then: the 3D viewer for the 235 hulls that have a model (and a 3D badge
    only on those, with the rest saying so rather than showing an empty stage);
    the Loadout panel with 2,195 real mounts, which as of I1 needs no server;
    the FIND tab over 7,932 items, 26,657 prices and 823 terminals from two
    dated UEX snapshots, which also needs no server; the keybinds overlay and
    its 691-action page; /loadout knowing 316 ships, offered by 221 of the 254
    and correctly not offered by the other 33; /holo; /download, whose two
    outbound links were checked and resolve (the GitHub release redirects to
    collector-v0.3.3 and returns 200); the HELP drawer; and /stick-test.
    WHAT IS REMOVED: nothing. No page, no feature, no data.
    WHAT IS NOT IN IT: the password gate, the testing stamp, and - as of I1 -
    any dependency on the API at all. If Railway is down the public site does
    not notice.
    THE OTHER THING WORTH SAYING OUT LOUD: this is the first time the public
    site would serve anything but a single HTML page. 497 files against
    Cloudflare's 20,000 limit and a largest file of 5.22 MB against its 25 MiB
    limit, so both are comfortable - but it is a change in kind, not in degree.

I6  DONE  7245ec9  404 SWEEP OF THE DEPLOYED TESTING SITE. CLEAN: 449 internal
    references across all seven shipped pages, every one 200. Plus 11 external
    links, every one 200 - including both outbound links on /download (the
    GitHub release redirects to collector-v0.3.3).
    checks/_verify_deployed_links.mjs.
    FROM THE ORIGIN IN BOTH DIRECTIONS - the references are discovered by
    FETCHING THE DEPLOYED PAGES, not by reading testing/_deploy. That is not
    pedantry: the local build is usually ahead of the deployed one, so a
    disk-driven sweep reports "missing" for files that have simply not shipped
    yet, and reports NOTHING AT ALL about a file that was deployed and then
    removed. Today it matters concretely - hardpoint_data.gen.js exists locally
    from I1 and is not deployed, and a disk-driven sweep would have called that
    a dead link.
    WHAT IT SWEEPS: every href and src in markup, every url() in CSS, every 3D
    model read out of the page's OWN CC_EMBED map, and every ship thumbnail
    DERIVED WITH THE PAGE'S OWN CC_SAFE RULE - because those paths are computed
    at runtime and appear nowhere in the markup for a link checker to find. 235
    models and 241 thumbnails are most of the 449. HEAD rather than GET for
    assets; nobody needs to download 341 MB to learn the files are there.
    THE CONTROL I6 NAMES: a URL known to be absent is mixed in with the real
    ones and the sweep must report it. It does - 404, reported. And --self-test
    points that canary at a page that DOES exist and requires the assertion to
    FIRE: it does, exit 1. If it had not fired the run exits 2, "the proof did
    not run", deliberately distinct from the exit 1 that means the self-test
    worked - because a self-test that cannot tell those apart is itself a check
    that cannot fail.
    THE FIRST VERSION CRIED WOLF AND THAT WAS FIXED RATHER THAN TOLERATED. It
    read the whole page and reported THIRTEEN dead links that were not links:
    src="${logo}" inside a template literal, URL.createObjectURL(new Blob(...))
    matched by the CSS url() pattern, an href being built at runtime. Every one
    404s if you ask a server for it and every one is fine. A checker that cries
    wolf gets switched off, which is worse than not having one - so <script>
    blocks are stripped before the markup patterns run, and CC_EMBED, the one
    thing genuinely needed from a script, is read from the raw page. Preconnect
    and dns-prefetch hrefs are dropped too: their href is an ORIGIN, not a
    document, so https://fonts.gstatic.com/ correctly 404s while the preconnect
    works perfectly.
    FOUND AND REPORTED, NOT FIXED - three of the seven pages are reachable by
    URL alone:
      /find, /keybinds   linked in the markup
      /loadout           linked from JAVASCRIPT only (the ship view builds
                         link.href='loadout.html#'+cls) - which is why the
                         sweep names the three cases separately rather than
                         calling this an orphan, since saying so would be a
                         checker stating something false
      /holo, /download, /stick-test   NOTHING on the site references them
    Not a failure and they serve. But a visitor cannot find them, and that is
    Sleven's call to make deliberately rather than to discover after the flip.
    ALSO WORTH KNOWING: /find.html, /index.html and /keybinds.html reach 200
    VIA A 307 to their extensionless form. Cloudflare's static assets do that.
    Not a failure; reported because a redirect somebody did not know about is
    the kind of thing that looks like a bug the first time it is noticed.

I7  DONE  e089b02  _deploy IS BUILT FROM _src, AND NOTHING WAS TYPED INTO IT.
    checks/_verify_deploy_drift.py, 10 assertions, clean.
    WHY THIS ONE MATTERS MORE THAN IT LOOKS: a hand edit in _deploy WORKS. It
    deploys, it serves, it looks right - and then somebody runs the build and it
    is gone, with no error, no warning and nothing in the diff to explain why a
    working feature stopped working.
    THREE KINDS OF FILE, PROVEN THREE WAYS, because lumping them together would
    mean proving the easy ones and quietly assuming the hard one:
      COPIED VERBATIM  12 of the 14 PAGES entries - compared byte for byte
                       against their _src source, NON-DESTRUCTIVELY, so a hand
                       edit is reported rather than overwritten by the very
                       check that found it.
      TRANSFORMED      holo.html, which has three.js inlined at a marker. It
                       must still begin and end with the _src text either side
                       of that marker, so an edit anywhere outside the injected
                       block is caught.
      ASSEMBLED        index.html, built from releases/latest.html plus the
                       layer plus a dozen substitutions. There is no source to
                       compare it to, so it is proven the only honest way -
                       rebuild, and require the sha256 not to move. It did not.
    AND ONE KIND STATED AS UNPROVEN RATHER THAN COUNTED AS CHECKED: models/ 235
    files, images/ 241, fonts/ 6. These have NO generator. models/ is even a
    build INPUT - build_deploy.py globs it to decide which ships have a 3D view.
    Nothing here can prove where they came from, and saying they passed would be
    a check that never looked.
    THE LIST OF WHAT SHOULD BE THERE IS READ OUT OF build_deploy.py's OWN PAGES,
    parsed with ast rather than executed and rather than copied. A copy of that
    list living in a checker is a second writer for the same fact (rule 14) and
    would drift the first time a page was added.
    THE PLANT: a file typed straight into _deploy, existing nowhere in _src.
    Reported. The planted copy was MOVED to _to_delete/ (hard rule 1 - nothing
    here deletes) and the real file restored byte for byte, verified.
    --self-test exits 1.
    THE PRE-RUN STATE, ANSWERED SEPARATELY AND HONESTLY. This run's first build
    (I1) overwrote _deploy, so the local directory can no longer answer "was
    anything hand-edited into _deploy before today". The DEPLOYED SITE can, and
    it is a record I cannot have touched: all twelve verbatim-copied files were
    fetched from the origin and compared against _src AT THIS RUN'S STARTING
    COMMIT (67e441a). ALL TWELVE BYTE-IDENTICAL - find, keybinds, loadout,
    download, stick-test, kb_modes.gen.js, sc_export.js, kb_actions.gen.js,
    holo_data.gen.js, loadout_data.gen.js, find_data.gen.js,
    find_checksum.gen.js.
    index.html cannot be compared that way, so it was probed rather than
    proven: its CC_MODELS map is character-identical to _layer.src.html at
    67e441a (4,858 chars), and both HELP data payloads are embedded verbatim
    from data-layer/processed at that commit (11,441 and 6,756 bytes). That is
    strong evidence and it is not the same as the byte comparison above - said
    plainly rather than rounded up to "verified".

I8  DONE  1f44a14  SWEEP. 42 controls, 42 ok, 0 failed, 0 skipped, 0 NOT RUN,
    in 147 seconds - WITH a live API server so the HTTP and panel controls ran
    for real, WITH the deployed origin included, and WITH CC_GEO_DIR pointing
    at 235 freshly decoded models so the geometry control ran for real instead
    of refusing.
    SIX ARE NEW THIS RUN: _verify_hardpoint_data (41), _verify_hardpoint_panel_
    offline.mjs (35), _verify_deploy_guards (43), _verify_version_single_source
    (20), _verify_deployed_links.mjs (449 URLs), _verify_deploy_drift (10).
    They were swept without anybody adding them to a list, which is what H9's
    discover() was for.
    THE INVERSION PASS: 16 ok, 0 failed, 26 skipped for having no --self-test.
    Up from 10 at H9 - every control written this run carries one.
    THE FIRST PASS FAILED, AND CORRECTLY. _verify_g3_matcher_delta.py exited 2,
    "NOT PERFORMED, CC_GEO_DIR is not set", exactly as it did at H9. Answered
    the same way rather than excused: 235 models decoded through
    testing/_src/decode_glb_points.js and the control re-run for real. It
    passes, and it still names the two ships the second pass gains as the two
    Ares. _verify_hardpoint_alignment ran with real geometry too.
    THE EMPTY-SWEEP GUARD STILL FIRES: --only with a filter matching nothing
    exits 1, "NOTHING WAS SWEPT".
    TWO DEFECTS THE SWEEP ITSELF FORCED OUT, both of them mine, both from this
    run:
      _verify_deployed_links.mjs exited 2 when its self-test's proof did not
      run - a code I invented to distinguish "the proof did not run" from "the
      test worked". run_all_controls.py only requires NON-ZERO, so exit 2 would
      have been recorded as a working self-test. That is the same shape as
      every silent success in this project: a distinction that exists only in
      the place nothing reads. It now exits ZERO in that case, so the sweep's
      own rule is what catches it.
      THE missing_encoding CHECKER CAUGHT ME. Four call sites in
      _verify_deploy_drift.py, because its local helper was named read_text.
      The helper does specify utf-8 - the findings were false. They were fixed
      anyway, by renaming the helper: a checker that cries wolf is a checker
      somebody eventually silences, and this is the one that makes hard rule 15
      machine-enforced. Worth more than four saved keystrokes.
    THE AUDITOR SUITE TOO.
      run_checks.py --group db    13 checkers ok, 0 errored. 188 findings,
                                  1 reopened, 1 closed, 187 unchanged.
      run_checks.py --group file  18 checkers ok, 0 errored. 287 findings, all
                                  unchanged - and NOT ONE of them names a file
                                  written in this run.
    RESTING STATE, checked rather than assumed: VERSION 0.4.0, set_version.py
    --check clean, _deploy holding the TESTING payload (gate present, stamped
    testing 2026-08-21), and the live worker URL still 404.

I9  DONE  0e866b8  TESTING SITE DEPLOYED, on Sleven's say-so and at his request.
    NOT the live site - nothing in this went near deploy_live.ps1 or
    wrangler.live.toml, and the live worker URL still 404s.
    Followed docs/RELEASING-THE-SITE.md section 5: rebuild (default, no
    --live), -WhatIf, then the real run.
    THE PAYLOAD GUARD PASSED AND SAID WHY: "payload : TESTING - password gate
    present, testing stamp present". 497 files, 350.8 MB, 235 models.
    WHAT ACTUALLY MOVED: TWO FILES. wrangler uploaded /index.html and
    /hardpoint_data.gen.js and left 495 already-uploaded assets alone - which
    is exactly and only what I1 changed. A deploy whose diff matches the work
    is worth recording; one that does not is the thing to worry about.
    VERIFIED FROM THE ORIGIN RATHER THAN FROM THE EXIT CODE:
      /                       200, 1,626,034 bytes, title carries the testing
                              stamp for 2026-08-21
      id="cc-kb"              present   cc-ship::after  present (x2)
      id="cc-gate"            present, and so is the whole gate mechanism -
                              root.classList.add('cc-locked'),
                              localStorage.getItem('ccGate'), and the CSS that
                              hides every sibling of #cc-gate
      /models/Hammerhead.glb  200, 3,608,636 bytes
      /hardpoint_data.gen.js  200, 152,564 bytes, sha256 IDENTICAL to the file
                              the build wrote
    STATED LIMIT: the gate's markup and script are proven present in the served
    bytes. Whether a browser then blocks is NOT proven from here - there is no
    browser on this machine and none was installed (rule 7). That is check 4 on
    the deploy script's own list and it is Sleven's to do.
    CONTROLS AGAINST THE NEWLY DEPLOYED SITE: _verify_find_deployed.mjs 27 of
    27 against the DEPLOYED origin, including that the published checksum
    describes the file the page actually reads.
    AND THE DEPLOY FOUND A DEFECT IN MY OWN I6 SWEEP, which is the entry that
    matters here. checks/_verify_deployed_links.mjs reported 449 internal
    references BEFORE the deploy and 449 AFTER - despite index.html having
    gained a <script src="hardpoint_data.gen.js">. A SWEEP THAT REPORTS THE
    SAME NUMBER AFTER YOU ADD A FILE IS NOT REPORTING ON THAT FILE.
    The cause: the stripper that removes inline JavaScript matched whole
    <script> ELEMENTS, so a self-closing <script src="..."></script> was
    deleted along with its src. The sweep was therefore blind to EVERY
    generated data file on the site - find_data.gen.js, find_checksum.gen.js,
    hardpoint_data.gen.js, kb_actions.gen.js, kb_modes.gen.js,
    loadout_data.gen.js, holo_data.gen.js and sc_export.js. Those are precisely
    the files whose absence breaks a page while the page still serves 200,
    which is the failure the sweep exists to catch.
    I6's clean result was therefore true but narrower than it read, and this
    corrects it rather than leaving it standing. Fixed by preserving the tags
    and removing only the inline body: 449 -> 457 references, ALL 200. So the
    deployed site was in fact fine; the sweep was not.
    AND A NAMED FLOOR SO IT CANNOT COME BACK QUIETLY: the four <script src>
    data files must appear in the swept set or the sweep FAILS and says the
    extractor has stopped seeing script tags. A blind spot that was only found
    by coincidence needs something that finds it on purpose next time.
    UNEXPLAINED AND RECORDED RATHER THAN GUESSED AT: wrangler reported "Read
    500 files from the assets directory" while every local count - python,
    PowerShell with and without -Force, and the deploy guard - says 497, and
    wrangler's own arithmetic agrees with 497 (495 already uploaded + 2 new).
    No dot-entries exist in _deploy. I do not know what the other three are and
    am not going to invent a reason.

L1  DONE  703c164  THE COMPONENT CATALOGUE IS DERIVED NOW, NOT WRITTEN.
    `build_loadout_data.py` carried a hand-typed list of FIVE component types.
    That is the by-type rule the order forbids, and it is now gone: every port
    on every ship is scanned and a type is kept when BOTH conditions hold - the
    port says `Editable`, AND its `CompatibleTypes` names a type with real
    items. 5 types -> 27. When CIG opens a port later, the next generation
    picks it up with no code change.
    THE FOUNDATION REPRODUCED EXACTLY, so §1 was not taken on trust:
    26,182 editable ports; stock ClassName resolves on 7,764; CompatibleTypes
    resolves on 8,544. C1's three figures, measured independently here.
    TYPES SELECTED (editable ports each): Missile 2488, WeaponGun 2046,
    Turret 773, Shield 532, Cooler 531, PowerPlant 401, MissileLauncher 379,
    Paints 306, Radar 297, QuantumDrive 253, JumpDrive 252, FlightController
    136, BombLauncher 100, WeaponAttachment 97, Container 69,
    LifeSupportGenerator 63, ManneuverThruster 30, CargoGrid 26,
    ExternalFuelTank 20, TractorBeam 19, Bomb 18, WeaponMining 17,
    SalvageHead 15, QuantumInterdictionGenerator 6, MainThruster 5,
    WeaponDefensive 4, EMP 2.
    Armor, FuelTank, FuelIntake and QuantumFuelTank are NOT excluded by name -
    they have zero editable ports, so the scan never selects them. That is the
    difference between a rule and a list, and it is why ExternalFuelTank (20
    editable, every one on a refueller) survives while plain FuelTank does not.
    SIZE, both figures because the order names one: 431,269 -> 2,583,573 bytes
    raw; 37.3 KB -> 191.9 KB GZIPPED. It grew 5.1x gzipped and the reason is
    not bloat, it is scope: the file now carries 25,875 ports instead of ~4,300
    slots of five types, because L4 says a fixed port is SHOWN. 18,001 of those
    are fixed. Four things were done to stop it being worse: `g` dropped (the
    group is already in LOADOUT_TYPES - 360 KB of the same eleven words),
    hardpoint names deduplicated into LOADOUT_HP (2,372 distinct for 25,875
    slots), fitment lists deduplicated by RULE (8,180 ports share 131 lists -
    3,662 entries instead of 552,310), and parts filtered to the 1,833 that
    some real port can actually take, of 5,384.
    AND THAT LAST FILTER IS THE ANSWER TO "DO NOT BUILD PICKERS FOR THRUSTERS".
    I did not exclude thrusters by type, because the game says 30 manoeuvre
    ports and 5 main ports ARE editable and a by-type exclusion is the exact
    mistake §1 is about. What the order was actually protecting against - 1,504
    thruster records shipped to serve 35 ports - is prevented by carrying only
    items some editable port accepts. Nobody gets a dead picker; nobody gets a
    false "cannot be changed" either. DECIDED-BY-DEFAULT, and cheap to reverse
    if Sleven wants the ports shown as fixed instead.
    CONTROL: checks/_verify_loadout_fitment.py, 40 assertions, and SEVEN
    MUTANTS ALL CAUGHT - type list reverted to the old five, an oversize part
    leaked into a list, every quantum picker emptied, fixed ports hidden, one
    resistance profile for every hull, every livery on every hull, and a port
    that stopped offering the part CIG fits in it.

L2  DONE  5041b24  THE STOCK LOADOUT IS THE SHIP'S OWN DEFAULTS, PROVEN PORT FOR
    PORT. Every slot carries `stock` read straight off the port's `ClassName`
    - not empty, not a guess, and not a class of part chosen by us.
    CONTROL, and the shape of it is the point: five named hulls (Cutlass
    Black, Avenger Stalker, Aurora MR, Hornet F7C, Prospector) are rebuilt from
    ships.json and compared PAIR BY PAIR - which part is in WHICH PORT - rather
    than by count. A count passes while the parts are shuffled between ports,
    and a Cutlass with its shields in the power-plant slots shows exactly the
    right number of components. That mutant is planted and caught.
    Plus the vacuity guard: the Cutlass Black must OPEN with parts fitted (26
    of its slots carry one), because "no mismatches" is trivially true of a
    ship that opens empty. That mutant is planted and caught too.
    Mutants now 9, all caught.
