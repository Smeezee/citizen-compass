# Memo

To:      Architecture
From:    Research
Date:    2026-09-06
Subject: Pass 2 STOPPED with zero rows. The priced variant matrix never rendered in this browser, and ship pages have now stopped rendering at all.
Status:  Answered

**Sleven's instruction was every ship, not a list. I tried to start and could not. Nothing
was recorded, nothing was guessed, and this is a not-performed report rather than a
partial one.**

## What happened, in order

**1. The priced matrix never appeared at any width.** On `F7C Hornet Wildfire Mk I`:

    pane natural width 466 px   the variant control is a DROPDOWN listing seven
                                variant NAMES and no prices at all
    emulated 1600 x 1000        the desktop nav appears with a "Variant Matrix"
                                item, but no element on the page carries a
                                variant class, and the section is absent from
                                the DOM. Page height 3,807 px, ending at
                                technical specs.

Scrolled to the section and to the page bottom, waited, re-checked. **Zero elements
matching `variant` in any class or id.** The nav item pointing at the section exists
while the section does not.

**2. It is not that ship.** Repeated on `Cutlass Black`, a currently-purchasable hull,
at 1600 px: page height 1,000, body text 337 characters, zero price elements. **Less
rendered than before, not more.**

**3. Ship pages have now stopped rendering.** Back at natural width, `Cutlass Black`
returns 262 characters of body text and no price. Earlier in this same session the same
page rendered its price and its variant dropdown correctly.

**Roughly thirty page loads against `robertsspaceindustries.com` preceded this.** I have
stopped rather than keep requesting, because if this is the site throttling me then
continuing makes it worse, and because I cannot tell throttling from a broken pane from
here. **Either way the instrument is not currently giving me the page.**

## What I did NOT do, and will not

**I did not take the variant names from the narrow dropdown and attach prices from
Pass 1.** The names and the prices would have come from two different places, and the
order says a price that is not on the page is `null` and must never be carried over from
elsewhere. Producing 253 rows that way would have looked like a completed Pass 2 and been
a merge.

**I did not query the GraphQL endpoint with an invented query.** Introspection is
disabled — it returns "Internal server error" — so any query shape would have been
guessed. The Apollo cache on a ship page holds one key, `ROOT_QUERY`, containing
`storeFront: "pledge"` and nothing else.

## What is reachable, if the browser recovers

**The variant NAME list, for every ship, with no prices.** At natural width the dropdown
prints them exactly — for the Wildfire: `F7C Hornet Wildfire Mk I`, `F7C Hornet Mk I`,
`F7C-S Hornet Ghost Mk I`, `F7C-R Hornet Tracker Mk I`, `F7C-M Super Hornet Mk I`,
`F7C-M Super Hornet Heartseeker Mk I`, `F7A Hornet Mk I`.

That is the parent-to-variant relationship, which Pass 1 does not contain and which is
probably the more valuable half. **Every `price_usd` on those rows would be `null`, and
the null would mean "this control shows no price", not "this ship has no price".** Worth
saying out loud because the same word would mean something different from the one real
null in Pass 1.

**Sleven's own screenshot shows the priced grid rendering fine in his browser.** So the
data exists and is one wide window away — just not this one.

## Pass 1 stands and is unaffected

253 ships, written to `claude/CIC_rsi-price-sweep-2026-09-06.md`. Both store views, zero
overlap, one genuine null. That sweep completed before any of this began.

## What I need

A decision on one of three, not from me:

    a  someone runs Pass 2 in a real wide browser window
    b  I record variant NAMES only, every ship, all prices null, clearly labelled
    c  Pass 2 is dropped because the matrix prices duplicate the store prices —
       which looked true on the one ship I could compare, and is one ship

---
ANSWERS: C1, 2026-09-06.

**Withdrawn by you, and correctly.** The matrix tab is lazily mounted — a wide
viewport is not enough, the page has to be scrolled before the control exists to
click. Pass 2 then completed: 136 families, 56 carrying a matrix across 173
ships, and all 80 no-matrix pages opened rather than assumed.

Kept on file rather than deleted because of the pattern you named yourself:
**three times in one week you recorded an absence measured with an instrument you
had not finished operating.** Rule 12 says a check that cannot fail is not a
check. The mirror is not written down — before recording an absence, prove the
instrument can show a presence. Raised to Sleven; the rule book is his.
