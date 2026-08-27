# Update — axes bind, no upload needed, and the page now says whether it can see your stick

Both orders built together. **Not deployed, nothing committed.**

## §1 Axis capture — `patch_axis_rebind_capture.py`

**FIRE at 0.55 of deflection from the axis's own centre, RE-ARM below 0.25.**

Why those: `DEADZONE` is 0.12 and exists to absorb drift and a knocked desk.
Binding has to require something nobody does by accident, so the threshold sits
past half travel — a resting stick cannot reach it and neither can a hand
brushing the grip. The 0.30 gap is hysteresis; without it a stick settling back
through a single threshold chatters, and "which axis did you mean" becomes
whichever frame won. Re-arm is **per axis per device**, so push Y, release, push
X and you get two bindings in the order pushed rather than a latch on the first.

Centre comes from the panel's existing `padCenter`, so a throttle resting at
-1.0 works without re-deriving anything. The token comes from the existing
`axName()` — no second axis table. An axis past `slider2` has no Star Citizen
name at all and is **refused** rather than bound to something invented.

**Only while a rebind is listening.** Outside one, that branch behaves exactly as
before — `hot` and nothing more, so the live readout is untouched.

## §1 token shape — read from evidence, not chosen

Both real fixtures contain `js1_x js1_y js1_z js1_rotz js2_x js2_y js2_rotz`
and **no directional variant of any kind**. So an axis binds as the axis; which
way it was pushed is not part of the binding.

## §2 Evidence at the moment of capture

`KB_DOF` is read rather than duplicated. **PROVEN:** `x y z rotz` (real player
profiles) and `slider1` (shipped defaults only). **UNATTESTED:** `rotx roty
slider2`. Binding an unattested axis works and is **labelled in the cell** —
*"unattested — never seen in a real profile"* — because never-seen is not the
same as invalid, and the difference has to reach the person writing the file.

## §3 The upload requirement is gone — verified end to end

```
baseline starts as none                                    PASS
startDefaults gives a usable baseline with NO upload        PASS
five stick controls bind with no profile loaded             PASS
a file is produced from defaults alone (1,074 bytes)        PASS
it contains ONLY the 5 deliberate bindings, not all 691     PASS
   v_pitch=js1_y  v_yaw=js1_x  v_roll=js1_rotz
   v_strafe_vertical=js2_y  v_attack1=js1_button1
both sticks declared in <options>                           PASS
an imported profile with zero changes is unchanged          PASS
```

A Star Citizen actionmap **overlays** the defaults rather than restating them,
so an empty overlay means "unchanged" and every entry is a deliberate change.
Import still works, unchanged, for editing a profile you already have — two ways
in, one editor. The page states which baseline is live at all times.

## Addendum — why it took a refresh, and the sentence nobody wrote

C1's three-gate reading is exactly right, and the third gate was the killer:
`gamepadconnected` was itself gated `if(dev!=="KBM")`, so the one event that
could recover the situation was **discarded on the default tab**.

**`patch_device_presence.py`:** a 400 ms `setInterval` whose only job is to ask
whether the set of connected devices changed. It calls `getGamepads()` and joins
the ids — no per-button or per-axis reads, and **no DOM work unless the answer
actually changed**. 2.5 calls a second against a 60 Hz input loop is noise.
`setInterval` deliberately, not rAF, because rAF is throttled to about one frame
a minute in a background tab. The heavy loop keeps its gating — that lag was
real. The distinction drawn is between *sampling input* and *knowing a device
exists*.

**The copy fix is the one I think matters most.** Chrome reports **nothing** for
a controller until a control on it is pressed while the page has focus, so a
correctly installed stick reads as absent until touched — and the page showed an
empty panel and said nothing. There is now an always-visible line:

> **No flight stick or gamepad seen yet.** Press any button on it and it will
> appear here — browsers do not report a controller until you touch it. If
> nothing appears, check the stick's own software is running.

and when devices are present it names them.

## §4 Prescriptive

A listening cell now states what it will accept *and* what is connected right
now, and a set binding shows **plain language beside the token** — "Stick 1 Y
axis" next to `js1_y` — so what lands in the file is never a surprise.

## §4 of the main order — the honesty that now matters more

Generating from defaults is **no longer a round trip**; it is us asserting we
know the format. **No file this tool has produced has ever been loaded by Star
Citizen** and `verified` stays hard-coded false.

**Sleven settles it in one test.** Export from defaults and drop the file in:

```
%USERPROFILE%\Documents\StarCitizen\...\USER\Client\0\Controls\Mappings\
```

then in-game: `Options → Keybindings → Control Profiles → load it`.

## Verification status, stated plainly

`roundtrip.js` ALL CHECKS PASSED · `mutate.js` 19/20 M18 · build and guard clean.
Everything above confirmed present in the **built** page, and the presence check
reached `index.html` too.

**What is NOT verified:** the axis threshold behaviour with a real stick, and
the reload-free detection cases 1–3. Headless Chrome cannot drive either —
`requestAnimationFrame` does not fire there, and it has been hanging on this
machine for the last hour, so the final UI pass ran in Node against the built
page's modules rather than in a browser. The measured cost figures the addendum
asks for need a real device and I do not have one.
