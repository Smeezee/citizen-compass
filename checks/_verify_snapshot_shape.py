"""Rule 12 proof for snapshot_shape_check. No network, no real snapshots.

A checker that has only ever returned PASS has not been shown to work. This
proves it in BOTH directions on synthetic trees:

  - a clean tree is NOT flagged (no false positive)
  - each defect it claims to catch is planted, one at a time, and confirmed
    caught (no silent success)
  - the two defects are proven INDEPENDENT: the loose-file defect and the
    zero-byte defect are separately detectable, because fixing the path join
    alone would leave real zero-byte artifacts in place at correct paths
  - an unreadable/absent root is reported as NOT PERFORMED, never as a pass

Run:  python checks/_verify_snapshot_shape.py
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from checks.source_checks import snapshot_shape_check  # noqa: E402

PASSED = 0
FAILED = []


def check(condition, message):
    global PASSED
    if condition:
        PASSED += 1
        print("  ok   " + message)
    else:
        FAILED.append(message)
        print("  FAIL " + message)


def results(findings, subject_suffix):
    """Every result string for findings whose subject ends with suffix."""
    return [f.result for f in findings if f.subject and f.subject.endswith(subject_suffix)]


def build_clean_tree(root: Path):
    """A structurally correct source: snapshots/ holds directories only, and
    every file in them has content."""
    snaps = root / "data-layer" / "external-sources" / "uexcorp" / "snapshots"
    good = snaps / "20260801T235530Z"
    good.mkdir(parents=True)
    (good / "_pull_summary.json").write_text('{"ok": true}', encoding="utf-8")
    (good / "_pull_stderr.log").write_text("no errors\n", encoding="utf-8")
    (good / "commodities.json").write_text('[{"name": "Agricium"}]', encoding="utf-8")
    return root


def main():
    tmp = Path(tempfile.mkdtemp(prefix="snapshot-shape-"))
    try:
        # ---- 1. clean tree must NOT be flagged --------------------------
        print("\n1. a clean tree is not flagged")
        clean = build_clean_tree(tmp / "clean")
        f = snapshot_shape_check(clean)
        check(results(f, ":loose-files") == ["PASS"], "clean tree: loose-files PASS")
        check(results(f, ":zero-byte") == ["PASS"], "clean tree: zero-byte PASS")
        check(not any(x.result == "DEFECT" for x in f),
              "clean tree produces no DEFECT (no false positive)")

        # ---- 2. NEGATIVE CONTROL: the real 2026-08-06 malformed names ----
        print("\n2. [NEG] loose files directly inside snapshots/ are caught")
        loose = build_clean_tree(tmp / "loose")
        snaps = loose / "data-layer" / "external-sources" / "uexcorp" / "snapshots"
        # byte-for-byte the shape that actually landed: separator and leading
        # underscore both gone, so the artifact is a SIBLING of the snapshot.
        (snaps / "20260806T033217Z.pullstderr.log").write_text("x" * 98, encoding="utf-8")
        f = snapshot_shape_check(loose)
        check(results(f, ":loose-files") == ["DEFECT"],
              "[NEG] a loose file in snapshots/ is a DEFECT")
        check(any("20260806T033217Z.pullstderr.log" in x.details
                  for x in f if x.subject.endswith(":loose-files")),
              "[NEG] the finding NAMES the offending file")
        check(results(f, ":zero-byte") == ["PASS"],
              "[NEG] a non-empty loose file does NOT also trip the zero-byte check")

        # ---- 3. NEGATIVE CONTROL: zero-byte at a CORRECT path ------------
        print("\n3. [NEG] zero-byte artifacts are caught independently")
        empty = build_clean_tree(tmp / "empty")
        snaps = empty / "data-layer" / "external-sources" / "uexcorp" / "snapshots"
        aborted = snaps / "20260801T015346Z.partial.aborted__pagesize50"
        aborted.mkdir()
        # Correct path, correct name, zero bytes. This is the one that survives
        # fixing the path join, which is why it is checked separately.
        (aborted / "_pull_summary.json").write_text("", encoding="utf-8")
        f = snapshot_shape_check(empty)
        check(results(f, ":zero-byte") == ["DEFECT"],
              "[NEG] a zero-byte file at a CORRECT path is still a DEFECT")
        check(results(f, ":loose-files") == ["PASS"],
              "[NEG] the two defects are independent - a correctly-pathed empty "
              "file does not trip the loose-file check")

        # ---- 4. both at once ---------------------------------------------
        print("\n4. both defects together are both reported")
        both = build_clean_tree(tmp / "both")
        snaps = both / "data-layer" / "external-sources" / "uexcorp" / "snapshots"
        (snaps / "20260806T033217Z.pullsummary.json").write_text("", encoding="utf-8")
        f = snapshot_shape_check(both)
        check(results(f, ":loose-files") == ["DEFECT"], "both: loose-file DEFECT raised")
        check(results(f, ":zero-byte") == ["DEFECT"], "both: zero-byte DEFECT raised")

        # ---- 5. absent root is NOT PERFORMED, not a pass ------------------
        print("\n5. a check that cannot run reports LIMITATION, never PASS")
        missing = tmp / "missing"
        missing.mkdir()
        f = snapshot_shape_check(missing)
        check([x.result for x in f] == ["LIMITATION"],
              "absent external-sources root -> LIMITATION")
        check(not any(x.result == "PASS" for x in f),
              "[NEG] an unperformed check never reports PASS")

        # a source dir with no snapshots/ at all
        bare = tmp / "bare"
        (bare / "data-layer" / "external-sources" / "uexcorp").mkdir(parents=True)
        f = snapshot_shape_check(bare)
        check([x.result for x in f] == ["LIMITATION"],
              "external-sources with no */snapshots -> LIMITATION")

        # ---- 6. the cap degrades to LIMITATION, never to a silent pass ----
        print("\n6. the file cap reports partial coverage honestly")
        capped = build_clean_tree(tmp / "capped")
        os.environ["CC_SNAPSHOT_SHAPE_MAX_FILES"] = "1"
        try:
            f = snapshot_shape_check(capped)
            check(any(x.result == "LIMITATION" and "PARTIAL" in x.details for x in f),
                  "hitting the cap reports PARTIAL coverage as a LIMITATION")
        finally:
            del os.environ["CC_SNAPSHOT_SHAPE_MAX_FILES"]

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n{PASSED} passed, {len(FAILED)} failed")
    if FAILED:
        for m in FAILED:
            print("  FAILED: " + m)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
