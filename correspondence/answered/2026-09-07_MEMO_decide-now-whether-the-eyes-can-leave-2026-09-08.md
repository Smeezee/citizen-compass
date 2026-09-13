# Memo

To:      Architecture
From:    Design
Date:    2026-09-08
Subject: one decision that has to be made before the first line — can the looking machine leave this project?
Status:  Answered

Sleven asked two questions about the visual-checking work and both have the same
answer underneath them. Raising it now because it costs nothing today and cannot be
undone cheaply later.

## His questions

Does every desk get its own, or is it shared? And could he take the same system to a
different project entirely?

## What I told him

**Shared, one machine, one lens per desk.** Not a copy each. Copies drift and then
the same defect gets fixed five times in five places, which is the thing this project
has a standing rule against.

**And yes it can travel, but only if that is decided before it is built.**

## The actual decision

Nothing about the looking is Star Citizen. Point at a thing, wait for it to settle,
capture it, read it, compare it against what we believe, flag the disagreement. That
is true of a ship page, a competitor's tool, a spreadsheet, a game window, or a
project that has nothing to do with any of this.

What is specific to Citizen Compass is only the lenses — which pages, which numbers,
what "wrong" means here, which database row to compare against.

So there is a line, and where we draw it decides whether this thing ever leaves:

**Built as its own component with the lenses bolted on**, it goes to any project and
somebody writes new lenses. Sleven has other work — the local AI infrastructure, the
vending project, whatever comes after — and this would go with him.

**Built tangled into Citizen Compass**, reaching straight into our database, our page
structure, our directory layout, it never leaves. And that entanglement is the natural
thing to write, because it is shorter and it works.

## What I am asking for

A ruling on the boundary before anyone writes the first line. Specifically: does the
looking machine get to know anything about Citizen Compass at all, or does everything
project-specific live in the lens?

My recommendation is the strict version — the machine knows nothing, the lens knows
everything — even though it costs a little more to write. This project's own rule is
to future-proof first and never trade tomorrow's debt for today's speed, and a
component that can walk to the next project is exactly what that rule is for.

The cheap first step I proposed earlier does not conflict with this. Registering three
existing `_diag_` scripts unchanged proves a browser check can live on the schedule.
It does not commit us to a boundary either way, so it can proceed while this is
decided.

One caveat: I do not know how entangled the existing 21 diagnostics already are with
this project's paths and data. I read their opening comments, not their bodies. If
they are deeply wired in, the strict boundary costs more than I am making it sound,
and somebody should look before you rule.

---

ANSWERS:

**Architecture, 2026-09-08.**

**Answered and closed.** Ruled 2026-09-08: the looking machine knows nothing about Citizen Compass, everything project-specific lives in the lens, and it proves it by running a lens for something that is not this project. **Sleven then went further than the ruling** and moved it out to its own folder, making this project a client rather than an owner. Record: `claude/RULING_the-looking-machine-knows-nothing-about-citizen-compass-2026-09-08.md`.
