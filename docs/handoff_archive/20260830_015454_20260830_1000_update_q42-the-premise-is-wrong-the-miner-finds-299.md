# Update — Q42: the miner is not broken. It finds 299 transactions across all four families, and the regex needed no change.

**2026-08-30 15:00 UTC / 2026-08-30 10:00 local · Code (background session)**

**The order's premise does not survive the measurement, and the order is what
made that visible: *"run the miner over the FULL archive - 243 files, 208 MB,
not one session."* Run that way, transactions is not zero.**

    archive: 244 file(s), 208.3 MB

    extractor              verified   hits
    transaction            true       299
    location_inventory     true       1041
    quantum_route          true       339
    ship_class             true       23648
    mission_template       true       2115
    mission_objective      true       7670
    game_tip               true       3383
    equipment              true       16876
    mission_payout         true       312
    contract               true       948
    actor_death            true       121
    vehicle_destroyed      true       11
    mineable_rock          true       20
    object_container       false      0
    spawn_location         false      0
    location_inventory_name false     0

## AGAINST THE PYTHON DIG, WHICH IS THE ONLY HONEST COMPARISON

    Python 2026-08-07        item 286   commodity 10    233 sessions
    Go today                 item 289   commodity 10    244 files

    family commodity buy      1
    family commodity sell     9
    family item buy         279
    family item sell         10

**All four transaction families the header names are present.** Commodity
matches exactly at 10. Item is 289 against 286 - three more, which is what a
larger archive read eleven files later should look like, not a discrepancy.

## SO NOTHING IS CHANGED, AND THAT IS THE DELIVERABLE

**I did not touch `reMineTxn`.** The order said not to before a failing line was
in front of me. **There is no failing line, because there is no failure** - and
changing a working pattern on the strength of a wrong premise is exactly what
the instruction was protecting against.

**The `transactions: 0` was real but it was measuring one session.** A single
Game.log from a player who did not shop that session contains no
`SShopBuyRequest`, and zero is the correct answer to that question. The
extractor's `Verified: true` is also correct: the pattern is confirmed by 299
live samples.

**The two zeros that remain are the two UNVERIFIED patterns**, plus
`location_inventory_name`, which the file already documents as speculative -
1038 RequestLocationInventory lines across the archive and not one carrying
`name="`. **Every zero in that table is a zero the file already predicted.**

## AND ONE FIGURE IN THE HEADER IS STALE

    header says   240 SECONDS over the real archive
    measured      35.1 seconds, 244 files, 208.3 MB

**The reasoning around it still stands** - it is unbounded work proportional to
how much someone has played, and isolating it from the selftest was right. But
the number a future reader would plan against is off by a factor of seven.
`gamelog_mine.go` is not in `OWNERS.md`; I am reporting the figure rather than
editing someone's file to correct a comment.

## THE DIAGNOSTIC

`citizen-collector/zz_q42_archive_test.go`. A test file, so it never reaches the
shipped binary; gated behind `CC_Q42=1`, so nobody reads 208 MB of somebody's
play history by accident - which is the header's own complaint about the
selftest that did exactly that; and it writes to `t.TempDir()`. It reports the
program's own per-extractor accounting via `buildExtractors`, not a second count
written by me.

    CC_Q42=1 go test -run Q42 -v -timeout 40m
