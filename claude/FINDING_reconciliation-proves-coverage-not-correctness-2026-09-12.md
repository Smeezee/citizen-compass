# FINDING — a clean reconciliation proves every row was READ. It proves nothing about whether the right question was ASKED of each row.

**2026-09-12. CIC. Caught in my own work, on the package sweep, before it shipped.**

## WHAT HAPPENED

The standing rider from the roles sweep says a paginated sweep is not finished until it is
reconciled against a known list. I did that. **253 rows read, 253 reconciled, 0 missing,
0 extra, 0 duplicates.** By the rider, the sweep was finished.

**It was wrong.** Six of the 253 answers were false.

The test applied to each page was a phrase regex that required the matched sentence to end
in a full stop:

    /[^.]{0,150}(comes with|includes|…)[^.]{0,150}\./gi

**RSI declares what a ship comes with in its bullet list, and bullet lists have no
terminal punctuation.** So the one place the answer lives was the one place the test could
not see. Ships whose bullets read "Includes an internally docked Kruger P-52 Merlin snub
fighter" came back as carrying no containment language at all.

**Six rows wrong: Constellation Andromeda, Constellation Aquila, 600i Explorer, 890 Jump,
Carrack w/C8X, Carrack Expedition w/C8X.** Four of them are among the ten ships that
actually do ship with other vehicles.

## HOW IT WAS CAUGHT, AND IT WAS NOT BY THE SWEEP

By checking a page whose answer was already known from outside the sweep. The
Constellation Andromeda has shipped with a P-52 Merlin for years; the sweep said it
contained nothing; the two could not both be true.

**Nothing internal to the sweep would ever have flagged it.** Every page loaded, every
page reconciled, every page returned a confident negative. A sweep that is wrong in the
same way on every row looks exactly like a sweep that is right.

## THE RULE THIS ADDS

**Reconciliation is a coverage check, not a correctness check.** It answers "did I read
everything" and is silent on "did I ask the right thing".

**So a sweep needs a second control, and it has to come from outside the sweep: at least
one row whose answer is known independently, checked against what the sweep returned for
it.** One known positive and one known negative is enough to catch a test that cannot see
its own subject matter. It costs one page.

**And be specifically suspicious of a sweep that returns almost all negatives.** That is
what a correct sweep looks like and it is also what a blind one looks like.

## WHAT WAS DONE

First pass discarded entirely rather than patched — a test that was wrong on six known rows
is not trustworthy on the 247 unknown ones. All 253 pages re-read with a test that reads
the bullet block directly and does not require punctuation. Result in
`claude/CIC_rsi-packages-and-contained-vehicles-2026-09-12.md`.

*CIC, 2026-09-12.*
