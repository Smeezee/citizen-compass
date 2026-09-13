To:      Owner
From:    Architecture
Date:    2026-09-08
Subject: the two files are pointed, not restated — and one of them was never a copy
Status:  Answered

You asked for one line. It needs two, because one of the two files turned out
not to be what the order assumed.

## `docs/ARCHITECTURE_DECISIONS.md` section 4 — DONE, as ordered

The locked text is untouched, word for word. One paragraph added under it,
marked NOTED and not AMENDED, saying the machine it refers to is a separate
project now, that this project is a client of it, and that its reasoning is
maintained there and only there. The section points. It does not restate.

## `design/ANGLES.md` — NOT CHANGED, and here is why

**It states no Looking Project position. Not one.** I read all 103 lines before
touching it.

What is in it is the sixty-angles method — look at a thing from as many
genuinely different positions as you can find, and if two angles would produce
the same finding they are one angle. That is your method for examining pages,
sites and datasets. Its three checklists are somebody else's page, one of ours,
and a dataset. Nothing about lenses, readers, conditions, graders or boundaries.

**I think two different things with similar names got joined.** "Sixty angles"
is this project's examination doctrine. "Ten ways to look" is Design's inventory
of ways a machine can read a screen, and that one is Looking Project material and
is over there. The second is not in ANGLES.md.

**The check that settles it:** I searched every current document in the
repository for the Looking Project, excluding mail and archived history.
`docs/ARCHITECTURE_DECISIONS.md` was the only file that came back. ANGLES.md did
not appear, because the words are not in it.

So there is nothing there to point at. Stripping the method half would have
removed this project's own doctrine and aimed the remainder at a folder that does
not hold it. **If you still want it moved, say so and it moves** — but you would
be moving your own examination method out of the project that uses it, and the
audit desk's standing pass leans on it directly.

## SEPARATELY — one question that is yours and that Design refused to assume

Design's push-to-talk design rests on capturing your microphone while you play.
It declined to decide that, in its own words, on the grounds that it is a
decision about your home and not a technical question.

**Nothing is authorised to be built and I am not asking for a design.** I am
putting the question where it belongs so it does not get assumed by whoever
builds first.

    1  Do you want your own microphone captured at all?

---

ANSWERS:

**Answered by Sleven, 2026-09-08, and carried out 2026-09-09.** He confirmed the reading — `design/ANGLES.md` stated no Looking Project position and two things with similar names had been joined — and then moved the file for a different reason: **the method is his, it predates this site, and more than one project uses it.** It now lives at `CCDesk-logs/ANGLES.md`; `design/ANGLES.md` is a pointer plus the questions specific to Citizen Compass. `docs/ARCHITECTURE_DECISIONS.md` Section 4 carries its pointer line with the locked text untouched.
