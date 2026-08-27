# HANDOFF — C3 edited the RSI watcher's trigger prompt. Rule 14 notice, so there is no silent second writer.

    from      C3 (Cowork), 2026-08-08 22:32 UTC
    to        C1 — you own the watchers
    why       Sleven asked C3 directly to fix the blind watcher. Recording it rather
              than leaving you to find a prompt you did not write.
    trigger   trig_01VUbUWSxvhJnHFcKRT98rMc — "RSI sweep — Citizen Compass (hourly)"
              cron unchanged (27 * * * *), still enabled, next run 23:27 UTC

---

## What was wrong

The watcher had **zero visibility for 3+ consecutive runs** — 0/6 sources, every
robertsspaceindustries.com / patchbot.io fetch returning `PROVENANCE_REQUIRED`. Control
fetches to other domains succeeded in the same runs, so it is a permission gate scoped to
those domains, and an unattended run has nobody to answer the prompt.

Before that, worse: at ~19:33 UTC Devtracker was **confirmed serving a frozen snapshot** — its
own page header read "Devtracker Posts - August 7th, 2026" during an August 8 run. It returned
200 and looked like data. The same failure mode already cost two missed PTU builds on
2026-08-07. **Sixth silent-success incident on this project.**

## What I changed — three edits, nothing else

**1. New `STEP 0a — THE PERMISSION GATE`**, inserted between STEP 0 and STEP 0b. Tells the
watcher the gate exists, that it is not a CIG outage and not a broken tool, to stop after
**two attempts per URL** instead of burning the run retrying, and to fall through to search.

**2. WebSearch promoted from footnote to primary path when blocked**, with mandatory honest
labelling:

    CONFIRMED  - fetched the page and read it
    REPORTED   - WebSearch surfaced it; name the source, treat as unconfirmed

A REPORTED build number is now worth logging *as REPORTED*. It may never be promoted to
CONFIRMED, and a blocked run may never read as a quiet one. Four standing search queries are
listed so a blocked run still produces signal instead of an outage log.

**3. Notification rule added.** It was re-notifying every hour about the same known block.
Now it notifies only for: a new LIVE build, a rename, a confirmed new ship, or **the gate
clearing**. Hourly repeats of a known problem bury the one that matters.

## What I did NOT change

Everything else is byte-identical: the cache-busting rule, the staleness test, all five
sources and their URLs, the classification list, both traps (rename-outranks-new-ship,
livery-is-not-a-ship), the state-write step, the report format, and all the standing rules.
Cron, enablement and notification channel untouched.

## Still broken, and not mine to fix

**The permission gate itself.** My edit routes around it; it does not clear it. That needs
either the domains pre-approved for the scheduled session or a different fetch path for
headless runs. **Sleven's, and he knows.** The watcher will now tell you when it clears.

Worth noting for whoever picks this up: **CIC reaches RSI and archive.org fine** — the gate
only bites unattended runs. So a browser-based path works and the scheduled one does not,
which points at the fix rather than at a workaround.

## The rule-14 position

C1 owns the watchers. C3 edited one. That is a second writer on your artifact, done at
Sleven's direct instruction and declared here in the same hour rather than discovered later —
which is the part that went wrong on 2026-08-07 with `citizen-collector/`. **If you want it
reverted or written differently, it is yours; say so and I will not touch it again.** The full
prior prompt is recoverable from the trigger's history if you want to diff it.
