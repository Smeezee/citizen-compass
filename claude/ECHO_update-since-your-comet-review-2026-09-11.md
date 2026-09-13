# ECHO — everything since your Comet review, 2026-09-11

**Filed 2026-09-11 by the Adjutant desk. Copy-paste block for Echo.** Covers what happened
after her review of the Comet test plan, plus the parts of the day she was never told.

---

Echo — this catches you up on Citizen Compass for 2026-09-11. Your last two inputs were the five answers (record, freeze, footer, cuts, export) and the review that stopped the Comet test. Here is what came of both, and everything else that moved. Times are US Central. Where something was checked by reading the site or the files, I say so; otherwise it comes from a desk's own report.

Keep using your labels: ESTABLISHED, RECOMMENDATION, FORECAST.

## 1. SLEVEN RULED ON ALL FIVE OF YOUR ANSWERS, ABOUT 02:30

In his words: "Make the committed Git repository the official record and treat the cloud as a copy. Freeze automation because it is safely off and disconnected. Before Q54 deploys, replace the false footer with honest wording; unfinished features are acceptable on the test site, false claims are not. Reduce duplicate reports, unnecessary desk reviews and routine owner approvals. For the Perplexity export, remove any document as soon as its approved version changes, then return it only after reapproval."

Your allow-list correction was checked against the probe log and accepted: both refused calls and the allowed call were all "Write"; only the path separated them. What is still untested is the allowance refusing a write by itself with an approver present. Architecture added a fact nobody had named: an allowance written as Edit(...) governed a Write call, so any containment argument based on the tool name is unsound.

## 2. WHAT ARCHITECTURE DID WITH THE RULINGS

**The record.** Specified, not built. One-way flow: finished on disk, committed, then mirrored, with the commit and content hash on every mirrored copy. Recovery of project-only documents by content hash, proven complete by arithmetic (every project document lands in one of four buckets and the buckets sum to the project's count). Your four-part reference check, each part provable by mutation.

Two limits it found: the one-way rule cannot be enforced, because any session can still write to the cloud project, so it becomes a detector that re-hashes mirrored copies instead. And "the authoritative set" needs a positive definition, because the documents folder currently holds empty files (an empty Untitled.md) that would pass "exists" and "tracked".

**The blocker.** No Cowork desk can commit at all. Architecture is barred from Git operations on the mounted repository after an eight-day index-lock jam, and the Cowork shell on Sleven's machine has been down since a Windows update on 2026-09-08. Only Claude Code can commit, and every commit still needs Sleven's word under the project's hard rule 2. **Who commits documents is undecided.**

**Proposed standing commit permission, for Sleven to rule on:** documents only, explicit file list, one item per commit, no push, no delete, no rename, nothing else in the same commit, and a pre-commit hook that refuses, proven able to refuse before the permission is ever used.

**The freeze.** Recorded in the state document and the queue. Code's freeze entry, read off the machine, corrected two things: the watcher that is actually running is a different binary from the one in the watcher's source folder, so a restart that rebuilds there would not be running what it thinks; and the spend cap was set on a claim of "about ten times the worst honest run" when one 26-second probe cost 0.527 against a cap of 2.00. The cap was left alone and put on the restart checklist.

**The export.** Drop-on-change written into the design as the ruling.

**The cuts.** Five named, each for Sleven's yes or no, not yet answered:
1. The narrative desk log. Recommended: cap it at ten lines of findings per pass rather than delete it, because three of the week's better findings came from writing it.
2. Status-only letters to the owner's tray. Only decisions, permissions and rulings go there.
3. A second desk reviewing a reversible change that already has a control, provided the control has been seen failing.
4. Routine commit approval for documents, under the permission above.
5. Design review of a spec that will be built within a day and is reversible. Anything touching a boundary keeps its review.

It kept your keep-list, and added two: verifying from a different source than the claim, and never deleting anything.

**Its candid point:** the record ruling adds a step to every document on the same day Sleven ordered cuts, and the five cuts do not pay for it. Net process went up. It suggested that if that was not intended, the mirror should shrink to what a session without repository access actually needs.

## 3. THE FRONT PAGE MOVED A LOT

All reported by Code, with the served site checked after each deploy.

- **03:12 — Q54 deployed.** The new page is the front door at /, the old one at /classic. The false footer was replaced before upload with: "aUEC prices are community-reported and dated — not verified in game. Verification is incomplete: most ships on this page do not yet show the patch they were checked against."
- **Found at 11:40, fixed and deployed at 12:50 — a regression Q54 caused.** From 03:12 the front door carried no "testing" stamp, so the test site was indistinguishable from a live one, and the deploy guard passed anyway because it only checked the old page's file. The stamp and the guard now both cover whichever page is the front door.
- **13:25 — Q57.** An invented sentence about the RAPTOR ship was removed at its real source on the test site. The chain was not where anyone had said: it comes from a data literal in an old page file, not the database. **The public site still shows the sentence.** Changing the public site is Sleven's call.
- **14:08 — Q55.P1.** Four old section links (#matrix, #dev, #calendar, #legend) land correctly again. Tab addresses and the back button are a separate item.
- **Code caught itself once:** it started the check run while another check was editing the payload, recognised the result would prove nothing, killed it and re-ran cleanly.
- **Queue:** C1 filed 25 entries for the missing features. 16 of them are keep-or-drop decisions for Sleven.

## 4. A PROBLEM FOUND BY CHECKING THE SITE FOR YOUR REVIEW

**On a phone, the test site hides its "testing" stamp.** At about 386 pixels wide the version line is set to not display, so the stamp is in the page but invisible, and the guard passes because it reads the file, not the screen. Found by the Adjutant desk in Chrome, then confirmed independently by Comet in run 1. Code took it at 14:08.

## 5. THE FEEDBACK FORM

Sleven ruled that the feedback route comes back on the new front page, sitting on the page rather than behind a link. The old route was a link out to JotForm and got zero submissions. It must clear after each note so one person can send several. Architecture recommends how. A third-party form keeps the site as plain files; storing notes in our own database would be the first time a visitor's request reaches a Citizen Compass server.

## 6. BLUE-GREEN DEPLOYMENT — PLANNED, NOT BUILT

Verdict: not now. Both sites are static files; the database is only read at build time on Sleven's machine; the one runtime call on the new page is a third-party exchange-rate lookup. Cloudflare keeps every deploy as a version with instant rollback to the last 100, per-version preview addresses, and upload-without-deploy. Netlify versions every deploy, including hand uploads, with instant rollback.

The one real gap: the live build is a separate rebuild, so its exact bytes are never seen before visitors get them. When the public site moves to Cloudflare, upload that build as a version, check it at its preview address, then deploy that version.

The milestone that justifies real blue-green: the first release where a visitor's request reaches our own server or database. Adopt expand-and-contract migrations now, because destructive migrations and downgrades are already barred and rollback would be code-only.

## 7. THE COMET REVIEW — YOUR FINDINGS WERE ALL ACCEPTED

Your six points and the external-link change were taken. The answer key was re-checked against the served, rendered site in Chrome, and every value held. The review became five runs: capability test, public site desktop, test site desktop, phone, comparison. Labels are CONFIRMED, UNVERIFIED and OPINION, with the stricter evidence rules you set.

**Run 1, capability test: PASSED.**
- Header count, all six stat boxes, and the three maker headings with their sub-lines were exact. The headings came back in CAPITALS, which is the page's styling rather than the embedded data, so it was reading the rendered page.
- It found the correct ship page and got Back to the list.
- At 390 pixels: one card per row, the fourth tab cut off, and no stamp visible, which independently confirmed section 4.
- Public site title, date and patch line: exact.
- It reported unprompted that one of its own clicks sent a tab to a blank page, and that it finished in a new tab.
- It used page inspection as well as screenshots for the layout answers.

**Run 1 did not meet your safety condition.** It ran in Sleven's everyday profile. The clue was that its first load showed no testing stamp, which only a tab opened before the 12:50 deploy could show, before the clean profile existed. It was confirmed when run 3, started in the new clean profile, hit the password gate.

**Run 2, public site, desktop: usable, labels honest.** 5 CONFIRMED, 1 UNVERIFIED, 1 OPINION.
- **P-001** Every ship name links out to RSI; there are no in-site ship pages.
- **P-002** No way to report a problem or leave a note.
- **P-003** No credits section.
- **P-004, the strongest:** the Idris-P row says its $1,900 price is "confirmed", while the Legend tab says the same price is in unresolved conflict with $1,500. The trust signal and the caveat sit on different tabs.
- **P-005** Tested by keyboard: the focus outline measured roughly 1.1:1 contrast against the background.
- **P-006 OPINION:** the patch information appears twice, in two styles.
- **P-007 UNVERIFIED:** no dedicated filter by buyable or manufacturer.

It could not know, and did not claim, that the public site's patch line is wrong: the game has been on 4.10 since late August. Nothing routed yet: the public site is frozen, and these findings are the baseline for the comparison run.

**Run 3, test site, desktop: stopped at the password gate in the clean profile, as instructed.** Sleven is unlocking it himself; the password is not given to Comet.

## 8. STILL WAITING ON SLEVEN

The cloud project's instruction that tells sessions to save to the cloud and not to disk. The five cuts. Who commits documents. Whether /next stays behind the password. Graphify before or after the brakes. Whether the repository is pushed and whether it is public. The public site's RAPTOR sentence. The 16 keep-or-drop feature decisions.

Your Graphify correction, that its local server includes GitHub tools able to call an authenticated command line, has not yet been checked against the source. The install is parked until it is.

## WHAT WOULD HELP FROM YOU

Short answers, only where you see a real problem:
1. Run 1 ran in the everyday profile. Anything in its results or its behaviour you would treat differently because of that?
2. The proposed standing commit permission in section 2. Is a pre-commit hook the right enforcement point, or is there a stronger established pattern for letting an agent commit documents only?
3. Architecture's point that net process went up. Is shrinking the mirror the right lever, or is there a better one?
