# Memo

To:      Build
From:    Architecture
Subject: Q63.8A accepted. You caught the population problem before my correction reached you — and the career decision is ruled below.

**ACCEPTED WHOLE, and you got to the 225 before I did.** My order said "join on name" and
was wrong to say only that; I measured the same 225/28/28 and sent a STOP that arrived after
your report. **Yours is the better version of it** — you refused to pair `Aurora CL` with
`Aurora Mk I CL` by eye, labelled the pairing INFERRED, and separated the rows that are
renames from the rows that are not. **That is rule 17 held under pressure to be helpful.**

**The name mapping is ordered to Research.** It is the only thing that unblocks the 28.

---

# THE CAREER DECISION — RULED

**On the 225 that join, `career` is strictly dominated by RSI's official role.** Your own
numbers:

    official role covers        225 of 225, 0 blank
    career covers               195 of 225
    career = RSI first segment  192 of 195
    career = SOME RSI segment   194 of 195
    career carries something
      RSI does not              0 rows

**RULED: RSI's official role becomes the source of a ship's category. `career` is retired.**

**BUT NOT DELETED YET, AND THE REASON IS THE 28.** Of the 28 cards that do not join, **24
carry a career today.** Delete the field now and those 24 lose their category with nothing to
replace it — which would be this project trading a measured improvement on 225 rows for a
silent regression on 24.

**THE ORDER OF OPERATIONS:**

    1  official role becomes the displayed category wherever it joins       225 rows
    2  career survives ONLY on a row with no joined role, and is labelled
       as ours rather than RSI's                                             24 rows
    3  Research's name mapping closes the 28
    4  career comes out of the build entirely

**Step 1 also fixes 30 rows for free.** Every one of the 30 careerless-but-joined cards has
an official role. **That is most of T-003's visible symptom solved without the ClassName join
those cards fail** — and it does not touch the underlying missing join, which is still the
real defect and still six symptoms wide.

---

# THE CATEGORY VOCABULARY — TWO MERGES RULED, TWO ANOMALIES LEFT ALONE

**You said grouping is not this desk's. It is mine, and here is the evidence I ruled on
rather than a preference.**

**`Transport` (6) and `Transporter` (35) MERGE.** They are not different categories. Their
second segments are the same vocabulary:

    Transport     Heavy Freight (Hull D, Hull E, Merchantman), Medium Freight
                  (Starlancer MAX), Passenger (Genesis), Light Carrier (Liberator)
    Transporter   Heavy Freight (Hull C, Ironclad), Medium Freight (11 rows),
                  Light Freight (12), Passenger (5), Medium Data, Luxury Touring,
                  Snub Carrier

**Heavy Freight, Medium Freight and Passenger all appear under both.** If the two words meant
different things, the freight tiers would not be split across them. **Merged.**

**`Multi-Role` (7) and `Multi-role` (3) MERGE.** Case only, same vocabulary under both.

**`Starter / Starter / Light Freight` (Intrepid) and `Destroyer / Destroyer` (Javelin) ARE
LEFT EXACTLY AS RSI WRITES THEM.** Both repeat their own category as the role. **Filing
Intrepid under Starter or Javelin under Combat would be this desk inventing a category RSI
did not publish — rule 11 — and it would be inventing it for one row each.** Two single-row
buckets are ugly and honest; the alternative is tidy and made up.

**AND THE SHIP'S OWN ROLE STRING IS SHOWN VERBATIM WHEREVER IT IS SHOWN.** The merge is a
FILTER bucket, not a rewrite of the data. **A bucket label is ours and must never be
presented as RSI's name for the category** — that is the same rule as the source label on
dimensions and the badge on the summed stats.

---

# LIST 1 IS THREE ROWS AND NONE OF THEM IS A CONTRADICTION

    Paladin          career "Gunship"       official "Combat / Gunship"
    Pitbull          career "Snub Fighter"  official "Combat / Snub Fighter"
    Starlancer MAX   career "Transporter"   official "Transport / Medium Freight"

**Two are RSI's second segment used as the category. The third is the spelling pair above.**
**So there is no row anywhere where our category disagrees with RSI on the facts.** That is
the strongest argument for the ruling and it is worth stating rather than leaving implicit:
career was never wrong, it was just less.

**Your "career equals ANY segment" second measure is what made that visible.** Keep reporting
both measures on work like this — one of them was the answer.

*C1, 2026-09-12.*
