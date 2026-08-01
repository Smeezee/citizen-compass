"""Verification fixtures for integrity_scan.py after the 2026-08-01 fixes.

Proves three things:
  1. the URL trimming fix clears the exact strings that produced false
     positives against 20260801T021731Z.partial, without accepting a genuinely
     unexpected domain;
  2. coverage now reaches every file, and an unreadable file fails the gate
     rather than passing by omission;
  3. the gate still EXITS 1 on a real finding - it has not become always-pass.

Read-only apart from files it creates under a temp dir of its own.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import integrity_scan as I  # noqa: E402

SCRIPT = Path(__file__).resolve().parent / "integrity_scan.py"
PY = sys.executable
failures = []


def check(label, got, expected):
    ok = got == expected
    if not ok:
        failures.append(f"{label}: got {got!r}, expected {expected!r}")
    print("  %-62s %-26s %s" % (label, repr(got), "OK" if ok else "*** FAIL (want %r)" % (expected,)))


print("=" * 90)
print("FIX 2 - URL trimming, against the EXACT strings that failed on 20260801T021731Z")
print("=" * 90)
# These are the literal netlocs the old regex produced, and the URLs behind them.
cases = [
    ("https://starcitizen.tools)",                 "starcitizen.tools",     True),
    ("https://star-citizen.wiki).",                "star-citizen.wiki",     True),
    ("https://docs.star-citizen.wiki)",            "docs.star-citizen.wiki", True),
    ("https://api.star-citizen.wiki",              "api.star-citizen.wiki", True),
    ("https://example.com/vehicles/arrow",         "example.com",           True),
    ("https://api.example.com/vehicles/uuid",      "api.example.com",       True),
    ("https://opensource.org/licenses/MIT",        "opensource.org",        True),
    ("https://a.nel.cloudflare.com/report/v4?s=x", "a.nel.cloudflare.com",  True),
    # Must still be caught - the fix must not launder a genuinely foreign host.
    ("https://evil.example.net/payload.js",        "evil.example.net",      False),
    ("https://pastebin.com/raw/abcd)",             "pastebin.com",          False),
    # A legitimately balanced paren must be preserved, not stripped.
    ("https://starcitizen.tools/Ship_(disambiguation)", "starcitizen.tools", True),
]
for url, want_host, want_allowed in cases:
    host = I.domain_of(url)
    check("host of %-48s" % url[:48], host, want_host)
    check("  allowed?", I.is_allowed(host), want_allowed)

print()
print("  balanced-paren path preserved:",
      I.trim_url("https://starcitizen.tools/Ship_(disambiguation)"))

print()
print("=" * 90)
print("FIX 1 + FIX 3 - coverage and exit codes, end to end")
print("=" * 90)

tmp = Path(tempfile.mkdtemp(prefix="integrity_fixture_"))

# ---- fixture A: known-good, mixed file types incl. non-JSON ----
good = tmp / "good"
good.mkdir()
(good / "data.json").write_text(json.dumps({"url": "https://api.star-citizen.wiki/api/vehicles"}), encoding="utf-8")
(good / "spec.yaml").write_text(
    "info:\n  license: https://opensource.org/licenses/MIT\n"
    "  docs: see https://starcitizen.tools) and https://example.com/vehicles/arrow\n",
    encoding="utf-8")
(good / "resp.headers").write_text(
    'HTTP 200\nreport-to: {"endpoints":[{"url":"https://a.nel.cloudflare.com/report/v4?s=abc"}]}\n',
    encoding="utf-8")
(good / "run.log").write_text("Pulling vehicles ...\n", encoding="utf-8")
(good / "binary.bin").write_bytes(bytes(range(256)))  # not valid utf-8
(good / "nested").mkdir()
(good / "nested" / "deep.json").write_text('{"a": 1}', encoding="utf-8")

# ---- fixture B: known-bad, active content ----
bad_ind = tmp / "bad_indicator"
bad_ind.mkdir()
(bad_ind / "page.json").write_text(json.dumps({"html": "<script>alert(1)</script>"}), encoding="utf-8")

# ---- fixture C: known-bad, unexpected domain in a NON-JSON file ----
bad_dom = tmp / "bad_domain"
bad_dom.mkdir()
(bad_dom / "notes.txt").write_text("exfil to https://evil.example.net/payload\n", encoding="utf-8")


def run(path):
    p = subprocess.run([PY, str(SCRIPT), str(path)], capture_output=True, text=True)
    return p.returncode, json.loads(p.stdout)


print("\n-- fixture A: known-good (6 files, 5 of them NOT .json, 1 nested, 1 binary) --")
rc, rep = run(good)
cov = rep["coverage"]
check("exit code", rc, 0)
check("files_seen", cov["files_seen"], 6)
check("files_scanned", cov["files_scanned"], 6)
check("coverage complete", cov["complete"], True)
check("any unexpected domains", any(f["unexpected_domains"] for f in rep["files"]), False)
check("any indicator hits", any(f["content_indicator_hits"] for f in rep["files"]), False)
print("   NOTE: under the OLD *.json glob this directory would have scanned only",
      len([f for f in rep["files"] if f["file"].endswith(".json")]), "of 6 files")

print("\n-- fixture B: known-bad, <script> in a JSON file --")
rc, rep = run(bad_ind)
check("exit code (must be 1)", rc, 1)
check("indicator detected", bool(rep["files"][0]["content_indicator_hits"]), True)

print("\n-- fixture C: known-bad, unexpected domain in a .txt (invisible to old glob) --")
rc, rep = run(bad_dom)
check("exit code (must be 1)", rc, 1)
check("files_seen", rep["coverage"]["files_seen"], 1)
check("unexpected domain found", "evil.example.net" in rep["files"][0]["unexpected_domains"], True)

print("\n-- fixture D: unreadable file must FAIL, not pass by omission --")
unread = tmp / "unreadable"
unread.mkdir()
(unread / "ok.json").write_text("{}", encoding="utf-8")
target = unread / "locked.json"
target.write_text("{}", encoding="utf-8")
handle = open(target, "r+")
try:
    import msvcrt
    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
    locked = True
except Exception:
    locked = False
if locked:
    rc, rep = run(unread)
    check("exit code (must be 1)", rc, 1)
    check("coverage complete", rep["coverage"]["complete"], False)
    check("files_unscanned", rep["coverage"]["files_unscanned"], 1)
    try:
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
    except Exception:
        pass
else:
    print("  (could not lock a file on this platform; exercising scan_file directly instead)")
    r = I.scan_file(tmp / "does_not_exist.json")
    check("scanned flag on unreadable", r["scanned"], False)
    check("unscanned_reason present", bool(r["unscanned_reason"]), True)
handle.close()

print()
print("=" * 90)
if failures:
    print("FAILURES (%d):" % len(failures))
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("ALL FIXTURE ASSERTIONS PASSED - gate still exits 1 on real findings, and no file is skipped")
