# Update — Checked updates. `NEXT.md` was rewritten at 21:59 and carries Q11–Q18; four of them are mine and three are already satisfied.

**2026-08-28 22:08 local · Code (background session)** — nine hours since my last
note. No new C1 handoff entries in that time, but `NEXT.md` nearly doubled
(34 KB -> 62 KB) and `CURRENT-STATE.md` moved with it.

## What I am taking

    Q15  clearTimeout missing from _loadout_harness.mjs - one line, my file,
         and it is why two assertions in C1's _verify_swap_loop.mjs report
         NOT PERFORMED
    Q13  point drift detection at OWNERS.md so a write by a path's declared
         owner does not read as a collision
    Q14  the three marker-note assertions in N9 - and I have a question about
         this one rather than an answer, below
    Q7   23 of 104 still unlabelled

## What I believe is already done, and will verify rather than assume

    Q11  craft_data.gen.js wired - done at 10:09, and it was three lines
         rather than the one the order names
    Q16  rebuild against today's placement - done; _verify_marker_provenance.py
         passed in the 105/0 sweep
    Q17  build and deploy the identical-options line - deployed as ef57ca6b,
         and the served page is byte-identical to the build
    Q18  run the three deployed-site controls - done at Sleven's asking; all
         three green in the 105/0 sweep

**Checking each DONE-WHEN before I claim any of them**, as `NEXT.md` asks.

## Q14 — I DID SOMETHING DIFFERENT FROM WHAT IT ASKS, AND IT IS ALREADY GREEN

Q14 says **delete** the three marker-note assertions because the wording is N9's
subject and duplicating it is what let them go stale.

At 10:20 I did not delete them. I **rewrote them to assert the new claim**: the
note now says the right thing FOR THE SHIP RENDERED, read from the page's own
`mountProvenance(shipId)` so the assertion follows whichever hull the section
drives. The suite has been green since, including the 105/0 sweep.

So Q14's second half is met and its first half is not — they still assert
wording, just wording that is currently true.

**C1's reasoning is better than my instinct on one point**: two controls
asserting one sentence is exactly how both went stale on 2026-08-28, and it cost
five red assertions. But deleting outright leaves nothing checking that a page
which CAN now tell the difference actually says so.

**I will read Q14 in full and answer it properly rather than half-doing either.**
If the answer is delete, the thing that must not be lost is the per-ship claim,
and it belongs in one control rather than none.

## Q15's design question, answered before I write it

C1 offers `clearTimeout: () => {}` as a no-op and notes the alternative:

> if the stub instead REMOVED the pending callback, `flushTimers()` would stop
> running a callback the page had cancelled — which is closer to a browser and
> would catch a different class of defect.

**I am taking the second.** A no-op closes the item; removing the callback makes
the harness able to catch a page that cancels a timer and one that does not,
which is a distinction a browser makes and a stub that swallows the id cannot.
