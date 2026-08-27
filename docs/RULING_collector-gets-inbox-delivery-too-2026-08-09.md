# RULING — `citizen-collector/` now goes through `inbox/` too. Second collision, same root cause, structural fix this time.

    from      C1, 2026-08-09
    for       the record — Code, and any future session touching citizen-collector/
    trigger   Code's report, same day: nine files in citizen-collector/ rewritten mid-
              session while Code was independently working the browser-fallback item.
    prior     claude/... "Rule 14 was violated in citizen-collector/, by C1, and Code
              caught it" — 2026-08-08, the first occurrence of the same failure shape.

---

## What happened, confirmed independently, not just taken on Code's report

Earlier the same day, Sleven directly instructed C1 to fix the collector's resend defect,
working straight in `citizen-collector/` — the pattern the original WO-UI-01 work used,
from before `inbox/`-mediated delivery existed for that directory specifically. C1 wrote
and delivered nine files via the device bridge:

    export.go, gamelog_mine.go, scrub.go, sent_rows_selftest.go, ui.go,
    ui_actions.go, ui_state.go, upload.go, upload_selftest.go

Confirmed via `stat`: all nine landed 2026-08-09 20:35:37–40 UTC, a ~3-second cluster
consistent with one batch write.

**Unknown to C1 at the time, a separate local Claude Code session was independently
active in the same directory**, working item 3 off `session-handoff-2026-08-09-collector.md`'s
open list — "the browser fallback has never executed." Code found the real bug behind that
item: `ui_browser_selftest.go` has 20 checks, but every one is downstream of
`webview2Available()`, which had no test in either direction — if it could only ever
return true, the fallback would be unreachable and all 20 checks would still pass. Code
added `webview2_detect_selftest.go`, confirmed on disk (2026-08-09 20:40:13 UTC, 8,486
bytes) with 9 named checks including an explicit positive control, a check that an
uninstall leftover is not counted as installed, and a check that the same `exeDir` yields
both possible answers — structurally sound, matches this project's hard rule 12.

Registering that new selftest required a read-modify-write of `main.go`. Confirmed via
`stat` and `grep`: `main.go`'s write landed 20:40:28 UTC, five minutes after C1's batch,
and both registrations coexist cleanly —

    514  runSentRowsExportSelftest(check)         <- C1's, from the resend fix
    518  runSentRowsExportPrivacySelftest(check)  <- C1's
    543  runWebView2DetectSelftest(check)          <- Code's, from this same session

**Nothing was lost. Verified directly, not assumed from either report.** But it was luck
of read/write ordering, not a guard — if Code's read had landed one write earlier, C1's
`main.go` changes would have been silently discarded by Code's own subsequent write, and
neither side would have known until something failed to compile or a check went missing.

Code stopped short of the remaining open item on its own list — extracting
`openInBrowser` out of `serveBrowserUI` into a testable seam, so the auth checks could run
against a real socket instead of handing synthetic requests straight to `authorised()` —
specifically because it had just found the second-writer condition and didn't want to do
that surgery uncertain who else might be touching the file. That was the right call to
make under uncertainty, and it's why this ruling exists: to remove the uncertainty going
forward rather than leave it to be re-judged case by case.

## Root cause: this is the second time, and it's structural, not a memory lapse

The first occurrence (2026-08-08, documented in `CURRENT-STATE.md`'s collector section) had
a different shape: C1 filed an order into `inbox/` and then did the work itself without
withdrawing the order — a coordination failure between C1's own actions. This time there
was no unwithdrawn order. Sleven directed C1 to work directly in the directory, reasonably,
because that's how collector work has always been done — and a separate Code session was
independently active there at the same time, with neither side aware of the other.

`citizen-compass/` proper got the `inbox/`-delivery discipline on 2026-08-07, specifically
because ad-hoc coordination had already failed multiple times by then (see "Session roles"
in `CURRENT-STATE.md`: two handoff watchers, a near-second scheduled task, three sessions
on one layer file, WO-UI-01 delivered to the claude.ai project instead of the repo and
never reaching Code). `citizen-collector/` never got the same treatment, on the reasoning
that it was a separate, smaller subproject usually worked by one agent at a time. **That
reasoning has now failed twice**, in two different ways, which is the signal that it's the
policy that's wrong, not the two incidents that are unlucky.

## The fix

**`citizen-collector/` now follows the same `inbox/`-delivery convention as the rest of
the repo.** A Cowork session does not write collector source directly — not even on a
direct instruction to fix something there — it writes a prompt for Code and delivers it
to `inbox/`, exactly like every citizen-compass order since 2026-08-09's exporter-swap
work. `inbox/`'s watcher already covers the whole repo, `citizen-collector/` included, so
this needs no new infrastructure — it needs C1 to stop treating that one directory as an
exception.

This is a process commitment on C1's side, not a mechanical guard — same honest caveat
this project already has on record for the first incident ("nothing was lost, and that is
due to Code's discipline, not C1's design"). If a genuinely urgent direct fix is ever
warranted again, the minimum bar is checking for a live Code session first and saying so
explicitly in the delivery, not assuming the directory is quiet because nobody said
otherwise.

## What's still open, unrelated to the collision itself

- Code's own remaining item: the end-to-end socket test for the four `serveBrowserUI`
  handlers, blocked on extracting `openInBrowser` into a testable seam. Reasonable to pick
  back up now that this ruling removes the uncertainty that paused it.
- Everything else on the collector's open-items list in `CURRENT-STATE.md` is unchanged by
  this — this ruling is scoped to the coordination failure, not a review of the collector's
  remaining work.
