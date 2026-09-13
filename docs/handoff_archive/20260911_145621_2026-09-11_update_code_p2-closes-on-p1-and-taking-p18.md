# Update — P2 closes on P1's evidence. Taking P18, the missing ship.

**2026-09-11 14:56 CDT / 19:56 UTC.** Mail read first: nothing new since
Owner's 13:55 letter, which is closed.

## Q55.P2 IS SATISFIED BY P1 AND NEEDS NO WORK

**DONE-WHEN:** *"either `#matrix` resolves to something on the front door, or it
is recorded as deliberately retired in a dated decision naming the dead
anchor."*

**It resolves.** P1 mapped it to the ships tab and that is proven on the served
site — `#matrix` lands on the ship list, `"AEGIS DYNAMICS · 28 ships · 19
buyable in game…"`, with a canary showing an unmapped address does not move the
page. **So the first branch is met and no decision is needed.**

**What is NOT closed by this**, and C1 already said so in the entry: whether the
TABLE VIEW itself returns is P21 and is Sleven's. **P2 was only ever about the
anchor not being a silent dead link.**

## TAKING Q55.P18

**DONE-WHEN** `Valkyrie Liberator` is on the front page, or the reason it cannot
be is written down. **BLOCKED-BY nothing — C1 ruled it a defect with an unknown
cause, and finding the cause is mine.**

**It is a real row and that is settled**, not by me: C1 found it in three
independent places, and I found a fourth this afternoon —
`price_corrections.json` carries it at **$375.00**, *"RSI store, Valkyrie
Liberator Edition"*, read on 2026-09-06 **by Sleven himself**.

**C1's lead:** our own record spells it two ways — `Valkyrie Liberator` in the
state document, `Valkyrie_Liberator_Edition` on the 2026-09-05 contact sheet —
and `editions.json` is one of three hand-maintained override files. **Look there
first, and rule 17 still forbids matching the two spellings by similarity to
make the counts agree.**

**One thing I can already narrow before opening anything**, from work done
earlier today: `frontpage_data.json` carries **254** rows and the built page
carries **253** cards. **So the row survives `build_frontpage_data.py` and is
lost inside `build_next_frontpage.py`** — the loss is downstream of the data
file, not in it. That is where I am starting.

*Code, 2026-09-11 14:56 CDT.*
