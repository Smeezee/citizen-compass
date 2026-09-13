# Memo

To:      Build
From:    Architecture
Date:    2026-09-07
Status:  Open
Subject: RULING on the five — they are three different cases, `family_id` stays NOT NULL, and four of the five are sourceable. Only RAPTOR is refused.

**You are unblocked on 231 of 232. B2 can proceed for everything except one row.**

## THE HEADLINE, AND I ALMOST GOT IT WRONG

Sleven's words when I put the five to him: *"those aren't families. Those are
models."* I took that to mean the schema was wrong and was ready to rule that
`family_id` should become nullable. **I would have changed an accepted design on a
premise I had not measured.**

Then I measured. **The 09-06 ruling stands unchanged: `family_id` NOT NULL, three
sources in order, disagreements reported rather than resolved.** No schema change.

What was actually wrong is that the five were treated as one problem. They are
three, and two of them were never blocked at all.

---

## CASE A — Hurricane and Intrepid. NOT BLOCKED. Source 2 already reaches them.

Your survey said *"Source 2 does not reach them either"*, measured by searching
`docs/FINDING_model-resolution-2026-08-23.json` — the **editions** block, 93
pairs. That file maps an edition to its base. **A ship with no editions is
correctly absent from it, so absence there proves nothing about whether CIG names
the ship.**

CIG does. It is already on our own rows:

    Hurricane   hull = ANVL_Hurricane    url /pledge/Standalone-Ships/Hurricane   $210
    Intrepid    hull = CRUS_Intrepid     url /pledge/Standalone-Ships/Intrepid    $65

**The ClassName is stored on the row. There is no matching step, no prefix
stripping, nothing for rule 17 to object to** — it is a field being read.

Cross-checked against CIG's 4.10 ship data for anything sharing the stem:

    ANVL_Hurricane            and its own countermeasure items, no other hull
    CRUS_Intrepid             plus CRUS_Intrepid_Collector_Indust

**Hurricane is a family of one.** **Intrepid is a family of one plus a Collector
paint**, and by Sleven's own fold rule — *"paint and nothing else folds into the
parent"* — that paint is a line on the Intrepid's card, not a second member.

**Note also that Intrepid is CRUSADER, not Drake.** I believed Drake before I
looked. Worth stating because it is exactly the sort of thing that gets written
into a hand-entered mapping from memory and never questioned again.

**A single-hull ship's family is itself.** That is not an invention and not a
null — it is the fact, and it is what Sleven meant by "those are models".

## CASE B — CSV-FM and Starlancer BLD. Source 3, with two independent citations each.

Neither is in the game and neither has a store page, so sources 1 and 2 both
correctly return nothing. They are what source 3 was designed for. **But they are
not unknowns** — two independent records already state the line, which is rule 16
satisfied:

    CSV-FM          our row's own note: "Concept cargo CSV variant"
                    CIG 4.10 ship data:  ARGO_CSV_Cargo
                    -> family CSV

    Starlancer BLD  our row's own note: "Concept construction variant of the
                                         Starlancer line"
                    CIG 4.10 ship data:  MISC_Starlancer_Max, MISC_Starlancer_TAC
                    -> family Starlancer

**The line demonstrably exists in CIG's own files in both cases.** The hand-entered
row records the family, both citations, today's date, and Sleven as approver —
exactly the shape the 09-06 ruling specified. Nothing is derived from a name.

**Sleven did not know what BLD was** and said so rather than guessing. It is the
construction variant of the Starlancer line, per our own note. If that note's
origin cannot be traced, say so and I will have it re-sourced rather than let it
harden into a fact.

## CASE C — RAPTOR. REFUSED under rule 19. This one needs Sleven.

I expected to find it was not a ship at all. **That was wrong and the data said
so before I wrote it down.** Its own record explains itself:

    id 215   n RAPTOR   m MISC   role Ground Vehicle   status pledge_only
    conf "verified"
    note "Flight-ready, no dealer. Referral-program reward only (50 referrals
          required) - not normally purchasable directly."
    url, price, hull, patch, length, crew, cargo, speed  ALL NULL

**It is real and it is a referral reward**, which is why it has no store page —
the same reason the Gladius Dunlevy has none. CIC's full sweep of all 253 store
rows across both views confirms no page exists. CIG's 4.10 ship data contains no
RAPTOR hull; the only Raptor anywhere in the data layer is
`MISL_S04_EM_TALN_Raptor`, **a missile**, which is not it.

So: no store URL, no ClassName, no manufacturer line any source connects it to.
**Three sources, three blanks. Rule 19 says that is refused, not resolved by
picking**, and I am refusing it.

### What that means for the migration

A NOT NULL column cannot be added while one row has no value. **One unsourceable
row does not reshape a schema for the other 231** — making the column nullable to
accommodate RAPTOR would let every future gap in silently.

**Two ways out, and it is Sleven's call, not ours:**

    1  he names RAPTOR's family - one word, and it is sourced to him
    2  RAPTOR comes out of the ships table until a source can answer it,
       and goes on the audit rather than being deleted

I have put it to him. **Do not wait on it.** Prepare the migration for all 232
with RAPTOR held out as the single known exception, prove it on the local
throwaway, and it applies the moment he answers.

---

## WHAT I AM ASKING YOU TO DO

    1  B2 proceeds. Hurricane and Intrepid take their own hull as their family,
       read off the row. No hand entry for those two.
    2  CSV-FM -> CSV and Starlancer BLD -> Starlancer go in the hand-entered
       mapping, each carrying BOTH citations above, today's date, and Sleven
       as approver.
    3  RAPTOR is held out, named in the migration's refusal list with the reason.
    4  Prove it on a local throwaway first, as you planned. Nothing touches the
       production database until that passes.

**DONE-WHEN:** the migration applies with `family_id` NOT NULL, 231 rows filled
from the three sources in order, RAPTOR the only exception and named as one, and
no row's family derived from a name.

## AND A CORRECTION TO YOUR SURVEY, MEANT AS ONE

*"Source 2 does not reach them either"* was measured against a file that could
not have answered the question. **The survey was still right to stop** — the gap
was real for three of the five and stopping was correct. But an absence proves
nothing unless the source searched is the one that would have carried the fact.
That is the same shape as the payout regex: the count was of lines that mentioned
the word, not of lines the reader actually read.
