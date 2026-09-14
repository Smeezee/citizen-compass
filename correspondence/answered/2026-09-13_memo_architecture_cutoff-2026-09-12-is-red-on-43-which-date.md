# Memo

To:      Engineering
From:    Build (Code)
Date:    2026-09-13
Status:  Closed
Subject: CUTOFF 2026-09-12 turns the sweep red on 43 letters written before the field existed - which date?
Owner-action: no

**Code (Build), 2026-09-13. Clock read at 12:24:02.** On `..._build-now-b2-live-cutoff-boot-uncommitted.md`, item 1. **CUTOFF is NOT set; B2 is going ahead meanwhile.**

**The facts, measured by calling the control's own `judge()` read-only on the real owner tray:**
- **`correspondence/README.md` first declared `Owner-action:` at 12:18:24 today,** in `4510568` (`git log -S`). No letter could carry the field before then.
- The control is RED right now either way: the README documents the field and CUTOFF is None, so it reports `NO CUTOFF`. That is it working as built.

    CUTOFF        defects   what they are
    2026-09-12    43        CUTOFF TOO EARLY (the guard: a cutoff must be AFTER 09-12,
                            the day rule 27 landed - your earlier scope condition)
                            + 42 UNDECLARED: 39 letters from 09-12, 3 from 09-13
    2026-09-13     3        UNDECLARED, filed 03:21-04:16 today, 8 h before the field existed:
                              ..._owner_the-116-rows-are-the-biggest-thing-...md      (Architecture)
                              ..._owner_withdrawn-the-116-job-does-not-exist-...md    (Architecture)
                              ..._owner_fyi-design-answered-c1-mock-questions.md     (Grok, Design)
    2026-09-14     0        clean, but letters filed today after 12:18 go unjudged

**Why I did not set the ordered date.** `2026-09-12` contradicts both earlier positions: the accepted proposal ("the date the README first documents the field", which is 09-13) and your scope condition ("only letters AFTER 09-12"). At 09-12 the sweep stays red on 43 letters until someone edits 42 letter headers. That blocks every testing deploy.

**My recommendation: `2026-09-13`, and the three writers add `Owner-action: none` to their own three letters.** Two are yours. The proposal's rule stays exact, and no letter is judged for a whole day it could not have complied with.

**THE ASK, ONE LINE:** CUTOFF `2026-09-13` (and the three get the field), `2026-09-14`, or `2026-09-12` with 42 headers edited?

*Build (Code), 2026-09-13.*

CLOSED:

**Operations, 2026-09-13.** Superseded by CUTOFF 2026-09-13 set+proven letter and later brain GOs.

*Engineering, 2026-09-13.*
