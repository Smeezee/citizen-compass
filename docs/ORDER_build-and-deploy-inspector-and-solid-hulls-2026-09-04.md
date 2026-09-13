# ORDER — build and deploy again. My fault, not yours.

> NOTE ON THIS FILE. It was written to `inbox/` in two passes and the inbox
> watcher moved each pass out separately, leaving Code two half-orders in
> `docs/` and an empty inbox. Both halves are preserved under `_to_delete/`.
> **Never append to a file in `inbox/`** - the watcher takes it within about a
> minute. Compose it whole, write it once.


From: C1 (Cowork), 2026-09-04
For: Code

## What went wrong
Your build ran at **16:48**. I created `testing/_src/_inspect.src.html` at **16:49:39**
and edited `deploy_pages.py` at **16:49:46** — ninety seconds too late. You did
exactly what the order said. The source it depended on did not exist yet.

Sleven opened the URL and got nothing. That is on me: I published an order and then
kept editing the thing it depended on.

**The comment-leak half of that order worked.** `_verify_no_leaked_comments.py` now
passes on all 23 pages; index.html and loadout.html are clean.

## RUN THESE

```
python testing/_src/build_deploy.py
```

```
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_testing.ps1
```

## ONE CHANGE NEEDED IN YOUR FILE FIRST — attribution, not cosmetics

`testing/_src/build_deploy.py`, add `'_inspect.html'` to `_SHIP_CONTENT_PAGES`:

    _SHIP_CONTENT_PAGES = {'index.html', 'loadout.html', 'holo.html', '_inspect.html'}

**The inspector displays 258 CIG ship models.** Your own comment on that set says a
page that shows a ship and does not say where it came from is the thing the rule
exists to prevent. Without this line it ships the trademark strip and NOT the source
and takedown notice.

## What I verified this time, in a browser, before writing this
I simulated your build exactly — `attribution.trademark_block()` plus
`source_notice()` appended before the closing body tag, then
`strip_comments.strip_for('_inspect.html', ...)` — and loaded the RESULT against the
real models folder.

    trademark only ....... OK, 212 comments stripped, 1,154,730 bytes
    with source notice ... OK, 212 comments stripped, 1,155,581 bytes
    in a real browser .... loads, next/prev, jump to ship 201, mark-broken,
                           reason chips, side toggle, report. 0 page errors.
                           Both notices visible at the bottom of the window.

## Two things that simulation caught, which shipping blind would not have

**1. The build would have REFUSED the page.** `strip_css` raised
`unterminated /* in CSS at offset 162` and `_for_deploy` exits on that — so the whole
build would have died, not just this page. Cause: a CSS comment I wrote contained a
literal closing-body tag, which cut the `<style>` block short in `strip_html`.
Reworded. **The tooling was right and my page was wrong**, same as the glossary leak
this morning.

**2. The attribution strip would have been invisible.** It is
`position:sticky;bottom:0`, and my page had `#app` at `height:100%` inside a body with
`overflow:hidden` — so the notice would have been pushed past the fold on a page that
shows 258 of CIG's ships. Body is now the flex column and `#app` takes what is left;
anything the build appends is the next row down and is visible. Confirmed in the
screenshot.

## Housekeeping
- `testing/_deploy/_inspect.html` — my hand-made copy — moved to
  `_to_delete/_inspect.html.handmade_20260904`. Only a real build should produce that
  file now. The deploy guard passes with it absent and with it present.
- `deploy_pages.py` still carries the one line added earlier:
  `('_inspect.src.html', '_inspect.html')`. Without it the guard REFUSES the deploy —
  proven by removing it and re-running the guard.
- `deploy_pages.py`, `check_deploy_clean.py` and `strip_comments.py` have no owner in
  `OWNERS.md`. C1 proposes you and has not claimed them; the one edit is declared in a
  GAPS section there.

## Then tell Sleven
`https://citizencompasstesting.citizencompass-contact.workers.dev/_inspect.html`

---

# ADDED AFTER THE ABOVE — the see-through fix rides this same build

`testing/_src/cc_viewer.js` (C1's file) now draws every hull double-sided. This is
the defect Sleven found in his own screenshot and it is on the live site too.

Changed: the `solid`, `hull` and `depth` materials in `_buildHoloMaterials`, plus
`Viewer.prototype.load` which now sets `_hullSide` from `cb.ship`. `xray` is
untouched — it was already DoubleSide on purpose.

**The depth pre-pass is the one that is easy to miss.** It writes the hull's depth.
Left front-side it omits exactly the triangles the surface pass now draws, and the
hull still reads through.

**This is a regression, not a gap.** `Viewer.prototype.load`'s own H1 comment records
that a PBR pass "set DoubleSide" and was removed. Removing it is what introduced
this. A comment did not stop it coming back.

Previous file preserved at `_to_delete/cc_viewer.js.pre_doubleside_*`.

## New control: `checks/_verify_hull_is_solid.mjs` (C1)
Loads the DEPLOYED `cc_viewer.js`, pulls out the real `_buildHoloMaterials` and its
real helpers, runs it under a stub THREE, and reads the `side` the materials
actually come out with. Behaviour, not a grep — a grep for "DoubleSide" passes on a
file where the word only appears in a comment.

**It earned its keep twice before it was finished:**

1. **It caught a bug in the fix.** `THREE.FrontSide` is `0`, so
   `this._hullSide || THREE.DoubleSide` threw FrontSide away. Every ship on the
   exception list would still have been drawn solid — the list would have looked
   wired and done nothing. Now `ccSideOr()` tests for undefined, never truthiness.
2. **Mutation testing caught a hole in the check itself.** Deleting the
   `ccHullSide()` call from `load()` left it GREEN, because a bare search for
   `ccHullSide(` matches the function's own declaration. It now looks inside
   `Viewer.prototype.load` specifically.

Three mutations, all correctly refused:

    surface pass back to FrontSide ....... FAIL
    only the depth pre-pass reverted ..... FAIL
    exception list stops being consulted .. FAIL
    unmutated ............................ ok

## The exception list is empty on purpose
`CC_SEE_THROUGH_HULLS = []` at the top of the viewer. Sleven is walking all 258 in
the inspector and will name the few that should keep the see-through look. Add names
there exactly as CC_MODELS spells them — exact string equality, rule 2, no fuzzy
matching. Empty means every hull is solid.
