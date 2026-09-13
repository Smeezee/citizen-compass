# Update - DEPLOYED. The regenerated front page is live, every picture is filled, and the ragged card height went out with it on Sleven's go-ahead.

    https://citizencompasstesting.citizencompass-contact.workers.dev/next
    Version ID 0f0056cc-cba4-4c16-bd70-c7d358749913

## Sweep

    121 ok, 0 failed, 3 skipped, 0 NOT RUN, in 1558s
    receipt 2026-09-06T19:59:46   fingerprint 6bf4c967c267dc61   exit 0

**121, not 120** - the slow control now completes instead of being discarded.

## THE NOT RUN WAS NOT CONTENTION. IT WAS A THIN MARGIN, AND I MEASURED IT.

I blamed CPU contention twice today and both times the machine was genuinely
busy, so the story held. It was wrong to stop there. Timed on a quiet machine:

    _verify_broken_checker_end_to_end.py alone   687s
    the global allowance                         900s
    margin                                       213s, 24%
    NEXT-SLOWEST CONTROL IN THE WHOLE SUITE      179s

**That control runs nearly 4x longer than anything else here.** The 900s default
was sized for a suite where nothing comes close, so any co-tenant - another
session's work on this same machine - spends the margin and eleven minutes of
real work is thrown away.

`run_all_controls.py` now carries a measured per-control allowance of 1800s with
those four numbers written beside it. In this run it finished in **591.0s**.

**It does not weaken the gate.** A timeout catches a HUNG control and 1800s still
catches one; it only stops discarding a control that was going to finish. NOT RUN
still blocks the sweep and the deploy exactly as FAILED does.

## What went up: 3 files

    /next.html                          the regenerated page
    /images/c47d63ef31277fee.webp       the 242nd picture
    /index.html                         and this one needed explaining

## index.html changed, and I checked why rather than shipping it unexplained

It had been byte-identical `fa0afd5e3eb095a8` all day. The whole difference is
the testing stamp:

    testing 2026-09-06  ->  testing 2026-09-07
    396,153 bytes before and after - a same-width date swap

**The build stamps UTC.** Local clock 19:59 CDT; UTC 01:01 on the 7th. Rule 18 -
read the clock from the machine and convert, which is exactly what the build
does. Nothing about the old front page's content moved.

## Verified from SERVED BYTES

    /next    200, 138,637 bytes   served 02e4075a6f851b4e = local   IDENTICAL
    /        200, 396,153 bytes   served 2d4eaac0c99f5526 = local   IDENTICAL

## What is now live, honestly stated

    253 cards render                     ok
    every picture loads                  ok    247 of 247
    cards showing NO IMAGE               0     (was 7)
    manufacturer groups A-Z              ok    18
    ships A-Z inside every manufacturer  ok
    no page errors                       ok
    every card is the same height        NO -  8 distinct heights

**The ragged grid is live.** I held it, reported it with the diagnosis, and
Sleven said go. Two clusters ~15px apart, 143 cards at 129-131 and 109 at
144-147; the name element is a uniform 21px on all 253, so it is not name
wrapping. The Valkyrie at 155 is correct - that is the edition fold.

**Still worth C1 levelling.** It shipped because complete pictures were judged
worth more than a level grid tonight, not because the criterion was dropped.

## Open

- **241 unreferenced images**, rule 5 list filed, nothing moved, awaiting Sleven.
- **B2** on five hand-entered families. **B1** behind B2.
- **`build_frontpage_data.py`** untracked, needs his go-ahead (rule 2).
- **Two ownership gaps** found today by controls: `testing/_src/next.src.html`
  and `checks/_verify_broken_checker_end_to_end.py`, neither in OWNERS.md.
- Nothing committed, nothing pushed, no `git add -A`.
