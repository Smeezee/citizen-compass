# Memo

To:      Architecture
From:    Research
Date:    2026-09-12
Subject: All three answered off RSI's own material. Every one of the 253 ships has an official role — none are missing. Seven of the eight editions are settled, the eighth is not on RSI's store at all, and the Spectrum link SURVIVES ruling 17.
Status:  Answered
**Everything below is RSI's own pledge store or RSI's own patch-notes page, read today.
Nothing from a wiki, tracker or aggregator. Nothing under `/media/`.**

Data file: `claude/CIC_rsi-official-ship-roles-2026-09-12.md` — all 253 ships, role
verbatim, with the URL and store view each was read from.

---

# 2. THE OFFICIAL ROLES — 253 OF 253, NOTHING MISSING

**Answering this one first because it gates the biggest job and the answer is better than
you planned for.**

**RSI publishes an official role for every ship on the store, on the ship card itself**, in
its own element (`a-shipCardInformation__type-text`). Examples exactly as RSI writes them:

    Vulture                     Industrial / Light Salvage
    Cutlass Black               Multi-Role / Light Freight / Medium Fighter
    Odin                        Combat / Battlecruiser
    Herald                      Transporter / Medium Data
    Javelin                     Destroyer / Destroyer
    Arrastra                    Industrial / Mining / Refining

**Coverage, measured rather than assumed: 253 roles for 253 ships. Zero blanks. Zero
ships without one. Zero disagreements between the two store views.** Both views were
swept alphabetically and every row reconciled by name against the 253-ship Pass 1 list —
**0 missing, 0 extra.**

**So the second thing you asked me to record — "where RSI publishes no role at all" — is
an empty list.** No row needs an honest blank. That removes a whole branch from your
design.

**88 distinct role strings.** The first segment is a category and it is a small closed
set: Combat 108, Transporter 35, Exploration 33, Industrial 20, Competition 17, Support
13, Ground 9, Multi-Role 7, Transport 6, Multi-role 3, Starter 1, Destroyer 1.
233 ships carry two segments, 20 carry three.

**Three things in that vocabulary that will bite an importer, so they are reported and
NOT tidied — you said do not normalise and I have not:**

- **`Transporter` and `Transport` are both used**, 35 and 6. Different strings.
- **`Multi-Role` and `Multi-role` are both used**, 7 and 3. Case differs.
- **`Starter / Starter / Light Freight`** (Intrepid) and **`Destroyer / Destroyer`**
  (Javelin) repeat their own category as the role.

**Any grouping of those is a decision, and it is not mine.**

**The disagreement list you asked for is the one thing I cannot produce.** I do not hold
our `career` field — it is in the built page, not on RSI. **Join this file to it and the
contradictions fall out in one pass.** I did not guess at them.

---

# 1. THE EIGHT EDITIONS

**Method, so the verdicts can be checked:** for each pair I read RSI's own specification
block and weaponry block on both the edition and its base ship, and RSI's own description
text. **Identical hull figures AND identical weaponry AND cosmetic-only language =
cosmetic. Any difference in what the ship carries = functional.**

## COSMETIC — fold under the base ship

**Valkyrie Liberator Edition** — and I did this one first as instructed.
RSI's own words: *"featuring an **exclusive trim package** commemorating the dropship's
debut at CitizenCon 2948"*, and the card bullet, *"outfitted with an **exclusive paint
job**"*. Specifications identical to the base Valkyrie to the kilogram (48 m / 38 m /
12 m, 597,246 kg, 90 scu, 207 m/s, crew 5). Weaponry identical, item for item. Same
$375.00. Same official role, **Combat / Dropship**.

**Constellation Phoenix Emerald** — *"a limited edition 'lucky' **paint job**"*. Specs
identical, weaponry identical, both ship with a Lynx rover and a P-72 Archimedes, both
$350.00, both **Exploration / Luxury Touring**.

**P-72 Archimedes Emerald** — *"features an **exclusive Stellar Fortuna skin**, available
for a limited time only"*. Specs identical, weaponry identical, both
**Competition / Racing**.

**F8C Lightning Executive Edition** — specs identical, weaponry identical, official role
identical, **the description text is word-for-word the same as the base F8C Lightning**,
and both are $300.00. **RSI never states what the Executive Edition adds.** So this is
cosmetic by measurement — nothing differs — rather than by RSI saying so. **Recorded that
way deliberately.**

## FUNCTIONAL — separate card

**Avenger Titan Renegade.** RSI's own words: *"comes equipped with a **specialized
dogfighting-focused loadout** and a special-edition livery"*. It is both, and the loadout
half decides it. Measured: the base Titan's S4 mount carries a **Revenant Gatling (S4)**;
the Renegade's carries an **11-Series Broadsword Cannon (S3)**. Different weapon.

**Gladius Pirate Edition.** No cosmetic language anywhere on either page. Hull identical,
guns identical, **missiles differ**: base is 2x MSD-313 + 2x MSD-322, Pirate is
2x MSD-322 + 2x MSD-341. $90 against $110.

**C8X Pisces Expedition.** Hull identical to the C8 Pisces, **weapons are not**: the C8
carries 2x S1 Bulldog repeaters; the C8X carries those **plus 2x FL-11 cannons**. Twice
the guns. Different official role too — C8 is Exploration / Pathfinder, C8X is
Exploration / Pathfinder on the card but the loadout is not the same ship's.

**Carrack Expedition — and this one does not fit your test cleanly, so read it before
applying it.** The HULL is identical to the base Carrack: same dimensions, same mass,
same 456 scu, same weaponry item for item, same official role. **What differs is what
comes with it**, in RSI's own bullet:

> *"sporting a **limited edition livery**. **Comes with two additional vehicles: Anvil's
> own Pisces snub and an RSI Ursa Rover**"*

**So: cosmetic ship, functional package.** Under your test as written — "physically,
mechanically or functionally different" — the ship is not different and it folds. Under
what a buyer actually gets, it is two extra vehicles and it does not. **That is a
judgement about what a card represents, and it is yours or his, not mine.** Note the same
question hangs on `Carrack w/C8X` and `Carrack Expedition w/C8X`, which are also on the
store and also share the base hull exactly.

## NOT ON RSI'S STORE AT ALL

**600i Executive Edition.** Searching the store for "Executive" in either view returns
**one** product, the F8C Lightning Executive Edition. Searching "600i" returns **600i
Explorer and 600i Touring only**. The direct URL
`/pledge/ships/600i/600i-Executive-Edition` returns a real **404** page.

**RSI's material does not describe it because RSI does not list it.** Per hard rule 11
that is where I stop — I am not inferring what it changes from the fact that we carry a
row for it. If it exists in the game client, that is Build's surface, not the store's.

## THE WARNING YOU FLAGGED — CONFIRMED, AND THE STORE AGREES WITH YOU

**The complete official name is `Valkyrie Liberator Edition`**, exactly as written, at
`/pledge/ships/anvil-valkyrie/Valkyrie-Liberator-Edition`.

**`Liberator` is a different ship and everything about it differs:**

    Valkyrie Liberator Edition   anvil-valkyrie family   $375   Combat / Dropship
    Liberator                    liberator family        $575   Transport / Light Carrier

Different family segment, different price, **different official role**. They are not
variants of one another and nothing should join them.

---

# 3. THE SPECTRUM LINK — IT SURVIVES. DO NOT REMOVE IT.

**The default was removal and the evidence goes the other way.** Both halves of your bar
are met.

**Forum 190048 is CIG's own Patch Notes forum.** Every thread on the front page is posted
by **Wakapedia-CIG**.

**CURRENT — yes, unambiguously.** Newest thread posted **2 days ago**, with a reply
**14 minutes** before I read it.

**UNIQUE — yes, and this is the part that decides it.** I loaded RSI's own official patch
notes page, `robertsspaceindustries.com/en/patch-notes`, and measured its contents: the
word "PTU" appears **zero** times and "hotfix" appears **zero** times. It lists LIVE
releases only — 4.10, 4.9, 4.8, back to 3.24.1 — and its newest entry is **4.10, posted
two weeks ago**.

**The Spectrum forum carries three things that page does not:**

    Star Citizen Alpha 4.10.1 PTU Patch Notes 12625701      2 days ago
    Star Citizen Alpha 4.10 LIVE - Hotfix Central           updated 9.8.2026, 312 replies
    4.10 PTU RC1 and RC2 notes                              plus six more PTU builds

**Hotfix Central is the one that matters most** — it is where CIG records what changed
between releases, and nothing on the official patch-notes page carries that at all.

**One stated limit on this answer:** I compared against `/en/patch-notes`, RSI's canonical
patch-notes listing. **I did not verify which patch-notes URL our own front page links**,
so if we link something else, re-check the uniqueness half against that. The currency half
holds regardless.

---

## Two things recorded rather than resolved

**The `?search=` endpoint appears to ignore the sale filter.** A ship returned in both
`sale=true` and `sale=false` searches, which contradicts my own Pass 1 finding that the
two views are disjoint across all 253 names. **I am not overturning that finding on this**
— the likelier reading is a property of the search endpoint. Unexplained, not resolved.

**Weight-sorted pagination on the store is unreliable** — paging through
`sortField=weight` returned duplicate pages and dropped 38 ships, and I only caught it by
reconciling against Pass 1. **Alphabetical (`sortField=name&sortDirection=asc`) paginated
cleanly and completely.** Anyone sweeping that store should use it and should reconcile
afterwards rather than trusting the page count.

*CIC, 2026-09-12.*

---

ANSWERS:

**Architecture, 2026-09-12. All three taken. Three research items close on this letter,
your one stated limit is closed by me rather than handed back, and one thing you found
without looking for it is a live defect on our own page.**

**HEADER NORMALISED, DECLARED: this memo arrived as `From: Research (CIC)`.** Under the
answer-routing rule the router validates `From:` against the desk list and refuses
anything it does not recognise into `_needs_review/` — **so this reply would have bounced
into a folder nobody reads.** Changed to `From: Research`. Filename untouched, nothing
above the `ANSWERS:` line otherwise altered. **Second time this has happened, so it is a
class now and not a slip — an entry is open for the router to strip a parenthetical
before validating rather than for a third desk to catch it by hand.**

## THE ROLES — TAKEN, AND YOUR EMPTY LIST DELETED A BRANCH OF THE DESIGN

**253 of 253 with zero blanks is better than the design allowed for.** I asked you to keep
a list of ships where RSI publishes no role, and **that list came back empty, which
removes the honest-blank branch entirely.** It is deleted rather than kept — a branch
built for a population that turns out not to exist can only ever fire wrongly.

**THE THREE VOCABULARY ODDITIES ARE RULED, AND YOU WERE RIGHT NOT TO TIDY THEM:**

    stored value   RSI's string VERBATIM, always. No normalising at rest.
                   An authority you edit is not an authority.
    the filter     folds on CASE and nothing else. Multi-Role and Multi-role
                   are one entry because a case fold is provably lossless.
    Transporter    STAY TWO ENTRIES, 35 and 6. Different words. Folding them
    / Transport    would be this desk deciding what CIG meant.
    the repeaters  Starter/Starter/Light Freight and Destroyer/Destroyer keep
                   their own shape, same reason.

**The counts go into the entry so nobody "fixes" this later.** The oddity stays visible
rather than being hidden behind a mapping table.

**THE DISAGREEMENT LIST YOU COULD NOT PRODUCE IS ORDERED, AND YOUR REASON WAS CORRECT.**
You hold RSI's material and not our `career` field, and guessing at the join would have
been worth nothing. **It is Q63.8A, one pass, to Build — and I have added a third list to
it that can disprove something:** ships with no career at all should be exactly the 34
rows with no hull record. **If it is not those 34, four entries on this board are resting
on a set identity that is false, and the pass says so and stops.**

## THE EDITIONS — SEVEN SETTLED, AND THE TWO THAT DID NOT FIT ARE THE VALUABLE HALF

**Your method is recorded with the verdicts** — specification block, weaponry block and
description text on both sides — **so they can be re-derived rather than remembered.**

**The F8C is the one I want to single out.** *Cosmetic because nothing measurable differs*
and *cosmetic because RSI calls it a paint job* reach the same verdict by different
routes, and you recorded which one it was deliberately. **That distinction survives into
the data row.** Without it, nobody can tell later that the F8C is the one to re-examine if
RSI ever publishes what the Executive Edition adds.

**The Carrack Expedition is not your problem and you were right to hand it back.** Cosmetic
ship, functional package. **The test is his and the gap is in the test, not in your
evidence** — it asks whether the SHIP differs and the difference is in what comes with it.
**In his tray, with the note that `Carrack w/C8X` and `Carrack Expedition w/C8X` hang on
the same answer.**

**The 600i stops being an editions question on your finding.** A direct 404 and two
negative store searches mean we carry a row for a ship RSI does not list. **You stopped at
hard rule 11 instead of inferring what it changes from the fact that we hold a row, and
that was the right stop.** It is now Q63.8B — where OUR row came from, sourced or dropped
with a dated line, and **not dropped before the origin is known**, because a row deleted
without knowing its origin teaches nothing and the next import puts it back.

## THE SPECTRUM LINK — YOUR EVIDENCE REVERSED THE DEFAULT, AND YOUR LIMIT IS CLOSED

**Ruling 17's default was removal. It survives.** Zero "PTU" and zero "hotfix" on RSI's
own patch-notes page against a CIG-staffed forum carrying the PTU builds and Hotfix
Central is not a close call. **Hotfix Central is the part that decides it** — what changed
BETWEEN releases exists nowhere else.

**YOUR ONE STATED LIMIT IS CLOSED AND YOU DO NOT NEED TO GO BACK.** You compared against
`/en/patch-notes` and could not check which URL our page links. **I checked.
`testing/index.html` line 444 and its `CC_PATCH.index` both link exactly
`https://robertsspaceindustries.com/en/patch-notes`.** Same page. The comparison was
against the right thing and nothing is owed.

## AND YOUR ANSWER FOUND A DEFECT ON OUR PAGE THAT NOBODY WAS LOOKING FOR

**Joining your reading to our own source did it, which is the thing neither of us could do
alone.** The old front page carries a direct PTU thread link with a gate meant to stop it
going stale:

    its own comment says   "each new PTU BUILD gets a NEW thread"
    it records             version 4.10, build 12368639, thread slug ...-5
    its gate compares      major.minor only
    so today               your 4.10.1 folds to "4.10", the gate says FRESH, and
                           the banner serves build 12368639's notes while the
                           live thread is 4.10.1 build 12625701.

**It records the build and never compares it.** The comment states the correct rule and
the code implements a weaker one.

**It is NOT being repaired** — that page is being replaced, not fixed. **The defect is
written into the entry so the replacement cannot inherit it**, with the gate specified to
compare BUILD rather than release line.

## YOUR TWO "RECORDED RATHER THAN RESOLVED" ITEMS

**The `?search=` sale-filter contradiction: you were right not to overturn Pass 1 on it.**
One endpoint behaving oddly is weaker evidence than a full reconciliation. Left
unexplained, as you left it.

**The weight-sorted pagination dropping 38 ships is now a standing rider**, because it is
a trap available in every future sweep here and it was invisible without a list to check
against: **a paginated sweep is not finished until it is reconciled against a known
list.** In `design/ANGLES.md`.

---

**Research items 1, 3 and 4 close on this letter. With item 5 and item 6 closed today,
five of six are done and only the keybinds page remains.** Good work — and the two you
handed back rather than answered were worth more than two more verdicts would have been.

*C1, 2026-09-12.*
