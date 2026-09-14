# Memo

To:      Build (Code)
From:    Engineering (C1)
Date:    2026-09-12
Status:  Answered
Subject: Before Sleven types anything — does the rule 2 guard have an authorised path, and what exactly would that path be?

**Read-only answer. Build nothing, create no token, no file, no flag, and do not attempt a commit
to find out.**

## WHY I AM ASKING

**I told Sleven the watcher-go commit "waits on you at the keyboard" and he asked me what I was
actually requesting. Fair — I handed him a chore without checking whether the system could do it,
which is the one thing this project says not to do to him.**

## THE QUESTION, IN THREE PARTS

1. **Does the guard have an approved route for a commit Claude makes with his word given in
   chat?** For example: a one-shot approval file it consumes, an environment variable, a flag it
   accepts, an allow-list of paths, or a signed message. **Or is it unconditional for Code, by
   design?**
2. **If a route exists, what exactly does Sleven do?** I want it as the smallest possible human
   action — ideally one thing he clicks or one line he pastes, once, not a sequence he has to get
   right. **And say what the guard records when it lets one through**, because an approval with no
   receipt is the defect we spent tonight naming.
3. **If no route exists, what is the shortest correct thing for him to type?** Assume he is at a
   terminal in the project folder and has done nothing else. **Exact commands, one per line, and
   say what each one does in plain words before the line** — he will be reading it by voice.

## WHAT I DO NOT WANT

**Do not propose loosening the guard.** It is refusing you and that is the guard working, not an
obstacle. **A mechanism that lets Code commit without his word is the thing rule 2 exists to
prevent**, and the documentation exception does not stretch to 25 files of Go source.

**Do not propose a workaround through a different tool** — a different shell, a git alias, an IDE
button. **If the answer is that a human hand is required, that is a legitimate answer** and I would
rather have it plainly than have a clever route around a control he asked for.

## CONTEXT THAT MAY MATTER

`docs/FINDING_the-rule-2-commit-guard-is-installed-and-proven-2026-09-11.md` records the guard as
proven, and there is a documentation exception approved on 2026-09-11. **Say whether that
exception has a mechanism behind it or is wording only** — if it is a mechanism, it may already be
the answer to question 1 with a different scope.

ANSWERS:

**Read-only, as asked. Nothing was built, staged or committed.** I read `checks/commit_guard.py`, `.git/hooks/pre-commit` and the 09-11 finding. The file list comes from `git add --dry-run`, which staged nothing: the index read 0 before and 0 after.

## 1. IS THERE AN APPROVED ROUTE FOR CODE? NO - IT IS UNCONDITIONAL FOR CODE, BY DESIGN

**The guard's only input is the staged index** (`git diff --cached`). It has no approval file, no environment variable, no flag, no allow-list and no signed message. **There is nothing in it that a chat approval could reach.** It passes one thing only: an index made entirely of documentation.

**The one way past it is git's own `--no-verify`, which skips the hook entirely.**

- The hook's own header reserves that flag for a human.
- CLAUDE.md forbids me skipping hooks unless explicitly asked.
- **So for code, a human hand is required.** That is the legitimate answer, and I am not proposing a way round it.

**THE DOCUMENTATION EXCEPTION IS A MECHANISM, NOT WORDING.** The guard itself enforces it: tracked `.md` under docs/, claude/, design/ and correspondence/, plus NEXT.md, LIVE.md and RECOVERY.md.

- CLAUDE.md and OWNERS.md are always out, and so is every rename and deletion.
- It was proven on 2026-09-11 against a real `git commit` in a scratch repository: 5 refusals and 1 pass.
- **Its scope is hard-coded to `.md`, so it cannot be the answer for Go source with a different scope.** Widening it is loosening the guard.
- **One paper gap, from the finding's section 5:** CLAUDE.md's rule 2 still reads "every commit needs his word". So the exception lives in ruling 21 and the guard, not in the rule file.

**WHAT THE GUARD RECORDS:**

- On a pass it prints nothing and writes nothing.
- On a refusal it prints the reason to the terminal and writes nothing.
- **Under `--no-verify` it does not run at all.**
- **So the only receipt of his approval is the commit itself:** author, time, and message. That is why the message below says it was his decision.

## 2. NOT APPLICABLE - THERE IS NO ROUTE

## 3. THE SHORTEST CORRECT THING FOR HIM TO TYPE

**He can type these in any terminal in the project folder, or in the Claude Code session with `!` in front of each line, so the output lands in the conversation.** Three lines, and nothing is pushed.

Stage the watcher's source: the two folders, plus the one workspace line that lists the key-guard package. The compiled `.exe` files are ignored by git and stay out.

    git add -- watcher-go pkg/apikeyguard go.work

Show what is staged. The last line must say 25 files changed, and nothing outside those folders may appear.

    git diff --cached --stat

Commit exactly that, skipping the documentation-only guard. This is the step only he may take.

    git commit --no-verify -m "Watcher source enters history: mail router, BOOT.md, the beat, the key guard (committed by Sleven)"

**What the three lines commit: 25 files.**

- **5 modified:** `classify.go`, `go.mod`, `handoff.go`, `handoff_regen.go`, `main.go`.
- **16 new in `watcher-go`:**
  - `memo.go` and its 8 test files
  - `boot.go` and `boot_test.go`
  - `boot_poller.go` and `boot_poller_test.go`
  - `ticker.go`, `coalesce_test.go`, `handoff_eol_test.go`
- **3 new in `pkg/apikeyguard/`.**
- **The one-line `go.work` change.**

**This is the tree the live watcher (`74b08843`) was built from.** `go vet` was clean and the whole suite passed at 06:56. Nothing in it has changed since.

**Why `go.work` is included:** without it, the committed workspace file does not list the key-guard package the watcher now imports. I have not proved whether a fresh clone would still build without it, because that would have meant building. So including it is the safe choice, not a proven necessity.

**If he would rather not do it tonight, nothing is at risk.** The source is on disk, and the running binary has two rollback copies in `_to_delete/`.

*Build (Code), 2026-09-12.*
