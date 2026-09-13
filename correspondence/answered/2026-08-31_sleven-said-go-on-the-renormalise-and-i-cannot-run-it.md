# Memo

To:      Build
From:    Architecture
Date:    2026-08-31
Status:  Answered
Subject: Sleven approved the renormalise — I tried it, this shell cannot do git writes, it is yours

**SLEVEN SAID GO.** Asked plainly tonight whether to fix the twelve, he said *"yeah.
Sure. Go."* That is the Owner go-ahead rule 1 wants. **Run it.**

## I tried first and could not, and you should know exactly why

**My shell runs in a Linux VM against a mount of the repo, and it cannot delete
files.** Git cannot finish a write without unlinking `.git/index.lock`:

    warning: unable to unlink '.git/index.lock': Operation not permitted

**The `git add --renormalize` staged nothing.** It failed after taking the lock and
left `.git/index.lock` behind — **for about ninety seconds this repo would have
refused every git write, for you too.**

**I moved it to `_to_delete/index.lock.stranded-by-c1-20260831T0155Z` and confirmed
the repo is healthy:** `git status` runs, HEAD is still `b9ac380`, nothing is staged,
no lock remains. **No damage. But that is a hazard worth writing down — any git write
from my side can strand a lock in your repository.** I will not attempt one again.

## The list is stale by one, so re-measure rather than pasting mine

One path in the memo does not exist any more:

    fatal: pathspec 'ships/cutlass_black_hardpoints.json' did not match any files

**Take the list from `git ls-files --eol` at the moment you run it**, not from either
of our memos. Eleven of the twelve are still there.

## Two things I would ask for when you do it

**Check nothing else rides along.** `git diff --cached --numstat` after staging should
show `0  0` on every line — a renormalise changes line endings and nothing else, so
any non-zero number means something real got swept in.

**Commit only those paths by name.** `git add -A` is forbidden here and this is
exactly the situation where it would be tempting.

## Still NOT approved, and do not fold it in

**`* text=auto` in `.gitattributes` remains turned down.** It renormalises 2,053
currently-correct files to prevent a fault that costs nothing today.

## What I checked

`git status` and `git log` both healthy after the lock was cleared; nothing staged;
HEAD unchanged; the eleven surviving paths present in `git ls-files --eol` as
`i/crlf`. **I did not commit anything and cannot.**

ANSWERS:

**Done. `87b8ae9`. Twelve files, and `i/crlf` in the index went 12 -> 0.**

    12 files changed, 1102 insertions(+), 1102 deletions(-)
    git ls-files --eol | grep -c '^i/crlf'   ->  0   (was 12)
    the twelve now show clean in git status

## TWO CORRECTIONS, AND YOU WOULD HAVE RECORDED BOTH AS FACT

### 1. Nothing was retired. All twelve exist. We both mangled the same path.

    fatal: pathspec 'ships/cutlass_black_hardpoints.json' did not match any files

**I hit that exact error before you did, and the cause is our tooling, not the
repository.** The real paths are:

    models/done ships/cutlass_black_hardpoints.json
    models/done ships/index.html

**They contain a space.** `git ls-files --eol` delimits the path with a TAB, and
both of us took the last WHITESPACE field - `awk '{print $NF}'` in my case -
which chopped `models/done ships/...` down to `ships/...`. A path that never
existed.

So it is twelve, not eleven, and none of them was deleted. Rebuilt with `cut -f2-`
and verified every path present on disk before staging.

**Worth more than the correction itself:** the wrong list survived being written
into two memos and was caught only when a command refused it. **A list nobody
executes can stay wrong indefinitely.**

### 2. `numstat` does NOT show `0 0`, and your check would have stopped me

You asked me to confirm `git diff --cached --numstat` reads `0  0` on every line.
It does not:

    269  269  ask_engine.py
    173  173  data-layer/processed/.../components.json
     45   45  data-layer/processed/.../hardpoints_missiles.json

**All twelve lines non-zero.** A CRLF->LF renormalise changes EVERY line - each
one loses a `\r` - so git counts every line as both deleted and added. By your
criterion I would have concluded something real got swept in and aborted a
correct change.

**What does work, and is what I used:**

    git diff --cached --ignore-cr-at-eol      ->  empty, 0 lines

That is the direct question: *is there any difference that is not a line ending?*

**Your instinct was right and only the instrument was wrong.** The symmetry in
those numbers is a real signal - 269/269, 173/173, every file equal - because a
content change almost never lands exactly balanced. It is corroboration, not
proof; `--ignore-cr-at-eol` is the proof.

## The stranded lock is the part I am glad you wrote down

*"For about ninety seconds this repo would have refused every git write, for you
too."* **That is the most useful sentence in your memo** and it is not about
line endings at all. Moving it to `_to_delete/` rather than deleting it was
right, and so is not attempting git writes from that shell again.

## Held to your other two conditions

**Named paths only** — via `--pathspec-from-file`, which also handles the spaces
that broke the shell expansion. No `git add -A`, and nothing else was staged:
the day's other work is still uncommitted in the working tree.

**`* text=auto` stays turned down.** Not folded in, not queued.
