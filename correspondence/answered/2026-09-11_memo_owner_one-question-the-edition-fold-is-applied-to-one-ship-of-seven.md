# Memo

To:      Owner
From:    Engineering
Subject: One question — the edition fold is applied to one ship out of seven, and it has now cost a day twice
Status:  Closed

**One decision. Everything behind it is measured and nothing is waiting on anything
else.**

## WHAT IS TRUE TODAY

**Seven edition-shaped ships are separate cards on the front page. Exactly one is folded
onto its parent.**

    separate cards       600i Executive Edition · F8C Lightning Executive Edition
                         Gladius Pirate · Avenger Titan Renegade
                         C8X Pisces Expedition · Carrack Expedition
                         Constellation Phoenix Emerald · P-72 Archimedes Emerald
    folded               Valkyrie Liberator  ->  shown as an edition line on the
                         Valkyrie card, $375

**The fold comes from `editions.json`, which has exactly one entry.** Build measured the
cards; I confirmed against the public site's own 254-row ship array. Two different files,
same answer.

## WHY IT IS WORTH ONE MINUTE OF YOURS

**It has read as a missing ship twice in one day** — once from the front-page inventory,
once from the outside review, which put "253 against 254, one ship missing" at the top of
its comparison. **Both times it cost a trace. A card count cannot see a row folded into
another card.**

**A rule applied to one of seven is not a rule.** It is an exception nobody can predict,
and the next count that disagrees costs the same time again.

## THE TWO WAYS OUT

**UNFOLD IT — my recommendation.** Delete the single `editions.json` entry. The Liberator
becomes its own card like the other seven, the two ship counts agree, and the mechanism
stops being an inconsistency. **Cost: one more card on the page, and the Valkyrie card
loses its "Liberator Edition | $375" line.** `editions.json` is also one of the three
hand-maintained override files already carrying a rule-14 second-writer flag, so a
mechanism with no users is one less thing to maintain.

**FOLD THEM ALL.** Keep the Liberator as it is and add the other seven to
`editions.json`, so each parent card carries its editions. **Cost: real work, eight
entries to write and maintain by hand, and the page loses seven cards.** It is the better
page if you think an edition is a variant of a ship rather than a ship.

**I recommend unfolding because it is the consistent answer with the least machinery, not
because it is the better page.** If you think editions belong on their parent's card, say
so and the work is the second option — it is a product judgement and it is yours.

## SEPARATELY, AND NOT A QUESTION

**Six ships have a built model and no row anywhere** — the four Best In Show 2949 ships,
Caterpillar Pirate Edition, Nautilus Solstice Edition. Found while answering this.
**Filed as Q55.P29; almost certainly limited editions nobody can buy, and the honest
outcome is probably a dated line saying so. Nothing needed from you.**

---

## QUESTIONS

1. The Valkyrie Liberator fold: unfold it so all eight editions are separate cards, or
   fold the other seven so every edition sits on its parent's card?

---

CLOSED:

**Owner, 2026-09-12. Answered and closed.** Ruled in the same file, and neither of your two options as written. The rule is the edition itself: cosmetic or paint-only folds under the base ship; physically, mechanically or functionally different gets its own card. Confirm the ship's full official name first and do not confuse it with the separate Anvil Liberator. Research the Valkyrie edition before changing it, then audit the other seven by the same rule.
