# RESULT — Comet run 2 of 5: the public site, desktop

**Run 2026-09-11 afternoon CDT by Sleven in Comet, prompt
`claude/PROMPT_comet-run-2-public-site-desktop-2026-09-11.md`. Assessed by the Adjutant
desk.** Whether it ran in the separate "CC Test" profile was not stated.

## ASSESSMENT

**Usable. The labels were applied honestly and the evidence mostly meets the bar.**

    first impression before purpose   done in order; got the purpose from the tagline
    six tasks                         1-3 done in one step each; 4 not possible (no
                                      in-site ship page); 5 not found; 6 partly
    findings                          5 CONFIRMED, 1 UNVERIFIED, 1 OPINION
    external links                    listed, 235, none opened, as instructed

**Label quality, finding by finding:**

    P-001  CONFIRMED  sound. Link addresses read, not followed.
    P-002  CONFIRMED  acceptable. Proving an absence is weaker than proving a presence;
                      it names every place it looked.
    P-003  CONFIRMED  sound, with the notice quoted word for word.
    P-004  CONFIRMED  strongest finding of the run. Two quotes from two tabs that
                      contradict each other.
    P-005  CONFIRMED  a real test: keyboard only, with measured colours and a ratio.
    P-006  OPINION    correctly labelled.
    P-007  UNVERIFIED correctly labelled; it says what it did not check.

**What it could not know, and correctly did not claim:** the public site says live
patch 4.9.0 and PTU 4.10.0. The game has been on 4.10 since late August, so that line
is wrong, and has been recorded as wrong since 2026-08-30 (`LIVE.md`). Comet was told not to
use outside knowledge and did not.

## WHAT IS NEW TO THE RECORD

**P-004, the Idris-P.** The price table says "confirmed" while the Legend tab says the
same price is in unresolved conflict. **The trust signal and the caveat are on different
tabs.** Same class as Q58 on the new page, where a clamp hides the word "disputed".
**Worth checking whether the new page repeats it** — run 3 will show.

**P-005, keyboard focus.** A measured 1.1:1 focus-outline contrast on the public page.

**The rest was already known:** no in-site ship pages on the public site, no feedback
route (already ruled to come back on the new page), no credits section.

## ROUTING

**None yet.** The public site is frozen at v0.3.9 and going live is Sleven's alone.
These findings are the baseline for run 5, the comparison. Anything the test site
repeats goes to Architecture then, with both runs' evidence together.

---

## COMET'S REPLY, VERBATIM AS SLEVEN CARRIED IT IN

No instructions addressed to me were found anywhere on the site.
Step 1 — First Impression
Screenshot of the unscrolled top of the page attached above.
a. What I think this is for: A reference tool for tracking and comparing prices of ships in a game — specifically "Star Citizen," based on the visible patch numbers, aUEC currency, and ship names. It reads like a spreadsheet-style lookup tool, not a store.
b. First three things my eye goes to: (1) The large "Citizen Compass" title with the tagline "Know where to buy, before you fly." directly under it; (2) the two colored status pills "● LIVE 4.9.0" and "◆ PTU 4.10.0" with the "Patch Notes ↗" link next to them; (3) the search box ("Search ships or categories...") with the "254 ships total" counter beside it.
c. What's confusing: The line "Patch: Alpha 4.9.0 'Frontier Tensions' (LIVE July 15-16, 2026) | Compiled/updated: 2026-07-30" sits directly above near-identical badges ("● LIVE 4.9.0 ◆ PTU 4.10.0"), so the same patch information appears to be stated twice in two different visual styles within a few pixels of each other — on first glance it wasn't obvious these two lines were saying the same thing rather than two different facts.
Step 2 — Match to Stated Purpose
My first impression (a price-lookup/reference tool for ship trustworthiness) matched the stated purpose reasonably well — the tagline itself gave it away. What I didn't pick up from the unscrolled view alone was that the site's core value is cross-checking buy locations and price trust levels; that only became clear once I saw the "Confirmed — starcitizen.tools 4.9.0" style notes in the table.
Step 3 — Six Tasks
1. Find "Cutlass Black" — Managed. 1 step: typed "Cutlass Black" into the search box, which filtered the table to "1 of 254 ships match." No sticking point.
2. Where it's bought, and price — Managed, 0 extra steps (visible in the same filtered row). Buyable only at "New Deal (Lorville)" (a checkmark; all other four dealer columns show "—"). Price (aUEC): 2,010,960. Pledge Price (USD): $105.00.
3. Whether the price has been checked, against which patch — Managed, 0 extra steps. The "Confidence/Notes" cell on that same row reads "Confirmed — starcitizen.tools 4.9.0."
4. Open the ship's details view — Not achievable on this site. The only "details" affordance is clicking the ship name itself, which carries a link icon and points away from the site to `https://robertsspaceindustries.com/en/pledge/ships/drake-cutlass/Cutlass-Black`. I confirmed this by inspecting the link's address without following it. The site has no in-site detail page for any ship — this is a systemic pattern, not unique to this one ship (confirmed across all ~254 ship name links; see the external links list below).
5. Report a problem / leave a note about the site — Could not find one. I checked all four nav tabs (Ship Purchase Matrix, Development Progress, Sale Calendar, Legend & Sources) and the page footer; none contain a contact, feedback, "report an issue," or note-leaving mechanism of any kind.
6. Credits and game-ownership notice — Partially managed. The ownership/trademark notice exists and is easy to find at the bottom of the Legend & Sources tab (2 steps: click "Legend & Sources," scroll to the footer): "This is an unofficial Star Citizen fan site, not affiliated with the Cloud Imperium group of companies. All content on this site not authored by its host or users are property of their respective owners," followed by "Official site: robertsspaceindustries.com" and "Star Citizen®, Roberts Space Industries® and Cloud Imperium® are registered trademarks of Cloud Imperium Rights LLC." However, there is no distinct "Credits" section naming any author or contributor — I found no such heading or text anywhere on the page.
Step 4 — Findings
ID: P-001
PAGE: https://citizencompass.netlify.app/ (Ship Purchase Matrix)
CATEGORY: navigation
LABEL: CONFIRMED
SEVERITY: slows it down
EVIDENCE: Clicking any ship name (e.g., "Cutlass Black 🔗") does not open an in-site details page. Checking the link's address shows it points to `https://robertsspaceindustries.com/en/pledge/ships/drake-cutlass/Cutlass-Black`, an external RSI page. This pattern held across all 229 ship name links found on the page (full list attached) — the site has no internal ship-detail view at all.
ID: P-002
PAGE: https://citizencompass.netlify.app/ (entire site: all four nav tabs and footer)
CATEGORY: missing information
LABEL: CONFIRMED
SEVERITY: blocks a task
EVIDENCE: I checked every nav tab (Ship Purchase Matrix, Development Progress, Sale Calendar, Legend & Sources) and the footer for any contact, feedback, "report a problem," or note-leaving link or button. None exists anywhere on the page.
ID: P-003
PAGE: https://citizencompass.netlify.app/#legend
CATEGORY: missing information
LABEL: CONFIRMED
SEVERITY: slows it down
EVIDENCE: The Legend & Sources footer contains only a generic legal/ownership notice — quoted word for word: "This is an unofficial Star Citizen fan site, not affiliated with the Cloud Imperium group of companies. All content on this site not authored by its host or users are property of their respective owners." There is no distinct "Credits" heading anywhere on the page naming an author, team, or contributor.
ID: P-004
PAGE: https://citizencompass.netlify.app/ (Ship Purchase Matrix, row for "Idris-P")
CATEGORY: ship information
LABEL: CONFIRMED
SEVERITY: slows it down
EVIDENCE: The Idris-P row's own "Confidence/Notes" cell reads, word for word: "Concept frigate variant. Pledge $1,900 - confirmed via RSI Pledge Store and a second source." It does not mention any discrepancy. But the separate Legend & Sources page states, word for word: "Known conflict: Aegis Idris-P shows $1,900 currently vs $1,500 in an older snapshot — both noted, not resolved for you." A visitor reading only the price table (where the price actually appears) would see the word "confirmed" and have no way of knowing there is an unresolved conflict, since that information lives on a different tab.
ID: P-005
PAGE: https://citizencompass.netlify.app/ (any interactive element, e.g. a ship link)
CATEGORY: accessibility
LABEL: CONFIRMED
SEVERITY: slows it down
EVIDENCE: I moved through the page using only the Tab key from a fresh load. The tab order itself was logical (patch-notes link → nav tabs → currency dropdown → search box → ship links in table order — no dead ends or traps). But the focus indicator itself is very low-contrast: I measured the page background as rgb(13, 27, 46) and the browser-reported focus outline color as rgb(16, 16, 16) — a contrast ratio of roughly 1.1:1, far below the 3:1 minimum the W3C recommends for focus indicators. In the attached screenshot (taken while a link was keyboard-focused), the outline is a thin box that is technically visible up close but easy to miss at a glance, especially against the busy, dark-navy table background.
ID: P-006
PAGE: https://citizencompass.netlify.app/ (top of page, unscrolled)
CATEGORY: first impression
LABEL: OPINION
SEVERITY: cosmetic
EVIDENCE: A first-time visitor scanning the top of the page sees the patch/date summary line ("Patch: Alpha 4.9.0 ... | Compiled/updated: 2026-07-30") immediately followed by two colored status pills repeating the same "LIVE 4.9.0" / "PTU 4.10.0" figures. I believe a typical visitor would briefly wonder whether these are two different pieces of information before realizing they overlap, because the same fact is shown twice in different visual treatments right next to each other.
ID: P-007
PAGE: https://citizencompass.netlify.app/ (Ship Purchase Matrix — general)
CATEGORY: missing information
LABEL: UNVERIFIED
SEVERITY: slows it down
EVIDENCE: I could not find any way to filter the ship table strictly by "in-game purchasable only" or by manufacturer using a dedicated control — only the free-text search box and scrolling exist for narrowing the 254-row list. I believe this would slow down a visitor who only wants to browse buyable ships, but I did not exhaustively test every part of the table header for a hidden filter control, so I can't rule one out with certainty.
Summary
1. Counts: 5 CONFIRMED (P-001 through P-005), 1 UNVERIFIED (P-007), 1 OPINION (P-006).
2. Top three to fix first:
* P-002 (no way to report a problem or leave a note) — this fully blocks Task 5 for every visitor with no workaround; even a simple email or form link would fix it.
* P-001 (no in-site ship details, every ship name leaves the site) — this is the single largest structural gap since it affects all ~229 ships and undercuts the site's stated job of being a self-contained reference.
* P-004 (price conflict disclosed only on a separate tab from where the conflicting price is shown) — a visitor relying on the main table alone would be misled by the word "confirmed" without ever seeing the caveat.
3. External links: Every link that leaves the site (235 total, none opened) is listed in the attached file — 6 reference links (starcitizen.tools, CStone, UEX Corp, RSI Pledge Store, the official robertsspaceindustries.com link, and the Patch Notes badge) plus 229 individual ship-name links, all pointing to `robertsspaceindustries.com` pledge pages.
