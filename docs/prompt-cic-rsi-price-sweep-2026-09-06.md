# BRIEF FOR CIC — read every price on the RSI store. Gather only. Change nothing.

    from      C1, 2026-09-06
    for       CIC (Claude in Chrome)
    REVISED   2026-09-06, after Pass 1 came back. Sleven overruled the part of
              this brief that had Pass 2 waiting on a list from C1. See section 3.
    origin    Sleven was saving ship pages for pictures, noticed our prices, and
              checked six Hornets by hand against the store's compare panel.
    status    five of six matched exactly. The sixth had no price on our side at
              all. That is the whole reason this brief exists.

---

## 1. Why this is worth your time, in one number

**87 of our 254 ships carry no pledge price at all.** Not a wrong price — no
price. Twenty-five have no RSI link either, so nobody can even go and look.

The prices we *do* hold are mostly right. Sleven's spot check found five of six
Hornet Mk I variants matching to the dollar. So this is not a correctness rescue.
**It is a coverage job.** A third of the list is blank and the front page prints
that blankness to every visitor.

## 2. The job is extraction. It is not analysis.

**Sleven's words: go and gather the information, extract it, nothing else.**

You cannot see our data and you are not being given it. So you are not comparing,
not judging a price wrong, not deciding a name should be different, not proposing
a fix. You read what the store says and you write it down. C1 does the comparing
afterwards, against files you have no access to.

If you find yourself forming an opinion about what our data *should* say, that is
the signal you have left your lane.

## 3. Two passes, and the second one is small on purpose

**Pass 1 — the store list.** Walk every page of the pledge store ship list,
including the pages past the first. One row per tile:

    name          exactly as the page prints it
    price_usd     the number only, or null when no price is shown
    url           the ship's own page
    read_on       the date

That is one sweep and it covers most of the 87.

**Pass 2 — every variant matrix. REVISED.**

The first version of this brief had you wait for a list of ships from C1. **Sleven
has overruled that: there is no list. Open the variant matrix for every one of the
253 ships Pass 1 found.** His reason is the right one — a list from C1 is a list of
the places C1 already suspects, and the whole point of going to the source is to
find what nobody suspected.

For each ship, open its page, open the Variant Matrix, and record every entry:

    parent, variant_name, price_usd, url, read_on

**A variant that was not in your Pass 1 list is the most valuable thing you can
bring back.** The store list page does not show every hull — Pass 1 already proved
that once, with the sale filter. Flag those rows so they are easy to find.

### The window has to be wide, and that is what stopped you

You reported the matrix rendering as a mobile list with names and no prices, in a
pane 466px wide. That is the whole blocker. **Resize the browser window before
Pass 2 starts** — `resize_window` to at least 1400px wide — and confirm on the
first ship that you are seeing the priced grid Sleven photographed, not the
name-only list. If the priced grid will not render at any width you can set, stop
and report. Do not collect the name-only list and call it Pass 2; a sweep that
silently measured the wrong thing is worse than no sweep.

### Write as you go

253 pages is long enough that something will interrupt it. **Work through the
manufacturers in alphabetical order and write your results out after each
manufacturer, not once at the end.** Append to the same project document. If you
stop halfway, what you have already collected must still be usable, and the next
session must be able to see exactly where you stopped.

**A variant matrix showing `0` is not the same as a variant showing nothing.**
Sleven photographed the F7A Hornet Mk II printing a literal `0` where a price
belongs. Record `0` as `0` and an absent price as `null`, and never merge them.
That distinction is the finding.

## 4. The rules that decide whether this is usable

**Do not fetch anything under `/media/` on that domain.** Rule 22. You are reading
page text. Pictures are Sleven's job and he is already doing it by hand.

**Names exactly as printed.** Rule 17, no fuzzy matching. Do not expand an
abbreviation, do not correct what looks like a typo, do not map a store name onto
a name you think we use. We already found one of these: the store calls it
*Valkyrie Liberator Edition* and we called it *Valkyrie Liberator*. That gets
resolved by hand, on our side, by a recorded alias — not by you deciding they are
the same thing.

**Null over a guess.** Rule 11, fail closed. No estimating, no carrying a price
across from a similar hull, no reading last year's sale price off a forum.

**Every row carries its URL and the date read.** Rule 20. A price with no source
and no date is not evidence and will be thrown out.

**A failure is a result.** Page will not load, price will not render, matrix will
not open — record the URL and what happened, and move on. Two retries, no more.
"I looked and there is nothing" remains a full answer.

## 5. What to hand back

One JSON object and nothing wrapped around it:

    {
      "read_on": "",
      "pass1": [ {"name":"", "price_usd": null, "url":""} ],
      "pass2": [ {"parent":"", "variant_name":"", "price_usd": null, "url":""} ],
      "failures": [ {"url":"", "what_happened":""} ]
    }

Write it into the claude.ai project as `claude/CIC_rsi-price-sweep-2026-09-06.md`
so it does not have to survive a trip through chat.

## 6. Stop conditions

Stop and report to C1 if the store's layout has changed enough that these
instructions no longer describe what is in front of you. Do not improvise a
different method and carry on — a sweep collected by an undocumented method is
worse than no sweep, because nobody can tell later what it actually measured.

## 7. What C1 checked before writing this, and what C1 did not

**Checked:** all 254 rows for a pledge price, an aUEC price and an RSI url; the
six Hornet Mk I variants Sleven photographed, against our figures, by exact name;
the two Valkyrie rows field by field, which is how the empty-duplicate row was
found and folded.

**Did NOT check:** whether the store list pages are still laid out the way the
older CIC briefs describe, and whether the compare panel is reachable without an
account. **Both are yours to find out and to report** — if the compare panel needs
a signed-in session, say so plainly and stop rather than working around it.
