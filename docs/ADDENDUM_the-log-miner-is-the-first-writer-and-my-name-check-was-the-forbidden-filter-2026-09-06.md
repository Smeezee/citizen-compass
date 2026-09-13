# ADDENDUM — two corrections to yesterday's order, both found by reading the collector instead of remembering it

    from      C1, 2026-09-06
    for       Code, Sleven
    amends    docs/ORDER_the-observations-table-and-the-exact-resolver-2026-09-06.md
              docs/DESIGN_the-fact-store-is-mostly-already-built-2026-09-06.md
    method    read citizen-collector/gamelog_mine.go and
              citizen-collector/captures/gamelog-dataset.json on the machine.

**Apply both before writing the migration. Everything else in the order stands.**

---

## CORRECTION 1 — my §5 name check is the exact thing this project already
## decided never to build, and the reasoning against it is better than mine

The order's §5 asked for:

    CHECK subject_text !~ '<a player-name shape>'

`gamelog_mine.go` forbids that in writing, at line 211, under the heading **THE
GOVERNING RULE FOR EVERYTHING DERIVED FROM ANYTHING - Sleven, 2026-08-13**. Its
argument, which I did not have and which is right:

> Handles look like ordinary words, so any heuristic either misses real ones or
> eats legitimate shop and item names - and both failures are silent.

It goes further and predicts this exact mistake, in advance, naming it:

> The day somebody builds the reading half, the frame data will not look like log
> data, and writing "a quick scrubber for the OCR output" will feel like the
> reasonable thing to do. THAT is the second, weaker mechanism the decision
> forbids. Extend this map, or write another one in this shape. **Do not write a
> filter.**

It was written for a path that did not exist yet. The path now exists and I
walked straight into it on the first try. **That comment did its job and I am
recording that it did.**

**What replaces it.** The same shape as `mineTxnKeep`: an ALLOW-LIST, not a
detector.

- The **panel table** names, per layout, which rectangles are readable and what
  each one is. A rectangle not named is never read, so its characters never
  exist. Chat, contacts, party and the friends list are not named, ever.
- The reader emits a field only if its `panel_key` + field name is on the
  allow-list. **A field not named there never reaches disk**, exactly as a log
  field not in `mineTxnKeep` never reaches disk.
- A `mineForbidden`-equivalent stays as belt and braces: a field named
  `playerName`, `handle`, `nickname` or similar is refused even if some future
  panel definition allow-lists it.

**Drop the regex CHECK from the migration.** Keep the structural half - no image
column, no path column - that part was right.

**The control (rule 12) changes with it.** Do not test that a handle-shaped
string is rejected; that tests a detector that no longer exists. Test instead:

1. A panel definition naming a rectangle that is not on the allow-list produces
   **zero** rows from that rectangle. Positive control in the same test: an
   allow-listed rectangle on the same frame produces its row, so a reader that
   emits nothing at all cannot pass.
2. A field named in `forbidden` is refused **even when a panel definition
   allow-lists it**, so the two mechanisms are proven independent.

## CORRECTION 2 — the first writer into `observations` is not the screen reader.
## It is the log miner, and it already works.

`gamelog_mine.go` reads Star Citizen's own `Game.log` and its `logbackups`
archive. **It needs no OCR, no shape table and no panel table.** From
`captures/gamelog-dataset.json`, schema 3, generated 2026-08-18, tool 0.3.3 -
counted, not estimated:

    ship_classes ........ 992      equipment_seen ...... 542
    quantum_routes ....... 57      contracts_seen ....... 55
    locations ............ 44      subsystems ........... 71
    deaths .............. 131      shop_class_names ..... 18
    builds ............... 34      mission_payouts ...... 16
    sent_txn_keys ....... 308

**Those 308 transactions carry `shopName`, `itemName`, `client_price`,
`quantity` and `currencyType`** - buy and sell, item and commodity - and they
were SENT and cleared rather than stored anywhere queryable. The transactions
list in the file is empty for that reason, not because none were found.

**Three consequences, in order of importance.**

**(a) The log gives the resolver its own test data, today, with no reading
half.** 992 ship class names and 542 equipment names against `shop_items` is a
real exact-match rate that can be measured this week. That is the number §8 of
the order asks for, and it turns out it can be answered from both sides rather
than one.

**(b) A log line is a better observation than a pixel and should be preferred
wherever both exist.** It is already structured, already field-named, already
allow-listed, and it cannot be misread. **The screen reader's job is what the
log does not emit** - a shelf price you did not buy, a stock level, a panel you
walked past - not a second, worse copy of what the log already says.

**(c) `observations` must therefore not assume a frame.** The order's columns are
already source-neutral, which is lucky rather than clever. Make it explicit:

    source_kind   varchar(16)  NOT NULL   'gamelog' | 'screen'

    CHECK source_kind IN ('gamelog','screen')

and `panel_key` becomes **nullable**, because a log observation has no panel.
Add:

    CHECK (source_kind = 'screen') = (panel_key IS NOT NULL)

so a screen row without a panel and a log row with one are both refused at the
database.

**Do not port the log miner in this order.** It stays where it is and keeps
working. A later order routes its output into `observations`; this one only makes
sure the table can take it without a migration to fix it.

## What this does NOT change

- No fuzzy matching. Still exact equality, still refuses two matches (rule 19).
- Still no new `facts` table.
- Still nothing in `citizen-collector/`. This addendum reads it; it does not edit
  it, and the log miner is not to be touched.
- Still nothing committed or pushed without Sleven's go-ahead (rule 2).

## §8 report-back, extended by one line

As well as the `shop_items` and `terminals` name counts, report **how many of the
992 ship class names and 542 equipment names in
`citizen-collector/captures/gamelog-dataset.json` match a `shop_items` name by
exact equality after casefold and trim.** Report the three numbers separately.
Do not attempt a near-match count; if the exact rate is low that is a catalogue
finding, not a reason to loosen the rule.

---

*C1, 2026-09-06. The correction in §1 was predicted in a code comment written
three weeks earlier. Read the collector before designing for it.*
