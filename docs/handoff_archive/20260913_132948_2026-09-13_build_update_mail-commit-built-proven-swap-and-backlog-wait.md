# Build update - the filed-mail commit is built and proven; the watcher swap and the 858-file backlog list wait on Sleven

**Code (Build), 2026-09-13. Clock read at 13:29:16.** Architecture's accepted cadence (section 2 of `..._three-architecture-rulings-...`).

**Built (all Code's, uncommitted):**
- **`checks/commit_filed_mail.py` (new).**
  - It reads the watcher's own log for every path filed under `correspondence/` or `docs/handoff_archive/`. A path counts when its LATEST filing is at least one beat old; it is taken where it sits NOW (by exact filename, and AMBIGUOUS is refused), and only if git sees it changed.
  - It imports `commit_guard.in_doc_set` and commits through the real pre-commit hook, as `Citizen Compass Watcher <watcher@local>` for author and committer. **It never pushes.**
  - **It refuses:**
    - a busy index
    - any path outside the doc set, which stops the whole batch
    - a guard refusal, which unstages exactly its own paths
    - more than 100 paths without `--approve <batch id>` (rule 5)
  - `--beat` keeps the hour. The receipt is `logs/mail_commit.json`.
- **`watcher-go/mail_commit.go` (new) and `ticker.go`:** the beat runs `commit_filed_mail.py --beat` after the fetch and BEFORE the uncommitted receipt. A failure is logged and stops nothing.
- **`watcher-go/mail_commit_test.go` (new).**

**Proof:**
- **Python self-test: 19 of 19,** in throwaway repositories with the REAL guard installed as the pre-commit hook and a bare remote.
- **Rule 12, Python: 14 of 14 mutants caught** on copies; the repo file is unchanged by hash.
- **Go:** `go vet` is clean and the full watcher suite passes.
  - **Rule 12, Go: 5 of 5 mutants caught,** in place, each restored and hash-checked byte-identical.
  - My first run had one mutant that did not apply (a CRLF anchor); I fixed the anchor and re-ran all five.
- **Real-tree dry run (13:24):**
  - **858 paths,** 0 outside the doc set, 0 ambiguous, 10 filed and gone, 1 waiting to settle
  - HEAD, the index and the receipt are unchanged
  - **By folder:** 322 `docs/handoff_archive`, 290 `correspondence/answered`, 90 open/build, 70 open/owner, 51 open/architecture, 23 open/design, 10 open/research, 2 open/audit
  - **The full list is `logs/mail_commit_backlog_dryrun.txt`:** batch `c0b7604720323000`, filed up to `2026-09-13 13:14:33`

**Candidate watcher:** `watcher-go/inbox_watcher_pending_20260913b.exe`, sha256 `1278201ccf697e8ab64f81855dfea5a20dca229c799daf7a58a3f636e0b22a00`, 5,950,976 bytes, gitignored. It replaces the live `f7166705...`.
- **Safe by construction:** after the swap, the hourly run refuses the backlog as `bulk` and commits nothing until it is approved.

**WAITING ON SLEVEN:**
1. **The watcher swap,** by the procedure on record.
2. **The backlog:** he sees the list (rule 5); on his word, a desk runs `--commit --until "2026-09-13 13:14:33" --approve c0b7604720323000`. If anything moved since then, it refuses, and a fresh list is shown.
3. **A code sitting, 8 paths:**
   - `checks/_verify_owner_asks.py`
   - `checks/record_router.py`
   - `checks/record_audit.py`
   - `checks/run_all_controls.py`
   - `checks/commit_filed_mail.py`
   - `watcher-go/ticker.go`
   - `watcher-go/mail_commit.go`
   - `watcher-go/mail_commit_test.go`
