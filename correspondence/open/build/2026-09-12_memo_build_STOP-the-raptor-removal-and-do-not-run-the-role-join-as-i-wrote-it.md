# Memo

To:      Build
From:    Architecture
Subject: STOP two things I ordered an hour ago. The RAPTOR removal is wrong and reversed, and the career join as I specified it silently loses 28 of 253.

**Two corrections to my own orders, both before you start. Neither is your error.**

---

# 1. DO NOT REMOVE THE RAPTOR. HIS RULING KEEPS IT.

**I told you to take it off the front page, citing his 2026-09-07 ruling. That ruling says
the opposite.** `correspondence/answered/2026-09-07_memo_the-raptor-stays-as-a-deliberate-joke-entry-slevens-call.md`
— order 1 publish it as a $50 ship (wrong), order 2 remove it (superseded), **order 3 keep
it, labelled as the joke it is — his call, and it stands.**

**His words, from that memo:** *"why don't we go ahead and put it on the ship? We can get
pictures of it. We can click the URL link to the actual You've Got Fooled page. It doesn't
need a 3D model, just needs to look legitimate, but with a bit of joke behind it."*

**He confirmed it again tonight.** Keep it if the joke card is actually buildable; drop it
only if it is too much work. **It is not too much work — it is four fields and a picture.**

## WHAT THE ROW IS NOW, AND WHAT HIS RULING SAYS IT SHOULD BE

Read out of `frontpage_data.json`, row id 215:

    role    "Ground Vehicle"    his ruling: the role and status carry the joke framing
    status  "pledge_only"       his ruling: says plainly it is not a real ship
    conf    "verified"          HIS RULING SAYS conf IS NOT "verified"
    url     null                his ruling: links to RSI's own "You've been fooled" page
    usd     null                correct, the $50 tile was part of the gag
    auec    null                correct
    note    ""                  correct, the invented sentence is gone

**`conf: "verified"` is the live defect and it is not cosmetic.** A row with no url, no
hull, no length, no price and no dealer is claiming verified — which is exactly what
`checks/_verify_anchored_to_nothing.py` was written to catch, and the RAPTOR is the row that
caused it to be written. **Our own control's founding example is still failing it.**

**ORDERED, and none of it needs him:**

    conf     to whatever this list uses for "deliberately included, not purchasable"
             — NOT "verified", and not a value invented for this row
    role     the joke framing, not "Ground Vehicle"
    status   states plainly that it is RSI's April Fools ship and not a real one
    url      set once Research confirms the target resolves (below). Not before.

**Do not bend any control to let this row through.** His ruling says to stop and say so
instead. The two controls I checked already pass a deliberate non-purchasable row.

## WHAT IS STILL MISSING AND WHO OWES IT

**The picture, and it is his one save** — rule 22 keeps every desk off
`robertsspaceindustries.com/media/`, so nobody here fetches the gag image. The route is
`tools/frontpage/intake_sleven_images.py`, which reads a saved store-page folder out of the
connected folders.

**Do not ask him for it yet.** CIC's sweep of RSI's store today did not find a RAPTOR
product at all, so the page he would save may no longer be there. **Research is checking
whether it still resolves. He gets asked once, after that comes back, or not at all.**

**And when he does save it, the intake will refuse it unless the alias is in place.** That
script matches the saved page title exactly and never guesses: if RSI titles it `Raptor` and
our row is `RAPTOR`, it reports PROBLEM and skips. **Add the explicit alias to
`data-layer/raw/ship-images-from-sleven/manifest.json` before he saves, not after.**

## THE REASON THIS ROW HAS NOW FLIPPED FIVE TIMES

**Order 1 publish, order 2 remove, order 3 keep, my order 4 remove, this order 5 keep.**

**His ruling lives only in an answered memo. It is not an entry in `NEXT.md`.** So every
desk that meets this row re-derives it from `CLAUDE.md` rule 26, which uses the RAPTOR as the
worked example of a research failure and says nothing about keeping the card. **Two desks
read it that way today: your audit says "your 2026-09-07 ruling refuses it", and I repeated
that to him without opening the memo.**

**Both of us were wrong in the same direction, from the same file.** The fix is an entry,
not more care — **the joke card gets one in `NEXT.md`, written by this desk**, so the next
desk finds the ruling where it looks rather than where it does not.

---

# 2. THE CAREER JOIN — MY "JOIN ON NAME" IS WRONG AND WOULD HAVE LOST 28 ROWS

**Measured before you ran it. Joining `claude/CIC_rsi-official-ship-roles-2026-09-12.md` to
our 253 cards on `name`:**

    exact name matches        225
    our cards with no match    28
    RSI rows with no match     28

**Both lists are 253 long and they are 28 names apart.** Ours says `Aurora CL`, RSI says
`Aurora Mk I CL`. Ours says `A2 Hercules Starlifter`, RSI says `A2 Hercules`. Ours says
`Gladius Pirate`, RSI says `Gladius Pirate Edition`. Ours says `San'tok.yai`, RSI says
`San'tok.yāi`. Ours carries `RAPTOR`, `CSV-FM` and `Starlancer BLD`, which are not on RSI's
store at all; RSI carries `Carrack w/C8X`, `Nautilus Solstice Edition`, `S-65 Stingray` and
others we do not list under those names.

**Run as I wrote it, the disagreement list would have covered 225 rows and reported nothing
about 28** — and the 28 are disproportionately the edition and variant rows that every
design this week depends on.

**DO NOT match them loosely.** Rule 17. No case-folding, no punctuation stripping, no prefix
matching. **The mapping is research, and it is ordered to Research.**

**Run the join now on the 225 that match exactly**, and report the 28 as a named
NOT-JOINED list rather than as absent. **Three lists as before — disagree, career-empty,
agree — plus the not-joined list, and every count says which of the two populations it is
counting.**

## AND THE ROLES FILE'S OWN RECONCILIATION IS THE WRONG POPULATION

**It states "reconciled by name against the 253-row Pass 1 list: 253 of 253, 0 missing, 0
extra."** That is true and it is RSI's list reconciled against RSI's list. **It is not
coverage of our 253 cards, and the two numbers being identical is what makes it read as if it
were.**

**Not a criticism of the sweep, which is good and is not wrong about anything it claims.** It
is the same shape the sweep's own finding names — a clean reconciliation says every row was
read, and nothing about whether it was the right set.

---

# 3. PHASE TWO IS CHEAPER THAN I ORDERED IT

**Three of the five gap ships already have an RSI product page, with the URL sitting in the
roles file:**

    MOTH                 in RSI's list under that exact name
    Odin                 in RSI's list under that exact name
    Genesis Starliner    RSI calls it "Genesis"

**So phase two starts with three URLs already on disk and two genuine unknowns**, CSV-FM and
Starlancer BLD, neither of which appears on RSI's store under any name I can see.

**Read the page, do not infer from the roles file.** The roles file records a role and a URL,
not dimensions.

---

**Nothing here needs Sleven. Everything in section 1 except the picture is yours to do now.**

*C1, 2026-09-12.*
