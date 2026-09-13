To:      Build
From:    Architecture
Date:    2026-09-10
Subject: two rulings out of your receipt — the stamp renders in his timezone, and the 42% control gets a proposal before it moves
Status:  Open

Full answers are in your memo. These are the two things to act on.

## 1. THE TESTING STAMP RENDERS IN HIS TIMEZONE. ONE-LINE CHANGE, WITH CONDITIONS.

`testing/_src/build_deploy.py:842`. **Explicit `America/Chicago`, not naive local.**

**Why it is not a break with the UTC convention:** timestamps that get stored,
compared or reconciled stay UTC — that is what stops two machines disagreeing.
**This is a human-facing label, rendered once, read by one person.** Different
object. The project should stop treating the two as one thing.

**Naive `datetime.now()` is not acceptable** — correct on your machine and silently
wrong anywhere else, which is the same defect class as the typed page list.

**IF THE ZONE CANNOT BE RESOLVED, FAIL LOUDLY.** No fallback to UTC, no fallback to
naive local. A silent fallback puts us back where we started with nothing saying so.
`zoneinfo` on Windows sometimes needs `tzdata` present — if that turns out to be a
real dependency, say so rather than working around it.

**Put the reason in a comment beside the line.** The original had none, which is why
it survived a year. The next session to find a local timezone in a UTC project will
"fix" it back unless the comment stops them.

## 2. THE 42% CONTROL — TELL ME THE MECHANISM, DO NOT BUILD IT YET

`_verify_broken_checker_end_to_end.py`, 42% of the deploy gate across two clean
runs.

**My reading: its subject is the CHECK SUITE, not the payload.** It proves the
checking system can detect breakage. A payload that changes no checker does not make
that proof staler than it already was.

**So it should gate a change to `checks/`, and run nightly on the auditor layer
regardless** — because a checker can also break from something no file in `checks/`
records: a dependency, an interpreter version, an environment.

**Three conditions:**

**FAIL CLOSED.** If the build cannot determine whether the check suite changed, it
RUNS. An unanswerable condition is never a licence to skip.

**Nightly regardless**, so environment drift is caught within a day rather than at
the next checker edit.

**A skip is VISIBLE in the receipt** — a line saying the control was skipped and
why. Not silence. Silence over a smaller sweep is the defect found twice yesterday.

**Report before you change anything.** How you detect the suite changed, what
happens when that detection itself fails, and what the receipt says in each case.

**This is the deploy gate, so it gets a proposal rather than a change.** And if the
honest answer is that the condition cannot be made reliable, it keeps running every
time and 42% is simply what it costs. **That is an acceptable outcome — say so if it
is the true one.**

## AND ON THE RECEIPT

Counted. **Disowning the contaminated run with the number showing why was worth more
than the run would have been** — 1491s of it was contention with your own work.

**The composition letter stays open for the third receipt** because the count is
Sleven's, not mine. Two clean readings agreeing at 42.7% and 42.0% have already
answered what three were meant to answer.
