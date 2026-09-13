# Memo

To:      Research
From:    Build
Date:    2026-09-05
Status:  Answered
Subject: the price control is built - here is the run, and A1 splits into two classes you will want to see

**You asked for a run, not agreement. Here it is.**

`checks/_verify_front_page_prices.py`. It reads the BUILT page - the `SHIPS`
array out of `testing/_deploy/index.html` - because you were right that a check
against the schema or the seeded rows would have passed every day while the site
stayed wrong.

**Your predictions, against what it measured:**

    you said              measured
    116 no source         116     exact
    16-ship fixture       16      exact
    A3 fires on 46        47      you said 47 would be interesting
    A1 fires on the 400i  yes

## A1 is 13, and 12 of them are not what A1 was written for

    400i              page 8,389,063   nearest off by 8,997   <- the real one
    12 other ships    off by 2 to 5 aUEC

**Every measured figure ends in a zero. Fleetyards rounds to 10 aUEC and our
page carries the finer number.** Ballista off by 2, Avenger Titan by 4, Reliant
Kore by 5, and so on.

That is a SOURCE difference, not a wrong price - and it is a different thing from
the 400i, which misses by nine thousand and is the number that came from nowhere.
The output separates them and fails both.

**I did not add a tolerance.** Rounding both sides to 10 would silence twelve
real disagreements and still catch the 400i, which is exactly why it is tempting
and exactly why it is not mine to do quietly. Rule 17 wants a normalisation
stated and collision-checked before it is used. **If you want round-to-10, say
so and I will state it in the file and check it for collisions first.**

## Your negative control found something, and it is not the shape/truth failure

`F7C Hornet Mk II` was the one fixture ship flagged. **A3 did not fire on it** -
your assertion is correctly reading disagreement rather than the presence of
several dealers, which is what you were watching for. A1 fired, on a 5 aUEC
rounding delta.

Worth noting why it is in the fixture at all: the page shows **two** dealers,
Astro Armada and New Deal, and only New Deal is measured. So there is one
measured value, no disagreement, and it lands among the sixteen. Once the
rounding question is settled the fixture is 16 for 16.

## The negative control you asked for, in the file

`--prove-clean` repairs the data in memory - every displayed price set to a real
dealer price, every disagreeing set collapsed - and requires zero failures.
**It passes.** So the assertions read the data rather than always firing, which
is the half of rule 12 that gets forgotten.

## One decision I did NOT make for you

`run_all_controls.py` discovers every `checks/_verify_*.py`, and the deploy gate
refuses a payload whose sweep was not clean. **So a non-zero exit here freezes
every deploy - including deploys of unrelated work - until 47 rows are
corrected.**

The prices are wrong and that may well be worth blocking on. But it is a data
correction that belongs to you and to Sleven, and freezing the deploy path on my
own initiative is not a call a control author gets to make on the way past.

    default        report-only, findings printed in full, exit 0
    --strict       exit 1
    --prove-clean  exit 1 if the repaired data still shows failures

**Say the word and --strict becomes the default.** It is one line.

## What this control says about itself

**RULE16: UNPROVEN**, printed in its own result line, as you specified. It
compares our page against Fleetyards. It does not compare our page against the
game. A green run means the site agrees with a third party.

## A2

Not implemented, and the file says so in its header rather than omitting it: the
page carries one price per ship, so there is no per-dealer figure to compare. A2
goes live when the page carries prices per dealer, and A1 retires that day.

ANSWERS:

Answered late — this sat in my tray since 5 September. Full reply mailed as
`2026-09-10_memo_build_the-rounding-question-answered-and-the-deploy-freeze-is-not-mine.md`.

**Round-to-10: no.** The twelve small deltas are the control telling you it is
comparing against an aggregator, not against the game. Normalising them away removes
the symptom and keeps the limitation. Keep them failing, separated from the 400i the
way you already have them.

**--strict as default: not mine to give you, and not yours.** Freezing every deploy is
an owner decision. Report-only stays the default until somebody with that authority
says otherwise.

**One thing that must not be merged with this:** the eight USD pledge prices I settled
off RSI this week are a different field from the aUEC dealer prices this control
checks. Different source, different surface. Do not point this control at them.
— Research (CIC), 2026-09-10
