"""
Citizen Compass — Handoff Generator

Produces LATEST_HANDOFF.md: one file that's always the current snapshot of
the project. You (or a brand-new AI) can open it or paste it in any time —
no need to hunt for the latest session notes.

It has three parts:

1. CURRENT STATE (auto) — rebuilt fresh every run from citizen-compass.ccpp:
   health score, ship/viewer counts, data file counts. Never hand-edit this,
   it gets overwritten every time.

2. RECENT UPDATES (append-only) — drop a small `.md` file into inbox/ with
   "update" in the filename or heading, containing just the new info, and
   it's appended as a new timestamped entry to a running log — nothing
   already logged is ever replaced or requires re-pasting. Shows the most
   recent entries newest-first; the full history always lives in
   docs/handoff_archive/_updates_log.md.

3. PROJECT NOTES — the body of the most recent *full* handoff-style
   document you dropped into inbox/ (filename/heading says "handoff" or
   "session archive"). This one still fully replaces on each drop — use it
   for a complete project-state rewrite, use an "update" doc for a small
   addition. Every raw doc you drop is archived untouched in
   docs/handoff_archive/ first — nothing is ever lost, only the *displayed*
   copy in LATEST_HANDOFF.md may be compressed.

Compression is done by your local Ollama model (qwen3:14b) if it's running
and reachable at localhost:11434. If it isn't, this falls back to showing
the raw handoff text unmodified — it never fails silently, and never
pretends compression happened when it didn't (check pipeline_log.txt).

Run any time for an on-demand refresh, no new file drop required:

    python generate_handoff.py

Requires ccpp.py in the same folder.
"""

import json
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent
CCPP_FILE = PROJECT_ROOT / "citizen-compass.ccpp"
LATEST_HANDOFF_PATH = PROJECT_ROOT / "LATEST_HANDOFF.md"
HANDOFF_ARCHIVE_DIR = PROJECT_ROOT / "docs" / "handoff_archive"
LATEST_RAW_PATH = HANDOFF_ARCHIVE_DIR / "_latest_raw.md"
LOG_FILE = PROJECT_ROOT / "pipeline_log.txt"
LEGACY_HANDOFF_SEED = PROJECT_ROOT / "CITIZEN_COMPASS_HANDOFF.md"

# --- optional local-AI compression ------------------------------------------
# Set to False to always show raw handoff text (no Ollama call at all).
USE_LOCAL_AI_COMPRESSION = True
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen3:14b"
OLLAMA_TIMEOUT_SECONDS = 120

HANDOFF_FILENAME_HINTS = ("handoff", "session_archive", "session-archive")
HANDOFF_HEADING_HINTS = ("HANDOFF", "SESSION ARCHIVE", "AI KNOWLEDGE BASE")

UPDATE_FILENAME_HINTS = ("update", "updates")
UPDATE_HEADING_HINTS = ("UPDATE", "UPDATES", "CHANGELOG")
UPDATES_LOG_PATH = HANDOFF_ARCHIVE_DIR / "_updates_log.md"
MAX_UPDATES_SHOWN = 20  # most recent entries shown in LATEST_HANDOFF.md; full history stays in the log file


def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def is_handoff_doc(path: Path, text: str) -> bool:
    name = path.stem.lower()
    if any(hint in name for hint in HANDOFF_FILENAME_HINTS):
        return True
    head = text[:500].upper()
    return any(hint in head for hint in HANDOFF_HEADING_HINTS)


def is_update_doc(path: Path, text: str) -> bool:
    """A small addition to append to the running log, as opposed to a full
    handoff doc that replaces PROJECT NOTES entirely. Checked *after*
    is_handoff_doc — a doc matching both is treated as a full handoff."""
    name = path.stem.lower()
    if any(hint in name for hint in UPDATE_FILENAME_HINTS):
        return True
    head = text[:500].upper()
    return any(hint in head for hint in UPDATE_HEADING_HINTS)


def compress_with_local_ai(raw_text: str):
    """Best-effort compression via local Ollama. Returns None on ANY failure
    (never raises) so callers always have a safe raw-text fallback."""
    if not USE_LOCAL_AI_COMPRESSION:
        return None

    prompt = (
        "Compress the following project handoff document into a tight "
        "briefing of no more than 25 bullet points. Preserve concrete "
        "specifics: file paths, counts, ship names, decisions made, and open "
        "issues. Do not add commentary or anything not present in the "
        "source text.\n\n---\n\n" + raw_text
    )
    payload = json.dumps({"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(
        OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT_SECONDS) as resp:
            result = json.loads(resp.read())
        compressed = result.get("response", "").strip()
        if compressed:
            log(f"Handoff compressed via local Ollama model ({OLLAMA_MODEL})")
            return compressed
        log("Ollama returned an empty response — using raw handoff text instead")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        log(f"Local AI compression unavailable ({e}) — using raw handoff text instead")
    except Exception as e:
        log(f"Local AI compression failed unexpectedly ({e}) — using raw handoff text instead")
    return None


def load_ccpp_stats():
    sys.path.insert(0, str(PROJECT_ROOT))
    try:
        from ccpp import CitizenCompassPacket
    except ImportError:
        log("⚠ ccpp.py not found in project root — LATEST_HANDOFF.md will be missing live stats")
        return None

    packet = CitizenCompassPacket()
    if CCPP_FILE.exists():
        packet.load(str(CCPP_FILE))
    else:
        if not packet.scan_project(PROJECT_ROOT):
            return None
        packet.save(str(CCPP_FILE))
    return packet


def build_auto_block(packet):
    if packet is None:
        return "**[UNKNOWN]** ccpp.py not found or scan failed — could not pull current project stats."

    scores = packet.scores
    crossref = packet.crossref
    inventory = packet.inventory

    lines = [
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
        "(auto-regenerated every time a file lands in inbox/ or this script runs — don't hand-edit this section)",
        "",
        f"**Project health score:** {scores.get('overall_health', '?')}/100",
        f"- Data completeness: {scores.get('data_completeness', '?')}%",
        f"- Viewer progress: {scores.get('viewer_progress', '?')}%",
        f"- Documentation: {scores.get('documentation', '?')}%",
        "",
        f"**Ships:** {crossref.get('ships_with_viewers', 0)} complete viewers / "
        f"{crossref.get('ships_total', 0)} total ({crossref.get('viewers_progress_pct', 0)}%)",
    ]

    ships = inventory.get("ships", {})
    complete = sorted(s["slug"] for s in ships.values() if s.get("viewer_complete"))
    if complete:
        lines.append(f"- Complete: {', '.join(complete)}")
    incomplete = sorted(s["slug"] for s in ships.values() if not s.get("viewer_complete"))
    if incomplete:
        shown = ", ".join(incomplete[:10])
        more = f" (+{len(incomplete) - 10} more)" if len(incomplete) > 10 else ""
        lines.append(f"- In progress / not started: {shown}{more}")

    lines.append("")
    lines.append("**Data layers:**")
    data_layers = inventory.get("data_layers", {})
    if data_layers:
        for name, data in data_layers.items():
            lines.append(f"- {name}: {data.get('file_count', 0)} files ({data.get('total_size_mb', 0)} MB)")
    else:
        lines.append("- (none detected)")

    lines.append("")
    lines.append(
        f"**Scripts:** {len(inventory.get('scripts', []))}  |  "
        f"**3D models:** {len(inventory.get('models', []))}  |  "
        f"**Docs:** {len(inventory.get('docs', []))}"
    )

    return "\n".join(lines)


def append_update(text: str, source_name: str):
    """Append one update entry to the running updates log. This never
    overwrites anything — each drop just adds a new timestamped entry, so
    you only ever need to write the new information, not the whole
    project history."""
    HANDOFF_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"### {timestamp} — {source_name}\n\n{text.strip()}\n"
    needs_leading_blank_line = UPDATES_LOG_PATH.exists() and UPDATES_LOG_PATH.stat().st_size > 0
    with open(UPDATES_LOG_PATH, "a", encoding="utf-8") as f:
        if needs_leading_blank_line:
            f.write("\n")
        f.write(entry)
    log(f"Appended update from {source_name} to updates log")


def _parse_update_entries():
    """Split the updates log back into individual timestamped entries."""
    if not UPDATES_LOG_PATH.exists():
        return []
    raw = UPDATES_LOG_PATH.read_text(encoding="utf-8")
    chunks = raw.split("\n### ")
    entries = []
    for i, chunk in enumerate(chunks):
        chunk = chunk.strip()
        if not chunk:
            continue
        entries.append(chunk if chunk.startswith("### ") else "### " + chunk)
    return entries


def build_updates_block():
    entries = _parse_update_entries()
    if not entries:
        return (
            "*No updates logged yet. Drop a small `.md` file into `inbox/` "
            "with \"update\" in the filename or heading — just the new "
            "information, nothing you've already logged — and it'll be "
            "appended here automatically, newest at the top.*"
        )
    newest_first = list(reversed(entries))
    shown = newest_first[:MAX_UPDATES_SHOWN]
    block = "\n\n".join(shown)
    remaining = len(newest_first) - len(shown)
    if remaining > 0:
        block += (
            f"\n\n*(+{remaining} older update(s) — full history in "
            "docs/handoff_archive/_updates_log.md)*"
        )
    return block


def _seed_raw_text_if_missing():
    """First-ever run: if nothing's been dropped into inbox yet but an
    existing CITIZEN_COMPASS_HANDOFF.md sits in the project root, use it to
    seed LATEST_HANDOFF.md instead of starting empty. Read-only — doesn't
    move or modify that file."""
    if LATEST_RAW_PATH.exists():
        return
    if LEGACY_HANDOFF_SEED.exists():
        HANDOFF_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
        text = LEGACY_HANDOFF_SEED.read_text(encoding="utf-8", errors="replace")
        LATEST_RAW_PATH.write_text(text, encoding="utf-8")
        log(f"Seeded LATEST_HANDOFF.md from existing {LEGACY_HANDOFF_SEED.name}")


def build_notes_block():
    _seed_raw_text_if_missing()

    if not LATEST_RAW_PATH.exists():
        return (
            "*No handoff document has been processed yet. Drop a handoff-style "
            "`.md` file into `inbox/` (filename or heading containing "
            "\"handoff\" or \"session archive\") and it'll appear here.*"
        )

    raw_text = LATEST_RAW_PATH.read_text(encoding="utf-8")
    compressed = compress_with_local_ai(raw_text)
    if compressed:
        return (
            compressed
            + "\n\n*(compressed by the local Ollama model from the most recently "
            "adopted handoff doc — the full original is kept in docs/handoff_archive/)*"
        )
    return (
        raw_text
        + "\n\n*(raw text of the most recently adopted handoff doc — local AI "
        "compression unavailable right now, showing it unmodified)*"
    )


def regenerate():
    packet = load_ccpp_stats()
    auto_block = build_auto_block(packet)
    updates_block = build_updates_block()
    notes_block = build_notes_block()

    content = (
        "# CITIZEN COMPASS — LATEST HANDOFF\n\n"
        "Copy/paste this whole file into a new AI conversation for instant "
        "context. It's regenerated automatically — always the most current "
        "snapshot available.\n\n"
        "---\n\n"
        "## CURRENT STATE (auto)\n\n"
        f"{auto_block}\n\n"
        "---\n\n"
        "## RECENT UPDATES (append-only, newest first)\n\n"
        f"{updates_block}\n\n"
        "---\n\n"
        "## PROJECT NOTES (from most recent full handoff doc)\n\n"
        f"{notes_block}\n"
    )
    LATEST_HANDOFF_PATH.write_text(content, encoding="utf-8")
    log(f"LATEST_HANDOFF.md regenerated ({len(content)} chars)")
    return LATEST_HANDOFF_PATH


if __name__ == "__main__":
    path = regenerate()
    print(f"Done. See {path}")
