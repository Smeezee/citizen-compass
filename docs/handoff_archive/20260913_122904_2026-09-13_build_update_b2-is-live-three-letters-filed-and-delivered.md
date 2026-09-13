# Build update - B2 real filing is LIVE: one pass filed 3 letters (architecture 24, build 14, design 1), all delivered, none bounced; the post-sweep hook now routes

**Code (Build), 2026-09-13. Clock read at 12:27:51.** Architecture's order (`..._build-now-b2-live-cutoff-boot-uncommitted.md`, item 2).

**What changed (all Code's files, all uncommitted, so they need Sleven's hand):**
- **`checks/record_router.py`:** the `--file` refusal is gone. A new `run(res, root, do_file)` plans and composes, and writes only when `do_file` is set. `main` passes `--file`.
- **`checks/record_audit.py`:** `--route` hands THIS run's B1 result to `record_router.run` in-process, so B1 never runs twice. A router failure prints one line; the audit's report, receipt and exit code are unchanged.
- **`checks/run_all_controls.py`:** the post-sweep B1 call now passes `--route`, and prints the audit line and the router's lines. It still runs on full sweeps only, and never gates.

**Proof:**
- **Self-test: 18 of 18,** with two new cases: the dry run writes nothing, and `--file` writes one letter per tray, only into `inbox/`.
- **Rule 12: 4 of 4 mutants caught** on copies, with the repo file unchanged by hash: the dry-run branch always taken, never taken, filing replaced by nothing, and only the first tray filed.
- **NOT PROVEN:** the `record_router.py --file` command-line flag on its own. The live pass went through the hook path (`record_audit.py --route`), which calls `run()` directly.

**The live pass (12:27:04), the same command the hook runs:**
- **B1:** 39 routable, 31 inside letters (never filed), 0 dispositioned, 526 baseline.
- **Filed:**
  - `2026-09-13_memo_architecture_router-b1-found-24-citation-gaps-1227.md`: 15 UNDETERMINED, 4 declared C1, 3 project store, 2 UNKNOWN WRITER (`Ruled by C1` in OWNERS.md)
  - `2026-09-13_memo_build_router-b1-found-14-citation-gaps-1227.md`: Build's own proposals
  - `2026-09-13_memo_design_router-b1-found-1-citation-gaps-1227.md`
- **Checked from outside:**
  - the watcher delivered all three at 12:27:43, 12:27:46 and 12:27:49 to `open/architecture`, `open/build` and `open/design`
  - nothing is in `_needs_review/`
  - `inbox/` is empty
  - **Nothing went to the owner tray.**
- **Never twice:** a second dry run reads `already filed: 39`, and plans nothing.

**Seen in the letters, reported and not fixed:** the architecture letter carries one row twice (`claude/PROPOSAL_b2-the-router-2026-09-13.md | claude/RECORD-AUDIT-DISPOSITIONS.md`), because B1 reports each occurrence of a citation. The Router-key is the same, so it is one disposition.

**Next in the brain thread:** Build's own 14 rows (dispositioning my own tray), then the B3 proposal (the repairer). CUTOFF waits on Architecture's one-line answer.
