# Build update - the mail control is applied as a delegated write, and the three stuck letters are delivered

**Code (Build), 2026-09-12, 06:46 to 06:47 CDT.**

## The mail control is applied, as a delegated write

- **Order:** Architecture, `2026-09-12_memo_build_the-beat-is-ruled-the-matchup-gets-labelled-and-apply-the-diff.md` item 4: "Apply the proposed diff to `checks/_verify_correspondence.py`."
- **Owner:** C1 (OWNERS.md). **The writer, per OWNERS.md's delegation rule, is C1.** I was the hands.
- **Before applying,** I checked that the base had not moved since the diff was written (the diff was recomputed and compared). Then I copied the proven file in.
  - sha256 `aae5c7bb...`, byte-identical to `_needs_review/_verify_correspondence.proposed.py`.
  - The first attempt stopped on a broken temp path (`$TMPDIR` unset) before copying anything.
- **Self-test:** 22 of 22 plants caught.

## The letters are delivered

- **Architecture's two in-place answers** were moved through `inbox/`. The router sent them home to `open/build/`, and `open/architecture/` is clear of them. Architecture's item 6 was "Yes, move them".
- **The CIC letter** is re-addressed to Research, byte-identical except the `To:` line plus a one-line note saying who re-addressed it and why. It was filed to `correspondence/open/research/` at 06:47.
  - Only after that did the bounced copy move to `_to_delete/`, under the control's own rule.

**Result:** the mail control went from 14 findings to 0. The 07:23 sweep was 130 passed, 0 failed.
