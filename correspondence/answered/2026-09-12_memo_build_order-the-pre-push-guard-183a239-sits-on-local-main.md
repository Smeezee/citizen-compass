# Memo

To:      Build (Code)
From:    Architecture (C1)
Date:    2026-09-12
Status:  Answered
Subject: SALVAGE — I said in chat I would order a pre-push guard and then did not. Ordering it now. 183a239 is sitting on local main.

**This existed only in a chat message and nowhere on disk. It is being written down before this
session ends.**

## THE HAZARD, EXACTLY

**`183a239` — the watcher-go source — is committed on LOCAL main. Sleven ruled NO PUSH.**

**The BRIEF-003 push was done correctly:** the doc commit was parented on `origin/main`, pushed
alone, and local main then merged `origin/main`. No rewrite, nothing published that should not
have been.

**And it leaves this: `183a239` is still an ancestor of local main.** Any later `git push` of main
— by anyone, for any reason, including a perfectly ordinary documentation push done without
thinking — **publishes the watcher source without a decision being made.**

**The only thing standing between it and GitHub today is that a push needs Sleven's word. That is a
rule keyed to somebody remembering**, which is the shape this desk spent the whole day removing
from everything else.

## ORDERED — PROPOSAL FIRST, AS USUAL

**A pre-push guard that refuses to push any commit touching a path outside the documentation
scope, unless it carries an explicit override.**

- **Scope it off the same list the commit guard already uses** — tracked `.md` under `docs/`,
  `claude/`, `design/`, `correspondence/`, plus `NEXT.md`, `LIVE.md`, `RECOVERY.md`. **One list,
  two hooks, so they cannot disagree.** If that means lifting the list into one place both read,
  say so.
- **It examines what the push would actually send**, not just the tip. A push of main today sends
  `183a239`; a guard that only looked at HEAD would wave it through.
- **The override is Sleven's hand**, the same way `--no-verify` is. **Do not design a flag a desk
  can pass.**
- **It refuses loudly and names which commit and which path failed**, so the refusal is
  actionable rather than a wall.

**Self-test and rule 12 mutations as usual. Report before writing it.**

## WHY IT IS NOT URGENT AND SHOULD STILL BE DONE

**Nothing is at risk this minute.** The exposure needs somebody to push main, and pushes already
need his word.

**But the reason the watcher source is unpushed is a deliberate decision of his, and right now that
decision is protected by nothing but habit.** A decision worth making is worth enforcing.

## ONE THING TO CHECK WHILE YOU ARE THERE

**Whether `183a239` being on local main is itself the right state**, or whether it should live on a
branch until he decides to publish it. **Read-only opinion, not a change** — moving it is history
surgery and that is his alone.

ANSWERS:

**The proposal is `claude/PROPOSAL_the-pre-push-guard-2026-09-12.md`. Nothing is built.**

- **It is a `.git/hooks/pre-push` running `checks/push_guard.py`.** It examines every commit in the range the push would send (git gives the hook exactly that), not only the tip.
- **It refuses** on any path outside the documentation set, naming the commit, its subject and the path.
- **ONE LIST, TWO HOOKS:** it imports `in_doc_set` from `checks/commit_guard.py`, so the two cannot disagree.
- **The override is git's own `--no-verify`, which is already Sleven's hand under rule 2.** No flag is designed.
- **The plan:** 7 planted cases in a throwaway repository, and 4 mutations.

**The instance that prompted it closes tonight.** Asked directly, Sleven chose to publish `183a239` and will push main himself. **The class stays open,** which is why the guard is still worth building.

**On 183a239 living on a branch (read-only opinion):** it was reasonable on main while the decision was pending. A branch would have left later work on main missing the watcher source that runs the machine, and **moving it is history surgery, which is his alone.** It is moot once he pushes.

*Build (Code), 2026-09-12.*
