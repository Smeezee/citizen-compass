# Memo

To:      Build
From:    Owner
Subject: Unfreeze one thing: the usage block goes in the wake log. Nothing else thaws.
Status:  Answered
**Authorised: step 1 of `claude/FINDING_the-304000-is-the-rules-file-read-once-per-tool-call-2026-09-10.md`.**
The launcher parses the usage block, prints it and throws it away. Fix that. Input, output,
cache created, cache read, and the request count if the payload carries one, written into
`logs/wake_log.jsonl` beside what is already there.

## THE BOUNDARY, AND IT IS NARROW

**This unfreezes the logging code. It does not unfreeze the wake system.** No scheduled
wakes, no watcher restart, no automation resumed. The change is written and proven the way
any other change is.

**Step 2 of that finding — three real wakes with the block recorded — is a separate
authorisation and I have not given it.** Running three wakes is running the automation. Bring
me a request naming the three runs, the spend cap in force, and that I will be at the desk
while they run. **Do not fold it into this one.**

## WHY IT IS WORTH DOING NOW

Sleven is deciding how to spend his Claude allowance across the desks, and every number in
that decision is currently unre-checkable — including the 304,000 that started it. **Until
the block is logged, any desk we move or delete to save tokens is a guess.**

**Nothing else in the freeze changes.**


---

ANSWERS:

**Build, 2026-09-11. Step 1 is already done - it landed with the containment probe on 2026-09-10, before this order reached me.** Checked, not assumed:

    scripts/wake_desk.py:787-833   writes event wake_usage with input_tokens,
                                   output_tokens, cache_creation_input_tokens,
                                   cache_read_input_tokens, num_turns,
                                   total_cost_usd, session_id - and
                                   usage_parsed:false when the block does not
                                   parse, so a missing count is never a zero
    logs/wake_log.jsonl            a real record, run 20260911T031909Z at
                                   2026-09-11T03:19:39Z: input 66, output
                                   1,663, cache created 44,149, cache read
                                   85,602, num_turns 5

**num_turns is the request count you asked for.** The launcher's own comment says cache_read is a SUM across calls and num_turns is what divides it. Architecture recorded this item closed at 02:41 on 2026-09-11.

**Nothing was changed for this reply. Step 2 - three real wakes - was not started**; it is separately authorised, as you wrote.
