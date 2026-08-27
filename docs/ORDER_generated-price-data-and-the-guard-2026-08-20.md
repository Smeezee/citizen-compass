# ORDER — FIND stops needing a server, the banner comes off, and the never-delete guard stops being an allowlist. RUN CONTINUOUSLY.

    from    C1, 2026-08-20
    for     Code
    status  GO. No stop points. Run rules are §1 of
              docs/ORDER_shop-and-price-layer-RUN-CONTINUOUSLY-2026-08-19.md.
              Read them again and obey them.
    ledger  APPEND to docs/LEDGER_shop-price-layer-2026-08-19.md. Same file.

---

## 0. THE HEADLINE: this unblocks E2 WITHOUT Railway

G6 is blocked because FIND needs a server and the server is down. **So FIND stops
needing a server.** The prices are a snapshot with a date stamped on them; they do
not change between UEX pulls. A page searching them needs a file, not a database.

**MEASURED, not estimated.** C1 built the exact payload and compressed it:

    every item, every price, every terminal, all 100 categories
      780 KB raw  ->  160 KB gzipped
    terminal index alone            10 KB gzipped
    search index (name + id only)   67 KB gzipped
    largest per-category shard      13 KB

**160 KB is the whole thing. DO NOT SHARD IT.** Splitting this into 56 files buys
nothing and costs 56 requests. One file.

The site already works this way - `holo_data.gen.js` and `loadout_data.gen.js`
are generated data. **FIND is the first page in the project that broke that
pattern and it broke on its first day.** This puts it back.

## 1. SLEVEN'S RULINGS

**R5. FIND reads generated data. The API stays for the bench and for writes.**
PostgreSQL remains the system of record. The generator reads it and writes the
site's copy. Nothing built in the A-G runs is wasted - the schema, importers,
auditors and API are what produce the file.

**R6. The snapshot date goes on EVERY price row, not once at the top.**
More honest, and the clutter is worth it. A number with no date is a claim; a
number with a date is evidence.

**R7. The raw snapshot is downloadable from the site, with a checksum.**
Costs nothing and it is the strongest form of "we can prove it" - a visitor can
check every number against the file the page actually read.

**R8. The site says what it can prove and NOT MORE.** See H4. This is the one
item where wording is the deliverable, so do not paraphrase it into something
smoother.

## 2. THE WORK

**H1. The generator.** A script that reads PostgreSQL and writes ONE generated
data file for the site, in the same style and location as the existing
`*.gen.js` files. Contents: items (id, name, category, size, company), their
price rows (terminal, buy, sell), the terminal index (name + resolved location),
the category list, and **the snapshot id and date**.
*Acceptance:* the file is produced and is under 250 KB gzipped. **If it is not,
stop and report the number rather than shipping something bigger than measured** -
C1's measurement was 160 KB and a large miss means the shape changed.
*Control:* row counts in the file equal row counts in the database. Assert it.

**H2. FIND reads the file.** Remove the API calls from the read path. Search,
category filter and price range all run in the browser.
*Control:* with the network blocked after first load, search still works. That is
the whole point of the change and it is the only control that proves it.

**H3. E2 — THE BANNER.** Deploy, then **fetch the deployed URL and confirm real
rows come back**. Real rows -> the banner comes off. **The rule has not changed
just because the source did: not on a build, not on a deploy, not on a local
server, not on a good feeling.** Fetch the live page or it stays up.
*This is now achievable without Railway. If it still fails, it fails for a new
reason and I want that reason in the ledger.*

**H4. Say what is provable, and not more.** The honest claim is:

    UEX reported this price at this terminal in the snapshot taken <date>.

**Not "this is the price."** The commodity price rows carry a `quality` field,
averaged buy/sell figures and stock levels - fields that exist because the numbers
are **submitted by players and rated for confidence**, not read out of the game.
The page must not imply otherwise. Put the distinction in plain words where a
visitor will read it, in the voice `README-FOR-TESTERS.txt` already uses.
*Control:* no wording on the page states or implies a price is measured from the
game.

**H5. The raw snapshot, downloadable, with a checksum** published beside it.
*Control:* download it, hash it, confirm it matches what the page claims.

**H6. The generator is a build step, not a thing somebody remembers.** It runs in
the normal build. A stale generated file must be detectable.
*Control:* change one row in the database, re-run the build, confirm the file
changed. **And the negative half: run the build twice with no database change and
confirm the file is byte-identical** - a generator with a timestamp baked into it
churns git forever and nobody notices for a year.

**H7. The never-delete guard is an allowlist and it is silently off for everything
built this week.** `app/preservation.py` protects 16 hardcoded tables. **None of
`shop_items`, `item_prices`, `terminals`, `locations`, `item_categories`,
`snapshots`, `shop_item_commodity_xref` or the hardpoint slot tables are in it** -
26,657 prices and 2,195 slots are unprotected right now. That is how the G5
control's `DELETE` reached a real table.

**Invert it: protect by default, with an explicit list of genuinely ephemeral
tables** (findings, harness throwaways). A new table is then protected by
construction.
**And add a check asserting every mapped table appears in exactly one of the two
lists**, so forgetting fails loudly instead of silently.
*Why not just add the eight tables:* that is the same failure next month, and
`preservation.py`'s own docstring argues against exactly that - "a rule that
depends on every future author remembering it is a convention."
*Control:* a new table added to the models with no classification **fails the
check**. Observe it failing. Then classify it and observe it pass.
**Take care with the e2e harness and the findings table** - they legitimately
delete, and that is what the ephemeral list is for.

**H8. The staleness flake order.** `docs/ORDER_collector-staleness-selftest-flake-2026-08-20.md`
exists. Execute it, with one amendment: **the ten-minute HANG is the primary
symptom, not a footnote.** Four checks that flake is a timing wobble; a selftest
that hangs for ten minutes is a deadlock or a wait with no timeout, and it is the
more serious of the two. The fix direction for the flakes is to **inject a clock
rather than read one** - a check whose result depends on machine load cannot be
trusted when it PASSES either.
**Do not cut a collector release. Do not install it anywhere.**

**H9. Sweep.** Re-run every control in `checks/`. H7 changes behaviour at the
engine that every session-opening check inherits.

## 3. WHAT MUST NOT HAPPEN

- **Do not remove the banner without a live fetch.** H3.
- **Do not shard the data file.** §0. 160 KB.
- **Do not delete the API.** R5. The bench uses it.
- **Do not let the generator bake a timestamp into its output.** H6.
- **Do not put the new tables in the old allowlist and call H7 done.** H7.
- **Do not claim a price is measured from the game.** H4.
- **Do not cut a release. Do not `git add -A`. Push at the end.**

## 4. REPORT

- The generated file's actual gzipped size against C1's measured 160 KB.
- Whether FIND works with the network blocked.
- Whether the banner came off, and if not, the new reason.
- Which tables ended up on the ephemeral list, and why each one is there.
- What the staleness hang turned out to be.
- Anything here you think is wrong. **H7's inversion is the part most worth
  arguing with** - it changes behaviour for every table in the project, and if you
  find a case where protect-by-default breaks something legitimate, that case is
  more valuable than finishing the item.
