"""
Rule 12 proof for the shop-layer importers' source guard.

RULE16: UNPROVEN - it imports load_envelope from the importer and drives that
function, so a guard that misreads a broken envelope misreads it here
too. The independent half is the INPUT: the snapshots are built in this
file, deliberately malformed in ways a real one never would be, and the
guard has to refuse them. A refusal that has been observed is worth more
than one that has only been read.

WHAT THIS PROVES
----------------
Every shop-layer importer reads UEX files through one function,
`load_envelope()`. That function is the only thing standing between a broken
snapshot and an import that reports success having stored nothing - which is
the failure §B5 names: "a malformed category file fails loudly, and does not
silently import zero rows and report success."

That guard is worth nothing until it has been watched refusing something. So
this feeds it, one at a time:

  * a file that does not exist
  * a file that is not JSON at all
  * a file that is JSON but not a UEX envelope
  * a file whose "data" is a dict rather than a list
  * a file whose "data" is a string

...and requires each one to fail LOUDLY (SystemExit), not to return an empty
list.

AND THE HALF THAT IS EASY TO GET WRONG
--------------------------------------
`{"status":"ok","http_code":200,"data":null}` must NOT fail. Forty-four of the
hundred category files in 20260801T235530Z look exactly like that, and they
are genuinely empty categories rather than broken pulls - confirmed against
the snapshot's own manifest, where all 100 entries carry HTTP 200 and envelope
status "ok". A guard that rejected those would block more than a third of the
catalogue import on data that is perfectly fine.

So the two cases sit next to each other deliberately: "empty" and "broken"
must be distinguished, and a guard that cannot tell them apart is the wrong
guard in whichever direction it errs.

Everything runs against throwaway files in a temp directory. Nothing is
planted in the repo and no database is touched.

Run: venv/Scripts/python.exe checks/_verify_shop_importers.py
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from import_uex_terminals import load_envelope  # noqa: E402

# (label, file contents or None to not create the file, must_fail)
CASES = [
    # ---- MUST fail loudly -------------------------------------------------
    ("a file that does not exist", None, True),
    ("a file that is not JSON at all", "this is not json {{{", True),
    ("valid JSON, but a bare list rather than an envelope",
     json.dumps([{"id": 1}]), True),
    ("valid JSON object with no 'data' key",
     json.dumps({"status": "ok", "http_code": 200}), True),
    ("'data' is a dict rather than a list",
     json.dumps({"status": "ok", "data": {"1": "a"}}), True),
    ("'data' is a string",
     json.dumps({"status": "ok", "data": "nope"}), True),
    ("'data' is a number",
     json.dumps({"status": "ok", "data": 42}), True),
    ("an empty file", "", True),
    ("truncated JSON", '{"status":"ok","data":[{"id":1}', True),

    # ---- MUST NOT fail ----------------------------------------------------
    ("a normal envelope with rows",
     json.dumps({"status": "ok", "http_code": 200,
                 "data": [{"id": 1}, {"id": 2}], "message": ""}), False),
    # The 44-file case. Genuinely empty, not broken.
    ("data: null - HTTP 200, envelope ok, no rows (44 real files look like this)",
     json.dumps({"status": "ok", "http_code": 200, "data": None,
                 "message": ""}), False),
    ("data: [] - an explicitly empty list",
     json.dumps({"status": "ok", "data": []}), False),
]


def main():
    passed, failed = 0, []
    workdir = Path(tempfile.mkdtemp(prefix="cc_shop_src_"))

    def record(ok, label, detail=""):
        nonlocal passed
        if ok:
            passed += 1
            print(f"  ok   {label}")
        else:
            failed.append(f"{label} {detail}".strip())
            print(f"  FAIL {label} {detail}")

    print("--- the source guard, fed one broken file at a time ---")
    for index, (label, contents, must_fail) in enumerate(CASES):
        path = workdir / f"case_{index}.json"
        if contents is not None:
            path.write_text(contents, encoding="utf-8")

        try:
            rows = load_envelope(path)
            raised = None
        except SystemExit as exc:
            rows, raised = None, str(exc)
        except Exception as exc:  # noqa: BLE001
            # Any other exception is still a failure to load, but it is NOT
            # the loud, explained failure the guard promises. Distinguishing
            # them matters: a bare KeyError tells whoever runs the pipeline
            # nothing about which file is broken or how.
            rows, raised = None, f"UNEXPLAINED {type(exc).__name__}: {exc}"

        if must_fail:
            explained = raised is not None and raised.startswith("MALFORMED SOURCE")
            record(explained, f"REFUSED: {label}",
                   f"got rows={rows!r} raised={raised!r}")
        else:
            record(raised is None and isinstance(rows, list),
                   f"ACCEPTED: {label} -> {len(rows) if rows is not None else None} rows",
                   f"raised={raised!r}")

    # ---------------------------------------------------------------
    print("\n--- empty and broken must not be confused for each other ---")
    # Stated as its own assertion because it is the actual risk: a guard that
    # is merely strict blocks 44 legitimate files, and a guard that is merely
    # permissive lets a truncated file import as zero rows and pass.
    empty = workdir / "empty_ok.json"
    empty.write_text(json.dumps({"status": "ok", "data": None}), encoding="utf-8")
    broken = workdir / "broken.json"
    broken.write_text('{"status":"ok","data":[{"id":1}', encoding="utf-8")

    try:
        empty_rows = load_envelope(empty)
        empty_ok = empty_rows == []
    except SystemExit:
        empty_ok = False
    try:
        load_envelope(broken)
        broken_ok = False
    except SystemExit:
        broken_ok = True

    record(empty_ok, "a genuinely empty endpoint returns [] and does not raise")
    record(broken_ok, "a truncated file raises rather than returning []")
    record(empty_ok and broken_ok,
           "the two are distinguished - the guard is neither blanket-strict "
           "nor blanket-permissive")

    print("\n" + "=" * 62)
    print(f"(fixtures under {workdir} - left in place, this project does not "
          f"delete)")
    if failed:
        print(f"FAILED {len(failed)} of {passed + len(failed)}:")
        for x in failed:
            print("  -", x)
        return 1
    print(f"All {passed} assertions passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
