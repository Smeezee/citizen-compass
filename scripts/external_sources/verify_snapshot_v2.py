#!/usr/bin/env python3
"""
verify_snapshot_v2.py - READ-ONLY integrity verification of a landed snapshot.

WHAT THIS IS, STATED HONESTLY
This is an integrity and content-heuristic scanner. It hashes every file,
strictly parses every JSON file, checks declared extension against actual
magic bytes, and flags active-content indicators and off-allowlist domains.

WHAT THIS IS NOT
It is NOT antivirus and it is NOT a malware scan. It runs no signatures,
unpacks no archives, analyses no binaries, and sandboxes nothing. A snapshot
must still get a real AV pass before release from quarantine. v1 of this
script was reviewed by Echo and rejected as a certification gate on exactly
this point, among others. That rejection was correct.

CHANGES FROM v1 (all 13 findings from Echo's 2026-07-31 review)
  1. inspection_complete now requires zero walk errors, zero read errors,
     every file hashed, and every .json file given a parse verdict. v1 could
     report complete with an unreadable file - reproduced, confirmed.
  2. The journal is bound to a run manifest carrying the snapshot's canonical
     path, the scanner version and a hash of the active configuration.
     Resume is refused if any differ. Individual records are revalidated
     against size+mtime before being reused. v1 keyed on relative path alone
     and would reuse snapshot A's hash for snapshot B's same-named file -
     reproduced, confirmed.
  3. Extension/content mismatch now covers every recognised type, not just
     .json. v1 detected an MZ executable saved as .png internally and then
     reported zero mismatches - reproduced, confirmed.
  4. The malware-scan claim is removed. See above.
  5. JSON files above --max-json-mem are structurally checked and labelled
     "structural_only" rather than silently claimed as fully validated.
  6. Files are re-stat'd after reading and flagged if they changed mid-run;
     the tree is re-enumerated at the end to catch additions and removals.
  7. Exit codes distinguish "scan complete, findings inside" from "scan
     incomplete". v1 always returned 0 - the same fail-open pattern this
     project's own audit criticised in integrity_scan.py.
  8. Symlinks and Windows reparse points are refused, not followed. v1 read
     and hashed a file outside the snapshot through a symlink - reproduced,
     confirmed.
  9. Chunk-overlap double counting fixed. v1 reported 2 occurrences for 1 -
     reproduced, confirmed.
 10. Strict JSON: NaN / Infinity / -Infinity are rejected and duplicate
     object keys are reported. v1 accepted {"x": NaN} as valid - confirmed.
 11. Windows extended-length paths applied to stat and enumeration, not just
     open, with correct UNC handling.
 12. Journal records for files no longer present are excluded from totals and
     reported separately as stale.
 13. Outputs are written to a temporary file and atomically replaced;
     duplicates.json is always written, empty when there are none.

SAFETY
  * Every source file is opened "rb". No "w", no "a", no "+".
  * No os.remove / os.unlink / os.rename against the snapshot, no shutil
    mutation, no network, no database, no subprocess.
  * Writes only inside --out, which must be outside the snapshot (enforced).
  * Safe to interrupt; safe to re-run.

USAGE
    python verify_snapshot_v2.py <snapshot_dir> --out <output_dir>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat as statmod
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

SCANNER_VERSION = "2.0.0"

CHUNK = 1024 * 1024
SCAN_OVERLAP = 256
PROGRESS_EVERY = 250
DEFAULT_MAX_JSON_MEM = 64 * 1024 * 1024      # above this, structural check only

EXIT_OK = 0            # scan complete; findings (if any) are in the report
EXIT_USAGE = 2         # bad arguments / refused to start
EXIT_INCOMPLETE = 3    # scan ran but coverage is NOT complete

INDICATORS = [
    "<script", "javascript:", "onerror=", "onload=", "onclick=",
    "eval(", "document.cookie", "<iframe", "data:text/html",
    "powershell", "cmd.exe", "base64,",
]

ALLOWED_DOMAINS = [
    "github.com", "githubusercontent.com", "github.io",
    "star-citizen.wiki", "starcitizen.tools", "starcitizen.fandom.com",
    "robertsspaceindustries.com", "cloudimperiumgames.com",
    "scunpacked.com", "erkul.games", "fleetyards.net", "uexcorp.space",
    "creativecommons.org", "opensource.org", "schema.org",
    "w3.org", "json-schema.org", "spdx.org", "gnu.org",
]

URL_RE = re.compile(rb"https?://([^\s\"'<>\\)\]},]+)", re.IGNORECASE)

MAGIC = [
    (b"\x89PNG\r\n\x1a\n", "png"), (b"GIF87a", "gif"), (b"GIF89a", "gif"),
    (b"\xff\xd8\xff", "jpeg"), (b"PK\x03\x04", "zip"), (b"PK\x05\x06", "zip"),
    (b"\x1f\x8b", "gzip"), (b"BZh", "bzip2"), (b"\xfd7zXZ\x00", "xz"),
    (b"%PDF-", "pdf"), (b"glTF", "glb"), (b"OggS", "ogg"), (b"RIFF", "riff"),
    (b"\x7fELF", "elf"), (b"MZ", "exe/dll"),
    (b"SQLite format 3\x00", "sqlite"), (b"\x00\x00\x01\x00", "ico"),
    (b"wOFF", "woff"), (b"wOF2", "woff2"),
]

# Finding 3: what each extension is ALLOWED to actually be. Anything detected
# outside its set is a mismatch. Applies to every recognised type now, not
# just .json.
EXT_EXPECTED: dict[str, set[str | None]] = {
    ".json": {None, "text"}, ".txt": {None, "text"}, ".md": {None, "text"},
    ".csv": {None, "text"}, ".tsv": {None, "text"}, ".yaml": {None, "text"},
    ".yml": {None, "text"}, ".ini": {None, "text"}, ".cfg": {None, "text"},
    ".js": {None, "text"}, ".css": {None, "text"}, ".log": {None, "text"},
    ".xml": {None, "text", "xml"}, ".svg": {None, "text", "xml"},
    ".html": {None, "text", "html", "xml"}, ".htm": {None, "text", "html", "xml"},
    ".png": {"png"}, ".jpg": {"jpeg"}, ".jpeg": {"jpeg"}, ".gif": {"gif"},
    ".ico": {"ico", "png"}, ".pdf": {"pdf"}, ".zip": {"zip"},
    ".gz": {"gzip"}, ".bz2": {"bzip2"}, ".xz": {"xz"},
    ".glb": {"glb"}, ".ogg": {"ogg"}, ".wav": {"riff"}, ".webp": {"riff"},
    ".exe": {"exe/dll"}, ".dll": {"exe/dll"}, ".so": {"elf"},
    ".db": {"sqlite"}, ".sqlite": {"sqlite"},
    ".woff": {"woff"}, ".woff2": {"woff2"},
}

TEXTUAL_EXTS = {
    ".json", ".txt", ".md", ".xml", ".html", ".htm", ".yaml", ".yml",
    ".csv", ".tsv", ".ini", ".cfg", ".js", ".css", ".svg", ".log", "",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def config_fingerprint() -> str:
    """Finding 2: resume must be refused if the rules changed underneath it."""
    blob = json.dumps({
        "version": SCANNER_VERSION,
        "indicators": sorted(INDICATORS),
        "allowed_domains": sorted(ALLOWED_DOMAINS),
        "magic": [m[1] for m in MAGIC],
        "ext_expected": {k: sorted(x or "none" for x in v)
                         for k, v in sorted(EXT_EXPECTED.items())},
        "chunk": CHUNK, "overlap": SCAN_OVERLAP,
    }, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()


class _Log:
    def __init__(self, path: Path):
        self.fh = open(path, "a", encoding="utf-8")

    def __call__(self, msg: str) -> None:
        line = f"[{now_iso()}] {msg}"
        print(line, flush=True)
        self.fh.write(line + "\n")
        self.fh.flush()

    def close(self) -> None:
        self.fh.close()


def ext_path(p: Path | str) -> str:
    """Finding 11: extended-length prefix, applied everywhere, UNC-aware."""
    s = os.path.abspath(str(p))
    if os.name != "nt" or s.startswith("\\\\?\\"):
        return s
    if len(s) <= 240:
        return s
    if s.startswith("\\\\"):
        return "\\\\?\\UNC\\" + s[2:]
    return "\\\\?\\" + s


def atomic_write_json(path: Path, obj) -> None:
    """Finding 13: never leave a half-written or stale report behind."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, ensure_ascii=False)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def atomic_write_text(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(text)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def sniff_magic(head: bytes) -> str | None:
    for sig, name in MAGIC:
        if head.startswith(sig):
            return name
    s = head.lstrip()[:512].lower()
    if s.startswith(b"<!doctype html") or s.startswith(b"<html"):
        return "html"
    if s.startswith(b"<?xml"):
        return "xml"
    return None


def looks_binary(head: bytes) -> bool:
    if b"\x00" in head:
        return True
    if not head:
        return False
    printable = sum(1 for b in head if 32 <= b < 127 or b in (9, 10, 13))
    return (printable / len(head)) < 0.75


def domain_allowed(domain: str) -> bool:
    d = domain.lower().split(":")[0]
    return any(d == a or d.endswith("." + a) for a in ALLOWED_DOMAINS)


def is_link_like(path: Path) -> tuple[bool, str | None]:
    """Finding 8: refuse symlinks AND Windows reparse points (junctions)."""
    try:
        st = os.lstat(ext_path(path))
    except OSError as e:
        return False, f"lstat failed: {e}"
    if statmod.S_ISLNK(st.st_mode):
        return True, "symlink"
    attrs = getattr(st, "st_file_attributes", 0)
    reparse = getattr(statmod, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    if attrs & reparse:
        return True, "reparse_point"
    return False, None


# --- Finding 10: strict JSON -------------------------------------------------

class StrictJSONError(ValueError):
    pass


def _reject_constant(name):
    raise StrictJSONError(f"non-standard JSON constant: {name}")


def _dup_key_hook(pairs):
    seen = set()
    dups = set()
    for k, _v in pairs:
        if k in seen:
            dups.add(k)
        seen.add(k)
    if dups:
        raise StrictJSONError(
            f"duplicate object key(s): {', '.join(sorted(dups)[:5])}")
    return dict(pairs)


def strict_json_loads(text: str):
    return json.loads(text, parse_constant=_reject_constant,
                      object_pairs_hook=_dup_key_hook)


def structural_json_check(path: Path) -> tuple[bool, str | None]:
    """Finding 5: for very large files, stream a bracket/quote balance check
    instead of buffering. Reported honestly as structural_only - never as a
    full parse."""
    depth = 0
    in_str = False
    esc = False
    saw_any = False
    try:
        with open(ext_path(path), "rb") as fh:
            while True:
                chunk = fh.read(CHUNK)
                if not chunk:
                    break
                for b in chunk:
                    c = chr(b)
                    if in_str:
                        if esc:
                            esc = False
                        elif c == "\\":
                            esc = True
                        elif c == '"':
                            in_str = False
                        continue
                    if c == '"':
                        in_str = True
                    elif c in "{[":
                        depth += 1
                        saw_any = True
                    elif c in "}]":
                        depth -= 1
                        if depth < 0:
                            return False, "unbalanced closing bracket"
    except OSError as e:
        return False, f"read failed: {e}"
    if in_str:
        return False, "unterminated string"
    if depth != 0:
        return False, f"unbalanced brackets (depth {depth})"
    if not saw_any:
        return False, "no JSON structure found"
    return True, None


# --- per-file inspection -----------------------------------------------------

def inspect_file(path: Path, rel: str, max_json_mem: int) -> dict:
    rec: dict = {
        "path": rel, "size": None, "mtime_ns": None, "sha256": None,
        "magic": None, "ext": path.suffix.lower(), "binary": None,
        "json_ok": None, "json_mode": None, "json_error": None,
        "indicators": {}, "unexpected_domains": {},
        "link_like": None, "changed_during_read": False, "error": None,
    }

    linky, kind = is_link_like(path)
    if linky:
        rec["link_like"] = kind
        rec["error"] = f"refused to follow {kind}"
        return rec

    try:
        st = os.stat(ext_path(path))
        rec["size"] = st.st_size
        rec["mtime_ns"] = st.st_mtime_ns
    except OSError as e:
        rec["error"] = f"stat failed: {e.__class__.__name__}: {e}"
        return rec

    h = hashlib.sha256()
    carry = b""
    ind_counts: dict[str, int] = defaultdict(int)
    dom_counts: dict[str, int] = defaultdict(int)
    dom_samples: dict[str, str] = {}
    json_buf = bytearray()
    is_json = rec["ext"] == ".json"
    buffer_json = is_json and rec["size"] is not None and rec["size"] <= max_json_mem
    scan_text = False
    read_bytes = 0

    try:
        with open(ext_path(path), "rb") as fh:
            first = True
            while True:
                chunk = fh.read(CHUNK)
                if not chunk:
                    break
                read_bytes += len(chunk)
                h.update(chunk)

                if first:
                    head = chunk[:8192]
                    rec["magic"] = sniff_magic(head)
                    rec["binary"] = looks_binary(head)
                    scan_text = (not rec["binary"]) and (
                        is_json or rec["ext"] in TEXTUAL_EXTS
                        or rec["magic"] in ("html", "xml", None))
                    first = False

                if buffer_json:
                    json_buf.extend(chunk)

                if scan_text:
                    window = carry + chunk
                    low = window.lower()
                    # Finding 9: a match lying entirely inside the carry was
                    # already counted on the previous window. Only count
                    # matches that start at or after the boundary minus
                    # (len(pattern) - 1), i.e. ones that genuinely straddle or
                    # start in the new chunk.
                    for ind in INDICATORS:
                        pat = ind.encode()
                        floor = max(0, len(carry) - len(pat) + 1)
                        start = 0
                        while True:
                            i = low.find(pat, start)
                            if i == -1:
                                break
                            if i >= floor:
                                ind_counts[ind] += 1
                            start = i + 1
                    for m in URL_RE.finditer(window):
                        if m.start() < max(0, len(carry) - 8):
                            continue
                        dom = m.group(1).split(b"/")[0].decode(
                            "ascii", errors="replace")
                        if not domain_allowed(dom):
                            dom_counts[dom] += 1
                            dom_samples.setdefault(
                                dom, m.group(0).decode(
                                    "ascii", errors="replace")[:200])
                    carry = chunk[-SCAN_OVERLAP:]
    except OSError as e:
        rec["error"] = f"read failed: {e.__class__.__name__}: {e}"
        return rec
    except MemoryError:
        rec["error"] = "read failed: MemoryError"
        return rec

    rec["sha256"] = h.hexdigest()

    # Finding 6: did it move under us while we were reading it?
    try:
        st2 = os.stat(ext_path(path))
        if st2.st_size != rec["size"] or st2.st_mtime_ns != rec["mtime_ns"]:
            rec["changed_during_read"] = True
            rec["error"] = (
                f"file changed during read (size {rec['size']}->{st2.st_size}, "
                f"mtime {rec['mtime_ns']}->{st2.st_mtime_ns})")
        elif read_bytes != rec["size"]:
            rec["changed_during_read"] = True
            rec["error"] = f"read {read_bytes} bytes, stat said {rec['size']}"
    except OSError as e:
        rec["error"] = f"re-stat failed: {e}"

    if is_json:
        if buffer_json:
            rec["json_mode"] = "full_parse"
            try:
                strict_json_loads(bytes(json_buf).decode("utf-8"))
                rec["json_ok"] = True
            except UnicodeDecodeError as e:
                rec["json_ok"] = False
                rec["json_error"] = f"not valid UTF-8: {e}"
            except StrictJSONError as e:
                rec["json_ok"] = False
                rec["json_error"] = f"strict: {e}"
            except json.JSONDecodeError as e:
                rec["json_ok"] = False
                rec["json_error"] = f"line {e.lineno} col {e.colno}: {e.msg}"
            except Exception as e:      # noqa: BLE001
                rec["json_ok"] = False
                rec["json_error"] = f"{e.__class__.__name__}: {e}"
        else:
            rec["json_mode"] = "structural_only"
            ok, err = structural_json_check(path)
            rec["json_ok"] = ok
            rec["json_error"] = err

    rec["indicators"] = dict(ind_counts)
    rec["unexpected_domains"] = {
        d: {"count": c, "sample": dom_samples.get(d, "")}
        for d, c in dom_counts.items()
    }
    return rec


def enumerate_tree(snap: Path) -> tuple[list[tuple[Path, str]], list[str], list[dict]]:
    files: list[tuple[Path, str]] = []
    errors: list[str] = []
    links: list[dict] = []

    def onerr(e: OSError) -> None:
        errors.append(f"{e.filename}: {e}")

    # followlinks=False is the default and is what we want - directory
    # symlinks are not descended into.
    for root, dirs, names in os.walk(snap, onerror=onerr, followlinks=False):
        for d in list(dirs):
            linky, kind = is_link_like(Path(root) / d)
            if linky:
                links.append({"path": str((Path(root) / d).relative_to(snap)
                                          ).replace("\\", "/"),
                              "kind": kind, "type": "dir"})
                dirs.remove(d)
        for name in names:
            p = Path(root) / name
            try:
                rel = str(p.relative_to(snap)).replace("\\", "/")
            except ValueError:
                continue
            files.append((p, rel))
    return files, errors, links


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Read-only integrity verification of a landed snapshot. "
                    "NOT a malware scan.")
    ap.add_argument("snapshot")
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-json-mem", type=int, default=DEFAULT_MAX_JSON_MEM,
                    help="JSON files larger than this get a structural check "
                         "only, reported as such (default 64 MiB)")
    args = ap.parse_args()

    snap = Path(args.snapshot).resolve()
    out = Path(args.out).resolve()

    if not snap.is_dir():
        print(f"ERROR: not a directory: {snap}", file=sys.stderr)
        return EXIT_USAGE
    try:
        out.relative_to(snap)
        print("ERROR: --out must be OUTSIDE the snapshot directory.",
              file=sys.stderr)
        return EXIT_USAGE
    except ValueError:
        pass

    out.mkdir(parents=True, exist_ok=True)
    log = _Log(out / "verify.log")
    journal_path = out / "journal.jsonl"
    manifest_path = out / "run-manifest.json"

    fingerprint = config_fingerprint()
    manifest = {
        "scanner": "verify_snapshot_v2.py",
        "scanner_version": SCANNER_VERSION,
        "config_fingerprint": fingerprint,
        "snapshot_canonical_path": str(snap),
        "created_utc": now_iso(),
    }

    log("=" * 72)
    log(f"verify_snapshot_v2.py {SCANNER_VERSION} - READ-ONLY. Not antivirus.")
    log(f"snapshot: {snap}")
    log(f"output:   {out}")

    # Finding 2: bind the journal to one snapshot + scanner + config.
    done: dict[str, dict] = {}
    if manifest_path.exists():
        try:
            prev = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as e:      # noqa: BLE001
            log(f"ERROR: run-manifest.json unreadable ({e}). Refusing.")
            log.close()
            return EXIT_USAGE
        mismatches = [
            k for k in ("scanner_version", "config_fingerprint",
                        "snapshot_canonical_path")
            if prev.get(k) != manifest[k]
        ]
        if mismatches:
            log("REFUSING TO RESUME - this output directory belongs to a "
                "different run:")
            for k in mismatches:
                log(f"  {k}: journal has {prev.get(k)!r}, this run is "
                    f"{manifest[k]!r}")
            log("Use a fresh --out directory.")
            log.close()
            return EXIT_USAGE
        manifest["created_utc"] = prev.get("created_utc", manifest["created_utc"])
        if journal_path.exists():
            with open(journal_path, "r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        r = json.loads(line)
                        done[r["path"]] = r
                    except Exception:   # noqa: BLE001
                        continue
            log(f"resuming: {len(done)} journalled record(s)")
    atomic_write_json(manifest_path, manifest)

    log("enumerating...")
    all_files, walk_errors, link_dirs = enumerate_tree(snap)
    current = {rel: p for p, rel in all_files}
    total = len(all_files)
    log(f"found {total} file(s); {len(walk_errors)} walk error(s); "
        f"{len(link_dirs)} link-like director(y/ies) skipped")

    # Finding 2 again: a journalled record is only reusable if the file is
    # still there AND its size and mtime are unchanged.
    reusable: dict[str, dict] = {}
    invalidated = 0
    for rel, rec in done.items():
        p = current.get(rel)
        if p is None:
            continue
        try:
            st = os.stat(ext_path(p))
        except OSError:
            continue
        if (rec.get("size") == st.st_size
                and rec.get("mtime_ns") == st.st_mtime_ns
                and rec.get("sha256")
                and not rec.get("error")):
            reusable[rel] = rec
        else:
            invalidated += 1
    if done:
        log(f"reusable: {len(reusable)}; re-scanning {invalidated} changed or "
            f"previously-failed record(s)")

    stale = sorted(set(done) - set(current))     # finding 12
    pending = [(p, r) for (p, r) in all_files if r not in reusable]
    log(f"{len(pending)} file(s) to inspect this run")

    started = time.time()
    processed = 0
    bytes_done = 0
    results: dict[str, dict] = dict(reusable)

    with open(journal_path, "a", encoding="utf-8") as jf:
        for path, rel in pending:
            rec = inspect_file(path, rel, args.max_json_mem)
            jf.write(json.dumps(rec, ensure_ascii=False) + "\n")
            jf.flush()
            results[rel] = rec
            processed += 1
            bytes_done += rec.get("size") or 0
            if processed % PROGRESS_EVERY == 0:
                el = max(time.time() - started, 0.001)
                rate = processed / el
                eta = ((len(pending) - processed) / rate / 60) if rate else 0
                log(f"  {processed}/{len(pending)}  "
                    f"{bytes_done/(1024*1024):.0f} MiB  {rate:.1f} f/s  "
                    f"ETA ~{eta:.0f} min")

    log("inspection pass complete; re-enumerating to detect drift...")
    after_files, after_walk_errors, _ = enumerate_tree(snap)
    after = {rel for _p, rel in after_files}
    appeared = sorted(after - set(current))          # finding 6
    vanished = sorted(set(current) - after)

    # -------- roll-up (finding 12: current files only) ----------------------
    records = [results[r] for r in sorted(results) if r in current]

    read_errors = [r for r in records if r.get("error")]
    link_files = [r for r in records if r.get("link_like")]
    changed = [r for r in records if r.get("changed_during_read")]
    json_files = [r for r in records if r.get("ext") == ".json"]
    json_bad = [r for r in json_files if r.get("json_ok") is False]
    json_structural = [r for r in json_files
                       if r.get("json_mode") == "structural_only"]
    no_hash = [r for r in records if not r.get("sha256")]
    json_no_verdict = [r for r in json_files if r.get("json_ok") is None]

    # finding 3: mismatch across every recognised extension
    ext_mismatch = []
    for r in records:
        expected = EXT_EXPECTED.get(r.get("ext"))
        if not expected:
            continue
        magic = r.get("magic")
        effective = magic if magic is not None else (
            None if not r.get("binary") else "binary")
        if effective == "binary" and None in expected:
            ext_mismatch.append({"path": r["path"], "ext": r["ext"],
                                 "detected": "binary-but-text-extension"})
        elif magic is not None and magic not in expected:
            ext_mismatch.append({"path": r["path"], "ext": r["ext"],
                                 "detected": magic})

    with_ind = [r for r in records if r.get("indicators")]
    with_dom = [r for r in records if r.get("unexpected_domains")]

    by_hash: dict[str, list[str]] = defaultdict(list)
    for r in records:
        if r.get("sha256"):
            by_hash[r["sha256"]].append(r["path"])
    duplicates = {h: p for h, p in by_hash.items() if len(p) > 1}

    dom_tot: dict[str, int] = defaultdict(int)
    ind_tot: dict[str, int] = defaultdict(int)
    for r in records:
        for d, i in (r.get("unexpected_domains") or {}).items():
            dom_tot[d] += i["count"]
        for i, c in (r.get("indicators") or {}).items():
            ind_tot[i] += c

    # -------- finding 1: honest completeness --------------------------------
    complete = (
        len(records) == total
        and not walk_errors
        and not after_walk_errors
        and not read_errors
        and not no_hash
        and not json_no_verdict
        and not changed
        and not appeared
        and not vanished
        and not link_files
        and not link_dirs
    )
    reasons = []
    if len(records) != total:
        reasons.append(f"inspected {len(records)} of {total} enumerated files")
    if walk_errors or after_walk_errors:
        reasons.append(f"{len(walk_errors)+len(after_walk_errors)} walk error(s)")
    if read_errors:
        reasons.append(f"{len(read_errors)} file(s) could not be read")
    if no_hash:
        reasons.append(f"{len(no_hash)} file(s) have no SHA-256")
    if json_no_verdict:
        reasons.append(f"{len(json_no_verdict)} .json file(s) got no parse verdict")
    if changed:
        reasons.append(f"{len(changed)} file(s) changed during the run")
    if appeared or vanished:
        reasons.append(f"tree changed: {len(appeared)} appeared, "
                       f"{len(vanished)} vanished")
    if link_files or link_dirs:
        reasons.append(f"{len(link_files)+len(link_dirs)} symlink/reparse "
                       f"point(s) refused - contents NOT verified")

    report = {
        "schema": "citizen-compass/snapshot-verification/2.0",
        "scanner_version": SCANNER_VERSION,
        "config_fingerprint": fingerprint,
        "generated_utc": now_iso(),
        "snapshot_path": str(snap),
        "read_only": True,
        "what_this_is_not": (
            "NOT a malware scan. No AV signatures, no archive unpacking, no "
            "binary analysis, no sandboxing. A real AV pass is still required "
            "before releasing a snapshot from quarantine."
        ),
        "coverage": {
            "inspection_complete": complete,
            "incomplete_reasons": reasons,
            "files_enumerated": total,
            "files_inspected": len(records),
            "files_unreadable": len(read_errors),
            "files_without_hash": len(no_hash),
            "json_files_found": len(json_files),
            "json_parsed_strictly": len(json_files) - len(json_structural),
            "json_structural_only": len(json_structural),
            "json_parse_failed": len(json_bad),
            "json_without_verdict": len(json_no_verdict),
            "symlinks_or_reparse_points_refused": len(link_files) + len(link_dirs),
            "files_changed_during_run": len(changed),
            "files_appeared_during_run": len(appeared),
            "files_vanished_during_run": len(vanished),
            "stale_journal_records_excluded": len(stale),
        },
        "findings": {
            "read_errors": len(read_errors),
            "json_parse_failures": len(json_bad),
            "extension_content_mismatch": len(ext_mismatch),
            "files_with_active_content_indicators": len(with_ind),
            "files_with_unexpected_domains": len(with_dom),
            "duplicate_hash_groups": len(duplicates),
            "walk_errors": len(walk_errors) + len(after_walk_errors),
            "link_like_entries": len(link_files) + len(link_dirs),
        },
        "indicator_totals": dict(sorted(ind_tot.items(), key=lambda kv: -kv[1])),
        "unexpected_domain_totals": dict(sorted(dom_tot.items(),
                                                key=lambda kv: -kv[1])),
        "detail": {
            "read_errors": [{"path": r["path"], "error": r["error"]}
                            for r in read_errors[:200]],
            "json_parse_failures": [
                {"path": r["path"], "error": r["json_error"],
                 "mode": r["json_mode"], "magic": r["magic"], "size": r["size"]}
                for r in json_bad[:200]],
            "extension_content_mismatch": ext_mismatch[:200],
            "files_with_active_content_indicators": [
                {"path": r["path"], "indicators": r["indicators"]}
                for r in with_ind[:200]],
            "files_with_unexpected_domains": [
                {"path": r["path"], "domains": r["unexpected_domains"]}
                for r in with_dom[:200]],
            "link_like_entries": (
                [{"path": r["path"], "kind": r["link_like"], "type": "file"}
                 for r in link_files[:100]] + link_dirs[:100]),
            "files_changed_during_run": [r["path"] for r in changed[:200]],
            "files_appeared_during_run": appeared[:200],
            "files_vanished_during_run": vanished[:200],
            "stale_journal_records": stale[:200],
            "walk_errors": (walk_errors + after_walk_errors)[:200],
        },
        "truncation_note": (
            "Detail lists cap at 200 entries. journal.jsonl beside this file "
            "holds every record untruncated - nothing was silently dropped."
        ),
    }

    atomic_write_json(out / "verification-report.json", report)
    atomic_write_text(
        out / "SHA256SUMS.txt",
        "".join(f"{r['sha256']}  {r['path']}\n"
                for r in records if r.get("sha256")))
    atomic_write_json(out / "duplicates.json", duplicates)   # always written

    log("-" * 72)
    log(f"files enumerated ....... {total}")
    log(f"files inspected ........ {len(records)}")
    log(f"json parsed strictly ... {len(json_files) - len(json_structural)}")
    log(f"json structural only ... {len(json_structural)}")
    log(f"json parse FAILURES .... {len(json_bad)}")
    log(f"ext/content MISMATCH ... {len(ext_mismatch)}")
    log(f"active-content hits .... {len(with_ind)} file(s)")
    log(f"unexpected domains ..... {len(with_dom)} file(s)")
    log(f"duplicate hash groups .. {len(duplicates)}")
    log(f"read errors ............ {len(read_errors)}")
    log(f"links/reparse refused .. {len(link_files) + len(link_dirs)}")
    log(f"changed during run ..... {len(changed)}")
    log(f"walk errors ............ {len(walk_errors) + len(after_walk_errors)}")
    log("-" * 72)
    log(f"INSPECTION COMPLETE: {complete}")
    for r in reasons:
        log(f"  incomplete because: {r}")
    log("Reminder: this is NOT a malware scan. A real AV pass is still "
        "required before quarantine release.")
    log("DONE. Nothing in the snapshot was modified.")
    log.close()

    return EXIT_OK if complete else EXIT_INCOMPLETE


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted. Progress is journalled - re-run to resume.",
              file=sys.stderr)
        sys.exit(130)
