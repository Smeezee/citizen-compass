"""
Git LFS pointer-stub gate for external source snapshots.

THE FAILURE THIS EXISTS TO CATCH
--------------------------------
A clone performed without git-lfs available replaces every LFS-tracked file
with a ~130 byte text stub:

    version https://git-lfs.github.com/spec/v1
    oid sha256:<hash>
    size 128570490

File count is unchanged. Directory structure is unchanged. Nothing is missing.
The snapshot looks complete while its largest dataset has been replaced by a
text file describing itself. For source 1, that is items.json - 128,570,490
bytes of real data, or 130 bytes of nothing.

This is a SILENT SUCCESS in the sense of CLAUDE.md hard rule 12, so this gate is
built to be able to fail and is exercised against a known-bad fixture before it
is trusted. Run --self-test to prove the failure path executes.

USAGE
    python lfs_pointer_scan.py <snapshot-dir> [--expect-large NAME:MIN_BYTES ...]
    python lfs_pointer_scan.py --self-test

Prints a JSON report to stdout. Never modifies anything.

EXIT CODES
    0  no pointer stubs found AND every --expect-large assertion passed
    1  a pointer stub was found, an assertion failed, or a file was unreadable
    2  usage error
"""
import json
import sys
from pathlib import Path

POINTER_SIGNATURE = b"version https://git-lfs.github.com/spec/v1"
# A pointer file is tiny by definition; reading a little more than the signature
# is enough to identify one without loading a 128 MB file into memory.
SNIFF_BYTES = 200

EXIT_OK = 0
EXIT_FAIL = 1
EXIT_USAGE = 2


def is_pointer_stub(path: Path) -> "tuple[bool, str | None]":
    """Return (is_stub, error). Reads only the first SNIFF_BYTES."""
    try:
        with path.open("rb") as f:
            head = f.read(SNIFF_BYTES)
    except OSError as e:
        return False, f"{type(e).__name__}: {e}"
    return head.startswith(POINTER_SIGNATURE), None


def scan(root: Path, expectations: dict) -> dict:
    stubs = []
    unreadable = []
    scanned = 0

    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        scanned += 1
        stub, err = is_pointer_stub(path)
        rel = str(path.relative_to(root)).replace("\\", "/")
        if err:
            unreadable.append({"file": rel, "error": err})
        elif stub:
            # Capture the stub's own contents - it names the size the real file
            # should have been, which is the most useful thing to report.
            try:
                stubs.append({"file": rel, "pointer_contents": path.read_text(
                    encoding="utf-8", errors="replace")[:300]})
            except OSError:
                stubs.append({"file": rel, "pointer_contents": "<unreadable>"})

    # Positive assertions: a named file must exist, exceed a byte floor, and
    # parse as JSON. Stated as assertions with recorded results so a later
    # reader can see the check ran rather than trusting that it did.
    assertions = []
    for name, min_bytes in expectations.items():
        target = root / name
        entry = {
            "file": name,
            "min_bytes_required": min_bytes,
            "exists": target.is_file(),
            "actual_bytes": target.stat().st_size if target.is_file() else None,
            "size_ok": False,
            "parses_as_json": False,
            "passed": False,
        }
        if entry["exists"]:
            entry["size_ok"] = entry["actual_bytes"] >= min_bytes
            try:
                with target.open("r", encoding="utf-8") as f:
                    json.load(f)
                entry["parses_as_json"] = True
            except Exception as e:
                entry["json_error"] = f"{type(e).__name__}: {str(e)[:200]}"
        entry["passed"] = entry["exists"] and entry["size_ok"] and entry["parses_as_json"]
        assertions.append(entry)

    failed_assertions = [a for a in assertions if not a["passed"]]
    return {
        "snapshot": str(root).replace("\\", "/"),
        "files_scanned": scanned,
        "pointer_stubs_found": len(stubs),
        "pointer_stubs": stubs,
        "unreadable_files": unreadable,
        "assertions": assertions,
        "failed_assertions": [a["file"] for a in failed_assertions],
        "verdict": "PASS" if not stubs and not unreadable and not failed_assertions else "FAIL",
    }


def self_test() -> int:
    """Prove the failure path executes. Rule 12: a check that cannot fail is
    not a check."""
    import shutil
    import tempfile

    failures = []

    def check(label, got, expected):
        ok = got == expected
        if not ok:
            failures.append(f"{label}: got {got!r}, expected {expected!r}")
        print("  %-56s %-8s %s" % (label, got, "OK" if ok else "FAIL(want %r)" % (expected,)))

    tmp = Path(tempfile.mkdtemp(prefix="lfs_selftest_"))
    try:
        # --- known-BAD: a real LFS pointer stub, exactly as git writes it ---
        bad = tmp / "bad"
        (bad / "sub").mkdir(parents=True)
        (bad / "items.json").write_text(
            "version https://git-lfs.github.com/spec/v1\n"
            "oid sha256:4d7a214614ab2935c943f9e0ff69d22eadbb8f32b1258daaa5e2ca24d17e2b3d\n"
            "size 128570490\n", encoding="utf-8")
        (bad / "sub" / "ordinary.json").write_text('{"fine": true}', encoding="utf-8")
        print("  -- known-bad fixture: LFS pointer stub in place of items.json --")
        r = scan(bad, {"items.json": 100 * 1024 * 1024})
        check("pointer_stubs_found", r["pointer_stubs_found"], 1)
        check("verdict", r["verdict"], "FAIL")
        check("assertion on items.json passed", r["assertions"][0]["passed"], False)
        check("stub reports intended size", "128570490" in r["pointer_stubs"][0]["pointer_contents"], True)

        # --- known-GOOD: real content, over the floor, valid JSON ---
        good = tmp / "good"
        good.mkdir()
        payload = json.dumps([{"className": "Entity_Datapad_Test", "pad": "x" * 400}] * 300)
        (good / "items.json").write_text(payload, encoding="utf-8")
        (good / "notes.txt").write_text("not json, not a pointer", encoding="utf-8")
        print("  -- known-good fixture: real JSON above the floor --")
        r = scan(good, {"items.json": 1000})
        check("pointer_stubs_found", r["pointer_stubs_found"], 0)
        check("verdict", r["verdict"], "PASS")
        check("assertion passed", r["assertions"][0]["passed"], True)

        # --- a file that is real JSON but UNDER the size floor must still fail ---
        print("  -- size floor is enforced independently of JSON validity --")
        r = scan(good, {"items.json": 100 * 1024 * 1024})
        check("verdict", r["verdict"], "FAIL")
        check("size_ok", r["assertions"][0]["size_ok"], False)
        check("parses_as_json", r["assertions"][0]["parses_as_json"], True)

        # --- a named file that is missing entirely must fail ---
        print("  -- missing expected file fails rather than passing by omission --")
        r = scan(good, {"nonexistent.json": 1})
        check("verdict", r["verdict"], "FAIL")
        check("exists", r["assertions"][0]["exists"], False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if failures:
        print("SELF-TEST FAILURES (%d):" % len(failures))
        for f in failures:
            print("  -", f)
        return EXIT_FAIL
    print("SELF-TEST PASSED - the gate detects pointer stubs and fails on them")
    return EXIT_OK


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__, file=sys.stderr)
        return EXIT_USAGE
    if args[0] == "--self-test":
        return self_test()

    root = Path(args[0])
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return EXIT_USAGE

    expectations = {}
    i = 1
    while i < len(args):
        if args[i] == "--expect-large":
            i += 1
            if i >= len(args) or ":" not in args[i]:
                print("--expect-large needs NAME:MIN_BYTES", file=sys.stderr)
                return EXIT_USAGE
            name, _, min_bytes = args[i].rpartition(":")
            expectations[name] = int(min_bytes)
        else:
            print(f"unknown argument: {args[i]}", file=sys.stderr)
            return EXIT_USAGE
        i += 1

    report = scan(root, expectations)
    print(json.dumps(report, indent=2))
    return EXIT_OK if report["verdict"] == "PASS" else EXIT_FAIL


if __name__ == "__main__":
    sys.exit(main())
