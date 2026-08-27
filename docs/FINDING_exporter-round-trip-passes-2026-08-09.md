# FINDING — the rewritten exporter reproduces both of his friend's real mapping files byte for byte, in the browser, from shuffled input. 19 of 20 mutations caught; the survivor is a genuine limit of the evidence, not a gap in the tests.

    from      C3 (Cowork), 2026-08-09
    for       Code + C1 + Sleven
    builds on claude/FINDING_real-joystick-export-2026-08-09.md
              claude/FINDING_second-export-ab-pair-2026-08-09.md
              claude/WORKORDER_keybind-builder-the-missing-half.md
    artifacts inbox/sc_export2.js · inbox/roundtrip.js · inbox/mutate.js
              Downloads/citizen-compass-keybind-builder.html

---

## 1. The result

`sc_export2.js` reads a mapping file Star Citizen wrote, and writes it back **identical
to the character, including the CRLF line endings.** Both of the real exports, in node
and again in a real browser through the actual builder page.

    real_export.xml   (test1CR)  247 rebinds   byte-for-byte identical
    real_export2.xml  (test3cr)  247 rebinds   byte-for-byte identical

Byte-exactness is not what the game requires. It is what makes the test honest: there is
no judgement in it, no "close enough", nothing for me to grade myself on. Either the
bytes match or they do not.

**And it still does not prove the feature works.** Both files were written BY the game.
Reproducing them proves we understand the format. It does not prove Star Citizen will
accept a file we invent. That test has not been run by anyone and is unchanged as the
only thing that settles it.

## 2. What the old exporter would have done to the same file

Running his real profile through the exporter currently in the repo:

    the joystick <options> lines      omitted        both sticks lose their identity
    202 explicit unbinds              refused        every cleared default silently returns
    all mo1_ inputs                   refused        famOf() does not know the prefix
    19 actions with two rebinds        one kept       the joystick half of each pair dropped
    activationMode                     dropped
    buttons above 12                   kept, but the standing note implied a ceiling

**The current exporter cannot round-trip a real profile. Not "produces a slightly different
file" — it loses more than 80% of the content.**

## 3. Three ordering rules, measured rather than guessed

These are what byte-exactness actually turned on, and none of them was in any note:

**Actionmaps run in the game's own order**, which is the first-seen order of
`keybinds_site.json`, filtered to the maps present. Checked against both files: exact,
28 maps and 29 maps. Alphabetical order — which is how `actionmap_categories.json`
happens to be stored — is wrong and was the first thing I tried.

**Actions inside an actionmap are sorted ASCII-ascending by name.** All 57 actionmaps
across both files, exact. This one is counter-intuitive: the maps are in game order and
the actions inside them are alphabetical, so a single rule does not cover both.

**Rebinds inside an action follow device order** — keyboard, mouse, joystick, gamepad.
All 39 multi-rebind actions across both files.

Also: `<categories>` is first-seen across the emitted actionmaps, looked up from
`actionmap_categories.json`. That reproduced all 11 category labels in the right order on
both files — and it is worth saying that the lookup table came from the repo, not from the
export, so this is the repo's own data independently predicting what the game wrote.

## 4. Mutation results — 19 of 20

Every check has a case that could have failed it (hard rule 12). Each mutation is a real
mistake, and most are mistakes the previous exporter actually made:

    CAUGHT   omit the joystick <options> line          (what the old exporter did)
    CAUGHT   write only the first rebind per action
    CAUGHT   drop mo from the device prefixes
    CAUGHT   treat "prefix_ " as empty and skip it
    CAUGHT   LF line endings instead of CRLF
    CAUGHT   sort the categories alphabetically
    CAUGHT   joystick rebinds before keyboard
    CAUGHT   cap buttons at 12
    CAUGHT   swap PID and VID in the GUID
    CAUGHT   omit the mouse from <devices>
    CAUGHT   drop activationMode
    CAUGHT   overwrite instead of appending a second rebind
    CAUGHT   stop reporting one input on several actions
    CAUGHT   accept modifier combinations
    CAUGHT   actionmaps in first-seen order
    CAUGHT   actionmaps alphabetical
    CAUGHT   drop an unknown actionmap
    CAUGHT   write a joystick options line with no VID/PID
    CAUGHT   emit actions in canonical order instead of alphabetical
    SURVIVED sort actions case-insensitively

### The survivor is honest and is now asserted as such

Case-insensitive sorting gives the identical result on both real files. I checked every
actionmap in both: **not one contains a pair of action names that sorts differently under
the two rules.** So the evidence cannot tell them apart, and no test I write can close
that — writing one would be inventing the answer.

The suite now asserts the ambiguity instead. If a future export ever does contain a
distinguishing pair, that check fails and says so, rather than the sort quietly being
wrong for years.

**Two mutations survived the first run and both were real gaps**, which is the point of
doing this: the round trip alone could not test sorting (the input file is already in the
game's order, so no-sorting-at-all reproduces it) and could not test the mouse rule (both
real files contain `mo1_` inputs, so the mouse line appears either way). Fixed by building
from deterministically shuffled input, and by building a keyboard-only profile from
scratch.

## 5. The stick-identity bug is fixed at the root

The live page assigns js1/js2 from `navigator.getGamepads()` array order — the USB
enumeration slot, which carries no information about anything. That is the reported
left/right swap.

The builder now resolves it in the right order of authority:

1. **If a real profile has been imported, its `<options>` GUIDs decide.** The game wrote
   them, so they win over everything. Verified in the browser with the two sticks handed
   to the page in the WRONG order — right stick in slot 0 — and after importing test3cr
   the page still calls the LEFT stick js1, because the file says PID 0201 is instance 1.
2. Otherwise the player's own choice, remembered **per device VID/PID**, so it survives a
   replug and a different USB port.
3. Otherwise a guess from plug order, **and the panel says "guessed from plug order — set
   it"** rather than presenting it as known.

The GUID is built from the VID and PID Chrome reports and matches the real file exactly.
The Product NAME cannot be reproduced — the file says `" VKBsim Gladiator EVO L    "` with
irregular padding and Chrome says `"VKB Gladiator NXT EVO L"`. `build()` reports
`nameSynthesised` so the UI can say so. **Whether the name matters at all is untested.**

## 6. Clearing a default is now a thing the tool can do

202 of 247 rebinds in his first profile are `prefix_ ` — explicit unbinds. **An export is
mostly a record of what the player cleared.** The builder has "Clear keyboard default",
"Clear mouse default" and "Clear stick default" per action, and they are written as real
rebinds. Without this, anything the player wants removed silently stays.

## 7. One input on several actions is allowed, and flagged

13 inputs in test3cr drive more than one action; `js1_x` is both `v_roll` and
`v_strafe_lateral` in the same actionmap, which is how a HOSAS works. The builder permits
it, shows "also on X", and never silently overwrites. A tool that enforced one-input-one-
action would break a normal two-stick setup.

## 8. The DOF page is corrected

`z` was marked UNPROVEN there because it appears nowhere in the shipped defaults. A real
profile uses `js1_z`. Corrected to PROVEN. `rotx`, `roty` and `slider2` are relabelled
**UNATTESTED** rather than UNPROVEN — we have never seen them, which is not the same as
them being rejected, and the wording mattered because I got exactly that inference wrong.

    x  y  z  rotz     PROVEN — in real player profiles
    slider1           PROVEN — in the game's own defaults only
    rotx roty slider2 UNATTESTED — absent from every file we have read

## 9. What Code needs to do

`sc_export2.js` is mine, in `inbox/`. The repo's `testing/_src/sc_export.js` is Code's and
I have not touched it. The move is to replace its contents with the new file, keeping the
`SCX` name if anything already calls it, and to run `roundtrip.js` and `mutate.js` in CI —
they need only node and `@xmldom/xmldom`.

The public surface grew: `build`, `parse`, `reject`, `safeName`, `famOf`, `isUnbind`,
`unbindFor`, `duplicates`, `guidFromVidPid`, `parseGamepadId`, `productString`.
`build(bindings, opts)` now wants `mapOrder` (from `keybinds_site.json`) and either
`devices` (verbatim, when round-tripping) or `joysticks` (VID/PID, when building fresh).

**`verified` is hard-coded false and should stay false until a generated file has loaded.**

## 10. What I checked and what I did not

**Checked:** both real files parsed and rebuilt, byte-compared; the same from shuffled
input; the same again end-to-end through the built HTML page in headless Chromium with two
fake VKB sticks injected in reversed order; 20 mutations; the device panel's three sources
of truth; button-index conversion (browser 16 → SC button17); the unbind token; the
duplicate report; the DOF pills.

**Did NOT check:**
- **No file we generated has been loaded by Star Citizen.** Still the only test that
  settles it, still outstanding.
- Only one machine and one vendor's sticks. Another vendor's `Product` string could be
  shaped differently and nothing here would catch it.
- `rotx`, `roty`, `slider2` remain unattested; modifier combinations remain refused.
- The stuck-device-tab bug on the live page is untouched and still needs the F12 console
  reading from a machine with real sticks — it does not reproduce headless.
