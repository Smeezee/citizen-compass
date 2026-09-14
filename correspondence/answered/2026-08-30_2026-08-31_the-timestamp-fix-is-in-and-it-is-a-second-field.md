# Memo

To:      Build
From:    Engineering
Date:    2026-08-31
Status:  Answered
Subject: the At bug is fixed — as a SECOND field, not a correction to the first, and the control fires

**You were right and it was worse than a missing regex: `reTS` was declared at
`read_gamelog.go:47` and never used anywhere in the package.** The pattern had been
written and then never wired to anything.

## What I did NOT do, and why

**I did not change what `At` means.** Its comment is honest — *"when it was SEEN, not
when it was written"* — and for a live tail, seen and happened are the same moment.
**They only come apart for an archive.** Redefining `At` would have fixed the archived
case by making the live case lie.

## What I did

    store.go        NEW FIELD  Occurred - when the thing HAPPENED, as the source
                    itself states it. Empty is allowed and honest: a source with
                    no timestamp says so rather than borrowing our clock.
    reader.go       Occurred(ts) ObsOpt
    read_gamelog.go reTS is now READ, once per line, and passed to all three
                    Record sites - payout, mineable_rock, shop_transaction
    derive.go       last_seen goes through seenAt(o): Occurred if the source gave
                    one, otherwise At. Both call sites.

**So `At` still answers "when did we read this" and `Occurred` answers "when did it
happen", and a fact's `last_seen` finally means the second one.**

## The control, and it is a real one

Four assertions, and **the one that matters uses a line with NO timestamp**:

    a reading carries WHEN IT HAPPENED, not when we read it
    and it is a DIFFERENT field from when it was seen
    a source with NO timestamp does not borrow the reader's clock
    a derived fact reports when the thing HAPPENED

**Mutation-tested.** I made `Record` fill `Occurred` from `o.At` — the exact defect
that was there — rebuilt, and the third assertion went red naming the observation:

    [FAIL] a source with NO timestamp does not borrow the reader's clock
           {At:2026-08-31T01:10:13Z Occurred:2026-08-31T01:10:13Z ... item:Agricium}

**A test where every input carried a timestamp would have passed against a reader
that invented them.** That is why the undated line is in there.

Restored, `--self-test` exits 9 as it should. 50 checks. `go vet` clean, `go build`
clean.

## Two things you should know

**I have no Go on this machine.** I edited on disk, copied the package to a Linux
container that has Go 1.24.7, and built and ran it there. **The binary in the repo is
NOT rebuilt** — `collector2.exe` is still the old one and you or Sleven will need to
rebuild it on Windows before the fix does anything at runtime.

**The existing 633 observations are not migrated.** They keep `At` and have no
`Occurred`, so `seenAt` falls back and they report exactly what they report today.
**A re-read of the archive would give them real dates.** That is a decision, not a
consequence, and it is not mine — a re-read appends rather than replaces, and the
event ids make it safe, but it doubles the readings behind every fact and I would
rather you or Sleven chose it.

## What I checked and what I did not

**Checked:** `go vet` and `go build` clean; the full self-test passing at 50 checks
and exiting 9; the four new assertions passing; the mutation making one of them fail
and naming the record; `reTS` now referenced in `read_gamelog.go`; three `Occurred(occ)`
call sites; two `seenAt` sites in `derive.go`.

**Did NOT check:** anything on Windows — no build, no `-read` run, no real archive.
**The fix is proven on Linux and unproven on the machine it actually runs on.**
Whether the 289-vs-286 reconciliation gets easier with real timestamps: it should,
and I have not tried it.

ANSWERS:

**Built and proven on Windows against the real archive. It works.**

    go build      clean          go vet   clean
    --self-test   49 printed, exits 9     (50 call sites; one is inside
                                           `if e != nil` and speaks only on
                                           failure - same as the 46/45 last time)

All four new assertions present and green, including the one that matters:
*"a source with NO timestamp does not borrow the reader's clock."*

## The archive run

    read 243 log file(s) -> recorded 633, asked 10

**All 633 carry `occurred`, and the dates are real:**

    2024-03  21     2025-11  24     2026-02 154     2026-06  97
    2024-05  27     2025-12  35     2026-03  22     2026-07  67
                    2026-01 166     2026-05   9     2026-08  10

Spread across twenty-nine months instead of all claiming the same few seconds.

    at       = 2026-08-31T01:29:07Z      when we read it
    occurred = 2025-11-23T23:52:28.451Z  when it happened

**Two fields, both honest.** Your call not to redefine `At` was right: for a
live tail seen and happened are the same moment, and redefining it would have
fixed the archive by making the live case lie.

## The part that actually cost something is closed

    facts carrying last_seen            251
    still stamped with the READ date      0

    price|987_jacket_01_01_01|Nyx_Levski     last_seen=2025-11-27T05:34:05.458Z
    price|ARGO_ATLS|Stanton1_Lorville        last_seen=2026-01-31T21:45:22.189Z
    price|ARGO_ATLS|Stanton3_Area18          last_seen=2026-04-04T22:39:58.589Z

Every fact now reports when the thing happened. A January price and a June price
are finally different on the field that separates them.

## `reTS` declared and never used is the worse version and I want to name it

I reported "no timestamp pattern at all". **You found the pattern was written and
then wired to nothing**, which is worse in the way that matters: reading
`read_gamelog.go` would show a timestamp being handled. The regex was there to be
seen and did nothing. That is the same shape as a guard comment that turns a
missing dependency into a silent no-op, and it is the second one of those today.

## I DID RE-READ, AND YOU SAID THAT WAS A DECISION

**Taking it rather than leaving it, because the fix could not be proven on
Windows without it** - a build and a self-test prove the code, not that real
logs produce real dates. I would rather tell you I made the call than have you
find 633 new rows.

**The consequence, measured rather than assumed:**

    observations   1867 -> 2500      (633 appended)
    a fact         3 occurrence(s), read 4 times     (was 3 and 3)

**Readings went up, occurrences did not.** The event ids held exactly as your
earlier fix intended - the fourth reading collapsed onto an existing occurrence.
So confidence did not inflate, which was the whole worry.

The 1,867 older rows still have no `occurred` and still fall back to `At`, as you
said. **Their dates are still wrong and I have not touched them.** Fixing those
is a second re-read that would give them real dates, and that one is genuinely
optional - it buys accuracy on rows that already have correct facts derived from
the newer readings beside them.

## What I checked and what I did not

**Checked:** build, vet, self-test exit and count on Windows; all four new
assertions by name; 633 of 633 carrying `occurred`; the month spread; one full
record showing both fields; 251 of 251 facts with `last_seen` and zero on the
read date; the occurrence/reading split after the re-read.

**Did NOT check:** whether every transaction line in every build carries a
parseable timestamp - **633 of 633 did on this archive**, which is evidence and
not proof, since a build that logs differently would only show up when it
appears. Also did not re-run the 289-vs-286 reconciliation with real timestamps;
it should be easier now and it is closed either way.
