# Memo

To:      Owner
From:    Build
Date:    2026-09-11
Subject: STEP A IS DONE. The watcher is swapped, all four conditions verified on the live tree, every test letter closed out. Stopping here.
Status:  Closed

**The mail system is now running the answer-routing build. Rollback is one copy
back and its full path is below. I have not begun step B.**

---

## 1. THE ROLLBACK, TAKEN FIRST

    C:\Users\david\citizen-compass\inbox_watcher.ROLLBACK-20260910-1948.exe
    5,768,192 bytes   mtime 2026-09-09 21:58
    sha256 6b22ec29b1f1116541bb812677f9317a7e72341e3c907f4a92a1fae9e9e46d20

**Copied and hash-verified against the running binary BEFORE anything was
stopped.** The hash of the rollback and the hash of what was then running are
identical, so the copy is the thing itself and not a near-miss.

**Now installed:**

    C:\Users\david\citizen-compass\inbox_watcher.exe
    5,770,752 bytes   mtime 2026-09-10 15:14
    sha256 f9d983b2ea7c8541a62d2e87dd3f16aec95e088030d9f6fa98acb5b471f84868

**That hash is the binary I proved yesterday afternoon, byte for byte** — I did
not rebuild. `memo.go` has not been touched since 15:07 and the binary was built
at 15:14, so the artefact installed is the artefact tested.

    running   pid 19112, started 2026-09-10 19:47:49
    task      Citizen Compass Inbox Watcher, state Running
    log       "Now watching for new files" at 19:47:50

**To roll back:** stop the task, copy the ROLLBACK file over `inbox_watcher.exe`,
start the task. The same three steps in reverse, and the old binary has not been
moved or renamed out from under you.

### ONE THING ABOUT THE SWAP YOU SHOULD KNOW

**I could not disable the scheduled task — `Disable-ScheduledTask` returned
Access denied** in an unelevated shell. **The task restarts itself after one
minute**, so the first stop simply produced a new process (pid 10084) while I was
still looking at it.

**So the swap was done inside the restart window as one uninterrupted sequence:**
stop, poll until the process was actually gone, copy, verify the hash on disk,
start. The process was gone in 1.0 seconds and the whole gap was a few seconds.
**Mail was unattended for that window and nothing arrived in it.**

**And a defect in my own reporting, found while doing it:** my first command
printed the word "disabled" on a line that ran unconditionally — *after* the
disable had failed. I read it, and for about thirty seconds I believed a thing
that had not happened. **That is the silent-success shape in my own tooling, in
the middle of the one change I was told to be careful with.** No harm resulted;
the next command showed the true state.

---

## 2. THE FOUR CONDITIONS, ON THE LIVE TREE

**Synthetic letters only. No live thread carried a test round. Every artefact is
closed out and named in §3.**

### CONDITION 1 — AN ANSWERED LETTER RETURNS TO THE SENDER'S TRAY. PASS.

A synthetic question `To: Audit, From: Build` was placed in `open/audit/`, then
answered.

    the answer arrives in open/build - the SENDER's tray              PASS
    and it is the answer, not the question                            PASS
    and it did NOT go to correspondence/answered/                     PASS
    the answered question left the addressee's tray                   PASS
    and the superseded copy was KEPT in _to_delete/ (rule 1)          PASS

The watcher's own words, from its log:

    19:49:09 ✓ 2026-09-10_SYNTH-A-do-not-action.md ->
             correspondence\open\build\...  (ANSWER for build from audit — ...)

**"ANSWER for build from audit" is the new wording and it names both ends**, so a
person reading the log can see which direction a letter travelled.

### CONDITION 2 — THE OPEN COPY SURVIVES A ROUTING FAILURE. PASS, AND THIS IS THE ONE THAT MATTERS.

**I did not simulate the failure. I caused one.**

The destination filename in `open/build/` was occupied by a file **held open by
another process**. `routeTo` must move an existing destination aside before it
writes, a locked file cannot be renamed, so `routeTo` returned its error — and
the supersede, which is gated on that error being nil, never ran.

    THE OPEN COPY SURVIVED - open/audit still held the question       PASS
    and nothing was moved to _to_delete/ for that letter              PASS

**Then I released the lock, and the system finished the job by itself:**

    19:50:05 ✓ 2026-09-10_SYNTH-B-do-not-action.md -> open\build\...
             and the supersede followed at 19:50:05

**So both halves are shown, in the right order, on the real system: the open copy
was still there for the fifty-five seconds routing was failing, and it was
superseded only once the answer had actually landed.** That is the property
stated exactly as you wrote it — *available until routing SUCCEEDS*.

**AND IT FOUND SOMETHING I HAVE TO REPORT RATHER THAN FIX.**

**During those fifty-five seconds the watcher logged nothing at all.** Not an
error, not a retry line, nothing. It silently re-attempted until the lock
cleared. Had that blocker been permanent — a file genuinely stuck open — **the
letter would have sat in `inbox/` indefinitely and the only visible trace would
have been its continued presence there.**

**That is the same shape as the `fsnotify` defect Architecture filed at 13:40:
the failure is real, recovery is attempted, and nobody is told.** It is not part
of step A, I have not touched it, and it belongs with that memo rather than in
this change.

### CONDITION 3 — A MISSING OR INVALID `From:` FAILS CLOSED. PASS, BOTH CASES.

**Invalid sender** — an answered memo `From: Research (CIC)`, a real value that
exists in your archive today and matches no tray:

    19:50:08 ✓ ... -> _needs_review\2026-09-10_SYNTH-C-do-not-action.md
             (answered memo from "Research (CIC)", which is not one of ...)

    it went to _needs_review with the reason on it                    PASS
    and the refusal moved NOTHING out of the addressee's tray         PASS
    and nothing was superseded                                        PASS

**Absent sender** — a document with `To:` and `Subject:` but no `From:` at all:

    19:50:11 ✓ ... -> docs\2026-09-10_SYNTH-D-do-not-action.md  (doc)

    it is not routed to any tray                                      PASS
    and it did not reach the archive either                           PASS

**The two failures are deliberately different.** An invalid sender is a memo that
cannot be delivered, so it is refused and reported. An absent `From:` is not a
memo at all — three headers are required — so it is filed as an ordinary
document. **A report that happens to contain "To:" is still not quietly posted to
somebody.**

### CONDITION 4 — THE LOOKING PROJECT. NOT ACCESSED, NOT AFFECTED.

Every path touched in this work is under `C:\Users\david\citizen-compass` and
every one is listed in §3. **No Looking Project path appears in the test script,
in any letter it wrote, or anywhere in the watcher's log.**

**And it is structural rather than a promise: the watcher takes its project root
from the directory its own executable sits in.** The binary is in the Citizen
Compass root, so the process cannot reach another project's tree at all.

### TWO OF MY OWN ASSERTIONS WERE WRONG, AND THE SYSTEM WAS RIGHT

My harness reported two failures. **Both were my timing, not the watcher's
behaviour**, and I checked before writing a word of this:

- It gave the unknown-`From:` letter forty seconds to appear in `_needs_review`.
  The watcher was still working through the queue behind the letter I had
  deliberately jammed, and filed it at 19:50:08 — **eight seconds after my check
  gave up.** The file is there, with the reason on it.
- It looked for an error line during the induced failure. There is none, because
  **the watcher does not log one** — which is the finding above, not a failed
  condition.

**I am reporting this rather than quietly fixing the harness, because "the test
said FAIL and I decided it was fine" is exactly the reasoning that should never
go unwritten.**

---

## 3. EVERY TEST LETTER, CLOSED OUT AND NAMED

**Moved, not deleted (rule 1), all into one dated folder:**

    _to_delete\SYNTH_step_a_verification_20260910\

        correspondence_open_build_2026-09-10_SYNTH-A-do-not-action.md
        correspondence_open_build_2026-09-10_SYNTH-B-do-not-action.md
        correspondence_open_build_2026-09-10_SYNTH-B-do-not-action__20260910194909.md
        correspondence_open_audit_2026-09-10_SYNTH-C-do-not-action.md
        _needs_review_2026-09-10_SYNTH-C-do-not-action.md
        docs_2026-09-10_SYNTH-D-do-not-action.md

**The original path is preserved in each filename**, so where a letter had been
is recoverable from the close-out folder alone.

**Two supersede records were left where the system put them**, because they are
evidence of the run rather than litter:

    _to_delete\2026-09-10_SYNTH-A-do-not-action.md.superseded-20260910-194909
    _to_delete\2026-09-10_SYNTH-B-do-not-action.md.superseded-20260910-195005

**Confirmed: no file matching `SYNTH-*` exists anywhere outside `_to_delete\`.**
No tray, `docs/`, `_needs_review/` or archive still holds one.

---

## 4. YOUR EIGHT QUESTIONS

**Q1 — the switch file.** Neither exists, and neither parent folder exists:

    C:\Users\david\.cc-control\automation.switch        does not exist
    C:\Users\david\.cc-control\                          does not exist
    C:\Users\david\.citizen-compass\automation.switch    does not exist
    C:\Users\david\.citizen-compass\                     does not exist

**There are no contents to quote.** The launcher reads absent as OFF, so the
automation is fail-closed exactly as intended, and **it stays that way until you
create the file.** Nothing I build will ever write it.

**Q2 — token counts in `wake_log.jsonl`. The code writes them; the file does not
carry any yet, and I will not pretend otherwise.**

The only usage-bearing record in the file is the old shape:

    {"event":"wake_end","desk":"audit","at_utc":"2026-09-10T16:45:18.328460+00:00",
     "seconds":81.06,"exit":0,"usage_parsed":true}

`usage_parsed: true` and not one count — **your original complaint, still sitting
in the file.** `parse_usage` now writes a `wake_usage` record carrying
`input_tokens`, `output_tokens`, `cache_creation_input_tokens`,
`cache_read_input_tokens`, `num_turns`, `total_cost_usd` and `session_id`, proven
on a replica. **No wake has run since that change, so no such record exists.
First real wake produces the first one.**

**Q3 — the write restriction on the 16:43:55 UTC wake. Read from the log's own
argv, not from memory. The Adjutant is right.**

    flags actually present:
      --append-system-prompt  --output-format  --restricted
      --permission-prompts none
      --disallowedTools Bash,PowerShell,WebFetch,NotebookEdit,Task,Agent
      --add-dir

    --tools          ABSENT
    --allowedTools   ABSENT

**That run had no allow-list at all — only a deny-list of six tools.** Write and
Edit were not path-restricted in any way. **The wake that "worked" carried no
containment**, and the later `Edit(inbox/**)` probe is the only run that has ever
demonstrated one.

**Q4 — does the watcher survive a reboot?** **Registered, yes; observed across a
reboot, no.**

    triggers      Daily AND At-logon
    restart       999 retries at 1-minute intervals
    state         Running

**The logon trigger is what would bring it back after a reboot, and I have not
seen a reboot.** What I did see tonight is the restart policy working: I stopped
the task and it relaunched itself within a minute, unprompted. **That is evidence
for the restart policy and not for the logon trigger.** Inferred from the
registration, not witnessed — say the word and the honest test is a reboot.

**Q5 — does the pending binary validate `From:` against the same closed list?
Yes, and it is now the running binary. Proven live tonight, not read off the
source.** `From:` is lowercased, trimmed and looked up in the same `memoTrays`
map `To:` uses. **On an answered memo only** — an open letter with an odd `From:`
still routes on `To:`, because refusing working traffic over a header nobody has
ever filled in carefully costs more than it saves. **An absent `From:` means the
document is not a memo at all** and is filed as an ordinary document. Both
demonstrated in condition 3.

**Q6 — which of the tray's letters are still actionable.** It is **33 now**, not
32. **I can give you a confident answer for the ones this session acted on and I
will not guess at the rest tonight:**

    STILL ACTIONABLE, certain
      4   the watcher can lose a letter (the fsnotify rescan) - unstarted
      18  extend the sixth document check to the open trays - unstarted
      27  the stamp goes local, the 42% control needs a proposal
      29  find every other typed list, make every sweep report its coverage
      30  build the card mark, three states derived
      13  seven prices ruled - explicitly "none of it is for today"

    SPENT, certain - ruling applied or go-ahead used
      2, 3, 5, 7, 8, 11, 12, 14, 15, 16, 17, 20, 21, 22, 23, 24, 25
      (2 is the ACL letter you superseded yourself; 12 you closed in writing)

    NEEDS RE-READING BEFORE I CLASSIFY IT
      6, 9, 10, 19, 26, 28, 31, 32, 33

**That is roughly seventeen spent, six live, nine unclassified** — close to your
estimate of fifteen. **The auditable record of what was closed and why is the
deliverable and it is not this paragraph**; it comes with the reconciliation,
which does not delay anything and which I have not started.

**Q7 — does the launcher need to read `protected_folders.txt`?** **My answer is
no, and the reason is rule 14 rather than convenience.**

That file is the watcher's instrument: it governs what the watcher will
auto-process out of `inbox/`. **A second program reading the same file to decide
something different is two readers of one artefact drifting apart** — three times
paid for in this repository already.

**What the launcher needs is not that file. It is a write restriction that comes
from the command line, where the runtime enforces it** — the `Edit(inbox/**)`
form the probe measured. A woken desk should be unable to write outside its
allowance whatever any text file says. **If protected folders must also bind a
woken desk, the honest answer is to derive both from one place and give the
launcher its own allow-list built from it — not to have the launcher re-read the
watcher's file and hope the two readings agree.**

**Q8 — is `scripts/wake_desk.py` at 52,942 bytes the version that ran the three
wakes? No.** 52,942 is its size right now, and **every one of those changes
landed after the three recorded wakes:** `run_id` and `v:1` on every record,
`at_utc` stamped centrally, the master switch and its gate, the 78 exit contract
with `wake_refused` records, and the usage record. **The three wakes ran against a
substantially smaller earlier file. Nothing in this file has been exercised by a
real wake.**

---

## 5. WHAT I HAVE NOT DONE

**Step B is not begun.** Containment comes back to you as its own authorisation
request, written by me, and it is not in this letter.

**The master switch is untouched and still does not exist.** You activate it,
nobody else, after the fifteen-point test.

**The watcher is not connected to the launcher.** Nothing calls `wake_desk.py`
but a person at a keyboard.

**No database work, no deployment, no unrestricted execution, nothing committed,
nothing pushed.**

**The tray reconciliation and the descendant ACL scan are both unstarted**, in
that order, and neither delayed this.

## 6. ONE THING FROM YOUR OTHER LETTER, SO IT IS NOT LOST

Your letter to Architecture settles that the Perplexity sandbox gets no access to
the live tree, ever — **and corrects my §8: `C:\Users\Public` is world-readable
by inheritance and must not be the export location.** That correction is right
and I had it wrong. **No ACL on this machine has been changed by me, then or
now.**

*Build, 2026-09-11. Reporting and stopping, as ordered.*

---

ANSWERS:

**Taken, all of it. Step A is accepted and closed. Nothing in this letter needs
another word from me.**

## THE THREE THINGS I WANT ON THE RECORD

**Condition 2 was CAUSED, not simulated, and that is the whole difference.** You
jammed the destination with a locked file, watched routing fail for fifty-five
seconds with the open copy intact, then released it and watched the system finish
the job itself. **A test where the failure never happened is no test, and you made
the failure happen.**

**Your own command lied to you mid-swap** — "disabled" printed on a line that ran
unconditionally after the disable had failed. **You caught it and wrote it down
rather than moving past it.** That is the fourth silent-success this week and the
only one found while it was happening.

**Two of your assertions failed and the system was right both times.** Forty
seconds was your timing, not the watcher's fault, and it filed eight seconds after
you gave up. **"The test said FAIL and I decided it was fine" is the reasoning that
should never go unwritten** — your line, and it is the standard.

## THE EIGHT ANSWERS — TWO MATTER MORE THAN THE REST

**Q1. Neither switch file exists and neither parent folder exists.** So automation
is fail-closed by absence rather than by setting. **Correct, and it stays that way
until I create it by hand.**

**Q3. The wake that "worked" carried no containment at all.** No allow-list, so
writes were not path-restricted. **That is step B's whole justification and it is
now on the record from the log's own argv rather than from anybody's memory.**

**Q2 is the answer I wanted to see.** The code writes token counts; the file carries
none, because no wake has run since. **You said so plainly instead of quoting a
record that does not exist.**

**Q7 — you refused a second reader of `protected_folders.txt` on rule 14 rather than
on convenience. Accepted.** Two programs reading one artefact to decide different
things is three times paid for here already.

## NEXT

**Write the step B authorisation request. That is the only thing I am waiting on
from you.**

**Do not start containment, do not touch the brakes, do not connect anything.**

**The tray reconciliation can proceed whenever it does not delay step B** — your
seventeen-six-nine split is close enough to my estimate that I am not going to
argue with it. **The nine you will not classify tonight are the right ones to leave
alone; re-read them when you get there rather than guessing now.**

**And the correction in your section 6 is noted and it was mine to make, not yours
to apologise for.**
