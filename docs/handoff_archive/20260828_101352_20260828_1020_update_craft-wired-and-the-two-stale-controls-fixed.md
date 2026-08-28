# Update — The crafting data is wired (it was three lines, not one), and the two controls Q9 stranded now assert the stronger claim.

**2026-08-28 10:20 local · Code (background session)** — Sleven: *"do the
deploy_pages line and keep going"*.

---

# 1. THE CRAFTING DATA — AND IT WAS NOT ONE LINE

C1's note said *"the build has to copy it in — one line in Code's
`deploy_pages.py`"*. Measured, three things were missing and the one line alone
would have shipped nothing:

    build_deploy.py     craft_data.gen.js lives in data-layer/derived/, and
                        PAGES copies from _src. Nothing brought it across.
    deploy_pages.py     the one line C1 named.
    loadout.src.html    the page had NO <script src="craft_data.gen.js">.
                        `craftLine()` checks `typeof CRAFT==="undefined"` and
                        returned nothing, silently, on every row.

All three done. **The page had been sitting on a working feature with no way to
load its data since 23:59 last night.**

## The copy fails closed on the PAIRING rather than on the file

    page asks + generator produced   copied, and the size printed
    page asks + no file              REFUSED - a script tag pointing at nothing
                                     is a 404 and a silently absent feature
    no page asks + file exists       reported, not copied - so a stale 88 KB
                                     does not ride along unnoticed

## Measured, not assumed

    CRAFT recipes                                 452
    fittable parts on the page                  3,283
    parts with a recipe the page can show         452

**452 of 452.** C1's join is CIG's own class name, case-folded, exact — and
every recipe lands on a part a reader can actually fit. Nothing was dropped in
the wiring.

    crafting data: copied into _src (87,949 bytes)
    pages copied: ... loadout_marker.gen.js, craft_data.gen.js, stick-test.html
    deploy guard: _deploy contains only known assets - safe to deploy

The guard accepted it without a separate edit, because `deploy_pages.py` is the
one list both the build and the guard import — rule 14 paying for itself.

---

# 2. THE TWO STALE CONTROLS, REWRITTEN RATHER THAN RELAXED

Five assertions across two controls demanded the page still apologise for
something Q9 fixed. The page now counts each ship's own dots:

    All 7 dots on this model come from the game's own ...
    5 of the 12 dots on this model come from the game's own ...
    The other 7 have no position in the ...

**Asserting the apology would now be asserting a falsehood.** What actually
needs defending is not that the page hedges — it is that an estimate is still
NAMED as an estimate wherever one is drawn, and that the page never claims a dot
was measured off the mesh.

`_verify_extremity_placement.py` **27 passed, 0 failed**:

    the note still names an estimate AS an estimate, for the hulls that have them
    and still says an estimate starts from the mount's NAME
    and it does NOT claim a dot was measured off the mesh
    and the per-dot provenance is what it counts, so the sentence is about
        THIS ship rather than the fleet

`_verify_ship_page.mjs` **242 assertions, 0 failed**. It reads the page's own
`mountProvenance(shipId)` and asserts the branch that matches the ship being
driven, so it follows whichever hull the section picks:

    every one of this ship's 7 dots is CIG's, so the note does not offer an
        estimate it does not have
    and the old fleet-wide hedge is gone - the note is about THIS ship
    and it says so as a count: "All 7 dots"

## One of them was asserting a code comment, and had been for a while

`"measured from the model" not in page` fired on **the note's own changelog** -
a `/* ... */` comment explaining what the sentence used to say. The original
worked around it by deleting the substring `"not measured from the model"`
before searching, which worked exactly as long as that sentence existed.

Comments are stripped before the absence check now. **An assertion that fires on
a file's history is asserting the wrong text.**

## And one of mine was nonsense, caught by its own failure

My first replacement contained `/${pv.cig}|all/.test(String(pv.cig))` - a regex
built from a number and tested against that same number, which can only ever be
true. It failed on the other half of the `&&`, which is the only reason I looked
at it. Replaced with three real assertions, one per branch of the note.

---

# 3. WHILE I WAS IN THERE

The marker counts moved again under C1's 23:45 overlay update, and the
provenance tally still closes exactly:

    hull markers   6,326 on 269 hulls
    provenance     2,006 from CIG geometry, 105 name-derived, 4,215 ancestor
                   = 6,326

**2,006 mounts on CIG's own coordinates**, up from 1,691 last night.

Full sweep running for a clean receipt; the deploy gate is refusing until it has
one, which is correct. Q7 stands at **43 of 100 labelled, 58 to go**.
