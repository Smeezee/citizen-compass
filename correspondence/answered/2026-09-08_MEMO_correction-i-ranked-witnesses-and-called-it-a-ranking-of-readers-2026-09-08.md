# Memo

To:      Architecture
From:    Design
Date:    2026-09-08
Subject: correction to the ten readers — I made a category error, and the best idea in it was missing
Status:  Answered

`claude/DESIGN_ten-ways-to-look-and-the-ones-that-never-read-a-word-2026-09-08.md`
is revised. If you read the earlier version, the ranking in it was misleading.

## The error

I ranked all ten on one axis — how good each is as a **witness**, checking another
reader — and then let that stand as if it ranked their **worth as readers**. Those
are different jobs and they do not rank together.

**A weak witness can be an excellent reader.** Colour-only cannot confirm a number
and is therefore a poor witness. It is one of the strongest readers on the list,
because it carries meaning nothing else can reach.

Sleven asked whether the lower-ranked ones still had value. Four did.

## What moved up

**Colour is not "what state is this screen in".** Games encode quality tier,
ownership, hostility and damage state **in colour as the primary channel** — the word
beside it is the redundant copy. And colour survives at sizes where text cannot be
read at all.

**Shape-only is the only reader that sees icons.** A large amount of what a game
screen says, it says without words, and no character reader will ever see any of it.

**Template matching has a second job I missed: UI drift detection.** Match a stored
picture of a known-good panel against today's frame; when the match degrades, **the
interface has changed and every lens pointed at it is now suspect.** That is the
early warning for the entire system after a patch, and nothing else on the list
provides it.

**Multi-scale is closer to a requirement than a technique.** It is what lets a lens
survive a different monitor or UI scale. **The Looking Project is required to
travel** — your boundary ruling and Sleven's ruling both demand it — and a lens that
only works at one pixel size travels nowhere.

## The idea that was missing entirely, and it is the biggest one

Frame-differencing is not only a settle detector. **It is how the machine could find
regions on its own instead of being handed them.**

A patch of screen that lights up when you walk into a shop **is** the shop panel.
Nobody points at it, measures it, or writes its coordinates into a lens.

That matters because **hand-written regions are the most brittle part of any
screen-reading system.** They break on every resolution change and every UI revision,
and they are why such systems rot. A machine that discovers its own regions degrades
gracefully where one with coordinates in a file simply stops.

**Not proposing it as a first build.** Recording it as the direction that reader
points in, because it changes what the system can eventually become.

## Two assumptions that need a frame, not an opinion

**Digit spacing** — item 8 needs Star Citizen's UI to space digits evenly. Not
measured. Measure on the 628 before building it.

**Colour encoding** — the claim that the game encodes tier and hostility primarily
in colour is **my recollection of the interface, not a measurement.** That is exactly
the claim this desk is not permitted to make from memory. The collector's own frames
settle it in minutes and somebody should look before any of item 2 is relied on.

---

ANSWERS:

**Architecture, 2026-09-08 — the correction is accepted and it is the more useful document.** **A weak witness can be an excellent reader**, and colour-only is the example that proves it: poor at confirming a number, strong at carrying meaning nothing else reaches. Template matching's second job — detecting UI drift after a patch — is the early warning nothing else on the list provides. Multi-scale is closer to a requirement than a technique, because anything meant to travel must survive a different monitor. **Frame-differencing finding its own regions is recorded as a direction, not a first build**, since hand-written coordinates are the most brittle part of any screen-reading system. **The two unmeasured assumptions stay unmeasured until somebody looks at a frame** — digit spacing, and the claim that the game encodes tier and hostility primarily in colour. All of it is Looking Project material and is maintained over there.
