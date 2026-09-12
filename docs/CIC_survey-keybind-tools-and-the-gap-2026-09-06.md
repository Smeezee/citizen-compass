# SURVEY — four people already build a keybind editor. The gap is not editing.

    from    C3, 2026-09-06
    why     Sleven: "I don't wanna do something that somebody else is already
            doing. I wanna do it different and better."
    status  Survey plus a design turn. Nothing built, nothing authorised.
    reads   docs/DESIGN_the-easiest-keybinding-setup-2026-09-06.md
    on disk 2026-09-12. Existed only in the claude.ai project until then.

---

## 1. WHAT ALREADY EXISTS — MEASURED, fetched 2026-09-06

**Star Binder** — `starbinder.space`, browser, free.
Visual keyboard laid out by device type (mouse/keyboard, controller, joystick).
Double-click to rebind, hold to clear, ctrl+alt-click to reset. Search and
filter by keyword and category. **A "Finder" mode that identifies which action
is bound to an input you press.** Custom bind strings, several activation modes,
XML import and export, device index management for multiple controllers.
Confirmed working with the VKB Gladiator NXT EVO. Chromium only; Firefox has
issues; some inputs (Mouse4/5, F23) do not work; the custom bind field has no
validation.

**Boxxy Binder** — `github.com/BoxximusPrime/SC-Binding-Utility`, Windows
desktop, Tauri + Rust, DirectInput.
Binding manager across all the major categories with filtering by device type
including button boxes. **A visual device viewer that stacks several templates
at once**, with adjustable font and button sizes. **A template editor** — build
your own device layout, upload an image, mirror it, save it as a profile. **An
input debugger** that watches the device live to identify unknown buttons.
**Auto-save that deploys straight into the game in near-real-time using console
commands, across several installs.** Also backs up character appearance.
Community templates shared on Discord.

**HCS Keybind Editor** — free, plus a premium beta at £9.99.
Import your binds from the game, search commands by name, edit keypresses and
combinations, configure joystick axes, buttons, hats and sliders, gamepad and
mouse. Backup and restore. Premium adds merging and recommended templates.
Standalone; does not need VoiceAttack.

**Joystick Diagrams** — GPL-2.0, covered in an earlier finding.
84 hardware-accurate SVG templates, reads Star Citizen action maps, produces a
printable reference card of what you fly with. **Read-only — it documents,
it does not edit.**

> **2026-09-12: the template library is a PICTURE source only.** Its keys are HID
> button numbers, and Architecture ruled 2026-09-10 that nothing in this project
> may key a control's identity to one. See
> `docs/FINDING_nothing-in-the-browser-knows-where-a-stick-button-is-2026-08-31.md`.

**Black Racoon Foundry** — a button visualiser. NOT READ; listed for completeness.

## 2. THE HONEST PART — my "one idea" is already built

The plan filed this morning rested on *"you never look up a key, you press it."*

**That is Star Binder's Finder mode.** It exists, it is free, it works in a
browser. The idea was not wrong, it was just not new, and I did not check before
writing it down.

**And Boxxy Binder is ahead of my plan in two places I had not thought of:**
deploying into the game live rather than exporting a file, and letting a user
build a template for hardware nobody has drawn.

**So the plan's §2 is withdrawn as a differentiator.** It stays as a
requirement — the tool must do it, because the good ones do — but it cannot be
the reason to build.

## 3. WHAT ALL FIVE HAVE IN COMMON, AND IT IS THE OPENING

**Every one of them is an EDITOR.** You arrive knowing what you want to change,
you change it, you export it. They are organised around the device and the
action list, and they all assume the user already knows what they want.

**Not one of them has an opinion.**

They will let you leave Eject next to Boost. They will let you bind a
countermeasure to a base button you have to look down for. They will not tell
you that thirty of your binds are for a ship you do not own. They will not tell
you what `IFCS - Proximity Assist - Toggle` actually does. **They edit. They do
not judge, explain, or teach.**

## 4. FIVE THINGS NOBODY DOES, AND WHY WE COULD

**A. Judge the layout, not just record it.**
Combat actions belong where your hand already is. That is a measurable property
once you know where the buttons physically are — which is the whole point of the
stick placement work already done. *"Countermeasure: flare is on a base button
you have to look down for"* is a sentence no existing tool can produce.

**B. Bind for the ship you actually fly.**
**This is the unfair advantage and it is sitting unused.** Citizen Compass holds
every ship's real components. A Vulture has a salvage head. A Prospector has a
mining laser. A Gladius has neither. So: *"you fly a Vulture — these nine
actions matter for salvage and four of them are unbound,"* and equally, *"you
have thirty-one mining binds and no mining ship."* **No other tool has the ship
database. It is the one thing they cannot copy quickly.**

**C. Say what the action does.**
691 action names, most of them CIG file shorthand. The project already built a
hover glossary and already holds CIG's own 90,121 label strings. **Plain English
on every action is data we hold and nobody else has assembled.**

**D. Learn from what you actually press.**
Later, and only on Sleven's machine: the collector already records which buttons
he uses. *"You have never once pressed thirty-four of your bound keys. You reach
for these twelve constantly, and three of them are awkward."* **Nothing else in
this space can do this at all.**

**E. Start from a set that means something.**
Everyone hands you the defaults and a blank canvas. Nobody says *"here are the
forty things that matter, in the order you will need them, and here is a sane
home for each."* That list is opinion, it is hand-written, and it is the
difference between a tool and a spreadsheet.

## 5. THE TURN — stop building an editor, build a check-up

**The others are editors. Ours should be a coach.**

Editing is table stakes and four people already do it, two of them well and one
of them free in a browser. **Building a fifth editor is the mistake this project
has a standing rule against.**

**So invert the front door.** You do not arrive at a blank keyboard. You arrive
by handing it what you already fly with:

    IMPORT YOUR MAP        the file the game already wrote
      -> here is what you fly with, drawn on your own hardware
      -> here is what is WRONG with it, ranked
           3 combat actions you cannot reach without looking
           2 real conflicts, same mode, same layer
           31 binds for a ship you do not own
           9 things your Vulture needs that are not bound at all
           17 actions bound to keys you have never pressed
      -> fix any line, on the board, in place
      -> put it back in the game

**Editing is still there — it is how you fix a line.** But it is the second
thing you do, not the first, and it is aimed at a problem the tool found rather
than at a list you have to search.

**That is a different product in the same space**, it uses three assets nobody
else has, and it does not require beating Star Binder at the thing Star Binder
is already good at.

## 6. WHAT THIS CHANGES IN THE EARLIER PLAN

**Kept:** one board that is your hardware; binding by pressing; showing the cost
before it is paid; same-key-different-mode is not a conflict; a record of what
you changed; per-line rebinding; the pad's layer problem; axes and hats needing
their own treatment.

**Withdrawn as a differentiator:** press-to-find. It is Star Binder's Finder.

**Added, and these are the reasons to build at all:** the reach check, the
ship-aware audit, plain English on every action, and later the used-versus-
unused pass.

**Added from the competition, because they are simply better ideas:** deploy
into the game rather than export a file (Boxxy), and let a user build a layout
for hardware nobody drew (Boxxy's template editor, which is also the answer to
the stick-artwork problem from the earlier findings).

## 7. WHAT I COULD NOT DO

**I have not seen Star Citizen's own keybinding menu.** I cannot run the game,
and the wiki page on Controls lists default binds without documenting the
interface. Every claim in §3 about the game's own menu being the thing to beat
is therefore **NOT CHECKED** — I know the tools, not the baseline.

> **CLOSED 2026-09-07.** Sleven sent a screenshot.
> `docs/FINDING_i-have-now-seen-the-games-own-keybinding-screen-2026-09-07.md`.

**Also not done:** Black Racoon's visualiser was found and not read. None of
these tools was actually used — everything above is read off their own pages,
which is what they claim rather than what they deliver.

---

**Survey and design turn. Not a work order. Nothing authorised.**

Sources: [Star Binder](https://starbinder.space/) ·
[Boxxy Binder](https://github.com/BoxximusPrime/SC-Binding-Utility) ·
[HCS Keybind Editor](https://www.hcsvoicepacks.com/products/star-citizen-keybind-editor-premium-joystick-controller-support) ·
[Joystick Diagrams](https://www.joystick-diagrams.com/) ·
[Black Racoon Foundry](https://www.blackracoon.net/?page=buttonsVisualizer)
