# Memo

To:      Architecture
From:    Owner (Sleven)
Date:    2026-09-13
Status:  Answered
Subject: Binding — loadout share links must work in Discord

**Most people share in Discord.** A loadout survive/share design that breaks there is not acceptable.

## BINDING

1. **A shared loadout link must paste and open correctly from a normal Discord message.**
2. If a full packed URL is too long for Discord, **use a short link/code** (same idea Erkul-class tools use) — still no accounts required for the basic share.
3. Do not ship a “works in the address bar but dies in Discord” tier-1.

Grok’s persistence review already flagged length; this is Owner confirming the channel that matters.

Cc Design via tray when routed. Nothing else ordered here — still talking; this constraint is settled.

*Owner (Sleven). Filed with Grok.*

---

ANSWERS:

# ARCHITECTURE DISPOSITION - 2026-09-13. BINDING TAKEN, AND IT IS ALREADY MET WITH ROOM TO SPARE.

**Grok had flagged length as the thing he tried to break and could not. That was an estimate. It is
now measured, out of `testing/_src/loadout_data.gen.js` - the file the page is actually built
from.**

    components in LOADOUT_PARTS            3,292   -> 12 bits per component id
    editable slots, median ship               23
    editable slots, WORST SHIP                89   RSI Polaris

    worst case   89 slots x 12 bits = 134 bytes -> ~179 characters
    whole URL, with ship id and patch stamp     -> ~250 characters
    a Discord message holds                        2,000 characters

**The worst loadout in the game is about an eighth of one Discord message.** And it does not need
clever packing - at a lazy two bytes per slot the Polaris is ~240 characters, still an eighth.

**SO YOUR FALLBACK IS NOT NEEDED. Your binding says: if the packed URL is too long for Discord, use
a short code. The condition does not fire.** No short code, no resolver, no store, no backend -
for the Discord case. **The binding stands and is satisfied; the fallback stays unbuilt because it
was conditional and the condition is false.**

**ONE THING THE MEASUREMENT DOES NOT COVER, SAID PLAINLY.** A link that WORKS and a link that LOOKS
TIDY are different features. A 250-character link pastes and opens; in Discord it shows as a long
blue line rather than a neat preview card. **If you want the card, that is an Open Graph tag on the
page, not a short code** - and a card that differs per build needs a server to render it, while one
static card the same for every build needs nothing. **That is a product choice and it is yours. It
is not a reason to build a resolver.**

**THE ACCEPTANCE TEST IS NOW THE CHANNEL RATHER THAN ARITHMETIC:** build the Polaris fully fitted,
share it, paste the link into a real Discord message, open it from there, and confirm the build
comes back identical. **Tier 1 is not done until that passes.**

**Payload goes after a `#`, base64url, no padding.** A fragment is never sent to a server, so no
server-side URL limit applies at all - and on a static Netlify site there is no server in the path
anyway.

**Full working: `claude/ANSWER_how-hard-is-it-to-make-a-loadout-survive-2026-09-13.md`. Nothing
built, nothing ordered.**

*C1 (Claude-09), 2026-09-13.*
