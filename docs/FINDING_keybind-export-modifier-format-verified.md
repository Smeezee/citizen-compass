# FINDING — modifier-key export format confirmed, plus one real export bug found

    from      C3 (Cowork), 2026-08-07
    for       C1 -> Code
    context   Resolves the last open question blocking WO-KEYBIND Product B
              (claude/plan-keybind-newplayer.md §7): how a modified key
              (Ctrl+something) is written in an exported control profile.
              Sleven ran the test in-game and sent two exports.
    method    Two real exports from Advanced Controls Customization ->
              Control Profiles, read directly, not inferred.

---

## 1. Modifier format — CONFIRMED

Rebinding an action to Left/Right Ctrl+K produces:

    <action name="holster">
     <rebind input="kb1_rctrl+k"/>
    </action>

**One `kb1_` prefix covers the whole combination; modifier and key are joined
by `+`.** Not two separate `kb1_`-prefixed tokens. This is what Product B's
export builder needs to generate a valid rebind for a modified key.

## 2. The `<categories>` header block — now understood, not guessed

A second export touching three actionmaps (`spaceship_general`,
`spaceship_movement`, `player_input_optical_tracking`) produced a
`<categories>` block listing only **two** entries: `@ui_CCSpaceFlight` and
`@ui_CGOpticalTracking`. **The categories block tracks UI-level groupings,
not one entry per actionmap** — a single UI category can cover more than one
internal actionmap name. Any code that generates this header needs to map
actionmap -> UI category, not just list whatever actionmap names got
touched.

## 3. A real export defect, found by accident — worth checking before Product B ships

In the same export:

```
<action name="v_pitch">
 <rebind input="js1_ "/>
</action>
```

**That's blank** — `js1_` followed by a trailing space, no actual axis
identifier. Every other rebind in both files is well-formed (`js1_x`,
`js1_button14`, `kb1_down`, `kb1_mouse4`, etc.) — this is the only malformed
entry seen across two real exports.

**Not yet known which side this is on:**
- If the in-game pitch axis is actually working correctly for the player who
  ran the test, then **the export itself has a bug** independent of the
  actual binding — meaning any parser built for Product B must handle a
  blank/malformed `rebind input` value gracefully (skip and flag it, never
  crash or silently treat `js1_` as a valid axis).
- If pitch is *not* working correctly in-game right now, the export is
  accurately reporting a binding that genuinely failed to register.

**Sleven has not yet confirmed which** — the test was run on a housemate's
machine with flight controls, not his own, and the immediate priority was
restoring their working setup rather than diagnosing the blank entry. Worth a
follow-up check next time there's access to that machine, but **this should
not block Product B's parser** — build it to tolerate a malformed `rebind`
value regardless of the eventual answer, since a real player's export could
contain the same thing.

## 4. Bonus, unrelated to the keybind question

The joystick device on that second export identifies as:

    Product="HBP Handbrake  {001F346E-0000-0000-0000-504944564944}"

A real, confirmed USB device string for a handbrake accessory — not one of
the two VKB Gladiators already in `device_facts.json`. Worth folding into
that dataset whenever device-facts work picks back up; not urgent.

## Net effect on Product B

The modifier-key blocker (`claude/plan-keybind-newplayer.md` §7) is resolved
— the format is known. The one new requirement this adds: **the parser must
tolerate a blank/malformed `rebind input` value without failing**, since real
exports can apparently contain one.
