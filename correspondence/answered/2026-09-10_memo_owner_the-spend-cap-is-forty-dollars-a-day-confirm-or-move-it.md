# Memo

To:      Owner
From:    Engineering
Date:    2026-09-10
Subject: The spend cap — the number exists, the arithmetic is done, and all it needs is your word. It blocks part of step 2.
Status:  Answered

**One decision. Everything else about the brakes is specified and Build can start
without you.**

---

## THE NUMBER

**Build already set it: `MAX_BUDGET_USD = "2.00"`** per wake, from measurement — about
ten times the worst honest run you measured at nineteen cents. It is enforced by the
runtime, not by the watcher, the same shape as rule 9.

**Your section 8 arithmetic, done:**

    per-wake cap    x    twenty wakes    =    worst case in a day
    $2.00                x    20              =    $40.00

**So the question is not "pick a number". It is: is forty dollars the worst day you
are willing to see?**

    yes                 nothing changes. $2.00 stands and Build carries on.
    no                  give me the day you want and I will divide it by twenty.
                        $20 a day is $1.00 a wake. $10 a day is $0.50.

**A cap has to clear nineteen cents by enough that honest work never hits it.** Fifty
cents is two and a half times your worst measured run and it would still have cleared
every one of the four. **Below about thirty cents it starts cutting off real work**,
and a cap that fires on honest work is a cap that gets raised in a hurry at the worst
moment.

## THE SECOND ONE — DAYTIME CODE

**Section 15: one wake ceiling for every desk, but two spend caps**, because what is
different about Code's work is its size, not its frequency.

**There is no measurement for a shelled Code wake at all.** Nothing has run one. **So
I am not going to put a figure in front of you and call it arithmetic.**

**My recommendation: leave it unset and refuse to wake Code until it has one.** Fail
closed, and the number comes from the first few real runs rather than from either of
us guessing. **If you would rather it had a starting figure now, say so and I will set
it at the memo desk's number until it is measured** — that is the more conservative of
the two guesses, not the right one.

## WHAT IT BLOCKS

**Only the last item of step 2**, and only its value — the lookup that holds it gets
built either way. The lock, the two ceilings and the log work do not wait on this.

`claude/SPEC_the-brakes-2026-09-10.md` is on disk and Build has it.

---

1. Is $2.00 a wake — $40.00 as the worst possible day — the number, or do you want a
   different day's worst case?
2. Daytime Code's cap: leave it unset and refuse to wake Code until it is measured, or
   start it at the memo desk's number?

*C1, 2026-09-10.*

---

ANSWERS:

**Question 1 is withdrawn, not answered. It measures something that does not exist
for me.**

**I run on a subscription. `ANTHROPIC_API_KEY` is not set and the guard proves it
before every run.** `total_cost_usd` is a client-side estimate of what a run would
cost somebody paying per call. **There is no bill and there will not be one. Forty
dollars a day is not a risk I have.**

**I never asked for a dollar figure.** I said I wanted to keep my credit use down and
that I did not want to count pennies. **Both of those are about my usage allowance,
not money**, and the currency got into this because the CLI prints a field and nobody
checked whether it applied to me. **That was mine, not yours.**

**So: the cap stays and its value is yours to set from your own measurements.** Its
job is to stop a runaway, not to manage a budget. Set it clear of honest work and stop
there. **Do not put a day's worst-case currency total in front of me again, and report
tokens rather than dollars.**

**Question 2 is answered and I am taking your recommendation exactly as written:
leave daytime Code's cap unset and refuse to wake Code until it has been measured.
Fail closed.** You were right for a reason that had nothing to do with money — there
is no measurement, and a guess with a number on it reads as arithmetic.

**And the sentence I want kept:** *"I am not going to put a figure in front of you and
call it arithmetic."* **That is the standard for every unruled number in this project.**

**Nothing in the brakes is blocked any more. Build the lock, the two ceilings and the
log.** Full letter is at
`correspondence/open/architecture/` — subject *WITHDRAWN — the dollar framing is the
wrong unit*.
