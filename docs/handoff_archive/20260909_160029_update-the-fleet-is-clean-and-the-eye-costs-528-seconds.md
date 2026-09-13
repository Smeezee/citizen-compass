# Update — 256 of 256 hulls draw, and the number that decides the other eighteen is 528.7s

**Filed 2026-09-09 15:59 CDT.** Header produced by `date`, not typed.

## THE FULL CONTACT SHEET RAN. THE FLEET IS CLEAN.

    LOAD FAILED  0      EMPTY     0
    INVISIBLE    0      OVERFLOW  0
    ok           256 of 256       page errors 0
    retried once 0

    fleet median coverage 6.24%  ->  invisible below 1.56%  (min observed 2.63%)

**Nothing is near the line** — the closest hull sits at 2.63% against a 1.56%
threshold, a 68% margin. This is the first fleet-wide render check this project
has ever had on a schedule, and every hull the site can serve, draws.

Output at `checks/_diag_output/contact_sheet/index.html`. Gitignored, rule 21 —
internal working material, 256 frames, never published.

## THE COST

    contact_sheet_eye     528.7s   (8m 48.7s)
    panel_dismiss_eye       7.8s
    pixel_probe_eye         2.1s
                          538.6s   - the sheet is 98.2% of it

    auditor file group before   238s   (3m 58s)
    auditor file group after    777s   (12m 57s)

**The auditor layer runs DAILY and unattended** — read from the task itself, not
assumed. 528.7s nightly is affordable. The same 528.7s in the deploy sweep would
have been 30% of it, which is why the eyes belong where they were put.

**Consequence worth stating plainly: this machine now renders 256 hulls every
night, and it did not yesterday.**

## THE WRAPPER WAS TESTED AGAINST THE REAL OUTPUT, NOT ONLY MY FIXTURES

Nine proof cases use stand-in output that this file wrote. **A proof that only
ever sees output the proof itself produced is a proof about the proof**, so I
replayed the actual 256-hull run through the registered wrapper:

    [PASS] contact_sheet_eye: 256 of 256 hulls clean; LOAD FAILED 0, EMPTY 0,
           INVISIBLE 0, OVERFLOW 0, page errors 0

It reads the real bytes.

## RECOMMENDATION SENT TO ARCHITECTURE

Two classes of eye, two orders of magnitude apart: a single-page eye is 2-9s and
effectively free — register all eighteen if they are that shape. **A fleet-wide
eye is the entire budget, and there should be at most one**; a second fleet-wide
question belongs as another pass inside the sheet that already has the hulls
loaded, not as a second walk of the fleet.

## WHAT IS STILL BLOCKED

**Q49** is built, drift-clean, in the payload, and cannot deploy: the gate needs a
full sweep and `_verify_correspondence.py` is red with 74 findings in
`answered/`, none of them mine.

**The Stop hook** is authorised by Sleven twice in writing and refused by this
session's own permission layer on `.claude/settings.json`.

Nothing committed.
