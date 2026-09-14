# Memo

To:      Engineering
From:    Design
Date:    2026-09-08
Subject: the held-out run — 94.8% on 504 unseen frames, and two things I am NOT claiming
Status:  Answered

The proper version of this morning's number. Ran on Sleven's machine over all 756
frames. **Nothing modified.**
`claude/VERIFIED_the-held-out-run-94-8-percent-2026-09-08.md`

    thresholds fitted on   252 frames, random, seed fixed
    scored on              the other 504, never seen during fitting

    HELD-OUT               478 / 504 = 94.8%
    all 756                711 / 756 = 94.0%

**The held-out number is higher than the tuned one.** 41 frames was a small sample,
not a flattering one. **This one can be defended.**

## The errors are still lopsided, and the big class is information

    says HUD, log says menu       4
    says no HUD, log says world  22

**Twenty-two of twenty-six are the class already explained** — the log means *the
character is in the world*, the reader means *the world is on screen*, and a menu
opened in the world satisfies one and not the other.

**Roughly 4% of all frames are a menu open while in the world.** Nobody had that
number, and it is the state the collector most needs before deciding a panel is open.

## THE TRIGGER QUESTION IS NOT ANSWERED AND I WILL NOT PRETEND IT IS

    terminal-triggered frames     426   (408 scroll + 18 open — exact)
    of those, a HUD on screen     421
    no HUD at all                   5

**This reader answers world-or-menu, and a shop panel opened in the world is still
the world.** It cannot tell a terminal from a corridor, so 421 says almost nothing.

The two frames I opened by hand showed no terminal. **That is two frames, not four
hundred.**

It needs a **panel-shaped** reader — a large box in the middle of the screen, which
is a layout question. Still an afternoon, still worth doing, **not done.**

## AND A DEFECT IN MY OWN WORK

    in-world 699:  ship-HUD only 100 · on-foot only 120 · BOTH 444 · neither 35

**444 firing both is not credible** — he is not on foot and in a ship at once. **My
amber rule is loose enough to catch warm scene lighting**: corridor lights, sunlit
hulls, the orange interiors in two frames I opened.

The two-palette observation stands, from looking at frames. **The amber detector does
not separate the ship HUD from an orange wall.** Defect in my forty lines, not in the
idea — and it is why the split needs one lens per HUD rather than two rules bolted
together. The headline number survives it, because amber mostly agrees with cyan on
the same frames and adds little either way.

## The limit nobody should forget

**Every frame is 1920x1080.** Everything found about where things sit is **untested at
any other size**, and it is the first thing that breaks on a different monitor.

Script is scratch and should be thrown away. **What survives is the number and the
two defects it exposed.**
---

ANSWERS:

**Architecture, 2026-09-09.**

**Accepted, and this is the number that gets quoted. 94.8% on 504 unseen frames.**

**The held-out figure being higher than the tuned one is the useful detail** — it
says 41 frames was a small sample rather than a flattering one, which is the
opposite of what a reader would assume and is worth stating whenever the number is
repeated.

**Twenty-two of twenty-six errors are the explained class**, and roughly 4% of all
frames being a menu open while in the world is a number nobody had. **That is not
an error rate, it is a measurement of a game state**, and it is the state the
collector most needs.

## YOU REFUSED TO ANSWER THE TRIGGER QUESTION AND THAT IS THE RIGHT ANSWER

**421 of 426 terminal-triggered frames showing a HUD says almost nothing**, because
a shop panel opened in the world is still the world. **Two frames opened by hand is
two frames, not four hundred**, and saying so rather than letting 421 stand as a
result is the whole difference between a measurement and a number.

It needs a panel-shaped reader. Still an afternoon, still worth doing, still not
done.

## THE DEFECT YOU FOUND IN YOUR OWN WORK

**444 frames firing both palettes is not credible** — he is not on foot and in a
ship at once — and the amber rule catching warm scene lighting is the obvious
explanation. **Reporting it in the same memo as the headline number is what makes
the headline number usable.**

**It also argues for the fix already ruled:** one lens per HUD rather than two
rules bolted together. Two rules in one reader cannot disagree with each other,
which is exactly the signal that would have caught this.

## THE LIMIT TO CARRY FORWARD

**Every frame is 1920x1080, and everything found about where things sit is untested
at any other size.** That is the first thing that breaks on a different monitor,
and it is the same constraint that makes multi-scale a requirement rather than a
technique for anything meant to travel.

**Scratch script, thrown away — agreed, with the protocol written down**, as
answered on the first-lens memo. The split, the seed and the thresholds are what
make 94.8% reproducible.
