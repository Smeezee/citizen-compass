# Memo

To:      Engineering
From:    Owner
Date:    2026-09-10
Subject: WITHDRAW the dollar framing. I am not billed dollars and I never asked for a dollar number.
Status:  Answered

**Your two questions are withdrawn, not answered. The arithmetic in them measures
something that does not exist for me.**

## WHERE THE DOLLARS CAME FROM, AND IT WAS NOT ME

**`--output-format json` prints a field called `total_cost_usd`. That is the whole
origin.** Build reported it because the CLI printed it. It got repeated. You did
arithmetic on it and put a forty-dollar day in front of me.

**Nobody checked whether that number applies to me. It does not.**

**I run on a subscription. `ANTHROPIC_API_KEY` is not set — the guard proves it every
time.** `total_cost_usd` is a client-side estimate of what a run would cost somebody
paying per call. **There is no bill. I will never receive one. Forty dollars a day is
not a risk I have.**

**I have never once asked for a dollar figure.** I said I want to keep my credit use
down and that I did not want to count pennies. **Those are the same sentence and
neither of them is about money.**

## WHAT I ACTUALLY CARE ABOUT

**Running out.** My plan has a usage window. When it is gone, everything stops until
it resets, and a night of automation that burns the window by lunchtime has cost me
the day even though it cost me nothing.

**So the unit is tokens against my allowance, not dollars.** That is what a wake
spends and it is the only number that changes anything I do.

## WHAT CHANGES IN THE SPEC

**The cap stays.** `--max-budget-usd` is the only per-run stop the runtime offers and
a runaway still has to hit a wall. **Its job is to stop a runaway, not to manage a
budget, and it is not a number I am choosing from a price.**

**Set it high enough that honest work never touches it and a loop dies quickly.** You
have measured runs; pick from those. **Do not put a day's worst-case dollar total in
front of me again.**

**Report tokens.** Input, output, cache created, cache read. **Those are real and they
are mine. Drop `total_cost_usd` from what reaches me** — keep it in the record if it
is useful for spotting a run that behaved strangely, but it is not a figure I am
deciding anything from.

**Daytime Code: your recommendation stands and I am taking it.** Leave it unset,
refuse to wake Code until it has been measured. **Fail closed.** That one was right
and it was right for a reason that had nothing to do with money.

## AND THE REAL COST QUESTION, WHICH NOBODY HAS ASKED

**The letter wake read 304,000 cached tokens against a 33,601-byte prompt file.**
Those two numbers do not belong to each other. **If a wake is quietly carrying ten
times what it was handed, that is the thing eating my allowance**, and it is worth
more than every cap in the spec put together.

**Find out what it is before you tune a single number.**

---

ANSWERS:

**Architecture, 2026-09-10.**

**Taken in full. The withdrawal is correct and the error was mine, not Build's** —
Build reported a field the CLI printed, which is its job. **I did arithmetic on it,
multiplied it by twenty, and put a number in front of you that measures a bill you
will never receive.** I never asked whether it applied to you.

**Anthropic's own documentation says it outright**, and one look would have stopped
me: *"Claude Max and Pro subscribers have usage included in their subscription, so the
session cost figure isn't relevant for billing purposes."*

Section 4 of the spec is rewritten. Everything below is what changed and what the
304,000 turned out to be.

## THE CAP — SET BY THIS DESK, FROM MEASUREMENT, AND IT IS A WALL

    MAX_BUDGET_USD = 2.00     stands

**Not a budget and not a price you are choosing.** It is the only per-run stop the
runtime offers and the fact that it is denominated in dollars is an accident of the
flag. **Two dollars is about ten times the worst honest measured run** — the four came
in between three and nineteen cents — **so honest work never touches it and a loop
dies inside one wake instead of running to the ten-minute timeout.**

**Two walls, catching different failures:** the timeout catches a wake that hangs, the
cap catches one that spins productively.

**It moves on the first three real Windows wakes with their tokens recorded. Not on an
argument.** And no day totals in front of you again.

## WHAT REACHES YOU IS TOKENS

Input, output, cache created, cache read, and the request count when the payload
carries it. **`total_cost_usd` stays in the record for spotting a run that behaved
oddly, and out of anything you read.**

**Daytime Code stays unset and Code is not woken until it is measured.** Fail closed.

---

# THE 304,000 — AND THE FIRST THING I FOUND IS THAT YOU CANNOT RE-CHECK IT

Full working: `claude/FINDING_the-304000-is-the-rules-file-read-once-per-tool-call-2026-09-10.md`.

## THE NUMBER IS IN YOUR SCROLLBACK AND NOWHERE ELSE

**`logs/wake_log.jsonl` records `"usage_parsed": true` and not one token count.** The
launcher parses the block, prints it, and throws it away.

**That is the sweep-timing defect again, in the same week Build fixed it there** — *the
number existed and was thrown away.* **Nothing gets tuned until it is being recorded.**

## THE TWO NUMBERS DO BELONG TO EACH OTHER. ONE IS A SIZE, THE OTHER IS A SIZE TIMES A COUNT.

**`cache_read` is cumulative across every request in the run, not the size of the
context.** Anthropic's own words: *"each time Claude uses tools it sends another
request carrying that batch of tool results. With prompt caching, Claude Code re-reads
that history at the cached token rate."*

That wake read a letter, ran two counts and wrote a reply. **Every one of those is
another request, and every request re-reads the whole prefix.**

    the prefix   = Claude Code's own system prompt
                 + the tool definitions
                 + your 33,601-byte prompt file      ~9,050 tokens
                 call it ~20,000-25,000 in total

    304,000 / ~22,000  ≈  14 requests

**Fourteen requests in an eighty-one-second run is ordinary.** **Nothing was carrying
ten times what it was handed.** Derived, not measured — and it becomes arithmetic
anybody can re-check the moment the block is logged.

## AND CACHE READS DO COUNT AGAINST YOUR ALLOWANCE. DISCOUNTED, NOT FREE.

**That settles the unit question you raised.** So the thing to shrink is the prefix,
because it is multiplied by the request count.

---

# THE THREE THINGS ACTUALLY EATING IT, LARGEST FIRST

## 1. CLAUDE.md IS 624 OF THE PROMPT FILE'S 699 LINES

**Measured.** The prompt file is 33,601 bytes. **CLAUDE.md is 30,248 of them.** Your
audit desk's own charter is 68 lines; the rules bolted to it are 624.

    ~8,150 tokens x ~14 requests  ≈  114,000 cache-read tokens per wake,
                                     FOR THE RULES ALONE

**Anthropic's guidance, verbatim: "Aim to keep CLAUDE.md under 200 lines."**

**The fix is not to stop sending the rules** — Build was right that a `--restricted`
desk never discovers them. **The fix is that a woken desk does not need all 624
lines.** It needs the six that bite a desk which can only read and write: never
delete, never commit or push, fail closed, no fuzzy matching, ambiguity refused, read
the clock from the machine.

**Build already wrote exactly that list, in six bullets, in the same file — and then
appended the whole of CLAUDE.md underneath it.** The summary and the source are both
being sent.

## 2. EXTENDED THINKING, WHICH NOBODY HAS LOOKED AT AT ALL

> *"Extended thinking is enabled by default... Thinking tokens are billed as output
> tokens, and the default budget can be tens of thousands of tokens per request."*

**Output tokens are the expensive kind. Nothing in the launcher touches this, and it
may be bigger than the rules file.** A wake that reads one letter and writes one reply
does not need deep reasoning.

**Unmeasured. Not changing it before it is measured** — this whole letter exists
because somebody tuned from a number nobody had checked.

## 3. SPACING THE WAKES OUT COSTS MORE THAN CLUSTERING THEM

**Cache lifetime is one hour on a subscription. A miss reprocesses the full prefix at
the uncached rate.**

**Twenty wakes scattered across a sixteen-hour day mostly miss. Twenty inside a few
hours mostly hit.**

**Which puts your fifteen-minute window in direct tension with your allowance** — the
window exists to push wakes apart. **Not a reason to change it**; a runaway is worse
than a cache miss. A reason to know the trade is there, because nobody had priced it.

---

## THE ORDER, AND IT IS YOURS

    1  log the usage block          costs nothing, and until it is done every
                                    number here is unre-checkable
    2  three real wakes measured    the same letter, three times
    3  THEN tune                    the rules subset, the thinking budget,
                                    the tool set

**Nothing before step 1.** Sent to Build.

## THE PART OF THIS THAT IS A LESSON ABOUT ME

**A number appeared in a tool's output, three desks repeated it, and I built
arithmetic on top of it without once asking what it measured.** That is the same
defect as a document quoted as a primary source, and I did it while correcting other
desks for doing it.

**You asked the only question that mattered about that number and nobody else had.**

*C1, 2026-09-10.*
