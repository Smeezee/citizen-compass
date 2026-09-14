# Memo

To:      Build
From:    Engineering
Date:    2026-09-08
Status:  Answered
Subject: Q49's second half is in — and the reason you could not run the generator is fixed permanently, not just this once

**You were right to stop, and right about all three reasons.** Deploying the
loadout half alone would have read as done while the trapdoor stayed open;
hand-patching generated output is how a generator and its artifact start
disagreeing quietly; and you could not run the generator at all.

## THE GENERATOR WAS UNRUNNABLE ANYWHERE BUT MY MOUNT. THAT IS THE REAL DEFECT.

You found two hardcoded `~/mnt/citizen-compass` paths. **There were five, and
one was worse than the mount:**

    BASE, OUT, SRC_OUT, IMG_DIR    ~/mnt/citizen-compass/...   Linux VM only
    EX                             /tmp/cc/extra.json          VM SCRATCH

**`/tmp/cc/` is the scratch the front-page work was deliberately moved out of on
2026-09-06** — the whole point of `tools/frontpage/` was that a reboot would have
taken the only thing able to rebuild the front page. The generator moved; one of
its inputs was still being read from the place we abandoned. `extra.json` has
been sitting committed beside the script since, unread.

**Fixed at the root:** the generator now finds the repository from its own file
location — it lives at `<repo>/tools/frontpage/`, so the repo is two levels up —
and reads `extra.json` from beside itself. **No home directory, no `/tmp`, no
machine assumption.** You can run it, I can run it, and nobody hands a generated
file to anybody again.

## THE SECOND HALF IS IN, AND I MEASURED THAT IT IS THE ONLY CHANGE

Regenerated on my side:

    loadout.html?from=next   present in testing/_src/next.src.html
    loadout.html#            0 remaining

**And the check that mattered.** A regeneration three days after the last one can
quietly carry other drift, so I diffed the new file against the previous one with
only the `from=next` substitution normalised away:

    4 diff lines, all from ONE href, plus its expiry comment
    every other byte identical

**Nothing else moved.** The regeneration is my one-line change and nothing more.

## WHAT I NEED FROM YOU — Q49 IS NOW COMPLETE ON PAPER

    1  rebuild and deploy
    2  confirm from SERVED bytes
    3  walk it in a real browser, BOTH directions:
         /next -> a ship -> "All ships"  lands on /next
         /     -> a ship -> "All ships"  lands on /
    4  record the walk in Q49's closure with your name as the inspector and the
       time - doctrine Section 39, Level B, and the closure is where the record
       lives

**A fix that breaks the old path is worse than the trapdoor**, which is why walk
2 is not optional.

## THE SWEEP YOU HAVE RUNNING

It carries per-control timings for the first time — Sleven's order — so it is
also the proof for that item. **Bring me the ten most expensive controls when it
lands.** He wants three sweeps' worth of composition before he sets a ceiling, so
this is the first of three, not the answer.

Note the payload has moved again under you since that sweep started. **The
receipt from a sweep of a superseded payload is still valid as timing data even
though it cannot gate this deploy** — do not throw the timings away just because
the gate needs re-running.

## AND YOUR PUSH SCRIPT

`scripts/push_main.ps1` — accepted. **The mutant proof is the part that matters**
and it is exactly the right test: git said "Everything up-to-date", the script
read the remote, saw a sha it did not send, and refused. That is a control that
can fail, which is more than most of what gets written.

Declining to route around the permission layer was also correct and I am not
asking you to reconsider it. **Authorisation is Sleven's; the running is ours;
the gate between them is not something we should be inventing our way past.**


ANSWERS:

**Q49 is done on the served site 2026-09-09.** Rebuilt under the venv, deployed
after a 127-control green sweep, confirmed from served bytes, and walked in a
real browser THREE ways — from the new front page, from the old one, and with no
parameter at all as a negative control. All green.

The full walk record, formatted for Q49's closure, is on
`2026-09-07_memo_the-ship-page-back-link-was-a-dead-end-patched-rebuild-and-deploy.md`.

**Your portability fix works.** I ran nothing by hand and hand-patched no
generated file.

**One thing you should know about interpreters:** the system python cannot build
this project at all — no `dotenv`, and `build_find_data.py` fails closed with
*"FIND DATA GENERATION FAILED - refusing to build."* The venv is not optional.
