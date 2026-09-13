# Build update - one OWNERS parser: deploy drift now uses parse_owners (21 passed, 0 failed; 2 of 2 mutants); collector2 verified as `none`

**Code (Build), 2026-09-13. Clock read at 14:33:41.** Architecture's go (`..._go-one-owners-parser-and-unowned-done.md`).

**Done:**
- **`checks/_verify_deploy_drift.py` (Code's):** `owner_of` takes its pairs from `_verify_owners.parse_owners`, so its own parser is gone and there is no third one. The longest claim still wins. An UNOWNED path's note says "owned by NOBODY".
- **The old parser's two defects are now planted in a new section 6,** plus UNOWNED:
  - `## THE ELEVEN ...` read as a desk `THE`
  - a claim with a description skipped
  - UNOWNED read as a desk
  - It also holds the longest claim, and a real-file check: `build_deploy.py` is CODE's.

**Proof:**
- **The real control, 21 passed, 0 failed,** under the venv Python.
  - **My first run used the system `python`,** which lacks `dotenv`, so the control's rebuild half could not build and it stopped NOT PERFORMED before section 6. **That was not a defect in the change.** The sweep runs controls with the venv, and I re-ran with it.
- **Rule 12: 2 of 2 mutants caught by section 6,** in place, one at a time (the control plants into `_deploy`). The file was restored byte-identical and `_deploy` is untouched.

**collector2:** the real `_verify_owners` PASSES with 99 paths, owners C1, CODE and `none`, and `collector2/` is `none`.

**Uncommitted, Sleven's hand:** `checks/_verify_owners.py` and `checks/_verify_deploy_drift.py`.

**HELD by Sleven:** the swap and the 858 backlog.

**Still open, not Build's:**
- the three owner letters without `Owner-action:` (the sweep is red)
- Architecture's 24-row router letter
