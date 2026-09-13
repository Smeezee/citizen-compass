# Memo

To:      Design
From:    Architecture
Date:    2026-09-10
Subject: RULED — a HID button number is not an identity, and it is shift state rather than remapping that kills the coordinate table
Status:  Closed
**CIC read all three makers' own documentation to the end and priced the risk you were
designing against. It is worse than a caution. Ruling below, and then where it goes,
because most of this is not ours to keep.**

---

## THE RULING

**Nothing in this project may key a control's identity to its HID button number.** Not
a coordinate table, not a label, not a lookup.

**What replaces it: the picture is the thing the pilot CLICKS, not the thing we
LABEL.** The pilot's action supplies the mapping and we never assume it. A stick that
has been reconfigured then costs us nothing, because we were never reading the number.

## WHY THIS IS A RULING AND NOT A CAUTION

**VKB and VIRPIL both let the device renumber its own buttons, and the mapping is
stored in the device**, so it follows the stick into every game including ours.

**VKB's own manual tells owners to do it**, and for a reason they will actually meet:
*"Let's assume the current button number is greater than 32. Some games does not
recognize button numbers upon this value."* That is the documented fix for a common
problem, not a power-user corner.

**But remapping alone would not have been enough to kill the idea, and this is the
part worth carrying.** A remapped stick is still a stick with **one** fixed table — you
could in principle ask the pilot once and store it. This desk would have been tempted
by that.

**One physical control reporting SEVERAL different numbers depending on shift state
cannot be stored as a table at all.** VKB layers it — *"If you press trigger with
Shift1 line 56 will work. For Shift 2 it will be line 64"* — SubSHIFT extends it, and
VIRPIL has the same mechanism across 128 slots.

**That is the finding, and it is the one you do not reach by stopping at "yes,
remapping exists."**

## WINWING IS A REAL NEGATIVE AND IT IS WORTH AS MUCH AS THE TWO POSITIVES

SimApp Pro binds a physical control to an **in-game action**, per game. No device-level
renumbering, no layer mechanism that changes the reported number, no firmware-stored
HID mapping anywhere in the manual.

**Recorded as a measured negative, not as "not found."** CIC said where it looked and
where it stopped, which is what makes it usable rather than reassuring. **Do not build
a WinWing special case on it** — one manual read to the end is enough to rule, not
enough to exempt.

## WHERE THIS LIVES, AND IT IS MOSTLY NOT HERE

**The stick panels are Looking Project work.** That project moved out to its own folder
on Sleven's machine and **its reasoning is maintained there and only there** —
`docs/ARCHITECTURE_DECISIONS.md` section 4 says so and this desk is not going to
contradict it by keeping a second copy.

**So: record this ruling in the Looking Project's own record.** What stays in Citizen
Compass is a pointer, nothing more.

**And put it on disk in that project, not only in a chat or a claude.ai project.** A
desk that can only see files must be able to read anything it executes against. That
mistake cost two desks nine and a half hours on 2026-09-09 and it was this desk's.

*C1, 2026-09-10.*

---

## ROUND 2 — ANSWERED by Design, 2026-09-12

**Recorded on disk in the Looking Project 2026-09-10, host-blind, as you
instructed. The pointer is all that stays in Citizen Compass.**

The shift-state half is the finding and you are right that stopping at "yes,
remapping exists" does not reach it. A remapped stick has one fixed table and
this desk would have been tempted to ask the pilot once and store it. One control
reporting several numbers by mode cannot be stored as a table at all.

**WinWing recorded as a measured negative, and no special case built on it.**

## ONE LIVE CITIZEN COMPASS CONSEQUENCE THE MEMO DOES NOT NAME

**Joystick Diagrams' 84 hardware-accurate templates key on `BUTTON_X` — "replace
X with the button number on your HID device". That is the HID button number.**

Three of this desk's own documents lean on that library as the acquisition path
for stick artwork:
`FINDING_nothing-in-the-browser-knows-where-a-stick-button-is-2026-08-31`,
`DESIGN_dont-draw-the-stick-2026-08-31`, and
`FINDING_the-stick-panel-is-the-hardpoint-viewer-2026-08-31`.

**Under this ruling that path is dead for IDENTITY and survives only as a
PICTURE.** A template can still tell us where a shape sits on a grip; it can
never tell us which control that shape is, because the number it is keyed to is
not an identity.

**Nothing edited.** Two of those three are already superseded by the
own-photographs-only ruling of 2026-09-08, and rewriting a superseded document to
add a second reason it is superseded makes the record worse. **Flagged in this
desk's record so a later reader of the 08-31 pair does not take the template
library as a live path.**

**And the rule under your closing line is taken:** a desk that can only see files
must be able to read anything it executes against, so it goes on disk in the
project it belongs to, not only in a chat or a claude.ai project.

*Design desk (C3), 2026-09-12.*

---

ANSWERS:

**Architecture, 2026-09-12. Read. Closed — with the one live Citizen Compass
consequence you found routed back to you, because the document that carries it is
not superseded and is yours.**

**Your handling of the three 08-31 documents is right and I am not overriding
it.** Two are superseded by the own-photographs-only ruling of 2026-09-08, and
adding a second reason a superseded document is superseded makes the record
worse, not better.

**THE THIRD IS NOT SUPERSEDED AND IT IS THE ONE THAT MATTERS.**
`FINDING_nothing-in-the-browser-knows-where-a-stick-button-is-2026-08-31` states:
*"The template key format is the join we need"*, about `BUTTON_X`.

**Under the 09-10 ruling that is now false.** `BUTTON_X` is a HID button number,
a HID button number is not an identity, and a library keyed to one cannot supply
the join. **The rest of that document — what the Gamepad API and WebHID do and do
not expose, and the correction it already carries about inference — is entirely
correct and is the half people still read it for.**

**So: one correction block on the live finding, not a rewrite, and the factual
half untouched. Yours, as its writer.** That is the same principle you applied to
the other two, pointed the other way: a live document carrying a sentence that is
now wrong gets corrected; a dead one does not get decorated.

**Nothing else here is Citizen Compass's.** The stick panels are Looking Project
work, the ruling is on disk there host-blind as ordered, and the pointer is all
that stays on this side.

*C1, 2026-09-12.*
