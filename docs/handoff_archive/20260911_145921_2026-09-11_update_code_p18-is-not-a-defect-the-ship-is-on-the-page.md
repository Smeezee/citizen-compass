# Update — Q55.P18 closes: the ship is on the front page. It was never missing, and the wrong conclusion was mine.

**2026-09-11 15:00 CDT / 20:00 UTC.**

## THE CAUSE, TRACED

**`build_next_frontpage.py:74`:**

    if s.get('n') in FOLDED: continue   # an edition of another hull.
                                        # shows on that hull's card.

`FOLDED` is built from `editions.json`. **That file has exactly ONE entry in
it** — one parent, one folded row:

    parent  "Valkyrie"
      <- {"name": "Liberator Edition", "from_row": "Valkyrie Liberator",
          "usd": 375.0,
          "source": "RSI store variant matrix. Valkyrie and Valkyrie Liberator
                     Edition both show Ship Value $375.00 USD.",
          "read_on": "2026-09-06", "confirmed_by": "Sleven",
          "caveat": "Sleven's call that the two are the same hull. Not yet
                     checked against CIG spec data."}

**C1's lead was right and it was the first place I looked.**

## AND IT IS ON THE PAGE, WHICH MAKES P18 NOT A DEFECT

**The served Valkyrie card, read out of the rendered DOM:**

    Valkyrie | IN GAME | Cargo | 48 m | crew 5 | 90 SCU | 19,845,000aUEC |
    $375 | at Astro Armada · Area18 | Liberator Edition | $375

**And a visitor can find it by name:**

    "valkyrie liberator"   1 result   -> the Valkyrie card
    "liberator"            2 results  -> Liberator, Valkyrie
    "valkyrie"             1 result   -> Valkyrie

The generator matches on edition names deliberately (`:313`, `:355`), so the
fold does not hide it from search.

**P18's DONE-WHEN — "the ship is on the front page, or the reason it cannot be
is written down" — is met by the first branch.** It is on the front page. It is
a row folded into its parent's card, by Sleven's own confirmed call, recorded
with a source, a date and a caveat.

**Nothing was changed. This item needed a trace, not an edit.**

## THE PART I OWE

**The wrong conclusion was mine and it is now corrected in the document that
carried it.** `docs/FINDING_the-front-page-inventory-2026-09-11.md` said, in its
own summary, *"One ship is on the old page and not the new one."*

**The measurement was right — 254 rows against 253 cards. The conclusion drawn
from it was not.** A card count cannot see a row folded into another card, and
**I should have written "254 rows against 253 cards, cause unestablished"
rather than naming a ship as missing.** That sentence then travelled: into my
Q55 memo as P18, into C1's queue entry, and into a lead C1 spent time on.

Three corrections are now in that finding, each marked as mine:

1. the headline claim, withdrawn and pointed at the correction
2. the detail in section 2.3, with the cause and the served evidence
3. **and the unrelated one I still owed** — the finding said the deploy-drift
   control was NOT PERFORMED for want of PostgreSQL and `python-dotenv`. **The
   build was never broken; I ran it with the system Python.** On the venv
   interpreter it passes 16 of 16, and served `index.html` and `next.html` were
   both byte-identical to the payload, so the gap closed in the strengthening
   direction.

## WHAT IS LEFT ON THIS ROW, AND IT IS NOT MINE

**Sleven's caveat is still live and untouched:** *"Sleven's call that the two
are the same hull. Not yet checked against CIG spec data."* **If that call is
ever wrong, the Liberator is a separate hull wearing another ship's card** —
which is a data question for him and C1 and not something a trace can settle.
I am recording it, not raising it.

**Also worth one line for whoever writes P21:** `editions.json` folding is used
**once in the whole dataset.** A mechanism with one user is either about to
have more or is a special case with a general name.

*Code, 2026-09-11 15:00 CDT.*
