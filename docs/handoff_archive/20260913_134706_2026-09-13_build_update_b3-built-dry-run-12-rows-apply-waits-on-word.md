# Build update - B3 (record_repair.py) is built and proven; the real dry run shows 12 HISTORY rows; nothing is applied until a `B3-apply` word; swap and backlog still HELD

**Code (Build), 2026-09-13. Clock read at 13:46:41.** Architecture's four rulings; Sleven's "go ... dry-run first".

**Built (Code's, uncommitted):**
- **`checks/record_repair.py` (new).**
  - It reads answered router letters: only letters with a `Router-key:` above `ANSWERS:` and `Status: Answered`. Each reply must be in one of the three ruled forms.
  - **It imports B1's `LEDGER`/`LEDGER_ROW` and `_verify_owners.parse_owners`,** so there is no second copy of either.
  - **HISTORY** appends a ledger row.
  - **MOVED** repoints a citation, and is refused when:
    - the new path is not on disk
    - the source is a letter, CLAUDE.md or OWNERS.md
    - the source's OWNERS owner is not the answering desk
    - the token is absent
  - **`--retire`** removes a row and leaves a `RETIRED` line, so the old reply is never re-added.
  - **Refused, and named:**
    - NOT SENT, MALFORMED and AMBIGUOUS replies (byte-identical twin letters count as one reply)
    - RESOLVED: the cited path exists now, so a row would only be stale
  - **`--apply ID` needs two things:** the batch computed now must hash to ID, AND a letter to Build from Architecture or Owner must carry `B3-apply: <ID>`. The receipt `logs/record_repair.json` names that letter.
- **`checks/record_router.py`:** the letter's reply instructions are now B3's three exact forms (ruling 1).

**Proof:**
- **B3 self-test: 27 of 27,** in a throwaway tree. The proof of an apply is **B1's own `audit()`** counting the row dispositioned, and reporting the gap again after a retire.
- **Rule 12: 16 of 16 mutants caught by a named case.**
  - The first run had 2 survivors, both weaknesses in my test: `sorted(os.walk())` walked the whole tree before the prune could act; and there was no case where a valid word exists but `--apply` names another ID.
  - Both are fixed. A crash is not counted as a catch.
- **B2 self-test: 19 of 19.** Its new case 19 fails when one form is dropped from the instructions.

**The real dry run (13:46):**
- **12 HISTORY rows,** all from Build's own answered letter
- **1 RESOLVED:** `checks/commit_filed_mail.py` exists now, so the "future" reply is not added
- 0 MOVED, and 0 NOT SENT, MALFORMED or AMBIGUOUS
- **BATCH-ID `0b183509c0df0794`**
- **Nothing was written:** no ledger and no receipt.

**NOT DONE, and not Build's to do:** `OWNERS.md` has no line for `claude/RECORD-AUDIT-DISPOSITIONS.md`. Architecture ruled it is Code's, but the file is C1's, so a memo went to Architecture.

**HELD by Sleven:** the watcher swap (`inbox_watcher_pending_20260913b.exe`) and the 858-file backlog. Neither is touched.

**Uncommitted Build code, 9 paths (his 8, plus `checks/record_repair.py`):**
- `checks/_verify_owner_asks.py`
- `checks/record_router.py`
- `checks/record_audit.py`
- `checks/run_all_controls.py`
- `checks/commit_filed_mail.py`
- `checks/record_repair.py`
- `watcher-go/ticker.go`
- `watcher-go/mail_commit.go`
- `watcher-go/mail_commit_test.go`
