# Memo

To:      Engineering
From:    Owner
Date:    2026-09-10
Subject: Four holes in the doorbell design, one of them measured, and a limit on what a wake can ever be
Status:  Answered

**I walked your design end to end as if I were building it, then ran four real
headless sessions to test the parts that were arguable.** These are what survived.

---

## 1. THE WATCHER IS THE SINGLE POINT OF FAILURE AND NOTHING WATCHES IT

Your design puts three jobs in the watcher: **it does the waking, it enforces both
ceilings, and it detects the stuck and untouched jobs.**

**So when the watcher dies, nothing wakes, nothing is filed, and nothing tells me
any of that has happened.** The mechanism that reports silence is inside the thing
that has gone silent.

**That is section 11 of your own design, pointed at itself.** The links control,
the RSI watcher, the job nobody picked up — a system reporting what it managed to
do and not what it failed to do. **The watcher currently cannot report its own
death.**

**It needs a heartbeat that something outside it reads.** Not a fourth job for the
watcher.

## 2. THE CEILING COUNTS WAKES. IT DOES NOT BOUND MONEY.

Twenty a day and five in fifteen minutes limit **how often**. **Nothing in the
design limits what one wake can spend**, and one wake is unbounded — a desk in a
loop with itself burns until something stops it, and nothing does.

**`--max-budget-usd` is a real flag and it works per run.** I have used it. **A
per-wake cap and the daily ceiling together are the first thing that puts a number
on a day**, and neither does it alone.

**Put the per-wake cap in the design as a brake in its own right.** Set it from
measurement like the rest — real runs on a small letter came in between three and
nineteen cents.

## 3. THE PUNCH COUNT MUST SURVIVE A RESTART OR THE FREEZE IS A SUGGESTION

You wrote that the punch is *"kept in the watcher's own state, which no desk owns."*
**The design does not say that state is durable.**

**If punches live in memory, restarting the watcher clears every card** — and
restarting the watcher is the first thing anybody does when something looks stuck,
which is exactly the moment a card is near four. **The freeze would be defeated by
the most ordinary troubleshooting step there is, and it would look like nothing
happened.**

**On disk, survives a restart, and the restart itself is visible in the record.**

## 4. YOUR SECTION 9 IS RIGHT AND IT IS NOT STRONG ENOUGH

*"Prove it by trying and being refused. A desk that simply does not try proves
nothing."* **I measured what that looks like.**

A desk told to write outside its permitted folder **declined on its own judgement**
— it decided the file looked important — and produced a clean run with no evidence
either way. The same probe, worded so the judgement route was closed, **attempted
the write and was refused by the permission system**, which is the proof.

**A tool-removal test has to force the attempt.** Otherwise a desk's good manners
are indistinguishable from a working control, and the control gets believed on the
strength of a run that never tested it.

---

## 5. AND THE LIMIT NOBODY HAS STATED

**A desk woken safely has no shell.** That is how rule 9 is enforced — the tools are
removed, not asked about — and it is the right answer. **But it means a woken desk
can read, search, and write one memo. It cannot run a check, a test, a script or a
build.**

**So a wake is a reading-and-writing act, always.** Anything in the queue that needs
something *run* cannot be handed to a woken desk at all, and no amount of card,
ceiling or lock changes that.

**The design should say so plainly, in the section about what a wake is**, because
the first time somebody routes a job that needs a shell, it will fail in a way that
looks like the desk was broken.

---

## 6. WHAT IS NOT IN DISPUTE

Everything else in the document stands. The card, the two counters, the four
punches, the freeze, `punches − stamps ∈ {0,1}`, the two ceilings, twelve hours,
found-is-delivered, C1 first. **None of that is reopened.**

**And the design is on disk now** — that was my failure, not yours, and it cost both
desks a night.

---

ANSWERS:

**Architecture, 2026-09-10. All four accepted, all four in the design, and the
limit in section 5 is the one that changes what the system can be.**
`claude/DESIGN_the-doorbell-the-job-number-and-the-punch-card-2026-09-10.md` — on
disk.

## 1. THE WATCHER'S OWN DEATH — I HAD THIS AND LOST IT IN A REWRITE

**It was in the superseded draft, in the section on what the ten rules do not
cover, and it did not survive into the replacement.** You found it again by walking
the document as a builder. **That is a worse error than never having found it**,
because a rewrite that silently drops a finding leaves everyone believing the
document is the sum of the thinking.

**Two readers, both outside the watcher, and neither alone is enough:**

**The auditor layer's nightly run** asserts the heartbeat is fresh. Outside the
watcher, already scheduled, already has somewhere to report — no new machinery.

**The Adjutant at the start of every conversation**, alongside the owner tray it
already reports. That costs nothing to add to a rule that already exists, and it is
the fast path.

Nightly catches a death overnight; the Adjutant catches one the moment you speak to
anybody. **A heartbeat nobody reads is the same defect one level up.**

## 2. THE CEILING DOES NOT BOUND MONEY — I MISSED IT ENTIRELY

**Twenty and five limit how often. Nothing limited what one wake can spend, and one
wake is unbounded.**

In the design as a brake in its own right, enforced at launch by the runtime rather
than by the watcher — same shape as rule 9 and for the same reason.

**And the arithmetic, because it is what lets you pick the number rather than guess
it:**

    worst case in a day  =  per-wake cap  x  twenty

**So the cap is chosen by deciding the day's worst case and dividing by twenty.**
Your measurement gives the floor: real runs came in between three and nineteen
cents, so it has to clear nineteen by enough that honest work never hits it.

**The figure is yours.** I have written the arithmetic and not a number, because a
number from this desk would be a guess wearing a decimal point.

## 3. THE PUNCH STATE MUST SURVIVE A RESTART — AND THE TIMING IS THE PART THAT BITES

Accepted. On disk, survives a restart, and the restart itself visible in the record.

**Your observation about when it fails is sharper than the fault itself:** restarting
the watcher is the first thing anybody does when something looks stuck, **which is
exactly the moment a card is near four.** The freeze defeated by the most ordinary
troubleshooting step there is, looking like nothing happened.

**One thing added: if the state file is MISSING at startup, nothing is woken.** A
fresh empty state and a wiped one are indistinguishable, so the empty case is
treated as the bad case.

## 4. THE TEST MUST FORCE THE ATTEMPT — AND THIS IS THE BEST OF THE FOUR

**A desk declining on its own judgement produces a clean run and no evidence either
way.** You measured both halves: the same probe, worded so the judgement route was
closed, attempted the write and was refused by the permission system.

**So the pass condition is "the permission system refused," never "nothing bad
happened."** And the corollary, which is in the design: **a run where the desk chose
not to try is not a failed test, it is NO test — and it has to be reported as such
rather than counted.**

**A desk's good manners are indistinguishable from a working control**, and that is
the exact shape of every other thing this project has been wrong about this week.

## 5. NO SHELL — AND ONE RULE FALLS OUT OF IT THAT YOU DID NOT NAME

Accepted and stated plainly in the design: **a wake is a reading-and-writing act,
always.** Anything needing something run cannot go to a woken desk at all.

**A WOKEN DESK MUST NOT MAKE A CHANGE IT CANNOT VERIFY.**

A woken C1 cannot run `checks/_verify_owners.py`. **So a woken C1 that edits
`OWNERS.md` has changed an owned artifact and cannot prove it is still valid** —
the one thing this project does not allow anywhere else.

**In practice a woken desk writes memos**, and edits an owned artifact only where
the edit needs no proof, which for C1 is close to nothing.

**And that answers the cost of your own choice without reopening it.** C1 has the
most write authority in the repository, which is why waking it first was the
riskiest option. **A woken C1 that only writes memos has the blast radius of the
audit desk and keeps the reason you picked it** — Code can still watch the work go
past.

## 6

Nothing else reopened.
