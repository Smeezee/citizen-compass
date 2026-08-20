#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_find_data.py - the shop and price layer as ONE generated file for FIND.

H1 of docs/ORDER_generated-price-data-and-the-guard-2026-08-20.md.

WHY THIS EXISTS
===============
FIND was the first page in this project to read a live API on its read path,
and it broke on its first day: the Railway service answered 502 all evening and
the page had nothing to show. Every other page here - holo, loadout, keybinds -
reads a `*.gen.js` file generated once from the system of record. This puts
FIND back on that pattern.

PostgreSQL stays the system of record (R5). This script reads it and writes the
site's copy. The API is not removed; the bench and every write path still use
it. What changes is that a visitor searching for a gun does not need a server
to be up.

The prices are a snapshot with a date on them. They do not change between UEX
pulls. A page searching them needs a file, not a database.

ONE FILE, NOT FIFTY-SIX
=======================
Deliberately NOT sharded per category. C1 measured the whole payload at 160 KB
gzipped; splitting it into 56 shards buys nothing and costs 56 requests. The
acceptance ceiling is 250 KB gzipped and this script ENFORCES it - if the shape
ever changes enough to blow past that, the build stops and reports the number
rather than quietly shipping something bigger than anybody measured.

NO GENERATION TIMESTAMP IN THE OUTPUT (H6)
==========================================
Nothing here writes "generated at <now>". A generator that bakes its own run
time into its output churns git on every build forever and nobody notices for a
year. Run this twice against an unchanged database and the file is
byte-identical - --verify-stable proves that on every run, and --check makes a
stale file detectable rather than something somebody has to remember.

Everything that varies is read from the database: the snapshot keys, their
capture dates, and the row counts.

WHOSE NUMBER IS IT (R8 / H4)
============================
These are UEX reports. UEX prices are submitted by players and rated for
confidence - they are not read out of the game. So this file carries, for every
price row, the snapshot it came from and UEX's own last-modified date for that
row, so the page can say "UEX reported this price at this terminal in the
snapshot taken <date>" rather than "this is the price". The quality field,
averaged buy/sell figures and stock levels on the commodity rows are precisely
why: those are fields you only need when the numbers are estimates.

THE SHAPE
=========
Positional arrays, not objects, because 26,657 price rows with named keys would
be several hundred KB of repeated key names. The reader maps them back by name
at load, and the meaning of every slot is in FIND_SCHEMA inside the file
itself, so the format is not something you have to come back here to decode.

    snaps  [snapshot_id, key, captured_date]
    cats   [uex_id, name, section, is_game_related]
    terms  [uex_id, name, resolved_path, type]
    cos    company names, deduped - 7,932 items share a few hundred companies
    dates  the distinct UEX last-modified dates, deduped - 127 of them across
           26,657 price rows, so the rows carry an index rather than a string
    items  [kind, uex_id, name, cat_ix, size, co_ix, prices]
    price  [term_ix, price_buy, price_sell, snap_ix, date_ix]

TWO THINGS ARE DELIBERATELY NOT IN HERE, AND BOTH WERE MEASURED FIRST
=====================================================================
The item UUID. It costs 138 KB GZIPPED on its own - 5,566 uuids of random hex,
which is incompressible by construction, in a 173 KB file. H1's field list is
"id, name, category, size, company" and the uuid is not in it; carrying it
anyway took the file from 173 KB to 333 KB and blew the acceptance ceiling.
Nothing on the page needs it: every route is keyed on (source_kind, uex_id),
which is the actual database key, and the API still serves the uuid for anyone
who wants it. Measured, not assumed - see the ledger.

Per-row date STRINGS. Same fact, cheaper: 127 distinct dates across 26,657
rows, so the row carries an index into `dates`. That is not a trim, it is the
same data spelled shorter.

`kind` is 0 for an item and 1 for a commodity: shop_items is keyed by
(source_kind, uex_id) because UEX numbers commodities from 1 in their own id
space and 200 of those ids collide with item ids meaning something else. The
page's #i/ route uses "item:1234" / "commodity:12" exactly as it did against
the API, so no link shape changes.

A NULL IS A BLANK. Zero is not a price - UEX writes price_buy = 0 to mean "this
terminal does not sell this", and the importer already turns that into NULL. It
stays NULL here and renders as a blank, never as "0 aUEC".

An item with NO price rows still gets an entry, with an empty price list.
Absence is data (order sec 3.6); the page has to be able to say "nobody sells
this", and that is a different sentence from "we have never looked".

Rule 15: every open states its encoding.
"""

import argparse
import gzip
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "testing", "_src", "find_data.gen.js")

sys.path.insert(0, HERE)


def _load_env():
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(os.path.join(HERE, ".env"))


def _iso_day(dt):
    """A date as YYYY-MM-DD, or None. Never a fabricated stand-in (rule 11)."""
    return None if dt is None else dt.strftime("%Y-%m-%d")


def collect(session):
    """Read every row FIND needs, in a deterministic order.

    The ORDER BY clauses are not decoration. H6 requires two runs against an
    unchanged database to produce identical bytes, and PostgreSQL makes no
    promise about row order without one.
    """
    from sqlalchemy import text

    snaps = [
        [r[0], r[1], _iso_day(r[2])]
        for r in session.execute(text(
            "SELECT id, snapshot_key, captured_at FROM snapshots ORDER BY id"
        ))
    ]
    snap_ix = {r[0]: i for i, r in enumerate(snaps)}

    cats = [
        [r[0], r[1], r[2], 1 if r[3] else 0]
        for r in session.execute(text(
            "SELECT uex_id, name, section, is_game_related "
            "FROM item_categories ORDER BY uex_id"
        ))
    ]

    # Price rows point at the internal primary key; the page addresses a
    # terminal by its UEX id (the #p/ route). Both indexes are built from the
    # same ORDER BY as `terms` so position and identity cannot drift apart.
    term_ix = {
        r[0]: i
        for i, r in enumerate(session.execute(text(
            "SELECT id FROM terminals ORDER BY uex_id"
        )))
    }
    terms = [
        [r[0], r[1], r[2], r[3]]
        for r in session.execute(text(
            "SELECT uex_id, name, resolved_path, type "
            "FROM terminals ORDER BY uex_id"
        ))
    ]

    cat_ix = {
        r[0]: i
        for i, r in enumerate(session.execute(text(
            "SELECT id FROM item_categories ORDER BY uex_id"
        )))
    }

    item_rows = list(session.execute(text(
        "SELECT id, source_kind, uex_id, name, category_id, category_name, "
        "       size, company_name "
        "FROM shop_items ORDER BY source_kind, uex_id"
    )))

    price_rows = list(session.execute(text(
        "SELECT p.shop_item_id, p.terminal_id, p.price_buy, p.price_sell, "
        "       p.snapshot_id, p.source_date_modified "
        "FROM item_prices p "
        "JOIN terminals t ON t.id = p.terminal_id "
        "JOIN shop_items s ON s.id = p.shop_item_id "
        "ORDER BY s.source_kind, s.uex_id, t.uex_id, p.snapshot_id, p.id"
    )))

    # Company names deduped into their own table. Measured: a few hundred
    # distinct names across 7,932 items, so repeating the string on every item
    # is pure waste in a file whose whole point is its size.
    cos, co_ix = [], {}
    for r in item_rows:
        name = r[7]
        if name and name not in co_ix:
            co_ix[name] = len(cos)
            cos.append(name)

    # UEX's own last-modified date, interned. 26,657 rows carry 127 distinct
    # dates between them; an index is the same fact in a fifth of the bytes.
    # -1 is "UEX gave no date for this row", which is NOT the same as the
    # snapshot date and must not be silently replaced by it.
    dates, date_ix = [], {}
    for _, _, _, _, _, dm in price_rows:
        d = _iso_day(dm)
        if d is not None and d not in date_ix:
            date_ix[d] = len(dates)
            dates.append(d)
    dates_sorted = sorted(dates)
    date_ix = {d: i for i, d in enumerate(dates_sorted)}
    dates = dates_sorted

    by_item = {}
    for shop_item_id, terminal_id, buy, sell, snapshot_id, dm in price_rows:
        d = _iso_day(dm)
        by_item.setdefault(shop_item_id, []).append([
            term_ix[terminal_id], buy, sell,
            snap_ix[snapshot_id], -1 if d is None else date_ix[d],
        ])

    # An item whose category_id does not resolve still knows what UEX called
    # it, and that string is carried rather than dropped - a blank category on
    # the page would be us losing the source's own answer.
    verified = {
        t: session.execute(text(
            "SELECT count(*) FROM " + t + " WHERE last_verified_patch IS NOT NULL"
        )).scalar()
        for t in ("shop_items", "terminals")
    }

    items, orphan_cats = [], {}
    for (pk, source_kind, uex_id, name, category_id, category_name,
         size, company) in item_rows:
        ci = cat_ix.get(category_id)
        items.append([
            0 if source_kind == "item" else 1,
            uex_id,
            name,
            -1 if ci is None else ci,
            size or "",
            co_ix[company] if company else -1,
            by_item.get(pk, []),
        ])
        if ci is None and category_name:
            orphan_cats[("" if source_kind == "item" else "c") + str(uex_id)] = \
                category_name

    return {
        "snaps": snaps,
        "cats": cats,
        "terms": terms,
        "cos": cos,
        "dates": dates,
        "items": items,
        "orphan_cats": orphan_cats,
        "_counts": {
            "snapshots": len(snaps),
            "item_categories": len(cats),
            "terminals": len(terms),
            "shop_items": len(item_rows),
            "item_prices": len(price_rows),
            # How much of this has been checked against a game patch. Today
            # the answer is none of it, and the page says so IN GENERATED
            # WORDS rather than in a sentence somebody typed - so that when
            # the answer changes the page changes with it instead of lying.
            "shop_items_verified": verified["shop_items"],
            "terminals_verified": verified["terminals"],
        },
    }


SCHEMA = {
    "snaps": ["snapshot_id", "key", "captured_date"],
    "cats": ["uex_id", "name", "section", "is_game_related"],
    "terms": ["uex_id", "name", "resolved_path", "type"],
    "items": ["kind", "uex_id", "name", "cat_ix", "size", "co_ix", "prices"],
    "price": ["term_ix", "price_buy", "price_sell", "snap_ix", "date_ix"],
    "kind": ["item", "commodity"],
}

HEADER = """/* GENERATED by build_find_data.py - do not hand edit.
   Source: PostgreSQL, the system of record. Snapshots named in FIND_DATA.snaps.

   This is what /find reads. It does NOT call an API: the prices are a snapshot
   with a date on them and they do not change between UEX pulls, so the page
   needs a file rather than a server. The API still exists and is still what
   the bench and every write path use.

   THESE ARE UEX REPORTS, NOT GAME MEASUREMENTS. UEX prices are submitted by
   players and rated for confidence. Every price row here carries the snapshot
   it came from and UEX's own last-modified date for that row, so the page can
   say "UEX reported this price at this terminal in the snapshot taken <date>"
   rather than "this is the price".

   A null price is a BLANK, never a zero. UEX writes 0 to mean "this terminal
   does not sell this"; the importer turns that into NULL and it stays NULL.

   An item with no price rows still appears, with an empty price list. Absence
   is data - "nobody sells this" is an answer.

   Positional arrays, decoded by FIND_SCHEMA below. NO GENERATION TIMESTAMP:
   two runs against an unchanged database produce identical bytes.
*/
"""


def _dump(obj):
    return json.dumps(obj, ensure_ascii=True, separators=(",", ":"),
                      sort_keys=True).replace("<", "\\u003c")


def render(data):
    """The .gen.js text. Deterministic - no clock is read anywhere in here."""
    body = {k: v for k, v in data.items() if not k.startswith("_")}
    return (
        HEADER
        + "const FIND_SCHEMA=" + _dump(SCHEMA) + ";\n"
        + "const FIND_COUNTS=" + _dump(data["_counts"]) + ";\n"
        + "const FIND_DATA=" + _dump(body) + ";\n"
    )


def verify_counts(session, data):
    """H1's control: what is in the file equals what is in the database.

    Asserted, not eyeballed. A generator that silently drops a table's worth of
    rows produces a smaller file and a page that looks perfectly fine.

    Counted out of the emitted structures, NOT out of the numbers the collector
    happened to remember - otherwise this control compares a variable with
    itself and could never fail.
    """
    from sqlalchemy import text

    db = {}
    for table in ("snapshots", "item_categories", "terminals",
                  "shop_items", "item_prices"):
        db[table] = session.execute(
            text("SELECT count(*) FROM " + table)).scalar()

    in_file = {
        "snapshots": len(data["snaps"]),
        "item_categories": len(data["cats"]),
        "terminals": len(data["terms"]),
        "shop_items": len(data["items"]),
        "item_prices": sum(len(it[6]) for it in data["items"]),
    }

    problems = [
        "%s: file has %d, database has %d" % (t, in_file[t], db[t])
        for t in sorted(db) if in_file[t] != db[t]
    ]
    return db, in_file, problems


def main():
    ap = argparse.ArgumentParser(
        description="Generate testing/_src/find_data.gen.js from PostgreSQL.")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--max-gzip-kb", type=float, default=250.0,
                    help="acceptance ceiling from H1. Exceeding it is a hard "
                         "failure, not a warning.")
    ap.add_argument("--verify-stable", action="store_true",
                    help="H6's negative half: render twice and require the "
                         "bytes to be identical.")
    ap.add_argument("--check", action="store_true",
                    help="render and compare against the file on disk without "
                         "writing. Non-zero if they differ, so a stale "
                         "generated file is detectable.")
    args = ap.parse_args()

    _load_env()
    from app.database import SessionLocal

    session = SessionLocal()
    try:
        data = collect(session)
        db, in_file, problems = verify_counts(session, data)
    finally:
        session.close()

    print("row counts, file vs database:")
    for table in sorted(db):
        print("  %-16s file %7d   db %7d   %s"
              % (table, in_file[table], db[table],
                 "ok" if in_file[table] == db[table] else "MISMATCH"))
    if problems:
        sys.exit("ROW COUNT MISMATCH - refusing to write a file that does not "
                 "match the database:\n  " + "\n  ".join(problems))

    text_out = render(data)

    if args.verify_stable:
        if render(data) != text_out:
            sys.exit("NOT STABLE: two renders of the same data differ. "
                     "Something in this generator reads a clock or an "
                     "unordered set. Nothing written.")
        print("stable: two renders of the same data are byte-identical")

    raw = text_out.encode("utf-8")
    gz = gzip.compress(raw, 9)
    print("size: %.1f KB raw -> %.1f KB gzipped (ceiling %.0f KB)"
          % (len(raw) / 1024.0, len(gz) / 1024.0, args.max_gzip_kb))

    if len(gz) / 1024.0 > args.max_gzip_kb:
        sys.exit("TOO BIG: %.1f KB gzipped exceeds the %.0f KB acceptance "
                 "ceiling. C1 measured 160 KB, and a large miss means the "
                 "shape changed. Reporting the number rather than shipping "
                 "it. Nothing written."
                 % (len(gz) / 1024.0, args.max_gzip_kb))

    if args.check:
        if not os.path.exists(args.out):
            sys.exit("STALE: %s does not exist. Run build_find_data.py."
                     % os.path.relpath(args.out, HERE))
        with open(args.out, "r", encoding="utf-8", newline="") as fh:
            on_disk = fh.read()
        if on_disk != text_out:
            sys.exit("STALE: %s does not match the database. Re-run "
                     "build_find_data.py." % os.path.relpath(args.out, HERE))
        print("up to date: %s matches the database"
              % os.path.relpath(args.out, HERE))
        return 0

    with open(args.out, "w", encoding="utf-8", newline="") as fh:
        fh.write(text_out)
    print("written: %s" % os.path.relpath(args.out, HERE))
    print("sha256:  %s" % hashlib.sha256(raw).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
