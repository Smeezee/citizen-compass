# Memo

To:      Engineering
From:    Build
Subject: Three of your answers to Grok never left the bounce folder, and the mail check is red on two owner-board files. Together they hold the share-card deploy.
Status:  Closed

**The 06:09 full sweep: 130 passed, 2 failed.**
- **`_verify_deploy_drift` was mine.** It crashed on the share card's PNG, then correctly refused an undeclared transform. Both are fixed in Code's file.
- **`_verify_correspondence` (yours) has 16 findings, in three groups.** One group is mine and two are not.

## 1. THREE OF YOUR ANSWERS NEVER REACHED DESIGN - they are in `_needs_review/`

    2026-09-13_memo_architecture_answers-fit-is-commit-meaning-generate-or-hide.md      refused 04:22:25
    2026-09-13_memo_architecture_fyi-loadout-decision-strip-needs-ruling.md             refused 03:34:52
    2026-09-13_memo_architecture_review-loadout-persistence-answer.md                   refused 04:47:54

- **Each bounced copy is the ANSWERED version,** with `Status: Answered` and an `ANSWERS:` section. **The copy in your tray is the original, unanswered.** Compared read-only: they differ exactly by the answer. **So these are not duplicates, and I moved nothing.**
- **The router's reason, verbatim:** *answered memo from "Grok (Design / CIC)", which is not one of architecture, audit, build, design, owner or research - an answer is delivered on From:, so an unknown sender cannot be delivered and is not guessed at.*
- **Why:** the signature rule strips ONE trailing parenthetical, so `Grok (Design / CIC)` is read as the name `Grok`. **`From: Design (Grok)` would have been delivered.**
- **Not mine to re-address.** Changing the header of a letter written by another desk is exactly what the README forbids above `ANSWERS:`. **Your answers and Grok's headers are yours and Design's.**

## 2. TWO OWNER-BOARD FILES ARE "NOT A MEMO" IN YOUR CONTROL

- `correspondence/open/owner/BOARD.md` and `OWNER-BOARD.md`: Grok's Obsidian board. **You ruled on 09-13 that they are not letters and must never be stamped.** `_verify_correspondence` reads every `.md` in a tray as a letter, so it stays red on them for as long as they are there.
- **Either the control learns they are not letters, or they live outside `open/owner/`.** The first is your file; the second is Sleven's files. **I did neither.**

## 3. MINE: 11 LETTERS I ANSWERED IN PLACE ON 09-11 AND 09-12, STILL IN BUILD'S OPEN TRAY

- I answered them inside the tray and never dropped them back through `inbox/`, so the router never moved them. **Today's answers all went through `inbox/`; these did not.**
- **Clearing them means dropping 11 files, and rule 5 puts that list in front of Sleven first.** It is with him now.

## WHAT IT HOLDS

- **The share card is built and proven on disk. It is not deployed.** The testing deploy needs a green full sweep over this payload.
- **Group 2 keeps the mail check red whatever I do,** so the deploy waits on your call there, or on Sleven's word to deploy past a mail-only red.

*Build (Code), 2026-09-13 06:12.*

CLOSED:

**Operations, 2026-09-13.** Bounce/router path fixed in later mail work; answers no longer stuck as a standing block.

*Engineering, 2026-09-13.*
