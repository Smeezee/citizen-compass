# Memo

To:      Build (Code)
From:    Owner (Sleven)
Date:    2026-09-12
Status:  Answered
Subject: Optional — echo-salvage_ zips also land a copy under design/echo-imports

**Not blocking.** Inbox already unpacks zips and sorts .md memos. Echo labeling is in `claude/PROMPT_echo-salvage-zip-for-inbox.md`.

**Nice-to-have when you next touch the watcher:** if a dropped zip basename starts with `echo-salvage_`, after extract/sort, also copy the original zip (or a receipt) into `design/echo-imports/_drop/` so Design can find the pack in one place without digging `_zip_archive/`.

Proposal first if non-trivial. No swap until proven. Low credits — skip until B1 is green if busy.

*Owner (Sleven). Drafted with Grok.*

ANSWERS:

**Proposed, not built:** `claude/PROPOSAL_the-echo-zip-receipt-2026-09-13.md`. B1 is green, so it came up next.

- **A receipt, not a copy.** It goes in `design/echo-imports/_drop/`. It names where the original zip was archived and where every memo inside it was filed.
- **Why:** the zip already lives once, in `_zip_archive/`, and a copy would be a second home for the same bytes. If you want the zip itself, it is one line.
- **It never changes routing,** and the watcher is its only writer.
- **The part that is not trivial:** the folder's README says `_drop/` is for zips somebody parks by hand. Receipts there change its meaning. **I recommend following your letter: receipts in `_drop/`, plus one README line saying so.**
- **Proof before any swap:** a new zip test with five cases and a mutation for each. **The watcher swap then needs your word,** as you said.

**Your one decision:** a receipt in `_drop/` plus one README line, yes or no?

*Build (Code), 2026-09-13, 08:11.*
