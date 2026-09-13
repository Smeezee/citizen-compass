# Build update - check 6 no longer counts CURRENT-STATE as present state; proven, before and after recorded

**Code (Build), 2026-09-12, 12:55 CDT.** Architecture's approval: `2026-09-12_memo_build_check-6-is-approved-and-three-things-are-mine-to-fix.md`.

- **`checks/file_checks.py` (Code's file):** `PRESENT_STATE_DOCS` drops `docs/CURRENT-STATE.md` and the dead root `CURRENT-STATE.md`. BOOT.md is deliberately not added, and a comment says why.
- **`checks/_verify_document_checks.py`:** a new "quiet" case (demoted CURRENT-STATE and BOOT.md naming dead paths). **All 32 cases pass.**
- **Mutations, 3 of 3 caught:** each removed entry put back, and BOOT.md added. All restored byte-identical (`_needs_review/check6_scope_mutations.py`).
- **Real tree:**
  - before: 38 documents, 5 DEFECT
  - after: 37 documents, 4 DEFECT
  - Only the CURRENT-STATE line (10 dead paths) is gone. The other four are left for the record auditor, as ruled.
- **No deploy is needed** (no payload file changed). **Not committed.**

**Nothing is queued for Code.**
