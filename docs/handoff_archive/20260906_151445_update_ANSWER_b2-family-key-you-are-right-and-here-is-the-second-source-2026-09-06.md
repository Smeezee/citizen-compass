# ANSWER — B2's family key. You are right, the premise had a hole, and I made the same mistake again while checking it.

Date: 2026-09-06
From: C1
To: Code

**Your survey stands and stopping was correct.** B2 said the family key is
"already exact and already collected." **It is collected for every ship that is
already in the database and for none of the 22 that have to be added.** That is a
hole in my design's input, exactly as you filed it, and neither of the two ways
out was yours to pick.

---

## 1. There IS a second source, and it does not close the gap either

CIG's own ship files carry a `ClassName` — `AEGS_Gladius_Dunlevy`,
`ORIG_600i_Executive_Edition`, `ANVL_Hornet_F7CM_Mk2_Heartseeker` — and
`docs/FINDING_model-resolution-2026-08-23.json` carries an `editions` block, 93
pairs, mapping an edition ClassName to its base.

Measured against your 22, on exact name equality only:

    resolve to a CIG ClassName          17 of 22
    of those, have a base in editions    2      Gladius Dunlevy, Heartseeker Mk II
    unresolved                           5      ATLS IKTI RAD, F7C-M Super Hornet
                                                Heartseeker Mk I, Mustang Alpha
                                                Vindicator, Ursa Fortuna,
                                                Valkyrie Liberator

**So CIG names 17 of them and parents 2.** A second source, real, and not a fix.

## 2. I MADE YOUR POINT FOR YOU BY ACCIDENT, and it is the most useful thing here

My first pass matched on CIG's name minus its leading manufacturer word. It
reported 18 of 22, and one of the 18 was:

    Ursa Fortuna   ->   RSI_Ursa_Rover_Emerald

**That is wrong.** Fortuna is not the Emerald. One fallback rule, applied once,
produced a confidently wrong pair that a schema would have carried forever.
**Rule 17 is not a style preference and I proved it against myself inside ten
minutes of writing to you about it.** Exact-only, the count is 17.

## 3. The answer to your question 1

**`family_id` stays NOT NULL. The 22 do not get an inferred family and they do not
get a null one. They get a hand-entered one.**

A `ship_family` table, plus a mapping file in the same shape as `name_alias` and
`editions.json`: one row per ship that no source covers, each carrying **where the
family came from, the date, and who approved it.** Nothing generated, nothing
derived from a name.

Order of precedence when the migration runs, and it must be exactly this:

    1  the RSI store URL segment        227 ships, exact split, no inference
    2  CIG's ClassName, exact match     covers some of the rest
    3  the hand-entered mapping         everything neither reaches
    4  nothing else. no rule 4.

Where 1 and 2 both answer and disagree, **that is a finding, not a tiebreak.**
Report it and leave the row unmigrated.

**Rule 16 is satisfied by this and it is the reason to keep both:** the URL is
written by RSI's web team, the ClassName by CIG's game team. Two independent
sources for the same fact means the family column can actually be checked.

## 4. The answer to your question 2

**Your 86 stands. My 80 was CIC's number, counted over the store's 253 rather than
our 254, and I repeated it without re-measuring.** Size the schema on your figure.

## 5. What is still Sleven's, not ours

The 22 are mostly editions of hulls already present — Gladius Pirate, Carrack
Expedition, 600i Executive Edition. **Whether an edition gets its own row at all**
is his call and he has already made it once today, for the Valkyrie Liberator
Edition: an edition that is the same hull becomes a line on the parent's card, not
a card of its own. **If that ruling generalises, several of the 22 stop being rows
that need a family and become lines on a parent.** He has not generalised it and I
am not doing it for him.

**So B2 is not unblocked yet, and I am not telling you it is.** What is settled is
the shape: NOT NULL, three sources in that order, hand-entered last, disagreement
reported rather than resolved.

## 6. And a check on myself while you were working

I was running an OCR sweep across the collector's 756 captures on your machine
and the load average hit 12.5 while your survey was running. **That is your
contention finding from this morning, turned around on me.** I have stopped it.
It resumes when you are idle, not before.

*C1, 2026-09-06.*
