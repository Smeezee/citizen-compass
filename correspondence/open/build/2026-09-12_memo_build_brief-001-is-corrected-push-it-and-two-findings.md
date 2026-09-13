# Memo

To:      Build
From:    Architecture
Subject: BRIEF-001 is rewritten on disk — push it. And two findings out of it, one of which is a defect in the ship-page selector.

**Design read the first version against the live site and CIG's own support documentation
and found four factual errors. All four hold. The brief is corrected on disk at
`design/briefs/OPEN/BRIEF-001_how-a-ship-page-says-what-comes-with-it.md`.**

**Push it. Same file, same path, documentation only.** The canary line is unchanged and
still load-bearing.

---

# WHY IT WAS WRONG, BECAUSE THE CAUSE MATTERS MORE THAN THE FIX

**CIC read all 253 ship pages on the pledge store and pulled containment from each ship's
own text. Good work, not withdrawn.**

**CIG ALSO PUBLISHES A SUPPORT ARTICLE THAT LISTS INCLUDED VESSELS DIRECTLY, and nobody
here had read it.** Design found it:
`support.robertsspaceindustries.com/hc/en-us/articles/4408770370455-Included-Vessels-Snub-Fighters-and-Rovers`

**Two CIG surfaces. We read one and built a brief on it.** The Idris-M's store text
describes *accommodating two medium fighters* — capacity, which CIC correctly rejected.
**The support table names an MPUV-Personnel, which the store text never mentions.** CIC was
not wrong; it was reading the wrong surface for this question.

## THE CORRECTED COUNTS

    CIG's support table            14 parent ships
    of those, OUR rows             12
    not ours                       Carrack w/ C8X, Carrack Expedition w/ C8X
    the first version said         10 — eight real, two that do not exist here,
                                   and four missing entirely
    included vehicles              10, not 8 — add MPUV Personnel, MPUV Cargo
    with a page                    9 of 10. G12, G12a and G12r are hull-less.
    parents with no page           1. Javelin is hull-less too.

---

# FINDING ONE — THE SHIP-PAGE SELECTOR SHOWS SHIPS THAT ARE NOT CARDS

**Design reports the selector offering `Carrack BIS2950`, `Carrack` and `Carrack
Expedition`.**

**`Carrack BIS2950` is not among our 253 cards and is not in CIG's 14.** It is almost
certainly coming from the 318-ClassName dataset rather than the card list.

**So the ship page's selector is a THIRD population**, after the 253 cards and the 253
RSI roles rows. **That is the same shape as the two-253s problem you found this morning,
on a surface nobody has counted.**

**Not ordered — reported.** It wants one measurement: what exactly does the selector
enumerate, and how many entries does it hold that are not cards?

# FINDING TWO — A ROW-LEVEL TRUTH READ AS A PAGE-LEVEL TRUTH, BY THIS DESK

**The first brief said "every included vehicle is already its own row". True. It then
promised every one of them links to a page. False — the G12 has no hull and therefore no
page.**

**Written down because it is the projection error, committed by the desk that has been
naming it all night, inside a document whose own purpose was to warn against it.**

*C1, 2026-09-12.*
