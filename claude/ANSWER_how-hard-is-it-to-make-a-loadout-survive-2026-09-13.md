# ANSWER — how hard is it to make a loadout survive?

**C1 (Claude-09), 2026-09-13, 04:3x CDT. His question, asked in chat. Nothing built, nothing
ordered.**

## THE SHORT ANSWER

**Cheap, if the link is the save file. Expensive, if we try to be a place that stores things.**

The question sounds like storage and it is not. **The thing that has to survive is the build, not
the storage.** Put the build in the URL and the link survives forever, on any browser, on any
device, and it can be sent to somebody else — with no server, no account and no database.

---

## FOUR WAYS, CHEAPEST FIRST

### 1. THE BUILD LIVES IN THE URL — RECOMMENDED

Encode the fitted components into a short string in the address bar. **Opening the link rebuilds
the loadout exactly.**

    survives         forever, any browser, any device, any day
    needs            no server, no database, no account, no login
    the user "saves" by bookmarking it or sending it to somebody
    cost             small - encode and decode a compact build string, plus a patch stamp

**It is also the only option on this list that is a feature rather than plumbing.** A build becomes
a link somebody posts in a Discord or a forum, and every one of those links is a route back to the
site. **Nothing else here does that.**

**THE ONE REAL RISK, AND IT HAS A CHEAP FIX.** A link encodes component identifiers. When the game
patches and identifiers move, an old link would silently decode into a different build. **So the
link carries the patch it was built on, and a stale link says so on arrival rather than pretending.**

**That is not extra work bolted on — it is the same machinery as `last_verified_patch` and the
verification mark already being designed.** The same honesty rule, one surface over.

### 2. NAMED SAVES IN THE BROWSER — NEARLY FREE, DO IT ALONGSIDE

A list of named builds kept in that browser's own storage.

    survives         reload, and days or weeks on that one browser
    dies             on a cache clear, and never travels to another device
    cost             hours

**Not a substitute for 1.** It is the convenience — "my builds on this machine" — and 1 is the
durable artifact. **Together they answer the question completely.**

### 3. SERVER-SIDE SAVES WITH A SHORT CODE — ONLY IF HE WANTS A LIST THAT FOLLOWS HIM

Post the build, get back a short code, anyone with the code loads it.

**AND THIS IS WHERE THE REAL NEWS IS.** *"We have a backend"* is true on paper and false in
practice.

    Railway project    mellow-eagerness, workspace smeezee's Projects
    Postgres           UP. 1 replica, 500 MB volume, sfo
    citizen-compass    LATEST DEPLOYMENT FAILED, 2026-08-22. Down for three weeks.

**Nothing on the public site depends on it, which is why nobody noticed** — the site is static on
Netlify and is served from a mirrored file, not from git and not from the API. **So it is not
broken for anything we do today. It IS broken for anything server-side we would start tomorrow.**

**Anything in tier 3 begins with getting that service deploying again, and that is the real cost,
not the save endpoint.** On top of it: this would be the first thing on the site that accepts input
from strangers, which makes spam, rate limits and "what do we do when somebody stores something
foul in it" real questions rather than hypothetical ones.

### 4. ACCOUNTS — NOT RECOMMENDED, AND NOT A SMALL STEP

Logins, passwords or email links, password resets, and holding personal data on people. **Much
bigger than the three above put together, and it buys nothing that 1 and 2 do not already give
him.**

---

## WHAT I WOULD DO

**1 and 2 together. No server, no account, and it fully answers "a different day, a different
browser."**

**Tier 3 only if he decides a person should be able to open a list of their builds from a machine
they have never used before** — and that decision, not the code, is the thing to think about,
because it is the first step toward tier 4.

## ONE THING THAT IS HIS AND NOT MINE

**A shared link is publication.** A build someone shares points at our site and carries our
wording. **That is rights and publication territory and it is settled by him, not designed by me**
— but it is worth knowing before it is built rather than after.

*C1 (Claude-09), 2026-09-13. Nothing built, nothing ordered.*

---

# REVISED 2026-09-13 04:4x CDT, AFTER DESIGN'S REVIEW

**Grok reviewed it straight and rated it 8/10. Tier 1 plus tier 2 stands. Four amendments taken,
one piece of his research corrected, and one of his findings turned around — it argues for us more
strongly than he read it.**

## FOUR AMENDMENTS, TAKEN

**1. COMPACT ENCODING IS A REQUIREMENT, AND TIER 1 IS NOT DONE UNTIL IT IS MEASURED.** Ship id plus
patch stamp plus slot-to-component SHORT ids. **Not display names, not verbose JSON.** His test is
now the acceptance criterion: **measure the longest URL a fully fitted largest hull produces before
tier 1 is called done.** My answer asserted "small" and never said what would make it untrue.

**2. ON A PATCH MISMATCH: BANNER PLUS PER-SLOT OUTCOME. HIS IS BETTER THAN MINE.** I had the link
saying it was built on an older patch. **That is a half-answer — it tells you something is wrong
and not what.**

    carry the patch or data-generation id in the link
    on mismatch: banner PLUS per-slot outcome - kept / dropped / unknown id
    NEVER silently map an old id to a different part
    refuse the whole page only if the payload cannot be parsed at all

**His line for it is the right rule: fail closed on identity, fail open on display with scars.**

**3. THE RAILWAY READ WAS A PROJECTION AND HE CAUGHT IT.** I concluded nothing depends on that API
**from the front page**, which is the exact error this project has made five times this week.
**"Nothing public depends on it" holds for the Netlify mirror; it does not prove the whole machine
never talks to that host.** Before tier 3: re-check the deploy AND search for any client fetch to
it. **Do not read the front page and call it the project.**

**4. THE VERIFICATION MARK AND THE MEANING RULES TRAVEL WITH THE LINK.** A shared build is a page a
stranger sees without ever visiting us. **It must carry the same verification honesty as the live
page, or we are exporting a certainty we refused to claim at home.** Same for Meaning's
generate-or-hide rule. **This was missing and it is a real gap.**

## ONE CORRECTION TO THE RESEARCH

**ORION OS is not a public product and there is nothing to find.** It is an in-development tool
built by a contact of Sleven's, discussed as a possible collaboration. **It is not a comparable to
study from outside and Grok should stop looking.** Erkul and HubCitizen-class tools were the right
substitutes.

## AND THE FINDING THAT ARGUES FOR US HARDER THAN HE READ IT

**He found that the field uses short opaque codes — `erkul.games/loadout/<shortCode>` and similar —
rather than fat URLs, and read it as a pattern we should learn from.**

**A short opaque code cannot exist without a store to resolve it against. That IS tier 3.** So the
finding does not say *we should use short codes*; it says **everyone else already built the backend
we are trying not to need.**

**And his own evidence is the argument against copying them.** He found that **Erkul's v4 to v5
rewrite broke old loadout URLs and did not migrate legacy hangar builds.** Those links died
**because the service behind them changed.**

    a short code survives only as long as the service resolving it
    a packed link carries the build itself and cannot be broken by us

**A packed URL is not the poor relation of a short code. It is the only one of the two that still
works if this project stops being maintained** — which, for a fan site of a game still in
development, is the durability question that matters.

**Where a short link is genuinely wanted later, it is a thin resolver in front of the packed
payload — not a reason to build the product.**

*Revised C1 (Claude-09), 2026-09-13.*

---

# MEASURED 2026-09-13 05:0x CDT — THE DISCORD BINDING IS ALREADY MET, WITH ROOM TO SPARE

**Sleven filed a binding: a shared loadout link must paste and open correctly from a normal
Discord message, and if a packed URL is too long, use a short code instead. Grok had flagged
length as the thing he tried to break and could not, on an estimate.**

**It is no longer an estimate. Counted out of `testing/_src/loadout_data.gen.js`, the file the page
is actually built from.**

## THE NUMBERS

    ships in the dataset                        318
    components in LOADOUT_PARTS               3,292   -> 12 bits per component id
    editable slots, median ship                  23
    editable slots, WORST SHIP                   89   RSI Polaris

    worst-case payload   89 slots x 12 bits  =  134 bytes  ->  ~179 base64url characters
    with ship id and patch stamp                            ->  ~200 characters
    a whole URL                                             ->  ~250 characters

    a Discord message holds                                     2,000 characters

**The worst loadout in the game is about an eighth of one Discord message.** It pastes, it opens,
and there is nothing to work around.

**And it does not even need clever packing.** At a lazy two bytes per slot instead of bit-packed
12s, the Polaris is 178 bytes and about 240 characters. **Still an eighth of a message.**

## PUT THE PAYLOAD AFTER A `#`

**In the fragment, not the query string.** A fragment is never sent to any server, so no
server-side URL limit applies at all — only the browser's, which is tens of thousands of
characters. **On a static Netlify site there is no server in the path anyway, and this keeps it
that way.**

**Alphabet: base64url, no padding.** `A-Za-z0-9-_` survives chat clients, forum software and
auto-linkifiers untouched.

## SO HIS FALLBACK IS NOT NEEDED, AND THAT IS THE POINT OF MEASURING

**His binding says: if the packed URL is too long for Discord, use a short link or code.
The condition does not fire.** No short code, no resolver, no store, no tier 3 — **for the Discord
case specifically.**

**The binding stands and is satisfied. The fallback stays unbuilt because it was conditional and
the condition is false.**

## ONE THING THE MEASUREMENT DOES NOT COVER, SAID PLAINLY

**A link that WORKS and a link that looks tidy are different features.** A 250-character link
pastes and opens; in Discord it renders as a long blue line rather than a neat preview card.

**If he wants a preview card, that is an Open Graph tag on the page, not a short code** — and a
per-build card needs something to render it, which is a server. **A single static card, the same
for every build, needs nothing.** That is a product choice and it is his; **it is not a reason to
build a resolver.**

## THE ACCEPTANCE TEST, NOW CONCRETE

**Build the Polaris fully fitted, share it, paste the link into a real Discord message, open it
from there, and confirm the build comes back identical.** Not arithmetic — the actual channel.

**That is the test tier 1 passes before it is called done**, and it replaces "measure the longest
URL" with something that either works or does not.

## ONE THING NOTICED IN PASSING, NOT A JOB

`LOADOUT_SHIPS` holds **two rows displaying as "RSI Polaris"** with identical slot counts, and
**three displaying as "Aegis Hammerhead"** (226, 226 and 224 slots, one of them the 2949 Best In
Show Edition). **Distinct keys, colliding display names.** That is the edition-and-variant question
already on the board, not a new defect. **Recorded so the next desk does not rediscover it as one.**

*Measured by C1 (Claude-09), 2026-09-13. Nothing built.*
