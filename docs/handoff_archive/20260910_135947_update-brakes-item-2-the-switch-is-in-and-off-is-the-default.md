    state        WORKING
    blocked_on
    clears_by

Filed at 14:04 CDT / 19:04 UTC, read from the machine.

# BRAKES, ITEM 2. THE MASTER SWITCH IS IN, IT IS OFF, AND A REAL RUN WITH NO
# `--dry-run` WAS SEEN TO REFUSE AT IT AND LAUNCH NOTHING.

## WHAT IT IS

    C:\Users\david\.citizen-compass\automation.switch      one file, read only
    the value "on", EXACTLY                                everything else OFF

**The launcher reads it and never writes it.** Nothing I built writes outside
the repository, so hard rule 6 is not engaged - **the file is made by hand,
once, which is the right hand for a master stop.**

**Absent, unreadable, or any other value is OFF, and it says which.** With
nothing on disk nothing ever wakes. That is correct today and it means
automation begins with a positive act rather than with an absence.

**"ON", "On", "yes", "true", "1" and "onn" are all OFF** - rule 17, and it is
deliberate: an unknown value is not a permission, and a case-insensitive
fallback here would be a normalisation nobody checked for collisions.

## WHERE THE GATE SITS, AND THIS IS THE ONE JUDGEMENT CALL

**The state is READ in step 0 on every invocation and printed on the receipt.
The REFUSAL sits where a launch would happen** - after the dry-run branch,
before the containment probe.

    switch       OFF   C:\Users\david\.citizen-compass\automation.switch (FileNotFoundError)

**A dry run starts nothing, and the switch governs starting** - the same
distinction section 7 draws for the ceilings, which stop a wake beginning and
never kill one in flight. **Refusing the dry run would also make the entire
pre-flight untestable while the switch is off, which is the state this machine
is in until every brake has been tripped.**

**So the dry run runs, and it says what a real one would do:**

    AND A REAL RUN WOULD REFUSE HERE: the master switch is OFF.

## OFF IS VISIBLE - `--switch`

    python scripts/wake_desk.py --switch
    OFF   C:\Users\david\.citizen-compass\automation.switch (FileNotFoundError)
    exit 3      0 means ON, 3 means OFF

**The roll call has to be able to ask without waking anything**, or "every desk
is idle" and "the automation is off" are the same line - section 8's own words.
It needs no desk, launches nothing, and writes nothing.

## HOW IT WAS TRIPPED - `checks/_prove_switch.py`, 24 PASS, 0 FAIL, 2 NOT PERFORMED

**The one that matters ran the REAL launcher with NO `--dry-run`:**

    it refuses at the gate and says so                     PASS   exit 1
    and it never reached step 1 - nothing was launched     PASS
    no wake record was written to the live log             PASS

**That run is safe only because the switch is genuinely off, and the harness
checks that before running it** - if the switch were ON it would spend, so it is
skipped and reported rather than run. That guard is in the harness, not in my
memory of it.

Plus twelve values through the reader (on, `on\n`, `  on  `, ON, On, yes, true,
1, empty, "on off", "onn", absent), a directory where the file should be, and
both directions of the gate function.

## THE TWO I DID NOT PERFORM, REPORTED AS NOT PERFORMED

    the ON path end to end                     it would launch a real wake and
                                               spend
    a woken desk TRIES to write the switch
    and is REFUSED                             section 9's second half needs a
                                               real wake

**Both land on the first wake after the brakes are finished, and neither is
counted as a pass.**

## WHAT I CHOSE NOT TO BUILD, SAID RATHER THAN LEFT IMPLICIT

**A refusal at the switch writes NO record.** The spec does not ask for one and
the switch is not a ceiling - nothing is withheld, nothing is consumed, the
letter never moved. **The consequence is that "the automation was off all night"
leaves no trace in `wake_log.jsonl`** - the switch file and the roll call are
where that state lives. Say the word if you want a record and it is three lines.

## EVERYTHING RE-RUN AFTER THE CHANGE

    checks/_verify_api_key_guard.py     36 passed, 0 failed
    checks/_prove_launcher_gate.py      four planted launchers, all correct
    checks/_prove_wake_record.py        item 1 still holds
    scripts/wake_desk.py --self-test    6 passed, 0 failed

`logs/wake_log.jsonl` is still 6,649 bytes, mtime 12:36. **Nothing has been
woken and nothing has been spent all afternoon.**

## NEXT

**Item 3, the per-desk lock.** Taken by the launcher rather than the watcher,
stale locks reported and never cleared, exactly one notice per stale lock.

Nothing committed.
