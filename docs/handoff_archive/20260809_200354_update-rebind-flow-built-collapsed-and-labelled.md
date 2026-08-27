# Update — rebind flow built, page collapsed, page explained. One file changed.

All seven acceptance points met and verified in a real browser, not by reading
the code. `testing/_src/keybinds.src.html` is the only file touched.

## C1's central claim was right, and I checked it before building on it

There was no rebind capability anywhere. Confirmed independently: the export path
read `binds = imported.binds` with nothing anywhere constructing a modified
array, and the browser rows carried no click handler at all. This was a missing
feature, not a discoverability problem.

## The thing that shaped the whole design, found before writing any UI

`KB_ACTIONS` (what the browser shows) and an imported profile are **two
different data sets that partly overlap**. Measured against the real fixture:

```
691  labelled actions in the browser
247  bindings in the profile
216  profile bindings that match a browser row
 31  profile bindings with NO row - actions with no label, so pass 2 never showed them
```

**Those 31 are why `KBEDIT` exists.** If export wrote only what the browser knew
about, 31 of somebody's real bindings would vanish without a word. So the working
copy is a full copy of everything imported, the browser is a *view* over part of
it, and anything the view cannot show passes through untouched. Verified: 247
bindings in, 247 out, after a rebind.

Second finding, same shape: **the fixture profile has zero keyboard bindings** —
it is joystick-only, 191 of its 247 entries being explicit unbinds. So a KBM
rebind against it is an *insert*, not an edit, and the tests exercise that path.

## What was built

**The rebind flow.** Click a binding cell → a listening state that says *"press a
key or mouse button · Esc to cancel"* → the key is captured and written to the
working copy. `×` clears a binding. The export writes the working copy.

**Key names are not invented.** `SC_KEY_FROM_CODE` maps `KeyboardEvent.code` to
the game's own vocabulary, read out of `keybinds_site.json` — `escape` not `esc`,
`lshift` not `shiftleft`, `np_0` not `numpad0`, `lbracket`, `equals`, `mwheel_up`.
**A key the map does not cover returns null and the rebind is refused with a
reason** rather than a guessed token being written into somebody's profile.
`sc_export.js`'s `reject()` is still the final gate after that, so modifier
combinations and `ms1_` are refused exactly as before.

**Conflicts are flagged, not resolved.** Rebinding onto an input already used in
the same actionmap shows *"kb1_j is already **<other action>**"* with **use it
anyway** / **cancel**. Neither auto-resolved nor hard-blocked.

**The board agrees with the list.** This needed more than redrawing: the board
renders `kb_modes.gen.js`, which is the game's *defaults*, so a redraw would have
kept confidently showing the old key. `kbOverlay` lifts each changed action off
its old cap and puts it on the new one, without ever mutating the generated data
— a baseline you edit is not a baseline.

**Sections collapse.** Closed by default, click to open, expand/collapse all.
Searching or filtering **auto-expands every matching section**, because a hidden
match would be worse than the flat list it replaced.

**The page says what it is.** A short block at the top: what this page does, that
it never touches the game, and the four steps — import, find, click the binding,
export — plus where the profile lives in the game's menus. The keyboard is
labelled explicitly as *a tester, not an editor*, since that is what it is.

## Acceptance — measured

| # | | evidence |
|---|---|---|
| 1 | rebind updates **both** views | driven in headless Chrome: "Emergency Exit Seat" default `U` → rebound `kb1_j` → **list row shows `kb1_j`, board moved `["U"]`→`["J"]`**, counter reads "1 action changed - export to save", clear returns it to `U` |
| 2 | export differs only in the changed action | real line diff vs the source file: **exactly 1 line differs**, `<rebind input="js1_button17"/>` → `<rebind input="kb1_j"/>` |
| 3 | zero rebinds still byte-identical | `roundtrip.js` **ALL CHECKS PASSED**, `mutate.js` **19/20, M18** — no regression |
| 4 | conflict names the other action | asserted: rebinding onto a used input returns that action's name |
| 5 | collapsed by default, filter auto-expands | browser-driven: default **35 headers / 0 rows**; search "eject" → **2 rows, 0 sections left closed**; category CAMERA → **31 rows, 0 closed**; expand all → **691**; collapse → **0** |
| 6 | obvious to a first-time visitor | intro block renders; judgement, not something I can measure |
| 7 | build + guard clean | both pass |

## A test of mine that was wrong, not the code

My first §5.2 assertion demanded the action's name appear in the changed lines.
It failed — because the `<rebind>` element carries the *input* and the action
name sits on the parent `<action>` element, a different line. The code was right
and the check was looking in the wrong place. Corrected to assert what actually
matters: exactly one line moves, it is a `<rebind>`, and it goes from the old
input to the new. Recording it because a red result from a bad assertion costs
the same as a real one.

## Scope

`keybinds.src.html` only. `sc_export.js`, `roundtrip.js`, `mutate.js`,
`holo.src.html`, fonts and `MANUAL_MATCHES` all untouched. **Not deployed** —
build only, as ordered. Nothing staged, nothing committed.

The two `_modelfolders.txt` / `_scunpacked_names.json` scratch files are still
untracked and still left alone.
