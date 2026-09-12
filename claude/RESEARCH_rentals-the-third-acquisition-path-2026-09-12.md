# RESEARCH — rentals, the third acquisition path, and the one thing in this proposal we must not build

**SOURCE NOT STATED. Relayed by Sleven, 2026-09-12, part two of the competitive search he is
running himself. NOT the Design desk and NOT Echo.**

**Companion to `claude/RESEARCH_the-competitive-landscape-and-where-we-win-2026-09-12.md`.
Verification pass and rulings in sections 0 and 7 are C1's. Sections 1 to 6 are the document as
received, unaltered.**

---

## 0. C1'S VERIFICATION PASS

### THE PREMISE IS RIGHT AND IT IS THE BEST THING EITHER PART OF THIS SEARCH FOUND

**We show buy-in-game and pledge. We do not show rentals.** The tagline is *"Know where to buy,
before you fly"*, and for a large number of hulls the honest answer to "how do I fly this" is
**rent it**, which the site currently cannot say at all. **That is a hole in the core promise,
not a missing feature**, and it outranks most of the landscape list on that basis.

### RULING — WE DO NOT PUBLISH A DERIVED RENTAL PRICE AS A PRICE

**This is the one part of the proposal that must not be built as written, and it is the part the
document is least worried about.**

**Every multi-day figure in this report is computed, not observed.** I re-derived all of them:

    69,458/day  ->  3 days  187,537  (= d1 x 3 x 0.90)   7 days  364,655  (= d1 x 7 x 0.75)
    50,274/day  ->  3 days  135,740  (= d1 x 3 x 0.90)   7 days  263,939  (= d1 x 7 x 0.75)

**Exact to the rounding. Not one of them came off a terminal.** The report says so itself, in
prose — *"UEX's public `vehicles_rentals_prices` mostly stores a daily number (week/month fields
are often copies of day)"* — and then **its own mockup prints the derived figures in the same
column as the observed one, with no mark on them.** A reader cannot tell which number was seen
and which was multiplied.

**That is the exact defect this project refuses everywhere else** — no fake component shop
prices, no guessed livery colours, no invented fuse failure, no loose name joins. **A rental
price we calculated is an invented price**, and a label in the legend does not fix a number
printed like a fact.

**The ruling:**

1. **An observed day rate displays as a price.**
2. **An unobserved 3-day or 7-day total does not display as a price at all.** It displays as the
   RULE — *"3 days: 10% off the daily rate"* — which is true, is CIG's, and is what the visitor
   actually needs in order to decide.
3. **When a tier has been observed on a terminal, it displays as a price, stamped, like any
   other.** Both states can coexist on one panel; they cannot look the same.

**This costs nothing and it is the version that is still correct in a year**, when CIG changes
the discount table and every derived figure on the site silently becomes a lie with a timestamp
on it.

### THE 30-DAY TIER IS AN OPEN UNKNOWN AND IT IS NOT SLEVEN'S TO CHECK

The report flags that older guides mention 30 days and the current wiki table lists only 1/3/7,
and proposes an in-game check. **The in-game check is his only if nothing else can answer it.**
**Route: CIC reads CIG's own rental UI documentation and the live wiki revision history before
anyone opens the game.** An unresearched unknown is unresearched, not ambiguous.

### THREE THINGS I COULD NOT VERIFY, AND ONE I THINK IS STALE

**NOT VERIFIED BY THIS DESK.** Every live figure here — ~46 rentable vehicles, ~32 terminals, the
0/10/25% discount table, insurance included for the window, stock-loadout-only, the real-time
timer that runs while logged out, and every aUEC example. **All plausible. None re-derived.**
None of it is published until it is.

**UNCERTAIN, AND FLAGGED BECAUSE A BUILDER WOULD TRIP ON IT:** the mockup places Teach's Rentals
at **Levski**. My understanding is that Levski was removed from the persistent universe several
Alpha versions ago, which would make that location stale rather than merely unverified. **I am
not confident and I have not checked.** It goes on the check list before any of these examples
are used as test fixtures.

**AN INTERNAL INCONSISTENCY IN THE MOCKUP.** The card line says *"always cheapest 1-day"* and
shows 50,274 at Traveler/Everus; the expanded panel for what reads as the same acquisition shows
*"Rent from 69,458/day"* at Teach's/Levski. **If those are one ship, the card and the detail
disagree about which desk is cheapest.** If they are two ships, the illustration needs saying so.
Small, and it is precisely the kind of thing that becomes a defect when someone builds from the
picture.

### RENTALS ARE NOT A FIELD. THEY ARE A SECOND RELATIONSHIP.

**Architecture note, and it is mine.** Our data model has ships to dealers to places, and the
whole structure assumes the transaction is a sale. **Renting shops are not dealers** — the report
is right that New Deal sells while Traveler, Vantage, Regal and Teach's rent — and a rental has
properties a sale does not: a duration, a discount tier, an included insurance window, and a
stock-only constraint.

**So `rn`/`rd` as a bolt-on pair of fields is the cheap version and it will need unpicking.**
The right shape is an acquisition relationship with a TYPE, so that buy, rent and pledge are
three instances of one thing rather than three parallel special cases — which is also exactly
what makes the acquisition ladder in section 6 trivial instead of a fourth special case.

**I am not ruling the final shape here**, because the hybrid-schema decision governs it and this
deserves a proper look against the existing dealer tables. **I am ruling that it is not built as
two loose fields on a card.**

### NO SERVER — AND THIS ONE SURVIVES IT

Unlike the community-sourced price freshness in part one, **rentals do not need a backend.**
Rental prices are baked at build time and stamped with patch and date, exactly like our dealer
prices already are. **Buildable today.**

### WHAT THE BREAK-EVEN IDEA GETS RIGHT, AND THE WORD IT IS MISSING

**"~36 days of rental equals the buy price"** — I checked it: 2,513,700 / 69,458 = 36.19. **The
arithmetic holds and the idea is the strongest thing in either document.** It is a real decision
tool, it is cheap, and no rival does it.

**But a break-even in days implies the two purchases are the same purchase, and they are not.**
A rental is stock-only, cannot be modified, and ends. **The number is honest; the framing is not,
unless it says what you do not get.** That belongs in the design, not in a footnote.

---

## 1. HOW RENTALS WORK — the document as received

From the wiki (Ship renting, updated July 2026 / Alpha 4.8.x) plus live UEX data on 4.10.

**Durations** — real-world time, keeps ticking while logged out:

- 1 day — 0%
- 3 days — 10% off vs 3x daily
- 7 days — 25% off vs 7x daily

Older guides also mention 30 days; the current wiki table only lists 1 / 3 / 7. Worth one in-game
check on 4.10 before hard-coding a month.

**Rules that matter for the UI:**

- Stock loadout only — no component changes
- Insurance included for the rental window
- The same hull can cost different aUEC at different rental desks
- Rental shops are not ship dealers — New Deal sells; Traveler, Vantage, Regal and Teach's rent

**Who rents (UEX live):** about 46 rentable vehicles across about 32 terminals, mainly Vantage,
Traveler, Regal Luxury and Teach's Rentals.

**Example live 1-day rows** (UEX, game_version 4.10.0): Vulture about 69.5k at Teach's; Cutlass
Black about 50–53k depending on station; Prospector about 70–73k.

**Data caveat:** UEX's public `vehicles_rentals_prices` mostly stores a daily number, and the
week and month fields are often copies of the day. So 3- and 7-day totals must either be derived
from the wiki discount table or verified per tier in-game and stored as all three — and CC's
show-conflicts, don't-invent rule applies.

## 2. WHAT OTHER TOOLS DO — the parity bar

**Not verified by this desk.**

- **UEX** — terminal lists, aUEC/day, freshness, API. Best live price source.
- **Wiki** — duration rules and location tables. Best rules and education.
- **FleetYards** — dealer and rental availability in the ship DB and API. Best structured "where".
- **Wipefest and similar** — flat comparison tables, often stale, still showing 3.22 pages. Do not
  copy their freshness.
- **Erkul** — shopping/cart energy for buys; rentals are not the hero. Buy-path UX to beat, not
  rental depth.
- **Citizen Compass** — buy and pledge only. Gap.

**Parity** = every rentable ship shows where, plus a 1-day price, plus durations, with patch and
date stamps.

## 3. ON THE SHIP CARD (CATALOG)

Keep the card scannable; detail one click deeper.

**On the card, always if rentable:**

- Small pill: **Rentable**, alongside In game / Pledge
- One line: *Rent from 50,274 aUEC / day · Traveler · Everus* — always the cheapest 1-day
- If not rentable: omit the line, do not clutter with an em dash

**Filter chip:** Rentable, next to Buyable in game.

## 4. ON EXPAND / THE LOADOUT "WHERE TO BUY" TAB

    Acquire
      Buy    2,513,700 aUEC · New Deal · Lorville   [verified 4.10 · date]
      Rent   from 69,458 / day
               Teach's Rentals · Levski
               1 day    69,458
               3 days   187,537   (-10%)
               7 days   364,655   (-25%)
      Pledge $175 · RSI

- Sort rental rows by cheapest day
- Show the price spread if stations differ — "+X at Vantage ARC-L1"
- Stamp community, patch and date like buy prices
- Note: stock only, no loadout edits, real-time timer

**C1: the 3-day and 7-day rows above are computed, not observed. See section 0.**

**Suggested data shape:**

    rn: true,
    rd: [
      { shop: "Traveler Rentals", place: "Everus Harbor", d1: 50274, d3: 135740,
        d7: 263939, patch: "4.10.0", at: "2026-09-12" }
    ]

Store d3/d7 only when verified; otherwise compute from d1 with a label distinguishing "discount
table (wiki)" from "checked in-game".

## 5. MATCH THEM — the parity checklist

- Rentable flag on every hull that can be rented
- All rental shops and places for that hull
- 1 / 3 / 7 day prices, with 30-day verified
- Patch and last-checked
- Filter and search — "rent Vulture", shop name
- Separate rental orgs from buy dealers in copy and icons

## 6. THEN GO BEYOND — the CC-native win

- **Try-before-buy math** — "N days of rental is about the buy price at the cheapest desk". For
  the Vulture: 2.51M / ~69k, about 36 days. Directly serves the "before you fly" promise.
- **Acquisition ladder on one card** — Rent, then Buy aUEC, then Pledge, with the honest best
  next step.
- **Cheapest desk map** — not just a list; closest and cheapest from where you are, later.
- **Teach's specials called out** when a rental loadout differs from stock; the wiki already notes
  modified rentals.
- **Conflict display** if UEX and the wiki disagree on a day rate — the same Idris-style honesty.
- **"Can't customise" reminder** when someone opens Loadout from a rentable ship's rent path,
  which stops Erkul-style confusion.

**Build order proposed:** ingest UEX rentals and terminal names; confirm the duration model
in-game once; card pill plus cheapest-day line plus Rentable chip; full duration table on detail;
break-even rent-vs-buy; freshness badges.

It offers to draft exact card UI copy and layout next, or a full parity gap list across rentals
and everything else against Erkul, FleetYards and UEX.

---

## 7. C1'S DISPOSITION

**Rentals go into BRIEF-002 as a ranked candidate alongside the landscape list**, carrying the
derived-price ruling and the relationship-not-a-field note as binding constraints.

**Not ordered yet, and deliberately: the UEX ingest.** Republishing another fan site's price data
under our own name is a sourcing and publication question, not an engineering one, and it goes to
Sleven before a line of ingest code is written.

**The 30-day unknown goes to CIC**, not to him.

*C1, 2026-09-12.*
