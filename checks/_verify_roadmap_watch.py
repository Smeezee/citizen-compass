"""Prove the roadmap watcher notices what matters and ignores what does not.
RULE16: INDEPENDENT - the diff is exercised with snapshot pairs
    constructed here, including the time_modified-only pair that must produce
    silence; the watcher cannot see what the fixture meant. The board refusal
    is checked against the real live API.


R1/R2 of AMENDS_roadmap-watcher-board-1-is-wrong-2026-08-27.

TWO FAILURES ARE POSSIBLE AND BOTH ARE BAD:

  a watcher that misses a real change      - the defect it was built to fix,
                                             which is how Sleven ended up
                                             telling C1 the roadmap had moved.
  a watcher that reports a change that is  - worse in practice, because it
  not one                                    trains everybody to ignore it.

The amends names the second one exactly: **never key on the modification date**,
because the API returns Aug 2024 for a card the UI renders as Aug 2021. So the
load-bearing assertion here is the NEGATIVE one - a card whose `time_modified`
moved and nothing else must produce silence.

Run:  python checks/_verify_roadmap_watch.py
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, HERE)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import roadmap_watch as W  # noqa: E402

RESULTS = []


def check(name, fn):
    try:
        fn()
    except AssertionError as exc:
        RESULTS.append(False)
        print("  FAIL  %s - %s" % (name, exc))
        return
    RESULTS.append(True)
    print("  pass  %s" % name)


def card(cid, name="A card", release="4.11", released="0", **extra):
    c = {"id": cid, "name": name, "release_id": "66", "released": released,
         "status": "In Progress", "body": "body text",
         "description": "body text", "category_id": "1",
         "time_created": "1760622364", "time_modified": "1760622364",
         "order": "1", "thumbnail": None, "importer_id": "x", "url_slug": "a-card"}
    c.update(extra)
    return c


def state(cards):
    return {"board": 1, "cards": {str(c["id"]): {
        "name": c["name"], "release": "4.11", "released": c["released"],
        "status": c["status"], "h": W.card_hash(c)} for c in cards},
        "releases": {}, "counts": {}, "fetched_at_utc": "t"}


# --------------------------------------------------------------- the cases

def t_added_is_reported():
    d = W.diff(state([card("1")]), state([card("1"), card("2", name="Nyx III")]))
    assert len(d["added"]) == 1, "an added card was not reported: %r" % d
    assert d["added"][0]["name"] == "Nyx III"
    assert not d["removed"] and not d["altered"]


def t_removed_is_reported():
    d = W.diff(state([card("1"), card("2")]), state([card("1")]))
    assert len(d["removed"]) == 1, "a removed card was not reported: %r" % d


def t_renamed_is_reported():
    d = W.diff(state([card("1", name="Nyx I")]),
               state([card("1", name="Nyx I and II")]))
    assert len(d["altered"]) == 1, "a renamed card was not reported: %r" % d
    assert d["altered"][0]["was"]["name"] == "Nyx I"
    assert d["altered"][0]["now"]["name"] == "Nyx I and II"


def t_released_flag_is_reported():
    d = W.diff(state([card("1", released="0")]), state([card("1", released="1")]))
    assert len(d["altered"]) == 1, "a card going released was not reported: %r" % d


def t_time_modified_alone_is_SILENCE():
    """THE ONE THE AMENDS WARNS ABOUT. A timestamp that moved is not news."""
    a = card("1", time_modified="1760622364")
    b = card("1", time_modified="1799999999", time_created="1799999999")
    d = W.diff(state([a]), state([b]))
    assert not (d["added"] or d["removed"] or d["altered"]), (
        "A CARD WHOSE ONLY CHANGE IS ITS TIMESTAMP WAS REPORTED AS A CHANGE. "
        "The API returns dates that disagree with what the site renders, so "
        "this would fire constantly and teach everybody to ignore it: %r" % d)


def t_order_and_thumbnail_alone_are_SILENCE():
    a = card("1", order="1", thumbnail=None, url_slug="a")
    b = card("1", order="9", thumbnail="pic.png", url_slug="b")
    d = W.diff(state([a]), state([b]))
    assert not (d["added"] or d["removed"] or d["altered"]), (
        "a card that only moved position or gained a thumbnail was reported "
        "as a roadmap change: %r" % d)


def t_identical_is_silence():
    d = W.diff(state([card("1"), card("2")]), state([card("1"), card("2")]))
    assert not (d["added"] or d["removed"] or d["altered"]), \
        "identical snapshots produced a change: %r" % d


def t_body_change_IS_reported():
    """The counterweight to the two silence tests: a real content edit must
    still be seen, or 'ignore the volatile fields' has been taken too far."""
    d = W.diff(state([card("1", body="old", description="old")]),
               state([card("1", body="Nyx II and III added", description="x")]))
    assert len(d["altered"]) == 1, \
        "a card whose BODY changed was not reported - the exclusion list is " \
        "too wide and real news is being dropped: %r" % d


def t_watcher_refuses_a_dead_board():
    """R0's assertion, at startup, every run - not once by hand months ago."""
    try:
        W.snapshot(2)          # the Squadron 42 board: no 4.x release at all
    except W.R0.BoardError as exc:
        assert "not the live release view" in str(exc), \
            "refused, but not for the expected reason: %s" % exc
        return
    raise AssertionError(
        "the watcher accepted board 2, which has no 4.x release. It would poll "
        "a board of finished history and report 'no change' forever, correctly.")


def main():
    print("Verifying the roadmap watcher notices change and ignores noise")
    check("an added card is reported", t_added_is_reported)
    check("a removed card is reported", t_removed_is_reported)
    check("a renamed card is reported", t_renamed_is_reported)
    check("a card going released is reported", t_released_flag_is_reported)
    check("a changed body IS reported", t_body_change_IS_reported)
    check("TIME_MODIFIED ALONE IS SILENCE", t_time_modified_alone_is_SILENCE)
    check("order/thumbnail/slug alone are silence",
          t_order_and_thumbnail_alone_are_SILENCE)
    check("CONTROL - identical snapshots are silence", t_identical_is_silence)
    check("the watcher refuses a board that is not the release view",
          t_watcher_refuses_a_dead_board)

    failed = RESULTS.count(False)
    print("\n%d checks, %d failed" % (len(RESULTS), failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
