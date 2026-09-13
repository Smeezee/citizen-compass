    state        WORKING
    blocked_on
    clears_by

Filed at the time in this file's archive name.

# THE MAIL IS READ. THE GUARD CHECK EXTENSION IS WHAT I AM STARTING.

## WHAT ARRIVED SINCE MY LAST UPDATE (13:15)

    13:19  Architecture   log the usage block; the dollar framing is withdrawn;
                          tune nothing until three wakes are measured
    13:23  Architecture   CORRECTION - the write warning is withdrawn, the
                          writes landed, stop watching for missing sections

**Both read.** The 13:19 memo's item 1 - put the four token figures and the turn
count in `logs/wake_log.jsonl` rather than only on the console - **is not yet
done**; `print_usage` reports them, `log_wake` still records only
`usage_parsed`. It goes in alongside the work below, since it is the same file
and it is five lines.

The 13:23 correction needs nothing from me: I had not started building around
the warning.

## WHAT I AM STARTING NOW

**Step 1 of the Owner's order of 12:46: extend `checks/_verify_api_key_guard.py`
so the PowerShell guard and the launcher's own refusal are asserted to agree.**

The two are not the same rule and the check will not pretend they are. The
PowerShell and Go guards refuse a **mismatch** between a declared intent and
what is set. `scripts/wake_desk.py:assert_no_api_key` refuses on **presence**,
unconditionally, because in print mode a key takes precedence over the
subscription with no approval step. **What has to agree is the variable name,
the fact that the refusal really fires, and that neither ever reads the value.**

## THEN

**The brakes**, in the order Architecture set: `run_id`/`v:1`, the switch, the
per-desk lock, the two ceilings with the withheld list, the spend cap as an
empty lookup that refuses to wake. Each tripped on purpose before the next is
started. I re-read `claude/SPEC_the-brakes-2026-09-10.md` at the point of
building it, not before - it has already changed twice today.

**Nothing wakes again until the brakes exist and have been tripped on purpose.**

Nothing committed.
