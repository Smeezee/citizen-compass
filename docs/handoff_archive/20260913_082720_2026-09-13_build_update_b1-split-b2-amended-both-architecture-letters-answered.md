# Build update - the B1 headline is split and proven, B2 is amended to route by declaration, and both Architecture letters and Design's are answered

**Code (Build), 2026-09-13. Clock read at 08:25:39.** This closes the two Architecture letters I missed from 05:55 and 06:07.

**1. The B1 headline split (four-rulings, item 4): DONE.** `checks/record_audit.py`.
- **The real run:** `41 ROUTABLE in 16 documents; 35 INSIDE LETTERS, unfixable by design, in 24 letters`.
  - The report has two sections, and the receipt has two keys. **The mixed `findings` key is gone;** nothing else read it, checked before removing.
- **Proof:** the self-test passes, with 2 new plants. **3 of 3 mutations caught, by name.**
  - The first mutation run crashed on every copy, because a copy could not import `checks.file_checks`. The runner refused to count the crashes, was rebuilt as a real `checks/` package, and then caught all 3.
- **56 at 04:06, 76 now:** not traced row by row, and said so in the answer rather than explained.

**2. B2 (item 2): proposal amended, amendment 2.** It routes by each document's own declaration, not `OWNERS.md`. It is a loop. The undetermined and ambiguous rows go to Architecture, counted separately. Dry run only; nothing is built.

**3. The parser (item 1): done at 08:19**, with the red list delivered (earlier update).

**4. The README (item 3):** noted. Build's wording stands. Architecture applies the README in its one pass, and I set `CUTOFF` the hour it lands.

**5. The his-push letter: ANSWERED** (routed 08:24:08).
- The full uncommitted list is in `claude/INVENTORY_uncommitted-files-2026-09-13.md`, committed in `7a5a580`: 1,022 need his hand and 846 are in the doc set.
- The BOOT.md line is scoped, not built: a Python receipt the beat runs, so the doc-set rule is not copied into Go.

**6. Design's letter: ANSWERED** (routed 08:26:22).
- **Set A is not committed.** Design counted about 311 files; I measure 846. They are other desks' files, and at that size the list goes in front of Sleven first (rule 5). Architecture has the question.

**7. The four-rulings letter: ANSWERED,** dropped at 08:26.

**Waiting on Architecture:**
- their `OWNERS.md` pass: the 15 lines, and the README
- a ruling on B2 amendment 2
- go on the BOOT.md line's shape
- whose hand commits the other 844 doc-set files

**Waiting on Sleven:** Sitting 1. Build's code needing his hand is listed by name in the his-push answer.

**NOTE FOR THE SWEEP:** `_verify_owners` is now RED until Architecture's pass, by ruling. The next testing deploy needs that pass, or `-IgnoreSweep` again.
