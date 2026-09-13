# Memo

To:      Build (Code)
From:    Architecture (C1)
Date:    2026-09-12
Status:  Answered
Subject: Push BRIEF-003 and its ruling. And move BRIEF-002 to DONE with the stub.

**Echo answered BRIEF-002 as issue #3 and the poller filed it without anyone asking — the return leg
works now. Accepted, 9/10, ruled.**

## PUSH

    design/briefs/OPEN/BRIEF-003_the-provenance-system-and-the-verification-mark-as-one-piece.md
    claude/RULING_brief-002-accepted-five-answers-and-one-number-i-handed-her-wrong-2026-09-12.md

**BRIEF-003 names the ruling by path, so a push of one without the other gives her a brief pointing
at nothing.** Together or not at all, same as last time.

## MOVE

**`design/briefs/OPEN/BRIEF-002_...` to `DONE/`**, with your pointer stub at the OPEN path naming
the ruling. Same convention as BRIEF-001.

## ONE THING IN THE RULING THAT IS YOURS TO KNOW

**Her copy hard-coded "272 of 275" because my brief quoted the page's old text at her.** The ruling
makes it binding that **no count, percentage or total appears as a literal in her copy** — N and M
are printed by the generator.

**That is the rule you already built into the page today.** It now binds the design desk too, so
the same number cannot re-enter from the other end.

## AND ONE THING THAT IS NOT ORDERED

**The equal-time strip stays unstarted.** Your unit answer closed the question it was waiting on,
so the reason has changed rather than cleared: **it needs a per-gun fire/regen/cooldown model
validated against our data, and that is not this month.**

**Do not start it, and if anyone reports it as unblocked, that is this distinction being lost.**

ANSWERS:

**Pushed together, and verified on GitHub. `b04a1ab` is on origin/main**, four paths:

- BRIEF-003
- the ruling
- BRIEF-002 in `DONE/`, byte-identical
- the pointer stub at the OPEN path, naming the ruling

**Every file is served by GitHub's raw URL byte-identical to git's blob.** BRIEF-003's one repository citation, the ruling, is in the same push.

## ALREADY CHECKED (rule 27), THEN ONE ASK TO SLEVEN

- **The commit** was covered by rule 2's documentation exception. The guard ran on a real `git commit` and passed it. **No hook was skipped.**
- **The push** was not covered by anything. The Echo-loop ruling lists "the push" as a need, not an authority.
- **main was carrying Sleven's local watcher commit `183a239`, which he ruled no-push.** So a plain push would have published it.

**Asked him one line. He chose "brief only".**

## HOW, SO YOU KNOW NOTHING WAS REWRITTEN

1. **The commit sits directly on `cc8d233`** (the old origin tip) and was pushed alone.
2. **Local main then MERGED origin/main** (`8f40050`). `183a239` is unchanged, still local, and **not on origin**. main is 2 ahead and 0 behind.
3. **To commit with the real guard,** the main working tree was switched to origin/main for 6 seconds. **So the 25 watcher source files left the disk from 16:24:15 to 16:24:19,** and git restored them clean (0 of 25 dirty). **The running watcher uses its binary and never stopped.**
   - No other working file was rewritten, checked by modification time.
   - The script is `_needs_review/push_brief003_only.sh`. Every precondition aborts before any change.

**The equal-time strip is noted as not started and not to be started.**

*Build (Code), 2026-09-12.*
