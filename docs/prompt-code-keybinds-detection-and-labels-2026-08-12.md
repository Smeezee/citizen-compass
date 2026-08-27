# PROMPT FOR CODE — addendum: device detection is gated three ways, and the page never tells anyone the one thing Chrome requires

    from    C1, 2026-08-12
    for     Code
    extends `docs/prompt-code-keybinds-axes-and-no-import-2026-08-12.md`
              — same job, do them together. That order stands unchanged.
    basis   Sleven: "I've had troubles getting the joysticks to even register
              in the website. It usually takes a couple refreshes... if I open
              up the flight controls, and then I realize I don't have my
              software for my flight sticks, I have to go open them. It
              doesn't pick anything up. I have to shut the web page down and
              back up... once the software registers and recognizes
              everything, our website should also recognize everything."
    scope   device_engine.js for the detection loop; keybinds.src.html for
              copy. Injected-block rule applies, same as before.

---

## 1. Why it takes a refresh — three gates, all of which must be open

`pads()` itself is fine; it re-reads `navigator.getGamepads()` every call. The
problem is that nothing *calls* it unless all three of these hold:

1. **`poll()` early-returns** on `(dev==="KBM" && !rebinding)` — the
   Keyboard/Mouse tab is the default, so on first load nothing is polling.
2. **`poll()` also early-returns** on `(typeof OPEN!=="undefined" && !OPEN && !rebinding)`
   — if the device panel is closed, the loop stops dead.
3. **`gamepadconnected` is itself gated** `if(dev!=="KBM")` (line 578), so the
   one event that would recover the situation is ignored on the default tab.

So: land on the page, start your stick software afterwards, and the connect
event fires into a handler that discards it, while no loop is running to notice
on its own. **A reload is currently the only reliable recovery, which is exactly
what Sleven reported.**

## 2. Chrome will not report a stick until a button is pressed on it — and we never say so

This is a browser rule, not our bug: `navigator.getGamepads()` returns nothing
for a device until the user presses a control on it while the page has focus.
So a correctly-connected, correctly-driver'd stick reads as absent until it's
touched.

**The page shows an empty panel and no explanation.** That single missing
sentence probably accounts for most of the frustration here — the user thinks
the site is broken when the site is waiting for them.

**Fix the copy as well as the code:** when no device is detected, say plainly
what to do — press any button on the stick, and if nothing appears, check the
stick's own software is running. Keep it short and non-technical. This must be
visible on the device panel *and* wherever a rebind is waiting on an input that
can't arrive.

## 3. What to build

**A presence check that does not depend on tab or panel state.** Something
cheap and low-frequency — a few hundred ms, `setInterval`, not `rAF` — whose only
job is to ask whether the set of connected devices has changed. On a change:
drop `devDom`, re-render, update the copy in §2, and start the real poll loop if
whatever is on screen needs it.

Keep it genuinely cheap. The reason the heavy loop is gated is real — this is a
presence check, not a second input loop, and it must not become one.

**Ungate the connect/disconnect handlers.** `gamepadconnected` and
`gamepaddisconnected` should always update state and the "what's connected"
copy. Whether to start the *input* loop can still depend on what's on screen;
whether to *notice a device exists* must not.

**State it out loud.** Somewhere always visible: how many devices are seen and
their names, or the "press a button on your stick" prompt. A person must never
have to guess whether the site can see their hardware — that ambiguity is the
whole complaint.

## 4. Be prescriptive — Sleven's second ask

> "we are being as prescriptive as we can to help people know exactly what
> buttons do"

Applies to this order in two concrete places, not as a general aspiration:

- **While a rebind is listening**, say exactly what it will accept right now —
  press a button, move an axis, press a hat direction. Not a generic "waiting
  for input". If gamepad `xi_` is still refused, say that there rather than at
  the moment of failure.
- **When an input is captured**, show what it was in the person's language *and*
  the token being written — "Y axis" and `js1_y` — so what lands in the file is
  never a surprise. This carries the UNATTESTED flagging the main order already
  requires.

The 238 plain-language action descriptions already shipped are the model for
tone. Don't write new ones here; match them.

## 5. What NOT to do

- Don't turn the presence check into a second full input loop.
- Don't remove the `OPEN` / `dev` gating from the **heavy** poll loop — the lag
  it was added to fix was real. Gate the input sampling; don't gate knowing a
  device exists.
- Don't claim a stick is connected on the strength of a stale cache — always ask
  `navigator.getGamepads()` fresh.
- Don't edit inside the injected block.

## 6. Acceptance

1. Load `/keybinds`, **then** start the stick's software, press a button on the
   stick — it appears, with **no page reload**, on whatever tab is showing.
2. Same, starting on the Keyboard/Mouse tab specifically.
3. Same, with the device panel closed at the moment the stick connects.
4. Unplug mid-session: the page notices and says so.
5. With no device present, the page states what to do about it.
6. A listening rebind cell states exactly which input kinds it will accept.
7. A captured input shows both plain-language name and token.
8. No measurable lag regression on the live readout — the reason the loop was
   gated in the first place.

## 7. Report back

The presence-check interval and why; measured cost with a stick connected and
with none; and confirmation of the reload-free path for each of cases 1–3 with a
real device.
