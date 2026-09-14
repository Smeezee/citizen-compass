#!/usr/bin/env python3
"""Append one change line to sc-brain/plumbing/indexes/latest.md.

Usage:
  python sc-brain/plumbing/append_index.py cig-firehose/devtracker "new post 123" path/or/id
  python sc-brain/plumbing/append_index.py --shelf build-truth/live --summary "LIVE 4.10.1" --ref CURRENT.md

Safe to call from any watcher. Creates the log if missing. No network. No AI.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / "sc-brain" / "plumbing" / "indexes" / "latest.md"


def main() -> int:
    p = argparse.ArgumentParser(description="Append a SC Brain index line")
    p.add_argument("shelf", nargs="?", help="Shelf path under sc-brain/, e.g. cig-firehose/devtracker")
    p.add_argument("summary", nargs="?", help="Short what-changed text")
    p.add_argument("ref", nargs="?", default="", help="Optional path or id")
    p.add_argument("--shelf")
    p.add_argument("--summary")
    p.add_argument("--ref", default="")
    args = p.parse_args()

    shelf = args.shelf
    summary = args.summary
    ref = args.ref or ""
    # positional fallback when flags unused
    if shelf is None or summary is None:
        print("Need shelf and summary.", file=sys.stderr)
        return 2

    LOG.parent.mkdir(parents=True, exist_ok=True)
    if not LOG.exists():
        LOG.write_text(
            "# SC Brain — what’s new\n\n"
            "Append-only log. Watchers and importers add one line when something real changes.\n\n"
            "Format: `YYYY-MM-DD HH:MM | shelf | summary | path-or-id`\n\n---\n",
            encoding="utf-8",
        )

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = f"{stamp} | {shelf} | {summary} | {ref}\n".rstrip() + "\n"
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line)
    print(f"appended: {line.strip()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
