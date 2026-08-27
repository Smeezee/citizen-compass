# Update — received the device-detection addendum; doing it with the axes order

From C1, 2026-08-12, extending
`docs/prompt-code-keybinds-axes-and-no-import-2026-08-12.md`.

## Where the main order already stands

- **§1 axis capture — built.** `patch_axis_rebind_capture.py`. Fire at 0.55 of
  deflection, re-arm below 0.25, only while a rebind is listening.
- **§3 no import — built and verified.** Five stick controls bound with nothing
  uploaded, exported to a 1,074-byte file containing **only the 5 deliberate
  bindings**, both sticks declared. `roundtrip.js` and `mutate.js` unaffected.
- **§2 UNATTESTED labelling — not yet.** Doing it with the addendum's §4, since
  both are about what the capture moment says.

## The addendum's §1 is a real three-way gate and its reading is correct

Confirmed: `poll()` early-returns on the KBM tab, early-returns when the panel
is closed, and `gamepadconnected` is itself gated `if(dev!=="KBM")` — so the one
event that could recover the situation is discarded on the default tab. A reload
really is the only current recovery.

**§2 is the part I would not have found.** Chrome reports no gamepad until a
control is pressed on it while the page has focus. A correctly-installed stick
reads as absent until touched, and the page says nothing — so the site looks
broken while it is actually waiting for the person. That is a copy fix worth
more than the code fix.

Building both, then reporting together.
