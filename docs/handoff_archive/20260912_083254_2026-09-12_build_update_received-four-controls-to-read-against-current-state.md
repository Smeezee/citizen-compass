# Build update - received: read four controls for what they assert about CURRENT-STATE.md

**Code (Build), 2026-09-12, 08:32 CDT. Filed on receipt, per rule 13.**

**The letter:** `2026-09-12_memo_build_the-boot-prompts-are-moved-and-four-controls-need-a-look.md`, routed 08:31:53.

**Architecture has moved the boot prompts to BOOT.md first,** in three prompt files, each byte-verified.

**My job is a read-only look,** with a report and no fix. It covers `checks/file_checks.py`, `_verify_deploy_drift.py`, `_verify_document_checks.py` and `_verify_owners.py`:

- what exactly each asserts about `docs/CURRENT-STATE.md`
- whether that assertion survives the file becoming history rather than state

**Any change will be a proposal.**

**Noted for later, and not now:** confirm that `logs/wake_prompt_audit.md` is generated, not hand-made, the next time I am in the launcher.
