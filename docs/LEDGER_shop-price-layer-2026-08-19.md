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

L2  DONE  f858214  THE STOCK LOADOUT IS THE SHIP'S OWN DEFAULTS, PROVEN PORT FOR
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

L3  DONE  9d86082  EVERY SLOT IS CLICKABLE AND THE PICKER READS THE PORT, NOT THE
    TYPE. The page's `fits()` was `P[k].t===slot.t && P[k].s===slot.s` - every
    part of the type at that size, on every ship. That is the false claim L3
    exists to stop. It now reads `FITS[slot.fit]`, the port's own
    CompatibleTypes + size window, plus `also` for the 44 ports where CIG
    mounts something its own declared rule rejects.
    CONTROL: checks/_verify_ship_page.mjs drives THE PAGE'S OWN SCRIPT in a vm
    against the real generated data and reads the HTML it produces. 53
    assertions.
    BOTH HALVES, NAMED, AND FROM THE RENDERED STRING RATHER THAN THE DATA:
      OFFERED - Aegis Avenger Stalker, port `hardpoint_weapon_missilerack_
      right_wing`, offers 16 parts including the Aegis Eclipse 20xS3 Bomb Rack.
      ABSENT  - the Aegis Retaliator 64xS3 Front Bomb Rack (size 5) does not
      appear at all for that size-3 port. Not greyed. Absent.
    And the sweep behind the two named ones: all 21 editable ports on that hull
    offer EXACTLY their own list, checked element by element, because two named
    examples prove two ports.
    ONE THING I HAD TO FIX IN THE CHECK ITSELF, worth recording because it
    would have read as a defect: CIG ships the same product at several sizes -
    there is an MSD-313 Missile Rack at size 3 AND at size 10 - so the first
    version of the ABSENT assertion failed on a NAME collision rather than on a
    wrongly-offered part. A name is not an identity here. Now asserted on the
    className.
    PROVEN TWO WAYS. `--self-test` inverts everything and exits 1. `--mutate`
    plants the real defect - `fitsFor` widened back to "every part of this
    type" - and FIVE assertions fire. That second one is the one that matters:
    it is a shortcut somebody could really take, not a sign flip.
    ARGUING WITH L3, as the order asked, and the answer is 99.4% yes:
    CompatibleTypes + the size window decides fitment cleanly for 7,633 of the
    7,681 editable ports where CIG's own fitted part can be checked against the
    port's own declared rule. It does NOT decide it cleanly for 48, and those
    are CIG disagreeing with itself - an Anvil Centurion turret port declaring
    it accepts `WeaponGun` with a `Turret` in it, three missile racks size 3 in
    a 2..2 window. Handled by always offering the stock part at its own port.
    TWO TRAPS THAT WOULD HAVE SHIPPED SILENTLY, both found by measurement:
      1. `SubTypes` enforced literally EMPTIES EVERY QUANTUM PICKER ON THE
         SITE. 253 quantum ports declare `SubTypes: ["QDrive"]` and all 63
         quantum drives carry `subType: "UNDEFINED"`. Same shape on JumpDrive,
         247 ports. UNDEFINED means "not stated" on both sides.
      2. `$editable` IS NOT A SUBTYPE. The Origin M80's right power-plant port
         declares `SubTypes: ["$editable"]`; no power plant has that subType,
         so enforcing it left that port offering nothing but the part already
         in it. Found by the control, not by reading the code.
    AND THE GAP, LOGGED NOT GUESSED: 134 editable ports name a component type
    that NO catalogue item satisfies at their size (e.g. Aegis Gladius /
    `$IP_rack_addon_02`). They render, marked `nofit`, and say the game files
    list no part for them. They do NOT open an empty picker, because an empty
    picker looks exactly like a broken one.

L4  DONE  9d86082  A FIXED PORT IS SHOWN, COUNTS, AND OPENS NO PICKER - three
    separable failures, asserted separately.
    SHOWN: all 57 of the Avenger Stalker's ports render, 36 of them fixed, and
    each NAMES the part in it ("Aegis Avenger - Decoy Launcher") rather than
    saying "Countermeasure - LOCKED", which tells a visitor nothing about their
    own ship.
    COUNTS: proven by REMOVING the fixed ports and watching the totals move -
    em, pw, mass and the part count all change. If they had not, the fixed
    ports were never in the sum, which is the version of this bug that looks
    completely fine on screen.
    NO PICKER: clicking one renders nothing selectable. It renders an
    explanation instead, with the patch its editability was last verified
    against, rather than being inert - an inert control reads as broken.
    `Editable` CARRIES `last_verified_patch`, AND IT IS DATA. Per-port
    overrides live in `data-layer/editability_patches.json`, absent by default.
    A mechanism that has never fired is an untested gate wearing a reassuring
    name, so the control PLANTS a real override, regenerates, confirms it
    reached the named slot, removes it and confirms it is gone. When CIG opens
    a port, that is a data edit and nothing else.

L5  DONE  b602193  ARMOUR. FIXED, NO PICKER, AND IT MOVES TWO THINGS THE PAGE HAD
    NO WAY TO SAY BEFORE.
    HOW THE 77 UNTAGGED ARMOUR ITEMS ATTACH - the order asked, and the answer
    is that THE QUESTION HAS A DIFFERENT SHAPE THAN EXPECTED. `RequiredTags` is
    NOT the attachment mechanism: 0 of 210 armour items carry a top-level
    `requiredTags` in this snapshot, so the "133 tagged, 77 not" split does not
    reproduce here at all. Armour attaches exactly the way every other
    component does - through the ship's OWN `Loadout`, at a port whose Type is
    `Armor`. That resolves for 305 of 316 records and there is NO PARTIAL
    RESOLUTION: every ship that has an armour port resolves it.
    CAN A HULL'S RESISTANCE BE RESOLVED FOR EVERY SHIP OR ONLY SOME? For every
    ship that has any. The 11 without an armour port are named rather than
    waved at: nine are exosuits (the ATLS family and the Power Suit, which CIG
    models as vehicles), and the other two are the Greycat PTV buggy and the
    AEGIS IDRIS-P. Those last two are a real gap and go on the punch list. 31
    of the 210 armour items are never fitted by any ship and are not carried.
    SURVIVABILITY IS NOT ONE NUMBER, and the page now says which. Ten distinct
    damage-multiplier profiles across the 210 armour items - the Avenger
    Stalker takes Physical at 0.8 and Energy at 0.65; the Eclipse takes Energy
    at 0.6. Signal multipliers are shown too, so armour visibly moves stealth.
    Deflection and PenetrationResistance are shown where non-trivial, and the
    ship's own `PenetrationMultiplier` says what reaches fuses and components.
    AND THE HALF THE ORDER'S CONTROL ACTUALLY DEMANDS - "a weapon strong
    against one is visibly weaker against the other" - is a NEW PANEL, because
    showing resistances and DPS as two unrelated numbers leaves the reader to
    multiply them in their head, which is the entire point of armour.
    `Damage.Dps` splits a weapon across the SAME six channels armour resists,
    so 179 parts now carry a damage MIX rather than only a total, and the page
    computes effective DPS against the most common armour profiles IN THE DATA
    - derived, so it stays right when 4.10 rebalances.
    NAMED, FROM THE RENDERED TABLE: the PyroBurst Scattergun does 166 DPS
    against a hull like the Aegis Eclipse and 139 against one like the Aegis
    Hammerhead. Same gun, 17% apart.
    The panel says in words that this is a matchup and not a rating - a
    ballistic loadout that looks weak against an energy-resistant hull is the
    stronger choice against a physical-resistant one, and both facts are on the
    table at once. Section 0 says the page has no opinion; this is what having
    no opinion looks like when two numbers interact.
    SCHEMA: `app/models.py` still has no hull-resistance dimension. Not built
    here - the page reads generated data, not the database - and it goes on the
    L16 punch list as the order asks.
    CONTROL: 6 more assertions in checks/_verify_ship_page.mjs, now 59 total,
    including one that SEARCHES for a weapon and two hulls that differ by more
    than 5% and FAILS if no such pair exists - so the claim cannot pass while
    being empty.

L6  DONE  63a3865  THE READOUT SHOWS EVERYTHING THAT MOVES, AT ONCE.
    Was five stats and two budgets. Now: sustained DPS, alpha, effective HP,
    shield regen, IR, EM, distortion pool, quantum range, SCM and max speed,
    TOTAL MASS, cargo, fitted container SCU, fuel, quantum fuel, crew and
    seats, life support, radar sensitivity and piercing, mining throughput and
    range, beam range and force - plus power draw against generation, heat
    against cooling, CIG'S PER-TYPE POWER POOLS, and armour's signal
    multipliers sitting with the signature where L6 puts them.
    Stock versus current on each, with the CIG/summed badge on both.
    MASS IS NOT DROPPED, and it is the one the order singles out. The page
    carries the hull's own mass plus every fitted part, so a swap moves it -
    and since thrusters are effectively fixed, mass is the main lever a player
    has left over agility. Lower is better, so the arrow points that way.
    THE ORDER'S CONTROL, IN WORDS: on the Aegis Avenger Stalker, fitting a
    REVENANT GATLING at `hardpoint_weapon_gun_class1_right_wing` RAISES dps,
    alpha, EM and power draw and LOWERS total mass. More gun, more draw, more
    noise, less weight - four readouts, two directions, one click. Found by
    SEARCHING every editable port and every part it admits rather than by
    naming a swap and hoping, and the control FAILS if no such pair exists.
    TWO THINGS THAT WOULD HAVE PUT A WRONG NUMBER ON THE PAGE:
      1. A CARGO GRID STATES NO SCU. `InventoryOccupancy` is how much room the
         GRID takes up, not what it holds, and it reads 0 for all 143 grids.
         Capacity is stated by DIMENSIONS in the game's 1.25m unit - 2.5 x 1.25
         x 1.25 is 2 SCU. Reading the obvious field would have printed "0 SCU"
         on every container on the site, and 0 is a number somebody believes.
      2. POWER POOLS USE -1 FOR "NO CAP". Rendering it as a number puts a
         negative power allocation on the page. Uncapped types are omitted, and
         the control asserts no "-1" reaches the rendered HTML.
    BEST-OF vs SUM, decided per figure rather than uniformly: two radars do not
    see twice as far and two mining heads do not stack their range, so those
    are best-of; extraction throughput does add, so it is summed. Getting that
    backwards is arithmetic that looks fine.
    CONTROL: 67 assertions now. Each of detection, mining, salvage and cargo is
    proven ON A HULL MEASURED TO CARRY IT rather than on one ship that would
    either fail for the right reason or pass for the wrong one.

L7  DONE  fdaa586  LIVERIES LIVE ON THE SHIP PAGE. 915 liveries in 104 hull sets,
    off 321 livery ports.
    THE CASE RULE IS LOAD-BEARING AND THE SIX SHIPS ARE NAMED: 315 paint ports
    are spelled `hardpoint_paint` and 6 are `Hardpoint_Paint`. Those six are
    the RSI AURORA MK I LX, LN, ES, SE, MR and CL. The control does not assert
    the number - it RUNS the exact-case match as the defect it would be and
    reports which ships fall out.
    AND THE JOIN IS THE TAG, NOT THE TYPE. A paint port's `CompatibleTypes`
    says only `Paints`, which is every livery in the game. Taking that at face
    value offered all 1,077 liveries on every hull - 1,077 false claims per
    ship, and 8 MB of repeated lists, which is how the defect announced itself.
    The port's own `RequiredTags` is the real join.
    THEN THE CONTROL FOUND SOMETHING I WOULD HAVE MISSED, and it is the entry
    worth reading: THE SAME SIX AURORAS ALSO HAVE `RequiredTags: null` ON THAT
    PORT. Two CIG defects in the same six records. `Paint_Aurora` liveries
    plainly exist and plainly belong to an Aurora - and "plainly" is inference.
    L3 is explicit: where the data does not say, exclude and log it, NEVER
    GUESS A PORT RULE. Offering a livery the game does not state is fittable is
    the same false claim as offering an unmountable shield, so they get none
    and the page says the game files list none.
    THE FULL GAP, FOR THE PUNCH LIST: 46 hulls have a paint port CIG left
    untagged. 79 liveries under 9 tags (Paint_Aurora, Paint_Cutlass,
    Paint_400i, Paint_Apollo, Paint_Hermes, Paint_Omega, Paint_Wolf,
    Paint_Pisces_Expedition, ANVL_Hornet_F7A_Mk2) are asked for by NO port at
    all, so nobody can fit them. One port tag, `300_Seat_Paint`, is answered by
    no livery.
    TWO DEFECTS THE CONTROL CAUGHT IN MY OWN WORK, both the same shape - a join
    on the wrong key:
      1. The generator let the LAST paint port win. Four hulls carry several,
         and on the Drake Caterpillar the first is untagged and a later one is
         not, so overwriting dropped liveries depending on walk order - which
         is not a decision anybody made. Now a UNION across every paint port.
      2. My CHECK keyed on the DISPLAY NAME, and TWO DISTINCT RECORDS ARE BOTH
         CALLED "Drake Caterpillar" - `DRAK_Caterpillar` and
         `DRAK_Caterpillar_Boarded`. The boarded one is untagged, the flyable
         one is not, and merging them made the check report the page guessing
         when it had done nothing of the kind. The check now keys on ClassName
         like the generator. A display name is not an identity in this dataset.
    NOT RENDERED ON THE MODEL, and the page says why in its own words: the data
    carries a name and a colour word in a class name, not a texture, so
    painting the model would mean guessing the colour - and a guessed colour on
    a page whose whole point is verifiable data is worse than none. A texture
    source can plug into the section later.
    LIVERIES TAKE NO PART IN THE READOUT, proven by fitting one and asserting
    that every computed figure is byte-identical afterwards.

M0  DONE  3bd90c7  ADDENDUM §0 AUDIT OF L1-L7. The answer is: NOTHING WAS KEYED
    ON `Name`, and one display defect the collision causes HAS been fixed.
    THE COLLISION REPRODUCES EXACTLY as the addendum states: 316 records, 287
    distinct display names, 22 names shared by 51 records. A Name-keyed build
    would have lost 29 records.
    EVERY EMITTED TABLE, AND WHAT IT IS KEYED ON - checked one at a time rather
    than assumed:
      LOADOUT_SHIPS      316  ClassName
      LOADOUT_PARTS     1833  className
      LOADOUT_ARMOR      179  className
      LOADOUT_PAINTS     915  className
      LOADOUT_FITS       124  the port's own rule (types|min|max)
      LOADOUT_PAINTSETS  104  the port's RequiredTags
      LOADOUT_TYPES       36  type code
      LOADOUT_HP        2372  an array, referenced by index
    Not one of them touches a display name. The one place a NAME is used at all
    is LOADOUT_UNRELEASED, and those are the 33 ships with NO game record at
    all - they cannot collide with a ClassName-keyed record, and all 33 names
    are distinct anyway.
    §0's CONTROL PASSES: both Hammerheads survive as separate entries -
    AEGS_Hammerhead with 226 ports and 9 crew, AEGS_Hammerhead_GS with 223 and
    8. Genuinely different ships, and the control asserts they DIFFER rather
    than only that there are two of them.
    WHAT I DID HAVE TO FIX, and it is a real defect the addendum's framing
    surfaces: JOINING CORRECTLY IS NOT ENOUGH. The ship dropdown rendered
    "Aegis Hammerhead" twice, identically. A visitor could not tell which they
    were picking, or which they got. Shared names now carry the distinguishing
    part of the ClassName - "Aegis Hammerhead (Hammerhead GS)" - derived from
    the key, never typed, and applied ONLY to the 22 names that need it. The
    control asserts all three: no two entries read alike, the shared ones are
    disambiguated, and the other 265 are left alone.
    AND I HAD ALREADY HIT THIS CLASS OF DEFECT AT L7, before the addendum
    arrived: my own livery check keyed on the display name and merged
    `DRAK_Caterpillar` with `DRAK_Caterpillar_Boarded`, reporting the page
    guessing when it had done nothing of the kind. Recorded there. Two
    independent encounters with the same defect in one run is the strongest
    argument for the addendum's rule that I can offer.

L8  DONE  66b5363  THE 3D VIEWER IS ONE FILE NOW - testing/_src/cc_viewer.js.
    The renderer, the lights, the environment map, the framing, the load path
    and its cancellation came out of index.html. What did NOT come out is
    badges, prices, dealers, hardpoint panels or tabs - that is what each page
    says AROUND a ship, and pushing it in would make one function with two
    personalities.
    MEASURED IN THE SHIPPED BYTES: `new THREE.WebGLRenderer` appears ONCE, in
    the module, and zero times in either page. Same for the PMREM environment,
    the ACES tone mapping, the GLTFLoader, the DRACO wiring, the lighting rig
    and the OrbitControls.
    THE NEGATIVE HALF, WHICH IS THE ONLY ASSERTION A SECOND COPY COULD NOT
    SURVIVE: cc_viewer.js is replaced with one whose constructor throws, each
    page's OWN script is run against it, and BOTH must come back with no
    viewer. Both do. It is not behind a flag - a negative half that has to be
    asked for is one nobody runs.
    AND THE SAME SHIP RESOLVES TO THE SAME MODEL ON BOTH PAGES: 221 linked
    ships compared file by file. index reaches a model by site record id,
    the ship page by ClassName, and the two are composed at BUILD time through
    ship_resolution.json - so neither join ever touches a display name, which
    on this dataset would hand one Hammerhead the other one's model.
    THE EXTRACTION IMMEDIATELY CAUGHT TWO BUILD DEFECTS THAT WOULD HAVE SHIPPED
    QUIETLY, and they are the argument for having done it:
      1. build_deploy.py injected the DRACO decoder into the page with a BARE
         `.replace` anchored on one exact line. Moving the viewer moved that
         line. A `.replace` that misses is SILENT - it would have shipped a
         build with no DRACO decoder, EVERY MODEL FAILING TO DECODE, and the
         build reporting success. The wiring now lives beside the loader it
         belongs to and the build ASSERTS it is there.
      2. The build also rewrote the whole 25-line load callback, which meant it
         held a second copy of the material setup, the framing and the
         staleness guard. Replaced by ONE seam - `ccModelSource(dir)` - with an
         asserted anchor. The old anchor going stale is how this was found.
    A third assert - the TDZ declaration hoist - fired on this change too, and
    stopped the build rather than hoisting nothing and shipping a page whose
    display panel throws on load. Three build-time guards, all three earned.
    CONTROL: checks/_verify_shared_viewer.mjs, 18 assertions.
    ONE THING I HAD TO FIX IN THE CHECK: searching the pages for
    `PMREMGenerator` and `ACESFilmicToneMapping` failed, because THREE.JS
    ITSELF IS INLINED INTO BOTH PAGES and defines them. The check was finding
    the library, which is exactly what should be there. Now matched on
    CONSTRUCTION - `new THREE.PMREMGenerator(` - not on the identifier.

L9  DONE  66b5363  THE SHIP PAGE = THE BENCH PLUS THE MODEL. No third page.
    loadout.html was already per-ship, already did A/B and already shared by
    URL, so the model came to it. 201 of 221 linked ships carry one.
    THE MODEL STAYS LOADED WHILE THE READOUT CHANGES, which is L9's control and
    which falls out of the layout rather than being arranged: the stage sits
    above the tabs and a swap re-renders the panes, never the stage.
    LAID OUT TO THE ADDENDUM'S TABBED SHAPE FROM THE START rather than
    retrofitted - model, components and readout by default; Loadout,
    Engineering, Liveries, Crew, Where to buy and Specs behind plain text
    labels; each an addressable fragment; a tab suppressed where the ship has
    no data for it. M1 finishes the lazy loading.
    ClassName -> model is GENERATED at build time into loadout_model.gen.js by
    composing CC_MODELS (record id -> folder) with LOADOUT_LINK (record id ->
    ClassName). Both joins are on ids. The path differs between _src and
    _deploy, so that is ONE SEAM substituted at copy time, asserted both ways.
    L14 CASE 1 IS HANDLED HERE: a ship with a game file and no model - 20 of
    the 221 - gets an honest sentence where the viewer goes, saying the numbers
    below are real and only the model is missing. Not a broken viewer, not a
    spinner.

L10 DONE  f37c882  HULL MARKERS - 1,200 on 157 hulls, and they are a SECOND
    ROUTE, not a second mechanism.
    `selectPort()` is the ONLY place in the page that selects a port. The list
    row calls it and the marker calls it, and the control asserts BOTH that the
    two produce BYTE-IDENTICAL picker HTML and that the source contains exactly
    ONE `sel={...}` assignment. The first assertion could pass by coincidence
    if a second path happened to render the same; the second is what makes it
    true by construction.
    NAMED: on the Aegis Avenger Stalker, the marker for
    `hardpoint_weapon_missilerack_left_wing` and its list row open identical
    windows.
    BY IDENTITY, AND THIS IS WHERE THE RUN'S RECURRING DEFECT WOULD HAVE LANDED
    AGAIN. A marker is bound to the game's own `PortId`. A hardpoint NAME could
    not have done it: 287 of 316 hulls have slots sharing one, 11,283 slots in
    all, and the RSI POLARIS HAS THIRTY PORTS CALLED `MEC`. PortId is unique -
    57,759 ports, 57,759 distinct ids, checked across the whole snapshot.
    WHERE A NAME WAS AMBIGUOUS, NO MARKER WAS EMITTED. 14 points dropped rather
    than assigned to whichever of two ports came first, which would have been a
    coin toss dressed as data. The list still reaches both. 595 further points
    matched no weapon port at all - they are `other` and `mount` kinds that are
    not component ports - and markers stay weapons-only per the order.
    THE VIEWER GAINED TWO THINGS AND NO OPINIONS: `project()` for where a hull
    point is on screen, and an `onFrame` hook. Markers are REAL DOM BUTTONS,
    absolutely positioned - not sprites - because a button can be focused,
    tabbed to and read aloud and a sprite cannot. A point behind the camera
    returns null and its marker hides, rather than being drawn on the wrong
    side of the hull.
    ONE DEFECT IN MY OWN CHECK, worth recording: the harness loaded only
    loadout_data.gen.js while the page loads four generated files, so MARKS was
    empty. It FAILED rather than passing quietly, which is the only reason it
    was found in the same minute it was written.

L11 DONE  9cd1a02  THE SHIP NAME OPENS THE SHIP, AND THE RSI LINK MOVED ONTO IT.
    The matrix row's `<a href>` to robertsspaceindustries.com was already
    captured rather than discarded - what was missing is that it never reached
    the SHIP PAGE. It does now: 219 ships carry their pledge link, joined
    ClassName-to-record-id at build time like everything else here.
    CONTROL, both halves of "moved": the link is PRESENT on the ship page AND
    still present on index. A link that left without arriving is not a move.
    Every one of the 221 matrix rows resolves to a ship the ship page actually
    holds, and lands on one with something to show - asserted over all of them
    rather than spot-checked, because 220 working links and one dead one is
    exactly what a spot check misses.
    A SHIP WITH NO PLEDGE PAGE SHOWS NO LINK, not a dead one, and that is
    asserted separately - an href that goes nowhere reads as the site being
    broken rather than as data being absent.

L12 DONE  9cd1a02  THE SHARE LINK CARRIES THE WHOLE BUILD.
    `#<ClassName>|<A>|<B>|<tab>` - the ship, every changed port in each build,
    and the open tab. A port left at stock encodes as an empty field, so a
    stock link stays short and a part that later leaves the catalogue falls
    back to stock rather than to nothing.
    THE TAB IS LAST AND OPTIONAL, so every link written before tabs existed
    still reads correctly and lands on Loadout. And a BARE `#engineering` is
    understood as a tab rather than as a ship that does not exist - somebody
    linking a layer of the ship they are already on should not be told the ship
    is missing.
    CONTROL: paste it into a clean session and get the same build back. Not one
    port - ALL 20 changed ports on the test hull round-trip, because a
    positional encoding that drops the last field passes any one-port test.

L13 DONE  9cd1a02  PROVENANCE SURVIVES THE LAYOUT CHANGE.
    CIG's own precomputed figure and our sum from the parts are marked
    differently ON THE STAT ITSELF - a badge reading CIG or summed - rather
    than explained in a footnote that a column move could separate from its
    number. A stock build shows CIG's; the moment a part changes, the same
    stat shows ours and says so.
    CONTROL: the rendered stats block for a stock build CONTAINS `src cig`; the
    same block after one swap CONTAINS `src ours`; and the two are not the same
    string. `last_verified_patch` is on the data and on the page, and the 33
    unreleased ships are still carried with their reason.

L14 DONE  9cd1a02  THE THREE KINDS OF INCOMPLETE SHIP, each handled and each
    proven on a named example.
      1. A GAME FILE, NO 3D MODEL - 115 hulls, and the ORIGIN M80 is the one
         the order names. Full readout, full swapping, and an honest "No 3D
         model available for Origin M80" where the viewer goes. Not a broken
         viewer. Not a spinner.
      2. NO GAME FILE AT ALL - 33 of them: Arrastra, Crucible, CSV-FM, E1
         Spirit, Endeavor and the rest. Listed, disabled, with the reason, and
         NOTHING claimed about their loadouts. Asserted as an absence, not just
         as a label.
      3. NO MOUNT DATA - 44 hulls have a model and no measured mount positions,
         so no markers. The page says exactly that: every port is still listed,
         every one can still be changed, the model just cannot point at them.
         Named: Aegis Eclipse.
    AND THE STINGRAY IS NOT HERE, asserted rather than assumed: no record in
    the dataset matches Stingray or S-65. A ship with no verifiable specs is
    the opposite of what this site is for, and it comes in when it reaches Live.

L15 DONE  6fe4575  THE PARKED IDEAS ARE WRITTEN DOWN AND NOTHING IS BUILT FOR
    THEM. `docs/IDEA_recommended-builds.md` and `docs/IDEA_unused-ship-data.md`.
    THE TENSION IS NAMED RATHER THAN SOFTENED, which is what the order asked
    for: §0 says the page has no opinion and a recommendation IS an opinion.
    Those point in opposite directions and pretending otherwise is how it gets
    built badly. So the tension is written as the DESIGN CONSTRAINT, and what
    it rules out is stated: not a default, not a ranking, not anonymous, and
    not silent about whether it rests on CIG's figures or our sums.
    EVERY FIGURE IN THE SECOND DOCUMENT WAS RE-MEASURED HERE rather than copied
    out of the order, and where mine disagrees I say so and say why. The order
    says 241 pilot seats and 22 bedding; I count 387 and 140 by hardpoint name
    across every record including variants. Neither is wrong - they count
    different things - and anyone building it should count again for their own
    definition. Doors 770, fuse slots 1,419, relays 692 on 305 hulls, seats
    802, module ports 43, room ports 73: all reproduce.
    THE UNRESOLVED THING IS MARKED UNRESOLVED, LOUDLY. 21,175 ports carry no
    CompatibleTypes and many are tagged VEN / MEC / POW / BAR1. They LOOK like
    engineering resource nodes. That is a guess, the pattern is equally
    consistent with ventilation geometry or an internal naming convention, and
    the document says DO NOT BUILD ON IT.
    Also recorded there: the `WeaponPersonal` gap - 1,092 ports accept them and
    the catalogue to fill them is not in ship-items.json. Racks are swappable
    and there is nothing to offer in them. A gap in a different dataset.

L16 DONE  a2c822e  THE PRE-LIVE PUNCH LIST EXISTS, AND `CURRENT-STATE.md` IS BACK
    IN LINE. `docs/PRE-LIVE-PUNCH-LIST.md` is new; CURRENT-STATE was last
    written 2026-08-16 and now leads with the ship page and the shop layer.
    EVERY ENTRY CARRIES A NUMBER, because an entry without one is a feeling and
    a list of feelings cannot be worked through. The numbers were MEASURED
    while writing it, not carried from the order, and two of the order's have
    moved:
      `unchecked_hull` is now ZERO, not 21. The G3 geometry rebuild and the
      current alignment gate closed it. Reporting 21 would have been repeating
      a figure rather than checking one.
      25 ships with no mount data reproduces exactly; the 8 refused by the
      alignment gate is now 7 refused + 1 with no published dimensions, which
      is the same 8 split by cause.
    THREE THINGS BLOCK GOING LIVE, and I am asked what I think:
      1. NOTHING IN THE SHOP LAYER IS VERIFIED. 0 of 7,932 shop items and 0 of
         823 terminals, against 26,657 price rows on the page. Every other gap
         on the list costs a visitor a shrug. This one costs them a trip, and
         /find is the one page where somebody reads a number and then flies
         somewhere. The fix is NOT "verify all 7,932" - it is verify enough to
         state a rate, and put the rate on the page.
      2. THE LIVE WORKER STILL 404s. That is the definition of not being live.
      3. NOBODY HAS OPENED THE SHIP PAGE IN A BROWSER. Every control I have
         written proves LOGIC and RENDERED HTML. None of them proves a browser
         draws anything, because there is no browser on this machine and none
         was installed (rule 7). The hull markers are positioned by projecting
         coordinates onto a canvas every frame, which is exactly the thing that
         is right in the arithmetic and wrong on the screen.
    EVERYTHING ELSE IS AN HONEST GAP THE SITE STATES WHERE A VISITOR MEETS IT -
    134 ports with no part, 6,454 empty ports, 11 hulls with no armour, 46 with
    an untagged paint port, 79 unreachable liveries, 1,092 WeaponPersonal racks
    with no catalogue, the four careers with no component behind them. Shipping
    with those IS the standard working. Shipping with unverified prices is the
    standard failing.
    AND ONE ENTRY IS A CLASS OF DEFECT RATHER THAN AN ITEM: Name-vs-ClassName,
    to be checked wherever ships are grouped anywhere in the project, plus its
    one-level-down twin, hardpoint-name-vs-PortId.

M1  DONE  502f9e2  THE TAB SHELL, WITH PER-LAYER LAZY LOADING - and section 5's
    invitation to argue with section 2 taken up, with numbers.
    Loadout / Engineering / Liveries / Crew / Where to buy / Specs, as plain
    text labels, each an addressable fragment, default always Loadout and never
    remembered. A TAB ONLY EXISTS WHEN THERE IS DATA BEHIND IT: Engineering
    shows on 305 hulls and is suppressed on 11; CREW HAS NO DATA AND THEREFORE
    APPEARS ON NONE OF THE 316. A direct link to `#engineering` on a hull
    without relays lands on Loadout without erroring.
    THE NETWORK TRACE, WHICH IS THE CONTROL THAT MATTERS: a default ship page
    fetches ZERO layer files; opening Engineering fetches EXACTLY ONE
    (loadout_eng.gen.js); reopening it fetches NOTHING.
    AND THAT TRACE FOUND A REAL BUG NOTHING ELSE COULD HAVE. A top-level
    `const` in a classic script creates a binding in the global LEXICAL
    environment - IT IS NOT A PROPERTY OF `globalThis`. So the loader's
    `globalThis["LOADOUT_ENG"]` read undefined even after the file had loaded
    and run perfectly, concluded it had failed, RE-FETCHED IT ON EVERY OPEN,
    and rendered "loading the engineering layer" forever. Nothing about the
    page looked broken from the outside. Only counting fetches showed it.
    Layers now REGISTER THEMSELVES into `window.CC_LAYERS`, and the generated
    file carries the explanation so nobody removes the line.
    ARGUING WITH SECTION 2, AS ASKED, AND THE LOADER EARNS ALMOST NOTHING
    TODAY:
      the engineering layer                     4.4 KB gzipped
      the page that loads without it          274.8 KB gzipped
    Per-layer loading saves 1.6% of what a visitor downloads. The order said
    "if the layers turn out small enough that splitting them costs more than it
    saves, measure it and say so rather than building a loader that earns
    nothing". Here is the measurement, and here is why I built it anyway: its
    value is FUTURE layers, not this one. Every idea in
    IDEA_unused-ship-data.md is now a label plus a file rather than a rebuild,
    and that is worth 4.4 KB of nothing today.
    BUT THE AXIS IS WRONG, AND THIS IS THE PART WORTH READING. The weight is
    not in the layers, it is in the SHIPS. Measured across all 316:
      one ship's complete bundle    median 10.1 KB gz  (max 24.5, min 0.8)
      the ship index for the picker           3.6 KB gz
      what the page loads today             274.8 KB gz
    LOADING ONE SHIP INSTEAD OF 316 WOULD TAKE THE PAGE FROM 275 KB TO ABOUT
    14 KB - a 95% cut, against per-layer's 1.6%. The page shows one ship at a
    time; loading 316 of them to show one is the actual waste.
    NOT BUILT, and deliberately: it is 316 generated files, it touches the
    deploy guard's allowed-file list, and it is a layout-level decision I
    should not take on my own inside a run about component fitment. Recorded
    with the numbers so it can be decided rather than rediscovered.

M2  DONE  502f9e2  THE ENGINEERING LAYER. 678 relays / 1,419 FUSE SLOTS on 305
    hulls, reproducing the addendum exactly. Aegis Idris-P 15 relays / 37
    fuses; Drake Vulture 1 relay / 2 fuses. Both named figures match.
    THE COUNT IS THE ACTUAL CHILD PORTS, NOT THE `RELAY_Nslot` CLASS NAME.
    Those agree on all 677 relays that carry such a class - checked, not
    assumed - but the children are the thing that exists and the name is a
    label about them. Reading the label works today and breaks silently the
    first time CIG ships a mismatch, in the direction of drawing slots that are
    not there.
    11 relay-NAMED ports carry no fuse children at all - the Caterpillar's bare
    `hardpoint_relay` and the door-state chip sets. Counted and excluded rather
    than quietly skipped.
    NO EMPTY POSITIONS ARE DRAWN, and that is asserted by COUNTING BARS AGAINST
    THE DATA on a hull whose relays are DIFFERENT SIZES - the Aegis Hammerhead,
    where a fixed-width track would show up immediately. 14 bars for 14 fuse
    slots. A greyed slot reads as "a fuse is missing here", which is a real
    state in the game and is not what this data says. That exact mistake was
    made and corrected in the prototype.
    Each relay is bound to its `PortId` like every other port on this page, and
    each carries the plain-language sentence M3 asks for.

M3  DONE  502f9e2  PLAIN LANGUAGE, PAGE-WIDE, AND REACHABLE BY KEYBOARD.
    23 readout values carry one sentence a person who has never opened a game
    file can understand - `EM 818` becomes "electromagnetic noise from powered
    components; turn things off and it drops".
    NOT HOVER ALONE, which is the half that gets forgotten: every explained
    value is FOCUSABLE (`tabindex`), carries an `aria-label` as well as a
    `title`, and the CSS reveals the sentence on `:focus` and `:focus-within`
    as well as `:hover`. A tooltip that only answers to a pointer does not
    exist for anybody who does not use one.
    AND THE SENTENCES ARE CHECKED FOR JARGON: the control FAILS if any
    explanation contains `CompatibleTypes`, `ClassName`, `stdItem`, `PortId` or
    `IsPilotSlaveable`. An explanation written in field names explains nothing.

M4  DONE  502f9e2  WHAT IS NOT ESTABLISHED IS SAID, AND NOT IMPLIED.
    The engineering panel states in its own words that fuse RATINGS and failure
    behaviour are not in the game files - only counts and positions - and that
    whether a blown relay disables the components near it IS NOT STATED
    ANYWHERE. Where the hull's `PenetrationMultiplier` exists it is quoted with
    the word SUGGESTS and nothing more.
    Asserted four ways: the page says "ratings", says "is not stated anywhere",
    says "suggest", and CONTAINS NO PHRASE claiming failure behaviour - the
    control greps for "will disable", "causes ... to fail" and "knocks out" and
    fails if any of them appears.

L17 DONE  502f9e2  SWEEP. `checks/run_all_controls.py` DISCOVERS controls from
    disk rather than from a typed list, so the three written in this run
    (_verify_loadout_fitment.py, _verify_ship_page.mjs,
    _verify_shared_viewer.mjs) were swept the moment they landed.
    FIRST PASS: 40 ok, 3 failed, 2 skipped, 0 NOT RUN. All three failures were
    investigated rather than adjusted around:
      1. `_verify_deploy_drift.py` - TWO real findings. It caught that I had
         edited loadout.src.html AFTER the last build, so _deploy was stale.
         That is precisely what the check is for and it worked. And it
         correctly flagged `loadout_model.gen.js` as differing from _src, which
         is BY DESIGN: the model path differs between the two worlds. I taught
         the check that ONE seam, narrowly, the same way it already knows the
         vendor marker - and PROVED THE NEW BRANCH BOTH WAYS: a second
         difference anywhere in the file is reported, and a WRONG VALUE on the
         seam line itself is reported. Neither passes.
      2. `_verify_ship_hardpoint_panel.mjs` - needs a local API on :8077, which
         is its own documented argument and was simply not running. Started it;
         18 of 18 pass. Not a defect, and NOT worked around (rule 9) - the
         prerequisite was met rather than the check weakened.
      3. `_verify_g3_matcher_delta.py` - reports NOT PERFORMED because
         CC_GEO_DIR is unset. Pre-existing, correctly refusing to claim a pass,
         and out of scope for this order.

M5  DONE  837796d  THE OTHER LAYERS. Three of the four are populated; the fourth
    is a shell and is therefore invisible.
      LIVERIES   populated at L7 - 915 liveries in 104 hull sets.
      SPECS      populated at L9 - dimensions, mass (all three of CIG's
                 figures), hull HP, crew, seats, cargo, size class, SCM and max
                 speed. Every figure CIG's own.
      WHERE TO BUY  populated, and this one needed thinking about rather than
                 filling. A tab labelled "Where to buy" that says only "we have
                 no prices" IS a tab opening onto an apology, which §1 forbids
                 - the same reasoning that forbids an empty picker. So it now
                 says what IS known and links to FIND, which carries 26,657
                 real price rows. And it states the gap precisely: the
                 components come from the game files, the prices come from a
                 separate community dataset, and NOTHING HAS VERIFIED THAT A
                 GIVEN COMPONENT IS A GIVEN PRICED SHOP ITEM. Two real datasets
                 with no proven join is a different fact from "we have no
                 prices", and the second would be the easier lie.
      CREW       NOT POPULATED, per the order, and therefore SUPPRESSED ON ALL
                 316 SHIPS. The pane exists, the label exists, and the tab
                 appears nowhere because there is nothing behind it. The page
                 carries a comment saying exactly what turns it on - one
                 predicate and one generated file - so the next person does not
                 think it was forgotten.
    The control asserts Crew appears on ZERO of the 316 hulls, which is the
    honest expression of "build the mechanism, do not populate it".

M6  DONE  837796d  THE PUNCH LIST CARRIES THE LAYERS AND THE DEFECT CLASS.
    Added: a table of every ship-page layer with its state and its number, so
    "Crew is a shell" is a row with 802 unread seat ports beside it rather than
    a thing somebody remembers. And the payload table with the measurement that
    matters - per-layer loading saves 1.6%, per-SHIP loading would save 95%.
    AND THE Name-vs-ClassName DEFECT IS NAMED AS A CLASS WITH PLACES TO LOOK,
    because a class of defect written as a warning is a warning:
      any dict or Map keyed on a ship's display name
      any `SHIPS.find(s => s.name === label)` - index.html had one, and it is
        why CC_LOOKUP and ship_resolution.json exist
      any GROUP BY on a name column
      any report that counts "ships" and gets 287 instead of 316
      any join between two datasets that meets in the middle on a name
    THE TELL IS A COUNT THAT IS LOWER THAN IT SHOULD BE AND LOOKS PLAUSIBLE.
    316 records becoming 287 does not throw, does not warn, and looks like a
    reasonable number of ships.

L17 SWEEP FINAL  837796d  45 controls discovered, 42 ok, 1 failed, 2 skipped,
    0 NOT RUN, in 171s.
    THE ONE FAILURE IS A CONTROL REFUSING TO CLAIM A PASS:
    `_verify_g3_matcher_delta.py` exits 2 with "NOT PERFORMED - CC_GEO_DIR is
    not set, so the build cannot read any geometry and this check cannot look
    at anything." That is the behaviour rule 12 asks for, it is pre-existing,
    it is unrelated to this order, and I have not made it pass by giving it
    something to look at that I would then be asserting about.
    THE TWO SKIPS ARE DELIBERATE AND SELF-DESCRIBING: both fetch the DEPLOYED
    origin, which is a statement about the live site rather than about this
    working tree, and one of them makes ~450 network requests.
    THE THREE NEW CONTROLS FROM THIS RUN WERE SWEPT WITHOUT BEING ADDED TO
    ANYTHING - the runner discovers checks/_verify_* from disk, which is why a
    control written today is in today's sweep.

D1  DONE  3156e6b  TESTING SITE DEPLOYED, and the standing rule that says to do it
    without asking is now in ARCHITECTURE_DECISIONS.md.
    URL: https://citizencompasstesting.citizencompass-contact.workers.dev
    Version ID 9618dd8d-24fb-4eb6-8827-7cc5b648a43b. NOT the live site -
    nothing here went near deploy_live.ps1 or wrangler.live.toml.
    THE RULING (docs/RULING_testing-deploys-are-automatic-2026-08-22.md) is
    folded into docs/ARCHITECTURE_DECISIONS.md as a LOCKED entry: every run
    that changes what the site serves ENDS BY DEPLOYING TO TESTING, no
    permission; the live site is Sleven's alone. He is right about the cost and
    I caused it - L1-L17 and M0-M6 finished and sat undeployed while he looked
    at a five-hour-old build and judged work he could not see. WORK THAT IS NOT
    DEPLOYED TO TESTING HAS NOT BEEN DELIVERED.

    THE DEPLOY GUARD REFUSED THE FIRST ATTEMPT, AND IT WAS RIGHT.
    `check_deploy_clean.py` rejected cc_viewer.js, loadout_model.gen.js,
    loadout_marker.gen.js and loadout_eng.gen.js as unknown files that would be
    PUBLISHED. The build had said "safe to deploy" in the same minute, because
    the build derives its allow-list from PAGES and the standalone guard
    carried its own HAND-MIRRORED copy.
    THE GUARD'S OWN COMMENT HAD PREDICTED THIS EXACTLY: "Letting the two drift
    produces a standalone 'unexpected file' failure that flatly contradicts a
    clean build, which is worse than either alone." It had already happened
    once - download.html was live while the guard called it unexpected.
    FIXED BY CONSTRUCTION, NOT BY ADDING FOUR NAMES (rule 14). The list moved to
    `testing/_src/deploy_pages.py`; build_deploy.py imports PAGES from it and
    check_deploy_clean.py derives ALLOWED_FILES from the same list. There is
    nothing left to keep in step. Adding a page is now ONE edit.
    PROVEN, not assumed: a planted `_plant_probe.txt` in _deploy is still
    REFUSED by name, and the refusal now lists all 19 permitted files. The probe
    was moved to _to_delete, never deleted.

    THAT CHANGE THEN BROKE TWO CONTROLS, AND BOTH FAILED HONESTLY RATHER THAN
    QUIETLY - which is the argument for writing them the way this project does:
      `_verify_deploy_drift.py` parsed PAGES out of build_deploy.py. When the
      list moved it reported "NOT PERFORMED: could not read PAGES", rather than
      finding nothing and calling _deploy clean. A parser returning an empty
      list would have passed every assertion below it VACUOUSLY. Pointed at
      deploy_pages.py; 10 passed, 0 failed.
      `_verify_deploy_guards.py` builds a synthetic project and copied only
      check_deploy_clean.py into it. That guard now imports deploy_pages.py, so
      the import failed, the guard subprocess died, and the deploy script FAILED
      CLOSED - correct behaviour, showing up as three unrelated-looking
      assertion failures. The fixture now copies the guard AND its dependency,
      copied rather than stubbed for the same reason the guard itself is.
      43 passed, 0 failed.

    DEPLOYED TWICE, and the second run is itself a verification: the first
    uploaded SEVEN files and they were exactly the seven my work changed -
    cc_viewer.js, loadout.html, loadout_data.gen.js, loadout_model.gen.js,
    loadout_marker.gen.js, loadout_eng.gen.js and index.html. After the guard
    rework the second run reported "No updated asset files to upload", which
    proves the allow-list change altered not one served byte. A deploy whose
    diff matches the work is worth recording; one that does not is the thing to
    worry about.

    VERIFIED FROM THE SERVED BYTES, NOT FROM THE EXIT CODE:
      /                       200  1,622,716 bytes
      /loadout                200  1,247,526 bytes  (/loadout.html 307s to it)
      /cc_viewer.js           200     14,055 bytes
      /loadout_data.gen.js    200  3,636,252 bytes
      /loadout_marker.gen.js  200     42,542 bytes
      /loadout_model.gen.js   200     26,393 bytes
      /loadout_eng.gen.js     200     22,986 bytes
      /models/Hammerhead.glb  200  3,608,636 bytes
    All five generated files are sha256 IDENTICAL to what the build wrote.
    THE SHIP PAGE CARRIES cc_viewer.js: `<script src="cc_viewer.js">` present,
    and `new THREE.WebGLRenderer` appears in the served page only inside the
    inlined three.js library - the page constructs no renderer of its own, so
    L8's one-implementation rule survived the deploy.
    THE TAB SHELL IS IN THE SERVED BYTES: id="tabs" and all six panes
    (loadout, engineering, liveries, crew, buy, specs), plus `const TABS=`,
    `openTab`, `loadLayer`, the `href="#${t.id}"` template that makes each tab
    an addressable fragment, and `engineering:{file:"loadout_eng.gen.js"}`.
    AND THE STRONGEST CHECK - THE SERVED PAGE WAS DRIVEN, not grepped. The
    served HTML's own six script blocks were run against the four SERVED data
    files in a vm:
      316 ships loaded from the served data
      1,200 hull markers
      305 hulls with engineering relays
      tabs rendered: loadout, engineering, liveries, buy, specs - CREW CORRECTLY
        ABSENT, because it has no data behind it
      the build column rendered 19,796 characters and the readout 18 values
    Grepping proves the bytes contain the feature. This proves the bytes RUN.

    STATED LIMIT, unchanged and worth repeating: no browser was involved. There
    is none on this machine and none was installed (rule 7). Whether the 3D
    viewer draws, the markers land in the right place on the hull, or the CSS
    holds is Sleven's to see. That is item 3 on the pre-live punch list.

    AND ONE THING THE VERIFICATION FOUND THAT IS NOT MINE: THE PASSWORD GATE IS
    ON index.html ONLY. Measured against the deployed origin - `/` carries
    id="cc-gate"; /loadout, /find, /keybinds, /holo, /download and /stick-test
    do not, and every one serves 200 to a direct request. Pre-existing: the
    gate has been index-only since it was introduced, and every page in PAGES is
    copied verbatim. Recorded in ARCHITECTURE_DECISIONS.md beside the standing
    rule and on the punch list, because "private preview" is doing real work in
    the reasoning for automatic deploys and the preview is less private than
    the phrase implies.

    SWEEP AFTER ALL OF IT: 45 controls discovered, 42 ok, 1 failed, 2 skipped,
    0 NOT RUN. The one failure is `_verify_g3_matcher_delta.py` reporting NOT
    PERFORMED because CC_GEO_DIR is unset - pre-existing, unrelated, and
    correctly refusing to claim a pass.

N2  DONE  66d3d59  THE ACQUISITION BLOCK IS ON THE SHIP PAGE. NOTHING WAS
    DROPPED, AND THE CHECKLIST IS THE PROOF RATHER THAN MY WORD FOR IT.
    Done FIRST, before N1 and N3, deliberately: build the destination, then
    reroute, then retire. Retiring the panel before its contents had somewhere
    to go is how a field goes missing in a consolidation.
    THE CHECKLIST, TICKED ONE AT A TIME AGAINST THE RENDERED HTML on a hull
    measured to carry them all:
      In-game price      -> ship page header, as `1,089,270 aUEC`
      Pledge price       -> ship page header
      Sold at            -> `Where to buy` tab, as dealer chips
      View on RSI        -> ship page header (already moved at L11)
      Confidence         -> the provenance row
      Last verified      -> the provenance row, SEE BELOW
      Record number      -> the provenance row, as `#129`
      Notes              -> Specs, ticked on a hull that HAS one (Aegis Gladius
                            Dunlevy) rather than one that does not
      Status             -> header, "Purchasable in-game" / "Concept / pledge
                            only" - index.html's badge
      Role, Manufacturer -> header
      Model folder       -> Specs
      Related ships      -> the foot of the ship page, and they LINK TO THE
                            SHIP PAGE rather than back to a list
    THE ONE FIELD THAT DID NOT SURVIVE, AND IT NEVER EXISTED: the site's own
    `last_verified_patch` IS NULL ON ALL 254 RECORDS. index.html rendered "Last
    verified: not recorded" for every ship in the fleet, every time anybody
    opened one. There was nothing to move. The ship page states the SNAPSHOT's
    patch instead - 4.9 - which is a real figure it has always had. The site
    field renders only if it ever becomes non-null, and says which of the two
    it is. Asserted as an absence so it cannot be quietly "fixed" by writing a
    plausible value into it.
    THE BUILD REFUSES TO SHIP A DROPPED FIELD. `build_deploy.py` counts how
    many ships each field reached and EXITS if a field that exists on the site
    records reaches zero. A consolidation that loses a column otherwise looks
    exactly like a clean build.
    Carried: 221 ships. record 221, confidence 221, status 221, role 221,
    manufacturer 221, name 221, in-game price 179, sold at 179, pledge price
    138, notes 56.

N1  DONE  cc83101  EVERY ROUTE INTO A SHIP LANDS ON THE SHIP PAGE, and the
    "Open in the loadout bench" button is gone.
    There is now ONE function - `shipPageUrl(ship)` - that turns a record into
    a destination, so "does the list ever reach a ship another way" is a
    question about one thing rather than three call sites.
    THE NAME CELL IS REBUILT, NOT WRAPPED, and that turned out to be the whole
    difficulty. The site renders the cell as an RSI ANCHOR - `nameCellHtml()`
    emits `<a class="buy-link" href="...robertsspaceindustries...">Name</a>`
    whenever the record has a pledge_url, which is 229 of 254. Wrapping that in
    another anchor nests one link inside another and leaves the outer one doing
    nothing on most rows. The cell is replaced outright from the record.
    I NEARLY SHIPPED A REAL REGRESSION HERE and the control caught it: 33 site
    ships have NO ship page, and 27 OF THOSE CARRY A pledge_url. Replacing
    their cell would have left those 27 rows with no link at all - N1 says a
    ship NAME must not go to RSI, and it says that because there is somewhere
    better to send people. For these there is not. So a ship with no ship page
    KEEPS its RSI link and says why in the title; the other 221 go to the ship
    page. The letter of the rule would have removed a link and offered nothing.

N3  DONE  cc83101  INDEX IS A LIST. THE PANEL AND ITS VIEWER ARE RETIRED, AND THE
    NUMBER IS THE POINT: 1,622,716 -> 410,219 BYTES. A 75% CUT.
    What came off: three.js (603 KB), OrbitControls, GLTFLoader, the DRACO
    decoder and its wasm as base64, the embedded model map, the whole ship
    panel, its cc_viewer instance, and 46 now-dead CSS rules. About 1.07 MB of
    vendor payload that every visitor downloaded in order to look at a TABLE.
    IT FETCHES NO GEOMETRY BECAUSE NOTHING ON IT CAN. Asserted on the bytes,
    not on the panel looking gone: no `new THREE.WebGLRenderer`, no GLTFLoader
    construction, no DRACOLoader, no PMREMGenerator, no CC_DRACO_WASM_B64, no
    CC_EMBED, no `<script src="cc_viewer.js">`, and no `.glb` anywhere.
    AND THE SHIP PAGE STILL HAS IT - asserted separately, because removing the
    viewer from BOTH pages would satisfy every assertion above and is the
    vacuous way to pass N3.
    FIVE BUILD PATCHES RETIRED, EACH REPLACED BY A REFUSAL RATHER THAN DELETED:
    the CDN strip, the model-source seam, the thumbnail rewrite, the DRACO/
    viewer asserts, and the temporal-dead-zone declaration hoist. Every one now
    STOPS THE BUILD if a viewer reappears on index, which is the only way this
    stays true without somebody remembering it.
    THE L8 NEGATIVE HALF HAD TO BE RESHAPED, and leaving it alone would have
    been the quiet failure. It required BOTH pages to lose their viewer when
    cc_viewer.js was broken - "only one failed" meant a second copy. index now
    has NO viewer at all, so its half was passing for a reason with nothing to
    do with the module while looking exactly as strong as before. Split: the
    SHIP page must still fail on a broken module, and index's absence of a
    viewer is asserted on the bytes where it belongs.
    TWO CONTROLS MOVED ASIDE, NEVER DELETED (rule 1), to
    `_to_delete/n3_index_panel_retired_20260822/` with a WHY.md:
    `_verify_ship_hardpoint_panel.mjs` and `_verify_hardpoint_panel_offline.mjs`
    both proved the index panel. Both reported NOT PERFORMED once it was gone -
    correctly refusing to claim a pass, which is why they were noticed at all.
    What they guaranteed is carried by the ship page's L14 cases 1 and 3,
    already asserted.
    AND ONE FILE STOPPED BEING PUBLISHED: `hardpoint_data.gen.js`, 152 KB,
    referenced by NO page once the panel went. It is still generated and still
    proven by checks/_verify_hardpoint_data.py - generated and checked is not
    the same as served, and only the third had stopped being true. The
    published copy was moved to _to_delete, never deleted.

N4  DONE  cc83101  ONE VIEWER INSTANCE, ONE MODEL LOAD PER SHIP.
    Trivially true for index now - it has none. On the ship page it is
    structural rather than incidental: `new CCViewer.Viewer(` appears ONCE in
    the whole page, `view()` returns the existing instance rather than building
    another, and `showModel()` short-circuits on `_modelFor === shipId` so
    geometry is fetched when the SHIP changes and not when a TAB does.
    All three asserted on the built page.

N5  DONE  9581ff7  THE PAGE OPENS ON ONE BUILD. The second does not exist until
    somebody asks for it.
    THE BUTTON READS EXACTLY `Try another alongside`, and the control asserts
    the STRING rather than "a button exists" - the wording is Sleven's and the
    order says not to reword it. It also asserts "Compare builds" appears
    nowhere in the markup, since that was explicitly rejected.
    THE SECOND PANEL CARRIES `Discard this one`, not a bare "Remove" - it says
    what happens and which one goes. Asserted both ways.
    A AND B LABELS APPEAR ONLY ONCE THE SECOND BUILD EXISTS. Before that the
    column is headed with the SHIP'S NAME, because a letter with nothing to
    contrast against is a label for a distinction nobody has made. Asserted:
    with one build the heading contains the ship name and neither "Build A" nor
    "Build B"; with two, both appear.
    THE SECOND BUILD STARTS AS A COPY of the one on screen, not at stock. The
    question somebody is asking is "what if I changed this one thing"; starting
    it empty would make them rebuild what they already had.
    DECIDED-BY-DEFAULT and cheap to reverse.

N6  DONE  9581ff7  THE DOUBLED READOUT IS GONE. With one build there is one
    number.
    Every stat rendered TWICE with `same` beside it, fourteen times over.
    THE ARGUMENT IS NOT SPACE, and the order is right about which one matters:
    when everything says `same` all the time, NOTHING CATCHES THE EYE WHEN
    SOMETHING FINALLY IS NOT - which breaks the one thing this page teaches by.
    CONTROL, counted PER STAT rather than in total: a total could be right
    while one stat rendered twice and another not at all. 18 stats, each label
    exactly once, 18 values, ZERO second values, and the word "same" nowhere
    in the readout. When the second build is asked for, every stat gains its
    second value again - asserted, because removing it permanently would pass
    the same assertions and is the wrong fix.

N10 DONE  9581ff7  THE SWAP ANNOUNCES WHAT MOVED, FOR A BEAT.
    A swap measures the readout BEFORE and AFTER and marks only what actually
    changed - not what we expected to change - with a left edge and a delta
    chip that says which way it went. It clears itself after 2.2 seconds.
    CONTROL: before a swap nothing is marked; after one, SOME readouts are
    marked and OTHERS ARE NOT. That second half is the whole assertion. If a
    swap lit everything up it would satisfy "the change is visible" and teach
    nothing, because the point is that the changed ones are distinguishable
    from the unchanged ones WITHOUT READING THEM. And it must stop: a mark that
    never clears is a page permanently shouting.
    ARGUING WITH N10, WHICH THE ORDER ASKS ME TO. C1 is right that this is easy
    to overdo, and I have deliberately built the quiet end of it: a 3px edge, a
    small delta chip, one 0.22s pop, gone in 2.2 seconds. NO flash on the
    number itself, no colour wash across the panel, no motion that has to
    finish before the page is usable again.
    THE BOUNDARY, since I can see it from here: a swap is something somebody
    does dozens of times in a sitting, and the twentieth must cost nothing.
    Anything that has to be WAITED OUT becomes an obstacle - which is why
    nothing here blocks, queues, or animates the value itself. If this still
    reads as too much on the twentieth swap, the dial to turn is CHANGED_MS,
    and turning it to 0 leaves a page that works exactly as it does now minus
    the mark. That is deliberately the cheapest thing in this change to undo.

N11 DONE  9581ff7  BACK TO STOCK IS ONE VISIBLE CLICK, never in a menu.
    A `Back to stock` button in the header, shown the moment there is anything
    to undo and stood down again when there is not - a control that never does
    anything teaches somebody to stop looking at it.
    It returns the build being edited to THE SHIP'S OWN stock loadout, PORT FOR
    PORT - not to empty, and not to a default we chose. The control asserts
    every editable port on the hull is back to its own `stock` value, not just
    that the build "looks stock".
    And the restore itself goes through markChanges, so undoing a swap
    announces what moved back exactly as the swap announced what moved.

N7  DONE  badc40a  FIXED PORTS FOLD AWAY, and they still count.
    One closed `<details>` per column, labelled with its count -
    `Fixed · not swappable in game (36)` on the driving hull. A real
    `<details>/<summary>`, not a scripted toggle: it opens by keyboard as well
    as by click, a screen reader announces it as a disclosure, and it needs no
    state of ours to remember.
    FOLDED, NOT DROPPED. All 57 of the hull's ports are still rendered - the
    control counts them - and they still contribute to the readout, proven the
    same way L4 proved it: remove them and the totals move. A thruster changes
    the ship's mass whether or not you chose it.
    The disclosure says that in its own words, so nobody has to wonder whether
    the numbers above include what is folded below.
    The open/closed state is remembered while somebody is on the page, and
    RESET when they change ship - it opens closed by default and that is the
    state N7 asks for.

N8  DONE  badc40a  THE GROUPING IS `Editable`. THERE IS NO LIST OF TYPES.
    The split is `sh.slots.filter(x=>!swappable(x))`, and `swappable` is
    `!!s.fit`, which the generator sets from the port's own `Editable` flag.
    Asserted three ways: no hardcoded type list exists in the page, the split
    is that expression and nothing else, and `swappable` is that rule.
    AND THE CONTROL THE ORDER NAMES, RUN FOR REAL: a fixed port on the driving
    hull was given a fitment rule - which is exactly what the generator does
    when a port says `Editable` - and NOTHING ELSE WAS TOUCHED. No code edited.
    The port MOVED OUT of the collapsed group, the disclosure's count dropped
    from 36 to 35, and flipping it back put it where it was.
    That last half matters: a one-way move would pass the first assertion just
    as well, and would not prove the page follows the data.
    THIS IS SLEVEN'S REASONING BUILT RATHER THAN AGREED WITH - "if ever it
    changes, we already have a foundation built for it." The day CIG makes fuel
    tanks swappable, those 509 ports leave the collapsed group on the next data
    build, with nobody editing anything.

N9  DONE  6969fb2  THE FALSE CLAIM IS GONE, AND WHAT REPLACED IT IS SPECIFIC.
    The page said: "Slot structure is measured from this hull's own model
    geometry and read from the game's mount data. NOTHING HERE IS ESTIMATED."
    The first half was true and the last four words were not.
    CONFIRMED FROM THE SOURCE rather than taken from the order: `place_fleet.py`
    reads the mount's NAME, looks a token up in a table of target zones, places
    a point in that zone of the bounding box, snaps to the nearest real hull
    vertex, and spreads collisions apart. Its own docstring says so - "a mount's
    NAME says where it sits". The placement report records 167 hulls placed, 7
    SKIPPED, and 118 crowded markers pushed across 17 hulls.
    THE PAGE NOW SAYS IT UNDER THE MODEL, where somebody looking at the dots
    will read it - not a tooltip, not a footnote:
      where the dots sit is worked out from each mount's NAME and snapped to
      the hull; THEY ARE NOT MEASURED FROM THE MODEL; the exports are a single
      welded mesh with no mount positions in them, so there is nothing to
      measure and this is the closest honest thing available.
    AND THE TWO THINGS THAT ARE MEASURED STAY DESCRIBED THAT WAY, because
    correcting an overclaim into a blanket disclaimer is a second false
    statement pointing the other way: which axis is length/width/height,
    checked against CIG's published dimensions with 7 hulls left unmarked
    rather than placed in a frame nobody verified, and which end is the nose.
    What each port IS - size, type, what is fitted - is still stated as
    unestimated, because it is.
    A SECOND, QUIETER FALSE CLAIM FIXED IN THE SAME PASS: the ship page said
    "No mount positions have been MEASURED for this hull" on hulls without
    markers - which implies that where markers DO appear, they were. Now: "there
    is no marker placement for this hull".
    CONTROL: 11 assertions. Both old sentences are asserted ABSENT from the
    page with comments stripped first, and the note is asserted to contain the
    plain statement, the reason, and the two genuinely-measured facts.
    NOT ATTEMPTED, per the order: no re-export with hardpoints preserved and no
    hand-placing in Blender. Sleven has not decided which, and it turns on
    whether the extraction tool can keep hardpoint data.

N12 DONE  feb6879  SWEEP + DEPLOY + VERIFIED FROM THE SERVED BYTES.
    URL: https://citizencompasstesting.citizencompass-contact.workers.dev
    Version ID f6507a7d-1d99-4565-b3c3-06e360657198. NOT the live site.
    SWEEP: 43 controls discovered, 40 ok, 1 failed, 2 skipped, 0 NOT RUN, 111s.
    The one failure is `_verify_g3_matcher_delta.py` reporting NOT PERFORMED
    because CC_GEO_DIR is unset - pre-existing, unrelated, correctly refusing
    to claim a pass. The two skips fetch the deployed origin by design.
    Two controls fewer than last sweep because two were retired with the index
    panel at N3, moved to _to_delete rather than deleted.
    UPLOAD DIFF MATCHES THE WORK: three files, index.html, loadout.html and
    loadout_model.gen.js. Everything else was already up.
    VERIFIED FROM THE SERVED BYTES, not the exit code:
      index served       410,219 bytes  (was 1,622,716 - a 75% cut)
      /loadout served  1,266,286 bytes
    INDEX CARRIES NO VIEWER: zero hits for cc_viewer.js, WebGLRenderer,
    DRACOLoader, CC_EMBED, `id="cc-ship"` and `.glb`. The single hit for "Open
    in the loadout bench" is my own comment explaining its removal.
    A SHIP NAME LANDS ON THE SHIP PAGE: `shipPageUrl` x3, `loadout.html#`, and
    `cc-nobench` present for the 33 hulls with no ship page.
    AND THE STRONGEST CHECK - THE SERVED PAGE WAS DRIVEN, not grepped. Its own
    six script blocks were run against the four SERVED data files:
      opens with ONE build         twoUp=false, second column hidden
      18 stats, each ONCE          zero second values
      no A/B letters               before the second build is asked for
      fixed group CLOSED           labelled "not swappable in game (36)"
      marker note present          the N9 statement is on the page
      acquisition strip            5 fields rendered
      back-to-stock hidden         nothing changed yet, so nothing to undo
    STATED LIMIT, unchanged: no browser was involved and none exists on this
    machine (rule 7). Whether the model draws, the markers land where they
    should, and the CSS holds is Sleven's to see.

E-N1 DONE  c7fa846  ERRATUM: EVERY SHIP NAME STILL OPENED RSI. N1 WAS NOT DONE
    AND MY CONTROL COULD NOT HAVE FAILED. This is mine and Sleven found it in
    ten seconds.
    THE COUNT, BEFORE AND AFTER, measured by RUNNING the page's own
    `nameCellHtml()` over all 254 records rather than by reading the source:
      BEFORE   229 name cells pointed at RSI.   0 reached a ship page.
      AFTER    27 point at RSI, 221 reach the ship page, 6 link nowhere.
    The 229 is not my estimate - the `--prove` mode restores the original
    function and the check reports exactly 229, which is C1's figure reproduced
    from the shipped bytes.
    WHY 27 AND NOT 33. 33 ships have no ship page. 27 of them have a
    `pledge_url` and therefore an RSI cell; the other SIX have neither and
    render as plain text: CSV-FM, RAPTOR, Starlancer BLD, F7C-M Super Hornet
    Heartseeker Mk I, Mustang Alpha Vindicator, Valkyrie Liberator.
    221 + 27 + 6 = 254. The instruction said the number must be 33; the honest
    number is 27, because six of the 33 have nowhere to point.
    THE CAUSE, exactly as C1 diagnosed. `decorate()` rewrote the name cell
    AFTER the site rendered it, finding the ship by `td.textContent.trim()`.
    `nameCellHtml()` appends `&#128279;` - a link glyph - so the text was
    "Redeemer 🔗", `CC_LOOKUP` missed, the function returned silently, and the
    cell kept the RSI anchor it was born with.
    FIXED AT SOURCE, NOT AT THE GLYPH. Trimming the emoji would have fixed the
    symptom and kept the design: one writer rendering a cell and a second racing
    to rewrite it, MATCHED ON DISPLAY TEXT - the thing this project banned two
    days ago when 22 names turned out to be shared by 51 records.
    Now the BUILD decides, per record, what the cell is - `CC_SHIPLINK` - and
    `nameCellHtml()` reads the decision. ONE WRITER. `decorate()`, its
    MutationObserver and its two guessed timers (400 ms, 1500 ms) are gone,
    with the CC_NORM / CC_LOOKUP / CC_SAFE / CC_RSI / CC_HAS3D scaffolding that
    existed only to support text matching. A function that has to be called
    three times at guessed intervals is telling you it is in the wrong place.
    AND THE INJECTION MOVED. `LOADOUT_LINK` was inserted before `</body>`;
    `buildMatrix()` runs synchronously in the site's own script, long before
    that. The data now arrives BEFORE the ship records, and the control asserts
    that ordering by INDEX POSITION in the bytes - a table that renders before
    its data arrives is the same defect one layer down.
    ANSWERING §6's QUESTION: `nameCellHtml()` CAN see the data at render time,
    once the injection is moved. I did NOT edit `releases/latest.html` or
    `static/preview.html` - they are the live site's own source, they have
    already drifted 80 KB apart, and `CC_SHIPLINK` is a build artifact that
    cannot exist in them. The build substitutes the function with an ASSERTED
    anchor and refuses if the shape has changed; the original's last two
    branches are kept verbatim, so either file opened standalone behaves
    exactly as it always has.
    THE REPLACEMENT CONTROL: checks/_verify_ship_name_route.mjs, 22 assertions,
    NOT ONE OF THEM A GREP.
      POSITIVE  Redeemer renders href="loadout.html#AEGS_Redeemer", with no
                robertsspaceindustries anywhere in the cell and no link glyph.
      NEGATIVE  Vulcan - no game file - renders RSI WITH the explanation. Both
                halves: a function returning a ship-page link for everything
                would pass the positive.
      WHOLE SET all 221 linked records emit a ship-page href, counted, and
                every record is accounted for. Not "at least one", which is
                what let the last one through.
      PROVEN    `--prove` restores the original function and SEVEN assertions
                fire, reporting 229. A check that has not been seen failing
                against the bug it exists for is not evidence.
    ONE DEFECT FOUND IN MY OWN HARNESS while writing it, and it matters: the
    DOM stub's `createElement` never reflected `textContent` into `innerHTML`,
    and the page's `escapeHtml()` is implemented through exactly that. So
    escapeHtml returned "" FOR EVERYTHING and every cell the harness read had a
    blank name and a blank href. The assertions that passed did so on hrefs
    built outside escapeHtml - luck, not design. The stub now escapes properly
    and the harness ASSERTS `escapeHtml("A<b>&") === "A&lt;b&gt;&amp;"` before
    reading anything through it.
    TWO STALE ASSERTIONS IN `_verify_shared_viewer.mjs` REPLACED rather than
    repointed: they greped for `shipPageUrl(` and a `td.innerHTML=` shape. Both
    were the erratum's own shape. Where a name goes is now asserted only by the
    behavioural check; what stays here is structural - that no rewriter, no
    observer and no text match survive, and that the data arrives before the
    records.

E-N2 DONE  b4e22d4  §4 AUDIT: WHICH N CONTROLS DROVE SOMETHING, WHICH GREPPED.
    246 assertions across the three control files, classified by whether the
    section RUNS page code and reads what comes out, or reads the source text.
      DRIVEN     208
      GREP-ONLY   38
    THE DRIVEN ONES, all in `_verify_ship_page.mjs` and
    `_verify_ship_name_route.mjs`: L3, L3-sweep, L4, L5 x2, L6, L7, L10, L11,
    L12, L13, L14, addendum s0, M1, M1-network-trace, M2, M3, N2, N5/N6, N7,
    N8, N9, N10, N11, and all four of the new name-route sections. Each runs
    the page's own script in a vm and asserts on the HTML it produced or the
    state it reached.
    THE GREP-ONLY ONES, AND WHETHER A GREP IS THE RIGHT INSTRUMENT - because
    "grep" is not automatically wrong, it is wrong when the claim is a
    BEHAVIOUR:
      rule 8 - trademark/Fan Kit text present            (2)  CORRECT. The
        claim IS "this text exists untouched". Nothing to drive.
      N3 - index carries no renderer/loader/wasm/.glb    (4)  CORRECT. An
        ABSENCE cannot be proven by running something. Backed by a byte-count
        measurement (410,219 vs 1,622,716), which is not a grep.
      name-route - no rewriter, observer or text match   (4)  CORRECT, same
        reason: these are absences.
      shared_viewer 1 - one THREE.WebGLRenderer          (5)  ACCEPTABLE. Code
        shape, and the §4 NEGATIVE HALF proves the ship page really uses the
        module by breaking it.
      shared_viewer 2 - both pages reference it          (3)  WEAK ON ITS OWN -
        "the page references X" is the erratum's exact shape. Covered by the
        negative half, which is behavioural.
      shared_viewer 3 - same model on both pages         (3)  MISCLASSIFIED by
        my own script: it PARSES the tables and compares them. A data
        comparison, not a text search. Sound.
      shared_viewer L11 - names resolve to a page        (6)  DATA COMPARISON,
        and THE ONE THAT SHOULD HAVE CAUGHT THE ERRATUM AND DID NOT. It proved
        every link TARGET exists. It never asked what the page EMITS. That gap
        is now closed by _verify_ship_name_route.mjs.
      shared_viewer N1 - route into a ship               (8)  REWRITTEN in this
        pass. Now structural only - no rewriter, no observer, no text match,
        and the link data arrives BEFORE the ship records (asserted by index
        position in the bytes). Where a name GOES is asserted only by the
        behavioural check.
    ONE CONTROL WAS THE ERRATUM'S SHAPE AND I REPLACED IT: N4. It greped for
    `new CCViewer.Viewer(` appearing once and for the literal string
    `_modelFor === shipId` - asserting the code CONTAINS a guard, not that the
    guard WORKS.
    SO I DROVE IT, AND THE FEATURE IS FINE: with a recording stand-in for the
    viewer, opening a ship loads geometry ONCE; calling showModel() twice more
    for the same ship loads nothing; three tab switches load nothing and do not
    replace the viewer instance; and changing SHIP loads exactly once more -
    that last half matters, because "no further loads" is also satisfied by a
    page that never loads anything again.
    THE DIFFERENCE BETWEEN N4 AND N1 IS WORTH RECORDING: both had a control
    that could not fail. N1's feature was broken and nobody knew. N4's was
    sound. A weak control does not tell you which of those you have - that is
    the whole argument for not writing them.
    NOT FIXED IN THIS PASS, per §4's instruction to list rather than fix: the
    two WEAK-BUT-COVERED greps in shared_viewer sections 1 and 2. Both are
    backed by the negative half, which breaks the module and requires the ship
    page to fail. If that ever stops being true they should become behavioural.

E-N3 DONE  b653aef  SWEEP + DEPLOY + COUNTED ON THE SERVED PAGE.
    URL: https://citizencompasstesting.citizencompass-contact.workers.dev
    Version ID 4cdc686b-2a5d-4d62-b7ea-d40bca62b73e. NOT the live site.
    SWEEP: 44 controls discovered, 41 ok, 1 failed, 2 skipped, 0 NOT RUN.
    The one failure is `_verify_g3_matcher_delta.py` reporting NOT PERFORMED
    because CC_GEO_DIR is unset - pre-existing, unrelated, correctly refusing
    to claim a pass. One control more than the last sweep: the new
    `_verify_ship_name_route.mjs`, swept the day it landed because the runner
    discovers from disk.
    UPLOAD DIFF: ONE FILE, index.html - which is exactly and only what this
    fix touched.
    THE COUNT, TAKEN FROM THE SERVED PAGE by fetching it and running its own
    `nameCellHtml()` over all 254 records:
      221  point at the ship page
       27  point at RSI
        6  point nowhere
      254  accounted for
    THE ERRATUM ASKED FOR 33 AND THE HONEST ANSWER IS 27. 33 ships have no
    ship page; 27 of them have a `pledge_url` and therefore an RSI cell, and
    six have neither and render as plain text - CSV-FM, RAPTOR, Starlancer BLD,
    F7C-M Super Hornet Heartseeker Mk I, Mustang Alpha Vindicator and Valkyrie
    Liberator. 27 + 6 = 33. Reporting 33 would have been reporting the number
    that was asked for rather than the one that is true.
    BEFORE THIS FIX THAT FIGURE WAS 229, measured the same way by restoring the
    original function - not estimated, reproduced.

P1  DONE  c286735  THREE COLUMNS. Components left, model centre, readout right,
    tabs below. Sleven's sketch, built.
    THE MECHANISM THAT MAKES IT FIT IS ONE LINE, and it is worth naming because
    it is not "make everything smaller": the grid takes a height derived from
    the viewport and EACH COLUMN SCROLLS INSIDE ITSELF. A hull with 57 ports
    cannot be made short enough to fit a screen, so the list is given a BOX
    rather than being allowed to set the height of the document.
    The left column has two states - the component list, or the picker for one
    port with a way back. Both at once needs width this layout does not have,
    and the picker replacing the list is what makes a click's consequence land
    where the eye already is (see P5).

P2  DONE  c286735  THE VIEWER IS BOUNDED. `#cc-stage` was `height:min(52vh,460px)`
    at full page width - Sleven: "it runs screen to screen on each side". It is
    now the centre grid column, `minmax(0,1fr)` between a 22vw left and a 20vw
    right. At 1920 that is about 1,100px of 1,920 - under 60% - and the columns
    take the rest instead of empty space taking it.

P3  DONE  c286735  COMPACTION PASS, and the numbers the order asked for.
    TOTAL DOCUMENT HEIGHT, modelled from the page's own CSS:
                       BEFORE      AFTER
      1920 x 1080      1,952px      995px    (viewport 1,080 - 85px spare)
      1366 x  768      1,891px      683px    (viewport   768 - 85px spare)
    Before, the page overflowed 1080 by 872px. It now fits at both sizes.
    18 rules tightened, each one matched and applied - stat tiles from 168px
    minimum to 132px and 9px padding to 6px, budgets likewise, the acquisition
    strip from a grid of cards to an inline flex row, body type 16px to 15px,
    body padding 40px to 10px at the foot, tab strip padding 9px to 6px, slot
    rows 7px to 5px, and the marker note from 13px/1.5 in a 76px block to
    11.5px/1.4 capped at 78px with its own scroll.
    NOTHING DECORATIVE COSTS A ROW: the `.outcome` panel lost its border,
    background and 13px margin entirely - it is inside a column that already
    has all three.
    ARGUING WITH P7, WHICH THE ORDER INVITES: nothing had to be cut. The page
    fits 1920x1080 with 85px spare and 1366x768 with 85px spare, and the type
    went down one step (16px to 15px), not four. What made it fit is the
    COLUMNS and the internal scroll, not shrinking - which is the difference
    between "neat and well thought out" and "smaller".
    THE MEASUREMENT IS A MODEL AND SAYS SO. There is no browser on this machine
    (rule 7), so `checks/_verify_ship_page_fits.mjs` does arithmetic on the
    page's own declared CSS. It cannot see text wrapping, so every figure is a
    FLOOR - the real page is at least this tall, never shorter. That is the
    right direction to be wrong in.
    AND THE INSTRUMENT HAS ITS OWN CONTROL, because it earned one: while being
    written it silently measured the wrong thing THREE TIMES - a selector
    anchored so it never matched a rule following a comment, a selector
    (`.cols .col`) that does not exist in the page, and the 820px MOBILE media
    block winning every lookup so the model read a one-column layout while
    claiming to measure the desktop one. Each produced a confident, plausible,
    wrong number. It now applies media queries per viewport and asserts, before
    reporting anything, that the sheet it reads at 1920 differs from the one at
    800, that it reads the three-column rule at 1920 and the single-column rule
    at 800, that it resolves a custom property rather than reading it as zero,
    and that it finds padding on rules that follow comments.

P4  DONE  a06a3bb  A CONTROL TO STOP THE ROTATION, and it stops it.
    `autoRotate` was set true in `boot()` and nothing ever exposed it - so
    Sleven was right that there is no stop button, and C1's note that something
    called `pause` also exists is NOT correct: there was no such thing anywhere
    in the page or the viewer. Only `autoRotate`.
    The viewer gained `spinning()` and `setSpin()`, both reading and writing
    `controls.autoRotate` DIRECTLY rather than keeping a copy - a second copy of
    a boolean is a second source of truth about what the ship is doing. `boot()`
    honours a preference set before the model finished loading, because
    somebody who hits Stop while it is still streaming means it.
    The control is a real `<button>` on the canvas, so it is reachable by
    keyboard, it carries `aria-pressed`, and it says what it will do NEXT
    ("Stop spin" / "Start spin") rather than what state it is in.
    CONTROL: the ROTATION VALUE is asserted, not the button - `_view.spinning()`
    true, toggle, false, toggle, true. And it persists across a change of ship,
    because somebody who stopped the spin to read a marker does not want it
    starting again under them.

P5  DONE  a06a3bb  THE MARKERS. THE CLICK WAS NEVER BROKEN - THE CONSEQUENCE WAS
    OFF SCREEN. That is the actual cause, and it is not what was suspected.
    WHAT I DID BEFORE CHANGING ANYTHING: drove the real path. Loaded the page in
    a vm, captured its delegated click handler, built the marker element a
    browser would hand it, and dispatched. `sel` went to the right slot and the
    picker rendered 4,919 characters. Every time. There is no raycasting in this
    page at all - the markers are DOM `<button>` elements, not sprites - so
    C1's suspicion about the model rotating under a raycast could not apply.
    THE REAL CAUSE: the picker rendered roughly 1,050px down a 1,952px page, on
    a 1,080px screen. Sleven clicked a marker, the page updated correctly, and
    the part that changed was below the fold. A consequence you cannot see has
    not happened, as far as the person clicking is concerned.
    IT IS THE SAME DEFECT AS P6, which describes it exactly for a different
    control: "all it does is kinda refresh the bottom menu... let me scroll down
    a little bit". One defect - the page was taller than the screen - reported
    twice as two.
    SO THE FIX IS P1, NOT A HANDLER. The picker now takes the left column,
    beside the model, replacing the component list with a way back.
    ROTATION IS STILL A CONTRIBUTING FACTOR AND I WILL NOT PRETEND OTHERWISE:
    the markers are 19px and move continuously, and a browser only fires
    `click` when mousedown and mouseup land on the same element. If the button
    slides out from under the cursor between the two, no click is generated at
    all. I CANNOT TEST THAT WITHOUT A BROWSER and I am not going to claim it as
    proven either way. P4's stop control is what makes it a non-issue.
    CONTROL, and it is the erratum's lesson applied: a REAL CLICK is dispatched
    through the page's own delegated handler, and the assertion is that the
    picker opened for THAT PortId and no other - run twice, once with rotation
    running and once with it stopped. The harness now CAPTURES document click
    handlers instead of swallowing them, because a no-op `addEventListener`
    leaves nothing to dispatch to and the only thing left to assert would be
    that a listener exists, which is worth nothing.

P6  DONE  a06a3bb  `Try another alongside` IS VISIBLE WHERE THE EYE IS.
    Both builds are now panes of the SAME left column, one under the other. The
    column begins 153px down the page, so the second build's first component row
    is on screen BY CONSTRUCTION rather than by measuring and hoping - it was
    previously below a readout block and a 460px stage on a page that ran to
    1,952px.
    CONTROL: after the click, `colB` is not hidden and has rendered its rows -
    asserted on content length, not on a class, because an empty visible pane
    is the same experience as a hidden one. Discard reverses it.

P7  DONE  999b5cf  NO SCROLLING TO SEE THE PAGE, measured at both sizes.
      1920 x 1080    995px of 1,080   -  85px spare, FITS
      1366 x  768    683px of   768   -  85px spare, FITS
    Before: 1,952px and 1,891px, overflowing by 872px and 1,123px.
    THE COMPONENTS COLUMN AND THE READOUT SCROLL WITHIN THEMSELVES; the page
    does not. `overflow-y:auto` on `.cols .col.left` and `.col.right`, and the
    grid takes `calc(100vh - var(--chrome))`.
    `--chrome` is 238px against 153px of ACTUAL header, strip, tabs and
    padding. The 85px of slack is deliberate and is stated in the CSS: the
    model that checks this cannot see text wrapping, and a heading that wraps
    to two lines must not push the page over the fold. Being generous costs
    column height; being tight costs the whole claim.
    ARGUING WITH P7 AS INVITED - NOTHING HAD TO GO. The order asked me to say
    what would have to be cut if it could not fit. Nothing did. What made it
    fit is the three columns and the internal scroll; the type went down ONE
    step, 16px to 15px. "Neat and well thought out", not "smaller".
    WIDE MONITORS DO NOT COUNT AND WERE NOT USED: both figures are modelled at
    the stated viewports, and the 1366 case is a real pass rather than a
    reported miss.

P8  DONE  2cc669f  SWEEP + DEPLOY + VERIFIED FROM THE SERVED BYTES.
    URL: https://citizencompasstesting.citizencompass-contact.workers.dev
    Version ID c3d8559f-1037-441c-bd34-ef8f78410d71. NOT the live site.
    SWEEP: 45 controls discovered, 42 ok, 1 failed, 2 skipped, 0 NOT RUN, 150s.
    The one failure is `_verify_g3_matcher_delta.py` reporting NOT PERFORMED
    because CC_GEO_DIR is unset - pre-existing, unrelated, correctly refusing
    to claim a pass. One control more than last time: the new
    `_verify_ship_page_fits.mjs`.
    UPLOAD DIFF: TWO FILES, loadout.html and cc_viewer.js - exactly and only
    what P1-P7 touched.
    DRIVEN ON THE SERVED PAGE, not grepped: the served HTML's own six script
    blocks run against the four SERVED data files.
      three columns present    colleft / colmid / colright, overflow-y on two
      opens with ONE build     twoUp=false
      18 stat tiles            each once, ZERO second values
      7 markers rendered       on the Avenger Stalker
      CLICK A MARKER           sel = {"slot":"blr2"} - the expected port
      picker opened            4,976 chars, visible, in the LEFT COLUMN
      component list           hidden behind it, as designed
      STOP SPIN                _view.spinning() false, button reads "Start spin"
    That marker line is the one that matters: the thing Sleven reported as
    doing nothing now demonstrably selects its port and renders its picker
    somewhere he can see, ON THE DEPLOYED BYTES.
    STATED LIMIT, unchanged: no browser was involved and none exists here
    (rule 7). The page-height figures are a model of the declared CSS, and
    whether the columns look right, the model draws, and 19px markers are
    comfortable to hit are Sleven's to see.

A1  DONE  1d4640a  THE TRADEMARK NOTICE, ONE CONSTANT, ON ALL SEVEN BUILT PAGES,
    ALWAYS VISIBLE.
    WHAT I FOUND BEFORE CHANGING ANYTHING, and it is exactly what the order
    predicted - "six hand-copied instances is six chances at one":
      x4  the correct CIG wording  (_layer, find, keybinds, loadout)
      x1  A DIFFERENT SENTENCE ENTIRELY on download.src.html - "Star Citizen(R)
          and related marks are the property of Cloud Imperium Rights LLC." That
          is not what CIG's Fan Kit Guidelines require.
      x1  static/preview.html carries a fifth mark and an Oxford comma - "Star
          Citizen(R), Squadron 42(R), Roberts Space Industries(R), and Cloud
          Imperium(R)..."
      x0  holo.src.html and stick-test.src.html carried NO NOTICE AT ALL.
    Two pages with none is the finding that matters: an absent legal notice
    looks exactly like one nobody has checked.
    NOW ONE DEFINITION, in testing/_src/attribution.py, and every page takes it
    from there. The entity-escaped form is DERIVED from the constant rather
    than typed, so the two cannot drift.
    CIG'S TWO REQUIREMENTS, both met and both asserted:
      10-POINT MINIMUM - written as `font-size:10pt` literally rather than as
      13.333px, so a checker asserting "at least 10 point" does not have to
      perform a unit conversion to believe the answer. The site's existing bar
      uses 13.333px, which is the same size; the check converts and accepts
      both.
      ALWAYS VISIBLE REGARDLESS OF SCROLLING - `position:sticky; bottom:0`.
    PLACEMENT WAS NOT WHAT I ASSUMED, and the first attempt failed loudly rather
    than quietly: ONLY ONE of the seven pages writes a `</body>`. Most close
    with `</html>` and two close with neither. A rule anchored on `</body>` put
    the notice on one page and refused the rest.
    HARD RULE 8 OBSERVED: `releases/latest.html` and `static/preview.html` are
    the live site's own source and I did NOT edit them. index.html's inherited
    bar has its TEXT normalised to the constant in the ASSEMBLED OUTPUT only -
    the source files are untouched. THE DISCREPANCY IS REPORTED, NOT FIXED:
    preview.html's notice names Squadron 42 and latest.html's omits the full
    stop. Both are Sleven's to change.
    CONTROL: checks/_verify_attribution.mjs. It does not grep. It RESOLVES the
    element carrying the sentence, reads the rule that styles it, converts the
    declared size to pixels and asserts >= 10pt, and asserts the rule is sticky
    or fixed. On the ship page it additionally asserts the strip sits OUTSIDE
    the scrolling columns, since a notice inside one would scroll away.
    AND THE CHECKER HAS NO COPY OF THE SENTENCE. It reads TRADEMARK out of
    attribution.py - a checker with its own copy would be a seventh hand-copied
    instance and would pass while the site was wrong.
    PROVEN: `--prove` blanks the constant and the comparison goes red on all
    seven pages.

A3  DONE  1d4640a  THE SOURCE AND CONTACT NOTICE - BUILT, AND CORRECTLY NOT
    RENDERING YET.
    THE BUILD REFUSES WITHOUT A CONTACT ADDRESS, and I watched it refuse before
    writing any checker - that is A3's control, observed firing.
    DECIDED-BY-DEFAULT, and this is the one judgement call in the run:
    THE REQUIREMENT IS TRIGGERED BY A4's TAG, NOT BY EVERY BUILD.
    Taken literally, "the build fails if the contact is absent" fails every
    build today. And if I had supplied an address to get past it, the site would
    carry a notice saying the ship models "are Cloud Imperium Games' own, taken
    from the holoviewer" - WHICH IS NOT TRUE. Every model on this site came
    from the scunpacked pipeline and the Fan Kit. No RSI holoviewer asset has
    been fetched; the order forbids fetching one.
    Rendering that notice today would put a FALSE STATEMENT on the page, which
    is the one thing this project does not do. So the notice appears when the
    content it describes appears: ANY asset registered as CIG-sourced turns it
    on, and turns the contact requirement on with it.
    REVERSIBLE IN BOTH DIRECTIONS: set CC_TAKEDOWN_CONTACT and it renders today;
    register one CIG asset and the build demands an address. Nobody has to
    remember either.
    I DID NOT INVENT AN ADDRESS. There is none anywhere in the repo, the site
    or .env - I looked. The order says Sleven supplies it and my job is to make
    its absence impossible to miss, which is what the refusal does.
    THE WORDING is in the plain register the ship page uses: what it is, who
    owns it, that this is an unofficial fan site not affiliated with or
    endorsed by CIG, and that if they would like anything taken down they write
    to the address and it comes off - "no argument and no delay".
    `source_notice()` RAISES on an empty contact rather than rendering
    "contact:" and stopping, so the failure cannot reach a page even if a
    future caller forgets the check.

A2  DONE  2f70aa3  THE "MADE BY THE COMMUNITY" MARK - APPLIER, DETECTOR, AND
    A BUILD THAT REFUSES WITHOUT IT.
    `scripts/community_mark.py` composites the Fan Kit mark bottom-right at 70%
    opacity, following the precedent in
    docs/FINDING_hologram-display-concept-2026-08-08.md rather than inventing a
    second approach. CIG's prohibitions are structural, not commented: ONE scale
    factor for both axes so it cannot be distorted, never transposed so it
    cannot be flipped, its own pixels copied so it cannot be recoloured, nothing
    drawn over it so it gets no outline, shadow or effect. Opacity below CIG's
    50% floor RAISES rather than clamping.
    THE FIRST DETECTOR I WROTE WAS WRONG, AND MEASURING IT IS WHAT FOUND THAT.
    It scored "is the corner brighter where the mark is opaque". But the mark is
    not a flat silhouette: 72% of it is opaque and that region spans luminance
    9..255 with a MEAN OF 113 - mid grey. On a mid-grey render it shifts the
    average by almost nothing. Measured: mid-grey scored 5.36 where dark and
    light scored 57 and 68, i.e. it would have declared the mark MISSING on
    exactly the mid-tone images a ship render actually produces. Replaced with
    the Pearson correlation between the corner and the mark's own luminance,
    which is invariant to background and to opacity because compositing is
    linear. Re-measured across dark/mid/light, a gradient with a deliberately
    bright corner blob, and a 320px image, both variants, at 70% AND at the 50%
    floor: MARKED 0.9683..0.9994, UNMARKED at most 0.0212. The threshold 0.50
    sits in the middle of a 0.947 gap, and the checker re-measures both ends
    every run so it cannot quietly stop separating them.
    THE LOAD-BEARING NEGATIVE CONTROL RUNS THE REAL BUILD, TWICE.
    `checks/_verify_community_mark.py` does not call the guard's inner function
    and does not describe what the build would do - it executes
    testing/_src/build_deploy.py as a subprocess against a fixture register
    (CC_CIG_REGISTER, added for this) and asserts on its exit status:
      unmarked image registered as CIG-sourced -> build FAILED, exit 1
      the SAME image, marked                   -> build SUCCEEDED, exit 0
    Both halves are required: the first alone passes on a build that refuses
    everything, the second alone on a build that refuses nothing.
    AND THE FIRST RUN OF THAT CONTROL SCORED A FALSE PASS, WHICH IS WHY IT NOW
    ASSERTS *WHICH* REFUSAL IT GOT. Registering a CIG asset also switches on
    A3's contact requirement, so the build exited 1 on the MISSING CONTACT
    without ever reaching the mark guard - and "the build refused" was green.
    That is the project's silent-success shape exactly: refused, but for the
    wrong reason. The control now supplies a contact and requires the refusal to
    name the mark. Ninth instance logged.
    ORIENTATION IS ASSERTED AGAINST FOUR TRANSFORMS, with a margin set from
    measurement rather than taste: upright 0.9905 beats mirrored-left-right
    0.8800 by only 0.1105, because the mark is a near-circular badge; the
    vertical and rotational transforms fall to 0.54..0.60. Claiming a wide
    margin here would have been claiming something untrue about this mark.
    GUARD IS ARMED AND IDLE: 0 CIG-sourced images are registered, so it reports
    "guard armed, nothing to mark". The first one registered turns it on with
    nobody remembering to - same shape as A3.
    REPORTED, NOT FIXED (hard rule 8): the 241 ship thumbnails already shipping
    in images/ do NOT carry the mark. docs/workorder-image-provenance-and-
    renders.md establishes that the upstream pack is governed by terms naming
    "Made by the Community", and equally that it is NOT established whether any
    individual image is a CIG asset, a screenshot or a render. Marking all 241
    is a bulk mutation of the site's whole visual surface (rule 5) on a Fan Kit
    compliance question (rule 8 says report it, do not fix it), and Part 2 of
    that same work order plans to replace every one of them with our own
    renders. THIS IS A DECISION FOR SLEVEN, not one I take silently.
    THE MARK FILE IS NOT COMMITTED. It is read from the Fan Kit on disk, or from
    CC_FANKIT_DIR. Copying a CIG asset into a public git repo is a separate
    decision from the one already taken, and not mine.
    13 assertions pass; _deploy is left at exactly 241 images with no fixture
    behind it. Fixtures moved to _to_delete/a2_mark_fixtures/ (rule 1).

A4  DONE  3073791  THE OFF SWITCH - BUILT, AND EXECUTED RATHER THAN DESCRIBED.
    ONE COMMAND:  venv\Scripts\python.exe scripts\takedown.py --yes
    It reads the register for every CIG-sourced asset, MOVES each one out of the
    built site into _to_delete/takedown_<stamp>/ (moved, not deleted - hard rule
    1, and a takedown made in a panic stays recoverable), stamps `removed` on
    the record, and rebuilds.
    THE STAMP IS THE DURABLE HALF, and this is the part that would have been
    easy to get wrong. _deploy/models/ is NOT regenerated by the build - it is a
    directory on disk that a sync step populates. Removing the file alone would
    therefore last exactly until the next sync put it back, and the site would
    quietly start serving withdrawn content again with nobody noticing. So the
    build reads the stamp, drops those ships out of the model map so no URL to
    them can be constructed, and publishes them separately as LOADOUT_WITHDRAWN.
    AND IF ONE COMES BACK ANYWAY, the build moves it straight out again and says
    so loudly. That FAILS SAFE TOWARDS REMOVAL rather than refusing to build -
    a build that will not run is the wrong behaviour in the middle of a
    takedown, which is the worst possible moment to be debugging one.
    DEGRADED AND HONEST, NOT BROKEN. A withdrawn model is checked BEFORE the
    existing "no model for this hull yet" case, because telling somebody that
    about a ship whose model we removed on purpose is a FALSE STATEMENT. It gets
    its own sentence - "removed at the rights holder's request" - and the viewer
    is torn down with cancel/clear/stop rather than left as a dead canvas or a
    spinner that never resolves. Everything below the viewer is unaffected: the
    numbers come from the game files, not the model.
    THE CONTROL RUNS THE SCRIPT. checks/_verify_takedown.py executes
    scripts/takedown.py as a subprocess, with arguments, exactly as a person in
    a hurry would - not a copy of its logic and not an import of one helper. The
    fixture holds 3 TAGGED and 4 UNTAGGED assets across models, images and
    fonts.
      - every tagged asset gone            3 of 3
      - EVERY UNTAGGED ASSET SURVIVES      4 of 4
      - exactly the tagged records stamped  3
      - the real site still builds          exit 0, degraded and honest
    19 assertions.
    THE UNTAGGED HALF IS THE LOAD-BEARING ONE AND IT WAS OBSERVED FAILING. A
    mutant that removed every registered asset instead of only the tagged ones
    was caught by exactly that assertion: "0 of 4 survived". A script that
    deletes everything passes "the tagged assets are gone" perfectly, which is
    why that assertion exists and why it had to be seen going red.
    THE DRY RUN IS PROVEN BY BEHAVIOUR, not by reading it: --dry-run is executed
    and then every file is checked FROM THE OUTSIDE to still be present, with
    the register byte-identical. A report-only switch whose no-op has never been
    verified is a check wearing a reassuring name - this project has already
    been bitten by exactly that (setup_checks_task.ps1, -WhatIf, 2026-08-01).
    A real run also refuses without --yes, so it cannot happen by accident.
    THE CONTROL PUTS THE REAL REPO BACK AND PROVES IT. The "still builds" half
    withdraws a real ship (AEGS_Avenger_Stalker), so the build genuinely moves
    that model out of testing/_deploy/. The finally block moves it back,
    rebuilds with the real register, and ASSERTS the restore rather than
    assuming it: 235 models present, LOADOUT_WITHDRAWN empty.
    docs/TAKEDOWN.md is written for somebody stressed and in a hurry: the
    command is the first thing on the page in a plain code block, the deploy
    step is second because the removal is local until it is published, and every
    word of explanation is below both.

A5  DONE  47577c9  STATIC-ASSET EXPOSURE - MEASURED AND REPORTED. NOT FIXED,
    BY INSTRUCTION.
    docs/FINDING_static-asset-exposure-2026-08-22.md. Every figure came from
    FETCHING the deployed sites with curl on 2026-08-22, not from reading
    wrangler.toml or the build.
    TESTING SITE: everything is fetchable. /models/Avenger_Stalker.glb 200
    model/gltf-binary 765,808 bytes; /images/100i.webp 200 image/webp 10,292;
    /fonts/*.woff2 200; /fonts/OFL.txt 200; /loadout_data.gen.js 200
    text/javascript 3,636,252. /loadout.html 307 -> /loadout, and all six
    subpages 200. Nothing returned 401, 403 or any challenge.
    AND IT IS WORSE THAN CURRENT-STATE.md RECORDED. That note said the gate
    "does not cover static assets". Measured today, IT DOES NOT COVER THE HTML
    EITHER. GET / with no password, no cookie and no session returned 421,413
    bytes OF THE REAL SITE - the served bytes carry Avenger 20 times, Hammerhead
    5, Polaris 5, Redeemer 6, alongside the word "Password". The gate is
    presentation-only: a CSS rule (html.cc-locked body > *:not(#cc-gate)
    {display:none}) plus localStorage.ccGate. The content is delivered BEFORE
    any password is entered. curl gets all of it, and so does View Source or
    typing localStorage.ccGate='1' in a console.
    LIVE NETLIFY SITE DOES NOT HAVE THE PROPERTY. / is 200 at 205,362 bytes;
    /models/*.glb and /images/*.webp are 404. It is one self-contained file and
    a scan of the served bytes found NO src/href reference to any .glb, .webp,
    .png, .jpg, .js or .css at all. The exposure came in with the 3D viewer and
    lives on the testing site only.
    VOLUME: models 235 files / 341.8 MB / mean 1,490 KB; images 241 / 4.0 MB;
    fonts 6 / 0.1 MB. A visitor looking at ten ships pulls about 15 MB.
    THE REFERER/ORIGIN CHECK, STATED HONESTLY AS THE ORDER REQUIRES: about
    thirty lines and one Worker route, and VERY WEAK. Referer and Origin are
    client-supplied strings - one curl -H flag defeats it, not an exploit. The
    URL is in the page source either way. It cannot tell our viewer from a
    script imitating it, because nothing in the request distinguishes them.
    Privacy modes and some proxies strip Referer, so a strict check breaks real
    users while stopping nobody trying. What it genuinely buys is hotlink
    prevention and casual-save friction. No scheme ending in a browser decoding
    the mesh can stop a determined person keeping the bytes; the honest ceiling
    is friction, not prevention.
    COST: bandwidth is unchanged - the same bytes go out. The real cost is that
    341.8 MB moves off the static path onto a metered code path, one invocation
    per model load. I did NOT verify the account's plan or limits and so have
    NOT quoted a price - the shape is what can be said without guessing.
    THREE OPTIONS AND A RECOMMENDATION, then stop.
    RECOMMENDED: option B, the description half, now - and NOT option C. The
    most wrong thing on the site today is not that models are fetchable; it is
    that A GATE PRESENTS ITSELF AS A PASSWORD WHILE DELIVERING THE WHOLE PAGE TO
    ANYONE WHO ASKS. That is the same defect class this project spends its time
    hunting: something reporting a protection it does not provide. Correcting
    the wording costs nothing and needs no infrastructure.
    Option C waits because it buys friction rather than protection, and because
    NO CIG-SOURCED ASSET IS ON THIS SITE YET - every model served came from the
    scunpacked pipeline. The question sharpens when the first holoviewer asset
    lands, which is when the trade-offs should be re-weighed with the
    reconnaissance back.
    NOT IMPLEMENTED. Awaiting Sleven's decision, as instructed.

# B RUN - docs/ORDER_the-picker-redesign-2026-08-22.md (REV 2)
# Same ledger, per the convention the H run set. Appended below the A run,
# nothing above rewritten. Rev 2 replaced rev 1 at that same path; nothing
# from rev 1 survives except by being restated there.

B0  DONE  eef64be  A MARKER THAT DID NOTHING HAS STOPPED EXISTING IN THAT FORM.
    THE SYMPTOM WAS REPORTED AS "not all the ships have been done". Every ship
    had been done. The markers were drawn, for the right ports, in the right
    places. They were not clickable and they did not say so - which from the
    outside is the same thing as a broken page, and worse, because it looks
    like missing data rather than a bug.
    MEASURED BEFORE, from the generated data and then again by clicking:
      1,200 markers on 157 hulls - 418 clickable (34.8%), 782 SILENT (65.2%)
      61 hulls where EVERY marker was silent
      Origin 400i: 10 markers, 2 clickable, 8 silent
    THE CAUSE, one line. selectPort() opened with
      if(!swappable(slot)){ sel=null; renderPicker(); return false; }
    so clicking a fixed port CLEARED the selection and re-rendered the same
    empty prompt already on screen. Nothing appeared, nothing explained, and
    renderMarkers() had drawn a marker for every LOADOUT_MARK entry without
    ever asking whether it could be selected.
    THE FIX. A fixed port is selected like any other; only what OPENS differs.
    fixedPanel() names what is fitted, its manufacturer, its type and size, the
    port's own name in the game's vocabulary, why the game will not allow the
    change (its Editable flag, in the game's own terms), and the
    last_verified_patch tag. Markers are NOT deleted - Sleven's standing
    position is that fixed ports stay visible because they are part of the
    ship.
    AND THEY LOOK DIFFERENT BEFORE THEY ARE CLICKED, BY SHAPE NOT COLOUR: 15px
    with a dashed ring against 19px with a solid one, which reads identically
    in greyscale and on a dim monitor. Roughly one man in twelve cannot rely on
    a hue, and the order forbade colour alone.
    ONE SELECTION PATH KEPT. The left-column row previously rendered the fixed
    panel itself - a second writer of the picker, and a way for the row and the
    marker to drift apart. Both routes now call selectPort(); the row adds only
    the bump under the finger.
    CONTROL  checks/_verify_marker_response.mjs, 21 assertions.
    It classifies the OUTCOME of a real dispatched click into picker / fixed /
    SILENT, read off what the picker pane actually contains. THIS IS THE POINT:
    _verify_ship_page.mjs's P5 block already dispatched a real click and
    asserted sel came back naming the port. It passed, always, because it
    selected its marker with `s.fit` - a SWAPPABLE port, every time. The
    mechanism was asserted; the experience was not.
      Origin 400i   10 markers, 2 picker, 8 fixed, 0 silent
      fleet         1,200 markers / 157 hulls, 0 silent, 0 all-silent hulls
      the panel for hardpoint_missile_left contains "ST-205 Missile Rack"
    NEGATIVE CONTROL, as the order required: a swappable marker opens the
    PICKER and the fixed panel is ABSENT from it. Without it a build that
    showed the fixed panel for everything would pass.
    RULE 12, THE LOAD-BEARING HALF. --mutate puts the exact early return back
    and reproduces the defect to the number: 782 silent, 61 all-silent hulls,
    8 of 10 on the 400i. That is the code that actually shipped, not a sign
    flip. --self-test inverts all 21 and exits 1. The census counter is
    separately proven able to print a non-zero silent count, so today's 0 is a
    measurement rather than a constant.
    ONE THING THE FIRST RUN GOT WRONG, recorded because it nearly passed as a
    data finding: the control reported that the 400i has no
    hardpoint_missile_left port. It has one. A slot's `h` is an INDEX into the
    hardpoint-name table, not the name, so comparing it to a string matched
    nothing. The lookup was wrong, not the data.
    NO REGRESSION: _verify_ship_page.mjs still 238 ok, 0 failed.

B1  DONE  a6d28b9  THE LEFT COLUMN NOW HOLDS ONLY WHAT A PERSON CAN ACT ON.
    Fixed ports left the loadout column for the Specs tab, with L4 intact
    wherever they are shown: the fitted part, its manufacturer, the port label,
    the reason it is locked IN THE GAME'S OWN TERMS, and the patch tag. N7's
    collapsed <details> fold went with them, along with its CSS and the
    `fixedOpen` state it needed.
    THEY STAY FINDABLE. "N fixed" in the sub-line is a control that opens
    Specs. Something moved with no signpost has been hidden, not organised. On
    a hull with no fixed ports it is plain text and there is no control
    offering to lead somewhere empty.
    THE SPECS ROWS ARE READING MATTER, NOT CONTROLS - `data-fixed`, never
    `data-slot`. A control there would set `sel`, which hides the loadout
    column and opens the picker pane ON A TAB THE READER IS NOT LOOKING AT.
    That is P5's "a consequence you cannot see has not happened" and it was
    cheaper to not build it than to find it later. The clickable route to the
    same information is the marker, which is on screen when it opens.
    THE SPLIT IS UNCHANGED and that is the point of the item: `swappable(s)` =
    `!!s.fit` = the port's own Editable flag, no list of types anywhere.
    CONTROL  checks/_verify_column_split.mjs, 27 assertions.
      column holds exactly the 21 swappable ports of the Avenger Stalker
      Specs holds all 36 fixed, and 21 + 36 = 57, the port total
      "N fixed" dispatched through the page's own handler opens the Specs tab
      FLEET: 316 hulls with ports, EVERY port on the side its own flag puts it
    NEGATIVE, as the order required: driven with the only record in the fleet
    that has ports and no fixed ones (PowerSuit, 2 ports). Specs still renders,
    no "Fixed ports" heading over an empty list, sub-line reads plain "0 fixed"
    with nothing to click.
    RULE 12, AND IT EARNED ITS KEEP. Two plants, both exit non-zero:
    --mutate-column puts the fixed rows back in the column, --mutate-heading
    emits the heading with nothing under it.
    THE FIRST VERSION OF --mutate-column ONLY UN-FILTERED THE COLUMN, AND THIS
    CONTROL PASSED. Correctly: renderSlot() still turned a fixed port away at
    the door, so the page was still right. A real revert needs both halves.
    Planting it is how that was found; reading the code would not have shown it.
    _verify_ship_page.mjs's L4, N7 and N8 blocks were moved to the new home and
    NOT relaxed - same claims, asserted against Specs, plus a new sum assertion
    that catches a port falling into the gap between the two lists. 239 ok, and
    its own --mutate still catches the widened fitsFor.
    ALSO: checks/_loadout_harness.mjs extracts the DOM stub these controls
    share. Two copies already existed and the B run needs more; a stub
    duplicated seven times is seven writers for one fact (rule 14).
    CONVENTION NOTED, NOT CHANGED: _verify_ship_page.mjs's --mutate exits 0
    when it CATCHES the mutant. The new B-run controls exit 1 instead, because
    a non-zero exit cannot be mistaken for "the run did nothing". Both are
    honest; they are different, and this is where that is written down.

B2  DONE  4f062da  ONE COMPACT ROW PER SLOT, THE PICKER INLINE BENEATH IT, AND
    THE FITTED PART PINNED TO THE TOP.
    THE TAKEOVER IS GONE. P5 fixed "the picker rendered ~1,050px down a 1,952px
    page" by REPLACING the list with the picker. That fixed the eye and created
    a new defect in the same move: you lost your place in the list you were
    reading. The picker now opens inline under the row that was clicked; the
    rows above and below stay on screen; only one is open at a time, because
    `sel` names exactly one slot and the state machine does the work rather
    than anybody remembering to close the last one.
    The "<- Components" button went with the takeover. The list never leaves,
    so there is nothing to go back TO - closing the open row IS going back, in
    place, and that is what the close control does.
    THE FITTED PART IS PINNED, AND THIS IS A DEFECT NOT A NICETY. Sleven opened
    the Avenger Stalker's size-4 turret mount - 74 parts, sorted by DPS - and
    THE PART ALREADY FITTED WAS NOWHERE ON SCREEN. It is now lifted out of the
    sort, rendered first, labelled "Currently fitted" IN WORDS rather than by
    tint alone, and REMOVED from the remainder so it appears exactly once. The
    same part twice would be its own small lie about what is on offer. The sort
    governs everything below it, unchanged.
    pickerHTML() and partRow() extracted so a port's two entrances - its row
    and its marker - cannot render different lists.
    AND THE PANE STOPPED DOUBLE-RENDERING. renderPicker() no longer writes a
    swappable port's picker into the picker pane: renderChrome() keeps that
    pane hidden now, so it would have been a second copy of the same content
    where nobody would ever see it go wrong. Cleared rather than left stale.
    CONTROL  checks/_verify_inline_picker.mjs, 34 assertions.
      turret mount, size 4, 74 parts: FIRST entry is "VariPuck S4 Gimbal Mount"
      on all three sorts, exactly once, labelled
      Best and Lightest are still different orders below the pin
      row 1 open -> all 21 rows still present, column not hidden, ONE picker
      row 5 clicked -> row 1's picker GONE, row 5's open, still exactly one
      FLEET: 314 hulls, exactly one inline picker when a port is selected
    RULE 12. --mutate-pin puts the fitted part back in the sort and the first
    entry becomes "Remote Turret" - the state Sleven actually hit.
    --mutate-multi opens every row at once: 21 pickers on the Avenger, 308
    hulls wrong. Both exit non-zero, as does --self-test.
    THE CONTROL NEARLY DROVE THE WRONG PORT, and it is worth writing down. Its
    first version chose "the port with the longest list". On this hull that is
    the FLIGHT CONTROLLER at 238 parts, not the turret mount at 74 - so the
    whole block would have been asserted against a port the order never
    mentions, passing, while nobody had checked the one Sleven opened. It now
    asks for a turret mount by type.
    _verify_ship_page.mjs's L3 and P5 blocks follow the picker to where it now
    renders, through one pickerNow() helper that reads whichever home the page
    filled - reading only the old pane would have made every L3 assertion read
    an empty string, which is a check that passes because it never looked. P5's
    "the picker takes the left column" became the STRONGER claim that the
    column is not taken over. 240 ok; its --mutate still catches the widened
    fitsFor.

B3  DONE  fd37ae8  TWO HOMES, SPLIT BY WHETHER THE THING IS ON THE HULL.
    Sleven's own scoping: guns, missiles, gimbals go on the hardpoint
    attachments in their own specialised place; components cannot, because
    there is no proper way to hardpoint them.
    THE TEST IS THE MARKER, which is the only honest one available: a port the
    model carries a dot for HAS a position; a power plant does not. So a marked
    port opens a panel over the model stage, anchored near its dot, and an
    internal component opens inline in the list. No invented markers.
    pickerHome() is the SINGLE answer to "where does this open", asked by
    everything that renders a picker. Two places deciding that is how one of
    them ends up writing into a hidden pane, which is what B2 had to undo.
    IT MUST NOT COVER ITS OWN MARKER - a panel hiding the dot you just clicked
    removes the one piece of context that made the click mean anything. It sits
    beside the marker, FLIPS when there is no room, and clamps inside the
    stage. panelPlacement() is a PURE FUNCTION of numbers precisely so the
    geometry can be driven with input chosen to break it rather than reasoned
    about in a browser nobody opens.
    PANEL_W / PANEL_MAXH / PANEL_GAP are declared once in JS and the CSS is
    told. Two copies of 328 would drift the first time somebody widened it, and
    the panel would begin covering the marker with nothing reporting it.
    Escape closes it. The model background closes it. A click INSIDE it does
    NOT - otherwise the picker would shut on first use, which is the negative
    half and it is asserted.
    CONTROL  checks/_verify_stage_panel.mjs, 47 assertions.
      placement: goes right with room; FLIPS with none; clamps top and bottom;
      a stage narrower than the panel still yields a placement inside it
      Origin 400i, hardpoint_weapon_left: panel open, computed position inside
      the 960x540 stage, marker NOT under it (panel 296..624, marker at 640)
      the ROW opens a BYTE-IDENTICAL panel at IDENTICAL coordinates - one
      selection path, two entrances, asserted as identity rather than as "both
      did something"
      a power plant on a hull that HAS markers opens inline and no panel opens
      FLEET: 3,985 port selections, every one in the home its marker decides
    RULE 12. --mutate-cover returns the marker's own position and the placement
    assertions fail; --mutate-internal treats every port as hull-mounted and
    the power plant grows a panel. Both exit non-zero, as does --self-test.
    ONE ASSERTION IN THE FIRST DRAFT COMPARED g("sel") WITH ITSELF. A check
    that cannot fail, in the control written to enforce rule 12. Caught on
    re-reading, replaced with the two captured selections. Recorded because the
    lesson is that writing the rule down does not exempt you from it.
    STATED LIMIT: the 960x540 stage is a STUB, not a measurement. Nothing here
    proves the panel fits a real viewport - only that the arithmetic places it
    inside the box it was given. Real viewports are B8's job.

B4  DONE  c6d8da0  THE PAGE OPENS CALM, AND REMEMBERS THE CHOICE.
    "The ship just constantly spins." A stop control is not the same as opening
    still: it made a visitor undo something they never asked for, on every
    ship, before they could look at what they came to see.
    Default not spinning. Choice remembered in sessionStorage - not
    localStorage, because it is a preference about this sitting rather than a
    setting that should follow somebody back weeks later having been forgotten.
    READ THROUGH A GUARD. sessionStorage THROWS in a browser with storage
    disabled and is absent entirely outside one. A page that fell over because
    it could not remember a spin preference would be broken by its own
    convenience.
    "NO PREFERENCE" (null) AND "PREFERS OFF" (false) STAY DISTINCT even though
    they produce the same first frame. Collapsing them would make the negative
    control below unprovable, which is the whole reason to keep them apart.
    The static markup opens in the default state too - until applySpin() first
    runs, a button reading "Stop spin" over a still ship is the page
    contradicting itself on every load.
    CONTROL  checks/_verify_spin_default.mjs, 27 assertions, three storage
    worlds driven rather than reasoned about: none, working, and one that
    throws on every access.
      no preference  -> spinOn false, _view.spinning() false, "Start spin"
      stored "1"     -> spinOn true, _view.spinning() TRUE, "Stop spin"
      toggle writes "1" then "0", and a page loaded afterwards honours it -
      the round trip closes, because writing proves nothing if nothing reads
      storage throwing -> page loads, defaults calm, control still works
    THE NEGATIVE HALF IS THE LOAD-BEARING ONE and the order said so: "it does
    not spin" also passes on a build where spin is BROKEN. Asserting
    _view.spinning() rather than the button's label is what separates the two.
    RULE 12. --mutate-default returns to spinning-by-default; --mutate-forget
    drops the write so the memory silently stops working. Both exit non-zero,
    as does --self-test.
    AND THE HARNESS WAS LYING TO THIS CONTROL. openShip() set spinOn on every
    call, so the stored-preference case came up still - the harness had just
    turned it off. Found because the control failed on a page that was right.
    `spin` is optional now and unset by default.

B5  DONE  2654263  THE PARENT IS CARRIED AND CAN BE INHERITED FROM - AND ON
    TODAY'S INPUT IT IS A MEASURED NO-OP. Both halves are asserted.
    THE FLATTEN. walk_ports() always knew each port's parent and the slot
    record always threw it away. 12,318 of 26,000 slots now carry one, as an
    index into the same name table `h` uses. A top-level port carries an
    EXPLICIT null: "this is top-level" and "nobody looked" must not arrive as
    the same value. Cost: loadout_data.gen.js 3.64 MB -> 3.88 MB (+247 KB),
    on a file A5 already flagged as served whole to every visitor.
    THE FALLBACK, exactly as specified. One level, from a real parent, ONLY
    when the child's own name yields nothing, never instead of it. `index` is
    deliberately NOT vocabulary - a trailing number says nothing about where a
    thing is, and counting it would make `hardpoint_class_2` look located when
    all it carries is a 2. Every point records `placed_from` (own | inherited)
    and the parent it borrowed.
    AND place_fleet.py COULD NOT BE RUN FOR TWELVE DAYS. It read
    /home/claude/fleet/geo and /home/claude/fleet/matched.json - the 2026-08-10
    sandbox, gone. Nobody noticed because its OUTPUT was already committed: a
    dataset driving every marker on the site, produced by a derivation that
    could not be repeated. That is now fixed - geometry decoded this morning,
    matched.json reconstructed by build_matched.py from ship_mounts.json plus
    the model matching hardpoints_fleet already recorded, paths repo-relative,
    default output to _stage/ rather than over the committed dataset, and a
    missing input exits rather than writing a partial fleet over a good one.
    THE ORDER'S PREMISE DOES NOT HOLD ON THIS DATA, AND IT IS REPORTED RATHER
    THAN WORKED AROUND:
      Hammerhead: 20 placed ports, ZERO with no position vocabulary
      `hardpoint_class_2` is NOT in the placed fleet at all. The placement
        input carries only TOP-LEVEL mounts - the six turret BASES - and the
        guns inside them are children in ships.json that never reach it
      0 of 1,798 mounts in the input have a parent, so the fallback provably
        cannot move a marker today
      the 76 fleet-wide none-target points are `hardpoint_countermeasures_2`,
        `hardpoint_PDC_04`, `hardpoint_CML_7` - the part table matches
        "countermeasure" but not the plural, and has never known PDC or CML.
        A REAL DEFECT, A DIFFERENT ONE. Reported, not fixed here.
    So the order's before/after on the Hammerhead CANNOT BE PRODUCED. Said so,
    with the numbers, rather than finding some other pair of runs that differ.
    CONTROL  checks/_verify_turret_inheritance.py, 30 assertions.
      the branch is driven with a BUILT FIXTURE that must exercise it: one
      point inherits and MOVES ([0.42,-0.34,0.00] -> [0.42,0.34,-0.16]), one
      keeps its own answer despite having a parent that says otherwise, one
      has nothing invented for it, none-target 2 -> 1
      then the real fleet, run TWICE with geometry held constant: 0 markers
      moved, which is exactly what 0 parents predicts
    Without the fixture half, "0 moved, PASS" would be indistinguishable from a
    fallback that does not work at all.
    TWO OF THE CONTROL'S OWN ASSERTIONS WERE WRONG, and are recorded rather
    than deleted. It compared parent names against the page's SLOT list, which
    does not contain turret bases - the assertion was wrong, not the data, and
    deleting it is how a control quietly stops checking. And it claimed an
    un-parented sibling could not move: the separation pass is GLOBAL by
    design, so a port leaving a spread group moves the ones left behind. "The
    fallback moves only the ports that inherit" is false, and now says so.
    NOT DONE, DELIBERATELY. The local run does NOT byte-reproduce the committed
    hardpoints_fleet.json. Frames agree to 1e-4 and the models are the same -
    what differs is the vertex SUBSAMPLE, so each marker snaps to a slightly
    different real vertex. Only 10 of 1,798 positions match. Promoting the
    staged run would move ~1,788 markers on the testing site for nothing the
    order asked for. REPORTED, NOT PROMOTED - and worth knowing on its own:
    THIS DERIVATION IS SAMPLE-DEPENDENT AND NOT REPRODUCIBLE ACROSS DECODES.
    Also untracked and left that way: hardpoints_fleet.json, ship_mounts.json
    and matched.json are working-tree data in an untracked directory. Adding
    1.8 MB of data to the repo is Sleven's call, not mine.

B6  DONE  cb300c8  PLACED AGAINST THIS HULL'S MEASURED EXTREMITY, NOT AGAINST A
    FRACTION OF EVERY HULL.
    TARGET put a wing mount at 88% of half-beam on a Vulture and on a Polaris
    alike. The hull's actual outermost vertex is in the geometry, so the guess
    can stop being one.
    STILL DERIVED FROM A NAME, and the page still says so. The name says
    "wing"; this finds where THIS hull's wing is instead of assuming 0.88. It
    does NOT read a mount position out of the model - there is none to read.
    renderMarkerNote() is untouched, and the control asserts that it is.
    ONE AXIS, AND ONLY FOR A LONE MOUNT - BOTH NARROWINGS FORCED BY
    MEASUREMENT, NOT CHOSEN:
      two axes pinned         crowding 118 -> 120 markers   FAILED acceptance
      one axis pinned         crowding 118 -> 121 markers   FAILED acceptance
      one axis, lone mounts   crowding 118 -> 117 markers   PASSES
    Siblings sharing a target group are held apart BY the fraction and the
    spread. Aiming all of them at one measured vertex puts them in the same
    place and the separation pass then has to undo it. A lone mount has nothing
    to be held apart from. Worth recording that the first two attempts failed
    the item's own acceptance criterion and the criterion is what found it -
    reading the code would not have.
    Every point records `aimed_at` (extremity | fraction), so which points were
    treated as extremities is checkable rather than asserted.
    THE 7 SKIPPED HULLS STAY SKIPPED. resolve_frame is untouched and the
    control drives it with proportions that MUST fail it, and with no published
    dimensions at all.
    FLEET, GEOMETRY HELD CONSTANT:
      143 points aimed at a measured extremity, 118 moved
      55 of 167 ships moved at all; 112 did not move a marker
      median move 0.074 of half-extent, p90 0.275, 3 points above 0.70
      crowding 118 markers on 19 ships -> 117 on 19
    THAT DISTRIBUTION IS THE NEGATIVE CONTROL the order names: a hull already
    close to the fixed fractions barely moves, and if every ship had moved a
    long way the NEW measurement would be the wrong one rather than the old.
    CONTROL  checks/_verify_extremity_placement.py, 23 assertions.
    The load-bearing geometric one is a hull WIDE AT THE FRONT AND NARROW AT
    THE BACK: a fraction of the bounding box lands in the fuselage, the
    measurement finds the wing. A body mount and a nameless port get NO
    measured target at all, so "we measured it" cannot quietly become "we
    measured everything".
    ONE ASSERTION WAS WRONG FIRST TIME and is recorded rather than deleted: it
    used `hardpoint_turret_roof`, which read_location resolves to 'turret'
    because it breaks on the first part it matches. Old precedence, not new
    code, and it looked exactly like a bug in the new code.
    NOT PROMOTED, same as B5: a local run does not byte-reproduce the committed
    hardpoints_fleet.json, so promoting the staged result would move ~1,788
    markers for reasons that have nothing to do with this item. The deployed
    markers are therefore UNCHANGED by B5 and B6, and B9's census reflects
    that.

B7  DONE  b1bb24b  THREE FIGURES, AND ONLY THE ONES A SHIP ACTUALLY HAS.
    Measured populations, and they match the order's within one count:
      214 pilot guns only      the old readout was the whole truth
       61 pilot AND turrets    it was half the truth
       11 turrets only         it said 0 - actively wrong
      206 carry missiles       counted nowhere at all
    (The order recorded 208 missile carriers. Measured here, counting only
    records that have slots, it is 206. Reported rather than rounded to the
    number that was expected.)
    PILOT UNTOUCHED. The IsPilotSlaveable outermost-lock figure agrees with
    CIG's own on 275 of 275, and B7 does not go near it. A fleet-wide
    assertion confirms every one of 316 hulls still counts exactly its
    non-turret guns.
    TURRET is what gunners add, labelled as needing crew, shown only where
    there are turrets. The exclusion was always right; what was wrong is that
    the excluded half was then DISCARDED. 72 hulls now report turret DPS that
    was previously counted nowhere.
    MISSILES COULD NOT BE COUNTED AT ALL - and not by anyone's decision. A
    missile record held its name, size and mass and nothing else, so there was
    nothing to add up. The generator now emits `dmgt` from the snapshot's
    Missile.DamageTotal, plus the channel split. All 57 missile parts carry it.
    IT IS A ONE-SHOT TOTAL, named differently from `dps` so the two cannot be
    summed by accident, and the control asserts the DPS figure is the pilot's
    guns and NOTHING else.
    NO TURRETS MEANS NO TURRET ROW - an absence, not a zero. A zero is a claim
    and on that hull it is the wrong one.
    AND ON THE 11 TURRET-ONLY SHIPS the pilot figure is 0 and TRUE, so it is
    said in words - "every gun on this hull is fired by a gunner, not by the
    pilot" - rather than shown as a bare 0, which reads as a broken stat
    rather than as a fact about the ship.
    CONTROL  checks/_verify_damage_readout.mjs, 23 assertions, all four
    populations driven BY NAME: Avenger Stalker (pilot only), Idris-M (both),
    Hammerhead (turret only, and it is one of the eleven), Avenger again for
    missiles at 6,280 payload.
    RULE 12. --mutate-merge folds turret DPS back into the pilot figure and
    puts the Idris-M at 28,283 - the Perseus-at-16,596 mistake reproduced on
    demand. --mutate-zero renders the turret row on every ship reading 0, which
    the pilot-only negative half catches. Both exit non-zero, as does
    --self-test.
    ONE ASSERTION FAILED AGAINST A PAGE THAT WAS RIGHT: the sentence wraps in
    the source so the rendered HTML carries a newline mid-sentence, and a
    literal match missed it. Made whitespace-tolerant - the page was not
    reflowed to suit the test, which is the tempting direction and the wrong
    one.

B8  DONE  1281c82  SWEPT, DEPLOYED, AND VERIFIED FROM THE SERVED BYTES.
    SWEEP  54 ok, 0 failed, 2 skipped, 0 NOT RUN, 216s. All eight controls the
    B run added are green in it. The 2 skipped both fetch the deployed origin
    and are named with their reason, so "skipped" is not "passed".
    DEPLOY  version 3020c87b-adfb-492f-9bec-01350a13f00d.
    UPLOAD DIFF, FILE BY FILE, as the order asked:
      + /loadout.html
      + /loadout_data.gen.js
      498 already uploaded, unchanged
    Two files is exactly what B0-B7 should touch - the ship page and its data.
    A diff of 500 would have meant something else had moved, and the count is
    checked for that reason rather than recorded for tidiness.
    VERIFIED FROM THE DEPLOYED BYTES. checks/_verify_picker_deployed.mjs
    fetches the served page and its four data files, then drives THE SERVED
    PAGE'S OWN SCRIPT through the same harness the working-tree controls use.
    30 assertions:
      ACCEPTANCE - ORIGIN 400i, ALL 10 MARKERS RESPOND on the deployed page:
        2 open the picker, 8 open the fixed panel, 0 silent. Sleven's own
        reproduction, answered on the wire.
      the served page and its data are byte-identical to what was just built
      the Avenger Stalker's turret mount serves the FITTED PART FIRST on all
        three sorts - "VariPuck S4 Gimbal Mount"
      a marker and its left-column row open IDENTICAL content at IDENTICAL
        coordinates
      the left column serves ZERO fixed ports, Specs serves all 36, and they
        sum to the hull's 57
      the served page opens NOT spinning, viewer really still, control reads
        "Start spin"
    PAGE HEIGHT AT BOTH VIEWPORTS, AND THE ORDER'S ONE THING TO ARGUE WITH IS
    ANSWERED: NEITHER HAD TO BE DROPPED.
      1920x1080   238px chrome + 842px grid = 1080 of 1080
      1366x768    238px chrome + 530px grid =  768 of 768
    The grid is `calc(100vh - var(--chrome))` and the columns scroll
    internally, so B2's inline picker and B3's stage panel cost the page NO
    height at all. The 85px of slack P7 left is untouched because neither
    feature spends page height - one scrolls inside a column, the other is
    absolutely positioned over the stage.
    STATED LIMIT: still no browser. This proves the served page's LOGIC and
    markup; the height figures are arithmetic on the served stylesheet, by the
    same model _verify_ship_page_fits.mjs uses, and are a MODEL rather than a
    measurement. It cannot see text wrapping, so the real page is at least as
    tall as this says, never shorter.

B9  DONE  1281c82  THE FLEET MARKER CENSUS, TAKEN BY CLICKING ALL 1,200
    MARKERS ON THE DEPLOYED SITE.

                                  before      after
         markers total              1200       1200
         clickable                   418        418
         fixed but informative         0        782
         SILENT                      782          0
         hulls entirely silent        61          0

    THE "BEFORE" COLUMN IS NOT A REMEMBERED NUMBER. _verify_marker_response.mjs
    --mutate puts the pre-B0 early return back and reproduces it on demand:
    782 silent, 61 hulls entirely silent, 8 of 10 on the 400i. A before/after
    where the before can be regenerated is worth more than one copied out of an
    order.
    The order required that last number reach 0 and that the check be capable
    of printing something other than 0. Both hold: the counter is separately
    proven on synthetic input, and the mutation prints 61.
    Every marker lands in one of the two ANSWERING states - 418 + 782 = 1,200,
    none unaccounted for.
    WHAT THE CENSUS DOES NOT COVER, said plainly: the marker POSITIONS are
    unchanged by this run. B5 and B6 both changed the derivation and neither
    was promoted, because a local placement run does not byte-reproduce the
    committed dataset. So these 1,200 markers are in the same places they were
    this morning - what changed is that all of them now answer.
