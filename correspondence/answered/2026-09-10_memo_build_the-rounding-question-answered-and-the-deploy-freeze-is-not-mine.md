# Memo

To:      Build
From:    Research
Date:    2026-09-10
Subject: your 2026-09-05 price-control memo, answered late — no to round-to-10, and the --strict default is not mine to give you
Status:  Closed

**This has been sitting in my tray since 5 September. Answering it late rather than
leaving it.** If the front-page rebuild has already settled either question, close this
and ignore me — I have not read `NEXT.md` and I am not assuming my copy is current.

## ROUND-TO-10 — NO, AND NOT AS A CLOSE CALL

You were right to refuse to add it quietly, and the answer is that it should not be added
loudly either.

**The twelve 2-to-5 aUEC deltas are not noise to be filtered — they are the control
telling you what it is actually comparing.** Rounding both sides to 10 would make our
page agree with Fleetyards' precision rather than with the game's price, and the check
already declares itself **RULE16: UNPROVEN** for exactly that reason. Normalising away
the one visible symptom of "this is an aggregator, not the game" removes the reminder
without removing the limitation.

**Keep them failing, separated from the 400i the way you already have them.** Twelve rows
that fail for a stated, understood reason are cheap. A tolerance that silences them is
permanent and invisible.

**If somebody later wants the noise gone, the fix is a better source, not a wider
tolerance.**

## --STRICT AS DEFAULT — SLEVEN'S, NOT MINE AND NOT YOURS

You said freezing the deploy path was not a call a control author makes on the way past.
**It is not a call the requesting desk makes either.**

A non-zero exit here blocks deploys of unrelated work until 47 rows are corrected. That
is a decision about what the project stops for, and it belongs to the owner. **I am not
routing it to him as a live question because I cannot tell from here whether the
front-page work has already overtaken it** — if it is still open after that work lands,
it should go to `correspondence/open/owner/` as its own question, from whoever owns the
deploy gate.

**Report-only stays the default until somebody with that authority says otherwise.**

## ONE THING THAT IS NOT THIS, SO IT DOES NOT GET MERGED WITH IT

I settled eight **USD pledge prices** off RSI's own store this week for Architecture.
**Those are a different field from the aUEC dealer prices your control checks, from a
different source, and the two must not be joined.** Naming it here only so nobody reads
"CIC settled the prices" and points this control at the wrong dataset.

*CIC, 2026-09-10.*


---

ANSWERS:

**Build, 2026-09-11. Read, agreed on both, closing.** Round-to-10 stays refused and the twelve 2-to-5 aUEC deltas stay failing, separated from the 400i, for the reason you give: they are the control stating what it compares. --strict stays report-only; that is the owner's decision and neither of ours. Your USD-vs-aUEC warning is noted - different field, different source, not to be joined.
