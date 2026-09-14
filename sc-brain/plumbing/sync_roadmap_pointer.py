#!/usr/bin/env python3
"""Copy a slim roadmap summary into sc-brain/cig-firehose/roadmap/CURRENT.md.

Reads roadmap-watcher-state.json only. No network. No AI.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / "roadmap-watcher" / "roadmap-watcher-state.json"
OUT_DIR = ROOT / "sc-brain" / "cig-firehose" / "roadmap"
OUT = OUT_DIR / "CURRENT.md"


def main() -> int:
    if not STATE.exists():
        print(f"Missing {STATE}", file=sys.stderr)
        return 1
    data = json.loads(STATE.read_text(encoding="utf-8"))
    # Keep summary small — keys vary; dump a short inventory
    keys = sorted(data.keys()) if isinstance(data, dict) else []
    size = STATE.stat().st_size
    mtime = datetime.fromtimestamp(STATE.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Roadmap watcher — current pointer",
        "",
        f"- **Source file:** `roadmap-watcher/roadmap-watcher-state.json`",
        f"- **File mtime:** {mtime}",
        f"- **Size:** {size} bytes",
        f"- **Top-level keys:** {', '.join(keys) if keys else '(not a dict)'}",
        "",
        "Full board payload stays in the watcher state file (large).",
        "Do not duplicate it into git — this pointer is the SC Brain entry.",
        "",
        f"Synced: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
    ]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    # index line
    append = ROOT / "sc-brain" / "plumbing" / "append_index.py"
    if append.exists():
        import subprocess
        subprocess.run(
            [sys.executable, str(append), "cig-firehose/roadmap", "synced CURRENT.md from roadmap-watcher state", str(OUT.relative_to(ROOT))],
            check=False,
        )
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
