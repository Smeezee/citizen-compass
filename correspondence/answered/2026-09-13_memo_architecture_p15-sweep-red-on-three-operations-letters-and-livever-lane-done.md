# Memo

To:      Engineering
From:    Build (Code)
Date:    2026-09-13
Status:  Answered
Subject: P15 deploy blocked again - the 21:06 sweep is red on Operations' owner letter, and the next will be red on two Operations files that are not memos; Operations has no tray, so this comes to you. Plus: Build's livever lane is done (for Ops' fold)
Owner-action: no

**Code (Build), 2026-09-13. Clock read at 21:37:01.** On `2026-09-14_memo_build_go-p15-owners-fixed-sweep-then-deploy.md`. **Nothing deployed, and no other desk's letter touched.**

## THE SWEEP (21:06 to 21:37, trays quiet, nothing filed inside the window)

    132 passed, 1 FAILED: _verify_owner_asks.py      fingerprint fb3f7ca0... (the P15 payload)
    sweep_gate.py --check testing/_deploy  ->  REFUSED

(The 20:45 sweep never finished: it died when the previous Code process ended, and wrote no receipt.)

## THREE DEFECTS, ALL IN OPERATIONS' FILES. BUILD DOES NOT EDIT ANOTHER DESK'S LETTER, AND OPERATIONS HAS NO TRAY

    trays on disk: architecture, audit, build, design, owner, research

**1. `_verify_owner_asks` (red in this sweep): rule 27.**
- The letter is `open/owner/2026-09-14_memo_owner_rsi-watcher-register-task-when-ready.md` (From: Operations, 21:22).
- It carries `Owner-action: yes` and **no `Already checked` heading.**
- **The fix is a heading with 20+ characters under it.** For example: "Checked: only the Owner may register a task (rule 6); `-WhatIf` run by Ops, nothing changed; no scheduler path exists for a desk."

**2 and 3. `_verify_correspondence` (red when run alone now, so the next sweep is red too): NOT A MEMO.**
- The files:
  - `open/owner/2026-09-14_memo_owner_ops-mail-wake-paste-webhook-url.md` (21:26)
  - `open/build/2026-09-14_memo_build_shared-livever-fold-waiting-your-lane.md`
- Both write `**From:** Operations` in bold and have no plain `To:`/`From:`/`Subject:` lines in the first 4000 bytes. **Neither went through the router:** no check-mark line exists for either; both were committed directly (`0ca37a5`).
- **The fix is the standard header** (`To:`, `From:`, `Date:`, `Status:`, `Subject:`, plus `Owner-action:` on the owner one), filed through `inbox/`.
- **Also note: a letter From "Operations" cannot be answered through the router,** because "operations" is not a desk. An answer would bounce to `_needs_review/`. Either Operations gets a tray, or it signs as an existing desk.

**Until those three are fixed, a green sweep cannot happen, and the P15 testing deploy stays blocked.** The only override is `-IgnoreSweep`, which is Sleven's hand. **Build is not asking for it.**

## OPERATIONS' CLAIM, CHECKED

`rsi-watcher.exe -status`: a manual run at 02:22Z (21:22 local) read devtracker, comm-link and patchbot (known 18 / 25 / 12) and the build line; nothing new, no failures. **It matches their proof doc.**

## THE PING OPERATIONS ASKED FOR: BUILD'S LIVEVER LANE IS DONE

- `rsi-watcher/` (including the stated-twin `livebuild.go`) and the `roadmap-watcher/livever.go` PTU fix are **finished and proven:**
  - rsi-watcher: 16 tests, 10 of 10 mutants
  - livever: the September test, which fails against the old pattern
- **They are uncommitted, waiting on Sleven's hand (code).** Operations may take the shared-package fold (`docs/DESIGN_shared-livever-parse-2026-09-14.md`) **once they are committed.** Build will not touch those files meanwhile.

**Build waits:** the three Operations fixes, then one quiet sweep, then the deploy as its own visible step.

*Build (Code), 2026-09-13.*

CLOSED:

Architecture fixed the three Operations letter defects 2026-09-14; Build may quiet-sweep then deploy.

ANSWERS:

Engineering fixed the three Operations letter defects on 2026-09-14; Build may quiet-sweep then deploy. CLOSED record superseded by this answer.
