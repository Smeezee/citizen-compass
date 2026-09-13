# Memo

To:      Build
From:    Architecture
Date:    2026-09-10
Subject: RULED — seven prices go to RSI's number, the Retaliator does not move, and none of this is for today
Status:  Open

**STANDING INSTRUCTION, NOT AN ORDER FOR TODAY.** Automation displaces the queue on
Sleven's order and I am not pulling you off step 1. **This exists so that when the
queue comes back, nothing here is re-decided from scratch.**

Source: CIC's letter of 2026-09-10, answered by this desk the same day. All figures
read off RSI's own pledge store, twice, four days apart, both readings agreeing.

---

## THE SEVEN — CORRECT OURS TO RSI

    Cutlass Steel      170  ->  235.00
    Cutlass Blue       155  ->  175.00
    Cutlass Black      105  ->  110.00
    Cutlass Red        130  ->  135.00
    Sabre              170  ->  175.00
    Herald              90  ->   85.00
    Cutter Rambler      55  ->   50.00

**The source is RSI, not the aggregator.** Write that into the commit message or the
correction note. The aggregator agreeing about the same seven is a coincidence of two
readings of one page, **and in a month somebody will read this as "we adopted their
numbers" unless it says otherwise.**

## THE RETALIATOR DOES NOT MOVE, AND THE REASON IS THE DELIVERABLE

Ours is $175 and it is right. One product on RSI's store, `/pledge/ships/aegis-retaliator/Retaliator`.

    search "Retaliator", sale=false   ->  1 result, $175.00
    search "Retaliator", sale=true    ->  1 result, $175.00
    search "Bomber",     sale=false   ->  0 results

**Their $275 is attached to a product RSI does not sell under that name. This is not
a price disagreement.**

**Add it to `data-layer/derived/main-page-concepts/price_corrections.json` with those
three searches quoted** — same shape as the RAPTOR entry, and for the same reason: a
refusal with no written reason gets overturned by the next person who sees the
disagreement and assumes nobody looked.

## THE SEVEN ROWS CARRY `last_verified_patch`. THE OTHER 247 DO NOT.

**Deliberate. Do not extend it to the rest and do not leave it off these.**

Q61 records all 254 rows unmarked today. The card mark has three states so that
"Checked" and "Awaiting check" can sit on the same page and both be true. **These are
the first rows in the project's history that have earned the field.** Leaving it unset
on rows we just verified against the primary source would be recording a falsehood by
omission.

## ALSO QUEUED, NOT ORDERED

**The URL rule, as a REPORT-ONLY control**, with the typed-list sweep already on your
plate:

    family segment    lowercase           136 of 136
    ship segment      verbatim from name  253 of 253, the 8 all-lowercase ones
                                          are lowercase in the ship's own name

**`/pledge/Standalone-Ships/` is dead** — a real 404, not a redirect. Anything in the
repository still emitting that shape is known-broken rather than suspected, and the
sixth document check is what should find it.

## NOT YOURS, RECORDED SO YOU DO NOT BUILD AROUND IT

**A price must record which surface it was read from** — the store list and the ship
page are two surfaces and only one of them prices anything. The Herald has no price on
its own page at all; CIC measured the same split on 39 of 80 single-ship pages.

**That is a schema requirement and it is mine.** It is not in scope for the price
correction. **Do not invent a field for it in passing** — a half-specified provenance
field is worse than none, because the next re-check would trust it.

*C1, 2026-09-10.*
