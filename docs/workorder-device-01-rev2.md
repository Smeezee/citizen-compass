# WORK ORDER — device panel: lag, hats, layout, guided mapping

    id            WO-DEVICE-01 rev 2
    supersedes    WO-DEVICE-01 (2026-08-05). Read this one.
    from          C2, 2026-08-05
    for           C1 -> Claude Code
    file          testing/_src/keybinds.src.html
    repo writes   C2 made none

Everything below came out of a live testing session on Sleven's own hardware:
**VKBsim Gladiator EVO R and EVO L, XT2 v2.199, VKBDevCfg v0.93.89,
NJoy32 firmware v2.20.D.** Both sticks were calibrated during the session and
now rest correctly — measured `0.020 / 0.000 / -0.010 / 0.000 ×6`.

**Four things are wrong or missing. One of them is a real bug.**

---

## D1 — THE LAG. This is the real bug, and it is not the polling.

**Symptom:** the page shows an axis off-centre after the stick has physically
returned to centre.

**The polling is correct.** `pads()` calls `navigator.getGamepads()` fresh every
frame (line 498) and `poll()` re-fetches the pad objects rather than holding a
stale reference. `requestAnimationFrame` throughout. **Nothing to fix there.**

**The cause is line 689:**

    if(changed||list.length!==(poll._n||0)){poll._n=list.length;renderDevice();}

and `renderDevice()` rebuilds the whole panel with `innerHTML`.

**With two devices declaring 128 buttons each, that is 256 button tiles plus
every axis bar destroyed and recreated — potentially every frame.** The trigger
is any axis moving more than 0.015:

    if(Math.abs(v-(prev.a[i]===undefined?v:prev.a[i]))>0.015) changed=true;

Move a stick and every frame is a full DOM teardown. **Frames get dropped, the
paint falls behind the input, and releasing the stick leaves a stale frame on
screen.** That is exactly the reported symptom.

**Fix: build the DOM once, then mutate.**

- Create tiles and bars on device connect / disconnect only.
- Keep a map of `index -> node` for buttons and axes.
- In `poll()`, update `textContent` and bar width directly. **No `innerHTML`
  after first render.**

**Assert:** with both sticks connected and one held at full deflection, the DOM
node count under the device panel does not change between frames. Release the
stick and the displayed value reaches centre within 100 ms.

---

## D2 — HATS. The page is showing a name Star Citizen cannot use.

The page currently labels a hat `js2_axis9`. **There is no such name in Star
Citizen.** Verified against CIG's own `defaultProfile.xml`: the joystick
vocabulary is

    js1_button1 ... js1_button128
    js1_hat1_up   js1_hat1_down   js1_hat1_left   js1_hat1_right
    js1_x   js1_y   js1_z   js1_rotx   js1_roty   js1_rotz   js1_slider1   js1_slider2

`JS_AX` (line 492) holds eight names. **Axis index 8 and beyond falls through to
`"axis"+i`, which produces a label the game will not accept.**

### The detection rule — deterministic, not a heuristic

A POV hat arrives through the Gamepad API as a single axis encoded in **sevenths**:

    -1.000   up
    -0.714   up-right
    -0.429   right
    -0.143   down-right
     0.143   down
     0.429   down-left
     0.714   left
     1.000   up-left
     1.286   centred / nothing pressed      <- 9/7, deliberately outside -1..1

**Sleven's stick rests at exactly 1.286.** Confirmed on screen.

**Rule:** an axis whose observed values are confined to that set, and which rests
at ~1.286, **is a POV hat.** Classify it as such and never draw it as an analog
bar.

### What to render instead

Name it `js2_hat1_up` / `hat1_down` / `hat1_left` / `hat1_right`, and draw it as
**a circle with a dot that moves to the pressed direction** — the same widget
VKB's own test tab uses, which Sleven specifically called out as the thing that
made it understandable.

**Number the hats per device** — `hat1`, `hat2`, `hat3` — in axis order, matching
how Star Citizen counts them.

**Do not offer "zero this axis" on a hat.** Re-centring it would destroy the
pattern the classifier depends on.

---

## D3 — ONE CONTROL CAN BE BOTH AN AXIS AND A BUTTON

**rev 1 modelled `points[]` for buttons and `axes[]` separately. That is wrong.**

The Gladiator's **Main Trigger has two stages** — confirmed in VKB's own
template, printed as "Main Trigger: 1, 2". Sleven found this live: the first
stage reads as a smooth analog axis, the detent at the end fires a button.

**Under the rev 1 model that becomes two dots in two places on the picture for
one thing under his finger.**

**Fix the data model before anything is built on it:** a *control* is the unit. A
control has a position and carries one or more *inputs* — any mix of axes,
buttons and hat directions.

    control: { id, label, x, y,
               inputs: [ {kind:"axis", index:2}, {kind:"button", index:1} ] }

---

## D4 — LAYOUT. Both devices at once, and only what is real.

**Sleven's requirement: seeing both controllers simultaneously is necessary.**
It currently is not possible — 128 tiles for device one push device two off the
bottom of the page.

**And the 128 is a VKB setting, not a browser limit.** Confirmed in VKBDevCfg →
**USB HID Controllers → `#But` = 128**. The device is configured to declare 128
buttons. **Roughly 34 are real** (see D5). So ~94 tiles per device can never
light up.

**Required:**

- **Both devices visible together**, side by side, without scrolling.
- **Show only controls that have fired this session.** Everything else collapses
  into one expandable line — *"94 further buttons this device declares but has
  not used."*
- **Add-on devices** — button boxes, pedals, throttle quadrants — behind a
  toggle. They are secondary and should not compete with the two things in the
  player's hands.
- **The full device report (`#dvcopy`) stays complete.** D4 changes what is
  displayed, never what is captured.

**This is also half the fix for D1** — fewer nodes is less to rebuild — but
**it is not a substitute for D1.** Do both.

---

## D5 — GUIDED MAPPING, not freeform clicking

rev 1 proposed: press a button, click where it is on your photo. **That works,
but it can be much better for devices where the control list is known.**

**VKB publish a control template per device.** Extracted from their own
templates for the Gladiator SCG — **these are the manufacturer's hardware
designations, i.e. facts, not artwork:**

| control | positions |
|---|---|
| A1 (Ministick) | press, up, down, left, right — **or** analog `A1(x)`, `A1(y)` |
| A2 (Red Button) | press |
| A3 (Center Hat) | press, up, down, left, right |
| A4 (Top Right Hat) — **Top Left** on the LH model | press, up, down, left, right |
| B1 (Side Button) | press |
| C1 (Thumb Hat) | press, up, down, left, right |
| D1 (Pinky Button) | press |
| Main Trigger | stage 1, stage 2 |
| Rapid Fire Trigger | up, down |
| F1, F2, F3 | base buttons |
| Sw1 (Base Left Side) | up, down |
| En1 (Base Right Side) | up, down |
| Axes | x, y, twist, throttle |

**34 discrete inputs. Not 128.**

**So the wizard becomes a checklist, not a blank page:**

> *"Press A3 Center Hat — up."* → captures whatever fires → next.

Ordered, complete, and it tells the person when they are done. **Freeform photo
clicking stays as the fallback** for any device with no known template.

**A1's two modes explain the difference between Sleven's two sticks.** The
ministick can run in **analog mode** (`A1(x)`, `A1(y)` — reads as a real axis
pair, centres cleanly, appears as `rotx` on his left stick) or as a **POV hat**
(appears as `axis9` on his right, resting at 1.286). **Same hardware, different
mode, set in VKBDevCfg.** The page should say so rather than let someone think
one stick is faulty.

**Licensing:** use the control *names* only. **Do not reproduce VKB's template
artwork** — the chart is credited to UntoldForce via the VKB Discord and the
layout is theirs. Names are hardware designations; the drawing is not.

---

## ORDER

1. **D1** — the lag. It is the only actual defect and it makes everything else
   feel broken.
2. **D4** — layout. Required for D1's benefit to be visible, and it is what
   Sleven asked for.
3. **D2** — hats. Currently emitting names the game rejects, which is worse than
   showing nothing.
4. **D3** — data model. Must land before any map is saved.
5. **D5** — guided mapping.

---

## ACCEPTANCE

    D1   DOM node count under the device panel is stable across frames;
         release-to-centre visible within 100 ms
    D2   a hat reports js2_hat1_up/down/left/right, renders as a circle,
         and is never offered a "zero this axis" control
    D3   the Main Trigger appears as ONE control carrying an axis and a button
    D4   both devices visible without scrolling; 0 button tiles at rest;
         exactly N after N distinct presses; #dvcopy output still complete
    D5   the wizard walks all 34 Gladiator controls in order and reports when done
    all  no VKB or other manufacturer artwork in the repo
    all  no account, no server-side storage

---

## NOT VERIFIED

- **Whether `js1`/`js2` survives a replug.** `slotOf()` assigns in connection
  order, first come first served. Sleven has two VKB devices. **A map keyed to
  `js1` could follow the wrong stick.** Still untested and still the biggest
  latent problem here.
- **Whether the hat should be `hat1` or a higher number** when a device exposes
  more than one POV.
- **Whether other manufacturers publish equivalent templates** — the D5
  checklist approach only pays off if they do.
- **Whether `#But` can be lowered from 128 in VKBDevCfg.** If it can, that is a
  one-setting fix for the user that beats any amount of UI work — **worth
  checking before building D4.**
