# Memo

To:      Engineering
From:    Owner
Date:    2026-09-10
Subject: Echo answered on the chain. It says three of our decided rules are broken. Tear into it before I believe any of it.
Status:  Answered

    claude/ECHO_the-routing-and-escalation-process-2026-09-10.md

**On disk, verbatim, nothing adopted.** Same standing as the automation proposal you
went at on 2026-09-09 — **an outside desk's work I do not trust until this desk has
been through it.**

## WHAT IT CLAIMS ABOUT RULES I ALREADY DECIDED

**Three of them, and I want your answer on each. It labels them as changes to
decided rules rather than slipping them past me, which is the only reason I am
taking them seriously at all.**

**1. THE FOUR-DELIVERY CEILING FIRES ON HEALTHY WORK.** Its arithmetic:

    1 Architecture   2 Build   3 Architecture (Build's problem)   4 Build (correction)

**and it says even the plain route Owner → you → Build → Audit → you reaches four
before you can close a job.** If that holds, my four does not stop runaways — it
stops ordinary work and puts me in the middle of it, which is the exact thing I am
building this to escape.

**You wrote the card. Is the arithmetic right?** If it is, say what the number
should count instead. **I am not moving four because an outside desk did some
addition. I will move it because you show me the same thing.**

**2. THE STAMP INVARIANT CANNOT SURVIVE A CRASHED DESK.** A desk that dies before
stamping leaves a punch outstanding; re-routing the job makes it two. **`punches −
stamps ∈ {0,1}` then goes red with nobody at fault.** It proposes the service being
able to record a visit as cancelled — **and says plainly not to fix it by forging a
stamp or deleting a punch, which is the answer I would have expected somebody to
reach for.**

**Does the hole exist? If it does, is a service-recorded cancellation the right shape,
or is there something better that does not add a third kind of mark?**

**3. AUDIT CANNOT PARTICIPATE UNDER ITS OWN CHARTER.** "Read-only, holds no files"
against a route that requires Audit to return a review letter. **It says the charter
needs a narrow exception. Check whether that is real or whether the memo path already
covers it.**

## THE ONE I ALREADY AGREE WITH

**`From:` is a claim, not authentication.** The service knows which desk it launched
and which job that session was given; the header is just text a desk typed. **Anything
that routes on the header alone can be walked past by whatever writes a header.**

**And it says the punch count cannot authenticate a route either** — a file moved by
hand keeps its count, and a passing count is not proof of a lawful move. **That is a
harder version of what I already believe and I want to know if you disagree.**

## HOW TO GO AT IT

**Same as the automation proposal.** Claim by claim. **Established, or its inference,
or its guess** — it labelled its own work that way, so check whether the labels are
honest rather than trusting them.

**Where it is right, say so plainly.** Where it is borrowing vocabulary from systems
that do not fit a file-based single machine, say that too — **it warns about that
itself in two places, which is either good faith or good cover.**

**Where it collides with something of mine that is already decided, do not soften it
and do not adopt it. Bring it to me with your own verdict on it.**

## WHAT I AM NOT ASKING FOR

**Not a design. Not an adoption. Not a plan.** A verdict on someone else's work, and
the three collisions answered.

**Nothing in the brakes or the doorbell changes on the strength of this letter.**
Build carries on with what it already has.

---

ANSWERS:

**Architecture, 2026-09-10.**

**Verdict in one line: two of the three collisions are real and the third is wrong
because Echo did not read our charter. Its labels are honest about its own certainty
and say nothing about whether it checked us — and that is the distinction to hold it
by.**

**It also found a defect in my brakes spec that neither of us had, and its one claim
I could verify against a primary source held up exactly.**

---

# COLLISION 1 — THE ARITHMETIC IS RIGHT. HERE IT IS ON MY OWN CARD, NOT ECHO'S.

You said you would move four when I showed you the same thing. So this is my count,
against my own words in section 3 of the design, not a repeat of Echo's.

**The card punches every time the watcher files a job to a desk.** Four punches, then
freeze.

    Owner files it            -> Architecture      punch 1
    Architecture hands over   -> Build             punch 2
    Build finds a problem     -> Architecture      punch 3
    Architecture corrects     -> Build             punch 4   FREEZE

**Build never runs the correction.** The freeze lands on the delivery that was
supposed to carry the fix.

**And the healthy route is worse, because nothing has gone wrong in it at all:**

    Owner -> Architecture   1
    -> Build                2
    -> Audit                3
    -> Architecture         4   FREEZE, before Architecture can close a job that
                                passed every check

**So four is not a runaway stop. It is a checkpoint that fires on a job doing exactly
what it is supposed to do.** Echo's arithmetic is correct and I get the same numbers.

## AND THERE IS AN AMBIGUITY IN MY OWN RULE THAT DECIDES HOW BAD IT IS

Section 3 says *"his own tray is not a lap — a job that goes to him and comes back
does not spend a punch."*

**It does not say whether YOUR FIRST FILING spends one.** Echo assumed it does. Read
the other way, every count above drops by one and the correction round survives.

**That ambiguity is mine and it is a defect by our own rule 19** — ambiguity is
refused, not picked. Whichever way it is settled, four is thin.

## WHAT THE NUMBER SHOULD COUNT INSTEAD — AND YOU ALREADY SAID IT

**Your own word, in the chain letter this afternoon: *"if C1 is unable to fix it in a
certain amount of rotations."***

**A rotation is a failed correction round. The card counts deliveries. Those are not
the same unit, and the delivery is the wrong one.**

**Echo reached the same place from the other direction** — *"a poor substitute for a
failed-round budget"* — and it got there from Temporal and Jira rather than from your
sentence. Two desks, two roads, same answer. **That is the strongest thing in its
whole reply.**

**So: two numbers doing two jobs, not one number doing both badly.**

    FAILED CORRECTION ROUNDS      the escalation trigger. Your "rotations".
                                  Architecture answers a Build failure, Build
                                  reports the result of trying it. That is one.
    DELIVERIES                    stays, as a RUNAWAY BACKSTOP at a much higher
                                  number. A job that has moved a dozen times
                                  without finishing or hitting the round limit
                                  is doing something nobody modelled.

**Your instinct for a hard stop survives intact. It just stops being the thing that
fires first.**

**The number for the rounds is yours and I am not putting one in front of you in this
letter** — you asked for a verdict, not a design, and picking it belongs with the
chain work you have already sent outside.

---

# COLLISION 2 — THE HOLE IS REAL. THE SHAPE ECHO PROPOSES IS ALMOST RIGHT AND THERE IS A BETTER ONE.

## THE HOLE

    filed to a desk      punches 1, stamps 0, difference 1     LEGAL - "a desk is
                                                               holding it"
    the desk dies        nothing will ever stamp it
    re-route it          punches 2, stamps 0, difference 2     THE FLAG

**Nobody did anything wrong and the control goes red.** Confirmed.

**And it is worse than a red light, because my own design has no legal move out of
it.** Section 4 says a stale lock is *reported, never cleared*, so the system
correctly notices the dead desk — **and then has nothing it is allowed to do.** The
detector works and the recovery does not exist.

## YOU ASKED FOR SOMETHING BETTER THAN A THIRD KIND OF MARK. THERE ISN'T ONE — BUT IT DOES NOT HAVE TO GO ON THE CARD.

**A third outcome has to be recorded somewhere.** A punch means handed out; a stamp
means handed back; there is no way to say *handed out, never came back, and we know
it*. **You cannot avoid recording that. You can only choose where it lives.** Any
answer that avoids it is forging a stamp or deleting a punch, and Echo is right to
name both and refuse them.

**But it belongs on the VISIT, not on the card.**

    a punch OPENS a visit
    a visit is CLOSED by exactly one of:  a desk stamp
                                          a service-recorded cancellation
    the invariant becomes:  open visits ∈ {0,1}

**That is the same arithmetic, expressed against visits instead of raw counts, and it
needs nothing new on the card** — the visit record already exists. The brakes spec
this afternoon already requires a `run_id` per visit, on the lock, on `wake_start` and
on `wake_end`. **The thing Echo says we must add is a thing today's spec already
built for another reason.**

**And it keeps what matters: a cancellation is service-written and visibly different
from a desk stamp**, so "the desk never answered" can never be laundered into "the
desk answered."

## THE PART ECHO MISSED, AND IT IS THE PART THAT WOULD HAVE BITTEN US

**Cancellation must not be automatic.**

My rule that a stale lock is reported and never cleared exists because **clearing it
automatically hides a death.** If the service can cancel a visit on its own judgement,
it has been handed exactly that power back through a different door — **crash recovery
becomes an automatic death-hider.**

Echo half-covers this with *"authorised recovery, previous custody safely closed"*,
but it never connects it to the never-auto-clear rule, because it does not know that
rule exists.

**So: the stale lock is reported first, and the cancellation is recorded only after
that report has been answered.** Notice, then close. Never close silently.

---

# COLLISION 3 — ECHO IS WRONG, AND THE REASON IT IS WRONG IS THE USEFUL PART

**The memo path already covers it. There is no exception needed.**

The audit desk's charter, in `claude/PROMPT_boot-a-new-c5.md` and in the "Session
roles" section of `docs/CURRENT-STATE.md` it is drawn from:

> *"You hold no artifact and you own no path. Nothing in `OWNERS.md` is yours. **You
> write nothing in the repository except memos dropped in `inbox/`.** That is the whole
> of your write access and it is not a guideline."*

**A review letter is a memo. The charter grants it in the same breath that it takes
everything else away.** Audit has answered letters through that path repeatedly this
week.

**Echo reasoned from the phrase "read-only, holds no files" and stopped before the
sentence that follows.** That is a source read halfway — the same class of error this
desk has been correcting all week, including in itself twice today.

## WHICH IS THE ANSWER TO YOUR QUESTION ABOUT ITS LABELS

**The labels are honest, and they are honest about the wrong axis.**

Where I can check them, they hold. It refuses to invent a frequency ranking and says
so — *"Giving you an empirical first-to-fourth ranking would be invented"* — and that
is the single thing it would have been easiest to fake. It calls two rounds *"a
proposed policy, not an industry-standard number."* It calls 60–90 seconds *"a
starting setting, not a sourced optimum."* **Nothing there is dressed up.**

**But the labels classify how sure it is of its SOURCES. They say nothing about
whether it read OURS.** The Audit claim carries no hedge at all and it is flatly
wrong about our document. **It never once says "I read your charter", because it
didn't.**

**So hold it by this: trust its labels about the outside world, and verify every
sentence it writes about us.** Two of its three "consequences" are real and the third
is a document it never opened, and they are presented identically.

---

# THE ONE YOU ALREADY AGREE WITH — I AGREE, AND THE HARDER VERSION IS A CORRECTION TO MY OWN DOCUMENT

**`From:` is a claim, not authentication.** No disagreement. The service knows what it
launched; the header is text a desk typed.

**And on the harder version: Echo is right and I was wrong, in writing, in the design
document.**

Section 2 of the design says a gap in the arithmetic *"means a file moved between
desks without going through the mail"* and calls the other direction *"the bypass."*

**Echo:** *"'anything else proves unauthorised movement' is false — partial writes or
interrupted service operations can also break it. And a passing count does not prove
lawful movement."*

**Both halves are correct.** A crashed desk breaks the invariant with nobody at fault
— that is collision 2, from my own document, proving Echo's point against my own
wording. And a file moved by hand keeps its counts intact, so a green invariant is
evidence of nothing.

**The invariant is a consistency check that can FLAG. It is not proof of wrongdoing
and its passing is not proof of anything at all.** My wording overclaims and it is
mine to fix.

---

# WHAT IT BORROWED THAT DOES NOT FIT — AND WHAT IT DID NOT KNOW WE ALREADY HAD

**The two state tables are the clearest case.** Twenty-odd states across two machines,
for six desks on one computer. That is Temporal and Airflow vocabulary carried over
whole. **Echo warns about this itself, twice, and then does it anyway.**

**The separation is right and the enumeration is not our size.** Splitting *what must
happen next* from *what this desk visit is doing* is correct and cheap — **and we
built it this morning** as `blocked_on` / `clears_by` plus the per-desk lock. Same
distinction, a tenth of the machinery.

**Three things it recommends that already exist and it could not know:**

    dead-letter handling        _needs_review/ at the repository root
    independent watchdog        the heartbeat, read by the nightly auditor AND
                                the Adjutant - design section 10
    a defined day for the
      start ceiling             America/Chicago, in the brakes spec

**Not its fault. Worth recording so nobody builds them twice** — this project has a
finding about reinventing the same idea seven times.

---

# WHAT IT GAVE US THAT WE DID NOT HAVE. FOUR THINGS, AND ONE IS A DEFECT IN MY OWN SPEC.

**1. RESERVE THE LAUNCH BEFORE LAUNCHING. THIS ONE IS MINE AND IT IS WRONG TODAY.**

> *"record reservations durably BEFORE launching. The sixth start in a rolling fifteen
> minutes and the twenty-first in the defined day must be refused rather than started
> and noticed afterwards."*

**My brakes spec counts from `wake_start` records, which the launcher writes at launch
time.** If the process starts and that write fails, the wake happened and the counter
never saw it. **The ceiling is short by one and nothing says so.**

Reserve first, launch second, identify the process third. **A defect in a document I
filed this afternoon, found by an outside desk, and I would not have found it by
re-reading my own spec.**

**2. THE WINDOWS CLAIM — AND IT IS THE ONE I VERIFIED AGAINST THE PRIMARY SOURCE.**

Echo says a watcher notification is *"a prompt to inspect, not an authoritative work
record."* Microsoft's own page for `ReadDirectoryChangesW`:

> *"If the buffer overflows, ReadDirectoryChangesW will still return true, but the
> entire contents of the buffer are discarded"*

> *"you should compute the changes by enumerating the directory or subtree"*

> *"ReadDirectoryChangesW fails with ERROR_NOTIFY_ENUM_DIR when the system was unable
> to record all the changes to the directory."*

**Quoted accurately. The label was ESTABLISHED and it is established.**

**And it lands on us.** `watcher-go/main.go` sweeps `inbox/` once at startup, then runs
an event loop forever. Its `watcher.Errors` branch does one thing: `logMsg("watcher
error: %v", err)`. **There is no periodic rescan and an error triggers nothing.**

**So a dropped notification means a letter sits in `inbox/` unread, and the only trace
is one line in a log nobody reads.** That is the mail service losing post silently,
which is the one thing it must never do. Sent to Build.

**3. The delivery arithmetic.** Collision 1. Real, and it corrects a number of yours.

**4. The unstamped-visit hole.** Collision 2. Real, and it corrects a rule of mine.

---

# WHAT I WOULD NOT TAKE FROM IT

**Not the state tables.** Right idea, wrong size, and we have the useful half already.

**Not "two rounds."** It says itself that is a proposed policy and not a sourced
number, and the number is yours.

**Not the ranked failure list as a priority order.** It labels it a forecast honestly,
and a forecast about a system nobody has run is not a work queue.

**And I have not re-read its other nine primary sources.** I checked the one with a
direct consequence for our own code. **A full citation audit is a separate job and
belongs with Audit, not with me** — hard rule 16, verification from a different
source, and I am not the right different source for a document I have just formed a
view on.

---

**Nothing above is adopted, nothing in the brakes or the doorbell changed on the
strength of it, and Build carries on.** The one thing I have sent onward is the
watcher defect, because it is live today and has nothing to do with the chain.

*C1, 2026-09-10.*
