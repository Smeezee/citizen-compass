# Memo

To:      Build
From:    Engineering
Date:    2026-09-08
Status:  Answered
Subject: Q — the sweep receipt records where the time went. Sleven's order, and it is carrying a number you already compute rather than measuring anything new.

**Sleven ruled on the sweep-runtime budget by refusing to pick one, and gave a
reason worth reading:**

    2026-09-06 full sweep    123 controls    1,606 seconds    26.8 minutes
    2026-09-07 full sweep    125 controls    2,871 seconds    47.9 minutes

**The runtime moved 79% in a day and nobody noticed**, because
`checks/.last_sweep.json` records total seconds and nothing else. We cannot say
what a sensible ceiling is when we cannot say where the time went, and his words
were that any figure now would be *"a guess wearing a decision's clothes."*

## THE ORDER

`checks/.last_sweep.json` gains a **per-control elapsed time for every control
it ran.**

**This measures nothing new.** `run_all_controls.py` already times each control
and prints the seconds on every result line. This carries a number that already
exists into the receipt.

**The file is yours.**

**DONE-WHEN:** a full sweep writes a receipt from which the ten most expensive
controls can be listed **without re-running anything.**

Once three full sweeps have written that receipt, I bring him the composition
and he sets the ceiling from real numbers.

## THE WORKING FIGURE UNTIL THEN — AND IT IS NOT A GATE

**Sixty minutes. A REPORT LINE, NOT A GATE.** Cross it and say so. **Do not stop
a deploy over it.** His reasoning, stated plainly: 60 sits above the worst run
we have with room to spare, and for no better reason than that, which is exactly
why it is provisional.

## ONE THING HE IS NOT ORDERING YET

`_verify_broken_checker_end_to_end.py` at **528 seconds** was about a third of
the 2026-09-06 sweep on its own. **He is not ordering anything about it.** When
the receipt can show composition, the question becomes whether it needs to run
on every sweep or belongs on its own schedule. **Bring it back then, with the
numbers.** Not before, and not as a side-effect of this item.

## AND A CORRECTION TO THE DOCTRINE THAT CAME OUT OF THE SAME MEASUREMENT

`docs/UX_DOCTRINE.md` is adopted at **v6.2** and its Section 9 no longer polices
only browser controls. His measurement:

    browser controls (.mjs)    51 controls     274 seconds     17% of runtime
    everything else (.py)      71 controls   1,330 seconds     83% of runtime

**The three most expensive controls in the suite are not browser controls.** A
rule accounting only for browser cost polices the smaller half. The section now
reads: **any** new control's cost is measured and reported, and the budget is a
ceiling on TOTAL sweep runtime rather than a per-control allowance.

## ALSO NEW ON YOUR QUEUE

**Q49, Q50 and Q51** are at the head of `CODE'S QUEUE` in `NEXT.md` — the first
three items written under the doctrine, with their acceptance criteria stated
before execution. **Q49 first**, on his instruction: the ship page's "All ships"
link is a trapdoor off the new front page, and he hit it himself.

**Do not route those back to him.** Section 39's escalation list is the only
reason to stop and ask.

ANSWERS:

**DONE-WHEN is met, and it was met before I got here. The working figure was
not, and now is.**

## THE RECEIPT — ALREADY CARRYING PER-CONTROL SECONDS

`checks/.last_sweep.json` holds a `timings` map, written by `run_all_controls.py`
from the `secs` it already computed. An earlier Build session landed it.

**Your DONE-WHEN, exercised on the receipt that is on disk right now, with
nothing re-run:**

    receipt 2026-09-07T22:42:23    1,741.8s total    124 controls timed

     652.6s  37.5%  _verify_broken_checker_end_to_end.py
     224.8s  12.9%  _verify_control_bytes.py
     147.6s   8.5%  _verify_marker_mesh_distance.py
      84.9s   4.9%  _verify_find_build_step.py
      69.6s   4.0%  _verify_marker_positions.mjs
      45.0s   2.6%  _verify_version_single_source.py
      43.4s   2.5%  _verify_community_mark.py
      40.8s   2.3%  _verify_g3_matcher_delta.py
      29.4s   1.7%  _verify_extremity_placement.py
      28.1s   1.6%  _verify_deploy_guards.py

    the ten most expensive          1,366.2s          78.4% of the sweep

**That is one full sweep of the three you want before bringing him the
composition.** This one ran at 29.0 minutes, not 47.9 — the 2,871s run you cite
is not the current receipt.

**`_verify_broken_checker_end_to_end.py` is 37.5% of it on its own**, and it is
the only control over ten percent. I am saying the number and nothing else, as
instructed. Not raising it, not proposing anything about it, and it will be there
when you ask with three receipts.

## THE WORKING FIGURE — IT WAS NOT IMPLEMENTED AND NOW IT IS

Your order says of sixty minutes: **"Cross it and say so."** Nothing said it.
`3600` appeared nowhere in the sweep; the figure lived only in this memo.

**`run_all_controls.py` now prints, after the summary line and only after a FULL
sweep:**

    OVER THE WORKING FIGURE: 5400s (90.0 min) against 3600s (60 min), 1800s over.
    REPORTED, NOT GATED - this does not stop a deploy and is not a failure. The
    figure is provisional and the receipt's per-control timings are what a real
    ceiling gets set from.

**It cannot gate.** `sweep_runtime_note()` is a pure function that returns a
string or `None`; the caller prints it and the exit code is never touched.

**Why the program says it rather than a person remembering to.** Rule 26's
standing obligation. A human comparing 2,871 against 3,600 at the end of a
48-minute run is exactly the repeatable manual step that is supposed to be
removed — and it is the step that already failed: **the 79% move was there to be
seen and nobody saw it.**

**A `--only` or `--self-test` run is silent at any duration.** A subset's runtime
against a whole-suite figure is two different things being compared, which is the
same reason the receipt keeps them in separate files.

## RULE 12 — `checks/_verify_sweep_runtime_line.py`, 8 CASES, 0.24s

A report line that silently never fires is worse than no line, because everybody
assumes it would have said something. So both directions, and the boundary from
both sides:

    1,741.8s  the current receipt              silent
    2,871.0s  your 47.9-minute sweep           silent
    3,599.0s  one second under                 silent
    3,600.0s  EXACTLY on it                    silent - 60:00.0 is not over
    3,600.1s  a tenth of a second over         SPEAKS
    5,400.0s  an hour and a half               SPEAKS
    7,200.0s  but on a --only run              silent
        0.0s  a zero-length sweep              silent

When it speaks it must name **both** numbers and say **NOT GATED** — asserted, so
the line cannot decay into a bare number the reader has to go and interpret.
`--self-test` exits 1.

## THE COST OF EVERYTHING I ADDED TO THE SWEEP TODAY, PER SECTION 9

    _verify_document_checks.py      0.6s
    _verify_eyes.py                 1.4s
    _verify_sweep_runtime_line.py   0.1s
                                    ---
                                    2.1s   0.12% of the current sweep

The six document checks and the two eyes themselves are on the auditor layer and
add **nothing** to the sweep. Only their proofs are swept.

## ONE DESIGN DECISION YOU SHOULD KNOW ABOUT

**The figure is defined in exactly one place** —
`SWEEP_WORKING_FIGURE_SECONDS` in `run_all_controls.py` — and the control reads
it from there rather than typing `3600` of its own. I considered also reporting
it from the auditor layer's `sweep_runtime_drift` checker and decided against it:
that would put the number in two files, which is the defect I have just spent the
afternoon telling you about on the desk list. **One definition, one place that
says it.**

Nothing committed.
