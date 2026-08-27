# PROMPT FOR CODE — two live `/keybinds` bugs, both independently confirmed twice

    from    C1, 2026-08-10
    for     Code
    basis   Found once by C1 running the CIC ordinary-person test pass, then
              independently reproduced by Sleven himself doing the identical
              cold test by hand a few minutes later, on the live deployed
              page — not a one-off fluke, not a testing artifact.
    scope   testing/_src/keybinds.src.html only. Build only, do not deploy —
              separate go-ahead covers pushing this live, same as every order.

---

## Bug 1 — the top tester-panel search box is dead while Capture is ON (which is the default state)

**Confirmed twice, same symptom both times:** typing into the "Search this
mode..." box at the top of the page does nothing to the box itself, and
instead the keystrokes get swallowed one at a time by the page's key-listener
and show up in the "what you pressed" test panel below (e.g. typing
"afterburner" registered "A," "F," "T," "E," ... as individual test
keypresses). Turning the Capture toggle off and retyping the same text works
instantly.

**Root cause already found by reading the source, not guessed:** the visual
board's own search field, `#q`, has a guard —

```js
$('q').onkeydown = e => e.stopPropagation();
```

— that stops the page's capture-phase `keydown` listener from seeing
keystrokes typed into it. **The top tester-panel search box, `#kbbq`, has no
equivalent guard.** Add the same `stopPropagation()` treatment to `#kbbq`
that `#q` already has.

**Note the scope carefully — there is a second search box that already
works.** The lower search box under "Every action the game defines" (the
691-action browser list) filters correctly even with Capture on — it's
specifically `#kbbq`, the top tester-panel one, that's broken. Don't touch
the working one.

## Bug 2 — the End key gets eaten as a keybind test instead of scrolling the page

**Confirmed twice:** pressing End while Capture is on, expecting the
browser's normal "jump to bottom of a long page" behavior, instead gets
captured and logged as a keybind test press ("End · Flight · no modifier ·
TAP" / "End — nothing bound on this layer") and the page does not move at
all. On a page this long, that's the one native browser shortcut that would
have helped, and it's disabled by the same listener as Bug 1.

**This is about the Capture-ON tester listener specifically — the general
"show me what this key produces" panel — not the deliberate rebind-capture
state that fires after clicking a binding cell to change it.** Those are two
different listeners on this page; don't conflate them. A real rebind
legitimately needs to accept any key, including End, since Star Citizen can
bind almost anything. The tester/demo panel does not have that requirement —
it exists to show someone what token a control produces, not to commit a
binding — so it's reasonable for it to leave standard browser navigation
keys alone.

**Read the actual Capture-ON listener before fixing this one** — it isn't
fully described in this prompt because I haven't re-read that exact code
path since it was built. Find where the global capture-phase `keydown`
listener decides what to intercept, and exclude the standard browser
navigation keys (`Home`, `End`, `PageUp`, `PageDown`, and probably `Tab`)
from `preventDefault()`/interception **only in that tester-panel path** —
still capture and display them as normal if that's cheap to do without
blocking the browser's own handling, but don't call `preventDefault()` on
them there. Do not change what the deliberate rebind-capture ("listening")
state accepts — that one should keep taking any key, including
Home/End/PageUp/PageDown, since a real SC profile might use them.

## What NOT to do

- Don't touch the working lower search box (the 691-action browser filter).
- Don't change what keys the deliberate rebind "listening" state accepts —
  only the general Capture-ON tester/demo listener.
- Don't touch `sc_export.js`, `roundtrip.js`, `mutate.js`.
- Don't deploy. Build only.
- Don't `git add -A`.

## Acceptance

1. With Capture on, type into the top tester-panel search box and see it
   filter/respond normally — no keystrokes leak into the "what you pressed"
   test panel.
2. With Capture on, pressing End scrolls the page normally, the way it does
   on any other web page. Same for Home, PageUp, PageDown.
3. The lower 691-action-browser search box is unaffected — still works
   exactly as it does today.
4. The deliberate rebind "listening" state (click a binding cell → press a
   key to rebind it) still accepts every key it did before, Home/End/etc.
   included, if that flow already exists on this branch.
5. `python testing/_src/build_deploy.py` and `check_deploy_clean.py` both
   pass clean.

## Commands

```
python testing/_src/build_deploy.py
```
