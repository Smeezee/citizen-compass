# Build update - all three mail repairs are built into one binary; the swap waits on Owner's go

**Code (Build), 2026-09-12. The clock read 02:37:04 CDT at the build.**

## Done, in `watcher-go/memo.go`

- **The close refusal:** a Closed or Done letter without a record is refused at filing.
- **The signature:** a `(...)` on To:/From: is taken as a signature, kept, and not used as the address.
- **The clear-out:** a byte-identical returned answer can be cleared from its tray.

## Proof

- `go test ./...` passes and vet is clean.
- **Mutation:** disabling each repair fails its own tests (4, 3 and 1). `memo.go` was restored byte-identical.
- Three existing tests were updated, and each change is commented.

## Binary

- **The new one:** `watcher-go/inbox_watcher_pending_20260912b.exe`, sha256 1dca1fde9aca383b..., console.
- **The superseded one-repair build** is moved to `_to_delete/inbox_watcher_pending_20260912.exe.superseded-by-20260912b`.
- **The running watcher is unchanged:** PID 19112, sha256 f9d983b2..., exactly one process.

## Memos

- **To Owner:** a follow-up to the swap request, naming the new binary and withdrawing the old one.
- **To Architecture:** the details of all three repairs.

## Waiting on

- Owner's go for the swap.
- The solo sweep for the zero-dimension fix, started 02:25 CDT. Deploy if it is green.
