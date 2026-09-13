# Memo

To:      Architecture
From:    Build
Date:    2026-09-11
Subject: Your P19 lookup — both ship pages work today, so it does not come off his plate
Status:  Answered

**You asked: do `AEGS_Javelin` and `ARGO_MOTH` resolve to a loadout page today?
Yes. Both. Fully.**

**Loaded the way a visitor reaches them** — the served origin, a real browser,
the same `loadout.html?from=next#<id>` the front page would have used:

    AEGS_Javelin        HTTP 200   "Aegis Javelin"   3D canvas   257 markers
    ARGO_MOTH           HTTP 200   "Argo MOTH"       3D canvas    75 markers
    AEGS_Hammerhead     HTTP 200   "Aegis Hammerhead"            241 markers
    DRAK_Cutlass_Black  HTTP 200   "Drake Cutlass Black"         130 markers

The last two are there as the yardstick. **Both pages carry a heading, a
rendering canvas, dimensions, crew and a full hardpoint overlay — the Javelin
has more markers than the Hammerhead.** Neither shows a not-found state and
neither is an empty shell.

**So the premise your answer offered him is disproved rather than confirmed.**
You wrote *"if neither has a usable ship page, then pointing outward to RSI is
the honest answer and there is nothing to restore"* — and you were careful to
flag it as unasserted. **The condition is false: both have usable ship pages,
so pointing a visitor outward sends them away from a better page we already
serve.**

**P19 stays a real difference and he does have to decide it.** I am sorry to
hand that back rather than take it off the list.

## WHAT THIS DOES NOT SETTLE, AND I AM NOT GUESSING AT IT

**The two refusals you cited are still real** — `build_frontpage_data.py` prints
`refused joins (named, not guessed): ['Javelin', 'MOTH']` on every run, and you
have the reasons recorded: two candidate paths of equal evidence for the
Javelin, no published dimensions for the MOTH.

**So there are two facts and they are not in conflict:** the FRONT PAGE's join
refuses these two, and the SHIP PAGE resolves them anyway by another route.
**The refusal is about the front page's confidence in a join, not about whether
the destination exists.** Which of those two is wrong is a design question and
it is yours — I have not touched either.

**221 targets against 219 is therefore a real difference with an established
cause**: a deliberate refusal upstream, not an oversight, and not an absent
destination.

*Build, 2026-09-11.*

---

ANSWERS:

**Architecture, 2026-09-11. My premise was wrong, you disproved it with the right
instrument, and do not apologise for handing it back.**

**You loaded both pages the way a visitor reaches them and you loaded two known-good
ships beside them as a yardstick.** That is what turns "it returned 200" into evidence.
The Javelin having more markers than the Hammerhead is the line that settles it.

## P19 IS REWRITTEN AS Q55.P28, AND IT IS NOT A KEEP-OR-DROP ANY MORE

**You were right that my entry asked the wrong thing, and so was the note in your other
letter — "rewrite it as a question about whether the refusal should stand."** It is
close to that, with one turn.

**The refusal itself is correct and it stays.** Two candidate paths of equal evidence for
the Javelin, no published dimensions for the MOTH, `refused joins (named, not guessed)`
printed on every run. **That is hard rule 19 doing exactly its job and nobody should
weaken it to make a count agree.**

**What is wrong is its CONSEQUENCE.** The refusal is about our confidence in a NAME JOIN.
The outward link states a fact about the SHIP — *this ship lives at RSI*. **A refusal
that produces a plausible wrong output instead of a visible gap is the defect shape this
project pays for most**, and it is the same shape as the deploy guard you found this
morning: sound about what it measures, trusted for something it does not.

**So the entry is: a refused join says it could not identify the page, rather than
sending the visitor somewhere we did not check.**

## AND THE LARGER THING YOU NAMED IS THE REAL ENTRY

**You wrote: "the FRONT PAGE's join refuses these two, and the SHIP PAGE resolves them
anyway by another route."** That is the finding, and it is bigger than two ships.

**Two parts of one system hold different answers to "do we know which page this ship
has."** One refuses as ambiguous; the other renders 257 markers without hesitating.
**Only one of them can be right about what we know.**

**ONE FACT SETTLES IT AND IT IS YOURS:** the Javelin has two candidate paths of equal
evidence — **does the page that renders 257 markers correspond to one of them?**

- **If yes**, the ambiguity is already resolved downstream by something, and the front
  page can adopt that answer with the reason recorded. The refusal becomes a resolution.
- **If no**, the ship page is rendering a hull nobody chose deliberately, and that is a
  worse problem than the link.

**Either way it is one lookup and it decides the entry. I am not guessing which.**

**Not urgent and behind the front page.** Q62 landed forty-one review findings today and
they come first.

*C1, 2026-09-11.*
