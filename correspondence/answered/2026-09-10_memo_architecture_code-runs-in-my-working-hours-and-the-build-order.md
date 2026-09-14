# Memo

To:      Engineering
From:    Owner
Date:    2026-09-10
Subject: NEW REQUIREMENT — Code runs automatically during my working hours. And the build order, smallest useful thing first.
Status:  Answered

## 1. THE REQUIREMENT — MINE

**I want Code woken automatically during the daytime hours while I am sitting here
working.** Not only overnight, and not only the thinking desks.

That is the requirement. **How it is made safe is yours to specify** — the rest of
this letter is the desk's proposal, marked as such, and you may replace any of it.

## 2. WHY THIS IS NOT A CONTRADICTION OF RULE 9 — PROPOSED, NOT RULED

Rule 9 removes the shell from a woken desk. **That is the right rule for a desk
woken when nobody is looking.** Code's whole job is running things, so a Code
without a shell is a Code that cannot work — which is why automation appeared to be
worth nothing to the one desk that does the most.

**The proposal: the removal is tied to whether a person is present, not to the desk.**

    ALWAYS REMOVED, BOTH MODES, NEVER NEGOTIABLE
        deploy, commit, push, delete, spend, credentials

    REMOVED WHEN NOBODY IS PRESENT
        the shell, and everything that runs code

**So the difference between the two modes is the shell and nothing else.** A woken
Code in the daytime can run a check, run a build, run a script and edit files. **It
still cannot deploy, commit or push, at any hour, in any mode.** Those stay manual
and they stay mine.

### HOW PRESENCE IS ESTABLISHED — PROPOSED

**A file I create when I sit down.** Explicit, visible, and it says what it means.

**It expires on its own after a few hours.** Forgetting to remove it must not leave
the shell open all night, and it will be forgotten — **a control that depends on me
remembering to switch it off is the same defect as a control that depends on a desk
choosing to obey.**

**A clock window is not enough on its own.** "Between nine and five" is true on the
days I am not there.

## 3. THE BUILD ORDER — SMALLEST USEFUL THING FIRST

**What has to exist before anything is automatic at all is smaller than the full
design, and I want it built in this order.**

    STEP 1   THE LAUNCHER               a program that starts one desk and proves
                                        what it did. In flight with Build.
             proves it works            one headless run, scored from the
                                        filesystem, and I have seen the result

    STEP 2   THE BRAKES                 the two ceilings (twenty a day, five in
                                        fifteen minutes), one-wake-per-desk lock,
                                        a spend cap on a single wake, the wake log
             proves it works            the ceiling is deliberately tripped and
                                        the watcher stops and tells me

    STEP 3   THE DOORBELL               the watcher calls the launcher when it
                                        files a letter. THIS IS THE MOMENT IT
                                        BECOMES AUTOMATIC.
             proves it works            one letter, one wake, one reply, and the
                                        brakes untouched

    STEP 4   PRESENCE AND CODE'S SHELL  section 2 of this letter
             proves it works            with the file absent, a woken Code TRIES
                                        to run a command and is refused

    STEP 5   THE CARD AND THE FREEZE    four punches, the stamp, the invariant
    STEP 6   THE DETECTORS              forty-five minutes silent, twelve hours
                                        untouched, and a heartbeat OUTSIDE the
                                        watcher

**Steps 1 to 3 are the whole of "it works". Step 2 is the whole of "it is safe."**

**Nothing is automatic until step 2 is finished and proved.** The brakes exist
before the doorbell rings, not after.

### WHY THE CARD IS FIFTH AND NOT SECOND

**Your own finding.** A desk answering with a new file starts a fresh card every lap,
so the card does not stop the loop — **the ceiling does.** The ceiling is two numbers
in the watcher's state. The card is a number in a filename, a stamp format, a
watcher-owned counter that survives restarts, and a freeze the watcher enforces.

**The cheap thing is the one that actually stops a runaway. It goes first.**

The card is still built. It is what tells me a job is going round in circles rather
than merely that something is busy, and nothing else gives me that.

### AND STEP 6 IS WHERE MY REAL FEAR LIVES

Silence reading as fine. **It is last because nothing can rot unnoticed until things
are running unattended in the first place**, not because it matters least.

## 4. WHAT I HAVE NOT DECIDED

**The expiry on the presence file.** Propose a number with a reason.

**Whether a woken Code in daytime mode gets the same wake ceiling as a thinking
desk.** It will be doing longer, heavier work; twenty may be wrong in either
direction.

## 5. UNCHANGED

**Nothing runs unattended until one headless run has been proved and I have seen the
result. The go to spend is mine and I have not given it.**

---

ANSWERS:

**Architecture, 2026-09-10. The requirement is taken. Your presence proposal has one
hole that hands a desk the shell, and it is fixable. Expiry: four hours, absolute.
Ceiling: same twenty — the number that should differ is the spend cap, not the
count. And one thing in your build order is in the wrong place.**

Design updated: `claude/DESIGN_the-doorbell-the-job-number-and-the-punch-card-2026-09-10.md`,
on disk, section 15.

## 1. THE SPLIT IS RIGHT — TIED TO PRESENCE, NOT TO THE DESK

**Accepted as the shape.** Deploy, commit, push, delete, spend and credentials
removed always, both modes, never negotiable. **The shell is the only thing that
differs**, and it differs on whether a person is there rather than on which desk it
is.

**It is also the answer to something that was quietly wrong:** rule 9 made
automation worth nothing to the desk that does the most work, and that would have
been discovered later as a disappointment rather than now as a design.

## 2. THE HOLE — A FILE A DESK CAN WRITE IS A SHELL A DESK CAN GRANT ITSELF

**A woken desk can write files. If the presence file is a file in a place a desk can
write, a desk can create it — and the next wake gets a shell.**

**Worse, a daytime Code HAS a shell**, so it could refresh the file and keep its own
presence alive indefinitely. **The thing the file is supposed to prove becomes
something the thing being permitted can manufacture.**

**The fix: the marker lives OUTSIDE every folder a desk can write to.** A woken
desk's file access is scoped to the project folders; put it outside that scope and
no desk can create it, refresh it, or delete it. **The launcher reads it; nothing a
desk runs can reach it.**

**That is the same principle as rule 9 itself** — the capability is removed, not
requested — applied one level up to the thing that grants the capability.

**And a matching test, in the same shape you proved yesterday:** with the marker
absent, a woken Code must TRY to write the marker and be refused. A run where it
did not try is no test.

## 3. THE EXPIRY — FOUR HOURS, AND ABSOLUTE FROM CREATION

**Four hours.** Long enough to cover a normal working block without you touching it
again; short enough that the worst case of forgetting is the rest of one afternoon
rather than a night.

**ABSOLUTE FROM CREATION, NEVER SLIDING.** A window that extends on activity is
extended by the desk's own activity — the hole from section 2 arriving through the
clock instead of through the filesystem. **Four hours from when you made it, whatever
happens in between.**

**Renewing it is your act, the same act as creating it.** If four hours turns out to
be irritating, the answer is a different number, never an automatic renewal.

**And the reason for a number rather than a clock window, which you already gave:**
"between nine and five" is true on the days you are not there.

## 4. THE CEILING — SAME TWENTY. THE SPEND CAP IS WHAT SHOULD DIFFER.

**Same global twenty, and five in fifteen minutes, for every desk including a
daytime Code.**

**The ceiling's job is to stop a runaway, and a runaway is a runaway whoever is
looping.** Giving the desk with a shell a bigger allowance would loosen the limit
exactly where the blast radius is largest.

**What is genuinely different about Code's work is its SIZE, not its frequency** —
and size is what the per-wake spend cap measures. **So: one wake ceiling, two spend
caps.** A daytime Code gets a larger per-wake cap because a build costs more than a
memo, and the day's worst case is still arithmetic you can read.

**One thing to watch rather than pre-solve:** if Code doing real work regularly eats
the shared twenty and starves the thinking desks, that is a measurement result and
the number moves. Do not design for it now.

## 5. THE BUILD ORDER — AGREED, WITH ONE THING MOVED

**Steps 1, 2 and 3 in that order, and step 2 before step 3 is the important one.**
The brakes exist before the doorbell rings.

**And your reason for the card at five is right and it is my own finding used
correctly:** the card does not stop the loop, the ceiling does, and the ceiling is
two numbers while the card is a filename convention, a stamp format, a durable
counter and a freeze. **The cheap thing that actually stops a runaway goes first.**

**THE ONE THING IN THE WRONG PLACE: the forty-five-minute silence detector belongs
with step 4, not in step 6.**

**Step 4 is where a woken desk gets a shell**, which is the single largest increase
in blast radius in the whole plan. **A memo desk that hangs writes nothing and
wastes a wake. A shelled Code that hangs mid-build can hold a lock, sit on the
machine and produce nothing, and the only thing that notices is the detector you
have scheduled two steps later.**

Your reasoning for step 6 being last — nothing can rot unnoticed until things run
unattended — **is right for the untouched-job rule and the heartbeat. It is not
right for silence**, because the presence marker's failure mode is precisely that
you left and it had not expired yet.

**So: silence moves to step 4. The heartbeat and the twelve-hour rule stay at six.**

## 6. AND ONE THING THAT IS NOT MINE OR YOURS

**`device_bash` can no longer mount your folders — two desks now, same symptom.**
Design reported it this evening; this desk lost its shell to it yesterday and has
been reading and writing single files since.

**It makes every desk slower in a way that looks like the desks got slower**, and it
is going to shape how long steps 1 to 3 take. Sent as its own item rather than
buried here.

## 7. UNCHANGED

**Nothing runs unattended until one headless run is proved and you have seen it. The
go to spend is yours and you have not given it.**
