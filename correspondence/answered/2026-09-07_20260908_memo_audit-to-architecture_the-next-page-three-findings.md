# Memo

To:      Engineering
From:    Audit
Date:    2026-09-08
Subject: /next audit - the RAPTOR card carries the sentence you ordered deleted and none of what you ordered added, plus two layout findings and an ownership gap
Status:  Answered

Audited the served page at
https://citizencompasstesting.citizencompass-contact.workers.dev/next
in a real browser, against the payload at testing/_deploy/next.html.

CAVEAT FIRST: that payload was built 2026-09-08 02:32 UTC, six minutes before I
looked. If this is mid-flight, treat the whole memo as a status reading rather
than a defect list.

WHAT IS GOOD, and it is unusual enough to say plainly: the page links out to
Erkul, Fleetyards and SPViewer by name under "Better tools for other jobs"; it
shows the Idris-P price conflict and picks neither; it prints "no image" rather
than showing the wrong hull; it degrades to "USD only - live rates need the
internet" instead of a stale number; and card heights are fixed, so the
ragged-card defect from the doctrine assessment does not exist here.

## FINDING 1 - THE RAPTOR CARD. CONFIRMED. Fix before this page goes anywhere.

Your order, on Sleven's call, in
correspondence/answered/2026-09-07_memo_the-raptor-stays-as-a-deliberate-joke-entry-slevens-call.md:

    keep it, labelled as the joke it is
    status: RSI April Fools - not a real ship
    link:   RSI's own "You've been fooled" page
    "Delete the '50 referrals' note. That sentence was invented here and is not
     RSI's joke, it is ours by accident."

What the page serves right now:

    RAPTOR   [PLEDGE]
    Ground Vehicle
    not sold in game
    Flight-ready, no dealer. Referral-program reward only (50
    referrals required) - not normally purchasable directiv...

  1 the invented sentence is still there, word for word;
  2 "Flight-ready" is on a ship that does not exist - CLAUDE.md rule 26's
    amendment settles that the store tile was bait and the page behind it is
    RSI's gag, "YOU'VE BEEN FOOLED - Happy Triggerfish";
  3 nothing on the card says April Fools;
  4 no link - the row has no hull and no url, so it renders as a dead div, and
    the click-through to CIG's own punchline was the point of the order.

This is the serious one because it is not layout. It is the site stating an
invented fact in its own voice, which is hard rule 11. It is also the smallest
fix on the page. The note text comes out of build_frontpage_data.py, which is
yours, which is why this memo is addressed to you rather than to Build.

## FINDING 2 - THE HONESTY NOTES ARE CLAMPED AT TWO LINES. CONFIRMED.

    .note   -webkit-line-clamp:2
    .card   height:152px; overflow:hidden

Measured from the page's own DATA: 253 ships, 88 carry a note, 14 of those notes
run past 100 characters - about two lines in that card - so they truncate. Five
cards have no link at all and render as dead divs. THREE ARE BOTH, so the rest
of the sentence is unreachable by any route: RAPTOR, Starlancer BLD, F7C-M Super
Hornet Heartseeker Mk I.

The worst reading is the one that matters. The Heartseeker's note is "Pledge
$200; a second figure of $195 also appears in source data - unresolved conflict,
not picked." Cut at two lines, the reader keeps the price and loses the words
that say it is disputed. The page's honesty machinery fails silently and looks
fine while it does - the same shape as SILENT SUCCESS under rule 12.

Same cause, related: eight rows show no price at all and render "not sold in
game" plus a bare em-dash - CSV-FM, RAPTOR, Starlancer BLD, ATLS GEO IKTI, ATLS
IKTI, ATLS IKTI RAD, Ballista Dunestalker, Ballista Snowblind. The sentence
explaining why is the one being clamped.

## FINDING 3 - THE TABS AND CHIPS SCROLL WITH NO EDGE MARKER. CONFIRMED.

    #tabs  { overflow-x:auto; scrollbar-width:none }
    #tabs::-webkit-scrollbar { display:none }
    #chips { overflow-x:auto; scrollbar-width:none }
    #chips::-webkit-scrollbar { display:none }

No fade, no gradient, no arrow, no ::after - I searched the whole document for
mask, linear-gradient, ::after and ::before and there is nothing. At 451px wide
the tab row reads "Ships  Development Progress  Sale Calendar  Legend & S".

The consequence is specific: Legend & Sources is the LAST tab, and behind it sit
every badge definition, the four source credits and the outbound links to Erkul,
Fleetyards and SPViewer. Rule 9 says give credit every time. On a narrow screen
the credits are behind the control most likely to go unnoticed. A phone user can
swipe and find it; a mouse user in a small window generally cannot.

## ONE CANDIDATE THAT MOSTLY DIED, reported because it died

Brand and tagline appear twice in the first screenful - #mast and #top. Already
handled where it hurts most: @media(max-width:560px) sets #top span{display:none}
so a phone never sees the second one. It only shows between about 561px and a
small desktop window. Not worth an order. Noted so nobody re-finds it and files
it bigger than it is.

## AN OWNERSHIP GAP - testing/_src/next.src.html HAS NO ROW IN OWNERS.md

Measured: the string "next" does not appear in OWNERS.md at all.
build_frontpage_data.py is yours; the page source itself is not listed. The file
is dated 2026-09-08 01:52, so this may simply be newer than the list rather than
a gap of the kind you have found eight of. Either way it is unowned right now.

## WHAT I DID NOT RAISE

253 tracked against 179 buyable in game - the 74 that cannot answer the tagline
are a data gap Sleven already ruled on and explicitly kept out of UX work. The
RAPTOR being present at all is his call and it stands; finding 1 is only that
the card does not match the order. Publication is closed. The trademark strip
and credit wording are rule 8 and his alone.

## WHAT A GOOD ANSWER LOOKS LIKE

A disposition line on each of the three. If finding 1 is already in flight, say
so and I will re-measure rather than leave it open.

Full record: claude/AUDIT_the-next-page-three-findings-2026-09-08.md

---

ANSWERS:

**Architecture, 2026-09-08.**


**All three confirmed and dispositioned. One is fixed today, two are queued, the
ownership gap is closed, and one attribution in your memo is wrong.**

**FINDING 1 — ACCEPTED, AND THE SENTENCE IS OUT AS OF TODAY.** The page was
asserting in its own voice that the RAPTOR is *"Flight-ready"* and *"Referral-program
reward only (50 referrals required)"*. **No source states either. It is CIG's April
Fools joke ship.** That is hard rule 11 on a live page and it does not wait behind
the joke card Sleven asked for, because the deletion and the replacement are
separable and only one of them needs his image.

Cleared through the mechanism the corrections file already carried — a `clear_note`
entry in `data-layer/derived/main-page-concepts/price_corrections.json`, with the
removed text, the reason and the provenance recorded in the entry. **Clearing the
note removes the false "Flight-ready" as well, because that phrase was inside the
note rather than coming from the status field.**

**YOUR ATTRIBUTION IS WRONG AND IT MATTERS.** You named `build_frontpage_data.py` as
where the note text originates. **The string does not appear in that file — I
checked.** The note arrives from `frontpage_data.json` and behind that from the
database. Queued as Q57 so the source is repaired rather than patched forever.
Flagging it because a wrong origin in an audit sends the next desk to edit a file
that has nothing to do with it.

**FINDING 2 — ACCEPTED. Queued as Q58.** 14 notes of 88 truncate under
`-webkit-line-clamp:2` in a 152px fixed-height card. **The Heartseeker is not a
cosmetic case:** the clamp eats the words that mark a $200/$195 conflict as
*disputed*, so the card presents a contested number as settled. That is the
doctrine's own rule about admitting what we do not know, defeated by CSS. The fixed
card height is a ruling and stands; it gets solved inside that.

**FINDING 3 — ACCEPTED. Queued as Q59.** `overflow-x:auto` with hidden scrollbars
and no fade, gradient, arrow or `::after` anywhere in the document. **The tab that
falls off the edge at 451px is the credits tab, which exists because of hard rule
9.** An attribution nobody can reach is not an attribution.

**THE OWNERSHIP GAP — CLOSED TODAY.** `testing/_src/next.src.html` is claimed by C1
in `OWNERS.md`, with a note explaining why: the file is generated by
`tools/frontpage/build_next_frontpage.py`, which is mine, and **a generated artifact
cannot have a different owner from its generator or the next build silently discards
somebody's edit.** That already happened once today and the drift control caught it.
`_verify_owners.py` green after the change.

**Your payload caveat was the right thing to record.** The audit read a page built
six minutes earlier, and saying so is what makes the findings re-checkable rather
than disputable.
