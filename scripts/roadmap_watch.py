"""The roadmap watcher. R1-R3 of AMENDS_roadmap-watcher-board-1-is-wrong.

WHAT THIS ANSWERS, AND WHY IT IS NOT last_verified_patch
========================================================
R3. The site knows which patch its DATA was verified against. It does not know
what CIG has ANNOUNCED since. Those are different questions and this answers the
second one. Nothing here touches `last_verified_patch`.

Sleven had to tell C1 that the Nyx planets had moved. Every source C1 could
reach was two weeks stale, the Comm-Link roundup returned page metadata to a
fetch, and the only person in the loop who knew was him. The API had it the
whole time.

THE KEY IS CARD PRESENCE PLUS A CONTENT HASH. NEVER `time_modified`.
====================================================================
The amends is explicit: never key on the modification date, because the API
returns Aug 2024 for a card the UI renders as Aug 2021. So `time_modified`,
`time_created`, `order`, `thumbnail` and `importer_id` are excluded from the
hash by name - a card that only shuffles position or gets its timestamp
rewritten is NOT a change, and reporting it as one would train everybody to
ignore this.

What IS compared: the set of card ids per release, and a hash over each card's
name, body, release, released flag and status.

ONE CODE PATH FOR THE TIMER AND FOR "CHECK NOW"
===============================================
`--once` and a scheduled run call the same function with the same arguments.
The amends asks for this by name: "a second path is a second thing to be wrong."

R1 - A CHANGE IS ONLY USEFUL IF SOMEBODY READS IT
=================================================
A detected change writes a dated finding into docs/, naming the cards added,
removed and altered, with the board id and the fetch time. A watcher that
detects a change and files it nowhere is indistinguishable from one that
detected nothing.

R2 - THE COMM-LINK ROUNDUPS ARE NOT THE EVIDENCE
================================================
They are unreadable to a fetch and this does not try. The finding carries a
field for a roundup URL as a POINTER FOR A PERSON, and it is left empty rather
than guessed at. The API is the route.

WHAT THIS DOES NOT DO
=====================
It does not schedule itself. Registering a Windows scheduled task is hard rule
6 and is Sleven's to approve. It also does not act on a change: the watcher
reports, and whether a Nyx planet changes what this site does is Sleven's call.

Usage:
    python scripts/roadmap_watch.py --once          # check now
    python scripts/roadmap_watch.py --once --dry-run
    python scripts/roadmap_watch.py --show          # what is stored
"""

import argparse
import datetime
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "checks"))

OUT_DIR = os.path.join(REPO, "data-layer", "derived", "roadmap-watcher")
STATE = os.path.join(OUT_DIR, "state.json")
DOCS = os.path.join(REPO, "docs")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# The R0 gate is imported rather than reimplemented: the watcher refuses to run
# against a board that is not the live release view, at startup, every time.
import _verify_roadmap_board as R0  # noqa: E402

# EXCLUDED FROM THE HASH BY NAME. Every one of these can move without anything
# CIG announced having changed.
VOLATILE = {"time_modified", "time_created", "order", "thumbnail",
            "importer_id", "url_slug"}


def log(m):
    print(m, flush=True)


def card_hash(card):
    keep = {k: v for k, v in sorted(card.items()) if k not in VOLATILE}
    return hashlib.sha256(json.dumps(keep, sort_keys=True,
                                     ensure_ascii=False).encode("utf-8")).hexdigest()[:16]


def snapshot(board):
    """The state this watcher compares. Presence plus content, never dates."""
    payload = R0.fetch(board)
    info = R0.examine(payload, board)
    # R0's assertions, at startup, as the amends requires.
    if not info["unreleased_cards"] or not info["releases_4x_or_higher"]:
        raise R0.BoardError(
            "board %d is not the live release view - %d unreleased cards, %d "
            "releases 4.x or higher. Refusing to watch a board of finished "
            "history, which would report 'no change' forever and be right."
            % (board, info["unreleased_cards"], len(info["releases_4x_or_higher"])))

    cards, releases = {}, {}
    for rel in (payload["data"].get("releases") or []):
        rname = rel.get("name")
        releases[str(rel.get("id"))] = {"name": rname,
                                        "released": rel.get("released")}
        for c in (rel.get("cards") or []):
            cards[str(c.get("id"))] = {
                "name": c.get("name"), "release": rname,
                "released": c.get("released"), "status": c.get("status"),
                "h": card_hash(c),
            }
    return {"board": board, "cards": cards, "releases": releases,
            "counts": {"cards": len(cards), "releases": len(releases),
                       "unreleased_cards": info["unreleased_cards"]},
            "fetched_at_utc": datetime.datetime.now(datetime.timezone.utc)
                .isoformat(timespec="seconds")}


def diff(old, new):
    o, n = old.get("cards", {}), new.get("cards", {})
    added = [n[k] | {"id": k} for k in sorted(set(n) - set(o))]
    removed = [o[k] | {"id": k} for k in sorted(set(o) - set(n))]
    altered = []
    for k in sorted(set(o) & set(n)):
        if o[k].get("h") != n[k].get("h"):
            altered.append({"id": k, "name": n[k].get("name"),
                            "release": n[k].get("release"),
                            "was": {x: o[k].get(x) for x in ("name", "release",
                                                             "released", "status")},
                            "now": {x: n[k].get(x) for x in ("name", "release",
                                                             "released", "status")}})
    return {"added": added, "removed": removed, "altered": altered}


def write_finding(d, new, path):
    when = datetime.datetime.now().strftime("%Y-%m-%d")
    lines = [
        "# FINDING — the roadmap moved, %s" % when,
        "",
        "**Written by the roadmap watcher, not by a person.** It reports; whether",
        "any of this changes what the site does is Sleven's call.",
        "",
        "    board        %d (Release View)" % new["board"],
        "    fetched      %s" % new["fetched_at_utc"],
        "    cards now    %d across %d releases"
        % (new["counts"]["cards"], new["counts"]["releases"]),
        "",
        "Keyed on card presence and a content hash. **Not on `time_modified`** —",
        "the API returns dates that disagree with what the site renders, so a card",
        "that only had its timestamp rewritten is not reported here.",
        "",
    ]
    for title, key, fmt in (
            ("Added", "added", lambda c: "%s  —  %s" % (c.get("name"), c.get("release"))),
            ("Removed", "removed", lambda c: "%s  —  was on %s" % (c.get("name"), c.get("release"))),
    ):
        lines.append("## %s (%d)" % (title, len(d[key])))
        lines.append("")
        lines += ["    " + fmt(c) for c in d[key]] or ["    none"]
        lines.append("")
    lines.append("## Altered (%d)" % len(d["altered"]))
    lines.append("")
    if not d["altered"]:
        lines.append("    none")
    for c in d["altered"]:
        lines.append("    %s" % c.get("name"))
        for f in ("name", "release", "released", "status"):
            if c["was"].get(f) != c["now"].get(f):
                lines.append("        %-9s %r -> %r" % (f, c["was"].get(f), c["now"].get(f)))
    lines += [
        "",
        "## The Comm-Link roundup",
        "",
        "    not matched",
        "",
        "R2: the roundups are a POINTER FOR A PERSON and never the evidence. They",
        "return page metadata to a fetch, so nothing is claimed here. The API is",
        "the route and the API is what this read.",
        "",
        "---",
        "",
        "*roadmap_watch.py, %s*" % new["fetched_at_utc"],
        "",
    ]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


def run(board, write=True):
    """THE ONE CODE PATH. --once and a scheduled run both land here."""
    new = snapshot(board)
    log("  board %d: %d cards across %d releases, %d unreleased"
        % (board, new["counts"]["cards"], new["counts"]["releases"],
           new["counts"]["unreleased_cards"]))

    old = None
    if os.path.exists(STATE):
        with open(STATE, encoding="utf-8") as fh:
            old = json.load(fh)

    if old is None:
        log("  no previous state - recording the first one. Nothing to compare "
            "against yet, and that is said rather than reported as 'no change'.")
        if write:
            os.makedirs(OUT_DIR, exist_ok=True)
            with open(STATE, "w", encoding="utf-8") as fh:
                json.dump(new, fh, indent=1, ensure_ascii=False)
        return 0

    d = diff(old, new)
    n = len(d["added"]) + len(d["removed"]) + len(d["altered"])
    if not n:
        log("  no change since %s" % old.get("fetched_at_utc"))
        if write:
            with open(STATE, "w", encoding="utf-8") as fh:
                json.dump(new, fh, indent=1, ensure_ascii=False)
        return 0

    log("  CHANGED: %d added, %d removed, %d altered"
        % (len(d["added"]), len(d["removed"]), len(d["altered"])))
    for c in d["added"][:8]:
        log("    + %s (%s)" % (c.get("name"), c.get("release")))
    for c in d["removed"][:8]:
        log("    - %s (was %s)" % (c.get("name"), c.get("release")))
    for c in d["altered"][:8]:
        log("    ~ %s" % c.get("name"))

    if write:
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(DOCS, "FINDING_roadmap-change-%s.md"
                            % datetime.datetime.now().strftime("%Y-%m-%d"))
        write_finding(d, new, path)
        log("  wrote %s" % os.path.relpath(path, REPO))
        with open(STATE, "w", encoding="utf-8") as fh:
            json.dump(new, fh, indent=1, ensure_ascii=False)
    else:
        log("  --dry-run: no finding written, state not advanced")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="check now")
    ap.add_argument("--show", action="store_true", help="print the stored state")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--board", type=int, default=R0.RELEASE_BOARD)
    args = ap.parse_args()

    if args.show:
        if not os.path.exists(STATE):
            log("no state recorded yet")
            return 0
        with open(STATE, encoding="utf-8") as fh:
            s = json.load(fh)
        log("board %s, fetched %s" % (s.get("board"), s.get("fetched_at_utc")))
        log("  %s" % json.dumps(s.get("counts"), ensure_ascii=False))
        return 0

    if not args.once:
        ap.error("nothing to do: pass --once to check now. This script does not "
                 "schedule itself - registering a scheduled task is hard rule 6 "
                 "and is Sleven's to approve.")
    return run(args.board, write=not args.dry_run)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except R0.BoardError as exc:
        print("ROADMAP WATCH NOT PERFORMED: %s" % exc, file=sys.stderr)
        sys.exit(2)
