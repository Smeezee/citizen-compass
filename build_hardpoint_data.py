#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_hardpoint_data.py - the ship page's hardpoint panel as ONE generated file.

I1 of docs/ORDER_the-public-site-needs-no-server-and-live-gets-a-deploy-script-2026-08-21.md.

WHY THIS EXISTS
===============
`testing/_deploy/index.html` made exactly one call to a live server: the
Loadout panel asked `CC_API + /api/v1/ships/models/<dir>/hardpoints`. That was
the last thing on the public site that needed Railway to be up, and Railway is
down. The panel's failure text was already honest - "The API did not answer, so
nothing is shown rather than something guessed" - and that text is not the
problem. The problem is that the feature is dead in public for as long as that
server is.

H1 solved this shape once for prices: they stopped needing a server and became
a file. 2,195 hardpoint slots is a smaller fact than 26,657 price rows. So the
site's copy is generated here from PostgreSQL, exactly as build_find_data.py
generates the price data, and the page reads a file.

THE API IS NOT REMOVED, AND THE FALLBACK IS NOT REMOVED
=======================================================
PostgreSQL stays the system of record (R5). The endpoint still exists, still
serves the same JSON, and the page still calls it when the generated file is
absent - including every one of its honest failure sentences. A page whose data
file failed to load behaves EXACTLY as it does today. That is checked, not
hoped: checks/_verify_ship_hardpoint_panel.mjs drives the shipped panel in a
sandbox with no HP_DATA defined, which is precisely the "file is missing" case.

NO GENERATION TIMESTAMP IN THE OUTPUT
=====================================
Same discipline as H6. Nothing here writes "generated at <now>". Two runs
against an unchanged database produce byte-identical output; --verify-stable
proves it on every run, and --check makes a stale file detectable rather than
something somebody has to remember.

THE SHAPE
=========
Positional arrays with the strings interned, for the same reason as the price
file: 2,195 slots with named keys would be mostly repeated key names, and the
few strings that repeat (126 stock item names, 5 kinds, 2 datasets, 10 coverage
reasons) repeat thousands of times between them.

    kinds     the distinct slot kinds - 5 of them across 2,195 slots
    stock     the distinct stock item names - 126 across 2,195 slots
    datasets  the distinct source datasets
    reasons   the distinct coverage reasons - a reason is a sentence, and 235
              models share 10 of them
    models    [model_key, status, reason_ix, slot_count, dataset_ix, slots]
    slot      [port, kind_ix, size, stock_ix, where]

KEYED BY model_key, THE SAME SPELLING RULE THE API USES
========================================================
The endpoint normalises its path segment with
`re.sub(r"[^a-z0-9]+", " ", raw.lower()).strip()`. The page has to apply the
same rule to the same input to get the same answer, so that rule is written
into the generated file's schema as the one the reader must implement, and the
page implements it once. A second, differently-spelled matcher is exactly the
join this project has already paid for elsewhere.

A SIZE IS NULL, NEVER 0. Mount data omits a size for some mounts, and 0 would
render as "size zero" - a value nobody measured. It stays null here and the
page omits the badge entirely, exactly as it does against the API.

A MODEL WITH NO SLOTS STILL GETS AN ENTRY, carrying its status and the build's
own reason. That is the whole point of the coverage table: "we know this hull
and have no mounts for it" and "we have never heard of this hull" are two
different answers and must stay two different answers. Dropping the empty ones
would collapse the first into the second.

Rule 15: every open states its encoding.
"""

import argparse
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "testing", "_src", "hardpoint_data.gen.js")

sys.path.insert(0, HERE)


def _load_env():
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(os.path.join(HERE, ".env"))


def collect(session):
    """Read every row the panel needs, in a deterministic order.

    The ORDER BY clauses are not decoration. Two runs against an unchanged
    database must produce identical bytes, and PostgreSQL makes no promise
    about row order without one. The slot ordering (kind, port) is the SAME
    ordering the API returns, so the file and the fallback render the same
    rows in the same order.
    """
    from sqlalchemy import text

    cov_rows = list(session.execute(text(
        "SELECT model_key, status, reason, slot_count, source_dataset "
        "FROM ship_hardpoint_coverage ORDER BY model_key"
    )))

    slot_rows = list(session.execute(text(
        "SELECT model_key, port, kind, size, stock_item_name, "
        "       detail->>'where' AS where_ "
        "FROM ship_hardpoints ORDER BY model_key, kind, port"
    )))

    kinds, kind_ix = [], {}
    stock, stock_ix = [], {}
    datasets, dataset_ix = [], {}
    reasons, reason_ix = [], {}

    def intern(value, table, index):
        """-1 is "the source states none", which is NOT an empty string."""
        if value is None:
            return -1
        if value not in index:
            index[value] = len(table)
            table.append(value)
        return index[value]

    by_model = {}
    for model_key, port, kind, size, stock_name, where in slot_rows:
        by_model.setdefault(model_key, []).append([
            port,
            intern(kind, kinds, kind_ix),
            size,
            intern(stock_name, stock, stock_ix),
            where,
        ])

    models = []
    for model_key, status, reason, slot_count, source_dataset in cov_rows:
        models.append([
            model_key,
            status,
            intern(reason, reasons, reason_ix),
            slot_count,
            intern(source_dataset, datasets, dataset_ix),
            by_model.get(model_key, []),
        ])

    # A slot whose model_key has no coverage row would be silently dropped by
    # the loop above, and the file would be smaller than the database with
    # nothing to show for it. Counted here so verify_counts() can refuse it.
    orphans = sorted(set(by_model) - {r[0] for r in cov_rows})

    return {
        "kinds": kinds,
        "stock": stock,
        "datasets": datasets,
        "reasons": reasons,
        "models": models,
        "_orphans": orphans,
        "_counts": {
            "models": len(cov_rows),
            "slots": len(slot_rows),
            "kinds": len(kinds),
            "stock_items": len(stock),
            "models_with_slots": sum(1 for m in models if m[5]),
            "models_without_slots": sum(1 for m in models if not m[5]),
        },
    }


SCHEMA = {
    "models": ["model_key", "status", "reason_ix", "slot_count",
               "dataset_ix", "slots"],
    "slot": ["port", "kind_ix", "size", "stock_ix", "where"],
    "status": ["placed", "absent", "refused", "skipped"],
    # The rule the reader must apply to a model folder name to get a model_key.
    # Written here so the page is not the only place it exists in JavaScript.
    "model_key_rule": "lowercase, then every run of characters outside [a-z0-9]"
                      " becomes a single space, then trim",
}

HEADER = """/* GENERATED by build_hardpoint_data.py - do not hand edit.
   Source: PostgreSQL, the system of record - ship_hardpoint_coverage and
   ship_hardpoints.

   This is what the ship page's Loadout panel reads. It was the LAST thing on
   this site that needed a live server: the panel called
   /api/v1/ships/models/<dir>/hardpoints, and that endpoint's host has been
   down. The endpoint still exists and the page still falls back to it when
   this file is absent, with every one of its failure sentences intact.

   A SIZE IS NULL, NEVER 0. Where the mount data states no size, none is shown.
   A 0 would read as "size zero", which is a value nobody measured.

   A MODEL WITH NO SLOTS STILL APPEARS, with its status and the build's own
   reason. "We know this hull and have no mounts for it" and "we have never
   heard of this hull" are different answers and stay different answers.

   Positional arrays, decoded by HP_SCHEMA below. NO GENERATION TIMESTAMP: two
   runs against an unchanged database produce identical bytes.
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
        + "const HP_SCHEMA=" + _dump(SCHEMA) + ";\n"
        + "const HP_COUNTS=" + _dump(data["_counts"]) + ";\n"
        + "const HP_DATA=" + _dump(body) + ";\n"
    )


def verify_counts(session, data):
    """The acceptance line: what is in the file equals what is in the database.

    Asserted, not eyeballed. A generator that silently drops a model's slots
    produces a smaller file and a panel that looks perfectly fine.

    Counted out of the emitted structures, NOT out of the numbers collect()
    happened to remember - otherwise this compares a variable with itself and
    could never fail.
    """
    from sqlalchemy import text

    db = {
        "models": session.execute(
            text("SELECT count(*) FROM ship_hardpoint_coverage")).scalar(),
        "slots": session.execute(
            text("SELECT count(*) FROM ship_hardpoints")).scalar(),
    }
    in_file = {
        "models": len(data["models"]),
        "slots": sum(len(m[5]) for m in data["models"]),
    }

    problems = [
        "%s: file has %d, database has %d" % (t, in_file[t], db[t])
        for t in sorted(db) if in_file[t] != db[t]
    ]

    # Each model's own slot_count is a second, independent statement of the
    # same fact, written by the importer. If it disagrees with the rows we
    # actually carry, one of the two is wrong and neither should ship.
    disagree = [m[0] for m in data["models"] if m[3] != len(m[5])]
    if disagree:
        problems.append(
            "%d model(s) carry a slot_count that disagrees with their own "
            "rows: %s" % (len(disagree), ", ".join(disagree[:5])))

    if data["_orphans"]:
        problems.append(
            "%d model_key(s) have slots but no coverage row, so their slots "
            "are not in the file: %s"
            % (len(data["_orphans"]), ", ".join(data["_orphans"][:5])))

    return db, in_file, problems


def main():
    ap = argparse.ArgumentParser(
        description="Generate testing/_src/hardpoint_data.gen.js from PostgreSQL.")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--max-gzip-kb", type=float, default=60.0,
                    help="acceptance ceiling. Exceeding it is a hard failure, "
                         "not a warning: a large miss means the shape changed, "
                         "which is H1's own lesson.")
    ap.add_argument("--verify-stable", action="store_true",
                    help="render twice and require the bytes to be identical.")
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
        print("  %-10s file %6d   db %6d   %s"
              % (table, in_file[table], db[table],
                 "ok" if in_file[table] == db[table] else "MISMATCH"))
    if problems:
        sys.exit("COUNT MISMATCH - refusing to write a file that does not "
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
                 "ceiling. A large miss means the shape changed - H1's own "
                 "lesson, where the culprit was 5,566 incompressible UUIDs "
                 "nothing used. Reporting the number rather than shipping it. "
                 "Nothing written." % (len(gz) / 1024.0, args.max_gzip_kb))

    if args.check:
        if not os.path.exists(args.out):
            sys.exit("STALE: %s does not exist. Run build_hardpoint_data.py."
                     % os.path.relpath(args.out, HERE))
        with open(args.out, "r", encoding="utf-8", newline="") as fh:
            on_disk = fh.read()
        if on_disk != text_out:
            sys.exit("STALE: %s does not match the database. Re-run "
                     "build_hardpoint_data.py." % os.path.relpath(args.out, HERE))
        print("up to date: %s matches the database"
              % os.path.relpath(args.out, HERE))
        return 0

    with open(args.out, "w", encoding="utf-8", newline="") as fh:
        fh.write(text_out)
    print("written: %s" % os.path.relpath(args.out, HERE))
    print("bytes:   %d" % len(raw))
    return 0


if __name__ == "__main__":
    sys.exit(main())
