# Update — starting: 35 controls say "I could not look" and are counted as defects

**2026-09-06 · Code (Build)**

Sleven picked this from the three I reported. Read the mail first per rule 24.

## The defect

C1's `FINDING_the-sweep-cannot-say-i-could-not-look-2026-08-29` established that
a control which starts, finds its resource absent and says so had no exit code
meaning that. **The runner was fixed** - `code == 2` becomes NOT RUN, with the
reasoning written into `run_all_controls.py`.

**The controls were not.** 56 print "NOT PERFORMED"; **35 never use exit 2.**
They say it in prose and exit 1, so the runner reads them as failures - and is
right to, on the information it has.

It cost time twice today. My sweep reported 8 failed: one real build-gate defect
and seven that printed "NOT PERFORMED: the build failed". C1 then diagnosed all
eight as environmental from their VM, which was wrong for this machine - a wrong
conclusion drawn from a display defect.

## RULE 5 - dry run first, and I am stopping on it

This touches more than ten files, so the first pass is report-only: it prints
every file, every line, and exactly what would change, and writes nothing.
**Sleven sees that list before anything is edited.**

## Scope

`checks/` is Code's by default. Of the 35, seven are C1's named files and I am
leaving them and listing them for C1 instead:

    _verify_marker_provenance.py   _verify_marker_census.py
    _verify_marker_spread.py       _verify_display_names.py
    _verify_no_agent_traces.py     _verify_placement_gate.py
    _verify_swap_loop.mjs

**Not every "NOT PERFORMED" print is an exit site.** Some report it mid-run
without terminating - `_verify_glossary_reaches.mjs` prints MARKED=0 under a
REPORTED, NOT FAILED heading and must keep exiting 0. Only a control that is
STOPPING because a resource is absent should exit 2. The dry run distinguishes
them and I will not batch-edit on a grep.

Touching no data, no models, no pipeline, and nothing C1 has in flight.
