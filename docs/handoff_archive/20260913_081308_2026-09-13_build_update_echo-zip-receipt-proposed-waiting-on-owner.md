# Build update - the echo-salvage zip receipt is proposed, not built; one decision is with Sleven

**Code (Build), 2026-09-13. Clock read at 08:11:37.** Queue item 7, Owner's optional letter. **Proposal first, because one part is not trivial.**

- **The proposal:** `claude/PROPOSAL_the-echo-zip-receipt-2026-09-13.md`. Scoped read-only from `watcher-go/zip.go`'s `handleZip`, which already knows every entry's destination and the archive path.
- **The recommendation:**
  - **A receipt, not a copy,** at `design/echo-imports/_drop/<zip>.receipt.md`. It names where the zip was archived and where every memo inside it went. The zip itself already lives once in `_zip_archive/`.
  - **The prefix is matched exactly** (`echo-salvage_`).
  - **It never changes routing,** and the watcher is its only writer.
- **The part that is not trivial:** the folder's README says `_drop/` is for zips parked by hand. Receipts there change its meaning, and nobody owns `design/echo-imports/`. I recommend receipts in `_drop/` plus one README line.
- **Proof plan:** a new `watcher-go/zip_receipt_test.go` with five cases and a mutation for each. **There is no zip test today.** The swap needs Sleven's word after that proof.
- **Answered through `inbox/`** to Owner's letter. **The one decision:** a receipt in `_drop/` plus one README line, yes or no?

**Stopping.** Nothing else is on Build's queue that is not waiting on Architecture or Sleven.
