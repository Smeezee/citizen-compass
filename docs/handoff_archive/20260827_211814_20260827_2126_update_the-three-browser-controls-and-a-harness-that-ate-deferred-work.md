# Update — The last three of the six are green, and one of them was the harness lying to every control that uses it.

**2026-08-27 21:26 local · Code (background session)** — the browser half of
*"run the remaining six"*.

## `_verify_dim.mjs` — 42/1 -> 43/43, exit 0

    FAILED: and neither side declares a token the other does not  css 58 vs engine 56

Named the two, rather than accepting a count:

    in CSS, NOT in palette():  ['bracket', 'panelglass']
    in palette(), NOT in CSS:  []

**A token the theme engine does not know about is never re-emitted, so it keeps
its Day value at every preset.** `--panelglass` is the stage panel's ground and
`--bracket` is its corner brackets - **the two things sitting directly over the
render, which is the exact place the dim exists for.** They stayed at full
brightness in Blackout.

Both are the SCRIMS shape and were simply never registered when they were added.
Their literals gave the base and the alpha, read rather than chosen:

    --bracket     rgba( 34,211,238,0.30)  = accent2 (#22D3EE) at 0.30
    --panelglass  rgba( 14, 27, 46,0.80)  = panel   (#0E1B2E) at 0.80

The CSS literals also carried a trailing zero the engine does not emit
(`0.30` vs `0.3`), so the value assertion caught them a second time. Written to
match.

**The control still fails on demand:** `--mutate-nofloor` exits 1 with the body
text sitting ON the floor at Blackout.

## `_verify_ship_page.mjs` — 241/1 -> 242/242, exit 0

    FAILED: there is exactly ONE place in the page that selects a port
            3 assignments to sel={...}

**The control was right and the page was wrong.** Three sites built the
selection object: `selectPort()`, `undoSwap()` and the ledger's revert handler.
Its stated reason holds - *"the marker and the list open the IDENTICAL window"*
is only true BY CONSTRUCTION while one place decides what a selection is.

And the two extras built it **without the `fixed` key**, so a port selected by
undo or revert carried a different shape from the same port selected by a click.
Both are guarded to swappable ports today, which is why nothing had gone
visibly wrong yet.

Added `setSel(slot)` as the one place the object is built. `selectPort` still
owns what opens and the `editing` decision; undo and revert now get the flag
**without gaining a render they did not ask for** - both their callers already
render. The behavioural counts are unchanged: still *"2 geometry loads across
two ships, three showModel() calls and three tab switches"*.

## `_verify_stage_panel.mjs` — 51/1 -> 54/54, exit 0. And this is the one worth reading

    FAILED: and it closes the panel

The page was not broken. **`checks/_loadout_harness.mjs` had
`setTimeout: () => 0`.** Every callback the page deferred was thrown away, and
nothing said so.

P1e clears the selection during the click and calls `setTimeout(renderAll, 0)`
deliberately - rendering inline would rebuild the DOM underneath the branches
that have not run yet. So in this harness the panel never closed, and the
control has been reporting a page defect that does not exist **for as long as
P1e has existed**.

**Twenty controls import that harness.** Any behaviour the page defers was
invisible to all of them - and the dangerous direction is not this one, it is an
assertion that some deferred cleanup did NOT happen passing because it never
could have.

Deferred callbacks are now QUEUED and `flushTimers()` runs them. **Not
auto-flushed**: running them inline would change the ordering every existing
control was written against, and a control that wants a deferred effect should
have to say so.

The assertion was also split, so it says which half failed:

    the click clears the selection during the event, before any render   (synchronous)
    and it DEFERRED a render rather than doing nothing   1 deferred callback(s) ran
    and it closes the panel

**A flush that runs nothing is now a failure**, so this cannot go green on a
page that has stopped deferring anything.

## Re-running all 20 harness users before I call this done

The harness change is designed to be inert unless `flushTimers()` is called, but
"designed to be" is not "measured to be". Result in the next note, then a build
and deploy - `loadout.src.html` changed, so the page has to reach testing.

Nothing committed, nothing pushed, live site untouched.
