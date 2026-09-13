# Memo

To:      Architecture
From:    Owner
Subject: The outside review of the test site is in. A filter hides most ground vehicles, and one ship shows two prices.
Status:  Closed

The full review is on disk, with Comet's findings word for word:
`claude/RESULT_comet-run-3-test-site-desktop-2026-09-11.md`. 25 findings, 21 of them
CONFIRMED, read off the served site at desktop width.

## CHECKED AGAINST THE PAGE'S OWN DATA BEFORE SENDING

**1. The category buttons hide ships (T-003).** The buttons filter on the career field.
"Ground" shows 7 ships. **29 ships have the role "Ground Vehicle"**, including Ballista,
Centurion, all five Cyclones, Nova Tank, Spartan, Storm, Ursa, X1 and PTV. **34 ships have
no career at all, so no button ever shows them.** The site gives a visitor a confident,
short, wrong answer. This is the worst one.

**2. One ship, two real-money prices (T-009).** The Cutlass Black card says $110, from the
front page's data. Its ship page says $105.00, which is also what the public site says. Two
sources disagree and the site shows both without saying so.

**3. The card and the ship page disagree on role (T-010).** Avenger Stalker: "Fighter" on the
card, "Interceptor" on the page. ATLS: "Ground Vehicle" on the card, "Cargo" on the page.

**4. The ship page drops data the site already has (T-011).** The Reclaimer's "Where to buy"
tab shows two bare dealer names. The card data behind the list carries both prices.

## FROM THE REVIEW, NOT RE-CHECKED BY ME

- T-008: a "PATCH 4.10 from Star Citizen's game files" badge sits under the dealer names and
  reads as if the price was checked against 4.10. The panel beneath says prices are not in
  the game files.
- T-012: the ATLS page says its ports "are listed on the left", and the left is empty.
- T-015 and T-016: contrast measured below 4.5:1 on the dealer city, maker sub-lines,
  counter labels and the testing stamp; the keyboard focus ring is near-black on near-black.
- T-019: an empty box of about 500 px under the shop-data explanation.
- T-020: 30 cards open the RSI store in a new tab with nothing to show they leave the site.
- T-021: the search suggestion covers the category buttons.
- T-022: the "(*)" marker in notes has no key in the legend.
- T-013, T-014, T-017, T-023, T-024, T-025: smaller inconsistencies, listed in the result.

## ALREADY ON THE QUEUE, AS FAR AS I CAN TELL

Map these against the Q55 entries rather than adding duplicates:

- No feedback route (T-005). Already ruled, on the page.
- Clipped card notes hiding the conflict warning (T-018). Same class as Q58.
- Back to the list loses the filter (T-004). Q55.P3.
- No link to /find from the new page (T-002).
- No patch attached to a price (T-007).

## WHAT I WANT

File what is new as queue entries, one per item, with the four above at the top in that
order. They are defects in what the site tells a visitor, not features, so none of them needs
my keep-or-drop. Bring me only anything that does.

---

ANSWERS:

**Architecture, 2026-09-11. Filed as Q62 in `NEXT.md`, your four at the top in your
order. Two things you should know: I added two findings beside your four, and three of
the review's findings are already waiting on you rather than on a desk.**

## YOUR FOUR ARE FILED IN YOUR ORDER

**T-003 is the worst and your reason is the right one.** A filter returning 7 of 29 does
not look broken — it looks like an answer. **It is also the clean separation from
Q55.P9: P9 is which taxonomy the site uses and is yours; T-003 is that the filter
silently drops ships under either taxonomy, and that is not a preference.**

**T-009 has a lead in it.** The seven RSI price corrections already queued put the
Cutlass Black at **$110** — so of the two numbers the site is showing, one is already
known to be stale, and the fix may be upstream of the display rather than in it.
Whoever takes it reads that entry first.

**T-011 and run 4's M-005 are the same defect from two directions and I filed them as
ONE entry.** The ship page is where a visitor goes to learn more and it tells them
less — that inverts the navigation, which is worse than the missing field.

## I ADDED TWO OF YOUR NOT-RE-CHECKED FINDINGS BESIDE THEM, BY YOUR OWN STANDARD

**Your ruling this morning: the test site may be unfinished, but it may not say anything
false.** T-008 and T-012 are the page asserting something untrue.

**T-008 — a badge says the price came from the game files and the panel below it says it
did not.** Two sentences on one screen, one of them false. **This is the footer defect
again, one component over, four hours later.**

**T-012 — the ATLS page says its ports "are listed on the left" and the left is empty.**

**Your order is unchanged; these ride beside your #2 and #3 rather than above them.** I
am telling you I did it rather than doing it quietly.

## THREE OF THE REVIEW'S FINDINGS ARE BLOCKED ON YOU, NOT ON A DESK

**You mapped five onto existing entries. Two of those land on items waiting for your
keep-or-drop, so filing them as defects does not move them:**

    T-002  no link to /find from the new page   IS Q55.P16 — question 4 in your tray
    T-007  no patch attached to a price         IS Q55.P5 and Q61 — question 1 in your tray

**T-005 is correct and closed** — the feedback route is ruled and on the page.

**T-018 I filed as its own entry rather than folding into Q58**, because Q58 is the old
page and this is the new front door: two artifacts, one writer each, and a fix to one
does not touch the other.

**T-004 I did NOT file as a new entry.** Q55.P3 already owns the mechanism and its
DONE-WHEN is extended instead — returning from a ship page restores the filter and the
scroll position, not only the tab. **One mechanism, two symptoms, one entry.**

## THE REST

Every remaining confirmed finding has its own entry. **T-013, T-014, T-017 and T-023 to
T-025 are filed individually and explicitly NOT batched** — they were found separately,
and one commit covering six has six possible causes when it fails.

**Nothing needed your keep-or-drop except what was already waiting on you. Nothing else
is coming back.**

*C1, 2026-09-11.*

---

**Owner, 2026-09-11. Read. Closed.** Run 5, the last of the review, went to you separately.
