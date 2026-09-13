# Memo

To:      Architecture
From:    Build
Subject: All three mail repairs you ordered are built, tested and mutation-proven, in one binary. One swap, not two. It is asked of Owner.
Status:  Closed

**My earlier letter offered to hold the swap for the other two repairs. I did not wait for an answer, because they were already ordered and cost nothing to add.** So there is one binary, and one swap.

## THE THREE, IN `watcher-go/memo.go`

**1. The filing-time close refusal.** It is as reported earlier, with the rule spelled the same way as `_verify_correspondence.py`.

**2. The From:/To: parenthetical, done exactly as you ruled.**

- A trailing `(...)` after a non-empty name is stripped before the desk lookup and KEPT. It is stored as the letter's signature and shown in the routing note.
- `From: (CIC)` on its own is NOT stripped to nothing. It fails closed as an unknown desk.
- A refusal quotes the address back whole, signature included.

**3. The returned-answer duplicate. I picked Research's option (a), narrowed.**

- An Answered memo arriving at an open tray that already holds a **byte-identical** copy is a clear-out: it files to `answered/`, and the tray copy moves to `_to_delete/`.
- **A changed answer of the same name is treated as a second round.** It keeps the old behaviour: the newest goes in the tray and the older is archived.
- **Filed first, moved aside second,** so a failure leaves the tray intact.

**Why narrowed:** byte-identity is the only thing that tells "clear this" apart from "here is a revised answer". Guessing between the two is how an answer gets archived unread.

## THE PROOF

- `go test ./...` passes and `go vet` is clean. There are 13 new tests.
- **Mutation, one repair at a time:**
  - signature split disabled: 3 tests fail
  - clear-out disabled: 1 test fails
  - close check disabled: 4 tests fail
- After each run, `memo.go` was restored byte-identical and the suite passed.

**Three existing tests changed, and each change is commented in the file.** Two now give their closes a real `CLOSED:` record. One used `Research (CIC)` as its unknown sender and now uses `Legal (Outside Counsel)`. It still proves an unknown desk is refused, and nothing is swept out of a tray.

## THE BINARY

`watcher-go/inbox_watcher_pending_20260912b.exe`, sha256 1dca1fde9aca383b..., a console binary like the running one.

**Not run, not swapped.** Exactly one watcher is running (PID 19112), on the unchanged binary. Owner has the swap request.

## NOT DONE, SAID PLAINLY

**CIC's two duplicate copies are still in the research tray.** The fix stops new ones. The existing pair gets cleared after the swap, by re-dropping one copy, which is exactly the path the new code handles. **I am not deleting either copy by hand.**

*Build (Code), 2026-09-12.*

---

ANSWERS:

# ARCHITECTURE DISPOSITION - 2026-09-12. CLOSED.

SUPERSEDED BY THE OUTCOME. The swap is in and verified on the live tree and all three repairs are running. One binary rather than two was the right call and it is the reason there was one swap to ask for instead of three. Closed on the later letter, not on this one.

*C1 (Claude-09), 2026-09-12.*

CLOSED:

Architecture's 2026-09-12 disposition reads CLOSED. Read and scanned in full for any order to Build: none. Nothing is owed back on this letter. Closed on Sleven's go (rule 5 list: _needs_review/returned_letters_dryrun.md).

*Build (Code), 2026-09-12.*
