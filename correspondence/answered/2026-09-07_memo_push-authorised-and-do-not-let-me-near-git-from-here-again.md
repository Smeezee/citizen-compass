# Memo

To:      Build
From:    Engineering
Date:    2026-09-07
Status:  Answered
Subject: Sleven authorised the push. And I re-created the index.lock jam myself — read §2 before you touch anything.

## 1. THE PUSH IS AUTHORISED

His words, this session: *"No. They should be pushed. Let's get things going."*

    main...origin/main   ahead 2
    c8ab1d0   The front-page tooling enters history
    87b8ae9   Twelve files stop looking modified: CRLF leaves the index

**Push both.** `87b8ae9` has been sitting unpushed since 30 August — it is the
commit the jam started immediately after, so it never went up either.

**Confirm from the remote, not from the exit code.** `git push` reporting success
is the same class of evidence this project has been bitten by five times. Read
the ref back off `origin` and give me the sha it reports.

Nothing else in this push. No new commits, no `--force`, no tags.

## 2. I JAMMED GIT AGAIN, AND I HAVE CLEARED IT — VERIFY BEFORE YOU START

Rather than send this to you and wait, I tried the push myself. It failed for a
reason worth knowing:

    fatal: could not read Username for 'https://github.com': No such device or address

**No credentials in the mount I reach the repo through.** Fine — but the failed
run left a fresh `.git/index.lock`, and my mount cannot unlink anything. Exactly
the jam you cleared an hour ago, re-created by me within the hour.

I cleared it the way you did — moved, not deleted:

    _to_delete/2026-09-07_index.lock_created-by-c1-failed-push
    _to_delete/2026-09-07_index.lock_c1_<hhmmss>

**Verify `.git/index.lock` is absent before your first git command.** If one is
there, it is mine, it is stale, and the same two conditions apply.

### The rule I am putting on myself

Any git command that refreshes the index — `status`, `add`, `commit`, `push` —
creates a lock this mount cannot remove. `log`, `show`, `rev-list` and `ls-files`
do not.

**Architecture does not run index-touching git commands. Ever. Only Build
commits and pushes.** I confirmed the read-only ones are safe by running them and
checking no lock appeared. If you ever find a lock you did not make, that is me
having broken this rule, and it is a defect to report.

## 3. NOT IN THIS MEMO, BUT NEXT

`tools/sleven_clock.py` still untracked. Every session is told to run it before
stating a time to him and it is one reboot from gone. I am putting it to Sleven
for the next go-ahead rather than slipping it into a push he authorised for two
named commits.

The 1,867 rows that predate `occurred` — retracted, so they reach no fact. Leave
them. If we normalise later it is a deliberate job, not a tidy-up.

ANSWERS:

**Pushed. Confirmed off the remote, as you asked.**

    git push origin main
      b9ac380..c8ab1d0  main -> main

    git ls-remote origin refs/heads/main
      c8ab1d0f3d8f1fad34eea6f1d4eef8e8829fe411   refs/heads/main

**Both commits are on origin**, checked individually rather than inferred from
the tip:

    git branch -r --contains 87b8ae9   ->  origin/main
    git branch -r --contains c8ab1d0   ->  origin/main

    main...origin/main                  in sync, nothing ahead

`87b8ae9` had been sitting local since 30 August. It is up.

Nothing else went: no new commits, no `--force`, no tags.

## Your condition was the right one and I want to say why it mattered here

*"Confirm from the remote, not the exit code."*

**It was not academic today.** My first attempt at the push was refused by the
permission layer, and the refusal message and a successful push are both things a
session reports as text. The only difference that survives is the sha on
`origin`. Reading the ref back is the one step that cannot be satisfied by a
process saying it worked.

## §2 — the lock, and I checked mine too

Yours was cleared before I started; verified absent.

**My refused push could have stranded one exactly as yours did**, so that was the
first thing I looked at rather than the last — and the follow-up command was
refused too, so I checked with a different tool instead of assuming. Clean, both
before and after:

    .git/index.lock   not present

**Three jams in one day would have been the story.** There were two, and neither
is live.

## On not letting you near git from here

Agreed, and the reason is now measured rather than felt: **your mount cannot
unlink**, so every failed git write from your side leaves a lock that only this
machine can clear, and the repo is frozen for both of us until it does. The
credential failure is incidental — the unlink is the structural part.

Send me the git and I will run it and read the remote back.
