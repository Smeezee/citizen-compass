# RULINGS — the decision packet, twenty-four answers

**Given by Sleven 2026-09-12 (late 2026-09-11 CDT) in reply to the consolidated decision
packet. Recorded by the Adjutant desk. His words are reproduced first, unchanged. The desk's
conflict notes follow and are marked as the desk's, not his.**

**Scope limit he set, in his words:** "They are not blanket authorization to begin unrelated
implementation." and "Do not begin new implementation merely because these rulings were
supplied."

---

## HIS RULINGS, VERBATIM

**Report system**

1. I am currently the only person who reads submitted reports. There is no guaranteed schedule yet, so the website must not promise one. After submission, display: "Saved. Thank you."
2. Use "Report issue" on the ship cards.

**Special editions**

3. Confirm the ship's complete official name. Do not confuse it with the separate Anvil Liberator.

Use this rule for every special edition:
- Cosmetic or paint-only edition: fold it under the base ship.
- Physically, mechanically, or functionally different edition: give it a separate card.

Research the Valkyrie edition before changing it. Audit the other seven edition cards using the same rule.

**Front page**

4. Keep confidence, source, and last-verified patch information on every ship card.
5. Restore the original site's full sorting and filtering abilities, including dealer, location, price, manufacturer, components, ship type, role, and the other previous options. Redesign them for the card layout instead of blindly copying the old interface.
6. Keep the budget filter. It may be redesigned for better usability.
7. Keep the manufacturer jump/filter.
8. Use Star Citizen's official intended ship roles as the authority. Broad career categories may remain as shortcuts only when they do not contradict the official roles.
9. Add a visible "Clear filters" control.
10. Add "Back to top," especially for long mobile pages.
11. Redesign the accessibility presets for the entire website: dyslexia-friendly, low vision, tired eyes, and reduced motion. Settings should follow the visitor between pages.
12. Keep useful readability controls, but drop CSS export.
13. Keep the keybinds page. First determine its current location and completion state, verify that its information is current, finish it if necessary, and then add a visible website link.
14. Keep the item and commodity finder and make it easier to reach.
15. Replace the old help panel with site-wide contextual help. Every page should have a help control explaining the page the visitor is currently using. Ship-page help should explain that ship's interface; front-page help should explain the front page; keybind help should explain the keybind page.
16. Keep the report form: one text box, no unnecessary pop-ups, submitted to our own server. Do not promise when it will be read.
17. Keep official patch-note links. Eventually, they should update automatically from the website's verified current-patch record instead of being manually typed. Remove the old Spectrum link unless it is verified to contain unique, current information.

Build and stabilize the desktop version first, then properly adapt and test tablet and phone layouts.

**Process changes**

18. Keep desk logs, but replace long narratives with a short structured record:
- Work taken
- Result
- Evidence
- Problems or decisions needed
- Next action or blocker

19. My tray should receive decisions, failures, permission requests, and one final completion notice for work I ordered. Routine progress belongs in the state record.
20. A second desk may be skipped for a small, reversible change only when an automated check covers it and that check has been deliberately proven capable of failing. Security, database, and deployment changes still require review.
21. Code may commit specifically named documentation files locally without asking me for every commit, but only after an automatic guard proves it refuses anything outside the allowed scope. This permission does not include code, deletion, pushing, or unrelated files.
22. Small, reversible specifications being built immediately may skip a separate design review. Security, database, deployment, irreversible, or expensive work still requires review.
23. Route document commits through Code. Do not restore Architecture's Git access until the previous repository-lock problem is understood and corrected.
24. Reduce the external AI-project mirror to only the documents outside sessions genuinely need. The local repository remains the complete official record. Avoid unnecessary duplicate documents and stale copies.

---

## THE DESK'S NOTES — CONFLICTS AND AMENDMENTS NEEDED

These are the Adjutant desk's, not Sleven's. None of them changes a ruling; each names a
document or a rule that now disagrees with one.

**A. Ruling 21 is an exception to hard rule 2 and the rule file has to say so.**
CLAUDE.md hard rule 2 says nothing is committed without his word. Ruling 21 creates a
standing, narrow exception: named documentation files, by Code, guard-first. Until the rule
file records the exception, the rule and the ruling disagree on paper. **Whoever owns
CLAUDE.md proposes the wording; it is his file to approve.**

**B. Ruling 24 amends the record spec.**
`claude/SPEC_the-record-is-what-is-committed-2026-09-11.md` specifies mirroring documents
with a provenance header and a detector that re-hashes them. Ruling 24 shrinks the mirror to
what outside sessions genuinely need. **The spec needs a section saying which documents
qualify, and the arithmetic proof in it has to be re-stated for a partial mirror, because
"every project document lands in one of four buckets" no longer holds.**

**C. Ruling 5 asks for component filtering, and the join it needs does not exist.**
The ship page's own disclosure says there is no proven link between the component data read
from the game files and the priced shop items. Dealer, location, price, manufacturer, ship
type and role are all supportable from data the site already holds. **Components are not,
today.** Either the join gets built first or that one filter waits; it should not be promised
on the page before it is true.

**D. Ruling 8 supersedes the career taxonomy and lands on an open defect.**
The new front page filters on a career field. Under ruling 8, official roles are the
authority and careers are shortcuts. **T-003 — the Ground button showing 7 of 29 ground
vehicles, and 34 ships under no button at all — is now a symptom of the taxonomy question
rather than a separate bug, and the two must be answered together.**

**E. Ruling 15 overlaps work that already exists and is switched off.**
`next.html` already carries a glossary with definitions and working tooltip code that nothing
calls (M-014). Contextual help and the glossary are two different things, but they are
adjacent, and building help without switching the glossary on would leave two half-systems.
**Sequence them in one entry.**

**F. Ruling 17's automatic patch link needs a record that does not exist yet.**
There is no single verified current-patch value the pages read from. The site is generated,
so "updates automatically" means at build time from that record. **The record is the
prerequisite, and it is the same record ruling 4 needs for last-verified-patch.**

**G. Desktop first changes the order of work already queued.**
Run 4's findings are phone findings (M-001 to M-013). Under "build and stabilise desktop
first", they move behind the desktop work rather than being dropped. **The review's own
re-run at the end still covers phone, so nothing is lost, but the queue order changes.**

**H. Ruling 11 needs settings to persist across pages on a site of plain files.**
That means storing the visitor's choice in their own browser. No server, no account. Worth
naming because it is the first piece of per-visitor state the site would hold.

**I. Ruling 19 slightly widens the cut Architecture proposed.** It proposed decisions,
permissions and rulings only; he adds failures and one completion notice per ordered job.

## ALREADY COVERED BY AUTHORISED WORK

- Ruling 4 — the patch-per-price item was already made a keep by the "fix everything the
  review found" letter (Q55.P5 / Q61). Ruling 4 is the fuller version of it.
- Ruling 14 — already a keep by the same letter (T-002 / Q55.P16).
- Rulings 1, 2 and 16 — the report control's build proposal is written and waiting; these
  three complete it. Still no build without his word on the proposal itself.
- Rulings 9 and 10 — new, but small and already in the front-page queue as proposals.

## NEEDS RESEARCH BEFORE ANY CHANGE

1. **The Valkyrie edition's full official name and what the edition actually changes** —
   cosmetic or functional — plus the same audit for the other seven edition cards, against
   RSI's own material. Ruling 3.
2. **The keybinds page: where it lives, how finished it is, whether its content is current.**
   Ruling 13.
3. **Whether the Spectrum link holds anything unique and current.** Ruling 17.
4. **The official role for each ship, from RSI's own material**, before the taxonomy changes.
   Ruling 8.
5. **Whether component-level filtering is possible at all** with today's data. Note C.
