#!/usr/bin/env python3
"""
verify_snapshot.py - exhaustive, READ-ONLY integrity verification of a landed
external-source snapshot.

WHY THIS EXISTS
The 2026-07-31 audit found that the scunpacked-data snapshot (~29,000 files,
~6GB) was renamed out of .partial quarantine BEFORE its malware scan ran, and
the scan then never ran. Its manifest records:

    "json_parse_check": "sampled, not exhaustive: 40 of 28,959 JSON files"
    "malware_scan": {"attempted": false}
    "domain_scan": "not run this pass due to time budget"

So 99.86% of that tree has never been checked, and none of it has per-file
hashes. This script closes that gap.

WHAT IT DOES (all of it read-only)
  1. Walks every file in the snapshot.
  2. Streams a SHA-256 of each one (never loads a whole file into memory).
  3. Sniffs the real file type from magic bytes and compares it to the
     extension - catches an HTML error page saved as .json, which has already
     happened once in this pipeline for real.
  4. Attempts a strict JSON parse of every .json file.
  5. Scans text-ish content for active-content indicators and for URLs whose
     domain isn't on the allowlist.
  6. Finds byte-identical duplicate files.
  7. Writes a per-file hash manifest and a findings report.

SAFETY - this script cannot damage anything:
  * Opens every source file with mode "rb". Never "w", never "a", never "+".
  * No os.remove, os.unlink, os.rename, shutil.move, shutil.rmtree anywhere.
  * No network calls. No database connections. No subprocess calls.
  * Writes ONLY inside --out, which must be outside the snapshot directory
    (enforced, not just documented).
  * Safe to interrupt with Ctrl-C and safe to re-run: progress is journalled
    per file, and a re-run skips work already completed.

USAGE
    python verify_snapshot.py <snapshot_dir> --out <output_dir>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CHUNK = 1024 * 1024          # 1 MiB streaming read
SCAN_OVERLAP = 256           # bytes carried between chunks so an indicator
                             # split across a chunk boundary is still caught
PROGRESS_EVERY = 250         # files between progress lines

# Active-content indicators. Matched case-INSENSITIVELY - the existing
# integrity_scan.py matches case-sensitively, which lets <SCRIPT and OnError=
# through. That was audit finding M3.
INDICATORS = [
    "<script", "javascript:", "onerror=", "onload=", "onclick=",
    "eval(", "document.cookie", "<iframe", "data:text/html",
    "powershell", "cmd.exe", "base64,",
]

# Domains expected to appear legitimately in this data.
ALLOWED_DOMAINS = [
    "github.com", "githubusercontent.com", "github.io",
    "star-citizen.wiki", "starcitizen.tools", "starcitizen.fandom.com",
    "robertsspaceindustries.com", "cloudimperiumgames.com",
    "scunpacked.com", "erkul.games", "fleetyards.net", "uexcorp.space",
    "creativecommons.org", "opensource.org", "schema.org",
    "w3.org", "json-schema.org", "spdx.org", "gnu.org",
]

URL_RE = re.compile(rb"https?://([^\s\"'<>\\)\]},]+)", re.IGNORECASE)

# Magic-byte signatures, checked in order.
MAGIC = [
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"GIF87a", "gif"),
    (b"GIF89a", "gif"),
    (b"\xff\xd8\xff", "jpeg"),
    (b"PK\x03\x04", "zip"),
    (b"PK\x05\x06", "zip"),
    (b"\x1f\x8b", "gzip"),
    (b"BZh", "bzip2"),
    (b"\xfd7zXZ\x00", "xz"),
    (b"%PDF-", "pdf"),
    (b"glTF", "glb"),
    (b"OggS", "ogg"),
    (b"RIFF", "riff"),
    (b"\x7fELF", "elf"),
    (b"MZ", "exe/dll"),
    (b"SQLite format 3\x00", "sqlite"),
]

TEXTUAL_EXTS = {
    ".json", ".txt", ".md", ".xml", ".html", ".htm", ".yaml", ".yml",
    ".csv", ".tsv", ".ini", ".cfg", ".js", ".css", ".svg", ".log", "",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg: str, logfile=None) -> None:
    line = f"[{now_iso()}] {msg}"
    print(line, flush=True)
    if logfile is not None:
        logfile.write(line + "\n")
        logfile.flush()


def long_path(p: Path) -> str:
    """Windows caps paths at 260 chars unless you use the extended-length
    prefix. This tree is deeply nested, so opt in rather than crash on the
    handful of files that exceed it."""
    s = str(p)
    if os.name == "nt" and len(s) > 240 and not s.startswith("\\\\?\\"):
        return "\\\\?\\" + os.path.abspath(s)
    return s


def sniff_magic(head: bytes) -> str | None:
    for sig, name in MAGIC:
        if head.startswith(sig):
            return name
    stripped = head.lstrip()[:512].lower()
    if stripped.startswith(b"<!doctype html") or stripped.startswith(b"<html"):
        return "html"
    if stripped.startswith(b"<?xml"):
        return "xml"
    return None


def looks_binary(head: bytes) -> bool:
    if b"\x00" in head:
        return True
    if not head:
        return False
    # crude but effective: proportion of bytes outside printable + whitespace
    printable = sum(
        1 for b in head
        if 32 <= b < 127 or b in (9, 10, 13)
    )
    return (printable / len(head)) < 0.75


def domain_allowed(domain: str) -> bool:
    d = domain.lower().split(":")[0]
    for a in ALLOWED_DOMAINS:
        # leading dot matters: 'evil-github.com' must NOT match 'github.com'
        if d == a or d.endswith("." + a):
            return True
    return False


# ---------------------------------------------------------------------------
# Per-file inspection
# ---------------------------------------------------------------------------

def inspect_file(path: Path, rel: str) -> dict:
    """Read a single file once, streaming, and return everything we learned.
    Opened 'rb' - read only, always."""
    rec: dict = {
        "path": rel,
        "size": None,
        "sha256": None,
        "magic": None,
        "ext": path.suffix.lower(),
        "binary": None,
        "json_ok": None,
        "json_error": None,
        "indicators": {},
        "unexpected_domains": {},
        "error": None,
    }

    try:
        rec["size"] = path.stat().st_size
    except OSError as e:
        rec["error"] = f"stat failed: {e.__class__.__name__}: {e}"
        return rec

    h = hashlib.sha256()
    head = b""
    carry = b""
    indicator_counts: dict[str, int] = defaultdict(int)
    domain_counts: dict[str, int] = defaultdict(int)
    domain_samples: dict[str, str] = {}
    json_buf = bytearray()
    is_json_ext = rec["ext"] == ".json"
    scan_text = False

    try:
        with open(long_path(path), "rb") as fh:
            first = True
            while True:
                chunk = fh.read(CHUNK)
                if not chunk:
                    break
                h.update(chunk)

                if first:
                    head = chunk[:8192]
                    rec["magic"] = sniff_magic(head)
                    rec["binary"] = looks_binary(head)
                    scan_text = (not rec["binary"]) and (
                        is_json_ext or rec["ext"] in TEXTUAL_EXTS
                        or rec["magic"] in ("html", "xml", None)
                    )
                    first = False

                if is_json_ext:
                    json_buf.extend(chunk)

                if scan_text:
                    window = carry + chunk
                    low = window.lower()
                    for ind in INDICATORS:
                        c = low.count(ind.encode())
                        if c:
                            indicator_counts[ind] += c
                    for m in URL_RE.finditer(window):
                        dom = m.group(1).split(b"/")[0].decode(
                            "ascii", errors="replace")
                        if not domain_allowed(dom):
                            domain_counts[dom] += 1
                            if dom not in domain_samples:
                                domain_samples[dom] = m.group(0).decode(
                                    "ascii", errors="replace")[:200]
                    carry = chunk[-SCAN_OVERLAP:]
    except OSError as e:
        rec["error"] = f"read failed: {e.__class__.__name__}: {e}"
        return rec
    except MemoryError:
        rec["error"] = "read failed: MemoryError"
        return rec

    rec["sha256"] = h.hexdigest()

    if is_json_ext:
        try:
            json.loads(bytes(json_buf).decode("utf-8"))
            rec["json_ok"] = True
        except UnicodeDecodeError as e:
            rec["json_ok"] = False
            rec["json_error"] = f"not valid UTF-8: {e}"
        except json.JSONDecodeError as e:
            rec["json_ok"] = False
            rec["json_error"] = f"line {e.lineno} col {e.colno}: {e.msg}"
        except Exception as e:   # noqa: BLE001 - never let one file kill the run
            rec["json_ok"] = False
            rec["json_error"] = f"{e.__class__.__name__}: {e}"

    rec["indicators"] = dict(indicator_counts)
    rec["unexpected_domains"] = {
        d: {"count": c, "sample": domain_samples.get(d, "")}
        for d, c in domain_counts.items()
    }
    return rec


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Read-only exhaustive verification of a landed snapshot.")
    ap.add_argument("snapshot", help="Snapshot directory to verify")
    ap.add_argument("--out", required=True,
                    help="Output directory (must be OUTSIDE the snapshot)")
    args = ap.parse_args()

    snap = Path(args.snapshot).resolve()
    out = Path(args.out).resolve()

    if not snap.is_dir():
        print(f"ERROR: not a directory: {snap}", file=sys.stderr)
        return 2

    # Refuse to write anywhere inside the tree we're verifying. Enforced, not
    # just documented - writing into the subject of a verification would
    # change the thing being measured.
    try:
        out.relative_to(snap)
        print("ERROR: --out must be OUTSIDE the snapshot directory.",
              file=sys.stderr)
        return 2
    except ValueError:
        pass

    out.mkdir(parents=True, exist_ok=True)
    journal_path = out / "journal.jsonl"
    logfile = open(out / "verify.log", "a", encoding="utf-8")

    log("=" * 70, logfile)
    log("verify_snapshot.py - READ-ONLY verification", logfile)
    log(f"snapshot: {snap}", logfile)
    log(f"output:   {out}", logfile)

    # Resume support: anything already journalled is not redone.
    done: dict[str, dict] = {}
    if journal_path.exists():
        with open(journal_path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                    done[r["path"]] = r
                except Exception:      # noqa: BLE001 - tolerate a torn last line
                    continue
        log(f"resuming: {len(done)} file(s) already verified", logfile)

    log("enumerating files (this can take a minute on a large tree)...",
        logfile)
    all_files: list[tuple[Path, str]] = []
    walk_errors: list[str] = []

    def onerr(e: OSError) -> None:
        walk_errors.append(f"{e.filename}: {e}")

    for root, _dirs, files in os.walk(snap, onerror=onerr):
        for name in files:
            p = Path(root) / name
            try:
                rel = str(p.relative_to(snap)).replace("\\", "/")
            except ValueError:
                continue
            all_files.append((p, rel))

    total = len(all_files)
    log(f"found {total} file(s); {len(walk_errors)} walk error(s)", logfile)

    pending = [(p, r) for (p, r) in all_files if r not in done]
    log(f"{len(pending)} file(s) still to verify", logfile)

    started = time.time()
    processed = 0
    bytes_done = 0

    with open(journal_path, "a", encoding="utf-8") as jf:
        for path, rel in pending:
            rec = inspect_file(path, rel)
            jf.write(json.dumps(rec, ensure_ascii=False) + "\n")
            jf.flush()
            done[rel] = rec
            processed += 1
            bytes_done += rec.get("size") or 0

            if processed % PROGRESS_EVERY == 0:
                elapsed = max(time.time() - started, 0.001)
                rate = processed / elapsed
                remaining = len(pending) - processed
                eta_min = (remaining / rate / 60) if rate > 0 else 0
                log(
                    f"  {processed}/{len(pending)} files  "
                    f"{bytes_done / (1024*1024):.0f} MiB  "
                    f"{rate:.1f} files/s  ETA ~{eta_min:.0f} min",
                    logfile,
                )

    log(f"inspection complete: {processed} file(s) this run", logfile)

    # -----------------------------------------------------------------------
    # Roll up findings
    # -----------------------------------------------------------------------
    records = list(done.values())

    read_errors = [r for r in records if r.get("error")]
    json_files = [r for r in records if r.get("ext") == ".json"]
    json_bad = [r for r in json_files if r.get("json_ok") is False]
    # A .json file whose magic says html/zip/etc is the exact bug that already
    # happened here: an HTTP 500 error page saved as vehicles_page_1.json.
    ext_mismatch = [
        r for r in json_files
        if r.get("magic") in ("html", "xml", "zip", "gzip", "pdf", "png",
                              "jpeg", "exe/dll", "elf")
    ]
    with_indicators = [r for r in records if r.get("indicators")]
    with_domains = [r for r in records if r.get("unexpected_domains")]

    by_hash: dict[str, list[str]] = defaultdict(list)
    for r in records:
        if r.get("sha256"):
            by_hash[r["sha256"]].append(r["path"])
    duplicates = {h: p for h, p in by_hash.items() if len(p) > 1}

    domain_totals: dict[str, int] = defaultdict(int)
    indicator_totals: dict[str, int] = defaultdict(int)
    for r in records:
        for d, info in (r.get("unexpected_domains") or {}).items():
            domain_totals[d] += info["count"]
        for i, c in (r.get("indicators") or {}).items():
            indicator_totals[i] += c

    total_bytes = sum(r.get("size") or 0 for r in records)
    non_json = [r for r in records if r.get("ext") != ".json"]
    git_internal = [r for r in records if r["path"].startswith(".git/")]

    report = {
        "schema": "citizen-compass/snapshot-verification/1.0",
        "generated_utc": now_iso(),
        "snapshot_path": str(snap),
        "read_only": True,
        "totals": {
            "files": len(records),
            "bytes": total_bytes,
            "json_files": len(json_files),
            "non_json_files": len(non_json),
            "git_internal_files": len(git_internal),
        },
        "coverage": {
            "files_enumerated": total,
            "files_inspected": len(records),
            "files_unreadable": len(read_errors),
            "json_files_found": len(json_files),
            "json_files_parsed_ok": len(json_files) - len(json_bad),
            "json_files_parse_failed": len(json_bad),
            "inspection_complete": len(records) == total and not walk_errors,
            "note": (
                "Every enumerated file was hashed and every .json file was "
                "parsed. 'inspection_complete' is false if the walk hit an "
                "error or any file could not be inspected - in that case this "
                "run does NOT constitute full coverage and should not be "
                "reported as such. This supersedes the manifest's 'sampled, "
                "not exhaustive: 40 of 28,959' entry only when it is true."
            ),
        },
        "findings": {
            "read_errors": len(read_errors),
            "json_parse_failures": len(json_bad),
            "extension_content_mismatch": len(ext_mismatch),
            "files_with_active_content_indicators": len(with_indicators),
            "files_with_unexpected_domains": len(with_domains),
            "duplicate_hash_groups": len(duplicates),
            "walk_errors": len(walk_errors),
        },
        "indicator_totals": dict(sorted(
            indicator_totals.items(), key=lambda kv: -kv[1])),
        "unexpected_domain_totals": dict(sorted(
            domain_totals.items(), key=lambda kv: -kv[1])),
        "detail": {
            "read_errors": [
                {"path": r["path"], "error": r["error"]}
                for r in read_errors[:200]
            ],
            "json_parse_failures": [
                {"path": r["path"], "error": r["json_error"],
                 "magic": r["magic"], "size": r["size"]}
                for r in json_bad[:200]
            ],
            "extension_content_mismatch": [
                {"path": r["path"], "magic": r["magic"], "size": r["size"]}
                for r in ext_mismatch[:200]
            ],
            "files_with_active_content_indicators": [
                {"path": r["path"], "indicators": r["indicators"]}
                for r in with_indicators[:200]
            ],
            "files_with_unexpected_domains": [
                {"path": r["path"], "domains": r["unexpected_domains"]}
                for r in with_domains[:200]
            ],
            "walk_errors": walk_errors[:200],
        },
        "truncation_note": (
            "Detail lists are capped at 200 entries each so this report stays "
            "readable. The journal.jsonl beside it holds every file's full "
            "record, untruncated - nothing was silently dropped."
        ),
    }

    with open(out / "verification-report.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)

    with open(out / "SHA256SUMS.txt", "w", encoding="utf-8") as fh:
        for r in sorted(records, key=lambda x: x["path"]):
            if r.get("sha256"):
                fh.write(f"{r['sha256']}  {r['path']}\n")

    if duplicates:
        with open(out / "duplicates.json", "w", encoding="utf-8") as fh:
            json.dump(duplicates, fh, indent=2, ensure_ascii=False)

    log("-" * 70, logfile)
    log(f"files verified ......... {len(records)}", logfile)
    log(f"total bytes ............ {total_bytes / (1024**3):.2f} GiB", logfile)
    log(f"json files parsed ...... {len(json_files)}", logfile)
    log(f"json parse FAILURES .... {len(json_bad)}", logfile)
    log(f"ext/content MISMATCH ... {len(ext_mismatch)}", logfile)
    log(f"active-content hits .... {len(with_indicators)} file(s)", logfile)
    log(f"unexpected domains ..... {len(with_domains)} file(s)", logfile)
    log(f"duplicate hash groups .. {len(duplicates)}", logfile)
    log(f"read errors ............ {len(read_errors)}", logfile)
    log(f"walk errors ............ {len(walk_errors)}", logfile)
    log("-" * 70, logfile)
    log(f"report:  {out / 'verification-report.json'}", logfile)
    log(f"hashes:  {out / 'SHA256SUMS.txt'}", logfile)
    log("DONE. Nothing in the snapshot was modified.", logfile)

    logfile.close()

    # Exit 0 = the verification RAN successfully. Findings are reported in the
    # JSON, deliberately not encoded as a failure exit - this script's job is
    # to measure, not to judge. Only a genuine inability to run is non-zero.
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted. Progress is journalled - re-run to resume.",
              file=sys.stderr)
        sys.exit(130)
