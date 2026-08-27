# PROMPT FOR CODE — the browser is exonerated. Stop guessing at the detection bug and instrument it.

    from    C1, 2026-08-12
    for     Code
    basis   Sleven ran `/stick-test` on his friend's machine with the real VKB
              pair: "it worked perfectly. Everything, every button worked. It
              worked just like it's supposed to."
    scope   keybinds.src.html + device_engine.js (injected-block rule applies).

---

## 1. What that result settles

`/stick-test` uses **none** of our detection code. It calls
`navigator.getGamepads()` on a bare `requestAnimationFrame` loop and nothing
else. It reported both sticks, every button, every axis, correctly.

So, on that exact machine, in that exact browser, with that exact hardware:

- The browser exposes the sticks fine.
- `navigator.getGamepads()` returns them.
- No permission, focus, driver, HID-mode or browser-support problem exists.

**The fault is in our page.** That is now established rather than suspected, and
it is a big narrowing — three rounds of fixes have been shipped against
possibilities that are now all eliminated.

## 2. Three causes I checked in the source and ruled OUT — don't re-derive these

I read each one specifically. All three were wrong:

1. **Not the tab `ok` flags.** `DEVS` (line 676) has `ok:1` on all three
   including `JOY`, so the `if(!DEVS.find(...).ok) return;` guard in the tab
   click handler is not blocking the switch.
2. **Not a missing render on tab switch.** The handler at line 742 calls
   `drawModes(); render();` and `render()` opens with
   `if(dev!=="KBM"){renderDevice();return;}`, plus `startPoll()` right after. That
   path looks correct.
3. **Not a stale cache in the presence check.** `ccDeviceNames()` re-reads
   `navigator.getGamepads()` on every 400 ms tick and caches only a signature
   string for comparison, never the device list.

**I have no fourth hypothesis, and I am not going to invent one.** Three
speculative fixes have already shipped on this and the symptom is unchanged.

## 3. What to build: make the page state what it can see

Not a debug mode, not a console log — **a visible line on the page**, permanent,
in plain language, because it also satisfies the "a person must never have to
guess whether the site can see their hardware" requirement already ordered.

It should report, live:

- how many devices `navigator.getGamepads()` returns **right now**, and their
  names
- which device-mode tab is selected
- whether the sampling loop is actually running
- when the presence check last saw a change

Phrase the first two for a normal person; the last two can be terser. **A
screenshot of that line, taken on the friend's machine, is the whole diagnosis**
— that's the point, since neither of us can reach that hardware.

**Then use it yourself.** Open `/keybinds` with any gamepad on your own machine
and compare its readout against `/stick-test` on the same machine. If they
disagree, the difference between the two pages is the bug, and `/stick-test`
is deliberately simple enough to diff against — that comparison is the reason
it was built independent.

## 4. Sleven's layout note, worth doing while you're in there

> "I wish I could have seen them side by side instead of having to scroll."

That's about `/stick-test` with two sticks — they stack vertically, so comparing
them means scrolling. Two devices should sit side by side on a wide screen and
fall back to stacked on a narrow one.

**The same complaint applies to `/keybinds`** — the stick-order fix already
ordered puts js1 left and js2 right, which only helps if both are visible at
once. Check that they are.

## 5. What NOT to do

- **Do not ship another speculative detection fix.** Instrument, get the
  readout from the real hardware, then fix what it actually shows.
- Don't make `/stick-test` depend on any site code — its independence is what
  made this finding possible.
- Don't edit inside the injected block.

## 6. Acceptance

1. `/keybinds` shows a live, plain-language line stating what it can see.
2. It updates without a reload when a device appears or disappears.
3. It's visible on every device-mode tab, including Keyboard/Mouse.
4. With a gamepad on your machine, `/keybinds` and `/stick-test` agree on the
   device count and names — or you report exactly where they diverge.
5. `/stick-test` shows two devices side by side on a wide window.
6. Build and deploy guard pass clean.

## 7. Report back

The comparison from item 4 — what each page reported on the same machine with
the same device. If they agree, say so plainly; that means the failure is
specific to his hardware or browser and the readout from his friend's machine
becomes the next step rather than anything you can fix blind.
