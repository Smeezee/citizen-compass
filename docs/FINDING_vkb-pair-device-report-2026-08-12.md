# FINDING — real device report from a VKB Gladiator NXT EVO pair, and the slot numbers are climbing

    from    C1, 2026-08-12
    source  "Copy device report" output, taken on Sleven's friend's machine
              with both sticks connected. Pasted verbatim into chat by Sleven.
    status  First real hardware data this project has held for these devices.
              `data-layer/raw/devices/device_facts.json` records ZERO sourced
              button indices for the VKB Gladiator NXT EVO; this is measured,
              not sourced, and it is better than what we had.

---

## 1. The slot numbers are DRIFTING UPWARD between sessions

Earlier screenshot, same machine, same two sticks:

```
js2   VKBsim Gladiator EVO R
js3   VKBsim Gladiator EVO L
```

This report, later, same machine, same two sticks:

```
js3   VKBsim Gladiator EVO L
js4   VKBsim Gladiator EVO R
```

**Both numbers went up by one, and the two sticks swapped relative order.**

This is worse than the sticky-slot problem already described in
`prompt-code-slot-numbering-and-input-stall-2026-08-12.md` §1. It is not a
one-off bad assignment — **it increments on reconnect**, so it will keep
climbing: js5, js6, js7, js8, and then whatever `guessSlot`'s
`padSlot[p.index]=1; return 1;` fallback does when nothing is free.

Every one of those is unusable in Star Citizen, which has js1 and js2.

The reconciliation fix already ordered still covers this, but it should be
built knowing the failure is **progressive and self-worsening**, not static —
and that a stored choice is being written back each time, so the bad state is
being persisted, not just computed.

## 2. Axis layout, identical on both sticks

```
axes[0]  x          resting  0.000
axes[1]  y          resting  0.000
axes[2]  z          resting  0.000  (-0.018 on the L stick)
axes[3]  rotx       resting  0.000
axes[4]  roty       resting  0.000
axes[5]  rotz       resting  0.000
axes[6]  slider1    resting  0.000
axes[7]  slider2    resting  0.000
axes[8]  NO STAR CITIZEN NAME - unusable in a binding
axes[9]  hat1       resting  1.286
```

**Three things worth keeping:**

- **`axes[8]` has no Star Citizen name.** The VKB exposes 10 axes; SC's
  vocabulary covers 8 plus the hat. So one physical axis on this hardware
  **cannot be bound at all**, and the page says so rather than inventing a
  token. That's the right behaviour and it should stay — but it's a real
  limitation to state plainly to anyone with this stick, not bury.
- **The hat reads 1.286 at rest**, which is the above-1.0 signature
  `noteHat()` uses to identify a POV hat as a hat rather than an axis. Working
  exactly as designed, confirmed on real hardware for the first time.
- **`z` rests at -0.018 on the L stick** — real drift, inside the 0.12
  deadzone. Confirms the deadzone is doing its job and that a naive
  "capture the first axis that moves" rule would have grabbed this one.

## 3. The axis names are an ASSUMED ORDER and the page admits it

Every axis line carries **"(order not confirmed)"**. The mapping from browser
axis index to Star Citizen axis name is assumed, not measured. `x` being
`axes[0]` is conventional, not guaranteed — and on a HOTAS with 10 axes and no
standard mapping, convention is doing a lot of work.

**This matters for exports.** Binding "pitch" to `js1_y` is only correct if
`axes[1]` really is the stick's Y. If the order is different on this hardware,
the file will be confidently wrong in a way nobody notices until they fly.

**Cheap way to settle it, next time anyone is at that machine:** on
`/stick-test`, move **one axis at a time, fully**, and note which index moves.
Ten movements, and the assumed order becomes a measured one. That is the single
highest-value thing that hardware can produce right now, and it takes about a
minute.

## 4. Buttons

Both sticks report **128 buttons**, mapped straight through:
`js<N>_buttonK` ⇄ browser index `K-1`, no gaps, 1..128.

**128 is the HID report size, not the physical control count.** A Gladiator
NXT EVO has roughly 13 physical controls. So ~115 of those tiles per stick are
permanently dead, and a panel rendering all of them is mostly empty boxes —
which is what the "Hide unused buttons" control is for. Worth confirming it
defaults on for a device reporting this many.

**What this does NOT give us:** which *physical* control is `button1`. The
browser index is authoritative for the binding, but VKB documents its controls
by physical label, and the numbering shifts with firmware mode — the exact
reason `device_facts.json` has no sourced indices. Mapping physical control to
index still needs someone pressing them one at a time and writing it down.

## 4b. THE EXPORTED FILE — first one ever produced from defaults, analysed

Sleven pasted the actual export. **The machinery is sound and the file is far
closer to correct than "not very good" suggested.** It has a proper root
element, a `CustomisationUIHeader`, a `<devices>` block, real `<options>` lines,
`<modifiers/>`, and well-formed actionmaps.

**The device GUIDs are genuinely right**, which is the part that would have been
hardest to get wrong quietly:

```
{0201231D-0000-0000-0000-504944564944}   EVO L
{0200231D-0000-0000-0000-504944564944}   EVO R
```

PID `0201`/`0200`, VID `231D`, and the tail is the ASCII of "PIDVID" — correct
DirectInput GUID form. Nobody guessed that; it came off the hardware.

**Four defects, in order of severity:**

1. **`instance="3"` and `instance="4"`, and every binding is `js3_*` / `js4_*`.**
   The slot drift from §1 is baked straight into the file. This alone makes it
   useless to Star Citizen. **Everything else here is cosmetic next to this.**

2. **The `<devices>` block declares four joysticks:**
   ```xml
   <joystick instance="1"/><joystick instance="2"/>
   <joystick instance="3"/><joystick instance="4"/>
   ```
   but only instances 3 and 4 have `<options>` lines. Instances 1 and 2 are
   declared and never described — phantom devices. The declared set must match
   the described set exactly.

3. **`js3_button29` is bound to two actions in concurrently-active maps** —
   `v_flightready` (spaceship_general) and `v_atc_request` (spaceship_movement).
   Both maps are live in flight, so that is a real conflict, and the conflict
   detection did not flag it. Worth checking whether the check only looks
   *within* one actionmap rather than across the ones active together.

4. **`js3_rotx` and `js3_roty` are UNATTESTED tokens** — neither appears in
   CIG's `defaultProfile.xml` nor in either real profile
   (`FINDING_joystick-axis-vocabulary-2026-08-12.md`). They were offered and
   bound with no warning. The unattested flagging that was ordered either isn't
   reaching the export path or isn't shown at capture time.

**The renumbering fix is worth stating precisely:** the exported instance
numbers must be **1..N over the connected sticks**, and the `js<N>_` prefixes in
every `<rebind>` must match. Because the `<options>` Product GUIDs identify
which physical stick is which instance, renumbering is safe — Star Citizen
resolves the device by GUID, not by the number. So even as a belt-and-braces
measure, **the export path should renumber to 1..N regardless of what the UI is
displaying**, so a bad UI state can never again produce an unusable file.

## 5. What this unblocks

- The reconciliation fix now has a measured failure mode, not a theory.
- The axis-capture work has a real axis inventory to test against, including
  the two edge cases that would break it: an unnameable axis and a hat that
  rests above 1.0.
- The prescriptive-labelling work has its first real device to describe — and a
  clear statement of what is still missing for it (physical control → index).
