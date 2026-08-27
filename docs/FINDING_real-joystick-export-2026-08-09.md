# FINDING — a real two-stick export answers every open joystick question, proves `sc_export.js` would write a broken file, and overturns two claims I made earlier today.

    from      C3 (Cowork), 2026-08-09
    for       C1 + Sleven (→ Code)
    source    layout_test1CR_exported.xml — a real Star Citizen export from Sleven's friend's
              machine, VKBsim Gladiator EVO L + R, 28 actionmaps, 228 actions, 247 rebinds.
    status    This supersedes the "NOT PROVEN" section of
              claude/finding-sc-mapping-export-format.md and parts of my own
              FINDING_device-panel-two-bugs and the DOF reference I shipped an hour ago.

---

## 1. THE ANSWER — a joystick DOES need an `<options>` line, and it carries a GUID

Verbatim from the file:

    <options type="keyboard" instance="1" Product="Keyboard  {6F1D2B61-D5A0-11CF-BFC7-444553540000}"/>
    <options type="joystick" instance="1" Product=" VKBsim Gladiator EVO L    {0201231D-0000-0000-0000-504944564944}"/>
    <options type="joystick" instance="2" Product=" VKBsim Gladiator EVO R    {0200231D-0000-0000-0000-504944564944}"/>

**`sc_export.js` deliberately omits that line and returns `verified:false`.** We now know
omitting it is wrong. Every joystick file the exporter has ever produced is missing the
device declaration. **That is the defect, it is proven rather than suspected, and it is the
one thing standing between this feature and working.**

The `<devices>` block also lists both sticks separately:

    <devices><keyboard instance="1"/><mouse instance="1"/><joystick instance="1"/><joystick instance="2"/></devices>

## 2. The GUID is fully derivable from what the browser already reports

The GUID is not opaque. Decoded:

    {0201231D-0000-0000-0000-504944564944}
     ^^^^ PID
         ^^^^ VID
                              ^^^^^^^^^^^^ ASCII for the literal string "PIDVID"

And Chrome's Gamepad API `id` for that same stick reads
`VKB Gladiator NXT EVO L (Vendor: 231d Product: 0201)` — **the same VID and PID.**

Reconstructed both GUIDs from the browser strings and compared to the real file:

    js1  built {0201231D-0000-0000-0000-504944564944}   MATCH
    js2  built {0200231D-0000-0000-0000-504944564944}   MATCH

**So the page can build the exact `<options type="joystick">` line itself, with no user input
and no guessing.** Formula: `{<PID><VID>-0000-0000-0000-504944564944}`, both 4 hex digits,
upper case.

**This also corrects my own finding from earlier today.** I wrote that the browser cannot know
which stick is which and that the user must set js1/js2 by hand. **The premise was wrong.**
Star Citizen does not assign by physical position either — it assigns by *device identity*,
and that identity is in the GUID, which the browser exposes. The correct fix is to match on
VID/PID, not to ask the user. A manual override is still worth keeping as a fallback, but it
should not be the mechanism.

**Worth noting for whoever builds it: on this machine js1 is the LEFT stick (PID 0201) and
js2 is the RIGHT (PID 0200).** Neither alphabetical nor connection order would have guessed
that.

## 3. `prefix_` followed by a SPACE means "explicitly unbound"

    <rebind input="kb1_ "/>      <rebind input="js2_ "/>      <rebind input="mo1_ "/>

**202 of the 247 rebinds in this file are of that shape.** An export is overwhelmingly a
record of what the player *cleared*, not what they set. Only 45 rebinds carry a real input.

**This changes what "an export contains only what changed" means.** It was already on record;
what is new is that *clearing a default counts as a change* and is written explicitly. A
builder that only emits positive bindings produces a materially different file from one the
game itself writes — and a user who unbinds something in our tool needs that `prefix_ `
written, or the game default silently stays.

## 4. `mo1_` is a real device prefix — the mouse rule needs refining

The settled note says "mouse rides the keyboard prefix: `kb1_mouse4`, never `ms1_`." That is
correct for mouse *buttons*. This file shows a second prefix for mouse *axes*:

    <action name="v_view_pitch_mouse"><rebind input="mo1_ "/></action>
    <action name="v_yaw_mouse">        <rebind input="mo1_ "/></action>
    <action name="weapon_melee">       <rebind input="mo1_ "/></action>

**`sc_export.js`'s `famOf()` only knows `kb`, `js` and `gp`, so it would REFUSE every `mo1_`
input as "no recognised device prefix."** Round-tripping a real profile through the current
exporter would silently drop these.

Caveat: every `mo1_` in this file is an unbind, so this proves the prefix exists and does not
prove what a bound mouse axis looks like.

## 5. `z` is a valid axis name — my DOF page is wrong and needs correcting

    <action name="v_mining_throttle"><rebind input="js1_z"/></action>

**I shipped a DOF reference an hour ago marking `z` as UNPROVEN because it appears nowhere in
the game's default profile. This file disproves that.** `z` is accepted and in real use.

Corrected status:

    x        PROVEN   in the shipped defaults, and here (js2_x)
    y        PROVEN   in the shipped defaults, and here (js2_y)
    rotz     PROVEN   in the shipped defaults, and here (js2_rotz)
    slider1  PROVEN   in the shipped defaults
    z        PROVEN   NOT in the defaults, but used in this real profile
    rotx     unproven still — appears in neither
    roty     unproven still
    slider2  unproven still

**The lesson is about the inference, not the fact.** "Absent from the shipped defaults"
never meant "invalid" — it only ever meant "unattested." I labelled an absence as evidence,
which is the exact pattern this project has logged five times, and I did it while writing a
document about being careful.

## 6. Buttons go to 22 — "button12 is the ceiling" was about the defaults only

Real buttons used: **1–22**, including 13, 14, 16, 17, 18, 19, 21 and 22.

The standing note that "the shipped joystick profile reaches only button12… that is the
entirety of out-of-box HOTAS support" is true **of the defaults**, and I repeated it in a way
that implied a limit. **The game accepts at least button22.** The defaults are poor; the
engine is not.

## 7. Two more mechanics worth building for

**Multiple `<rebind>` under one action — 19 actions do this**, one per device:

    <action name="v_afterburner">
      <rebind input="kb1_ "/>          <- keyboard cleared
      <rebind input="js2_button1"/>    <- and bound on the right stick
    </action>

Our model of one input per action is too narrow.

**`activationMode` is a real attribute**, on 4 rebinds here, all `press`:

    <rebind input="kb1_ " activationMode="press"/>

`keybinds_site.json` already carries an `activation` field per action (tap, press,
delayed_hold_no_retrigger…), so this is representable — it is just not currently written.

## 8. Still unproven after this file

- **Modifier combinations.** Zero inputs in this file contain `+`. `sc_export.js` still
  refuses them, still correctly.
- **Whether the `Product` *name* text matters** or only the GUID. This file has
  `" VKBsim Gladiator EVO L    "` with irregular leading and trailing spaces, while Chrome
  reports `"VKB Gladiator NXT EVO L"` — different strings for the same device. **Do not assume
  the name is free-form until someone loads a file with a name that does not match.**
- What a *bound* `mo1_` axis looks like.
- `rotx`, `roty`, `slider2`.

## 9. What Code should change in `sc_export.js`

1. **Emit `<options type="joystick" instance="N" Product="…"/>`** built from VID/PID per §2.
   This is the fix that makes joystick export actually work.
2. **Add `mo` to `famOf()`** so mouse-axis inputs are not refused.
3. **Support an explicit unbind** — write `prefix_ ` when a user clears a default.
4. **Allow multiple rebinds per action**, one per device.
5. **Carry `activationMode`** through from the action data where it is not the default.
6. **Assign js1/js2 by VID/PID match, not by browser slot order.**
7. **`verified` can become true for joystick output once 1 is done and a generated file has
   actually loaded** — but not before. The test is still the test.

## 10. What I checked and what I did not

**Checked:** parsed the whole file; counted every actionmap, action, rebind, prefix and input;
decoded both joystick GUIDs and reconstructed them from Chrome's own id strings to confirm the
derivation; compared every claim in the existing findings against it.

**Did NOT check:** I have not loaded any file into the game — this is one real export read
carefully, not a round trip. Everything in §9 is a change to make, not a change proven to
work. And this is a **single machine with two VKB sticks**; a different vendor could format
the `Product` string differently, which §8 flags rather than assumes.
