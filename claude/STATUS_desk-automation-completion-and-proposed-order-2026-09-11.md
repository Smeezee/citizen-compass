# Citizen Compass Desk Automation — Completion Status and Proposed Order v1

    from     the Adjutant desk
    date     2026-09-11
    scope    evidence only. No order was sent, no letter answered, moved or
             closed, no spec or script touched, nothing in the queue reordered.
    method   trays, specs, launcher source, watcher source, wake log, Code's
             handoff archive, and the governing records read directly.
    limit    THIS DESK HAS NO SHELL. Nothing below was re-run. Where a component
             is recorded as working, the evidence and its date are named and it
             is labelled as previously demonstrated — not as reverified today.

    LABELS   VERIFIED TODAY      read or observed directly during this review
             DEMONSTRATED        proved by Code, with the evidence named
             IMPLEMENTED         code exists; behaviour not reverified
             SPECIFIED           written down, not built
             UNKNOWN             no evidence either way
             BLOCKED             finished work waiting on a decision

---

## 1. CURRENT ARCHITECTURE

**One machine. Files in folders. No broker, no queue, no database in the path.**

A memo is written and dropped in `inbox/`. A Go service, `inbox_watcher.exe`,
running as a scheduled task, reads the header and moves the file into
`correspondence/open/<desk>/`. To answer, a desk edits the same file under an
`ANSWERS:` line, sets `Status: Answered`, and drops it back in `inbox/`.

Routing requires `To:`, `From:` and `Subject:` inside the first 4000 characters or
the text is not treated as a memo. The addressee list is closed — six trays:
architecture, build, research, audit, design, owner. An unknown addressee goes to
`_needs_review/` rather than being guessed at. A filename with no leading ISO date
gets one prefixed.

**A second program, `scripts/wake_desk.py`, can start one desk headless.** It is a
thing a person types. **Nothing calls it.** That single fact is the difference
between what exists and what was asked for.

**The desks themselves are Claude sessions.** A desk started by the launcher has no
shell — the tools that run commands are removed before it starts. It can read,
search, and write one letter. That is deliberate and it is how rule 9 is enforced.

---

## 2. COMPONENT STATUS

### THE MAIL PATH

**Mail watcher — VERIFIED TODAY.** Running as a service throughout. Roughly twenty
memos were filed correctly during this session, within seconds of each drop,
including three that were answered and moved. `watcher-go/memo.go` read directly.

**Desk routing — VERIFIED TODAY.** `memoDestination` routes on a closed map of six
trays. Unknown addressee refused to `_needs_review/`. Observed working on every
memo sent today.

**Answer routing — BLOCKED.** The defect is confirmed by reading the source:
`memoDestination` tests `Status: Answered` **before** it looks at `To:`, so every
answered memo goes to `correspondence/answered/` regardless of who asked. Nine of
C1's letters to the Owner landed there today and none reached his tray.

**The fix is built and proved.** Code reports five tests written and run against the
old router first — all five failed, as they must — then passing against the new one;
nine of nine on a real copy of the tree, including the answer reaching the Owner's
tray, the superseded copy kept rather than deleted, and an unknown sender refused
without moving anything. **DEMONSTRATED, 2026-09-10, memo
`the-answer-routing-is-built-and-proved-the-swap-is-yours`.**

    running now   C:\Users\david\citizen-compass\inbox_watcher.exe  UNTOUCHED
    built, staged watcher-go\inbox_watcher_pending_20260910.exe

**The swap has not happened and is waiting on the Owner.**

**`From:` validation — SPECIFIED, built in the pending binary, not reverified.**
The live `memo.go` extracts `From:` and validates nothing. The new routing decides
the destination from it, so it must be checked the way `To:` is. Code reports the
test `TestAnAnsweredMemoFromAnUnknownDeskIsRefused` failing against the old router
and passing against the new.

**Open-copy cleanup — BLOCKED, same swap.** `clearOpenCopy` would delete the answer
it just filed. Code demonstrated it: ran the old sweep forty times and it took the
answer on nine of them. **Intermittent, which is why nobody found it by reading.**

### THE LAUNCH PATH

**Manual desk launcher — DEMONSTRATED, 2026-09-10.** `scripts/wake_desk.py`, now
52,942 bytes. Three real launches recorded in `logs/wake_log.jsonl`: a wake at
16:43:55–16:45:18 UTC, exit 0, 81 seconds, reply reached the Owner's tray; then a
containment probe and a second letter at 17:35. **Read today; not re-run.**

**Automatic desk wake-up — SPECIFIED, NOT BUILT.** Design section 4 defines the wake
as a consequence of a successful filing. The watcher does not call the launcher.
**This is the single missing piece between the current system and the intended
result.**

**Adjutant intake — DOES NOT EXIST, and it is not merely unbuilt.** See section 5.

**Manual fallback — VERIFIED TODAY, and it is the only mode in operation.**
Every desk runs because the Owner opens its window and types. That is the fallback
and it is currently the whole system.

### THE BRAKES

**Master switch — IMPLEMENTED, not reverified, and its file state is unverifiable
from this desk.**

    the code says   SWITCH_PATH = ~\.cc-control\automation.switch
    default         OFF. Absent, unreadable, empty or any value but exactly
                    "on" means off. Case-sensitive.
    written by      nothing, ever. Created by hand, once.

**The two reported paths — the contradiction is resolved and the code is right.**
`wake_desk.py` uses `.cc-control\`, and carries a comment explaining why
`.citizen-compass\` was rejected: it differs from the repository folder by one
character, so mistyped one way the switch never exists and nothing wakes, mistyped
the other way it lands where a woken desk could write it. **The `.citizen-compass`
path appears only in prose — in Code's own summary and in this desk's earlier
memo — never in executable code. Both prose references are wrong.**

**Neither switch file could be checked.** `C:\Users\david\.cc-control\` is outside
every folder connected to this session, so existence and contents are **UNKNOWN to
this desk** and must be answered by Code.

**Per-run spending cap — IMPLEMENTED, never tripped.** `MAX_BUDGET_USD = "2.00"` is
in the launcher. The runtime enforces it, not our code, so it has never been shown
to bite. Spec section 9 requires a real run at `0.01` to prove it.

**Twenty per day — SPECIFIED, NOT BUILT.**
**Five in fifteen minutes — SPECIFIED, NOT BUILT.**
**One active run per desk — SPECIFIED, NOT BUILT.**
**One active run globally — SPECIFIED, NOT BUILT.** Spec section 2A, added after
outside research found it missing entirely: six desks means six concurrent sessions
were permitted by the design as written.

### THE CARD, THE LOOP, THE ESCALATION

**Permanent job number — SPECIFIED, NOT BUILT.** Design section 1.
**Handoff counter (punch and stamp) — SPECIFIED, NOT BUILT.** Design section 2.
**Loop detection — SPECIFIED, NOT BUILT.** Design section 6, and it names the
ceilings as the primary defence rather than the card. Neither is built.
**Freeze and Owner escalation — SPECIFIED, NOT BUILT.** Design section 3.

### THE RECORD

**Audit record — PARTIALLY IMPLEMENTED.** `logs/wake_log.jsonl` exists and carries
`wake_start` and `wake_end` per launch. Code reports adding `v:1`, `at_utc` and a
`run_id` shared by a probe and its letter, and reports that the usage block now
reaches the log — **previously it recorded `usage_parsed: true` and not one token
count.** Both IMPLEMENTED, neither reverified.

**The log has already changed shape once and the old records are still in it.** Two
records use `desk`; the current code writes `label`. The spec requires that
unrecognised records **fail the count** rather than being skipped, because a skipped
record undercounts wakes and an undercounted wake is a ceiling that permits too
many.

**Crash recovery — SPECIFIED ONLY.** The reservation-before-launch sequence, the
grace check for a reservation with no start, and the refusal to double-start a
letter that already carries a completed reservation are all in spec section 3.
None built.

**Restart after reboot — UNKNOWN.** `setup_watcher_task.ps1` exists, so the watcher
is probably registered as a scheduled task and probably survives a reboot. **Nobody
has tested it and this desk cannot.** The launcher is not a service and would not
restart at all.

---

## 3. THE CURRENT QUEUE

### WAITING ON SLEVEN — three letters in `correspondence/open/owner/`

    the answer-routing swap        built, every gate met, binary staged
    the failed-rotations number    C1 needs it to finish the escalation rule
    two desks have lost the shell  his machine, connection or tooling

### BUILD — thirty-two open letters

**Genuinely live, in the order they now sit:**

    1  file the ACL audit to disk           ALREADY DONE, 19:24:50. This desk's
                                            letter of 20:44 is redundant and
                                            should be closed as superseded.
    2  the launcher write rule is wider
       than the watcher's                   C1 calls it step 1
    3  the brakes spec gained three
       sections and the switch is decided   C1
    4  the watcher can lose a letter and
       only a log line would say so         C1, 19:20, new finding
    5  the remaining brakes items           per-desk lock, global concurrency,
                                            both ceilings, the cap lookup

**Ten older letters queued behind automation**, oldest 2026-09-07: the stop hook,
the card mark, the typed-list sweep, the sweep-time blocker, the seven RSI prices,
Raptor, the sixth document check, the 42-percent control.

**And roughly fifteen are spent** — rulings already applied, corrections already
taken, go-aheads already used. **This is a finding, not housekeeping.** The tray is
now hard to read; it took three passes to separate the five live items from the
rest, and the roll call this system is meant to produce would render the same
confusion.

### ARCHITECTURE — empty

One letter from 2026-09-08, the sweep-time composition question, open eight days.

### AUDIT — one letter

The throwaway test letter. It has been told to close it and has not been woken since.

### NOT YET ROUTED — the two new jobs

    Perplexity export design    unrouted. Architecture's, not Build's.
    descendant ACL scan         unrouted. Build's.

### CONFLICTS

**None found between existing orders.** The one redundancy is item 1 above.

**One ordering hazard:** the answer-routing swap and the brakes both change how a
wake behaves. The spec's own rule — *a change that rides along with another change
has two possible causes when it fails* — means they must not ship together.

---

## 4. CONTRADICTIONS AND UNKNOWNS

**The switch path in prose disagrees with the switch path in code.** Resolved above;
the code is authoritative and both prose references are wrong.

**The switch file itself is unverified.** Outside every connected folder.

**`wake_log.jsonl` holds two record shapes and nothing distinguishes them** except
which keys are present.

**The successful wake had no write-path restriction.** Recorded in
`docs/CURRENT-STATE.md`: the command that succeeded carried no `--tools` and no
`--allowedTools` — only `--restricted`, `--permission-prompts none`, a deny list and
`--add-dir <repo root>`. **Containment is an open hole, not a solved one**, and the
difference between that run and the Linux run that was denied is two variables, not
one. **Recorded as unexplained.**

**`protected_folders.txt` has exactly one reader.** The watcher honours it at any
depth; the launcher has never heard of it.

**Restart-after-reboot has never been tested by anyone.**

**Whether the claude.ai project was ever backfilled** for the 2026-08-27 to
2026-09-07 gap is unknown.

---

## 5. BLOCKING DEFECTS

**B1. A desk cannot reply to anybody.** Until the swap, every answer lands in an
archive nobody reads. **This blocks step 7 of the intended result outright** and it
is already costing whole days.

**B2. Nothing wakes a desk.** Blocks steps 2, 5 and the entire purpose.

**B3. The Adjutant cannot be woken at all, for two separate reasons.**

*Its boot prompt is unreachable.* Every desk the launcher can start needs a charter
on disk that the launcher can read. C1 and C5 have one in `claude/`. **The
Adjutant's charter lives in `CCDesk-logs\ADJUTANT.md`, outside the repository**, and
`BOOT_PROMPTS` in the launcher registers exactly one desk — audit.

*It has no intake location.* **The Adjutant's tray is the Owner's tray** — a
deliberate decision of 2026-09-08, on the reasoning that everyone addressing the
Owner is addressing this desk. So step 1 of the intended result would have Sleven
dropping requests into the same folder desks drop answers into.

**B4. No containment.** The wake that worked had no write-path restriction of any
kind. An unattended desk today could write anywhere in the repository.

**B5. No concurrency limit of any kind.** Neither per-desk nor global.

---

## 6. THE FOUR ARCHITECTURE QUESTIONS, WITH RECOMMENDATIONS

**These are recommendations from this desk. None is decided and none is implemented.**

### 6.1 WHERE OWNER INTAKE SHOULD LIVE

**Recommendation: a separate `correspondence/open/adjutant/` tray, and the Owner tray
becomes outbound-only.**

The current arrangement conflates two directions in one folder. Intake is *Sleven →
the machine*; the Owner tray is *the machine → Sleven*. Once mail flows both ways
automatically, a folder that is both is a folder where nobody can tell what is
waiting for whom.

**The cost, stated plainly:** it reverses a decision of 2026-09-08 that was made for
a good reason — one tray, no new upkeep, everyone addressing the Owner is addressing
this desk. **That reason was sound when the Adjutant was a person-driven session and
it stops being sound the moment the Adjutant is woken by a program.**

**The alternative, if reversing that is unwelcome:** keep one folder and separate by
message type rather than location — a `Type: Request` header that only Sleven's
letters carry. **This desk does not recommend it.** It makes correctness depend on a
header being present rather than on a file being in a place, and a missing header
would route a request as an answer.

### 6.2 WHERE THE ADJUTANT'S CHARTER MUST LIVE

**Recommendation: the canonical charter moves to `claude/PROMPT_boot-an-adjutant.md`,
inside the repository, beside C1's and C5's.**

The launcher reads boot prompts from `claude/`. Reaching `CCDesk-logs` would require
widening its read boundary to a second tree outside the repository — the same
boundary argument that keeps the switch outside it.

**`CCDesk-logs\ADJUTANT.md` becomes a pointer, not a copy.** Two copies of a
charter is rule 14 exactly, and this desk has already watched that file lose four
rules in one day to a second writer.

**One caveat that must not be lost:** the charter describes a desk that signs in the
Owner's name and whose existence is concealed from every desk but Audit. Moving it
into `claude/` puts it where C1 and Code can read it. **That is a disclosure
decision and it is Sleven's, not this desk's.**

### 6.3 SEPARATE FOLDERS, TYPES, OR ROUTING RULES

**Recommendation: separate folders, and deterministic routing that does not depend on
a header being present.**

The pending answer-routing fix already establishes the principle — a memo's
destination is derived from `Status` plus a validated `From:`. **Intake should
follow the same shape: the tray a letter sits in determines what it is.** A folder
cannot be forgotten, mistyped or truncated past the 4000-character header window.

### 6.4 WAKING THE ADJUTANT WITHOUT GIVING IT A SHELL

**Recommendation: no new capability is needed. Wake it with the unattended tool set
already proved.**

**The Adjutant is the one desk whose entire job is reading and writing letters.** It
needs Read, Glob, Grep and Write, which is exactly the set the successful wake used.
It needs no shell, no database, no git, no deploy.

**Two things it does need that no other desk needs**, and they are both boundary
questions: read access to `CCDesk-logs` for the desk day pages, and read access to
whatever holds the switch state so it can report OFF in the roll call. **Both argue
for the roll call being produced by the launcher or the watcher and handed to the
Adjutant as text, rather than the Adjutant being granted two new read boundaries.**

---

## 7. PROPOSED BUILD ORDER

**Each step is proved before the next begins. A change that rides along with another
change has two possible causes when it fails.**

    STEP A   THE SWAP                                    needs Sleven's word
             Replace the watcher with the pending binary. Correct answer
             routing and validated From: arrive together because they are one
             binary. PROVE: an answer reaches the sender's tray on the LIVE
             tree; the open copy survives; an unknown From: fails closed.
             ROLLBACK: the current binary, kept under a dated name.

    STEP B   CONTAINMENT                                 Build
             Establish what write restriction the successful wake actually had
             and give the launcher one. Nothing unattended runs until a desk
             has been made to TRY a write outside its folder and be refused.

    STEP C   THE BRAKES, IN THE SPEC'S OWN ORDER         Build
             1 run_id and v:1 on every record, and the token counts stored
             2 the switch, read before anything else
             3 the per-desk lock, plus global concurrency of one
             4 both ceilings, counted from reservations, with the withheld list
             5 the spend cap as a per-desk lookup
             Each one TRIPPED deliberately before the next is started.

    STEP D   THE ADJUTANT'S BOOT PATH                    needs Sleven's decision
             6.2 and 6.1 settled, the charter moved, the intake tray created.
             Nothing here runs; it is placement.

    STEP E   THE DOORBELL                                Build
             The watcher calls the launcher on a successful filing. THIS IS THE
             MOMENT IT BECOMES AUTOMATIC and it is deliberately last of the
             mechanisms.

    STEP F   THE CARD AND THE FREEZE                     Build
             Job number, punch, stamp, four and freeze, Owner escalation.

    STEP G   THE DETECTORS                               Build
             Forty-five minutes silent, twelve hours untouched, and a heartbeat
             read by something outside the watcher.

**Nothing in steps E to G runs with the switch on until step H.**

    STEP H   ACTIVATION                                  Sleven only
             The switch is created by hand, once, by him.

---

## 8. PROPOSED VERIFICATION ORDER — THE FIFTEEN-POINT TEST

**Run entirely on synthetic letters, on a copy of the tree, except where the spec
says a control can only be proved live.** A test where the control was never reached
is **NO TEST** and is reported as such, never counted as a pass.

    1   one intake letter creates one job          job number appears once
    2   the Adjutant starts at most once           one run_id, one lock
    3   the order reaches exactly one desk         one tray, no copies
    4   the destination desk starts at most once   reservation refuses the second
    5   the answer returns to the sender           STEP A already proves this
    6   the open copy clears only after routing    kill the move mid-way; the
                                                   open copy must survive
    7   an invalid or missing From: fails closed   refusal observed, nothing moved
    8   an ambiguous destination fails closed      _needs_review, nothing moved
    9   a duplicate letter creates no duplicate    replay the same filesystem
        work                                       event; one reservation only
    10  a loop reaches its limit and freezes       two synthetic desks exchanging
                                                   valid answers; four punches,
                                                   freeze, Owner tray
    11  ceilings block further starts              seed 19 then 20 then 21; and
                                                   six inside fifteen minutes
    12  the switch off prevents launching          and a woken desk must TRY to
                                                   write the switch and be refused
    13  a crash leaves recoverable evidence        interrupt after reservation,
                                                   then after launch. No refund,
                                                   no duplicate.
    14  every transition carries one job number    the whole history in one file
    15  nothing else is affected                   no database, no deploy, no
                                                   other project. The Looking
                                                   Project is excluded entirely.

**Proof-of-capability, and it applies to all fifteen:** each test is first run
against the code *before* the control exists, or against a deliberately blinded
version, and must **fail**. Code has already established this method twice — five
routing tests failed against the old router, and the change detector was proved by
blinding it.

---

## 9. DECISIONS REQUIRED FROM SLEVEN

    1  The watcher swap. Everything downstream waits on it.
    2  The failed-rotations number, and whether the first filing spends a
       delivery.
    3  Owner intake: a new adjutant tray, or one folder with typed messages.
    4  Whether the Adjutant's charter may move into `claude/`, where C1 and
       Code can read it. THIS IS A DISCLOSURE DECISION.
    5  Where the two new jobs sit. Recommendation: export design to C1 now,
       in parallel, costing the critical path nothing; ACL scan to Build last.
    6  Whether Build's fifteen spent letters may be closed.

---

## 10. EXACT QUESTIONS FOR CODE

    Q1   Does `C:\Users\david\.cc-control\automation.switch` exist, and what
         are its exact contents, byte for byte? Does
         `C:\Users\david\.citizen-compass\automation.switch` exist at all?
    Q2   Does `logs/wake_log.jsonl` now carry token counts, or still only
         `usage_parsed`? Quote one record.
    Q3   What write restriction did the wake of 16:43:55 UTC actually have?
         The record says no `--tools` and no `--allowedTools`. Confirm from
         the log, not from memory.
    Q4   Is the watcher registered as a scheduled task that survives a reboot?
         Has that ever been observed, or is it inferred from the setup script?
    Q5   Does the pending binary validate `From:` against the same closed desk
         list that `To:` uses, and what happens to a memo whose `From:` is
         absent entirely?
    Q6   Which of the thirty-two letters in your tray do you consider still
         actionable? List the numbers only.
    Q7   Does `protected_folders.txt` need a second reader in the launcher, or
         is the write rule sufficient on its own?
    Q8   Is `scripts/wake_desk.py` at 52,942 bytes the version that ran the
         three recorded wakes, or has it changed since?

---

*Adjutant, 2026-09-11. Evidence only. Nothing sent, nothing changed.*
