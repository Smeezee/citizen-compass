# Memo

To:      Owner
From:    Build
Subject: The sweep ran and is red again on the same control, on three different letters filed into answered/ fourteen minutes after it started. Nothing deployed, no override.
Status:  Open

**This answers `2026-09-12_memo_build_the-sweep-has-not-run-since-your-fix-so-t008-is-still-not-out`. It is your step 3: red on the same control, so I have stopped, and this is what it says now.**

## YOUR FOUR POINTS

**1. The sweep has run.** It ran alone, from 00:22:31 to 01:06:13 CDT (2,618 s), and the receipt was written at 01:06:13. **Result: 128 passed, 1 failed (`_verify_correspondence.py`), 3 skipped, 0 not run.**

**2. Not deployed.** The sweep is red, so T-008 and the Q58 +3 are still built and still sitting in the payload.

**3. What the control says now.** It is not the six letters. **They pass.** It is three new letters:

    answered/2026-09-08_20260908_memo_audit-to-design_ten-pairs-for-angles-md-if-you-want-them.md
    answered/2026-09-08_20260908_memo_audit-to-design_the-lens-audit-five-answers-and-one-that-breaks-the-central-claim.md
    answered/2026-09-08_20260908_memo_audit-to-design_your-open-question-answered-the-collector-already-does-half-of-this.md

- **All three were filed into `answered/` at 00:36:50**, fourteen minutes after the sweep started. I had run the control alone at 00:21, before starting the sweep, and it passed. **The sweep did not miss them. They did not exist yet.**
- **Each one ends with a bare `CLOSED.`** It has a full stop where the marker has a colon, and nothing under it. The control wants `CLOSED:` with a record under it, so it is right to go red.

**4. The six cleared letters are MARKED, and verified.**

- `CLOSED:` sits above each closing paragraph.
- I checked every byte either side of the marker against the original.
- The originals are aside in `_to_delete/closed_marker_20260912/`.
- **The sweep confirms it independently: none of the six is in its findings.**

## WHAT UNBLOCKS IT

**These are Audit-to-Design letters, and neither desk asked me to mark them.** Under Architecture's own rule, marking them is "a file I noticed on the way", which is not delegation. **I have asked Architecture for a named go on the three, the same form as the six.**

- **A word from you does the same thing.** One minute to mark them.
- Then the full sweep, about 44 minutes, because the deploy gate reads the full receipt.
- Then the deploy, with a receipt that names every entry it carried, per the grouped-deploy ruling.

**The class will keep doing this until the filing-time refusal is built.** Every close filed without a marker while a sweep runs turns the next deploy red. That refusal is one of the three mail repairs Architecture ordered behind the front page.

- **I recommend moving it ahead of the front page.** Tonight it is the thing standing in the front page's way.
- **Until it exists, every sweep can be overtaken by a letter filed while it runs.**

## ALSO ARRIVED WHILE IT RAN, NOT ACTED ON, because you said nothing else changes

- **The roles file is now on disk** (`claude/CIC_rsi-official-ship-roles-2026-09-12.md`, 72,130 bytes). Q63.8A lists 1 and 2 can run, and they are next after the deploy.
- **Audit filed a finding on `panel_dismiss_eye`:** its docstring and its code describe different checks. It is queued.

*Build (Code), 2026-09-12.*
