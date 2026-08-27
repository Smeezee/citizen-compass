# FINDING — a second export from the same machine gives us an A/B pair. Instance numbers are stable, buttons reach 29, and one input routinely drives several actions.

    from      C3 (Cowork), 2026-08-09
    for       C1 + Sleven (→ Code)
    source    test3cr.xml — same machine, same two VKB sticks, different profile.
              Diffed against test1CR.xml from the same session.
    extends   claude/FINDING_real-joystick-export-2026-08-09.md

---

## 1. Why a second file is worth more than twice one file

One export tells you the schema. **Two exports from the same hardware tell you what is fixed
and what is the player's choice** — and that is the distinction a builder has to get right.

## 2. Device declarations are byte-identical across both profiles

    keyboard inst 1   Keyboard  {6F1D2B61-D5A0-11CF-BFC7-444553540000}
    joystick inst 1   VKBsim Gladiator EVO L    {0201231D-0000-0000-0000-504944564944}
    joystick inst 2   VKBsim Gladiator EVO R    {0200231D-0000-0000-0000-504944564944}

**Identical. Same GUIDs, same instance numbers, both profiles.**

This is the confirmation the VID/PID approach needed. The instance number is a property of
*the device on that machine*, not of the profile — so a builder that derives `js1`/`js2` by
matching VID/PID will agree with whatever the game already decided, across every profile that
machine produces. **Left stick is js1, right is js2, consistently.**

## 3. Buttons reach 29, not 22

Combined across both files, real button numbers used:

    1 2 3 4 6 7 8 9 10 11 12 13 14 16 17 18 19 21 22 25 26 27 28 29

**Highest is `js1_button29`.** My previous finding said 22 because that is all the first file
showed. **Do not treat any observed maximum as a ceiling** — each new file has raised it. The
right position is that no upper bound has been observed, and a builder should not impose one.

## 4. The axis picture, now from two real profiles

    used across both files:  x, y, z, rotz
    js1 uses:                x, y, z, rotz     (all four)
    js2 uses:                x, y, rotz
    still unattested:        rotx, roty, slider2

`slider1` is in the game's shipped defaults but appears in neither real profile — so it is
attested by the defaults, not by these. `z` is now doubly confirmed.

**Corrected status for the DOF page:** four axis names PROVEN by real use (x, y, z, rotz),
one PROVEN by the defaults only (slider1), three still unattested (rotx, roty, slider2).

## 5. The diff is small and clean, which validates the "only what changed" model

    test1CR   45 actions carrying a real binding
    test3cr   56 actions carrying a real binding
    added 11 · changed 4 · removed 0

What he actually did between the two:

    + v_pitch                 js2_y        added the real flight axes
    + v_roll                  js1_x
    + v_yaw                   js2_rotz
    + v_strafe_longitudinal   js1_y
    + v_atc_request           js1_button29     and reached for the high buttons
    + v_deploy_landing_system js1_button26
    + v_retract_landing_system js1_button25
    + v_power_toggle          js1_button28
    + v_power_toggle_thrusters js1_button27
    ~ v_afterburner           js2_button1  -> js1_button2    moved work onto the left stick
    ~ v_space_brake           js2_button2  -> js1_button3
    ~ v_strafe_lateral        js2_x        -> js1_x
    ~ v_strafe_vertical       js2_rotz     -> js1_rotz

**Nothing was removed.** He iterated on a layout rather than rebuilding it — which is exactly
the workflow the builder's Import needs to support: load the existing profile, adjust, export.

## 6. THE ONE THAT CHANGES THE UI — an input drives several actions, routinely

**13 inputs in test3cr are bound to more than one action.** Nine across different actionmaps,
**four within the same actionmap**:

    js1_x          spaceship_movement.v_roll   AND  spaceship_movement.v_strafe_lateral
    js2_button8    spaceship_movement.v_autoland  AND  .v_toggle_landing_system
    js1_hat1_left  spaceship_targeting.v_target_toggle_lock_index_1
                   AND  .v_target_toggle_pin_index_1_hold
    js1_hat1_up    same shape        js1_hat1_right  same shape

The `js1_x` one is the instructive case: **roll and lateral strafe on the same axis** is how a
HOSAS layout works — the ship's flight mode decides which applies. The hat pairs are a tap
versus hold split on one direction.

**So "one input, one action" is wrong, and a builder that enforces it would prevent a normal
HOSAS setup.** The rule should be: allow it, show it, never silently overwrite. When someone
binds an input already in use, the tool should say *"this is also on X"* and let them decide —
because sometimes that is the point and sometimes it is a mistake, and only the person knows.

My prototype currently replaces any existing binding for the same action, which is right, but
it says nothing when the same *input* lands on a second action. That needs adding.

## 7. Consolidated: what a correct exporter must do

Carrying forward from the first finding, with §2/§3/§6 added:

1. Emit `<options type="joystick">` with the GUID built from VID/PID — **now confirmed stable
   across profiles.**
2. Add `mo` to the recognised device prefixes.
3. Write `prefix_ ` for an explicit unbind.
4. Allow multiple `<rebind>` under one action.
5. Carry `activationMode` where set.
6. Derive js1/js2 by VID/PID, not slot order.
7. **Impose no button-number ceiling.**
8. **Permit one input on several actions; warn, do not block.**

## 8. What I checked and what I did not

**Checked:** parsed both files; compared device declarations exactly; diffed every action and
rebind between them; collected every axis name and button number across both; counted
multi-action inputs and separated same-actionmap from cross-actionmap cases.

**Did NOT check:** still no file has been loaded into the game by me or anyone — both of these
were produced *by* Star Citizen, which proves the format is what the game writes, not that our
generated files will be accepted. **That test is still outstanding and is still the only one
that settles it.** Both files are also from one machine with one vendor's sticks; the
`Product` string format for other vendors remains unverified.
