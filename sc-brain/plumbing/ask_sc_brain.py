#!/usr/bin/env python3
"""Tiny local ask surface for SC Brain. No AI. No network.

Usage:
  python sc-brain/plumbing/ask_sc_brain.py shelves
  python sc-brain/plumbing/ask_sc_brain.py recent
  python sc-brain/plumbing/ask_sc_brain.py find hardpoint
  python sc-brain/plumbing/ask_sc_brain.py tree
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _out(s: str) -> None:
    try:
        print(s)
    except UnicodeEncodeError:
        print(s.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8', errors='replace'))

ROOT = Path(__file__).resolve().parents[2]
BRAIN = ROOT / "sc-brain"
LATEST = BRAIN / "plumbing" / "indexes" / "latest.md"


def cmd_shelves() -> int:
    skip = {"plumbing", "_meta"}
    for p in sorted(BRAIN.iterdir()):
        if p.is_dir() and p.name not in skip and not p.name.startswith("."):
            readme = p / "README.md"
            blurb = ""
            if readme.exists():
                for line in readme.read_text(encoding="utf-8", errors="replace").splitlines():
                    if line.strip() and not line.startswith("#"):
                        blurb = line.strip().lstrip("\ufeff")[:100]
                        break
            _out(f"{p.name:16} {blurb}")
    return 0


def cmd_recent(n: int) -> int:
    if not LATEST.exists():
        print("No latest.md yet.")
        return 0
    lines = [
        ln for ln in LATEST.read_text(encoding="utf-8", errors="replace").splitlines()
        if ln.strip() and not ln.startswith("#") and not ln.startswith("---") and "|" in ln
    ]
    for ln in lines[-n:]:
        _out(ln)
    if not lines:
        print("(empty — watchers will append here)")
    return 0


def cmd_find(query: str) -> int:
    q = query.lower()
    hits = []
    for path in BRAIN.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".json", ".jsonl", ".txt"}:
            continue
        rel = path.relative_to(BRAIN).as_posix()
        if q in rel.lower():
            hits.append(rel)
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if q in text.lower():
            hits.append(rel)
    for h in hits[:50]:
        _out(h)
    if not hits:
        print("No hits.")
    elif len(hits) > 50:
        print(f"... and {len(hits) - 50} more")
    return 0


def cmd_tree() -> int:
    for path in sorted(BRAIN.rglob("*")):
        if path.is_dir():
            rel = path.relative_to(BRAIN).as_posix()
            if rel == ".":
                continue
            _out(rel + "/")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Ask SC Brain (local, free)")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("shelves", help="List top shelves")
    recent = sub.add_parser("recent", help="Show latest index lines")
    recent.add_argument("-n", type=int, default=20)
    find = sub.add_parser("find", help="Find files/text under sc-brain")
    find.add_argument("query")
    sub.add_parser("tree", help="List folder tree")
    args = p.parse_args()
    if args.cmd == "shelves":
        return cmd_shelves()
    if args.cmd == "recent":
        return cmd_recent(args.n)
    if args.cmd == "find":
        return cmd_find(args.query)
    if args.cmd == "tree":
        return cmd_tree()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
