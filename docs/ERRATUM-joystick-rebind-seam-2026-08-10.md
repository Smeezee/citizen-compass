# ERRATUM — my joystick order sent you into the injected block. Your recovery is right; here's the correction on the record.

    from    C1, 2026-08-10
    for     Code
    amends  docs/prompt-code-keybind-rebind-joystick-2026-08-10.md §1
    why     that document is the single writer of its own instructions, and it
              currently contains advice that cannot work. Amending it rather
              than leaving a wrong order in the repo for the next re-run.

---

## 1. The mistake was mine, and it's the second one in this same order

My §1 said: *"The cleanest seam is probably inside `fireDev` itself."*

**`fireDev` is inside the injected block.** `inject_engine.py` overwrites
everything between the `DEVICE PANEL rev 2` marker and
`if(dev!=="KBM") renderDevice(); });` from `device_engine.js` on every build, in
silence, in **both** hosts. So the edit I told you to make is deleted by the
next build, by design.

This is written down in `CURRENT-STATE.md` in as many words — *"Device-panel
work goes in `device_engine.js` or it is deleted"* — and I wrote a prompt that
walked straight into it anyway. That's twice on this one order: first the
keyboard-and-mouse-only scoping gap, now this. Both mine, neither yours.

You found it the right way, too — by noticing your own test passed on tokens
already present in the fixture and calling it vacuous rather than banking it.
That is the check-that-cannot-fail pattern this project keeps getting caught by,
caught by you this time before it cost anything.

## 2. The corrected instruction, which is what you already built

Verified against the working tree just now, not taken from your report:

- `device_engine.js` holds the hooks (lines 464, 492, 545) — correct, it is the
  single writer.
- Every hook is guarded `!!(window.KBREBIND && KBREBIND.listening())` — correct,
  and load-bearing: `_layer.src.html` is the **second** host and its overlay has
  no rebind UI, so the guard makes the injected copy a clean no-op there instead
  of a crash on the homepage.
- `window.KBREBIND` is published from `keybinds.src.html:1803`, **outside** the
  injected block — correct, so it survives every build.
- Both gates fixed (`poll()` and `startPoll()`), and entering the listening
  state calls `startPoll()` at line 1795 — correct, and it closes the case I was
  about to raise: `gamepadconnected` still returns early on the KBM tab, but it
  doesn't matter, because the loop is already running by then and `poll()`
  re-reads `navigator.getGamepads()` every frame.

**Confirmed in sync:** the exact `device_engine.js` text is present in both
`keybinds.src.html` and `_layer.src.html`.

So: nothing to redo. §1's "seam inside `fireDev`" should read **"the seam goes
in `device_engine.js`, called through a hook the page publishes from outside the
injected block."** That's the standing pattern for this class of change, and it
respects one-writer instead of fighting it.

## 3. One thing to verify with a real stick, which I have NOT proven

Not a finding — a named risk with a specific failure shape, so it gets tested
rather than assumed either way.

`poll()` ends with `rafId=requestAnimationFrame(poll)`, and it calls
`renderDevice()` unconditionally just before that. `renderDevice()` calls
`buildDevice(list)` whenever `!devDom`.

**During a rebind started from the Keyboard/Mouse tab, the device panel may not
be in the DOM at all.** If `buildDevice` throws on a missing container, the
exception lands *before* the re-arm line — so the loop dies silently after one
frame and the cell sits listening forever. **That is exactly the symptom Sleven
reported originally**, which is why it's worth ruling out rather than reasoning
about.

Cheap check: start a rebind from the KBM tab and confirm `poll()` is still
running several seconds later (a counter, a breakpoint, or just watching the
device readout update). If it does throw, the fix is a guard in `renderDevice`
or moving the `renderDevice()` call behind a panel-exists check — **not**
wrapping `poll()` in a try/catch, which would hide it.

Your harness can't settle this and neither can mine. It needs the stick.

## 4. Sequencing — you were right to run this first

You noted the master order hadn't reached you. Correct, and running the joystick
order first was the right call regardless: it's the one blocking Sleven's HOTAS
testing. `docs/prompt-code-MASTER-clear-the-queue-2026-08-10.md` is filed now and
carries his explicit go-ahead to commit, push **and** deploy. Treat the joystick
work as its item 1c already done, and pick up the rest — holo viewer, the
keybinds search/navkeys pair, the fonts, the collector shortcut ordering — then
push and deploy per its §5.
