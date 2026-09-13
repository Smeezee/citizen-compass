    state        BLOCKED
    blocked_on   the go-ahead to swap the running watcher binary
    clears_by    OWNER

Filed at 15:16 CDT / 20:16 UTC — `date` run at 15:14:32, this typed straight
after it.

# THE ANSWER-ROUTING FIX IS BUILT, TESTED, MADE TO FAIL FIRST, AND PROVED END TO
# END ON A COPY. THE RUNNING WATCHER IS UNTOUCHED AND STAYS THAT WAY.

**Full report to him: `correspondence/open/owner/` — "the answer routing is
built and proved, the swap is yours".** This is the working record.

## THE CHANGE

`watcher-go/memo.go`, three edits:

    memoDestination   Open -> open/<To:>, Answered -> open/<From:>,
                      Closed/Done -> answered/. From: validated on an ANSWERED
                      memo only.
    clearOpenCopy     takes the tray it must not touch
    classifyMemo      the supersede gate is "is it answered", not "did it land
                      in answered/"

**Six new filesystem tests plus two rewritten ones.** The old
`TestAnAnsweredMemoLeavesTheOpenTray` asserted the string `memoDestination`
returned and never opened a directory - `memo.go` says so in its own comment -
so it is now `TestAnAnsweredMemoGoesBackToTheSender` and it touches the disk.

## THE THREE PROOFS, AND THE SECOND IS THE ONE I WOULD HAVE SKIPPED

**1. The suite.** `go test -count=3 ./...` - ok, 3.9s. The main routing test
runs its own scenario 25 times with a fresh tree each time, because the failure
it guards is a randomised map order and one green run is one coin toss.

**2. Made to fail first.** The new tests were run against the PRE-PATCH
`memo.go` in a copied tree: **five failed, five passed.** The five that passed
assert behaviour that did not change, which is what a regression guard is for.

**And the harness refuses to call a non-zero exit a failure** - it requires an
actual `--- FAIL` line, because a package that will not compile exits non-zero
too, and reading that as "the test failed" is the defect this project keeps
finding elsewhere. It caught itself doing exactly that on the first run: the
copy could not resolve `../pkg/...` and the harness announced success.

**3. The unguarded sweep, counted rather than argued.** Called forty times the
old way: **it moved the ANSWER rather than the stale question on nine of the
forty runs.**

## END TO END, ON A COPY, WITH THE REAL BINARY

Nine assertions, all pass, listed in the memo to him. **The copy cannot reach
the live inbox and that is structural:** the watcher takes its project root from
the directory its own executable is in, so a binary in a temp folder is
physically unable to see `citizen-compass\inbox`. **No second watcher on the
real tray was ever possible during this** - rule 14 closed by where the file is
rather than by my remembering.

The live `inbox/` listing was captured before and after and is identical.

## WHAT IS STAGED

    running, untouched   inbox_watcher.exe                     5,768,192 bytes
                                                               2026-09-09 21:58
    built and waiting    watcher-go\inbox_watcher_pending_20260910.exe
                                                               5,770,752 bytes
                                                               2026-09-10 15:14

**Nothing was replaced, nothing was scheduled, nothing was restarted.**

## ONE DEFECT IN MY OWN HARNESS, FOUND AND FIXED

The end-to-end script printed the watcher's log to a cp1252 console and threw
`UnicodeEncodeError` on a `✓` - **after every assertion had already passed.**
That is `CLAUDE.md`'s own standing caveat about `log()` and Unicode symbols,
one layer out. The evidence was intact; the reporting crashed on it. Fixed by
running under `PYTHONIOENCODING=utf-8`.

## NEXT

**Blocked on the swap, which is his.** Nothing else in this piece of work can
move until he answers.

**So the queue goes back to brakes item 3, the per-desk lock**, which is where
it was when BUILD IT arrived. The watcher's missing rescan (Architecture, 13:40)
is still unstarted and deliberately not bundled into this build - a failed swap
with two changes in it has two possible causes.

Nothing committed.
