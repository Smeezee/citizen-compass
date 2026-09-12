# DESIGN — the fact store the collector needs is 80% already in this database, and the missing 20% is one table and one resolver

    from      C1, 2026-09-06
    for       Sleven, Code
    trigger   Sleven: "design it from the ground up... then build it or give it to
              code to build." The ground-up design was going to be a new table.
              It should not be. This document is why, and what to build instead.
    method    read app/models.py, alembic/versions/, citizen-collector/ on the
              machine. Not from the planning docs, which have been wrong about
              this repo in both directions.

---

## 1. The conclusion first

**I was about to specify a new `facts` table. That would have been a duplicate of
work already done, already migrated, and already carrying the exact properties I
was about to argue for.**

`snapshots` + `item_prices` is a fact store. It is append-only. Its unique key
includes `snapshot_id` specifically so a second pull ADDS rows instead of
overwriting them - the comment in `models.py` says so, and names the incident
that caused it ("the roadmap watcher overwrote history once on this project and
it cost a rebuild"). `snapshots.source` is already generic, and its own comment
already anticipates non-UEX writers: *"scunpacked and the wiki land snapshots
the same way and will want rows here."*

**A screen-reading collector is another writer of exactly that shape.** It does
not need a parallel store. It needs a row in `snapshots` with
`source = 'collector'` and a `snapshot_key` naming the play session.

## 2. What is genuinely missing, and it is the thing that actually matters

`item_prices` cannot take a screen reading directly, and the reason is a rule,
not an oversight:

    shop_item_id  ForeignKey("shop_items.id")   NOT NULL
    terminal_id   ForeignKey("terminals.id")    NOT NULL

**The collector reads a STRING. It does not know an id.** It sees the characters
`TITANIUM` and `8.20` in a panel. To write an `item_prices` row something must
turn `TITANIUM` into a `shop_items.id`, and rule 17 forbids doing that by
similarity. Rule 19 forbids resolving the ambiguity by picking.

So a reading that does not resolve **has nowhere to go**, and today it would be
either dropped or forced. Both are wrong. Dropped loses a real observation;
forced writes a guess into a table whose whole design is about not guessing.

**That gap is the entire foundational job.** Everything else about the collector
- the shape table, the panel table, the storage budget - is downstream of it.

## 3. The design: one table, one resolver, nothing else

### 3.1 `observations` - what the screen said, before anything is known about it

Append-only. Strings, not ids. Every row is a statement about a rectangle of
pixels at a moment, and is true whether or not it ever resolves.

    id
    snapshot_id      FK snapshots.id      NOT NULL   the play session
    observed_at      timestamptz          NOT NULL   from the frame, not insert time
    game_patch       text                 NOT NULL   rule 20; read off the debug overlay
    game_build       text                            same source
    context_text     text                            what the panel called the place
    subject_text     text                 NOT NULL   the string read, verbatim
    attribute        text                 NOT NULL   'price_buy' | 'price_sell' | 'stock' | ...
    value_text       text                 NOT NULL   the string read, verbatim
    value_num        numeric                         parsed, NULL if it would not parse
    reader_confidence numeric             NOT NULL   0..1, the reader's own certainty
    panel_key        text                 NOT NULL   which layout this came from
    detail           jsonb                           glyph ids, pixel boxes, per-char scores

**`subject_text` and `value_text` are kept verbatim forever.** They are the
receipt. If the resolver is later found wrong, the string is still there to
re-resolve - the correction reaches backwards because the raw reading was never
thrown away. This is the same reasoning `item_prices.detail` already uses to
keep UEX's pre-transformation values.

**No image is stored in this table and none is referenced.** Rule 21 - a frame
may contain a name, nothing derived from it ever may. `detail` holds glyph ids
and boxes, never a crop, never a path to one.

**Constraints, at the database and not in the writer** (A7's own argument - an
importer can be bypassed, a CHECK cannot):

    CHECK value_num IS NULL OR value_num >= 0
    CHECK reader_confidence BETWEEN 0 AND 1
    CHECK length(subject_text) > 0
    CHECK subject_text !~ '<a player-name shape>'      see §5

### 3.2 `observation_links` - the resolution, kept separate from the reading

Exactly the `shop_item_commodity_xref` pattern, and for the same reason: a link
records a relationship without modifying either side, and can be dropped whole
if the rule behind it is reversed.

    id
    observation_id   FK observations.id   NOT NULL  UNIQUE
    shop_item_id     FK shop_items.id                 nullable
    terminal_id      FK terminals.id                  nullable
    method           text                 NOT NULL   'exact' only, today
    linked_at        timestamptz          NOT NULL

**UNIQUE on `observation_id`** - one reading resolves to one thing or to nothing.
A second link is refused at insert, loudly, naming the row. That is this
project's preferred failure and it is already how the xref table behaves.

**`method` exists so a future non-exact method can never be mistaken for an
exact one after the fact.** Today it takes exactly one value.

### 3.3 The resolver - exact equality, and it refuses

    subject_text  ==  shop_items.name        exact, case-folded, trimmed
    context_text  ==  terminals.name         exact, case-folded, trimmed

Nothing else. No edit distance, no prefix, no token overlap, no "closest match".
An observation that matches zero rows stays unlinked. An observation that
matches two rows stays unlinked **and is reported**, because two exact matches is
a defect in the catalogue, not an ambiguity to resolve (rule 19).

**Unlinked is a normal, permanent, non-lossy state.** The reading is kept. It
becomes answerable the day the catalogue gains the name. That is the mechanism
by which the store gets better without the collector being re-run.

### 3.4 Promotion to `item_prices`

A linked observation whose attribute is a price becomes an `item_prices` row
under its own `snapshots` row. Nothing about `item_prices` changes. The site
already reads it.

**This is why the whole design is worth it:** the day the resolver works, the
collector's readings appear on the site through the code that is already
running, with no new read path and no new front-end work.

## 4. What this buys, stated plainly

- **The collector can be rewritten, replaced, or deleted and the observations
  survive**, because they are strings in a table that has no dependency on the
  program that wrote them.
- **The site's data and the collector's readings share one store**, so the
  companion later reads one place.
- **A wrong reading is fixable in the past**, because the verbatim string is
  kept and the link is separate from the reading.
- **Nothing is guessed**, and the unresolved pile is a measurable number that
  says exactly how much catalogue is missing.

## 5. The name rule, made structural rather than promised

Rule 21 is currently a discipline. In this design it becomes a constraint.

- `observations` holds no image and no path to one. There is no column for it.
- A CHECK constraint refuses a `subject_text` matching the shape of a player
  handle in the contexts where handles appear (chat, contacts, party). **The
  panel table decides which panels are readable at all, and chat is not one of
  them** - the reader never looks at that rectangle, so the string never exists
  to be stored.
- **The control that could fail (rule 12):** a test feeds the reader a frame
  containing a known handle in the chat panel and asserts zero rows are written
  from that rectangle. It must be possible for that test to fail.

## 6. What I am NOT proposing, and why

**Not a new `facts` table.** Duplicates `item_prices`. See §1.

**Not a generalised importer pipeline.** Standing rule: build 2-3 concrete
importers before generalising. The collector is the second writer after UEX. The
third does not exist yet. Generalising now is the mistake this project already
decided not to make.

**Not SQLite or a file store.** Postgres is already on the machine, already
required by the build, and putting the readings anywhere else recreates the exact
corner this design exists to avoid.

**Not a confidence column on `item_prices`.** Its own comment refuses one and the
reasoning is right - the provenance is carried by the snapshot. The reader's
confidence belongs on the observation, which is where uncertainty actually lives.

## 7. The open decision that is Sleven's, not mine

**Whether the existing collector program is rebuilt or kept and re-fitted.**

Sleven said "completely rebuilt as a program." I want that decision made against
the measurement rather than the impression, so here it is.

What exists today and works, on record: **575 selftest checks, 0 failed**, on
Windows, 2026-08-27. Windows.Graphics.Capture is implemented and captured 756
frames. There is a working service install, autostart, consent gate, a scrub
path, an export path, and a selftest harness that is the reason this project can
trust anything about the collector at all.

What is wrong is **one layer**: it decides when to snap by predicting the moment,
and it predicts wrong - 426 of 756 frames are labelled `terminal_open` or
`terminal_scroll` and the ones opened show a seat interior, a chat window and the
quit-to-desktop dialog. Not one shows a shop panel.

**My recommendation was to keep the shell and replace that layer**, because the
shell is the part that took months and is proven, and the trigger logic is the
part that is provably wrong. A full rebuild throws away the 575 checks along with
the 426 bad triggers.

---

## 2026-09-06 — WHAT IS AGREED, AND WHAT IS STILL BEING DESIGNED

**C1 first wrote this section as "RULED, settled, nobody reopens it." Sleven
corrected that on the spot:** *"Don't rule anything as set in stone. The
collector's rebuild is still being designed. I know we have agreed upon foundation
pieces, but everything else is still being designed."*

**He is right and the correction is recorded rather than quietly applied.** The
direction was agreed. The design was not, and a document calling an unfinished
design settled is how a project stops thinking about it.

### AGREED FOUNDATIONS — do not re-argue these

**It is a rebuild, not a refit.** His words: *"it's a complete rebuild because
we're gonna be building a program, not a set of things working in the
background... we're gonna take the basic things that did work with the collector,
and we're gonna redesign them into this more advanced program that will grow."*

**The trigger layer dies.** 426 of 756 frames mislabelled, not one showing a shop
panel. That is the measured reason the refit argument lost.

**These carry in as redesigned modules, not as inherited code:** the log miner,
Windows.Graphics.Capture, the scrub path, service install, and the selftest
discipline.

**Live screen reading, not recorded film.** Ruled 2026-09-06 — *"yes cancel
it."* The 2026-08-02 recommendation against a live watcher is withdrawn; it was
argued on the frame-rate cost of an RTX 3060 Ti and he now has far more card than
that. See `docs/RULING_the-film-study-recommendation-is-withdrawn-2026-09-06.md`,
which also records the two things film study was right about that the live reader
must be designed not to lose.

**No consent right now, by ruling.** *"There doesn't need to be any consent on the
collector right now. at all because the collector is gonna be rebuilt on only my
computer. Once I finish building it, then we will reevaluate all the consent it
needs and figure out how to properly do it before it's ever shipped to anybody."*
So the old text, its 2,600-character assertion and `consentVersion = 4` retire
with the old program rather than being trimmed or raised.

### STILL BEING DESIGNED — open, and Sleven is designing it

**Everything not in the list above.** The program's structure. What "reads
continuously" actually means in code. Where the module boundaries fall. How the
observations table and the exact resolver sit inside it. Which of the thirty
advanced ideas ever get built — that list is explicitly marked *do not action*.

**Nothing here is C1's to close.** Sections 1–6 of this document were written
before any of it and are proposals, not decisions.

### One thing C1 is holding, and it is a question, not a ruling

A program with no consent is correct on one machine and defective the moment
anything leaves it. **"We will figure it out before it ships" is an intention, and
an intention cannot fail** — which is rule 12's exact shape.

**A possible answer, for Sleven to accept or reject when the design is further
along:** the build refuses to produce a distributable artifact — installer, signed
binary, public download — while consent is unresolved, as a build failure rather
than a warning. **That is a suggestion. It is not decided and it is not a
requirement until he says so.**

### A note on the 575 checks, because the argument may come back

The case against a rebuild was that it discards 575 passing selftests. Worth
recording so it is weighed rather than repeated: **a selftest written against a
program that predicted the wrong moment was proving the wrong thing correct.**
What has value is the discipline, not those particular checks. **That is C1's
reading, not a ruling.**
