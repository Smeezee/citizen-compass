"""
Rule 12 proof for B5's stated control, at the IMPORTER level.

RULE16: UNPROVEN - it imports import_uex_items_all and drives it, so the refusal
being judged is produced by the code being judged. The independent half is
real: the row counts are read back out of the database with SQL, not from
anything the importer reports, so an importer that claimed success having
stored nothing is caught.

§B5: "a malformed category file fails loudly, and does not silently import
zero rows and report success."

checks/_verify_shop_importers.py already proves the source guard in isolation.
This proves the thing that actually matters, which is not the same claim: that
`import_uex_items_all.py` as a whole refuses to run, exits non-zero, and
LEAVES THE DATABASE UNTOUCHED when one of its hundred files is broken.

Those come apart easily. A guard can raise correctly while the importer around
it catches the exception, logs a warning, imports the other 99 files and exits
0 - which is precisely the "silently import zero rows and report success"
failure, just moved one level up.

THE FOUR CASES
--------------
  1. one malformed file among good ones  -> non-zero exit, NOTHING imported
  2. every file empty (data: null)       -> non-zero exit. Not a catalogue
     with no items in it; a pull that did not land. Each individual file is
     perfectly valid, so the per-file guard cannot catch this one.
  3. no category files at all            -> non-zero exit
  4. a normal directory                  -> exit 0 and rows imported, or
     every assertion above is satisfied by an importer that always fails

Runs against throwaway snapshot directories in a temp folder, with the
importer's SNAPSHOT_ROOT redirected there. NOTHING is written to the real
database - case 4 runs with --dry-run and proves the positive by reading the
insert count the importer REPORTS. A real run there would put two fake
liveries into shop_items permanently, because this project never deletes and
blocks deletion at the engine, and a control that pollutes the data it checks
is worse than no control.

Run: venv/Scripts/python.exe checks/_verify_items_import_b5.py
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import import_uex_items_all as importer  # noqa: E402
from app.database import engine  # noqa: E402
from sqlalchemy import text  # noqa: E402

GOOD_ROWS = [
    {"id": 9900001, "id_category": 20, "name": "Control Test Livery A",
     "uuid": "cc-control-test-a", "category": "Liveries", "section": "Liveries",
     "slug": "control-a", "size": "", "date_modified": 1700000000},
    {"id": 9900002, "id_category": 20, "name": "Control Test Livery B",
     "uuid": None, "category": "Liveries", "section": "Liveries",
     "slug": "control-b", "size": "", "date_modified": 1700000000},
]


def envelope(rows):
    return json.dumps({"status": "ok", "http_code": 200, "data": rows,
                       "message": ""})


def build(tmp, name, files):
    """A throwaway snapshot directory. `files` is {category_id: contents}."""
    directory = tmp / name
    directory.mkdir(parents=True, exist_ok=True)
    for category, contents in files.items():
        (directory / f"items_category_{category}.json").write_text(
            contents, encoding="utf-8"
        )
    return directory


def item_count():
    with engine.connect() as conn:
        return conn.execute(text("select count(*) from shop_items")).scalar()


def run(snapshot_name, extra_args=()):
    """Run the importer's main() against a snapshot name, capturing its exit."""
    argv = sys.argv
    sys.argv = ["import_uex_items_all.py", "--snapshot", snapshot_name,
                *extra_args]
    try:
        return importer.main()
    except SystemExit as exc:
        # load_envelope() raises SystemExit for a malformed file. That IS the
        # loud failure - it is recorded as a non-zero outcome, not as a crash.
        return exc.code if isinstance(exc.code, int) else 1
    finally:
        sys.argv = argv


def main():
    passed, failed = 0, []

    def record(ok, label, detail=""):
        nonlocal passed
        if ok:
            passed += 1
            print(f"  ok   {label}")
        else:
            failed.append(f"{label} {detail}".strip())
            print(f"  FAIL {label} {detail}")

    tmp = Path(tempfile.mkdtemp(prefix="cc_b5_"))
    real_root = importer.SNAPSHOT_ROOT
    importer.SNAPSHOT_ROOT = tmp

    try:
        baseline = item_count()
        print(f"--- baseline: shop_items holds {baseline} rows ---\n")

        # -- 1. one malformed file among good ones --------------------------
        print("--- KNOWN-BAD: one malformed file among good ones ---")
        build(tmp, "malformed", {
            20: envelope(GOOD_ROWS),
            32: '{"status":"ok","data":[{"id":1}',      # truncated
            33: envelope(GOOD_ROWS),
        })
        code = run("malformed")
        after = item_count()
        record(code != 0, f"exits non-zero (got {code})")
        record(after == baseline,
               f"imported NOTHING ({after} rows, baseline {baseline})",
               "IT IMPORTED THE OTHER FILES ANYWAY")

        # -- 2. every file empty --------------------------------------------
        print("\n--- KNOWN-BAD: every category file empty (a pull that did "
              "not land) ---")
        build(tmp, "allempty", {
            20: envelope(None), 32: envelope(None), 33: envelope([]),
        })
        code = run("allempty")
        after = item_count()
        record(code != 0,
               f"exits non-zero (got {code})",
               "a 100%-empty pull reported SUCCESS")
        record(after == baseline, f"imported nothing ({after} rows)")

        # -- 3. no category files at all ------------------------------------
        print("\n--- KNOWN-BAD: no category files at all ---")
        (tmp / "nofiles").mkdir(parents=True, exist_ok=True)
        code = run("nofiles")
        record(code != 0, f"exits non-zero (got {code})")

        # -- 3b. a snapshot directory that does not exist -------------------
        code = run("no_such_snapshot_directory")
        record(code != 0, f"missing directory exits non-zero (got {code})")

        # -- 4. THE POSITIVE CASE -------------------------------------------
        # Without this, every assertion above is satisfied by an importer that
        # refuses everything unconditionally - which would pass three checks
        # and be completely broken.
        #
        # Done with --dry-run ONLY, deliberately. A real run here would write
        # two fake liveries into the production shop_items table, and this
        # project never deletes (rule 1) and blocks deletion at the engine
        # (app/preservation.py) - so those rows would be permanent, and a
        # control that permanently pollutes the data it checks is worse than
        # no control. The dry run still proves what is needed, because it
        # reports the insert count it WOULD have made.
        print("\n--- POSITIVE: a good directory must import, and say so ---")
        build(tmp, "good", {20: envelope(GOOD_ROWS)})

        reported = []
        real_log = importer.log
        importer.log = lambda message: (reported.append(message),
                                        real_log(message))[1]
        try:
            code = run("good", extra_args=("--dry-run",))
        finally:
            importer.log = real_log

        after = item_count()
        record(code == 0, f"a valid snapshot exits 0 (got {code})")
        record(after == baseline,
               f"--dry-run wrote nothing ({after} rows, baseline {baseline})",
               "THE DRY RUN WROTE TO THE DATABASE")

        # "exit 0" must be earned by finding the rows, not by doing nothing.
        insert_line = next(
            (m for m in reported if m.startswith("inserted ")), ""
        )
        record(insert_line.startswith(f"inserted {len(GOOD_ROWS)},"),
               f"and it reported the work it would do: {insert_line!r}",
               f"expected 'inserted {len(GOOD_ROWS)}, ...'")
        record(any("2 source items" in m for m in reported),
               "it read both source rows")

    finally:
        importer.SNAPSHOT_ROOT = real_root

    print("\n" + "=" * 62)
    print(f"(fixtures under {tmp})")
    if failed:
        print(f"FAILED {len(failed)} of {passed + len(failed)}:")
        for x in failed:
            print("  -", x)
        return 1
    print(f"All {passed} assertions passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
