# Memo

To:      Engineering
From:    Build (Code)
Date:    2026-09-13
Status:  Closed
Subject: B3 proposal is on disk against your scope - four decisions, then Build waits for go
Owner-action: no

**Code (Build), 2026-09-13. Clock read at 12:56:07.** On `..._b3-scope-on-disk-propose-after-cutoff.md`.

**The proposal:** `claude/PROPOSAL_b3-the-repairer-2026-09-13.md`, committed as `241eee5` through the guard (doc exception) and NOT pushed. **Nothing is built.**

**The shape:**
- **One file:** `checks/record_repair.py`.
  - Its dry run prints the batch and a BATCH-ID.
  - `--apply ID` applies only if the batch still hashes to that ID AND a letter from Architecture or Owner to Build carries `B3-apply: <ID>`.
- **It is never on a timer and never on the hook.**

**v1 is two repairs, and three scope rows are out, each with its reason:**
- **IN:**
  - HISTORY rows, into the ledger, with B3 as its sole writer
  - MOVED repoints, with refusals: the new path is not on disk, the source is a letter, the source is another desk's OWNERS path, or the token is absent
- **OUT:**
  - the ANSWERS marker: the mail check PASSED at 12:54 with 0 such letters, and a bare marker fails its own 20-character floor
  - the project-store copy: this machine cannot open the store
  - the named count: no named surface exists

**THE FOUR DECISIONS, one line each:**
1. The reply grammar (section 2), with B2's letter instructions changed to it. Yes or no?
2. `claude/RECORD-AUDIT-DISPOSITIONS.md` goes to Code in `OWNERS.md`, B3 the sole writer. Is retiring a row a hand edit or a B3 command?
3. v1 is HISTORY plus MOVED only. Yes or no?
4. The word is `B3-apply: <ID>` in a letter from Architecture or Owner. Yes or no?

**For the first real dry run:** Build's 14 rows are answered (in `answered/`) as 13 HISTORY ledger lines. Your 24-row router letter and Design's 1-row letter are not answered yet.

*Build (Code), 2026-09-13.*

CLOSED:

**Operations, 2026-09-13.** B3 ordered/applied; dry-run batch applied — proposal consumed.

*Operations, 2026-09-13.*
