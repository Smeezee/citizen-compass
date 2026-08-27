# FINDING — Board 1 *is* the release view, and Nyx I-III are all on 4.11

**Written by Code, 2026-08-27. Corrects
`AMENDS_roadmap-watcher-board-1-is-wrong-2026-08-27.md`.**
**R0 of that amends: find the real board before writing anything that polls one.**

---

## The correction

The AMENDS says:

> **Board 1 is not the current release view. It returns 2018.** Fetched
> 2026-08-27, it answers with releases **3.1 through 3.3.5**, all marked
> released... No 4.x anything. No Nyx.

Fetched from this machine the same day, `GET /api/roadmap/v1/boards/1` returns:

    name  "Release View"    slug  "Release-View"
    39 releases, running 3.1 -> 3.2 -> ... -> 4.11 -> "Star Citizen 1.0"
    12 of them numbered 4.x
    8 unreleased releases: 3.8, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11, Star Citizen 1.0
    518 unreleased cards

**The 2018 entries are the START of the list, not the whole of it.** Reading the
first few and stopping is an easy mistake and it inverted the conclusion.

**So the original work order's endpoint was right.** There is no wrong-board
defect to fix. What the AMENDS asked for as a consequence — R0, a check that
refuses a board of finished history — is still worth having, and now exists.

    board 1   Release View   39 releases, 12 x 4.x, 518 unreleased cards
    board 2   Squadron 42    10 releases, no 4.x at all, newest Q3 2020
    board 3   does not exist  {"success":0,"code":"ErrInvalidObject"}

Board 2 is the control: a real board, HTTP 200, with unreleased cards and no
4.x release. A check that cannot tell it from the release view is not checking.

## Sleven was right about Nyx, and the API had it all along

He told C1 about a roadmap change on the Nyx planets in 4.11. C1 could not
confirm it: every source it could reach was 13-14 August and said Nyx I only.

The live board says:

    4.11   Nyx I     released=0
    4.11   Nyx II    released=0
    4.11   Nyx III   released=0

All three, on 4.11, all unreleased. Alongside them on that release: the Tiburon
as a Wikelo offering, Genesis Planet Tech v5, Starchitect, and four weapons.

**The article route was the blocked one; the API was never blocked.** That is
the whole argument for building the watcher on the API and treating the
Comm-Link roundups as a pointer for a person — which is what R2 already says.

## R0's check exists and is proven

`checks/_verify_roadmap_board.py`

    python checks/_verify_roadmap_board.py            board 1: GREEN
    python checks/_verify_roadmap_board.py --control  board 2: 1 FAIL, CONTROL PASSED

It asserts the polled board carries at least one unreleased card AND at least
one release numbered 4.x or higher, and it is meant to run at startup and refuse
— not warn — because the failure it guards against is a watcher reporting
"no change" forever, correctly, about history.

The board id and the evidence are written to
`data-layer/derived/roadmap-watcher/MANIFEST.json`, including this correction.

## Not done

Only R0. Nothing that polls on a timer has been built, and no roadmap change has
been filed anywhere. R1, R2 and R3 are untouched.

---

*Code, 2026-08-27.*
