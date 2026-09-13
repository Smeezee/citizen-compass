    state        IDLE
    blocked_on
    clears_by

Filed at the time in this file's archive name. **Measured without spending
anything.**

# THE 304,000 IS SIX CALLS READING ONE CONTEXT. Nothing is carrying ten times what
# it was handed.

## THE ANSWER

**`cache_read_input_tokens` in the result JSON is a SUM ACROSS THE API CALLS IN
THE RUN, not the size of the cached context.**

    the letter          6 API calls    per-call read 46,864 -> 55,763    sum 304,083
    containment probe   2 API calls    0 then 48,995                     sum  48,995
    wake 1 (11:43)      6 API calls    0 then ... 30,803                 sum 103,756

**304,083 / 6 = 50,680.** The context is roughly fifty thousand tokens and it is
re-read once per call. **The 33,601-byte prompt file is inside that fifty
thousand, not one tenth of it.**

## HOW IT WAS MEASURED, AND IT COST NOTHING

The CLI writes a session transcript per run under the user profile - the runbook
noted this and said to keep it because the transcript is evidence. **It is, and
this is the first time it has been.** Three transcripts, one per headless run,
each holding the per-call usage block. Counted, deduplicated by message id, no
re-run.

    ~/.claude/projects/C--Users-david-citizen-compass/
        318ffa5b-...  wake 1
        7bf5e875-...  containment probe
        a52a32ce-...  the letter

## THE THING WORTH KNOWING THAT NOBODY ASKED FOR

**The cache survived between the two runs.** The letter's FIRST call read 46,864
rather than creating it - it reused what the probe had built twenty seconds
earlier. The probe paid 50,026 of creation; the letter paid only 9,935 of
increments.

**So back-to-back wakes are already much cheaper than the first**, and **any edit
to the prompt file throws that away.** That is worth knowing before anything
touches `CLAUDE.md` or the charter - not as a reason to leave a rule out, as a
reason to expect the next wake after an edit to cost like a first one.

## THE PART I CANNOT ACCOUNT FOR, STATED AS A GAP

    wake 1     charter only, 3,110 bytes, FULL tool set        context ~30,803
    probe      charter + CLAUDE.md, 33,601 bytes, 4 tools      context ~48,995
                                                              delta   +18,192

**`CLAUDE.md` is 30,248 bytes.** At the four-bytes-per-token that English usually
runs at, that is about 7,500 tokens. **The measured delta is 18,192, and the tool
set was cut at the same time, which should have pushed the other way.**

**I cannot explain the difference from anything on disk and I am not going to
guess at it.** I have no tokenizer here to count the file exactly, so the honest
statement is: the prefix grew by 18,192 tokens when 30,248 bytes were added, and
the ratio is not one I can derive. **It may be ordinary and it may not.** If you
want it resolved, one measured run with a deliberately shortened prompt file
would separate it - that spends, and I have not run it.

## WHERE THE ALLOWANCE ACTUALLY GOES

    per wake  =  context (~50,000)  x  number of calls

**Six calls to write one memo.** The call count is as big a lever as the prefix,
and nothing in the brakes spec touches either. Reported, not acted on.

## TWO CHANGES MADE, BOTH SMALL AND BOTH IMPLIED BY YOUR LETTERS

**Dollars are out of the report.** `print_usage` now prints the four token
figures and `num_turns`, and says in the output that cache_read is a sum across
calls so the next reader does not have to re-derive this. **`total_cost_usd` still
goes to `logs/wake_log.jsonl`** where it can flag an odd run, and appears in no
report.

**The result JSON is now kept.** `logs/wake_payload_<label>_<timestamp>.json`,
every run. **The run that raised this question had nothing on disk to answer it
with**, and it was answerable only because the CLI happened to persist a
transcript elsewhere. That was luck, and it cost nothing to remove.

Dry run re-checked clean after both changes. Nothing was launched.

## NEXT

**The guard check** - extending `checks/_verify_api_key_guard.py` so the
PowerShell guard and the launcher's own refusal are asserted to agree. That was
next before this jumped the queue, and it is next again.

**Then the brakes**, which I have not started: the switch first, then the lock,
the two ceilings, the wake log records with `run_id` and a version field, and the
spend cap as a lookup with nothing in it that refuses to wake. **`claude/SPEC_the-brakes-2026-09-10.md`
is on disk and I have read the two memos about it but not the spec itself yet** -
I will read it at the point of building, since it has already changed once today.

**Nothing wakes again until the brakes exist and have been tripped on purpose.**

Nothing committed.
