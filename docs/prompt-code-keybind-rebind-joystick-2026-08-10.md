# PROMPT FOR CODE — the rebind flow doesn't capture joystick/HOTAS or gamepad input, only keyboard and mouse

    from    C1, 2026-08-10
    for     Code
    basis   Sleven, hands-on at his friend's machine with a real HOTAS:
              "I uploaded a file from Star Citizen... but I'm still not able
              to actually program the buttons. It says press a key or mouse
              button. But when I actually click it with the flight sticks,
              it's not doing what it's supposed to do."
    on me   This is a gap in my own original rebind order
              (`prompt-code-keybind-rebind-and-layout-2026-08-10.md`), not a
              miss on your end — I scoped §1's capture step as "the next
              keydown or mousedown" and didn't say anything about joystick or
              gamepad input, even though the action browser lists bindings
              across all four input types in one list. You built exactly what
              I asked for, including the "press a key or mouse button" prompt
              text — it's just missing a third of what it needs to do.
    scope   testing/_src/keybinds.src.html only. Build only, do not deploy —
              same go-ahead discipline as everything else.

> ## ⚠ CORRECTED 2026-08-12 — READ BEFORE §1
>
> **§1 below says the seam is "probably inside `fireDev` itself." That is
> WRONG and will silently revert on the next build.** `fireDev`, `poll()` and
> `startPoll()` all live inside the injected block that `inject_engine.py`
> overwrites from `device_engine.js` on every build, in both hosts.
>
> **Correct instruction: the seam goes in `device_engine.js`, called through a
> hook the page publishes from OUTSIDE the injected block** (`window.KBREBIND`,
> published from `keybinds.src.html`), and every call site must be guarded
> `!!(window.KBREBIND && KBREBIND.listening())` because `_layer.src.html` is a
> second host whose overlay has no rebind UI.
>
> This was built and shipped that way in commit `0f0409c`. Full account,
> including one unresolved liveness risk:
> `docs/ERRATUM-joystick-rebind-seam-2026-08-10.md`.
>
> Leaving §1's original text below rather than rewriting it, so the mistake
> stays visible instead of quietly disappearing.

---

## 0. What's confirmed by reading the shipped code, not guessed

The rebind flow's capture step is exactly two listeners:

```js
document.addEventListener('keydown', function(e){ ... commit(..., 'kb1_'+tok); }, true);
document.addEventListener('mousedown', function(e){ ... commit(..., 'kb1_'+n); }, true);
```

Nothing listens for a gamepad or joystick button while `listening` is
truthy. Meanwhile the page already has a complete, working joystick/HOTAS
read path for the live device panel — `poll()` → `fireDev(p, label, sc,
press)` — which already produces the exact SC-vocabulary token
(`js1_button3`, `xi_a`, `js2_hat1_up`, etc.) as its `sc` argument. That's the
piece to reuse, not rebuild.

**One thing that will bite you if missed:** `poll()` opens with
`if(dev==="KBM"||...) return` — the gamepad polling loop is currently only
running while the device-mode tab is set to Gamepad or Joystick/HOTAS. A
rebind needs to work regardless of which tab happens to be selected, since
the action browser shows keyboard, mouse, joystick and gamepad bindings
together in one list — nothing in the UI tells someone to switch tabs before
rebinding a stick input, and requiring it would be a confusing, undocumented
precondition. Make sure input capture during a rebind isn't gated on `dev`.

## 1. The fix

> **Superseded on the seam location — see the correction block at the top of
> this document. The reasoning below is right; the file to edit is not.**

While `listening` is set, capture joystick/gamepad input the same way
keydown/mousedown already do, and feed it through the same `commit(map,
action, sc)` path — reuse `fireDev`'s existing SC-token production rather
than writing a second version of that mapping. The cleanest seam is probably
inside `fireDev` itself: when `listening` is truthy, call `commit` with its
`sc` value instead of (or in addition to) the normal live-display update, the
same way the keydown handler special-cases on `listening` before doing
anything else.

Two things already built elsewhere on this page that the fix needs to
respect, not reintroduce:

- **Hats.** A hat's SC token already comes out right from the existing
  polling code (`js1_hat1_up`, etc.) — just make sure a rebind captures that
  full token, not a synthetic guess.
- **One control, two identities.** The existing device panel already knows a
  physical control can be an axis AND a button (the Gladiator trigger case).
  Don't assume a rebind only ever wants a button-shaped input.

## 2. Same rules as the original order, unchanged

- Conflict handling (flag, don't auto-resolve or hard-block) applies to
  joystick/gamepad captures exactly the same as keyboard ones.
- The untouched-binding round-trip guarantee still has to hold —
  `roundtrip.js` / `mutate.js` after this change, not just a manual export.
- Update the "press a key or mouse button" prompt text to actually describe
  what it now accepts, so it doesn't keep telling a HOTAS owner to do
  something that isn't what's happening. Something like "press a key, click
  a mouse button, or press a joystick/gamepad control" — your call on the
  exact wording, just make it true.

## 3. What NOT to do

- Don't rebuild joystick reading from scratch — `poll()`/`fireDev()` already
  does this correctly, reuse it.
- Don't gate rebind capture on the currently-selected device-mode tab.
- Don't touch the keyboard/mouse capture paths — they're correct as shipped.
- **Don't edit inside the injected block** — see the correction at the top.
- Don't deploy. Build only.

## 4. Acceptance

1. With a real or emulated gamepad/joystick connected, click a bound action
   in the browser, press a button on the stick, and see the binding update
   to the correct `js1_...` / `xi_...` token — **without needing to switch
   the device-mode tab first.**
2. A hat press captures its full compound token correctly.
3. Conflict detection fires the same way it does for keyboard/mouse when a
   joystick input is already used elsewhere in the same layer.
4. Export after a joystick rebind round-trips correctly — verify with a real
   diff, same discipline as the original order.
5. The listening-state prompt text accurately describes what it accepts.
6. `roundtrip.js` / `mutate.js` still pass.

## 5. STATUS — DONE, 2026-08-12, commit `0f0409c`

Shipped and live on the testing site. `/keybinds` verified byte-identical,
local 95,438 = live 95,438.

**Two things this order did NOT settle, carried forward rather than closed:**

- **Gamepads still refuse to rebind** (`xi_a`), deliberately and with a
  readable reason — the tester and the exporter disagree about the prefix and
  there is no evidence on this machine to settle which is right. Joystick and
  HOTAS are unaffected. Do not "fix" this by picking a prefix.
- **The poll-loop liveness question is open.** `renderDevice()` runs
  unconditionally immediately before `rafId=requestAnimationFrame(poll)` and
  has no container guard, so if it throws during a rebind started from the
  Keyboard/Mouse tab, the loop dies after one frame and the cell listens
  forever. A headless attempt to settle this produced a **false positive** —
  `requestAnimationFrame` doesn't run in that harness at all, so "poll ran 0
  times" was the environment, not the code. It needs a **visible browser**
  (no stick required): start a rebind from the KBM tab and watch whether the
  device readout keeps updating. If it freezes, guard `renderDevice` — not a
  try/catch around `poll()`, which would hide it.

## Commands

```
node testing/_src/roundtrip.js
```

```
node testing/_src/mutate.js
```
