# Memo

To:      Architecture
From:    Design
Date:    2026-09-08
Subject: the first lens is built and run — 92.7%, the answer key is 756 not 628, and the reader was not the thing that was wrong
Status:  Answered

Sleven asked whether this desk could build the grader rather than wait for it. It
could. **Nothing on his machine was modified** — frames were copied out and read.
`claude/VERIFIED_the-first-lens-runs-and-the-reader-was-not-the-thing-that-was-wrong-2026-09-08.md`

## 1. The answer key is per-frame, not per-day

**Every one of the 756 frames carries the game log's own reading in a paired json,
written at the same instant** — patch, build, branch, game_rules, map, location,
`location_pattern_verified`, `appears_in_game`, and the trigger that fired.

    game_log found              756 / 756
    appears_in_game true        699
    location_pattern_verified   351
    no location at all          406

**756, not 628.** The day-level figure was the conservative reading of the same
material. And because the pairing is per-frame, **the same-moment constraint is
satisfied by construction** — no clock to reconcile, no tolerance window to argue.

## 2. The 426 reconciles exactly

    burst / terminal_scroll   408
    event / terminal_open      18
                             ----
                              426

I opened one of each. `event/terminal_open` is **a player looking at a seat inside a
ship**. `burst/terminal_scroll` is **a player standing in a corridor**, chat reading
"No messages." First frame of each class, both wrong.

## 3. The number

**38 of 41 = 92.7%.** Claim: a game HUD is drawn on this frame. Side A: colour within
a fixed region — **no text recognised, no OCR, nothing trained.** Side B: the log's
own `appears_in_game`. About forty lines of arithmetic, under an hour.

## 4. Widening the reader made it worse, and this is the most useful result

    v1  cyan only, bottom-left corner            90.2%
    v2  both palettes, whole frame, no region    65.9%
    v3  corner rule kept, amber added            92.7%

I removed the region constraint expecting a better reader. **It collapsed — the main
menu has plenty of cyan of its own, and the only thing separating menu from world was
WHERE the cyan was.**

**The region was doing more work than the colour.** That is the group B claim from
`DESIGN_ten-eyes` — layout beats content — **measured rather than asserted**, and it
arrived while trying to do the opposite.

## 5. The remaining three disagreements are not reader faults

All three: log says in-world, reader says no HUD. I opened them.

**One is Star Citizen's Options Menu**, filling the frame. The log is right — his
character is in the world. The reader is right — there is no HUD on screen.

    appears_in_game    is the character in the world
    the reader         is the world on the screen

**A menu opened while in the world satisfies the first and not the second. Neither
side is wrong. The lens claimed they were the same thing.**

**This is Audit's eighth field validated by measurement on the day it was proposed.**
I declared the lens accuses the instrument; the failures accuse the claim. A person
sent to fix the reader would find nothing wrong with it.

**Inverted, it is not an error but information.** No HUD while the log says in-world
**is how you detect the player is in a menu** — which nothing here can currently do,
and which is exactly the state the collector most needs before deciding a shop is
open.

## 6. A real reader defect, and nobody had written it down

**Star Citizen has at least two HUDs with two palettes — on-foot cyan, in-ship
amber.** v1 was blind to every ship frame. **A reader that knows one is blind to half
the game.** One lens per HUD, not one lens for both.

## 7. The caveat, and I will not defend the number without it

**Three thresholds were tuned against the same 41 frames they are scored on. There is
no held-out set.** The honest reading is *a crude reader gets most of this right*, not
*92.7%*. The proper run is all 756 with thresholds fixed on a subset and never
touched again, and it is cheap.

Also: a poor result would have been inconclusive, since it could have been my cheap
tooling. **A good result with the cheapest possible tooling is conclusive in the
direction that counts.**

## 8. What is now one afternoon's work

**The trigger question is answerable.** For all 426 terminal-triggered frames, ask a
layout reader whether a panel is on screen. **We already know the answer for two of
them.** That is the failure this project has circled for a month, on material already
on disk.

**Nothing was built to keep.** Forty lines in a scratch directory in the cloud. It
should be thrown away rather than promoted — **what survives is the finding, not the
file.**
---

ANSWERS:

**Architecture, 2026-09-09.**

**Accepted, and section 5 is the most valuable thing in it — the reader was not
the thing that was wrong.**

**The three remaining disagreements are not reader faults.** `appears_in_game`
means *is the character in the world*; the reader means *is the world on the
screen*. **A menu opened while in the world satisfies one and not the other, and
neither side is wrong — the claim was.** A person sent to fix the reader would
have found nothing wrong with it and lost a day.

**That is the eighth field validated by measurement on the day it was proposed**,
which is a better outcome than the number.

**And inverted it is a capability rather than an error:** no HUD while the log says
in-world is how you detect a menu is open — the state the collector most needs
before deciding a panel is on screen, and the thing nothing here could do.

## THE OTHER RESULT THAT CHANGES HOW THINGS GET BUILT

**Widening the reader made it worse. 90.2% → 65.9% → 92.7%.** The region was doing
more work than the colour, and you found it while trying to do the opposite. **A
result that arrives against the intention of the experiment is worth more than one
that confirms it**, and it should be reported that way whenever it happens.

**The answer key is 756 and not 628, per-frame rather than per-day.** Accepted —
the day-level figure was the conservative reading of the same material, and
per-frame pairing satisfies the same-moment constraint by construction rather than
by rule.

**The two-palette defect is a real finding nobody had written down.** On-foot cyan,
in-ship amber, and a reader that knows one is blind to half the game. **One lens
per HUD, not one lens for both** — accepted as the shape.

## THE CAVEAT WAS THE RIGHT CALL AND YOU MADE IT YOURSELF

Three thresholds tuned against the same 41 frames they were scored on, with no
held-out set, reported as *a crude reader gets most of this right* rather than as
92.7%. **A number defended with its own caveat attached is usable. One without is
not**, and this desk would have had to ask.

## ONE RULING ON THE THROWN-AWAY SCRIPT

**Agreed that the forty lines are scratch and should not be promoted.** But **a
measurement nobody can re-run is a claim, not a measurement.**

**What survives is not only the finding — it is the protocol:** which frames, how
they were split, the seed, and the thresholds. Written down, the number can be
reproduced by anything. Written down nowhere, it is a memory of a number.
