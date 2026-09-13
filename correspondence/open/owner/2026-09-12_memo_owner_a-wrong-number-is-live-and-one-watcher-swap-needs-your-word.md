# Memo

To:      Owner (Sleven)
From:    Architecture (C1)
Date:    2026-09-12
Status:  Open
Subject: A wrong number is live on the loadout page. And one watcher change needs your word.

**Both came out of Code's two replies tonight. Everything else in them is ruled and ordered and
does not need you.**

---

## 1. THE PAGE IS SHOWING A FIGURE THAT IS NO LONGER TRUE

**The loadout bench says it reproduces CIG's pilot DPS on "272 of the 275 ships".**

**That sentence is typed into the page by hand, and the generator's latest run says 277 and
zero.** Nobody invented it — somebody typed a true number and then the data moved underneath it.

**It is live now and it is wrong in the direction that flatters us**, which is the worst
direction for a site whose whole argument is that it does not do that.

**Ordered, and it needs nothing from you:** the count is emitted by the generator and printed by
the page. No hand-typed figure survives in that sentence.

**A second one alongside it, same job:** the page says "Pilot DPS" and means the *sustained*
column. Most other tools quote CIG's *burst* column, which is a different and larger number. **A
visitor who checks us against Erkul today finds a mismatch and concludes we are wrong.** The page
will say sustained, in that word.

**And the good news on the question I sent Code:** our data is exactly what its name says. No unit
mix anywhere, 181 of 181 weapon parts consistent. **The trust mark is arithmetically sound — it
just claims less than it appears to**, which is the wording question already with Echo.

---

## 2. WHAT NEEDS YOUR WORD

**Code has brain two v0 scoped and prototyped already.** Real numbers, from a real example page
generated off tonight's tree:

    the page              115 lines, about 1,700 tokens
    one regeneration      0.09 seconds
    what it replaces      about 115,000 tokens

**About one and a half per cent of the boot read.** It is so cheap to rebuild that it does not
need to detect changes at all — it just regenerates from the whole tree every cycle, so there is
nothing to miss. That is better than what I ordered and I took his design over mine.

**The change that is yours: it touches the watcher.** `LATEST_HANDOFF.md` has a "CURRENT STATE
(auto)" section that is known wrong — it currently says 4 ships where the front page has 253.
**The plan is to delete that section and have the watcher write the new boot page instead, as its
own clearly named file, with one line in LATEST_HANDOFF pointing at it.** One current page, one
writer.

**That is the only part waiting on you. Say go and it is scoped to build.**

---

## 3. THE THING THAT MAKES THIS SAFE, AND CODE FOUND IT BY BREAKING IT

**His prototype printed a confidently wrong fact on its first run** — a parser lifted the word
"verified" out of ordinary prose and printed it as a date.

**His own conclusion is the best line anyone has written on this project tonight:** *a digest can
be confidently wrong, and a desk that trusts it stops reading the deep file.*

**So v0 does not go live until a planted change to every source moves the page, and a missing
source shows as missing rather than as a blank.** That is now a ship condition, not a nice-to-have.

**It already works once:** the example found `LATEST_HANDOFF` and the front page disagreeing, and
named both sources instead of picking one.

ANSWERS:
