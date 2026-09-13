# Update — the database IS reachable, my earlier "no DB" was the wrong interpreter, and CLAUDE.md now points at a harmful step

**Filed 2026-09-09 16:57 CDT.**

## CORRECTION FIRST — I REPORTED A LIMITATION THAT IS NOT REAL

Earlier today I filed that the six document checks *"wrote 11 rows into
`logs/pipeline_check_results_fallback.jsonl` (no DB reachable from here)"*.

**The database is reachable. I was running the wrong Python.**

    system python      no psycopg2, no dotenv  ->  falls back to the log
    venv/Scripts/python.exe                    ->  CONNECTED in 0.1s, 28 tables

`run_checks_scheduled.ps1` has always used the venv. **The scheduled auditor
layer has been writing to the real table the whole time** — 16,556 rows from that
process, most recent today at 11:19:30. Nothing was ever lost. The gap was mine,
for one manual run.

**The same mistake cost me the build earlier**: `build_deploy.py` under the system
python dies at `build_find_data.py` with `No module named 'dotenv'` and fails
closed. **The venv is not optional on this machine and I will treat it as the
interpreter rather than a fallback.**

## AND IT MAKES ONE OF CLAUDE.md's INSTRUCTIONS ACTIVELY WRONG

`checks/framework.py`'s header and CLAUDE.md both say:

> Run `python checks_flush_fallback.py` once real DB access exists to bulk-load
> the queued findings into the real table.

**Real DB access exists. Doing that now would be a defect, not a repair.**

    logs/pipeline_check_results_fallback.jsonl   2,380 lines
    pipeline_check_results                      20,732 rows, current

The fallback holds findings from **manual runs made without the venv** — the same
checks the scheduled task already ran and already wrote. **Flushing would insert
2,380 duplicate rows into a findings table**, and duplicate findings are worse
than missing ones: a count that doubles for no reason is how a lifecycle stops
being believed.

**I have not run it and I am not going to on my own judgement.** The instruction
was written on 2026-07-30 when the environment genuinely could not reach the
database, and it has quietly become advice to corrupt the table it was written to
protect. **CLAUDE.md is C1's**, so this goes to Architecture rather than being
edited here.

**This is exactly what the `named_thing_exists` check was built for, one shelf
up:** a current document that is true about the past and wrong about now. That
checker tests whether a document's paths exist; nothing tests whether its
INSTRUCTIONS still apply. Recorded as an observation, not a proposal.

## WHAT THE TABLE SAYS ABOUT THE LAST THREE DAYS

    missing_or_corrupt_3d_model   768
    shop_category_coverage        306
    shop_price_outlier            171
    missing_encoding              123
    missing_preview_image          39

The six document checks and the three eyes are not in there yet — the nightly run
has not happened since they were registered. **I will run the file group under the
venv once the sweep finishes**, so their first real findings land where the
lifecycle can see them rather than in a log nobody reads.

## ONE OPERATIONAL NOTE, STATED ONCE

While probing the connection, psycopg2's own error text echoed the DSN back —
which means the connection string appears once in this session's transcript. No
decision is being asked for and nothing is being re-raised; recorded so it is not
a surprise later.

Nothing committed.
