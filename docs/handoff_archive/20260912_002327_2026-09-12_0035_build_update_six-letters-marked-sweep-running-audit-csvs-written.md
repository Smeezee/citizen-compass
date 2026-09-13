# Build update - the six letters are marked, the sweep is running alone, and the audit's five CSVs are on disk

**Code (Build), 2026-09-12, about 00:35 CDT.**

## 1. THE SIX LETTERS - DONE, ON ARCHITECTURE'S NAMED GO

The go is Architecture's ANSWERS block on
`correspondence/open/build/2026-09-11_memo_architecture_correction-it-is-six-letters-not-two-and-my-count-was-truncated.md`:
"GO ON ALL SIX", with the six named by path.

- I added `CLOSED:` above each closing paragraph as a direct edit, not an inbox re-drop. Each letter grew by 9 bytes (LF). I checked byte-identity around the marker on all six.
- The originals are aside in `_to_delete/closed_marker_20260912/`.
- Script: `_needs_review/mark_six_closed_20260912.py`. I ran it dry first, then with --apply. It refuses on a missing anchor, a doubled anchor or an existing marker.
- `checks/_verify_correspondence.py` run alone: **PASS**.

## 2. THE SWEEP IS RUNNING ALONE

It started about 00:33 CDT. Nothing else is running against the payload. Log: `_needs_review/sweep_20260912_solo.log`.

**If it is green, T-008 and the Q58 +3 get deployed and verified on the served site. If it is red, they do not go out, and the failures get named.**

## 3. OWNER'S AUDIT, PHASE ONE - IN FLIGHT, NOT YET REPORTED IN

Five CSVs are written in `claude/`, as `AUDIT-2026-09-12-*.csv`:

| CSV | rows |
|---|---|
| ship-inventory | 254 |
| missing-pictures | 6 |
| missing-models | 36 |
| model-capabilities | 256 |
| dimension-coverage | 253 |

The report is still being written. One measurement is being redone first: the bounding boxes. They came from raw accessor bounds, and 31 files carry node transforms, so a raw box is not the drawn size for those files. I am recomputing the boxes in world space, reading only the files, before any size gets reported.

The audit is read-only against the project. Nothing in it has been corrected along the way.

## 4. MAIL READ THIS TURN

Four answers came back at 00:14:

- The six-letter go.
- The superseded two-letter one.
- Q63.8A: Research has been ordered, and I have stopped chasing it.
- Keybinds.

Three mail repairs are ordered behind the front page:

- the From: parenthetical
- clearing a returned answer from the sender's tray (the duplicate)
- refusing, at filing time, a Closed or Done memo that has no marker.
