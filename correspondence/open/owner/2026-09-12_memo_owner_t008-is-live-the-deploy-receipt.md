# Memo

To:      Owner
From:    Build
Subject: T-008 is live. The sweep went green on its second run tonight, the deploy went out, and here is the receipt of everything it carried.
Status:  Open

**This answers `2026-09-12_memo_build_the-sweep-has-not-run-since-your-fix-so-t008-is-still-not-out`, step 2.**

## THE GATE

- **The sweep:** 129 passed, 0 failed, 3 skipped, 0 not run. It ran alone from 01:18:47 to 01:56:45 CDT.
- **The deploy:** `scripts/deploy_testing.ps1`, **without the override.** It confirmed the receipt matched the exact payload (fingerprint 3932b69f857f7ac4).
- **Cloudflare version:** 4eac592f-8ef2-4cd4-8cbb-8ff0a9c852ab.

## THE RECEIPT - EVERY ENTRY THE DEPLOY CARRIED

**Cloudflare uploaded 3 changed files. The other 524 were already there.**

    loadout.html   T-008. The badge now reads "component data from Star Citizen's
                   game files" instead of claiming a verification that did not happen.
    next.html      Q58 +3: three CSS lengths on the front page's cards
                   (.spacer min-height 0, .at margin 1px, .pr margin 3px), and
                   the testing stamp's date.
    classic.html   the old front page. Its testing stamp now reads 2026-09-12.
                   The previous served copy was not kept, so I cannot prove the
                   stamp date is its only change. I say so rather than assume it.

**Nothing else landed in the payload since the last deploy.** No other file changed.

## CHECKED ON THE SERVED SITE, NOT ASSUMED

- **Every page Cloudflare now serves is byte-identical to what was built.** A model serves at its exact local size.
- **The T-008 badge is live.**
- **Notes, in a real browser at four widths:**
  - No card has text cut at its edge. That is 0 of 253 at every width, and the check proves it can catch a planted cut.
  - 16 notes are still shortened with "..." at desktop. That is expected: the three fixes do not change it, and the rest of that item is Architecture's.

**One correction of my own, filed with Architecture:** I had called the +3 "zero spill". The measurement behind that figure cannot be re-derived, so I withdrew it and replaced it with the check above, which states what it counts.

## THE SIX LETTERS AND THE THREE

- **The six are marked**, and both sweeps confirmed it.
- **I marked the three late arrivals on your "go".** I read that as the go on those three. The originals are set aside, if you meant otherwise.

*Build (Code), 2026-09-12.*
