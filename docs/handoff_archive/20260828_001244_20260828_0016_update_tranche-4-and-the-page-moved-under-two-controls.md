# Update — Q7 tranche 4 done (43 of 100). And the sweep's two failures are one page change at 23:59 that Q9 made possible.

**2026-08-28 00:16 local · Code (background session)**

---

# THE SWEEP'S TWO FAILURES ARE THE SAME EVENT

    96 ok, 2 failed, 3 skipped, 0 NOT RUN, in 566s
    FAIL  _verify_extremity_placement.py     3 assertions
    FAIL  _verify_ship_page.mjs              2 assertions

**All five assertions are about one sentence**, and they read like this:

    renderMarkerNote still says the positions are NOT measured from the model
    and still says the derivation starts from the mount's NAME
    and B6 added no claim that anything is now measured from geometry
    and still says what the FALLBACK is - the mount's name, snapped, an estimate
    and admits it cannot say which of the two THIS ship's dots are

**Every one of them asserts an apology the page no longer needs to make.**

`testing/_src/loadout.src.html` changed at **23:59:07**, and the change is C1
**using the field Q9 emitted 40 minutes earlier**:

    function mountProvenance(cls){ ... for(const m of list){ if(m.from==="cig") cig++; } }

    /* THAT LIMITATION IS GONE FOR MOST OF THE FLEET. CIG's own geometry was ... */
    /* ONLY THE ESTIMATE IS NAMED. A dot on CIG's own coordinate is the
       ordinary case on 244 of 271 classes ... */

So the page now says, per ship, how many dots are CIG's own and how many are
worked out — **which is exactly Q9's DONE-WHEN, delivered by the other side of
the field I added.** The five assertions are the old hedge, and they are stale
rather than wrong-when-written.

**I have not touched them.** The note's wording is N9's subject, and
`_verify_ship_page.mjs` says so in its own comment: *"N9 REWRITTEN 2026-08-27 BY
THE SESSION THAT CHANGED THE PAGE (C1)"*. The page changed seventeen minutes ago
and the same session will almost certainly finish the pair. Rewriting someone
else's wording assertions while they are mid-edit is how two writers make a mess.

## And the rule 14 question is still open, with a fact in it

C1 said at 23:00 it would **not write into `testing/_src/` again** until Sleven
decided who owns those two files. `loadout.src.html` was written at 23:59.

**I am not making a second complaint out of it.** The record genuinely names
those files as C1's in two places, I overstated the rule once already tonight,
and the change is good work that used my field the day I added it. **But Sleven
has still not answered, and the question does not go away by being asked twice.**

## One line is explicitly mine, and the data for it exists

C1's new crafting line ends: *"INERT UNTIL THE DATA IS WIRED. `CRAFT` is emitted
by build_crafting_demand.py and the build has to copy it in — one line in Code's
`deploy_pages.py`."*

Both exist:

    build_crafting_demand.py                        23:12
    data-layer/derived/crafting-demand/craft_data.gen.js

**Not doing it in this pass.** The page that would read it is being edited right
now, and wiring a data file into the payload while its consumer is in flight is
the same mistake in the other direction. It is a named, bounded task and it is
next.

---

# Q7 TRANCHE 4 — THE SHOP AND DATABASE FAMILY

    labelled     43  (20 INDEPENDENT, 23 UNPROVEN)     was 37
    unlabelled   58                                    was 63

All five controls green after labelling.

**Two INDEPENDENT, and both for the same good reason - they leave the process.**
`_verify_shop_api.py` starts the real application and makes real HTTP requests,
and its own docstring explains why it refuses a TestClient: that would exercise
the same handlers while proving neither that the app starts nor that the router
is mounted. `_verify_shop_schema_db.py` plants bad rows and lets **Postgres**
refuse them — the evidence is what the database does, not what any Python this
project wrote thinks it would do.

**Three UNPROVEN**, all the same shape: `_verify_shop_checks.py`,
`_verify_shop_importers.py` and `_verify_commodity_xref.py` import the auditors,
the envelope loader and the xref builder respectively, so a wrong rule is wrong
on both sides. Each still proves the half that usually goes missing — the code
refusing input constructed here that it MUST refuse.

## A tool problem worth recording rather than working around

Tranche 4's first pass reported `_verify_shop_schema_db.py` as **NOT DONE:
anchor matched 0 times** — because that file is CRLF and the anchor was written
LF. **The right failure**: it named the file and skipped it rather than writing
something approximate.

The applier is now line-ending aware and reports which convention each file uses.
No file has had its line endings rewritten, which would have turned a six-line
label into a whole-file diff.

Sweep receipt currently red on the two stale controls above, so the deploy gate
is correctly refusing. Nothing committed since `fee621f`.
