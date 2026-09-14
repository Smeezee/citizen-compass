# Memo

To:      Engineering
From:    Build (router)
Subject: B1 found 3 citation gap(s) in documents you wrote
Status:  Open

**Filed by `checks/record_router.py` (B2) from B1's record audit.** Each gap below sits
in a document that declares you wrote it, or is labelled if it does not say.

**Reply under `ANSWERS:`, one line per row, in exactly one of these forms.** B3
(`checks/record_repair.py`) reads them; anything else is named MALFORMED, never guessed.

    `<source>` | `<token>` | <class> | <note>      HISTORY - class is one of
                                                   example future absence history fix-pending
    MOVED `<source>` | `<token>` -> `<new path>`   B3 repoints it, on Architecture's word
    DEFECT `<source>` | `<token>`                  fixed at the source; B1 stops reporting it

---

    source    docs/DESIGN_ops-mail-wake-on-new-letter-2026-09-14.md
    citation  correspondence/_ops_state/mail_wake_state.json
    kind      absent
    routed    UNDETERMINED - no declaration
Router-key: docs/DESIGN_ops-mail-wake-on-new-letter-2026-09-14.md | correspondence/_ops_state/mail_wake_state.json

---

    source    docs/DESIGN_shared-livever-parse-2026-09-14.md
    citation  pkg/rsiboard
    kind      absent
    routed    UNDETERMINED - no declaration
Router-key: docs/DESIGN_shared-livever-parse-2026-09-14.md | pkg/rsiboard

---

    source    docs/DESIGN_shared-livever-parse-2026-09-14.md
    citation  pkg/livever
    kind      absent
    routed    UNDETERMINED - no declaration
Router-key: docs/DESIGN_shared-livever-parse-2026-09-14.md | pkg/livever

*Build (router), 2026-09-13.*
