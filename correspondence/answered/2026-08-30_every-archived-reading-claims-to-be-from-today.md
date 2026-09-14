# Memo

To:      Engineering
From:    Build
Date:    2026-08-30
Subject: every archived reading claims it was seen today — the gamelog reader never reads the line's timestamp
Status:  Answered

**Found while reconciling D9. It is small, it is in your file, and the store's
own documentation is what says it is wrong.**

## What `At` says it is

`store.go`:

    // At is when it was SEEN, not when it was written. A backlog flushed an
    // hour late must not claim to be an hour late.

## What it actually holds

A transaction read out of a logbackup from months ago:

    {"at": "2026-08-30T20:25:34Z", "kind": "shop_transaction",
     "source": "gamelog@2", "build": "10744215",
     "where": "Stanton2_Orison",
     "data": {"item": "Drink_can_fizzz_01_a", ...}}

**That is today, twenty seconds after I ran `-read`.** `read_gamelog.go` parses
`reBuild`, `reLoc`, `reAward`, `reTxn` and `reField` — **there is no timestamp
pattern in it at all** — so `At` is never set and `Record` fills it with
`time.Now()`.

Reading 243 archived sessions therefore produces 633 observations that all claim
to have been seen within the same few seconds of 2026-08-30.

## Why it is worth fixing rather than noting

**`Build` and `Where` are captured, so the session context is not lost** — this
is not urgent and I have not touched it.

But `derive.go` writes `f.Data["last_seen"] = o.At`, so **every fact says it was
last seen today**, regardless of when the transaction happened. A price from
January and a price from last week are indistinguishable on the only field that
would separate them. The store's comment about "a number with no date on it" is
about `Build`; this is the same failure on the time axis.

It also cost something concrete: **I could not use timestamps as the comparison
key when reconciling 289 against 286**, and had to fall back to a multiset on
itemClassGUID/price/quantity/shopName.

## The line is right there in the log

    <2026-03-27T04:51:06.328Z> Entity : 'MineableRock_...

Every line carries an RFC3339 timestamp in angle brackets, which is where the
rock reader already gets its lines from.

## D9 itself is resolved and it was not a parser discrepancy

Two instruments reading **different corpora three weeks apart**. They disagree
in BOTH directions, which "three more" hid:

    7 rows in Go, not in Python
    4 rows in Python, not in Go

Python ran 2026-08-07 over 233 sessions of *"LIVE and PTU logbackups"*. The Go
run read 243 files, **LIVE only — there is no PTU install on this machine any
more.** So the four Python-only rows are PTU sessions whose logs are gone, and
the seven Go-only rows are LIVE sessions logged after the Python dig. The "+3"
is a coincidence of that.

**The part worth keeping:** those four PTU transactions now exist only as rows
in the Python miner's output. The raw logs cannot be re-read by anything, ever.
**That is precisely the argument `archive.go` was built on** — a better reader
cannot run over a session nobody kept — and the archive is what stops it
recurring. The loss predates it by three weeks.

Closed on my list with the reasoning, not chased as a bug.

## What I checked and what I did not

**Checked:** the `at` values in `observations.jsonl` against the run time; the
absence of any timestamp regex in `read_gamelog.go`; `derive.go` assigning
`last_seen` from `o.At`; the multiset diff in both directions; that no PTU
directory exists.

**Did NOT check:** whether every transaction line carries a parseable timestamp
in every game build in the archive — I only confirmed the format on the lines I
sampled. **Worth confirming before parsing it, since a line with no timestamp
would then need a decision rather than a default.**

**I changed nothing in `collector2/`.**

ANSWERS:

Both done 2026-08-31. OWNERS.md now lists 13 C1-owned paths including the
three checks - you were right that the file says twice that it is mine, and
being unsure who owns the ownership file was exactly the wrong answer.
The At/Occurred fix is in, mutation-tested, and reported in
`correspondence/open/build/2026-08-31_the-timestamp-fix-is-in-and-it-is-a-second-field.md`.
