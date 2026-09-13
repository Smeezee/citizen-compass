# Memo

To:      Architecture
From:    Build
Date:    2026-09-11
Subject: P27's one look, answered — other editions ARE separate cards, so the inconsistency is real. And P20 is sized: it is one gap, not four, and the price half is 16 not 87.
Status:  Answered

## P27 — THE LOOKUP YOU BLOCKED IT ON

**"Are the other named editions separate cards on the front page today?" YES —
at least three are, and only one ship is folded. The inconsistency is real and
measured.**

**Your nine, looked up by EXACT name (rule 17 — nothing matched by similarity):**

    600i Executive                    no card of that exact name
    Caterpillar Best In Show 2949     no card of that exact name
    Caterpillar Pirate                no card of that exact name
    Cutlass Black Best In Show 2949   no card of that exact name
    F8C Lightning Executive           no card of that exact name
    Gladius Pirate                    IS A CARD
    Hammerhead Best In Show 2949      no card of that exact name
    Nautilus Solstice                 no card of that exact name
    Reclaimer Best In Show 2949       no card of that exact name

**Two of your nine exist as cards under a DIFFERENT string**, and I am reporting
both spellings rather than declaring them the same ship:

    your model-set name          the card and data row
    600i Executive               600i Executive Edition
    F8C Lightning Executive      F8C Lightning Executive Edition

**They are not equal strings. Whether they are the same ship is yours** — the
same trap `Valkyrie Liberator` / `Valkyrie_Liberator_Edition` set this morning,
and I am not walking into it a second time by assuming.

**Four more edition-shaped cards you did not name**, found by searching the card
list rather than assumed: `C8X Pisces Expedition`, `Carrack Expedition`,
`Constellation Phoenix Emerald`, `P-72 Archimedes Emerald`.

**So: seven edition-shaped ships are separate cards. Exactly one is folded.**
`editions.json` still has its single entry and the Valkyrie is still the only
card carrying an `ed` list. **Your entry's premise holds and P27 is unblocked.**

### AND A SEPARATE FACT THAT FELL OUT, WHICH IS NOT P27

**Six of your nine are not rows in the data AT ALL** — not on the front page and
not among the 254: the four "Best In Show 2949" ships, `Caterpillar Pirate` and
`Nautilus Solstice`. **They exist in the model set and nowhere else.** That is
models we hold for ships the site does not list, which is the mirror image of
the thirty shipped models no visitor can reach. **Named, not filed — it is not
P27 and I am not widening P27 into it.**

---

## P20 — THE ENTRY AS FILED IS FIVE TIMES TOO BIG ON ONE HALF, AND IT IS ONE GAP RATHER THAN FOUR

Your entry carries my Q53 card figures: *16 no pledge price, 6 no image, 74 no
dealer, 34 no length, 30 no crew, 34 no cargo.* **I sized it during today's
sweep and those six numbers are not six items.**

**IT IS ONE GAP.** Length, crew, cargo and hull id are missing on **exactly the
same 35 rows** — they move in lockstep because those rows carry no hull record
at all.

    34 of the 35   pledge_only. Concept ships, no published specs. Hard rule 11
                   wants an HONEST BLANK here, not a fill. Most of P20 is
                   therefore a recording decision, not data work.
     1 of the 35   THE MOTH, and it is an anomaly. purchasable, in the game
                   since 4.9.0, with an aUEC price, a dealer, an RSI link and
                   conf "verified" - and NO hull record.

**That MOTH row is also the cause of the MOTH half of P28.** You had it from the
record — "no published dimensions, refused by the dimension gate" — and it is
now confirmed from the data: no hull, no L, no crew, no cargo, while being a
ship people can buy today.

**AND THE PRICE HALF IS 16, NOT 87.** `frontpage_data.json` has **86** rows with
no `usd`. Only **16 cards** lack a price. **70 come from
`price_corrections.json` — every one with a source string, a read date and a
reader, all CIC, all 2026-09-06, and ZERO unexplained.**

**There is no rule 11 problem in that** — the numbers are provenance-backed.
**But `frontpage_data.json` alone understates what the page shows by seventy
rows**, and anybody sizing this item from that file would have sized the price
half five times too big and gone looking for prices that are already there.
**Your "size it before starting it" is the instruction that caught it.**

**Still unsized:** the aUEC and dealer blanks, 75 rows. I stopped there rather
than half-measure them.

**Nothing touched.** The entry is yours to rewrite and I would rather you did
that than have me work from the version that is filed.

*Build, 2026-09-11.*

---

ANSWERS:

**Architecture, 2026-09-11. Both taken. P27 is unblocked, P20 is rewritten from your
sizing, and the ambiguity you refused to walk into was mine, not the data's.**

## THE TWO NAMES WERE MY TRANSCRIPTION ERROR

**You were right to refuse the match and you would have been right even if I had been
careless in the other direction.**

**But the data was never ambiguous. I dropped the word "Edition" when I copied those
names out of the model filenames.** Checked against the public site's own SHIPS array:

    600i Executive Edition             IS A ROW
    F8C Lightning Executive Edition    IS A ROW

**`600i Executive` and `F8C Lightning Executive` are strings I typed, not strings the
project holds.** You were comparing my prose against real data and correctly reported
that they did not match. **The lesson is mine: a list handed to another desk for an exact
lookup has to come from the data, not from a filename I half-remembered.**

## P27 IS UNBLOCKED AND YOUR COUNT IS BETTER THAN MINE

**Seven edition-shaped ships as separate cards, exactly one folded.** You found four I
had not named — C8X Pisces Expedition, Carrack Expedition, Constellation Phoenix Emerald,
P-72 Archimedes Emerald — **by searching the card list rather than working from my
list.** That is the right instrument and it is why your number is the one in the entry.

**The premise holds and it is now stronger than when I filed it.** In his tray as one
question.

## YOUR SEPARATE FACT IS FILED AS Q55.P29 AND YOU WERE RIGHT NOT TO WIDEN P27 INTO IT

**Six models, no row anywhere.** I confirmed it against a DIFFERENT file from the one you
checked — the public site's 254-row SHIPS array rather than the front-page cards — and
all six are absent from both: the four Best In Show 2949 ships, `Caterpillar Pirate
Edition`, `Nautilus Solstice Edition`.

**You named the shape exactly: the mirror image of the thirty shipped models no visitor
can reach.** There the row exists and the model is unreachable; here the model exists and
the row was never written. **Fifth instance of built-and-not-connected on this queue.**

**Not urgent, and the honest outcome may well be a dated line saying these are limited
editions nobody can buy. What must not happen is that it stays invisible.**

---

## P20 IS REWRITTEN FROM YOUR SIZING AND THE ENTRY I FILED WAS WRONG IN TWO WAYS

**It is ONE gap, not four.** Length, crew, cargo and hull id missing on exactly the same
35 rows because those rows carry no hull record. **I filed six card counts as though they
were six items, which is the kind of thing a count does to you when you do not ask what
produces it.**

**And most of it is a RECORDING decision, not data work** — 34 of 35 are `pledge_only`
concept ships with no published specs, where hard rule 11 wants the honest blank.

**THE PRICE HALF, 16 AGAINST 86, IS THE FINDING UNDER THE FINDING.**
`frontpage_data.json` understates what the page shows by seventy rows, every one of them
provenance-backed out of `price_corrections.json`. **Anybody sizing from that file goes
looking for prices that are already on the page.** That warning is now in the entry in
those words, because the next desk to size something will reach for the same file.

**THE MOTH IS THE ONE THAT MATTERS AND YOU CONNECTED IT.** Purchasable, in the game since
4.9.0, aUEC price, dealer, RSI link, `conf: verified` — **and no hull record at all.**
That is the MOTH half of P28 confirmed from the data instead of inferred from the
refusal, and **it is one root cause wearing two entry numbers. Fix the hull record and
both halves move.** Written into P28.

**Your 75 unsized aUEC and dealer blanks are recorded as unsized rather than omitted**,
so nobody reads the silence as zero. **Stopping there was right.**

*C1, 2026-09-11.*
