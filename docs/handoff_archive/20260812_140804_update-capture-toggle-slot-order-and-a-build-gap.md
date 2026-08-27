# Update — Capture no longer silences sticks, panel renders in slot order, search box fixed. And the build ships broken JS without complaining.

All four built. **Not deployed, nothing committed.**

## 1. The Capture toggle was silencing the sticks

Confirmed exactly as C1 read it. Button and hat events fired only behind
`typeof capture==="undefined"||capture`; **naming does not go through that flag**,
so with Capture OFF the panel listed both sticks by name and relayed nothing
from them. Sleven: *"it's recognizing the sticks. It's just not relaying the
actual information."*

Now decided in **one** function, `ccInputAllowed()`, so the two call sites cannot
drift: **a rebind always fires, toggle or not.** Outside a rebind the flag keeps
its exact meaning over the live readout, which is all it was ever for.

**The toggle now says what it governs:** *"Reading your keys: ON/OFF"*, with a
tooltip stating it only affects the live tester and that rebinding always works.
"Capture" left people to guess, and the guess cost them their sticks.

## 2. `#kbbq` — one line, and it was the reason anyone touched that toggle

The page-level key handler swallows keystrokes to drive the tester, so typing in
the action-browser search went to the keyboard board instead of the box. `#q` has
carried the same `stopPropagation` guard since it was written; this box never got
it. Added.

That closes the loop C1 named: the search was dead, the workaround was "turn
Capture off", and that silently disabled the sticks. **Two innocent bugs adding
up to "nothing works and I don't know why."**

## 3. Sticks now render in slot order

`buildDevice()` walked `pads()` directly — `navigator.getGamepads()` order, i.e.
plug order — so the labels were right and the **placement** was raw USB order.
Hence "the right stick on the left". Sorted by resolved slot immediately before
render. **Nothing about how identity is resolved changed** — profile GUIDs, then
remembered choice, then an admitted guess. Standard-mapping gamepads sort after
the sticks so a controller never displaces one.

**The swap affordance is visible now.** It existed — clicking a slot chip cycles
js1..js8 and remembers it per VID/PID — but the only hint was a `title`
attribute. There is now a real button on the chip: **"wrong stick? click to
swap"**, shown only when the slot was guessed or remembered, never when a
profile decided it.

## THE BUILD SHIPS BROKEN JAVASCRIPT WITHOUT COMPLAINING

Mid-task I put a real newline inside a JS string literal in `device_engine.js`.
`node --check` caught it — **but `build_deploy.py` had already run, injected it
into both hosts, printed `deploy guard: safe to deploy`, and exited 0.**

`inject_engine.py` copies the engine between markers and never parses it. So a
syntax error in `device_engine.js` reaches `_deploy` and the deploy guard has
nothing to say about it, because the guard checks **which files** are present,
not whether they work. A page whose entire device panel fails to parse looks
exactly like a successful build.

Repaired, and all four script blocks in the built page now parse — I checked by
extracting and running `node --check` on each. **Flagging the gap rather than
fixing it here**, since adding a syntax gate to the build is its own change and
this order did not ask for one. It is worth doing: today it caught me, and next
time nobody may be looking.

## State

`roundtrip.js` ALL CHECKS PASSED · `mutate.js` 19/20 M18 · rebind suite ALL
PASSED · guard clean. Everything verified present in **both** built hosts.

**What is NOT verified:** acceptance 1, 2 and 4 all require a real pair of
sticks. Capture-OFF rebinding, axis capture during a rebind, and left/right
placement are code-verified only. Headless cannot drive them — `rAF` does not
fire there — and I do not have the hardware.
