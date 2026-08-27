# FINDING — the device reader stops itself and has exactly one way back on, and that way needs a gamepad to be newly connected. This is why Sleven's stick works sometimes and not others, and it is very likely the "stuck device tab" bug from two days ago.

    from      C3 (Cowork), 2026-08-10
    for       C1 -> Code
    reported  Sleven, testing the live keybind page: "sometimes they work,
              sometimes they don't... it's recognising them, but nothing's
              coming up." The stick's own software shows axes and buttons
              working at the same moment the page shows nothing.
    file      testing/_src/device_engine.js
    likely    the same root cause as claude/FINDING_device-panel-two-bugs-2026-08-09.md
              BUG 2, which did not reproduce headless

---

## 1. The defect, in three lines of the file

**The poll kills itself** — line 392, first statement in `poll()`:

    if(dev==="KBM"||(typeof OPEN!=="undefined"&&!OPEN)){ rafId=null; return; }

So the loop stops whenever the device tab is Keyboard/Mouse **or** the panel is
not open. That part is deliberate and sensible: do not burn a frame callback on a
panel nobody is looking at.

**Restarting is guarded** — line 439:

    function startPoll(){ if(rafId===null&&dev!=="KBM") rafId=requestAnimationFrame(poll); }

**And `startPoll()` is called from exactly one place in the entire file** — line
441:

    window.addEventListener('gamepadconnected',function(){
      if(dev!=="KBM"){ devDom=null; renderDevice(); startPoll(); } });

I grepped for every call site. There is one.

## 2. What that means in use

Once the poll has stopped, **the only thing that starts it again is a
`gamepadconnected` event.** Nothing else calls `startPoll()`:

- switching the device tab back from Keyboard/Mouse to a stick — **does not**
- opening the panel again, i.e. `OPEN` going true — **does not**
- bringing the browser window back to the front — **does not**
- `gamepaddisconnected` — calls `renderDevice()` but **not** `startPoll()`

And `gamepadconnected` only fires when a gamepad is **newly** connected, and in
Chrome only after a button is pressed while the page has focus. **A stick that was
already plugged in when the page loaded may never fire it again.**

So the sequence that kills it is ordinary use: open the page, look at the stick,
click over to Keyboard/Mouse or close the panel — poll stops — click back to the
stick, and there is nothing running. The panel still lists the device, because
`renderDevice()` runs on its own; it just never updates. **That is exactly
Sleven's description: "it's recognising them, but nothing's coming up."**

The recovery he found by accident — "I'll go show it and something will pop up" —
is consistent with something eventually producing a connect event, most likely a
button press waking the API on a device the browser had not yet enumerated.

## 3. This is probably BUG 2 from 2026-08-09, finally explained

`FINDING_device-panel-two-bugs-2026-08-09.md` reported tabs stuck on
Keyboard/Mouse and I could not reproduce it headless. I recorded the theory as
"something in Sleven's actual browser that headless does not have" and refused to
write a fix on it.

**The reason it did not reproduce is now clear, and it was not the device data.**
In that harness I drove the tabs with `dev` changing and the panel open, so the
poll never entered the state it cannot leave. The bug needs the poll to STOP —
Keyboard/Mouse selected, or the panel closed — and then a real stick that is
already connected, so no `gamepadconnected` ever fires to restart it. My harness
injected fresh gamepads, which fires the event, which restarts the poll, which
hides the defect.

**I am not calling it the same bug, because the earlier report was about tabs not
switching and this is about the reader not running.** They may be one thing or
two. But they share the state, and this one is proven from the code rather than
theorised, so it should be fixed first and the tab report re-tested afterwards.

## 4. The fix

`startPoll()` is correct. The problem is that almost nothing calls it. It needs to
be called from every place the conditions can become true again:

- the device tab handler, whenever `dev` changes to anything other than `KBM`
- wherever `OPEN` is set true
- `visibilitychange` when the document becomes visible, and `window.onfocus` —
  `requestAnimationFrame` does not run in a background tab, so returning to the
  page should re-arm rather than hope
- `gamepaddisconnected` — a second stick may still be live

`startPoll()` already guards on `rafId===null`, so calling it more often is safe
and cannot start two loops. **This is a call-site problem, not a logic problem.**

Worth considering as well: `poll()` deciding its own lifetime is what makes this
fragile. Something that stops itself and cannot be started by the events that
change its own conditions will keep finding new ways to be dead. Whoever fixes it
may prefer to have the state changes drive the loop rather than the loop inspect
the state.

## 5. Do NOT close the earlier finding on this

The outstanding request for an F12 console reading still stands and is still
worth having. If the console is clean when the panel is dead, that supports this
diagnosis. If there is a red error, there is a second thing wrong and this fix
would have masked it.

## 6. What I checked and what I did not

**Checked:** every `rafId` assignment in `device_engine.js` (lines 41, 392, 437,
439) and every call site of `startPoll()` (one, line 441); the guard conditions on
both `poll()` and `startPoll()`; the two gamepad event listeners and what each
does.

**Did NOT check:**
- **I have not reproduced it.** This is read from the deployed source and it
  matches the reported symptom closely, but nobody has watched the poll stop and
  fail to restart on a real machine.
- Whether `OPEN` is toggled anywhere that would also need the call — I do not have
  the file that owns `OPEN`; the `typeof OPEN!=="undefined"` guard says it lives
  outside `device_engine.js`.
- Whether this also explains the tab-switching half of the earlier report. §3 says
  why I am not claiming that.
