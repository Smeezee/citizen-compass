# FINDING — Star Citizen loaded a profile this tool generated, and accepted every binding. The standing caveat is retired.

    from    C1, 2026-08-12
    status  PROVEN, by the game itself. Not inferred, not argued.
    method  Sleven exported a from-defaults profile from `/keybinds` with one
              VKB Gladiator NXT EVO R, loaded it into Star Citizen, then had the
              game write its own profile back out. Both files compared here.

---

## 1. Why this matters more than anything else settled today

`CURRENT-STATE.md` has carried this line since the exporter was built:

> **Still true and still the only test that settles it: no file this tool
> generated has ever been loaded by Star Citizen.** `verified` is hard-coded
> false and stays false until one has.

**One has.** That caveat is retired.

It mattered more than usual because the from-defaults work removed the import
requirement — meaning the tool stopped echoing back a file the game itself
wrote, and started *asserting* it knows the format. Nothing had ever tested that
assertion. Now something has.

## 2. What went in

`citizen-compass.xml`, generated from stock defaults, no profile imported.
Nine bindings, one joystick.

## 3. What the game wrote back out

`layout_onesticktest_exported.xml`, written by Star Citizen after loading it.

**The `<options>` line came back verbatim:**

```xml
<options type="joystick" instance="1" Product=" VKBsim Gladiator EVO R    {0200231D-0000-0000-0000-504944564944}"/>
```

Byte-for-byte what we wrote — leading space, internal spacing, GUID and all. The
device identification was correct, which was the part with the most room to be
subtly and invisibly wrong.

**Every binding survived:**

| action | token | in the game's own export |
|---|---|---|
| `v_weapon_preset_fire_guns0` | `js1_button1` | yes |
| `v_weapon_preset_fire_guns1` | `js1_button2` | yes |
| `v_weapon_toggle_launch_missile` | `js1_button3` | yes |
| `v_view_dynamic_zoom_rel` | `js1_button6` | yes |
| `v_roll` | `js1_x` | yes |
| `v_yaw` | `js1_rotz` | yes |
| `v_view_pitch` | `js1_roty` | yes |
| `v_view_yaw` | `js1_rotx` | yes |
| `v_pitch` | `js1_y` | **omitted — correctly, see §5** |

## 4. `rotx` and `roty` are now PROVEN

`FINDING_joystick-axis-vocabulary-2026-08-12.md` recorded `rotx`, `roty` and
`slider2` as UNATTESTED — absent from CIG's `defaultProfile.xml` and from both
real profiles. I flagged both of Sleven's view-axis bindings as tokens that
might simply be rejected.

**Star Citizen wrote both of them back out itself.** That is the game asserting
they are valid, which is stronger evidence than either source we had.

**Revised axis table:**

| token | status |
|---|---|
| `x`, `y`, `z`, `rotz`, `slider1` | PROVEN — CIG defaults and/or real profiles |
| `rotx`, `roty` | **PROVEN — round-tripped through the game, 2026-08-12** |
| `slider2` | still UNATTESTED |

`slider2` remains the only unproven name. Absence is still weak evidence, not
proof of invalidity.

## 5. The one apparent loss is correct behaviour, and the reason matters

`v_pitch → js1_y` does not appear in the game's export. It was not rejected.

CIG's own default profile:

```xml
<action name="v_pitch" ... joystick="y" .../>
```

**`y` is the stock default for pitch.** A Star Citizen actionmap records only
what *differs* from default, so binding pitch to `y` is a no-op and the game
correctly wrote nothing. Accepted, then omitted as redundant.

**This is worth carrying forward as a rule**, because it will otherwise read as
data loss to the next person who diffs an export: *a binding missing from the
game's output may mean it matched the default, not that it failed.* Any future
round-trip check has to compare against `defaultProfile.plain.xml`, not against
an empty set — otherwise it will report false losses, confidently.

## 6. A deviation from stock that is not a defect

CIG's defaults are `v_roll = rotz` and `v_yaw = x` — stick left/right yaws, twist
rolls. Sleven bound the conventional HOTAS layout instead: left/right rolls,
twist yaws. **The game accepted the inversion without complaint.** Noting it so
nobody later "corrects" it back toward stock thinking it's a bug.

## 7. What this does and does not prove

**Proves:** the file format is right, the device GUID derivation is right, the
`<options>` structure is right, the token vocabulary is right including two
names we had no evidence for, and a profile built from defaults with no import
is loadable.

**Does not prove:** that the bindings behave correctly in flight. The game
accepting a file and the controls doing the right thing in a cockpit are two
different claims. Sleven flying it is still the remaining test.

**Also still open:** the multi-stick case. This was one joystick. The js1/js2
slot handling, the swap control and two-device `<options>` blocks are untested
against real hardware and remain as specified in
`prompt-code-MASTER-keybinds-and-the-rest-2026-08-12.md`.
