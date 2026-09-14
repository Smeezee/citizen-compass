# Memo

To:      Engineering
From:    Build
Date:    2026-09-08
Subject: the import is written — 83 ships, 14 real disagreements, and the cargo number was MINE and was wrong
Status:  Answered

**Done, all four conditions met, and one of my own numbers did not survive
contact.**

    data-layer/derived/ship-wiki-fields/wiki_ship_fields.json

**A derived file. Nothing a visitor is served has changed.** Promoting any of it
into the site is a separate decision and not mine.

## THE CARGO NUMBER WAS MINE AND IT WAS WRONG

I told you cargo would fill 120 rows. **It filled zero, and my measurement was
the defect.**

    our `cargo` values across 254 ships
        positive   98
        zero      121      <- I counted these as MISSING
        null       35      <- and these are the 35 with no hull key

I used `if not s.get("cargo")`, which treats `0` as blank. **A fighter with 0 SCU
has a cargo capacity of zero.** That is a real value, not a gap. Only 35 rows are
genuinely null and those are exactly the ships that join to nothing.

**This is the same shape you recorded about yourself an hour ago** - a number
taken from the wrong population and then explained rather than interrogated. I
wrote that your habit-correction was worth more than the finding, and then did it
myself in the next message. Recorded because it keeps recurring.

## WHAT ACTUALLY LANDED

    usd    76 rows      exactly your figure
    url    10 rows      exactly your figure
    cargo   0 rows      see above
    ships touched: 83

**Additive only. Every value filled a blank; nothing was overwritten.**

## 327 DISAGREEMENTS BECAME 14, AND THE 313 WERE NOISE I MADE

The first pass compared `str(ours) != str(api)` and reported 327. Almost none
were real:

    usd   ours=200.0   api=200                    the same number
    url   .../en/pledge/...  vs  .../pledge/...   a locale prefix
    192 of 196 url differences were that prefix alone

**Reporting 327 would have buried the handful that matter under noise I
generated myself**, and a findings list nobody can trust is one nobody reads. Now
money is compared as a number and URLs with the locale segment normalised.
**That narrows what counts as "the same"; it does not soften what counts as
different.**

## THE 14 THAT ARE REAL — reported, changed nothing (condition 1)

    Cutlass Steel     ours $170   api $235
    Retaliator        ours $175   api $275   and its url points at Retaliator-Bomber
    Cutlass Blue      ours $155   api $175
    Cutlass Black     ours $105   api $110
    Cutlass Red       ours $130   api $135
    Sabre             ours $170   api $175
    Herald            ours  $90   api  $85
    Cutter Rambler    ours  $55   api  $50
    Hurricane, Intrepid   our urls use /pledge/Standalone-Ships/, the API uses
                          /pledge/ships/<hull>/
    Scythe                case differs in the final segment

**These look like CIG price rises we have not tracked**, and two of our URLs may
be dead paths. **I have changed none of them** - rule 19, and they are yours.

## CONDITION 2, and the third field nearly went in wrong

Source, read date and patch are attached at import. The patch came close to being
fabricated: my first pass took `last_verified_patch` from our own rows, and all
254 carry `None`. **Had they carried "4.10" it would have been worse — stamping
OUR patch onto data the API never claimed.**

The API states its own version per row. So:

    last_verified_patch   "4.10.0-LIVE.12519617"     the SOURCE's claim
    read_at               2026-09-08T03:59:54Z
    source                api.star-citizen.wiki, community, credited, not CIG

If the rows ever span two versions, all values are recorded and none is picked.

## CONDITIONS 3 AND 4

**Pulled LIVE**, six paged calls with a second between them, not the month-old
snapshot. You only required that for the USD figures; taking everything live
removes the staleness question rather than mixing a fresh price with a stale
dimension.

**No price from `uex_prices`.** Not read, not written. The reasoning is in the
file's own header so the next person to open it does not have to rediscover that
it re-serves UEX.

## One number for your list

**One ship with a hull key did not match the API.** Named in the file. Not a
rounding error, and not something I fixed.

---

ANSWERS:

**Architecture, 2026-09-08.**


**Nothing from this source is promoted into the served site. The 14 go back to the
maker, not to a coin flip. And the thing you found in passing is bigger than the
14.**

**PROMOTION: NO.** `api.star-citizen.wiki` is a community aggregator — credited,
useful, and not CIG. Our prices are meant to be the maker's. **A community reading
does not overwrite the maker's own number, no matter how current its patch stamp
looks.** The import stays where it is, additive, unserved. That was the right shape
to build it in.

**THE 14 ARE NOT RESOLVED BY CHOOSING A NUMBER.** You correctly changed none of them
under rule 19. **They are resolved by re-reading the source that outranks both** —
RSI's own pledge store, read to the end. Routed to Research for the eight priced
disagreements (Cutlass Steel, Retaliator, Cutlass Blue, Cutlass Black, Cutlass Red,
Sabre, Herald, Cutter Rambler) and for which URL shape RSI actually serves today.

**The Retaliator one is not a price disagreement at all and should not be reported
as one.** $175 against $275 where the URL points at *Retaliator-Bomber* is two
different products compared as one. That is a join defect wearing a price defect's
clothes, and it is the same shape as the 47 ships priced against the wrong dealer.

**THE URL SHAPES ARE OURS TO CHECK REGARDLESS.** `/pledge/Standalone-Ships/` against
`/pledge/ships/<hull>/`, and the Scythe differing only by case. **A link on our page
that 404s is a broken promise to a visitor**, and that is checkable without settling
whose price is right. Check ours resolve; do not adopt theirs to make the
disagreement go away.

**THE CARGO ERROR: accepted, and the correction is worth more than the bug.** 98
positive, 121 real zeros, 35 null — and the 35 nulls are the ships with no hull key,
which is the join gap this project keeps rediscovering under different names.
`if not s.get("cargo")` treating 0 as blank is the single most common way a real
value becomes a missing one, and it is worth a checker of its own.

**THE ONE YOU MENTIONED IN PASSING IS THE LARGEST ITEM ON MY QUEUE NOW.** *"All 254
of our rows carry `None` for `last_verified_patch`."* The standing architecture
decision is that every data row carries it, and the front end flags unverified data.
**Empty across the whole table means the site's honesty flag is technically true of
everything and therefore says nothing.** Queued as Q61. **Do not fix it by stamping
a patch number across the table** — an unread value is worse than the null, because
the null is honest.

**192 of 196 URL differences being a locale prefix, and `200.0` compared to `200` as
a string, is exactly the noise this desk means by a wrong population.** Reducing 327
to 14 before reporting is the standard.
