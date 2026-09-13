# ORDER — take the takedown notice off the inspector. My line, my mistake.

From: C1 (Architecture), 2026-09-05
For: Build (Code)
Priority: do this before the remaining queue items.

## The line and who put it there

`testing/_src/build_deploy.py`, `_SHIP_CONTENT_PAGES`:

```
_SHIP_CONTENT_PAGES = {'index.html', 'loadout.html', 'holo.html',
                       # The inspector shows 258 CIG ship models. ...
                       # Added 2026-09-04 on C1's order; the page itself is C1's.
                       '_inspect.html'}
```

**I ordered that on 2026-09-04 and it was wrong.** The file is yours, so the
edit is yours - I have not touched it.

## Why it was wrong

`_inspect.html` is a **private internal tool**. It is password-gated, it exists
so Sleven can click through 256 ships and mark defects, and **it is going to be
deleted when that job is finished.** It has no visitors and never will.

The source-and-takedown notice exists so that a page showing CIG's ship models
tells a stranger where they came from and how to ask for them to be removed.
**There is no stranger here.** Putting "if you would like any of this taken
down, write to..." on a scratch page nobody outside this project can open is not
compliance, it is noise on a tool - and Sleven read it as exactly that.

The reasoning in the comment - *"a page that shows a ship and does not say where
it came from is what this set exists to prevent"* - is sound for a public page
and does not apply to a private one. I applied a public-page rule to a private
page without noticing the difference.

## TASK

1. **Remove `'_inspect.html'` from `_SHIP_CONTENT_PAGES`**, and the comment block
   that justifies it. Replace it with a short note saying the set is for pages a
   member of the public can reach, and that the inspector was removed on
   2026-09-05 because it is private, password-gated and temporary.
2. **`_verify_takedown.py` will need the same edit** if it asserts the notice is
   present on `_inspect.html`. Check before you change it - if it derives its
   list from `_SHIP_CONTENT_PAGES` it needs nothing.
3. Rebuild and confirm the notice is gone from `_inspect.html` and **still
   present on `index.html`, `loadout.html` and `holo.html`.** That last half is
   the one that matters: this must remove a notice from one private page, not
   weaken it on the three public ones.

**DONE-WHEN** the inspector carries no source/takedown notice and the three
public pages still do, both stated from the built files rather than from the
source.

## Standing constraints

- Testing only. Do not deploy the live site.
- Do not `git add -A`. Nothing commits or pushes without Sleven's go-ahead.
