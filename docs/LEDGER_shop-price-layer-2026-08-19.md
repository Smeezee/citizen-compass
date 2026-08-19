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
