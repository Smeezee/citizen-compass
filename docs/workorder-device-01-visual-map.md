# WORK ORDER — device detection and the visual button map

    id            WO-DEVICE-01
    raised by     C2 (Cowork), 2026-08-05
    for           C1 -> Claude Code
    file          testing/_src/keybinds.src.html   (39,125 bytes, 2026-08-05 20:06)
    repo writes   C2 made none
    gate          WO-D0 must run first. It decides whether WO-D1 exists at all.

Observed live on Sleven's machine: **VKB Gladiator EVO L, `231D-0201`**,
128 buttons, 8 axes, raw / no standard mapping.

---

## WHAT ALREADY WORKS — do not rebuild it

Read from source, not assumed:

    line 492   const JS_AX=["x","y","z","rotx","roty","rotz","slider1","slider2"];
               with the comment "HOTAS axis order is device-dependent.
               This is the COMMON order, not a promise."   <- correct and honest
    line 519   btnName() -> prefix + "_button" + (i+1), "Button "+(i+1)+"  (browser index "+i+")"
               SC counts from 1, the browser from 0. THIS IS CORRECT.
    line 528   renderDevice() - reads p.id, p.buttons.length, p.axes.length, p.mapping
    line 694   addEventListener('gamepadconnected', ...)
               slotOf() assigns js1..js8 in connection order
               DEADZONE 0.12, DRIFT 0.06, #dvcal "Set centre", #dvcopy "Copy device report"

**Axes read correctly.** Confirmed live: `0.021 / 0.550 / 1.000 / 0.000 / 0.000 /
-0.017`. **The device id string is already parsed and displayed.** That string is
the whole hook for everything below.

---

## WO-D0 — THE GATE. Ten seconds. Do this before anything else.

Sleven reports buttons "not recognizing all the way."

**Three possible causes and only one is ours:**

1. `p.buttons.length` is **128** because the device or the HID layer declares
   128. The grid renders one tile per reported button, so ~100 tiles can never
   light. **Display problem, ours.**
2. **VKB onboard logic.** A physical button assigned to a shift layer or a mode
   emits a different logical button, or none, until that layer is active.
   **Device configuration, not ours.**
3. **Hat switches** report as buttons, as a POV, or as an axis pair depending on
   device setup. A hat in axis mode looks dead to a button watcher.
   **Device configuration, not ours.**

**The test, and it is not optional:**

> Windows → **Set up USB game controllers** (`joy.cpl`) → Gladiator → Properties.
> Press every button that appears dead in the tester.

    Windows does not light it either  ->  device config. NOTHING here can fix it.
                                          Report and stop.
    Windows lights it, tester does not -> a real bug. Diagnose before WO-D1.

**Do not write code before this runs.** Building a visual map on top of an
unexplained input bug produces a map with holes and no way to tell whether the
hole is the map or the device.

---

## WO-D1 — quiet the grid (small, do regardless)

**In:** `renderDevice()`, the `p.buttons.forEach((b,i)=>...)` block.

Track which indices have fired at least once this session — `padPrev` already
holds per-pad state and is the natural home.

- **Never fired:** collapse into a single line — *"96 further buttons this device
  reports but has not used."* Expandable.
- **Has fired:** render as now.

**Rationale:** 128 tiles for a stick with ~30 usable controls is why it reads as
broken. **This is a display change only. Do not filter the underlying data** —
the device report must still list everything.

**Assert:** with nothing pressed, the visible tile count is 0 plus the collapsed
line. After pressing 5 distinct buttons, exactly 5 tiles are visible.

---

## WO-D2 — surface the identity (small, do regardless)

The device string is already read into `p.id` and rendered inside `.dvchip .nm`.
**Promote it.** It is currently a title attribute on a small chip.

Show, prominently: the full id, the parsed **VID-PID** (`231D-0201`), the button
and axis counts, and whether the mapping is `standard` or `raw`.

**Why it matters beyond cosmetics:** VID-PID is the key everything in WO-D3 hangs
off, and a user reporting a problem needs to be able to read it off the screen.

---

## WO-D3 — the visual map

**The constraint, stated plainly:** the Gamepad API returns an index and a
pressed value. **It returns no name, no position, no picture, and no HID usage
info.** There is no way to know index 12 is the trigger. **No API provides this,
for any device, in any browser.** A map must exist; the only question is who
builds it.

**Answer: the user builds their own, once, in about two minutes.**

### Flow

1. Device detected, no map for this VID-PID → offer to make one.
2. **User uploads a photo of their own stick** (see §Images below).
3. **Press a physical button.** The page captures the index that fired.
4. **Click that button's position on the photo.** A dot is placed.
5. Repeat as far as they care to. **Partial maps are valid and useful.**
6. Save.

Thereafter every press lights the correct dot.

### Storage

    key      vid-pid  (e.g. "231D-0201")
    value    { photo: <data or blob ref>,
               points: [ {index: 12, x: 0.42, y: 0.31, kind: "button"}, ... ],
               axes:   [ {index: 1,  x: 0.50, y: 0.60, label: "pitch"}, ... ],
               made_by, made_at, device_id_string }

**Coordinates normalised 0..1**, never pixels — the photo will be displayed at
different sizes.

**Export and import as a small JSON file**, so a map can be shared. One person
maps a Gladiator EVO and everyone with one benefits. **A wrong map is
self-evident the moment a button is pressed**, so this needs little moderation.

**Storage note:** the site uses no accounts and stores nothing server-side. Maps
live in the browser and travel as files. **Do not add an account for this.**

### Images — the licensing answer

**Do not use manufacturer product photos.** VKB's, Thrustmaster's and Logitech's
images are theirs.

    A. the user's own photo    preferred. No licensing question exists.
                               Looks like the thing in their hand.
                               Works for home-built and rare kit.
    B. an outline we draw      ours, reusable, for when no photo is uploaded
    C. a numbered generic shape  honest fallback

**Build A first.** Least work, no legal question, best result.

---

## ACCEPTANCE

    WO-D0   joy.cpl result recorded in the inbox, per cause, before any code
    WO-D1   0 visible tiles at rest; exactly N visible after N distinct presses;
            the device report still lists all 128
    WO-D2   VID-PID "231D-0201" readable on screen without hovering
    WO-D3   a map made on one machine, exported, imported on another, lights the
            same dots
    all     no manufacturer imagery anywhere in the repo
    all     no account, no server-side storage, no login

---

## FORBIDDEN

1. **No manufacturer product photography.**
2. **No account system.** Standing rule: never require an RSI login, and this
   project has no accounts at all.
3. **Do not filter the device report.** WO-D1 changes what is *displayed*; the
   "Copy device report" output (`#dvcopy`) must remain complete, because it is
   what someone pastes when asking for help.
4. **Do not guess a layout for any device.** A map is made by the person holding
   the stick or it does not exist.

---

## NOT VERIFIED

- **The joy.cpl result.** WO-D0. Everything else is downstream of it.
- **How the Gladiator's hat reports** — buttons, POV, or axes. Visible by pressing
  it and watching which section of the tester reacts.
- **Whether 128 is the device's declaration or a browser cap.** `p.buttons.length`
  is reported as 128; the source of that number was not established.
- **Whether `js1`/`js2` slot assignment survives a replug** when two VKB devices
  are connected. `slotOf()` assigns in connection order, first come first served
  — **Star Citizen's own instance numbering is known to shuffle, and Sleven has
  a stick and a separate base attached.** Worth testing; a map keyed to `js1`
  would follow the wrong device.
- **Whether the map should key on VID-PID or on the full `p.id` string.** Two
  identical sticks would share a VID-PID and need distinguishing.
