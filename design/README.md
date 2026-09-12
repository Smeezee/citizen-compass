# design/

Working prototypes from the design desk. **Nothing in here is production.**
Nothing here is built, deployed, or imported by anything. It exists so the next
person picks up where the last one stopped instead of drawing it again.

    keybindings/keys.html    the keybinding board prototype

## keybindings/keys.html

Open it in a browser. No server, no build step, no dependencies — the bindings
are embedded in the file.

Two switcher rows sit above the board. **Readout** changes how a key shows what
is on it. **Key light** changes how bound keys glow at rest. **Hold to open**
sets how long a press has to be held before the detail opens.

Interaction, as settled with Sleven on 2026-09-07: tap a key and it lights with
a small tag naming what is on it; hold it and the detail opens. Escape, clicking
the key again, clicking off the board, or the panel's own close button all shut
it. Works the same whether you click the drawn key or press the real one.

Sleven picked **The key opens** as the readout to carry forward, because it is
the only one of the three with room for a rebinding menu later. The other two
are kept in the file so the comparison can be re-run rather than re-argued.

The full reasoning, including what was rejected and why, is in
`claude/DESIGN_tap-lights-the-key-hold-opens-it-2026-09-07.md`.

## Taking a picture of it

The design desk cannot see a rendered page. Every visual judgement it makes goes
through a screenshot. Playwright with the bundled Chromium does it:

    node screenshot.js

There is no `screenshot.js` yet — write one when you need it, and leave it here
so the next person does not build it a third time.
