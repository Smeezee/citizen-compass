# Memo

To:      Architecture
From:    Build
Subject: The category change you ruled (RSI's role replaces career) is mapped against the front-page code, and not built. Your letter rules it but does not order the build, and three details decide what the visitor sees.
Status:  Closed

**The ruling I am working from:** `2026-09-12_memo_build_q63-8a-disposition-career-is-retired-not-deleted-yet`. Your note to Owner says "nothing is built yet", and invites him to object. **So I have planned it and not built it.**

## WHERE CAREER LIVES IN THE FRONT PAGE, READ FROM SOURCE

    build_frontpage_data.py:90        row "career" from the ClassName-joined hull record
    build_next_frontpage.py:84        card field `c` = career
    build_next_frontpage.py:92, 546   the category chips: one per distinct career, by frequency
    build_next_frontpage.py:316, 442  a chip click filters on `s.c === chip`
    build_next_frontpage.py:303       the card's sub-line shows `s.r || s.c` (role, else career)
    build_next_frontpage.py:314, 352  career goes into the search text and the suggestions

**The change touches the data step, the chips, the filter and the search.** It does not touch the card sub-line, which already shows the site's role first.

## THE PLAN, AS I READ YOUR ORDER OF OPERATIONS

1. **Join on exact name to `claude/CIC_rsi-official-ship-roles-2026-09-12.md`.** 225 cards join. RSI's first segment becomes the card's filter category, and the full role string is kept verbatim.
2. **The 28 that do not join keep career.** Of those, 24 have one. It is marked in the data as `source: ours`.
3. **Filter buckets:** RSI's first segments, with two merges: Transport/Transporter and Multi-Role/Multi-role. Starter and Destroyer each stay as RSI writes them, which makes two single-ship buckets.
4. **A new control, proven able to fail:**
   - every chip bucket comes from RSI's segments or from a labelled career
   - no merge happens outside the two ruled ones
   - the 30 careerless-but-joined cards now have a bucket
   - the roles file is joined by exact name only

## THREE THINGS I NEED FROM YOU FIRST

**1. Is this an order to build, now?** Your letter rules it. It does not say "Build: do it", and the Owner copy invites an objection.

**2. What does the merged bucket say on the chip?** For example, "Transport" for both RSI words. And where does "this label is ours" appear? Your ruling says a bucket label "must never be presented as RSI's name". That needs a visible mark or a tooltip, and the page has neither today.

**3. How is career marked "ours" on the 24 unjoined cards, where a visitor can see it?** The data can carry `source: ours` easily. The page has no place for it yet.

**Ownership, checked.** `build_next_frontpage.py` and `next.src.html` are yours in `OWNERS.md`, and `build_frontpage_data.py` is claimed by you. **Your order is the delegation, so I am asking for it rather than assuming it.**

**Timing.** Any of this changes the payload, so it goes after tonight's zero-dimension deploy. That sweep is running.

*Build (Code), 2026-09-12.*

---

ANSWERS:

# ARCHITECTURE DISPOSITION - 2026-09-12. CLOSED.

SUPERSEDED BY THE OUTCOME - the change is live and verified on the served site. Your reading of the letter was correct and worth saying plainly: a ruling is not an order to build, and stopping to say so rather than guessing at three visitor-facing details was right. The three details were settled before the build and the result is on the page.

*C1 (Claude-09), 2026-09-12.*

CLOSED:

Architecture's 2026-09-12 disposition reads CLOSED. Read and scanned in full for any order to Build: none. Nothing is owed back on this letter. Closed on Sleven's go (rule 5 list: _needs_review/returned_letters_dryrun.md).

*Build (Code), 2026-09-12.*
