# Memo

To:      Build
From:    Owner
Date:    2026-09-10
Subject: When you stop, say it in a field as well as in words — the words are not reaching me
Status:  Open

**Starting now, every time you stop without finishing, the report opens with these
three lines before any prose:**

    state        BLOCKED
    blocked_on   the exact thing that would clear it — a path, a job number, a
                 desk, a decision
    clears_by    the desk that can clear it, or OWNER when nobody else can

**Same three lines when you finish** — `state: IDLE` or `state: WORKING`, the other
two empty.

## WHY

**Your explanations are good and they are not reaching me.** My words, and they are
a defect report rather than a complaint:

*"Sometimes Code stops because something important needs to be fixed or resolved
first. His explanations can be difficult for me to read and understand, so I might
think he's simply sitting idle and tell him to continue. Then the issue he was
waiting on could get pushed aside without being fixed."*

**Last night is the example.** You stopped at 00:33 because the design document was
not on disk, and you said so in the first line of the heading. **It was still being
guessed at nine and a half hours later.** Nothing about how you wrote it was wrong.
**A paragraph cannot be read by a machine, and a machine is what has to route this
once the doorbell is live.**

**Keep writing the prose exactly as you do.** It is what makes the record worth
having. **The field is not a summary of it — it is the thing that decides where the
letter goes**, and I do not want that decision resting on anybody reading correctly,
including me.

## AND THE ONE THAT MATTERS MOST TO ME

**When I tell you to proceed and your blocker is still standing, stop again on the
same blocker and say so.** Do not take a "go" from me as the blocker being cleared.
**I will sometimes say it without understanding what you were waiting on. That is
the failure I am trying to design out, and you refusing is what catches it.**

You already did exactly this last night when three memos carried three different
numbers. **Same instinct, applied to blockers.**

## SCOPE

**This is a change to how you report, not to what you build.** Architecture is
specifying how the field is carried in the stamp and how the watcher routes on it.
**Do not build routing against this letter — start writing the three lines.**
