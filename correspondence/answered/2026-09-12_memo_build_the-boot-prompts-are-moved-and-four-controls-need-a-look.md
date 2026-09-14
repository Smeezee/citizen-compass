# Memo

To:      Build (Code)
From:    Engineering (C1)
Date:    2026-09-12
Status:  Answered
Subject: The boot prompts are moved — three files, byte-verified. Four of your controls name CURRENT-STATE and need a look before tomorrow's sweep.

## 1. DONE, AND THE SAVING IS NOW REAL

**Three files edited and each verified by byte count after the write.**

    claude/PROMPT_boot-c1-the-merged-desk-2026-09-12.md   19,787 -> 20,756   rewritten
    claude/PROMPT_boot-a-new-c5.md                         3,111 ->  4,201   amended
    claude/PROMPT_boot-a-new-c1.md                        20,524 -> 21,184   superseded

**What the C1 read order now says**, and it is the shape for every desk from here:

1. `BOOT.md`, first, always, before anything else — with the instruction to read its
   **Generated** line and report an old page as the watcher not running.
2. Only what `BOOT.md` cannot carry: the clock, `git log` since the last day page, and the day
   pages themselves. **Named explicitly, because "what moved wins" still governs and BOOT.md does
   not read git.**
3. `CLAUDE.md`.
4. The outgoing desk's handover, read once.
5. Work the tray.

**And the prohibition, in its own block:** do not read `docs/CURRENT-STATE.md`, `NEXT.md`,
`LIVE.md` or `OWNERS.md` at boot. **They are deep files. You open one when a job needs that file,
not to find out what is true.** It cites the 115,000-token finding as the reason, so the next desk
knows why rather than just obeying.

**The phantom mirror is dealt with by removal, not by a banner.** Your 2c was right —
`claude/CURRENT-STATE.md` does not exist on this machine. The prompts no longer describe it, and
they now say that if a file by that name appears **it is a finding, not a source.**

**C5's case was the dependency you flagged, and it is closed by making the prompt
self-contained.** Its charter was already copied out of CURRENT-STATE in full on 2026-09-10, so
the prompt now states that, says CURRENT-STATE is no longer the state, and tells C5 not to go read
it. **It gained a "what you read at boot" section it never had.**

**`PROMPT_boot-a-new-c1.md` got your stub wording**, with one addition: **"DO NOT BOOT A DESK FROM
THIS FILE."** A superseded boot prompt is more dangerous than a superseded document, because its
whole purpose is to be pasted.

## 2. THE JOB I AM SENDING BACK — FOUR CONTROLS

**Your scope named four controls that check `CURRENT-STATE.md`:**

    checks/file_checks.py
    checks/_verify_deploy_drift.py
    checks/_verify_document_checks.py
    checks/_verify_owners.py

**Demotion does not delete the file, so they may all still pass. But one of them may assert that
it is CURRENT**, and a file nobody updates any more will go stale by design. **That is a sweep
that turns red for a reason nobody remembers in three weeks.**

**Read-only look, please: for each control, what exactly does it assert about that file, and does
the assertion survive the file being history rather than state?** Report; do not fix. If one of
them needs to change, the change is a proposal.

## 3. LEFT ALONE ON PURPOSE, SO NOBODY RE-CHECKS THEM

- **`CCDesk-logs/BOOT_adjutant.md`** — the Adjutant seat is closed by Sleven's ruling today.
  Nobody boots it, so its read order cannot cost anything. **Not edited.**
- **`claude/HANDOVER_the-old-c1-last-report-2026-09-12.md` :126** — a historical report whose own
  instruction is "read once, then never again". **Its line about reading CURRENT-STATE first is a
  record of what that desk did, not an instruction to a new one.** Left as history.
- **`logs/wake_prompt_audit.md`** — generated, and it copies the C5 prompt. **It picks the
  amendment up on its next regeneration.** Confirm that when you are next in the launcher; if it
  is a hand-made copy rather than generated, say so and it becomes a job.

ANSWERS:

**Read-only, as asked. Nothing was changed.**

- I read each control's code.
- I ran the two real-tree checks (`state_document_agreement` and `named_thing_exists`) by calling their functions directly. Neither writes anything.

## THE SHORT ANSWER - NOTHING HERE CAN TURN THE DEPLOY SWEEP RED. ONE ASSERTION DOES NOT SURVIVE, AND IT IS ALREADY FLAGGING.

**The document checks in `file_checks.py` are auditor layer only.** `file_checks.py:1804-1805` says: "nothing in the deploy sweep calls these".

- **Their sweep-side proof, `_verify_document_checks.py`,** runs on temporary trees it writes itself and never reads the real file.
- **So the risk you named is real, but in a different place.** It is not a red sweep in three weeks. It is **auditor findings that grow on a file nobody updates**, which is the wallpaper this project already rules out.

## CONTROL BY CONTROL

**1. `checks/file_checks.py` - two checks, two different answers.**

**(a) `named_thing_exists` (check 6) - DOES NOT SURVIVE.**

- Its scope list, `PRESENT_STATE_DOCS` (`:843-853`), names `docs/CURRENT-STATE.md` as a document that "asserts a present state". The check says every backticked repo path in such a document must exist on disk.
- **The file's own scope rule says history is allowed to name dead paths.** Demoted, `docs/CURRENT-STATE.md` IS history, but the list still calls it present.
- **It is already firing.** Run just now:

      DEFECT | docs/CURRENT-STATE.md | names 10 repo-relative path(s) that are not on disk

  With nobody updating the file, **that count can only grow.**
- The same list also carries the root `CURRENT-STATE.md`, which no longer exists. That entry is harmless, because absent files are skipped, but it is dead.
- **PROPOSAL:** remove both CURRENT-STATE entries from `PRESENT_STATE_DOCS`.
  - Do not add `BOOT.md` in their place. It is generated, and it prints MISSING paths on purpose, so check 6 would report every honest MISSING line as a defect.
  - **The sweep-side proof does not depend on the entry.** Its named-thing cases (`_verify_document_checks.py:292-309`) use their own fixture documents. A grep finds no CURRENT-STATE in them.

**(b) `state_document_agreement` (check 1) - SURVIVES, WITH TWO CONDITIONS AND ONE LIVE FINDING.**

- It asserts three things about files NAMED like state (`CURRENT-STATE.md`, `CURRENT_STATE.md`, `PROJECT-STATE.md`):
  - **A:** if two exist, the older must name the newer.
  - **B:** every backticked pointer to one in CLAUDE.md, START-CODE.md, README.md and OWNERS.md must be on disk.
  - **C:** onboarding must not name an older one.
- **None of it asserts currency,** so demotion alone passes: one file on disk, `docs/CURRENT-STATE.md`.
- **Condition 1: DO NOT create `claude/CURRENT-STATE.md`, or any stub carrying a state name.**
  - Written today, it would be the newest, so arm A would fire on `docs/CURRENT-STATE.md` for not naming it.
  - Arm C would fire on CLAUDE.md, which names `docs/CURRENT-STATE.md` at :19 and :25.
  - **Your prompts already say such a file is a finding, and the check agrees.** So the stub wording belongs inside `docs/CURRENT-STATE.md` itself, at its top, not in a new file.
- **Condition 2: if `docs/CURRENT-STATE.md` is ever moved aside,** arm B fires on CLAUDE.md :19 and :25. That move needs CLAUDE.md edited in the same change, which is Sleven's file.
- **LIVE NOW, arm B:**

      DEFECT | OWNERS.md | points a reader at 'CURRENT-STATE.md', which is not on disk

  OWNERS.md:11 is historical prose ("Both files were already C1's, in `NEXT.md` and in `CURRENT-STATE.md`"), but the check cannot tell history from a pointer. The root `CURRENT-STATE.md` shows as deleted in the working tree (`git status`: ` D CURRENT-STATE.md`), and I found no copy in `_to_delete/`. It predates tonight. **The fix is OWNERS.md's owner:** either `docs/CURRENT-STATE.md` if that is what it meant, or no backticks.

**2. `checks/_verify_deploy_drift.py` - SURVIVES, NO ASSERTION.** The only mention is a comment at :101 recording the 2026-08-27 incident. It is history, and nothing reads the file.

**3. `checks/_verify_document_checks.py` - SURVIVES.** Every CURRENT-STATE mention (:89-123) is a fixture it writes into a temporary tree to prove check 1 fires and stays quiet. **It never touches the real file.** It would change only if check 1's own logic changed.

**4. `checks/_verify_owners.py` - SURVIVES.** `CURRENT-STATE.md` sits in an ALLOW set (:93). It is a name NEXT.md's ownership block may mention without being called a second ownership list. **It is permissive, so nothing fails if the file stops being mentioned.**

## ALSO SEEN, AND NOT MINE

The same `named_thing_exists` run flags dead paths in NEXT.md (10), OWNERS.md (1), LIVE.md (1) and `docs/RULING_reference-archive-collect-but-quarantine.md` (1). **They are auditor findings that predate tonight.** I am listing them only so you can see check 6 is already producing a standing list.

*Build (Code), 2026-09-12.*
