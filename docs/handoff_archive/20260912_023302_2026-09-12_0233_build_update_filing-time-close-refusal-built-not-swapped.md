# Build update - the filing-time refusal of an unmarked close is built and tested, and NOT swapped in

**Code (Build), 2026-09-12 02:32 CDT.** This is the first of the three mail repairs Architecture ordered ("a memo arriving with `Status: Closed` or `Done` and no disposition marker is refused to `_needs_review/` with the reason").

## THE CHANGE - `watcher-go/memo.go`

`classifyMemo` now refuses a Closed or Done letter that has neither an `ANSWERS:` nor a `CLOSED:` line with 20 or more characters under it.

- **The refusal reuses the existing path to `_needs_review/`,** with the reason attached, the same way an unknown desk is refused.
- **The rule is spelled like `checks/_verify_correspondence.py`'s:** the same two markers, the same optional bold, the same threshold. The router and the control cannot disagree about what a record is.
- **Answered and Open letters are not touched.**

## THE PROOF

- **`go test ./...` passes and `go vet` is clean.**
- **Seven new tests** (`memo_closed_record_test.go`). The first one is tonight's exact case: a closing round that ends in a bare `CLOSED.`.
- **Mutation (rule 12):** with `closedRecord` forced to say ok, all 4 refusal tests FAIL. After the restore, `memo.go` is byte-identical and they pass.
- **Two existing routing tests encoded the old behaviour** (a close with no record filed to `answered/`). Their Closed and Done cases now carry a real record. Their routing assertions are unchanged.

## THE BINARY - BUILT, NOT RUN, NOT SWAPPED

    watcher-go/inbox_watcher_pending_20260912.exe   5,773,824 bytes
    sha256 1594d21deb4d3bd1...   PE subsystem 3 (console), same as the running copy

- **The running copy is `inbox_watcher.exe` (sha256 f9d983b2...).** It is byte-identical to `inbox_watcher_pending_20260910.exe`.
- **Going by file times, the only sources changed since that binary are my three files.** So the new binary should differ from the running one by this refusal only. This is an inference from modification times, not a rebuild comparison.
- **I did not run it.** Running it would start a second watcher process on one inbox.

## ONE FACT FOR THE RECORD, NOT A REQUEST

**`watcher-go/memo.go` and most of the memo tests are untracked in git.** The router's source exists only in the working tree. Committing it is Sleven's call.

## WAITING ON

**A go for the swap.** The last swap had its own named approval ("STEP A APPROVED - swap the watcher. Then stop."). I am asking for this one the same way, and not assuming it.

## STILL IN FLIGHT

The solo sweep for the zero-dimension fix, started at 02:25 CDT.
