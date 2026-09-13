# RULING — Sleven on pulling assets out of the game client

    from      Sleven, 2026-09-06. Filed verbatim by C1.
    context   asked whether our ships could be made to look like CIG's, C1
              reported that CIG's per-part models and real material colours are
              in the game client on his machine, that the format is half decoded
              here already, and that **the Fan Kit question on converting client
              assets is his alone.**
    revised   same day. C1's first filing said converted assets could not reach
              the testing host without per-item permission. Sleven corrected it:
              the testing host is cleared. Only the public site is held.

---

## His words

> "I have no problem pulling the data from the game. At this current moment, it's
> her personal use and when it becomes public use, it will be probably known if
> they wanted to come down where they will."

## What C1 reads that as, stated so he can correct it

**Personal use, on his own machine, now: yes.** Decoding, converting and looking
at CIG's own files locally is authorised by the owner.

**The TESTING host: yes.** Corrected by him the same day, because C1's first
filing of this ruling drew the line too tight:

> "No. It absolutely can go to the live test site. And before it goes live, we'll
> take care of everything else."

The testing host is password-gated and private. Converted assets are cleared for
it, and no separate permission is needed each time.

**The PUBLIC site: not yet, and that is where the question actually bites.** He
named the risk rather than dismissing it — that once it is public it would likely
be seen, and CIG could act. **His plan is to handle it before going live, not to
ignore it.** Going live is already off the queue until he raises it himself, so
this changes nothing about that.

**So the line is public, not local, and not testing.** Local work and testing
deploys proceed. **Nothing derived from converted client assets goes onto the
PUBLIC site without him saying so.** A session reading this as permission to
publish publicly has misread it.

## What this unblocks locally

`Data.p4k` holds CIG's per-part models — `DRAK_Cutlass_Black.cga` declares **209
nodes against the 1 our shipped model has** — and CIG's material files state every
ship's colours as numbers. The container, the name table and the node array are
already decoded in this repo; the outstanding piece is one mesh chunk, and two
maintained open-source converters already handle it.

**It is the same root cause as several open defects** — the see-through hulls, the
85X/Fury duplication, the missing Constellation landing gear, the outdated
Freelancer airframe, and 113 hardpoint markers placed from names rather than
geometry. All of them come from shipping somebody else's flattened export.

## What C1 is NOT doing

**Not arguing the rights question in either direction.** Rule 23: rights and
credentials are closed, and flagging is raising. This document records his ruling
and the boundary it draws. It makes no case.

**Nothing downloaded, nothing converted, nothing run.** No converter has been
fetched. This is a ruling on file, not a start.

*C1, 2026-09-06.*
