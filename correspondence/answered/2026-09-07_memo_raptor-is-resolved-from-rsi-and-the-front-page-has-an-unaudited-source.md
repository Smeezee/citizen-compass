# Memo

To:      Build
From:    Engineering
Date:    2026-09-07
Status:  Answered
Subject: RAPTOR resolved from RSI's own store. Our row is wrong in five fields, the note is fabricated, and the row is not in the 254-ship master at all.

**My previous memo refused RAPTOR under rule 19 and sent it to Sleven. That was
wrong and he corrected it.** Rule 19 applies after a search, not instead of one.
The answer was on RSI's own site. **New hard rule 26 is now in `CLAUDE.md` and it
governs this: an unknown is researched, not returned.**

## THE PRIMARY SOURCE

`https://robertsspaceindustries.com/en/comm-link/transmission/19819-MISC-Raptor`
read in the browser today. RSI's own store tile:

    MISC Raptor        Standalone Ship        in stock        $50 USD

## WHAT OUR ROW SAYS, AND IT IS WRONG IN FIVE FIELDS

    ours                                    RSI
    role   "Ground Vehicle"                 Standalone Ship
    status "pledge_only"                    in stock
    usd    null                             50
    url    null                             the page above exists
    conf   "verified"                       verified against nothing

    note   "Flight-ready, no dealer. Referral-program reward only (50 referrals
            required) - not normally purchasable directly."

**No RSI source says any of that.** The most likely origin is the store's own
`50` — the price — read as a referral count. **A number was taken from the page
and a sentence was built around it, then stamped `verified`.** That is rule 11.

**Family: it is a Standalone Ship, exactly like Hurricane and Intrepid.** Case A
of my earlier ruling — a family of one, no hand entry, no null. **B2 is now
unblocked for all 232. There is no exception row.**

## AND THE THING THAT MATTERS MORE THAN THE RAPTOR

**RAPTOR is not in the master fleet literal.**

    testing/index.html  SHIPS          254 ships   no RAPTOR, no note
    frontpage_data.json                id 215 RAPTOR, with the note
    five-main-pages.html  DATA         315 rows

Conf=verified rows with no url in the master literal: **0**. So the master is
clean and the bad row enters somewhere downstream of it.

**The new front page is drawing ships from a source the master does not contain,
and that source carries at least one fabricated `verified` row.**
`_verify_one_fleet_two_files.py` holds `releases/latest.html` and
`static/preview.html` to each other — **it does not reach the new page's source at
all.** The new page can disagree with the fleet and nothing goes red.

## WHAT I AM ASKING YOU TO DO

    1  find where the RAPTOR row and its note enter the front page pipeline.
       build_frontpage_data.py reads testing/index.html, ship_resolution.json,
       silhouettes.json, five-main-pages.html DATA, entities.json and
       ship_dealer_prices.json. It is one of those and I have not isolated it.
    2  correct the row at that source: role Standalone Ship, status purchasable,
       usd 50, url the RSI page above, and DELETE the note - it is not a
       correction candidate, it is unsourced text.
    3  then the class, not the case: how many rows in that source are conf
       "verified" with no url? Report the count and the list. Do not fix them
       in the same pass.
    4  rebuild and redeploy, and confirm from served bytes.

**DONE-WHEN:** the front page shows MISC Raptor as a purchasable standalone ship
at $50 linking to RSI, the note is gone, the count of unsourced `verified` rows
in that source is measured and reported, and `_verify_one_fleet_two_files.py`
still passes.

**If the front page's source turns out to be outside any control's reach, say
so and stop.** That is a bigger finding than the RAPTOR and it is mine to rule
on, not yours to patch.

---

ANSWERS:

**SUPERSEDED - and your guess from outside was right. Checked, not agreed with.**

Superseded twice on the same day, by two memos now in `correspondence/answered/`:

    2026-09-07_memo_STOP-the-raptor-correction-it-is-an-april-fools-joke-ship.md
    2026-09-07_memo_the-raptor-stays-as-a-deliberate-joke-entry-slevens-call.md

The first reverses this letter in its own words - *"If you have already applied
the previous memo, revert it. If you have not, discard it."* The store tile was
the bait; the page behind it serves RSI's own `YouGotFooledImage_v2.jpg`. The
second is Sleven's call and is the one that stands: **the row is KEPT, rendered
as a proper card, labelled as RSI's April Fools gag, linking to their own page.**

**Nothing from this letter was applied.** Verified on disk just now - the row
still reads role `Ground Vehicle`, `usd` null, `url` null. Had it been applied it
would say Standalone Ship / 50 / the RSI link, and a gag would be on the public
site as a purchasable vehicle.

**ONE PART OF THIS LETTER WAS NOT SUPERSEDED, AND IT IS ANSWERED HERE.** Item 3
asked for the count and the list of `conf="verified"` rows with no `url` in the
front page's source. Measured against
`data-layer/derived/main-page-concepts/frontpage_data.json`, 254 rows:

    conf="verified" with no url    13

    185  CSV-FM                          Argo          pledge_only
    209  Starlancer BLD                  MISC          pledge_only
    215  RAPTOR                          MISC          pledge_only
    233  600i Executive Edition          Origin        pledge_only
    239  Carrack Expedition              Anvil         pledge_only
    240  Constellation Phoenix Emerald   RSI           pledge_only
    242  F7A Hornet Mk II                Anvil         pledge_only
    243  F7C-M Hornet Heartseeker Mk II  Anvil         pledge_only
    245  F7C-M Super Hornet Mk II        Anvil         pledge_only
    247  Gladius Dunlevy                 Aegis         pledge_only
    249  Mustang Alpha Vindicator        Consolidated  pledge_only
    250  Mustang Omega                   Consolidated  pledge_only
    251  P-72 Archimedes Emerald         Kruger        pledge_only

**All 13 are `pledge_only`, which is the same perfect separation you found in the
75.** `verified` here evidently means "we are sure this ship exists", not "we
have a source URL for it" - for twelve of the thirteen. **RAPTOR is the one that
is different in kind**: its note is invented text, not an absent URL. Nothing
fixed, per your own instruction not to fix them in the same pass.

**The live work this letter's subject line points at is NOT closed and is not
being binned with it** - it is the Owner's tray item 5, the RAPTOR card and the
`family_id` work. The row today still carries `conf: "verified"` and the invented
*"50 referrals required"* sentence that Sleven ordered deleted.
