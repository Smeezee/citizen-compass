# Memo

To:      Engineering
From:    Research
Date:    2026-09-06
Subject: Pass 1 done — the store is 253 ships, not 70, and the default view hides the other 183. Pass 2 not started.
Status:  Answered

**Data written to the claude.ai project as `claude/CIC_rsi-price-sweep-2026-09-06.md`,
one JSON object, nothing around it. This memo is the part that would not fit in it.**

## The thing that would have made Pass 1 wrong

`/pledge/ships` redirects to `?sale=true`. That view is **4 pages, 70 ships**, and it is
what anybody lands on.

Setting `sale=false` gives **10 pages, 183 ships**.

**The two sets are DISJOINT. Zero overlap, checked by name.** `sale=true` is what is
currently purchasable; `sale=false` is everything else. Neither is the whole store.

    sale=true    70
    sale=false  183
    overlap       0
    total       253

Every row in the JSON carries a `store_view` field saying which sweep it came from,
because "price shown" means a different thing in each — one is a live purchase price,
the other is a listed value on a ship you cannot currently buy.

**I swept both and merged them. That is not a different method, it is the whole ship
list the order asked for.** Reporting it because taking the default view would have
handed you 28% of the store looking like 100%.

## Nulls and zeros

**One true null across all 253: `F7A Hornet Mk II`.** Its card has no price element at
all — not a blank, not a zero, the node is absent. Recorded as `null`.

**No ship anywhere showed $0.** Checked explicitly. So in Pass 1 the null/zero
distinction has exactly one case and it is a null.

Every other row carries a price and the currency is USD throughout.

## Pass 2 — not started, and there is a second reason beyond the gate

The order gates Pass 2 on you naming ships. You have not, so it is correctly unstarted.

**But it would also have been blocked.** The priced variant grid — the "Select ships to
compare" panel — only renders on a wide window. The browser pane here is **466 px**, and
at that width the same control degrades to a plain dropdown listing variant names with
**no prices at all**. Forcing a 1600 px emulated viewport did not populate it either.

So when you send the list, Pass 2 needs either a genuinely wide browser window or a
different reader. **I have not improvised one.**

## Two observations for whoever picks the Pass 2 list

**The matrix may not add prices.** On `F7C Hornet Wildfire Mk I` I could read the seven
variant names from the narrow-width dropdown, and the six prices visible in Sleven's own
screenshot of the wide view match the Pass 1 store prices exactly, ship for ship. **On
that one ship the matrix adds the parent-to-variant relationship, not new prices.** One
ship. Not a claim about the rest.

**`F7A Hornet Mk II` is the ship worth putting first on your list.** It is the only
priced-null in the store, so its variant matrix entry is the one place a price for it
could exist. If the matrix shows a figure there, the matrix carries something the store
list does not — and that settles whether Pass 2 is worth running across 253 ships or
only across the handful with gaps.

## Method and limits

Read with a real browser at the pane's own width; names, prices and hrefs taken from the
page's own elements — `c-shipCard__title`, `a-priceUnit__amount`, `a-priceUnit__currencyCode`
— not parsed out of running text, so nothing was tidied or reconstructed. Clock read from
the machine: 2026-09-06.

**No failures. Every page of both sweeps loaded first time; the `failures` array is empty
and that is a measured empty, not an unrun check.**

**Not checked:** any variant matrix; whether a third store filter exists beyond
`sale=true`/`sale=false`; whether the 253 total matches any count the store states about
itself, because it states none that I found.

---
ANSWERS: C1, 2026-09-06.

Applied. 79 corrections through `price_corrections.json` — 70 prices we never
held and 9 that had drifted — each row carrying its RSI source, the store view it
came from and the read date. **The front page went from 167 priced cards to 237.**

The finding that outlives the numbers is yours, not the prices: **the store's
default view is filtered to what is on sale and the two lists are disjoint.**
Anyone sweeping the page they land on collects 70 ships and never learns the
other 183 exist. That is now on file so it cannot be rediscovered a third time.

Full answer to your four questions in
`docs/RESPONSE_to-cic-four-questions-on-the-sweep-2026-09-06.md`.
