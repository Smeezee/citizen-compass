"""R0 - the board the roadmap watcher polls is the LIVE release view.

Order: docs/AMENDS_roadmap-watcher-board-1-is-wrong-2026-08-27.md, R0.
    "Write the check that could fail: assert the polled board contains at least
     one unreleased card and at least one release numbered 4.x or higher. A
     board that answers only with released history must fail the control,
     loudly, at startup - not after months of silence."

THE DEFECT THIS EXISTS TO CATCH
===============================
A watcher pointed at a board of finished history polls every four hours and
correctly reports that nothing ever changed. No error, no empty response, no
crash - a green watcher watching a museum. That is why this runs AT STARTUP and
refuses rather than warning.

WHAT THE PROBE ACTUALLY FOUND, 2026-08-27
=========================================
The AMENDS says board 1 "is not the current release view, it returns 2018".
**That is not what the endpoint returns.** Board 1 is named "Release View",
slug "Release-View", and carries 39 releases running from 3.1 to
"Star Citizen 1.0" - including twelve 4.x releases and eight unreleased ones.
The first few entries are indeed 2018-era, which is what that reading saw; the
list continues.

    board 1   Release View        39 releases, 12 of them 4.x, 8 unreleased
    board 2   Squadron 42         10 releases, none 4.x, newest is Q3 2020
    board 3   does not exist      {"success":0,"code":"ErrInvalidObject"}

So the work order's endpoint was right and board 1 is the one to poll. This
check is what makes that claim falsifiable rather than a note in a document.

Board 2 is kept as the CONTROL: it is a real board, it answers 200, it has
unreleased cards - and it has no 4.x release at all. A check that cannot tell it
apart from the release view is not checking anything.

Usage:
    python checks/_verify_roadmap_board.py                 # assert board 1
    python checks/_verify_roadmap_board.py --board 2       # assert board 2
    python checks/_verify_roadmap_board.py --control       # board 2 MUST fail
    python checks/_verify_roadmap_board.py --write-manifest
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "data-layer", "derived", "roadmap-watcher")
API = "https://robertsspaceindustries.com/api/roadmap/v1/boards/%d"
UA = "citizen-compass roadmap watcher (unofficial fan site)"
RELEASE_BOARD = 1
CONTROL_BOARD = 2
MIN_MAJOR = 4          # "4.x or higher", per R0


class BoardError(RuntimeError):
    pass


def fetch(board):
    req = urllib.request.Request(API % board,
                                 headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            if r.status != 200:
                raise BoardError("board %d returned HTTP %s" % (board, r.status))
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        # Hard rule 9: a blocked or failing fetch is the answer. It is reported,
        # never routed around.
        raise BoardError("board %d could not be fetched: %r. Reported as NOT "
                         "CHECKED - not retried by another route." % (board, exc))


def major_of(name):
    m = re.match(r"^\s*(\d+)", str(name or ""))
    return int(m.group(1)) if m else None


def examine(payload, board):
    if not payload.get("success"):
        raise BoardError("board %d: %s" % (board, payload.get("msg") or payload))
    data = payload.get("data") or {}
    releases = data.get("releases") or []
    unreleased_cards, four_plus, newest = 0, [], None
    for rel in releases:
        maj = major_of(rel.get("name"))
        if maj is not None and maj >= MIN_MAJOR:
            four_plus.append(rel.get("name"))
        for card in (rel.get("cards") or []):
            if not card.get("released"):
                unreleased_cards += 1
        if maj is not None and (newest is None or maj > newest):
            newest = maj
    return {
        "board": board,
        "name": data.get("name"),
        "slug": data.get("url_slug"),
        "releases": len(releases),
        "releases_4x_or_higher": four_plus,
        "unreleased_cards": unreleased_cards,
        "highest_major": newest,
    }


RESULTS = []


def check(cond, label, detail=""):
    RESULTS.append(bool(cond))
    print("  %s %s%s" % ("ok  " if cond else "FAIL", label,
                         ("  " + detail) if (detail and not cond) else ""))
    return cond


def assert_live(info):
    check(info["unreleased_cards"] > 0,
          "the board carries at least one UNRELEASED card  (%d)" % info["unreleased_cards"],
          "a board of finished history would poll green forever")
    check(len(info["releases_4x_or_higher"]) > 0,
          "and at least one release numbered %d.x or higher  (%d)"
          % (MIN_MAJOR, len(info["releases_4x_or_higher"])),
          "highest major seen was %r - this is not the live release view"
          % info["highest_major"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--board", type=int, default=RELEASE_BOARD)
    ap.add_argument("--control", action="store_true",
                    help="run against the known-bad board; it MUST fail")
    ap.add_argument("--write-manifest", action="store_true")
    args = ap.parse_args()

    board = CONTROL_BOARD if args.control else args.board
    print("=" * 66)
    print("R0 - IS BOARD %d THE LIVE RELEASE VIEW?" % board)
    if args.control:
        print("CONTROL MODE: board %d is the Squadron 42 board. It MUST fail." % board)
    print("=" * 66)

    info = examine(fetch(board), board)
    print("\n  %r  slug=%r  %d releases, highest major %s"
          % (info["name"], info["slug"], info["releases"], info["highest_major"]))
    print("")
    assert_live(info)

    failed = RESULTS.count(False)
    print("")
    if args.control:
        if failed:
            print("CONTROL PASSED: %d assertion(s) failed against a board that is not "
                  "the release view. This check can tell them apart." % failed)
            return 0
        print("CONTROL FAILED: the Squadron 42 board passed. This check cannot "
              "distinguish a live board from a dead one, and its green result on "
              "board %d means nothing." % RELEASE_BOARD)
        return 3

    if failed:
        print("RED - board %d is not the live release view." % board)
        return 1

    if args.write_manifest:
        os.makedirs(OUT_DIR, exist_ok=True)
        raw = json.dumps(info, sort_keys=True).encode("utf-8")
        man = {
            "generated_by": "checks/_verify_roadmap_board.py --write-manifest",
            "order": "docs/AMENDS_roadmap-watcher-board-1-2026-08-27.md (R0)",
            "verified_at_utc": datetime.datetime.now(datetime.timezone.utc)
                .isoformat(timespec="seconds"),
            "endpoint": API % board,
            "board_id": board,
            "evidence": info,
            "evidence_sha256": hashlib.sha256(raw).hexdigest(),
            "control_board": CONTROL_BOARD,
            "correction": (
                "AMENDS_roadmap-watcher-board-1-is-wrong states that board 1 is not "
                "the current release view and returns 2018. The endpoint returns 39 "
                "releases from 3.1 to Star Citizen 1.0; the 2018 entries are the "
                "start of the list, not the whole of it. Board 1 IS the Release View."),
        }
        path = os.path.join(OUT_DIR, "MANIFEST.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(man, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
        print("wrote %s" % os.path.relpath(path, REPO))

    print("GREEN - board %d is the live release view." % board)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BoardError as exc:
        print("NOT CHECKED: %s" % exc, file=sys.stderr)
        sys.exit(2)
