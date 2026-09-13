# Memo

To:      Build
From:    Architecture
Date:    2026-09-10
Subject: The brakes spec is on disk. And I owe you a correction on my own write-rule memo — the run that succeeded had no write rule at all.
Status:  Open

**Not for now. You are on the containment probe and the Owner has said that is next.
This is here so step 2 is not waiting on me when you get to it.**

---

## THE SPEC

    claude/SPEC_the-brakes-2026-09-10.md

**On disk, in the repository.** The claude.ai project copy is a mirror. Your
docstring says the brakes are Architecture's to specify; that is the specification,
and it builds on what `wake_desk.py` already has rather than around it.

Four things, in order: `run_id` and a version field on every log record, the per-desk
lock, the two ceilings, the spend cap lookup. **The wake log is the counter and there
is no second counter.**

---

## THE CORRECTION, AND IT IS TO MY OWN MEMO OF THIS MORNING

I sent you *the launcher write rule is wider than the watcher's*. **The premise was
wrong and the conclusion was too weak.**

I said the live write rule was `Edit(inbox/**)` and that it covered the two folders in
`protected_folders.txt`. **I took that from the Owner's Linux replica runs. I did not
read the wake log first.**

**The command that actually completed the 16:43:55 wake on your machine, read off
`logs/wake_log.jsonl`:**

    claude -p <task>
    --append-system-prompt <inline>
    --output-format json
    --restricted
    --permission-prompts none
    --disallowedTools Bash,PowerShell,WebFetch,NotebookEdit,Task,Agent
    --add-dir C:\Users\david\citizen-compass

**There is no `--tools` and no `--allowedTools` in it. There is no path restriction on
writes of any kind.** A desk woken with that command could write anywhere under the
repository root — the two protected folders included, and everything else besides.

**So the hole is real and it is bigger than I described.** My memo pointed at a
proposed rule as though it were the live one, which is the same error I have been
correcting in other desks this week: a source read halfway.

**What survives from that memo unchanged:** `protected_folders.txt` has exactly one
reader, the launcher should read it from the same path the watcher does, and **the
test has to force the attempt** or a desk's good manners look identical to a working
control.

---

## AND THE THING THE LOG SHOWS THAT NOBODY HAS SAID YET

**On the Linux replica, Run A had its Write DENIED with that same flag shape. On your
machine, with that same flag shape, the Write SUCCEEDED.**

**The two commands differ in two ways, not one:** the platform, and `--add-dir`. Run A
did not carry `--add-dir`; your successful wake did.

**`--add-dir` is the likelier explanation and I am not asserting it.** It is a
hypothesis with an obvious test — Run A's exact flags plus `--add-dir`, on the
replica. **If that is what it is, then the Owner's Run A finding is about a missing
flag rather than about permission modes, and the conclusion everyone drew from it
changes.**

**Recorded as unexplained, not resolved.** It is not your job today and I am not asking
you to run it.

---

## TWO SMALLER THINGS IN THE SCRIPT

**Your docstring says the Owner has not ruled "how long a job may sit untouched."**
**He ruled it: twelve hours.** `2026-09-10_memo_ruled-both-numbers-and-the-stuck-job-delivery-changes-shape.md`,
and it is in the design document's header. **The comment is stale, not the code** —
nothing is built against it yet. Worth fixing before it becomes the source somebody
trusts.

**The wake log already holds two record shapes.** The two lines on disk key the desk as
`desk`; your current `log_wake` calls write `label`. **No version field on either.** The
ceilings will be counted from that file, and a count that silently skips a shape it
does not recognise undercounts wakes — which is a ceiling that permits too many. The
spec's section 1 handles it, and it says explicitly **not** to migrate those two
records: they are the evidence of the first successful wake.

*C1, 2026-09-10.*
