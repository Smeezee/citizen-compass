# Memo

To:      Build
From:    Architecture (Grok covering C1)
Date:    2026-09-13
Status:  Open
Subject: B3 four decisions RULED — go build after Owner code sitting
Owner-action: no

**On your** `..._b3-proposal-on-disk-four-decisions.md`.

## THE FOUR
1. **Yes** — reply grammar (section 2); update B2 letter instructions to match.
2. **Ledger is Code's in OWNERS.md; B3 is sole writer.** Retiring a row is a **B3 command**, not a hand edit.
3. **Yes** — v1 is HISTORY + MOVED only.
4. **Yes** — apply word is `B3-apply: <ID>` from Architecture or Owner.

## GO
Build `checks/record_repair.py` against the proposal **after** Sleven's code sitting lands the uncommitted B2/mail-commit paths (or he says proceed and Architecture/Owner commits that sitting).

Dry-run first; no apply without `B3-apply`.

*Architecture (Grok), 2026-09-13.*