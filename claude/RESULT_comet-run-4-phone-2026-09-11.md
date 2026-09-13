# RESULT — Comet run 4 of 5: the test site, phone width

**Run 2026-09-11 evening CDT by Sleven in a new Comet "Computer" conversation, prompt
`claude/PROMPT_comet-run-4-phone-2026-09-11.md`. Assessed by the Adjutant desk against the
deployed files in `testing/_deploy/` as they stood after the latest rebuild.**

## ASSESSMENT

**Clean run, followed the rules.** 14 CONFIRMED, 0 UNVERIFIED, 2 OPINION. It set the width
by device emulation (390 × 844) and kept checking that the width held. It stopped at the
password gate and asked. It measured tap targets, contrast and scroll widths instead of
eyeballing them, and it ran a real keyboard test.

One small inconsistency, not material: it reports a 390 px viewport but a 375 px page
client width on /next. The 15 px gap is most likely a scrollbar in the emulated view.

**One item closed by this run.** The testing stamp is now visible at phone width
("testing 2026-09-11 …", read without scrolling). The phone-hides-the-stamp defect sent to
Code at 14:08 is fixed as far as a visitor sees.

## CHECKED AGAINST THE DEPLOYED FILES BY THE ADJUTANT DESK

- **M-014 holds, and the fix is already written but switched off.** `next.html` carries a
  full glossary with "aUEC" = "Alpha United Earth Credit" and "SCU" = "Standard Cargo Unit",
  plus the tooltip code that shows it on tap, hover or keyboard focus. That code is never
  called on the front page, so no definition ever appears. The ship page calls it only for
  part names.
- **M-005 holds.** Neither "New Deal" nor "Lorville" appears anywhere in `loadout.html` or its
  data file `loadout_data.gen.js`. The ship page has no way to say where the Cutlass Black
  is sold.
- **M-008 holds in code.** On the ship page, "← All ships" is rewritten to plain `next.html`
  with no search, filter or position. Same defect as T-004 / Q55.P3, now also seen on a phone.
- **M-011 recomputed.** Stamp colour #4a5c6d on #06090d = 2.89:1, as Comet measured.
- **M-007:** the ship dropdown `<select id="ship">` has no width rule in the page's styles
  that the desk could find. The 425 px measurement itself was not re-measured.

## DUPLICATES OF EARLIER FINDINGS

- M-004 (Cutlass Black $110 vs $105.00) = run 3 T-009, already routed.
- M-008 = T-004 / Q55.P3.
- M-011 is the phone view of T-015/T-016 (low contrast).

## ROUTED

To Architecture:
`memo_architecture_comet-run-4-found-the-glossary-is-built-and-never-switched-on.md`.

---

## COMET'S REPLY, VERBATIM AS SLEVEN CARRIED IT IN

Only one site was open throughout: citizencompasstesting.citizencompass-contact.workers.dev. No other tabs appeared, no web search was used, and I saw no on-page text addressed to me as an agent. The site did ask for a password, and I stopped and asked you before entering the one you gave me.
Width
390 pixels wide (390×844), set with the browser's device-emulation override (the same mechanism as a phone view in page-inspection tools). It stayed at 390 for the entire session — I checked it repeatedly and it never drifted.
Step 1 — First impression (top of /next, no scrolling)
a. My first guess: a database/tracker for Star Citizen ships — it shows six stat tiles ("253 SHIPS TRACKED," "237 WITH A PLEDGE PRICE," "179 BUYABLE IN GAME," "18 MANUFACTURERS," "5 SHIP DEALERS," "28 JOBS COVERED"), a live status strip, tabs, a search box, filter chips, and the start of a ship list.
b. First three things my eye went to: the "Citizen Compass" title (white + cyan), the big bold numbers in the stat tiles, and the green "IN GAME" badge on the first ship card's thumbnail.
c. What's confusing: the status strip packs several jargon terms together with no explanation ("Live 4.10.0 'Siege of Orison'," "PTU —," "aUEC," "SCU") and the filter-chip row visibly cuts off mid-word ("Ex...") at the right edge with no arrow or fade to signal there's more to scroll to.
Screenshot taken and reviewed.
Step 2 — Match to stated purpose
Fairly well for the shopping/price part — the price, shop, and "in game vs. pledge-only" status are front and center on every card. It matched less well for the "judge how trustworthy" part: the trust-and-sourcing tab ("Legend & Sources") isn't visible on the first screen at all, so a first-time visitor wouldn't discover the credibility framing unless they happened to scroll a horizontally-clipped tab row.
Step 3 — Five tasks

1. Search "Cutlass Black": Succeeded. 1 tap (into the search box) + typing the name; results filtered live, no submit needed, no scrolling required.
2. Find where it's bought and the price: Succeeded, for free — the same search-result card already showed "IN GAME," "2,010,960 aUEC," "$110," "at New Deal · Lorville." 0 extra taps.
3. Open the ship's details page, find the same info: Partially succeeded. 1 tap opened a page titled "Loadout Bench." It showed "IN-GAME PRICE 2,010,960 aUEC" and "PLEDGE PRICE $105.00" — but the pledge price disagrees with the $110 shown on the list, and the shop name/city ("New Deal · Lorville") is not shown anywhere on this page at all. Got stuck on: the missing shop info and the price mismatch.
4. Get back to the list — same place? No. Tapping "← All ships" (1 tap) lands at the very top of the full, unfiltered 253-ship list with the search box empty — the "Cutlass Black" search and scroll position are gone.
5. Find the website's version, finished or test: Found a status line reading "testing 2026-09-11 · Live 4.10.0 'Siege of Orison' · PTU — · Ship data compiled 2026-07-30," visible without scrolling. There's no separate version number for the website software itself, only this "testing" date-stamp, the "testing" subdomain name, and the "Private preview" password gate — all pointing to this being a test build, not a finished release.

Step 4 — Phone-width page checks

* /next: No page-level sideways scroll (measured: page scroll-width 375px = client-width 375px). But two inner rows scroll sideways with no visible cue: the filter-chip row (scroll-width 1155px vs. visible 331px) and the section-tab row (scroll-width 464px vs. visible 331px) — the "Legend & Sources" tab and a currency selector are both hidden off-screen until scrolled.
* Cutlass Black ship page (loadout page): The whole page scrolls sideways — measured page scroll-width 437px vs. viewport 390px, caused by a ship-variant dropdown measuring 425px wide. Scrolling right cuts labels off on the left ("MANUFACTURER" becomes "FACTURER").
* Tabs/menus reachable: All four tabs (Ships, Development Progress, Sale Calendar, Legend & Sources) opened correctly once reached.
* Readable without zooming: Mostly yes; smallest measured text was the "aUEC" unit label at about 9.5px.
* Tap targets (measured in pixels): CONFIRMED — section tabs ≈ 31px tall, filter chips ≈ 30px tall, ship-page Day/Night/Blackout toggle ≈ 27px tall, "Try another alongside"/"Copy share link" ≈ 35px tall. All below the common 44px minimum. The search box (48px) and each full ship card (331×152px) are comfortably large.

Step 5 — Findings
ID: M-001
PAGE: https://citizencompasstesting.citizencompass-contact.workers.dev/next
WIDTH: 390px
CATEGORY: phone layout
LABEL: CONFIRMED
SEVERITY: slows down
EVIDENCE: The filter-chip row's scrollable width measures 1155px against a visible width of 331px. In the initial view the last visible chip is cut off reading "Ex" (full label "Exploration"), with no arrow, fade, or label indicating more chips exist.
ID: M-002
PAGE: https://citizencompasstesting.citizencompass-contact.workers.dev/next
WIDTH: 390px
CATEGORY: navigation
LABEL: CONFIRMED
SEVERITY: slows down
EVIDENCE: A currency selector (options USD/EUR/GBP/CAD/AUD/JPY) sits at the end of that same chip row. At the default scroll position it measures left=1108px, right=1177px — entirely outside the 390px viewport. Scrolling the chip row to its far right end (824px of scroll) brings it into view; nothing on screen signals it is there before that.
ID: M-003
PAGE: https://citizencompasstesting.citizencompass-contact.workers.dev/next
WIDTH: 390px
CATEGORY: navigation
LABEL: CONFIRMED
SEVERITY: slows down
EVIDENCE: The section-tab row (Ships / Development Progress / Sale Calendar / Legend & Sources) has a scrollable width of 464px against a visible width of 331px. "Legend & Sources" — the tab explaining sourcing and trust — starts at left=353px, right=486px, so only ~37px of it is inside the 390px viewport and the rest is clipped by the row's own scroll container.
ID: M-004
PAGE: https://citizencompasstesting.citizencompass-contact.workers.dev/next vs. .../loadout?from=next#DRAK_Cutlass_Black
WIDTH: 390px
CATEGORY: ship page
LABEL: CONFIRMED
SEVERITY: slows down
EVIDENCE: List page text (quoted): "Cutlass Black IN GAME Fighter 37.5 m crew 3 46 SCU 2,010,960aUEC $110 at New Deal · Lorville." Ship detail page text (quoted): "PLEDGE PRICE $105.00." Same ship, same visit, two different pledge prices ($110 vs. $105.00).
ID: M-005
PAGE: https://citizencompasstesting.citizencompass-contact.workers.dev/loadout?from=next#DRAK_Cutlass_Black
WIDTH: 390px
CATEGORY: missing information
LABEL: CONFIRMED
SEVERITY: slows down
EVIDENCE: Searched the full extracted text of this page for "New Deal" and "Lorville" — neither string appears anywhere, even though the list page shows this ship is sold "at New Deal · Lorville."
ID: M-006
PAGE: https://citizencompasstesting.citizencompass-contact.workers.dev/loadout?from=next#DRAK_Cutlass_Black
WIDTH: 390px
CATEGORY: phone layout
LABEL: CONFIRMED
SEVERITY: cosmetic
EVIDENCE: The page heading element's full text is "Drake Cutlass Black (Cutlass Black)" but its box measures scrollWidth 341px against a clientWidth of only 164px, and on screen it renders as "Drake Cutlass …" (screenshot taken).
ID: M-007
PAGE: https://citizencompasstesting.citizencompass-contact.workers.dev/loadout?from=next#DRAK_Cutlass_Black
WIDTH: 390px
CATEGORY: phone layout
LABEL: CONFIRMED
SEVERITY: slows down
EVIDENCE: Whole-document scrollWidth measured 437px against a 390px viewport. The ship-variant dropdown element measures 425px wide (left=12px, right=437px), causing the page to scroll sideways. Manually scrolling right by 62px shifts all left-hand labels off-screen (screenshot shows "MANUFACTURER" cut to "FACTURER," "IN-GAME PRICE" cut to "ME PRICE").
ID: M-008
PAGE: https://citizencompasstesting.citizencompass-contact.workers.dev/next
WIDTH: 390px
CATEGORY: navigation
LABEL: CONFIRMED
SEVERITY: slows down
EVIDENCE: Steps: search "Cutlass Black" → open its card → tap "← All ships." Result: search box value is empty (`''`), page URL is back to plain `/next`, and scroll position is 0 — the full 253-ship list from the top, not the filtered "Cutlass Black" result.
ID: M-009
PAGE: https://citizencompasstesting.citizencompass-contact.workers.dev/next
WIDTH: 390px
CATEGORY: accessibility
LABEL: CONFIRMED
SEVERITY: slows down
EVIDENCE: Measured with page inspection tools: section tabs (e.g. "Ships") ≈ 59×31px; filter chips (e.g. "Buyable in game") ≈ 121×30px. Both below the commonly cited 44×44px minimum touch-target size.
ID: M-010
PAGE: https://citizencompasstesting.citizencompass-contact.workers.dev/loadout?from=next#DRAK_Cutlass_Black
WIDTH: 390px
CATEGORY: accessibility
LABEL: CONFIRMED
SEVERITY: slows down
EVIDENCE: Measured: "Day" toggle 44×27px, "Night" 51×27px, "Blackout" 71×27px, "Try another alongside" 156×35px, "Copy share link" 120×35px — all shorter than 44px tall.
ID: M-011
PAGE: https://citizencompasstesting.citizencompass-contact.workers.dev/next
WIDTH: 390px
CATEGORY: accessibility
LABEL: CONFIRMED
SEVERITY: cosmetic
EVIDENCE: Computed style of the text "testing 2026-09-11": color rgb(74,92,109) at 11px, on an effective background of rgb(6,9,13). Calculated contrast ratio 2.89:1, below the WCAG minimum of 4.5:1 for normal text.
ID: M-012
PAGE: https://citizencompasstesting.citizencompass-contact.workers.dev/next
WIDTH: 390px
CATEGORY: accessibility
LABEL: CONFIRMED
SEVERITY: cosmetic
EVIDENCE: The "aUEC" unit label renders at 9.5px font size with a computed contrast ratio of 4.34:1 against its background, both below common minimum guidance (WCAG 4.5:1 for text this size).
ID: M-013
PAGE: https://citizencompasstesting.citizencompass-contact.workers.dev/next
WIDTH: 390px
CATEGORY: accessibility
LABEL: CONFIRMED
SEVERITY: slows down
EVIDENCE: Actual keyboard test: on load, focus starts in the search box. Pressing Tab moves to "Buyable in game," then "Combat," "Transporter," etc. — the section tabs (Ships/Development Progress/Sale Calendar/Legend & Sources) are not reached this way; they only appear by pressing Shift+Tab. Forward-Tab order would require cycling through all filter chips, the currency selector, and all 253 ship-card links before wrapping back to them.
ID: M-014
PAGE: https://citizencompasstesting.citizencompass-contact.workers.dev/next (all tabs)
WIDTH: 390px
CATEGORY: missing information
LABEL: CONFIRMED
SEVERITY: slows down
EVIDENCE: Searched the extracted text of all four tabs (Ships, Development Progress, Sale Calendar, Legend & Sources) for "Standard Cargo" and "stands for" — no match. "SCU" and "aUEC" appear on every single ship card but are never spelled out anywhere on the site.
ID: M-015
PAGE: https://citizencompasstesting.citizencompass-contact.workers.dev/next
WIDTH: 390px
CATEGORY: first impression
LABEL: OPINION
SEVERITY: cosmetic
EVIDENCE: A first-time visitor unfamiliar with Star Citizen, seeing "Live 4.10.0 'Siege of Orison,' PTU —, aUEC, SCU" all in the first screenful with no definitions in sight, would likely be unsure what several of these mean before scrolling further — a judgment based on typical unfamiliarity with genre jargon, not a measurement.
ID: M-016
PAGE: https://citizencompasstesting.citizencompass-contact.workers.dev/loadout?from=next#DRAK_Cutlass_Black
WIDTH: 390px
CATEGORY: phone layout
LABEL: OPINION
SEVERITY: cosmetic
EVIDENCE: The weapons/loadout list sits in its own visibly-scrollbarred box nested inside the page (seen in screenshot). On a touchscreen a first-time visitor's swipe near that box would likely scroll the small inner list instead of the outer page — a judgment based on common nested-scroll behavior, not confirmed by an actual finger-swipe test.
Summary

1. Counts: 14 CONFIRMED, 0 UNVERIFIED, 2 OPINION.
2. Fix first: M-008 (list state lost on "back," breaks the basic search→browse→return loop), M-004 (price disagreeing between list and detail page undermines the site's core trust promise), M-005 (shop location missing on the detail page, the single most important fact for "where to buy").
3. External links (none opened):
   * [View Drake Cutlass Black on RSI](https://robertsspaceindustries.com/en/pledge/ships/drake-cutlass/Cutlass-Black) and 29 more links to robertsspaceindustries.com pledge-ship pages for concept/pledge-only ships — 30 total; examples: [Javelin](https://robertsspaceindustries.com/en/pledge/ships/aegis-javelin/Javelin), [Nautilus](https://robertsspaceindustries.com/en/pledge/ships/aegis-nautilus/Nautilus), [Vulcan](https://robertsspaceindustries.com/en/pledge/ships/vulcan/Vulcan)
   * [starcitizen.tools — ship and purchasing data](https://starcitizen.tools/)
   * [CStone — live in-game dealer verification](https://finder.cstone.space/)
   * [UEX Corp — price cross-check](https://uexcorp.space/)
   * [Erkul — loadouts and DPS](https://www.erkul.games/)
   * [Fleetyards — fleet tracking and images](https://fleetyards.net/)
   * [SPViewer — ship stat comparison](https://www.spviewer.eu/)
   * [citizencompass.contact@gmail.com](mailto:citizencompass.contact@gmail.com) (mail link, not a website)
