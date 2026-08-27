# PROMPT FOR CODE — the Capture toggle silently kills stick input, and the panel lays sticks out in USB order instead of slot order

    from    C1, 2026-08-12
    for     Code
    extends the two orders already filed today. Same job, do them together.
    basis   Sleven, on a real HOTAS pair: "it does recognize the controllers...
              It tells me their name in the box at the top. It still keeps
              getting stuck, the right stick on the left and the left stick on
              the right... even when the buttons aren't working, the axes
              aren't working, it will tell me which sticks are plugged in. So
              it's recognizing the sticks. It's just not relaying the actual
              information from them."
    scope   device_engine.js (injected-block rule applies) and
              keybinds.src.html for the toggle's copy.

---

## 1. The Capture toggle disables device input, and that is almost certainly what he's hitting

`device_engine.js` fires button and hat events only when the page-level
`capture` flag is on:

```
511   else if(typeof capture==="undefined"||capture){     <- buttons
529   if(dir && (typeof capture==="undefined"||capture))  <- hats
```

`capture` is the **Capture: ON/OFF** toggle (`keybinds.src.html:720` default
true, toggled at 971). Turn it off and the sticks go silent — the panel still
names them, because naming comes from `renderDevice()`, which doesn't check the
flag. **Exactly his symptom: it sees the sticks, it just relays nothing.**

**This is on me.** The top search box is dead while Capture is ON (the
still-unfixed `#kbbq` bug), and I told him to switch Capture off as the
workaround. I didn't know that also silences the sticks. So the two bugs
combine into "nothing works and I don't know why."

**Do:**

- **Rebind capture must never depend on this flag.** While
  `KBREBIND.listening()` is true, device input fires regardless of the toggle —
  same reasoning as the `dev`/`OPEN` gates already fixed in `0f0409c`. Nothing
  in the UI tells anyone the toggle affects rebinding, and it shouldn't.
- **Say what the toggle does.** Right now it's one word. It needs to state that
  it controls the live tester readout. If it keeps affecting the readout only,
  label it that way.
- **Fix `#kbbq` in the same pass** if the other order hasn't already — it's the
  reason anyone touches this toggle at all. It's one `stopPropagation` guard,
  matching what `#q` already has at line 944.

## 2. The sticks are laid out in USB order, not slot order

`buildDevice()` renders with a plain `list.forEach`, and `list` comes from
`pads()`, which is `navigator.getGamepads()` order — OS enumeration. So the
**labels** are right, because `slotSource()`/`padSlot` already resolve js1/js2
properly, but the **left-to-right placement** is raw plug order. Hence: correct
names, wrong sides.

**Fix: sort by resolved slot before rendering.** js1 leftmost, then js2, and so
on. The identity logic is already correct and is not what needs changing — only
the render order reads from the wrong thing.

**The manual override already exists and nobody can find it.** Clicking a slot
chip cycles js1..js8 and remembers it per VID/PID; the only hint is a `title`
attribute reading "guessed from plug order - click to set" — invisible unless
you happen to hover the right 20 pixels. Make it visible: a real affordance with
a label, near the chip. Sleven asked for "a way to swap it or something" — there
is one, it's just hidden.

Once §2 lands, cycling a slot should also **move** the panel, not just relabel
it. That's the whole point of the fix.

## 3. What NOT to do

- Don't make rebind capture depend on the Capture toggle.
- Don't change how js1/js2 identity is *resolved* — profile GUIDs, then
  remembered choice, then a guess that admits it. That order is correct.
- Don't reorder by anything other than resolved slot — not name, not plug order.
- Don't edit inside the injected block.

## 4. Acceptance

1. Capture OFF, start a rebind, press a stick button — it binds.
2. Capture OFF, move an axis during a rebind — it binds (per the axis order).
3. The toggle's label states what it actually governs.
4. Two sticks connected: the one resolved as js1 renders left, js2 right,
   regardless of plug order.
5. Cycling a slot moves the panel and the label together, and survives a reload.
6. The swap affordance is findable without hovering for a tooltip.
7. `#kbbq` search works with Capture ON.

## 5. Report back

Confirmation of 1, 2 and 4 with a real pair of sticks, and what the toggle's
label now says.
