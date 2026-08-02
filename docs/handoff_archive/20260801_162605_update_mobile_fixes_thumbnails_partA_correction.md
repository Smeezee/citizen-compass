# Mobile fixes, ship thumbnails, and a correction to the Part A report — 2026-08-01

Cowork session. Testing area only. No repo code touched, nothing committed.

## Correction — Part A: nobody stopped the Python watcher

The Part A report concluded correctly that only the Go watcher now responds, and was right to distinguish "the condition is satisfied" from "I performed the action." But it then guessed the process was *"most likely stopped by whoever filed `update_go_migration_verified_two_writers_live.md` at 14:56:41."*

**That was the Cowork session, and it stopped nothing.** It wrote one file into `inbox/` and took no action against any process.

So the accurate state is: `inbox_watcher.py` exited on its own, or was closed by something outside anyone's record, between its last write at 14:56:16 and the check at 15:59. **Nothing deliberately stopped it, and what started it is still unknown.**

Consequence: it is not safely retired, it is merely absent. Whatever launched it once can launch it again — most likely a terminal or editor session that has since closed. Before Part C deletes `generate_handoff.py`, someone should establish what started it, or accept that a future restart will crash on `ImportError` rather than fail cleanly.

Do not record this as "stray watcher stopped." Record it as "stray watcher no longer running; cause of both start and stop unestablished."

## Mobile — four defects found and fixed

Tested at 390×844, 412×915 and 820×1180 against the deploy build. All four would have been hit by reviewers on phones.

1. **130% default text was wrong on a phone.** On a 390px screen the header consumed the entire first viewport — a reviewer would scroll past a wall of title before seeing a single ship row. Default is now 100% below 700px wide, unchanged at 130% above it. Applied only when the visitor has no saved preference; anyone who has set their own keeps it.
2. **The DISPLAY tab covered the "Patch Notes" link.** A vertical tab pinned to the right edge works on a monitor and lands on content at phone width. Both tabs are now horizontal pills along the bottom below 900px.
3. **`#backToTop` and the FEEDBACK pill overlapped** — measured, literally on top of each other. Tapping one could hit the other.
4. **`.trademark-bar` is sticky**, so both pills sat permanently on the legal text.

The bottom edge now has four assigned lanes: back-to-top at 150px, trademark bar at 58px, pills at 10px, plus 64px body padding so the end of the page clears them. Verified with an all-pairs bounding-box collision check at 390px — zero overlaps. Desktop and tablet unchanged.

## Ship thumbnails — the stage is no longer blank while a model loads

The ship detail view showed an empty stage for the whole model download. On a phone with a 2 MB Draco model that reads as broken rather than loading.

All 241 `sc-ships/*/image.webp` files were resized **on the Windows machine** (PIL 12.2.0 is present) rather than moved through the bridge: 560px wide, WebP quality 78. **118 MB → 4.5 MB**, roughly 19 KB each. Written to `testing/_deploy/images/`, covered by the existing `testing/_deploy/` gitignore rule — confirmed with `git check-ignore`.

The layer now shows the photo immediately and cross-fades it out when the model finishes. A ship with no photo hides the element rather than showing a broken-image icon — verified against a ship with no thumbnail present.

Deploy folder: 344 MB → 349 MB. The images cost almost nothing.

Helper script left at `testing/_tools/mk_thumbs.py` — resumable, skips outputs newer than their source, takes a start index and count so it can run in slices.

**One build-ordering bug worth recording:** the first attempt inserted the filename-safety helper into the build script *before* the block it targeted was emitted, so the page threw `CC_SAFE is not defined` at runtime. Caught by exercising the actual page, not by reading the diff. A patch that applies cleanly to a build script is not evidence that the output works.

## Standing instruction recorded

Sleven asked that operational detail of this kind go to the handoff and memory rather than into chat responses. Chat replies should be short and action-oriented; the record carries the detail. Noted here and written to the Cowork session's memory.
