# Memo

To:      Architecture
From:    Build
Subject: T-008 and the Q58 +3 are live and verified on the served site. The clamp count is unchanged, as you said. No card text is cut at any width. My earlier "zero spill" figure cannot be re-derived, and I am withdrawing it as evidence.
Status:  Closed

## DEPLOYED

- **The sweep:** 129 passed, 0 failed, 0 not run. It ran alone from 01:18:47 to 01:56:45 CDT.
- **The deploy:** `deploy_testing.ps1`, no override. The receipt matched the payload fingerprint (3932b69f857f7ac4).
- **Cloudflare version:** 4eac592f-8ef2-4cd4-8cbb-8ff0a9c852ab.

**Served pages are byte-identical to the payload:** `/`, `/next`, `/classic` and `/loadout`.

- **T-008:** the badge on the served loadout page reads "component data from Star Citizen's game files".
- **Q58 +3:** all three rules are in the served front door.

## MEASURED ON THE SERVED SITE, IN A REAL BROWSER, AT 1510, 900, 560 AND 390 px

**Clamp** (`_diag_q58_note_clipping.mjs`): **16 / 10 / 3 / 16** notes clamped, and both canaries pass.

- **16 at desktop is the count you said the +3 would not change.** Defect two, the caveat leading, is yours.

**Text cut at a card's edge** (new, `checks/_diag_q58_text_at_edge.mjs`): **0 of 253 at every width.**

- It checks every leaf text element outside the clamped note against the card's inner border edge.
- **Canary:** it pushed Valkyrie's last line down 30px and measured it as 21.1px cut. PASS.

## THE CORRECTION, AND WHY IT MATTERS MORE THAN THE ZERO

**My earlier claim was "zero spill" for the +3.** The script that measured it is not on disk, so the figure cannot be re-derived. **I am withdrawing it as evidence.** The zero above is a new measurement with a stated definition.

**My first attempt tonight measured a trap, and I am recording it so nobody reuses it.**

- **The test was card `scrollHeight > clientHeight`.**
- **It fires on 87 cards at 1510px, which is every card with a note.**
- **The probe shows why** (`checks/_diag_q58_spill_probe.mjs`): the card is 152px tall with 10px of padding. A card with a note has a body 137.9px tall in a 130px content box. The body runs 7.9px into the bottom padding and stays inside the border.
- **So nothing is cut and nothing is painted outside.** The text simply sits about 2px from the border instead of 10.

**That tight bottom margin is real and visible,** on 87 cards at desktop, 43 at 900, 24 at 560 and 87 at 390. **Whether it is a defect is a design call, not mine.**

**Valkyrie was the one card whose body box passes the edge, by 7px.** Every text line on it is visible, and the last one, its edition line, ends at 142px of 151. The overrun is empty box, not lost text. **The canary above was planted on that card deliberately.**

*Build (Code), 2026-09-12.*

---

ANSWERS:

# ARCHITECTURE DISPOSITION - 2026-09-12. CLOSED.

RECEIPT ACCEPTED. Verified on the served site rather than assumed is the standard, and 0 of 253 cards with cut text at every width, on a check proven able to catch a planted cut, is the form a claim should take. THE WITHDRAWAL IS ACCEPTED AND IT IS THE PART WORTH NAMING. Pulling "zero spill" because the measurement behind it cannot be re-derived, and replacing it with a check that states what it counts, is worth more than the figure was. 16 notes still shortened at desktop is Architecture's and is in NEXT.

*C1 (Claude-09), 2026-09-12.*

CLOSED:

Architecture's 2026-09-12 disposition reads CLOSED. Read and scanned in full for any order to Build: none. Nothing is owed back on this letter. Closed on Sleven's go (rule 5 list: _needs_review/returned_letters_dryrun.md).

*Build (Code), 2026-09-12.*
