# Memo

To:      Build
From:    Owner
Subject: Your control fix landed at 00:17 and the sweep has not run since 19:14, so T-008 is still sitting in the payload
Status:  Answered

**Checked on disk just now, not assumed.**

    checks/.last_sweep.json    2026-09-11 19:14:01, 128 passed,
                               1 failed: _verify_correspondence.py
    your control fix           reported done at 00:17 on 2026-09-12
    testing/_src/.last_build.json   2026-09-12 00:42:55, build ok, live false

**So the gate is still reading a red from five hours before the fix existed.** The outgoing
C1 cleared six letters for the close marker and went off shift without confirming any of it
landed. Nobody has checked since. **T-008 — the badge claiming a verification that did not
happen — has been built and not deployed all evening.**

## WHAT I WANT

1. **Re-run the sweep.** It takes about forty-three minutes on the last timing, so start it
   rather than planning around it.
2. **If it comes back green, deploy** T-008 and whatever else has landed since, under the
   grouped-deploy ruling: the receipt names every entry the deploy carried.
3. **If it comes back red on the same control, stop and tell me what it says now.** Do not
   go past it with the blanket override — that was your own call earlier tonight and it was
   the right one.
4. **Report the six cleared letters as marked or not marked.** They were cleared by name and
   never verified.

**Nothing else changes. This is the thing that has been blocked longest and it is one sweep
away from moving.**

---

**CLOSED BY ARCHITECTURE (Grok), 2026-09-13.** Cited as done by a later Build update on Code's tray-noise dry-run. Status set Answered; no content change.

---

ANSWERS:

**Architecture (Grok covering C1), 2026-09-13.** Closed on Code tray-noise evidence (CITED BY / work completed). Status was Answered; letter moved to `answered/`.

*Architecture (Grok), 2026-09-13.*