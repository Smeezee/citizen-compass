# Build update - B1's citation fix and the beat's isolation, both proven; four letters answered

**Code (Build), 2026-09-12. Clock read at 19:43:19.**

- **The B1 citation fix** (`checks/record_audit.py`):
  - A citation into `correspondence/` resolves by exact filename wherever the mail system filed the letter. Two places is AMBIGUOUS.
  - A non-letter citing into a tray is listed as TRANSIENT.
  - **Self-test passes, and 11 of 11 mutations are caught.**
  - **Real tree:** 38 resolved through the mail system, 12 transient, 57 findings, 4.1 s. Tonight's moved letters are no longer dead, and a never-existing filename still is.
- **Beat isolation, proven by breaking it:**
  - A new Go test hangs the fetch, and the mail path's BOOT.md write still finishes in 0.1 s. The lock-across-fetch mutation is caught (6 of 6).
  - A real fetch with the network refused recorded `did-not-look` in 2.1 s, into temp files only.
  - **No production change, so no swap.**
- **Credential check, read-only:** no GitHub credential that can comment on an issue was found (gh signed out, no token variables, no `.env` key).
- **Commits:** Sleven chose, directly, to commit `skills/` and CLAUDE.md himself and push main, publishing `183a239`. The guard refuses both to Code.
- **Answered:** the three-orders letter (CIC already done at 06:47), the withdrawal (nothing is waiting to deploy), and both commit letters.

**Next in the queue:** close the returned letters (a rule 5 dry-run list first), then the pre-push guard proposal, the status-line refusal, and the echo zip.
