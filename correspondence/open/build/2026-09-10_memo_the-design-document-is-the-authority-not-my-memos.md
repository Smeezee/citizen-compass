# Memo

To:      Build
From:    Owner
Date:    2026-09-10
Subject: the design document is the authority for the card, not my memos — and one rule in mine is wrong
Status:  Open

**Stop building the card against my memos. Build it against
`claude/DESIGN_the-doorbell-the-job-number-and-the-punch-card-2026-09-10.md`.**

I have now sent you three versions of the same rules in one night and the newest
one carries a defect. **That is a second source of truth and I made it. Architecture
owns this design; I do not.**

## THE RULE THAT IS WRONG

My last memo said the punch count and the stamp count must always be **equal**, and
that any gap is a flag.

**That would go red on every live job.** The watcher punches when it files the
letter to a desk. The desk stamps when it passes it back. **So while a desk is
holding the file, punches are one ahead of stamps, correctly.**

**Architecture caught it. The rule is `punches − stamps` is 0 or 1. Anything else
is the flag.**

Everything else in my last memo stands — four punches then freeze, the job number
in the filename, one file never remade, stamps machine-readable and counted per
desk, forty-five minutes of silence, only my stamp resets the counter.

## AND ONE THING ARCHITECTURE READ BETTER THAN I DID

**The daily wake ceiling is not a backstop. It is the primary defence.** A desk
that answers with a NEW file starts a fresh card, so the four-punch limit never
fires on that path — **the ceiling is the only thing that catches it.** Treat it
with that weight when you build it.

**I have not set the number yet.** It and the untouched-job age rule are in my tray
as a job of their own. **Do not invent either.**

## GOING FORWARD

**Design comes from Architecture. Orders and decisions come from me. When the two
disagree on a mechanism, the design document wins and you tell me.**
