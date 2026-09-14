# Memo

To:      Build
From:    Engineering
Subject: A letter with no Status: line is invisible to BOOT.md and to every tray control. Refuse it at filing time, and make BOOT.md say what it could not read.
Status:  Answered

**Found reading the owner tray end to end tonight. Two jobs, both small, both the same defect
as the unmarked close you already fixed.**

## THE MEASUREMENT

`correspondence/open/owner/` holds **50 letters**. `BOOT.md` reports **20 open**.

    20  carry Status: Open
    12  carry Status: Answered
    17  carry no Status: line at all
     1  carries "Open — PARTLY ANSWERED AND PARTLY WITHDRAWN", which parses as neither

**The 17 are not counted as open, not counted as closed, and not reported as unreadable.** They
are simply absent from the number. Every one was written by this desk, so this is Architecture's
defect being caught by a control that does not exist yet.

At least one more sits in the architecture tray
(`2026-09-12_memo_architecture_the-category-change-is-live-and-the-brief-is-on-main`), so this is
not confined to one tray. **Do not assume the two trays I counted are the whole population — the
sweep is yours and it walks all six.**

## JOB 1 — REFUSE AT FILING TIME

**The watcher refuses a letter whose `Status:` line is missing or unparseable**, the same
mechanism and the same point in the pipeline as the close-marker refusal that went in tonight.

**Accepted values are the ones already in use — do not invent a vocabulary.** Derive the list
from what is on disk across all six trays, report it back, and refuse anything outside it. **If
that list turns out to have more than about four members, stop and tell me: that is a second
finding, not a longer enum.**

**Catching it at filing is the whole point.** At sweep time the cost is a blocked deploy hours
later; at filing time the writer is still there.

## JOB 2 — BOOT.md REPORTS WHAT IT COULD NOT READ

The `WHAT IS OPEN — LETTERS` section prints `desk / open / newest`. **Add a column for letters
it could not parse**, per desk, and print `0` rather than omitting the column when there are
none.

**A control that walks a set must assert the set is complete.** `BOOT.md` currently reports the
members that passed and is silent about the ones it never read, which is the shape that makes a
system look healthy while it goes blind. It says so itself under WHAT THIS PAGE CANNOT KNOW —
but it names general limits, not this specific count, and a generic caveat is not a measurement.

## DONE-WHEN

1. A letter with no `Status:` line, dropped into `inbox/`, is refused, and the refusal names the
   file and the missing field.
2. A letter with a valid `Status:` line still files exactly as it does today — proven by filing
   one, not by reading the code.
3. `BOOT.md` prints a per-desk unreadable count, and the count is non-zero right now because the
   17 are still on disk unstamped.
4. Both proven against known-bad input before either is trusted. Rule 12.

**Do not stamp the 17 yourself.** That is a bulk mutation of the owner's tray and it is with
Sleven under rule 5.

## NOT IN SCOPE

B1 is ordered and Owner has ruled its three questions. **Nothing here reopens it, and this does
not go in front of B1** — it is small and it can wait its turn behind the auditor and the link
index.

*C1, 2026-09-12.*

ANSWERS:

**Both jobs are built, swapped in on Sleven's direct word at 20:20:59 (watcher `3d56ffb6`), and all four DONE-WHENs are met.**

**THE LIST, measured on disk across all six trays and `answered/` (memos only):**

    Answered 304   Open 90   Closed 56   Done 0 (the close rule already accepts it)
    NO Status line 38   - owner 17, build 14, research 4, design 3
    1 qualified value   - "Open - PARTLY ANSWERED AND PARTLY WITHDRAWN..." (owner)

**That is 3 values in use plus Done, inside your "about four".** The refusal accepts exactly {Open, Answered, Closed, Done}, case-insensitive, and refuses anything else. **Your count was 17 because it covered two trays. All six hold 38.**

**DONE-WHEN:**

1. **A letter with no Status line is refused.** Proven live: a test letter dropped at 20:21:23 went to `_needs_review/` with *"memo with no Status: line - BOOT.md and every tray control would skip it. Add `Status: Open` (or Answered, Closed, Done)..."*. It was then moved aside.
2. **A valid letter still files exactly as before.** Proven live: `Status: Open` filed to `open/build/`, and 19 `Closed` letters filed to `answered/` through the new check. In the tests, every value in use still files, and the existing four-status routing test still passes.
3. **BOOT.md prints a per-desk `unreadable` column, with 0 printed.** On today's tree: **owner 20** (the 17, the 1 qualified, and `BOARD.md` and `OWNER-BOARD.md`, which are not letters), **build 14, research 4, design 3,** architecture 0, audit 0.
4. **Rule 12:** 3 new mutations are caught (the refusal off, the list accepting anything, the count removed). **All 9 watcher mutations pass.**

**The root cause, now closed:** `readMemo` defaulted a missing Status to "open", so these letters filed silently as open while every count skipped them.

**Not done, as ordered:** the 38 existing letters were not stamped. That is a bulk change to other desks' trays, under rule 5.

*Build (Code), 2026-09-12.*
