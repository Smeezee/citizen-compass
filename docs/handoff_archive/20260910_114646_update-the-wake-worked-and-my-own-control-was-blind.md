# Update — the wake WORKED. Seven of eight conditions pass. The eighth was blind and I am not calling it green.

Filed at the time in this file's archive name. **Run at your word, 2026-09-10.**

## IT WORKED

    started            2026-09-10 16:43:55 UTC
    ended              2026-09-10 16:45:18 UTC
    wall clock         81.1 seconds
    exit               0, on its own

C5 woke with nobody present, read the letter in its tray, answered it, wrote one
reply into `inbox/`, and stopped. The watcher filed it to
`correspondence/open/owner/2026-09-10_20260910_memo_audit-to-owner_the-test-letter-answer-91-py-79-mjs.md`.

**The answer is 91 `.py` and 79 `.mjs`, and I re-counted it independently before
telling you it was right:**

    ls -1 checks/*.py    91      the desk said 91
    ls -1 checks/*.mjs   79      the desk said 79

**Exact, both.** It also said which subdirectories it did not open, corrected its
own miscount mid-memo rather than tidying it, and warned that `checks/` is written
to daily so a re-count tomorrow may differ. That is the right shape of answer.

**One detail in its reasoning is wrong and the numbers are still right.** It said
`__pycache__` "would have inflated the `.py` figure with compiled copies". It would
not - those files end `.pyc`, which does not end in `.py`. Recursive and
non-recursive `.py` counts are both 91, which proves it. Small, but this is a
project where a right answer with a wrong reason is worth naming.

## THE COST — TOKENS ARE REAL, THE DOLLAR IS AN ESTIMATE

    input                   162
    output                6,393      of which 3,816 thinking
    cache creation       32,409
    cache read          103,756

    total_cost_usd       0.5377      CLIENT-SIDE ESTIMATE, not the invoice

Per model: `claude-opus-5[1m]` did the work, $0.536603; `claude-haiku-4-5` was
used for 993 in / 14 out, $0.001063. **Both are `"costBasis": "list"` and
`"provider": "firstParty"`.**

## WHICH ALLOWANCE IT DREW FROM — I CANNOT ANSWER THIS AND WILL NOT GUESS

**This is the claim the whole design rests on and the run did NOT settle it.**

What the run actually shows is `"provider": "firstParty"` and `"costBasis": "list"`
- that it went to Anthropic directly, priced at list. **Neither field says
subscription or pay-as-you-go.** No field in the JSON does.

`ANTHROPIC_API_KEY` was unset in the environment this launched from, which is the
condition under which a normal `claude` run uses the subscription login - and that
is an inference from the guard's own reading of the environment, **not an
observation of an account being debited.** The only thing that would settle it is
your usage page.

**Reported as unresolved rather than assumed.** Rule 11.

## CONDITION 8 WAS BLIND, AND THAT IS THE FINDING

You called it the real control. **It reported "nothing changed" and it could not
have reported anything else** — because `git status` cannot see a gitignored path,
and `inbox/`, the one directory the desk was told to write to, is gitignored.

    .gitignore:28   inbox/
    .gitignore:15   logs/
    .gitignore:26   .claude/
    .gitignore:30   _needs_review/
    .gitignore:46   _to_delete/

    git status --porcelain inbox/     returns nothing, ever

**The run wrote two files I know about and git saw neither:** the reply in `inbox/`
and `logs/wake_log.jsonl`. A woken desk could have written into `.claude/`, moved
something into `_to_delete/`, or dropped anything at all into those five
directories, and my control would have printed "nothing. The before and after
states are identical."

**That is a check that cannot fail — hard rule 12, in the control I built to
enforce your condition 8.** It manufactured exactly the confidence the rule warns
about, and it did it on the first run.

**So condition 8 is NOT PERFORMED, not passed.** Seven of eight.

**Nothing suggests the desk misbehaved** - its own memo says it read the letter,
listed one directory and wrote the reply, and the tracked tree is genuinely
unchanged. **But "no evidence of a write" and "evidence of no write" are different
statements and only one of them was measured.**

## WHAT I AM DOING ABOUT IT, AND WHAT I AM NOT

**Fixing the control.** It will take a manifest - path, size, mtime - of the
gitignored directories a desk could plausibly reach, either side of the run, and
diff it alongside `git status`. **And it will declare its own coverage**, naming
which trees it walked and which it excluded for size, because a control that walks
a set must say the set is complete - Architecture's order, and this is the case
that proves it.

**Not re-running the wake to re-test condition 8 without your word.** The fix can
be proven with known-bad input on its own - plant a file in `inbox/`, confirm the
control names it - and that costs nothing. **Only that dry proof is happening
unless you say otherwise.**

## THE OTHER SEVEN, FOR THE RECORD

    1  starts with nobody present     PASS   --permission-prompts none
    2  reads the letter in its tray   PASS   it answered the question in it
    3  writes a reply into inbox/     PASS   the file exists
    4  the watcher files it to owner  PASS   correspondence/open/owner/
    5  exits on its own               PASS   exit 0, 81.1s, no intervention
    6  real token counts              PASS   the usage block above
    7  both numbers correct           PASS   re-counted independently, exact
    8  nothing else changed           NOT PERFORMED - see above

Nothing committed.
