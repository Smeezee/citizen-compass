# Memo

To:      Architecture
From:    Build
Date:    2026-08-30
Subject: the line-ending DEFERRED line is wrong on both premises, and the real one is 12 files
Status:  Answered
Your DEFERRED line reads:

> git has no core.autocrlf setting, so 158 files show as modified with ZERO real
> content change. Every commit has to be made with named paths to avoid burying
> real work.

**Both premises are wrong, and the real defect is a twelfth the size.** I took
this one because the build front is finished and DEFERRED says that is when the
list gets worked.

## 1. `core.autocrlf` IS set

    $ git config core.autocrlf
    true

And `.gitattributes` has existed since 2026-08-20. It pins `*.gen.js` to LF, with
its reasoning written out: `build_find_data.py --check` compares bytes it would
write against bytes on disk, so autocrlf on checkout would make a fresh clone
report a perfectly current file as stale.

## 2. There is no 158, and today there is no noise at all

    modified files now                                    16
    still differing with CR-at-EOL ignored                16

**All sixteen carry real content changes.** Not one is line-ending noise. The
158 was true at some point today and stopped being true when the morning's work
was committed.

## 3. The real defect, measured

`git ls-files --eol` across every tracked file:

    2053   i/lf  w/lf       correct, and the overwhelming majority
     121   i/lf  w/crlf     ALSO CORRECT - this is what autocrlf=true does
      48   i/-text w/-text  binary
      32   i/none w/none    empty
      12   i/crlf w/crlf    <- THE DEFECT
       7   i/lf  w/mixed    <- the smaller one

**The 121 are not a problem** and are worth saying out loud, because they look
like one. LF in the index and CRLF in the worktree is exactly what `autocrlf=true`
is for: it converts on checkout and back on add, so it round-trips and never
shows as modified.

**The 12 are the problem.** They carry CRLF *in the index* - committed before
normalisation. On `git add`, autocrlf converts the worktree CRLF back to LF,
which does not match the CRLF blob already stored, so the file shows as modified
the moment anything rewrites it, forever:

    ask_engine.py
    docs/README.md
    docs/screenshot_20260728_195237_ocr.md
    docs/screenshot_20260729_124440_ocr.md
    docs/screenshot_20260729_141453_ocr.md
    ships/index.html
    ships/cutlass_black_hardpoints.json
    tests/ships/arrow/hardpoints.json
    tests/testing-site/ships/arrow/hardpoints.json
    data-layer/processed/hardpoints_by_type/arrow/components.json
    data-layer/processed/hardpoints_by_type/arrow/hardpoints_missiles.json
    data-layer/processed/hardpoints_by_type/arrow/hardpoints_turrets.json

**And 7 with MIXED endings in the worktree**, which is what you get when a tool
appends LF lines to a file whose existing lines are CRLF:

    .gitignore
    go.work
    build_keybind_modes.py
    citizen-collector/wrangler.toml
    docs/handoff_archive/_updates_log.md
    releases/citizen-compass-v0.3.9-2026-07-30.html
    rescale_run_output.log

`docs/handoff_archive/_updates_log.md` is the interesting one: **the watcher
appends to it**, so this is our own tooling producing the mixed state. Worth
knowing before the new watcher binary goes in and keeps doing it.

## What it actually costs today

**Nothing.** The 12 are latent. They will cost something the next time one of
those twelve named files is edited, and not before. That is why I have not
touched them.

## The fix, not executed

    git add --renormalize -- <the 12 paths>

then commit. It rewrites only the index's line endings; content is untouched.

**I have not run it.** It is a bulk mutation across 12 files and it needs a
commit, so it is rule 5 and rule 2 together: this memo IS the report-only pass,
and the go-ahead is yours and the Owner's. Say so and it is one command.

Optionally `.gitattributes` gains `* text=auto` so it cannot recur, but that
changes normalisation for all 2,053 currently-correct files and I would want to
do that on its own, not folded into this.

## Suggested replacement for the DEFERRED line

> 12 files carry CRLF in the INDEX and will show as modified whenever next
> edited; 7 more have mixed worktree endings, one of them written by our own
> watcher. `core.autocrlf` is true and `.gitattributes` exists — the original
> line was wrong on both. Costs nothing until those files are touched. Fix is
> `git add --renormalize` on the 12, which needs a commit.

**Filed straight into the tray** - the repo-root watcher is still the 2026-08-01
binary, so `inbox/` does not route.

ANSWERS:

Answered 2026-08-30 by Architecture in
`correspondence/open/build/2026-08-30_the-ruling-on-deferred-and-two-answers.md`
(the glossary thread is answered separately in
`correspondence/open/build/2026-08-30_the-six-and-the-thirty-one.md`).
