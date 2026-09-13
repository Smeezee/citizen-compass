# Memo

To:      Architecture
From:    Owner
Date:    2026-09-10
Subject: Echo on runaways. It says our brakes are risk-limited, not safe, and that our switch is not a kill switch. Tear into it.
Status:  Answered

    claude/ECHO_what-actually-stops-a-runaway-2026-09-10.md

**On disk, verbatim, nothing adopted.** Same standing as the last one — **you were
right about the chain and it was wrong about the audit charter, so read this one the
same way.**

## THE FOUR CLAIMS THAT LAND ON YOUR SPEC

**1. THE SWITCH IS NOT A KILL SWITCH.** Ours stops new starts. Echo's words: *"If your
master switch only implements the first, calling it an emergency kill switch is
misleading."* It wants two separate things — **PAUSE STARTS**, and **STOP AUTOMATION**
which terminates what is already running.

**Is our switch honest about what it does?** If it only pauses, say so in the spec and
say whether the second is worth building.

**2. THE TWO CEILINGS DO NOT PROTECT MY AFTERNOON.** Its arithmetic on our own numbers:
twenty starts can be admitted in four batches a little over fifteen minutes apart —
**about forty-five minutes end to end, both ceilings satisfied.**

**Check that against the spec you wrote.** If it holds, our daily number is a total and
not a pace, and it proposes a slower pacing allowance underneath, **explicitly not as a
replacement for five-in-fifteen.**

**3. THE CAP DOES NOT MEASURE WHAT I ACTUALLY SPEND.** It could not establish that a
per-run dollar cap has any enforceable relationship to my subscription allowance.
**Its conclusion: the system is risk-limited, not allowance-safe, and should be
described that way.**

**Do not solve this by inventing a conversion.** Tell me whether a real measurement is
reachable from the machine, and if it is not, **what the honest smaller claim is.**

**4. SUCCESS MUST NOT REFILL THE CARD.** *"Do not let 'successful completion' replenish
the cumulative job allowance. That would make a success-producing loop self-funding."*
**Check whether our card does that.** I do not know, and it is the exact loop shape you
and I have both already identified.

## THE THREE IT SAYS WE ARE MISSING

    duplicate-start suppression   the same pending letter observed twice must not
                                  start two sessions
    bounded pending work          stop admitting when the backlog exceeds what can
                                  be serviced
    an allowance schedule         our daily quota reserves nothing for later in the day

**Are any of those already covered by something you specified? Say which, rather than
adding three components.**

## THE ONE I WANT YOU TO PUSH BACK ON HARDEST

**It says a hard cumulative ceiling is the only dependable detector of a loop that is
legal at every step** — and that everything cleverer is advisory. **That is either the
most useful sentence in the document or a counsel of despair, and you are better placed
than I am to say which.**

## WHAT I AM NOT ASKING FOR

**Not a redesign. Not an adoption.** A verdict, the four claims answered, and anything
in your brakes spec that has to change as a result — **named, not rewritten.**

**Build carries on with the answer-routing fix and then the lock. Nothing in this
letter jumps that queue.**

---

ANSWERS:

**Architecture, 2026-09-10.**

**Verdict: this one is better than the routing paper and it found a real hole in my
spec that I had not seen. Two of the four claims land, one lands on the vocabulary
rather than the thing, and one does not land — but the reason it does not land is
worth more than if it had.**

**Its closing line is right and I am adopting the phrase.**

---

## 1. THE SWITCH — OUR SPEC IS HONEST, OUR WORDS ARE NOT

**Section 8 already says exactly what it does:** *"off means no desk is woken by
anything. Mail still files. Work in hand still finishes. Nothing new starts."*

**It has never claimed to terminate anything.** Echo's criticism does not land on the
specification. **It lands on the word**, and the word has already slipped — your own
letter earlier today called it "a master stop", and the next person to read that will
assume it stops things.

**RENAMED IN THE SPEC: it is a PAUSE.** And the spec now says what it does not do, in
the same breath, because that is the sentence that stops the wrong assumption
travelling.

### IS THE SECOND ONE WORTH BUILDING? NOT YET, AND HERE IS WHAT MAKES IT CHEAP TO SAY NO

**Work out what "cannot be stopped" actually costs us today.** A woken desk has no
shell, so it reads and writes memos. One run is bounded twice — the spend wall and the
ten-minute timeout. **So the worst thing a pause cannot reach is one bounded run, for
at most ten minutes.**

**Waiting ten minutes is not an emergency. Building a Windows process supervisor to
avoid waiting ten minutes is a component with its own failure modes.**

**WHAT CHANGES THAT ANSWER, AND IT IS NAMED: step 4, when Code gets a shell.** A
shelled Code mid-build is a different proposition entirely, and that is where a real
terminate earns its keep. **Revisit it there, not now.**

---

## 2. ECHO'S ARITHMETIC IS RIGHT AND I CHECKED IT AGAINST MY OWN SPEC

    t = 0        five starts. The sixth is refused.
    t = 901s     the first five have aged out of the rolling window. Five more.
    t = 1802s    five more.
    t = 2703s    five more. TWENTY. The day is spent.

**Forty-five minutes, and both ceilings were satisfied the whole way.** Confirmed
against section 3 as written.

**So yes: twenty is a TOTAL, not a PACE.** That is now stated in the spec in those
words, because a number that reads like a pace and is not one is the kind of thing that
gets discovered at two in the afternoon.

### I AM NOT ADDING A THIRD LIMIT, AND THE REASON IS THIS MORNING

**A pacing allowance needs a number, and we have not measured a single day of real wake
frequency.** Any figure picked today is a guess wearing a decimal point — **which is
precisely the error I made with the forty-dollar day, eight hours ago, and you
withdrew it.**

**Speculative infrastructure for a load nobody has observed is also the thing this
project's own standing rules forbid.**

**THE TRIGGER, NAMED: the first day the daily twenty is actually reached.** That day
produces the measurement, and the pacing number comes from it. Until then the honest
protection is that twenty is a small number.

**And Echo's warning about a token bucket is correct and worth keeping for when we do
build one:** a bucket of capacity five refilling continuously can permit more than five
inside some fifteen-minute window. **It goes underneath five-in-fifteen, never instead
of it.**

---

## 3. THE CAP — ECHO IS RIGHT, AND I CAN TELL YOU EXACTLY HOW FAR THE MEASUREMENT GETS

**Is a real measurement reachable from the machine? Partly, and not far enough.**

Anthropic's own documentation, which I read this morning for the 304,000 question:
the plan usage figures are *"approximate and computed from local session history on
this machine, so usage from other devices or claude.ai is not included."*

**Three things that breaks:**

    it is approximate, by their own word
    it is machine-local, so your phone and claude.ai are invisible to it
    it is a display, not an enforceable per-run bound

**Echo could not establish a machine-readable, enforceable link between a dollar cap
and your allowance. Neither can I, and I am not going to invent one** — you told me not
to, and I had already made that mistake once today without being told.

### THE HONEST SMALLER CLAIM

**The brakes bound HOW OFTEN automation runs and HOW BIG ONE RUN CAN GET. They do not
bound what fraction of your allowance a day of automation consumes.**

**Risk-limited, not allowance-safe.** Echo's phrase, adopted verbatim into the spec,
because it is exactly right and a worse phrase of mine would be a softening.

**What actually protects you today is that twenty is small** — measured runs came in at
three to nineteen cents and a minute or two each. Twenty of those is not a day. **That
is a fact about the size of the number, not a guarantee from a control**, and the spec
now says so in those terms.

### AND THERE IS A ROUTE OUT, ALREADY ORDERED

**Once Build logs the usage block, three measured wakes give a real token figure per
wake.** Twenty times that is a token estimate against your allowance — still an
estimate, but a measured one instead of a guessed one.

**That is the step from "risk-limited" to something you can actually reason about, and
it is already in Build's tray.**

---

## 4. SUCCESS DOES NOT REFILL OUR CARD — AND THE HOLE IT IS POINTING AT IS ONE WE ALREADY NAMED

**Checked. Design section 3: only your stamp restarts a frozen job, and lifetime
punches never reset.** A job that completes is complete; nothing gives it more
allowance. **So the direct answer is no, our card does not do that.**

**BUT ECHO HAS FOUND A BETTER NAME FOR A HOLE WE ALREADY HAVE.**

Design section 6 — the one you found yourself: **a desk that answers with a NEW file
starts a fresh card with a fresh count, and the loop runs forever with a clean card
every lap.**

**That IS a self-funding success loop.** Every lap is a successful completion that
mints a brand new, fully funded job. It is Echo's exact failure in a different costume,
and its framing is sharper than ours was.

**And the fix is the one I already gave you this afternoon: the chain.** A route rule
counts the EDGE, not the paper — `you → Build` is `you → Build` whether it carries job
0417 or a fresh 0419. **The new-file dodge stops working, and it stops working for
free.**

**Three separate threads landing on the same fix is the strongest argument any of them
has had.**

---

## THE THREE IT SAYS WE ARE MISSING — ONE IS REAL, ONE IS ALREADY THERE, ONE DOES NOT APPLY

**DUPLICATE-START SUPPRESSION — mostly covered, with a named gap.** The per-desk lock
already stops two sessions for one desk, and `run_id` gives each visit an identity.
**The gap is after the lock releases:** a repeated filesystem event for a letter already
handled could start a second run. **One line on the reservation closes it** — refuse a
reservation for a letter that already has a completed one. Added to the spec; it costs
nothing because reservations already exist.

**BOUNDED PENDING WORK — does not apply, and I am not adding it.** Echo is importing
queue-depth control from systems where a queue can overflow and drop messages. **Ours
is a folder. Letters are preserved by construction and the ceilings already stop
admission.** A backlog bound would be a component guarding against a failure our
storage cannot have.

**AN ALLOWANCE SCHEDULE — that is claim 2 and it has the same answer.** Named, not
built, trigger set.

---

## THE ONE YOU ASKED ME TO PUSH BACK ON HARDEST

**"A hard cumulative ceiling is the only dependable detector of a loop that is legal at
every step."**

**It is true, and it is not a counsel of despair, and the reason is that Echo has
drawn the wrong dichotomy.**

### WHY IT IS TRUE

**Telling productive repetition from pointless repetition requires knowing what the
work is for.** No deterministic check knows that. Echo's own line is the evidence:
semantic no-progress detectors *"must distinguish legitimate investigation from
repetition"*, and they get distrusted and switched off. **We have watched exactly that
happen to controls in this repository three times this week.**

### WHY IT IS NOT DESPAIR

**The ceiling does not have to CATCH the loop. It has to stop the damage while
something that can understand takes a look.** That something is you, and the whole
design is built to put a frozen job in front of you with its entire history attached.

**A ceiling is a brake on a machine's momentum, not a substitute for a person's
judgement. Those were never the same job.**

### AND THE DICHOTOMY IS WRONG — THERE IS A THIRD CATEGORY

**Echo offers two options: dumb ceilings, or clever advisory detectors. It misses
rules about SHAPE.**

    Build -> Design -> Research -> Build      illegal under a route rule
                                              REGARDLESS of whether anyone
                                              understands the work

**That is deterministic, it is not a ceiling, and it is not advisory.** Same for the
permanent job number, and for one-writer-per-artifact.

**A structural rule does not need to know what the work is for. It only needs to know
what shape the work is allowed to take.** That is the category Echo's own best
recommendation — the state machine in its first paper — actually belongs to, and it did
not connect the two.

**So: the most useful sentence in the document, with one word wrong. Not "the only
dependable detector" — the only dependable detector OF PROGRESS. Shape is checkable;
progress is not.**

---

## WHAT CHANGES IN THE SPEC — NAMED, AS YOU ASKED

**1. A GLOBAL CONCURRENCY LIMIT, INITIALLY ONE. THIS IS A REAL MISS AND IT IS MINE.**

**My spec has a PER-DESK lock and no global one. Six desks means six sessions could run
at once**, and nothing anywhere says otherwise. Echo's first recommendation, and it is
right.

**One at a time. It also shrinks everything else** — it is what makes the ten-minute
un-stoppable window in claim 1 a single run rather than six.

**2. The switch is renamed a PAUSE**, and says what it does not do.

**3. "Twenty is a total, not a pace"** — stated, with the forty-five-minute arithmetic
in it, and the trigger for adding pacing.

**4. "Risk-limited, not allowance-safe"** — Echo's phrase, verbatim, in section 4.

**5. Duplicate-start suppression** — one clause on the reservation.

**NOT CHANGING, AND NAMED SO NOBODY THINKS IT WAS MISSED:** a turn limit. `--max-turns`
is real and it bounds the exact thing this morning's finding identified as the
multiplier. **But we have no measured turn count for a real wake — fourteen is my
estimate and nothing has verified it — and Echo's own table lists turn limits among the
first things to fire on honest work.** It goes in when the usage block gives a real
number. Same trigger as everything else today: **measure, then tune.**

*C1, 2026-09-10.*
