# PROPOSAL - the echo-salvage zip receipt (nothing is built)

    from      Build (Code), 2026-09-13 08:11
    for       Owner, who asked, and Architecture, who queued it as Build's item 7
    order     2026-09-12_memo_build_optional-echo-salvage-zip-receipt-in-design-imports
    status    PROPOSAL, because the letter said "proposal first if non-trivial" and one
              part of it is not trivial. No swap until proven, as ordered.

## THE ASK

**When a dropped zip's name starts with `echo-salvage_`,** after it is extracted and sorted, **also put the original zip, or a receipt for it, in `design/echo-imports/_drop/`,** so Design can find the pack in one place without digging through `_zip_archive/`.

## WHAT THE WATCHER DOES TODAY (read, not assumed)

`watcher-go/zip.go`, `handleZip`:
1. extracts every entry to a temporary folder
2. routes each file through `classifyAndRoute`, logging each destination
3. archives the original zip untouched in `_zip_archive/` (gitignored)

**Every fact a receipt needs is already known at the end of that function:** each entry's destination or failure, and the archive path. **There is no zip test in `watcher-go` today.**

## WHAT I WOULD BUILD

**A receipt, not a copy.** A file named `design/echo-imports/_drop/<zip name>.receipt.md`, containing:

    the zip's name, size and sha256
    where the original was archived        _zip_archive/<name>
    every entry -> where it was filed       (or FAILED, with the reason)
    counts: sorted, failed

- **Why a receipt:** the zip already lives, once, in `_zip_archive/`. **A copy would be a second home for the same bytes**, and this project has paid for two-places three times this week. The receipt points at the one copy and says where every memo inside it went, which is the thing Design actually has to dig for today. **If you want the zip itself there, it is one line to change.**
- **The prefix is matched exactly:** `echo-salvage_`, as Echo's own instructions spell it (lowercase). A zip not named that way gets no receipt (rule 17).
- **It never changes routing.** The receipt is written after everything is filed. If it cannot be written, the watcher logs one line, and every memo still lands where it would have.
- **The watcher is its only writer** (rule 14). It writes nowhere else under `design/`.

## THE ONE PART THAT IS NOT TRIVIAL

**`design/echo-imports/README.md` says `_drop/` is for when "someone manually parks a zip outside the watcher flow".** Receipts written there by the watcher change what that folder means, and the README would then be wrong. **Nobody owns `design/echo-imports/` in `OWNERS.md`.** So either:

- **(a)** receipts go in `_drop/`, as your letter says, **and the README gains one line** saying so; or
- **(b)** receipts go in a sibling folder, `design/echo-imports/_receipts/`, and `_drop/` keeps its meaning.

**My recommendation: (a).** It is what you asked for, one line keeps the README true, and a second folder is one more place to look.

## PROOF, BEFORE ANY SWAP

**A new `watcher-go/zip_receipt_test.go`** that builds real zips in a temporary tree:
1. An `echo-salvage_` zip with two memos and one unrecognised file writes one receipt. The receipt names both memos' trays, the unrecognised file's `_needs_review/` path, and the archive path.
2. A zip named any other way writes no receipt.
3. `Echo-salvage_...` (a capital E) writes no receipt. The prefix is exact.
4. Receipt folder unwritable: every file still routes, and exactly one log line says so.
5. The same zip dropped twice: the second receipt does not overwrite the first; it gets a new name.

**Rule 12:** a mutation for each assertion. **Then the swap needs your word,** as your letter said.

**The size:** about 50 lines in `zip.go`, plus the test.

*Build (Code), 2026-09-13.*
