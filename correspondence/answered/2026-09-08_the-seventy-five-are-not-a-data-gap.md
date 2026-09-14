# Memo

To:      Engineering
From:    Build
Date:    2026-09-08
Subject: the ten-ship trial — the API fills ZERO of the 75, because the 75 are not a data gap at all
Status:  Answered

**Your four questions answered, and the headline premise does not survive the
measurement. Nothing written into production.**

**And it cost no network calls.** A completed snapshot of that API was already on
disk — `data-layer/external-sources/api.star-citizen.wiki/snapshots/20260801T021731Z`,
295 vehicles, landed 2026-08-01 by `scripts/external_sources/api_star_citizen_wiki.py`.
Everything below is off that. **It is a month old and its price URLs say
`version=4.9.0-LIVE`**, which is fine for shape, keying and coverage and NOT fine
for judging a price disagreement — flagged where it matters.

---

## THE HEADLINE: THE 75 ARE NOT MISSING DATA

    our ships with NO dealer and NO aUEC price      75
      ...carrying a hull key                        41
      ...matched in the API by exact class_name     40
      ...THE API HAS A PRICE FOR                     0

**Zero. The join works perfectly and not one of them has a purchase row.**

Then I checked what those 75 have in common:

    status of the 75 with no price     pledge_only    75
    status of the 179 with a price     purchasable   179

**Perfect separation.** The 75 are pledge-only ships. **They cannot be bought in
game, so there is no in-game price to find — from this API, from UEX, from
Fleetyards, or from CIC clicking 253 pages.** Our data is already correct on
this axis; a blank is the true value.

*"Know where to buy, before you fly"* is not failing 75 ships. It is telling the
truth about 75 ships you cannot buy.

**So please do NOT brief CIC on them.** That is the one route that would spend a
human's time looking for something that does not exist.

## AND IT WOULD LOSE ELEVEN PRICES WE ALREADY HAVE

    ships where WE have a price and the API does not      11 of 178

An import that trusted the API over our rows would blank those.

---

## 1. WHAT IT FILLS, across all 254 rather than only the ten

    field    missing    API would fill
    cargo      156          120
    usd         87           76
    url         25           10
    L           35            0
    crew        35            0
    vmax        67            0
    career      35            0

**The four zeros are the same 35 ships** — the ones with no hull key, which
therefore do not join at all. The API is not missing that data; we have nothing
to join it to.

**So the genuine yield is cargo, pledge USD and a few pledge URLs.** Real, worth
having, and not the thing the memo was about.

## 2. DISAGREEMENTS: ZERO ON THE TEN — AND THAT IS NOT REASSURING

Every field we both hold matched exactly, including all six prices.

**That is because it is not an independent source.** The field is literally named
`uex_prices`, and the terminals are UEX terminal codes — `NDLOR` = New Deal,
Teasa Spaceport, Lorville. **This API re-serves UEX**, which we already hold
directly at `data-layer/external-sources/uexcorp`.

**Rule 16 matters here:** importing prices from it would not add a second source,
it would add the same source at one remove — and make a future disagreement
between "two sources" impossible to interpret. Your Fleetyards pull IS
independent of UEX. This is not.

## 3. HOW IT KEYS — exact, and no fuzzy matching needed

    api vehicles                    295
    distinct class_name values      295
    class_name claimed twice          0
    our ships with a hull key   219 of 254
    joined on class_name, case-folded, EXACT   218
    unmatched                         1

**Case-folding is the only normalisation and it produced no collisions**, so
rule 17 has nothing to object to. One ship with a hull key did not match; it is
named in the trial output and is a finding, not a rounding error.

## 4. WHAT IT DOES NOT CARRY

    confidence  ABSENT      last_verified_patch  ABSENT
    notes       ABSENT      status               ABSENT
    silhouette  ABSENT      role/career/speed    present

**`confidence` and `last_verified_patch` being absent is the important pair.**
Every row we imported would need both attached by us at import time — the credit
and the read date do not come with the data.

Also: **127 of 295 API vehicles have no purchase row at all**, so this is not a
price source for 43% of what it carries.

---

## WHAT I RECOMMEND, AND IT IS NOT WHAT YOU ASKED FOR

**Do not run the 254-ship pull for prices.** It fills none of the gap that
prompted it and duplicates a source we already hold.

**A small import IS worth doing** — cargo on 120, pledge USD on 76, pledge URL on
10 — with source, read date and `last_verified_patch` on every row, handled like
`commodity_guids.json`. That is a separate authorisation and I have written
nothing.

**The 35 with no hull key are the real join gap** and no API fixes that. They are
ours to key.

## What I checked and what I did not

**Checked:** the snapshot's 295 vehicles across six pages; the class_name join
both directions; the status split on all 254; the eleven where we have a price
and it does not; the field-by-field fill counts; the `uex_prices` provenance from
the terminal codes.

**Did NOT check:** anything live — no network call was made, so I cannot say
whether the CURRENT API differs from this month-old snapshot. **If you want the
prices re-confirmed against today, say so and I will pull the ten live.** I did
not, because the snapshot answers all four of your questions and the fifth
question — "is it current" — was not one of them.

---

ANSWERS:

**Architecture, 2026-09-08.**

**Accepted and closed. B4 is withdrawn.** I called the 75 price-less ships a defect and they are not one: all 75 are `pledge_only` and all 179 priced ones are `purchasable`. **The API filling zero of them is the correct outcome, not a failed trial.** This was the third of four wrong-population errors in one week and it is recorded as such.
