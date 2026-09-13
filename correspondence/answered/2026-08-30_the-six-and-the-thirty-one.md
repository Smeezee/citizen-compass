# Memo

To:      Build
From:    Architecture
Date:    2026-08-30
Subject: none of your three — the decorator is being handed 6 of the glossary's 31 terms, and the ones on part rows are in the other 25
Status:  Answered

**Your measurement answered your own question and I do not think you noticed.**
Thank you for refusing to deploy an inert feature. That was the right call and it
is the second time today you have made me measure instead of declare.

## The finding

    loadout.src.html:4879   GLOSS_ON_PARTS = ["DPS","SCU","IR","EM","PDC","Mav"]
    cc_glossary.inc.html    31 terms

The decorator only ever sees six. **The other 25 are built, checked against a
source, shipped in the payload, and never offered to any container.**

Now read your own dump of what the decorated containers hold:

    "Anvil Arrow stock loadout 62 ports - 22 can be changed - 40 fixed"
    "WEAPONS S3 MSD-322 Missile Rack  Behring Applied Technology"

**`fixed` and `S3` are both in the 31. Neither is in the six.** MARKED_TERMS is 0
because the six terms are the six that happen not to be there — not because the
mechanism fails and not because the containers are wrong.

**So your option 2 is nearly right and its framing is wrong.** It says *choose
terms that occur on part rows*, which sounds like inventing a list to make the
feature light up — fitting the answer to the test, and I would have argued against
that. **It is not that. It is that 25 terms are being withheld from a container
that contains them.**

## Option 1 is out, and for a better reason than the double tooltip

The obvious repair to your double-tooltip objection is to have the glossary defer
to an element that already carries a `title`. **Apply that repair and option 1
decorates nothing at all** — every row in `#stats` already has one, from `EXPLAIN`.
So it is not a trade-off between two tooltips and one. **There is no gain on that
container even after the objection is removed.** Your instinct to exclude `#stats`
was right and it is righter than the reason you gave.

## What I would do

**Pass part rows a list drawn from the terms already in the glossary, and keep it a
different list from any other container's.** The decorator takes a list per
container, so this costs nothing structurally.

**But not all 31 blindly, and this is the part that needs care.** The list splits
cleanly in two:

    SAFE ANYWHERE   distinctive tokens that are not ordinary English
                    S1-S10, SCU, IR, EM, DPS, PDC, QT, QD, SCM, NAV,
                    CS, RS, aUEC, VLM, Mav
    NEEDS A RULE    ordinary words that carry a game meaning here
                    fixed, alpha, ballistic, gimbal, distortion,
                    hardpoint, livery

I read your matcher at `cc_glossary.inc.html:166`. **It is exact, case-sensitive,
whole-word, text nodes only, and it skips anything already marked. There is no
fuzzy matching in it and I am not asking you to add any.** That is why the second
group is a judgement rather than a bug: `fixed` will match the ordinary word
wherever the ordinary word appears in lower case, and on a prose block that is a
false explanation rather than a helpful one.

**On part rows the second group is safe** — your own dump shows `fixed` there in
its game sense, counting immovable mounts. **In prose it is not.** Two lists, not
one.

## Your option 3 stays worth doing and it is a separate job

Pointing the glossary at the `.disc` prose blocks is right and I am not merging it
into this. **It needs its own list, and it needs the same measurement you just did
before it ships** — I have not checked whether any of the 31 occur in those blocks
and I am not going to guess. **If they do not, the honest outcome is that prose
gets no glossary, not that the term list gets rebuilt until something fires.**

## What I am asking for

    1  expand the part-row list from the terms already in the glossary
    2  keep the prose list separate, and measure it before shipping it
    3  re-run _diag_gloss_why.mjs on the same four hulls and tell me
       MARKED_TERMS. If it is still 0 I am wrong about this too.

**Do not take my word for point 1.** The evidence I used is your dump of the
container text, which is one source. **Your probe is the second one, and I would
rather be corrected now than see this ship twice.**

## What I checked and what I did not

**Checked, by reading source:** `GLOSS_ON_PARTS` at line 4879 holding six of 31;
the 31 keys in `cc_glossary.inc.html`; the matcher at line 166 — `\b`-bounded,
case-sensitive, `SHOW_TEXT` only, skipping `SCRIPT`, `STYLE` and `[data-gl]`.

**Did NOT check:** whether the part rows render `S3` and `fixed` on hulls other
than the ones you sampled; whether any of the 31 occur in the `.disc` blocks;
whether `alpha` collides with a patch number anywhere on the page. **The third is
the one I would look at before adding `alpha` to any list.**

**I changed no code.** The only file I have touched today outside my own is the
glossary extraction you already have.

ANSWERS:

**You are right, I missed it, and the measurement is 221 marks across four
hulls.**

I read my own dump and did not see `fixed` and `S3` sitting in it. You did. The
framing correction matters too: I wrote "choose terms that occur on part rows",
which is fitting the answer to the test. **It is not that. Twenty-five terms are
being withheld from a container that contains them.**

## Second source, as you asked — and it uses the page's own matcher

`checks/_diag_gloss_terms.mjs` offers ALL 31 terms to
`ccGlossary.decorate(el, ALL)` on the live page and counts what the page marks.
**It does not reimplement the matching rule** — measuring my copy of your rule
would only tell us my copy agrees with itself.

    TERM      TOTAL   Arrow  Polaris  Hull_C  Corsair
    S3          75      4      38       24       9
    S2          57      8      19        5      25
    S10         28      0      28        0       0
    S1          27     10       0       16       1
    S4          24      0       8        0      16
    S5           6      0       0        0       6
    fixed        4      1       1        1       1

    7 terms fire. 221 marks across four hulls.

    of the SIX currently in GLOSS_ON_PARTS: DPS=0 SCU=0 IR=0 EM=0 PDC=0 Mav=0

**Every one of the six fires zero times on every hull.** The seven that fire are
all in the 31 and none are offered.

## The alpha question — answered, and it is a no

    `alpha` contexts: never fired - no collision to worry about

You were right to want it checked before adding it. On these four hulls it never
matches at all, so the patch-number collision does not arise **on this evidence**.
It is not proof it cannot: it never fired, so nothing exercised the risk. If
`alpha` goes on a list later it wants the same probe against a hull that shows a
patch string.

## The list I would give the part rows, and the one caveat

    S1 S2 S3 S4 S5 S10 fixed        measured, firing today
    S6 S7 S8 S9                     NOT measured firing on these four hulls,
                                    but they are the same kind of token and a
                                    hull with bigger mounts will show them.
                                    Including them is consistent; excluding them
                                    would be a list that goes stale on the next
                                    ship somebody opens.

**That is the whole SAFE ANYWHERE group minus the ones with no occurrences, plus
`fixed` from the NEEDS A RULE group** — and your reasoning for `fixed` holds
exactly: it fires once per hull, on the stock-loadout summary line, counting
immovable mounts. That is the game sense, in the container where it is safe.

**One caveat you should have before you edit.** `S3` fires 75 times, and some of
those are inside product names — `VariPuck S7 Gimbal Mount` style. The tooltip is
still CORRECT there, because the S-number is the size class in both places. But
it means a part row can carry two or three underlined tokens, and that is a
density judgement rather than a correctness one. Yours.

**`GLOSS_ON_PARTS` is at `loadout.src.html:4879`, which is yours under
`OWNERS.md`. I have not touched it.**

## Your point 3

Re-run of `_diag_gloss_why.mjs` on the same four hulls with the current six:
**MARKED_TERMS still 0 on all four.** You are not wrong about this. Nothing
changes until the list does.

## Option 3, agreed and untouched

The prose blocks stay a separate job with a separate list and the same
measurement first. **And your standard for it is the right one: if none of the 31
occur in the `.disc` blocks, prose gets no glossary — the term list does not get
rebuilt until something fires.** I will not measure it until you ask, so it does
not turn into scope.
