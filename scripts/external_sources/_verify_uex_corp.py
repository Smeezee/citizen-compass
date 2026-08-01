"""Rule 12 fixtures for uex_corp.py. No network: requests.get and time.sleep
are stubbed.

A retrieval script whose failure path has never executed is untested no matter
how many times it has succeeded. Every case below MUST fail, and is asserted to.
"""
import importlib.util
import json
import shutil
import sys
import tempfile
import types
from pathlib import Path

import requests as real_requests

spec = importlib.util.spec_from_file_location(
    "uex_corp", str(Path(__file__).resolve().parent / "uex_corp.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

failures = []
_real_monotonic = __import__("time").monotonic
m.time = types.SimpleNamespace(sleep=lambda s: None, monotonic=_real_monotonic)


def check(label, got, expected):
    ok = got == expected
    if not ok:
        failures.append(f"{label}: got {got!r}, expected {expected!r}")
    print("  %-58s %-10s %s" % (label, got, "OK" if ok else "FAIL(want %r)" % (expected,)))


class FakeResp:
    def __init__(self, status=200, ctype="application/json", body=None, headers=None):
        self.status_code = status
        self.headers = {"Content-Type": ctype}
        if headers:
            self.headers.update(headers)
        if body is None:
            body = json.dumps({"status": "ok", "data": [{"uuid": "abc", "name": "Gear"}]})
        self.content = body.encode()
        self.text = body
        self.url = "stub://uex"
    def json(self):
        return json.loads(self.text)


def stub(seq):
    it = iter(seq)
    def _get(*a, **k):
        item = next(it)
        if isinstance(item, Exception):
            raise item
        return item
    return _get


TO = real_requests.exceptions.Timeout("simulated read timeout")
CE = real_requests.exceptions.ConnectionError("simulated connection reset")


def run_fetch(seq):
    m.requests = types.SimpleNamespace(get=stub(seq), exceptions=real_requests.exceptions)
    tmp = Path(tempfile.mkdtemp(prefix="uex_fixture_"))
    try:
        meta = m.fetch("items", "/items/", tmp, "fake-token")
        return meta, sorted(p.name for p in tmp.iterdir())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


print("=" * 80)
print("MUST-FAIL CASES - each writes ZERO files")
print("=" * 80)

print("\n  -- rejected status: HTTP 401 (the credential case) --")
meta, files = run_fetch([FakeResp(401, "application/json", '{"status":"error"}')])
check("files written", files, [])
check("written_to_disk", meta["written_to_disk"], False)
print("     error: %s" % meta["error"])

print("\n  -- rejected status: HTTP 500 x5, ceiling exhausted --")
meta, files = run_fetch([FakeResp(500, "text/html", "<html>err</html>")] * 5)
check("files written", files, [])
check("written_to_disk", meta["written_to_disk"], False)

print("\n  -- unparseable body behind a 200 + JSON content-type --")
meta, files = run_fetch([FakeResp(200, "application/json", "{not valid json")])
check("files written", files, [])
check("written_to_disk", meta["written_to_disk"], False)
print("     error: %s" % meta["error"][:90])

print("\n  -- 200 but HTML content-type --")
meta, files = run_fetch([FakeResp(200, "text/html", "<html>hi</html>")])
check("files written", files, [])
check("written_to_disk", meta["written_to_disk"], False)

print("\n  -- 200, valid JSON, but NOT a UEX envelope (no 'data') --")
meta, files = run_fetch([FakeResp(200, "application/json", '{"status":"ok"}')])
check("files written", files, [])
check("written_to_disk", meta["written_to_disk"], False)
print("     error: %s" % meta["error"])

print("\n  -- 200, valid envelope shape, but status != 'ok' (app-level failure) --")
meta, files = run_fetch([FakeResp(200, "application/json", '{"status":"error","data":null}')])
check("files written", files, [])
check("written_to_disk", meta["written_to_disk"], False)
print("     error: %s" % meta["error"])

print("\n  -- rate limit: 429 x5 with Retry-After, ceiling exhausted --")
meta, files = run_fetch([FakeResp(429, "application/json", '{"status":"error"}',
                                  {"Retry-After": "3"})] * 5)
check("files written", files, [])
check("written_to_disk", meta["written_to_disk"], False)
check("attempts", meta["attempts"], 5)
check("all attempts were 429", all(a["outcome"] == "http_429" for a in meta["attempt_log"]), True)

print("\n  -- five consecutive timeouts: recorded as error, nothing written --")
meta, files = run_fetch([TO] * 5)
check("files written", files, [])
check("written_to_disk", meta["written_to_disk"], False)
check("attempts", meta["attempts"], 5)

print()
print("=" * 80)
print("MUST-SUCCEED CASES - or the checks are simply rejecting everything")
print("=" * 80)

print("\n  -- 200, JSON, valid UEX envelope --")
meta, files = run_fetch([FakeResp()])
check("files written", files, ["items.json"])
check("written_to_disk", meta["written_to_disk"], True)
check("record_count", meta["record_count"], 1)
check("envelope_status", meta["envelope_status"], "ok")
check("sha256 recorded", bool(meta["sha256"]), True)
check("byte_size recorded", meta["byte_size"] > 0, True)
check("elapsed_seconds recorded", meta["elapsed_seconds"] is not None, True)

print("\n  -- 429 then success: honours Retry-After and recovers --")
meta, files = run_fetch([FakeResp(429, "application/json", '{"status":"error"}',
                                  {"Retry-After": "7"}), FakeResp()])
check("files written", files, ["items.json"])
check("attempts", meta["attempts"], 2)
check("waited per Retry-After", meta["attempt_log"][0]["waited_seconds_before_next"], 7)

print("\n  -- timeout then success --")
meta, files = run_fetch([TO, FakeResp()])
check("files written", files, ["items.json"])
check("attempts", meta["attempts"], 2)

print()
print("=" * 80)
print("Retry-After - both RFC 7231 forms, clamped to [0, 60], never raises")
print("=" * 80)
import datetime as _dt
import email.utils as _eu
now = _dt.datetime.now(_dt.timezone.utc)
for label, raw, expect in [
    ("delta-seconds 10", "10", 10),
    ("delta-seconds 9999 -> clamped", "9999", 60),
    ("negative -> floored", "-5", 0),
    ("HTTP-date +5h -> clamped", _eu.format_datetime(now + _dt.timedelta(hours=5)), 60),
    ("HTTP-date in past -> floored", _eu.format_datetime(now - _dt.timedelta(hours=1)), 0),
    ("garbage -> default", "whenever", 5),
    ("missing -> default", None, 5),
    ("empty -> default", "   ", 5),
]:
    check(label, m.parse_retry_after(raw), expect)

print()
print("=" * 80)
print("main() contract")
print("=" * 80)
saved = dict(__import__("os").environ)
try:
    __import__("os").environ.pop("UEX_API_TOKEN", None)
    rc = m.main.__wrapped__(  # type: ignore[attr-defined]
    ) if hasattr(m.main, "__wrapped__") else None
except Exception:
    rc = None
finally:
    __import__("os").environ.clear()
    __import__("os").environ.update(saved)
sys.argv_backup = sys.argv[:]
sys.argv = ["uex_corp.py", tempfile.mkdtemp(prefix="uex_main_")]
import os as _os
_tok = _os.environ.pop("UEX_API_TOKEN", None)
try:
    rc = m.main()
    check("main() returns 1 when UEX_API_TOKEN is absent", rc, 1)
finally:
    if _tok is not None:
        _os.environ["UEX_API_TOKEN"] = _tok
    sys.argv = sys.argv_backup

print()
print("=" * 80)
if failures:
    print("FAILURES (%d):" % len(failures))
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("ALL FIXTURES PASSED - every must-fail case failed, no rejected response reached disk")
