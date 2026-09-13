# Memo

To:      Owner
From:    Architecture
Subject: The front page keep-or-drops — fourteen items grouped into six questions, with a recommendation on the four where I have a technical basis and none on the rest
Status:  Closed

**Q54 shipped and the new front page is missing fourteen things the old one had.
Build measured every one off the served pages and deliberately proposed no direction,
because Q53 records these as yours. I have grouped them into six questions.**

**Everything that is NOT a decision is already filed and moving.** Four dead links, the
missing testing stamp, a deploy guard looking at the wrong page, the resubmit control
and a ship that went missing — all in `NEXT.md` under Q55, none of them waiting on you.

---

## 1. THE PER-ROW CONFIDENCE NOTE — the biggest single item, and I do recommend

    old   254 of 254 rows carry a confidence and source note, 61 distinct texts
    new    50 of 253 cards carry any confidence sentence
           4 of 253 carry a patch number ANYWHERE — text, title, aria-label, data-*

**Recommend: carry it over.** This is the one on the list I would argue for rather than
present, and the basis is the project's own doctrine rather than taste. **Every row
carries `last_verified_patch` and the front end flags unverified data** — that is a
standing architecture decision, not a preference, and the new front page does not do
it. **Your footer claim had to be withdrawn this morning for exactly this reason.**

**The cost is real and it is not layout work.** It is getting provenance onto 253 rows,
and Q61 already records all 254 as unmarked.

## 2. THE FINDING TOOLS — six items, one question

    P6   sorting                9 of 10 columns were sortable. None now.
    P7   budget filter          gone
    P8   jump to manufacturer   the maker grouping survived; the jump control did not
    P9   role taxonomy          19 role buttons WITH COUNTS -> 11 career chips with none
    P10  clear-filter + chip    gone
    P11  back to top            gone, on a page of 253 cards

**P9 is not "restore the missing eight".** The old one was ROLE, the new one is CAREER
— a different taxonomy, not a subset. Answering it means saying which one the site
uses, not adding chips.

**Recommend only a floor, not a set:** on 253 cards, **back to top and a visible
clear-filter are the two that stop being features and start being a usability floor.**
The other four are genuinely your call and I am not pushing one.

## 3. THE ACCESSIBILITY OVERLAY — and it is two questions wearing one name

The old page's DISPLAY panel: 7 presets, 6 fonts, 11 sliders, a CSS export box, saved
automatically. **Largest single absence by volume. None of it on the new page.**

**Four of the seven presets are accommodations rather than styling** — *Easier on tired
eyes*, *Dyslexia friendly*, *Low vision — 150%, bold, high contrast*, *Calm — muted
colour, no motion*.

**Recommend: decide those four separately from the rest.** Retiring a colour preset and
retiring a dyslexia setting are different acts, and I would not want them answered with
one word by accident. **Build flagged this and declined to decide it; so do I.**

## 4. TWO PAGES THAT SERVE RIGHT NOW AND NOBODY CAN REACH

    /keybinds   94,082 bytes, alive today, no link from the front door
    /find       31,387 bytes, alive today, no link from the front door

**Recommend: decide either way, but do not leave them as they are.** Linked or
retired are both fine answers; **orphaned is the worst of the three and it is what we
have.**

**This is the third instance of one shape, not two preferences.** Thirty ships have a
model built, shipped and reachable by no visitor — that is already on the queue. Work
paid for and thrown away, three times, by different routes.

## 5. THE HELP PANEL AND THE FEEDBACK FORM — no recommendation

**P13, the help panel:** gone. Your call, and I have no technical basis for either
direction.

**P14, the feedback form:** gone. **Zero submissions, and you checked yourself that the
zero is real rather than the password gate hiding them.** If it carries over in any
form, the resubmit control is already a filed requirement and waits on this answer.

## 6. THE TWO SHIPS AND THE TWO LINKS — and one of them may not be a defect at all

**P19 — the Javelin and the MOTH now point to RSI instead of our own ship page.**

**Hold this one: it may be correct behaviour rather than a drop, and Build could not
have known.** The record says the Javelin has two paths of equal evidence, one under
`dmg`, and the MOTH has no published dimensions and is refused by the dimension gate.
**If neither has a usable ship page, pointing outward is the honest answer and there is
nothing to restore.** I have not asserted that — it needs one look, and it is on
Build's side of the queue, not yours. **You may get this one back as "no decision
needed".**

**P17 — two outward links dropped:** RSI patch notes, and the Spectrum thread. Small,
your call. **The Spectrum one was not in the eight you measured** — it is one anchor
among 262 and the link count never surfaced it.

---

## WHAT I AM NOT ASKING YOU

**The trademark and disclaimer strip differs between the two pages in both
directions.** Recorded, not filed as work for anyone, because hard rule 8 puts every
word of it with you and says report rather than fix. **No desk has an entry for it,
including me. Raise it when you want to; nobody is waiting.**

---

## QUESTIONS

1. The per-row confidence note — carry it over, or record a decision that the front
   page does not show provenance?
2. The six finding tools — which of sorting, budget filter, jump-to-manufacturer, the
   role-versus-career taxonomy, clear-filter and back-to-top carry over?
3. The accessibility overlay — answer the four accommodation presets separately from
   the fonts, sliders, colour presets and CSS export. Which of each?
4. `/keybinds` and `/find` — linked from the front door, or retired?
5. The help panel, and the feedback form — keep or drop each?
6. The two dropped outward links — keep or drop? (The two ships are on hold pending one
   look by Build and may need no answer from you.)

---

CLOSED:

**Owner, 2026-09-12. Answered and closed.** All fourteen are ruled in `claude/RULINGS_the-decision-packet-twenty-four-answers-2026-09-12.md`, items 4 to 17, with the desk's conflict notes under them. Desktop is built and stabilised first; tablet and phone are adapted and tested after.
