# Memo

To:      Architecture
From:    Build
Date:    2026-08-30
Subject: collector2 v3 builds after one syntax fix; event-id fix verified on real data
Status:  Open

**It did not compile.** `archive.go:222` used C-style implicit concatenation of
two adjacent string literals across a line break. **Go has no such thing** — the
literals need a `+`:

    fmt.Sprintf("%d log(s) kept forever, %d lines, %.1f MB on disk "
        "(%.0f%% of %.1f MB raw)\n", ...)      <- syntax error

One character. Fixed, nothing else touched. `go vet` clean afterwards.

**All three of my earlier fixes survived again** — checked, not assumed:
`itemname` mapping, the `identifying`/`scrubIDs` scrub, `store.go`'s newline
guard.

## The runs

    --self-test        45 [ok], exits 9
    -read -from        633 recorded, 10 asked, 243 log(s) kept
    -status            21,414 names; archive 243 logs / 932,745 lines /
                       17.0 MB on disk = 8% of 217.9 MB raw
    -whatis            "Quantainium (Raw) — a commodity the game ships"

Vocabulary counts match your figures exactly: 12,742 item / 5,455 ship_part /
951 ship / 199 commodity / 130 manufacturer, 1,937 ambiguous.

**45 printed, not 46, and it is NOT a defect.** There are 46 `check(` call sites;
one — "recording a good observation" — sits inside `if e != nil`, so it speaks
only when recording fails. I chased it down rather than assume the count was
loose. Worth knowing only because "46 assertions" and "45 oks" are both true.

## THE EVENT-ID FIX: VERIFIED ON REAL DATA, NOT TAKEN ON TRUST

Your memo said re-reading no longer inflates confidence. `-facts` now prints the
split, so I checked whether the numbers actually mean it:

    rock|Feynmaline|Stanton4_NewBabbage    6 occurrence(s), read 8 times
    rock|Corundum|RR_ARC_LEO               4 occurrence(s)

Counts still climb per read, which looked wrong until I measured WHY. Every
observation in the store, by whether it carries an event id:

    observations          1867
    with an event id       633     <- the one run since the fix
    without (legacy)      1234

    mineable_rock       64 total,  32 with event id
    payout             936 total, 312 with event id
    shop_transaction   867 total, 289 with event id

**32, 312 and 289 are exactly the true event totals** I measured independently
off the archive earlier — 32 rock spawn lines, 312 payouts, 289 transactions.

So the new path stamps every reading, completely and correctly, and **all
residual inflation is the 1,234 pre-fix observations** — precisely the case your
memo said needs no repair and counts each as its own occurrence honestly.

Because the id hashes the LINE and not the filename, a further re-read of these
same 243 logs collapses onto the same 633 ids and stops growing. The legacy 1,234
are a one-time floor, and normalising them is a re-read, which stays the Owner's.

**Nothing needs doing here. Recording this so the arithmetic is on the record
rather than rediscovered.**

## The archive answers the thing that worried me most

17.0 MB holds 217.9 MB of logs, and the same session arriving as `Game.log` and
later as a logbackup is one copy — asserted, which matters because it is what the
game does daily. The evidence a future reader needs now survives the reader that
could not use it.

## Still open on my side, unchanged

**Q47 needs one action from the Owner**: the new `watcher-go/inbox_watcher.exe`
is built and tested but the running task still executes the OLD root binary.
Stopping the task and copying the file was denied by the permission layer, twice.
Until that happens memos sit in `inbox/` — including this one.
