# The completeness picture, measured — and what "usable for the newest player" has to mean

**From C2. 2026-08-02. Planning input, not a build. Nothing written to the repository.**

Sleven's position: the missing images do not matter much if the information is
structured so the newest player can use it, because the asset is having
everything in one place that other sites scatter.

**That position is correct, and it is now measured rather than asserted.** But
it carries an obligation, in §3.

---

## 1. WHAT AN ITEM PAGE CAN ACTUALLY ANSWER — all 7,728 measured

|  | has a price | no price | total |
|---|---:|---:|---:|
| **has a description** | **2,337 (30%)** | 3,007 (39%) | 5,344 (69%) |
| **no description** | 461 (6%) | 1,923 (25%) | 2,384 (31%) |
| **total** | 2,798 (36%) | 4,930 (64%) | 7,728 |

Read as four different pages:

- **2,337 — the full answer.** What it is, what it costs, which shops, where
  those shops are, how old the price is. **No competitor has this combination
  for a single item.**
- **3,007 — "what it is" without "where to buy".** Still a real page: CIG's own
  description, category, manufacturer, and an honest line about stock.
- **461 — "where to buy" without "what it is".** Weakest class, and the one
  where a picture would help most.
- **1,923 — neither.**

## 2. THE FLOOR IS MUCH HIGHER THAN 25%

The 1,923 with neither description nor price are not blank. Checking what else
they carry — manufacturer, size, RSI store link, pledge-only flag, patch stamp:

    5 extra fields      3
    4 extra fields    202
    3 extra fields    385
    2 extra fields    515
    1 extra field     682
    0 extra fields    136

**Only 136 items — 1.8% of the catalogue — have nothing beyond a name and a
category.** The other 1,787 carry something worth putting on a page.

**So the real shape is:** 69% can say what a thing is, 36% can say where to buy
it, and **98.2% can say something more than its name.** That is a much better
starting position than "no images, 64% unpriced" suggests, and it is the number
that should be quoted internally instead of the scary one.

---

## 3. THE OBLIGATION THIS CREATES

"Usable for the newest player" is not a design intention. Left as one it becomes
a slogan that everybody agrees with and nobody can fail.

**Proposed testable standard — the four questions.** Every item page answers
these in plain words, above the fold, in this order, and **each has a defined
answer when the data is missing:**

| # | question | when known | when not known |
|---|---|---|---|
| 1 | **What is this?** | CIG's description | category + manufacturer + size, as a sentence |
| 2 | **Can I get it, and how?** | "Sold at 4 shops" | "You can't buy this in the game — it came with a pledge" *or* "No shop we know of stocks this" |
| 3 | **What does it cost?** | cheapest price + where | omitted entirely, never "N/A" or "—" |
| 4 | **How sure are you?** | price age + source | "This is a player report, and gear prices swing a lot" |

**Question 4 is the one nobody else answers at all**, and it is the whole reason
to trust the site over a confident wrong number elsewhere.

**This is assertable, which is the point.** Four coverage classes exist in §1;
the test is that a page from each renders all four questions with no blank
field, no dangling label, and no dash standing in for an answer. That is a rule
12 check, not a design review.

### The rule that follows

**A missing field must never produce a visible gap.** Not an empty heading, not
"Unknown", not a grey placeholder box where an image would go. **Sections
disappear; sentences change.** A page with three of four answers should look
like a page that was only ever meant to have three.

This is stricter than the earlier plan's "assert a page renders correctly with
optional fields empty" — that permits an empty-but-present section. At 64%
unpriced and 100% imageless, empty-but-present is most of the site.

---

## 4. WHERE THE "EVERYTHING IN ONE PLACE" CLAIM IS TRUE, AND WHERE IT IS NOT

Worth being precise, because the claim is the strategy.

**True:** UEX has prices and terminals but no item descriptions or stats. Erkul
has ship-component stats but no FPS gear, no prices, no locations. The wiki has
lore and some stats but not current prices. **The join across all of it exists
only here** — item, description, stats, price, shop, location, patch stamp,
confidence.

**Not yet true:** for the 461 price-without-description items we hold *less*
than the wiki does. For liveries and cosmetics we hold almost nothing anyone
wants. And for anything needing an image, we hold nothing at all.

**So the honest version of the claim is narrower and stronger:** *for the things
people actually search for — gear, weapons, components, consumables — this is
the only place the whole answer sits on one page.* It is not "we have everything
about everything," and it should not be sold as that internally, because the
first person to check a livery page will find out.

---

## 5. WHAT THIS CHANGES ABOUT BUILD ORDER

Nothing about the plan. One thing about priority:

**The description wiring (WO-CRAFT-01 §WO-1) is the highest-value item in the
project and this measurement raises it further.** It is the difference between
2,798 pages that can answer anything (36%) and 5,344 that can (69%). It needs no
new data, no decisions, and it is not blocked by the tab layout question that
holds up everything else in Build A.

**Images stay worth chasing for one narrow group** — the 461
price-without-description items, where a picture is the only thing that would
tell someone what they are looking at. 1,387 items carry an RSI store link,
which is the cheapest route to a legitimate image and has not been examined.

---

## 6. NOT VERIFIED

- **Whether the 461 overlap with the 1,387 carrying an RSI store link.** Not
  computed. If they do, that group has a cheap fix.
- **Whether the 136 truly-bare items are real game content** or debug/placeholder
  records. `fps-items.json` is known to carry ~230 placeholder entries, so some
  of the 136 may not deserve a page at all.
- **Whether descriptions are evenly spread across the doorways.** 69% is the
  total; a doorway sitting at 20% would look broken while the average looked fine.
  **Worth computing before the doorway pages are designed.**
