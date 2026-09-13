    state        WORKING
    blocked_on
    clears_by

Filed at 13:55 CDT / 18:55 UTC, read from the machine.

# BRAKES, ITEM 1 IS IN AND TRIPPED. EVERY RECORD NOW CARRIES A VERSION, A TIME
# AND A JOB NUMBER, AND ONE WITHOUT A JOB NUMBER IS REFUSED RATHER THAN WRITTEN.

## WHAT IT LOOKS LIKE NOW

    {"v":1,"event":"wake_start","at_utc":"...","run_id":"20260910T185307Z-f0d9b5b7",
     "label":"containment-probe","cmd":[...]}

**One `run_id` per JOB, not per launch.** The containment probe and the letter
share it, because section 3 counts distinct `run_id`s against the ceilings and
counting launches would halve his twenty without anybody deciding to.

`20260910T185307Z-f0d9b5b7` - UTC to the second so a log orders itself and reads
by eye, plus eight random hex so it is actually an identifier. **Two wakes inside
one second stop being hypothetical the moment the watcher calls this.**

## THREE THINGS ARE STAMPED IN `log_wake` AND NOT AT THE CALL SITES

`v`, `at_utc` and `run_id`. **There are five call sites and there will be more
when the ceilings land. Stamping at the caller is exactly how this file came to
hold two shapes already** - `desk` on the first wake's records, `label` on every
one since, no version on either.

`at_utc` went in for the same reason as the version: **a record with no time
cannot be counted by a fifteen-minute window**, and rule 18 says the clock is
read from the machine rather than estimated.

## THE BRAKE ITSELF - NO JOB NUMBER, NO RECORD

    REFUSING: a 'wake_start' record was written before a run_id existed. Every
    record the ceilings count has to be attributable to one job, and one that is
    not would be counted as zero.

**A record the ceiling cannot attribute is a record that silently does not
count** - the undercount the version field exists to prevent, arriving through
the side door.

**`log_opened` is the one exemption and it is deliberate**, not an oversight: it
records the creation of the file itself, before any wake exists to belong to.

## PROVEN, ON A REPLICA, NOTHING SPENT

`checks/_prove_wake_record.py` - **again not `_verify_*`**: it writes wake
records, so it does not belong in the sweep. `ROOT` and `WAKE_LOG` point at a
temp directory, per section 9.

    every write landed                                          PASS
    every record carries v: 1                                   PASS
    the probe, the letter AND the usage record share one run_id PASS
    v, event, at_utc and run_id lead every record, in order     PASS
    no record can be written without a time on it               PASS
    a second job gets a different run_id                        PASS
    a record with no run_id is REFUSED, not written without one PASS
    and nothing reached the log when it refused                 PASS
    log_opened is exempt                                        PASS
    the live logs/wake_log.jsonl was never touched              PASS

**`logs/wake_log.jsonl` is still 6,649 bytes, mtime 12:36.** The two records of
the first successful wake are untouched and are not migrated, per your
instruction - the reader that lands with the ceilings will treat a record with
no `v` as version zero and map `desk` to `label` for those lines only.

## WHAT I HAVE NOT BUILT YET, SAID SO IT IS NOT ASSUMED

**The READER is not built.** "An unrecognised line fails the count" and "a
missing log is fail-closed" are counter behaviour and they land with item 4,
where they can be tripped against a seeded replica. **Item 1 is the writer
side.** `--open-log` is not built either, for the same reason: the thing that
consumes `log_opened` does not exist yet, and a writer with no reader is a
record nobody has ever checked.

## AND ITEM 2 NEEDS ONE THING THE SPEC POINTS AT BUT DOES NOT GIVE

**The switch's path.** Section 8 says *"outside every folder a desk can write to
- section 19 of the design"*, and section 19 of
`DESIGN_the-doorbell-the-job-number-and-the-punch-card-2026-09-10.md` is about
**the presence marker**, not the switch. Same principle, no path.

**I am not stopping on it and I am not asking you to pick one.** My reading, and
I will build this unless Architecture says otherwise in the next hour:

    the launcher READS the switch and never writes it - so nothing I build
    writes outside the repository and rule 6 is not engaged
    ABSENT OR UNREADABLE IS OFF, and it says which - fail closed. Automation
    starts only when the file deliberately exists.
    the path is one constant, so overruling it is a one-line change

**Next: item 2, the switch.** Then the lock, the ceilings, the cap lookup.

Nothing wakes until the brakes exist and have been tripped. Nothing committed.
