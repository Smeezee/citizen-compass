# RULING from Sleven — what folds into a parent ship. And C1's test for it does not work yet.

Date: 2026-09-06
From: C1
To: Code

## The rule, in his words

> "If it is considered an addition, but when actually looked at the stats, it's just a
> paint job on its own URL page, it goes inside of the main hull. If it is a variant that
> is physically different, whether it's different fins or guns or whatever the combination
> is, there typically is a physical, a slight physical difference, and you can see that in
> the 3D models. If there's a difference physically, then it is its own ship. Like the
> Cutter and the Cutter Rambler and the Cutter Scout. The same ship, but they are
> different variants, and they have different features. Physically and technologically."

And, asked whether gear alone counts:

> "I know that the model only catches physical, but we do know that the Cutter Scout has
> different technology... like it has better scanners."

**So there are two ways to earn a card, and one way to lose it:**

    different 3D model          -> its own card
    different equipment         -> its own card
    paint and nothing else      -> folds into the parent as a line

The Valkyrie Liberator Edition is the worked example he ruled on directly: same hull, same
price, so it became a line on the Valkyrie's card rather than an empty row of its own.

## And here is the part you need more than the rule

**I built a test for it and the test does not work. Do not run the 22 through it.**

The idea was sound — CIG's own data holds an `editions` block, 93 pairs, and 92 of the 93
inherit the parent's model rather than carrying their own. Add a loadout comparison and it
should sort them.

**What it actually produced: 18 of 22 "own card", 4 refused, and 0 folds.**

Three things wrong with it, all mine:

**1. A test that almost never says no is not a test.** Rule 12. Eighteen passes out of
eighteen judgeable cases means it is not discriminating, it is waving things through.

**2. Absence from CIG's `editions` block is being read as proof of being a real ship.** It
is not. That block has 93 entries and nothing establishes it is complete. Fourteen of my
eighteen "own card" verdicts rest on that assumption alone.

**3. It cannot judge the one case we know the answer to.** The Valkyrie Liberator Edition
has no CIG file under the name we hold, so the test refuses it — the single case where
Sleven has already ruled, and the test is silent. **A test that cannot reproduce a known
answer has not been validated against anything.**

## So what you should actually do

**Nothing with the 22 yet, on this account.** The rule is settled; the automatic sort is
not. Sorting them stays a hand call against the rule above until a test exists that can
reproduce the Valkyrie answer without being told it.

**B2 is a separate question and is unaffected.** The family key gap you found stands exactly
as you filed it, and my answer of 15:14 is unchanged: `family_id` NOT NULL, three sources in
order — store URL, then CIG ClassName on exact match, then a hand-entered mapping — and a
disagreement between sources is reported rather than resolved.

## Still needing Sleven, not me

**The commit of `build_frontpage_data.py`.** Untracked, mine, and rule 2 puts the go-ahead
with him. He has not given it. Nothing else in B0 moves until he does.

*C1, 2026-09-06.*
