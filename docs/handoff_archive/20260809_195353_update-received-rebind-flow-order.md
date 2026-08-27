# Update — received: build the rebind-and-save flow, shorten the page, make it obvious

From C1, 2026-08-10, off Sleven's hands-on test of `/keybinds`. Logging receipt
before starting, per rule 13.

C1's central claim is that there is **no rebind capability at all** — that this
is a missing feature, not a discoverability problem. Verifying that myself
before building on it, since I wrote pass 2 and would rather find my own gap
than assume someone else's reading of it.

Three things to build:

1. **Rebind flow** in the action browser — click a binding cell, capture the
   next key/mouse press, write to a working copy, re-render both views, export
   the working copy. Conflicts flagged by name, not auto-resolved.
2. **Collapse the 691 rows** — sections closed by default, search/filter must
   auto-expand any section containing a match.
3. **Say what the page is** at the top, and caption the controls.

One design question I expect to hit immediately, flagged now: the action browser
renders `KB_ACTIONS`, which is generated from the game's **default** profile.
An imported profile is the user's **overrides**. Those are two different data
sets, so "the current binding" the browser shows today is the game default, not
what the person actually has bound. A rebind flow that ignores that would show
one answer while exporting another. Expect an overlay step.

Build only. No deploy. `sc_export.js`, `roundtrip.js` and `mutate.js` not to be
touched.
