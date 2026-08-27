# HANDOFF — the 35 section descriptions now exist in the repo. Code's blocker on 2A pass 2 is cleared.

    from      C3 (Cowork), 2026-08-09
    for       Code (via C1)
    answers   docs/handoff_archive/20260809_172751_update-2A-pass2-...md, "NOT MET" item 2
    location  data-layer/derived/keybind-sections/kb_section_desc.json
              data-layer/derived/keybind-sections/MANIFEST.json

---

## 1. Code was right, and the blocker was mine

Code's update says the 35 section descriptions "live in a prototype that is not in this
repo — I searched." **That is correct.** They were in my builder prototype's `data.json`
and nowhere else, and my work order referred to them as if they were repo data. That was my
error, not a gap in the search.

Code declined to write 35 plausible sentences rather than ship unauditable text. **That was
the right call and it should be the standing one** — authored prose that looks like
extracted data is exactly the sort of thing this project cannot tell apart six months later.

They are now on disk, written to `data-layer/derived/` per the established pattern for
derived output that the inbox watcher's classifier cannot route. Not dropped in `inbox/` —
a `.json` array or an unrecognised shape would have been shunted to `_needs_review/`, which
is where five files from order 1 ended up this afternoon.

## 2. What the file is, and what it is not

**It is authored prose.** Thirty-five sentences I wrote explaining what each section
controls, so a player knows what they are about to bind. It carries no
`last_verified_patch`, because there is nothing in a patch to verify it against.

**It is not extracted from the game and not from CIG.** Anyone reading it later should be
able to tell that immediately; the file says so in its own `note` field and the manifest
says it again under `what_this_is_NOT`.

## 3. Two discrepancies found while checking it, both resolved

Keys are compared against the distinct `group` values in
`data-layer/processed/keybinds_site.json`: **35/35 exact, no extras, no gaps.** Getting
there needed two corrections.

**`Other` was dropped.** The prototype had an "Other" catch-all bucket. It is an artefact of
how the prototype grouped its own leftovers and is not a section in the repo data. Shipping
it would have created a 36th section that exists nowhere.

**`Vehicle - Mobiglas` was added, and is worth a note.** It is a real section in the repo
data that the prototype never displayed, because **all 28 of its actions are unlabelled** —
`label: null` on every row — and the prototype browsed only the 691 labelled ones. I wrote
its description against the actual action names (`ui_3d_display_*` — pan, rotate, zoom, pin
on the mobiGlas holo display) rather than guessing from the section title, and the text
states plainly that the game names none of these actions, so a reader is not left wondering
why the section is empty.

This matters for pass 2's own numbers: the browser will show 34 sections with content and
one that is legitimately empty. **That is the data being honest, not a bug**, and the page
should say so rather than hiding the section.

## 4. What Code needs to do

Emit it from `build_kb_actions.py` as `KB_SECTION_DESC`, the same way the action data is
already generated — read from `data-layer/derived/keybind-sections/kb_section_desc.json`,
never pasted into the page. The generator already owns `kb_actions.gen.js`; this is one more
key in the same output, so no second writer is created.

Pass 2's acceptance point 3 should move from "section descriptions ❌ — no source data" to
met. **The font half stays NOT MET** — that is Sleven's licensing call and nothing here
touches it.

## 5. Two things in Code's updates worth recording beyond this order

**The build-ordering defect is the most valuable thing found today, by anyone.**
`inject_engine.py` ran after `index.html` had been assembled from an in-memory string, so a
`device_engine.js` change reached the index page only on the *next* build — silently, exit
0, with a comment directly above the call asserting the guarantee the code did not provide.
Code found it by grepping the built artifact for a symbol the patch had just added, which is
the only thing that would have shown it. **Any past session that patched the engine and
built once shipped an index page carrying the previous engine.** That is worth a line in
`CURRENT-STATE.md` independent of this order.

**My order had a real gap Code caught:** `SCX` is not present on the index page, because
`device_engine.js` is injected into both hosts but only `keybinds.src.html` loads
`sc_export.js`. Unguarded, the identity code would have thrown there. The order did not
mention it. Guarded call sites and a fall-through to the labelled guess is the right
handling.

## 6. What I checked and what I did not

**Checked:** all 35 keys against the distinct `group` values in `keybinds_site.json`, with
an assertion rather than a read-through; the 28 `Vehicle - Mobiglas` action names and their
null labels; per-section labelled-action counts, which are in the file so the page can show
them.

**Did NOT check:** whether the prose reads well to a player who has never flown — it is my
writing and I am not the right judge of it. **Anything in it that is wrong about the game is
wrong because I wrote it wrong**, and it should be corrected in the data file rather than
patched in the page. I have also not run `build_kb_actions.py` against it; that is Code's.
