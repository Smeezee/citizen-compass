"""
Flush queued checker findings from the fallback log into pipeline_check_results.

WHY THIS EXISTS
---------------
checks/framework.py's write_findings() degrades gracefully: with no database
connection it appends findings to logs/pipeline_check_results_fallback.jsonl
instead of losing them, and its docstring says to run
`python checks_flush_fallback.py` once real DB access exists.

That script was never written. So from 2026-07-30 onward every finding the
auditors produced went into a log file with no path into the table - 874 of
them, across seven runs, that nobody has read. The system worked and was
talking to an empty room.

WHAT IT DOES
------------
Reads the JSONL, inserts each finding into pipeline_check_results, and does NOT
double-insert on a second run. Dedupe is on the full tuple
(check_name, subject, result, details, source_process, checked_at) - matching
what framework.py writes - so re-running is safe and a partially-completed load
can simply be re-run.

On success the log is moved aside with a timestamp rather than deleted. Nothing
here is worth losing to a partial load, and CLAUDE.md rule 1 forbids deleting in
this repo regardless.

FINDINGS-ONLY
-------------
This script INSERTs into pipeline_check_results and moves one log file. It
touches no other table and modifies no data anywhere, per
ARCHITECTURE_DECISIONS.md section 4 (LOCKED).

USAGE
    python checks_flush_fallback.py              # flush, then archive the log
    python checks_flush_fallback.py --dry-run    # report what would happen
    python checks_flush_fallback.py --keep-log   # flush but leave the log
    python checks_flush_fallback.py --self-test  # rule 12: prove it on fixtures

EXIT CODES
    0  flushed cleanly (or nothing to do)
    1  a finding could not be loaded, or the load failed
    2  usage error
"""
import argparse
import datetime
import json
import os
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
FALLBACK_LOG = REPO_ROOT / "logs" / "pipeline_check_results_fallback.jsonl"
ARCHIVE_DIR = REPO_ROOT / "logs" / "flushed"

REQUIRED_FIELDS = ("check_name", "subject", "result", "details", "source_process", "checked_at")
VALID_RESULTS = ("DEFECT", "WARNING", "LIMITATION", "PASS")

EXIT_OK = 0
EXIT_FAIL = 1
EXIT_USAGE = 2


def load_findings(path: Path):
    """Parse the JSONL. Returns (findings, malformed).

    A malformed line is reported, never silently skipped - a flush that quietly
    drops findings is the same class of failure as a gate that cannot fail.
    """
    findings, malformed = [], []
    if not path.is_file():
        return findings, malformed
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except Exception as e:
            malformed.append({"line": lineno, "error": f"{type(e).__name__}: {e}", "raw": line[:120]})
            continue
        missing = [f for f in REQUIRED_FIELDS if f not in row]
        if missing:
            malformed.append({"line": lineno, "error": f"missing fields: {missing}", "raw": line[:120]})
            continue
        if row["result"] not in VALID_RESULTS:
            malformed.append({"line": lineno, "error": f"invalid result {row['result']!r}", "raw": line[:120]})
            continue
        findings.append(row)
    return findings, malformed


def _key(row):
    """The dedupe tuple: the full finding as framework.py wrote it."""
    return tuple(row[f] for f in REQUIRED_FIELDS)


def existing_keys(conn):
    """Every finding already in the table, as comparable tuples."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT check_name, subject, result, details, source_process, checked_at "
            "FROM pipeline_check_results"
        )
        rows = cur.fetchall()
    out = set()
    for r in rows:
        checked_at = r[5].isoformat() if hasattr(r[5], "isoformat") else str(r[5])
        out.add((r[0], r[1], r[2], r[3], r[4], checked_at))
    return out


def flush(conn, findings, dry_run=False):
    """Insert findings not already present. Returns (inserted, skipped)."""
    have = existing_keys(conn)
    to_insert = []
    skipped = 0
    seen_this_run = set()
    for row in findings:
        k = _key(row)
        if k in have or k in seen_this_run:
            skipped += 1
            continue
        seen_this_run.add(k)
        to_insert.append(row)

    if dry_run or not to_insert:
        return len(to_insert), skipped

    with conn.cursor() as cur:
        for row in to_insert:
            cur.execute(
                "INSERT INTO pipeline_check_results "
                "(check_name, subject, result, details, source_process, checked_at) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (row["check_name"], row["subject"], row["result"],
                 row["details"], row["source_process"], row["checked_at"]),
            )
    conn.commit()
    return len(to_insert), skipped


def archive_log(path: Path) -> Path:
    """Move the log aside with a timestamp. Never deletes (rule 1)."""
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    dest = ARCHIVE_DIR / f"pipeline_check_results_fallback_{stamp}.jsonl"
    shutil.move(str(path), str(dest))
    return dest


def summarise(findings):
    counts = {}
    for r in findings:
        counts[r["result"]] = counts.get(r["result"], 0) + 1
    return counts


# --------------------------------------------------------------------------
# Rule 12: prove it against known-bad input before trusting it.
# --------------------------------------------------------------------------
def self_test() -> int:
    import sqlite3
    import tempfile

    failures = []

    def check(label, got, expected):
        ok = got == expected
        if not ok:
            failures.append(f"{label}: got {got!r}, expected {expected!r}")
        print("  %-58s %-8s %s" % (label, got, "OK" if ok else "FAIL(want %r)" % (expected,)))

    class FakeConn:
        """Minimal psycopg2-shaped wrapper over sqlite3, so the real flush()
        and existing_keys() code paths execute rather than being simulated."""
        def __init__(self):
            self.db = sqlite3.connect(":memory:")
            self.db.execute(
                "CREATE TABLE pipeline_check_results ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, check_name TEXT, subject TEXT, "
                "result TEXT, details TEXT, source_process TEXT, checked_at TEXT)")

        def cursor(self):
            outer = self

            class Cur:
                def __enter__(self_inner):
                    self_inner.c = outer.db.cursor()
                    return self_inner
                def __exit__(self_inner, *a):
                    self_inner.c.close()
                def execute(self_inner, sql, params=None):
                    self_inner.c.execute(sql.replace("%s", "?"), params or ())
                def fetchall(self_inner):
                    return self_inner.c.fetchall()
            return Cur()

        def commit(self):
            self.db.commit()

        def count(self):
            return self.db.execute("SELECT count(*) FROM pipeline_check_results").fetchone()[0]

    tmp = Path(tempfile.mkdtemp(prefix="flush_selftest_"))
    try:
        good = {
            "check_name": "demo", "subject": "thing", "result": "PASS",
            "details": "fine", "source_process": "test", "checked_at": "2026-08-02T00:00:00",
        }
        second = dict(good, subject="other", result="DEFECT", details="broken")

        # --- malformed input must be REPORTED, never silently dropped ---
        p = tmp / "bad.jsonl"
        p.write_text(
            json.dumps(good) + "\n"
            + "{not json\n"
            + json.dumps({"check_name": "x"}) + "\n"
            + json.dumps(dict(good, result="BOGUS")) + "\n"
            + json.dumps(second) + "\n",
            encoding="utf-8")
        findings, malformed = load_findings(p)
        print("  -- known-bad fixture: unparseable line, missing fields, invalid result --")
        check("valid findings parsed", len(findings), 2)
        check("malformed lines reported", len(malformed), 3)
        check("malformed are not silently dropped", all("error" in m for m in malformed), True)

        # --- IDEMPOTENCE: the claim the work order says must be tested ---
        print("  -- idempotence: run twice, row count must not change --")
        conn = FakeConn()
        ins1, skip1 = flush(conn, findings)
        after1 = conn.count()
        ins2, skip2 = flush(conn, findings)
        after2 = conn.count()
        check("first run inserted", ins1, 2)
        check("row count after first run", after1, 2)
        check("second run inserted", ins2, 0)
        check("second run skipped as duplicates", skip2, 2)
        check("row count UNCHANGED after second run", after2, 2)

        # --- duplicates WITHIN one file are also collapsed ---
        print("  -- duplicate lines within a single file --")
        p2 = tmp / "dupes.jsonl"
        p2.write_text((json.dumps(good) + "\n") * 3, encoding="utf-8")
        f2, _ = load_findings(p2)
        conn2 = FakeConn()
        ins, skipped = flush(conn2, f2)
        check("3 identical lines insert once", ins, 1)
        check("row count", conn2.count(), 1)

        # --- a genuinely different finding still inserts (not over-dedup) ---
        print("  -- a different finding must still insert --")
        third = dict(good, details="a different detail")
        ins3, _ = flush(conn2, [third])
        check("distinct finding inserted", ins3, 1)
        check("row count", conn2.count(), 2)

        # --- dry run must not write ---
        print("  -- dry run writes nothing --")
        conn3 = FakeConn()
        would, _ = flush(conn3, findings, dry_run=True)
        check("dry run reports what it would insert", would, 2)
        check("dry run inserted nothing", conn3.count(), 0)

        # --- archiving moves, never deletes ---
        print("  -- archive moves the log, does not delete it --")
        p3 = tmp / "tomove.jsonl"
        p3.write_text(json.dumps(good) + "\n", encoding="utf-8")
        global ARCHIVE_DIR
        saved = ARCHIVE_DIR
        ARCHIVE_DIR = tmp / "flushed"
        try:
            dest = archive_log(p3)
            check("original gone from source path", p3.exists(), False)
            check("archived copy exists", dest.exists(), True)
            check("archived content preserved", json.loads(dest.read_text(encoding="utf-8"))["check_name"], "demo")
        finally:
            ARCHIVE_DIR = saved

        # --- missing log is a no-op, not a crash ---
        print("  -- absent log is a clean no-op --")
        f4, m4 = load_findings(tmp / "does_not_exist.jsonl")
        check("no findings", len(f4), 0)
        check("no malformed", len(m4), 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if failures:
        print("SELF-TEST FAILURES (%d):" % len(failures))
        for f in failures:
            print("  -", f)
        return EXIT_FAIL
    print("SELF-TEST PASSED - idempotent, malformed input reported, dry run inert, archive preserves")
    return EXIT_OK


def main() -> int:
    ap = argparse.ArgumentParser(description="Flush queued checker findings into pipeline_check_results.")
    ap.add_argument("--dry-run", action="store_true", help="report what would be inserted, write nothing")
    ap.add_argument("--keep-log", action="store_true", help="do not archive the log after a successful flush")
    ap.add_argument("--self-test", action="store_true", help="prove the script against known-bad input (rule 12)")
    ap.add_argument("--log", default=str(FALLBACK_LOG), help="path to the fallback log")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    log_path = Path(args.log)
    findings, malformed = load_findings(log_path)

    if not log_path.is_file():
        print(f"no fallback log at {log_path} - nothing to flush")
        return EXIT_OK

    print(f"fallback log: {log_path}")
    print(f"  findings parsed:  {len(findings)}")
    print(f"  malformed lines:  {len(malformed)}")
    for m in malformed[:10]:
        print(f"    line {m['line']}: {m['error']}")
    if findings:
        print(f"  by result:        {summarise(findings)}")

    if malformed:
        # Fail closed. A flush that quietly drops findings is the same failure
        # this whole layer exists to catch.
        print("\nREFUSING TO FLUSH: malformed lines present. Nothing was inserted, "
              "nothing was archived. Fix or remove those lines and re-run.", file=sys.stderr)
        return EXIT_FAIL

    if not findings:
        print("nothing to flush")
        return EXIT_OK

    try:
        import psycopg2
        from dotenv import load_dotenv
        load_dotenv(REPO_ROOT / ".env")
        url = os.environ.get("DATABASE_URL") or os.environ.get("RAILWAY_DATABASE_URL")
        if not url:
            print("DATABASE_URL is not set - cannot flush", file=sys.stderr)
            return EXIT_FAIL
        conn = psycopg2.connect(url.replace("postgresql+psycopg2://", "postgresql://"))
    except Exception as e:
        print(f"could not connect to the database: {type(e).__name__}: {e}", file=sys.stderr)
        print("findings remain queued in the log - nothing was lost", file=sys.stderr)
        return EXIT_FAIL

    try:
        inserted, skipped = flush(conn, findings, dry_run=args.dry_run)
        print()
        print(f"  inserted: {inserted}")
        print(f"  skipped (already present): {skipped}")
        if args.dry_run:
            print("  DRY RUN - nothing was written and the log was not archived")
            return EXIT_OK
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM pipeline_check_results")
            total = cur.fetchone()[0]
        print(f"  pipeline_check_results now holds: {total}")
    finally:
        conn.close()

    if not args.keep_log:
        dest = archive_log(log_path)
        print(f"  log moved aside (not deleted) -> {dest}")

    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
