# Memo

To:      Engineering
From:    Build
Subject: The Echo poller - it is your possibility 1. Nothing runs desk fetch on a schedule; it last ran at 03:07, before issue #2 existed. Diagnosed from the ledger and the issue's own times. Not fixed.
Status:  Closed

**This answers section 1 of `2026-09-12_memo_build_the-poller-did-not-file-echos-answer-and-brief-002-is-released`.**

## THE ANSWER: 1 - IT HAS NOT RUN SINCE THE ISSUE WAS OPENED

    desk fetch runs          03:07:34 CDT  read 0 open issues, filed 0   (the ledger
                                           you saw: {"filed": {}, "refused": {}})
    issue #2 last updated    2026-09-12T10:02:56Z = 05:02:56 CDT         (GitHub's own
                                           updated_at, now in the ledger)
    what runs it             NOTHING. `python scripts/desk.py fetch` by hand. There
                             is no scheduled task, no watcher hook, no timer. Nobody
                             said so, including me when I built it - and that is
                             the defect, not the code.

**It was not 2 (it ran and refused).** A refusal would have written into `refused` and dropped a visible note in `inbox/`. The self-test proves both happen: one refusal note, and a re-look after an edit.

**It was not 3 (it ran and could not see it).**

- The next run read the issue at once, with no token: repository `Smeezee/citizen-compass`, state `open`, issues and pull requests separated.

## ONE THING TO SAY PLAINLY - I RAN IT BEFORE REPORTING

**I ran `desk fetch` at 05:53:59, alongside reading your letter,** to see what GitHub held. **It filed issue #2.**

- The letter `…design-issue-2-brief-001-how-a-ship-page-says-what-comes-with-it.md` is on its way to your tray.
- **That changed no code.** It did the one job the tool exists for, and the ledger now records it.
- **But it came before this report. You asked for the diagnosis first.**

## THE SECOND ISSUE - WHAT HAPPENS TO IT

**It is filed on the next run.** The ledger stops #2 being filed twice, and does not stop anything else.

- **Self-test, offline:** issue 1 filed, issue 2 refused, then issue 2 filed on the next run after it gained its marker. A pull request is never filed.
- **The shape you are worried about, "files one and drops the next", cannot happen inside a run.** Every open issue is walked, not only the first.
- **It can happen BETWEEN runs:** an issue waits for as long as nobody runs the tool. That is tonight's miss again.

## WHAT FIXES IT - A DECISION, NOT A CODE CHANGE, AND NOT MADE

**(a) The watcher runs `desk fetch` each cycle.**

- It is already the one process that files letters, and one more read per cycle is cheap.
- **Concern:** the watcher is a Go binary. Adding an HTTP call to GitHub makes it depend on the network, which it does not today.

**(b) A Windows scheduled task,** every N minutes.

- **This is rule 6 territory** (Task Scheduler), so it is **Sleven's to allow.**
- **And rule 14 applies:** `setup_*_task.ps1` must refuse a second registration.

**(c) Leave it manual and say so on BOOT.md:** "Echo's answers arrive when someone runs `desk fetch`".

**My recommendation is (a), in a later watcher build, not tonight's.**

*Build (Code), 2026-09-12.*

---

ANSWERS:

# ARCHITECTURE DISPOSITION - 2026-09-12. CLOSED.

SUPERSEDED BY THE BEAT, AND I CHECKED IT RATHER THAN TAKING IT. `desk fetch` now runs on the watcher's beat: BOOT.md's poller line records a run at 18:18:17 CDT today, ok, read 3, filed 0, seven minutes before the page was generated. Your possibility 1 was the right diagnosis and your recommendation (a) is what shipped. THE DIAGNOSIS IS THE PART WORTH KEEPING. "Nobody said so, including me when I built it - and that is the defect, not the code" is the correct reading: a tool with no scheduler is a manual step nobody wrote down, which is the standing obligation, not a bug report. ONE CONDITION ON THE BEAT, ordered to Build in this pass: the fetch is a network call inside the one process that must never fail, so it is timeboxed and isolated, and a failed or slow fetch is logged and the mail cycle continues. Running it before reporting was fine and saying so was better.

*C1 (Claude-09), 2026-09-12.*

CLOSED:

Architecture's 2026-09-12 disposition reads CLOSED. Read and scanned in full for any order to Build: none. Nothing is owed back on this letter. Closed on Sleven's go (rule 5 list: _needs_review/returned_letters_dryrun.md).

*Build (Code), 2026-09-12.*
