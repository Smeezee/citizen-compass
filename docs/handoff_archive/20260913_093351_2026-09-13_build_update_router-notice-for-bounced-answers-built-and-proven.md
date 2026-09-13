# Build update - a bounced answer now tells the desk that wrote it: built and proven, NOT live

**Code (Build), 2026-09-13. Clock read at 09:33:25.** Architecture's order (`..._boot-line-go-the-844-are-not-a-chore-and-a-bounced-answer-is-invisible.md`, item 3).

**What was built:** `watcher-go/memo_bounce_notice.go` (new) and one call in `memo.go`.
- **When the router refuses an ANSWER,** it drops a notice into the tray of the desk that wrote the answer. **That is the letter's `To:` desk.** The letter's `From:` is the unresolvable name that caused the bounce, so it cannot be the address for the notice either.
- **The notice is itself a memo:** To the answering desk, `From: Build (router)`, `Status: Open`. It names the letter, where it now sits in `_needs_review/`, and the router's reason.
- **Nothing about routing changes.** The answer still lands in `_needs_review/` exactly as before. The notice is written only AFTER that move succeeds, and a notice that cannot be written is recorded in the router's note, not a failed route.
- **No notice** for a deliverable answer or a refused open letter. If `To:` is not a desk either, the note says nobody could be told. **A re-dropped bounce is told once, and the notice is never overwritten.**
- **One guard was removed before testing,** because no test could make it fail: the only refusal an answered letter can reach is the unknown sender (rule 12).

**Proof:**
- `go vet` is clean. **The whole watcher suite passes,** including the existing unknown-sender refusal test.
- **6 new tests through the real router, in both directions:**
  - a refused answer gives exactly one notice, in the answering desk's tray, and the notice routes there itself
  - a deliverable answer gives none
  - an open letter with an odd `From:` gives none
  - `To:` not a desk means nobody told
  - a re-drop is told once, and a desk's mark on the notice survives
  - a refused non-answer mentions no notice
- **Rule 12: 5 of 5 mutations caught,** each in place, restored, and hash-checked.

**NOT LIVE. The next step is ONE watcher swap for both changes** (this, and the BOOT.md uncommitted line). It is Sleven's word, after proof, and it will be asked once, with the candidate binary's hash.
