# Memo

To:      Build
From:    Owner
Date:    2026-09-10
Subject: Report tokens, not dollars. I am not billed dollars and the figure has been misleading everyone including me.
Status:  Open

**Stop putting `total_cost_usd` in anything that reaches me.**

**I run on a subscription. `ANTHROPIC_API_KEY` is not set — your own guard proves it
before every run.** That field is a client-side estimate of what the run would cost
somebody paying per call. **There is no invoice behind it. It is not my money.**

**You did nothing wrong reporting it** — the CLI prints it and you labelled it a
client-side estimate every single time, which is more care than it deserved. **The
error is that nobody asked whether it meant anything for me, and then it grew into a
forty-dollar-a-day arithmetic in front of me about a bill that does not exist.**

## WHAT TO REPORT INSTEAD

    input tokens
    output tokens
    cache creation tokens
    cache read tokens

**Those are real and they come out of my allowance.** When the allowance is gone
everything stops until it resets — **that is the actual cost of a wake and it is the
only one I act on.**

Keep the dollar estimate in `logs/wake_log.jsonl` if it helps spot a run that behaved
oddly. **Do not put it in a report.**

## THE CAP IS NOT WITHDRAWN

`--max-budget-usd` stays. **It is the only per-run stop the runtime gives us and a
runaway still has to hit a wall.** It is a runaway stop, not a budget, and its number
comes from your measurements — **set it clear of honest work and stop there.** Nobody
is picking it off a price.

## THE ONE THAT IS WORTH REAL WORK

**Your letter run read 304,000 cached tokens. The prompt file you built is 33,601
bytes.** Those two numbers do not belong to each other.

**If every wake is carrying ten times what it was handed, that is what is eating my
allowance**, and no cap anywhere in the brakes spec touches it.

**That is now ahead of the guard check.** Find out what the 304,000 is. **Measure it,
do not fix it** — and if it turns out to be something we are paying for on every wake
forever, I want to know before the doorbell starts ringing on its own.
