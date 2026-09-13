# DESIGN — the doorbell, the job number, and the punch card. Executable by Build.

    from    C1, architecture
    date    2026-09-10
    order   Sleven, 2026-09-10: automation first. The ten wake rules are his.
            The card, the two counters, four punches and the freeze are his,
            decided, and not to be re-opened.
    numbers ALL SET. Four punches. Forty-five minutes of silence. Twenty wakes a
            day AND no more than five in any fifteen minutes. Twelve hours
            untouched. A per-wake spend cap, section 8. Every one is a starting
            number he expects to move from measurement rather than argument.
    revised 2026-09-10 evening, on his four holes and one limit. Sections 7, 8,
            9, 11 and 12 are new or rewritten. Nothing else reopened.
    revised 2026-09-11 — HE RULED BOTH CARD NUMBERS. Section 3 gains them:
            TWO failed correction rounds escalate to him, and HIS FIRST FILING
            SPENDS NO DELIVERY. The four becomes a runaway backstop rather
            than the escalation trigger. Nothing else reopened.
    revised 2026-09-10 later, on his two requirements — blocked must not look
            like idle, and the roll call. Sections 17, 18 and 19 are new; the
            build order in 16 gained one column. Nothing else reopened.
    THIS FILE LIVES ON DISK. The claude.ai project copy is a MIRROR. A desk that
            can only see files must be able to read anything it executes against,
            and this document not being on disk cost both desks a night.

---

## 0. WHAT HE SOLVED THAT THIS DESK DID NOT

Recorded first because it changes who was right.

**This desk found the two-desk loop and could not close it.** The answer offered
was to count wakes per desk pair. **He rejected it with a better reason: a pair
count misses three desks going round in a circle.** One card on the job catches
that and everything else.

**He found the hole in his own answer before anyone else did** — *a desk that
answers by creating a NEW file starts a fresh count, and the loop runs forever with
a clean card every lap.* **That single behaviour makes everything else here
decoration.** Section 6 is about nothing else.

**The number in the filename resolved a conflict in his own earlier ruling.** The
2026-09-08 ruling kept returns out of `inbox/` because the watcher renames what it
files. **With the number in the name, the watcher preserves the number and may
change the rest**, so returns go through the mail like everything else.

**And he found four holes in this document by walking it as a builder and running
four real headless sessions against the arguable parts.** All four are carried
below. **One of them — the watcher's own death — was in the superseded version of
this design and this desk dropped it in the rewrite.**

---

## 1. THE JOB NUMBER

**Issued once, at first filing. Never changes. Lives in the filename.**

    0417_the-links-control-never-saw-the-new-page.md

**In the name so a number can be said out loud and something fetches the file.**
It is also what lets the watcher rename the rest of the filename freely without
losing the thread.

**The file is passed around and edited in place. It is never remade.**

---

## 2. THE TWO COUNTERS

    THE PUNCH    the watcher marks the job every time it files it to a desk.
                 The watcher's punch is the authority.

    THE STAMP    the desk writes one line before passing the file back. Always
                 the same shape, machine-readable. Which desk, and when.

**A stamp written as prose cannot be counted and kills the whole check.**

### THE PUNCH STATE IS ON DISK AND SURVIVES A RESTART — HIS HOLE 3

The first version said the count is *"kept in the watcher's own state, which no
desk owns"* and **never said that state is durable.**

**If punches live in memory, restarting the watcher clears every card.** And
restarting the watcher is the first thing anybody does when something looks stuck —
**which is exactly the moment a card is near four.** The freeze would be defeated by
the most ordinary troubleshooting step there is, and it would look like nothing
happened.

**On disk. Survives a restart. And the restart itself is visible in the record.**

**AND IF THE STATE FILE IS MISSING AT STARTUP, NOTHING IS WOKEN.** A fresh empty
state and a wiped one are indistinguishable, so the empty case is treated as the
bad case. Fail closed, same as everywhere else here.

### THE INVARIANT — NOT EQUALITY

He wrote: *the punch count and the total stamp count must always be equal.*

**They are never equal while a desk is working.** The watcher punches when it
files; the desk stamps when it finishes.

    punches - stamps == 0     at rest, waiting to be filed onward
    punches - stamps == 1     a desk is holding it right now. NORMAL.
    anything else             THE FLAG

**As strict equality the control goes red on every live job and gets switched off
in its first week.** The intent survives untouched — a gap means a file moved
between desks without going through the mail, which is the one failure the watcher
cannot see by itself.

**Stamps two or more BELOW punches:** a desk was handed the job and passed it on
without stamping, or the watcher filed it twice.

**Stamps ABOVE punches:** a desk touched a job the watcher never gave it. **That is
the bypass, and it is the more serious direction.**

**Per-desk stamp counts, not only the total** — his, and it is the forensics.

---

## 3. FOUR PUNCHES, THEN IT FREEZES

**Four. Then the job stops and goes to `correspondence/open/owner/` with its whole
history.**

**FREEZE IS A STATE, NOT A DESTINATION.** The watcher refuses to file a frozen job
to any desk and refuses to punch it. **Movement is enforced, because movement is the
watcher's. Editing in place cannot be prevented, only detected** — a stamp with no
punch behind it is section 2's flag.

**ONLY HIS STAMP RESTARTS IT, PLUS A COUNTER THAT NEVER RESETS.**

    job 0417    punches 3    resets 3    lifetime punches 15

**A forged reset can lie about who did it. It cannot hide that a reset happened.**

**Four is tight and he said so.** It will sometimes fire on honest work; firing
costs him a glance. **His own tray is not a lap** — a job that goes to him and comes
back does not spend a punch.

### RULED 2026-09-11 — BOTH NUMBERS, AND THE ESCALATION TRIGGER IS NOT THE DELIVERY COUNT

**TWO FAILED CORRECTION ROUNDS, AND THEN IT COMES TO HIM. THERE IS NO THIRD ATTEMPT.**

    a CORRECTION ROUND begins when Architecture answers an identified Build
    failure with a revised approach, and ends when Build reports the result of
    attempting that revision.

    the initial failed Build attempt is NOT a correction round
    a consultation with another desk is NOT a new round
    a renamed blocker does not erase prior rounds

**One round is not a pattern** — the first correction often works, which is what a
correction is for. **Two is the smallest number that tells "the fix did not work"
apart from "the fix keeps not working."**

**THE COST, ACCEPTED BY HIM:** occasionally a job reaches him that a third round
would have solved. That costs a glance and a *go again*. **The reverse mistake costs
a morning.**

**HIS FIRST FILING DOES NOT SPEND A DELIVERY. Only desk-to-desk handoffs count
toward the four.**

His reason, and it is the one recorded: **the four exists to catch desks going round
in circles with each other, and him handing work in is not a lap.** It also makes the
rule above consistent — **the owner edge spends no punch in either direction, which
is one rule instead of one rule and an exception.**

**WHY THIS MATTERS MORE THAN IT LOOKS:** the healthy route
Owner → Architecture → Build → Audit → Architecture was landing on four and freezing
a job that had passed every check. **Exempt the filing and it lands on three and
closes.**

### SO THE FOUR IS A RUNAWAY BACKSTOP, NOT THE ESCALATION TRIGGER

**The rounds fire first and they are what brings a job to him.** The four still
freezes, but it now catches only the case the rounds do not describe — a job moving
between desks in a shape nobody modelled.

**Two numbers, two jobs.** Neither does the other's work.

**HIS WORDS, RULED 2026-09-11, AND THEY ARE THE TEST:**

    TWO FAILED CORRECTION ROUNDS   brings a job to him. THIS IS THE TRIGGER.
    FOUR DELIVERIES                a runaway backstop. IT SHOULD NOW ALMOST
                                   NEVER FIRE, and if it does, that is a
                                   signal in itself.

**"A backstop that fires regularly is a trigger nobody labelled, and a trigger that
never fires is a backstop nobody trusts."**

**SO THE FOUR FIRING IS ITSELF REPORTED AS A SIGNAL.** Not only "job 0417 froze" —
**the rounds are not working, and he wants to hear that.** A freeze on the four after
this ruling is evidence about the mechanism, not only about the job.

---

## 4. THE WAKE

**The wake is a consequence of a successful filing, not a scan of the trays.**

**A file that appears in a tray by any other route produces no wake at all.** This
desk moved 47 memos with a shell last week and would have been surprised.

**The woken desk is handed its job number**, not told to go and look.

**ONE WAKE PER DESK AT A TIME.** A lock per desk, taken before, released at the end
log. **A stale lock is reported, not cleared** — clearing it automatically hides a
death. A letter arriving while a desk is locked is filed and does not wake it.

**A WAKE THAT PRODUCES NOTHING STILL LOGS AN END**, or it looks like a hang.

---

## 5. STUCK IS MEASURED BY SILENCE

**No time limit on a task.** What separates working from stuck is whether it is
still producing.

**Forty-five minutes with nothing written, and it surfaces to him.** The number is
thin and he said so.

**"Nothing written anywhere" is too broad to be a test.** A desk writing a scratch
file every minute while achieving nothing looks alive. **It needs a short named list
of what counts as production** — a memo, a repo file, a deliberate progress line.

**And section 12 makes that sharper: a woken desk cannot run anything, so a long
job of its is a long READ.** A desk reading for an hour must emit a progress line
or it trips a rule it is obeying.

---

## 6. THE NEW-FILE LOOP — THE HOLE HE NAMED

A → B on job 0417. B answers by writing 0418. A replies with 0419. **Every card is
clean, every count is one, and it runs forever.**

**The stamp rule does not fire** — a new job with one punch and one stamp is legal
by construction.

**A desk checking before it works is a second pair of eyes and not a control.**

**THE WAKE CEILING IS WHAT ACTUALLY STOPS IT.** His words: *a desk answering with a
new file dodges the card every lap; the ceiling is the only thing left.*

**One cheap detector, not to be built yet:** the rate at which new job numbers are
issued. Six new numbers between the same two desks inside ten minutes while nothing
else moved is not work.

---

## 7. THE CEILING — TWO LIMITS. HIS RULING.

    twenty wakes per day, across all desks
    AND no more than five in any fifteen minutes

**Over EITHER, the watcher stops waking anything and tells him.**

**Twenty wakes can burn in twenty minutes and still be inside a daily budget while
the damage is done. The fifteen-minute window catches a runaway in minutes rather
than at midnight.**

### THE MOST LIKELY FALSE TRIP IS HIM, ON DAY ONE

He drops three memos to three desks at once — three wakes. Each replies to a fourth
— six wakes inside ten minutes. **The window fires on entirely normal owner
traffic.** It will look like a malfunction rather than a limit working.

### THE CEILING MUST NOT SILENCE THE THING THAT REPORTS IT

**A notice into his tray is not a wake.** It wakes no desk and counts against
neither limit. **Otherwise a burst of stuck-job notices trips the ceiling and the
system loses the ability to say it has stopped.**

---

## 8. THE CEILING COUNTS WAKES. IT DOES NOT BOUND MONEY. — HIS HOLE 2

**Twenty a day and five in fifteen minutes limit HOW OFTEN. Nothing limits what one
wake can spend, and one wake is unbounded.**

**A per-wake spend cap is a brake in its own right**, set at launch, enforced by the
runtime rather than by the watcher — the same shape as rule 9, and for the same
reason.

**The two together are the first thing that puts a number on a day, and neither
does it alone:**

    worst case in a day  =  per-wake cap  x  twenty

**So the cap is chosen by deciding the day's worst case and dividing by twenty.**
His measurement: real headless runs on a small letter came in between three and
nineteen cents. **A cap has to clear nineteen cents by enough that honest work never
hits it, and stay low enough that twenty of them is a number he is willing to see.**

**The number is his.** Recorded here as arithmetic rather than a figure, because a
figure picked by this desk would be a guess wearing a decimal point.

---

## 9. RULE 9 — AND THE TEST MUST FORCE THE ATTEMPT. HIS HOLE 4.

Whatever launches a desk launches it **without** deploy, commit, push, delete, spend
or credential tools. Deny rules remove a tool rather than prompting for it; an
allow-list restricts nothing on its own.

**"Prove it by trying and being refused" was right and not strong enough. He
measured what it looks like when it is not:**

**A desk told to write outside its permitted folder DECLINED ON ITS OWN
JUDGEMENT** — it decided the file looked important — and produced a clean run with
no evidence either way. **The same probe, worded so the judgement route was closed,
attempted the write and was refused by the permission system.** That is the proof.

**So a tool-removal test has to FORCE the attempt.** Otherwise a desk's good manners
are indistinguishable from a working control, **and the control gets believed on the
strength of a run that never tested it.**

**The pass condition is "the permission system refused," never "nothing bad
happened."** A run where the desk chose not to try is not a failed test — it is no
test at all, and it must be reported as such rather than counted.

---

## 10. THE WATCHER IS THE SINGLE POINT OF FAILURE — HIS HOLE 1

**Three jobs live in the watcher: the waking, both ceilings, and the detection of
stuck and untouched jobs.**

**So when the watcher dies, nothing wakes, nothing is filed, and nothing says so.
The mechanism that reports silence is inside the thing that has gone silent.**

**This desk had the finding and lost it in a rewrite.** It was in the superseded
version and did not survive into the replacement. He found it again by walking the
document as a builder.

**It needs a heartbeat that something OUTSIDE it reads. Not a fourth job for the
watcher.**

    the watcher writes a heartbeat, and nothing else about it is its business

    read by  the auditor layer's nightly run - a control asserting the
             heartbeat is fresh. Outside the watcher, already scheduled,
             already has somewhere to report.

    read by  the Adjutant at the start of every conversation, alongside the
             owner tray it already reports. That is the fast path and it
             costs nothing to add to a rule that already exists.

**Neither alone is enough and together they are.** The nightly control catches a
death overnight; the Adjutant catches one the moment he speaks to anybody. **A
heartbeat nobody reads is the same defect one level up.**

---

## 11. A WOKEN DESK HAS NO SHELL — HIS LIMIT, AND WHAT FOLLOWS FROM IT

**That is how rule 9 is enforced: the tools are removed, not asked about. It is the
right answer and it has a consequence that has to be stated before somebody trips
over it.**

**A woken desk can read, search, and write. It cannot run a check, a test, a script
or a build.**

**So a wake is a reading-and-writing act, always.** Anything in the queue that needs
something *run* cannot be handed to a woken desk at all, and no card, ceiling or
lock changes that. **The first time somebody routes a job needing a shell, it will
fail in a way that looks like the desk was broken.**

### AND THE RULE THAT FALLS OUT OF IT

**A woken desk must not make a change it cannot verify.**

C1 woken cannot run `checks/_verify_owners.py`. So a woken C1 that edits `OWNERS.md`
has changed an owned artifact **and cannot prove it is still valid** — which is the
one thing this project does not allow anywhere else.

**In practice: a woken desk writes MEMOS.** It edits an owned artifact only where
the edit needs no proof, and for C1 that is close to nothing.

**This answers the cost in section 13 without arguing with his choice.** C1 has the
most write authority in the repository, and a woken C1 that only writes memos has
the blast radius of the audit desk while keeping the reason he chose it.

---

## 12. WHAT LIVES WHERE — THE RULE THAT COST A NIGHT

**Anything a desk has to execute against goes ON DISK, in the repository, first.**

**The claude.ai project is a mirror for him to read across sessions. It is not a
delivery mechanism to a desk that can only see files.**

This design existed only in the project. Build searched for it by exact name, by
`DESIGN_*` across the repository, and by content, found nothing, and correctly
refused to build against memos instead. **Nine and a half hours, both desks idle,
and neither of them at fault.**

**It is section 11 of this document pointed at this document:** the write
succeeded, and nothing reported that it had landed somewhere unreachable. **Fourth
instance in two days.**

**The check that would have caught it:** the sixth document check already ordered —
*a document names a file, folder or tool that does not exist* — extended to cover
memos in `correspondence/open/`. This design's path was named in a memo to Build the
moment it was filed, and the check would have gone red then.

---

## 13. WHICH DESK WAKES FIRST — HIS CHOICE

**C1, because it does the most direct work with Code, so Code can watch it and
verify it.** Waking a desk nobody is watching proves nothing.

**The cost, stated once and not argued:** C1 has the most write authority in the
repository. **Section 11 removes most of it** — a woken desk writes memos, because
it cannot verify anything it changes.

**Rule 9 gets proved before the first wake, not after**, and by a probe that forces
the attempt.

---

## 15. PRESENCE, AND CODE'S SHELL IN THE DAYTIME — HIS REQUIREMENT, 2026-09-10

**He wants Code woken automatically during his working hours, not only the thinking
desks and not only overnight.** The requirement is his; how it is made safe is this
desk's.

### THE SPLIT IS ON PRESENCE, NOT ON THE DESK

    ALWAYS REMOVED, BOTH MODES, NEVER NEGOTIABLE
        deploy, commit, push, delete, spend, credentials

    REMOVED WHEN NOBODY IS PRESENT
        the shell, and everything that runs code

**The shell is the only thing that differs between the two modes.** A woken Code in
the daytime can run a check, a build or a script and edit files. **It still cannot
deploy, commit or push, at any hour, in any mode.**

**This also fixes something that was quietly wrong:** rule 9 as written made
automation worth nothing to the desk that does the most work.

### THE MARKER LIVES OUTSIDE ANYTHING A DESK CAN WRITE TO

**His proposal was a file he creates when he sits down. A file in a place a desk can
write is a shell a desk can grant itself** — a woken desk writes the marker, and the
next wake gets a shell. **And a daytime Code already HAS a shell, so it could
refresh its own presence indefinitely.** The thing the marker proves becomes
something the permitted thing can manufacture.

**So the marker lives OUTSIDE every folder a desk can write to.** A woken desk's
file access is scoped to the project folders; the marker sits outside that scope.
The launcher reads it; nothing a desk runs can reach it.

**Same principle as rule 9 itself — the capability is removed, not requested —
applied one level up, to the thing that grants the capability.**

**The test, in the shape he proved on 2026-09-10:** with the marker absent, a woken
Code must TRY to write it and be refused. **A run where it did not try is no test.**

### FOUR HOURS, ABSOLUTE FROM CREATION

**Four hours.** Long enough to cover a working block untouched; short enough that
forgetting costs the rest of one afternoon rather than a night.

**ABSOLUTE, NEVER SLIDING.** A window that extends on activity is extended by the
desk's own activity — the filesystem hole arriving through the clock. Four hours
from creation whatever happens in between.

**Renewal is his act, the same act as creation.** If four hours is irritating the
answer is a different number, never an automatic renewal.

**And a clock window alone is not enough**, his point: "between nine and five" is
true on the days he is not there.

### THE CEILING IS THE SAME TWENTY. THE SPEND CAP IS WHAT DIFFERS.

**One wake ceiling for every desk including a daytime Code.** The ceiling stops a
runaway, and a runaway is a runaway whoever is looping. **Loosening it for the desk
with a shell would loosen it exactly where the blast radius is largest.**

**What is different about Code's work is its SIZE, not its frequency**, and size is
what the per-wake spend cap measures. **One wake ceiling, two spend caps.**

If Code's real work regularly eats the shared twenty and starves the thinking
desks, that is a measurement result and the number moves. Not designed for now.

---

## 16. THE BUILD ORDER — HIS, WITH ONE THING MOVED

    STEP 1   THE LAUNCHER               starts one desk, proves what it did
             + THE SWITCH               section 19. It is a file the launcher
                                        reads before it launches anything, and
                                        it is cheapest here.
    STEP 2   THE BRAKES                 both ceilings, the per-desk lock, the
                                        per-wake spend cap, the wake log
    STEP 3   THE DOORBELL               the watcher calls the launcher. THIS IS
                                        WHERE IT BECOMES AUTOMATIC.
             + BLOCKED_ON / CLEARS_BY   section 17. The routing rule has to
                                        exist the moment filing causes a wake.
    STEP 4   PRESENCE AND CODE'S SHELL  section 15
             + THE SILENCE DETECTOR     MOVED HERE from step 6
    STEP 5   THE CARD AND THE FREEZE    four punches, the stamp, the invariant
    STEP 6   THE REST OF THE DETECTORS  twelve hours untouched, and the
                                        heartbeat outside the watcher
             + THE ROLL CALL            section 18. It reads the heartbeat, so
                                        it cannot be finished before the
                                        heartbeat exists.

**Step 2 before step 3 is the important one: the brakes exist before the doorbell
rings.**

**The card is fifth for his reason and it is this desk's own finding used
correctly** — the card does not stop the loop, the ceiling does; the ceiling is two
numbers and the card is a filename convention, a stamp format, a durable counter
and a freeze. **The cheap thing that actually stops a runaway goes first.**

### WHY SILENCE MOVED TO STEP 4

**Step 4 is where a woken desk gets a shell — the largest single increase in blast
radius in the plan.**

**A memo desk that hangs writes nothing and wastes a wake. A shelled Code that hangs
mid-build holds a lock, sits on the machine, and produces nothing** — and the only
thing that would notice is a detector scheduled two steps later.

His reason for step 6 being last is right for the untouched-job rule and the
heartbeat. **It is not right for silence, because the presence marker's failure mode
is exactly that he left and it had not expired yet.**

---

## 14. THE SHAPE THIS KEEPS SOLVING

    nothing quiet stays invisible

**Four instances in two days.** The links control sweeping four pages and reporting
clean. The RSI watcher blind on four of five sources for a month. A job nobody
picked up. **A design filed where the desk that needed it could not see it.**

**Every one is a system reporting what it managed to do and not what it failed to
do**, and every number and every heartbeat in this design serves that one line.

*C1, 2026-09-10.*
