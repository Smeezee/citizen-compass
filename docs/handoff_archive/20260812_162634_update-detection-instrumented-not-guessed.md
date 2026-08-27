# Update — instrumented, not guessed. And the readout is built to isolate detection from rendering.

Built. **Not deployed** — the order's acceptance is build-only and no go-ahead
covers a deploy. One word and it goes.

## Item 4 cannot be done here, and I am not going to pretend otherwise

There is **no gamepad on this machine**. Windows lists only virtual emulation
*buses* — Nefarius/ViGEm, Logitech G HUB, Oculus — which are drivers that would
let software create a virtual pad, not devices. Nothing for
`navigator.getGamepads()` to return.

So the `/keybinds` vs `/stick-test` comparison the order asks for needs hardware
I do not have. Reporting that rather than producing a comparison of two empty
lists and calling it agreement.

## What I built instead makes that comparison unnecessary

**The new readout calls `navigator.getGamepads()` directly, ungated — the same
bare call `/stick-test` uses.** It does not go through `pads()`, `poll()`,
`renderDevice()`, the tab gate, the panel gate or the capture flag. That is
deliberate, and it splits the remaining possibilities in two:

- **line says 0 while `/stick-test` says 2** — then two pages in the same
  browser get different answers from the same API, which would be extraordinary
  and would point somewhere none of us has looked.
- **line says 2 while the panel shows nothing** — then detection is fine and
  **the bug is in rendering or gating**, which is a much smaller haystack and
  one we can read.

A screenshot of that line from the friend's machine answers which, and that was
the point.

## What it reports

Plain language first: *"2 controllers detected: VKB Gladiator NXT EVO L (29
buttons, 8 axes, standard)"*, or the press-a-button guidance when there are
none. Then a terser mechanics line: **tab · panel open/closed · reading keys
on/off · sampling loop running (N frames) · last change HH:MM:SS**. Visible on
every tab including Keyboard/Mouse, and repainted on a 1s timer as well as on
the device event, because the counters move without any device changing and a
stale diagnostic is worse than none.

**The frame count is a real liveness signal, and that matters.** It is
incremented inside `poll()` itself, not read from `rafId` — I checked earlier
and `rafId` is not liveness: it sat unchanged at 2 for three seconds while
`poll()` had run **zero** times, which reads identically to a healthy loop. A
number that climbs is proof; a handle is not.

## Sleven's layout note

`/stick-test` now lays devices out in a grid: side by side from 900px, stacked
below that. Comparing a HOTAS pair is the entire job of that page and stacking
them made it a scroll.

On `/keybinds`, the panel already uses `.dvcols.pair` — a `repeat(auto-fit,
minmax(330px,1fr))` grid — so two sticks sit side by side there already, and the
slot-order fix means js1 is the left one.

## Not done, deliberately

**No fourth speculative detection fix.** C1 ruled out three causes in the source
and said there was no fourth hypothesis worth inventing; three have already
shipped against this symptom. Instrument, read the real readout, then fix what
it shows.

`/stick-test` still shares no code with the site — that independence is what
produced this finding and it stays.

## State

Build and deploy guard clean. Every inline script in every built page parses
(my own gate, since the injector's new one only covers the engine).
`roundtrip.js` ALL CHECKS PASSED, `mutate.js` 19/20 M18.
