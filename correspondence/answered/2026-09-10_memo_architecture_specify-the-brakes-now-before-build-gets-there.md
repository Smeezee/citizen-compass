# Memo

To:      Architecture
From:    Owner
Date:    2026-09-10
Subject: Specify the brakes now — Build is blocked on a poke and I do not want it blocked twice
Status:  Answered

**Build has finished step 0 and its dry run is clean. It is stopped waiting for a
word from me, and the word is in its tray.**

**The next thing it needs after the probe is your brakes specification, and if that
is not written when it gets there, it stops again.** I would rather it never
notices the gap.

## WRITE IT NOW, BUILDABLE

Step 2 of the build order. **Nothing is automatic until this exists and has been
proved by being tripped on purpose.**

    THE TWO CEILINGS      twenty wakes a day, five in any fifteen minutes
    THE LOCK              one wake per desk at a time
    THE SPEND CAP         per wake, and it is a real flag - Build has it working
    THE WAKE LOG          what a record carries, and the stop-everything rule
    THE SWITCH            off means nothing is woken; mail still files, work in
                          hand still finishes

## THE FIVE THINGS I WANT ANSWERED IN IT

**1. Where does the count live, and does it survive the watcher restarting?**
You told me the punch count must survive a restart or the freeze is a suggestion.
**The same question applies to the day's wake count**, and it is worse here — the
first thing anyone does to a watcher that looks stuck is restart it, and that is
exactly when the count is high.

**2. What happens at the moment a ceiling trips.** Not "it stops and tells me" —
what stops, what is already in flight, what happens to the letter that would have
caused the twenty-first wake, and how it resumes.

**3. A stale lock is reported and not cleared** — your own rule. **Say who reads
that report**, because a report nothing reads is the shape this project keeps
paying for.

**4. The notice path is not throttled.** Your own finding: a notice into my tray is
not a wake and must not count against either limit, or a burst of trouble silences
the thing that reports trouble.

**5. How each brake is PROVEN.** Your section 9 standard, applied to all four:
**deliberately trip it and be refused.** A brake that has never fired is a brake
nobody has tested. **Say exactly what Build should do to make each one fire.**

## AND THE ONE I HAVE NOT DECIDED

**Whether the switch is one switch or one per desk.** One is simpler and I will
never mis-set it. Per-desk lets me stop one runaway without stopping everything.
**Give me your answer rather than the options.**

## WHY THIS IS URGENT AND THE OTHER THINGS ARE NOT

**Every stall today has been a desk arriving somewhere the next instruction had not
been written yet.** Build at 00:33 on a design that was not on disk. Build at 12:16
on a word that had not been given. **This is the third one and it has not happened
yet, which is the only reason it is worth a letter.**

---

ANSWERS:

**Architecture, 2026-09-10.**

    claude/SPEC_the-brakes-2026-09-10.md

**On disk, in the repository, and in Build's tray.** Your five questions are answered
in it and the switch is decided. Below is only what you would not get by reading the
headings.

**It was already written when your letter arrived** — `wake_desk.py` says in its own
docstring that the brakes are Architecture's, and your GO memo to Build said the same,
so it was a job pointed at this desk with no letter attached to it. **Your letter then
added five things it did not cover**, and those are sections 7, 8 and 9.

## 1. THE COUNT — THE WAKE LOG IS THE COUNTER AND THERE IS NO SECOND ONE

`logs/wake_log.jsonl`, on disk, survives any restart. Derived, never stored, same as
the desk list and the roll call.

**Your restart worry is right and it needs one thing the punch rule did not.** "Missing
means fail closed" applied here would mean a brand new install can never wake anything.
**So the log is opened once, deliberately, with a `log_opened` record — and after that a
missing file is fail closed.** That makes "never installed" and "wiped" distinguishable,
which is the whole point of the rule.

**And the log has already changed shape once with no version field.** Two records on
disk key the desk as `desk`; the current code writes `label`. **A count that quietly
skips a shape it does not recognise undercounts wakes, and an undercounted wake is a
ceiling that permits too many.** Unrecognised line now fails the count. Those two
records are not migrated — they are the evidence of the first successful wake.

## 2. THE TRIP — AND YOU MADE ME FIND A HOLE ANSWERING IT

The check runs before the lock and before any process, so the twenty-first wake costs
nothing. **What is already running is not killed** — the ceiling governs starting.

**The letter stays where the watcher filed it. And that is where the hole was.** Section
4 says a wake is a consequence of filing, never a scan — **so a letter held by a ceiling
would sit in a tray looking like ordinary post and nothing would ever pick it up again.**
Your own defect, arriving inside the brake built to prevent it.

**Fixed without reintroducing a scan:** a withheld wake writes a `wake_withheld` record,
and when the ceiling clears the watcher replays **the list it wrote itself**, oldest
first, subject to the same ceilings. Nothing looks at the trays.

**The two ceilings do not behave the same way and treating them alike would be wrong in
both directions.** The fifteen-minute window is a THROTTLE and self-clears as records age
out — your own example is you, on day one, dropping three memos at once. **The daily
twenty is a STOP for the day**, clearing at midnight America/Chicago or on your word.
Twenty in a day is not traffic, it is a symptom, and a stop that lifts itself twenty
minutes later is not a stop.

## 3. WHO READS THE STALE-LOCK REPORT

**The Adjutant at the start of every conversation, and the nightly auditor control.**
The same pair as the heartbeat, for the same reason: the Adjutant catches it the moment
you speak to anybody, the nightly control catches one that happened while nobody did.
**Neither alone; together they are enough.**

**And the roll call renders it**, because a desk holding a stale lock reads as WORKING
to everything else — which is the exact confusion this system exists to remove.

## 4. THE NOTICE PATH

Not a wake, not counted, and **built so it cannot reach the counter at all** — a
separate function with no access to the ceiling code. **Not "remembers not to count
it."** A rule that depends on somebody remembering it is a rule with one reader, which
is the third time that shape has come up today.

## 5. HOW EACH ONE IS PROVEN

Section 9 of the spec has the exact steps. Two things worth saying here:

**The counter tests run on a REPLICA, not on the live log.** Seeding the real file with
fakes corrupts the evidence, and marking them as fakes lets the counter skip them, which
defeats the test. A copy of the repository — the method you already used for the four
headless runs.

**The spend cap is the one that must be real.** The runtime enforces it, not our code,
so a replica proves nothing. **Set it to a cent, launch one wake, and require the
refusal.** Pennies, and it is the only way to know the flag bites.

**And the daily ceiling's test shows BOTH sides of the boundary** — nineteen seeded,
the twentieth must LAUNCH, the twenty-first must be refused. Off-by-one is the likeliest
defect in a counter and a test that only shows the refusal would pass on a ceiling set
at nineteen.

## THE SWITCH — ONE SWITCH

**Not per-desk, and here is the reason rather than the preference.**

**A per-desk switch has a state that can be wrong in a way one switch cannot: three on,
one off, set weeks ago and forgotten.** A desk switched off individually looks exactly
like a desk with nothing to do — **which is the defect your other letter this morning is
named after.**

**And what a per-desk switch is for is already covered twice:** one desk looping is what
the ceilings catch, in fifteen minutes rather than at midnight; one desk that must not
run is what not giving it work achieves.

**THE COST, PLAINLY: stopping one broken desk stops all four.** That is the trade. It is
worth it because the switch's real job is the two-in-the-morning stop, where being
unmistakable beats being precise.

**WHAT WOULD CHANGE IT:** if you throw the master switch because of ONE desk more than
two or three times, that is a measurement result and per-desk has earned its way in.

## ONE THING YOUR LETTER GOT RIGHT ABOUT TODAY THAT IS WORTH KEEPING

**"Every stall today has been a desk arriving somewhere the next instruction had not
been written yet."** That is three for three and it is a better description of the
failure than anything in my design document.

**It is also an argument against my own tray discipline.** My tray was empty twice today
while a job with my name on it sat in somebody else's docstring. **A desk that only works
its tray waits to be asked.** Filed in my log.

*C1, 2026-09-10.*
