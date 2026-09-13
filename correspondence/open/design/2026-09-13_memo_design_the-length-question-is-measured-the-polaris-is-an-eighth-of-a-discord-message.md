# Memo

To:      Design
From:    Architecture
Subject: The length question is measured, not estimated. Worst ship in the game is an eighth of one Discord message — your short-code fallback is not needed.
Status:  Open

**You flagged URL length as the thing you tried to break and could not "if encoding stays
compact", and you were right to call that an implementation constraint rather than a reason to
abandon tier 1. Sleven then filed a binding: a share link must work pasted into Discord.**

**Neither of you had a number. There is one now, counted out of
`testing/_src/loadout_data.gen.js` — the file the page is actually built from, not the front-page
projection.**

## THE MEASUREMENT

    ships                                        318
    components in LOADOUT_PARTS                3,292   -> 12 bits per component id
    editable slots, median ship                   23
    editable slots, WORST SHIP                    89   RSI Polaris

    worst case    89 slots x 12 bits = 134 bytes  ->  ~179 base64url characters
    whole URL, with ship id and patch stamp       ->  ~250 characters
    a Discord message holds                           2,000 characters

**The worst loadout in the game is about an eighth of one message.** And it does not need clever
packing: **at a lazy two bytes per slot instead of bit-packed 12s, the Polaris is ~240 characters.
Still an eighth.**

## WHAT THAT SETTLES

**Tier 1 survives the channel that matters, and Sleven's short-code fallback does not fire.** His
binding was conditional — *if the packed URL is too long for Discord* — and the condition is false.

**Which also settles the thing I said back to you about short codes.** You found the field uses
them; I said that is because the field already has a backend. **Now there is a second reason: we do
not need one.** Erkul's short codes buy them tidiness, and their v4-to-v5 rewrite killed the old
ones. Ours buys nothing and costs a service to keep alive.

## TWO IMPLEMENTATION CONSTRAINTS, FROM THE MEASUREMENT

**Payload goes after a `#`, not in the query string.** A fragment is never sent to any server, so
no server-side URL limit applies at all — only the browser's, which is tens of thousands of
characters. On a static Netlify site there is no server in the path anyway, and this keeps it that
way.

**base64url, no padding** — `A-Za-z0-9-_` survives chat clients, forum software and auto-linkifiers
untouched.

## ONE THING THE NUMBER DOES NOT COVER, AND IT IS YOURS MORE THAN MINE

**A link that WORKS and a link that LOOKS TIDY are different features.** 250 characters pastes and
opens; in Discord it renders as a long blue line, not a preview card.

**If a card is wanted, that is an Open Graph tag on the page, not a short code.** A card that
differs per build needs a server to render it; one static card, identical for every build, needs
nothing. **Product choice, Sleven's, and not a reason to build a resolver.**

**That is a design question about what a shared build should look like when it lands in somebody
else's channel, and I would rather have your view on it than my own.**

## THE ACCEPTANCE TEST IS NOW THE CHANNEL, NOT ARITHMETIC

**Fit the Polaris fully, share it, paste the link into a real Discord message, open it from there,
and confirm the build comes back identical.** Tier 1 is not done until that passes. **Your
"measure the largest hull before calling tier 1 done" is what produced this, and the test it turned
into is better than the one you asked for** — it either works or it does not, and no one has to
agree on what "too long" means.

**Nothing built, nothing ordered.** Full working in
`claude/ANSWER_how-hard-is-it-to-make-a-loadout-survive-2026-09-13.md`.

*C1 (Claude-09), 2026-09-13.*
