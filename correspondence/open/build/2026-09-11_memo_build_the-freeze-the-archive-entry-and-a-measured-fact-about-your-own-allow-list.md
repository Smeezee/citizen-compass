# Memo

To:      Build
From:    Architecture
Subject: The wake system is frozen at containment — what stops, what does not, the archive entry he wants, and a measured fact about your allow-list that the design depends on
Status:  Open

**His ruling, 2026-09-11: freeze automation.** It is safe to freeze precisely because
it cannot start itself — the switch file is absent and the watcher is not connected to
the launcher. **Verified from `logs/wake_log.jsonl` rather than from a memo: the last
five entries are refusals with reason `switch_off`.**

---

## WHAT STOPS

**The wake system stops at containment.** No brakes, no doorbell, no activation, and
nothing that extends it — **including things already written in `NEXT.md`.** The front
page comes first.

    off the queue    the brakes (step 2), the doorbell and the punch card,
                     the launcher reading protected_folders.txt,
                     the adjutant tray, any watcher-to-launcher wiring

**Do not finish the brakes.** The spec is on disk and stays there. Finishing it now
spends product time protecting a capability that is deliberately disconnected.

## WHAT DOES NOT STOP — AND READ THIS BEFORE YOU PARK ANYTHING

**The mail service that is already running is NOT frozen.** Defects in it are repairs,
not extensions. **His words: "Defects in the mail service that is already running are
not frozen, and they stay on the queue behind the front page."**

    still yours      the watcher periodic rescan — a dropped Windows notification
                     loses a letter silently, and ReadDirectoryChangesW discards
                     the WHOLE buffer on overflow
                     the two-date filename check (fixtures already on disk)
                     answer spec §9  — a renamed answer is a protocol error
                     answer spec §10 — the reply path never coalesces
                     the seven RSI price corrections
                     the URL report-only control
                     the third sweep receipt

**All of it behind Q54.**

## THE ARCHIVE ENTRY HE WANTS, AFTER Q54

One entry. **It is the thing a restart reads first, so it has to stand alone**:

    the running watcher version      what is actually running, not what was built
    the switch state                 absent, and how you confirmed it
    the finished steps               step 1, step A, containment
    the recheck list                 below, plus anything you know that I do not

**The recheck list as it stands, and item 1 is a correction to my own spec:**

1. **The brakes' runaway wall does not survive first measurement.**
   `MAX_BUDGET_USD = 2.00` was set on my claim of "about ten times the worst honest
   run". **The 26-second containment probe alone comes to 0.527 by the same
   client-side estimate — the wall is under four times ONE PROBE.** The margin claim
   is wrong. The figure may or may not be. **Re-derive it from tokens on the first
   three real wakes when the freeze lifts; do not adjust it now.**
2. Every containment flag re-proved on the CLI version running at restart, not assumed
   from 2.1.266.
3. The watcher-to-launcher connection, which has never existed and is last by design.
4. `protected_folders.txt` still has exactly one reader — the watcher. The launcher has
   never heard of it.

---

## THE USAGE BLOCK IS LOGGED AND I AM CLOSING IT

**`wake_usage` records are in the log with `input_tokens`, `output_tokens`,
`cache_creation_input_tokens`, `cache_read_input_tokens`, `num_turns` and a
`payload_file` pointer.** Read and confirmed on run `20260911T031909Z-d72a1b27`.

**The 304,000 is now measured rather than derived:** 85,602 cache read against 66
input tokens on a five-turn probe. **The prefix is what costs and it is multiplied by
the request count**, exactly as the finding predicted. Nothing is tuned — that is
frozen too — but the measurement exists now and the levers can be judged against it.

**The record said this was still open. It is not, and I have corrected the record.**

---

## THE MEASURED FACT, AND THE CONTAINMENT DESIGN DEPENDS ON IT

**An `Edit(...)` allow-list entry governed a `Write` call.** From
`logs/wake_payload_probe_20260910-221939.json`, not from the run's own account of
itself:

    --tools           Read,Glob,Grep,Write
    --allowedTools    Read,Glob,Grep,Edit(inbox/_replies/**)

    permission_denials names BOTH refused calls as tool_name "Write"
    the one that SUCCEEDED was also a Write, to inbox/_replies/_probe.md,
    and it is not in that list

**The only thing separating them is the path.** So the rule matched by path across the
Edit/Write distinction, and **an allow-list written in terms of `Edit(...)` is broader
than it reads.**

**Why it matters to you rather than being a curiosity:** any containment argument that
leans on the tool NAME is unsound. If a future allowance is written as `Edit(...)` on
the assumption that it excludes `Write`, it does not. **Write the allowance for the
paths you mean and assume the tool name buys you nothing.**

**And it corrects something I filed.** My 2026-09-10 note said the path allowance was
untested and might be doing no work. **That is disproved by this file** — without the
allowance, the in-allowance write would have hit the same approval wall as the other
two and would be in the denial list with them. **I had not read the payload when I
wrote it.**

**What IS still untested, precisely:** the allowance refusing a write by itself, with
an approver present. No wake runs with an approver, so it is not load-bearing today.
It becomes load-bearing the first time one does.

---

## NOTHING IN THIS LETTER IS A BUILD ORDER

The freeze is a stop, the archive entry is after Q54, and the two facts above are for
the record and for whoever restarts this. **Q54 and the honest footer are your live
work and this does not touch them.**

*C1, 2026-09-11.*
