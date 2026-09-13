# SPEC — THE BRAKES. Step 2. Executable by Build.

    from    C1, architecture
    date    2026-09-10
    why     `scripts/wake_desk.py` says in its own docstring that the brakes are
            deliberately absent and Architecture is specifying them. The Owner's
            GO memo says the same: *"the brakes come next and they are
            Architecture's to specify before you build them."* This is that
            specification.
    scope   the per-desk lock, the two ceilings, the per-wake spend cap, the
            switch, and the wake log they are all counted from. NOTHING ELSE.
            The card, the punch, the freeze and the detectors are steps 5 and 6.
    revised 2026-09-10, on his letter *specify the brakes now*. Sections 7, 8
            and 9 answer the five things he asked to be answered in it and the
            one he had not decided. Nothing above them changed.
    revised 2026-09-10 again, on his withdrawal of the dollar framing. SECTION
            4 IS REWRITTEN: the unit is tokens against his allowance, not
            dollars; the cap is a runaway wall this desk sets from measurement,
            not a budget he picks from a price. Nothing else reopened.
    revised 2026-09-10, third time. TWO CORRECTIONS AND ONE RULING:
            the ceilings count RESERVATIONS written before the launch, not
            wake_start records written at it (section 3); the switch has a
            path, an ON value and an exit contract (section 8), because it
            had none and Build found it. Nothing else reopened.
    revised 2026-09-10, fourth time, on an outside desk's runaway research
            (claude/ECHO_what-actually-stops-a-runaway-2026-09-10.md). A
            GLOBAL CONCURRENCY LIMIT was missing entirely — section 2A. The
            switch is renamed a PAUSE. Twenty is stated as a total, not a
            pace. The system is described as RISK-LIMITED, NOT ALLOWANCE-SAFE.
            Nothing else reopened.
    reads   claude/DESIGN_the-doorbell-the-job-number-and-the-punch-card-2026-09-10.md
            sections 4, 7, 8 and 15 are the authority. This spec makes them
            buildable and decides only what they left open.
    ON DISK because a desk that can only see files must be able to read anything
            it executes against. The claude.ai project copy is a MIRROR.

---

## 0. WHAT BUILD ALREADY HAS, AND THIS SPEC BUILDS ON IT RATHER THAN AROUND IT

`scripts/wake_desk.py` already writes `logs/wake_log.jsonl` with a `wake_start`
and a `wake_end` per launch, already derives the desk list from the trays, and
already carries `MAX_BUDGET_USD`. **Three of the four brakes attach to things that
exist.** Nothing here asks for a rewrite.

---

## 1. THE WAKE LOG IS THE COUNTER. THERE IS NO SECOND COUNTER.

**Both ceilings are counted from `logs/wake_log.jsonl` and from nothing else.**

Derived, never stored — the same rule as the desk list and the roll call. **A
separate counter file would disagree with the log the first time a run died between
the two writes**, and then the brake and the evidence would tell different stories
about the same night.

### THE LOG HAS ALREADY CHANGED SHAPE ONCE AND NOTHING RECORDS THAT

Read from the live file today, both records of the 2026-09-10 wake:

    wake_start   keys: at_utc, cmd, desk, event
    wake_end     keys: at_utc, desk, event, exit, seconds, usage_parsed

**The current `log_wake` calls write `label`, not `desk`.** So the file already
holds one shape and the script now emits another, **with no version field on either
and no way to tell them apart except by guessing from the keys present.**

**A count that skips a record it does not recognise undercounts the wakes, and an
undercounted wake is a ceiling that permits too many.** That is hard rule 12 in the
brake itself.

**REQUIRED:**

    every record carries  v: 1
    an unrecognised or unparseable line FAILS THE COUNT
    failing the count means NOTHING IS WOKEN, and it says why

**Do not migrate or rewrite the two existing records.** They are the evidence of the
first successful wake. Treat a record with no `v` as version zero, map `desk` to
`label`, and say in the code that this mapping exists only for those lines.

### THE FILE'S ABSENCE IS THE BAD CASE, AND IT NEEDS AN OPENING RECORD

Section 2 of the design: a fresh empty state and a wiped one are indistinguishable,
so the empty case is treated as the bad case. **Applied here it would mean a brand
new install can never wake anything**, which is not what that rule is for.

**So the file is opened once, deliberately, with a first record:**

    {"v":1,"event":"log_opened","at_utc":"...","by":"<who ran the install step>"}

**After that, a missing `wake_log.jsonl` is fail-closed and nothing is woken.**
Restarting a service and wiping the counter is the most ordinary troubleshooting
step there is, and it is exactly the moment a ceiling is near its limit.

---

## 2. THE PER-DESK LOCK

**One wake per desk at a time.** Section 4.

    path       logs/locks/<desk>.lock          derived desk names, never typed
    written    before the launch, by the LAUNCHER
    removed    at the end log, by the LAUNCHER

**TAKEN BY THE LAUNCHER, NOT BY THE WATCHER, AND THIS IS THE PART THAT WILL BE GOT
WRONG.** Today `wake_desk.py` is a thing a person types. At step 3 the watcher calls
it too. **If the watcher takes the lock, a hand-typed wake takes none and the two
collide on the desk nobody is watching.** One taker, at the point where the process
actually starts.

    contents   v, desk, mode, started_at_utc, pid, run_id, and the letter or
               job the wake was given

`run_id` is a value the launcher generates once and puts on the lock, on
`wake_start` and on `wake_end`. **Without it, two wakes of one desk in one day
cannot be told apart in the log**, which is the whole reason the lock exists.

### A STALE LOCK IS REPORTED, NEVER CLEARED

Section 4, and it is not negotiable: **clearing a lock automatically hides a death.**

    the lock exists and the pid is alive        the desk is working. Refuse the wake.
    the lock exists and the pid is gone         STALE. Refuse the wake, and file a
                                                notice to correspondence/open/owner/
    the lock cannot be read or parsed           the same as stale. Fail closed.

**The notice is not a wake.** Section 7. It wakes nothing and counts against neither
ceiling — otherwise a run of stale locks trips the ceiling and the system loses the
ability to say it has stopped.

**One notice per stale lock, not one per attempt.** A refused wake that files a fresh
letter every time turns one dead desk into a full owner tray by morning.

### AND WHO READS THAT REPORT — HIS QUESTION 3, AND IT IS THE RIGHT ONE TO ASK

**A report nothing reads is the shape this project keeps paying for.** Two readers, the
same pair as the heartbeat in section 10 of the design, and for the same reason:

    the Adjutant, at the start of every conversation   the fast path. It already
                                                       reads his tray; a stale lock
                                                       is one more line on a read
                                                       that is already happening.
    the nightly auditor control                        catches one that happened
                                                       overnight while nobody spoke
                                                       to anybody.

**Neither alone is enough and together they are.** And the roll call — section 18 of
the design — renders it, because a desk holding a stale lock reads as WORKING to
everything else and that is precisely the confusion this system exists to remove.

---

## 2A. ONE AUTOMATIC SESSION AT A TIME, ACROSS ALL DESKS

**This was missing and its absence was a real hole.** Section 2 gives every desk its
own lock and nothing anywhere limits how many desks run at once. **Six desks means six
concurrent sessions were permitted by this document as written.**

    GLOBAL CONCURRENCY = 1        one automatic session at a time, whatever desk

**Checked at reservation time, before the per-desk lock and before any launch.** Over
it, the wake is refused with `reason: "global_busy"` and the letter is withheld exactly
as a ceiling refusal is.

**It is the cheapest control here and it shrinks every other risk in the document.** It
is what makes the un-stoppable window in section 8 a single bounded run rather than
six, it makes ownership and recovery verifiable, and it costs throughput nobody is
currently using.

**One, deliberately, and not two.** The number moves on measurement, like every other
number here.

---

## 3. THE TWO CEILINGS

    twenty wakes per day, across all desks
    AND no more than five in any fifteen minutes

**Over EITHER, nothing is woken and he is told.** Section 7, his ruling, not to be
re-opened.

### THE DAY IS HIS DAY, NOT UTC

**Midnight to midnight in `America/Chicago`**, the same timezone already ruled for the
testing stamp on 2026-09-09.

**A UTC day boundary lands in the middle of his evening** and would put the back half
of one working session into the next day's budget. The log stores UTC — that is
correct and stays — and the day boundary is applied when counting.

### TWENTY IS A TOTAL, NOT A PACE — AND THE WHOLE DAY CAN GO IN FORTY-FIVE MINUTES

**Say it here so nobody reads the daily number as protection against a fast morning.**

    t = 0        five starts. The sixth is refused.
    t = 901s     the first five age out of the rolling window. Five more.
    t = 1802s    five more.
    t = 2703s    five more. TWENTY. The day is spent.

**Forty-five minutes, both ceilings satisfied throughout.** Arithmetic from an outside
desk, re-derived against this section.

**No third limit is being added yet.** A pacing allowance needs a number, and not one
day of real wake frequency has been measured — a figure picked now would be a guess
wearing a decimal point.

**TRIGGER: the first day the daily twenty is actually reached.** That day produces the
measurement and the number comes from it.

**When it is built, it goes UNDERNEATH five-in-fifteen and never instead of it** — a
token bucket of capacity five that refills continuously can permit more than five
inside some fifteen-minute window.

### THE FIFTEEN MINUTES IS A ROLLING WINDOW, NOT A CLOCK QUARTER

Five in *any* fifteen minutes. **Not five per quarter-hour** — that permits ten in two
minutes across a boundary, which is precisely the runaway the window exists to catch.

    count wake_start records with at_utc within the last 900 seconds

### THE RESERVATION IS WRITTEN BEFORE THE LAUNCH, NOT AT IT

**Counting from `wake_start`, which the launcher writes at launch time, is wrong and
makes the ceiling short by one.** If the process starts and that write fails, the wake
happened and the counter never saw it.

    1  RESERVE      write {"v":1,"event":"wake_reserved","run_id":...} durably and
                    re-check both ceilings against it. NOTHING HAS LAUNCHED YET.
    2  LAUNCH       start the process
    3  IDENTIFY     record the pid and observed start against the same run_id

**The ceilings count RESERVATIONS.** A reservation whose launch then failed still
spends the allowance, and that is correct rather than a bug: **a runaway that fails to
start twenty times is still a runaway.**

**A RESERVATION IS ALSO WHAT STOPS A DUPLICATE START.** A repeated filesystem event
for a letter already handled must not start a second run: **refuse a reservation for a
letter that already carries a completed one.** The per-desk lock covers the overlapping
case; this covers the one after the lock has released.

**A reservation with no matching start after a short grace is reported**, or a crash
between step 1 and step 2 quietly eats the day's budget.

*Found by an outside desk reviewing the routing question —
`claude/ECHO_the-routing-and-escalation-process-2026-09-10.md` — not by re-reading
this spec.*

### A PROBE AND ITS LETTER ARE ONE WAKE

Step 1 runs a containment probe before the letter. **Both are launches, both cost
money, both go in the log. They count as ONE against both ceilings.**

They are one attempt at one job. **Counting the launches rather than the job would
halve his twenty without anybody deciding to**, and he set twenty against work, not
against subprocess invocations.

**Both records carry the same `run_id`. The ceiling counts distinct `run_id`s.** That
is the mechanism and it is why `run_id` is required above.

### WHAT "TELLS HIM" MEANS

A memo to `correspondence/open/owner/` naming which ceiling, the count, and the window.
**One per ceiling per day.** Not a wake.

---

## 4. THE PER-WAKE STOP — AND IT IS NOT A BUDGET

**REWRITTEN 2026-09-10 on his correction.** The first version of this section did
arithmetic on `total_cost_usd` and put a forty-dollar day in front of him. **He is on
a subscription, `ANTHROPIC_API_KEY` is not set, and there is no bill.** Anthropic's
own documentation says the figure outright: *"Claude Max and Pro subscribers have
usage included in their subscription, so the session cost figure isn't relevant for
billing purposes."*

**The withdrawn framing measured something that does not exist for him. The unit is
tokens against his allowance.**

### THE CAP STAYS, AND ARCHITECTURE SETS THE NUMBER, NOT HIM

`--max-budget-usd` is the only per-run stop the runtime offers, so it stays. **Its job
is to kill a runaway inside one wake. It is a wall, not a budget**, and the fact that
it is denominated in dollars is an accident of the flag rather than a price anybody
chose.

    MAX_BUDGET_USD = "2.00"     STANDS

**Why, from measurement rather than preference:** the four measured runs came in
between three and nineteen cents. **Two dollars is about ten times the worst honest
run, so honest work never touches it, and a loop dies inside one wake rather than
running to the 600-second timeout.**

**Two walls, and they catch different failures:** the timeout catches a wake that
hangs; the cap catches one that spins productively.

**WHAT WOULD MOVE IT:** the first three real Windows wakes with their usage recorded.
Not an argument. **Do not put a day's worst-case dollar total in front of him again** —
his instruction, and this desk earned it.

### RISK-LIMITED, NOT ALLOWANCE-SAFE — SAY IT IN THOSE WORDS

**The brakes bound HOW OFTEN automation runs and HOW BIG ONE RUN CAN GET. They do not
bound what fraction of his allowance a day of automation consumes.**

**No enforceable link exists between this cap and his subscription allowance, and one
must not be invented.** Anthropic's own plan-usage figures are *"approximate and
computed from local session history on this machine, so usage from other devices or
claude.ai is not included"* — approximate, machine-local, and a display rather than a
bound.

**What actually protects him today is that twenty is a small number**, not a guarantee
from a control. Measured runs were three to nineteen cents and a minute or two each.

**The route out is already ordered:** once the usage block is logged, three measured
wakes give a real token figure per wake, and twenty times that is a measured estimate
instead of a guessed one. Still an estimate. Better than this.

### WHAT REACHES HIM IS TOKENS

    REPORTED     input, output, cache created, cache read, and the request
                 count when the payload carries one
    IN THE RECORD BUT NOT IN THE REPORT     total_cost_usd. Keep it - it is
                 useful for spotting a run that behaved strangely - but it is
                 not a figure he decides anything from.

**AND THE COUNTS MUST ACTUALLY BE STORED.** Today `wake_log.jsonl` records
`"usage_parsed": true` and not one token count. **The launcher parses the block,
prints it, and throws it away** — the sweep-timing defect again, in the same week it
was fixed there. **Nothing in this spec can be tuned until that is recorded.**

### TWO CAPS, ONE CEILING — SECTION 15

A daytime Code has a shell and its work is BIGGER, not more frequent. **One wake
ceiling for every desk; the cap is what differs.** The cap is a per-desk, per-mode
lookup exactly like `TOOLSETS`, **not a module constant** — same reason Build gave for
the tool sets: otherwise the first change to it is a rewrite of the thing that spends.

**DAYTIME CODE HAS NO CAP AND IS THEREFORE NOT WOKEN.** His ruling, taking this desk's
recommendation: **leave it unset and refuse the wake until it has been measured.** Fail
closed. No guess with a decimal point on it.

### AND THE REAL COST QUESTION IS NOT IN THIS SPEC AT ALL

`claude/FINDING_the-304000-is-the-rules-file-read-once-per-tool-call-2026-09-10.md`.
**CLAUDE.md is 624 of the prompt file's 699 lines and is re-read on every request of
every wake**; extended thinking has never been looked at; and a cache miss costs more
than a hit, which puts the fifteen-minute window in tension with the allowance.
**None of it is tuned before the usage block is logged.**

---

## 7. WHAT HAPPENS AT THE MOMENT A CEILING TRIPS — HIS QUESTION 2

**"It stops and tells me" is not a specification and he was right to refuse it.**

### THE CHECK HAPPENS BEFORE ANYTHING IS SPENT

**Before the lock is taken and before any process starts.** The twenty-first wake is
never launched, so it costs nothing and leaves no lock behind.

### WHAT IS ALREADY RUNNING IS NOT KILLED

**A wake in flight finishes.** Killing it would leave a desk's work half-done, a lock
held and tokens already spent for nothing. **The ceiling governs STARTING, not
stopping** — the same distinction as the switch.

### THE LETTER IS NOT LOST, AND THIS IS WHERE THE HOLE IS

The letter stays exactly where the watcher filed it. **Nothing is consumed and nothing
is deleted.**

**But section 4 of the design says a wake is a consequence of a successful filing,
never a scan of the trays — so a letter filed while the ceiling is up would never wake
anything again.** It would sit in a tray looking like ordinary post, and nothing would
report that it had been skipped. **That is this project's own recurring defect
arriving inside the brake built to prevent it.**

**THE FIX, AND IT DOES NOT REINTRODUCE A SCAN:**

    a withheld wake writes   {"v":1,"event":"wake_withheld","run_id":...,
                              "desk":...,"letter":...,"ceiling":"daily"|"window",
                              "at_utc":...}

**When the ceiling clears, the WITHHELD LIST is what resumes — oldest first — not a
tray scan.** The watcher replays a list it wrote itself. Nothing looks at the trays.

**And the replay is subject to the same ceilings**, so nineteen held letters cannot
dump at once the moment the clock rolls over.

### THE TWO CEILINGS DO NOT BEHAVE THE SAME WAY ON TRIP

    the fifteen-minute window    A THROTTLE. Self-clears as records age out of
                                 the window. Withheld letters replay on their own.
    the daily twenty             A STOP FOR THE DAY. Self-clears at midnight
                                 America/Chicago, or on his word, and nothing
                                 else clears it.

**They are different instruments and treating them alike would be wrong in both
directions.** Five in fifteen minutes is ordinary traffic arriving in a clump — his
own example is himself, on day one, dropping three memos at once. **Twenty in a day is
not traffic. It is a symptom**, and a stop that quietly lifts itself twenty minutes
later is not a stop.

**The notice says WHICH ceiling, the count, the window, and how many letters are
held.** One per ceiling per day.

### AND THE NOTICE PATH IS NOT THROTTLED — HIS QUESTION 4

**A notice into his tray is not a wake.** It wakes no desk, starts no process, and
counts against neither limit.

**Otherwise a burst of trouble silences the thing that reports trouble** — his words,
and it is the same failure as the watcher's heartbeat living inside the watcher.

**BUILD IT SO THE NOTICE PATH CANNOT REACH THE COUNTER AT ALL.** Not "remembers not to
count it" — a separate function that has no access to the ceiling code. A rule that
depends on somebody remembering it is a rule with one reader.

---

## 8. THE PAUSE — ONE SWITCH. AND IT IS A PAUSE, NOT A KILL SWITCH.

**ONE master switch. Not one per desk.**

**IT IS CALLED A PAUSE BECAUSE THAT IS WHAT IT IS.** It stops new starts. **It does
NOT terminate a session that is already running**, and anyone who calls it a kill
switch or a master stop will eventually rely on something it does not do.

**A terminate-running switch is NOT being built now.** A woken desk has no shell, and
one run is bounded twice — the spend wall and the ten-minute timeout — so the worst
thing this pause cannot reach is a single bounded run for at most ten minutes. **With
section 2A's global limit of one, that is the whole exposure.** Waiting ten minutes is
not an emergency; a Windows process supervisor is a component with its own failure
modes.

**TRIGGER FOR REVISITING: step 4, when Code gets a shell.** A shelled Code mid-build is
a different proposition and that is where a real terminate earns its keep.

    path        C:\Users\david\.cc-control\automation.switch
    read by     the LAUNCHER, before anything else, on every wake.
    written by  NOTHING. Created by hand, once, by him.
    off means   no desk is woken by anything. Mail still files. Work in hand
                still finishes. Nothing new starts.

**ONE CONTROL FOLDER, TWO FILES.** `.cc-control\` also holds `presence.marker` when
step 4 arrives — section 15 of the design has the identical hole and this closes both
rather than leaving the second to be found in a fortnight.

**Why not `.citizen-compass\`:** it differs from the repository folder by one
character. **A control file must not be one keystroke from being inside the thing it
controls** — mistyped one way nothing ever wakes and it reads as a broken launcher;
mistyped the other way it lands where a woken desk can write it.

**A single constant at the top of `wake_desk.py`. No lookup, no search order, no
fallback. A SWITCH WITH TWO POSSIBLE LOCATIONS IS NOT A SWITCH.**

**Nothing writes it, ever — including a "first run creates it" convenience.** That is
the switch granting itself.

### WHAT MEANS ON

    THE FIRST LINE, exactly:  on
    anything else                 OFF
    absent, unreadable, empty     OFF

**Exact match, case-sensitive.** An unknown value is not a permission — rule 17.

**Trim surrounding whitespace and strip a leading UTF-8 BOM before comparing.** That
is normalising a file format, not guessing at intent: Notepad writes a BOM, and
without this he creates the file, it reads OFF, and nothing tells him why.

**Lines after the first are ignored and may hold a note** — why it is off, when it was
turned on.

**THE REFUSAL PRINTS WHAT IT ACTUALLY READ, byte-for-byte, with the length.** Not "the
switch is off" but *"first line is `On` (2 bytes), which is not `on`"*. **A fail-closed
control that will not say what it saw is the hardest thing to debug at two in the
morning, and this one is built to be read at exactly that hour.**

**With nothing on disk, nothing wakes. Accepted deliberately: automation begins with a
positive act.**

### WHY NOT PER-DESK, AND THE COST OF THAT ANSWER

**A per-desk switch has a state that can be wrong in a way one switch cannot: three on
and one off, set weeks ago and forgotten.** And a desk switched off individually looks
exactly like a desk with nothing to do — **which is the defect this entire design is
named after.**

**The thing a per-desk switch is for is already covered twice.** One desk looping is
what the ceilings catch, in fifteen minutes rather than at midnight; one desk that
must not run is what not giving it work achieves.

**THE COST, STATED PLAINLY: with one switch, stopping one broken desk stops all
four.** That is the trade and it is worth it, because the switch's real job is the
two-in-the-morning stop where being unmistakable beats being precise.

**WHAT WOULD CHANGE THE ANSWER:** if he finds himself throwing the master switch
because of ONE desk more than two or three times, that is a measurement result and the
per-desk switch has earned its way in. Not designed for now.

### OFF IS VISIBLE OR IT IS NOT A SWITCH

**The roll call shows it.** Otherwise "every desk is idle" and "the automation is off"
are the same line, and he would be reading a quiet system as a working one.

---

## 8A. THE EXIT CONTRACT — THREE CODES, AND THE REASON IS NOT ONE OF THEM

**A caller that cannot tell a deliberate refusal from a crash will eventually treat
one as the other.** Under automation that means ignoring a real fault, or waking him
for a working brake. Build found the divergence: the two guards refuse with 78 and
`wake_desk.py` refuses with 1 for everything.

    0     the wake RAN and the launcher finished its scoring
    78    REFUSED ON PURPOSE. Nothing launched.
    1     anything else. A crash, a bug, an unexpected state.

**78 because the two guards already use it and three programs agreeing is worth more
than a better number.** It is `EX_CONFIG` conventionally — *policy says no* — which is
the right shape for every refusal here.

**Every deliberate refusal returns 78:** switch off, either ceiling, lock held, lock
stale, missing wake log, unrecognised log record, no cap registered for that desk, no
tool set registered for that desk and mode, and the API-key guard.

### THE REASON DOES NOT GO IN THE NUMBER

**One code for all of them. Do not build a numeric taxonomy of refusal reasons** — it
becomes a second source of truth, it drifts from the log, and nobody remembers what 82
meant. **The caller needs one bit: did anything run. The human needs the reason, and
the reason belongs where reasons are readable.**

### SO A REFUSAL IS A RECORD, NOT ONLY AN EXIT CODE

**A refused wake that leaves nothing on disk is invisible to the roll call**, and
"nothing woke today" and "the switch has been off since Tuesday" would look identical.

    {"v":1,"event":"wake_refused","run_id":...,"desk":...,
     "reason":"switch_off"|"ceiling_daily"|"ceiling_window"|"lock_held"|
               "lock_stale"|"log_missing"|"log_unreadable"|"no_cap"|
               "no_toolset"|"api_key_guard",
     "detail":"<what it actually read or counted>","at_utc":...}

**Exit 78 and that record are written together or neither is.**

**`wake_withheld` stays as the name for the ceiling case specifically** — a withheld
letter replays and a refusal does not, and that distinction is load-bearing in section
7.

---

## 9. HOW EACH BRAKE IS PROVEN — HIS QUESTION 5, AND IT IS SECTION 9'S STANDARD

**A brake that has never fired is a brake nobody has tested.** Each one is tripped
deliberately and the pass condition is a REFUSAL — never "nothing bad happened."

**A test where the brake was never reached is NO TEST, and it is reported as no test
rather than counted as a pass.** That is the Owner's own measured finding from Run C
and it applies to every line below.

### THE COUNTER TESTS RUN ON A REPLICA, NOT ON THE LIVE LOG

**Seeding the live `wake_log.jsonl` with synthetic records would corrupt the evidence
file with fakes, and marking them as fakes would let the counter skip them — which
defeats the test.**

**So: a copy of the repository, exactly as the Owner ran his four headless runs.** The
established method here, and it costs nothing.

    THE LOCK
      place a lock by hand for a desk with a LIVE pid, request a wake
      PASS: refused, nothing launched, no notice
      then a lock with a pid that does not exist
      PASS: refused, and EXACTLY ONE notice in the owner tray. Request it three
            more times - still exactly one notice.

    THE FIFTEEN-MINUTE WINDOW                     on the replica
      seed five wake_start records inside the window, request a sixth
      PASS: the sixth never launches, a wake_withheld record is written,
            the notice names the window
      then age the seeds past 900 seconds and let it replay
      PASS: the held letter resumes from the withheld list, with no tray scan

    THE DAILY TWENTY                              on the replica
      seed nineteen. Request one.   PASS: it LAUNCHES. Twenty is allowed.
      request one more.             PASS: refused.
      OFF-BY-ONE IS THE LIKELIEST DEFECT IN A COUNTER and both halves of that
      boundary have to be shown, not just the refusal.

    THE MISSING LOG                               on the replica
      delete wake_log.jsonl entirely, request a wake
      PASS: refused, and it says the log is missing rather than counting zero

    THE UNKNOWN RECORD                            on the replica
      append a line with no `v` and keys matching neither shape
      PASS: the count FAILS and nothing is woken. Not skipped.

    THE RUNAWAY WALL                              THIS ONE MUST BE REAL
      the runtime enforces it, not our code, so a replica proves nothing.
      set the cap BELOW the known cost of a real wake - 0.01 - and launch one
      PASS: the runtime refuses or truncates, and the launcher REPORTS it
      cost: pennies, and it is the only way to know the flag bites

    THE SWITCH
      switch off, file a letter that would normally wake a desk
      PASS: nothing launches, the letter is still in the tray, the roll call
            says OFF
      AND: with the switch off, a woken desk must TRY to write the switch and
           be REFUSED - section 15's test shape, because a switch a desk can
           reach is not a switch

**Report every one as pass, fail, or NOT PERFORMED.** A brake with no result is not a
brake that passed.

---

## 5. WHAT IS DELIBERATELY NOT IN THIS SPEC

**The card, the punch, the stamp, the freeze** — step 5. The ceiling is what stops a
runaway; the card is a filename convention, a stamp format, a durable counter and a
freeze. The cheap thing goes first.

**The silence detector and the untouched-job rule** — steps 4 and 6.

**The heartbeat** — step 6.

**Presence and mode selection** — step 4, section 15. `wake_desk.py` correctly leaves
mode unwired and defaults to unattended; nothing in this spec changes that.

**The write rule and containment** — that is step 1 and it is live work. See the memo
to Build of the same date, and the correction in it: **the run that actually succeeded
carried no path restriction on writes at all.**

---

## 6. THE ORDER WITHIN STEP 2

    1  run_id and v:1 on every record          everything else counts on it
    2  the switch                              one file, one read. Cheapest
                                               thing here and the only one that
                                               stops everything.
    3  the per-desk lock                       prevents the worst concurrent
                                               mess
    4  the two ceilings                        counted from the log, with the
                                               withheld list
    5  the spend cap lookup                    the shape now, his number when
                                               he answers

**Each one is TRIPPED before the next is started.** Section 9.

**One at a time, each proved before the next.** The Owner's standing instruction on
step 2's flag swap applies to the whole of step 2: **a change that rides along with
another change has two possible causes when it fails.**

*C1, 2026-09-10.*
