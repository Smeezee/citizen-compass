# PROMPT FOR CODE — build the actual rebind-and-save flow, then fix the page length and clarity

    from    C1, 2026-08-10
    for     Code
    basis   Sleven's own hands-on test of `/keybinds`, KBM mode, just now:
              "I do like what it is. I didn't see a way to actually edit it
              so I could [change a binding], bring it out and save it... it
              needs to be shorter, not such a long scroll... it needs to be
              very obvious what the page is and what the controls are."
    scope   testing/_src/keybinds.src.html only. Build only, do not deploy —
              separate go-ahead covers pushing this live, same as every order.

---

## 0. §1 is a real gap, not a discoverability problem — read this before assuming there's a hidden button

I read the actual page source before writing this, not just the deployed
render, because "I didn't see a way to edit it" is exactly the kind of claim
worth checking before writing a UI-polish prompt for a feature that might
already exist.

**There is no rebind capability anywhere in `keybinds.src.html`.** Confirmed
by reading both click handlers:

- The visual keyboard board's click handler (`document.addEventListener(
  'click', e => { if(dev!=="KBM")return; const k=e.target.closest(
  '.key[data-id]')...` around line 690) only **displays** what's bound to the
  clicked key in the `#rk`/`#ract` readout panel. It does not mutate anything.
- The action browser (`#kbb`, built in pass 2) renders `KB_ACTIONS` into a
  plain `<table>` — label, current binding, description — with **no click
  handler on the rows at all.** It's a reference list, not an editor.
- The export function (`expBtn.addEventListener('click', ...)`) only ever
  writes out `imported.binds` **completely unchanged** if a profile was
  imported, or an empty device-only profile if not. Nothing anywhere
  constructs a modified `binds` array.

**This was in scope from the start and didn't land.** `docs/WORKORDER_
builder-ui-and-viewer-2026-08-09.md` §item 3 says "Import, **edit**, export of
a real mapping file" — pass 1 built import/export, pass 2 built browse. Edit
is the piece that's still missing, not a UI-clarity issue layered on top of
something that already works. Build it now.

---

## 1. The rebind flow

**Entry point: the action browser table (`#kbblist`), not the visual board.**
It already lists every action with its current binding across all input types
(keyboard, mouse, joystick, gamepad — the `a.k / a.mo / a.j / a.g` fields
`binds()` already joins together), it's searchable and filterable, and it
covers all 691 actions, not just the ones with a physical key on a KBM board.
That's the one place a rebind UI naturally covers the whole game rather than
just the visible keyboard layout.

**Behavior:**

1. Click a binding cell (`.bind` column) → enter a "listening" state, visibly
   different (the cell should say something like *"press a key, click a mouse
   button, or Esc to cancel"* — make the listening state impossible to miss,
   this directly answers Sleven's "make it obvious" ask).
2. Capture the next `keydown` or `mousedown` (respect existing exclusions —
   don't let this fire while the search box has focus, same guard the board's
   `capture` toggle already respects).
3. Write the result into a **working copy** of the current binds, not
   `imported.binds` directly — keep the original import untouched in memory so
   "did I actually change anything" stays answerable, same honesty principle
   the export code already follows ("no rebinds ... an honest empty profile
   rather than a pretend one").
4. Re-render the affected row immediately, and re-render the visual board too
   if the action has a KBM binding — the two views must never show two
   different answers for the same action.
5. Export uses the working copy. **The untouched-binding round-trip guarantee
   still has to hold** — `roundtrip.js` / `mutate.js` exist specifically to
   catch this class of regression; run them after wiring this in, don't just
   eyeball one export.

**Conflicts — flag, don't silently allow or silently block.** If the newly
captured input is already bound to a different action in the same layer, warn
in the UI (name the other action) before committing the change, and let
Sleven's click confirm it either way. Don't auto-resolve it and don't hard-
block it — this project's standing rule for ambiguous cases is flag, not
auto-fix.

**Unbind:** clicking a bound cell's clear affordance (however you choose to
expose it — an "×" next to the capture prompt is reasonable) should remove
that binding from the working copy, not just visually hide it.

## 2. The page is too long — collapse it

By default the action browser renders all 35 sections open, all 691 rows in
the DOM at once, under a full-width visual keyboard board that's already tall.
That's the "long, slow scroll" complaint.

- **Sections collapse by default.** Click a section header to expand it.
  Provide an "expand all / collapse all" control for anyone who wants the old
  behavior back.
- **Searching or filtering by category auto-expands whatever matches** — a
  collapsed section that happens to contain the thing you searched for is a
  worse bug than the current flat list, so make sure a match is never hidden
  behind a closed section.
- Consider whether the visual keyboard board itself needs to be full height
  by default, or whether it could collapse/shrink once a device mode is
  chosen — your call, but the goal is: get to useful content without a
  monitor's worth of scrolling first.

## 3. Make the page obvious

Add a short, plain-language block at the top of the page — above the mode
switcher is probably right — stating what this page is and what to do with
it: view your Star Citizen keybindings, import your real profile, browse
every action the game defines, click a binding to change it, export when
done. A sentence or two, not a wall of text. Label the existing controls that
currently rely on someone guessing (the Capture toggle, the device-mode
buttons, import/export) with a short inline caption if they don't already
have one — check what's there now before assuming something needs adding.

## 4. What NOT to do

- Do not touch `sc_export.js`, `roundtrip.js`, or `mutate.js` — the write-back
  format logic is proven and this order builds on top of it, not inside it.
- Do not touch `holo.src.html`, `build_holo_data.py`, or anything from the
  holo-viewer order in flight.
- Do not touch fonts or `MANUAL_MATCHES`.
- Do not deploy. Build only.
- Do not `git add -A`.

## 5. Acceptance

1. In KBM mode, click a bound action's binding cell in the action browser,
   press a different key, and see the action browser row **and** the visual
   board both reflect the change immediately.
2. Export after a rebind produces a file where only the changed action(s)
   differ from the imported original — verify with a real diff against the
   source file, not by reading the export.
3. Export with **zero** rebinds still round-trips byte-identical, same as
   today — run `roundtrip.js` / `mutate.js` and confirm nothing regressed.
4. Rebinding to a key already used by another action in the same layer shows
   a warning naming the conflicting action before committing.
5. Sections in the action browser are collapsed by default and expand on
   click; a search or category filter auto-expands any section containing a
   match.
6. A first-time visitor can tell what the page does and how to rebind
   something without having read any external explanation.
7. `python testing/_src/build_deploy.py` and `check_deploy_clean.py` both pass
   clean.

## Commands

```
node testing/_src/roundtrip.js
```

```
node testing/_src/mutate.js
```

```
python testing/_src/build_deploy.py
```
