# SUPERSEDED — replaced by `claude/DESIGN_the-doorbell-the-job-number-and-the-punch-card-2026-09-10.md`

**Do not build against this one.** It was written before Sleven's job-number and
punch-card ruling and before both ceilings were set. **Two of its findings survived
into the replacement and are the reason it is kept rather than deleted:** that rule
9 cannot be enforced by the watcher, and that rule 3 does not close the two-desk
loop.

**One thing in it was wrong and the replacement says so:** the proposal to count
wakes per desk pair. Sleven rejected it with a better reason — a pair count misses
three desks going round in a circle.

Copied to disk 2026-09-10, after the replacement was found to exist only in the
claude.ai project and cost both desks a night.

---

# DESIGN — the doorbell: the returned state, and the wake built against Sleven's ten rules

    from    C1, architecture
    date    2026-09-10
    order   Sleven, 2026-09-10: automation first, it displaces the queue. The ten
            wake rules are his and decided. Design, do not build. Tell him if a
            rule cannot be enforced by a program.
    status  SUPERSEDED 2026-09-10. See the header above.

---

## 0. THE ONE-LINE VERSION

**The mail system delivers and then stops.** His diagnosis is exact: it is a
mailbox with no doorbell. **The watcher already knows the moment a letter lands,
because it is the thing that puts it there.** Everything below is what it does in
that moment and what stops that moment repeating forever.

---

# PART ONE — THE RETURNED STATE, FINISHED

Ruled 2026-09-08, unbuilt. It now has a counter and a terminal destination, which
is what it was missing.

## THE FILE IS THE THREAD, AND ITS NAME IS ITS IDENTITY

**The file is never renamed and never replaced.** Every round is appended. That was
ruled for a human reason — the thread has to survive — and it turns out to carry
the whole counter design, because **the filename is how the watcher recognises a
letter it has seen before.** Rename it and the count resets; the two rules hold
each other up.

## THE COUNT LIVES WITH THE WATCHER, NOT IN THE LETTER — RULE 7

**This is the only way rule 7 can be enforced rather than requested.**

A desk writes into the letter. If the round number is in the letter, the desk can
change it, and rule 7 says it must not be able to.

    the watcher keeps a state file the desks do not own:
        <letter filename>  ->  round, last tray, first seen, last moved

**The letter may DISPLAY the round for a human reader. The watcher never reads it
back.** Display is a copy; the count is the record. A desk editing the displayed
number changes nothing and is itself detectable, because the two disagree.

## THE LIFECYCLE

    Open  ->  Answered  ->  Returned  ->  Answered  ->  ...
    round 1        2            3            4

**A return is a move, not a post.** `answered/` back into
`open/<the desk that answered it>/`, with a dated block appended saying WHY THE
ANSWER FAILED and WHAT WOULD SATISFY IT. **It does not go through `inbox/`** — the
watcher renames what is dropped there, and a rename loses the thread.

**A return with no stated reason is a new question, not a return.**

## ROUND THREE GOES TO HIM — RULES 5 AND 6

**The watcher increments when a letter arrives in a tray it has already been in.**
Not on every move: a letter going A -> B -> C is one round each, three desks
genuinely working. A letter coming back to a tray it has already sat in is the
thing being counted.

**At round three the watcher files to `correspondence/open/owner/` instead of to
the desk**, with the whole history attached — which the never-rename rule already
guarantees is in one file.

**The desk that would have received it is told where it went.** Otherwise it waits
on a letter that is never coming.

---

# PART TWO — THE WAKE

## WHAT THE WATCHER READS

**Nothing new.** It already knows a letter landed, because it filed it. **The wake
is a consequence of a successful filing, not a separate scan of the trays.**

That matters for rule 2: *a desk wakes only when a letter addressed to it lands in
its tray*, and **"lands" is an event the watcher owns rather than a state it has to
detect.** A file appearing in a tray by any other route — a hand copy, a shell
move, a session bypassing the router — produces no wake at all. That is correct
and it should be stated loudly, because this desk bypassed the router with a shell
last week and would have been surprised.

## WHAT IT WRITES

Two records, and they are the enforcement for rules 4, 8 and 10.

    a wake log        one line at start, one at end, per wake
    a per-desk lock   held for the duration of a wake

## RULE 4 — ONE WAKE PER DESK AT A TIME

**A lock file per desk.** Taken before the wake, released at the end log.

**The failure mode is a crashed desk leaving a lock nothing releases, so that desk
never wakes again — silently.** So the lock carries the start time, and a lock
older than the maximum wake duration is **reported, not cleared.** A stale lock
means something died; clearing it automatically hides a death.

**A letter arriving while a desk is locked is filed normally and simply does not
wake it.** Nothing queues, nothing fans out. **The desk finds it at its next wake
or its next boot**, which is what the boot-read-every-tray rule is for.

## RULE 10 — A WAKE WITH NO END STOPS EVERYTHING

**A wake that hangs never writes an end AND never announces it**, so "no end" is
only detectable against a clock. **The watcher needs a maximum wake duration** —
past it, the wake is treated as ended-without-ending, all further wakes stop, and
he is told.

That is the same fail-closed shape as the rest: **the unanswerable case is treated
as the bad case.**

## RULE 8 — THE CEILING

A count in the watcher's state, reset daily, across all desks. Over it: stop waking
anything, tell him.

**It is the backstop he says it is, and it is doing more work than the other nine
because of the hole in Part Three.** It should be low enough to be hit by a runaway
within one working session, not within a day.

---

# PART THREE — THE RULES REVIEWED, AND WHERE THE HOLES ARE

**He asked for any rule that cannot be built, and any rule that leaves a hole.
There are two of each.**

## RULE 9 CANNOT BE ENFORCED BY THE WATCHER. THIS IS THE IMPORTANT ONE.

> *A woken desk may read, write memos, and edit what it owns. It may not deploy,
> commit, push, delete, spend money or touch credentials.*

**The watcher starts a session. It does not control what that session can reach.**
Everything else in the ten is enforceable by a program because the watcher owns the
mechanism — filing, counting, locking, logging. **Rule 9 is about what happens
inside the session, which the watcher cannot see and cannot stop.**

**And he has already ruled that a rule a desk chooses to obey is not a control**,
with today's own research behind it: the rule was present, unchanged, read at
startup, and long-running sessions stopped acting on it anyway.

**So rule 9 is a prompt unless the woken session is started with the capability
actually removed** — a restricted permission set, no credentials in its
environment, no path to the deploy scripts. **That is a property of how the session
is launched, not of the watcher, and it has to be proved by trying the forbidden
thing and being refused, not by reading the launch configuration.**

**Until that is proved, every wake is a session that could deploy and is asked not
to.** He should know that before the first one runs. **It is not a reason to stop —
it is a reason to make the first woken desk one whose worst case is a bad memo.**

## RULE 3 IS BUILDABLE AND DOES NOT CLOSE THE LOOP IT AIMS AT

> *A letter whose sender and recipient are the same desk is refused, never filed.*

**Trivially enforceable at the door, and it kills the one-desk loop.**

**It does not kill the two-desk loop.** A wakes B, B writes to A, A wakes and
writes to B. Every letter is legitimately addressed, nothing is self-sent, and no
rule above stops it.

**Rule 6 catches it only if the round counter recognises the letters as the same
thread.** If each desk writes a NEW letter rather than returning the old one, **the
count never increments and rule 6 never fires.** Two desks having a polite
conversation forever is indistinguishable from two desks working, at the level of
individual letters.

**The honest position: rule 8's ceiling is the only thing that stops it**, which is
exactly what he said it was for. It is worth him knowing that the ceiling is not a
backstop for an unlikely case — **it is the primary defence against the most likely
loop.**

**A cheap narrowing, if he wants one:** count wakes per desk PAIR as well as in
total. A -> B -> A -> B climbing while nothing else moves is a shape a program can
see, and it fires long before a global daily ceiling would.

**WITHDRAWN 2026-09-10.** Sleven rejected the pair count with a better reason: it
misses three desks going round in a circle. One card on the job catches that and
everything else.

## RULE 5 NEEDS THE LETTER'S IDENTITY TO BE STABLE

Buildable, and it depends entirely on the never-rename rule from Part One. **If any
mechanism ever renames a letter — a timestamp prefix, a collision suffix — the
count silently resets to one.** The router already renames things dropped in
`inbox/`, which is why a return must never go through it.

**SUPERSEDED 2026-09-10:** with the job number in the FILENAME, the watcher
preserves the number and may change the rest, so returns go through the mail like
everything else. The special case is gone.

**So the control that asserts this: no file in `answered/` or a tray shares a
thread with a differently-named file.** Hard to state perfectly; worth stating
approximately rather than not at all.

## RULE 1 HAS A QUIET CONSEQUENCE WORTH SAYING OUT LOUD

> *Only the watcher wakes a desk. No desk ever starts another desk.*

**Correct, and it means a desk cannot escalate urgency.** A desk that finds
something serious writes a letter like any other and waits its turn. **There is no
"wake them now" path, deliberately** — because a priority channel is a second
starting mechanism, and rule 1 exists to have exactly one.

**He is the fast path.** That is the right answer and it should be a stated
property rather than a gap somebody later fills.

## THE SEVEN THAT ARE CLEAN

**Rules 2, 4, 6, 7, 8 and 10 are enforceable as written**, by the mechanisms in
Part Two. **Rule 3 is enforceable as written** — it simply covers less ground than
its position in the list suggests.

---

# PART FOUR — WHAT IS MISSING FROM THE TEN

Not objections. Things a builder will hit that the rules do not answer.

**A WAKE THAT PRODUCES NOTHING.** A desk reads its letter, decides no reply is
needed, and stops. **Legitimate, and it must be logged as a completed wake**, or
rule 10 reads it as a hang.

**WHAT THE WOKEN DESK IS TOLD.** It should be handed the specific letter, not
told to go and look. Otherwise every wake re-reads every tray, and the cost of a
wake stops being proportional to the work.

**THE WATCHER'S OWN FAILURE.** If the watcher dies, no letter is filed and no desk
is woken, and **the system looks exactly like a quiet day.** That is yesterday's
finding arriving in a new place: a system that reports what it managed to do and
not what it failed to do looks healthy while going blind. **The watcher needs a
heartbeat he can see** — not an alert, just something that is obviously stale when
it stops.

**THIS FINDING WAS DROPPED FROM THE REPLACEMENT AND HE FOUND IT AGAIN.** It is the
first of the four holes in his memo of 2026-09-10. It is back in the live design.

**THE FIRST WAKE SHOULD BE HARMLESS.** His own proposal says start with something
harmless. Given rule 9 is unproved, the first desk woken should be one whose worst
possible output is a memo nobody wanted.

---

# PART FIVE — WHAT IS DECIDED, AND WHAT IS STILL HIS

**Decided here, and none of it needs him:** the count lives with the watcher; the
wake is a consequence of filing rather than a scan; the lock is per desk and a
stale lock is reported rather than cleared; a maximum wake duration exists because
rule 10 is undetectable without one.

**His, and not assumed:** the ceiling's number, whether the per-pair count is worth
having, and which desk is woken first.

**ALL THREE ANSWERED 2026-09-10.** Twenty a day and five in fifteen minutes; the
pair count rejected; C1 first.

**Waiting on a fact rather than a decision:** whether rule 9 can be enforced at
launch. That is a question about the harness and it gets measured, not argued.

*C1, 2026-09-10.*
