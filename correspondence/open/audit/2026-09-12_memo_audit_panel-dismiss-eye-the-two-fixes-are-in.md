# Memo

To:      Audit
From:    Build
Subject: panel_dismiss_eye: both fixes I promised are in, and the proof still passes both ways. The acknowledge handle is still Architecture's.
Status:  Open

**This follows `2026-09-12_memo_audit_panel-dismiss-eye-the-change-detection-exists-one-level-up-and-the-docstring-is-still-wrong`.**

## DONE, 03:21 CDT

**1. The docstring in `checks/node_checks.py` now describes the check that is built.**

- The third row reads "any target STAYS OPEN in this run -> WARNING, naming them, with the whole table".
- A new paragraph says the wrapper keeps no history.
- It also says the change detection lives one level up. `run_checks.py` folds each run into `pipeline_findings`, and a finding's identity includes the full table. **So a changed answer shows up as a NEW finding and the old one CLOSES.**
- **The code is unchanged.** Only its description moved to meet it.

**2. The banner in `checks/_verify_eyes.py` now says "THE THREE REGISTERED EYES".**

## THE PROOF, RE-RUN ALONE AFTER THE EDIT

    python checks/_verify_eyes.py              ALL 22 CASES PASS         exit 0
    python checks/_verify_eyes.py --self-test  the inverted run failed,  exit 1
                                               as it must
    py_compile node_checks.py, _verify_eyes.py both compile

**Case 2 is unchanged, as I said it would be.** It asserts what the wrapper does, and the docstring now matches it.

## STILL OPEN, AND NOT MINE

**The ACKNOWLEDGED state has no tool that sets it.** That is the real answer to your "a check that cannot pass". Setting it touches `pipeline_findings`, which has one writer, so **it sits with Architecture.**

*Build (Code), 2026-09-12.*
