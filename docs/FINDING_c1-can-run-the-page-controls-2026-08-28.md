# FINDING — C1 can run 32 of the 33 page controls, and has been queueing them to Code for weeks on a premise that was only half true

    from    C1 (Cowork), 2026-08-28
    status  MEASURED. Not an inference — every control below was executed in
            the Cowork VM and its exit code read.

---

## 1. THE PREMISE THAT WAS WRONG

Every check-running item C1 has written for Code carries some version of this:

> **C1 WROTE THIS AND HAS NEVER RUN IT.** No headless Chromium in the Cowork
> VM; it reports NOT PERFORMED at the launch step.

**That sentence is true, and the conclusion drawn from it was not.** It is true
of the nine controls that drive Playwright. It is false of everything built on
`checks/_loadout_harness.mjs`, which is not a browser at all — it is a DOM stub
running the page's own script under `node:vm`. **Node is on this machine.**

    node --version        v22.23.2, in the Cowork VM

**Measured today, one at a time, exit codes read:**

    harness-based page controls        33
    run and pass here                  32
    fail                                1   `_verify_ship_page.mjs`, and it is
                                            failing on purpose — see Q14
    cannot run here (Playwright)        9   a real browser, genuinely absent
    cannot run here (deployed origin)   3   a statement about the served site
    cannot run here (PostgreSQL)       13+  psycopg2 / sqlalchemy, and the
                                            database is on the Windows machine

**So the honest division is not "Code runs the checks and C1 writes them".** It
is: **C1 can run anything that needs only the page's logic. Code is needed for a
real browser, the served site, the database, and PowerShell.**

---

## 2. WHAT THIS COST, CONCRETELY

`_verify_marker_note.mjs` was written, run, and **found to be wrong twice**
inside the same hour, without Code touching it:

- One assertion was red because a regex could not cross a line break in an
  indented template literal.
- **The same flaw made a different assertion silently GREEN** — the one testing
  that a phrase was ABSENT. A regex that can never match passes every negative
  test in a file.

Under the old division, both would have gone into `inbox/` as a queue item,
waited for Code, and come back as a failure report — with the silent green one
**not reported at all**, because it passed. It was found by running the thing.

**That is the general cost.** A control written by someone who cannot run it is
a control whose first execution happens in someone else's session, hours later,
with the author absent.

---

## 3. WHAT CHANGES, AND WHAT DOES NOT

**Changes.** C1 runs every harness control it writes, before filing anything.
A queue item that says "C1 has never run this" is now an admission that C1 did
not bother, not a statement about the machine — **unless the control needs a
browser, the served site, the database or PowerShell**, which it must then say
by name.

**Does not change.** Q8 stands exactly as written: `_verify_stage_still.mjs`
drives Playwright, C1 genuinely cannot run it, and it remains the only control
over the thing Sleven asked for most plainly. **Nothing here reduces what Code
is needed for; it reduces what he is needed for unnecessarily.**

**Also does not change: the build.** `build_deploy.py` reads PostgreSQL. A
Cowork session cannot build, so the harness runs against `testing/_src`, which
is the page's source and is exactly what these controls are about.

---

## 4. THE UNCOMFORTABLE PART

This was discoverable at any point by typing `node --version`. It was not
discovered because the limitation was written down once, correctly, about
browsers — and then carried forward as a general fact about the session,
repeated in queue item after queue item, and never re-tested.

**That is the same failure as the one found four hours earlier today**, where
`CURRENT-STATE.md`'s headline marker numbers had been carried forward from the
pipeline's manifests and were wrong at the last step. Both were true when
written. Both were quoted instead of re-measured.

**A number or a limit that gets repeated is exactly the one to re-measure**,
because repetition is what stops anybody looking.

— C1
