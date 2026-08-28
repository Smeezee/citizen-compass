# Update — 101 controls green, the gate let it through, and it deployed. Q10's DONE-WHEN is closed at both ends. Q7 is past halfway.

**2026-08-28 10:45 local · Code (background session)**
Version `00321a0b-3c9b-45ea-aedd-5c368b857919`.

---

# Q10 — CLOSED

    101 ok, 0 failed, 3 skipped, 0 NOT RUN, in 679s

    sweep   : 101 control(s) green against this exact payload (2026-08-28T10:37:16)
    gate exit=0

**The first clean sweep receipt this project has ever had**, and the gate read it
and let the deploy through.

Q10's DONE-WHEN needed both halves and now has both:

    a deliberately-reddened control STOPS a deploy   proven in section 11 of
                                                    _verify_deploy_guards.py,
                                                    on both scripts
    a swept, clean payload GETS THROUGH              proven here, on the real
                                                    456 MB payload

**A gate that only ever refuses is not a gate either.** Until this run the
passing side had only been shown against throwaway fixtures.

## What it took to get there, and none of it was the gate being wrong

Three sweeps failed before this one, and every failure was a real staleness the
gate surfaced rather than a defect in the gate:

    _verify_rule16_labels.py        a control 90 seconds old with a label the
                                    regex could not read
    _verify_extremity_placement.py  3 assertions demanding an apology Q9 removed
    _verify_ship_page.mjs           2 more of the same
    _verify_child_markers.py        a baseline predating C1's 23:45 overlay
    _verify_placer_candidates.py    two ports differing in the fifth decimal

**Five controls, five different kinds of stale, none of them a bug in the
thing being shipped.** That is what 94 controls that could not stop anything
had been hiding.

---

# THE DEPLOY

    Found 3 new or modified static assets to upload
    + /craft_data.gen.js
    + /loadout_marker.gen.js
    + /loadout.html

Verified from outside rather than from the build log:

    /craft_data.gen.js            HTTP 200, 87,949 bytes
    served /loadout               carries <script src="craft_data.gen.js">
    _verify_deployed_links.mjs    SWEEP CLEAN, canary reporting

**The link sweep went from 18 internal references to 19** — it found the new
script tag by itself, which is a second, independent confirmation that the page
really does load the file.

---

# Q7 — TRANCHE 5, AND PAST HALFWAY

    labelled     52  (23 INDEPENDENT, 29 UNPROVEN)     was 43
    unlabelled   51                                    was 58

All seven controls green after labelling.

**This tranche is the checker-of-checkers family**, and it produced an
observation worth keeping rather than seven near-identical labels. Six are
UNPROVEN for the same reason and each says so in the same words:

> This is a RULE 12 control, and rule 16 is a different axis. Proving a checker
> fires on input that must trip it and stays silent on clean input is exactly
> what rule 12 asks for, and this file does both halves. **Being UNPROVEN under
> rule 16 is not a criticism of it** - it is the observation that a checker
> cannot be an independent source of truth about itself.

**The one INDEPENDENT is instructive by contrast.**
`_verify_never_delete_guard.py` does not ask the guard whether it refused - it
**SELECTs the row back out of the database**. Its own second paragraph says why:
a delete that failed for some other reason would look identical from the guard's
side. Postgres is the witness, and Postgres did not write the guard.

`_verify_schema_checks.py` is the near miss, and its label says so: the offending
state is a **real table in a real database**, so the condition being detected
genuinely exists rather than being a fixture pretending to. Only the verdict is
the checker's own — which is enough to make it UNPROVEN, and worth distinguishing
from the ones whose input is a temp directory.

---

# WHERE THINGS STAND

    Q1-Q6, Q8, Q9, Q10   done
    Q7                   52 of 103 labelled, 51 to go
    C1's crafting line   wired and serving

Nothing committed since `fee621f` — there is a substantial working tree now:
Q9's provenance field, Q10's whole mechanism, five Q7 tranches, the crafting
wiring, three re-baselined controls and C1's page work.
