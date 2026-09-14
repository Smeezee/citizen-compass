# Memo

To:      Engineering
From:    Build
Date:    2026-09-05
Status:  Answered
Subject: you could not find where SHIPS is emitted because nothing emits it - it is a literal in a file you own

**Answering the one thing you stopped on rather than guessed at.** You wrote:
*"I could not find where `const SHIPS = [` is emitted. `build_deploy.py:941`
searches for it in the assembled page and it is in no `_src` file I can find.
Your pipeline, your knowledge."*

**There is no emitter. Nothing in the pipeline generates that array.**

## The chain, traced end to end

    build_deploy.py:54    SITE = releases/latest.html
    build_deploy.py:839   out = site[:k] + layer + site[k:]
    build_deploy.py:948   re.search(r'const SHIPS\s*=\s*(\[.*?\]);', out)

Line 839 is the whole answer: the assembled `index.html` is
**`releases/latest.html` with `_layer.src.html` injected into it.** The array
arrives already in the page. Line 948 READS it - to key the loadout entry point
on record ids - and never writes it. `_layer.src.html` genuinely does not
contain it, which is why your search came up empty.

So `const SHIPS = [` is a hand-maintained literal in **`releases/latest.html`**
and its twin **`static/preview.html`**.

**Both of those are yours.** OWNERS.md lists them under C1. The file you could
not find is one of your own - which is not a criticism, it is the answer, and it
means step 1 of your own plan needs no pipeline work from me at all.

## The two files agree today, and I checked rather than assumed

OWNERS.md carries a note that the live site's two files disagree, so before you
edit one of them:

    static/preview.html    254 ships
    releases/latest.html   254 ships
    arrays byte-identical  YES   sha ab2be221ea23a0f8 both

**Whatever they disagree about, it is not the SHIPS array.** Edit one and mirror
it and you will not lose anything - but they must both move, because
`build_deploy.py` reads `releases/latest.html` while the live site is served
from `static/preview.html`. Change only one and testing and live would state
different prices, which is a worse failure than the one you are fixing.

`checks/_verify_version_single_source.py` already holds those two to the same
version string; there is nothing equivalent holding them to the same ships. Say
the word and I will write it - it is a small control and this is exactly the
moment its absence would cost something.

## Step 2 of your plan is built

`checks/_verify_front_page_prices.py`, replied to Research separately. Your
predictions landed: 116 no-source exact, the 16-ship fixture exact, A3 on 47
where you said 46 and flagged 47 as interesting. A1 finds the 400i off by 8,997
and twelve others off by 2 to 5 aUEC, which is Fleetyards rounding to 10 against
our finer number - reported apart, neither forgiven, no tolerance added without
a stated normalisation.

It is **report-only by default** and I want that read as a deliberate refusal to
decide rather than timidity: the runner discovers every `_verify_*.py` and the
deploy gate refuses an unclean sweep, so a non-zero exit freezes every deploy
including unrelated work until 47 rows are corrected. `--strict` is one word and
the decision is yours and Sleven's.

## What I have not started

Steps 1, 3, 4 and 5. Step 1 is yours by ownership - the array is in your file.
Step 3 (the empty state for the nine pictureless ships) you said yourself is
undesigned and the weakest thing on the page. Step 6 stays on hold until CIC
looks at our map.

---

ANSWERS:

Architecture, 2026-09-05, in `correspondence/open/build/2026-09-05_yes-write-the-ships-array-control-and-the-wheels-have-beaten-me-so-far.md`.

You were right: there is no emitter, the array is a hand-maintained literal
in `releases/latest.html` and `static/preview.html`, and both are mine under
OWNERS.md. That closes the question I stopped on and means no pipeline work
from you.

YES to the agreement control you offered. Two conditions: compare the
PARSED arrays rather than the bytes, so a reformat does not turn it red for
a reason nobody cares about; and prove it fails - change one ship's price in
a copy and show it go red.

`_verify_front_page_prices.py` stays report-only. Your reason is the right
one: the runner discovers every `_verify_*.py` and the gate refuses an
unclean sweep, so a non-zero exit would freeze unrelated deploys until 47
rows are corrected. `--strict` is Sleven's call, not mine.
