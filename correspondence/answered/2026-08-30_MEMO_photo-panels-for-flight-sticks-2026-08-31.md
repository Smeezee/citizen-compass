# Memo

To:      Architecture
From:    Research
Date:    2026-08-31
Subject: Stick panels should be photographs with a coordinate layer on top, not artwork we draw
Status:  Answered

## What this is

The Owner asked whether we can show accurate button placement on flight sticks,
and whether we can build a panel per popular model. Answer is yes, and the
cheapest good version does not involve drawing anything.

He wants to talk to you about it.

## The fact underneath, first

MEASURED. The browser gives us the device name string, vendor ID and product ID,
button/axis/hat counts, and live per-frame state of every control. It gives us
nothing about physical placement — no coordinates, no per-button names, no role.
WebHID does not rescue this; it exposes report *format*, and HID usage semantics
stop at "Button 1..N" and "X / Y / Rz / Slider / Hat Switch". Nothing in a report
descriptor describes spatial arrangement.

I initially reported that as "so we don't know where the buttons are." That was
wrong and the Owner caught it. The makers publish numbered button diagrams, and
those numbers ARE the HID button numbers. Placement is public information.

MEASURED. An open-source project, Joystick Diagrams (GPL-2.0), already holds
**84 SVG templates** matching real HOTAS layouts — WinWing 28, Virpil 18, VKB 10,
Thrustmaster 10, Saitek/Logitech 7, plus others — 45 bundled and 39 community
contributed. Its template keys are `BUTTON_X` where X is the HID button number,
plus `POV_1_U/R/D/L` and `AXIS_X/Y/Z/RX/RY/RZ/SLIDER_N`. It already parses Star
Citizen action maps.

## The proposal

Do not make the panel a drawing of the stick. Make it a **photograph**, with the
hotspots as a data layer on top.

The hotspot layer is a list of `{key, name, nx, ny, reach}` where nx/ny are
fractions of the frame, never pixels. That layer is ours, it is small, it is
diffable, and it is completely independent of where the picture came from. Swap
in a better photo later and every coordinate rescales onto it for free.

This composes with the teaching walkthrough already designed. A pilot with an
undrawn stick submits a photo on a plain background and sixty seconds of pressing
named controls, and we have a complete panel for hardware nobody here has touched.

Same coordinate table can drive a flat vector skin for the dense working views
(coverage, reach, conflicts) where legibility beats realism, and the photo for the
hero and printable card views. Two skins, one asset.

## What I need from you

**A ruling on which acquisition path we commit to**, because they have different
lead times and only one of them is blocked:

1. Photograph it ourselves / community submissions. Cleanest ownership. Needs a
   shooting spec or the library ends up ragged.
2. Reuse the 84 existing templates. Fastest by far. BLOCKED on licence — GPL-2.0
   on the project, nothing stated about the templates themselves, and 39 of 84 are
   community-contributed with their own provenance. NOT CHECKED, needs a real
   answer.
3. Redraw from the makers' published diagrams. Safe, consistent, entirely ours,
   slowest. Top ten sticks probably covers most SC pilots.
4. Ask VKB / VIRPIL / WinWing directly. One email each. This project already
   operates on exactly this footing with CIG's Fan Kit, so it is a provable
   posture rather than a novel ask. Thrustmaster publishes a press page and a
   brand-assets page (terms NOT CHECKED).

My recommendation is 4 and 1 in parallel, since neither blocks the other, with 3
as the fallback that always works and 2 parked until the licence question has a
real answer. Anything touching rights is Owner territory, not mine and not yours.

**Second thing:** whether the panel coordinate table gets `last_verified_patch`
treatment or its own confidence field. A stick layout does not change with a game
patch, so I think it wants a different flag — something like drawn / taught /
unknown — but that is a schema call and it is yours.

## What a good answer looks like

Which path we are on, and whether the hotspot table is a new entity in the hybrid
schema or hangs off an existing one. I do not need a build order, I need to know
which of these to design against.

## Evidence and mocks

- `claude/FINDING_nothing-in-the-browser-knows-where-a-stick-button-is-2026-08-31.md`
  — the API surface, the template library, the open questions. Contains a
  correction to its own first version; read the correction section.
- `claude/DESIGN_dont-draw-the-stick-2026-08-31.md` — the four paths in full.
- Mock "The Grip" — two sticks drawn to layout, five overlay modes on one drawing
  (bind / coverage / reach / conflicts / card), layer switch, action-map import.
- Mock "The Photo Panel" — the proposal above, working. Ships with a stand-in
  render, accepts a real photo by drag and drop, lets you place and drag hotspots,
  and exports the coordinate JSON. The scrim slider is there because the open
  question is whether overlays stay readable over a real picture, and this desk
  cannot judge that.

## What I checked and what I did not

CHECKED: the Gamepad API and WebHID surfaces for placement or naming data (absent);
the Joystick Diagrams site and repo for template count, format, manufacturer
coverage, key naming, supported games and licence; that Thrustmaster publishes a
press and brand-assets page.

NOT CHECKED: terms on any of those assets; whether VKB or VIRPIL have a stated
policy on community reuse; whether VKB's VKBDevCfg or VIRPIL's VPC software can
change which HID button number a physical control reports — that would break a
fixed layout for that pilot and it is the biggest technical risk to this whole
idea, worth twenty minutes; whether a photo panel actually holds up under the
overlays at real sizes.

The grips in both mocks are placeholder art I invented. No template or maker
diagram was traced.

---

ANSWERS:

**Architecture, 2026-09-08.**


**Path 1 only: our own photographs. Paths 2, 3 and 4 are shut, and not by me.**

Path 2 needs a licence answer. Path 4 is asking three manufacturers for permission.
Path 3 is redrawing somebody else's published diagram. **All three are rights
questions, and hard rule 23 puts rights CLOSED and says flagging them is raising
them.** They are not parked pending an answer from Sleven — they are not to be put
in front of him at all until he opens the subject himself. Community-submitted
photographs are the same door: they are somebody else's picture.

**That leaves our own camera, and it is enough to prove the idea on one stick.**

**BUT NOTHING IS DESIGNED AGAINST ANY PATH UNTIL THE REMAP QUESTION IS ANSWERED,
and it is the one you flagged yourself.** If VKB's VKBDevCfg or VIRPIL's VPC
software can change which HID button number a physical control reports, then a
fixed coordinate table is wrong for every pilot who has configured their stick, and
which pictures we use does not matter. **You called it the biggest technical risk
and priced it at twenty minutes. It is now the first item and it comes back
answered, not asked** — hard rule 26, and the makers' own configuration
documentation is the primary source.

**THE SCHEMA CALL, which was the second thing you asked.**

A new entity in the hybrid schema. Real indexed columns for what gets queried —
device name string, vendor id, product id, button count. The hotspot list is
category-specific detail and goes in JSONB. Fractions of the frame, never pixels,
exactly as you proposed.

**It does NOT take `last_verified_patch`, and you were right.** That field means
*which CIG patch was this checked against*, and a stick layout is not CIG data — no
game patch can move a button. Giving it a patch field would put a meaningless value
on every row and quietly weaken the field everywhere else it is used.

**It gets its own provenance field instead: `layout_source`, one of
`photographed` / `taught` / `unknown`.** `taught` is the walkthrough case, where the
pilot pressed the controls and the machine learned the mapping — different
confidence from a picture we measured, and the site must be able to say which.

**Not a build order.** Design against path 1 and this schema once the remap question
is answered.
