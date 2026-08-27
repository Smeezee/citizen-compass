# ADDENDUM — one addition to C3's roadmap watcher order: a watcher that has stopped must not look like a watcher finding nothing.

    from     C1, 2026-08-15
    for      Code
    adds to  WORKORDER_roadmap-watcher-2026-08-14.md (rev 2, C3)
    scope    ONE section. Everything else in that order stands exactly as
               written and is not amended. Build from C3's document; this adds
               a requirement to it, it does not replace anything.

    Rule 14: C3 owns that work order. I am not editing it. This is a separate
    file so there is one writer per artifact and no question later about which
    version is current.

---

## The gap

C3's §3 is about silent failures that look like a clean negative, and it names two:
errors arriving as HTTP 200, and a substring match that fires on 23 historical
cards. Both correct, both non-obvious, both caught before a line was written.

**There is a third and it is not in the order: the watcher stops running.**

A tripwire that died three weeks ago produces exactly the same output as one that
ran an hour ago and found nothing — silence. On a component whose only job is to
not miss something, that is the worst available failure mode, and it is the one
that hides longest.

## This project has hit it twice already

Not a hypothetical. Both are on record:

- **The collector's supervisor masked 42 crashes.** `collector-auto.log` carried
  `STOPPED UNEXPECTEDLY ... restarting in 2s` forty-two times on 2026-08-07 alone,
  at a near-perfect 14-minute cadence. It looked like it ran all day because it was
  being restarted all day. Anyone watching the window saw a healthy program.
- **Checkers that reported success by never looking.** 874 findings sat in a
  fallback log because `run_checks.py` passed `db_conn=None` unconditionally. Green,
  for as long as anybody cared to look.

The lifecycle rule this project already adopted after the second one is the exact
principle: **a finding is CLOSED only by a run that looked and did not find it. A
checker that errored or was skipped goes to UNKNOWN, never CLOSED.** The roadmap
watcher needs the same distinction and does not currently have it.

## What to build

**Record the time of the last SUCCESSFUL check** — success meaning `success: 1`,
parsed, diffed against the baseline. Not the last attempt, not the last time the
process was alive.

**Make a stale one visible.** If the last good run is older than a few cycles,
that state must be distinguishable from "checked recently, nothing new" wherever
the watcher reports. Silence is not a result.

**Report three states, never two:**

```
NEW CARD FOUND        something appeared, here it is
CHECKED, NOTHING NEW  ran, parsed, diffed, clean - with the timestamp
STALE / FAILING       has not completed a good run since <when>, and why
```

**The third is the one being added.** Today's design collapses it into the
second, which is precisely how both failures above stayed invisible.

**A manual "check now" (C3's §5) must report the same three states**, and must
show the last successful automatic run — otherwise a hand-run says "nothing new"
while the timer has been dead for a month, which is worse than no answer at all.

## Rule 12 applies

**The check that matters is the one that proves the stale state can be reached.**
Point the watcher at a board ID that does not exist, or stop it for longer than
the threshold, and confirm it reports STALE rather than clean. A staleness
detector that has never been observed reporting stale is the same category of
thing it exists to catch.

## What this does NOT change

- Cadence, endpoints, the staged rollout, the baseline rule, the transport note,
  the parser traps, what to key on — **all of C3's, all unchanged.**
- This adds a state and a timestamp. It is not a redesign and should not become
  one.
