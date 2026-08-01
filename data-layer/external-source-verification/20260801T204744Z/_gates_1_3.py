"""Gates 1-3 plus the pre-scan SHA-256 baseline for source 1 run 20260801T204744Z.

One pass over the snapshot: every file is read once, hashed, magic-byte
inspected, and (if .json) parsed. Writes:
  01_gates_1_3.json          - gate results
  01_prescan_sha256.json      - {name: [size, sha256]} for the alteration check
"""
import hashlib
import json
import sys
from pathlib import Path

RUN = "20260801T204744Z"
REPO = Path(__file__).resolve().parents[3]
D = REPO / "data-layer/external-sources/scunpacked-data/snapshots" / (RUN + ".partial")
M = REPO / "data-layer/external-source-verification" / RUN

SIGS = {
    b"MZ": "DOS/PE executable", b"\x7fELF": "ELF executable",
    b"PK\x03\x04": "ZIP archive", b"\x1f\x8b": "gzip", b"Rar!": "RAR archive",
    b"\xca\xfe\xba\xbe": "Java class/Mach-O", b"%PDF": "PDF",
    b"\x89PNG": "PNG", b"#!": "shell shebang",
}

files = sorted(p for p in D.rglob("*") if p.is_file())
print("files found: %d" % len(files), flush=True)

baseline = {}
type_flags = []
json_failures = []
json_ok = 0
read_errors = []
zero_byte = []

for i, p in enumerate(files, 1):
    rel = str(p.relative_to(D)).replace("\\", "/")
    try:
        size = p.stat().st_size
        if size == 0:
            zero_byte.append(rel)
        h = hashlib.sha256()
        head = b""
        with p.open("rb") as f:
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk:
                    break
                if not head:
                    head = chunk[:8]
                h.update(chunk)
        baseline[rel] = [size, h.hexdigest()]
    except OSError as e:
        read_errors.append({"file": rel, "error": "%s: %s" % (type(e).__name__, e)})
        continue

    # GATE 3 - magic bytes vs extension
    for sig, label in SIGS.items():
        if head.startswith(sig):
            type_flags.append({"file": rel, "signature": label})
    if p.suffix.lower() == ".json" and size > 0 and head.lstrip()[:1] not in (b"{", b"["):
        type_flags.append({"file": rel, "signature": "extension .json but does not begin with { or ["})

    # GATE 2 - every .json parsed individually
    if p.suffix.lower() == ".json":
        try:
            with p.open("r", encoding="utf-8") as f:
                json.load(f)
            json_ok += 1
        except Exception as e:
            json_failures.append({"file": rel, "error": "%s: %s" % (type(e).__name__, str(e)[:200])})

    if i % 5000 == 0:
        print("  ...%d/%d" % (i, len(files)), flush=True)

json_total = sum(1 for p in files if p.suffix.lower() == ".json")

# GATE 1 - files present
expected_present = {
    "items.json": (D / "items.json").is_file(),
    ".gitattributes": (D / ".gitattributes").is_file(),
    "ships/ dir": (D / "ships").is_dir(),
}
git_dir_absent = not (D / ".git").exists()

gate1 = (all(expected_present.values()) and git_dir_absent
         and not zero_byte and not read_errors and len(files) > 0)
gate2 = not json_failures and not read_errors
gate3 = not type_flags

report = {
    "run": RUN,
    "snapshot": str(D).replace("\\", "/"),
    "total_files": len(files),
    "total_bytes": sum(v[0] for v in baseline.values()),
    "gate_1_files_present": {
        "result": "PASS" if gate1 else "FAIL",
        "expected_present": expected_present,
        "git_directory_absent": git_dir_absent,
        "zero_byte_files": zero_byte,
        "read_errors": read_errors,
    },
    "gate_2_json_parses": {
        "result": "PASS" if gate2 else "FAIL",
        "json_files_found": json_total,
        "json_files_parsed_ok": json_ok,
        "parse_failures": json_failures,
        "note": "Every .json file parsed individually - full check, not sampled.",
    },
    "gate_3_file_type_inspection": {
        "result": "PASS" if gate3 else "FAIL",
        "files_inspected": len(files),
        "flagged": type_flags,
        "signatures_checked": sorted(v for v in SIGS.values()),
    },
}

(M / "01_gates_1_3.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
(M / "01_prescan_sha256.json").write_text(json.dumps(baseline, indent=0), encoding="utf-8")

print()
print("GATE 1 files present:        %s" % report["gate_1_files_present"]["result"])
print("   .git absent:             %s" % git_dir_absent)
print("   zero-byte files:         %d" % len(zero_byte))
print("GATE 2 json parses:          %s  (%d/%d parsed, %d failures)" % (
    report["gate_2_json_parses"]["result"], json_ok, json_total, len(json_failures)))
print("GATE 3 file-type inspection: %s  (%d flagged)" % (
    report["gate_3_file_type_inspection"]["result"], len(type_flags)))
if type_flags[:10]:
    for t in type_flags[:10]:
        print("     %s -> %s" % (t["file"], t["signature"]))
print()
print("PRE-SCAN BASELINE: %d files, %d bytes" % (len(baseline), report["total_bytes"]))
sys.exit(0 if (gate1 and gate2 and gate3) else 1)
