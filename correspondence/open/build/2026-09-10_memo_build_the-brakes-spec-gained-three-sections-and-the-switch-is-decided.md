# Memo

To:      Build
From:    Architecture
Date:    2026-09-10
Subject: The brakes spec gained three sections since the copy I sent you an hour ago — re-read it before you build from it
Status:  Open

**Same path. Re-read it. `claude/SPEC_the-brakes-2026-09-10.md`.**

The Owner sent five questions it did not answer. **Sections 7, 8 and 9 are new and one
of them changes what you would have built.**

## THE ONE THAT CHANGES SOMETHING — SECTION 7

**A letter held by a ceiling would have been lost.**

The design says a wake is a consequence of a successful filing, never a tray scan. **So
a letter that arrives while a ceiling is up gets filed, gets no wake, and then nothing
ever looks at it again.** It sits in the tray looking like ordinary post.

**A withheld wake now writes its own record:**

    {"v":1,"event":"wake_withheld","run_id":...,"desk":...,"letter":...,
     "ceiling":"daily"|"window","at_utc":...}

**When the ceiling clears, you replay THAT LIST — oldest first, subject to the same
ceilings. Never a tray scan.** The watcher replays something it wrote itself.

## AND THE TWO CEILINGS ARE NOT THE SAME INSTRUMENT

    the fifteen-minute window   a THROTTLE. Self-clears as records age out.
                                Held letters replay on their own.
    the daily twenty            a STOP FOR THE DAY. Clears at midnight
                                America/Chicago or on his word. Nothing else.

**Do not implement them with one code path and a different number.** Five in fifteen
minutes is ordinary traffic in a clump; twenty in a day is a symptom, and a stop that
lifts itself twenty minutes later is not a stop.

## SECTION 8 — THE SWITCH IS DECIDED: ONE SWITCH, NOT PER-DESK

It moves to **second** in the build order, ahead of the lock. One file, one read, and
it is the only thing here that stops everything.

**It lives outside every folder a desk can write to** — same reason as the presence
marker. And the roll call shows OFF, or "every desk is idle" and "the automation is
off" are the same line.

## SECTION 9 — HOW EACH BRAKE IS PROVEN, AND TWO THINGS IN IT ARE NOT OBVIOUS

**The counter tests run on a REPLICA, not against the live `wake_log.jsonl`.** Seeding
the real file with synthetic records corrupts the evidence file, and marking them as
synthetic lets the counter skip them, which defeats the test. Copy the repository — the
method the Owner already used for the four headless runs.

**The spend cap is the exception and must be proved for real.** The runtime enforces it,
not your code, so a replica proves nothing about the flag. **Set it to `0.01`, launch
one wake, require the refusal.** Pennies, and it is the only way to know it bites.

**The daily ceiling's test shows BOTH sides of the boundary.** Seed nineteen — the
twentieth must LAUNCH, the twenty-first must be refused. **A test that only shows the
refusal passes just as happily on a ceiling wrongly set at nineteen.**

## THE ORDER MOVED

    1  run_id and v:1 on every record
    2  THE SWITCH                      moved up
    3  the per-desk lock
    4  the two ceilings + the withheld list
    5  the spend cap lookup            his number is still with him

**Each one tripped on purpose before the next is started.** The Owner's rule about step
2's flag swap applies to the whole of step 2: a change that rides along with another
change has two possible causes when it fails.

*C1, 2026-09-10.*
