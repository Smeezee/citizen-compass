# Build update - Build's 14 router rows are answered; the B3 proposal is committed (241eee5, not pushed); Build waits on Architecture's go and Sleven's sitting

**Code (Build), 2026-09-13. Clock read at 12:56:07.**

**1. Build's 14 router rows: ANSWERED in place,** with the text above `Status:` unchanged (by script). The watcher filed the letter to `correspondence/answered/` at 12:54:51.
- **All 14 are HISTORY, as 13 distinct keys:**
  - 6 absence
  - 4 example
  - 3 future
  - 1 history
- Each is a ready ledger line in B1's `LEDGER_ROW` format, with its line number as evidence.
- **Not written into `claude/RECORD-AUDIT-DISPOSITIONS.md` by hand:** the B3 scope makes the repairer that file's writer (rule 14).

**2. The B3 proposal:** `claude/PROPOSAL_b3-the-repairer-2026-09-13.md`, **committed `241eee5`** through the commit guard (doc exception). **NOT pushed;** main is 1 ahead of origin.
- **v1 is HISTORY plus MOVED.**
- **The apply needs two things:** the batch hash must be unchanged since the dry run, AND a `B3-apply: <ID>` letter from Architecture or Owner.
- **Three scope rows are out, each with its reason:**
  - the ANSWERS marker: the mail check PASSED at 12:54 with 0 such letters
  - the project store: this machine cannot open it
  - the named count: no named surface exists
- **Memo to Architecture** with the four decisions: `..._b3-proposal-on-disk-four-decisions.md`.

**3. Delivered, none bounced:** the CUTOFF memos to Architecture (12:53:43) and Design (12:54:45).

**WAITING ON ARCHITECTURE:**
- the four B3 decisions, then go
- the `Owner-action:` field on their two owner letters

**WAITING ON DESIGN:** the field on its one owner letter. **The sweep is red on `_verify_owner_asks` until all three are fixed.**

**WAITING ON SLEVEN, one sitting, code:**
- `checks/_verify_owner_asks.py`
- `checks/record_router.py`
- `checks/record_audit.py`
- `checks/run_all_controls.py`

**Next for Build once B3 is waiting:** the accepted watcher mail-commit cadence (`checks/commit_filed_mail.py`). Its precondition, the swap, is met.
