# FINDING — device panel: the swapped sticks are confirmed and have a definite cause. The stuck tab does not reproduce, and I am not going to guess at it.

    from      C3 (Cowork), 2026-08-09
    for       C1 + Sleven (→ Code)
    ask       Sleven, testing the live keybind page: sticks shown left/right reversed, and
              once on Keyboard/Mouse the device tabs will not switch back.
    method    Read `device_engine.js` and the deployed `_deploy/keybinds.html`, then loaded
              the real deployed page in headless Chromium and drove the tabs — first with no
              device, then with two injected sticks.

---

## BUG 1 — sticks appear on the wrong sides. CONFIRMED, reproduced, cause is definite.

Injected two sticks named to make the order visible, and the panel rendered:

    column 1 (left)   js1 — VKB Gladiator NXT EVO R
    column 2 (right)  js2 — VKB Gladiator NXT EVO L

**The Right stick took the left column, the Left stick took the right column.** Exactly the
symptom.

**Cause.** `device_engine.js:70` builds the list straight out of `navigator.getGamepads()` and
renders it in array order. `slotOf()` (line 76) then assigns `js1`, `js2` by first-seen order
and caches it on `p.index`.

**`p.index` is the browser's connection slot. It carries no information about where a stick
physically sits.** It follows USB enumeration order — which port, which was plugged in first,
sometimes which was powered up first. **The browser cannot know left from right, and nothing in
the code claims to; the two-column layout just implies an order the data does not have.**

**This is not fixable by sorting.** There is no attribute to sort on — `id` strings are vendor
text and "R"/"L" appearing in Sleven's is luck, not a standard. The only correct fix is to
**let the person say which is which, and remember it.** A swap control on the panel, persisted
per device id.

**And it matters more than cosmetics, because it decides what gets written into the mapping
file.** `prefix()` returns `js1_` / `js2_` from that same slot number. **If the browser's order
disagrees with Star Citizen's DirectInput order, every joystick binding in an exported profile
lands on the wrong stick** — and it fails silently, which is this project's recurring failure
shape. Whoever wires the binding builder needs to treat "which stick is js1" as a fact the user
supplies, never as one the browser reports.

**Unverified and worth knowing:** I have not confirmed whether Star Citizen's own js1/js2
assignment matches the browser's. It very likely does not, since they enumerate through
different APIs. That is part of the same ten-minute in-game test already outstanding.

## BUG 2 — tabs stuck on Keyboard/Mouse. DOES NOT REPRODUCE. Cause unknown.

**What I tried.** Loaded the real deployed `keybinds.html` and clicked through the device tabs,
twice over:

    no device connected        JOY -> PAD -> KBM -> JOY -> PAD -> JOY    all switched, no errors
    two sticks injected        JOY -> KBM -> JOY -> PAD -> JOY           all switched, no errors

`dev` changed correctly every time, `rafId` started and stopped as designed, the click handlers
were still attached at the end, and **zero console errors or page exceptions in either run.**

**Two theories I checked and eliminated, so nobody re-checks them:**

- **The `.ok` guard.** The handler starts `if(!DEVS.find(x=>x.id===b.dataset.d).ok) return;`,
  which looks exactly like a tab-disable. It is not: `DEVS` is a `const` with `ok:1` hardcoded
  on all three entries and nothing ever writes to it. The guard can never fire.
- **Handlers destroyed by a re-render.** `#devs` is rebuilt with `innerHTML` and the handlers
  re-attached in the same function; after six switches all three buttons still had a live
  `onclick`.

**So the bug is real but environmental — something in Sleven's actual browser that headless
does not have.** The most likely shape is a JavaScript exception thrown mid-render that kills
the click handler, and the difference between his machine and my harness is the real device
data: his VKB reports its true button count (sticks can report 128; my fake reported 29), real
axis values, and hat readings above 1.0 that the code specifically handles as a special case.
**That is a theory, not a finding, and I am not going to write a fix on it.**

**One piece of evidence settles it, and it takes ten seconds.** When the tabs stick:

1. Press **F12** to open developer tools.
2. Click the **Console** tab.
3. Read out any red error lines — the message and the file/line.

If there is a red error, that is the bug and it will name its own location. If the console is
clean, the cause is something else entirely and I will look again with that ruled out.

**Second, cheaper question that would also narrow it:** does it stick only after a stick has
been connected during the session, or also on a fresh page load where you go straight to
Keyboard/Mouse and back? That separates "device data broke something" from "tab logic."

## What I checked and what I did not

**Checked:** `device_engine.js` in full for the slot/order logic; the deployed
`_deploy/keybinds.html` device-tab handler; live tab switching in a real browser under two
device conditions; handler persistence after repeated switching; console and pageerror streams
in both runs.

**Did NOT check:**
- **Could not reproduce bug 2**, so its cause is unknown and nothing above should be treated as
  a diagnosis of it.
- Did not test with a device that reports 128 buttons, real hat axes above 1.0, or
  connect/disconnect events mid-session — all plausible triggers I could not simulate faithfully.
- Did not test the second standalone copy of the page (`keybinds.src.html`), which is still an
  open rule-14 duplicate and may behave differently from the deployed build.
- Did not modify any code, and did not touch anything on Sleven's machine.
