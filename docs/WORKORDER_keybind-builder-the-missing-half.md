# WORK ORDER — the keybind page's missing half. The exporter already exists, is tested, and is wired to nothing.

    from      C3 (Cowork), 2026-08-08
    for       C1 (→ Code)
    ask       Sleven, testing the live site: "there's no way to actually help somebody set up
              their key binds for what's in Star Citizen. I can see JS one button push, JS two,
              three, all the axes. But how do I set it up to put it into Star Citizen?"

---

## 0. The answer to the question, first

**Star Citizen loads a mapping XML file. The site should generate it.** That is the bridge
between "I know my button is index 3" and "my stick is set up in game."

**And most of it is already built.** Three of the four pieces exist:

    settled   the file format             claude/finding-sc-mapping-export-format.md
    BUILT     the exporter                testing/_src/sc_export.js  (6.4 KB, SCX.build)
    BUILT     23 tests with negatives      testing/_src/test_sc_export.js
    BUILT     button detection             testing/_src/device_engine.js (deployed, working)
    MISSING   anything connecting them     <- this is the whole job

**`sc_export.js` is an orphan.** Grepped the source tree and the deploy: it is referenced by
**nothing** — no page, no build step, not present in `_deploy/`. It was written 2026-08-06 and
has sat unused since. This is the third orphan-file instance on this project (after
`kb_overlay.inc.html` and the viewer material in `_layer.src.html`), and the reason Sleven
cannot find the feature is that it was never attached to a page.

**So this is a wiring job plus one screen, not a build-from-scratch.**

## 1. Why this is not a convenience feature

From the project's own reading of the game's shipped profile:

> `button1 … button12`, `x`, `y`, `rotz`, `slider1`, `hat1_up/down/left/right`
> — *that is the entirety of out-of-box HOTAS support.*

**Star Citizen ships bindings for twelve buttons, one hat and one slider.** Sleven's own VKB
Gladiator NXT EVO has 13 controls; the WinWing Ursa Minor has 44. Anyone with a modern stick
**cannot use most of their hardware** without hand-writing XML. That is the actual problem the
page exists to solve, and right now the page stops one step short of solving it.

## 2. STOP — the test that has to come before the build

**The joystick export path has never been confirmed to load in the game.** From
`finding-sc-mapping-export-format.md`, recorded honestly at the time:

> Whether a joystick needs its DirectInput `Product` GUID in an `<options type="joystick">`
> line, or binds by instance order. His exports were keyboard-only.
> …Joystick bindings **are emitted**, the `<options type="joystick">` line is **omitted**, and
> the result is returned with `verified:false`.

**The one thing this whole feature is for is the one thing nobody has tested.** If the game
silently declines a joystick mapping without that `<options>` line, every file the builder
produces will fail the same way — and it fails *silently*, which is the worst shape: nothing
errors, the binds just are not there, and the player blames their stick.

**Ten-minute test, and it decides the design:**

1. Bind two or three joystick controls in game by hand. Export the profile from the game.
2. Read the export: is there an `<options type="joystick" ...>` line, and does it carry a
   Product GUID?
3. Generate an equivalent file with `SCX.build()`, drop it in
   `USER\Client\0\Controls\Mappings\` **before launch**, load it via Options → Keybindings →
   Advanced Controls → Control Profiles (or console `pp_RebindKeys <filename>`), and confirm
   the binds actually appear.

**Nothing else in this order should be built until step 3 comes back green.** If it fails,
the fix is probably just emitting the `<options type="joystick">` line with the device's real
GUID — which the device panel can already read — but that is a guess until tested.

**Also unresolved and worth folding into the same session:** how a modifier combination is
written. `sc_export.js` currently **refuses** combos outright rather than guessing. Bind
something to a joystick button + modifier, export, and read it. That turns a refusal into a
feature.

## 3. What to build, once the test passes

**A binding builder screen.** Three columns, no wizard:

**Left — pick an action.** The data is already there: 691 labelled actions across six modes in
`keybinds_site.json`, plus 238 plain-English descriptions already written and shipped
(`keybind_descriptions_draft.json`). Filter by mode, search by name. **Join on `(action, map)`,
never `action` alone** — `v_yaw_left` means different things under `spaceship_movement` and
`vehicle_driver`, which the descriptions work already caught once.

**Middle — press the control you want it on.** `device_engine.js` already detects this and
already shows the raw index. **The conversion is where the bug will be: Star Citizen numbers
buttons from 1, the browser Gamepad API from 0.** That off-by-one is documented and must be
applied exactly once, in one place, with a test that fails if it is applied twice or not at
all.

**Right — the pending binding list**, with a Remove on each, and an Export button.

**Export** calls `SCX.build()` and downloads the XML. Alongside it, plain instructions: where
the file goes, that it must be in place **before** the game launches, and both load routes.
The console route matters — it bypasses the UI's profile-slot limit.

**Import** should also exist: read a mapping XML back in so someone can adjust an existing
profile rather than starting over. The parser is the same schema, read instead of written.

## 4. Design rules that follow from what is already proven

- **Emit only what the user changed.** Confirmed from Sleven's own exports: a real export
  carries only rebinds, never all 1,103 actions. Do not "helpfully" write out defaults.
- **Mouse rides the keyboard prefix** — `kb1_mouse4`, never `ms1_`.
- **Never invent an input name.** If a control has no name in SC's vocabulary
  (`button1..12`, `x`, `y`, `rotz`, `slider1`, `hat1_*`), say so and refuse the binding rather
  than guessing a name the game will ignore. The device panel's existing honesty rule — show
  the raw index, mark guesses — carries over unchanged.
- **A refused binding is listed, never silently dropped.** `sc_export.js` already returns a
  `refused` array; the UI must show it. A binding that vanishes without comment is the same
  silent-failure class this project keeps logging.
- **`verified:false` must reach the screen.** If the file is generated by an unproven path,
  the person downloading it needs to know before they wonder why their stick does nothing.

## 5. Acceptance

- A generated joystick file **loads in the running game** and the binds appear. Nothing else
  counts; this is the only test that matters.
- Round-trip: export a profile, import it back, get the same bindings.
- The 0-vs-1 index conversion has a test that fails if it is applied twice.
- A refused binding appears in the UI with a reason.
- `sc_export.js` is reachable from the built page — check `_deploy/`, not the source tree,
  because `build_deploy.py` substitutes its own copies of some blocks and patching only the
  source layer can silently do nothing.

## 6. What I checked and what I did not

**Checked:** `sc_export.js` and `test_sc_export.js` exist and are referenced by nothing in
`testing/_src/` or `testing/_deploy/`; `device_engine.js` is present and carries SC's joystick
vocabulary; `defaultProfile.plain.xml`, `keybinds_site.json`,
`keybind_descriptions_draft.json` and `keybind_troubleshooting.json` are all on disk; the file
format is settled in `claude/finding-sc-mapping-export-format.md` from Sleven's own exports.

**Did NOT check:**
- **I did not read `sc_export.js` in full** — only its header, public surface and stated
  guarantees. Its correctness is asserted by its 23 tests, which I also did not run.
- **I did not run the game or load any file.** Every claim about what Star Citizen accepts
  comes from the existing finding, which came from Sleven's own exports — not from me.
- Did not check whether `keybinds.src.html` (the second standalone copy of the keybind page,
  already flagged as a rule-14 violation) would also need this, or should be deleted first.
  **That decision should come before the wiring, not after**, or the work gets done twice.
- Did not touch any code, the build, or the site.
