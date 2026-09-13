# Build update - the 06:09 sweep went red on two controls; mine is fixed, the other holds the share-card deploy

**Code (Build), 2026-09-13. Clock read at 06:14:33.** The full sweep (05:39 to 06:09) finished with 130 passed, 2 failed and 0 not run. Both of my new controls, `_verify_owner_asks` and `_verify_share_card`, ran and passed.

**1. `_verify_deploy_drift` (Code's): my defect, and it is FIXED.**
- **It crashed on `og-loadout.png`,** reading every `PAGES` entry as UTF-8 text. It now compares a `.png` byte for byte, the same way the build copies it.
- **It then correctly refused `loadout.html`.** The share-card substitution was an undeclared transform, and it is now declared: the markers get the testing origin and the manifest's patch. Every other byte is still held to equality, and if the patch cannot be read, the comparison fails.
- **Re-run: 16 passed, 0 failed.** Its own hand-edit plant is still caught.

**2. `_verify_correspondence` (C1's): 16 findings.**
- **3 are Architecture's answers to Grok, stuck in `_needs_review/`.** The router cannot deliver to `From: Grok (Design / CIC)`, because the name before the signature is "Grok".
  - They were compared with the tray copies: the bounced copies carry the answers, so they are NOT duplicates. **Nothing moved.**
- **2 are the owner-board files,** which Architecture ruled are not letters.
- **11 are letters I answered in place on 09-11 and 09-12** and never dropped back through `inbox/`. Clearing them means dropping 11 files, and **rule 5 puts that list in front of Sleven first.**
- **Memo delivered to Architecture at 06:14:05:** `..._three-grok-answers-are-stuck-and-the-mail-check-holds-the-share-card.md`.

**The share card is built and proven on disk, and NOT deployed.**
- `deploy_testing.ps1` refuses a red sweep. `-IgnoreRedCheck` covers only its own browser checks; **the sweep gate's only override is `-IgnoreSweep`.** No ruling lets a desk use it, so it waits on Sleven's word.
- **Otherwise the route is:** clear the 11, Architecture settles the board files and the three answers, re-sweep for about 30 minutes, then deploy.

**With Sleven:**
1. the 11-letter list (rule 5)
2. deploy past a mail-only red, or wait

**With Architecture:**
1. the owner-ask wording and the README owner
2. the routing basis and the owners-parser shape
3. the `deploy_pages.py` owner
4. the three stuck answers and the board files

**Uncommitted (Code's and delegated):**
- `checks/push_guard.py`
- `checks/_verify_share_card.py`
- `checks/_verify_deploy_drift.py`
- `testing/_src/build_deploy.py`
- `testing/_src/deploy_pages.py`
- `testing/_src/loadout.src.html` (delegated)
- `testing/_src/og-loadout.png`
- `.git/hooks/pre-push`, which is not tracked

Nothing committed.
