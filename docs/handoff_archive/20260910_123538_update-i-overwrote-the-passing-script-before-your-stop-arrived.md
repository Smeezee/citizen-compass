    state        WORKING
    blocked_on
    clears_by

Filed at the time in this file's archive name. **Rule 13, on arrival, before the
runs.**

## THE URGENT PART FIRST: I OVERWROTE THE PASSING SCRIPT

**`scripts/wake_desk.py` was rewritten. The version that completed the wake is
gone from disk and it was never committed, so git does not have it either.**

The sequence, from the watcher's own log and the file times, not from memory:

    ~12:12  I rewrote scripts/wake_desk.py in place
     12:15  self-test run against the rewritten file
     12:25  your STOP arrived: "copy the passing version aside first, by name,
            before you touch a line"
     12:29  your GO arrived

**The instruction arrived after the act. That is the sequence, not an excuse** —
I replaced a working artifact without parking a copy, and I would have had to
think of that myself.

## WHAT SURVIVES, AND IT IS THE LOAD-BEARING HALF

    _to_delete/2026-09-10_the_passing_wake_run/THE_COMMAND_THAT_RAN.md

**That is not a reconstruction from memory.** It is the exact record
`logs/wake_log.jsonl` wrote at launch, holding the full argv of the run that
worked:

    --output-format json  --restricted  --permission-prompts none
    --disallowedTools Bash,PowerShell,WebFetch,NotebookEdit,Task,Agent
    --add-dir <ROOT>   --append-system-prompt <the charter, as text>

plus the start, the end, 81.06s and exit 0. **Your own correction memo makes the
same point: the wake log records the command.**

**I am deliberately NOT reconstructing the 382 lines from memory.** I could
produce something close and it would be a fabrication wearing the name of a
recovery. The behaviour that mattered is recorded above; the prose around it is
not, and saying so is the honest answer.

## THE TWO LETTERS, AND WHY I AM PROCEEDING

    12:25:57   STOP - do not replace the script that passed
    12:29:06   GO   - step 1, then step 2 if step 1 passes

**The GO is the newer of the two and it is unambiguous about running.** It also
praises the flag-probe work, which exists only in the rewrite - so it was written
with the new script in front of you.

**One point where they genuinely differ, and I am not silently picking it:** the
STOP says the `--tools` / `--allowedTools` swap must move on its own, after the
probe, "otherwise a failure has two possible causes." The GO says run step 2.

**My reading, stated so you can overrule it rather than discover it:** step 1 IS
that separate measurement. The probe uses the path rule and nothing else new, and
if it passes, the flag set has been measured on this machine for exactly the write
path step 2 needs. The two-cause problem the STOP names is resolved by the probe
passing, not carried into step 2.

**So: step 1 now. If it passes, step 2. If the outside write succeeds, I stop** -
no step 2, no loosening, no second attempt with a different rule.

**If that reading is wrong, say so and I will re-run step 2 on the original flag
set.** It is pennies either way.

Nothing committed.
