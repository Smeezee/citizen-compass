# Memo

To:      Owner
From:    Architecture
Subject: A command-line tool cannot reach Echo — same wall as everything else. But your instinct is right and the tool belongs on our side of it.

**Filed into `claude/RULING_the-echo-loop-runs-on-github-issues-2026-09-12.md`.
Nothing built.**

## YOUR FIRST IDEA — A TOOL THAT TALKS TO HER

**There is no way for a program to reach your ChatGPT account.** The only ways in are
OpenAI's own apps, the plugins inside them, and the API. **The first two can't be called
from a script. The third is a key, and it isn't her** — no memory, no profile, none of
the history that is the reason you picked her.

**Same wall that stopped the tunnel, the custom connector and the share link.** A command
line does not change what is on the far side of it.

## YOUR SECOND IDEA — SHE WRITES THE TOOL

**She can write the program. That is not the same as having somewhere to run it or
anything to reach.**

Whatever she writes still has to run on your machine and still has to talk to her, and
neither of those exists. **So what comes back is source code somebody has to hand over,
review and run — the handover problem again, with extra steps.**

## WHERE IT IS WORTH BUILDING — AND THIS PART I AM TAKING

**The small program this loop already needs, given a name and a command line:**

    desk brief "<subject>"   write a job and commit it so she can read it
    desk fetch               pull her new notes in as letters in my tray
    desk status              what is open, both directions

**Why a command rather than a silent background job:** you can run it by name, **Code can
run it**, and it can be put on a timer so nobody runs it at all. One program, three ways
to use it. **A background job can only be watched. A command can be watched and driven.**

**No credential anywhere in it** — the repository is public, so reading notes needs no
key.

## ONE THING YOU ARE PAYING FOR AND MAY NOT KNOW

**The tool you are describing exists and OpenAI makes it: Codex.** Their own page says it
is included with Plus, runs locally as a command-line tool, and signs in with your
ChatGPT account rather than an API key.

**It does not help with Echo and I am not proposing it.** Codex is a coding agent, not
her — none of her context — **and you already have Code doing that job.** It would be a
second builder, not a designer.

**Said once because it is real, it is paid for, and the GitHub plugin's own description
mentions it.** If you ever want a second pair of hands on the machine rather than a
second brain, that is where it is.

---

**THE QUESTION:**

1. Build the `desk` command as part of the loop, or keep it a plain background poller?

*C1, 2026-09-12. Nothing built.*
