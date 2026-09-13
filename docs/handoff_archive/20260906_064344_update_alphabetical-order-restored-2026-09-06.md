# update - alphabetical order restored on the front page demo, 2026-09-06

**Sleven caught an ordering regression I introduced.** The demo was sorting
manufacturers by how many ships they have and ships by length. **His standing
decision, from the original page and live on the test site today, is
alphabetical: manufacturers A to Z, and ships A to Z inside each maker, matching
RSI's own store order.**

Fixed. Sorting now uses `Intl.Collator('en',{numeric:true})` so the
number-leading names fall in the order a person expects - 100i, 125a, 135c, 300i
- rather than the order a plain string sort would give.

Verified in a real browser: Aegis Dynamics leads, and inside it Avenger Stalker,
Avenger Titan, Avenger Titan Renegade, Avenger Warlock, Eclipse, Gladius,
Gladius Dunlevy, Gladius Pirate, Gladius Valiant, Hammerhead, Idris-M, Idris-P,
Javelin, Nautilus, Reclaimer, Redeemer, Retaliator, Sabre.

    cards 254 of 254   first paint 260 ms   console errors 0

**The lesson, and it is the same one this project keeps writing down:** the
ordering was a decision Sleven had already made and that was already shipping. I
replaced it while rebuilding the page and never checked what the live page did.
**Read what is already there before changing how it behaves.**

C1, 2026-09-06.
