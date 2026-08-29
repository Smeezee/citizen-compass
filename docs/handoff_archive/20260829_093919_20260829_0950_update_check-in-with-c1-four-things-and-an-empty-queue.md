# Update — check-in with C1: Q20 is pushed, Code's queue is empty, and four things are waiting on C1. One of them is a single line.

**2026-08-29 09:50 local · Code (background session) · addressed to C1**

Sleven asked me to check in with you. I have no channel to you that I own —
`NEXT.md` is yours and I do not write it — so this is the handoff, which is the
path `OWNERS.md` leaves open.

**Everything below was measured this morning, not read off the board.**

## 1. HISTORY MOVED. `4710d30` IS PUSHED.

    4710d30   383 files changed, 14,043 insertions, 17,912 deletions
    1a1b4b7..4710d30  main -> main
    working tree      clean, 0 entries

Sleven gave the go-ahead in session, so rule 2 is satisfied. Staged by path,
never `git add -A`; `_to_delete/` contributed 0 files, checked in the index
before and in `git log -1 --name-only` after. **Nothing went to the live site.**

Your `data-layer/derived/hardpoint-placement/` (285 files),
`holo-hardpoints-align/` (3) and `crafting-demand/` (1) are all in it, along
with `build_hardpoint_placement.py` and `build_hardpoint_overlay.py`. **If you
have uncommitted work on the Cowork mount, it is not in this commit and I did
not go looking for it.**

## 2. Q7's LAST LABEL IS YOURS, AND IT IS ONE LINE

Run just now rather than quoted:

    RULE 16 LABELS - 105 check(s)
      labelled            104  (55 INDEPENDENT, 49 UNPROVEN)
      unlabelled          1
      malformed label     0

    $ grep -c RULE16 checks/_verify_panel_dismiss.mjs
    0

`_verify_panel_dismiss.mjs` is yours in `OWNERS.md`. **I am not writing a line
into your file to close my own queue item** — that is the exact move rule 14
exists against. One `RULE16: <INDEPENDENT|UNPROVEN> - <reason>` line from you
and Q7 is 105 of 105.

**Mind the separator.** `malformed label 0` is true today and the gate now tells
the two apart, but the fourth comma was two hours after the third.

## 3. AN OWNERSHIP GAP, IN THE DIRECTORY WHERE A FILE WENT MISSING

    data-layer/derived/holo-hardpoints-align/    yours
    data-layer/derived/holo-hardpoints/          NOBODY'S

`_verify_owners.py` passes — A, B and C all green — because it validates the
paths that are listed. **It cannot see a path nobody claimed.** Your own words:
*"a path that is not in this file has no declared owner. That is not permission;
it is a gap, and finding one is worth reporting."*

**And it is the directory where rule 1 was not followed.**
`loadout_marker.pre-C1-20260828.js` was **deleted** from the working tree rather
than moved to `_to_delete/`, and `pre-C1-20260829.js` replaced it. Content is
safe in `1a1b4b7` and both the delete and the replacement are recorded in
`4710d30`'s message rather than quietly absorbed. **I did not do it and I cannot
tell which session did** — which is itself the argument for the directory having
a name against it. `OWNERS.md` is yours; the assignment is your call.

## 4. THE FOURTH COMMA WANTS A `docs/DECISION_*`

Your note says it plainly — *worth a `docs/DECISION_*` rather than a fifth
occurrence* — and it has now cost you an hour and me three dry-run cycles. I
have not written it: the format is the shared contract and I did not want to
rule on it alone. **Yours or mine?** I will write it today if you say mine.

## 5. YOUR OFF-HULL TEN ARE ON NOBODY'S QUEUE

`FINDING_four-hulls-draw-a-dot-in-empty-space-2026-08-29.md` — 2,193 dots, 87.2%
exactly on the hull, ten that are not:

    BANU_Defender   port 50 @19px, port 51 @38px      DRAK_Corsair  3 of 15
    TMBL_Storm_AA   port 4 @15px                      VNCL_Glaive   port 43 @16px

It is committed and it is real, and **it is not an item on any queue.** The
Defender is also a client-record hull, which is the set I drove through a browser
at 08:40 — that control proves the dots DRAW; it cannot say they draw in the
right place, and the label says so.

## WHAT I NEED FROM C1

    the one line in _verify_panel_dismiss.mjs     closes Q7 at 105 of 105
    an owner for data-layer/derived/holo-hardpoints/
    the DECISION doc on the separator             yours or mine
    whether the off-hull ten become Q21
    what is next                                  Code's queue is empty

**One thing is mine and I am not passing it to you:** the sweep's own
`_verify_deploy_drift.py` rebuilds the artifacts other controls read, which
perturbs the measurement and destroyed a "before" copy I needed on the 28th. I
have flagged it twice and not ruled. I will rule on it rather than ask.

Going live is Sleven's and stays off the queue.
