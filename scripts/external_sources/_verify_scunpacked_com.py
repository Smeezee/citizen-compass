"""Offline verification for scunpacked_com.py after the CC-07 fixes.

No network: requests.get and time.sleep are stubbed. Proves the five
behaviours the fix is supposed to guarantee, plus Retry-After parsing.
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
    "scunpacked_com", str(Path(__file__).resolve().parent / "scunpacked_com.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

failures = []
slept = []
# sleep is stubbed so backoffs do not actually wait; monotonic is passed through
# to the real clock because the script now records per-attempt elapsed time.
_real_monotonic = __import__("time").monotonic
m.time = types.SimpleNamespace(sleep=lambda s: slept.append(s), monotonic=_real_monotonic)


def check(label, got, expected):
    ok = got == expected
    if not ok:
        failures.append(f"{label}: got {got!r}, expected {expected!r}")
    print("    %-52s %-14s %s" % (label, repr(got), "OK" if ok else "*** FAIL (want %r)" % (expected,)))


class FakeResp:
    def __init__(self, status=200, ctype="application/json", body=None, headers=None):
        self.status_code = status
        self.headers = {"Content-Type": ctype}
        if headers:
            self.headers.update(headers)
        body = '{"ships": []}' if body is None else body
        self.content = body.encode()
        self.text = body
        self.url = "stub://scunpacked"
        self.history = []


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
    tmp = Path(tempfile.mkdtemp(prefix="scunpacked_fixture_"))
    try:
        meta = m.fetch("ships", "/api/v2/ships.json", tmp)
        files = sorted(p.name for p in tmp.iterdir())
        return meta, files
    finally:
        shutil.rmtree(tmp)


print("=" * 84)
print("CONSTANTS")
print("=" * 84)
check("REQUEST_TIMEOUT_SECONDS", m.REQUEST_TIMEOUT_SECONDS, 180)
check("MAX_RETRY_AFTER_SECONDS", m.MAX_RETRY_AFTER_SECONDS, 60)

print()
print("=" * 84)
print("FIX 1 - write-before-status: a rejected response must write ZERO files")
print("=" * 84)

print("\n  -- HTML 500 (the classic error-page-as-data case) --")
meta, files = run_fetch([FakeResp(500, "text/html; charset=utf-8",
                                  "<!DOCTYPE html><html>Server Error</html>")] * 5)
check("files on disk", files, [])
check("written_to_disk", meta["written_to_disk"], False)
check("file_path", meta["file_path"], None)
check("first 200 chars kept", meta["rejected_body_first_200_chars"].startswith("<!DOCTYPE html>"), True)
print("    error: %s" % meta["error"])

print("\n  -- HTTP 200, application/json, unparseable body --")
meta, files = run_fetch([FakeResp(200, "application/json", "{not valid json")])
check("files on disk", files, [])
check("written_to_disk", meta["written_to_disk"], False)
print("    error: %s" % meta["error"])

print("\n  -- HTTP 200 but Content-Type text/html --")
meta, files = run_fetch([FakeResp(200, "text/html", "<html>hi</html>")])
check("files on disk", files, [])
check("written_to_disk", meta["written_to_disk"], False)
print("    error: %s" % meta["error"])

print("\n  -- HTTP 200, application/json, valid body (must WRITE) --")
meta, files = run_fetch([FakeResp()])
check("files on disk", files, ["ships.json"])
check("written_to_disk", meta["written_to_disk"], True)
check("byte_size recorded", meta["byte_size"], 13)
check("sha256 recorded", bool(meta["sha256"]), True)
check("attempts", meta["attempts"], 1)

print()
print("=" * 84)
print("FIX 2 - retry and timeout")
print("=" * 84)

print("\n  -- timeout on attempt 1, then success: retries, does not crash --")
meta, files = run_fetch([TO, FakeResp()])
check("files on disk", files, ["ships.json"])
check("attempts", meta["attempts"], 2)
check("outcomes", [a["outcome"] for a in meta["attempt_log"]], ["exception", "response"])

print("\n  -- timeout + connection error, then success: 3 attempts --")
meta, files = run_fetch([TO, CE, FakeResp()])
check("attempts", meta["attempts"], 3)
check("exception types", [a.get("exception_type") for a in meta["attempt_log"]],
      ["Timeout", "ConnectionError", None])

print("\n  -- five consecutive timeouts: ceiling exhausts and RAISES (no infinite loop) --")
m.requests = types.SimpleNamespace(get=stub([TO] * 5), exceptions=real_requests.exceptions)
try:
    m.get_with_retry("stub://x")
    check("raised", False, True)
except real_requests.exceptions.Timeout as e:
    check("raised Timeout", True, True)
    check("attempts recorded", len(getattr(e, "attempts_log", [])), 5)

print("\n  -- fetch() surfaces an exhausted ceiling as an error, writes nothing --")
meta, files = run_fetch([TO] * 5)
check("files on disk", files, [])
check("written_to_disk", meta["written_to_disk"], False)
check("attempts", meta["attempts"], 5)
print("    error: %s" % meta["error"][:88])

print("\n  -- 429 with Retry-After is honoured, then success --")
meta, files = run_fetch([FakeResp(429, "application/json", "{}", {"Retry-After": "7"}), FakeResp()])
check("files on disk", files, ["ships.json"])
check("attempts", meta["attempts"], 2)
check("first outcome", meta["attempt_log"][0]["outcome"], "http_429")
check("waited", meta["attempt_log"][0]["waited_seconds_before_next"], 7)

print()
print("=" * 84)
print("Retry-After parsing - both forms, clamped to [0, 60], never raises")
print("=" * 84)
import datetime as _dt
import email.utils as _eu
now = _dt.datetime.now(_dt.timezone.utc)
cases = [
    ("delta-seconds 10", "10", 10),
    ("delta-seconds 9999 -> clamped", "9999", 60),
    ("negative -> floored", "-5", 0),
    ("HTTP-date +5h -> clamped", _eu.format_datetime(now + _dt.timedelta(hours=5)), 60),
    ("HTTP-date in past -> floored", _eu.format_datetime(now - _dt.timedelta(hours=1)), 0),
    ("garbage -> default", "soon-ish", 5),
    ("missing -> default", None, 5),
    ("empty -> default", "   ", 5),
]
for label, raw, expect in cases:
    got = m.parse_retry_after(raw)
    check(label, got, expect)
got = m.parse_retry_after(_eu.format_datetime(now + _dt.timedelta(seconds=30)))
print("    %-52s %-14s %s" % ("HTTP-date +30s (approx 29-30)", got, "OK" if 28 <= got <= 30 else "*** FAIL"))
if not 28 <= got <= 30:
    failures.append("HTTP-date +30s out of range: %r" % got)

print()
print("=" * 84)
print("FIX 3 - metadata recorded on every response, accepted or rejected")
print("=" * 84)
meta, _ = run_fetch([FakeResp(500, "text/html", "<html>err</html>")] * 5)
for field in ["byte_size", "sha256", "attempts", "attempt_log", "written_to_disk", "status_code"]:
    check("rejected response has %s" % field, field in meta, True)

print()
print("=" * 84)
if failures:
    print("FAILURES (%d):" % len(failures))
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("ALL ASSERTIONS PASSED - no rejected response reached disk; no network was used")
