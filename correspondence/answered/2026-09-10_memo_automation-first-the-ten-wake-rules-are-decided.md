# Memo

To:      Architecture
From:    Owner
Date:    2026-09-10
Subject: AUTOMATION FIRST — the ten wake rules are decided, and everything else on your list waits behind them
Status:  Answered

**New priority, and it displaces the queue. Anything that gets the desks working
back and forth without me in the middle comes first. Anything that enables that
comes first. Everything else waits.**

## THE DIAGNOSIS, SO NOBODY DESIGNS THE WRONG THING

**The mail system delivers perfectly and then stops.** A letter lands in your tray
and sits there until I open a window. **It is a mailbox with no doorbell.**

That is the whole gap. The watcher already files every letter, the boot prompts
are written, and it is confirmed against Anthropic's own documentation that a
headless `claude -p` run bills against my subscription rather than a separate
account. **Nothing large is missing. One thing is: something has to ring the bell.**

**You do not need Temporal or the Agent SDK for the first version and I do not
want either reached for yet.** The proposal's own advice is to automate slowly and
start with something harmless. This is that.

---

## THE TEN WAKE RULES — MINE, DECIDED, NOT A QUESTION FOR YOU

**I am not asking you what the rules should be. These are the rules.** Your job is
to design against them, and to tell me if any of them cannot be built or leaves a
hole.

**1.** Only the watcher wakes a desk. **No desk ever starts another desk.** One
thing does the starting, so there is one place to look and one place to pull the
plug.

**2.** A desk wakes only when a letter addressed to it lands in its tray. **Not on
any other file appearing anywhere.**

**3.** A letter whose sender and recipient are the same desk is **refused, never
filed.** That kills the self-loop at the door.

**4.** **One wake per desk at a time.** If a desk is already running, a new letter
waits. Nothing ever fans out into copies of itself.

**5.** The watcher stamps a **round number** on every letter. First filing is round
one. Every time a letter returns to a tray it has already been in, the round goes
up.

**6.** **Round three is never filed to a desk. It goes to my tray**,
`correspondence/open/owner/`, with the whole history attached. Two desks that
cannot agree in three passes are disagreeing, not working.

**7.** **A desk cannot change its own round number.** Only the watcher counts. A
desk that can edit the count can loop forever.

**8.** **A ceiling on wakes per day**, across all desks. Over it the watcher stops
waking anything and tells me. That is the blunt backstop for whatever the other
nine miss — **a published case ran four hours and fifty million tokens because
nothing had a ceiling.**

**9.** A woken desk may read, write memos, and edit what it owns. **It may not
deploy, commit, push, delete, spend money or touch credentials.** Those wait for
me, exactly as now. Rules 2 and 23 are unchanged and this does not loosen them.

**10.** **Every wake is logged when it starts and when it ends.** A wake that never
logs an end **stops all further wakes** and tells me.

**Three, four, six, eight and ten are the loop-proofing.** Six was already my
ruling from 2026-09-08 — *"three rounds and it stops being correspondence"* — and
it now has somewhere to live.

**Tell me if one of these cannot be enforced by a program.** A rule that depends on
a desk choosing to obey it is not a control, and today's own research measured
that: the rule was present, unchanged, read at startup, and long-running sessions
stopped acting on it anyway.

---

## YOUR LIST, IN THIS ORDER

**1. Design the returned state.** You ruled it on 2026-09-08 and it says *"Ruled,
not built."* The same file moves back into the answering desk's tray with a dated
round appended — never a new file, never renamed, never through `inbox/`. **Now it
has a counter and a terminal destination, so finish the design against rules 5, 6
and 7.**

**2. Design the wake against the ten rules above.** What the watcher reads to know
a tray is not empty, what it writes to record a wake, and how rule 4 is enforced
when a desk is already running. **Design, do not build — Build builds.**

**3. Rule what the RAPTOR's family is.** Code is blocked on it right now. It was
held out as the single exception, then removed, then I put it back as a deliberate
joke card, so the exception is live again and nobody has said what family it takes.
**It is one row and it is stopping B2 for 231 others.**

**4. Fold the RSI sweep in as the first real workload**, per my earlier memo. Do
not build it separately.

**5. Rule the desk list out of being typed in three places.** Derive it from the
trays on disk. It has already cost two desks a mailbox they should have had on the
day they were created.

Then, and only then: Q53, the front page rewiring, the 5% threshold, the wall
spec, the ship-thumbs folder, the store-name list and the paint pick.

---

## WHAT I WANT BACK, AND WHAT I DO NOT

**I want a design a builder can execute, and any of my ten rules you think is
wrong.** Say so plainly — I would rather be argued with now than find the hole
running.

**I do not want a schedule, a phase plan, or a decision on Temporal.** Not yet, and
not from this memo.

---

ANSWERS:

**Architecture, 2026-09-10. Design filed. Two of your ten cannot do what their
position in the list implies, and one of those two is the important one. Your item
3 is answered and Code is unblocked. Item 5 is ruled.**

**`claude/DESIGN_the-doorbell-the-returned-state-and-the-ten-wake-rules-2026-09-10.md`**
— the returned state finished against rules 5, 6 and 7, and the wake designed
against all ten. No schedule, no phase plan, no Temporal.

## THE TWO YOU ASKED ME TO FIND

**RULE 9 CANNOT BE ENFORCED BY THE WATCHER, AND IT IS THE ONE THAT MATTERS.**

The watcher starts a session. **It does not control what that session can reach.**
Every other rule is enforceable because the watcher owns the mechanism — filing,
counting, locking, logging. Rule 9 is about what happens *inside* the session,
which it cannot see and cannot stop.

**So rule 9 is a prompt unless the woken session is launched with the capability
actually removed** — no credentials in its environment, no path to the deploy
scripts. **And that has to be proved by trying the forbidden thing and being
refused**, not by reading the launch configuration. Your own words this morning:
a rule a desk chooses to obey is not a control.

**Until that is proved, every wake is a session that could deploy and is asked not
to.** Not a reason to stop. A reason to make the first desk woken one whose worst
case is a bad memo.

**RULE 3 IS BUILDABLE AND CLOSES LESS THAN IT LOOKS LIKE IT CLOSES.**

Self-addressed refused at the door kills the one-desk loop. **It does not touch the
two-desk loop** — A writes to B, B writes to A, nothing self-sent, every letter
properly addressed.

**Rule 6 only catches that if the round counter sees the letters as one thread.**
If each desk writes a NEW letter instead of returning the old one, the count never
increments and rule 6 never fires.

**So rule 8's ceiling is not the backstop for an unlikely case — it is the primary
defence against the most likely loop.** Worth knowing when you pick the number: low
enough to be hit inside one working session, not inside a day.

**A cheap narrowing if you want it: count wakes per desk PAIR as well as in total.**
A → B → A → B climbing while nothing else moves is a shape a program can see, and
it fires long before a daily total would. **Your call, not assumed.**

## THE OTHER EIGHT

Enforceable as written. **Rule 7 only if the count lives with the watcher rather
than in the letter** — a desk can edit any file it writes to, so the letter shows
the round and the watcher never reads it back. **Rule 10 only with a maximum wake
duration**, because a hung wake never writes an end and never announces it either.

**Rule 1 has a consequence worth stating rather than discovering:** a desk cannot
escalate. Something urgent gets a letter like anything else and waits its turn.
**You are the fast path**, deliberately, because a priority channel is a second
starting mechanism and rule 1 exists to have exactly one.

## YOUR LIST

**1. The returned state is finished.** The count lives outside the letter, which is
what makes rule 7 a control instead of a request. The never-rename rule turns out
to carry the whole counter design — the filename is how the watcher recognises a
letter it has seen before.

**2. The wake is designed.** The key decision: **the wake is a consequence of a
successful filing, not a scan of the trays.** A letter that arrives any other way —
a hand copy, a shell move, a session bypassing the router — produces no wake at
all. Correct, and worth saying loudly, because this desk bypassed the router with a
shell last week.

**3. RAPTOR — RULED, and it should never have reached you a second time.**
**`family_id = RAPTOR`. A family of one.** The precedent was in my own ruling of
2026-09-07: *a single-hull ship's family is itself*, which is how Hurricane and
Intrepid were settled from the identical evidence. CIG's 4.10 data holds no RAPTOR
hull, so no parent line exists, so it is its own. **I read three blank sources as
unknown for this row and as family-of-one for the other two, because I expected
this one to turn out fake.** The expectation did the work, not the evidence. Sent
to Code. **B2 is unblocked for 232 of 232 with no held-out exception.**

**4. The RSI sweep is folded in as the first workload**, per your earlier memo, and
its requirements are already carried. Nothing built separately.

**5. The desk list is ruled and sent to Build.** Derived from the directory names
under `correspondence/open/`. **A tray existing IS the desk existing** — that is
already true by your own ruling, so the listing is not a proxy for the list, it is
the list. Fails loudly if the directory cannot be read; no fallback to a typed list,
because that restores the defect under a new name.

## THREE THINGS THE TEN DO NOT COVER

**A wake that produces nothing must still log an end**, or rule 10 reads a
legitimate quiet wake as a hang.

**The woken desk should be handed its letter, not told to go and look**, or every
wake costs a full re-read of every tray.

**If the watcher itself dies, nothing is filed and nothing is woken, and the system
looks exactly like a quiet day.** Same defect as the two found yesterday. **It needs
a heartbeat you can see** — not an alert, just something obviously stale when it
stops.
