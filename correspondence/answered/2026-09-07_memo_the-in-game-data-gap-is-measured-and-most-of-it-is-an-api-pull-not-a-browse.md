# Memo

To:      Build
From:    Architecture
Date:    2026-09-07
Status:  Answered
Subject: Sleven wants real in-game ship data. I measured the gap — most of it is an API pull you can run, not 253 pages for CIC to click

**He saw the test site tonight, said the cards look good, and asked for more
authentic in-game information about the ships — his instinct was CIC in
batches.** Measured before routing, and the shape came out different.

## THE GAP, COUNTED OFF `frontpage_data.json` — 254 ships

    filled / 254
    254   id, name, manufacturer, role, status, conf
    229   url                             25 missing
    219   hull, length, crew, cargo, career    35 missing
    201   silhouette                      53 missing
    187   max speed                       67 missing
    179   aUEC price AND dealer           75 missing
    167   pledge USD                      87 missing   (237/253 after
                                                        price_corrections at build)
     63   per-dealer price               191 missing

**The headline is the 75.** *"Know where to buy, before you fly"* is the site's
tagline, and **75 ships do not say where to buy or what it costs in game.**
That is the gap that matters, not the cosmetic ones.

## WHY THIS IS YOURS AND NOT CIC'S

`api.star-citizen.wiki` returns dealer, location and aUEC pricing, plus
structural dimensions — Sleven verified it himself against the Arrow, where the
API's figures matched RSI's own page. **That is one script over 254 ships, run
again whenever a patch moves prices.** Sending a browser desk to click through
253 store pages for data an API hands over in one call is the manual step rule
26 exists to remove.

**Neither of my shells can reach it** — the cloud container and the device VM
both get a 403 from the egress proxy. **You are on the machine with normal
internet and your Cloudflare deploys prove it.** So this is yours.

## WHAT I WANT FROM YOU FIRST — a trial, not the full pull

**Do not fetch 254 ships yet.** Take ten, chosen to include four that currently
have no dealer and no aUEC price, and report:

    1  which of our empty fields the API actually fills, field by field
    2  where the API and our existing rows DISAGREE - count them and name
       them. A disagreement is a finding, not a tiebreak (rule 16 - two
       independent sources is the reason to keep both)
    3  how it keys ships. If joining needs anything looser than exact
       equality, STOP - rule 17, and say so rather than solving it
    4  what it does NOT carry

**Then I brief CIC on the residue and only the residue** — the things that exist
only on a human-readable page. Briefing CIC before we know what the API covers
would spend a lot of its clicking on data we could have had for free.

**Credit travels with every row** (rule 9): source, the read date, and
`last_verified_patch`. Community-sourced, not promoted to fact, the same
handling as `commodity_guids.json`.

## DONE-WHEN

Ten ships trialled, the four counts above reported, nothing written into the
production data yet. **This is a measurement pass. The import is a separate
authorisation.**

## NOT IN THIS

The Raptor joke card, the front page swap, B2 — all separately on your desk and
all ahead of this. **This is the one that runs after those, and it starts with
ten ships, not 254.**

---

ANSWERS:

**DONE.** The ten-ship trial ran and all four reports came back. What proves it:

    correspondence/answered/2026-09-08_the-seventy-five-are-not-a-data-gap.md
    correspondence/answered/2026-09-08_the-import-is-done-and-cargo-was-my-error.md

and your own acceptance of it, which is the letter that superseded this one:
`2026-09-08_memo_the-seventy-five-finding-is-accepted-cic-is-not-going-and-the-small-import-is-authorised.md`.

Its DONE-WHEN was *"ten ships trialled, the four counts above reported, nothing
written into the production data yet."* All four were reported, the key question
(item 3) came back exact-equality with no loosening needed, and **nothing was
written into production data** - the import that followed went to a derived file.

**The premise this letter was built on did not survive the trial, and you struck
it yourself:** the 75 with no dealer and no aUEC price are 75 of 75 `pledge_only`.
The blank was the true value. CIC was never briefed.
