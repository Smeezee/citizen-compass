# Memo

To:      Architecture
From:    Build
Date:    2026-09-11
Subject: Q55 — the proposed queue entries, one per item, from the Q53 inventory. Yours to file; I cannot write NEXT.md.
Status:  Answered

**Q55's DONE-WHEN is entries, not implementation:** *"each item the inventory
marked ABSENT or CHANGED has its own queue entry, its own DONE-WHEN, and lands
on its own."* **`NEXT.md` says one writer, C1, and Code never edits it**, so the
entries are written here in full and filing them is yours. Number them as you
like — I have used P-numbers precisely so they do not look like queue IDs.

**Every figure below was read off the SERVED pages in a real browser**, and the
full working is `docs/FINDING_the-front-page-inventory-2026-09-11.md` with raw
JSON in `_needs_review/q53/`. **Q54 has since shipped**, so where the swap
changed an answer I have re-stated it rather than leaving the inventory's
wording.

**I have not decided any keep-or-drop.** Q53 records that as Sleven's, in his
words. Group B below is his and I have deliberately not proposed which way.

---

## GROUP 0 — CLOSED BY Q54. RECORDED SO NOBODY RE-OPENS IT

**The password gate.** The inventory marked it ABSENT from the new page. Q54
made the gate follow the front door, so `/` presents it to a fresh visitor and
`/classic` does too. **No entry needed. Closed.**

---

## GROUP A — SETTLED OR MECHANICALLY FORCED. THESE CAN LAND WITHOUT A NEW DECISION

### P1 — THE FOUR SECTION ADDRESSES STOPPED RESOLVING WHEN THE FRONT DOOR MOVED
**DONE-WHEN** `/#matrix`, `/#dev`, `/#calendar` and `/#legend` each land a
visitor on the matching content on the served site, and a control proves all
four from served bytes rather than from the page source.
**BLOCKED-BY** nothing.

**Measured.** On the old page all four resolved to a real element and scrolled
to it — `scrollY` 307, 16576, 17602 and 17808. On `/next` all four report **no
element with that id** and `scrollY` 0. Since Q54, `/` IS `/next`, **so those
four URLs are broken on the front door right now.** Anyone who bookmarked or
shared one has a dead link today.

**Why this is not a preference.** It is a live address that stopped resolving.
`#matrix` has no counterpart at all and belongs in P2; the other three have tab
views and need only an address.

### P2 — THE TABLE VIEW HAS NO COUNTERPART AND `#matrix` POINTS AT NOTHING
**DONE-WHEN** either `#matrix` resolves to something on the front door, or it is
recorded as deliberately retired in a dated decision and the dead anchor is
stated. **Not left as a link that silently goes nowhere.**
**BLOCKED-BY** P1 for the mechanism.

### P3 — NOTHING ON THE FRONT PAGE HAS AN ADDRESS
**DONE-WHEN** a visitor on any tab can copy the URL, send it, and have the
recipient arrive on the same tab; and the back button returns to the previous
tab. Proven on the served site.
**BLOCKED-BY** nothing. **Shares a mechanism with P1 and is still its own item**
— P1 is four specific old URLs, this is every tab from now on.

**Measured.** Clicking each of the four tabs leaves `location.hash` and
`location.search` empty. `?q=` is ignored on both pages, so a search cannot be
shared either — and that one is not a regression, it never worked.

### P4 — THE RESUBMIT CONTROL IS A STATED REQUIREMENT AND IT IS BUILT TODAY
**DONE-WHEN** whatever comment route exists on the front page resets after each
submission so one person can send several without reloading.
**BLOCKED-BY** Sleven's keep-or-drop on the form itself (Group B, P14) — **but
the requirement does not depend on that.** Q55 already states it as his, from
the round of feedback that produced the form, and says it survives even if the
form is replaced.

**Measured.** The old page's FEEDBACK panel carries `cc-fb-again`, labelled
*"Send another response"*. **It exists and works today, and the new front page
has no comment route at all**, so the requirement is currently satisfied by a
page that is no longer the front door.

---

## GROUP B — HIS KEEP-OR-DROP. I HAVE NOT PROPOSED WHICH WAY

**Each of these is a capability the old front page has and the new one does
not. The entry states the measurement and the DONE-WHEN for carrying it over;
none of them should be started until he says so.**

### P5 — THE PER-ROW CONFIDENCE NOTE
**DONE-WHEN** every ship row on the front page carries the confidence and source
note that the old page carried, or a dated decision records which subset does
and why the rest do not.
**BLOCKED-BY** his decision. **This is the biggest single difference on the
list and it is a data-quality one, not a layout one.**

**Measured.** Old: **254 of 254** rows carry a CONFIDENCE / NOTES cell, 61
distinct texts, 165 of them *"Confirmed — starcitizen.tools 4.9.0"*. New: **50
of 253** cards carry any confidence sentence, and **4 of 253** carry a patch
number anywhere — rendered text, `title`, `aria-label`, or any `data-*`
attribute, all four checked. **The footer no longer claims otherwise** (Q54),
but the data is still missing from the page.

**Related and not the same item:** Q61 is the database's
`last_verified_patch`; this is what the front page shows a reader.

### P6 — SORTING
**DONE-WHEN** the front page can be reordered by the columns the old page could
be reordered by, or a decision records that sorting is retired.
**BLOCKED-BY** his decision.
**Measured.** Old: a click handler on **9 of 10** headers — ship, role, aUEC
price, each of the five dealers, and pledge price. New: no `th`, no sort
control, and no sort word anywhere in the page text.

### P7 — THE BUDGET FILTER
**DONE-WHEN** a visitor can filter the front page by what they can afford.
**BLOCKED-BY** his decision.
**Measured.** Old: a number input, placeholder `e.g. 3,000,000`. New: nothing
equivalent.

### P8 — JUMP TO MANUFACTURER
**DONE-WHEN** a visitor can jump to a maker's ships without scrolling the whole
list.
**BLOCKED-BY** his decision.
**Measured.** Old: a `MANUFACTURERS` tab plus 18 maker buttons with counts. New:
**the grouping survives** — the list is under maker headings with counts like
*"28 ships · 19 buyable in game"* — **and the jump control does not.**

### P9 — THE ROLE TAXONOMY AND ITS COUNTS
**DONE-WHEN** the front page's category filter covers what the old page's
covered, or a decision records the new taxonomy as the intended one.
**BLOCKED-BY** his decision.
**Measured.** Old: **19 role buttons with counts** (`Fighter 59`, `Cargo 44`,
`Ground Vehicle 29`, `Exploration 24`, `Racing 20`…). New: **11 career chips
with no counts.** **This is a different taxonomy, not a subset** — the old one
is role, the new one is career, so "restore the missing eight" is not what this
asks.

### P10 — CLEAR-FILTER AND THE FILTER-STATE CHIP
**DONE-WHEN** a visitor can see that a filter is applied and clear it in one
action.
**BLOCKED-BY** his decision.
**Measured.** Old: `cc-bclr` (Clear filter), `cc-state` with `cc-state-clr`
(Reset). New: neither.

### P11 — BACK TO TOP
**DONE-WHEN** a visitor at the bottom of 253 cards can return to the top without
scrolling.
**BLOCKED-BY** his decision.
**Measured.** Old: `#backToTop`. New: absent.

### P12 — THE ACCESSIBILITY OVERLAY
**DONE-WHEN** the front page offers the display controls the old one offered, or
a decision records them as retired from the front page.
**BLOCKED-BY** his decision. **This is the largest single absence by volume.**
**Measured.** Old `DISPLAY` panel: 5 sub-panels, **7 presets** (including
*Easier on tired eyes*, *Dyslexia friendly*, *Low vision — 150%, bold, high
contrast*, *Calm — muted colour, no motion*), **6 font choices**, **11 sliders**,
a CSS export box with Copy, Reset all, and *"Settings saved automatically"*.
New: none of it.

**Worth saying plainly and not deciding for him:** four of those seven presets
are accessibility accommodations rather than styling.

### P13 — THE HELP PANEL
**DONE-WHEN** the front page offers help, or a decision retires it.
**BLOCKED-BY** his decision.
**Measured.** Old: `HELP` tab with a stepped panel and `← Back a step`. New:
absent.

### P14 — THE FEEDBACK ROUTE
**DONE-WHEN** his decision is recorded either way, and if it carries over, P4's
reset requirement is met.
**BLOCKED-BY** his decision. **Q53 already records that he checked the form
himself: zero submissions, and that the zero is real rather than a symptom of
the password gate.** He corrected his own earlier caveat on that. **The
keep-or-drop is still his and is not made.**
**Measured.** Old: a Jotform iframe — which is why it never appeared in an
anchor-based link count, it is a frame `src` — plus `cc-fb-again`.

### P15 — THE KEYBINDS PANEL, AND `keybinds.html`
**DONE-WHEN** his decision is recorded, and if the front page is to reach the
keybinds page at all, it links to it.
**BLOCKED-BY** his decision.
**Measured.** Old: a `KEYBINDS` tab with its own board, a device search box and
`Capture everything (full screen)`, **and** a plain link to `keybinds.html`.
New: neither. **`/keybinds` still serves, 94,082 bytes — the page is alive and
unreachable from the front door.**

### P16 — THE FINDER, AND `find.html`
**DONE-WHEN** as P15.
**BLOCKED-BY** his decision.
**Measured.** Old: a `FIND IT` tab and a link to `find.html`. New: neither.
**`/find` still serves, 31,387 bytes — alive and unreachable from the front
door.**

### P17 — THE TWO OUTWARD LINKS THAT WERE DROPPED
**DONE-WHEN** his decision is recorded for each.
**BLOCKED-BY** his decision.
**Measured.** Gone from the front page: RSI patch notes
(`robertsspaceindustries.com/en/patch-notes`) and the Spectrum thread
(`.../spectrum/community/SC/forum/190048`). **The Spectrum one was not in the
eight he measured** — it is one anchor among 262 and the link count did not
surface it.

### P18 — THE SHIP LIST IS ONE SHORT
**DONE-WHEN** `Valkyrie Liberator` is either on the front page or recorded in a
dated decision as a name the old page should not have carried.
**BLOCKED-BY** one lookup, not a decision — **and rule 19 says the ambiguity is
refused rather than resolved by picking, so somebody has to look rather than
guess.**
**Measured.** 254 rows against 253 cards. Compared by exact equality both ways,
`Valkyrie Liberator` is the only name with no counterpart under any reading.
`Valkyrie` and `Liberator` exist separately on both pages.

### P19 — TWO SHIPS LOST THEIR SHIP PAGE
**DONE-WHEN** the Javelin and the MOTH either link to `loadout.html` from the
front page as they used to, or a decision records why they point outward.
**BLOCKED-BY** his decision.
**Measured.** Old: 221 distinct `loadout.html#ID` targets. New: 219.
`AEGS_Javelin` and `ARGO_MOTH` link to RSI instead.

### P20 — THE FIELD GAPS ON THE NEW CARD
**DONE-WHEN** each named gap is either filled or recorded as unknown in the way
hard rule 11 requires — an honest blank, not a guess.
**BLOCKED-BY** nothing technical; it is data work and it should be sized before
it is started.
**Measured, out of 253 cards:** 16 show no pledge price (`Ballista
Dunestalker`, `Ballista Snowblind`, `Khartu-al`, `San'tok.yai`, `ATLS GEO IKTI`,
`ATLS IKTI`, `ATLS IKTI RAD`, `CSV-FM`, `RAPTOR`, `Starlancer BLD`, `Aurora CL`,
`Aurora ES`, `Aurora LN`, `Aurora LX`, `Aurora MR`, `Nova Tank`); 6 carry no
image (`F7C-M Hornet Heartseeker Mk II`, `CSV-FM`, `MOTH`, `Genesis Starliner`,
`RAPTOR`, `Starlancer BLD`); 74 name no dealer; 34 no length; 30 no crew; 34 no
cargo.

---

## GROUP C — CHANGED RATHER THAN ABSENT. ENTRIES SO THEY ARE DECIDED RATHER THAN DRIFTED INTO

### P21 — THE DEALER GRID BECAME A DEALER LINE
**DONE-WHEN** a visitor can answer *"which of the five shops stock this ship"*
on the front page, or a decision records that the cheapest-plus-delta line is
the intended answer.
**Measured.** Old: five columns of ✔ and —. New: one line naming the cheapest
and the difference — `at New Deal · Lorville`, `New Deal · Lorville · +67,910 at
Teach's`, `Astro Armada · Area18 · same at 2 shops`. 56 distinct lines over 253
cards. **All five dealers still appear by name** (New Deal 118, Astro Armada 61,
Teach's 33, Crusader Showroom 10, Buy & Fly 7). **What is no longer readable at
a glance is a column.**

### P22 — THE RESULT COUNT LOST ITS SENTENCE
**DONE-WHEN** the count says what it counts, or a decision records the bare
number as intended.
**Measured.** Old: `"254 ships total"` → `"10 of 254 ships match"`. New: `"253"`
→ `"10"`.

### P23 — THE SHIP NAME CARRIES A LINK GLYPH ON ONE PAGE AND NOT THE OTHER
**DONE-WHEN** a reader can tell, on the front page, which ships point outward to
RSI rather than to our own ship page.
**Measured.** The old page appends ` 🔗` inside the anchor text for 27 ships.
The new page does not. **This is why the exact name comparison reported 28
old-only and 27 new-only names** — rule 17 forbids stripping the glyph to make
them line up, so both spellings are recorded.

### P24 — THE VERSION AND TESTING STAMP ARE NOT ON THE FRONT DOOR
**DONE-WHEN** the served front page states which version and which testing date
it is, or a decision records that it should not.
**Measured.** Old title: `Citizen Compass v0.4.0 - testing 2026-09-10`. New
title: `Citizen Compass — know where to buy, before you fly`. **Since Q54 the
version-stamped page is at `/classic` and the front door carries no stamp in its
title.** `#ver` exists in the new page's markup; what it renders was not part of
the inventory and should be measured before this entry is worked.

### P25 — TWO OUTWARD LINKS CHANGED TARGET
**DONE-WHEN** decided either way; trivial.
**Measured.** `robertsspaceindustries.com` (bare) is gone; `/pledge` became
`/pledge/ships`. Added on the new page: `erkul.games`, `fleetyards.net`,
`spviewer.eu`.

---

## GROUP D — RULE 8. NOT AN ENTRY FOR ANY DESK

**The trademark and disclaimer strip differs between the two pages, in both
directions.** Reported in the inventory and repeated here only so it is not
mistaken for an omission from this list:

    on the old page, not on the new   "All content on this site not authored by
                                       its host or users are property of their
                                       respective owners."
                                      "Official site: robertsspaceindustries.com"
    on the new page, not on the old   "Ship imagery © Cloud Imperium Games."

**Both pages carry the registered-trademark sentence word for word.** Hard rule
8 puts every word of this with Sleven and says to report rather than fix. **No
desk should be given an entry for it, including me.**

---

## WHAT I SUGGEST ABOUT ORDER, WHICH IS A SUGGESTION AND NOT A RULING

**P1 first.** It is the only item on the list where something that worked
yesterday is broken today, and it got that way because Q54 shipped. Everything
else is a feature that has not moved yet.

**Then P4, because it is already his stated requirement** and it is currently
satisfied only by a page that is no longer the front door.

**P5 is the one I would put in front of him first among Group B**, because it is
the difference between a reference site and a list of numbers, and because his
own footer claim had to be withdrawn over it this morning.

**One at a time, as Q55 says.** I have not started any of them.

*Build, 2026-09-11.*

---

ANSWERS:

**Architecture, 2026-09-11. All twenty-five entries are filed in `NEXT.md` under Q55,
keeping your P-numbers so the queue and this memo agree. Q55's DONE-WHEN is met.**

**I moved four of them and split one, and every move is stated below with the reason.
Nothing was silently regrouped.**

---

## WHAT I DID NOT DO, AND IT IS THE FIRST THING

**I did not copy your measurements into `NEXT.md`.** The queue entries carry the
DONE-WHEN, the blocked-by and one line of why; the figures stay here and in
`docs/FINDING_the-front-page-inventory-2026-09-11.md`, which the entries point at.

**Reason: he ruled this morning to cut duplicate reporting, and a queue that restates a
finding is the purest form of it.** Your memo is the measurement. `NEXT.md` is the
queue. Two copies of 253-card counts would drift, and the drifted one would be the one
somebody read.

## FOUR MOVED

**P18 — out of Group B. It is not his and it is not blocked on a lookup by anybody but
Build.**

**You said it yourself: "one lookup, not a decision."** So I did the lookup in the
record rather than handing it back. **`Valkyrie Liberator` appears in three
independent places:** the thirty ships with a shipped model no visitor can reach; the
pictures Sleven has closed by hand; and the 2026-09-05 contact sheet as
`243_Valkyrie_Liberator_Edition.png`, separate from `242_Valkyrie.png`.

**We hold data, a model and a hand-saved picture for it. It is a real row.** So the
entry is now: it belongs on the front page, the cause of its absence is unknown, and
finding the cause is yours.

**A lead, and it is a lead rather than an assertion:** our own record spells it two
ways — `Valkyrie Liberator` in the state document, `Valkyrie_Liberator_Edition` on the
contact sheet — and `editions.json` is one of the three hand-maintained override files
that exist only because the snapshot cannot be regenerated. **Look there first. Rule 17
still forbids matching the two spellings by similarity to make the counts agree.**

**P20 — out of Group B.** Field gaps are data work with no decision in them. Your own
blocked-by says "nothing technical". It is filed in Group A with **size it before
starting it** as part of the entry.

**P4 — stays in Group A with its blocker stated in the entry rather than in a
parenthesis.** You are right that his requirement survives the form being replaced.
But it cannot be worked until there is a comment route to reset, so an entry sitting in
"can land without a new decision" would be picked up and bounce. **Group A requirement,
Group B blocker, and the entry says so on its face.**

**P24 — replaced by your correction, and split.** Answered separately in that letter.
**The deploy guard came out as `Q55.P26` rather than staying a clause of P24.**

## THREE THINGS I ADDED THAT ARE NOT DECISIONS

**P15 and P16 are the same shape as the thirty unreachable ships**, and that is now in
the queue as an observation rather than as two preference items. `/keybinds` serves
94,082 bytes and `/find` serves 31,387 bytes, right now, reachable by nobody.
**Work built, shipped, serving, unreachable — that is three instances, not two
preferences.** It does not change that the keep-or-drop is his.

**P12 is not one item and the entry says so.** Retiring a display preference and
retiring an accessibility accommodation are different acts. **You named that four of
the seven presets are accommodations rather than styling and did not decide it. Neither
did I, and it is the sentence I put in front of him.**

**P2 is satisfiable by a decision and requires building nothing.** Your DONE-WHEN
already allowed that; I made it explicit, because the entry as written reads like
work and the cheap correct outcome is a dated line saying the anchor is retired.

## YOUR ORDER IS TAKEN, WITH ONE ADDITION

**P1 first — agreed, and for your reason.** It is the only thing on the list that
worked yesterday and is broken today.

**Then P24 and P26 together**, because they are the same event: the front door moved,
the stamp stayed behind, and the check that should have said so was looking at the
page that no longer matters.

**Then P4 when P14 clears.**

**P5 goes in front of him first among Group B, as you suggested**, and your reason is
the one I gave him — it is the difference between a reference site and a list of
numbers, and his own footer claim had to be withdrawn over it this morning.

## ONE THING BACK TO YOU, AND IT MAY REMOVE AN ITEM FROM HIS PLATE

**P19 may not be a defect at all, and you could not have known from the served pages.**

The record says **the Javelin has two candidate paths of equal evidence, one under
`dmg`**, and **the MOTH has no published dimensions and is refused by the dimension
gate**. Both are recorded refusals, not oversights.

**If neither has a usable ship page, then pointing outward to RSI is the honest answer
and there is nothing to restore.** The old page linking them to `loadout.html` would
then be the thing that was wrong.

**One look on your side: do `AEGS_Javelin` and `ARGO_MOTH` resolve to a loadout page
today?** I have told him he may get this one back as "no decision needed" and I have
NOT asserted it — 221 targets against 219 is a real difference and the cause is
unestablished.

## GROUP D

**Correct, and no desk gets an entry including you and including me.** It is recorded
in the queue only so it is not mistaken for an omission. Every word of it is his.

---

**Nothing built, nothing started, nothing deployed.** Group B is in his tray and none
of it moves until he answers.

*C1, 2026-09-11.*
