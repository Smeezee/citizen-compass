# FINDING — the 304,000 is the rules file, read once per tool call. And the number is not in any file.

    date     2026-09-10
    from     C1, architecture
    asked    Sleven: *"The letter wake read 304,000 cached tokens against a
             33,601-byte prompt file. Those two numbers do not belong to each
             other... Find out what it is before you tune a single number."*
    method   measured off the repository, plus Anthropic's own published
             documentation. Every figure below says whether it is measured,
             derived, or estimated. Nothing is asserted from memory.

---

## 0. THE FIRST ANSWER IS THAT NOBODY CAN RE-CHECK 304,000, INCLUDING HIM

**`logs/wake_log.jsonl` records `"usage_parsed": true` and does not record a single
token count.** Read from the file today, the whole of what the letter wake stored
about what it spent:

    {"event":"wake_end","desk":"audit","at_utc":"2026-09-10T16:45:18...",
     "seconds":81.06,"exit":0,"usage_parsed":true}

**The launcher parses the usage block, prints it to the console, and throws it
away.** The 304,000 exists in his scrollback and nowhere else.

**This is the sweep-timing defect again**, in the same week Build fixed it there:
*"The number existed and was thrown away."* **First fix, before any tuning: the usage
block goes in the wake log.**

---

## 1. WHAT THE PROMPT FILE ACTUALLY IS — MEASURED

    logs/wake_prompt_audit.md      33,601 bytes    699 lines   ~9,050 tokens est
      of which CLAUDE.md           30,248 bytes    624 lines   ~8,150 tokens est
      the C5 boot prompt            3,111 bytes     68 lines     ~840 tokens est

**CLAUDE.md is ninety per cent of the prompt file.** The desk's own charter is 68
lines; the project rules bolted to it are 624.

**And it is inline on purpose.** Build's note in the file: *"It is reproduced below in
full, because this session runs with --restricted and does NOT discover it on its
own."* That reasoning is correct and this finding does not overturn it.

---

## 2. WHY 304,000 AND 9,050 DO BELONG TO EACH OTHER — THE MECHANISM

**They are not the same kind of number. One is a size; the other is a size times a
count.**

Anthropic's own documentation, on why usage climbs:

> "Claude Code sends your full conversation with every request, and each time Claude
> uses tools it sends another request carrying that batch of tool results. With prompt
> caching, Claude Code re-reads that history at the cached token rate"

**So `cache_read_input_tokens` is CUMULATIVE ACROSS REQUESTS, not the size of the
context.** The letter wake read a letter, ran two counts and wrote a reply — every one
of those tool calls is another request, and every request re-reads the whole prefix.

**The arithmetic, and it is DERIVED rather than measured:**

    the cached prefix  =  Claude Code's own system prompt
                       +  the tool definitions for Read, Glob, Grep, Write
                       +  the 33,601-byte prompt file        ~9,050 tokens
                       call it ~20,000-25,000 tokens in total

    304,000 / ~22,000  ≈  14 requests

**Fourteen requests in an 81-second run that read a file, ran two globs and wrote a
reply is entirely ordinary.** The number is not evidence of anything carrying ten
times what it was handed. **It is evidence that the prefix is read fourteen times.**

**NOT PROVEN, and it cannot be until section 0 is fixed.** The prefix size and the
request count are both unrecorded. Once the usage block is logged, this is arithmetic
anybody can re-check: `cache_read ÷ prefix ≈ requests`.

---

## 3. AND CACHE READS DO COUNT AGAINST HIS ALLOWANCE. THIS IS THE UNIT QUESTION SETTLED.

**They are discounted. They are not free.** Same source, same sentence: the history is
re-read *"at the cached token rate"*, and the paragraph exists to explain why a
one-line question can draw usage for a whole conversation.

**So the thing to reduce is the prefix, because it is multiplied by the request
count.** Every token in that 33,601-byte file is paid for roughly fourteen times per
wake.

---

## 4. THE THREE LEVERS, LARGEST FIRST, WITH HONEST CONFIDENCE

### LEVER 1 — CLAUDE.md IS 624 LINES AND IS RE-READ ON EVERY REQUEST

**Derived, from measured inputs:**

    ~8,150 tokens  x  ~14 requests   ≈  114,000 cache-read tokens per wake
                                        FOR THE RULES ALONE
    x 20 wakes a day                 ≈  2.3 million tokens a day

**Anthropic's own guidance, verbatim:** *"Aim to keep CLAUDE.md under 200 lines by
including only essentials."* **Ours is 624.**

**The fix is NOT to stop sending the rules.** Build was right that a `--restricted`
desk does not discover them. **The fix is that a woken desk does not need all 624
lines** — it needs the ones that bite a desk that can only read and write: never
delete, never commit or push, fail closed, no fuzzy matching, ambiguity refused, read
the clock from the machine. **Build already wrote exactly that list in the boot
prompt's own "THE RULES YOU INHERIT" section, in six bullets.**

**So the whole of CLAUDE.md is being sent as well as a correct summary of the part
that applies.** That is the finding.

### LEVER 2 — EXTENDED THINKING, WHICH NOBODY HAS LOOKED AT AT ALL

> "Extended thinking is enabled by default... Thinking tokens are billed as output
> tokens, and the default budget can be tens of thousands of tokens per request
> depending on the model."

**Output tokens are the expensive kind and nothing in the launcher touches this.**

**UNMEASURED, and it may be larger than lever 1.** A wake that reads one letter and
writes one reply does not need deep reasoning. The levers are `--effort` and
`MAX_THINKING_TOKENS`.

**Do not change it before measuring it** — this document exists because somebody tuned
from a number nobody had checked.

### LEVER 3 — SPACING THE WAKES OUT COSTS MORE THAN CLUSTERING THEM

> "your first message after a break longer than the cache lifetime misses the cache
> and reprocesses your full context. The lifetime is an hour on a subscription"

**A cache MISS reprocesses the prefix at the full rate rather than the cached one.**

**Twenty wakes scattered across a sixteen-hour day mostly miss. Twenty wakes inside a
few hours mostly hit.**

**AND THAT IS IN TENSION WITH THE FIFTEEN-MINUTE WINDOW**, which exists to push wakes
apart. **The brake and the allowance want opposite things**, and nobody has priced
which matters more.

**Strongly supported by the documented mechanism; not measured here.** It is not a
reason to change the window — the window is a runaway stop and a runaway is worse than
a cache miss. It is a reason to know the trade exists.

---

## 5. WHAT I AM NOT SAYING

**I am not saying the wake carried ten times what it was handed.** The 304,000 is
consistent with an ordinary fourteen-request run against an ordinary prefix, and the
alarming reading of it comes from comparing a cumulative figure with a single size.

**I am not saying there is nothing to fix.** Sending 624 lines of rules fourteen times
per wake is worth fixing whether or not it explains that number.

**And I am not saying any of this is measured.** One count is missing from the log,
one lever has never been looked at, and the third is a documented mechanism rather
than an observation of our own runs.

---

## 6. THE ORDER OF WORK

    1  LOG THE USAGE BLOCK            input, output, cache created, cache read,
                                      and the request count if the payload
                                      carries one. Costs nothing. Until this is
                                      done, every number here is unre-checkable
                                      and so is his.
    2  READ THREE REAL WAKES          the same letter, three times, with the
                                      block recorded
    3  THEN, and only then, tune      the rules subset, the thinking budget,
                                      the tool set

**Nothing is tuned before step 1.** His instruction, and it is the right one.

---

## SOURCES

- Anthropic, *Manage costs effectively* — https://code.claude.com/docs/en/costs
- Anthropic, *Models, usage, and limits in Claude Code* — https://support.claude.com/en/articles/14552983-models-usage-and-limits-in-claude-code

Measured from `logs/wake_log.jsonl`, `logs/wake_prompt_audit.md`, `CLAUDE.md` and
`claude/PROMPT_boot-a-new-c5.md` on 2026-09-10.

*C1, 2026-09-10.*
