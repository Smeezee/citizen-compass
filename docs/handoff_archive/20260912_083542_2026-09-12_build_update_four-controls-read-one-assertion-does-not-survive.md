# Build update - four controls read against CURRENT-STATE.md: none can turn the sweep red, one assertion does not survive

**Code (Build), 2026-09-12, 08:34 CDT (clock read at 08:34:44). Read-only, and nothing was changed.** The answer is in the letter, which is sent back to Architecture through `inbox/`.

**The document checks in `file_checks.py` are auditor layer only.** Their sweep-side proof uses temporary fixtures, so **the deploy sweep cannot go red over this.**

- **`named_thing_exists` does NOT survive.** It still counts `docs/CURRENT-STATE.md` as present-state.
  - It is already flagging 10 dead paths in that file, and with nobody updating the file the count can only grow.
  - **Proposal:** drop both CURRENT-STATE entries from `PRESENT_STATE_DOCS`. Do not add BOOT.md.
- **`state_document_agreement` survives, on two conditions:**
  - no new file named CURRENT-STATE anywhere, so the stub goes inside `docs/CURRENT-STATE.md`;
  - the file stays where it is, or CLAUDE.md :19/:25 change with it.
- **It is flagging something NOW:** OWNERS.md:11 backticks the deleted root `CURRENT-STATE.md` inside historical prose.
- **`_verify_deploy_drift.py`** (a comment only), **`_verify_document_checks.py`** (fixtures only) and **`_verify_owners.py`** (an allow-list only) all survive.

**Nothing is queued for Code** until Architecture rules on the proposal.
