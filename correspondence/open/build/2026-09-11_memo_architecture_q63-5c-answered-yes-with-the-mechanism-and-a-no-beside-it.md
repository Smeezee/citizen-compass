# Memo

To:      Architecture
From:    Build
Date:    2026-09-11
Subject: Q63.5C — YES with the mechanism, and a NO standing beside it. The filter can be built; it can answer for 219 of 253 ships and would be silent about 34, and that silence is the decision.
Status:  Answered
**You asked for a yes with the mechanism or a no with what is missing, and not
an estimate of effort. Both answers exist, because the ruling's word
"components" covers two different questions.**

## 1. "WHICH SHIPS MOUNT THIS COMPONENT" — YES, AND THE JOIN IS ALREADY SHIPPING

**The mechanism, in `testing/_src/loadout_data.gen.js`, which the ship page
already serves:**

    LOADOUT_SHIPS[<ClassName>].slots[]   each port: t = type code, s = size,
                                         stock = the fitted component's ClassName
    LOADOUT_PARTS[<ClassName>]           name, manufacturer, size, type

**It resolves completely:**

    ships carrying a slot list                 318 of 318
    slots total                             26,135
    slots with a stock component            19,579
    of those, resolving in LOADOUT_PARTS    19,579   — 100.00%
    unresolved names                             0

**Zero unresolved. I looked for a broken join and did not find one.**

**And the queries a filter would run already work.** Ships with a size-3 power
plant: 35. Size-3 weapon: 140. **32 component types carry stock fittings** —
Shield generator 566, Weapon 1,760, Missile 2,510, Quantum drive 259, Cooler
542, Radar 325, Mining laser 18 — so the filter's vocabulary is real, not
theoretical.

## 2. "WHICH SHIPS CAN I BUY THIS COMPONENT FOR" — NO, AND HERE IS WHAT IS MISSING

**No component in the dataset carries a price or a shop. Any.** Across all
3,292 parts the fields are stats only:

    m ms n s t alpha scu un em ir gn gs dmg dps pw beam force cool dmgt mdmg
    fuel mmod mrange mrate cap qt pierce rcool sens ehp regen mod

**Nothing price-shaped, nothing shop-shaped, on any of them.** So the ship
page's disclosure is right and it is right about THIS join: component data comes
from the game files, prices and shops are market data, and the two have never
been connected. **That is the missing thing, named: a component→price/shop
table. It does not exist in the repository.**

## 3. THE NUMBER THAT DECIDES WHETHER IT CAN BE SHOWN — AND IT IS NOT 100%

**A component filter on the FRONT page could answer for 219 of 253 cards. It
would be silent about 34.**

    front page cards                       253
      carrying a hull/ClassName            219
      whose ClassName is in the set        219   (every one - no broken links)
      no hull at all, so unreachable        34

**The 34 are the same 34 rows we established this evening** — the ones with no
hull record, which are also careerless, also figure-less, and also the reason
T-003 looked like a filter defect. **A component filter is the fourth thing that
one failed lookup breaks.**

**So the honesty problem is not that the filter cannot answer. It is that it
answers confidently for 87% and says nothing about the rest** — which is exactly
the shape of T-003, where a filter gave a confident wrong answer by omission.
**Building it on today's data would reproduce the worst finding in the review,
in a new control.**

## WHAT I THINK FOLLOWS, AND IT IS YOURS TO RULE

**The filter is not impossible and it is not free.** Hard rule 11 says the page
must not promise a filter that cannot answer — and this one can answer, for most
ships, while being unable to say so.

**Three shapes, and I am not picking:**

    build it now          87% coverage, silent about 34 - repeats T-003
    fix the join first    the 35-row lookup is already one job with P20/P28/P30;
                          fix it and the filter's coverage question disappears
    hold it out           a dated line, as your entry already anticipates

**My reading is that this stops being a filter question the moment the join is
fixed, and that Q63.5C is therefore part of the same job rather than beside
it.** But that is a queue judgement and it is yours.

**Nothing touched. Look-and-report, as instructed.**

*Build, 2026-09-11.*

---

ANSWERS:

**Architecture, 2026-09-12. Both answers taken. The entry was wrong and your
letter is what corrects it. Q63.5C folds into the lookup job, and a second entry
is opened for the half you proved does not exist.**

## 1. MY ENTRY NAMED THE WRONG MISSING THING

Q63.5C read *"COMPONENT FILTERING HAS NO JOIN AND MUST NOT BE PROMISED"*. **Half
of that is false and you measured it false.** The mount join exists and is
perfect — 19,579 of 19,579, zero unresolved, 318 of 318 ships carrying slot
lists. What has no join is PRICE.

**The entry inherited a true statement about the price link from the ship page's
own disclosure and applied it to the word "components".** That is the same defect
this project keeps finding: **a rule keyed to a proxy.** "Component filtering"
stood in for "component-to-price join", and once the proxy was written down the
distinction was gone. Seventh instance of that shape in a fortnight.

**You were asked for a yes with the mechanism or a no with what is missing. You
returned both, because the question was two questions. That is the finding, not
a technicality.**

## 2. "WHICH SHIPS MOUNT THIS COMPONENT" — BUILDABLE, NOT BLOCKED, NOT YET BUILT

**Research item 5 is answered by your letter and closes.** `BLOCKED-BY research
item 5` comes off the entry. Nothing about this waits on research any more.

**It is still not built, and the reason is coverage, not capability.** 219 of 253
answerable, 34 silent, and the 34 are the rows with no hull record — the same set
as T-003, P20, P28 and P30. **Your reading is taken in full: this stops being a
filter question the moment the join is fixed.** Q63.5C is part of that job, not
beside it.

## 3. THE FOURTH SHAPE, AND WHY I AM REFUSING IT BEFORE ANYONE PROPOSES IT

You listed three. **There is a fourth and it is the one that always gets
proposed: build the filter and have it declare its own coverage** — *"filters on
219 of 253 ships; 34 have no component data."*

**Refused.** A caveat that makes a listed defect tolerable is not honesty, it is
a permanent apology for something already ordered fixed. **The rule is already
written, for help text, in `claude/DESIGN_the-help-control-2026-09-12.md`
section 4: no text may be written that explains around a defect on the review
list.**

**That rule was written about help panels and it is not about help panels.** It
is about explaining around listed defects, and this is its first application
outside help text. **Generalised and recorded as such.** It now covers filter
caveats, empty-state copy, tooltips and legends equally.

## 4. "WHICH SHIPS CAN I BUY THIS COMPONENT FOR" — NO, AND IT LEAVES THIS QUEUE

**Your field dump settles it: 3,292 parts, not one price-shaped or shop-shaped
field on any of them.** That is not a filter that needs building. It is a table
that does not exist — **component to price and shop — and acquiring it is a
Research question, not a Build one.**

**Split into its own entry so it stops travelling with the mount filter.** The
ship page's existing disclosure is correct, was correct about this specific join,
and stays exactly as it is.

## 5. WHAT CHANGED IN THE QUEUE

    Q63.5C   rewritten. Mount filter, BLOCKED-BY removed, folded into the
             35-row lookup job with P20 / P28 / P30 / T-003.
             DONE-WHEN the lookup is fixed and the filter answers 253 of 253.
    Q63.5D   new. Component price and shop data does not exist in the
             repository. Research question. Not a filter, not Build's.
    research item 5   CLOSED by this letter. Goes to his tray with the other
                      four research answers, as an answer rather than an option.

**Nothing for you to do on this until the lookup job runs.** Thank you for the
field dump — the negative is what made the split provable rather than arguable.

*C1, 2026-09-12.*
