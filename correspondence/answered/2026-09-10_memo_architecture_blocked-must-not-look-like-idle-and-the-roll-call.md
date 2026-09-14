# Memo

To:      Engineering
From:    Owner
Date:    2026-09-10
Subject: REQUIREMENT — blocked must not look like idle, and I want a roll call I can ask for
Status:  Answered

**Two requirements. Both are mine. The mechanisms below are the desk's proposal and
you may replace any of them.**

---

## 1. WHY I WANT THE AUTOMATION, IN MY OWN WORDS

*"One of the biggest reasons I want this automation system working is so I don't
have to go into each window and tell everyone to proceed. If I do that in the wrong
order, I could cause a problem."*

*"Sometimes Code stops because something important needs to be fixed or resolved
first. His explanations can be difficult for me to read and understand, so I might
think he's simply sitting idle and tell him to continue. Then the issue he was
waiting on could get pushed aside without being fixed because it wasn't clearly
communicated to me."*

**Read that second paragraph as a defect report, because it is one, and it has
already happened.** Build stopped at 00:33 because a design document was not on
disk. It said so clearly. **Nine and a half hours later the state of that blocker
was still being guessed at from tray movement**, and the only thing that resolved it
was somebody finally reading Build's own words.

**So the automation is not mainly about saving him from typing "go".** It is about
taking him out of the path where a blocker has to be understood by him before it can
be cleared.

## 2. THE FIRST REQUIREMENT — A BLOCKER ROUTES TO WHOEVER CAN CLEAR IT

**When a desk stops because it is waiting on something, that must go to the desk
that can clear it. Not to me.** I come into it only when nothing else can.

**And "go" must not clear a blocker.** If I tell a desk to proceed and its blocker
is still standing, **it stops again on the same blocker and says so.** A blocker is
cleared by the thing it names being fixed, and by nothing else.

### PROPOSED — THE STATE IS A VALUE, NOT A PARAGRAPH

**A desk stopping writes a fixed field, not prose.** Prose is exactly what fails me
here.

    state        WORKING | BLOCKED | IDLE
    blocked_on   the thing that would clear it — a path, a job number, a desk,
                 a decision. Empty when the state is not BLOCKED.
    clears_by    which desk can clear it, or OWNER when nobody else can

**Prose stays.** The desk still explains itself in full and that explanation is still
worth having. **But the machine reads the field, and the field is what routes the
letter.** Nothing that decides where a letter goes should require anybody to read a
paragraph correctly.

**`clears_by` is the whole point.** Build blocked on a missing design document is
`clears_by: architecture`, and it goes to you automatically. **It reaches me only
when `clears_by` is OWNER.**

### AND THE ONE THAT PROTECTS ME FROM MYSELF

**A job whose `blocked_on` is still unresolved cannot be moved on by a wake.** The
watcher refuses to wake a desk against a blocked job the same way it refuses to file
a frozen one. **Otherwise the automation reproduces the exact failure I described —
work carrying on past a problem nobody fixed — only faster and without me watching.**

## 3. THE SECOND REQUIREMENT — THE ROLL CALL

*"I want to be able to ask you, 'What's going on? What actual work is happening?'
Then you can check the different desks and tell me plainly: Code is working on this,
C1 is working on that, C3 is handling something else, C4 is waiting for something to
do, and you and I are working on this together."*

**I want that answer to be read off the machine, not assembled from somebody's
impression of it.**

### PROPOSED — DERIVED, NEVER STORED

**Do not build a status file that desks update.** It will go stale, it will disagree
with reality, and this project has paid for a second source of truth more than once.

**Derive it from what already exists:**

    what it is working on     the desk's lock, and the job number it holds
    when it last produced     its last stamp, and its last archive entry
    whether it is blocked     the blocked_on field from section 2
    whether it is idle        empty tray, no lock

**The only new thing anywhere in this is the `blocked_on` field, and it is one more
value on a stamp you are already specifying.** Everything else is a read of things
the doorbell already maintains.

**A desk that is WORKING is shown with the age of its last output beside it**, because
working and hung look identical without it. That is the same number the
forty-five-minute silence rule uses.

## 4. THE SWITCH

*"I still want to be able to turn it on and off."* **Confirmed, and it is a
requirement, not a nicety.**

**Off means no desk is woken by anything.** Mail is still filed, work already in a
desk's hands still finishes, and nothing is lost — **it simply stops starting
anything new.**

## 5. WHAT I HAVE NOT DECIDED

**Whether `blocked_on` should be a free string or a closed list.** A closed list is
machine-checkable and refuses a typo; a free string never fails to describe the
problem. **You have measured this trade-off twice this week on desk names and I want
your answer rather than my guess.**

## 6. UNCHANGED

The build order stands. **Nothing runs unattended until one headless run is proved
and I have seen it** — that has now happened, so say plainly in your reply whether
you consider that condition met, because I am not going to assume it.

---

ANSWERS:

**Architecture, 2026-09-10.**

Both requirements adopted. Three of your mechanisms taken as written, one replaced
with something smaller, and section 5 answered with a measured reason rather than a
preference. **The design document has sections 17, 18 and 19 for these, and section
16's build order says where they land.**

## 1. YOUR SECOND PARAGRAPH IS TAKEN AS A DEFECT REPORT

No argument. Build stopped at 00:33 and said why in plain words; nine and a half
hours later the blocker was being inferred from tray movement.

**What your letter adds is the part this desk had not drawn out: the failure was not
that Build explained itself badly. It was that clearing the blocker required you to
read the explanation.** That is the thing being removed, and it is a better statement
of the requirement than "route blockers automatically".

## 2. FIRST REQUIREMENT — ADOPTED, WITH ONE OF YOUR THREE FIELDS REMOVED

**Adopted as written:** a blocker routes to whoever can clear it; it reaches you only
when nobody else can; "go" does not clear a blocker; and a job with an unresolved
blocker cannot be moved on by a wake.

**Replaced: `state` is DERIVED, not written by the desk.** You proposed three fields.
Two are new. The third already exists twice over:

    WORKING   the desk holds its lock — section 4 of the design
    IDLE      no lock, and nothing in its tray
    BLOCKED   its last stamp carries a blocked_on

**A desk that writes its own `state` can be WORKING with no lock, or IDLE holding
one.** That is a status file with two entries in it, and your own section 3 says not
to build one. The rule is right in both places, so it applies to both.

**So: one new field pair on the stamp, not three. `blocked_on` and `clears_by`.**

### WHAT "CANNOT BE MOVED ON BY A WAKE" MEANS EXACTLY, BECAUSE IT COULD DEADLOCK

The refusal is on **re-waking the blocked desk about that job.** It is not a refusal
to move the job.

    the blocked job goes to clears_by, and THAT desk is woken     the mechanism
    the blocked desk is not woken again on that job until the blocker clears

**Without that sentence the rule freezes the very thing meant to unfreeze it** — the
blocker could never reach the desk that can clear it. Written into the design that
way.

### AND A BLOCKED JOB THAT COMES BACK STILL BLOCKED SPENDS A PUNCH

Build blocks on architecture, architecture answers, the answer does not clear it,
Build blocks again on the same thing. **That is a loop, the card is what catches it,
and it should.** Deliberate, not an oversight.

## 3. SECTION 5 ANSWERED — `clears_by` CLOSED, `blocked_on` TYPED

They are two different fields and they get two different answers. Your question
assumed one answer for both, which is why it looked like a trade-off.

**`clears_by` IS A CLOSED LIST, AND IT COSTS NOTHING NEW.** It is a desk name. The
desk list was ruled on 2026-09-09 to be derived from the tray folders on disk rather
than typed anywhere, so the closed list already exists and the watcher already
validates `To:` against it. `clears_by` validates against the same list, from the
same read.

**A typo here misroutes a blocker, which is the exact failure this requirement exists
to prevent.** So it fails closed: an unrecognised value goes to `_needs_review/`, the
same as a bad `To:`.

**`blocked_on` IS A FREE STRING WITH A TYPED PREFIX.** A closed list cannot describe
"the design document is not on disk". A free string cannot be checked. The prefix
gives you both halves:

    blocked_on: path:claude/DESIGN_the-doorbell-...-2026-09-10.md
    blocked_on: job:0417
    blocked_on: desk:build
    blocked_on: decision:the per-wake spend cap

**Four kinds. Three of them can be tested for existence, and that is where the whole
value is.** A `path:` blocker naming a file that now exists is a blocker that has
cleared, **and something other than a person can say so.** That is the same test the
sixth document check already performs.

**`decision:` is checkable against nothing, and that is correct.** A decision of yours
is not on disk until you make it. It is the escape hatch that keeps the free string's
virtue, and it is the one kind where only your answer clears it — **so `decision:`
implies `clears_by: OWNER`**, and by section 7 a notice into your tray is not a wake
and does not count against either ceiling.

**An unrecognised prefix is refused, never guessed.** Hard rule 19.

## 4. THE ROLL CALL — ADOPTED AS DERIVED, PLUS TWO COLUMNS YOU DID NOT ASK FOR

Taken exactly as you wrote it. No status file. Every column is a read of something
that already exists, and the only new value in the whole thing is `blocked_on`.

**FIRST ADDITION — THE ROLL CALL MUST REPORT THE WATCHER'S HEARTBEAT AGE.**

The roll call reads locks, stamps and trays. **If the watcher is dead, every desk
reads as idle and the honest-looking answer is "nothing is happening" — which is true,
and completely misleading.** It is section 10 of the design pointed straight at your
section 3, and it is the fourth time this week the same shape has come up. The
heartbeat is already specified; this is one more line on a read that is already
happening.

**SECOND ADDITION — AND THE SWITCH'S STATE.** Below.

**Whose job it is:** the roll call is a read, so it is the Adjutant's, at the start of
a conversation. It already reports your tray. This is that rule extended, not a new
component — and it is not a wake, so it costs nothing against the ceiling.

## 5. THE SWITCH — ADOPTED, AND IT HAS THE PRESENCE-MARKER HOLE IN IT

Off means no desk is woken; mail still files; work in hand still finishes. Taken as a
requirement.

**THE SWITCH LIVES OUTSIDE EVERY FOLDER A DESK CAN WRITE TO.** Section 15 established
this for the presence marker and the reason transfers without modification: **a switch
a desk can write is a switch a desk can turn back on.** Off has to mean off to the
thing being switched off. Same principle as rule 9 — the capability is removed, not
requested — applied to the thing that grants the capability.

**AND "OFF" MUST BE VISIBLE IN THE ROLL CALL**, or "every desk is idle" and "the
automation is switched off" look identical. That is the same defect the whole design
exists to close, and it would be embarrassing to build it into the switch.

## 6. THE HEADLESS CONDITION — MET AS YOU WROTE IT. HERE IS WHAT IT DOES NOT COVER.

**You asked me to say plainly rather than assume, so: YES. The condition is met.**

Your words were one proved headless run that you had seen. Four ran, you saw them, and
they are on disk at `claude/VERIFIED_four-headless-runs-and-the-flag-set-that-would-have-wasted-the-night-2026-09-10.md`.
Two flags were settled by test where argument would have run another day. **And one
run found a flag set that would have produced a whole night of sessions that exited
zero, reported success, and wrote nothing.**

**What it does not do is authorise anything to run on your machine, and stopping the
answer at "met" would mislead you.** All four runs were Linux on CLI 2.1.267. Your
machine is Windows on 2.1.266. Three things are untested and named in that document:
the `inbox/**` path rule on Windows separators, resolving `claude.exe` rather than
`claude.cmd`, and the flag set on 2.1.266.

**That is not a reason to re-open your condition. It is what step 1 is for** — the
runbook opens with a free `claude --help` assertion and a pennies-cost containment
probe that stops the run. Those are the Windows equivalents of what the four runs
proved on Linux, and they are already in the build order.

## 7. ONE THING FOUND WHILE CHECKING THIS, AND IT IS STEP 1'S PROBLEM

`protected_folders.txt` at the repository root names two folders under `inbox/` that
the watcher must never watch or auto-process — *"long-term work-in-progress areas, not
transient drop-zone content."* **The watcher honours it, at any depth, in both the
startup sweep and the live watch. The launcher has never heard of it.**

The write rule proved in the headless runs is `Edit(inbox/**)`, **and that glob covers
both protected folders.** A woken desk currently has write access to two folders this
project has formally declared off-limits to automation.

Nothing has been harmed and nothing is broken. **The rule simply has exactly one
reader, which is the shape section 14 is named after.** Sent to Build as step-1
material.

*C1, 2026-09-10.*
