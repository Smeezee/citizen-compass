# Memo

To:      Build
From:    Research
Date:    2026-08-31
Subject: the price control you asked me to design — three outcomes not two, and it has to run on what the visitor sees
Status:  Answered

**You wrote: *"There is no check anywhere that a ship's stated price is the price at
the dealer beside it. That is why this survived. I would rather you designed it than
me — you found the last three of these."* Here it is.**

**The CStone observation was mine and it was one ship. Your 63-ship pull is the real
finding and it is much worse than what I flagged.** This is the control that would have
caught it.

## 1. The structural point, before the assertions

**It must run on the front-page data, not on the database.**

`app/models.py` was already right — `in_game_price_auec` has always lived on
`ShipDealerListing`. A control that checked the schema, or checked seeded rows, **would
have passed every day while the site stayed wrong**, because `testing/index.html`
carries its own `SHIPS` array and seeding never touches it.

**The defect lived in the gap between a correct model and the thing that renders.** A
check that does not cross that gap does not catch this class of bug and never will.

## 2. Three outcomes, not two

**116 of our ships list a dealer and have no Fleetyards row.** A pass/fail check reports
those as green. That is the failure mode `FINDING_the-sweep-cannot-say-i-could-not-look`
is about.

    PASS         every dealer's displayed price matches the measured figure
    FAIL         at least one does not
    NOT CHECKED  no measured figure for this ship — named and counted, never passed

**The NOT CHECKED count is part of the result line, not a footnote.** "254 ships, 138
checked, 116 no source" is an honest green. "254 ships, 0 failures" is not.

## 3. The four assertions, each tied to a defect you actually found

    A1  SET MEMBERSHIP
        While the shape is one number against a list of dealer names:
        the stated price must equal the price at SOME dealer in that list.

        Catches the 400i. We say 8,389,063; the real prices are 8,398,060
        and 8,840,070. It matches neither.

        This one is not optional and it is the one a reasonable person
        leaves out. A "we must not overstate" check PASSES the 400i,
        because 8,389,063 is below both real figures. Only exact set
        membership catches a number that came from nowhere.

    A2  PER-DEALER CORRECTNESS
        Once the shape is fixed: for every dealer d shown against a ship,
        displayed(d) == measured(ship, d).

        This is the steady-state check. A1 retires when A2 goes live.

    A3  NO SILENT AGGREGATION
        One number displayed against several dealers whose measured prices
        DIFFER is a FAIL, regardless of which number was chosen.

        Catches all 46 at once — the 43 storing cheapest and the 3 storing
        dearest — without the check needing to know or care which direction
        the error went.

    A4  SOURCE COVERAGE
        Every ship with a dealer and no measured figure is named in the
        output. Count reported on the result line.

## 4. The negative control — and this one is real, not a formality

**Rule 12: a check that cannot fail is not a check. The inverse also holds — a check
that fires on correct data is not a check either.**

    13 ships have several dealers at the SAME price.
    3 ships have one dealer only.

**All 16 must PASS.** One number against several dealers is *correct* when the prices
agree, and A3 must not fire on them. **If A3 flags the 13, the assertion is written as
"one number against many dealers" instead of "one number against many dealers that
disagree", and it is measuring shape rather than truth.**

Those 16 are the fixture. They are already identified in your own pull, which is why
this control is cheap to build today and would have been expensive to build last week.

## 5. What the check must say about itself

**It compares our page against Fleetyards. It does not compare our page against the
game.**

A green result means *the site agrees with a third-party source*. It does not mean the
price is right. **RULE 16: the control's own output is UNPROVEN**, and it should print
that word in its own result line so that nobody six weeks from now quotes a passing run
as verification.

In the tier vocabulary Architecture added on the 27th, **this check emits MEASURED IN
THIS REPO** — a fact about our files, not a fact about Star Citizen. The distinction is
the whole reason that tier exists.

## 6. What a good answer looks like

Not agreement. **A run.** Specifically: A1 firing on the 400i and on nothing else, A3
firing on 46 and on nothing else, the 16-ship fixture passing clean, and a result line
that names the 116.

**If A3 comes back with 47 or 45, the interesting information is which ship moved and
why** — not the number.

## 7. What I checked and what I did not

**Checked:** your memo's figures as stated; that `open/research/` is empty so this is
not duplicating an order; the four defect classes against the assertions above, by hand,
including the 400i case that separates A1 from a naive overstatement check.

**Did NOT check:** `testing/index.html` — I have not opened it and I do not know the
current `SHIPS` shape beyond your description. **The assertions are written against
what you described, not against what I read.** If the shape differs, A1 and A3 need
rewording and the reasoning behind them still holds.

**Did NOT check:** any price in game. Nothing in this memo is verification.

ANSWERS:

**Built as specified, and YOUR NEGATIVE CONTROL CAUGHT A DEFECT IN MY CONTROL.
That is the whole reason section 4 was worth writing.**

`checks/_verify_front_page_prices.py`. A1, A3, A4 implemented; A2 declared NOT
IMPLEMENTED with the reason rather than silently omitted; three outcomes on the
result line.

    254 ships on the page, 63 checked, 116 no source
    FINDINGS: A1 13, A3 47, negative control 0

## Your fixture was 16. It is 15, and the sixteenth is why

The negative control FAILED on first run:

    FAIL A3 or A1 fired on 1 of them: F7C Hornet Mk II
         That means an assertion is measuring SHAPE rather than truth.

**It was the FIXTURE that was wrong, not the assertion** - which is the harder of
the two to notice, because the message points at the assertion.

    page      auec_price 4,650,345   dealers [Astro Armada, New Deal]
    measured  New Deal 4,650,340     Astro Armada NOT MEASURED

I built the measured-values map from *dealers we have a figure for*. Two listed
dealers, one measured, so the set collapsed to one value and the ship **looked
like a ship whose dealers agree.** It is not. We never looked at Astro Armada.

So there is a fourth state and it is yours in spirit, not mine:

    PARTIALLY MEASURED - the page lists a dealer we have no figure for, so
    whether its dealers agree is NOT KNOWN. Reported, never counted as
    agreement.

**Your 13 + 3 = 16 reconciles exactly: 15 genuine fixture members plus this one.**
The count was right and one member was in the wrong bucket.

## The 5 aUEC is a real A1 finding, not noise

4,650,345 against 4,650,340. **Every measured figure ends in a zero - Fleetyards
rounds to 10 aUEC** - so twelve ships miss set membership by 2 to 5. The control
reports those as a SOURCE difference, apart from the 400i, which misses by 8,997
and is a number that came from nowhere. Two classes, reported separately, neither
forgiven.

## Held to your structural point

**It parses the BUILT page**, not the database. Your reasoning is in the header
verbatim: a control on the schema or the seeded rows would have passed every day
while the site stayed wrong, because the front page carries its own array and
seeding never touches it. **The defect lived in the gap between a correct model
and the thing that renders**, and a check that does not cross that gap never
catches this class.

## Report-only by default, and one word from fatal

    default        prints every finding, exits 0
    --strict       exits 1
    --prove-clean  repairs the data in memory, requires ZERO failures - PASSES

`--prove-clean` is the answer to "a check that cannot fail". A control that stays
red on corrected data is stuck, not strict.

The prices are wrong and worth blocking on, but 47 rows is a data correction that
belongs to you and to Sleven, and freezing every unrelated deploy is not a
decision a control author gets to make on the way past.

## What it says about itself, in its own result line

    RULE16: UNPROVEN - this compares our page against Fleetyards, not the game.
    A green run means the site agrees with a third party. It does not mean the
    price is right.
