# I have now seen the game's own keybinding screen

**C3 · 2026-09-07 · closes a gap the survey doc admitted to**
**On disk 2026-09-12. It existed only in the claude.ai project until then.**

`CIC_survey-keybind-tools-and-the-gap-2026-09-06.md` ended with an admission: I had
never seen Star Citizen's own keybinding menu, so every comparison in it was against
third-party tools only. Sleven sent a screenshot of it. This closes that gap.

## What the screen is

Options Menu → Keybindings. A full keyboard drawn on screen, plus the numpad and arrow
cluster, plus a line drawing of a mouse at the right. Two pickers sit at the bottom
right: the category (**Flight**) and the device (**Keyboard / Mouse**). A **Back**
button and an **Advanced Controls Customization** button sit at the bottom left.

Below the board is a legend of about eighteen two-letter codes — SC scan mode, MG mining
mode, SA salvage mode, SFH salvage focus heads, IM interaction mode, LN landing mode,
TU turret, QT quantum travel active, AD advanced camera mode, AC arena commander, ML
missile mode, and M1/M2/M3 for the three modifiers — plus `*` for hold and `**` for
double tap.

## What it actually does, and where it hurts

**Every binding on a key is printed on that key at once.** The R key carries four lines.
The B key carries three. The text is roughly six pixels tall. On a 1080p screen it is not
readable — it is a texture that tells you *a key is busy*, not *what the key does*.

**The mode is a prefix letter, not a colour.** To know that `SA Fracture` only applies in
salvage mode you read the two letters, then look down at the legend to decode them. The
colours that are present are tied to the code, not to a category you can hold in your
head. Our board answers this with a mode filter at the top — pick Flight and only flight
bindings are on the board at all.

**Modifier keys are outlined in their own colour.** Left Shift is red (Modifier 2), Left
Alt is orange (Modifier 1), Right Alt is pink (Modifier 3), and every binding that uses
one is prefixed M1/M2/M3 on the key. This is the one idea on the screen worth stealing:
the modifier key itself is visibly the source of the colour, so you can trace a binding
back to the key that unlocks it. Our board has +Shift / +Alt / +Ctrl as tabs, which is
clearer to read but loses that visual tie back to the physical modifier key.

**Unbound keys are dark and empty, bound keys are white-outlined.** One flat state for
"busy". No sense of how busy, and no way to ask for free keys.

**There is no search.** Nothing on the screen finds an action by name. If you want to know
what "Decoupled Toggle" is bound to you hunt for it with your eyes. This is the largest
single gap and the strongest argument for the search box we already have.

**Rebinding lives behind another door.** Advanced Controls Customization is a separate
screen. The board itself is a reference, not an editor — which is, notably, the same
conclusion the survey doc reached about what our page should be.

## What this changes about our page

Nothing that was already decided is overturned. Three things are confirmed:

The mode filter is right, because their alternative — printing every mode on every key —
is the thing that makes their screen unreadable. The search box is right, because they
have nothing like it. The "one binding readable at a time" idea is right, because their
screen proves that showing all of them means showing none of them.

One thing is worth adding: their modifier colouring. When the +Shift tab is active, the
two Shift keys on our board should light in the tab's own colour, so the physical key you
are holding is visibly the reason the board changed. That is a small addition and it is
theirs, not mine.

## Checked and not checked

**Checked:** every claim above is read directly off the screenshot Sleven sent — a Flight,
Keyboard/Mouse view, taken at Levski, game build `sc-alpha-4100-1254-5760`.

**Not checked:** the Gamepad and Joystick device views of the same screen — I have not
seen either, so I still do not know how the game draws a stick or a pad. The Advanced
Controls Customization screen — not seen. Whether the screen behaves differently at a
resolution other than 1920×1080. Whether any of it is navigable by controller.
