    state        WORKING
    blocked_on
    clears_by

Filed at the time in this file's archive name. Rule 13, on arrival, before
starting. **No wake is running, so this is not a drop in the minutes around one.**

## RECEIVED

    report-tokens-not-dollars                              Owner
    containment-holds-next-the-guard-check-then-the-brakes  Owner
    the-brakes-spec-is-on-disk-...                         Architecture
    the-brakes-spec-gained-three-sections-...              Architecture

## TAKEN, WITH NO ARGUMENT

**Dollars come out of every report.** Tokens in, tokens out, cache created, cache
read - those are the four, because those are what come out of the allowance.
`total_cost_usd` stays in `logs/wake_log.jsonl` only, where it can still flag a run
that behaved oddly. **You are right that nobody asked whether it meant anything for
you, and I labelled it carefully instead of questioning it, which is not the same
thing.**

**`--max-budget-usd` stays.** A runaway still has to hit a wall, its number came
from measurement, and nobody is picking it off a price.

**The two failed conditions stay failed. The watcher-subtraction does not get
built.** The operational rule goes somewhere the next session finds it rather than
into a third clever control.

**`CLAUDE.md` is not trimmed and I will not propose a shorter extract.**

## WHAT I AM DOING NOW, AND ONLY THIS

**Measuring what the 304,000 cache-read tokens actually is.** Ahead of the guard
check, on your instruction.

**And I intend to measure it WITHOUT spending anything.** The runbook noted that
session persistence writes a transcript outside the repository under the user
profile. If that transcript is there, it holds the per-call token usage for the
run that already happened, and the answer can be counted rather than re-bought.
**If it is not there, I will say so and ask before running anything.**

**Measure, do not fix.** Your words.

## ONE THING I ALREADY KNOW I GOT WRONG

`wake_desk.py` printed selected fields of the result JSON and **kept none of it**.
So the run I need to explain has no payload on disk. **Whatever the answer turns
out to be, the fix that outlives it is to persist the whole JSON block per run**,
which costs nothing and would have made this measurement free.

Nothing committed.
