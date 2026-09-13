# RESULT — Comet run 5 of 5: the two sites side by side

**Run 2026-09-11 night CDT by Sleven in a new Comet "Computer" conversation, prompt
`claude/PROMPT_comet-run-5-comparison-2026-09-11.md`. Site A = the test site's new front
page; Site B = the public site. Assessed by the Adjutant desk. This closes the five-run
review.**

**Redaction.** Comet wrote the test-site password into its reply in plain text. It is
replaced below with [PASSWORD REDACTED BY THE ADJUTANT DESK]. The project rule is that the
password is never written into any file. Comet's code-block fences around each finding are
also removed; nothing else is changed.

## ASSESSMENT

**Usable, rules followed, 19 CONFIRMED / 0 UNVERIFIED / 3 OPINION.** Its "not found" claims
say where it looked and what it searched for, as the prompt required.

**The headline is right, with a correction Comet could not make.** Comet judged that a
first-time visitor would trust Site B more, because B puts one price and a "Confirmed —
starcitizen.tools 4.9.0" tag in the same row, while A shows two prices and hides its caveats.
That judgement is fair on what is on screen. But B's clearer trust signal is partly false:

- B's "Confirmed … 4.9.0" and its "LIVE 4.9.0" banner name a patch the game left in late
  August. A's "Live 4.10.0" is the correct one.
- Run 2 (P-004) showed B calling the Idris-P "confirmed" while its own Legend says that price
  is in unresolved conflict.

So the lesson is to carry over **where** B puts trust (next to the price, zero clicks),
**not what B claims**. That is the per-row confidence note already at the top of the Q53
inventory, and it has to be true.

**Independent confirmation of run 3.** C-003 and C-021 re-find T-008 without being told it:
the "PATCH 4.10" badge reads as price verification when it only covers components.

## CHECKED AGAINST THE DEPLOYED FRONT PAGE BY THE ADJUTANT DESK

From `testing/_deploy/next.html`, rebuilt 2026-09-11:
- **C-013 holds.** "General 2026 outlook" and "Known non-purchasable ships" do not appear, nor
  "Bengal". "Vanduul" appears only inside one ship's note.
- **C-015 holds.** No "Patch Notes" link.
- **C-018 holds.** The front page has no link to `find.html`.
- The password does not appear in the page file.

Not re-checked: C-002 (253 vs 254 ships), C-014 (dealer checkmark columns), C-016, C-017.

## WHAT IS NEW, AGAINST RUNS 1–4

Things the public site has that the new front page lacks (the regression list):
C-013 the two Development Progress paragraphs; C-014 every dealer per ship at a glance;
C-015 a patch-notes link; C-016 an RSI link on every ship in the list; C-017 finer
categories (19 against 12, and see T-003); C-002 one ship fewer (253 against 254),
unexplained.

Already routed: C-001 = T-009 / M-004; C-005/C-006 = T-005 (feedback, ruled); C-003/C-021 =
T-008; C-018/C-020 = T-002 (no link to /find).

## ROUTED

To Architecture:
`memo_architecture_comet-run-5-found-what-the-public-site-has-that-the-new-page-lacks.md`.

---

## COMET'S REPLY, AS SLEVEN CARRIED IT IN (PASSWORD REDACTED)

I finished the full audit across both sites. Here is the complete report.

## Step 1 — Five Tasks On Each Site

**Site A** (password-gated, entered "[PASSWORD REDACTED BY THE ADJUTANT DESK]"):

| Task | Result | Steps | Where I got stuck |
|---|---|---|---|
| 1. Find Cutlass Black | Done | 2 (click search box, type name) | — |
| 2. Price + where bought | Done | 2 (same view as above) | Card shows "$110" and "2,010,960 aUEC" at "New Deal · Lorville" |
| 3. Verify price + patch | Only partly | 5–6 (open ship → "Where to buy" tab → expand 2 disclosures) | The only patch-specific note ("PATCH 4.10") turns out to be about loadout/component data, not the price. The actual price caveat is a separate, easy-to-miss footer line |
| 4. Report a problem | Not really | Checked all 4 nav tabs | Only found a takedown email scoped to Cloud Imperium Games, not general feedback |
| 5. Credits/ownership | Done | 0 clicks, scroll to footer | No separate contributor-credits list, only a copyright notice |

**Site B** (no password):

| Task | Result | Steps | Where I got stuck |
|---|---|---|---|
| 1. Find Cutlass Black | Done | 2 (click search box, type name) | — |
| 2. Price + where bought | Done | 2 (same view) | Same row shows "$105.00" and a ✓ under "New Deal (Lorville)" |
| 3. Verify price + patch | Done | 2 (same view, zero extra clicks) | Same row's Confidence/Notes column: "Confirmed — starcitizen.tools 4.9.0" |
| 4. Report a problem | Not possible | Read the entire page | No trace of "contact," "report," "feedback," "email," or "credit" anywhere on the page |
| 5. Credits/ownership | Done | 0 clicks, scroll to footer | Same pattern as A — ownership notice, no contributor list |

**Which site made it easier, per task:** Task 1 — same. Task 2 — same. Task 3 — Site B, clearly (0 extra steps vs. 5–6, and one clean sentence vs. two disclosures that need careful reading to avoid confusing component-verification with price-verification). Task 4 — same (neither works, though A at least surfaces an email). Task 5 — same.

## Step 2 — What One Site Has That The Other Doesn't

**a. Useful things on Site B not found on Site A** (this is the important list):
- A Confidence/Notes column built into the main ship table, giving a plain-language check plus a specific source and patch number for every ship with zero extra clicks (e.g., "Confirmed — starcitizen.tools 4.9.0" for Cutlass Black).
- A table with a ✓/— checkmark column for each of the 5 dealers, so a visitor can see every stocking location for any ship at a glance, instead of visiting each ship individually.
- A clickable "● LIVE 4.9.0 ◆ PTU 4.10.0 Patch Notes ↗" banner linking straight to the official patch notes. Site A only shows plain, unlinked patch text.
- Every ship name links directly to its official RSI pledge page right from the main table (confirmed via the row's HTML: `href="https://robertsspaceindustries.com/en/pledge/ships/drake-cutlass/Cutlass-Black"`). On Site A you must open the internal ship page first before an RSI link appears.
- Two extra paragraphs on the Development Progress section not present on Site A: "General 2026 outlook" (mentions multiple manufacturers with ships "re-entering development" for 2026) and "Known non-purchasable ships" (explains the RSI Bengal, RSI Pegasus, and Vanduul alien ships are lore/NPC-only and not something a player is missing).
- A more granular, 19-item searchable category list (Bomber, Capital/Multi-crew, Data, Interdiction, Medical, Minelayer, Racing, Refuel, Salvage, Search & Rescue, Support/Repair, Touring/Luxury, etc.) versus Site A's 12 broader filter buttons.

**b. Useful things on Site A not found on Site B:**
- Full in-site ship detail pages (Loadout, Engineering, Liveries, Where to buy, Specs tabs) including — per Site A's own footer note — "the 3D model, its hardpoints in CIG's own positions, and the full loadout." Site B only ever links out to RSI.
- A homepage stats dashboard: "253 SHIPS TRACKED / 237 WITH A PLEDGE PRICE / 179 BUYABLE IN GAME / 18 MANUFACTURERS / 5 SHIP DEALERS / 28 JOBS COVERED." Site B shows only a single line, "254 ships total."
- A hidden item/commodity price tool (reachable only via a disclosure link on a ship's "Where to buy" tab, not from the main nav) offering "26,657 price rows... 7,932 items across 823 terminals and 100 categories," plus a downloadable, hash-verifiable data file for self-checking.
- Detailed methodology disclosures explaining exactly how — and how much — the price and component data are (and aren't) linked, including supporting stats ("318 ships, 3292 components...").
- A "BETTER TOOLS FOR OTHER JOBS" section recommending Erkul, Fleetyards, and SPViewer for other tasks.
- A "no image" legend entry explaining that ships without a picture are shown as a gap rather than a wrong hull.
- A contact email, even though scoped narrowly to Cloud Imperium takedown requests — Site B has no contact information anywhere.

**c. Disagreements for the same ship:**
- Cutlass Black pledge price: Site A's own list-card shows "$110"; Site A's own detail page for the identical ship shows "PLEDGE PRICE $105.00"; Site B shows "$105.00". So Site A disagrees with itself, and Site B's number matches Site A's detail page but not what a visitor sees first on Site A's list.
- Ship count: Site A states "253" (homepage tile and "v0.4.0 · 253 ships"); Site B states "254 ships total."
- Patch used for verification: Site B's tag reads "Confirmed — starcitizen.tools 4.9.0" for the price. Site A's only patch-specific note on this ship, in the "Where to buy" tab's "PATCH 4.10" disclosure, reads "Component names, manufacturers, sizes and stats are read from Star Citizen's own game files — scunpacked snapshot 20260827T225641Z, last verified against patch 4.10" — which covers loadout components, not the price. Site A's actual price caveat is the separate sitewide line: "aUEC prices are community-reported and dated — not verified in game."

## Step 3 — Trust Information For Cutlass Black

**Site A:** I had to scroll to the bottom of any tab to find the sitewide disclaimer: "aUEC prices are community-reported and dated — not verified in game. Verification is incomplete: most ships on this page do not yet show the patch they were checked against." To find anything ship-specific, I had to search "Cutlass Black" → click the ship → click "Where to buy" → expand two collapsed panels, which read "NO PRICE JOIN — shop data is real, the link to these parts is not proven... Two real datasets with no proven join is a different thing from having no prices" and "PATCH 4.10 — from Star Citizen's game files · scunpacked 20260827T225641Z... last verified against patch 4.10" — the latter is about components, not the price.

**Site B:** In the very same search-result row (0 extra clicks), the Confidence/Notes column reads: "Confirmed — starcitizen.tools 4.9.0." No further explanation of what "Confirmed" means or how it was checked appears anywhere (I checked the row's underlying markup for a tooltip or expandable note — none exists).

## Step 4 — Other Findings

## Findings

ID: C-001
SITE: BOTH
PAGE: Site A Ships tab (card) + Site A ship detail page + Site B Ship Purchase Matrix row
CATEGORY: disagreement
LABEL: CONFIRMED
SEVERITY: slows it down
EVIDENCE: Steps: search "Cutlass Black" on Site A → card shows "$110" beside "2,010,960aUEC" and "at New Deal · Lorville" → click the card → detail page stat box reads "PLEDGE PRICE $105.00". On Site B, search "Cutlass Black" → row shows "$105.00" in the Pledge Price column.

ID: C-002
SITE: BOTH
PAGE: Site A homepage + Site B Ship Purchase Matrix
CATEGORY: disagreement
LABEL: CONFIRMED
SEVERITY: cosmetic
EVIDENCE: Site A homepage tile reads "253 SHIPS TRACKED" and version line reads "v0.4.0 · 253 ships". Site B reads "254 ships total" directly under the Ship Purchase Matrix heading.

ID: C-003
SITE: BOTH
PAGE: Site A Cutlass Black detail page ("Where to buy" tab) + Site A footer + Site B Ship Purchase Matrix row
CATEGORY: disagreement
LABEL: CONFIRMED
SEVERITY: slows it down
EVIDENCE: Site B row: "Confirmed — starcitizen.tools 4.9.0". Site A sitewide footer: "aUEC prices are community-reported and dated — not verified in game." Site A's only patch note on this ship (expand "PATCH 4.10" panel): "last verified against patch 4.10" — for components, not price.

ID: C-004
SITE: BOTH
PAGE: Site A Cutlass Black detail page vs Site B Ship Purchase Matrix
CATEGORY: navigation
LABEL: CONFIRMED
SEVERITY: slows it down
EVIDENCE: Steps to reach a patch/source-backed price check: Site A needs search → click ship → click "Where to buy" → expand 2 disclosures (5 actions). Site B needs only the initial search (0 extra actions); the answer is in the same row.

ID: C-005
SITE: B
PAGE: https://citizencompass.netlify.app (entire single page)
CATEGORY: missing information
LABEL: CONFIRMED
SEVERITY: blocks a task
EVIDENCE: Read the full text of every section (Ship Purchase Matrix, Development Progress, Sale Calendar, Legend & Sources) and searched it for "contact", "report", "feedback", "email", "mailto", "issue", "bug", "suggest", "credit" — none of these words appear anywhere on the page.

ID: C-006
SITE: A
PAGE: https://citizencompasstesting.citizencompass-contact.workers.dev/next (all 4 tabs)
CATEGORY: missing information
LABEL: CONFIRMED
SEVERITY: slows it down
EVIDENCE: Read the full text of the Ships, Development Progress, Sale Calendar, and Legend & Sources tabs. The only contact-related text found: "If Cloud Imperium Games would like any of this taken down, write to citizencompass.contact@gmail.com and it will be removed." No general feedback/bug-report form exists.

ID: C-007
SITE: A
PAGE: Site A homepage
CATEGORY: only on A
LABEL: CONFIRMED
SEVERITY: cosmetic
EVIDENCE: Site A shows tiles: "253 SHIPS TRACKED / 237 WITH A PLEDGE PRICE / 179 BUYABLE IN GAME / 18 MANUFACTURERS / 5 SHIP DEALERS / 28 JOBS COVERED." Read Site B's full page text — only "254 ships total" appears, no equivalent breakdown.

ID: C-008
SITE: A
PAGE: Site A ship detail page
CATEGORY: only on A
LABEL: CONFIRMED
SEVERITY: slows it down
EVIDENCE: Site A footer text: "Click any ship for the 3D model, its hardpoints in CIG's own positions, and the full loadout." Detail-page tabs observed: Loadout, Engineering, Liveries, Where to buy, Specs. On Site B, the Cutlass Black row's only link, per its HTML, is `<a class="buy-link" href="https://robertsspaceindustries.com/...">` — an external link, not an internal detail page.

ID: C-009
SITE: A
PAGE: https://citizencompasstesting.citizencompass-contact.workers.dev/find.html
CATEGORY: only on A
LABEL: CONFIRMED
SEVERITY: cosmetic
EVIDENCE: This page states "26,657 price rows, read from a file. 7,932 items across 823 terminals and 100 categories" with a downloadable file and a sha256 hash for self-verification. Searched Site B's full text for "FIND", "commodity", "terminal", "hash", "sha256", "download" — none found.

ID: C-010
SITE: A
PAGE: Site A Cutlass Black detail page
CATEGORY: only on A
LABEL: CONFIRMED
SEVERITY: cosmetic
EVIDENCE: Expandable text: "This site does hold real shop and price data... Nothing has verified that a given game file component IS a given priced shop item..." plus stats "318 ships, 3292 components, 27 types". No equivalent explanatory text found anywhere in Site B's page text.

ID: C-011
SITE: A
PAGE: Site A Legend & Sources tab
CATEGORY: only on A
LABEL: CONFIRMED
SEVERITY: cosmetic
EVIDENCE: Section titled "BETTER TOOLS FOR OTHER JOBS" naming Erkul, Fleetyards, and SPViewer. Searched Site B's Legend & Sources text for "Erkul", "Fleetyards", "SPViewer", "BETTER TOOLS" — none found.

ID: C-012
SITE: A
PAGE: Site A Legend & Sources tab
CATEGORY: only on A
LABEL: CONFIRMED
SEVERITY: cosmetic
EVIDENCE: Legend entry: "no image — no picture held, shown as a gap rather than a wrong hull." Site B's Legend & Sources section lists only 4 entries (In-Game Purchasable, Pledge Only, "Flyable, no in-game dealer", "Not yet flyable"); searched its text for "no image" — not found.

ID: C-013
SITE: B
PAGE: Site B Development Progress section
CATEGORY: only on B
LABEL: CONFIRMED
SEVERITY: cosmetic
EVIDENCE: Two paragraphs: "General 2026 outlook (context, not confirmed ship names): ...multiple manufacturers... have additional ships 're-entering development'..." and "Known non-purchasable ships (context, not a price list): ...the RSI Bengal..., the RSI Pegasus..., and every Vanduul alien ship...". Read Site A's full Development Progress tab text and searched for "General 2026 outlook", "Known non-purchasable", "RSI Bengal", "RSI Pegasus", "Vanduul" — none found.

ID: C-014
SITE: B
PAGE: Site B Ship Purchase Matrix
CATEGORY: only on B
LABEL: CONFIRMED
SEVERITY: cosmetic
EVIDENCE: Table columns include a ✓/— cell for each of 5 named dealers per ship row (confirmed via the Cutlass Black row's HTML showing 5 separate `<td class="center check">` cells). Site A instead writes locations as inline text on each card (e.g. "at New Deal · Lorville").

ID: C-015
SITE: B
PAGE: Site B homepage
CATEGORY: only on B
LABEL: CONFIRMED
SEVERITY: cosmetic
EVIDENCE: Banner text and link: "● LIVE 4.9.0 ◆ PTU 4.10.0 Patch Notes ↗" pointing to the official patch notes (not opened). Searched Site A's full page text for "Patch Notes" and "patch-notes" — neither found; Site A shows only plain text "Live 4.10.0 'Siege of Orison' · PTU —".

ID: C-016
SITE: B
PAGE: Site B Ship Purchase Matrix
CATEGORY: only on B
LABEL: CONFIRMED
SEVERITY: cosmetic
EVIDENCE: Cutlass Black row HTML: `<a class="buy-link" href="https://robertsspaceindustries.com/en/pledge/ships/drake-cutlass/Cutlass-Black" target="_blank">`. On Site A's list/card view no such link exists; an RSI link only appears after opening the internal detail page.

ID: C-017
SITE: B
PAGE: Site B Ship Purchase Matrix
CATEGORY: only on B
LABEL: CONFIRMED
SEVERITY: cosmetic
EVIDENCE: Text: "Categories you can search: Bomber, Capital/Multi-crew, Cargo, Data, Exploration, Fighter, Ground Vehicle, Gunship, Interdiction, Medical, Minelayer, Mining, Multi-role, Racing, Refuel, Salvage, Search & Rescue, Support/Repair, Touring/Luxury" (19 items) versus Site A's 12 visible filter buttons: "Buyable in game, Combat, Transporter, Exploration, Competition, Support, Industrial, Ground, Multi-Role, Starter, Gunship, Snub Fighter".

ID: C-018
SITE: A
PAGE: Site A ship detail page / main navigation
CATEGORY: navigation
LABEL: CONFIRMED
SEVERITY: cosmetic
EVIDENCE: The FIND tool is not linked from the main nav bar (Ships, Development Progress, Sale Calendar, Legend & Sources). It is only reachable by opening a ship's detail page, clicking "Where to buy", and clicking the "Where the shop data actually is" disclosure link, which leads to find.html.

ID: C-019
SITE: BOTH
PAGE: Site A Legend & Sources tab / Site B Legend & Sources section
CATEGORY: disagreement
LABEL: CONFIRMED
SEVERITY: cosmetic
EVIDENCE: Both sites separately flag the same underlying fact with different wording. Site A: "Known conflict, shown rather than resolved: the Aegis Idris-P reads $1,900 on the store today against $1,500 in an older snapshot." Site B: "Known conflict: Aegis Idris-P shows $1,900 currently vs $1,500 in an older snapshot — both noted, not resolved for you." (Same substance, not a true disagreement, but reworded independently — listed for completeness.)

ID: C-020
SITE: A
PAGE: Site A ship detail page
CATEGORY: navigation
LABEL: OPINION
SEVERITY: cosmetic
EVIDENCE: A first-time visitor exploring only the four visible nav tabs would very likely never find the FIND tool, since reaching it requires already being three levels deep on a specific ship page and expanding a disclosure that doesn't obviously promise a second tool.

ID: C-021
SITE: BOTH
PAGE: Site A Cutlass Black detail page / Site B Ship Purchase Matrix row
CATEGORY: trust
LABEL: OPINION
SEVERITY: slows it down
EVIDENCE: A first-time visitor asking "has this been checked, and against which patch" would likely accept Site B's one-line "Confirmed — starcitizen.tools 4.9.0" at face value, whereas on Site A they would likely conflate the "PATCH 4.10" component note with price verification, since the real price caveat sits in a separate sitewide disclaimer they may not connect to this specific ship.

ID: C-022
SITE: BOTH
PAGE: Site A Cutlass Black card/detail page / Site B Ship Purchase Matrix row
CATEGORY: trust
LABEL: OPINION
SEVERITY: slows it down
EVIDENCE: Because Site A shows two different prices for the same ship ($110 vs $105.00) while Site B is internally consistent at $105.00, a first-time visitor is likely to trust Site B's number more simply for not contradicting itself, even though Site A discloses far more about data sourcing once you dig into its detail pages.

## Ending Summary

**Counts:** 19 CONFIRMED, 0 UNVERIFIED, 3 OPINION.

**Which site would a first-time visitor trust more for "where can I buy this ship and for how much":** Probably Site B. It states one consistent price ($105.00) with a plain source-and-patch tag right where you find the ship, whereas Site A undermines its own credibility by showing two different prices ($110 vs $105.00) for the identical ship depending on which page you're on, and its real verification story is spread across a sitewide disclaimer and buried, easy-to-misread disclosure panels.

**Three things to carry over first, by ID:**
1. C-014 / C-015 — carry Site B's per-shop checkmark matrix and inline Confidence/Notes tag onto Site A, since it removes 5 extra clicks and 2 disclosure-panels' worth of confusion from confirming a price and its source.
2. C-005 / C-006 — build a real, general feedback/report-a-problem path (neither site fully has one, but Site A already has a contact email to extend, while Site B has none at all).
3. C-001 — resolve the internal $110 vs $105.00 mismatch on Site A before anything else, since a first-time visitor hitting two different numbers for the same ship undermines trust in every other number on the site.
