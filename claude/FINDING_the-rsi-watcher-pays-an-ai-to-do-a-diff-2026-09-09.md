# FINDING — the RSI watcher pays for a language model to do a set difference

    date     2026-09-09
    desk     Adjutant
    raised   by Sleven, unprompted: "why can't we have a local program that's
             not an AI, that's not burning credits do this?"
    answer   He is right, and the case is stronger than he put it.

---

## WHAT IS ACTUALLY RUNNING

A scheduled task, `RSI sweep — Citizen Compass (hourly)`, cron `27 * * * *`,
created 2026-08-06, on `claude-sonnet-5`. It starts a **fresh session with no
memory** every hour and hands it a roughly 4,000-word prompt. The last run
fired at 21:27:54 and finished at 21:49:53 — **twenty-two minutes of model
time, twenty-four times a day.**

## THE HONEST SPLIT — WHAT NEEDS A MIND AND WHAT DOES NOT

**Needs no intelligence whatever.** Every hour, on every run:

    fetch devtracker, comm-link list, patchbot        HTTP GET
    append a cache-busting query parameter            string concatenation
    compare post IDs against a stored set             set difference
    compare the LIVE build string against stored      string equality
    compare relative age strings against last run     string equality
    write the state file                              file write
    notify when something changed                     conditional

**That is the entire job on a quiet hour.** The watcher's own quiet-run counter
says most hours are quiet. **A shell script does all of it and costs nothing.**

**Genuinely needs judgement**, and only when something new actually appears:

    is this a new hull or a livery of an existing one
    is this a RENAME — which silently breaks 316 name joins
    which of BUILD / DEVPOST / SHIP / ROADMAP / ECONOMY / EVENT
    what does this comm-link post actually say

**So the question is not whether a machine can do this. It is why the expensive
part runs on the hours when there is nothing to think about.**

## THE PART THAT MAKES IT WORSE — IT IS PAYING TO BE BLIND

From the watcher's own state file, this run:

- **Devtracker — CONFIRMED STALE.** The top post's age has read "51 minutes
  ago" across three consecutive fetches spanning about two real hours. This is
  the project's *first* source, checked first every run.
- **Status page — content roughly seven weeks stale.** It reports 4.9.0 as
  current and 4.10.0 as "scheduled", against a LIVE build that shipped
  2026-08-26.
- **Roadmap, both views — FAILED, standing.** JavaScript-rendered. Never
  worked.
- **Pledge / ships — FAILED, standing.** Same reason.

**Two of five sources are stale, two have never worked, and one works.** That is
what is being paid for hourly.

**And the two that have never worked need exactly the thing a local program can
have and a WebFetch cannot: a real browser.** Chromium driving those pages
would do *better* than the current arrangement on the sources that matter most —
the roadmap is one of the six classifications and has never once been read.

## THE SHAPE THAT FIXES IT

**A local watcher does the diff. A session gets woken only when the diff is not
empty.**

    every hour, locally, free      fetch, diff IDs and build strings, write
                                   state, detect staleness, do nothing else
    only on a real change          wake one session, hand it the specific new
                                   item, get the classification, stop

That removes roughly twenty-three of twenty-four runs a day and leaves the
model doing the only part that needs a model.

**This is not new infrastructure.** The repository already runs `inbox_watcher.exe`
as a Go service, already has `roadmap-watcher/` and `setup_roadmap_task.ps1`, and
the project's standing architecture decision is that long-running components run
as real background services — auto-start, silent, survive reboot, no console
window. **This is another watcher next to the ones already built to that
pattern**, not a new idea.

**It also satisfies a rule the automation research produced today**: a wake
trigger must be structurally incapable of firing on its own output. Here the
trigger is a new post ID published by CIG — nothing a woken session can
produce. Clean by construction.

## WHAT IS NOT BEING CLAIMED

**Not that the current watcher is useless.** It has caught real things, it
caught its own cache fault, and its prompt carries hard-won rules — the planted
control, the livery trap, the rename trap, the write budget. **Those rules move
into the local program's spec; they are not thrown away.**

**Not that this is free to build.** It is a real piece of work: fetching,
parsing, a stored ID set, a headless browser for the two JS pages, and the wake
path. **The saving is ongoing and the cost is once**, which is the correct shape,
but it is not nothing.

**Not costed.** Nobody here has measured what the hourly runs actually consume,
and no number should be invented. **The argument stands on the work being wrong
work, not on a figure.**

## WHAT SLEVEN HAS TO DECIDE

Whether the hourly sweep moves to a local program with the model kept for
classification only. **It changes how a running system works, so it is his, not
a routine next step.**
