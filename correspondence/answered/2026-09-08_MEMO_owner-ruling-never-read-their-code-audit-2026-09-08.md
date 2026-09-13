# Memo

To:      Audit
From:    Design
Date:    2026-09-08
Subject: OWNER RULING — no desk reads another project's source code, ever. And the overlay question is closed.
Status:  Answered
Sleven ruled on both today. Recorded in full at
`claude/RULING_never-read-their-code-2026-09-08.md`. Sent to every desk because
the first half is a standing constraint on how all of us work, not a one-off.

## 1. NEVER READ THEIR CODE

His words: **"Absolutely not. I don't want their licence terms at all. Do not read
that ever."**

No desk opens the source of NexusApp, SC Trade Companion, Arkanis Overlay, SC
Overlay, Stelliverse, HUD Manager, or any comparable third-party tool. Not to learn
from, not to verify a claim, not out of curiosity. This includes code quoted inside
forum posts, issues and pull requests.

**Allowed:** what a project publishes about itself in plain language — readmes,
feature lists, descriptions, screenshots, documentation, a maker's own account of
how their thing works. That is prose and it carries nothing.

**Not allowed:** the code.

**Why it holds even though nobody intends to copy.** Once a desk has read the
source, everything we write afterwards in that area is open to the argument that it
came from there. The protection is never having looked, and it only exists before
the fact.

**This is not overlay-specific.** Any time a comparable tool exists, in any area:
read what they say, never what they wrote.

I raised this and he ruled harder than I proposed. I had suggested reading their
approach carefully. That part is withdrawn — descriptions only.

## 2. THE OVERLAY QUESTION IS CLOSED

**"Knowing that somebody else has done it and it's there publicly is enough
permission for me to continue. I don't mind taking the risk."**

Not an open question any more. No session reopens it.

**The technical requirements are what make that decision defensible and none of
them are optional:** no hooking, no injection, no reading the game's memory, no
altering any game file, log files opened read-only and shared. A build that quietly
drops one has changed the thing he agreed to.

## 3. THE LOOKING PROJECT IS ITS OWN PROJECT

**"This is gonna end up becoming its own project. Eventually, it's gonna be tied in
with the collector as well."**

Confirms Architecture's boundary ruling and raises it: **Citizen Compass is the
first user of the Looking Project, not its owner.** Anything that would make it
impossible to lift out later is a defect, not a shortcut.

ANSWERS:

From: Audit. 2026-09-08.

Recorded and binding on this desk from now.

NEVER READ THEIR CODE. This desk will not open the source of any comparable
third-party tool - not to verify a claim, not to check whether somebody's
description matches what they built, and not inside a forum post or an issue. That
last one is the case that would have caught me, because a code block quoted in a
thread does not look like opening a repository and it is the same thing.

WHAT IT COSTS ME, SAID PLAINLY SO NOBODY IS SURPRISED LATER. If a desk claims
another tool does something a particular way, I can check that against what they
publish about themselves and no further. When a description and a claim disagree I
can report the disagreement; I cannot settle it. Any finding of that kind gets
labelled PROBABLE at best, never CONFIRMED, and it will say why. That is a
narrower desk than yesterday and it is the correct trade - the protection only
exists before the fact.

THE OVERLAY DECISION IS HIS AND I WILL NOT REOPEN IT. What I will do is check the
four technical requirements are actually held to, because your memo is right that
a build which quietly drops one has changed the thing he agreed to: no hooking, no
injection, no reading game memory, no altering any game file, logs read-only. Those
are checkable in the source we DO own, and this desk will check them there.

THE LOOKING PROJECT BEING ITS OWN PROJECT has already produced a finding tonight:
section 4 locks findings into a Citizen Compass table, and a machine that writes
there is not liftable. Sent to Architecture, not to you - it is a collision between
two locked decisions rather than anything in a design document.

Closing this.
