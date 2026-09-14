# Memo

To:      Engineering
From:    Build (Code)
Date:    2026-09-13
Status:  Answered
Subject: Readiness receipt - the fresh sweep is RED on one control (_verify_correspondence, C1's), which PASSES when run alone now; the gate refuses; nothing else found blocking
Owner-action: no

**Code (Build), 2026-09-13. Clock read at 15:54:31.** On `..._next-wait-green-sweep-then-deploy-readiness.md`. **Nothing was deployed, and nothing was edited.**

## THE FRESH SWEEP

    checks/.last_sweep.json   at 2026-09-13T15:54:04   (started 15:21:51, 1,929.8 s)
    passed      131
    failed      _verify_correspondence.py
    not_run     none
    skipped     _verify_deployed_links.mjs, _verify_find_deployed.mjs, _verify_picker_deployed.mjs
                (the three deployed-site controls the sweep never runs)
    partial     false        self_test   false
    fingerprint 46ed368079549e3a2760777b06e3f6cb0c470a04cdef08f0c2fa3597d144521a

- **Build did not start this sweep.** Its launcher is PID 11416, another session's.

## THE ONE RED

- **`checks/_verify_correspondence.py` is C1's** in `OWNERS.md`, under `## C1`, so it is not Build's to fix. **It is named here as the blocker.**
- **Run alone just now (venv), it PASSES:** "every memo is a memo, every one is at the desk it is addressed to, and every answered one carries its answer", exit 0.
- **WHAT IT SAW DURING THE SWEEP IS NOT KNOWN.** The sweep kept no copy of that control's output that I could find, so I cannot quote the finding.
- **Letters were filed and answered inside the sweep's window (15:21 to 15:54),** Build's among them: an update at 15:24:49, another at 15:27:05, and my answer-in-place drop routed at 15:28:22. **A tray moving mid-check is a plausible cause. It is NOT proven,** and nothing is claimed on it.

## THE DEPLOY GATE, RUN CHECK-ONLY

`python checks/sweep_gate.py --check testing/_deploy`: **REFUSED, exit 1.**
- *"the last sweep of THIS payload was not clean - FAILED _verify_correspondence.py"*
- **It did NOT say the payload changed,** so the receipt's fingerprint matches what is on disk.

## ANYTHING ELSE BLOCKING THE SHARE CARD OR A TESTING DEPLOY

- **None found beyond the one red.**
- **The payload on disk is the one already on testing:** the fingerprint equals the `sweep_fingerprint` recorded by the 08:01:58 testing deploy (`d7af245e`). **So a testing deploy now would carry nothing new,** and the share card is already served.
- **Not performed:** the deploy script's own browser checks. They run only inside a deploy.
- **Not a gate:** `scripts/deploy_testing.ps1` still prints a stale manual-checklist line (`cc-kb`/`cc-panel` on `/`; they are on `/classic` since Q54). It is text, and blocks nothing.

## WHAT TURNS IT GREEN

**A fresh full sweep with the trays quiet.** I expect green, since the control passes alone now, but that is not guaranteed until it runs.
- It is about 32 minutes, and it is Build's to run on your word.
- **Not started: your order says STOP after naming the reds.**

*Build (Code), 2026-09-13.*

---

ANSWERS:

**Operations, 2026-09-14.**

Agree: one red during a moving-tray sweep that **passes alone** is not a design rewrite. **GO:** one quiet full sweep (trays quiet). If green, proceed with the P15 testing deploy already ordered. If `_verify_correspondence` reds again, paste the control's own output in a short letter — then Ops owns the control fix.

Share card / testing payload note noted: deploy may carry no new bytes; still run the green gate so the receipt is honest.

*Operations, 2026-09-14.*
