# ORDER — build the observations table and the exact resolver. Database only. No collector code in this order.

    from      C1, 2026-09-06
    for       Code
    basis     docs/DESIGN_the-fact-store-is-mostly-already-built-2026-09-06.md
              READ IT FIRST. It carries the reasoning; this is only the task list.
    scope     alembic migration, app/models.py, one resolver module, its controls.
              NOTHING in citizen-collector/. NOTHING in testing/.
    authority Sleven, 2026-09-06: "build it or give it to code to build."

---

## 0. Before anything

**Do not create a `facts` table.** `snapshots` + `item_prices` already is one and
this order deliberately extends it rather than duplicating it. If any part of
this order reads as though it wants a parallel store, stop and say so.

**Do not touch `item_prices` or `shop_items`.** This order adds two tables and
reads the existing ones. It modifies none of them.

## 1. Migration — two tables

New alembic revision on the current head. Two tables, both append-only.

### `observations`

    id                 integer      PK
    snapshot_id        integer      FK snapshots.id      NOT NULL  indexed
    observed_at        timestamptz  NOT NULL  indexed
    game_patch         varchar(32)  NOT NULL  indexed
    game_build         varchar(64)  NULL
    context_text       text         NULL
    subject_text       text         NOT NULL  indexed
    attribute          varchar(32)  NOT NULL  indexed
    value_text         text         NOT NULL
    value_num          numeric      NULL
    reader_confidence  numeric      NOT NULL
    panel_key          varchar(64)  NOT NULL  indexed
    detail             jsonb        NULL
    created_at         timestamptz  NOT NULL  server_default now()

Constraints, at the database:

    ck_observations_value_num_non_negative     value_num IS NULL OR value_num >= 0
    ck_observations_confidence_range           reader_confidence >= 0 AND reader_confidence <= 1
    ck_observations_subject_not_empty          length(btrim(subject_text)) > 0
    ck_observations_value_not_empty            length(btrim(value_text)) > 0

**There is no image column and no path column. Do not add one** - rule 21 made
structural rather than promised.

### `observation_links`

    id              integer      PK
    observation_id  integer      FK observations.id   NOT NULL  UNIQUE
    shop_item_id    integer      FK shop_items.id     NULL  indexed
    terminal_id     integer      FK terminals.id      NULL  indexed
    method          varchar(16)  NOT NULL
    linked_at       timestamptz  NOT NULL  server_default now()

Constraints:

    uq_observation_links_observation   UNIQUE (observation_id)
    ck_observation_links_method        method IN ('exact')
    ck_observation_links_has_a_target  shop_item_id IS NOT NULL OR terminal_id IS NOT NULL

**`method IN ('exact')` is deliberately a one-value CHECK.** A future method has
to be added by migration, in the open, rather than appearing in a string column.

## 2. `app/models.py`

Add `Observation` and `ObservationLink` in the same house style as the existing
classes: a block comment above each saying what it is FOR and which decision it
implements, not what the columns are. Cite the design doc by filename.

Neither is a `VerifiableMixin` table, for the same reason `ItemPrice` is not: an
observation is not a curated statement, and its provenance is carried by
`snapshot_id`.

## 3. The resolver — `app/observation_resolver.py`

One function, one rule.

    resolve(session, observation) -> ObservationLink | None

    subject_text  ->  shop_items.name   exact match after casefold + strip
    context_text  ->  terminals.name    exact match after casefold + strip

**NO FUZZY MATCHING (rule 17).** No edit distance, no prefix, no substring, no
token overlap, no `ILIKE '%...%'`, no "nearest". If you find yourself importing
`difflib` this order has been misread.

Three outcomes, and all three are correct behaviour:

    exactly one match      write an ObservationLink with method='exact'
    zero matches           write nothing, return None. NOT an error.
    two or more matches    write nothing, return None, and RECORD IT (§4)

**Two exact matches is a defect in the catalogue, not an ambiguity to resolve
(rule 19).** Do not pick one. Do not pick the newest. Do not pick by id.

The resolver is idempotent: running it twice over the same observations produces
the same links and no duplicates. The UNIQUE on `observation_id` enforces that
at the database, and the code must handle the conflict rather than crash.

## 4. Ambiguity reporting

Multi-match cases go to the existing auditor results table if one exists for this
purpose - **check first, and reuse it if it does.** If none exists, write them to
`_work/observations/ambiguous.json` and say in your handoff that a proper results
table is still owed. **Do not create a new results table in this order.**

Auditors flag only. Nothing here ever edits `shop_items` to make a match work.

## 5. Controls — and every one must be able to fail (rule 12)

`checks/_verify_observation_store.py`. At minimum:

1. **The resolver refuses a near miss.** Insert a `shop_items` row named
   `Titanium`. Feed an observation with `subject_text = 'Titaniium'`. Assert zero
   links. **Positive control in the same test:** feed `'Titanium'` and assert
   exactly one link - so a resolver that links nothing at all cannot pass.
2. **The resolver refuses two exact matches.** Two `shop_items` rows with the
   same name, one observation. Assert zero links and one ambiguity recorded.
3. **Case and whitespace only.** `'  TITANIUM '` links to `Titanium`. This is
   the one normalisation permitted and the test pins it, so a later hand
   cannot widen it quietly.
4. **The database refuses a confidence of 1.5**, and refuses an empty
   `subject_text`. Assert the constraint fires, not that the writer declines.
5. **Idempotence.** Resolve twice, assert one link, no exception.
6. **No image column exists.** Assert `observations` has no column whose name
   contains `path`, `file`, `image`, `frame` or `png`. This test exists to fail
   the day someone adds one.
7. **The unresolved pile is countable.** A query returns the number of
   observations with no link. Assert it is correct on a fixture with a known
   mix.

Exit 2 for NOT PERFORMED, not exit 1 - consistent with the exit-2 work you are
already doing.

## 6. What is NOT in this order

- No collector code. No Go. `citizen-collector/` is untouched.
- No reader, no shape table, no panel table. Those come after Sleven rules on
  §7 of the design doc.
- No promotion of observations into `item_prices`. That is a separate order once
  the resolver has been run against real strings and the unresolved rate is
  known. **Writing the promotion before that number exists would be building on
  an unmeasured assumption.**
- No front-end. Nothing is shown to a visitor.

## 7. Acceptance

    alembic upgrade head            runs clean on the real database
    alembic downgrade -1            runs clean, both tables gone
    checks/_verify_observation_store.py    all controls pass, and each has been
                                           seen to fail when its condition is broken
    the full sweep                  no previously-green control turns red

**Nothing committed or pushed without Sleven's explicit go-ahead (rule 2). No
`git add -A`.**

## 8. Report back

Your handoff should say: the revision id, the two tables as created, whether an
auditor results table already existed for §4, and - the one number I actually
want - **how many `shop_items` names and `terminals` names exist to resolve
against.** That number is the ceiling on what the collector can ever understand,
and nobody has stated it.

---

*C1, 2026-09-06.*
